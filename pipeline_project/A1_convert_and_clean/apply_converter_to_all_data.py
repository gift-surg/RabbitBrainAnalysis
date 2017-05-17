import os
import numpy as np
from os.path import join as jph


from bruker2nifti.study_converter import convert_a_study


root_raw_data    = '/Volumes/sebastianof/rabbits/00_raw_data'
root_destination = '/Volumes/sebastianof/rabbits/01_nifti'


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


def main_converter(PTB_convert_ex_skull=False,
                    PTB_convert_ex_vivo=False,
                    PTB_convert_in_vivo=True,
                    PTB_convert_op_skull=False,
                    ACS_convert_ex_vivo=False):

    if PTB_convert_ex_skull:

        pfo_raw_pilot_ex_skull = jph(root_raw_data, 'PTB', 'ex_skull')
        pfo_destination_ex_skull = jph(root_destination, 'PTB', 'ex_skull')

        convert_a_group(pfo_raw_pilot_ex_skull, pfo_destination_ex_skull)

    if PTB_convert_ex_vivo:

        pfo_raw_pilot_ex_vivo = jph(root_raw_data, 'PTB', 'ex_vivo')
        pfo_destination_ex_vivo = jph(root_destination, 'PTB', 'ex_vivo')

        convert_a_group(pfo_raw_pilot_ex_vivo, pfo_destination_ex_vivo)

    if PTB_convert_in_vivo:

        pfo_raw_pilot_in_vivo = jph(root_raw_data, 'PTB', 'in_vivo')
        pfo_destination_in_vivo = jph(root_destination, 'PTB', 'in_vivo')

        convert_a_group(pfo_raw_pilot_in_vivo, pfo_destination_in_vivo)

    if PTB_convert_op_skull:

        pfo_raw_pilot_op_skull = jph(root_raw_data, 'PTB', 'op_skull')
        pfo_destination_op_skull = jph(root_destination, 'PTB', 'op_skull')

        convert_a_group(pfo_raw_pilot_op_skull, pfo_destination_op_skull)

    if ACS_convert_ex_vivo:

        pfo_raw_acs_ex_vivo = jph(root_raw_data, 'ACS', 'ex_vivo')
        pfo_destination_acs_ex_vivo = jph(root_destination, 'ACS', 'ex_vivo')

        convert_a_group(pfo_raw_acs_ex_vivo, pfo_destination_acs_ex_vivo)


if __name__ == '__main__':

    main_converter()
    #
    # run_thread1 = True
    # run_thread2 = False
    # run_thread3 = False
    #
    # if run_thread1:
    #     main_converter(PTB_convert_ex_skull=True,
    #                    PTB_convert_ex_vivo=True,
    #                    PTB_convert_in_vivo=False,
    #                    PTB_convert_op_skull=False,
    #                    ACS_convert_ex_vivo=False)
    #
    # if run_thread2:
    #     main_converter(PTB_convert_ex_skull=False,
    #                    PTB_convert_ex_vivo=False,
    #                    PTB_convert_in_vivo=True,
    #                    PTB_convert_op_skull=True,
    #                    ACS_convert_ex_vivo=False)
    #
    # if run_thread3:
    #     main_converter(PTB_convert_ex_skull=False,
    #                    PTB_convert_ex_vivo=False,
    #                    PTB_convert_in_vivo=False,
    #                    PTB_convert_op_skull=False,
    #                    ACS_convert_ex_vivo=True)
