from matrixscreener import *

def test_import_all():
    "global import * should import cam, experiment and imagej"
    assert 'cam' in globals()
    assert 'experiment' in globals()
    assert 'imagej' in globals()

def test_module_has_attr():
    "import matrixscreener should import submodules"
    import matrixscreener
    assert hasattr(matrixscreener, 'cam')
    assert hasattr(matrixscreener, 'experiment')
    assert hasattr(matrixscreener, 'imagej')
