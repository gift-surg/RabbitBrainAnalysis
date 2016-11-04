"""
Based on nifty_fit, should be installed on the system before running the program.
"""
import os
import numpy as np
import nibabel as nib

from definitions import root_ex_vivo_dwi
from tools.auxiliary.squeezer import squeeze_image_from_path
from tools.auxiliary.utils import reproduce_slice_fourth_dimension_path
from tools.parsers.parse_brukert_txt import parse_brukert_dwi_txt


# paths

# Controller
step_squeeze                           = False
copy_and_reorient_mask_from_template   = True
cut_dwi_with_masks                     = False
step_extract_bval_b_vect_slope         = False
step_extract_compute_tensor_map        = False

# only at the end of the process!
step_reorient                           = False

# safety, if on, plot only the command at terminal
safety_on = True


# Parameters
subjects = ['1201', '1203', '1305', '1404', '1507', '1510', '1702', '1805']


# dtifit -k ScaledData.nii.gz -b DwEffBval.txt -m Brain_mask.nii.gz -r bvecs.txt -w --save_tensor -o DTI/DT
# http://www.cabiatl.com/Resources/Course/tutorial/html/dti.html
# http://www.mccauslandcenter.sc.edu/crnl/sw/tutorial/html/dti.html
# fit_dwi -source imput_image.nii.gz -bval b_values -bvec b_vectors -mask mask of the image


""" SQUEEZE """
if step_squeeze:

    for sj in subjects:

        path_dwi_nii_original = os.path.join(root_ex_vivo_dwi, sj, 'DWI', sj + '_DWI_original.nii.gz')
        path_dwi_nii_squeezed = os.path.join(root_ex_vivo_dwi, sj, 'DWI', sj + '_DWI.nii.gz')
        cmd1 = ' cp {0} {1} '.format(path_dwi_nii_original, path_dwi_nii_squeezed)
        cmd2 = ' squeezer({0} {1}) '

        print '\n Squeeze for DWI images: execution for subject {0}.\n'.format(sj)

        print cmd1
        print cmd2
        if not safety_on:
            os.system(cmd1)
            print squeeze_image_from_path(path_dwi_nii_squeezed, path_dwi_nii_squeezed)

""" Bring the masks from the 3D pipelines, reorient them as the DWI, extend their slices to the same dwi dimension """
if copy_and_reorient_mask_from_template:

    for sj in subjects:
        path_3d_nii_oriented_mask_ciccione = ''
        path_3d_nii_mask_for_dwi = ''

        print '\n Copy, reoriend and adapt mask for DWI: execution for subject {0}.\n'.format(sj)

        #fslorient -deleteorient $MSK; fslswapdim $MSK z y -x $MSK; fslorient -setqformcode 1 $MSK;
        cmd = ''' cp {0} {1};
                  fslorient -deleteorient {1};
                  fslswapdim {1} x y z {1};
                  fslorient -setqformcode 1 {1};'''.format(path_3d_nii_oriented_mask_ciccione, path_3d_nii_mask_for_dwi)

        print cmd

        # adapt the mask to the shape of the dwi
        path_dwi_to_take_the_shape = ''
        d = nib.load(path_dwi_to_take_the_shape).shape[-1]

        print 'reproduce_slice_fourth_dimension_path(path_3d_nii_mask_for_dwi, path_3d_nii_mask_for_dwi, d)'

        if not safety_on:
            reproduce_slice_fourth_dimension_path(path_3d_nii_mask_for_dwi, path_3d_nii_mask_for_dwi, d)
            os.system(cmd)


""" cut the mask from the anatomical images """
if cut_dwi_with_masks:

    for sj in subjects:

        path_dwi_nii_input = ''
        path_dwi_nii_mask  = ''
        path_3d_cropped_roi_result = ''

        print '\nCutting newly-created ciccione mask on the subject: execution for subject {0}.\n'.format(sj)

        cmd = 'seg_maths {0} -mul {1} {2}'.format(path_dwi_nii_input, path_dwi_nii_mask, path_3d_cropped_roi_result)

        print cmd
        if not safety_on:
            os.system(cmd)


""" step_extract_bval_b_vect_slope """

if step_extract_bval_b_vect_slope:

    for sj in subjects:

        path_dwi_txt_input = ''

        print '\nParse the txt data files b-val b-vect and slopes: execution for subject {0}.\n'.format(sj)

        parse_brukert_dwi_txt(path_dwi_txt_input, output_folder=os.path.dirname(path_dwi_txt_input))


""" correct for the slopes on the trimmed images """



""" Finally! Perform the DWI analysi """







""" REORIENT data - only after all the analysis!!! """
if step_reorient:

    for sj in subjects:

        path_3d_nii_original = os.path.join(root_ex_vivo_dwi, sj, '3D', sj + '_3D_original.nii.gz')
        path_3d_nii_oriented = os.path.join(root_ex_vivo_dwi, sj, '3D', sj + '_3D_zzz.nii.gz')

        print '\nReorient: execution for subject {0}.\n'.format(sj)

        # Orientation to be confirmed!!
        cmd = ''' cp {0} {1};
                  fslorient -deleteorient {1};
                  fslswapdim {1} x y z {1};
                  fslorient -setqformcode 1 {1};'''.format(path_3d_nii_original, path_3d_nii_oriented)
        print cmd
        if not safety_on:
            os.system(cmd)

