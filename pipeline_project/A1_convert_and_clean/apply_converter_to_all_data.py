import os
from os.path import join as jph
import pickle
from bruker2nifti.converter import Bruker2Nifti

from tools.definitions import pfo_subjects_parameters
from pipeline_project.A0_main.main_controller import ListSubjectsManager
from tools.definitions import root_study_rabbits
from tools.auxiliary.utils import print_and_run
from labels_manager.tools.aux_methods.sanity_checks import check_path_validity


def convert_subjects_from_list(subj_list):

    print '\n\n CONVERTING SUBJECTS {} \n'.format(subj_list)

    for sj in subj_list:
        print 'Subj {} conversion!\n'.format(sj)

        sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

        group = sj_parameters['group']
        category = sj_parameters['category']

        pfo_input_sj = jph(root_study_rabbits, '00_raw_data', group, category, sj)
        check_path_validity(pfo_input_sj)
        pfo_output = jph(root_study_rabbits, '01_nifti', group, category)
        pfo_output_sj = jph(root_study_rabbits, '01_nifti', group, category, sj)

        if os.path.exists(pfo_output_sj):
            cmd = 'rm -r {}'.format(pfo_output_sj)
            print('Folder {} where to convert the study exists already... ERASED!'.format(pfo_output_sj))
            print_and_run(cmd)

        conv = Bruker2Nifti(pfo_input_sj, pfo_output, study_name=sj)
        conv.correct_slope = True
        conv.verbose = 0
        conv.convert()


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
