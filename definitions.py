import os
import nibabel as nib
import numpy as np

root_dir = os.path.abspath(os.path.dirname(__file__))


# Before refactoring:

root_path_data = '/Users/sebastiano/Documents/UCL/a_data/bunnies'  # only path to be modified!

path_data_nifti = os.path.join(root_path_data, 'from_leuven', 'nifti_converted')
path_data_raw = os.path.join(root_path_data, 'from_leuven', 'raw_bruker')

path_data_examples = os.path.join(root_path_data, 'z_examples')


path_a_case = os.path.join(path_data_examples, 'test_bias_field', '1305_3D_manually_aligned.nii.gz')

root_ex_vivo_template = os.path.join(root_path_data, 'pipelines', 'ex_vivo_template')

root_in_vivo_template = os.path.join(root_path_data, 'pipelines', 'in_vivo_template')

root_ex_vivo_dwi = os.path.join(root_path_data, 'pipelines', 'ex_vivo_DWI')

root_in_vivo_dwi = os.path.join(root_path_data, 'pipelines', 'in_vivo_DWI')

root_ex_vivo_MSME = os.path.join(root_path_data, 'pipelines', 'ex_vivo_MSME_T2')

root_2_subjects_study = os.path.join(root_path_data, 'pipelines', '2_subjects_study')
root_2_subjects_study_2 = os.path.join(root_path_data, 'pipelines', '2_subjects_study_2')


# after refactoring

root_pilot_study = '/Users/sebastiano/Documents/UCL/a_data/bunnies/pilot_study'




# TODO - Ultra folder structure refactoring

