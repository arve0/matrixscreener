# encoding: utf-8
"""
Stitch images with ImageJ.
"""
import os
from tempfile import NamedTemporaryFile

# lazy hardcode, TODO windows, linux
IMAGEJ_PATH = '/Applications/Fiji.app/Contents/MacOS/ImageJ-macosx'
DEBUG = False


def stitch_macro(folder, filenames, output_filename, x_size=5, y_size=5,
           x_start=0, y_start=0, overlap=10):
    """
    Creates a stitch macro for ImageJ with Grid/Collection stitching plugin.
    Parameters are the same as in the plugin and are described in further detail
    here: http://fiji.sc/Image_Stitching#Grid.2FCollection_Stitching.

    Default parameters:
    - Compute overlap
    - Subpixel accurancy
    - Save computation time (but use more RAM)
    - Fusion method: Linear blending
    - Regression threshold: 0.30
    - Max/avg displacement threshold: 2.50
    - Absolute displacement threshold: 3.50


    Parameters
    ----------
    folder: string
        Folder to find images. Example: /path/to/slide--S00/chamber--U01--V02/
    filenames: string
        Filenames of images. Example: field-X{xx}-Y{yy}/image-X{xx}-Y{yy}.ome.tif
    output_filename: string
        Filename of fused image.
    x_size, y_size: int
        Number of images in x and y direction.
    x_start, y_start:
        Which number to start with.
    overlap:
        Amount of overlap in images.

    Returns
    -------
    String with macro.
    """

    macro = []
    macro.append('run("Grid/Collection stitching",')
    macro.append('"type=[Filename defined position]')
    macro.append('order=[Defined by filename         ]')
    macro.append('grid_size_x={}'.format(x_size))
    macro.append('grid_size_y={}'.format(y_size))
    macro.append('tile_overlap={}'.format(overlap))
    macro.append('first_file_index_x={}'.format(x_start))
    macro.append('first_file_index_y={}'.format(y_start))
    macro.append('directory=[{}]'.format(folder))
    macro.append('file_names={}'.format(filenames))
    macro.append('output_textfile_name=TileConfiguration.txt')
    macro.append('fusion_method=[Linear Blending]')
    macro.append('regression_threshold=0.30')
    macro.append('max/avg_displacement_threshold=2.50')
    macro.append('absolute_displacement_threshold=3.50')
    macro.append('compute_overlap')
    macro.append('subpixel_accuracy')
    macro.append('computation_parameters=[Save computation time (but use more RAM)]')
    # use display, such that we can specify output filename
    macro.append('image_output=[Fused and display]");')
    macro.append('selectWindow("Fused");')
    macro.append('run("Save", "save=[{}]");'.format(output_filename))
    macro.append('close();')

    return ' '.join(macro)


def run_imagej(macro):
    """
    Runs ImageJ with the suplied macro.

    Parameters
    ----------
    macro: string
        Macro to send to ImageJ.

    Returns
    -------
    Exit code to ImageJ.
    """
    with NamedTemporaryFile(mode='w', suffix='.ijm') as m:
        m.write(macro)
        m.flush() # make sure macro is written before running ImageJ
        if DEBUG:
            cmd = IMAGEJ_PATH + ' --headless {}'.format(m.name)
        else:
            cmd = IMAGEJ_PATH + ' --headless {} >> /dev/null 2>&1'.format(m.name)
        exit_code = os.system(cmd)

    if exit_code != 0:
        msg = 'ERROR: ImageJ did not exit correctly, exit code {}.'.format(exit_code)
        if not DEBUG:
            msg += '\nTry using matrixscreener.imagej.DEBUG = True'
        print(msg)

    return exit_code
