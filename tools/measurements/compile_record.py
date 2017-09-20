import os
import pandas as pd

from os.path import join as jph
import pickle

from labels_manager.tools.descriptions.manipulate_descriptors import LabelsDescriptorManager as LDM
from labels_manager.main import LabelsManagerMeasure as LMM

from tools.definitions import pfo_subjects_parameters, pfi_labels_descriptor


def get_rabbit_record(list_pfi_anatomies,
                      list_pfi_segmentations,
                      indexes,
                      subject_name,
                      pfi_label_descriptor,
                      pfi_info_excel_table,
                      pfo_subjects_param=None,
                      tot_volume_prior=None,
                      verbose=1):
    """
    :param list_pfi_anatomies:
    :param list_pfi_segmentations:
    :param subject_name:
    :param pfi_label_descriptor:
    :param pfi_info_excel_table:
    :param pfo_subjects_param:
    :param tot_volume_prior: if there is a prior on the total volume.
    (this parameter should be created from the ICV estimator and loaded from a dataset in subsequent steps).
    :param verbose:
    :return: rabbit record
    A rabbit record is a dictionary of the form
    {'Subject info': se_subject_info, 'Measurements' : measurements}
    where se_subject_info is a pandas Series containing the data parsed from the info files
    in the excel table and measurements is a pandas dataframe with the relevant information.
    """

    # -- sanity check input

    assert len(list_pfi_anatomies) == len(list_pfi_segmentations) == len(indexes)

    # --- Get the subject info parameters:

    if pfo_subjects_param is not None and pfi_info_excel_table is not None:
        # load subject parameter
        sj_parameters = pickle.load(open(jph(pfo_subjects_param, subject_name), 'r'))
        # load related excel file
        xl = pd.ExcelFile(pfi_info_excel_table)
        assert sj_parameters['study'] in xl.sheet_names
        df = xl.parse(sj_parameters['study'])
        # from 32.01 to '3201'
        df['ID Number'] = df['ID Number'].astype(str).str.replace('.', '')
        df = df.set_index('ID Number')
        # data series for the given subject
        se_subject_info = df.loc[subject_name][:10]
        se_subject_info['ID Number'] = subject_name
    else:
        se_subject_info = pd.Series({'ID Number': subject_name})

    # --- Get the subject measurements:

    measurements = {}

    ldm = LDM(pfi_label_descriptor)
    multi_label_dict = ldm.get_multi_label_dict(keep_duplicate=True, combine_right_left=True)

    for pfi_anat, pfi_segm, ind in zip(list_pfi_anatomies, list_pfi_segmentations, indexes):

        if verbose > 0:
            print('\nAnalysis index {}'.format(ind))
            print('Anatomy : {}, \nSegmentation : {}'.format(pfi_anat, pfi_segm))

        if os.path.exists(pfi_segm) and os.path.exists(pfi_anat):
            m = LMM()
            df_vol = m.volume(segmentation_filename=pfi_segm, labels=multi_label_dict, anatomy_filename=pfi_anat,
                              tot_volume_prior=tot_volume_prior, where_to_save=None)

            del m
        else:
            df_vol = None  # No dataframe if the file does not exist...

        measurements.update({ind : df_vol})

    return {'Subject info': se_subject_info, 'Measurements' : measurements, 'labels' : multi_label_dict}


