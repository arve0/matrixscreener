#!/usr/bin/env python
# encoding: utf-8

# readme
import os
if os.path.exists('README.rst'):
    long_description = open('README.rst').read()
else:
    long_description = ''

from setuptools import setup

setup(name='matrixscreener',
      version='0.4.2',
      description='Python API for Leica LAS AF MatrixScreener',
      author='Arve Seljebu',
      author_email='arve.seljebu@gmail.com',
      license='MIT',
      url='https://github.com/arve0/matrixscreener',
      packages=['matrixscreener'],
      install_requires=['pydebug', 'Pillow', 'fijibin'],
      long_description=long_description)
