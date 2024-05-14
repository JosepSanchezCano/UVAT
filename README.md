# UVAT
Josep Sánchez, Jose-Luis LISANI
University of the Balearic Islands

[Paper (pending)]

The Underwater Video Annotation Tool (UVAT) is an open source tool that greatly improves the time needed to annotate video data. This repository contains the code for the tool to work in Linux and Windows systems.


![Flux diagram showing the most common workflow](https://github.com/JosepSanchezCano/UVAT/blob/main/flux.png?raw=true)

Demo video



https://github.com/JosepSanchezCano/UVAT/assets/152962791/9275e2c0-3b44-40ab-9eee-f96212e86fed


## Installation

To install the tool some instruction for the Ubuntu command lines will be given

** Need to have: **

    - Python 3.10+*
    - PyTorch and corresponding Cuda

** Install with conda **

```bash
git clone https://github.com/JosepSanchezCano/UVAT
cd UVAT
conda create --name UVAT --file requirements.txt
```

To be able to run the application is needed to download the weights from : link

It is enough to drop the folder inside the repository

