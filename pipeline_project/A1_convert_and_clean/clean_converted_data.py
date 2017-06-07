import os
from os.path import join as jph

from definitions import root_study_rabbits
from pipeline_project.A0_main.main_controller import subject, ListSubjectsManager
from tools.correctors.path_cleaner import clean_a_study


def cleaner_converted_data_from_list(subj_list):

    print '\n\n CLEANING CONVERTER SUBJECTS {} \n'.format(subj_list)
    print subj_list

    for sj in subj_list:
        group = subject[sj][0][0]
        category = subject[sj][0][1]
        pfo_to_be_cleaned = jph(root_study_rabbits, '01_nifti', group, category, sj)
        assert os.path.exists(pfo_to_be_cleaned)

        print 'Study subject {} cleaning. \n'.format(sj)

        clean_a_study(pfo_to_be_cleaned)


if __name__ == '__main__':

    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull = False
    lsm.execute_PTB_ex_vivo = False
    lsm.execute_PTB_in_vivo = False
    lsm.execute_PTB_op_skull = False
    lsm.execute_ACS_ex_vivo = False

    lsm.input_subjects = ['2702', ]  # [ '2502bt1', '2503t1', '2605t1' , '2702t1', '2202t1',
    # '2205t1', '2206t1', '2502bt1']
    #  '3307', '3404']  # '2202t1', '2205t1', '2206t1' -- '2503', '2608', '2702',
    lsm.update_ls()

    print lsm.ls

    cleaner_converted_data_from_list(lsm.ls)
