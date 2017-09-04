import os
from os.path import join as jph

# plotting stuff:
import numpy as np
import matplotlib
from matplotlib.patches import Circle, Wedge, Polygon
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt

import pandas as pd

from a_experiments.distances_between_segmentations_computations import modalities
from a_experiments.distances_between_segmentations_paths import pfo_manual, pfo_study, pfo_automatic, pfo_output


for mod in modalities:
    print '\n\n\n--------------------------'
    print 'Analysis {}'.format(mod)
    print '--------------------------\n'

    pfi_automatic_MV = jph(pfo_automatic, 'target1111_T1_segm_{}.nii.gz'.format(mod))
    pfi_manual_1 = jph(pfo_manual, '1111_approved.nii.gz')

    where_have_been_saved = jph(pfo_output, 'distances_approved_{}.pickle'.format(mod))

    num_fig = 1
    title = 'tri-metric'

    fig = plt.figure(num_fig, figsize=(6, 7.5), dpi=100)
    ax = fig.add_subplot(111)
    ax.set_position([0.1, 0.29, 0.8, 0.7])

    fig.canvas.set_window_title(title)

    if os.path.exists(where_have_been_saved):
        df = pd.read_pickle(where_have_been_saved)
        for dist in ('dice score', 'dispersion'):  # 'precision'
            print dist, df[dist]['means'], df[dist]['std']
        print 'precision', 1.0, 0.1

        dice = (df['dice score']['means'], df['dice score']['std'])
        prec = (1.0, 0.1)
        disp = (df['dispersion']['means'], df['dice score']['std'])





    else:
        print('File {} not (yet) present.'.format(where_have_been_saved))
