# encoding: utf-8
"""
Access matrix scans from Leica LAS AF MatrixScreener (Data Explorer)
through an object.
"""
# doc-format https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt

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
class Experiment:
    def __init__(self, path):
        """Leica LAS AF MatrixScreener experiment.

        Parameters
        ----------
        path : string
            Path to matrix scan containing 'slide-S00'(assumed) and 'AdditinalData'.

        Raises
        ------
        FileNotFoundError
            If *slide--S00* isn't found.

        Attributes
        ----------
        path : string
            Path to experiment.
        slide_path : string
            Path to *experiment/slide--S00*
        wells : list
            List of *matrixscreener.experiment._Well* objects.
        wells_u, wells_v : int
            Number of wells in u and v direction.
        """
        assumed_slide = 'slide--S00'
        self.path = os.path.abspath(path)
        self.slide_path = os.path.join(self.path, assumed_slide)

        # number of wells in U(x), V(y) direction
        chambers = glob.glob(self.slide_path + '/chamber--*')
        if len(chambers) == 0:
            raise FileNotFoundError
        last_chamber = chambers[-1]
        u, v = last_chamber.split('--U')[1].split('--V')
        self.wells_u = int(u) + 1 # directory string start at 0
        self.wells_v = int(v) + 1

        # check number of chambers
        if len(chambers) != self.wells_u * self.wells_v:
            print('Warning: Did scan complete? ' +
                  'Number of chambers != wells_u * wells_v in ' + self.path)

        # add wells (assume slide--S00)
        self.wells = []
        for chamber in chambers:
            p = os.path.join(self.slide_path, chamber)
            self.wells.append(_Well(p))


    def __str__(self):
        return 'matrixscreener.Experiment at path {}'.format(self.path)


    def stitch(self, folder=None):
        """
        Stitches all wells in experiment. Stitched images are saved in
        experiment root.

        Images which already exists are omitted from ImageJ stitching.

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
            output_files.extend(well.stitch(folder))

        return output_files



class _Well:
    def __init__(self, path):
        """Well of Leica matrix experiment.

        Provides
        --------
        channels : int
        fields : list
        fields_x, fields_y : int
        u, v : int
        z_stacks : int

        Parameters
        ----------
        path : string
            Path to 'chamber--UXX-VXX' containing field folders
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
        self.fields_x = int(x) + 1 # directory string start at 0
        self.fields_y = int(y) + 1

        # check number of fields
        if len(fields) != self.fields_x * self.fields_y:
            print('Warning: Did scan complete? Number of fields != fields_x * fields_y in ' + self.path)

        # add fields
        self.fields = []
        for field in fields:
            p = os.path.join(self.path, field)
            self.fields.append(_Field(p))

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
        list
            Filenames for stitched images.
        """
        if folder is None:
            folder = self.path

        # create macro
        macro = []
        output_files = []
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
                output_files.append(output)
                if os.path.isfile(output):
                    # file already exists
                    continue
                macro.append(stitch_macro(self.path, filenames, output, self.fields_x, self.fields_y))

        # stitch images with ImageJ
        if len(macro) != 0:
            run_imagej(' '.join(macro))

        # remove files which are not created
        output_files = [filename for filename in output_files
                            if os.path.isfile(filename)]

        return output_files



class _Field:
    def __init__(self, path):
        """Field of Leica matrix experiment.

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
        last_z_stack = _between('--Z', '--', last_image)
        self.z_stacks = int(last_z_stack) + 1
        # number of channels
        last_channel = _between('--C', '.ome.tif', last_image)
        self.channels = int(last_channel) + 1

        # add images
        self.images = []
        for image in images:
            f = os.path.join(self.path, image)
            self.images.append(_Image(f))



class _Image:
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
        """
        self.fullpath = filename
        self.filename = os.path.basename(filename)
        self.path = os.path.dirname(filename)

        u = _between('--U', '--', self.filename)
        v = _between('--V', '--', self.filename)
        self.u = int(u)
        self.v = int(v)

        x = _between('--X', '--', self.filename)
        y = _between('--Y', '--', self.filename)
        z = _between('--Z', '--', self.filename)
        self.x = int(x)
        self.y = int(y)
        self.z = int(z)

        channel = _between('--C', '.ome.tif', self.filename)
        self.channel = int(channel)

        # image properties, xml
        page = tifffile.TIFFfile(filename).pages[0]
        self.shape = page.shape
        self.xml = page.tags['image_description'].value


    def __str__(self):
        return '{}, z:{}, channel:{}'.format(self.filename, self.z, self.channel)




# functions
def _between(before, after, string):
    """Strip string and return whats between before and after.

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
    string
        String between before and after.
    """
    return string.split(before)[1].split(after)[0]
