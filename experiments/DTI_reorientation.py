"""
Playground for the manipulation of a test DTI.
See http://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FDT/FAQ#What_conventions_do_the_bvecs_use.3F
And mind that the when the orientation is required, it must be done
BEFORE the processing, in coherence with the b-vectors.
"""

import os
import numpy as np
import nibabel as nib

from definitions import root_ex_vivo_dwi

from tools.auxiliary.squeezer import squeeze_image_from_path
from tools.auxiliary.utils import cut_dwi_image_from_first_slice_mask_path, set_new_data
from tools.parsers.parse_brukert_txt import parse_brukert_dwi_txt
from tools.correctors.slope_corrector import slope_corrector_path
from tools.parsers.separate_shells import separate_shells_txt_path, separate_shells_dwi_path


root_test = '/Users/sebastiano/Documents/UCL/a_data/bunnies/pipelines/ex_vivo_DWI/zz_test_3'

dwi_image = os.path.join(root_test, '1203_DWI.nii.gz')
dwi_txt = os.path.join(root_test, '1203_DWI.txt')


step_reorient          = False

# extract mask and crop
step_extract_first_slice  = False
step_create_1d_layer_mask = False
step_dilate_mask          = False
step_cut_to_mask_dwi      = False

dil_mask_factor = 3

step_extract_b_values  = False
step_correct_slope     = False
step_perform_dti       = True
step_open_and_see      = False

safety_on = False



# Reorient DWI
if step_reorient:

    print 'REORIENT IMAGE \n'

    dwi_reoriented_image = os.path.join(root_test, '1203_DWI_reoriented.nii.gz')
    cmd = ''' cp {0} {1};
          fslorient -deleteorient {1};
          fslswapdim {1} -z -y -x {1};
          fslorient -setqformcode 1 {1};'''.format(dwi_image, dwi_reoriented_image)

    print cmd
    if not safety_on:
        os.system(cmd)


# Create mask and crop it.

"""  Extract first slice of the DWI as a stand-alone image """
if step_extract_first_slice:

    # create the folder masks:
    cmd_0 = 'mkdir -p {0}'.format(os.path.join(root_test, 'masks'))

    path_oriented_as_dwi_1305_3d_template = os.path.join(root_ex_vivo_dwi, 'templates', '1305_3D.nii.gz')
    path_oriented_as_dwi_1305_3d_ciccione = os.path.join(root_ex_vivo_dwi, 'templates', '1305_3D_mask_fin_dil5.nii.gz')

    path_dwi = os.path.join(root_test, '1203_DWI_reoriented.nii.gz')
    path_first_slice_dwi_extracted = os.path.join(root_test, 'masks', '1203_DWI_reoriented_first_slice.nii.gz')

    print '\n Extraction first layer DWI.\n'

    if not safety_on:
        os.system(cmd_0)
        nib_dwi = nib.load(path_dwi)
        # Extract first slice and save as the fixed image - Keep the same header.
        nib_dwi_first_slice_data = nib_dwi.get_data()[..., 0]
        nib_first_slice_dwi = set_new_data(nib.load(path_dwi), nib_dwi_first_slice_data)
        nib.save(nib_first_slice_dwi, path_first_slice_dwi_extracted)

""" Create the 1-time dimension DWI mask """
if step_create_1d_layer_mask:

    cmd_0 = 'mkdir -p {0}'.format(os.path.join(root_test, 'transformations'))

    path_first_slice_dwi_extracted = os.path.join(root_test, 'masks', '1203_DWI_reoriented_first_slice.nii.gz')

    path_oriented_template = os.path.join(root_ex_vivo_dwi, 'templates', '1305_3D.nii.gz')
    path_oriented_mask = os.path.join(root_ex_vivo_dwi, 'templates', '1305_3D_mask_fin_dil5.nii.gz')

    path_affine_transformation_output = os.path.join(root_test, 'transformations', 'orientation_on_template.txt')
    path_3d_warped_output = os.path.join(root_ex_vivo_dwi, 'zz_trash','test_on_unoriented_1305.nii.gz')

    path_mask_output = os.path.join(root_test, 'masks', 'oriented_roi_mask.nii.gz')

    cmd_1 = 'reg_aladin -ref {0} -flo {1} -aff {2} -res {3} -rigOnly ; '.format(path_first_slice_dwi_extracted,
                                                                         path_oriented_template,
                                                                         path_affine_transformation_output,
                                                                         path_3d_warped_output)

    cmd_2 = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(path_first_slice_dwi_extracted,
                                                                                 path_oriented_mask,
                                                                                 path_affine_transformation_output,
                                                                                 path_mask_output)

    print '\n Register and propagate ciccione to first slice'
    print cmd_1
    print cmd_2

    if not safety_on:
        os.system(cmd_0)
        # Register and propagate ciccione to first slice and save the registered ciccione -
        # same header of the 3d image.
        os.system(cmd_1 + cmd_2)

