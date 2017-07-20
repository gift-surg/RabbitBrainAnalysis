"""
Propagate and fuse T1
"""
import os
from os.path import join as jph

from tools.definitions import root_study_rabbits, root_internal_template
from pipeline_project.A0_main.main_controller import ListSubjectsManager, subject, templ_subjects
from propagate_and_fuse_utils import rigid_propagation_inter_modality, \
    rigid_orientation_from_histo_to_given_coordinates
from propagator import propagate_all_to_one


def propagate_and_fuse_per_subject_list_over_all_modalities(subj_list,
                                                            controller_fuser,
                                                            controller_propagator,
                                                            controller_inter_modality_propagator):
    print '\n\n Propagating and fusing per category. ' \
          'Target group folder {0}\n' \
          'Subjects template {1}\n'.format(subj_list, templ_subjects)

    for sj_target in subj_list:

        group = subject[sj_target][0][0]
        category = subject[sj_target][0][1]
        pfo_target = jph(root_study_rabbits, 'A_data', group, category, sj_target)

        assert os.path.isdir(pfo_target)
        # If sj_target belongs to the template simply reorient the manual segmentation constituting the template.
        if sj_target in templ_subjects:
            print('\n\n{} is in the template, alignment of the manual segmentation'.format(sj_target))
            sj_source = sj_target
            pfo_source = jph(root_internal_template, sj_target)
            rigid_orientation_from_histo_to_given_coordinates(sj_source, pfo_source, sj_target, pfo_target,
                                                              controller_propagator)
        else:
            print('\n\n{} is NOT in the template, Propagation started'.format(sj_target))
            propagate_all_to_one(sj_target, pfo_target, root_internal_template, templ_subjects, controller_fuser)
        # if the S0 is available you can transfer the obtained segmentation on other modalities.
        if os.path.exists(jph(pfo_target, 'mod', sj_target + '_S0.nii.gz')):  # dwi have been computed. Ready to move
            print('\n\nPropagation of the segmentation {} T1 to other modalities.'.format(sj_target))
            # propagate within modalities
            # pfo_sj = jph(pfo_target, sj_target)
            rigid_propagation_inter_modality(sj_target, pfo_target, controller_inter_modality_propagator)
        else:
            print 'NO DWI for subject {} yet'.format(sj_target)


if __name__ == '__main__':

    print('Propagate and fuse, local run. ')

    controller_fuser_ = {'set header bicommissural'    : False,
                         'aff alignment'               : False,
                         'Propagate aff to segm'       : False,
                         'Propagate aff to mask'       : False,
                         'Get differential BFC'        : False,
                         'N-rig alignment'             : False,
                         'Propagate to target n-rig'   : False,
                         'Smooth result'               : False,
                         'Stack warps and segm'        : False,
                         'Fuse'                        : False,
                         'save result'                 : False,
                         'dominant method'             : 'STEPS'
                         }

    controller_propagator_ = {'set header bicommissural'  : False,
                              'rig alignment'             : False,
                              'Propagate aff to segm'     : False,
                              'Propagate aff to mask'     : False,
                              'Smooth'                    : False,
                              'save result'               : False}

    controller_inter_modality_propagator_ = {'compensate squeezing'           : True,
                                             'rig register to S0'             : True,
                                             'rig propagate to S0'            : True,
                                             'rig register MSME_up to MSME'   : True,
                                             'rig propagate segm_S0 to MSME'  : True}

    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull = False
    lsm.execute_PTB_ex_vivo = False
    lsm.execute_PTB_in_vivo = False
    lsm.execute_PTB_op_skull = False
    lsm.execute_ACS_ex_vivo = False

    lsm.input_subjects = ['3103', ]  # [ '2502bt1', '2503t1', '2605t1' , '2702t1', '2202t1',
    # '2205t1', '2206t1', '2502bt1']
    #  '3307', '3404']  # '2202t1', '2205t1', '2206t1' -- '2503', '2608', '2702',
    lsm.update_ls()

    propagate_and_fuse_per_subject_list_over_all_modalities(lsm.ls, controller_fuser_, controller_propagator_,
                                                            controller_inter_modality_propagator_)
