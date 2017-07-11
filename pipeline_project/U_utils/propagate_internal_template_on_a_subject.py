import os
from os.path import join as jph

from tools.definitions import root_study_rabbits, root_internal_template
from pipeline_project.A0_main.main_controller import subject, templ_subjects
from pipeline_project.A3_register_template_over_all_subjects.template_registration_utils import propagate_all_to_one


def propagate_and_fuse_over_new_subject(subj_list, controller_fuser):

    for sj_target in subj_list:

        group = subject[sj_target][0][0]
        category = subject[sj_target][0][1]
        pfo_target = jph(root_study_rabbits, 'A_data', group, category, sj_target)

        assert os.path.isdir(pfo_target)

        print('\n\n{} is NOT in the template, Propagation started'.format(sj_target))
        propagate_all_to_one(sj_target, pfo_target, root_internal_template, templ_subjects, controller_fuser)


if __name__ == '__main__':

    print('Propagate and fuse, local run. ')

    controller_fuser_ = {'set header bicommissural'  : True,
                         'aff alignment'             : True,
                         'Propagate aff to segm'     : True,
                         'Propagate aff to mask'     : True,
                         'Get differential BFC'      : True,
                         'N-rig alignment'           : True,
                         'Propagate to target n-rig' : True,
                         'Smooth result'             : True,
                         'Stack warps and segm'      : True,
                         'Fuse'                      : True,
                         'save result'               : True
                         }

    new_subject = ['0000', ]
    propagate_and_fuse_over_new_subject(new_subject, controller_fuser_)
