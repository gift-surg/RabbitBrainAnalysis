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

        if sj_target in multi_atlas_subjects:
            # Propagate when in atlas (the subject is already manually segmented, no need to propagate back):
            propagator_when_in_atlas()  # TODO BELOW
        else:
            # Propagate when not in atlas, using SPOT-A-NeonatalRabbit:


            sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj_target), 'r'))

            study = sj_parameters['study']
            category = sj_parameters['category']

            pfo_target = jph(root_study_rabbits, 'A_data', study, category, sj_target)

            spot_sj = SpotDS(atlas_pfo=root_atlas,
                             target_pfo=pfo_target,
                             target_scaffoldings_folder_name='z_tmp',
                             pfo_subjects_parameters=pfo_subjects_parameters)

            # template parameters:
            spot_sj.atlas_list_charts_names = multi_atlas_subjects
            spot_sj.atlas_list_suffix_modalities = ['T1', 'S0', 'V1', 'MD', 'FA']
            spot_sj.atlas_list_suffix_masks = ['roi_mask', 'reg_mask']

            # --- target parameters
            spot_sj.target_parameters = sj_parameters

            spot_sj.target_list_suffix_modalities = [['T1'], ['S0', 'V1', 'MD', 'FA']]

            spot_sj.bfc_corrector_cmd = bfc_corrector_cmd
            msg = 'bias field corrector command {} does NOT exist'.format(spot_sj.bfc_corrector_cmd)
            assert os.path.exists(spot_sj.bfc_corrector_cmd), msg

            # settings propagator:
            spot_sj.controller_propagator = {'Propagation_methods': 'Multi',
                                             'Affine_options': '',
                                             'Reorient_chart_hd': True,
                                             'Aff_alignment': True,
                                             'Propagate_aff_to_segm': True,
                                             'Propagate_aff_to_mask': True,
                                             'Get_differential_BFC': False,  # if multi try to put this off.
                                             'N-rig_alignment': True,
                                             'Propagate_to_target_n-rig': True,
                                             'Smooth_results': True,
                                             'Stack_warps_and_segms': True,
                                             'Speed': False,
                                             # not all modalities acquisitions are considered
                                             'Selected_modalities_suffix_for_multimodal_propagation' : ['T1', 'FAinT1'],
                                             'Selected_masks_suffix_for_multimodal_propagation'      : ['T1', 'S0inT1'],
                                             'Parameters_nrigid_registration': ' -be 0.95 -ln 6 -lp 3 '   #  -vel -be 0.5 -ln 6 -lp 4  -smooR 0.07 -smooF 0.07  '
                                             }

            # settings fuser:
            spot_sj.controller_fuser = {'Fusion_methods': ['MV'],
                                        'Fuse': True,
                                        'STAPLE_params': OrderedDict([('pr_1', None)]),
                                        'STEPS_params': OrderedDict([('pr_{0}_{1}'.format(k, n), [k, n, 0.4])
                                                                     for n in [5, 7, 9]
                                                                     for k in [5, 11]]),  # k-pixels, n (5 or lower), beta
                                        'Inter_mod_space_propagation': True,
                                        'Save_results': True}

            spot_sj.num_cores_run = num_cores_run
            #
            spot_sj.propagate()
            spot_sj.fuse()
            spot_sj.integrate_target_as_atlas_chart()



