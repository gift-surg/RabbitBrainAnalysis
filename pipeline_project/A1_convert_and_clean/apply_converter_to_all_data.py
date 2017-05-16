import os
import numpy as np
from os.path import join as jph


from bruker2nifti.study_converter import convert_a_study


root_raw_data    = '/Volumes/sebastianof/rabbits/00_raw_data'
root_destination = '/Volumes/sebastianof/rabbits/01_nifti'


# controller

def main_converter(PTB_convert_ex_skull=False,
                    PTB_convert_ex_vivo=False,
                    PTB_convert_in_vivo=True,
                    PTB_convert_op_skull=False,
                    ACS_convert_ex_vivo=False):

    if PTB_convert_ex_skull:

        pfo_raw_pilot_ex_skull = jph(root_raw_data, 'PTB', 'ex_skull')
        pfo_destination_ex_skull = jph(root_destination, 'PTB', 'ex_skull')

        assert os.path.exists(pfo_raw_pilot_ex_skull)
        assert os.path.exists(pfo_destination_ex_skull)

        subj_list = np.sort(list(set(os.listdir(pfo_raw_pilot_ex_skull)) - {'.DS_Store'}))

        print '\n\n SUBJECTS EX SKULL\n'
        print subj_list

        for sj in subj_list:

            print 'Subj {} conversion!\n'.format(sj)

            study_in = os.path.join(pfo_raw_pilot_ex_skull, sj)
            assert os.path.isdir(study_in)
            convert_a_study(study_in, pfo_destination_ex_skull, verbose=0, correct_slope=True, study_name=sj)

    if PTB_convert_ex_vivo:

        pfo_raw_pilot_ex_vivo = jph(root_raw_data, 'PTB', 'ex_vivo')
        pfo_destination_ex_vivo = jph(root_destination, 'PTB', 'ex_vivo')

        assert os.path.exists(pfo_raw_pilot_ex_vivo)
        assert os.path.exists(pfo_destination_ex_vivo)

        subj_list = np.sort(list(set(os.listdir(pfo_raw_pilot_ex_vivo)) - {'.DS_Store'}))

        print '\n\n SUBJECTS EX VIVO \n'
        print subj_list

        for sj in subj_list:

            print 'Subj {} conversion!\n'.format(sj)

            study_in = os.path.join(pfo_raw_pilot_ex_vivo, sj)
            assert os.path.isdir(study_in)
            convert_a_study(study_in, pfo_destination_ex_vivo, verbose=0, correct_slope=True, study_name=sj)

    if PTB_convert_in_vivo:

        pfo_raw_pilot_in_vivo = jph(root_raw_data, 'PTB', 'in_vivo')
        pfo_destination_in_vivo = jph(root_destination, 'PTB', 'in_vivo')

        assert os.path.exists(pfo_raw_pilot_in_vivo)
        assert os.path.exists(pfo_destination_in_vivo)

        subj_list = np.sort(list(set(os.listdir(pfo_raw_pilot_in_vivo)) - {'.DS_Store'}))

        print '\n\n SUBJECTS IN VIVO \n'
        print subj_list

        for sj in subj_list:

            print 'Subj {} conversion!\n'.format(sj)

            study_in = os.path.join(pfo_raw_pilot_in_vivo, sj)
            assert os.path.isdir(study_in)
            convert_a_study(study_in, pfo_destination_in_vivo, verbose=0, correct_slope=True, study_name=sj)

    if PTB_convert_op_skull:

        pfo_raw_pilot_op_skull = jph(root_raw_data, 'PTB', 'op_skull')
        pfo_destination_op_skull = jph(root_destination, 'PTB', 'op_skull')

        assert os.path.exists(pfo_raw_pilot_op_skull)
        assert os.path.exists(pfo_destination_op_skull)

        subj_list = np.sort(list(set(os.listdir(pfo_raw_pilot_op_skull)) - {'.DS_Store'}))

        print '\n\n SUBJECTS OPEN SKULL \n'
        print subj_list

        for sj in subj_list:

            print 'Subj {} conversion!\n'.format(sj)

            study_in = os.path.join(pfo_raw_pilot_op_skull, sj)
            assert os.path.isdir(study_in)
            convert_a_study(study_in, pfo_destination_op_skull, verbose=0, correct_slope=True, study_name=sj)

    ''' ACS ex vivo  '''

    if ACS_convert_ex_vivo:

        pfo_raw_extra_14 = jph(root_raw_data, 'ACS', 'ex_vivo')
        pfo_destination_extra_14 = jph(root_destination, 'ACS', 'ex_vivo')

        assert os.path.exists(pfo_raw_extra_14)
        assert os.path.exists(pfo_destination_extra_14)

        subj_list = np.sort(list(set(os.listdir(pfo_raw_extra_14)) - {'.DS_Store'}))

        print '\n\n SUBJECTS EXTRA 14 \n'
        print subj_list

        for sj in subj_list:

            print 'Subj {} conversion!\n'.format(sj)

            study_in = os.path.join(pfo_raw_extra_14, sj)
            assert os.path.isdir(study_in)
            convert_a_study(study_in, pfo_destination_extra_14, verbose=0, correct_slope=True, study_name=sj)


# manual multi-thread: run in three different terminals changing false to true in each position


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
