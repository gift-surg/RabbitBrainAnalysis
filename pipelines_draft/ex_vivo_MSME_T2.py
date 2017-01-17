import os
import numpy as np
import nibabel as nib

from definitions import root_ex_vivo_MSME
from tools.correctors.bias_field_corrector4 import bias_field_correction_slicewise
from tools.auxiliary.utils import set_new_data, cut_dwi_image_from_first_slice_mask_path
from tools.correctors.MSME_T2_correctors import corrector_MSME_T2_path


# controller

step_recombine_and_reorient = False
step_extract_first_slice    = False
step_obtain_cutting_mask    = False
step_dilate_mask            = False
step_cutting_roi            = False
step_bfc                    = True  # not supported for 4d volumes. Performed slice-wise.

# Parameters:

subjects = ['1305'] #, '1203', '1305', '1404', '1507', '1510', '1702', '1805', '2002']
dil_mask_factor = 0

# Bias field correction parameters:

bfc_tag = '_bfc_default_'

convergenceThreshold = 0.01
maximumNumberOfIterations = (50, 20, 20, 10)
biasFieldFullWidthAtHalfMaximum = 0.15
wienerFilterNoise = 0.01
numberOfHistogramBins = 200
numberOfControlPoints = (4, 4, 4)
splineOrder = 3


# safety, if on, plot only the command at terminal
safety_on = False
verbose_on = True


for sj in subjects:

    """ RECOMBINE AND REORIENT """
    if step_recombine_and_reorient:

        path_to_original = os.path.join(root_ex_vivo_MSME, sj, 'MSME', sj + '_MSME.nii.gz')
        path_to_oriented = os.path.join(root_ex_vivo_MSME, sj, 'MSME', sj + '_MSME_oriented.nii.gz')

        if verbose_on:
            print '\n Recombine and reorient step for subject {} . '.format(sj)

        # re-orinetation command
        cmd = 'fslorient -deleteorient {0}; ' \
              'fslswapdim {0} x z -y {0}; ' \
              'fslorient -setqformcode 1 {0}; '.format(path_to_oriented)

        if not safety_on:
            corrector_MSME_T2_path(path_to_original, path_to_oriented)
            os.system(cmd)
            print '\n ... And now reoriented for subject {} . '.format(sj)

    """ EXTRACT REGION OF INTERESTS"""
    """ Extract first slice """
    if step_extract_first_slice:

        # create the folder masks:
        cmd_0 = 'mkdir -p {0}'.format(os.path.join(root_ex_vivo_MSME, sj, 'masks'))

        path_to_oriented = os.path.join(root_ex_vivo_MSME, sj, 'MSME', sj + '_MSME_oriented.nii.gz')
        path_first_slice_msme_extracted = os.path.join(root_ex_vivo_MSME, sj, 'masks', sj + '_first_echo_MSME.nii.gz')

        if verbose_on:
            print '\n Extraction first layer MSME: execution for subject {0}.\n'.format(sj)

        if not safety_on:
            os.system(cmd_0)
            nib_msme = nib.load(path_to_oriented)
            # Extract first slice and save as the fixed image - Keep the same header.
            nib_msme_first_slice_data = nib_msme.get_data()[..., 0]
            nib_first_slice_msme = set_new_data(nib.load(path_to_oriented), nib_msme_first_slice_data)
            nib.save(nib_first_slice_msme, path_first_slice_msme_extracted)

    """ Register the cutting mask """
    if step_obtain_cutting_mask:

        cmd_0 = 'mkdir -p {0}'.format(os.path.join(root_ex_vivo_MSME, sj, 'transformations'))

        path_first_slice_msme_extracted = os.path.join(root_ex_vivo_MSME, sj, 'masks', sj + '_first_echo_MSME.nii.gz')

        path_oriented_as_1305_3d_template = os.path.join(root_ex_vivo_MSME, 'templates', '1305_3D.nii.gz')
        path_oriented_as_1305_3d_ciccione = os.path.join(root_ex_vivo_MSME, 'templates', '1305_3D_roi_mask_4.nii.gz')

        path_affine_transformation_output = os.path.join(root_ex_vivo_MSME, sj, 'transformations',
                                                         sj + '_on_unoriented_1305.txt')
        path_3d_warped_output = os.path.join(root_ex_vivo_MSME, 'zz_trash', sj + '_on_unoriented_1305.nii.gz')

        path_mask_output = os.path.join(root_ex_vivo_MSME, sj, 'masks', sj + '_ciccione_roi_mask.nii.gz')

        cmd_1 = 'reg_aladin -ref {0} -flo {1} -aff {2} -res {3} -rigOnly ; '.format(path_first_slice_msme_extracted,
                                                                             path_oriented_as_1305_3d_template,
                                                                             path_affine_transformation_output,
                                                                             path_3d_warped_output)

        cmd_2 = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(path_first_slice_msme_extracted,
                                                                                     path_oriented_as_1305_3d_ciccione,
                                                                                     path_affine_transformation_output,
                                                                                     path_mask_output)

        if verbose_on:
            print '\n Register and propagate ciccione to first slice and save the registered ciccione:' \
                  ' execution for subject {0}.\n'.format(sj)
            print cmd_1
            print cmd_2

        if not safety_on:
            os.system(cmd_0)
            # Register and propagate ciccione to first slice and save the registered ciccione -
            # same header of the 3d image.
            os.system(cmd_1 + cmd_2)

    """ dilate the newly created mask for safety reasons. """
    if step_dilate_mask:

        path_mask = os.path.join(root_ex_vivo_MSME, sj, 'masks', sj +'_ciccione_roi_mask.nii.gz')
        cmd = 'seg_maths {0} -dil {1} {0}'.format(path_mask, dil_mask_factor)

        if verbose_on:
            print cmd

        if not safety_on:
            os.system(cmd)

    """ Cut all the layers of the image with the cutting mask """
    if step_cutting_roi:

        path_to_oriented = os.path.join(root_ex_vivo_MSME, sj, 'MSME', sj + '_MSME_oriented.nii.gz')
        path_mask = os.path.join(root_ex_vivo_MSME, sj, 'masks', sj +'_ciccione_roi_mask.nii.gz')
        path_to_cropped = os.path.join(root_ex_vivo_MSME, sj, 'MSME', sj + '_MSME_cropped.nii.gz')

        if verbose_on:
            print '\nCutting newly-created ciccione mask on the subject: execution for subject {0}.\n'.format(sj)

        if not safety_on:
            cut_dwi_image_from_first_slice_mask_path(path_to_oriented,
                                                     path_mask,
                                                     path_to_cropped)


    """ BIAS FIELD CORRECTION """
    if step_bfc:

        path_to_cropped = os.path.join(root_ex_vivo_MSME, sj, 'MSME', sj + '_MSME_cropped.nii.gz')
        path_to_bfc_corrected = os.path.join(root_ex_vivo_MSME, sj, 'MSME', sj + '_MSME_bfc.nii.gz')

        if verbose_on:
            print '\nBias field correction: execution for subject {0}.\n'.format(sj)

        if not safety_on:

            nib_input = nib.load(path_to_cropped)
            data_bfc_corrected = bias_field_correction_slicewise(nib_input.get_data(),
                                                                 convergenceThreshold=convergenceThreshold,
                                  maximumNumberOfIterations=maximumNumberOfIterations,
                                  biasFieldFullWidthAtHalfMaximum=biasFieldFullWidthAtHalfMaximum,
                                  wienerFilterNoise=wienerFilterNoise,
                                  numberOfHistogramBins=numberOfHistogramBins,
                                  numberOfControlPoints=numberOfControlPoints,
                                  splineOrder=splineOrder,
                                  print_only=safety_on)

            nib_bfc = set_new_data(nib_input, data_bfc_corrected)
            nib.save(nib_bfc, path_to_bfc_corrected)
