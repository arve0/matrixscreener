# encoding: utf-8
"""
Access matrix scans from Leica LAS AF MatrixScreener (Data Explorer)
through an object.
"""
# doc-format https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt

# imports
import os, glob, re
from collections import namedtuple
from .imagej import stitch_macro, run_imagej



# variables in case custom folders
_slide = 'slide'
_chamber = 'chamber'
_field = 'field'
_image = 'image'



# classes
class Experiment:
    def __init__(self, path):
        """Leica LAS AF MatrixScreener experiment.

        Parameters
        ----------
        path : string
            Path to matrix scan containing 'slide-SXX' and 'AdditinalData'.

        Attributes
        ----------
        path : string
            Full path to experiment.
        dirname : string
            Path to folder below experiment.
        basename : string
            Foldername of experiment.
        """
        _set_path(self, path)

        self._slide_path = _pattern(path, _slide)
        self._well_path = _pattern(self._slide_path, _chamber)
        self._field_path = _pattern(self._well_path, _field)
        self._image_path = _pattern(self._field_path, _image)

        # alias
        self.chambers = self.wells

    @property
    def slides(self):
        "List of paths to slides."
        return glob.glob(self._slide_path)

    @property
    def wells(self):
        "List of paths to wells."
        return glob.glob(self._well_path)

    @property
    def fields(self):
        "List of paths to fields."
        return glob.glob(self._field_path)

    @property
    def images(self):
        "List of paths to images."
        return glob.glob(self._image_path)

    def __str__(self):
        return 'matrixscreener.Experiment({})'.format(self.path)

    def stitch(self, folder=None):
        """Stitches all wells in experiment with ImageJ. Stitched images are
        saved in experiment root.

        Images which already exists are omitted stitching.

        Parameters
        ----------
        folder : string
            Where to store stitched images. Defaults to experiment path.

        Returns
        -------
        list
            Filenames of stitched images. Files which already exists are also
            returned.
        """
        if not folder:
            folder = self.path

        output_files = []
        for well in self.wells:
            output_files.extend(stitch(well, folder))

        return output_files


# methods
def stitch(path, output_folder=None):
    """Stitch well given by path.

    Parameters
    ----------
    path : string
        Well path.
    output_folder : string
        Folder to store images. If not given well path is used.

    Returns
    -------
    list
        Filenames for stitched images.
    """
    output_folder = output_folder or path

    fields = glob.glob(_pattern(path, _field))

    # assume we have rectangle of fields
    xs = [attribute_as_int(field, 'X') for field in fields]
    ys = [attribute_as_int(field, 'Y') for field in fields]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    fields_x = len(set(xs))
    fields_y = len(set(ys))

    # assume all fields are the same
    # and get properties from images in first field
    images = glob.glob(_pattern(fields[0], _image))

    # assume attributes are the same on all images
    attr = attributes(images[0])

    # find all channels and z-stacks
    channels = []
    z_stacks = []
    for image in images:
        channel = attribute(image, 'C')
        if channel not in channels:
            channels.append(channel)

        z = attribute(image, 'Z')
        if z not in z_stacks:
            z_stacks.append(z)


    # create macro
    macro = []
    output_files = []
    for Z in z_stacks:
        for C in channels:
            filenames = (_field + '--X{xx}--Y{yy}/' +
                    _image + '--L' + attr.L +
                    '--S' + attr.S +
                    '--U' + attr.U +
                    '--V' + attr.V +
                    '--J' + attr.J +
                    '--E' + attr.E +
                    '--O' + attr.O +
                    '--X{xx}--Y{yy}' +
                    '--T' + attr.T +
                    '--Z' + Z +
                    '--C' + C +
                    '.ome.tif')

            output_file = 'u{}v{}ch{}z{}.tif'.format(attr.u, attr.v, int(C), int(Z))

            relpath = os.path.relpath(output_folder, path)
            rel_filename = os.path.join(relpath, output_file)

            output = os.path.join(output_folder, output_file)
            output_files.append(output)
            if os.path.isfile(output):
                # file already exists
                continue
            macro.append(stitch_macro(
                    path, filenames, fields_x, fields_y,
                    output_filename=rel_filename,
                    x_start=x_min, y_start=y_min))

    # stitch images with ImageJ
    if len(macro) != 0:
        run_imagej(' '.join(macro))

    # remove files which are not created
    output_files = [filename for filename in output_files
                        if os.path.isfile(filename)]

    return output_files


def attribute(path, name):
    """Returns the two numbers found behind --[A-Z] in path. name should be
    [A-Z]. If several matches are found, the last one is returned
    """
    matches = re.findall('--' + name + '([0-9]{2})', path)
    if matches:
        return matches[-1]
    else:
        return None

def attribute_as_int(*args):
    "Short hand for int(attributes(*args))"
    return int(attribute(*args))

def attributes(path):
    """Get attributes from path based on format --[A-Z]. Returns namedtuple
    with upper case attributes equal to what found in path (string) and lower
    case as int. If path holds several occurrences of same character, only the
    last one is kept.

    Example
    -------
    path = '/folder/file--X00-X01.tif' returns
    namedtuple('attributes', 'X x')('01', 1)
    """
    matches = re.findall('--([A-Z]{1})([0-9]{2})', path)

    keys = []
    values = []
    for k,v in matches:
        if k in keys:
            # keep only last key
            i = keys.index(k)
            del keys[i]
            del values[i]
        keys.append(k)
        values.append(v)

    lower_keys = [k.lower() for k in keys]
    int_values= [int(v) for v in values]

    attributes = namedtuple('attributes', keys + lower_keys)

    return attributes(*values + int_values)



# helper functions
def _pattern(*names):
    "Returns globbing pattern for name1/name2/../lastname + '--*'"
    return os.path.join(*names) + '--*'


def _set_path(self, path):
    "Set self.path, self.dirname and self.basename."
    import os.path
    self.path = os.path.abspath(path)
    self.dirname = os.path.dirname(path)
    self.basename = os.path.basename(path)


def _between(before, after, string):
    """Strip string and return whats between before and after as integer.

    Parameters
    ----------
    before : string
        String to match before wanted portion
    after : string
        String to match after wanted portion
    string : string
        String to parse

    Returns
    -------
    int
        Partion between before and after as integer.
    """
    return int(string.split(before)[1].split(after)[0])
