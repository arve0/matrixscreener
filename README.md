# matrixscreener #
This is a python module for interfacing with *Leica LAS AF MatrixScreener*.
It can read experiments and communicate with the microscope over network.

For example, the module can be used to stitch wells from an experiment exported
with the *LAS AF Data Exporter*, as well as programmatically selecting
slides/wells/fields/images given by position attributes (U, V, X, Y, z-stack),
channel, etc.

The module is developed on Mac OS X, but should work on Linux and Windows too.
If you find any bugs, please report them as an
[issue](https://github.com/arve0/matrixscreener/issues/new) on github. Pull
request are also welcome.


## Features ##
- Access experiment as a python object
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

**do stuff on all images**
```python
from matrixscreener import experiment

scan = experiment.Experiment('path/to/experiment--')

for image in scan.images:
    do stuff...
```

**do stuff on specific wells/fields**
```python
from matrixscreener import experiment

# select specific parts
selected_wells = [well for well in scan.wells if 'U00' in well]
for well in selected_wells:
    do stuff...

def condition(path):
    x_above = experiment.attribute(path, 'X') > 1
    x_below = experiment.attribute(path, 'X') < 5
    return x_above and x_below

selected_fields = [field for field in scan.fields if condition(field)]
for field in selected_fields:
    do stuff..
```

**subtract data**
```python
from matrixscreener.experiment import attribute

# get all channels
channels = [attribute(image, 'C') for image in scan.images]
min_ch, max_ch = min(channels), max(channels)
```

**communicate with microscope**
```python
from matrixscreener.cam import CAM

cam = CAM()   # initiate and connect, default localhost:8895

# some commands are created as short hands
# start matrix scan
response = cam.start_scan()
print(response)

# but you could also create your own command with a list of tuples
command = [('cmd', 'enableall'),
           ('value', 'true')]
response = cam.send(command)
print(response)

# or even send it as a bytes string (note the b)
command = b'/cmd:enableall /value:true'
response = cam.send(command)
print(response)
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
All commands should be documented in docstrings in
[numpy format](https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt).

An [online](http://matrixscreener.readthedocs.org) version is available.

It can also be read with [pydoc](https://docs.python.org/3.4/library/pydoc.html)
or any editor that does autocomplete with docstrings.

In example:
```
pydoc matrixscreener
pydoc matrixscreener.cam
pydoc matrixscreener.experiment
pydoc matrixscreener.imagej
```
