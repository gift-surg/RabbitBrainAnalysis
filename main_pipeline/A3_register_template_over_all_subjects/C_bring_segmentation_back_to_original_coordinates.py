# if sp.controller_fuser['Inter_mod_space_propagation'] and len(sp.target_list_suffix_modalities) > 1:
#     # THIS HAPPENS ALL WITHIN THE TARGET - no interaction with multi-atlas here.
#     # Rigid registration and propagationfrom the pivot of the main space modality
#     # to the others pivots of the space mod.
#
#     # leading modality target paths
#     pfi_leading_mod_0_anatomy = jph(sp.target_pfo, sp.arch_modalities_name_folder,
#                                     '{0}_{1}.nii.gz'.format(sp.target_name, leading_mod))
#     pfi_leading_mod_0_reg_mask = jph(sp.target_pfo, sp.arch_masks_name_folder, '{0}_{1}_{2}.nii.gz'.format(
#         sp.target_name, leading_mod, sp.target_list_suffix_masks[1]))
#
#     for space_mod_j in sp.target_list_suffix_modalities[1:]:
#         leading_mod_j = space_mod_j[0]
#         assert not leading_mod == leading_mod_j
#
#         # other modality target paths
#         pfi_leading_mod_j_anatomy = jph(sp.target_pfo, sp.arch_modalities_name_folder,
#                                         '{0}_{1}.nii.gz'.format(sp.target_name, leading_mod_j))
#         # as the mask is only for the first time-point, if more than one time-point is present, extract the first
#         # time-point in the temporary folder.
#         nib_leading_mod_j_anatomy = nib.load(pfi_leading_mod_j_anatomy)
#         if len(nib_leading_mod_j_anatomy.shape) > 3:
#             pfi_tmp_fist_timepoint = jph(pfo_tmp_fusion,
#                                          'first_timepoint_' + '{0}_{1}.nii.gz'.format(sp.target_name, leading_mod_j))
#             cmd = 'seg_maths {0} -tp 0 {1}'.format(pfi_leading_mod_j_anatomy, pfi_tmp_fist_timepoint)
#             print_and_run(cmd)
#             pfi_leading_mod_j_anatomy = pfi_tmp_fist_timepoint
#
#         pfi_leading_mod_j_mask = jph(sp.target_pfo, sp.arch_masks_name_folder, '{0}_{1}_{2}.nii.gz'.format(
#             sp.target_name, leading_mod_j, sp.target_list_suffix_masks[1]))
#
#         # REGISTER mod_0 over mod_j:
#         print('- rig register mod_space {0} to mod space {1}'.format(
#             sp.target_list_suffix_modalities[0], space_mod_j))
#         pfi_rigid_transf_mod_0_to_mod_j = jph(
#             pfo_tmp_fusion, 'inter_mod_{0}_over_{1}_aff_transf.txt'.format(leading_mod, leading_mod_j))
#         pfi_rigid_warp_mod_0_to_mod_j = jph(
#             pfo_tmp_fusion, 'inter_mod_{0}_over_{1}_warp.nii.gz'.format(leading_mod, leading_mod_j))
#
#         cmd = 'reg_aladin -ref {0} -rmask {1} -flo {2} -fmask {3} -aff {4} -res {5} -omp {6} -rigOnly  '. \
#             format(pfi_leading_mod_j_anatomy, pfi_leading_mod_j_mask,
#                    pfi_leading_mod_0_anatomy, pfi_leading_mod_0_reg_mask,
#                    pfi_rigid_transf_mod_0_to_mod_j, pfi_rigid_warp_mod_0_to_mod_j,
#                    sp.num_cores_run)
#         print(cmd)
#         print_and_run(cmd)
#
#         # PROPAGATE all result_ segmentation mod_0 over mod_j - in the mod_j space:
#         for filename in os.listdir(pfo_tmp_fusion):
#             if filename.startswith('result_' + sp.target_name + '_' + leading_mod + '__'):
#                 print('\n- rig propagate {0}, mod_space {1} to mod space {2}'.format(
#                     filename, sp.target_list_suffix_modalities[0], space_mod_j))
#                 pfi_segm_mod_0 = jph(pfo_tmp_fusion, filename)
#                 pfi_segm_mod_j = jph(pfo_tmp_fusion, filename.replace(
#                     'result_' + sp.target_name + '_' + leading_mod + '__',
#                     'result_' + sp.target_name + '_' + leading_mod_j + '__'))
#
#                 cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
#                     pfi_leading_mod_j_anatomy, pfi_segm_mod_0, pfi_rigid_transf_mod_0_to_mod_j, pfi_segm_mod_j)
#                 print_and_run(cmd)