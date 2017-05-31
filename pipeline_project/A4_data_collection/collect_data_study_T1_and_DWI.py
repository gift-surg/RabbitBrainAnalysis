import os
from os.path import join as jph

from definitions import pfi_excel_table_ACS, root_study_rabbits, pfi_excel_table_PTB
from pipeline_project.A0_main.main_controller import ListSubjectsManager, subject
from tools.measurements.compile_record import compile_record


def compile_record_T1_DWI_from_subject_list(subj_list):

    print '\n\n Collecting data subjects in the list {}'.format(subj_list)

    for sj in subj_list:
        # grab modalities
        group = subject[sj][0][0]
        category = subject[sj][0][1]
        pfo_input_data = jph(root_study_rabbits, 'A_data', group, category)
        pfo_sj = jph(pfo_input_data, sj)
        pfi_T1 = jph(pfo_sj, 'mod', sj + '_T1.nii.gz')
        pfi_FA = jph(pfo_sj, 'mod', sj + '_FA.nii.gz')
        pfi_ADC = jph(pfo_sj, 'mod', sj + '_MD.nii.gz')
        # -
        can_collect_data = True
        if not os.path.exists(pfi_T1):
            print('RECORD DATA not possible for subject {}. T1 not present'.format(sj))
            print pfi_T1
            can_collect_data = False
        if not os.path.exists(pfi_FA):
            print('RECORD DATA not possible for subject {}. FA not present'.format(sj))
            can_collect_data = False
        if not os.path.exists(pfi_ADC):
            print('RECORD DATA not possible for subject {}. ADC not present'.format(sj))
            can_collect_data = False
        # grab segmentations
        pfi_segm_T1_sj = jph(pfo_sj, 'segm', sj + '_T1_segm.nii.gz')
        pfi_segm_S0_sj = jph(pfo_sj, 'segm', sj + '_S0_segm.nii.gz')
        if not os.path.exists(pfi_segm_T1_sj):
            print('RECORD DATA not possible for subject {}. Segmentation T1 not present'.format(sj))
            can_collect_data = False
        if not os.path.exists(pfi_segm_S0_sj):
            print('RECORD DATA not possible for subject {}. Segmentation S0 not present'.format(sj))
            can_collect_data = False
        if can_collect_data:

            pfo_output_record_sj = jph(pfo_input_data, sj, 'records')
            cmd = 'mkdir -p {}'.format(pfo_output_record_sj)
            os.system(cmd)
            # grab label descriptor
            pfi_multi_labels_descr = jph(root_study_rabbits, 'A_data', 'Utils', 'multi_label_descriptor.txt')
            assert os.path.exists(pfi_multi_labels_descr)
            # grab excel table
            if subject[sj][0][0] == 'ACS':
                pfi_excel_table = pfi_excel_table_ACS
            elif subject[sj][0][0] == 'PTB':
                pfi_excel_table = pfi_excel_table_PTB
            else:
                raise IOError
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


if __name__ == '__main__':
    print('Collect data, local run. ')

    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull = False
    lsm.execute_PTB_ex_vivo = False
    lsm.execute_PTB_in_vivo = False
    lsm.execute_PTB_op_skull = False
    lsm.execute_ACS_ex_vivo = False

    lsm.input_subjects = ['2702', ]  # [ '2502bt1', '2503t1', '2605t1' , '2702t1', '2202t1',
    # '2205t1', '2206t1', '2502bt1']
    #  '3307', '3404']  # '2202t1', '2205t1', '2206t1' -- '2503', '2608', '2702',
    lsm.update_ls()

    compile_record_T1_DWI_from_subject_list(lsm.ls)
    # execute_processing_DWI(controller_steps, rpa_dwi)
