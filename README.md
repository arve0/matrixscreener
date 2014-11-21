# MatrixScreener #
This is an python module which can be used to read and stitch the structured output from a Leica LAS AF Matrix Screener when using the data exporter (ome.tifs organized in slide/chamber/field folders).

This modules is developed on Mac OS X. If you find any bugs on Linux or Windows, please report them as an issue on github or send a pull request.


## Features
- Access experiment as python object
- ImageJ stitching


## Install ##
```
pip install matrixscreener
```


## Examples ##
### stitch well ###
```
import matrixscreener

experiment = matrixscreener.Experiment('path/to/experiment--')
well = experiment.wells[0]

print(matrixscreener.imagej.IMAGEJ_PATH) # default is for fiji on mac os x
matrixscreener.imagej.IMAGEJ_PATH = '/path/to/imagej'
matrixscreener.imagej.DEBUG = True # turn on output from ImageJ

well.stitch('/path/to/output/files/')
```

### do stuff on all images ###
```
from matrixscreener import Experiment
experiment = Experiment('path/to/experiment--')
for well in experiment.wells:
    for field in well.fields:
        for image in field.images:
            image_data = imread(image.fullpath)
            do stuff...
```


## Dependencies ##
- tifffile
- numpy
- ImageJ with Grid stitching plugin (fiji is recommended)


## Develop ##
```
git clone https://github.com/arve0/matrixscreener.git
cd matrixscreener
# hack
./setup.py install
```
