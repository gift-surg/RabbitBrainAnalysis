import os
import numpy as np
from os.path import join as jph


from bruker2nifti.scan_converter import convert_a_scan
from bruker2nifti.study_converter import convert_a_study


root_raw_data    = '/Volumes/sebastianof/rabbits/0_raw_data'
root_destination = '/Volumes/sebastianof/rabbits/0_nifti'

# controller
convert_ex_skull = False
convert_ex_vivo  = False
convert_in_vivo  = False
convert_op_skull = False
convert_extra_14 = False


''' convert pilot '''

if convert_ex_skull:

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
        # HEAD SUPINE HERE!
        convert_a_study(study_in, pfo_destination_ex_skull, verbose=0, correct_slope=True, study_name=sj)


if convert_ex_vivo:

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


if convert_in_vivo:

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


if convert_op_skull:

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


''' convert extra_14 '''
if convert_extra_14:

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
