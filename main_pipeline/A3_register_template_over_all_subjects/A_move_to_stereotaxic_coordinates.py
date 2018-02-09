"""
A) re-orient the chart in stereotaxic coordinate.
"""
import os
from os.path import join as jph
import pickle
import numpy as np

from labels_manager.main import LabelsManager

from tools.definitions import root_study_rabbits, pfo_subjects_parameters, root_atlas, num_cores_run
from main_pipeline.A0_main.main_controller import ListSubjectsManager
from tools.auxiliary.lesion_mask_extractor import percentile_lesion_mask_extractor
from tools.auxiliary.reorient_images_header import set_translational_part_to_zero, orient2std
from tools.auxiliary.utils import print_and_run
from labels_manager.tools.aux_methods.sanity_checks import check_path_validity
from tools.correctors.bias_field_corrector4 import bias_field_correction
from main_pipeline.A0_main.subject_parameters_manager import get_list_names_subjects_in_atlas
"""
Processing list for each T1 of each subject:
(there are artefacts shared by multiple modalities, the group subdivision is meaningless. It must be done
subject-wise, using the map of parameters under U_Utils/maps)

Generate intermediate folder
Generate output folder
Orient to standard - fsl
Get mask - subject params.
Cut mask
Bias field correction
Compute registration and lesion mask
"""


def move_to_stereotaxic_coordinate_per_subject(sj, controller):
    print('\nProcessing T1 {} started.\n'.format(sj))

    sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

    study = sj_parameters['study']
    category = sj_parameters['category']

    pfo_sj = jph(root_study_rabbits, 'A_data', study, category, sj)

    pfo_sj_mod  = jph(pfo_sj, 'mod')
    pfo_sj_segm = jph(pfo_sj, 'segm')

    assert os.path.exists(pfo_sj_mod)
    assert os.path.exists(pfo_sj_segm)

    print('Initialise folder structure in stereotaxic coordinates')

    pfo_sc_sj = jph(pfo_sj, '')



    if controller['Reorient_chart_hd']:

        print('- set header bicommissural for each pivotal modality in {0}'.format(options['pivotal_modality']))

        # angles = sp.target_parameters['angles']
        # if isinstance(angles[0], list):
        #     theta = angles[0][1]
        # else:
        #     theta = angles[1]
        #
        # # mods
        # mo = pivotal_mods[0]
        # pfi_chart_atlas_mo = jph(pfo_chart_atlas_mod, '{0}_{1}.nii.gz'.format(sp.target_name, mo))
        # assert os.path.exists(pfi_chart_atlas_mo)
        # # bicomm_header:
        # pfi_chart_atlas_mo_oriented = jph(pfo_tmp, 'bicomm_header_{0}_{1}.nii.gz'.format(sp.target_name, mo))
        # cmd = 'cp {0} {1}'.format(pfi_chart_atlas_mo, pfi_chart_atlas_mo_oriented)
        # print_and_run(cmd)
        # if theta > 0:
        #     lm = LabelsManager()
        #     lm.header.apply_small_rotation(pfi_chart_atlas_mo_oriented,
        #                                    pfi_chart_atlas_mo_oriented,
        #                                    angle=theta, principal_axis='pitch')
        #
        # # mask
        # pfi_chart_atlas_roi_reg_mask = jph(pfo_chart_atlas_masks, '{0}_{1}.nii.gz'.format(
        #     sp.target_name, sp.target_list_suffix_masks[0]))
        # assert os.path.exists(pfi_chart_atlas_roi_reg_mask), pfi_chart_atlas_roi_reg_mask
        # pfi_chart_atlas_reg_mask_reoriented = jph(pfo_tmp, 'bicomm_header_{0}_{1}.nii.gz'.format(
        #     sp.target_name, sp.target_list_suffix_masks[0]))
        # cmd = 'cp {0} {1}'.format(pfi_chart_atlas_roi_reg_mask, pfi_chart_atlas_reg_mask_reoriented)
        # print_and_run(cmd)
        # if theta > 0:
        #     lm = LabelsManager()
        #     lm.header.apply_small_rotation(pfi_chart_atlas_reg_mask_reoriented,
        #                                    pfi_chart_atlas_reg_mask_reoriented,
        #                                    angle=theta, principal_axis='pitch')


def move_to_stereotaxic_coordinate_from_list(subj_list, controller):

    print '\n\n Move to stereotaxic coordinate from list {} \n'.format(subj_list)
    for sj in subj_list:
        move_to_stereotaxic_coordinate_per_subject(sj, controller)


if __name__ == '__main__':
    print('process T1, local run. ')

    controller_steps = {
        'Orient header'           : False,
        'Register_main_modality'  : False,
        'Propagate_to_masks'      : False,
        'Propagate_to_segm'       : False,
        'register roi masks multi-atlas' : False,
        'adjust mask'         : True,
        'cut masks'           : True,
        'step bfc'            : False,
        'create lesion mask'  : True,
        'create reg masks'    : True,
        'save results'        : False,
        'speed'               : True}

    options = {}

    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull = False
    lsm.execute_PTB_ex_vivo = False
    lsm.execute_PTB_in_vivo = False
    lsm.execute_PTB_op_skull = False
    lsm.execute_ACS_ex_vivo = False

    lsm.input_subjects = ['4302']
    lsm.update_ls()

    move_to_stereotaxic_coordinate_from_list(lsm.ls, controller_steps, options)




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

