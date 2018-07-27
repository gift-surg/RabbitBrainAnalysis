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


root_output = jph(root_study_rabbits, 'B_stats', 'ACS_01_New')


def subject_comparison_total_volume(sj_list, controller, subjects_grouping=None, coord_system='original'):
    print('subject_comparison_total_volume for subjects {}'.format(sj_list))

    if controller['get_data']:
        print('--- get data')
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
        print('--- get graphs')

        df_tot_vols_subjects = pa.read_csv(jph(root_output, 'tot_vols_subjects_{}.csv'.format(coord_system)))

        fig, ax = plt.subplots(figsize=(8, 4))
        fig.canvas.set_window_title('Brain volume per subject')
        sns.set(color_codes=True)

        ax.bar(range(len(sj_list)), df_tot_vols_subjects['volume'].as_matrix())

        if subjects_grouping is not None:
            assert np.sum(subjects_grouping) == len(subjects)
            vals = df_tot_vols_subjects['volume'].as_matrix()

            cumulative_grouping = np.cumsum([0] + subjects_grouping)
            vals_grouped = [[vals[l] for l in range(cumulative_grouping[k], cumulative_grouping[k + 1])] for k in range(len(cumulative_grouping) - 1)]
            medians_of_vals_grouped = [np.median(li) for li in vals_grouped]

            for i, m in enumerate(medians_of_vals_grouped):
                ax.hlines(y=m, xmin=cumulative_grouping[i] - 0.3, xmax=cumulative_grouping[i + 1] - 0.7, color='r', alpha=0.5, linestyles='dashed')

        ax.set_title('Brain volume per subject')
        ax.set_ylabel('vol (mm^3)')
        ax.set_xlabel('Subject Id')
        ax.set_xticks(range(len(sj_list)))
        ax.set_xticklabels(sj_list, ha='center', rotation=45, fontsize=10)
        ax.xaxis.labelpad = 20

        plt.tight_layout()

        plt.savefig(jph(root_output, 'brain_volume_per_subject{}.pdf'.format(coord_system)), format='pdf', dpi=200)

        plt.close()


def subject_comparison_volume_per_region(sj_list, ldm, labels_num, controller, subjects_grouping=None, macro_label_name=None,
                                         coord_system='original', cleaning=None):
    """

    :param sj_list:
    :param ldm:
    :param labels_num:
    :param controller:
    :param macro_label_name:
    :param coord_system:
    :param cleaning:
    :return:
    """
    print('subject_comparison_volume_per_region {} for subjects {}'.format(labels_num, sj_list))
    dict_labels = ldm.get_dict()
    labels_names = [dict_labels[k][2].replace(' ', '') for k in labels_num]

    if macro_label_name is None:
        macro_label_name = ''
        for ln in labels_names:
            macro_label_name += ln + ' '
        macro_label_name = macro_label_name.strip().replace(' ', 'AND')

    # Output csv data file
    pfi_where_to_save_volume_for_macro_region = jph(root_output,
                                                    'VOLregion{}_{}.csv'.format(macro_label_name, coord_system))

    if controller['get_data']:
        print('--- get data')
        array_tot_vol_per_region = np.zeros(len(sj_list), dtype=np.float64)

        for sj_index, sj_id in enumerate(sj_list):
            sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj_id), 'r'))
            study = sj_parameters['study']
            category = sj_parameters['category']
            root_subject_input = jph(root_study_rabbits, 'A_data', study, category, sj_id)

            if coord_system == 'original':
                pfi_vol_regions_csv = jph(root_subject_input, 'report', '{}_vol_regions.csv'.format(sj_id))
            elif coord_system == 'stereotaxic':
                pfi_vol_regions_csv = jph(root_subject_input, 'stereotaxic', 'report',
                                          '{}stx_vol_regions.csv'.format(sj_id))
            else:
                raise IOError

            assert os.path.exists(pfi_vol_regions_csv), pfi_vol_regions_csv

            df_vol = pa.read_csv(pfi_vol_regions_csv)
            tot_vol_per_region = 0.0
            for l in labels_num:
                tot_vol_per_region += df_vol.loc[df_vol['Labels'] == l]['Volume'].values[0]

            array_tot_vol_per_region[sj_index] = tot_vol_per_region

        vol_region_per_subject = pa.DataFrame({'sj': sj_list, 'Volume' : array_tot_vol_per_region},
                                              columns=('sj', 'Volume'))

        vol_region_per_subject.to_csv(pfi_where_to_save_volume_for_macro_region, index=False)

    if controller['get_graphs']:
        print('--- get graphs')
        df_tot_vols_subjects = pa.read_csv(pfi_where_to_save_volume_for_macro_region)

        fig, ax = plt.subplots(figsize=(8, 4))
        fig.canvas.set_window_title('Brain volume per subject')
        sns.set(color_codes=True)

        ax.bar(range(len(sj_list)), df_tot_vols_subjects['Volume'].as_matrix())

        if subjects_grouping is not None:
            assert np.sum(subjects_grouping) == len(subjects)
            vals = df_tot_vols_subjects['Volume'].as_matrix()

            cumulative_grouping = np.cumsum([0] + subjects_grouping)
            vals_grouped = [[vals[l] for l in range(cumulative_grouping[k], cumulative_grouping[k+1])] for k in range(len(cumulative_grouping) - 1)]
            medians_of_vals_grouped = [np.median(li) for li in vals_grouped]

            for i, m in enumerate(medians_of_vals_grouped):
                ax.hlines(y=m, xmin=cumulative_grouping[i], xmax=cumulative_grouping[i+1] - 1, color='r', alpha=0.5, linestyles='dashed')

        ax.set_title('Region {} volume per subject ({})'.format(macro_label_name, coord_system))
        ax.set_ylabel('vol (mm^3)')
        ax.set_xlabel('Subject Id')
        ax.set_xticks(range(len(sj_list)))
        ax.set_xticklabels(sj_list, ha='center', rotation=45, fontsize=10)
        ax.xaxis.labelpad = 20

        plt.tight_layout()

        plt.savefig(jph(root_output, 'VOLregion{}_{}.pdf'.format(macro_label_name, coord_system)),
                    format='pdf', dpi=200)
        plt.close()


