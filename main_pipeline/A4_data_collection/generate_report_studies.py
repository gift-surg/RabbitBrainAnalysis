import os
import pandas as pd
import nibabel as nib

from os.path import join as jph
import pickle

from labels_manager.tools.descriptions.manipulate_descriptors import LabelsDescriptorManager as LDM
from labels_manager.main import LabelsManagerMeasure as LMM

from labels_manager.tools.caliber.volumes_and_values import get_values_below_labels, \
    from_values_below_labels_to_volumes, from_values_below_labels_to_mu_std

from tools.definitions import pfo_subjects_parameters, pfi_labels_descriptor


labels_per_group_WM_GM_CSF = {'WM'  : ['Midbrain', 'Globus Pallidus', 'Putamen', 'Thalamus'],  # In-progress myelination
                              'GM'  : ['Frontal', 'Occipital', 'Parietal'],
                              'CSF' : ['Ventricular system', 'Periventricular area']}   # PBS for the ex - vivo rather than CSF


def generate_pre_report_each_mod(pfo_report,
                                 list_pfi_anatomies,
                                 list_pfi_segmentations,
                                 modalities,
                                 sj_name,
                                 pfi_labels_descriptor,
                                 tot_volume_prior=None,
                                 verbose=1):

    pfo_pre_report = jph(pfo_report, 'z_pre_reports')

    # -- sanity check input
    assert len(list_pfi_anatomies) == len(list_pfi_segmentations) == len(modalities)

    if tot_volume_prior is None:
        tot_volume_prior = [None, ] * len(modalities)

    ldm = LDM(pfi_labels_descriptor)
    multi_label_dict = ldm.get_multi_label_dict(keep_duplicate=True, combine_right_left=True)
    labels_list = [multi_label_dict[l] for l in multi_label_dict.keys()]
    labels_list_WM = []
    for l in labels_per_group_WM_GM_CSF['WM']:
        labels_list_WM += multi_label_dict[l]
    labels_list_GM = []
    for l in labels_per_group_WM_GM_CSF['GM']:
        labels_list_GM += multi_label_dict[l]
    labels_list_CSF = []
    for l in labels_per_group_WM_GM_CSF['CSF']:
        labels_list_CSF += multi_label_dict[l]

    # For each modality:
    for j in range(len(modalities)):

        if verbose > 0:
            print('\nPre-report modality {}'.format(modalities[j]))
            print('Anatomy : {} \nSegmentation : {}'.format(list_pfi_anatomies[j], list_pfi_segmentations[j]))

        # load images:
        im_anat = nib.load(list_pfi_anatomies[j])
        im_seg = nib.load(list_pfi_segmentations[j])

        # --- ALL LABELS ---
        # Save values below
        values_below_labels_all = get_values_below_labels(im_anat=im_anat, im_seg=im_seg, labels_list=labels_list)
        fi_all = open(jph(pfo_pre_report, 'z_{0}_{1}_values_below_labels.pickle'.format(sj_name, modalities[j])), 'w+')
        pickle.dump(values_below_labels_all, fi_all)

        # Save volumes values
        df_volumes_all = from_values_below_labels_to_volumes(values_below_labels_all, im_seg, labels_list,
                                                         multi_label_dict.keys(), tot_volume_prior=tot_volume_prior[j])
        fi_vol_all = open(jph(pfo_pre_report, 'z_{0}_{1}_df_vol_below_labels.pickle'.format(sj_name, modalities[j])), 'w+')
        df_volumes_all.to_pickle(fi_vol_all)

        # Save mu std
        df_mu_std = from_values_below_labels_to_mu_std(values_below_labels_all, labels_list, multi_label_dict.keys())
        fi_mu_std_all = open(jph(pfo_pre_report, 'z_{0}_{1}_df_msu_std_below_labels.pickle'.format(sj_name, modalities[j])) , 'w+')
        df_mu_std.to_pickle(df_mu_std, fi_mu_std_all)

        del values_below_labels_all, fi_all, fi_vol_all, fi_mu_std_all, df_volumes_all, df_mu_std

        # --- WM LABELS ---

        # Save values below labels
        values_below_labels_WM = get_values_below_labels(im_anat=im_anat, im_seg=im_seg, labels_list=labels_list_WM)
        fi = open(jph(pfo_pre_report, 'z_{0}_{1}_values_below_labels_WM.pickle'.format(sj_name, modalities[j])), 'w+')
        pickle.dump(values_below_labels_WM, fi)

        # Save volumes values

        # Save mu std



        del values_below_labels_WM, fi

        # --- GM LABELS ---

        # Save values below labels GM
        values_below_labels_GM = get_values_below_labels(im_anat=im_anat, im_seg=im_seg, labels_list=labels_list_GM)
        fi = open(jph(pfo_pre_report, 'z_{0}_{1}_values_below_labels_WM.pickle'.format(sj_name, modalities[j])), 'w+')
        pickle.dump(values_below_labels_GM, fi)

        # Save volumes values

        # Save mu std


        del values_below_labels_GM, fi

        # --- CSF LABELS ---

        # Save values below labels CSF
        values_below_labels_CSF = get_values_below_labels(im_anat=im_anat, im_seg=im_seg, labels_list=labels_list_CSF)
        fi = open(jph(pfo_pre_report, 'z_{0}_{1}_values_below_labels_WM.pickle'.format(sj_name, modalities[j])), 'w+')
        pickle.dump(values_below_labels_CSF, fi)

        # Save volumes values

        # Save mu std

        del values_below_labels_CSF, fi


