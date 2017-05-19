import os
from os.path import join as jph
import numpy as np

from tools.measurements.compile_record import compile_record
from definitions import root_docs_dropbox, root_pilot_study_pantopolium


def compile_record_per_group(pfo_input_data, pfo_output_record, tuple_subjects=()):
    assert os.path.exists(pfo_input_data)
    subj_list = np.sort(list(set(os.listdir(pfo_input_data)) - {'.DS_Store'}))
    if not tuple_subjects == ():
        subj_list = tuple_subjects

    print '\n\n Collecting data for a group of subjects. ' \
          'Target group folder {0}\n' \
          'Subjects {1}\n'.format(pfo_input_data, subj_list)

    for sj in subj_list:
        pfo_sj = jph(pfo_input_data, sj)
        pfo_output_record_sj = jph(pfo_output_record, sj)

        # grab modalities
        pfi_T1 = jph(pfo_sj, 'all_modalities', sj + '_T1.nii.gz')
        pfi_FA = jph(pfo_sj, 'all_modalities', sj + '_FA.nii.gz')
        pfi_ADC = jph(pfo_sj, 'all_modalities', sj + '_MD.nii.gz')
        assert os.path.exists(pfi_T1)
        assert os.path.exists(pfi_FA)
        assert os.path.exists(pfi_ADC)
        # grab segmentations
        pfi_segm_T1_sj = jph(pfo_sj, 'segm', sj + '_T1.nii.gz')
        pfi_segm_S0_sj = jph(pfo_sj, 'segm', sj + '_S0.nii.gz')
        assert os.path.exists(pfi_segm_T1_sj)
        assert os.path.exists(pfi_segm_S0_sj)
        # grab label descriptor
        pfi_multi_labels_descr = jph(root_pilot_study_pantopolium, 'A_data', 'Utils', 'multi_label_descriptor.txt')
        assert os.path.exists(pfi_multi_labels_descr)
        # grab excel table
        pfi_excel_table = jph(root_docs_dropbox, 'REoP_Pilot_MRI_Data.xlsx')
        assert os.path.exists(pfi_excel_table)

        print '\n\n DATA PARSING SUBJECT {} \n\n'.format(sj)

        # Compile records
        compile_record(pfi_T1=pfi_T1,
                       pfi_FA=pfi_FA,
                       pfi_ADC=pfi_ADC,
                       pfi_multi_lab_descriptor=pfi_multi_labels_descr,
                       pfi_segm_T1=pfi_segm_T1_sj,
                       pfi_segm_FA=pfi_segm_S0_sj,
                       pfi_segm_ADC=pfi_segm_S0_sj,
                       pfi_excel_table=pfi_excel_table,
                       subject_name=sj,
                       pfo_output=pfo_output_record_sj,
                       save_human_readable=True,
                       create_output_folder_if_not_present=True
                       )


def compile_record_all(extract_data_PTB_ex_skull=True,
                       extract_data_PTB_ex_vivo=True,
                       extract_data_PTB_in_vivo=True,
                       extract_data_PTB_op_skull=True,
                       extract_data_ACS_ex_vivo=True):

    print root_pilot_study_pantopolium
    root_data    = jph(root_pilot_study_pantopolium, 'A_data')
    root_records = jph(root_pilot_study_pantopolium, 'B_records')

    if extract_data_PTB_ex_skull:
        pfo_PTB_ex_skull_data = jph(root_data, 'PTB', 'ex_skull')
        pfo_PTB_ex_skull_records = jph(root_records, 'PTB', 'ex_skull')
        # ---------------
        tuple_subjects = ()  # can force the input to a predefined input list of subjects if they exists.
        # ---------------
        compile_record_per_group(pfo_PTB_ex_skull_data, pfo_PTB_ex_skull_records, tuple_subjects)

    if extract_data_PTB_ex_vivo:
        pfo_PTB_ex_vivo_data = jph(root_data, 'PTB', 'ex_vivo')
        pfo_PTB_ex_vivo_records = jph(root_records, 'PTB', 'ex_vivo')
        # ---------------
        tuple_subjects = ()
        # ---------------
        compile_record_per_group(pfo_PTB_ex_vivo_data, pfo_PTB_ex_vivo_records, tuple_subjects)

    if extract_data_PTB_in_vivo:
        pfo_PTB_in_vivo_data = jph(root_data, 'PTB', 'in_vivo')
        pfo_PTB_in_vivo_records = jph(root_records, 'PTB', 'in_vivo')
        # ---------------
        tuple_subjects = ()
        # ---------------
        compile_record_per_group(pfo_PTB_in_vivo_data, pfo_PTB_in_vivo_records, tuple_subjects)

    if extract_data_PTB_op_skull:
        pfo_PTB_op_skull_data = jph(root_data, 'PTB', 'op_skull')
        pfo_PTB_op_skull_records = jph(root_records, 'PTB', 'op_skull')
        # ---------------
        tuple_subjects = ()
        # ---------------
        compile_record_per_group(pfo_PTB_op_skull_data, pfo_PTB_op_skull_records, tuple_subjects)

    if extract_data_ACS_ex_vivo:
        pfo_ACS_ex_vivo_data = jph(root_data, 'ACS', 'ex_vivo')
        pfo_ACS_ex_vivo_records = jph(root_records, 'ACS', 'ex_vivo')
        # ---------------
        tuple_subjects = ()
        # ---------------
        compile_record_per_group(pfo_ACS_ex_vivo_data, pfo_ACS_ex_vivo_records, tuple_subjects)


if __name__ == '__main__':
    compile_record_all(extract_data_PTB_ex_skull=True,
                       extract_data_PTB_ex_vivo=True,
                       extract_data_PTB_in_vivo=True,
                       extract_data_PTB_op_skull=True,
                       extract_data_ACS_ex_vivo=True)
