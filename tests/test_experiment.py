import pytest

@pytest.fixture(scope='session')
def experiment():
    import matrixscreener
    from os import path
    
    folder = path.join(path.dirname(__file__), 'experiment--test')
    return matrixscreener.Experiment(folder)


def test_stitch(tmpdir, experiment):
    "It should stitch images without error."
    well = experiment.wells[0]
    well.stitch(tmpdir.strpath)

    # both channels stitched
    assert len(tmpdir.listdir()) == 2


def test_looping(experiment):
    for well in experiment.wells:
        for field in well.fields:
            for image in field.images:
                assert image.filename
