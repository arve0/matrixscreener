#!/usr/bin/env python
# encoding: utf-8

from setuptools import setup, find_packages

setup(name='LeicaExperiment',
      version='0.1.0',
      description='Class based approach to reading ome.tifs from Leica LAS Matrix Screener',
      author='Arve Seljebu',
      author_email='arve.seljebu@gmail.com',
      license='MIT',
      url='https://github.com/arve0/leicaexperiment',
      py_modules=['leicaexperiment'],
      install_requires=['tifffile', 'numpy'])
