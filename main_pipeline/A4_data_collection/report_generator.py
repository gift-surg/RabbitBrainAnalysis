import os
import pandas as pa
import nibabel as nib
from collections import OrderedDict
from matplotlib import pyplot as plt
import copy

from os.path import join as jph
import cPickle as Pickle

from labels_manager.tools.descriptions.manipulate_descriptors import LabelsDescriptorManager as LdM

from labels_manager.tools.caliber.volumes_and_values import get_values_below_labels, \
    from_values_below_labels_to_volumes, from_values_below_labels_to_mu_std, get_total_volume

from tools.definitions import pfi_labels_descriptor


class ReportGenerator(object):
    """
    Report is a dictionary: {'info' : subject_info, 'measurement' : subject_measurements}
    subject_info pandas.Series
    subject_measurements pandas.DataFrame
    """
    def __init__(self):
        self.pfo_report = ''
        self.pfo_pre_report = ''

        self.list_pfi_anatomies = ''
        self.list_pfi_segmentations = ''
        self.modalities = ''
        self.sj_name = ''

        self.pfi_labels_descriptor = ''
        self.pfi_info_excel_table = ''
        self.pfo_subjects_param = ''

        self.tot_volume_prior = None

        self.verbose = 1

        self.dict_labels_names_per_group_WM_GM_CSF = {'WM': ['Midbrain', 'Globus Pallidus', 'Putamen', 'Thalamus'],
                                                      'GM': ['Frontal', 'Occipital', 'Parietal'],
                                                      'CSF': ['Ventricular system', 'Periventricular area']}

    def check_attributes(self):
        assert len(self.list_pfi_anatomies) == len(self.list_pfi_segmentations) == len(self.modalities)
        assert os.path.exists(self.pfi_labels_descriptor)
        assert os.path.exists(self.pfi_info_excel_table)
        assert os.path.exists(self.pfo_subjects_param)

    def generate_structure(self):
        os.system('mkdir -p {}'.format(self.pfo_report))
        os.system('mkdir -p {}'.format(self.pfo_pre_report))

    def generate_pre_report_each_mod(self):
        ldm = LdM(pfi_labels_descriptor)
        multi_label_dict = ldm.get_multi_label_dict(keep_duplicate=True, combine_right_left=True)
        labels_list = [multi_label_dict[l] for l in multi_label_dict.keys()]
        labels_names_list = multi_label_dict.keys()
        # labels WM GM CSF
        labels_list_WM = []
        for l in self.dict_labels_names_per_group_WM_GM_CSF['WM']:
            labels_list_WM += multi_label_dict[l]
        labels_list_GM = []
        for l in self.dict_labels_names_per_group_WM_GM_CSF['GM']:
            labels_list_GM += multi_label_dict[l]
        labels_list_CSF = []
        for l in self.dict_labels_names_per_group_WM_GM_CSF['CSF']:
            labels_list_CSF += multi_label_dict[l]

        labels_list = labels_list + [labels_list_WM] + [labels_list_GM] + [labels_list_CSF]
        labels_names_list = labels_names_list + ['WM', 'GM', 'CSF']

        # For each modality:
        for j in range(len(self.modalities)):

            if self.verbose > 0:
                print('\nPre-report modality {}'.format(self.modalities[j]))
                print('Anatomy : {} \nSegmentation : {}'.format(self.list_pfi_anatomies[j],
                                                                self.list_pfi_segmentations[j]))

            # load images:
            im_anat = nib.load(self.list_pfi_anatomies[j])
            im_seg = nib.load(self.list_pfi_segmentations[j])

            # ---  GET TOTAL VOLUME ---
            df_tot_vol = pa.DataFrame(
                {self.modalities[j]: pa.Series(get_total_volume(im_seg, labels_to_exclude=[0]),
                                               index=['Num voxels', 'Vol mm3'])}
            )
            pfi_vol_tot = jph(self.pfo_pre_report,
                              '{0}_{1}_total_volume.pickle'.format(self.sj_name, self.modalities[j]))
            with open(pfi_vol_tot, "w+") as f:
                Pickle.dump(df_tot_vol, f)

            # --- ALL LABELS ---
            # Save values below
            se_values_below_labels_all = get_values_below_labels(im_anat=im_anat, im_seg=im_seg, labels_list=labels_list,
                                                              labels_names=labels_names_list)
            pfi_all = jph(self.pfo_pre_report,
                          '{0}_{1}_values_below_labels.pickle'.format(self.sj_name, self.modalities[j]))

            pa.to_pickle(se_values_below_labels_all, pfi_all)

            # with open(pfi_all, "w+") as f:
            #     Pickle.dump(values_below_labels_all, f)

            # with open(jph(pfo_pre_report,
            # '{0}_{1}_values_below_labels.pickle'.format(sj_name, modalities[j])), "r") as f:
            #     values_below_labels_all = pickle.load(f)

            # Save volumes values
            df_volumes_all = from_values_below_labels_to_volumes(se_values_below_labels_all.values, im_seg,
                                                                 labels_list,
                                                                 labels_names_list,
                                                                 tot_volume_prior=self.tot_volume_prior)
            fi_vol_all = open(
                jph(self.pfo_pre_report,
                    '{0}_{1}_df_vol_below_labels.pickle'.format(self.sj_name, self.modalities[j])), 'w+')
            df_volumes_all.to_pickle(fi_vol_all)
            # Save mu std
            df_mu_std_all = from_values_below_labels_to_mu_std(se_values_below_labels_all.values,
                                                               labels_list,
                                                               labels_names_list)
            fi_mu_std_all = open(
                jph(self.pfo_pre_report,
                    '{0}_{1}_df_mu_std_below_labels.pickle'.format(self.sj_name, self.modalities[j])), 'w+')
            df_mu_std_all.to_pickle(fi_mu_std_all)

            del se_values_below_labels_all, pfi_all, fi_vol_all, fi_mu_std_all, df_volumes_all, df_mu_std_all, f

        # Merge all the volume measurements in one dataframe:
        pfi_vol_tot_first_mod = jph(self.pfo_pre_report,
                                    '{0}_{1}_total_volume.pickle'.format(self.sj_name, self.modalities[0]))
        df_vol_tot = pa.read_pickle(pfi_vol_tot_first_mod)

        for mod in self.modalities[1:]:
            pfi_vol_tot_mod = jph(self.pfo_pre_report, '{0}_{1}_total_volume.pickle'.format(self.sj_name, mod))
            df_vol_mod = pa.read_pickle(pfi_vol_tot_mod)
            df_vol_tot = pa.merge(df_vol_tot, df_vol_mod, how='outer', left_index=True, right_index=True)
        pfi_vol_all_mods = jph(self.pfo_pre_report, '{0}_total_volumes.pickle'.format(self.sj_name))
        df_vol_tot.to_pickle(pfi_vol_all_mods)

        # clean the volume measurement dataframes:
        for mod in self.modalities:
            pfi_vol_tot_mod = jph(self.pfo_pre_report, '{0}_{1}_total_volume.pickle'.format(self.sj_name, mod))
            os.system('rm {}'.format(pfi_vol_tot_mod))

    def pre_report2report(self):

        # -> SUBJECT INFO <-

        # Get the subject info parameters from parameter files and excel files:
        if self.pfo_subjects_param is not None and self.pfi_info_excel_table is not None:
            # load subject parameter
            sj_parameters = Pickle.load(open(jph(self.pfo_subjects_param, self.sj_name), 'r'))
            # load related excel file
            xl = pa.ExcelFile(self.pfi_info_excel_table)
            assert sj_parameters['study'] in xl.sheet_names
            df = xl.parse(sj_parameters['study'])

            df['ID Number'] = df['ID Number'].astype(str).str.replace('.', '')  # from 32.01 to '3201'
            df = df.set_index('ID Number')
            # data series for the given subject
            se_subject_info = df.loc[self.sj_name][:10]
            se_subject_info['ID Number'] = self.sj_name
        else:
            se_subject_info = pa.Series({'ID Number': self.sj_name})

        # Add volumes and ICV to the Info:
        pfi_pre_report_vols = jph(self.pfo_pre_report, '{}_total_volumes.pickle'.format(self.sj_name))
        df_pre_report_vols = pa.read_pickle(pfi_pre_report_vols)
        for mod in self.modalities:
            index_pre_report = '{} vol mm3'.format(mod)
            se_subject_info[index_pre_report] = df_pre_report_vols[mod]['Vol mm3']

        se_subject_info['Tot volume prior'] = self.tot_volume_prior

        # -> SUBJECT MEASUREMENTS <-

        # Takes the vol from the first modality and the mean standard deviation, as stand_alone
        # then it accumulates the mu and std for the subsequent modalities.
        dict_measurements = OrderedDict()
        pfi_vol_tot_first_mod = jph(self.pfo_pre_report,
                                    '{0}_{1}_df_vol_below_labels.pickle'.format(self.sj_name, self.modalities[0]))
        df_vol_tot_first_mod = pa.read_pickle(pfi_vol_tot_first_mod)

        dict_measurements.update({'label number': df_vol_tot_first_mod['Labels']})
        dict_measurements.update({'Number of Voxels': df_vol_tot_first_mod['Num voxels']})
        dict_measurements.update({'Vol over Tot': df_vol_tot_first_mod['Vol over Tot']})
        dict_measurements.update({'Volume': df_vol_tot_first_mod['Volume']})

        pfi_mu_std_tot_first_mod = jph(self.pfo_pre_report,
                                       '{0}_{1}_df_mu_std_below_labels.pickle'.format(self.sj_name, self.modalities[0]))
        df_mu_std_first_mod = pa.read_pickle(pfi_mu_std_tot_first_mod)

        dict_measurements.update({'Average {}'.format(self.modalities[0]): df_mu_std_first_mod['Average below label']})
        dict_measurements.update({'Std {}'.format(self.modalities[0]): df_mu_std_first_mod['Std below label']})

        for mod in self.modalities[1:]:
            pfi_mu_std_tot_mod = jph(self.pfo_pre_report,
                                     '{0}_{1}_df_mu_std_below_labels.pickle'.format(self.sj_name, mod))
            df_mu_std_mod = pa.read_pickle(pfi_mu_std_tot_mod)

            dict_measurements.update({'Average {}'.format(mod): df_mu_std_mod['Average below label']})
            dict_measurements.update({'Std {}'.format(mod): df_mu_std_mod['Std below label']})

        # --- Get the subject measurements:
        df_measurements = pa.DataFrame.from_dict(dict_measurements)
        report = {'Info': se_subject_info, 'Measurements': df_measurements}

        # Save:
        pfi_report = jph(self.pfo_report, '{}_report.pickle'.format(self.sj_name))
        with open(pfi_report, "w+") as f:
            Pickle.dump(report, f)

    def save_report_human_readable(self):

        pfi_report = jph(self.pfo_report, '{}_report.pickle'.format(self.sj_name))
        report = pa.read_pickle(pfi_report)
        if not os.path.exists(pfi_report):
            print('{} not generated yet'.format(pfi_report))
        else:
            report['Info'].to_string(jph(self.pfo_report, '1201_info.txt'))
            report['Measurements'].to_string(open(jph(self.pfo_report, '1201_measurements.txt'), 'w+'))

            report['Info'].to_csv(open(jph(self.pfo_report, '1201_info.csv'), 'w+'))
            report['Measurements'].to_csv(open(jph(self.pfo_report, '1201_measurements.csv'), 'w+'))

    def generate_boxplot(self, show=True):
        for mod_d, mod in enumerate(self.modalities):
            pfi_values_below_labels_mod = jph(self.pfo_pre_report, '{0}_{1}_values_below_labels.pickle'.format(self.sj_name, mod))
            se_values_below_labels_mod = pa.read_pickle(pfi_values_below_labels_mod)

            ldm = LdM(pfi_labels_descriptor)
            multi_label_dict = ldm.get_multi_label_dict(keep_duplicate=False, combine_right_left=True)

            index_subset_fig_1 = multi_label_dict.keys()

            index_subset_fig_1 = copy.deepcopy(index_subset_fig_1)
            index_subset_fig_2 =['WM', 'GM', 'CSF']

            se_values_below_labels_all = se_values_below_labels_mod.loc[index_subset_fig_1]
            se_values_below_labels_WM_GM_CSF = se_values_below_labels_mod.loc[index_subset_fig_2]

            title = 'boxplot_{0}_{1}'.format(self.sj_name, mod)
            graph_title = 'Values below label subject {0}, modality {1}'.format(self.sj_name, mod)

            fig = plt.figure(mod_d, figsize=(14, 7), dpi=80, facecolor='w', edgecolor='k')
            fig.subplots_adjust(left=0.075, right=0.95, top=0.9, bottom=0.25)
            # set title
            fig.canvas.set_window_title(title)

            # boxplot 1
            ax0 = fig.add_subplot(111)
            ax0.boxplot(se_values_below_labels_all.values)
            ax0.set_xticklabels(se_values_below_labels_all.index, rotation=90)

            # # boxplot 1
            # ax1 = fig.add_subplot(122)
            # ax1.boxplot(se_values_below_labels_WM_GM_CSF.values)
            # ax1.set_xticklabels(se_values_below_labels_WM_GM_CSF.index, rotation=30)

            fig.suptitle(graph_title)

            fig.savefig(jph(self.pfo_pre_report, graph_title + '.png'))
            if show:
                plt.show(block=True)


