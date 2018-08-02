import os
from os.path import join as jph
import pickle
from bruker2nifti.converter import Bruker2Nifti

from tools.definitions import pfo_subjects_parameters
from main_pipeline.A0_main.main_controller import ListSubjectsManager
from tools.definitions import root_study_rabbits
from LABelsToolkit.tools.aux_methods.utils import print_and_run
from LABelsToolkit.tools.aux_methods.sanity_checks import check_path_validity


def convert_single_subject(sj):
    print '\n\nSubj {} conversion!\n'.format(sj)

    sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

    study = sj_parameters['study']
    category = sj_parameters['category']

    pfo_input_sj = jph(root_study_rabbits, '01_raw_data_unzipped_TMP', study, category, sj)
    check_path_validity(pfo_input_sj)
    pfo_output = jph(root_study_rabbits, '02_nifti', study, category)
    print_and_run('mkdir -p {}'.format(pfo_output))
    pfo_output_sj = jph(pfo_output, sj)

    if os.path.exists(pfo_output_sj):
        cmd = 'rm -r {}'.format(pfo_output_sj)
        print('Folder {} where to convert the study exists already... ERASED!'.format(pfo_output_sj))
        print_and_run(cmd)

    conv = Bruker2Nifti(pfo_input_sj, pfo_output, study_name=sj)
    conv.correct_slope = True
    conv.verbose = 1
    conv.convert()

    # check for external files - secondary study to be merged
    if sj_parameters['merge_with'] is not None:

        sj_ext = sj_parameters['merge_with']

        # phase 0: unzip:
        pfo_input_sj_ext_zipped = jph(root_study_rabbits, '00_raw_data_zipped', study, category, sj_ext)

        if not os.path.exists(pfo_input_sj_ext_zipped):
            raise IOError('Declared external study for subject {} in folder {} not found'.format(sj, pfo_input_sj_ext_zipped))

        pfo_input_sj_ext = jph(root_study_rabbits, '01_raw_data_unzipped_TMP', study, category, sj_ext)
        cmd = 'tar -xvf {} -C {}'.format(pfo_input_sj_ext_zipped, pfo_input_sj_ext)
        print cmd
        print_and_run(cmd)

        # Phase 1: convert:
        pfo_output_ext = jph(root_study_rabbits, '02_nifti', study, category)

        conv = Bruker2Nifti(pfo_input_sj_ext, pfo_output_ext, study_name=sj_ext)
        conv.correct_slope = True
        conv.verbose = 1
        conv.convert()

        # Phase 2: merge the two folder structures with extra names:
        pfo_output_sj_ext = jph(root_study_rabbits, '02_nifti', study, category, sj_ext)

        # for each folder in the externally converted file, move them in the main study with additional name.


def convert_subjects_from_list(subj_list):

    print '\n\n CONVERTING SUBJECTS {} \n'.format(subj_list)

    for sj in subj_list:
        convert_single_subject(sj)


if __name__ == '__main__':

    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull = False
    lsm.execute_PTB_ex_vivo  = False
    lsm.execute_PTB_in_vivo  = False
    lsm.execute_PTB_op_skull = False
    lsm.execute_ACS_ex_vivo  = False

    lsm.input_subjects = ['4303', ]  # [ '2502bt1', '2503t1', '2605t1' , '2702t1', '2202t1',
    # '2205t1', '2206t1', '2502bt1']
    #  '3307', '3404']  # '2202t1', '2205t1', '2206t1' -- '2503', '2608', '2702',
    lsm.update_ls()

    print lsm.ls

    convert_subjects_from_list(lsm.ls)
