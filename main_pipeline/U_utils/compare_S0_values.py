import os
import numpy as np
import pandas as pa
import pickle
from os.path import join as jph
import seaborn as sns
import matplotlib.pyplot as plt
from collections import OrderedDict

from LABelsToolkit.tools.descriptions.manipulate_descriptors import LabelsDescriptorManager as LdM

from tools.definitions import root_study_rabbits, pfo_subjects_parameters, pfi_labels_descriptor


root_output = jph(root_study_rabbits, 'B_stats', 'S0Comparison')
S0_timepoints = 7


def subject_comparison_S0_tissue_values_in_DWI(sj_list, ldm, labels_num, controller, subjects_grouping=None,
                                                      macro_label_name=None, coord_system='original',
                                                      cleaning=None):
    """
    Analyse the data in the report folder, FA or MD per region
    :param sj_list:
    :param ldm: label descriptor manager
    :param labels_num: plain list of labels that will define a macro region
    :param controller:
    :param coord_system: 'original' or 'stereotaxic'
    :param cleaning: method to clean the data.
    :return:
    """
    print('subject_comparison_values_below_labels_per_region {} for subjects {}'.format(labels_num, sj_list))

    if controller['get_data']:
        print('--- get data')
        tot_data_sj_vs_S0s = np.zeros([len(sj_list), S0_timepoints])




        pfi_where_to_save_data_below_S0_first_datapoints = jph(root_output, 'data.txt')

        with open(pfi_where_to_save_data_below_S0_first_datapoints, 'wb') as handle:
            pickle.dump(tot_data_sj_vs_S0s, handle)

    if controller['get_graphs']:
        print('--- get graphs')

        with open(pfi_where_to_save_data_below_macro_region_for_mod_for_subjects, 'rb') as handle:
            tot_data_distribution = pickle.load(handle)

        fig, ax = plt.subplots(figsize=(8, 4))
        fig.canvas.set_window_title('{} per region {}'.format(mod, macro_label_name))
        sns.set(color_codes=True)

        ax.boxplot([tot_data_distribution[k] for k in sj_list])

        if subjects_grouping is not None:
            assert np.sum(subjects_grouping) == len(subjects)
            medians = [np.median(tot_data_distribution[k]) for k in sj_list]
            cumulative_grouping = np.cumsum([0] + subjects_grouping)
            medians_grouped = [[medians[l] for l in range(cumulative_grouping[k], cumulative_grouping[k+1])] for k in range(len(cumulative_grouping) - 1)]
            medians_of_medians_grouped = [np.median(li) for li in medians_grouped]

            for i, m in enumerate(medians_of_medians_grouped):
                ax.hlines(y=m, xmin=cumulative_grouping[i] + 1, xmax=cumulative_grouping[i+1], color='r', alpha=0.5, linestyles='dashed')

        ax.set_title('{} per region {}'.format(mod, macro_label_name))
        ax.set_ylabel('{}'.format(mod))
        ax.set_xlabel('Subject Id')
        ax.set_xticks(range(1, len(tot_data_distribution.keys())+1))
        ax.set_xticklabels(sj_list, ha='center', rotation=45, fontsize=10)
        ax.xaxis.labelpad = 20

        plt.tight_layout()

        # plt.show()

        plt.savefig(jph(root_output, '{}region{}_{}.pdf'.format(mod, macro_label_name, coord_system)), format='pdf',
                    dpi=200)
        plt.close()


if __name__ == '__main__':

    pass

    if True:
        # total volumes stereotaxic coordinates as histogram:
        subject_comparison_total_volume(subjects, controller=controller_, subjects_grouping=subjects_grouping_,
                                        coord_system='original')

    if True:
        # single regions volume across subjects as histogram:
        for reg in ptb_related_regions.keys():

            for coordinates in ['original', 'stereotaxic']:
                subject_comparison_volume_per_region(subjects, ldm, ptb_related_regions[reg], controller_,
                                                     subjects_grouping_, macro_label_name=reg, coord_system=coordinates,
                                                     cleaning=None)

    if True:
        for reg in ptb_related_regions.keys():

            for coordinates in ['original', 'stereotaxic']:

                # comparison FA
                subject_comparison_values_below_labels_per_region(subjects, ldm, ptb_related_regions[reg], controller_,
                                                                  subjects_grouping_, macro_label_name=reg,
                                                                  coord_system=coordinates, mod='FA', cleaning=None)

                # comparison MD
                subject_comparison_values_below_labels_per_region(subjects, ldm, ptb_related_regions[reg], controller_,
                                                                  subjects_grouping_, macro_label_name=reg,
                                                                  coord_system=coordinates, mod='MD', cleaning=None)

    # total volumes stereotaxic coordinates as histogram:


