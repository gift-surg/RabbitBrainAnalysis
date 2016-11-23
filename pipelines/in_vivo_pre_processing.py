"""
Based on nifty_reg, nifty_seg and freesurfer, should all be installed on the system before running the program.
"""

import os
import numpy as np

from definitions import root_in_vivo_template
from tools.correctors.bias_field_corrector4 import bias_field_correction
from tools.auxiliary.lesion_mask_extractor import simple_lesion_mask_extractor_path

"""
Preliminary template for the selected ex-vivo subject.
"""

########################
# paths templates ROI: #
########################

# TODO provisional: need to create the roi of the in vivo ad hoc
path_subj_1305_templ         = os.path.join(root_in_vivo_template, 'templates', '1305_3D.nii.gz')
path_subj_1305_mask_ciccione = os.path.join(root_in_vivo_template, 'templates', '1305_3D_roi_mask_2.nii.gz')

####################
# Controller:      #
####################

# No need to reorient!
step_thr                   = False
step_register_masks        = False
step_cut_masks             = False
step_bfc                   = True
step_compute_lesion_masks  = False
step_compute_registration_masks = False


safety_on = False
verbose_on = True

####################
# Parameters:      #
####################


subjects = ['0802_t1']

thr = 300

# Registration parameters:

rigid_only_reg_mask = False

if rigid_only_reg_mask:
    suffix_reg_mask = '_rigid'
    suffix_command_reg_mask = ' -rigOnly '
else:
    suffix_reg_mask = '_affine'
    suffix_command_reg_mask = ''

# Bias field correction parameters:

bfc_tag = '_bfc_default_'

convergenceThreshold = 0.001
maximumNumberOfIterations = (50, 50, 50, 50)
biasFieldFullWidthAtHalfMaximum = 0.15
wienerFilterNoise = 0.01
numberOfHistogramBins = 200
numberOfControlPoints = (4, 4, 4)
splineOrder = 3


##################
# PIPELINE:      #
##################


