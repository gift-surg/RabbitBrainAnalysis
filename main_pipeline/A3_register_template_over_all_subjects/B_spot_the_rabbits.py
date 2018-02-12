import os
from os.path import join as jph
import pickle
from collections import OrderedDict

from tools.definitions import root_study_rabbits, root_atlas, pfo_subjects_parameters, bfc_corrector_cmd, \
    num_cores_run
from main_pipeline.A0_main.main_controller import ListSubjectsManager

from spot_a_rabbit.spot import SpotDS


def spot_a_list_of_rabbits(subjects_list):
    # TODO - A lot TODO here, integrate with the new structure of the multi-atlas.
    multi_atlas_subjects = ['1201', '1203', '1305', '1404', '1507', '1510', '1702', '1805', '2002', '2502', '3301', '3404']

    for sj_target in subjects_list:

        # if in template just copy the modality.

        pass
        # if sj_target in multi_atlas_subjects:
        #     # Propagate when in atlas (the subject is already manually segmented, no need to propagate back):
        #     propagator_when_in_atlas()  # TODO BELOW
        # else:
        #     # Propagate when not in atlas, using SPOT-A-NeonatalRabbit:
        #
        #
        #     sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj_target), 'r'))
        #
        #     study = sj_parameters['study']
        #     category = sj_parameters['category']
        #
        #     pfo_target = jph(root_study_rabbits, 'A_data', study, category, sj_target)
        #
        #     spot_sj = SpotDS(atlas_pfo=root_atlas,
        #                      target_pfo=pfo_target,
        #                      target_scaffoldings_folder_name='z_tmp',
        #                      pfo_subjects_parameters=pfo_subjects_parameters)
        #
        #     # template parameters:
        #     spot_sj.atlas_list_charts_names = multi_atlas_subjects
        #     spot_sj.atlas_list_suffix_modalities = ['T1', 'S0', 'V1', 'MD', 'FA']
        #     spot_sj.atlas_list_suffix_masks = ['roi_mask', 'reg_mask']
        #
        #     # --- target parameters
        #     spot_sj.target_parameters = sj_parameters
        #
        #     spot_sj.target_list_suffix_modalities = [['T1'], ['S0', 'V1', 'MD', 'FA']]
        #
        #     spot_sj.bfc_corrector_cmd = bfc_corrector_cmd
        #     msg = 'bias field corrector command {} does NOT exist'.format(spot_sj.bfc_corrector_cmd)
        #     assert os.path.exists(spot_sj.bfc_corrector_cmd), msg
        #
        #     # settings propagator:
        #     spot_sj.controller_propagator = {'Propagation_methods': 'Multi',
        #                                      'Affine_options': '',
        #                                      'Reorient_chart_hd': True,
        #                                      'Aff_alignment': True,
        #                                      'Propagate_aff_to_segm': True,
        #                                      'Propagate_aff_to_mask': True,
        #                                      'Get_differential_BFC': False,  # if multi try to put this off.
        #                                      'N-rig_alignment': True,
        #                                      'Propagate_to_target_n-rig': True,
        #                                      'Smooth_results': True,
        #                                      'Stack_warps_and_segms': True,
        #                                      'Speed': False,
        #                                      # not all modalities acquisitions are considered
        #                                      'Selected_modalities_suffix_for_multimodal_propagation' : ['T1', 'FAinT1'],
        #                                      'Selected_masks_suffix_for_multimodal_propagation'      : ['T1', 'S0inT1'],
        #                                      'Parameters_nrigid_registration': ' -be 0.95 -ln 6 -lp 3 '   #  -vel -be 0.5 -ln 6 -lp 4  -smooR 0.07 -smooF 0.07  '
        #                                      }
        #
        #     # settings fuser:
        #     spot_sj.controller_fuser = {'Fusion_methods': ['MV'],
        #                                 'Fuse': True,
        #                                 'STAPLE_params': OrderedDict([('pr_1', None)]),
        #                                 'STEPS_params': OrderedDict([('pr_{0}_{1}'.format(k, n), [k, n, 0.4])
        #                                                              for n in [5, 7, 9]
        #                                                              for k in [5, 11]]),  # k-pixels, n (5 or lower), beta
        #                                 'Inter_mod_space_propagation': True,
        #                                 'Save_results': True}
        #
        #     spot_sj.num_cores_run = num_cores_run
        #     #
        #     spot_sj.propagate()
        #     spot_sj.fuse()
        #     spot_sj.integrate_target_as_atlas_chart()


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