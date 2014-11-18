#!/usr/bin/env python
# encoding: utf-8
"""
Example of how to use LeicaExperiment.
"""

from glob import glob
from tifffile import imsave, imshow
from leicaexperiment import Experiment

# get file names
experiments = glob('/path/to/experiment--*')

# create experiments in a list
leica_experiments = []
for e in experiments:
    leica_experiments.append(Experiment(e))

# merge and invert
for experiment in leica_experiments:
    well = experiment.wells[0] # assume only one well
    for channel in range(well.channels):
        for z in range(well.z_stacks):
            # print what we're doing
            output = { 't': experiment.str_time,
                       'ch': channel,
                       'z': z }
            print('Merging experiment {t} channel {ch} z-stack {z}'.format(output))
            # merge the specified z-stack
            img = well.merge(z, channel)
            # save image
            filename = (experiment.path.replace('experiment--', 'merged/') +
                        'ch' + str(channel) + 'z' + str(z) + '.tif')
            imsave(filename, img)
            # invert and save
            print('Inverting...')
            img = 255-img
            filename = (experiment.path.replace('experiment--', 'inverted/') +
                        'ch' + str(channel) + 'z' + str(z) + '.tif')
            imsave(filename, img)
