import os
from os.path import join as jph
from scipy.stats import norm

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import rcParams

from main_pipeline.A5_further_data_analysis.A_histograms import get_histogram
from main_pipeline.A5_further_data_analysis.A_steering_wheels import visualise_multiple_testing


if __name__ == '__main__':

    pfo_data_output = '/Users/sebastiano/a_data/TData/rabbits/bootstrapping'
    dpi = 200
    dict_caption = {1: 'T', 2: 'PT', 3: 'LPT', 4: 'LPT+'}
    list_regions = [
        'Internal capsule',
        'Hypothalamus',
        'Hippocampus',
        'Corpus Callosum',
        'Claustrum',
        'Thalamus',
        'Caudate nucleus',
        'Amygdala',
        'Putamen']

    controller = {'figure1' : False,
                  'figure2' : False,
                  'figure3' : False,
                  'figure4' : True,
                  'figure5' : True,
                  'figure6' : True}

    save = True
    show = False

    # FIGURE 1: histogram total volume group 1 vs group 2 boostrapped with Pearson index and percentile annotation.
    if controller['figure1']:

        print('\nCreating figure 1 ...')

        A, B = 1, 2
        pfi_VOL_median_g1_txt = jph(pfo_data_output, 'VOL_median_g{}.txt'.format(A))
        pfi_VOL_median_g2_txt = jph(pfo_data_output, 'VOL_median_g{}.txt'.format(B))
        pfi_bootstrap_median_gA_gB_txt = jph(pfo_data_output, 'VOL_boostrap_median_g{}_g{}.txt'.format(A, B))

        for p in [pfi_VOL_median_g1_txt, pfi_VOL_median_g2_txt, pfi_bootstrap_median_gA_gB_txt]:
            assert os.path.exists(p), p

        median_A = np.loadtxt(pfi_VOL_median_g1_txt)
        median_B = np.loadtxt(pfi_VOL_median_g2_txt)

        median_diff = np.abs(median_A - median_B)

        boostrap_data = np.loadtxt(pfi_bootstrap_median_gA_gB_txt)

        print(len(set(boostrap_data)))

        get_histogram([boostrap_data], ['Term vs. Pre-Term'], [median_diff],
                      percentile_annotation=True, dpi=dpi,
                      x_label='Bootstrapped median')

        if save:
            pfi_whereto_save_fig_1 = jph(pfo_data_output, 'bootstrap_fig1_TvsPT_vol.pdf')
            plt.savefig(pfi_whereto_save_fig_1, format='pdf', dpi=dpi)
        if show:
            plt.show()

    # FIGURE 2: six histograms for all the six combinations of full volume
    if controller['figure2']:

        print('\nCreating figure 2 ...')

        list_data = [[], []]
        list_median_diffs = [[], []]
        list_titles = [[], []]
        index = 0

        for A, B in [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]:
            pfi_VOL_median_g1_txt = jph(pfo_data_output, 'VOL_median_g{}.txt'.format(A))
            pfi_VOL_median_g2_txt = jph(pfo_data_output, 'VOL_median_g{}.txt'.format(B))
            pfi_bootstrap_median_gA_gB_txt = jph(pfo_data_output, 'VOL_boostrap_median_g{}_g{}.txt'.format(A, B))

            for p in [pfi_VOL_median_g1_txt, pfi_VOL_median_g2_txt, pfi_bootstrap_median_gA_gB_txt]:
                assert os.path.exists(p), p

            median_A = np.loadtxt(pfi_VOL_median_g1_txt)
            median_B = np.loadtxt(pfi_VOL_median_g2_txt)

            median_diff = np.abs(median_A - median_B)

            boostrap_data = np.loadtxt(pfi_bootstrap_median_gA_gB_txt)

            title_figure = '{} vs. {}'.format(dict_caption[A], dict_caption[B])

            list_median_diffs[index//3].append(median_diff)
            list_data[index//3].append(boostrap_data)
            list_titles[index//3].append(title_figure)

            index += 1

        print(len(list_data))
        print(len(list_median_diffs))

        get_histogram(list_data, list_titles, list_median_diffs, nrows=2, ncols=3, figsize=[6, 4])

        plt.tight_layout()
        if save:
            pfi_whereto_save_fig_1 = jph(pfo_data_output, 'bootstrap_fig2_vols.pdf')
            plt.savefig(pfi_whereto_save_fig_1, format='pdf', dpi=dpi)
        if show:
            plt.show()

    # FIGURE 3: Steering wheel for the total volume.
    if controller['figure3']:

        pearsons = []

        for A, B in [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]:
            pfi_VOL_median_g1_txt = jph(pfo_data_output, 'VOL_median_g{}.txt'.format(A))
            pfi_VOL_median_g2_txt = jph(pfo_data_output, 'VOL_median_g{}.txt'.format(B))
            pfi_bootstrap_median_gA_gB_txt = jph(pfo_data_output, 'VOL_boostrap_median_g{}_g{}.txt'.format(A, B))

            for p in [pfi_VOL_median_g1_txt, pfi_VOL_median_g2_txt, pfi_bootstrap_median_gA_gB_txt]:
                assert os.path.exists(p), p

            median_A = np.loadtxt(pfi_VOL_median_g1_txt)
            median_B = np.loadtxt(pfi_VOL_median_g2_txt)

            median_diff = np.abs(median_A - median_B)
            boostrap_data = np.loadtxt(pfi_bootstrap_median_gA_gB_txt)

            mu, sigma = norm.fit(boostrap_data)

            pears = np.round(np.abs(median_diff - mu) / sigma, decimals=1)

            pearsons.append(pears)

        title_figure = 'Brain volume difference'

        vals = {'Zero'       : 'T',
                'One'        : 'PT',
                'Two'        : 'LPT',
                'Three'      : 'LPT+',
                'Zero_One'   : pearsons[0],
                'Zero_Two'   : pearsons[1],
                'Zero_Three' : pearsons[2],
                'One_Two'    : pearsons[3],
                'One_Three'  : pearsons[4],
                'Two_Three'  : pearsons[5],
                }

        visualise_multiple_testing([vals], titles=[title_figure], figsize=(3, 2.5))
        plt.tight_layout()
        if save:
            pfi_whereto_save_fig_1 = jph(pfo_data_output, 'bootstrap_fig3_vols_wheels.pdf')
            plt.savefig(pfi_whereto_save_fig_1, format='pdf', dpi=dpi)
        if show:
            plt.show()

    # FIGURE 4: Steering wheels for each region
    if controller['figure4']:

        list_vals = [[], [], []]
        list_titles = [[], [], []]

        index = 0

        for region in list_regions:
            pearsons = []

            for A, B in [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]:
                pfi_VOL_median_g1_txt = jph(pfo_data_output, 'VOL_REG_median_g{}_vol{}.txt'.format(A, region.replace(' ', '')))
                pfi_VOL_median_g2_txt = jph(pfo_data_output, 'VOL_REG_median_g{}_vol{}.txt'.format(B, region.replace(' ', '')))
                pfi_bootstrap_median_gA_gB_txt = jph(pfo_data_output,
                                                     'VOL_REG_boostrap_median_g{}_g{}_vol{}.txt'.format(A, B, region.replace(' ', '')))

                for p in [pfi_VOL_median_g1_txt, pfi_VOL_median_g2_txt, pfi_bootstrap_median_gA_gB_txt]:
                    assert os.path.exists(p), p

                median_A = np.loadtxt(pfi_VOL_median_g1_txt)
                median_B = np.loadtxt(pfi_VOL_median_g2_txt)

                median_diff = np.abs(median_A - median_B)
                boostrap_data = np.loadtxt(pfi_bootstrap_median_gA_gB_txt)

                mu, sigma = norm.fit(boostrap_data)

                pears = np.round(np.abs(median_diff - mu) / sigma, decimals=1)

                pearsons.append(pears)

            title_figure = '{}'.format(region)

            vals = {'Zero': 'T',
                    'One': 'PT',
                    'Two': 'LPT',
                    'Three': 'LPT+',
                    'Zero_One': pearsons[0],
                    'Zero_Two': pearsons[1],
                    'Zero_Three': pearsons[2],
                    'One_Two': pearsons[3],
                    'One_Three': pearsons[4],
                    'Two_Three': pearsons[5],
                    }

            title = ''

            list_vals[index//3].append(vals)
            list_titles[index//3].append(title_figure)
            index += 1

        rcParams['axes.titlepad'] = -4
        visualise_multiple_testing(list_vals, titles=list_titles, nrows=3, ncols=3, add_colorbar=False,
                                   figsize=(5, 5.3))
        plt.tight_layout()
        if save:
            pfi_whereto_save_fig_1 = jph(pfo_data_output, 'bootstrap_fig4_vols_region_wise_wheels.pdf')
            plt.savefig(pfi_whereto_save_fig_1, format='pdf', dpi=dpi)
        if show:
            plt.show()

    # FIGURE 5: as figure 4 with FA
    if controller['figure5']:

        list_vals = [[], [], []]
        list_titles = [[], [], []]

        index = 0

        for region in list_regions:
            pearsons = []

            for A, B in [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]:
                pfi_FA_median_g1_txt = jph(pfo_data_output,
                                            'FA_REG_median_g{}_FA{}.txt'.format(A, region.replace(' ', '')))
                pfi_FA_median_g2_txt = jph(pfo_data_output,
                                            'FA_REG_median_g{}_FA{}.txt'.format(B, region.replace(' ', '')))
                pfi_bootstrap_median_gA_gB_txt = jph(pfo_data_output,
                                                     'FA_REG_boostrap_median_g{}_g{}_FA{}.txt'.format(A, B,
                                                                                                        region.replace(
                                                                                                            ' ', '')))

                for p in [pfi_FA_median_g1_txt, pfi_FA_median_g2_txt, pfi_bootstrap_median_gA_gB_txt]:
                    assert os.path.exists(p), p

                median_A = np.loadtxt(pfi_FA_median_g1_txt)
                median_B = np.loadtxt(pfi_FA_median_g2_txt)

                median_diff = np.abs(median_A - median_B)
                boostrap_data = np.loadtxt(pfi_bootstrap_median_gA_gB_txt)

                mu, sigma = norm.fit(boostrap_data)

                pears = np.round(np.abs(median_diff - mu) / sigma, decimals=1)

                pearsons.append(pears)

            title_figure = '{}'.format(region)

            vals = {'Zero': 'T',
                    'One': 'PT',
                    'Two': 'LPT',
                    'Three': 'LPT+',
                    'Zero_One': pearsons[0],
                    'Zero_Two': pearsons[1],
                    'Zero_Three': pearsons[2],
                    'One_Two': pearsons[3],
                    'One_Three': pearsons[4],
                    'Two_Three': pearsons[5],
                    }

            title = ''

            list_vals[index // 3].append(vals)
            list_titles[index // 3].append(title_figure)
            index += 1

        rcParams['axes.titlepad'] = -4
        visualise_multiple_testing(list_vals, titles=list_titles, nrows=3, ncols=3, add_colorbar=False,
                                   figsize=(5, 5.3))
        plt.tight_layout()

        pfi_whereto_save_fig_1 = jph(pfo_data_output, 'bootstrap_fig5_FA_region_wise_wheels.pdf')
        plt.savefig(pfi_whereto_save_fig_1, format='pdf', dpi=dpi)

        plt.show()

    # FIGURE 6: as figure 4 with MD
    if controller['figure6']:
        list_vals = [[], [], []]
        list_titles = [[], [], []]

        index = 0

        for region in list_regions:
            pearsons = []

            for A, B in [(1, 2), (1, 3), (1, 4), (2, 3), (2, 4), (3, 4)]:
                pfi_MD_median_g1_txt = jph(pfo_data_output,
                                           'MD_REG_median_g{}_MD{}.txt'.format(A, region.replace(' ', '')))
                pfi_MD_median_g2_txt = jph(pfo_data_output,
                                           'MD_REG_median_g{}_MD{}.txt'.format(B, region.replace(' ', '')))
                pfi_bootstrap_median_gA_gB_txt = jph(pfo_data_output,
                                                     'MD_REG_boostrap_median_g{}_g{}_MD{}.txt'.format(A, B,
                                                                                                      region.replace(
                                                                                                          ' ', '')))

                for p in [pfi_MD_median_g1_txt, pfi_MD_median_g2_txt, pfi_bootstrap_median_gA_gB_txt]:
                    assert os.path.exists(p), p

                median_A = np.loadtxt(pfi_MD_median_g1_txt)
                median_B = np.loadtxt(pfi_MD_median_g2_txt)

                median_diff = np.abs(median_A - median_B)
                boostrap_data = np.loadtxt(pfi_bootstrap_median_gA_gB_txt)

                mu, sigma = norm.fit(boostrap_data)

                pears = np.round(np.abs(median_diff - mu) / sigma, decimals=1)

                pearsons.append(pears)

            title_figure = '{}'.format(region)

            vals = {'Zero': 'T',
                    'One': 'PT',
                    'Two': 'LPT',
                    'Three': 'LPT+',
                    'Zero_One': pearsons[0],
                    'Zero_Two': pearsons[1],
                    'Zero_Three': pearsons[2],
                    'One_Two': pearsons[3],
                    'One_Three': pearsons[4],
                    'Two_Three': pearsons[5],
                    }

            title = ''

            list_vals[index // 3].append(vals)
            list_titles[index // 3].append(title_figure)
            index += 1

        rcParams['axes.titlepad'] = -4
        visualise_multiple_testing(list_vals, titles=list_titles, nrows=3, ncols=3, add_colorbar=False,
                                   figsize=(5, 5.3))
        plt.tight_layout()
        if save:
            pfi_whereto_save_fig_1 = jph(pfo_data_output, 'bootstrap_fig6_MD_region_wise_wheels.pdf')
            plt.savefig(pfi_whereto_save_fig_1, format='pdf', dpi=dpi)
        if show:
            plt.show()