def save_rabbit_record(rabbit_record, pfo_root_subject, join_measurements=True, verbose=1):
    """
    Save by default in .csv in .pickle and in .txt for human readable.
    :param rabbit_record:
    :param pfo_output:
    :param join_measurements: join measurements in a single dataframe. can be False for debug purposes to see
    what is going on in each individual region.
    :return:
    """

    # -- Generate output folder
    pfo_output_record = jph(pfo_root_subject, 'records')
    os.system('mkdir -p {}'.format(pfo_output_record))

    # -- get output filename
    id_number = rabbit_record['Subject info']['ID Number']
    fin_output = '{}_record'.format(id_number)

    # -- save in .pickle -
    with open(jph(pfo_output_record, '{}.pickle'.format(fin_output)), 'wb') as handle:
        pickle.dump(rabbit_record, handle, protocol=pickle.HIGHEST_PROTOCOL)

    if not join_measurements:
        # -- save in csv
        rabbit_record['Subject info'].to_csv(jph(pfo_output_record, 'subject_info_{}.csv'.format(fin_output)))
        for k in rabbit_record['Measurements'].keys():
            if rabbit_record['Measurements'][k] is not None:
                rabbit_record['Measurements'][k].to_csv(jph(pfo_output_record, '{0}_{1}.csv'.format(fin_output, k)))

    else:

        # join measurements in a single dataset
        # here it saves as well in txt
        pass

if __name__ == '__main__':
    root_main_pantopolium = '/Volumes/sebastianof/'
    root_study_rabbits = jph(root_main_pantopolium, 'rabbits')
    root_study_rabbits = jph(root_main_pantopolium, 'rabbits')

    pfi_info_excel_table = jph(root_study_rabbits, 'A_data', 'DataSummary.xlsx')
    subject_name = '3103'

    pfo_data_sj       = jph(root_study_rabbits, 'A_data', 'ACS', 'ex_vivo', subject_name)

    pfi_T1            = jph(pfo_data_sj, 'mod', '{}_T1.nii.gz'.format(subject_name))
    pfi_g_ratio       = jph(pfo_data_sj, 'mod', '{}_g_ratio.nii.gz'.format(subject_name))
    pfi_FA            = jph(pfo_data_sj, 'mod', '{}_FA.nii.gz'.format(subject_name))
    pfi_MD            = jph(pfo_data_sj, 'mod', '{}_MD.nii.gz'.format(subject_name))
    pfi_T2map_up      = jph(pfo_data_sj, 'mod', '{}_T2map_up.nii.gz'.format(subject_name))

    suffix_segmentaion = '_MV_s'
    pfo_automatic_segm = jph(pfo_data_sj, 'segm', 'automatic')

    pfi_T1_segm       = jph(pfo_automatic_segm, '{0}_T1_segm{1}.nii.gz'.format(subject_name, suffix_segmentaion))
    pfi_g_ratio_segm  = jph(pfo_automatic_segm, '{0}_S0_segm{1}.nii.gz'.format(subject_name, suffix_segmentaion))
    pfi_FA_segm       = pfi_g_ratio_segm
    pfi_MD_segm       = pfi_g_ratio_segm
    pfi_T2map_up_segm = pfi_g_ratio_segm

    list_pfi_anatomies = [pfi_T1, pfi_g_ratio, pfi_FA, pfi_MD, pfi_T2map_up]
    list_pfi_segmentations = [pfi_T1_segm, pfi_g_ratio_segm, pfi_FA_segm, pfi_MD_segm, pfi_T2map_up_segm]
    indexes = ['T1', 'g_ratio', 'FA', 'MD', 'T2map']

    print list_pfi_anatomies
    print list_pfi_segmentations
    print indexes

    rec = get_rabbit_record(list_pfi_anatomies=list_pfi_anatomies,
                            list_pfi_segmentations=list_pfi_segmentations,
                            indexes=indexes,
                            subject_name=subject_name,
                            pfi_label_descriptor=pfi_labels_descriptor,
                            pfi_info_excel_table=pfi_info_excel_table,
                            pfo_subjects_param=pfo_subjects_parameters,
                            verbose=1)

    # with open('/Users/sebastiano/Desktop/tmp.pickle', 'wb') as handle:
    #     pickle.dump(rec, handle, protocol=pickle.HIGHEST_PROTOCOL)
    #
    # with open('/Users/sebastiano/Desktop/tmp.pickle', 'rb') as handle:
    #     rec = pickle.load(handle)

    save_rabbit_record(rec, pfo_data_sj, join_measurements=False)
