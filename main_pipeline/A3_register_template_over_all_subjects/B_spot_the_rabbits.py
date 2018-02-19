import os
from os.path import join as jph
import pickle
from collections import OrderedDict

from tools.definitions import root_study_rabbits, root_atlas, pfo_subjects_parameters, bfc_corrector_cmd, \
    num_cores_run
from main_pipeline.A0_main.main_controller import ListSubjectsManager

from spot_a_rabbit.spot import SpotDS


def spot_a_list_of_rabbits(subjects_list):

    multi_atlas_subjects = ['1201', '1203', '1305', '1404', '1507', '1510', '1702', '1805', '2002', '2502', '3301', '3404']

    for sj_target in subjects_list:
        print('\nAutomatic segmentation with SPOT-A-NeonatalRabbit - subject {} started.\n'.format(sj_target))

        sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj_target), 'r'))

        if sj_parameters['in_atlas']:
            # SPOT only the rabbits not already in the atlas.
            return

        study = sj_parameters['study']
        category = sj_parameters['category']

        pfo_target = jph(root_study_rabbits, 'A_data', study, category, sj_target, 'stereotaxic')

        # --- initialise the class spot:
        spot_sj = SpotDS(atlas_pfo=root_atlas,
                         target_pfo=pfo_target,
                         target_name=sj_target,
                         parameters_tag='P1')
        """
        Parameters tag -> correspondence:
        'P1' -> Multi modal T1 and FA + BFC on T1.
        """
        # Template parameters:
        spot_sj.atlas_name = 'MANRround3'  # Multi Atlas Newborn Rabbit
        spot_sj.atlas_list_charts_names      = multi_atlas_subjects
        spot_sj.atlas_list_suffix_modalities = ['T1', 'S0', 'V1', 'MD', 'FA']
        spot_sj.atlas_list_suffix_masks      = ['roi_mask', 'roi_reg_mask']
        spot_sj.atlas_reference_chart_name   = '1305'
        spot_sj.atlas_segmentation_suffix    = 'approved_round3'

        # --- target parameters
        spot_sj.target_list_suffix_modalities = ['T1', 'S0', 'V1', 'MD', 'FA']
        spot_sj.target_name                   = sj_target

        # --- Utils
        spot_sj.bfc_corrector_cmd = bfc_corrector_cmd
        spot_sj.num_cores_run     = num_cores_run

        # --- Propagator option
        spot_sj.propagation_options['Affine_modalities']        = ('T1', 'FA')
        spot_sj.propagation_options['Affine_reg_masks']         = ('T1', 'S0')  # if (), there is a single mask for all modalities
        spot_sj.propagation_options['Affine_parameters']        = ' -speeeeed '
        spot_sj.propagation_options['N_rigid_modalities']       = ('T1', 'FA')  # if empty, no non-rigid step.
        spot_sj.propagation_options['N_rigid_reg_masks']        = ('T1', 'S0')  # if [], same mask for all modalities
        spot_sj.propagation_options['N_rigid_slim_reg_mask']    = True
        spot_sj.propagation_options['N_rigid_mod_diff_bfc']     = ('T1',)  # empty list no diff bfc. - put a comma!!
        spot_sj.propagation_options['N_rigid_parameters']       = ' -be 0.5 -ln 6 -lp 4  -smooR 1.5 -smooF 1.5 '
        spot_sj.propagation_options['N_rigid_same_mask_moving'] = True
        spot_sj.propagation_options['Final_smoothing_factor']   = 0

        # --- Propagator controller
        spot_sj.propagation_controller['Aff_alignment']          = True
        spot_sj.propagation_controller['Propagate_aff_to_segm']  = True
        spot_sj.propagation_controller['Propagate_aff_to_mask']  = True
        spot_sj.propagation_controller['Get_N_rigid_slim_mask']  = True
        spot_sj.propagation_controller['Get_differential_BFC']   = True
        spot_sj.propagation_controller['N_rigid_alignment']      = True
        spot_sj.propagation_controller['Propagate_n_rigid']      = True
        spot_sj.propagation_controller['Smooth_results']         = True
        spot_sj.propagation_controller['Stack_warps_and_segms']  = True

        # --- Fuser option
        spot_sj.fuser_options['Fusion_methods'] = ['MV']  #, 'STAPLE', 'STEPS']
        spot_sj.fuser_options['STAPLE_params']  = OrderedDict([('pr1', None)])
        spot_sj.fuser_options['STEPS_params']   = OrderedDict([('pr{0}.{1}'.format(k, n), [k, n, 4])
                                                             for n in [9] for k in [5, 11]])
        # --- Fuser controller
        spot_sj.fuser_controller['Fuse']         = True
        spot_sj.fuser_controller['Save_results'] = True

        spot_sj.spot_on_target_initialise()
        spot_sj.propagate()
        spot_sj.fuse()


if __name__ == '__main__':

    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull = False
    lsm.execute_PTB_ex_vivo  = False
    lsm.execute_PTB_in_vivo  = False
    lsm.execute_PTB_op_skull = False
    lsm.execute_ACS_ex_vivo  = False

    lsm.input_subjects = ['4501', '4305']
    lsm.update_ls()

    spot_a_list_of_rabbits(lsm.ls)
