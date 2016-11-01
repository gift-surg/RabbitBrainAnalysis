import os


root_dir = os.path.abspath(os.path.dirname(__file__))

root_path_data = '/Users/sebastiano/UCL/a_data/bunnies'
path_data_nifti = os.path.join(root_path_data, 'from_leuven', 'nifty_converted')
path_data_raw = os.path.join(root_path_data, 'from_leuven', 'raw_brukert')

path_data_examples = os.path.join(root_path_data, 'z_examples')
