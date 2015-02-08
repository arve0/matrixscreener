import pytest
from py import path

@pytest.fixture
def experiment(tmpdir):
    "'experiment--test' in tmpdir. Returns Experiment object."
    from matrixscreener.experiment import Experiment
    e = path.local(__file__).dirpath().join('experiment--test')
    e.copy(tmpdir.mkdir('experiment'))

    return Experiment(tmpdir.join('experiment').strpath)


@pytest.fixture
def ometif16bit(tmpdir):
    "16 bit ome.tif image in tmpdir. Returns py.path.local object of image."
    image = path.local(__file__).dirpath().join('images', '16bit.ome.tif')
    image.copy(tmpdir)

    return tmpdir.join(image.basename)


def test_stitching(tmpdir, experiment):
    "It should stitch images without error."
    files = experiment.stitch(tmpdir.mkdir('stitched').strpath)

    # returned files same as output
    assert files == tmpdir.join('stitched').listdir(sort=True)
    # both channels stitched
    assert len(files) == 2


def test_looping(experiment):
    "It should be able to loop through wells, fields and images."
    for well in experiment.wells:
        assert type(well) == str
    for field in experiment.fields:
        assert type(field) == str
    for image in experiment.images:
        assert type(image) == str


def test_compression(tmpdir, experiment):
    "It should compress and decompress experiment without dataloss."
    from matrixscreener.experiment import decompress
    from PIL import Image
    import numpy as np

    # compress
    pngs = experiment.compress(folder=tmpdir.mkdir('pngs').strpath)

    # reported output is actually written and the same amount
    assert pngs == tmpdir.join('pngs').listdir('*.png', sort=True)
    assert len(pngs) == len(experiment.images)

    # keep data for decompress test
    origs = []
    orig_tags = []

    # check that compression is lossless
    for tif,png in zip(experiment.images, pngs):
        img = Image.open(tif)
        orig = np.array(img)
        origs.append(orig)
        orig_tags.append(img.tag.as_dict())
        compressed = np.array(Image.open(png))

        # is lossless?
        assert np.all(orig == compressed)

    new_tifs = decompress(pngs, folder=tmpdir.mkdir('new_tifs').strpath)

    # reported output is actually written and the same amount as original
    assert new_tifs == tmpdir.join('new_tifs').listdir(sort=True)
    assert len(new_tifs) == len(experiment.images)

    # orig and decompressed images have similar file size
    for orig,new_tif in zip(experiment.images, new_tifs):
        diff = abs(path.local(orig).size() - path.local(new_tif).size())
        assert diff < 1024

    omit_tags = [273, 278, 279]
    # check that decompression is lossless
    for tif,orig,orig_tag in zip(new_tifs, origs, orig_tags):
        img = Image.open(tif)
        decompressed = np.array(img)

        # compress->decompress is lossless?
        assert np.all(orig == decompressed)

        # check if TIFF-tags are intact
        tag = img.tag.as_dict()
        for omit in omit_tags:
            del tag[omit]
            del orig_tag[omit]
        assert tag == orig_tag


def test_stitch_png(tmpdir, experiment):
    "It should stitch compressed images."
    experiment.compress(delete_tif=True)
    files = experiment.stitch(folder=tmpdir.mkdir('stitched').strpath)

    # returned files same as output
    assert files == tmpdir.join('stitched').listdir(sort=True)
    # both channels stitched
    assert len(files) == 2


def test_16bit(ometif16bit):
    "It should compress and decompress 16 bit TIFF without dataloss."
    from matrixscreener.experiment import compress
    from PIL import Image
    import numpy as np

    tif = ometif16bit.strpath
    png = compress(tif)[0]

    tif_data = np.array(Image.open(tif))
    png_data = np.array(Image.open(png))

    assert np.all(tif_data == png_data)
