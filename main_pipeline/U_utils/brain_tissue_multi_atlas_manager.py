"""
Script to create the brain tissue multi atlas for the skull stripping
based on segmentation propagation and label fusion.
"""
import os
import pickle
from os.path import join as jph

from tools.definitions import root_atlas_BT, pfo_subjects_parameters, multi_atlas_brain_tissue_subjects, \
    root_study_rabbits

from LABelsToolkit.tools.aux_methods.utils import print_and_run
from LABelsToolkit.main import LABelsToolkit


def create_brain_tissue_multi_atlas(sj_list, controller):

    for sj in sj_list:
        print('Adding subject {} to brain tissue multi atlas. \n'.format(sj))

        sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

        study = sj_parameters['study']
        category = sj_parameters['category']

        root_sj = jph(root_study_rabbits, 'A_data', study, category, sj)

        assert os.path.exists(root_sj)

        # input data:
        pfi_T1_sj   = jph(root_sj, 'mod', '{}_T1.nii.gz'.format(sj))
        pfi_T1_segm = jph(root_sj, 'segm', '{}_T1_segm.nii.gz'.format(sj))

        # copy to destination (BT = brain tissue multi atlas):

        root_sj_BT = jph(root_atlas_BT, sj)
        if controller['Delete_first']:
            print_and_run('rm -r {}'.format(root_sj_BT), short_path_output=False)

        print_and_run('mkdir -p {}'.format(root_sj_BT))

        pfi_T1_sj_BT = jph(root_sj_BT, '{}_T1.nii.gz'.format(sj))
        pfi_brain_tissue_sj_BT = jph(root_sj_BT, '{}_brain_tissue.nii.gz'.format(sj))

        print_and_run('cp {0} {1}'.format(pfi_T1_sj, pfi_T1_sj_BT))
        print_and_run('cp {0} {1}'.format(pfi_T1_segm, pfi_brain_tissue_sj_BT))

        # Elaborate data in destination:
        # -- from segmentation to brain tissue:

        cmd = 'seg_maths {0} -bin {0}; ' \
              'seg_maths {0} -dil 1 {0}; ' \
              'seg_maths {0} -fill {0}; ' \
              'seg_maths {0} -ero 1 {0} '.format(pfi_brain_tissue_sj_BT)

        print_and_run(cmd)

        # -- from brain tissue to roi mask (dilated of the brain tissue):
        pfi_roi_mask_BT = jph(root_sj_BT, '{}_roi_mask.nii.gz'.format(sj))
        cmd1 = 'cp {} {}'.format(pfi_brain_tissue_sj_BT, pfi_roi_mask_BT)
        print_and_run(cmd1)

        cmd2 = 'seg_maths {0} -dil 3 {0}'.format(pfi_roi_mask_BT)
        print_and_run(cmd2)


