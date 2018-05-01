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


root_output = jph(root_study_rabbits, 'B_stats', 'General')


def subject_comparison_total_volume(sj_list, controller, coord_system='original'):

    if controller['get_data']:

        tot_vols = np.zeros(len(sj_list), dtype=np.float64)

        for sj_index, sj_id in enumerate(sj_list):
            sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj_id), 'r'))
            study = sj_parameters['study']
            category = sj_parameters['category']
            root_subject_input = jph(root_study_rabbits, 'A_data', study, category, sj_id)

            if coord_system == 'original':
                pfi_report_vols = jph(root_subject_input, 'report', '{}_vol_regions.csv'.format(sj_id))
            elif coord_system == 'stereotaxic':
                pfi_report_vols = jph(root_subject_input, 'stereotaxic', 'report', '{}stx_vol_regions.csv'.format(sj_id))
            else:
                raise IOError

            if not os.path.exists(pfi_report_vols):
                raise IOError('Report for subject {} not present'.format(sj_id))

            df_volumes = pa.read_csv(pfi_report_vols)

            tot_vols[sj_index] = df_volumes.loc[df_volumes['Labels'] < 255].loc[df_volumes['Labels'] > 0]['Volume'].sum()

        df_tot_vols_subjects = pa.DataFrame({'subject': sj_list, 'volume': tot_vols}).set_index('subject')
        df_tot_vols_subjects.to_csv(jph(root_output, 'tot_vols_subjects_{}.csv'.format(coord_system)))

    if controller['get_graphs']:

        df_tot_vols_subjects = pa.read_csv(jph(root_output, 'tot_vols_subjects_{}.csv'.format(coord_system)))

        fig, ax = plt.subplots(figsize=(8, 4))
        fig.canvas.set_window_title('Brain volume per subject')
        sns.set(color_codes=True)

        ax.bar(range(len(sj_list)), df_tot_vols_subjects['volume'].as_matrix())
        ax.set_title('Brain volume per subject')
        ax.set_ylabel('vol (mm^3)')
        ax.set_xlabel('Subject Id')
        ax.set_xticks(range(len(sj_list)))
        ax.set_xticklabels(sj_list, ha='center', rotation=45, fontsize=10)
        ax.xaxis.labelpad = 20

        plt.tight_layout()

        plt.savefig(jph(root_output, 'brain_volume_per_subject{}.pdf'.format(coord_system)), format='pdf', dpi=200)


