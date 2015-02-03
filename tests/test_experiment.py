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
