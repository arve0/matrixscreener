# encoding: utf-8
"""
Class Experiment(path) to organize matrix scans from Leica LAS MatrixScreener (data explorer's ome.tif).
"""
# format https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt

# libaries
import os, glob, tifffile, numpy
from .imagej import stitch_macro, run_imagej

## notes
#
# - one z-plane at the time
# - put this in docstring when done
#
#
#

# classes
class Experiment(object):
    def __init__(self, path):
        """Leica LAS matrixscreener scan job.

        Parameters
        ----------
        path: string
            Path to matrix scan containing 'slide-S00'(assumed) and 'AdditinalData'.

        Raises
        ------
        FileNotFoundError:
            If slide--S00 is not found.

        Returns
        -------
        None
        """
        assumed_slide = 'slide--S00'
        self.path = os.path.abspath(path)
        self.slide_path = os.path.join(self.path, assumed_slide)
        self.str_time = self.path.split('experiment--')[1]

        # number of wells in U(x), V(y) direction
        chambers = glob.glob(self.slide_path + '/chamber--*')
        if len(chambers) == 0:
            raise FileNotFoundError
        last_chamber = chambers[-1]
        u, v = last_chamber.split('--U')[1].split('--V')
        self.last_well_u = u # string of last u,v
        self.last_well_v = v
        self.wells_u = int(u) + 1 # directory string start at 0
        self.wells_v = int(v) + 1

        # check number of chambers
        if len(chambers) != self.wells_u * self.wells_v:
            print('Warning: Did scan complete? Number of chambers != wells_u * wells_v in ' + self.path)

        # add wells (assume slide--S00)
        self.wells = []
        for chamber in chambers:
            p = os.path.join(self.slide_path, chamber)
            self.wells.append(Well(p))


    def __str__(self):
        return 'leicaexperiment at path {}'.format(self.path)


    def stitch(self):
        """
        Stitches all wells in experiement and save them in experiment root.
        """
        for well in self.wells:
            well.stitch(self.path)



class Well(object):
    def __init__(self, path):
        """Well of Leica matrix scan.

        Parameters
        ----------
        path: string
            Path to 'chamber--UXX-VXX' containing field folders

        Returns
        -------
        None
        """
        self.path = path

        # setup position - U(x) and V(y)
        u, v = self.path.split('--U')[1].split('--V')
        self.u = int(u)
        self.v = int(v)

        # find number of fields
        fields = glob.glob(self.path + '/field--*')
        if len(fields) == 0:
            raise FileNotFoundError
        last_field = fields[-1]
        x, y = last_field.split('--X')[1].split('--Y')
        self.last_field_x = x # string of last x,y
        self.last_wells_y = y
        self.fields_x = int(x) + 1 # directory string start at 0
        self.fields_y = int(y) + 1

        # check number of fields
        if len(fields) != self.fields_x * self.fields_y:
            print('Warning: Did scan complete? Number of fields != fields_x * fields_y in ' + self.path)

        # add fields
        self.fields = []
        for field in fields:
            p = os.path.join(self.path, field)
            self.fields.append(Field(p))

        # z-stacks, assume they are the same for all fields
        self.z_stacks = self.fields[0].z_stacks
        self.channels = self.fields[0].channels


    def stitch(self, folder=None):
        """Stitch all z-stacks and channels in well.

        Parameters
        ----------
        folder: string
            Folder to store images. Default is well.path.

        Returns
        -------
        Exit code from ImageJ.
        """
        if folder is None:
            folder = self.path

        # create macro
        macro = []
        for z in range(self.z_stacks):
            for ch in range(self.channels):
                filenames = ('field--X{xx}--Y{yy}/' +
                        'image--L00--S00--U{:02}'.format(self.u) +
                        '--V{:02}'.format(self.v) +
                        '--J20--E00--O00--X{xx}--Y{yy}--T00' +
                        '--Z{:02}'.format(z) +
                        '--C{:02}'.format(ch) +
                        '.ome.tif')
                filename = 'u{}v{}ch{}z{}.tif'.format(self.u, self.v, ch, z)
                output = os.path.join(folder, filename)
                macro.append(stitch_macro(self.path, filenames, output))

        # stitch images with ImageJ
        exit_code = run_imagej(' '.join(macro))

        return exit_code



class Field(object):
    def __init__(self, path):
        """Field of Leica matrix scan.

        Provides
        --------
        channels:
        images:
        path:
        str_x, str_y, str_z_stacks:
        x, y:
        z_stacks:

        Parameters
        ----------
        path: string
            Path to 'field--Xnn-Ynn' containing image...ome.tifs

        Returns
        -------
        None
        """
        self.path = path

        # setup x and y properties to field
        x, y = path.split('--X')[1].split('--Y')
        self.str_x, self.str_y = x, y
        self.x = int(x)
        self.y = int(y)

        # find number of z scans
        images = glob.glob(self.path + '/image--*.ome.tif')
        last_image = images[-1]
        last_z_stack = between('--Z', '--', last_image)
        self.str_z_stacks = last_z_stack
        self.z_stacks = int(last_z_stack) + 1
        # number of channels
        last_channel = between('--C', '.ome.tif', last_image)
        self.str_channels = last_channel
        self.channels = int(last_channel) + 1

        # add images
        self.images = []
        for image in images:
            f = os.path.join(self.path, image)
            self.images.append(Image(f))



class Image():
    def __init__(self, filename):
        """OME-TIFF image.

        Provides TODO:description
        --------
        channel:
        filename:
        fullpath:
        path:
        u,v:
        x,y,z:
        xml:

        Parameters
        ----------
        filename:
            Complete filename including path to image...ome.tif

        Returns
        -------
        None
        """
        self.fullpath = filename
        self.filename = os.path.basename(filename)
        self.path = os.path.dirname(filename)

        u = between('--U', '--', self.filename)
        v = between('--V', '--', self.filename)
        self.u = int(u)
        self.v = int(v)

        x = between('--X', '--', self.filename)
        y = between('--Y', '--', self.filename)
        z = between('--Z', '--', self.filename)
        self.x = int(x)
        self.y = int(y)
        self.z = int(z)

        channel = between('--C', '.ome.tif', self.filename)
        self.channel = int(channel)

        # image properties, xml
        page = tifffile.TIFFfile(filename).pages[0]
        self.shape = page.shape
        self.xml = page.tags['image_description'].value


    def __str__(self):
        return '{}, z:{}, channel:{}'.format(self.filename, self.z, self.channel)




# functions
def between(before, after, string):
    """Strip string and return whats between before and after.

    Parameters
    ----------
    before:
        String to match before wanted portion
    after:
        String to match after wanted portion
    string:
        String to parse

    Returns
    -------
    String between before and after.
    """
    return string.split(before)[1].split(after)[0]
