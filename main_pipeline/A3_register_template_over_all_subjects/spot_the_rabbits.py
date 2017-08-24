import os
from os.path import join as jph
import pickle
from collections import OrderedDict

from tools.definitions import root_study_rabbits, root_internal_template, pfo_subjects_parameters, bfc_corrector_cmd
from main_pipeline.A0_main.main_controller import ListSubjectsManager

from spot_a_rabbit.spot import SpotDS


def spot_a_list_of_rabbits(subjects_list, controller_fuser, controller_propagator):

    for sj_target in subjects_list:

        sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj_target), 'r'))

        study = sj_parameters['study']
        category = sj_parameters['category']

        pfo_target = jph(root_study_rabbits, 'A_data', study, category, sj_target)

        spot_sj = SpotDS(template_pfo=root_internal_template,
                         target_pfo=pfo_target,
                         target_scaffoldings_folder_name='z_tmp')

        # template parameters:
        spot_sj.template_list_charts_names = ['1201', '1203', '1305', '1404', '1507', '1510', '1702', '1805', '2002',
                                                '2502']
        spot_sj.template_list_suffix_modalities = [['T1', 'S0', 'V1', 'MD', 'FA']]
        spot_sj.template_list_suffix_masks = ['roi_mask', 'reg_mask']

        # --- target parameters
        spot_sj.target_parameters = sj_parameters

        spot_sj.controller_propagator = controller_propagator

        spot_sj.controller_fuser = controller_fuser

        spot_sj.bfc_corrector_cmd = bfc_corrector_cmd
        msg = 'bias field corrector command {} does NOT exist'.format(spot_sj.bfc_corrector_cmd)
        assert os.path.exists(spot_sj.bfc_corrector_cmd), msg

        spot_sj.propagate()
        spot_sj.fuse()


if __name__ == '__main__':

    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull = False
    lsm.execute_PTB_ex_vivo  = False
    lsm.execute_PTB_in_vivo  = False
    lsm.execute_PTB_op_skull = False
    lsm.execute_ACS_ex_vivo  = True

    # lsm.input_subjects = ['3103', ]  # [ '2502bt1', '2503t1', '2605t1' , '2702t1', '2202t1',
    # '2205t1', '2206t1', '2502bt1']
    #  '3307', '3404']  # '2202t1', '2205t1', '2206t1' -- '2503', '2608', '2702',
    lsm.update_ls()

    controller_propagator_ = {'Propagation_methods'       : 'Mono',
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

    controller_fuser_ = {'Fuse'           : True,
                         'fusion methods' : ['MV', 'STEPS', 'STAPLE'],  # 'MV', 'STAPLE',
                         'STAPLE_params'  : OrderedDict([('pr_1', None)]),
                         'STEPS_params'   : OrderedDict([('pr_1', [3, 3, None]),
                                                         ('pr_2', [3, 3, 2.0]),
                                                         ('pr_3', [3, 3, 4.0]),
                                                         ('pr_4', [3, 4, None]),
                                                         ('pr_5', [3, 4, 2.0]),
                                                         ('pr_6', [3, 4, 4.0]),
                                                         ('pr_7', [3, 5, None]),
                                                         ('pr_8', [3, 5, 2.0]),
                                                         ('pr_9', [3, 5, 4.0])]),  # k, n ,beta
                         'Inter_mod_space_propagation'   : True,
                         'Save_results'                  : True}

    spot_a_list_of_rabbits(lsm.ls, controller_propagator_, controller_fuser_)
