import os
import numpy as np
import pandas as pa
import pickle
from os.path import join as jph
import seaborn as sns
import matplotlib.pyplot as plt
from collections import OrderedDict

from nilabels.tools.aux_methods.label_descriptor_manager import LabelsDescriptorManager as LdM

from tools.definitions import root_study_rabbits, pfo_subjects_parameters, pfi_labels_descriptor


root_output = jph(root_study_rabbits, 'B_stats', 'W8_LACS_Saline')  # W8_LACS_Saline


def subject_comparison_total_volume(sj_list, controller, subjects_grouping=None, legend=None, coord_system='original',
                                    axis_title='Brain volume per subject'):
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

        barlist = ax.bar(range(len(sj_list)), df_tot_vols_subjects['volume'].as_matrix())

        if subjects_grouping is not None:

            if legend is not None:
                assert len(subjects_grouping) == len(legend)

            colors = ['b', 'g', 'c', 'm', 'y']
            for nk in range(len(subjects_grouping)):
                for k in range(subjects_grouping[nk]):
                    bar_num = sum(subjects_grouping[:nk]) + k
                    barlist[bar_num].set_color(colors[nk % len(colors)])
                    if legend is not None and k == 0:
                        barlist[bar_num].set_label(legend[nk])

            assert np.sum(subjects_grouping) == len(subjects)
            vals = df_tot_vols_subjects['volume'].as_matrix()

            cumulative_grouping = np.cumsum([0] + subjects_grouping)
            vals_grouped = [[vals[l] for l in range(cumulative_grouping[k], cumulative_grouping[k + 1])]
                            for k in range(len(cumulative_grouping) - 1)]
            medians_of_vals_grouped = [np.median(li) for li in vals_grouped]

            for i, m in enumerate(medians_of_vals_grouped):
                ax.hlines(y=m, xmin=cumulative_grouping[i] - 0.3, xmax=cumulative_grouping[i + 1] - 0.7,
                          color='r', alpha=0.5, linestyles='dashed')

        ax.set_title(axis_title + ' ({})'.format(coord_system))
        ax.set_ylabel('vol (mm^3)')
        ax.set_xlabel('Subject Id')
        ax.set_xticks(range(len(sj_list)))
        ax.set_xticklabels(sj_list, ha='center', rotation=45, fontsize=10)
        ax.xaxis.labelpad = 20

        if legend is not None:
            ax.legend(loc="lower right", frameon=True)

        plt.tight_layout()

        plt.savefig(jph(root_output, 'brain_volume_per_subject{}.pdf'.format(coord_system)), format='pdf', dpi=200)

        plt.close()


def subject_comparison_volume_per_region(sj_list, ldm, labels_num, controller, subjects_grouping=None, macro_label_name=None,
                                         coord_system='original', cleaning=None, axis_title='Brain volume per subject'):
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
    dict_labels = ldm.get_dict_itk_snap()
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

        barlist = ax.bar(range(len(sj_list)), df_tot_vols_subjects['Volume'].as_matrix())

        if subjects_grouping is not None:

            if legend is not None:
                assert len(subjects_grouping) == len(legend)

            colors = ['b', 'g', 'c', 'm', 'y']
            for nk in range(len(subjects_grouping)):
                for k in range(subjects_grouping[nk]):
                    bar_num = sum(subjects_grouping[:nk]) + k
                    barlist[bar_num].set_color(colors[nk % len(colors)])
                    if legend is not None and k == 0:
                        barlist[bar_num].set_label(legend[nk])

            assert np.sum(subjects_grouping) == len(subjects)
            vals = df_tot_vols_subjects['Volume'].as_matrix()

            cumulative_grouping = np.cumsum([0] + subjects_grouping)
            vals_grouped = [[vals[l] for l in range(cumulative_grouping[k], cumulative_grouping[k+1])] for k in range(len(cumulative_grouping) - 1)]
            medians_of_vals_grouped = [np.median(li) for li in vals_grouped]

            for i, m in enumerate(medians_of_vals_grouped):
                ax.hlines(y=m, xmin=cumulative_grouping[i], xmax=cumulative_grouping[i+1] - 1, color='r', alpha=0.5, linestyles='dashed')

        ax.set_title(axis_title + ' - region {} ({})'.format(macro_label_name, coord_system))
        ax.set_ylabel('vol (mm^3)')
        ax.set_xlabel('Subject Id')
        ax.set_xticks(range(len(sj_list)))
        ax.set_xticklabels(sj_list, ha='center', rotation=45, fontsize=10)
        ax.xaxis.labelpad = 20

        if legend is not None:
            ax.legend(loc="lower right", frameon=True)

        plt.tight_layout()

        plt.savefig(jph(root_output, 'VOLregion{}_{}.pdf'.format(macro_label_name, coord_system)),
                    format='pdf', dpi=200)
        plt.close()


