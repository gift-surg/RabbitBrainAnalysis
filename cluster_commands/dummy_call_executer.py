import argparse
import os
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path)
sys.path.append(os.path.dirname(dir_path))

print dir_path
print os.path.dirname(dir_path)
from pipeline_project.A0_main.main_executer import main_runner
# from definitions import root_study_rabbits

parser = argparse.ArgumentParser()
parser.add_argument('-i', dest='str_input', type=str, required=True)
args = parser.parse_args()


f = open('../output_{}.txt'.format(args.str_input), 'w+')
f.writelines(args.str_input + '\n')
# f.writelines(root_study_rabbits + '\n')
f.writelines(main_runner.__file__ + '\n')
f.close()


