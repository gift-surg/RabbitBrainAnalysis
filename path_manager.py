import os


root_dir = os.path.abspath(os.path.dirname(__file__))

root_path_data = '/Users/sebastiano/Documents/UCL/a_data/bunnies'  # only path to be modified!

path_data_nifti = os.path.join(root_path_data, 'from_leuven', 'nifty_converted')
path_data_raw = os.path.join(root_path_data, 'from_leuven', 'raw_brukert')

path_data_examples = os.path.join(root_path_data, 'z_examples')


path_a_case = os.path.join(path_data_examples, 'test_bias_field', '1305_3D_manually_aligned.nii.gz')