#
#
#
#
#
# # TODO move this on Rabbit brain analysis, as not concerned with the atlas propagation
# # but only with the data analysis.
# def propagator_when_in_atlas():
#     """
#     All based on the pivotal of the main modality (T1).
#     When the segmentation of the T1 is propagated on the main chart, then spaces modalities
#     are aligned and the segmentation is resampled on the other spaces internally to the Target.
#     :param sp: Spot Data Structure
#     :return:
#     """
#
#     print('Propagate and stack all charts segmentations to {}'.format(sp.target_pfo))
#     assert isinstance(sp, spot.SpotDS)
#
#     pfo_tmp        = jph(sp.scaffoldings_pfo, sp.arch_scaffoldings_propagation_name_folder + '_in_atlas')
#     pfo_tmp_fusion = jph(sp.scaffoldings_pfo, sp.arch_scaffoldings_fusion_name_folder + '_in_atlas')
#
#     print_and_run('mkdir -p {}'.format(sp.scaffoldings_pfo))
#     print_and_run('mkdir -p {}'.format(pfo_tmp))
#     print_and_run('mkdir -p {}'.format(pfo_tmp_fusion))
#
#     pfo_target_mod = jph(sp.target_pfo, sp.arch_modalities_name_folder)
#     pfo_target_masks = jph(sp.target_pfo, sp.arch_masks_name_folder)
#
#     pfo_chart_atlas_mod   = jph(sp.atlas_pfo, sp.target_name, sp.arch_modalities_name_folder)
#     pfo_chart_atlas_masks = jph(sp.atlas_pfo, sp.target_name,sp.arch_masks_name_folder)
#     pfo_chart_atlas_segm  = jph(sp.atlas_pfo, sp.target_name,sp.arch_segmentations_name_folder)
#
#     # Shared by template-chart and target.
#
#     pivotal_mods = [k[0] for k in sp.target_list_suffix_modalities]
#
#     print('Target {} is a chart of the template'.format(sp.target_name))
#
#     if sp.controller_propagator['Reorient_chart_hd']:
#
#         print('- set header bicommissural for each pivotal modality in {0}'.format(pivotal_mods))
#
#         angles = sp.target_parameters['angles']
#         if isinstance(angles[0], list):
#             theta = angles[0][1]
#         else:
#             theta = angles[1]
#
#         # mods
#         mo = pivotal_mods[0]
#         pfi_chart_atlas_mo = jph(pfo_chart_atlas_mod, '{0}_{1}.nii.gz'.format(sp.target_name, mo))
#         assert os.path.exists(pfi_chart_atlas_mo)
#         # bicomm_header:
#         pfi_chart_atlas_mo_oriented = jph(pfo_tmp, 'bicomm_header_{0}_{1}.nii.gz'.format(sp.target_name, mo))
#         cmd = 'cp {0} {1}'.format(pfi_chart_atlas_mo, pfi_chart_atlas_mo_oriented)
#         print_and_run(cmd)
#         if theta > 0:
#             lm = LabelsManager()
#             lm.header.apply_small_rotation(pfi_chart_atlas_mo_oriented,
#                                            pfi_chart_atlas_mo_oriented,
#                                            angle=theta, principal_axis='pitch')
#
#         # mask
#         pfi_chart_atlas_roi_reg_mask = jph(pfo_chart_atlas_masks, '{0}_{1}.nii.gz'.format(
#             sp.target_name, sp.target_list_suffix_masks[0]))
#         assert os.path.exists(pfi_chart_atlas_roi_reg_mask), pfi_chart_atlas_roi_reg_mask
#         pfi_chart_atlas_reg_mask_reoriented = jph(pfo_tmp, 'bicomm_header_{0}_{1}.nii.gz'.format(
#             sp.target_name, sp.target_list_suffix_masks[0]))
#         cmd = 'cp {0} {1}'.format(pfi_chart_atlas_roi_reg_mask, pfi_chart_atlas_reg_mask_reoriented)
#         print_and_run(cmd)
#         if theta > 0:
#             lm = LabelsManager()
#             lm.header.apply_small_rotation(pfi_chart_atlas_reg_mask_reoriented,
#                                            pfi_chart_atlas_reg_mask_reoriented,
#                                            angle=theta, principal_axis='pitch')
#
#         # segm
#         pfi_chart_atlas_segm = jph(pfo_chart_atlas_segm, '{0}_{1}.nii.gz'.format(
#             sp.target_name, sp.arch_approved_segmentation_suffix))
#         assert os.path.exists(pfi_chart_atlas_segm), pfi_chart_atlas_segm
#         pfi_chart_atlas_segm_oriented = jph(pfo_tmp, 'bicomm_header_{0}_{1}_segm.nii.gz'.format(
#             sp.target_name, sp.arch_approved_segmentation_suffix))
#         cmd = 'cp {0} {1}'.format(pfi_chart_atlas_segm, pfi_chart_atlas_segm_oriented)
#         print_and_run(cmd)
#         if theta > 0:
#             lm = LabelsManager()
#             lm.header.apply_small_rotation(pfi_chart_atlas_segm_oriented,
#                                            pfi_chart_atlas_segm_oriented,
#                                            angle=theta, principal_axis='pitch')
#
#     if sp.controller_propagator['Aff_alignment']:
#         mo = pivotal_mods[0]
#
#         # reference
#         pfi_target_mo   = jph(pfo_target_mod, '{0}_{1}.nii.gz'.format(sp.target_name, mo))
#         pfi_target_mask = jph(pfo_target_masks, '{0}_{1}_{2}.nii.gz'.format(sp.target_name, mo,
#                                                                             sp.target_list_suffix_masks[0]))
#
#         # floating
#         pfi_chart_atlas_mo_oriented = jph(pfo_tmp, 'bicomm_header_{0}_{1}.nii.gz'.format(sp.target_name, mo))
#         pfi_chart_atlas_reg_mask_reoriented = jph(pfo_tmp, 'bicomm_header_{0}_{1}.nii.gz'.format(
#             sp.target_name, sp.target_list_suffix_masks[0]))
#
#         assert os.path.exists(pfi_target_mo), pfi_target_mo
#         assert os.path.exists(pfi_target_mask), pfi_target_mask
#         assert os.path.exists(pfi_chart_atlas_mo_oriented)
#         assert os.path.exists(pfi_chart_atlas_reg_mask_reoriented)
#
#         # output
#         pfi_chart_atlas_on_target_mo_aff = jph(pfo_tmp, 'chart_{0}_on_target_{0}_{1}_rigid_aff.txt'
#                                                   .format(sp.target_name, mo))
#         pfi_chart_atlas_on_target_mo_warp = jph(pfo_tmp, 'chart_{0}_on_target_{0}_{1}_warp.nii.gz'
#                                                    .format(sp.target_name, mo))
#
#         cmd = 'reg_aladin -ref {0} -rmask {1} -flo {2} -fmask {3} -aff {4} -res {5} -omp {6} -rigOnly'.format(
#             pfi_target_mo, pfi_target_mask,
#             pfi_chart_atlas_mo_oriented, pfi_chart_atlas_reg_mask_reoriented,
#             pfi_chart_atlas_on_target_mo_aff, pfi_chart_atlas_on_target_mo_warp, sp.num_cores_run)
#
#         print_and_run(cmd)
#
#     if sp.controller_propagator['Propagate_aff_to_segm']:
#         mo0 = pivotal_mods[0]
#
#         pfi_target_mo0 = jph(pfo_target_mod, '{0}_{1}.nii.gz'.format(sp.target_name, mo0))
#         pfi_chart_atlas_segm_oriented = jph(pfo_tmp, 'bicomm_header_{0}_{1}_segm.nii.gz'.format(
#             sp.target_name, sp.arch_approved_segmentation_suffix))
#         pfi_chart_atlas_on_target_mo_aff = jph(pfo_tmp, 'chart_{0}_on_target_{0}_{1}_rigid_aff.txt'
#                                                   .format(sp.target_name, mo0))
#         assert check_path_validity(pfi_target_mo0)
#         assert check_path_validity(pfi_chart_atlas_segm_oriented)
#         assert check_path_validity(pfi_chart_atlas_on_target_mo_aff)
#         pfi_templ_segm_aff_registered_on_sj_target = jph(pfo_tmp_fusion, 'result_{0}_{1}__IN_ATLAS.nii.gz'.format(
#             sp.target_name, mo0))
#         cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
#             pfi_target_mo0, pfi_chart_atlas_segm_oriented, pfi_chart_atlas_on_target_mo_aff,
#             pfi_templ_segm_aff_registered_on_sj_target)
#         print_and_run(cmd)
#
#         # Inter-modal segmentation on Target: does not involve the equivalent step for extra template
#         # elements in the
#
#         if len(pivotal_mods) > 1:
#             for mo in pivotal_mods[1:]:
#
#                 # mo
#                 if mo == 'MSME':
#                     pfi_target_mo = jph(pfo_target_mod, 'MSME_tp0', '{0}_{1}_tp0.nii.gz'.format(sp.target_name, mo))
#                 else:
#                     pfi_target_mo = jph(pfo_target_mod, '{0}_{1}.nii.gz'.format(sp.target_name, mo))
#
#                 pfi_target_mo_mask = jph(pfo_target_masks, '{0}_{1}_{2}.nii.gz'.format(
#                     sp.target_name, mo, sp.target_list_suffix_masks[1]))
#
#                 # mo0
#                 pfi_main_mod_segmented = jph(pfo_target_mod, '{0}_{1}.nii.gz'.format(sp.target_name, mo0))
#
#                 pfi_main_mod_segmented_mask = jph(pfo_target_masks, '{0}_{1}_{2}.nii.gz'.format(
#                     sp.target_name, mo0, sp.target_list_suffix_masks[1]))
#
#                 assert os.path.exists(pfi_target_mo), pfi_target_mo
#                 assert os.path.exists(pfi_target_mo_mask), pfi_target_mo_mask
#                 assert os.path.exists(pfi_main_mod_segmented), pfi_main_mod_segmented
#                 assert os.path.exists(pfi_main_mod_segmented_mask), pfi_main_mod_segmented_mask
#
#                 pfi_main_mo_target_on_other_mo_target_aff = jph(pfo_tmp,
#                     '{0}_main_mo_target_{1}_on_other_mo_target_{2}.aff'.format(sp.target_name, mo0, mo))
#                 pfi_main_mo_target_on_other_mo_target_warp = jph(pfo_tmp,
#                     '{0}_main_mo_target_{1}_on_other_mo_target_{2}.nii.gz'.format(sp.target_name, mo0, mo))
#
#                 cmd0 = 'reg_aladin -ref {0} -rmask {1} -flo {2} -fmask {3} -aff {4} -res {5} -omp {6} -rigOnly'.format(
#                     pfi_target_mo, pfi_target_mo_mask,
#                     pfi_main_mod_segmented, pfi_main_mod_segmented_mask,
#                     pfi_main_mo_target_on_other_mo_target_aff, pfi_main_mo_target_on_other_mo_target_warp,
#                     sp.num_cores_run)
#                 print_and_run(cmd0)
#
#                 assert os.path.exists(pfi_templ_segm_aff_registered_on_sj_target)
#
#                 pfi_templ_segm_aff_registered_on_sj_target_mo = jph(pfo_tmp_fusion,
#                     'result_{0}_{1}__IN_ATLAS.nii.gz'.format(sp.target_name, mo))
#
#                 cmd1 = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
#                     pfi_target_mo, pfi_templ_segm_aff_registered_on_sj_target, pfi_main_mo_target_on_other_mo_target_aff,
#                     pfi_templ_segm_aff_registered_on_sj_target_mo)
#                 print_and_run(cmd1)
#
#     if sp.controller_fuser['Save_results']:
#         # Here ends the propagate and fuse step when the subject is in the multi-atlas. The fuse step is bypassed.
#
#         pfo_segmentations_results = jph(sp.target_pfo, sp.arch_segmentations_name_folder)
#         cmd0 = 'mkdir -p {}'.format(pfo_segmentations_results)
#         print_and_run(cmd0)
#
#         for filename in os.listdir(pfo_tmp_fusion):
#             if filename.startswith('result_'):
#                 cmd = 'cp {0} {1}'.format(jph(pfo_tmp_fusion, filename),
#                                           jph(pfo_segmentations_results,
#                                               filename.replace('result_', '').replace('__IN_ATLAS', '_segm')))
#                 print_and_run(cmd)
#
#
#


















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
