import os

from pipeline_project.A0_main.main_controller import ListSubjectsManager, templ_subjects
from definitions import root_study_rabbits, root_main_dropbox

from pipeline_project.A1_convert_and_clean.apply_converter_to_all_data import convert_subjects_from_list
from pipeline_project.A1_convert_and_clean.clean_converted_data import cleaner_converted_data_from_list

from pipeline_project.A2_process_modalities.process_T1 import process_T1_from_list
from pipeline_project.A2_process_modalities.process_DWI import process_DWI_from_list
from pipeline_project.A2_process_modalities.process_MSME import process_MSME_from_list
from pipeline_project.A2_process_modalities.process_g_ratio import process_g_ratio_from_list

from pipeline_project.A3_register_template_over_all_subjects.propagate_and_fuse_main import \
    propagate_and_fuse_per_subject_list_over_all_modalities

from pipeline_project.A4_data_collection.collect_data_study_T1_and_DWI import compile_record_T1_DWI_from_subject_list
from pipeline_project.A4_data_collection.collect_data_study_g_ratio import compile_record_g_ratio_from_subject_list

from pipeline_project.U_utils.upate_shared_results import send_data_to_hannes_from_list
from pipeline_project.U_utils.copy_to_excel_file import save_data_into_excel_file


if __name__ == '__main__':

    assert os.path.isdir(root_study_rabbits), 'Connect to cluster / Pantopolio!'

    ''' Set parameters per subjects or per group '''

    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull  = False
    lsm.execute_PTB_ex_vivo   = False
    lsm.execute_PTB_in_vivo   = False
    lsm.execute_PTB_op_skull  = False
    lsm.execute_ACS_ex_vivo   = False

    lsm.input_subjects = ['2702', ]  # [ '2502bt1', '2503t1', '2605t1' , '2702t1', '2202t1',
    # '2205t1', '2206t1', '2502bt1']
    #  '3307', '3404']  # '2202t1', '2205t1', '2206t1' -- '2503', '2608', '2702',
    lsm.update_ls()

    print lsm.ls

    ''' Set steps '''

    step_A1         = False
    step_A2_T1      = True
    step_A2_DWI     = True
    step_A2_MSME    = True
    step_A2_g_ratio = True
    step_A3         = True
    step_A4         = True
    step_A5         = True

    ''' Step A1 - convert, clean and create aliases '''
    if step_A1:
        print('\nStep A1\n')
        convert_subjects_from_list(lsm.ls)
        cleaner_converted_data_from_list(lsm.ls)

    ''' Step A2 - T1 '''
    if step_A2_T1:
        print('\nStep A2 T1\n')
        controller_A2_T1 = {'orient to standard'  : True,
                            'register roi masks'  : True,
                            'propagate roi masks' : True,
                            'adjust mask'         : True,
                            'cut masks'           : True,
                            'step bfc'            : True,
                            'create lesion mask'  : True,
                            'create reg masks'    : True,
                            'save results'        : True}

        process_T1_from_list(lsm.ls, controller_A2_T1)

    ''' Step A2 - DWI '''
    if step_A2_DWI:
        print('\nStep A2 DWI\n')
        controller_DWI = {'squeeze'                : True,
                            'orient to standard'   : True,
                            'register roi masks'   : True,
                            'propagate roi masks'  : True,
                            'adjust mask'          : True,
                            'cut mask dwi'         : True,
                            'cut mask b0'          : True,
                            'correct slope'        : True,
                            'eddy current'         : True,
                            'fsl tensor fitting'   : True,
                            'adjust dti-based mod' : True,
                            'bfc b0'               : True,
                            'create lesion mask'   : True,
                            'create reg masks'     : True,
                            'save results'         : True}

        process_DWI_from_list(lsm.ls, controller_DWI)

    ''' Step A2 - MSME '''
    if step_A2_MSME:
        print('\nStep A2 MSME\n')
        controller_MSME = {'squeeze'                  : True,
                            'orient to standard'       : True,
                            'extract first timepoint'  : True,
                            'register tp0 to S0'       : True,
                            'register msme to S0'      : True,
                            'extract first tp in s0 space' : True
                           }

        process_MSME_from_list(lsm.ls, controller_MSME)

    ''' Step A2 - g-ratio '''
    if step_A2_g_ratio:
        print('\nStep A2 g-ratio\n')
        controller_g_ratio = {'transpose b-vals b-vects'  : True,
                              'noddi'                     : True,
                              'save T2_times'             : True,
                              'get acquisition echo time' : True,
                              'fit msme'                  : True,
                              'extract first tp noddi'    : True,
                              'compute g-ratio'           : True,
                              'save results'              : True}

        process_g_ratio_from_list(lsm.ls, controller_g_ratio)

    ''' Step A3 - Propagate template '''
    if step_A3:
        print('\nStep A3\n')
        controller_fuser_ = {'set header bicommissural'  : True,
                             'aff alignment'             : True,
                             'Propagate aff to segm'     : True,
                             'Propagate aff to mask'     : True,
                             'Get differential BFC'      : True,
                             'N-rig alignment'           : True,
                             'Propagate to target n-rig' : True,
                             'Smooth result'             : True,
                             'Stack warps and segm'      : True,
                             'Fuse'                      : True,
                             'save result'               : True
                             }

        controller_propagator_ = {'set header bicommissural' : True,
                                  'rig alignment'            : True,
                                  'Propagate aff to segm'    : True,
                                  'Propagate aff to mask'    : True,
                                  'Smooth'                   : True,
                                  'save result'              : True}

        controller_inter_modality_propagator_ = {'compensate squeezing'     : True,
                                                 'rig register to S0'       : True,
                                                 'rig propagate to S0'      : True,
                                                 'rig register to MSME_up'  : True,
                                                 'rig propagate to MSME_up' : True,
                                                 'MSME_up to MSME'          : True}
        pfo_templ_subjects_input = os.path.join(root_main_dropbox, 'study', 'A_internal_template')
        list_templ_subjects_input = templ_subjects

        propagate_and_fuse_per_subject_list_over_all_modalities(lsm.ls, controller_fuser_, controller_propagator_,
                                                                controller_inter_modality_propagator_)

    ''' Step A4 - Data collection '''
    if step_A4:
        print('\nStep A4\n')
        compile_record_T1_DWI_from_subject_list(lsm.ls)
        compile_record_g_ratio_from_subject_list(lsm.ls)

    if step_A5:
        send_data_to_hannes_from_list(lsm.ls, records_only=False)
        save_data_into_excel_file(lsm.ls)