""" dilate the newly created mask for safety reasons. """
if step_dilate_mask:

    path_mask = os.path.join(root_test, 'masks', 'oriented_roi_mask.nii.gz')
    cmd = 'seg_maths {0} -dil {1} {0}'.format(path_mask, dil_mask_factor)

    print cmd

    if not safety_on:
        os.system(cmd)

""" cut the mask from the anatomical images - this will reduce the size of the DWI significantly """
if step_cut_to_mask_dwi:

    path_dwi = os.path.join(root_test, '1203_DWI_reoriented.nii.gz')
    path_mask = os.path.join(root_test, 'masks', 'oriented_roi_mask.nii.gz')
    path_dwi_cropped = os.path.join(root_test, '1203_DWI_reoriented_cropped.nii.gz')

    print '\nCutting newly-created ciccione mask on the subject.\n'

    if not safety_on:
        cut_dwi_image_from_first_slice_mask_path(path_dwi,
                                                 path_mask,
                                                 path_dwi_cropped)

# Extract b-vals and b-vect and correct for the orientation

if step_extract_b_values:

    # expected
    rotation_matrix = np.array([[0, 0, -1], [0, -1, 0], [-1, 0, 0]])

    # expected with flipping convention
    #rotation_matrix = np.array([[0, 0, -1],[0, -1, 0],[1, 0, 0]])

    print '\nParse the txt data files b-val b-vect and slope.\n'
    print 'matrix = {0}'.format(rotation_matrix)

    if not safety_on:
        parse_brukert_dwi_txt(dwi_txt,
                              output_folder=root_test,
                              prefix='txt_',
                              rotation=rotation_matrix)

# Correct for the slope:

if step_correct_slope:

        path_slopes_txt_input = os.path.join(root_test, 'txt_VisuCoreDataSlope.txt')

        path_input_dwi = os.path.join(root_test, '1203_DWI_reoriented_cropped.nii.gz')
        path_output_dwi_slope_corrected = os.path.join(root_test, '1203_DWI_slope_corrected.nii.gz')

        print '\n Slope correction.\n'

        if not safety_on:
            slope_corrector_path(path_slopes_txt_input,
                                 path_input_dwi,
                                 path_output_dwi_slope_corrected)

# Perform DTI:

if step_perform_dti:

    # dtifit -k ScaledData.nii.gz -b DwEffBval.txt -m Brain_mask.nii.gz -r bvecs.txt -w --save_tensor -o DTI/DT
    path_input_dwi    = os.path.join(root_test, '1203_DWI_slope_corrected.nii.gz')
    path_input_bval   = os.path.join(root_test, 'txt_DwEffBval.txt')
    path_input_bvect  = os.path.join(root_test, 'txt_DwGradVec.txt')
    dwi_roi_mask      = os.path.join(root_test, 'masks', 'oriented_roi_mask.nii.gz')

    output_folder = os.path.join(root_test, 'analysis_fsl')
    path_output_dti    = os.path.join(output_folder, 'fsl_')

    # create the folder analysis_fit if nor present:
    cmd_0 = 'mkdir -p {0}'.format(output_folder)

    cmd = 'dtifit -k {0} -b {1} -r {2} -m {3} ' \
          '-w --save_tensor -o {4}'.format(path_input_dwi,
                                           path_input_bval,
                                           path_input_bvect,
                                           dwi_roi_mask,
                                           path_output_dti)

    print 'DTI fit mechanism! \n'
    print cmd

    if not safety_on:
        os.system(cmd_0)
        os.system(cmd)

# OBSERVE NOW! If the values makes sense.

if step_open_and_see:
    pass
    #os.system('mrview ')