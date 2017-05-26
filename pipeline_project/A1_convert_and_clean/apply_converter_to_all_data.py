import os
from os.path import join as jph

import numpy as np
from bruker2nifti.study_converter import convert_a_study

from definitions import root_study_pantopolium
from pipeline_project.A0_main.main_controller import RunParameters


root_raw_data    = jph(root_study_pantopolium, '00_raw_data')
root_destination = jph(root_study_pantopolium, '01_nifti')


def convert_a_group(pfo_group_to_convert, pfo_goup_destination):

    assert os.path.exists(pfo_group_to_convert)
    assert os.path.exists(pfo_goup_destination)

    subj_list = np.sort(list(set(os.listdir(pfo_group_to_convert)) - {'.DS_Store'}))

    print '\n\n SUBJECTS in {}\n {} \n'.format(pfo_group_to_convert, subj_list)

    for sj in subj_list:
        print 'Subj {} conversion!\n'.format(sj)

        study_in = os.path.join(pfo_group_to_convert, sj)
        assert os.path.isdir(study_in)
        convert_a_study(study_in, pfo_goup_destination, verbose=0, correct_slope=True, study_name=sj)


def execute_converter(rp):

    assert os.path.isdir(root_study_pantopolium), 'Connect pantopolio!'
    assert isinstance(rp, RunParameters)

    if rp.execute_PTB_ex_skull:
        pfo_raw_pilot_ex_skull = jph(root_raw_data, 'PTB', 'ex_skull')
        assert os.path.isdir(pfo_raw_pilot_ex_skull), pfo_raw_pilot_ex_skull
        pfo_destination_ex_skull = jph(root_destination, 'PTB', 'ex_skull')
        convert_a_group(pfo_raw_pilot_ex_skull, pfo_destination_ex_skull)

    if rp.execute_PTB_ex_vivo:
        pfo_raw_pilot_ex_vivo = jph(root_raw_data, 'PTB', 'ex_vivo')
        assert os.path.isdir(pfo_raw_pilot_ex_vivo), pfo_raw_pilot_ex_vivo
        pfo_destination_ex_vivo = jph(root_destination, 'PTB', 'ex_vivo')
        convert_a_group(pfo_raw_pilot_ex_vivo, pfo_destination_ex_vivo)

    if rp.execute_PTB_in_vivo:
        pfo_raw_pilot_in_vivo = jph(root_raw_data, 'PTB', 'in_vivo')
        assert os.path.isdir(pfo_raw_pilot_in_vivo), pfo_raw_pilot_in_vivo
        pfo_destination_in_vivo = jph(root_destination, 'PTB', 'in_vivo')
        convert_a_group(pfo_raw_pilot_in_vivo, pfo_destination_in_vivo)

    if rp.execute_PTB_op_skull:
        pfo_raw_pilot_op_skull = jph(root_raw_data, 'PTB', 'op_skull')
        assert os.path.isdir(pfo_raw_pilot_op_skull), pfo_raw_pilot_op_skull
        pfo_destination_op_skull = jph(root_destination, 'PTB', 'op_skull')
        convert_a_group(pfo_raw_pilot_op_skull, pfo_destination_op_skull)

    if rp.execute_ACS_ex_vivo:
        pfo_raw_acs_ex_vivo = jph(root_raw_data, 'ACS', 'ex_vivo')
        assert os.path.isdir(pfo_raw_acs_ex_vivo), pfo_raw_acs_ex_vivo
        pfo_destination_acs_ex_vivo = jph(root_destination, 'ACS', 'ex_vivo')
        convert_a_group(pfo_raw_acs_ex_vivo, pfo_destination_acs_ex_vivo)


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
