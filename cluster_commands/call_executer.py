import argparse
import os
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(dir_path))

from tools.definitions import pfo_subjects_parameters
from main_pipeline.A0_main.subject_parameters_manager import list_all_subjects
from main_pipeline.A0_main.main_executer import main_runner


parser = argparse.ArgumentParser()
parser.add_argument('-i', dest='str_input', type=str, required=True)
args = parser.parse_args()

all_subj = list_all_subjects(pfo_subjects_parameters)

if args.str_input in all_subj:
    main_runner([args.str_input, ])
else:
    print('The subject {} is not in the list, no computations done.'.format(args.str_input))
