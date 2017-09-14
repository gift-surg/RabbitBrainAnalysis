import os
from os.path import join as jph

# plotting stuff:
import numpy as np
import matplotlib
from matplotlib.patches import Circle, Wedge, Rectangle
from matplotlib.collections import PatchCollection
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm

import pandas as pd

from a_experiments.distances_between_segmentations_computations import modalities
from a_experiments.distances_between_segmentations_paths import pfo_manual, pfo_study, pfo_automatic, pfo_output


# module to be integrated in labels_manager.viewer

''' Data for Plottings '''

dist_keys = ('precision', 'dice score', 'dispersion')  # ordere x, y, radius

mods = ['MV_s', 'STAPLE_pr_1_s', 'STEPS_pr_1_s', 'STEPS_pr_2_s', 'STEPS_pr_3_s_smol05', 'STEPS_pr_3_s_smol10',
              'STEPS_pr_3_s', 'STEPS_pr_4_s', 'STEPS_pr_5_s']
colors = cm.rainbow(np.linspace(0, 1, len(mods)))

''' Tri metric plot '''

num_fig = 1
title = 'tri-metric'

r_std_scaling_factor = 0.1

fig = plt.figure(num_fig, figsize=(10, 8), dpi=100)
fig.canvas.set_window_title(title)

ax = fig.add_subplot(111)
ax.set_position([0.1, 0.1, 0.8, 0.8])
ax.grid()

for mod, col in zip(mods, colors):
    print '\n\n\n--------------------------'
    print 'Analysis {}'.format(mod)
    print '--------------------------\n'

    pfi_automatic_MV = jph(pfo_automatic, 'target1111_T1_segm_{}.nii.gz'.format(mod))
    pfi_manual_1 = jph(pfo_manual, '1111_approved.nii.gz')

    where_have_been_saved = jph(pfo_output, 'distances_approved_{}.pickle'.format(mod))

    # ----
    if os.path.exists(where_have_been_saved):
        df = pd.read_pickle(where_have_been_saved)
        for dist in dist_keys:
            print dist, df[dist]['mean'], df[dist]['std']

        # grab variables from pandas df, critical as means and std needs to be in the row data frames:
        x_mu, x_std = df[dist_keys[0]]['mean'], df[dist_keys[0]]['std']
        y_mu, y_std = df[dist_keys[1]]['mean'], df[dist_keys[1]]['std']
        r_mu, r_std = df[dist_keys[2]]['mean'], df[dist_keys[2]]['std'] * r_std_scaling_factor

        # central point:
        centre_data = (x_mu, y_mu)

        # square_background and error cross
        # p_prec_dice_error = Rectangle((x_mu - x_std, y_mu - y_std), 2 * x_std, 2 * y_std, facecolor='r', alpha=0.5)

        # dispersion
        p_disp_circle = Circle(centre_data, r_mu, color=col, fill=False)

        # dispersion error
        p_disp_error = Wedge(centre_data, r_mu + (r_std / 2.), 0, 360, width=r_std, alpha=0.2, color=col)

        for p in [p_disp_circle, p_disp_error]:
            print ax.add_patch(p)

        # add cross error-bar in the center
        ax.errorbar(x_mu, y_mu, xerr=x_std, yerr=y_std, color=col, label=mod)
        ax.legend()
        ax.set_xlabel(dist_keys[0])
        ax.set_ylabel(dist_keys[1])
        ax.set_aspect('equal', 'datalim')
        ax.set_title('Tri-metric : {}'.format(str(dist_keys)))

    else:
        print('File {} not (yet) present.'.format(where_have_been_saved))

plt.show(block=False)


''' boxplot - '''

num_fig = 2
title = 'dice score - precision - dispersion'

fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(12, 5))
plt.subplots_adjust(left=0.075, right=0.95, top=0.9, bottom=0.25)
fig.canvas.set_window_title(title)

for axis_id, distance in enumerate(dist_keys):

    scores_per_mod = []
    for mod in mods:

        where_have_been_saved = jph(pfo_output, 'distances_approved_{}.pickle'.format(mod))

        df = pd.read_pickle(where_have_been_saved)
        df_new = df.drop(['mean', 'std'])

        scores_per_mod.append(df_new[distance].values)

    bplot = axes[axis_id].boxplot(scores_per_mod, patch_artist=True)
    for patch, color in zip(bplot['boxes'], colors):
        patch.set_facecolor(color)
    axes[axis_id].grid()
    axes[axis_id].set_title(distance)
    axes[axis_id].set_ylabel(distance)

xtickNames = plt.setp(axes, xticklabels=mods)
plt.setp(xtickNames, rotation=90, fontsize=8)

plt.show(block=False)