for sj in subjects:

    """ *** PREPROCESSING *** """

    """ THRESHOLD """
    if step_thr:

        path_3d_nii_input = os.path.join(root_in_vivo_template, sj, '3D', sj + '_3D.nii.gz')
        path_3d_nii_output = os.path.join(root_in_vivo_template, sj, '3D', sj + '_3D_thr' + str(thr) + '.nii.gz')

        cmd = 'seg_maths {0} -thr {1} {2}'.format(path_3d_nii_input, thr, path_3d_nii_output)

        if verbose_on:
            print '\nThreshold: execution for subject {0}.\n'.format(sj)
            print cmd

        if not safety_on:
            os.system(cmd)

    """ REGISTER MASKS """
    if step_register_masks:

        path_3d_nii_fixed = os.path.join(root_in_vivo_template, sj, '3D', sj + '_3D_thr' + str(thr) + '.nii.gz')
        path_affine_transformation_output = os.path.join(root_in_vivo_template, sj, 'transformations',
                                                         '1305_on_' + sj + '_3D' + suffix_reg_mask + '.txt')

        path_3d_warped_output = os.path.join(root_in_vivo_template, 'zz_trash', '1305_on_' + sj + '_3D.nii.gz')
        path_resampled_mask_output = os.path.join(root_in_vivo_template, sj, 'masks',
                                                  'ciccione_1305_on_' + sj + '_3D_mask' + suffix_reg_mask + '.nii.gz')

        cmd_1 = 'reg_aladin -ref {0} -flo {1} -aff {2} -res {3} {4} ; '.format(path_3d_nii_fixed,
                                                                               path_subj_1305_templ,
                                                                               path_affine_transformation_output,
                                                                               path_3d_warped_output,
                                                                               suffix_command_reg_mask)
        cmd_2 = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(path_3d_nii_fixed,
                                                                                      path_subj_1305_mask_ciccione,
                                                                                      path_affine_transformation_output,
                                                                                      path_resampled_mask_output)
        if verbose_on:
            print '\nRegistration ciccione mask: execution for subject {0}.\n'.format(sj)
            print cmd_1 + cmd_2

        cmd_0 = 'mkdir -p {0}'.format(os.path.join(root_in_vivo_template, sj, 'transformations'))

        if not safety_on:
            os.system(cmd_0)
            os.system(cmd_1 + cmd_2)

    """ CUT MASKS """
    if step_cut_masks:

        path_3d_nii_input = os.path.join(root_in_vivo_template, sj, '3D', sj + '_3D_thr' + str(thr) + '.nii.gz')
        path_3d_nii_mask  = os.path.join(root_in_vivo_template, sj, 'masks',
                                         'ciccione_1305_on_' + sj + '_3D_mask' + suffix_reg_mask + '.nii.gz')
        path_3d_cropped_roi_result = os.path.join(root_in_vivo_template, sj, '3D',
                                                  sj + '_3D_thr' + str(thr) + '_masked.nii.gz')

        cmd = 'seg_maths {0} -mul {1} {2}'.format(path_3d_nii_input, path_3d_nii_mask, path_3d_cropped_roi_result)

        if verbose_on:
            print '\nCutting newly-created ciccione mask on the subject: execution for subject {0}.\n'.format(sj)
            print cmd

        cmd_0 = 'mkdir -p {0}'.format(os.path.join(root_in_vivo_template, sj, 'masks'))

        if not safety_on:
            os.system(cmd_0)
            os.system(cmd)

    """ BIAS FIELD CORRECTION """
    if step_bfc:

        path_3d_nii_input = os.path.join(root_in_vivo_template, sj, '3D',
                                         sj + '_3D_thr' + str(thr) + '_masked.nii.gz')

        path_3d_nii_output = os.path.join(root_in_vivo_template, sj, '3D',
                                          sj + '_3D_thr' + str(thr) + '_masked' + bfc_tag + '.nii.gz')

        if verbose_on:
            print '\nBias field correction: execution for subject {0}.\n'.format(sj)

        if not safety_on:
            bias_field_correction(path_3d_nii_input, path_3d_nii_output,
                                  pfi_mask=None,
                                  prefix='',
                                  convergenceThreshold=convergenceThreshold,
                                  maximumNumberOfIterations=maximumNumberOfIterations,
                                  biasFieldFullWidthAtHalfMaximum=biasFieldFullWidthAtHalfMaximum,
                                  wienerFilterNoise=wienerFilterNoise,
                                  numberOfHistogramBins=numberOfHistogramBins,
                                  numberOfControlPoints=numberOfControlPoints,
                                  splineOrder=splineOrder,
                                  print_only=safety_on)

    """ *** CREATE LESION MASKS AND REGISTRATION MASKS FOR THE CO-REGISTRATION *** """

    """ COMPUTE LESIONS MASKS """

    # compute lesion masks
    if step_compute_lesion_masks:

        source = os.path.join(root_in_vivo_template, sj, '3D',
                              sj + '_3D_thr' + str(thr) + '_masked' + bfc_tag + '.nii.gz')
        source_ciccione = os.path.join(root_in_vivo_template, sj, 'masks', 'ciccione_1305_on_' + sj +'_3D_mask_affine.nii')
        target_lesion_mask = os.path.join(root_in_vivo_template, sj, 'masks', sj + '_lesion_mask.nii.gz')

        print "Lesions masks extractor for subject {} \n".format(sj)

        simple_lesion_mask_extractor_path(source, target_lesion_mask, source_ciccione, safety_on=safety_on)

    """ COMPUTE REGISTRATION MASKS """

    # compute registration masks from lesions masks
    if step_compute_registration_masks:

            source_ciccione = os.path.join(root_in_vivo_template, sj, 'masks', 'ciccione_1305_on_' + sj +'_3D_mask_affine.nii')
            source_lesion_masks = os.path.join(root_in_vivo_template, sj, 'masks', sj + '_lesion_mask.nii.gz')
            target_registration_masks = os.path.join(root_in_vivo_template, sj, 'masks', sj + '_registration_mask.nii.gz')

            print "Create registration mask for subject {} \n".format(sj)

            cmd = '''seg_maths {0} -sub {1} {2} '''.format(source_ciccione, source_lesion_masks, target_registration_masks)
            print cmd

            if not safety_on:
                os.system(cmd)





