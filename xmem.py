import os
from os import path
from argparse import ArgumentParser
import shutil
import gc
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
import numpy as np
from PIL import Image

from XMem.inference.data.test_datasets import LongTestDataset, DAVISTestDataset, YouTubeVOSTestDataset
from XMem.inference.data.mask_mapper import MaskMapper
from XMem.model.network import XMem
from XMem.inference.inference_core import InferenceCore

from progressbar import progressbar

import cv2
from XMem.inference.interact.interactive_utils import image_to_torch, index_numpy_to_one_hot_torch, torch_prob_to_numpy_mask, overlay_davis

torch.set_grad_enabled(False)

# default configuration
CONFIG = {
    'top_k': 30,
    'mem_every': 5,
    'deep_update_every': -1,
    'enable_long_term': True,
    'enable_long_term_count_usage': True,
    'num_prototypes': 128,
    'min_mid_term_frames': 5,
    'max_mid_term_frames': 10,
    'max_long_term_elements': 10000,
}

DEVICE = "cuda"

class Xmem:

    def __init__(self,num_obj = 0, propagation_frames = 200) -> None:
        self.network = XMem(CONFIG, './XMem/saves/XMem.pth').eval().to(DEVICE)
        
        self.max_frames = num_obj

        self.current_frame_index = 0

        self.max_propagation_frames = propagation_frames
        #torch.set_grad_enabled(False)

    def setMaxFrames(self, numFrames):
        self.max_frames = numFrames

    def setNumObj(self, num_obj):
        self.procesor = InferenceCore(self.network, config = CONFIG)
        self.procesor.set_all_labels(range(1, num_obj + 1 ))

    def _obtainIdsFromMask(self,mask):
        ids = []

    def propagate(self,frames,mask, num_obj,current_frame = 0):

        processor = InferenceCore(self.network, config=CONFIG)
        processor.set_all_labels(range(1, num_obj+1)) # consecutive labels
        masks = []
        #print(mask)
        mask_aux = np.array(mask).astype(np.uint8)
        mask_aux = cv2.resize(mask_aux,(1280,720))

        #print(frames[0].shape)
        height,width, _ = frames[0].shape

        self.current_frame_index = current_frame

        frames_propagated = 0

        first_frame = True
        with torch.cuda.amp.autocast(enabled=True):

            while self.current_frame_index < self.max_frames and frames_propagated < self.max_propagation_frames:
                frame = frames[self.current_frame_index]

                print(f"frame: {self.current_frame_index}")
                aux_frame = cv2.resize(frame,(1280,720))
                frame_torch, _ = image_to_torch(aux_frame, device=DEVICE)

                #print(frame)
                if first_frame:
                    mask_torch = index_numpy_to_one_hot_torch(mask_aux, num_obj +1).to(DEVICE)

                    prediction = processor.step(frame_torch, mask_torch[1:])
                    first_frame = False
                else:
                    print(f"Mem info: {torch.cuda.mem_get_info()}")
                    prediction = processor.step(frame_torch)

                prediction = torch_prob_to_numpy_mask(prediction)
                
                prediction = cv2.resize(prediction,(width,height),interpolation=cv2.INTER_NEAREST_EXACT)
                # cv2.imshow("ventana",prediction*255)
                # cv2.waitKey(0)

#                print(prediction)
                #print(np.unique(prediction))
                masks.append(prediction)    

                self.current_frame_index += 1
                frames_propagated += 1

                #torch.cuda.empty_cache()
                #gc.collect()
            #print(masks)
        
        return masks