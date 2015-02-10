# encoding: utf-8
"""
Stitch images with ImageJ.

* ``matrixscreener.imagej._bin`` should be set if you are on Windows or Linux.
"""
import pydebug, subprocess, os, fijibin
from tempfile import NamedTemporaryFile

# debug with DEBUG=matrixscreener python script.py
debug = pydebug.debug('matrixscreener')

_bin = fijibin.BIN

def stitch_macro(folder, filenames, x_size, y_size, output_filename,
                 x_start=0, y_start=0, overlap=10):
    """
    Creates a ImageJ Grid/Collection stitching macro. Parameters are the same as
    in the plugin and are described in further detail here:
    http://fiji.sc/Image_Stitching#Grid.2FCollection_Stitching.

    **Default stitch parameters:**

    * Filename defined positions
    * Compute overlap
    * Subpixel accurancy
    * Save computation time (but use more RAM)
    * Fusion method: Linear blending
    * Regression threshold: 0.30
    * Max/avg displacement threshold: 2.50
    * Absolute displacement threshold: 3.50


    Parameters
    ----------
    folder : string
        Path to folder with images or folders with images.
        Example: */path/to/slide--S00/chamber--U01--V02/*
    filenames : string
        Filenames of images.
        Example: *field-X{xx}-Y{yy}/image-X{xx}-Y{yy}.ome.tif*
    x_size : int
        Size of grid, number of images in x direction.
    y_size : int
        Size of grid, number of images in y direction.
    output_filename : string
        Where to store fused image. Should be `.png`.
    x_start : int
        Which x position grid start with.
    y_start : int
        Which y position grid start with.
    overlap : number
        Tile overlap in percent. ImageJ will find the optimal overlap, but a
        precise overlap assumption will decrase computation time.

    Returns
    -------
    string
        IJM-macro.
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
    # this is 'Fused and display' for previous stitching version!!
    macro.append('image_output=[Fuse and display]");')
    # save to png
    macro.append('selectWindow("Fused");')
    macro.append('run("PNG ...", "save=[{}]'.format(output_filename))
    macro.append('imageiosaveas.codecname=png')
    macro.append('imageiosaveas.filename=[{}]");'.format(output_filename))
    macro.append('close();')

    return ' '.join(macro)


def run_imagej(macro):
    """
    Runs ImageJ with the suplied macro. Output of ImageJ can be viewed by
    running python script with environment variable DEBUG=matrixscreener.

    Parameters
    ----------
    macro : string
        IJM-macro to run.

    Returns
    -------
    int
        ImageJ exit code.
    """
    # avoid verbose output of ImageJ when DEBUG environment variable set
    env = os.environ.copy()
    debugging = False
    if 'DEBUG' in env:
        if env['DEBUG'] == 'matrixscreener' or env['DEBUG'] == '*':
            debugging = True
        del env['DEBUG']

    with NamedTemporaryFile(mode='w', suffix='.ijm') as m:
        m.write(macro)
        m.flush() # make sure macro is written before running ImageJ

        cmd = [_bin, '--headless', '-macro', m.name]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, env=env)
        out, err = proc.communicate()

        for line in out.decode('latin1', errors='ignore').splitlines():
            debug('stdout:' + line)
        for line in err.decode('latin1', errors='ignore').splitlines():
            debug('stderr:' + line)

    if proc.returncode != 0 and not debugging:
        print('matrixscreener ERROR: ImageJ exited with code {}.'.format(proc.returncode))
        print('matrixscreener Try running script with `DEBUG=matrixscreener python script.py`')

    return proc.returncode