def extract_brain_tissue_from_multi_atlas(target_T1, output_roi_mask, output_brain_mask, target_pre_mask=None,
                                          root_atlas_BT=root_atlas_BT,
                                          multi_atlas_subjects_list=multi_atlas_brain_tissue_subjects,
                                          pfo_tmp='.z_tmp', alpha=0):
    """
    sj: subjects in the multi-atlas. Target: element to be segmented.
    :param target_T1:
    :param output_roi_mask:
    :param output_brain_mask:
    :param target_pre_mask:
    :param root_atlas_BT:
    :param multi_atlas_subjects_list:
    :param pfo_tmp:
    :param alpha: angle to rotate the sj in the template
    :return:
    """

    assert os.path.exists(target_T1)



    pfi_moving_T1 =

        # --- Get the angle difference from histological (template) to bicommissural (data) and orient header ---
        if isinstance(sj_parameters['angles'][0], list):
            angles = sj_parameters['angles'][0]
        else:
            angles = sj_parameters['angles']

        angle_parameter = angles[1]

        pfi_sj_ref_coord_system_hd_oriented = jph(pfo_tmp, 'reference_for_T1_hd_oriented.nii.gz')
        pfi_reference_brain_tissue_hd_oriented = jph(pfo_tmp, 'reference_for_brain_tissue_hd_oriented.nii.gz')
        pfi_reference_reg_mask_hd_oriented = jph(pfo_tmp, 'reference_for_reg_mask_hd_oriented.nii.gz')

        lm = LABelsToolkit()
        lm.header.apply_small_rotation(pfi_sj_ref_coord_system, pfi_sj_ref_coord_system_hd_oriented,
                                       angle=angle_parameter, principal_axis='pitch')
        lm.header.apply_small_rotation(pfi_reference_brain_tissue, pfi_reference_brain_tissue_hd_oriented,
                                       angle=angle_parameter, principal_axis='pitch')
        lm.header.apply_small_rotation(pfi_reference_reg_mask, pfi_reference_reg_mask_hd_oriented,
                                       angle=angle_parameter, principal_axis='pitch')

        # set translational part to zero
        lm.header.modify_translational_part(pfi_sj_ref_coord_system_hd_oriented, pfi_sj_ref_coord_system_hd_oriented,
                                            np.array([0, 0, 0]))
        lm.header.modify_translational_part(pfi_reference_brain_tissue_hd_oriented, pfi_reference_brain_tissue_hd_oriented,
                                            np.array([0, 0, 0]))
        lm.header.modify_translational_part(pfi_reference_reg_mask_hd_oriented, pfi_reference_reg_mask_hd_oriented,
                                            np.array([0, 0, 0]))

        # get the registration mask as reg_mask and brain tissue product:
        pfi_reg_mask_times_brain_tissue_affine_for_sj = jph(pfo_tmp,
                                                            'reference_for_roi_mask_times_brain_tissue_hd_oriented.nii.gz')
        cmd = 'seg_maths {0} -mul {1} {2}'.format(pfi_reference_brain_tissue_hd_oriented,
                                                  pfi_reference_reg_mask_hd_oriented,
                                                  pfi_reg_mask_times_brain_tissue_affine_for_sj)
        print_and_run(cmd)

        pfi_affine_transformation_ref_on_subject = jph(pfo_tmp, 'aff_ref_{0}_on_{1}.txt'.format(atlas_sj, sj))
        pfi_3d_warped_ref_on_subject = jph(pfo_tmp, 'warp_ref_{0}_on_{1}.nii.gz'.format(atlas_sj, sj))
        cmd = 'reg_aladin -ref {0} -flo {1} -fmask {2} -aff {3} -res {4} -omp {5} -speeeeed '.format(
            pfi_std,
            pfi_sj_ref_coord_system_hd_oriented,
            pfi_reg_mask_times_brain_tissue_affine_for_sj,
            pfi_affine_transformation_ref_on_subject,
            pfi_3d_warped_ref_on_subject,
            num_cores_run)
        print cmd
        print_and_run(cmd)

        print('- propagate roi masks {}'.format(sj))

        assert check_path_validity(pfi_affine_transformation_ref_on_subject)
        pfi_brain_tissue_from_multi_atlas_sj = \
            jph(pfo_tmp, '{0}_T1_roi_mask_from_atlas{1}_not_adjusted.nii.gz'.format(sj, atlas_sj))
        cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
            pfi_std,
            pfi_reference_brain_tissue_hd_oriented,
            pfi_affine_transformation_ref_on_subject,
            pfi_brain_tissue_from_multi_atlas_sj)
        print_and_run(cmd)

        list_brain_mask_registered_on_target.append(pfi_brain_tissue_from_multi_atlas_sj)

        # label fusion MV of the region of interest for the final region of interest:

        # create the stack of the registered roi masks:


    pfi_stack_roi_mask = jph(pfo_tmp, '{0}_T1_roi_masks_from_atlases_stack.nii.gz'.format(sj))
    lt = LABelsToolkit()
    lt.manipulate_shape.stack_list_pfi_images(list_brain_mask_registered_on_target, pfi_stack_roi_mask)

    # get output from the stack:
    cmd = 'seg_maths {0}  -merge {1} {2} '.format(
        jph(pfo_tmp, '{0}_T1_roi_mask_from_atlas{1}_not_adjusted.nii.gz'.format(sj, list_names_subjects_in_atlas[0])),
        len(list_names_subjects_in_atlas) - 1,
        4
    )
    for p in list_names_subjects_in_atlas[1:]:
        cmd += ' {} '.format(jph(pfo_tmp, '{0}_T1_roi_mask_from_atlas{1}_not_adjusted.nii.gz'.format(sj, p)))
    cmd += ' {} '.format(pfi_stack_roi_mask)
    print_and_run(cmd)

    # merge the roi masks in one:
    pfi_roi_mask_not_adjusted_multi = jph(pfo_tmp, sj + '_T1_roi_mask_not_adjusted_MV.nii.gz')
    cmd = 'seg_LabFusion  -in {0} -out {1} -MV '.format(pfi_stack_roi_mask, pfi_roi_mask_not_adjusted_multi)
    print_and_run(cmd)












if __name__ == '__main__':

    controller_creator = {'Delete_first' : True}

    # create_brain_tissue_multi_atlas(multi_atlas_brain_tissue_subjects, controller_creator)

    extract_brain_tissue()