if __name__ == '__main__':

    from tools.definitions import pfo_subjects_parameters, pfi_labels_descriptor, root_study_rabbits

    selected_segmentation_suffix = '_IN_TEMPLATE'
    sj = '1201'

    sj_parameters = Pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))
    study = sj_parameters['study']
    category = sj_parameters['category']

    pfo_data_sj = jph(root_study_rabbits, 'A_data', study, category, sj)

    rg = ReportGenerator()

    rg.sj_name = sj
    rg.pfo_report = jph(pfo_data_sj, 'report')
    rg.pfo_pre_report = jph(pfo_data_sj, 'report', 'z_pre_report')

    pfi_T1 = jph(pfo_data_sj, 'mod', '{}_T1.nii.gz'.format(sj))
    pfi_g_ratio = jph(pfo_data_sj, 'mod', '{}_g_ratio.nii.gz'.format(sj))
    pfi_FA = jph(pfo_data_sj, 'mod', '{}_FA.nii.gz'.format(sj))
    pfi_MD = jph(pfo_data_sj, 'mod', '{}_MD.nii.gz'.format(sj))
    pfi_T2map = jph(pfo_data_sj, 'mod', '{}_T2map.nii.gz'.format(sj))

    rg.list_pfi_anatomies     = [pfi_T1, pfi_g_ratio, pfi_FA, pfi_MD, pfi_T2map]

    pfo_automatic_segm = jph(pfo_data_sj, 'segm', 'automatic')
    pfi_T1_segm = jph(pfo_automatic_segm, '{0}_T1_segm{1}.nii.gz'.format(sj, selected_segmentation_suffix))
    pfi_g_ratio_segm = jph(pfo_automatic_segm, '{0}_S0_segm{1}.nii.gz'.format(sj, selected_segmentation_suffix))
    pfi_FA_segm = pfi_g_ratio_segm
    pfi_MD_segm = pfi_g_ratio_segm
    pfi_T2map_segm = pfi_g_ratio_segm

    rg.list_pfi_segmentations = [pfi_T1_segm, pfi_g_ratio_segm, pfi_FA_segm, pfi_MD_segm, pfi_T2map_segm]
    rg.modalities = ['T1', 'g_ratio', 'FA', 'MD', 'T2map']

    rg.pfi_labels_descriptor = pfi_labels_descriptor
    rg.pfi_info_excel_table = jph(root_study_rabbits, 'A_data', 'DataSummary.xlsx')
    rg.pfo_subjects_param = pfo_subjects_parameters
    rg.tot_volume_prior = None
    rg.verbose = 1

    rg.check_attributes()
    rg.generate_structure()

    # rg.generate_pre_report_each_mod()
    # rg.pre_report2report()
    # rg.save_report_human_readable()

    rg.generate_boxplot()
