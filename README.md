# LeicaExperiment #
This is an python class which can be used to read the structured output from a Leica LAS Matrix Scan when using the data exporter (ome.tifs organized in slide/chamber/field folders).


## Features
- ImageJ stitching


## Install ##
```
pip install leicaexperiment
```


## Examples ##
### stitch well ###
```
from leicaexperiment import Experiment
experiment = Experiment('path/to/experiment--')
well = experiment.wells[0]
well.stitch('/path/to/output/files/')
```

### do stuff on all images ###
```
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
- imagej with Grid stitching plugin (fiji is recommended)
