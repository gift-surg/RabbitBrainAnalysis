import os
from os.path import join as jph
from scipy.stats import norm

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

if __name__ == '__main__':

    pfo_data = '/Users/sebastiano/a_data/TData/rabbits'

    # Data-frames:
    pfi_df_volume_bup            = jph(pfo_data, 'df_volumes.csv')
    pfi_df_volume_per_region_bup = jph(pfo_data, 'df_volumes_per_region.csv')
    pfi_df_FA_per_region_bup     = jph(pfo_data, 'df_FA_per_region.csv')
    pfi_df_MD_per_region_bup     = jph(pfo_data, 'df_MD_per_region.csv')

    for ph in [pfi_df_volume_bup, pfi_df_volume_per_region_bup, pfi_df_FA_per_region_bup, pfi_df_MD_per_region_bup]:
        assert os.path.exists(ph), ph

    list_regions = ['Hippocampus',
                    'Caudate nucleus',
                    'Putamen',
                    'Thalamus',
                    'Hypothalamus',
                    'Corpus Callosum',
                    'Internal capsule',
                    'Claustrum',
                    'Amygdala']


    # create an histogram

    x = np.random.normal(size=1000)
    mu, sigma = norm.fit(x)
    observed = 1.4

    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=[5, 3], dpi=200)

    fig.canvas.set_window_title('test fitting normal')

    sns.distplot(x, fit=norm, ax=ax, kde=False)

    y_lim_low, y_lim_high = ax.get_ylim()

    ax.plot([2.8, 2.8], [y_lim_low, y_lim_high], color='r')

    sns.plt.show()