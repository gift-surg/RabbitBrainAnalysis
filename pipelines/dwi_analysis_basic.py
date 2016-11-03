"""
Based on nifty_fit, should be installed on the system before running the program.
"""
import os
import numpy as np

from definitions import root_ex_vivo_dwi
from tools.auxiliary import squeezer

# paths

# Controller
step_squeeze                      = False
import_mask_from_template         = True
step_extract_bval_b_vect_slope    = False
step_extract_compute_tensor_map   = False

# only at the end of the process!
step_reorient                     = False

safety_on = False



# Parameters
subjects = ['1201', '1203', '1305', '1404', '1507', '1510', '1702', '1805']





# dtifit -k ScaledData.nii.gz -b DwEffBval.txt -m Brain_mask.nii.gz -r bvecs.txt -w --save_tensor -o DTI/DT
# http://www.cabiatl.com/Resources/Course/tutorial/html/dti.html
# http://www.mccauslandcenter.sc.edu/crnl/sw/tutorial/html/dti.html
# fit_dwi -source imput_image.nii.gz -bval b_values -bvec b_vectors -mask mask of the image


""" SQUEEZE """
if step_squeeze:

    for sj in subjects:
        path_dwi_nii_current = os.path.join(root_ex_vivo_dwi, sj, 'DWI', sj + '_DWI.nii.gz')
        path_dwi_nii_original = os.path.join(root_ex_vivo_dwi, sj, 'DWI', sj + '_DWI_original.nii.gz')
        cmd = ''' cp {0} {1} '''.format(path_dwi_nii_current, path_dwi_nii_original)

        print cmd
        if not safety_on:
            os.system(cmd)



if import_mask_from_template:
    #fslorient -deleteorient $MSK; fslswapdim $MSK z y -x $MSK; fslorient -setqformcode 1 $MSK;
    pass



""" REORIENT """
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