def subject_comparison_values_below_labels_per_region(sj_list, ldm, labels_num, controller, subjects_grouping=None,
                                                      macro_label_name=None, coord_system='original', mod='FA',
                                                      cleaning='', eroded=False, axis_title='Values ', legend=None):
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

    dict_labels = ldm.get_dict_itk_snap()
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

        if subjects_grouping is None:

           ax.boxplot([tot_data_distribution[k] for k in sj_list])

        else:

            if legend is not None:
                assert len(subjects_grouping) == len(legend)

            colors = ['b', 'g', 'c', 'm', 'y']

            patch_artist = []

            for nk in range(len(subjects_grouping)):
                bar_pos = []
                for k in range(subjects_grouping[nk]):
                    bar_num = sum(subjects_grouping[:nk]) + k
                    bar_pos.append(bar_num)

                patch_box = ax.boxplot([tot_data_distribution[k] for k in [sj_list[m] for m in bar_pos]],
                                       positions=[p + 1 for p in bar_pos], notch=True, patch_artist=True)
                for bp in patch_box['boxes']:
                    bp.set_facecolor(colors[nk])
                patch_artist.append(patch_box['boxes'][0])

            assert np.sum(subjects_grouping) == len(subjects)
            medians = [np.median(tot_data_distribution[k]) for k in sj_list]
            cumulative_grouping = np.cumsum([0] + subjects_grouping)
            medians_grouped = [[medians[l] for l in range(cumulative_grouping[k], cumulative_grouping[k+1])] for k in range(len(cumulative_grouping) - 1)]
            medians_of_medians_grouped = [np.median(li) for li in medians_grouped]

            for i, m in enumerate(medians_of_medians_grouped):
                ax.hlines(y=m, xmin=cumulative_grouping[i] + 1, xmax=cumulative_grouping[i+1], color='r', alpha=0.5, linestyles='dashed')

        ax.set_title(axis_title + ' {} per region {}'.format(mod, macro_label_name))
        ax.set_ylabel('{}'.format(mod))
        ax.set_xlabel('Subject Id')
        ax.set_xticks(range(1, len(tot_data_distribution.keys())+1))
        ax.set_xticklabels(sj_list, ha='center', rotation=45, fontsize=10)
        ax.xaxis.labelpad = 20

        ax.set_xlim(left=0.5, right=len(sj_list) + 0.5)

        if legend is not None:
            ax.legend(patch_artist, legend, loc='upper left', frameon=True)

        plt.tight_layout()

        # plt.show()

        if eroded:
            pfi_where_to_save_fig = jph(root_output, '{}region{}_{}{}_eroded.pdf'.format(mod, macro_label_name, coord_system, cleaning))
        else:
            pfi_where_to_save_fig = jph(root_output, '{}region{}_{}{}.pdf'.format(mod, macro_label_name, coord_system, cleaning))

        plt.savefig(pfi_where_to_save_fig, format='pdf', dpi=100)
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

    subjects_not_present = []

    # --------- BELOW: W8 three trials: ---------

    # subjects_A = ['12503', '5302', '5303', '5508', '5510', '55BW']
    # subjects_B = ['13601', '13603', '13604', '13605', '13610', '13701', '13706', '13707', '13709']
    # subjects_C = ['14101', '14402', '14403', '14503', '14504', '14603']
    #
    # subjects = subjects_A + subjects_B + subjects_C
    # subjects_grouping_ = [len(subjects_A), len(subjects_B), len(subjects_C)]
    # legend = ['trial1', 'trial2', 'trial3']

    # ---------- BELOW subjects Saline, ACS: ------------

    LACS = ['12503', '13701', '13706', '13707', '13709', '14503', '14504', '14603']
    saline = ['13601', '13602', '13603', '13604', '13605', '14401', '14402', '14403',  '14302', '14301']
    T = ['55BW', '13610', '14101', '14203']
    PT = ['5302', '5303', '5508', '5510']

    subjects = LACS + saline + T + PT
    subjects_grouping_ = [len(LACS), len(saline), len(T), len(PT)]
    legend = ['LACS', 'Saline', 'Term', 'PreTerm']

    # -----------------------------------------------------

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
                                        coord_system='stereotaxic', legend=legend)

    if True:
        # single regions volume across subjects as histogram:
        for reg in ptb_related_regions.keys():

            for coordinates in ['stereotaxic']:  # 'original',
                subject_comparison_volume_per_region(subjects, ldm, ptb_related_regions[reg], controller_,
                                                     subjects_grouping_, macro_label_name=reg, coord_system=coordinates,
                                                     cleaning=None)

    if True:
        for reg in ptb_related_regions.keys():

            print('\n\n---- REGION {} ----'.format(reg))

            for coordinates in ['stereotaxic']:  # 'original',

                # # ---- Without erosion

                # comparison FA - no erosion, no outliers filter
                subject_comparison_values_below_labels_per_region(subjects, ldm, ptb_related_regions[reg], controller_,
                                                                  subjects_grouping_, macro_label_name=reg,
                                                                  coord_system=coordinates, mod='FA',
                                                                  cleaning='', eroded=False, legend=legend)

                # comparison MD - no erosion, no outliers filter
                subject_comparison_values_below_labels_per_region(subjects, ldm, ptb_related_regions[reg], controller_,
                                                                  subjects_grouping_, macro_label_name=reg,
                                                                      coord_system=coordinates, mod='MD',
                                                                      cleaning='', eroded=False, legend=legend)

                # # comparison FA - no erosion, outliers filter
                # subject_comparison_values_below_labels_per_region(subjects, ldm, ptb_related_regions[reg], controller_,
                #                                                   subjects_grouping_, macro_label_name=reg,
                #                                                   coord_system=coordinates, mod='FA',
                #                                                   cleaning='_no_outliers', eroded=False)
                #
                # # comparison MD - no erosion, outliers filter
                # subject_comparison_values_below_labels_per_region(subjects, ldm, ptb_related_regions[reg], controller_,
                #                                                   subjects_grouping_, macro_label_name=reg,
                #                                                   coord_system=coordinates, mod='MD',
                #                                                   cleaning='_no_outliers', eroded=False)

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
