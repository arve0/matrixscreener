#!/usr/bin/env python
# encoding: utf-8
"""
Class Experiment(path) to organize matrix scans from Leica LAS MatrixScreener (data explorer's ome.tif).
"""
# format https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt

# libaries
import os, glob, tifffile, numpy

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
        self.str_u, self.str_v = u, v
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


    def stitch(self, z_stack=0, channel=0, overlap=None):
        """Merge images from specified z-stack.

        Parameters
        ----------
        z-stack: int
            Which Z-stack to stitch.
        channel: int
            Which channel to stitch.
        overlap: float
            If images should be cut when stitched.

        Returns
        -------
        ndarray of stitched image.
        """
        if z_stack >= self.z_stacks or channel >= self.channels:
            return None

        # filter out the images we want
        images = [image for field in self.fields
                        for image in field.images
                            if image.z == z_stack and
                               image.channel == channel]

        # create empty array for stiched image
        y = images[0].shape[0]
        x = images[0].shape[1]
        shape = (self.fields_y * y, self.fields_x * x)
        stitched_image = numpy.zeros(shape, dtype=numpy.uint8) # TODO do not hard code type

        # stitch images
        for image in images:
            start_y = image.y * y
            start_x = image.x * x
            stop_y = start_y + y
            stop_x = start_x + x
            image_data = tifffile.imread(image.fullpath, key=0)
            image_data = numpy.rot90(image_data, k=3)
            # TODO: possible to detect rotation?
            stitched_image[start_y:stop_y, start_x:stop_x] = image_data

        return stitched_image



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
def main():
    #TODO
    """Run when executed as script."""

    path = raw_input('What directory is the files in (relative or absolute)?\n')
    # set as working directory, instead of concatenate path + filename
    os.chdir(path)
    files = os.listdir('.')
    print('First file: ' + files[0])
    try:
        y_size = getYSize(files)
    except Exception:
        print('Error: Files in right format?')
        exit(1)
    print('Y size: ' + str(y_size))
    if raw_input('Seems right? Continue? (y/n) ').lower() == 'y':
        for f in files:
            x = getX(f)
            r = x * y_size + getY(f)
            ch = 'ch' + str(getChannel(f)) + '-'
            new_name = ch + str(r) + '.tif'
            os.rename(f, new_name)
            print('Renaming ' + f + ' to ' + new_name)



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



if __name__ == '__main__':
    main()
