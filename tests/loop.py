from matrixscreener import Experiment
experiment = Experiment('experiment--test')
for well in experiment.wells:
    for field in well.fields:
        for image in field.images:
            print('image {}'.format(image.filename))
