# v 0.6.1
- readme on pypi, because...

# v 0.6.0
- receive will wait until timeout for command

# v 0.5.2
- explicit disable
- debug in cam-module

# v 0.5.1
- require fijibin>=0.0.3

# v 0.5.0
- do compression and stitching with multiprocessing
- move imagej submodule to fijibin

# v 0.4.2
- fix new image filename format (four characters for some attributes)
- use absolute paths for slides, wells, etc
- escape paths in imagej macro

# v 0.4.1
- Experiment.compress method
- Experiment.stitched property
  - stitched images now uses same format as original files
    (stitched--UXX-VXX...png) so that attributes(filename) can be used
- Include Fiji with pypi package fijibin
- more elaborate tests
- support for 16 bit ome.tif

# v 0.4.0
- add compress/decompress function
- fix missing /cmd:enable for enable method

# v 0.3.1
- connect upon initialization
- fix parse errors in `bytes_as_dict`
  - better handles format "errors"
- assume first response is information in `get_information`
- use non-blocking socket reading

# v 0.3.0
- parameters from names, resolving bug when job (J) was incorrectly set
- design class flat instead of nested
  - loop with list comprehensions
- added support for Computer Assisted Microscopy (CAM)

# v 0.2.1
- omit already stitched files

# v 0.2.0
- rename from leicaexperiment to matrixscreener
- well.merge() is removed
- imagej stitching added: Experiment.stitch() and well.stitch()
