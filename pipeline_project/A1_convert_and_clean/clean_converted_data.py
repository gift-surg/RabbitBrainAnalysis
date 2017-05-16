import os
import numpy as np
from os.path import join as jph


from tools.correctors.path_cleaner import clean_a_study
from definitions import root_pilot_study_pantopolium


print root_pilot_study_pantopolium
root_nifti = jph(root_pilot_study_pantopolium, '01_nifti')

# controller
PTB_clean_ex_skull = False
PTB_clean_ex_vivo  = False
PTB_clean_in_vivo  = True
PTB_clean_op_skull = False
ACS_clean_ex_vivo = False


''' convert pilot '''

if PTB_clean_ex_skull:

    pfo_PTB_ex_skull = jph(root_nifti, 'PTB', 'ex_skull')

    assert os.path.exists(pfo_PTB_ex_skull)

    subj_list = np.sort(list(set(os.listdir(pfo_PTB_ex_skull)) - {'.DS_Store'}))

    print '\n\n SUBJECTS EX SKULL\n'
    print subj_list

    for sj in subj_list:

        print 'Study subject {} cleaning!\n'.format(sj)

        clean_a_study(jph(pfo_PTB_ex_skull, sj))


if PTB_clean_ex_vivo:

    pfo_PTB_ex_vivo = jph(root_nifti, 'PTB', 'ex_vivo')

    assert os.path.exists(pfo_PTB_ex_vivo)

    subj_list = np.sort(list(set(os.listdir(pfo_PTB_ex_vivo)) - {'.DS_Store'}))

    print '\n\n SUBJECTS EX SKULL\n'
    print subj_list

    for sj in subj_list:
        print 'Study subject {} cleaning!\n'.format(sj)

        clean_a_study(jph(pfo_PTB_ex_vivo, sj))


if PTB_clean_in_vivo:

    pfo_PTB_in_vivo = jph(root_nifti, 'PTB', 'in_vivo')

    assert os.path.exists(pfo_PTB_in_vivo)

    subj_list = np.sort(list(set(os.listdir(pfo_PTB_in_vivo)) - {'.DS_Store'}))

    print '\n\n SUBJECTS EX SKULL\n'
    print subj_list

    for sj in subj_list:
        print 'Study subject {} cleaning!\n'.format(sj)

        clean_a_study(jph(pfo_PTB_in_vivo, sj))


if PTB_clean_op_skull:

    pfo_PTB_op_skull = jph(root_nifti, 'PTB', 'in_vivo')

    assert os.path.exists(pfo_PTB_op_skull)

    subj_list = np.sort(list(set(os.listdir(pfo_PTB_op_skull)) - {'.DS_Store'}))

    print '\n\n SUBJECTS EX SKULL\n'
    print subj_list

    for sj in subj_list:
        print 'Study subject {} cleaning!\n'.format(sj)

        clean_a_study(jph(pfo_PTB_op_skull, sj))


''' convert extra_14 '''

if ACS_clean_ex_vivo:

    pfo_ACS_ex_vivo = jph(root_nifti, 'ACS', 'ex_vivo')

    assert os.path.exists(pfo_ACS_ex_vivo)

    subj_list = np.sort(list(set(os.listdir(pfo_ACS_ex_vivo)) - {'.DS_Store'}))

    print '\n\n SUBJECTS EX SKULL\n'
    print subj_list

    for sj in subj_list:
        print 'Study subject {} cleaning!\n'.format(sj)

        clean_a_study(jph(pfo_ACS_ex_vivo, sj))