def subject_comparison_values_below_labels_per_region(sj_list, ldm, labels_num, controller,
                                                      macro_label_name=None, coord_system='original', mod='FA',
                                                      cleaning=None):
    """
    Analyse the data in the report folder, FA or MD per region
    :param sj_list:
    :param ldm:
    :param labels_num: plain list of labels that will define a macro region
    :param controller:
    :param coord_system:
    :param mod: can be 'FA' or 'MD'
    :param cleaning: method to clean the data.
    :return:
    """
    dict_labels = ldm.get_dict()
    labels_names = [dict_labels[k][2].replace(' ', '') for k in labels_num]

    if macro_label_name is None:
        macro_label_name = ''
        for ln in labels_names:
            macro_label_name += ln + ' '
        macro_label_name = macro_label_name.strip().replace(' ', 'AND')

    if controller['get_data']:
        tot_data_distribution = {}

        for sj_index, sj_id in enumerate(sj_list):
            sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj_id), 'r'))
            study = sj_parameters['study']
            category = sj_parameters['category']
            root_subject_input = jph(root_study_rabbits, 'A_data', study, category, sj_id)

            list_data_below_labels_for_sj = []
            for l, l_names in zip(labels_num, labels_names):

                if coord_system == 'original':
                    pfi_report_mod = jph(root_subject_input, 'report', '{}_{}_{}_{}.csv'.format(sj_id, mod, l, l_names))
                elif coord_system == 'stereotaxic':
                    pfi_report_mod = jph(root_subject_input, 'stereotaxic', 'report',
                                          '{}stx_{}_{}_{}.csv'.format(sj_id, mod, l, l_names))
                else:
                    raise IOError

                assert os.path.exists(pfi_report_mod), pfi_report_mod

                list_data_below_labels_for_sj.append(np.loadtxt(pfi_report_mod))

            all_data = np.concatenate(list_data_below_labels_for_sj)

            if cleaning == 'remove outliers':
                q25, q75 = np.percentile(all_data, 25), np.percentile(all_data, 75)
                iqr = q75 - q25
                all_data = all_data[(all_data > q25 - 1.5 * iqr) + (all_data < q75 + 1.5 * iqr)]

            tot_data_distribution.update({sj_id: all_data})

        pfi_where_to_save_data_below_macro_region_for_mod_for_subjects = \
            jph(root_output, 'data_below_{}_regions_{}_{}.pickle'.format(mod, macro_label_name, coord_system))

        with open(pfi_where_to_save_data_below_macro_region_for_mod_for_subjects, 'wb') as handle:
            pickle.dump(tot_data_distribution, handle)

    if controller['get_graphs']:
        pfi_where_to_save_data_below_macro_region_for_mod_for_subjects = \
            jph(root_output, 'data_below_{}_regions_{}_{}.pickle'.format(mod, macro_label_name, coord_system))

        with open(pfi_where_to_save_data_below_macro_region_for_mod_for_subjects, 'rb') as handle:
            tot_data_distribution = pickle.load(handle)

        fig, ax = plt.subplots(figsize=(8, 4))
        fig.canvas.set_window_title('{} per region {}'.format(mod, macro_label_name))
        sns.set(color_codes=True)

        ax.boxplot([tot_data_distribution[k] for k in sj_list])
        ax.set_title('{} per region {}'.format(mod, macro_label_name))
        ax.set_ylabel('{}'.format(mod))
        ax.set_xlabel('Subject Id')
        ax.set_xticks(range(1, len(tot_data_distribution.keys())+1))
        ax.set_xticklabels(sj_list, ha='center', rotation=45, fontsize=10)
        ax.xaxis.labelpad = 20

        plt.tight_layout()

        plt.savefig(jph(root_output, '{}region{}_{}.pdf'.format(mod, macro_label_name, coord_system)), format='pdf', dpi=200)

def vol_Single_region():
    # TODO
    pass


if __name__ == '__main__':


    ptb_related_regions = OrderedDict()

    # ptb_related_regions['CerebellarHemisphere'] = [179, 180]
    # ptb_related_regions['Thalamus'] = [83, 84]
    # ptb_related_regions['Hippocampus'] = [31, 32]
    # ptb_related_regions['InternalCapsule'] = [223, 224]
    # ptb_related_regions['CaudateNucleus'] = [69, 70]
    # ptb_related_regions['CorpusCallosum'] = [218]
    # ptb_related_regions['MedialPrefrontalAndFrontal'] = [5, 6, 7, 8]
    ptb_related_regions['AnteriorCommissure'] = [233]

    controller = {'get_data'   : True,
                  'get_graphs' : True}

    subjects = ['12307', '12308', '12402', '12504', '12505', '12607', '12608', '12609', '12610']
    ldm = LdM(pfi_labels_descriptor)

    # total volumes stereotaxic coordinates as histogram:
    # subject_comparison_total_volume(subjects, controller=controller, coord_system='original')

    for k in ptb_related_regions.keys():

        for coordinates in ['original', 'stereotaxic']:

            # comparison FA
            subject_comparison_values_below_labels_per_region(subjects, ldm, ptb_related_regions[k], controller,
                                                              macro_label_name=k, coord_system=coordinates, mod='FA',
                                                              cleaning=None)

            # comparison MD
            subject_comparison_values_below_labels_per_region(subjects, ldm, ptb_related_regions[k], controller,
                                                              macro_label_name=k, coord_system=coordinates, mod='MD',
                                                              cleaning=None)



    # total volumes stereotaxic coordinates as histogram:

    #
