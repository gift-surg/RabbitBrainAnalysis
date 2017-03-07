import os
from os.path import join as jph
from definitions import root_pilot_study

from tools.auxiliary.utils import print_and_run, reproduce_slice_fourth_dimension_path


def generate_skull_stripped(sj, control):
    """
    PIPELINE
    Take all_modalities and propose the skull stripped version, based on the
     preliminary segmentation propagation.

    Input: all modalities in the all-modalities folder for each subject, and the preliminary segmentation
    Output: preliminary segmentation will provide a brain_mask_from_segmentation (first output of the pipeline)
            mask is used to skull-strip the subjects.
            Finally the V1 modality is multiplied for the FA map.


    :param sj: subkect
    :param control: dictionary with control
    :return:
    """

    ''' path manager '''
    pfo_in_vivo_study = jph(root_pilot_study, 'A_template_atlas_in_vivo')
    pfo_all_modalities = jph(pfo_in_vivo_study, sj, 'all_modalities')
    pfo_all_modalities_no_skull = jph(pfo_in_vivo_study, sj, 'all_modalities_no_skull')

    pfo_segmentations = jph(pfo_in_vivo_study, sj, 'segmentations')
    pfo_masks = jph(pfo_in_vivo_study, sj, 'masks')

    list_all_modalities = ['FA', 'MD', 'S0', 'T1', 'V1']

    ''' pipeline '''
    if control['step_generate_output_folder']:
        cmd = 'mkdir -p {0}'.format(pfo_all_modalities_no_skull)
        print_and_run(cmd, safety_on=control['safety_on'])

    if control['generate_mask_brain']:
        # --- Change this pfi when new, more accurate segmentations are available: --- #
        pfi_segmentation = jph(pfo_segmentations, 'automatic', 'prelim_' + sj + '_template_smol_t3_reg_mask.nii.gz')
        # ---  --  --- #
        pfi_brain_mask = jph(pfo_masks, sj + '_brain_mask_from_segmentation.nii.gz')

        if not os.path.exists(pfi_segmentation):
            raise IOError('Segmentation to create brain mask {} does not exists'.format(pfi_segmentation))

        cmd0 = 'seg_maths {0} -bin {1}'.format(pfi_segmentation, pfi_brain_mask)
        cmd1 = 'seg_maths {0} -fill {0}'.format(pfi_brain_mask)
        cmd2 = 'seg_maths {0} -dil 1 {0}'.format(pfi_brain_mask)
        cmd3 = 'seg_maths {0} -ero 1 {0}'.format(pfi_brain_mask)
        cmd4 = 'seg_maths {0} -smol 1.2 {0}'.format(pfi_brain_mask)

        print_and_run(cmd0, safety_on=control['safety_on'])
        print_and_run(cmd1, safety_on=control['safety_on'])
        print_and_run(cmd2, safety_on=control['safety_on'])
        print_and_run(cmd3, safety_on=control['safety_on'])
        print_and_run(cmd4, safety_on=control['safety_on'])

    if control['skull_strip_all']:

        pfi_brain_mask = jph(pfo_masks, sj + '_brain_mask_from_segmentation.nii.gz')
        pfi_brain_mask_stack = jph(pfo_masks, sj + '_brain_mask_from_segmentation_stack3.nii.gz')

        for mod in list_all_modalities:

            pfi_modality_with_skull = jph(pfo_all_modalities, sj + '_' + mod + '.nii.gz')
            pfi_modality_no_skull   = jph(pfo_all_modalities_no_skull, sj + '_' + mod + '_no_skull.nii.gz')

            if mod == 'V1':
                reproduce_slice_fourth_dimension_path(pfi_brain_mask, pfi_brain_mask_stack, num_slices=3, repetition_axis=3)
                cmd = 'seg_maths {0} -mul {1} {2}'.format(pfi_modality_with_skull, pfi_brain_mask_stack, pfi_modality_no_skull)
                print_and_run(cmd, safety_on=control['safety_on'])
                cmd = 'rm {}'.format(pfi_brain_mask_stack)
                print_and_run(cmd, safety_on=control['safety_on'])
            else:
                cmd = 'seg_maths {0} -mul {1} {2}'.format(pfi_modality_with_skull, pfi_brain_mask, pfi_modality_no_skull)
                print_and_run(cmd, safety_on=control['safety_on'])

    if control['adjust_V1']:

        pfi_FA = jph(pfo_all_modalities_no_skull, sj + '_FA_no_skull.nii.gz')
        pfi_V1 = jph(pfo_all_modalities_no_skull, sj + '_V1_no_skull.nii.gz')
        pfi_FA_stack = jph(pfo_all_modalities_no_skull, sj + '_FA_no_skull_stack.nii.gz')
        reproduce_slice_fourth_dimension_path(pfi_FA, pfi_FA_stack, num_slices=3, repetition_axis=3)

        cmd = 'seg_maths {0} -mul {1} {0}'.format(pfi_V1, pfi_FA_stack)
        print_and_run(cmd, safety_on=control['safety_on'])
        cmd = 'rm {}'.format(pfi_FA_stack)
        print_and_run(cmd, safety_on=control['safety_on'])