def subject_comparison_values_below_labels_per_region(sj_list, ldm, labels_num, controller, subjects_grouping=None,
                                                      macro_label_name=None, coord_system='original', mod='FA',
                                                      cleaning='', eroded=False):
    """
    Analyse the data in the report folder, FA or MD per region
    :param sj_list:
    :param ldm: label descriptor manager
    :param labels_num: plain list of labels that will define a macro region
    :param subjects_grouping:
    :param controller:
    :param coord_system: 'original' or 'stereotaxic'
    :param mod: can be 'FA' or 'MD'
    :param cleaning: method to clean the data.
    :return:
    """
    print('\n\n-------------------')
    print('subject_comparison_values_below_labels_per_region {} for subjects {}, mod {}'.format(labels_num, sj_list, mod))

    dict_labels = ldm.get_dict()
    labels_names = [dict_labels[k][2].replace(' ', '') for k in labels_num]

    if macro_label_name is None:
        macro_label_name = ''
        for ln in labels_names:
            macro_label_name += ln + ' '
        macro_label_name = macro_label_name.strip().replace(' ', 'AND')

    # output data

    if eroded:
        pfi_where_to_save_data_below_macro_region_for_mod_for_subjects = \
            jph(root_output, 'data_below_{}_regions_{}_{}{}_eroded.pickle'.format(mod, macro_label_name, coord_system, cleaning))
    else:
        pfi_where_to_save_data_below_macro_region_for_mod_for_subjects = \
            jph(root_output, 'data_below_{}_regions_{}_{}{}.pickle'.format(mod, macro_label_name, coord_system, cleaning))

    if controller['get_data']:
        print('--- get data')
        tot_data_distribution = {}

        for sj_index, sj_id in enumerate(sj_list):
            sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj_id), 'r'))
            study = sj_parameters['study']
            category = sj_parameters['category']
            root_subject_input = jph(root_study_rabbits, 'A_data', study, category, sj_id)

            list_data_below_labels_for_sj = []
            for l, l_names in zip(labels_num, labels_names):

                if eroded:

                    if coord_system == 'original':
                        pfi_report_mod = jph(root_subject_input, 'report', '{}_{}_{}_{}_eroded.csv'.format(sj_id, mod, l, l_names))
                    elif coord_system == 'stereotaxic':
                        pfi_report_mod = jph(root_subject_input, 'stereotaxic', 'report', '{}stx_{}_{}_{}_eroded.csv'.format(sj_id, mod, l, l_names))
                    else:
                        raise IOError

                else:

                    if coord_system == 'original':
                        pfi_report_mod = jph(root_subject_input, 'report', '{}_{}_{}_{}.csv'.format(sj_id, mod, l, l_names))
                    elif coord_system == 'stereotaxic':
                        pfi_report_mod = jph(root_subject_input, 'stereotaxic', 'report', '{}stx_{}_{}_{}.csv'.format(sj_id, mod, l, l_names))
                    else:
                        raise IOError

                assert os.path.exists(pfi_report_mod), pfi_report_mod

                list_data_below_labels_for_sj.append(np.loadtxt(pfi_report_mod))

            all_data = np.concatenate(list_data_below_labels_for_sj)

            if cleaning == '':
                pass

            elif cleaning == '_no_outliers':
                q25, q75 = np.percentile(all_data, 25), np.percentile(all_data, 75)
                iqr = q75 - q25
                len_all_data = len(all_data)
                all_data = [j for j in all_data if (q25 - 1.5 * iqr < j < q75 + 1.5 * iqr)]
                print('outliers removed subject {}: {}'.format(sj_id, len_all_data - len(all_data)))

            elif cleaning == '_only_iqr':
                q25, q75 = np.percentile(all_data, 25), np.percentile(all_data, 75)
                len_all_data = len(all_data)
                all_data = [j for j in all_data if (q25 < j < q75)]
                print('outside interquartile removed subject {}: {}'.format(sj_id, len_all_data - len(all_data)))

            else:
                raise IOError

            tot_data_distribution.update({sj_id: all_data})

        with open(pfi_where_to_save_data_below_macro_region_for_mod_for_subjects, 'wb') as handle:
            pickle.dump(tot_data_distribution, handle)

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

        if eroded:
            pfi_where_to_save_fig = jph(root_output, '{}region{}_{}{}_eroded.pdf'.format(mod, macro_label_name, coord_system, cleaning))
        else:
            pfi_where_to_save_fig = jph(root_output, '{}region{}_{}{}.pdf'.format(mod, macro_label_name, coord_system, cleaning))

        plt.savefig(pfi_where_to_save_fig, format='pdf',
                    dpi=200)
        plt.close()

    if controller['save_medians']:
        with open(pfi_where_to_save_data_below_macro_region_for_mod_for_subjects, 'rb') as handle:
            tot_data_distribution = pickle.load(handle)
        se = pa.Series([np.median(tot_data_distribution[k]) for k in tot_data_distribution.keys()], index=tot_data_distribution.keys())
        se = se.sort_index()

        if eroded:
            pfi_where_to_save_medians = jph(root_output, 'Median_below_{}_region{}_{}{}_eroded.csv'.format(mod, macro_label_name, coord_system, cleaning))
        else:
            pfi_where_to_save_medians = jph(root_output, 'Median_below_{}_region{}_{}{}.csv'.format(mod, macro_label_name, coord_system, cleaning))

        se.to_csv(pfi_where_to_save_medians)

