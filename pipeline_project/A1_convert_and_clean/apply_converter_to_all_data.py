import os
from os.path import join as jph

from bruker2nifti.study_converter import convert_a_study

from pipeline_project.A0_main.main_controller import subject, ListSubjectsManager
from tools.definitions import root_study_rabbits
from tools.auxiliary.utils import print_and_run


def convert_subjects_from_list(subj_list):

    print '\n\n CONVERTING SUBJECTS {} \n'.format(subj_list)

    for sj in subj_list:
        print 'Subj {} conversion!\n'.format(sj)

        group = subject[sj][0][0]
        category = subject[sj][0][1]
        pfo_input_sj = jph(root_study_rabbits, '00_raw_data', group, category, sj)
        assert os.path.exists(pfo_input_sj)
        pfo_output = jph(root_study_rabbits, '01_nifti', group, category)
        pfo_output_sj = jph(root_study_rabbits, '01_nifti', group, category, sj)

        if os.path.exists(pfo_output_sj):
            cmd = 'rm -r {}'.format(pfo_output_sj)
            print('Folder {} where to convert the study exists already... ERASED!'.format(pfo_output_sj))
            print_and_run(cmd)

        convert_a_study(pfo_input_sj, pfo_output, verbose=0, correct_slope=True, study_name=sj)

if __name__ == '__main__':

    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull = False
    lsm.execute_PTB_ex_vivo  = False
    lsm.execute_PTB_in_vivo  = False
    lsm.execute_PTB_op_skull = False
    lsm.execute_ACS_ex_vivo  = False

    lsm.input_subjects = ['2702', ]  # [ '2502bt1', '2503t1', '2605t1' , '2702t1', '2202t1',
    # '2205t1', '2206t1', '2502bt1']
    #  '3307', '3404']  # '2202t1', '2205t1', '2206t1' -- '2503', '2608', '2702',
    lsm.update_ls()

    print lsm.ls

    convert_subjects_from_list(lsm.ls)
