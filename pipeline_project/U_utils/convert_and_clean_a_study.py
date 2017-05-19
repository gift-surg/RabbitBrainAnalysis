import numpy as np
import os

from bruker2nifti.scan_converter import convert_a_scan
from bruker2nifti.study_converter import convert_a_study

from tools.correctors.path_cleaner import clean_a_study


if 0:

    root = '/Users/sebastiano/Desktop/test_PV/'
    study_out = os.path.join(root, 'nifti')
    assert os.path.isdir(study_out)

    for sj in ['1702', '2702']:
        study_in = os.path.join(root, 'raw', sj)
        assert os.path.isdir(study_in)
        convert_a_study(study_in, study_out, verbose=2, correct_slope=True, study_name=sj)

if 0:
    # source = '/Volumes/sebastianof/rabbits/00_raw_data/PTB/ex_vivo/3604'
    source = '/Users/sebastiano/Downloads/3604'
    list_subjects = np.sort(list(set(os.listdir(source)) - {'.DS_Store'}))
    # destination = '/Users/sebastianof/rabbits/00_nifti/PTB/ex_vivo/'
    destination = '/Users/sebastiano/Downloads/ex_vivo/'

    convert_a_study(source, destination, study_name='3604')

    # clean_a_study('/Users/sebastianof/rabbits/01_nifti/PTB/ex_vivo/3604')
    clean_a_study('/Users/sebastiano/Downloads/ex_vivo/3604')

if 1:
    source = '/Volumes/sebastianof/rabbits/00_raw_data/test_study/Trial_0702'
    destination = '/Volumes/sebastianof/rabbits/01_nifti/test_study/'
    convert_a_study(source, destination, study_name='Trial_0702')

    # clean_a_study('/Users/sebastianof/rabbits/01_nifti/PTB/ex_vivo/3604')
    clean_a_study('/Volumes/sebastianof/rabbits/01_nifti/test_study/Trial_0702')
