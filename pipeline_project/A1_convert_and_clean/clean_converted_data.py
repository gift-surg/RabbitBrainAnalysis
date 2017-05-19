import os
import numpy as np
from os.path import join as jph


from tools.correctors.path_cleaner import clean_a_study
from definitions import root_pilot_study_pantopolium


print root_pilot_study_pantopolium
root_nifti = jph(root_pilot_study_pantopolium, '01_nifti')


def cleaner_converted_data(pfo_to_be_cleaned):

    assert os.path.exists(pfo_to_be_cleaned)

    subj_list = np.sort(list(set(os.listdir(pfo_to_be_cleaned)) - {'.DS_Store'}))

    print '\n\n SUBJECTS in {}\n {} \n'.format(pfo_to_be_cleaned, subj_list)
    print subj_list

    for sj in subj_list:
        print 'Study subject {} cleaning!\n'.format(sj)

        clean_a_study(jph(pfo_to_be_cleaned, sj))


def main_cleaner(PTB_clean_ex_skull=False,
                 PTB_clean_ex_vivo=False,
                 PTB_clean_in_vivo=False,
                 PTB_clean_op_skull=True,
                 ACS_clean_ex_vivo=False):
    
    global root_nifti
    
    if PTB_clean_ex_skull:

        cleaner_converted_data(jph(root_nifti, 'PTB', 'ex_skull'))
        
    if PTB_clean_ex_vivo:

        cleaner_converted_data(jph(root_nifti, 'PTB', 'ex_vivo'))
        
    if PTB_clean_in_vivo:
    
        cleaner_converted_data(jph(root_nifti, 'PTB', 'in_vivo'))
    
    if PTB_clean_op_skull:
    
        cleaner_converted_data(jph(root_nifti, 'PTB', 'op_skull'))
    
    if ACS_clean_ex_vivo:
    
        cleaner_converted_data(jph(root_nifti, 'ACS', 'ex_vivo'))


if __name__ == '__main__':
    main_cleaner()
