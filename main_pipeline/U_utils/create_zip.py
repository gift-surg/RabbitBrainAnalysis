import os
from os.path import join as jph
import pickle

from LABelsToolkit.tools.aux_methods.utils import print_and_run

from tools.definitions import pfo_subjects_parameters
from tools.definitions import root_study_rabbits
from main_pipeline.A0_main.main_controller import ListSubjectsManager


def zipper_from_subject_list(subject_list):

    print('ZIPPER!')

    for sj in subject_list:

        print('-zipping {}'.format(sj))

        pfi_param = jph(pfo_subjects_parameters, sj)

        assert os.path.exists(pfi_param)

        sj_parameters = pickle.load(open(pfi_param, 'r'))

        study = sj_parameters['study']
        category = sj_parameters['category']

        pfo_main = jph(root_study_rabbits, '00_raw_data_zipped', study, category)

        pfi_input_unzipped_folder = jph(pfo_main, sj)
        assert os.path.exists(pfi_input_unzipped_folder), pfi_input_unzipped_folder

        cmd = 'pushd {0}; zip -r {1} {2} -x ".DS_store" -x "__MACOSX" '.format(pfo_main, '{}.zip'.format(sj), sj)

        os.system(cmd)


if __name__ == '__main__':

    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull  = True
    lsm.execute_PTB_ex_vivo   = True
    lsm.execute_PTB_in_vivo   = True
    lsm.execute_PTB_op_skull  = True
    lsm.execute_ACS_ex_vivo01 = False
    lsm.execute_ACS_ex_vivo02 = True
    lsm.update_ls()

    lsm.append(['12307', '12308', '12309', '12402', '12504', '12505', '12607', '12608', '12609', '12610'])

    print lsm.ls

    # zipper_from_subject_list(['0213403'])
