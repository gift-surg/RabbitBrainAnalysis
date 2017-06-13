import os
from os.path import join as jph

from tools.definitions import root_study_rabbits
from pipeline_project.A0_main.main_controller import subject


# working directory:
here = os.path.abspath(os.path.dirname(__file__))

# fetch the g_ratios for each subject and for each region
subjects_list_input = []
pfi_list_records_subjects_output = []

for sj in subjects_list_input:
    group = subject[sj][0][0]
    category = subject[sj][0][1]
    pfi_record_sj = jph(root_study_rabbits, 'A_data', group, category, sj, 'records', sj + '_records.npy')

    pfi_list_records_subjects_output.append(pfi_record_sj)

    # TODO from here!
