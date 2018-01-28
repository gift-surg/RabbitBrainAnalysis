from tools.auxiliary.sanity_checks import check_libraries
from collections import OrderedDict

from main_pipeline.A0_main.subject_parameters_creator import reset_parameters_files
from main_pipeline.A0_main.subject_parameters_manager import get_list_names_subjects_in_template, \
    check_subjects_situation

from tools.definitions import pfo_subjects_parameters

from main_pipeline.A0_main.main_controller import ListSubjectsManager
from main_pipeline.A1_convert_and_clean.apply_converter_to_all_data import convert_subjects_from_list
from main_pipeline.A1_convert_and_clean.clean_converted_data import cleaner_converted_data_from_list
from main_pipeline.A2_process_modalities.process_DWI import process_DWI_from_list
from main_pipeline.A2_process_modalities.process_MSME import process_MSME_from_list
from main_pipeline.A2_process_modalities.process_T1 import process_T1_from_list
from main_pipeline.A2_process_modalities.process_T2_map import process_t2_maps_from_list
from main_pipeline.A2_process_modalities.process_g_ratio import process_g_ratio_from_list

from main_pipeline.A3_register_template_over_all_subjects.spot_the_rabbits import spot_a_list_of_rabbits

# from main_pipeline.A4_data_collection.generate_report_studies import compile_report_from_subject_list
from main_pipeline.U_utils.upate_shared_results import send_data_to_hannes_from_list


