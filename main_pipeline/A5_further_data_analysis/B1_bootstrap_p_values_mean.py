import os
from os.path import join as jph
import pandas as pd
import numpy as np


if __name__ == '__main__':

    pfo_data = '/Users/sebastiano/a_data/TData/rabbits'

    # Path input data-frames:
    pfi_df_volume_bup            = jph(pfo_data, 'df_volumes.csv')
    pfi_df_volume_per_region_bup = jph(pfo_data, 'df_volumes_per_region.csv')
    pfi_df_FA_per_region_bup     = jph(pfo_data, 'df_FA_per_region.csv')
    pfi_df_MD_per_region_bup     = jph(pfo_data, 'df_MD_per_region.csv')

    for ph in [pfi_df_volume_bup, pfi_df_volume_per_region_bup, pfi_df_FA_per_region_bup, pfi_df_MD_per_region_bup]:
        assert os.path.exists(ph), ph

    # Parameters

    num_boostraps = 1000

    list_regions = ['Hippocampus',
                    'Caudate nucleus',
                    'Putamen',
                    'Thalamus',
                    'Hypothalamus',
                    'Corpus Callosum',
                    'Internal capsule',
                    'Claustrum',
                    'Amygdala']

    controller = {'bootstrap_volumes'        : True,
                  'bootstrap_volumes_regions': False,
                  'boostrap_FA_regions'      : False,
                  'boostrap_MD_regions'      : False}

    # Paths main output folder -  All saved in txt as list of numbers. Meaning specified in the file name.

    pfo_data_output = jph(pfo_data, 'bootstrapping_mean')

    # Operations

    if controller['bootstrap_volumes']:
        df_vols = pd.read_csv(pfi_df_volume_bup, index_col=0)

        for A in range(1, 5):
            pfi_VOL_median_gA_txt = jph(pfo_data_output, 'VOL_mean_g{}.txt'.format(A))
            mean_gA = df_vols.loc[df_vols['group'] == A]['volume'].mean()
            print('saving mean group {}, {}'.format(A, mean_gA))
            np.savetxt(pfi_VOL_median_gA_txt, [mean_gA])

        for A, B in [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]:

            num_elements_gA = len(df_vols.loc[df_vols.group == A].volume)
            num_elements_gB = len(df_vols.loc[df_vols.group == B].volume)

            tot_index = df_vols.group[df_vols.group.isin({A, B})].index.tolist()

            print('A = {}, B = {} \nNum index A = {}, Num index B = {} \nTot index {}\n\n'.format(
                A, B, num_elements_gA, num_elements_gB, tot_index
            ))

            pfi_bootstrap_mean_gA_gB_txt = jph(pfo_data_output, 'VOL_boostrap_mean_g{}_g{}.txt'.format(A, B))
            with open(pfi_bootstrap_mean_gA_gB_txt, 'w') as f:

                for i in range(num_boostraps):

                    index_group_A = set(np.random.choice(tot_index, num_elements_gA))
                    index_group_B = set(tot_index) - index_group_A

                    bootsrapped_mean_A = np.mean([df_vols.loc[df_vols.group.isin({A, B})].volume[id_a] for id_a in index_group_A])
                    bootsrapped_mean_B = np.mean([df_vols.loc[df_vols.group.isin({A, B})].volume[id_b] for id_b in index_group_B])

                    bootsrapped_mean_diff = bootsrapped_mean_A - bootsrapped_mean_B

                    f.write("%s\n" % bootsrapped_mean_diff)

    elif controller['bootstrap_volumes_regions']:

        df_vol_regions = pd.read_csv(pfi_df_volume_per_region_bup, index_col=0)

        for region in list_regions:

            column_name = 'vol {}'.format(region)

            for A in range(1, 5):
                pfi_VOL_REG_median_gA_txt = jph(pfo_data_output, 'VOL_REG_median_g{}_{}.txt'.format(A, column_name.replace(' ', '')))
                median_reg_gA = df_vol_regions.loc[df_vol_regions.group == A][column_name].median()
                print('saving median group {}, region{}, {}'.format(A, region, median_reg_gA))
                np.savetxt(pfi_VOL_REG_median_gA_txt, [median_reg_gA])

            for A, B in [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]:

                num_elements_gA = len(df_vol_regions.loc[df_vol_regions.group == A][column_name])
                num_elements_gB = len(df_vol_regions.loc[df_vol_regions.group == B][column_name])

                tot_index = df_vol_regions.group[df_vol_regions.group.isin({A, B})].index.tolist()

                print('A = {}, B = {} \nNum index A = {}, Num index B = {} \nTot index {}\n\n'.format(
                    A, B, num_elements_gA, num_elements_gB, tot_index
                ))

                pfi_bootstrap_median_gA_gB_txt = jph(pfo_data_output, 'VOL_REG_boostrap_median_g{}_g{}_{}.txt'.format(A, B, column_name.replace(' ', '')))
                with open(pfi_bootstrap_median_gA_gB_txt, 'w') as f:

                    for i in range(num_boostraps):
                        index_group_A = set(np.random.choice(tot_index, num_elements_gA))
                        index_group_B = set(tot_index) - index_group_A

                        bootsrapped_mean_A = np.median([df_vol_regions.loc[df_vol_regions.group.isin({A, B})][column_name][id_a] for id_a in index_group_A])
                        bootsrapped_mean_B = np.median([df_vol_regions.loc[df_vol_regions.group.isin({A, B})][column_name][id_b] for id_b in index_group_B])

                        bootsrapped_mean_diff = bootsrapped_mean_A - bootsrapped_mean_B

                        f.write("%s\n" % bootsrapped_mean_diff)

    elif controller['boostrap_FA_regions']:

        df_FA_regions = pd.read_csv(pfi_df_FA_per_region_bup, index_col=0)

        for region in list_regions:

            column_name = 'FA {}'.format(region)

            for A in range(1, 5):
                pfi_FA_REG_median_gA_txt = jph(pfo_data_output, 'FA_REG_median_g{}_{}.txt'.format(A, column_name.replace(' ', '')))
                median_reg_gA = df_FA_regions.loc[df_FA_regions.group == A][column_name].median()
                print('FA: saving median group {}, region{}, {}'.format(A, region, median_reg_gA))
                np.savetxt(pfi_FA_REG_median_gA_txt, [median_reg_gA])

            for A, B in [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]:

                num_elements_gA = len(df_FA_regions.loc[df_FA_regions.group == A][column_name])
                num_elements_gB = len(df_FA_regions.loc[df_FA_regions.group == B][column_name])

                tot_index = df_FA_regions.group[df_FA_regions.group.isin({A, B})].index.tolist()

                print('FA: A = {}, B = {} \nNum index A = {}, Num index B = {} \nTot index {}\n\n'.format(
                    A, B, num_elements_gA, num_elements_gB, tot_index
                ))

                pfi_bootstrap_median_gA_gB_txt = jph(pfo_data_output,
                                                     'FA_REG_boostrap_median_g{}_g{}_{}.txt'.format(A, B,
                                                                                                     column_name.replace(
                                                                                                         ' ', '')))
                with open(pfi_bootstrap_median_gA_gB_txt, 'w') as f:

                    for i in range(num_boostraps):
                        index_group_A = set(np.random.choice(tot_index, num_elements_gA))
                        index_group_B = set(tot_index) - index_group_A

                        bootsrapped_mean_A = np.median(
                            [df_FA_regions.loc[df_FA_regions.group.isin({A, B})][column_name][id_a] for id_a in
                             index_group_A])
                        bootsrapped_mean_B = np.median(
                            [df_FA_regions.loc[df_FA_regions.group.isin({A, B})][column_name][id_b] for id_b in
                             index_group_B])

                        bootsrapped_mean_diff = bootsrapped_mean_A - bootsrapped_mean_B

                        f.write("%s\n" % bootsrapped_mean_diff)

    elif controller['boostrap_MD_regions']:
        df_MD_regions = pd.read_csv(pfi_df_MD_per_region_bup, index_col=0)

        for region in list_regions:

            column_name = 'MD {}'.format(region)

            for A in range(1, 5):
                pfi_MD_REG_median_gA_txt = jph(pfo_data_output, 'MD_REG_median_g{}_{}.txt'.format(A, column_name.replace(' ', '')))
                median_reg_gA = df_MD_regions.loc[df_MD_regions.group == A][column_name].median()
                print('MD: saving median group {}, region{}, {}'.format(A, region, median_reg_gA))
                np.savetxt(pfi_MD_REG_median_gA_txt, [median_reg_gA])

            for A, B in [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]:

                num_elements_gA = len(df_MD_regions.loc[df_MD_regions.group == A][column_name])
                num_elements_gB = len(df_MD_regions.loc[df_MD_regions.group == B][column_name])

                tot_index = df_MD_regions.group[df_MD_regions.group.isin({A, B})].index.tolist()

                print('MD: A = {}, B = {} \nNum index A = {}, Num index B = {} \nTot index {}\n\n'.format(
                    A, B, num_elements_gA, num_elements_gB, tot_index
                ))

                pfi_bootstrap_median_gA_gB_txt = jph(pfo_data_output,
                                                     'MD_REG_boostrap_median_g{}_g{}_{}.txt'.format(A, B,
                                                                                                    column_name.replace(
                                                                                                        ' ', '')))
                with open(pfi_bootstrap_median_gA_gB_txt, 'w') as f:

                    for i in range(num_boostraps):
                        index_group_A = set(np.random.choice(tot_index, num_elements_gA))
                        index_group_B = set(tot_index) - index_group_A

                        bootsrapped_mean_A = np.median([df_MD_regions.loc[df_MD_regions.group.isin({A, B})][column_name][id_a] for id_a in index_group_A])
                        bootsrapped_mean_B = np.median([df_MD_regions.loc[df_MD_regions.group.isin({A, B})][column_name][id_b] for id_b in index_group_B])

                        bootsrapped_mean_diff = bootsrapped_mean_A - bootsrapped_mean_B

                        f.write("%s\n" % bootsrapped_mean_diff)

