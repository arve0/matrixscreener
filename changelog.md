# v 0.4.1
- Experiment.compress method
- Experiment.stitched property
  - stitched images now uses same format as original files
    (stitched--UXX-VXX...png) so that attributes(filename) can be used
- Include Fiji with pypi package fijibin

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