if __name__ == '__main__':

    assert os.path.exists(root_output)

    ptb_related_regions = OrderedDict()

    ptb_related_regions['CerebellarHemisphere']       = [179, 180]
    ptb_related_regions['Thalamus']                   = [83, 84]
    ptb_related_regions['Hypothalamus']               = [109, 110]
    ptb_related_regions['Hippocampus']                = [31, 32]
    ptb_related_regions['InternalCapsule']            = [223, 224]
    ptb_related_regions['CaudateNucleus']             = [69, 70]
    ptb_related_regions['CorpusCallosum']             = [218]
    ptb_related_regions['MedialPrefrontalAndFrontal'] = [5, 6, 7, 8]
    ptb_related_regions['AnteriorCommissure']         = [233]

    controller_ = {'get_data'     : True,
                   'get_graphs'   : True,
                   'save_medians' : True}
    #
    # preterm = ['1201', '1203', '1305', '1404', '1505', '1507', '1510', '2002',
    #            '3301', '3303', '3404', '4302',  '4304', '4305', '4901',
    #            '4903', '5001']
    #
    # # '1501', '1504' '1508', '1509', '1511', '2013', '2202', '2205', '2206' : in vivo and not in subjects parameters.
    # # '4303','4406', :  rejected.
    #
    # term = ['1702', '1805', '2502', '2503', '2608',  '4501', '4504', '4507', '4601',  '4603', '13003', '13004',
    #         '13005', '13006']
    # # '2605', '2702', '4602',  Rejected.
    #
    # subjects = preterm + term
    # subjects_grouping_ = [len(preterm), len(term)]
    #

    subjects_not_present = []

    subjects = ['12307', '12308', '12309', '12402', '12504', '12505', '12607', '12608', '12609', '12610', '13102', '13201', '13202', '13401', '13402', '13403', '13403retest']

    subjects_grouping_ = None

    for sj in subjects:
        sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))
        study = sj_parameters['study']
        category = sj_parameters['category']
        sj_report_input = jph(root_study_rabbits, 'A_data', study, category, sj, 'stereotaxic', 'report',)

        if not os.path.exists(sj_report_input):
            subjects_not_present.append(sj)

    print subjects_not_present

    ldm = LdM(pfi_labels_descriptor)

    if True:
        # total volumes stereotaxic coordinates as histogram:
        subject_comparison_total_volume(subjects, controller=controller_, subjects_grouping=subjects_grouping_,
                                        coord_system='stereotaxic')

    if True:
        # single regions volume across subjects as histogram:
        for reg in ptb_related_regions.keys():

            for coordinates in ['stereotaxic']:  # 'original',
                subject_comparison_volume_per_region(subjects, ldm, ptb_related_regions[reg], controller_,
                                                     subjects_grouping_, macro_label_name=reg, coord_system=coordinates,
                                                     cleaning=None)

    if True:
        for reg in ptb_related_regions.keys():

            for coordinates in ['stereotaxic']:  # 'original',

                # # ---- Without erosion

                # comparison FA - no erosion, no outliers filter
                subject_comparison_values_below_labels_per_region(subjects, ldm, ptb_related_regions[reg], controller_,
                                                                  subjects_grouping_, macro_label_name=reg,
                                                                  coord_system=coordinates, mod='FA',
                                                                  cleaning='', eroded=False)

                # comparison MD - no erosion, no outliers filter
                subject_comparison_values_below_labels_per_region(subjects, ldm, ptb_related_regions[reg], controller_,
                                                                  subjects_grouping_, macro_label_name=reg,
                                                                      coord_system=coordinates, mod='MD',
                                                                      cleaning='', eroded=False)

                # comparison FA - no erosion, outliers filter
                subject_comparison_values_below_labels_per_region(subjects, ldm, ptb_related_regions[reg], controller_,
                                                                  subjects_grouping_, macro_label_name=reg,
                                                                  coord_system=coordinates, mod='FA',
                                                                  cleaning='_no_outliers', eroded=False)

                # comparison MD - no erosion, outliers filter
                subject_comparison_values_below_labels_per_region(subjects, ldm, ptb_related_regions[reg], controller_,
                                                                  subjects_grouping_, macro_label_name=reg,
                                                                  coord_system=coordinates, mod='MD',
                                                                  cleaning='_no_outliers', eroded=False)

                # # ---- With erosion
                # if coordinates  == 'stereotaxic':
                #
                #     # comparison FA - erosion, no outliers filter
                #     subject_comparison_values_below_labels_per_region(subjects, ldm, ptb_related_regions[reg], controller_,
                #                                                       subjects_grouping_, macro_label_name=reg,
                #                                                       coord_system=coordinates, mod='FA',
                #                                                       cleaning='', eroded=True)
                #
                #     # comparison MD - erosion, no outliers filter
                #     subject_comparison_values_below_labels_per_region(subjects, ldm, ptb_related_regions[reg], controller_,
                #                                                       subjects_grouping_, macro_label_name=reg,
                #                                                       coord_system=coordinates, mod='MD',
                #                                                       cleaning='', eroded=True)
                #
                #     # comparison FA - erosion, outliers filter
                #     subject_comparison_values_below_labels_per_region(subjects, ldm, ptb_related_regions[reg], controller_,
                #                                                       subjects_grouping_, macro_label_name=reg,
                #                                                       coord_system=coordinates, mod='FA',
                #                                                       cleaning='_no_outliers', eroded=True)
                #
                #     # comparison MD - erosion, outliers filter
                #     subject_comparison_values_below_labels_per_region(subjects, ldm, ptb_related_regions[reg], controller_,
                #                                                       subjects_grouping_, macro_label_name=reg,
                #                                                       coord_system=coordinates, mod='MD',
                #                                                       cleaning='_no_outliers', eroded=True)

# get the values of boxplot from
# https://stackoverflow.com/questions/29779079/adding-a-scatter-of-points-to-a-boxplot-using-matplotlib/43380973#43380973
