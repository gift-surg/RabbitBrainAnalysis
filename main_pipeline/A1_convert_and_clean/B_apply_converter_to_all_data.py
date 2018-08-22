import os
from os.path import join as jph
import pickle
from bruker2nifti.converter import Bruker2Nifti

from tools.definitions import pfo_subjects_parameters
from main_pipeline.A0_main.main_controller import ListSubjectsManager
from tools.definitions import root_study_rabbits
from nilabel.tools.aux_methods.utils import print_and_run


def converter_given_pfo_input_and_pfo_output(pfo_input_sj, pfo_output, sj_name):
    """
    Converter auxiliary function related to subject name and path to folder to convert and where to convert.
    Externalised to avoid code repetitions, as called twice.
    :param pfo_input_sj: input folder to convert
    :param pfo_output: input folder where to convert
    :param sj_name: usual sj parameter
    :return:
    """
    print_and_run('mkdir -p {}'.format(pfo_output))
    pfo_output_sj = jph(pfo_output, sj_name)

    if os.path.exists(pfo_output_sj):
        cmd = 'rm -r {}'.format(pfo_output_sj)
        print('Folder {} where to convert the study exists already... ERASED!'.format(pfo_output_sj))
        print_and_run(cmd)

    conv = Bruker2Nifti(pfo_input_sj, pfo_output, study_name=sj_name)
    conv.correct_slope = True
    conv.verbose = 1
    conv.convert()


def convert_single_subject(sj):

    print '\n\nSubj {} conversion!\n'.format(sj)

    sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

    study = sj_parameters['study']
    category = sj_parameters['category']

    pfo_input_sj = jph(root_study_rabbits, '01_raw_data_unzipped_TMP', study, category, sj)
    assert os.path.exists(pfo_input_sj), pfo_input_sj
    pfo_output = jph(root_study_rabbits, '02_nifti', study, category)

    converter_given_pfo_input_and_pfo_output(pfo_input_sj, pfo_output, sj)

    # Check for external files
    # |---> Secondary study to be merged. If any convert it as well (unzipping must have happened in module A_).
    sj_exts = sj_parameters['merge_with']
    if sj_exts is not None:
        print('\nExternal files related to subject {} found. Conversion in started.'.format(sj))
        for sj_ext in sj_exts:
            print('Converting file {} associated with subject {}'.format(sj_ext, sj))
            pfo_input_sj_ext = jph(root_study_rabbits, '01_raw_data_unzipped_TMP', study, category, sj_ext)
            assert os.path.exists(pfo_input_sj_ext), pfo_input_sj_ext
            pfo_output_ext = jph(root_study_rabbits, '02_nifti', study, category)

            converter_given_pfo_input_and_pfo_output(pfo_input_sj_ext, pfo_output_ext, sj_ext)


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
