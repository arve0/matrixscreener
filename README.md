# matrixscreener #
This is a python module for interfacing with *Leica LAS AF/X Matrix Screener*.
It can read experiments and communicate with the microscope over network.

The module can be used to:

- stitch wells from an experiment exported with the *LAS AF Data Exporter*
- batch compress images lossless
- programmatically select slides/wells/fields/images given by attributes like
    - slide (S)
    - well position (U, V)
    - field position (X, Y)
    - z-stack position (Z)
    - channel (C)
- read experiment data from OME-XML

The module is developed on Mac OS X, but should work on Linux and Windows too.
If you find any bugs, please report them as an
[issue](https://github.com/arve0/matrixscreener/issues/new) on github. Pull
request are also welcome.


## Features ##
- Access experiment as a python object
- Compress to PNGs without loosing precision, metadata or colormap
- ImageJ stitching (Fiji is installed via [fijibin](https://github.com/arve0/fijibin))
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

print(matrixscreener.imagej._bin) # Fiji installed via package fijibin
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

**batch lossless compress of experiment**
```
import matrixscreener as ms

e = ms.experiment.Experiment('/path/to/experiment')
pngs = ms.experiment.compress(e.images)
print(pngs)
```
See also [this notebook](http://nbviewer.ipython.org/github/arve0/matrixscreener/tree/master/notebooks/compress.ipynb).


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

**specific test, here compression test**
```
pip install pytest numpy
py.test -k compression tests/test_experiment.py
```

**specific test with extra output, jump into pdb upon error**
```
DEBUG=matrixscreener py.test -k compression tests/test_experiment.py --pdb -s
```


## API Reference ##
All commands should be documented in docstrings in
[numpy format](https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt).

API reference is available [online](http://matrixscreener.readthedocs.org),
can be read with [pydoc](https://docs.python.org/3.4/library/pydoc.html)
or any editor/repl that does autocomplete with docstrings.

In example:
```
pydoc matrixscreener
pydoc matrixscreener.cam
pydoc matrixscreener.experiment
pydoc matrixscreener.imagej
```
