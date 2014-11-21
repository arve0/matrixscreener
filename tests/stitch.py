import matrixscreener

print('matrixscreener version {}'.format(matrixscreener.VERSION))

experiment = matrixscreener.Experiment('experiment--test')
well = experiment.wells[0]

matrixscreener.imagej.DEBUG = True # turn on output from ImageJ

well.stitch('.')
