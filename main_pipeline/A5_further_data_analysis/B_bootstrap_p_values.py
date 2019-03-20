import os
from os.path import join as jph


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

