# encoding: utf-8
"""
Access matrix scans from Leica LAS AF MatrixScreener (Data Exporter)
through an object.
"""
##
# imports
##
import os, re, pydebug
from glob import glob
from collections import namedtuple
from .imagej import stitch_macro, run_imagej

# compress
from PIL import Image
from PIL.ImagePalette import ImagePalette
import json
from copy import copy

# debug with `DEBUG=matrixscreener python script.py`
debug = pydebug.debug('matrixscreener')


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
        return glob(self._slide_path)

    @property
    def wells(self):
        "List of paths to wells."
        return glob(self._well_path)

    @property
    def fields(self):
        "List of paths to fields."
        return glob(self._field_path)

    @property
    def images(self):
        "List of paths to images."
        tifs = _pattern(self._image_path, extension='tif')
        pngs = _pattern(self._image_path, extension='png')
        imgs = []
        imgs.extend(glob(tifs))
        imgs.extend(glob(pngs))
        return imgs

    @property
    def stitched(self):
        "List of stitched images if they are in experiment folder."
        return glob(_pattern(self.path, 'stitched'))

    def __str__(self):
        return 'matrixscreener.Experiment({})'.format(self.path)

    def __repr__(self):
        return self.__str__()

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
            Filenames of stitched images. Files which already exists before
            stitching are also returned.
        """
        debug('stitching ' + self.__str__())
        if not folder:
            folder = self.path

        output_files = []
        for well in self.wells:
            output_files.extend(stitch(well, folder))

        return output_files

    def compress(self, delete_tif=False, folder=None):
        """Lossless compress all images in experiment to PNG. If folder is
        omitted, images will not be moved.

        Images which already exists in PNG are omitted.

        Parameters
        ----------
        folder : string
            Where to store PNGs. Defaults to the folder they are in.
        delete_tif : bool
            If set to truthy value, ome.tifs will be deleted after compression.

        Returns
        -------
        list
            Filenames of PNG images. Files which already exists before
            compression are also returned.
        """
        return compress(self.images, delete_tif=delete_tif, folder=folder)



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
    debug('stitching ' + path + ' to ' + output_folder)
    output_folder = output_folder or path

    fields = glob(_pattern(path, _field))

    # assume we have rectangle of fields
    xs = [attribute(field, 'X') for field in fields]
    ys = [attribute(field, 'Y') for field in fields]
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    fields_x = len(set(xs))
    fields_y = len(set(ys))

    # assume all fields are the same
    # and get properties from images in first field
    images = glob(_pattern(fields[0], _image))

    # assume attributes are the same on all images
    attr = attributes(images[0])

    # find all channels and z-stacks
    channels = []
    z_stacks = []
    for image in images:
        channel = attribute_as_str(image, 'C')
        if channel not in channels:
            channels.append(channel)

        z = attribute_as_str(image, 'Z')
        if z not in z_stacks:
            z_stacks.append(z)

    debug('channels ' + str(channels))
    debug('z-stacks ' + str(z_stacks))

    # create macro
    _, extension = os.path.splitext(images[-1])
    if extension == '.tif':
        # assume .ome.tif
        extension = '.ome.tif'
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
                    extension)
            debug('filenames ' + filenames)

            cur_attr = attributes(filenames)._asdict()
            output_file = 'stitched--U{U}--V{V}--C{C}--Z{Z}.png'.format(**cur_attr)
            debug('output_file ' + output_file)

            relpath = os.path.relpath(output_folder, path)
            rel_filename = os.path.join(relpath, output_file)
            debug('rel_filename ' + rel_filename)

            output = os.path.join(output_folder, output_file)
            output_files.append(output)
            if os.path.isfile(output):
                # file already exists
                continue
            macro.append(stitch_macro(
                    path, filenames, fields_x, fields_y,
                    output_filename=rel_filename,
                    x_start=x_min, y_start=y_min))

    # exit immediately
    macro.append('eval("script", "System.exit(0);");')
    debug('macro ' + ' '.join(macro))

    # stitch images with ImageJ
    if len(macro) != 0:
        run_imagej(' '.join(macro))

    # remove files which are not created
    output_files = [filename for filename in output_files
                        if os.path.isfile(filename)]

    return output_files

def compress(images, delete_tif=False, folder=None):
    """Lossless compression. Save images as PNG and TIFF tags to json. Process
    can be reversed with `decompress`.

    Parameters
    ----------
    images : list of filenames
        Images to lossless compress.
    delete_tif : bool
        Wheter to delete original images.

    Returns
    -------
    list of filenames
        List of compressed files.
    """
    if type(images) == str:
        # only one image
        return compress([images])

    filenames = copy(images) # as images property will change when looping

    compressed_images = []
    for orig_filename in filenames:
        debug('compressing {}'.format(orig_filename))
        try:
            new_filename, extension = os.path.splitext(orig_filename)
            # remove last occurrence of .ome
            new_filename = new_filename.rsplit('.ome', 1)[0]

            # if compressed file should be put in specified folder
            if folder:
                basename = os.path.basename(new_filename)
                new_filename = os.path.join(folder, basename + '.png')
            else:
                new_filename = new_filename + '.png'

            # check if png exists
            if os.path.isfile(new_filename):
                compressed_images.append(new_filename)
                msg = "Aborting compress, PNG already exists: {}".format(new_filename)
                raise AssertionError(msg)
            if extension != '.tif':
                msg = "Aborting compress, not a TIFF: {}".format(orig_filename)
                raise AssertionError(msg)

            # open image, load and close file pointer
            img = Image.open(orig_filename)
            img.load() # load img-data before switching mode, also closes fp

            # get tags and save them as json
            tags = img.tag.as_dict()
            with open(new_filename[:-4] + '.json', 'w') as f:
                if img.mode == 'P':
                    # keep palette
                    tags['palette'] = img.getpalette()
                json.dump(tags, f)

            # check if image is palette-mode
            if img.mode == 'P':
                # switch to luminance to keep data intact
                debug('palette-mode switched to luminance')
                img.mode = 'L'
            if img.mode == 'I;16':
                # https://github.com/python-pillow/Pillow/issues/1099
                img = img.convert(mode='I')

            # compress/save
            debug('saving to {}'.format(new_filename))
            img.save(new_filename)
            compressed_images.append(new_filename)

            if delete_tif:
                os.remove(orig_filename)

        except (IOError, AssertionError) as e:
            # print error - continue
            print('matrixscreener {}'.format(e))

    return compressed_images



def decompress(images, delete_png=False, delete_json=False, folder=None):
    """Reverse compression from tif to png and save them in original format
    (ome.tif). TIFF-tags are gotten from json-files named the same as given
    images.


    Parameters
    ----------
    images : list of filenames
        Image to decompress.
    delete_png : bool
        Wheter to delete PNG images.
    delete_json : bool
        Wheter to delete TIFF-tags stored in json files on compress.

    Returns
    -------
    list of filenames
        List of decompressed files.
    """
    if type(images) == str:
        # only one image
        return decompress([images])

    filenames = copy(images) # as images property will change when looping

    decompressed_images = []
    for orig_filename in filenames:
        debug('decompressing {}'.format(orig_filename))
        try:
            filename, extension = os.path.splitext(orig_filename)

            # if decompressed file should be put in specified folder
            if folder:
                basename = os.path.basename(filename)
                new_filename = os.path.join(folder, basename + '.ome.tif')
            else:
                new_filename = filename + '.ome.tif'

            # check if tif exists
            if os.path.isfile(new_filename):
                decompressed_images.append(new_filename)
                msg = "Aborting decompress, TIFF already exists: {}".format(orig_filename)
                raise AssertionError(msg)
            if extension != '.png':
                msg = "Aborting decompress, not a PNG: {}".format(orig_filename)
                raise AssertionError(msg)

            # open image, load and close file pointer
            img = Image.open(orig_filename)
            img.load() # load img-data before switching mode, also closes fp

            # get tags from json
            info = {}
            with open(filename + '.json', 'r') as f:
                tags = json.load(f)
                # convert dictionary to original types (lost in json conversion)
                for tag,val in tags.items():
                    if tag == 'palette':
                        # hack hack
                        continue
                    if type(val) == list:
                        val = tuple(val)
                    if type(val[0]) == list:
                        # list of list
                        val = tuple(tuple(x) for x in val)
                    info[int(tag)] = val

            # check for color map
            if 'palette' in tags:
                img.putpalette(tags['palette'])

            # save as tif
            debug('saving to {}'.format(new_filename))
            img.save(new_filename, tiffinfo=info)
            decompressed_images.append(new_filename)

            if delete_png:
                os.remove(orig_filename)
            if delete_json:
                os.remove(filename + '.json')

        except (IOError, AssertionError) as e:
            # print error - continue
            print('matrixscreener {}'.format(e))

    return decompressed_images


def attribute(path, name):
    """Returns the two numbers found behind --[A-Z] in path. If several matches
    are found, the last one is returned.

    Parameters
    ----------
    path : string
        String with path of file/folder to get attribute from.
    name : string
        Name of attribute to get. Should be A-Z or a-z (implicit converted to
        uppercase).

    Returns
    -------
    integer
        Returns number found in path behind --name as an integer.
    """
    matches = re.findall('--' + name.upper() + '([0-9]{2})', path)
    if matches:
        return int(matches[-1])
    else:
        return None


def attribute_as_str(path, name):
    """Returns the two numbers found behind --[A-Z] in path. If several matches
    are found, the last one is returned.

    Parameters
    ----------
    path : string
        String with path of file/folder to get attribute from.
    name : string
        Name of attribute to get. Should be A-Z or a-z (implicit converted to
        uppercase).

    Returns
    -------
    string
        Returns two digit number found in path behind --name.
    """
    matches = re.findall('--' + name.upper() + '([0-9]{2})', path)
    if matches:
        return matches[-1]
    else:
        return None

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
def _pattern(*names, **kwargs):
    """Returns globbing pattern for name1/name2/../lastname + '--*' or
    name1/name2/../lastname + extension if parameter `extension` it set.

    Parameters
    ----------
    names : strings
        Which path to join. Example: _pattern('path', 'to', 'experiment') will
        return `path/to/experiment--*`.
    extension : string
        If other extension then --* is wanted.
        Example: _pattern('path', 'to', 'image', extension='*.png') will return
        `path/to/image*.png`.

    Returns
    -------
    string
        Joined glob pattern string.
    """
    if 'extension' not in kwargs:
        kwargs['extension'] = '--*'
    return os.path.join(*names) + kwargs['extension']


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
