# LeicaExperiment
This is an python class which can be used to read the structured output from a Leica LAS Matrix Scan when using the data exporter (ome.tifs organized in slide/chamber/field folders).


# Examples
## merge z-stack
```
from leicaexperiment import LeicaExperiment
experiment = LeicaExperiment('path/to/experiment--')
for well in experiment.wells:
    for channel in range(well.channels):
        for z in range(well.z_stacks):
            img = well.merge(z, channel)
            do stuff...
```

## do stuff on all images
```
experiment = LeicaExperiment('path/to/experiment--')
for well in experiment.wells:
    for field in well.fields:
        for image in field.images:
            image_data = imread(image.fullpath)
            do stuff...
```
