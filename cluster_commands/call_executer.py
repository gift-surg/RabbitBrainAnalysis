import argparse
import os
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.dirname(dir_path))

from pipeline_project.A0_main.main_controller import subjects_controller
from pipeline_project.A0_main.main_executer import main_runner


parser = argparse.ArgumentParser()
parser.add_argument('-i', dest='str_input', type=str, required=True)
args = parser.parse_args()

if args.str_input in subjects_controller.keys():
    main_runner([args.str_input, ])
else:
    print('The subject {} is not in the list, no computations done.'.format(args.str_input))
