import pytest

@pytest.fixture(scope='session')
def experiment():
    from matrixscreener.experiment import Experiment
    from os import path

    folder = path.join(path.dirname(__file__), 'experiment--test')
    return Experiment(folder)


def test_stitch(tmpdir, experiment):
    "It should stitch images without error."
    files = experiment.stitch(tmpdir.strpath)

    # both channels stitched
    assert files == tmpdir.listdir()


def test_looping(experiment):
    "It should be able to loop through wells, fields and images."
    for well in experiment.wells:
        assert type(well) == str
    for field in experiment.fields:
        assert type(field) == str
    for image in experiment.images:
        assert type(image) == str

def test_compression(experiment):
    "It should compress and decompress experiment without dataloss."
    import matrixscreener as ms
    from PIL import Image
    import numpy as np
    from copy import copy
    from tempfile import TemporaryDirectory
    from os import path, replace

    # make a copy of filenames for easier looping
    tifs = copy(experiment.images)
    pngs = ms.experiment.compress(experiment.images)

    with TemporaryDirectory() as tmp:
        origs = [] # keep data for decompress test

        # check that compression is lossless
        for i,(tif,png) in enumerate(zip(tifs, pngs)):
            origs.append(np.array(Image.open(tif)))
            compressed = np.array(Image.open(png))

            # move tifs to tmp directory
            basename = path.basename(tif)
            replace(tif, path.join(tmp, basename))

            # print some debugging
            print('check if png image data is identical ' + basename)
            assert np.all(origs[i] == compressed)

        # we are finished with pngs -> delete them on decompress
        ms.experiment.decompress(experiment.images,
                                 delete_png=True, delete_json=True)

        # check that decompression is lossless
        for tif,orig in zip(tifs, origs):
            decompressed = np.array(Image.open(tif))
            assert np.all(orig == decompressed)
            # move back
            basename = path.basename(tif)
            print('move back image ' + basename)
            replace(path.join(tmp, basename), tif)