def main_runner(subj_list):

    check_libraries()

    # Set steps

    steps = {'reset_parameters' : False,  # if this is true it does not do anything else.
             'step_A1'          : False,
             'step_A2_T1'       : False,
             'step_A2_DWI'      : False,
             'step_A2_MSME'     : False,
             'step_A2_T2maps'   : False,
             'step_A2_g_ratio'  : False,
             'step_A3'          : True,
             'step_A4'          : False,
             'step_A5'          : False}

    print('STEPS')
    for k in sorted(steps.keys()):
        print('{0:<20} : {1}'.format(k, steps[k]))

    ''' Re-set parameter files '''
    if steps['reset_parameters']:
        print('\nStep 0 : reset parameters and examine then\n')
        reset_parameters_files(pfo_where_to_save=pfo_subjects_parameters)
        print('Subjects summary: ')
        check_subjects_situation(pfo_subjects_parameters)
        print('\nTemplate:')
        sjs = get_list_names_subjects_in_template(pfo_subjects_parameters)
        print(sjs)
        # NOTE: does not go further
        print('Parameter re-computed. The pipeline ends here')
        return

    ''' Step A1 - convert, clean and create aliases '''
    if steps['step_A1']:
        print('\nStep A1\n')
        convert_subjects_from_list(subj_list)
        cleaner_converted_data_from_list(subj_list)

    ''' Step A2 - T1 '''
    if steps['step_A2_T1']:
        print('\nStep A2 T1\n')
        controller_A2_T1 = {'orient to standard'  : True,
                            'register roi masks'  : True,
                            'adjust mask'         : True,
                            'cut masks'           : True,
                            'step bfc'            : True,
                            'create lesion mask'  : True,
                            'create reg masks'    : True,
                            'save results'        : True}

        process_T1_from_list(subj_list, controller_A2_T1)

    ''' Step A2 - DWI '''
    if steps['step_A2_DWI']:
        print('\nStep A2 DWI\n')
        controller_DWI = {'squeeze'              : True,
                          'orient to standard'   : True,
                          'create roi masks'     : True,
                          'adjust mask'          : True,
                          'cut mask dwi'         : True,
                          'cut mask S0'          : True,
                          'correct slope'        : True,
                          'eddy current'         : True,
                          'fsl tensor fitting'   : True,
                          'adjust dti-based mod' : True,
                          'bfc S0'               : True,
                          'create lesion mask'   : True,
                          'create reg masks'     : True,
                          'save results'         : True}

        process_DWI_from_list(subj_list, controller_DWI)

    ''' Step A2 - MSME '''
    if steps['step_A2_MSME']:
        print('\nStep A2 MSME\n')
        controller_MSME = {'squeeze'                       : True,
                           'orient to standard'            : True,
                           'extract first timepoint'       : True,
                           'register tp0 to S0'            : True,
                           'register msme to S0'           : True,
                           'get mask for original msme'    : True,
                           'bfc'                           : True,
                           'bfc up'                        : True,
                           'save results'                  : True,
                           'save results tp0'              : True
                           }

        process_MSME_from_list(subj_list, controller_MSME)

    ''' Step A2 - T2Maps '''
    if steps['step_A2_T2maps']:
        print('\nStep T2 maps\n')
        controller_T2maps = {'get acquisition echo time'  : True,
                             'process each MSME input'    : True,
                             'correct origin'             : True,
                             'save results'               : True}

        process_t2_maps_from_list(subj_list, controller_T2maps)

    ''' Step A2 - g-ratio '''
    if steps['step_A2_g_ratio']:
        print('\nStep A2 g-ratio\n')
        controller_g_ratio = {'transpose b-vals b-vects'  : True,
                              'noddi'                     : True,
                              'save T2_times'             : True,
                              'get acquisition echo time' : True,
                              'fit msme'                  : True,
                              'extract first tp noddi'    : True,
                              'compute g-ratio'           : True,
                              'save results'              : True}

        process_g_ratio_from_list(subj_list, controller_g_ratio)

    ''' Step A3 - Propagate template '''
    if steps['step_A3']:
        print('\nStep A3\n')
        controller_propagator = {'Propagation_methods'        : 'Mono',
                                  'Affine_options'            : '',
                                  'Reorient_chart_hd'         : True,
                                  'Aff_alignment'             : True,
                                  'Propagate_aff_to_segm'     : True,
                                  'Propagate_aff_to_mask'     : True,
                                  'Get_differential_BFC'      : True,
                                  'N-rig_alignment'           : True,
                                  'Propagate_to_target_n-rig' : True,
                                  'Smooth_results'            : True,
                                  'Stack_warps_and_segms'     : True,
                                  'Speed'                     : False}

        controller_fuser = {'Fuse': True,
                             'Fusion_methods'  : ['MV', 'STEPS', 'STAPLE'],  # 'MV', 'STAPLE',
                             'STAPLE_params'   : OrderedDict([('pr_1', None)]),
                             'STEPS_params'    : OrderedDict([('pr_1', [3, 3, None]),
                                                              ('pr_2', [3, 3, 2.0]),
                                                              ('pr_3', [3, 3, 4.0]),
                                                              ('pr_4', [3, 4, None]),
                                                              ('pr_5', [3, 4, 2.0]),
                                                              ('pr_6', [3, 4, 4.0]),
                                                              ('pr_7', [3, 5, None]),
                                                              ('pr_8', [3, 5, 2.0]),
                                                              ('pr_9', [3, 5, 4.0])]),  # k, n ,beta
                             'Inter_mod_space_propagation'    : False,
                             'Save_results'                   : True}

        spot_a_list_of_rabbits(subj_list, controller_propagator, controller_fuser)

    ''' Step A4 - Data collection '''
    if steps['step_A4']:
        print('\nStep A4\n')
        pass  # in progress!
        # compile_report_from_subject_list(subj_list)

    if steps['step_A5']:
        send_data_to_hannes_from_list(subj_list, records_only=False)


if __name__ == '__main__':

    # assert os.path.isdir(root_study_rabbits), 'Connect to cluster / Pantopolio!'

    ''' Set parameters per subjects or per group '''

    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull  = False
    lsm.execute_PTB_ex_vivo   = False
    lsm.execute_PTB_in_vivo   = False
    lsm.execute_PTB_op_skull  = False
    lsm.execute_ACS_ex_vivo   = False

    # lsm.input_subjects = ['1201', '1203', '1305', '1404', '1507', '1510', '1702', '1805', '2002', '2502', '3301', '3404']
    lsm.input_subjects = ['4302']
    # template_subjects = ['1201', '1203', '1305', '1404', '', '1510', '1702', '1805', '2002', '2502', '3301', '3404']
    lsm.update_ls()

    print(lsm.ls)

    main_runner(lsm.ls)
