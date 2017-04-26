"""
Quick and dirty module to apply dtfit to a folder containing appropriate files.
"""
import os


# in input folder we want to find input_dwi b_values, b_vectors, mask
pfi_input_folder  = '/Users/sebastiano/Desktop/test_fsl_dir/2503_t1_LSP'
pfi_output_folder = os.path.join(pfi_input_folder, 'z_fsl_elaboration')

# check input folder
if not os.path.exists(pfi_input_folder):
    raise IOError('Input folder {} does not exist'.format(pfi_input_folder))


# create output folder if not exists
os.system('mkdir -p {}'.format(pfi_output_folder))

# collect data and see if they exists

subject_name = '2503_t1'
pfi_input_dwi    = os.path.join(pfi_input_folder, subject_name + '_DWI.nii.gz')
pfi_input_bvals  = os.path.join(pfi_input_folder, subject_name + '_DwEffBval.txt')
pfi_input_bvects = os.path.join(pfi_input_folder, subject_name + '_DwGradVec.txt')
pfi_roi_mask_dwi = os.path.join(pfi_input_folder, subject_name + '_DWI_mask.nii.gz')

for path_j in [pfi_input_dwi, pfi_input_bvals, pfi_input_bvects, pfi_roi_mask_dwi]:
    if not os.path.exists(path_j):
        raise IOError('file {} does not exist'.format(path_j))

# collect commands to change folder and apply fsl
here = os.getcwd()

cmd0 = 'cd {}'.format(pfi_output_folder)

cmd1 = 'dtifit -k {0} -b {1} -r {2} -m {3} -w --save_tensor -o {4}'.format(pfi_input_dwi,
                                                                           pfi_input_bvals,
                                                                           pfi_input_bvects,
                                                                           pfi_roi_mask_dwi,
                                                                           pfi_output_folder)
cmd2 = 'cd {}'.format(here)

# execute commands
os.system(cmd0)
os.system(cmd1)
os.system(cmd2)


for i in range(1, 4):
    os.system('seg_maths {0} -abs {0}'.format(os.path.join(pfi_input_folder,
                                                           'z_fsl_elaboration_V' + str(i) + '.nii.gz')))