def merge_pre_reports(pfo_report, sj_name, sub_list_modalities, pfi_info_excel_table, pfo_subjects_param, verbose):

    # --- Get the subject info parameters from parameter files and excel files:

    if pfo_subjects_param is not None and pfi_info_excel_table is not None:
        # load subject parameter
        sj_parameters = pickle.load(open(jph(pfo_subjects_param, sj_name), 'r'))
        # load related excel file
        xl = pd.ExcelFile(pfi_info_excel_table)
        assert sj_parameters['study'] in xl.sheet_names
        df = xl.parse(sj_parameters['study'])
        # from 32.01 to '3201'
        df['ID Number'] = df['ID Number'].astype(str).str.replace('.', '')
        df = df.set_index('ID Number')
        # data series for the given subject
        se_subject_info = df.loc[sj_name][:10]
        se_subject_info['ID Number'] = sj_name
    else:
        se_subject_info = pd.Series({'ID Number': sj_name})

    # --- Get the subject measurements:

    # TODO combine measurement dictionary in a single dataframe

    return {'Subject info': se_subject_info}


def generate_boxplot():
    pass


def erase_intermediate():
    pass






if __name__ == '__main__':
    root_main_pantopolium = '/Volumes/sebastianof/'
    root_study_rabbits = jph(root_main_pantopolium, 'rabbits')
    root_study_rabbits = jph(root_main_pantopolium, 'rabbits')

    pfi_info_excel_table = jph(root_study_rabbits, 'A_data', 'DataSummary.xlsx')
    sj_name = '1201'

    pfo_data_sj       = jph(root_study_rabbits, 'A_data', 'PTB', 'ex_vivo', sj_name)

    pfi_T1            = jph(pfo_data_sj, 'mod', '{}_T1.nii.gz'.format(sj_name))
    pfi_g_ratio       = jph(pfo_data_sj, 'mod', '{}_g_ratio.nii.gz'.format(sj_name))
    pfi_FA            = jph(pfo_data_sj, 'mod', '{}_FA.nii.gz'.format(sj_name))
    pfi_MD            = jph(pfo_data_sj, 'mod', '{}_MD.nii.gz'.format(sj_name))
    pfi_T2map         = jph(pfo_data_sj, 'mod', '{}_T2map_up.nii.gz'.format(sj_name))

    suffix_segmentaion = '_IN_TEMPLATE'
    pfo_automatic_segm = jph(pfo_data_sj, 'segm', 'automatic')

    pfi_T1_segm       = jph(pfo_automatic_segm, '{0}_T1_segm{1}.nii.gz'.format(sj_name, suffix_segmentaion))
    pfi_g_ratio_segm  = jph(pfo_automatic_segm, '{0}_S0_segm{1}.nii.gz'.format(sj_name, suffix_segmentaion))
    pfi_FA_segm       = pfi_g_ratio_segm
    pfi_MD_segm       = pfi_g_ratio_segm
    pfi_T2map_segm    = pfi_g_ratio_segm

    list_pfi_anatomies = [pfi_T1, pfi_g_ratio, pfi_FA, pfi_MD, pfi_T2map]
    list_pfi_segmentations = [pfi_T1_segm, pfi_g_ratio_segm, pfi_FA_segm, pfi_MD_segm, pfi_T2map_segm]
    modalities = ['T1', 'g_ratio', 'FA', 'MD', 'T2map']

    print list_pfi_anatomies
    print list_pfi_segmentations
    print modalities

    pfo_report = jph(pfo_data_sj, 'report')
    os.system('mkdir -p {}'.format(pfo_report))

    generate_pre_report_each_mod(pfo_report,
                                   list_pfi_anatomies=list_pfi_anatomies,
                                   list_pfi_segmentations=list_pfi_segmentations,
                                   sj_name=sj_name,
                                   pfi_labels_descriptor=pfi_labels_descriptor,
                                   modalities=modalities)

    # rep = get_rabbit_report(list_pfi_anatomies=list_pfi_anatomies,
    #                         list_pfi_segmentations=list_pfi_segmentations,
    #                         modalities=modalities,
    #                         sj_name=sj_name,
    #                         pfi_label_descriptor=pfi_labels_descriptor,
    #                         pfi_info_excel_table=pfi_info_excel_table,
    #                         pfo_subjects_param=pfo_subjects_parameters,
    #                         verbose=1)
    #
    # # with open('/Users/sebastiano/Desktop/tmp.pickle', 'wb') as handle:
    # #     pickle.dump(rec, handle, protocol=pickle.HIGHEST_PROTOCOL)
    # #
    # # with open('/Users/sebastiano/Desktop/tmp.pickle', 'rb') as handle:
    # #     rec = pickle.load(handle)
    #
    # save_rabbit_report(rep, pfo_data_sj, join_measurements=False)
