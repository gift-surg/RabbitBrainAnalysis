import os
from os.path import join as jph

import numpy as np

from definitions import root_study_rabbits
from pipeline_project.A0_main.main_controller import RunParameters
from tools.correctors.path_cleaner import clean_a_study


def cleaner_converted_data(pfo_to_be_cleaned, bypass_subjects=None):

    assert os.path.exists(pfo_to_be_cleaned)

    subj_list = np.sort(list(set(os.listdir(pfo_to_be_cleaned)) - {'.DS_Store'}))

    # allow to force the subj_list to be the input tuple bypass subject, chosen by the user.
    if bypass_subjects is not None:

        if set(bypass_subjects).intersection(set(subj_list)) == {}:
            raise IOError
        else:
            subj_list = bypass_subjects

    print '\n\n SUBJECTS in {}\n {} \n'.format(pfo_to_be_cleaned, subj_list)
    print subj_list

    for sj in subj_list:
        print 'Study subject {} cleaning!\n'.format(sj)

        clean_a_study(jph(pfo_to_be_cleaned, sj))


def execute_cleaner(rp):

    assert isinstance(rp, RunParameters)

    root_nifti = jph(root_study_rabbits, '01_nifti')

    if rp.execute_PTB_ex_skull:
        study = 'PTB'
        category = 'ex_skull'
        pfo_target = jph(root_nifti, study, category)
        assert os.path.exists(pfo_target)
        cleaner_converted_data(pfo_target, bypass_subjects=rp.subjects)

    if rp.execute_PTB_ex_vivo:
        study = 'PTB'
        category = 'ex_vivo'
        pfo_target = jph(root_nifti, study, category)
        assert os.path.exists(pfo_target)
        cleaner_converted_data(pfo_target, bypass_subjects=rp.subjects)

    if rp.execute_PTB_in_vivo:
        study = 'PTB'
        category = 'in_vivo'
        pfo_target = jph(root_nifti, study, category)
        assert os.path.exists(pfo_target)
        cleaner_converted_data(pfo_target, bypass_subjects=rp.subjects)

    if rp.execute_PTB_op_skull:
        study = 'PTB'
        category = 'op_skull'
        pfo_target = jph(root_nifti, study, category)
        assert os.path.exists(pfo_target)
        cleaner_converted_data(pfo_target, bypass_subjects=rp.subjects)

    if rp.execute_ACS_ex_vivo:
        study = 'ACS'
        category = 'ex_vivo'
        pfo_target = jph(root_nifti, study, category)
        assert os.path.exists(pfo_target)
        cleaner_converted_data(pfo_target, bypass_subjects=rp.subjects)


if __name__ == '__main__':

    rpa = RunParameters()

    rpa.execute_PTB_ex_skull = True
    rpa.execute_PTB_ex_vivo = True
    rpa.execute_PTB_in_vivo = True
    rpa.execute_PTB_op_skull = True
    rpa.execute_ACS_ex_vivo = True

    execute_cleaner(rpa)
