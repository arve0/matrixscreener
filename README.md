# matrixscreener #
This is an python module for interfacing with Leica LAS AF MatrixScreener.
It can read experiments and communicate with microscope over network.

The module can be used to stitch wells from an experiment exported with the
LAS AF *Data Exporter*, as well as programmatically selecting
slides/wells/fields/images given by position attributes (U, V, X, Y, z-stack),
channel, etc.

The module is developed on Mac OS X, but should work on Linux and Windows too.
If you find any bugs, please report them as an issue on github. Pull request
are also welcome.


## Features ##
- Access experiment as python object
- ImageJ stitching
- Communicate with microscope over CAM TCP/IP socket


## Install ##
```
pip install matrixscreener
```


## Examples ##
**stitch experiment**
```python
import matrixscreener
# create short hand
Experiment = matrixscreener.experiment.Experiment

# path should contain AditionalData and slide--S*
scan = Experiment('path/to/experiment')

print(matrixscreener.imagej._bin) # default is for fiji on mac os x
matrixscreener.imagej._bin = '/path/to/imagej'

# if path is omitted, experiment path is used for output files
stitched_images = experiment.stitch('/path/to/output/files/')
```

**stitch specific well**
```python
from matrixscreener import experiment

# path should contain AditionalData and slide--S*
stitched_images = experiment.stitch('/path/to/well')
```

**do stuff on images**
```python
from matrixscreener import experiment

scan = experiment.Experiment('path/to/experiment--')

# select specific parts
selected_wells = [well for well in scan.wells if 'U00' in well]
for well in selected_wells:
    do stuff...

def condition(path):
    x_above = experiment.attribute_as_int(path, 'X') > 1
    x_below = experiment.attribute_as_int(path, 'X') < 5
    return x_above and x_below

selected_fields = [field for field in scan.fields if condition(field)]
for field in selected_fields:
    do stuff..
```

**subtract data**
```python
from matrixscreener.experiment import attribute_as_int

# get all channels
channels = [attribute_as_int(image, 'C') for image in scan.images]
min_ch, max_ch = min(channels), max(channels)
```

**speak with microscope**
```python
from matrixscreener.cam import CAM

cam = CAM()   # initiate
cam.connect() # default localhost:8895

# command as tuples in list with keys and values
command = [('cmd', 'enableall'),
           ('value', 'true')]
response = cam.send(command)

# command as bytes string
command = b"/cmd:enableall /value:true"
bytes_sent = cam.socket.send(command)
response = cam.socket.recv(cam.buffer_size)
```


## Dependencies ##
- ImageJ with Grid stitching plugin (fiji is recommended)


## Develop ##
```
git clone https://github.com/arve0/matrixscreener.git
cd matrixscreener
# hack
./setup.py install
```

## Testing ##
```
pip install tox
tox
```

## API Reference ##
Use `pydoc matrixscreener`, `pydoc matrixscreener.cam`,
`pydoc matrixscreener.experiment`, `pydoc matrixscreener.imagej` or read it
[online](http://matrixscreener.readthedocs.org).
