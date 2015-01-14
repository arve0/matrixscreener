"""
Read and stitch ome.tifs from Leica LAS AF MatrixScreener Data Exporter.
"""
from .experiment import Experiment
from .cam import *

VERSION = '0.2.1'

__all__ = [ 'Experiment',
            'CAM',
            'tuples_as_bytes',
            'tuples_as_dict',
            'bytes_as_dict' ]
