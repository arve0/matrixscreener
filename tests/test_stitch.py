import matrixscreener
from os import path



def test_stitch(tmpdir):
    "It should stitch images without error."
    folder = path.join(path.dirname(__file__), 'experiment--test')

    experiment = matrixscreener.Experiment(folder)
    well = experiment.wells[0]
    well.stitch(tmpdir.strpath)

    # both channels stitched
    assert len(tmpdir.listdir()) == 2
