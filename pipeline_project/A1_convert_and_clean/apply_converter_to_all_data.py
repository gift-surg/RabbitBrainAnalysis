import os
from os.path import join as jph

import numpy as np
from bruker2nifti.study_converter import convert_a_study

from definitions import root_study_rabbits
from pipeline_project.A0_main.main_controller import RunParameters


def convert_a_group(pfo_group_to_convert, pfo_group_destination, bypass_subjects=None):

    assert os.path.exists(pfo_group_to_convert)
    assert os.path.exists(pfo_group_destination)

    subj_list = np.sort(list(set(os.listdir(pfo_group_to_convert)) - {'.DS_Store'}))

    if bypass_subjects is not None:
        if set(bypass_subjects).intersection(set(subj_list)) == {}:
            raise IOError
        else:
            subj_list = bypass_subjects

    print '\n\n SUBJECTS in {}\n {} \n'.format(pfo_group_to_convert, subj_list)

    for sj in subj_list:
        print 'Subj {} conversion!\n'.format(sj)

        study_in = os.path.join(pfo_group_to_convert, sj)
        assert os.path.isdir(study_in)

        # if the folder is not empty, eliminate it before doing the conversion
        specific_dest_folder = jph(pfo_group_destination, sj)
        if os.path.exists(specific_dest_folder):
            cmd = 'rm -r {}'.format(specific_dest_folder)
            print('Folder {} where to convert the study exists already... ERASED!'.format(specific_dest_folder))
            os.system(cmd)

        convert_a_study(study_in, pfo_group_destination, verbose=0, correct_slope=True, study_name=sj)


def execute_converter(rp):

    assert isinstance(rp, RunParameters)
    root_raw_data = jph(root_study_rabbits, '00_raw_data')
    root_destination = jph(root_study_rabbits, '01_nifti')

    if rp.execute_PTB_ex_skull:
        study = 'PTB'
        category = 'ex_skull'
        pfo_source = jph(root_raw_data, study, category)
        assert os.path.isdir(pfo_source), pfo_source
        pfo_destination = jph(root_destination, study, category)
        convert_a_group(pfo_source, pfo_destination, bypass_subjects=rp.subjects)

    if rp.execute_PTB_ex_vivo:
        study = 'PTB'
        category = 'ex_vivo'
        pfo_source = jph(root_raw_data, study, category)
        assert os.path.isdir(pfo_source), pfo_source
        pfo_destination = jph(root_destination, study, category)
        convert_a_group(pfo_source, pfo_destination, bypass_subjects=rp.subjects)

    if rp.execute_PTB_in_vivo:
        study = 'PTB'
        category = 'in_vivo'
        pfo_source = jph(root_raw_data, study, category)
        assert os.path.isdir(pfo_source), pfo_source
        pfo_destination = jph(root_destination, study, category)
        convert_a_group(pfo_source, pfo_destination, bypass_subjects=rp.subjects)

    if rp.execute_PTB_op_skull:
        study = 'PTB'
        category = 'op_skull'
        pfo_source = jph(root_raw_data, study, category)
        assert os.path.isdir(pfo_source), pfo_source
        pfo_destination = jph(root_destination, study, category)
        convert_a_group(pfo_source, pfo_destination, bypass_subjects=rp.subjects)

    if rp.execute_ACS_ex_vivo:
        study = 'ACS'
        category = 'ex_vivo'
        pfo_source = jph(root_raw_data, study, category)
        assert os.path.isdir(pfo_source), pfo_source
        pfo_destination = jph(root_destination, study, category)
        convert_a_group(pfo_source, pfo_destination, bypass_subjects=rp.subjects)


if __name__ == '__main__':

    rpa = RunParameters()

    rpa.execute_PTB_ex_skull = True
    rpa.execute_PTB_ex_vivo = True
    rpa.execute_PTB_in_vivo = True
    rpa.execute_PTB_op_skull = True
    rpa.execute_ACS_ex_vivo = True

    rpa.subjects = None
    rpa.update_params()

    execute_converter(rpa)
