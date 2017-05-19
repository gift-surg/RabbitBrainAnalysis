"""
Propagate and fuse T1
"""

import os
from os.path import join as jph

from propagate_and_fuse_utils import propagate_and_fuse_per_group_over_all_modalities
from definitions import root_pilot_study_pantopolium, root_pilot_study_dropbox
from pipeline_project.U_utils.maps import templ_subjects


def propagate_and_fuse_all(controller_fuser,
                           controller_propagator,
                           controller_inter_modality_propagator,
                           pfo_templ_subjects,
                           list_templ_subjects,
                           propagate_and_fuse_PTB_ex_skull=True,
                           propagate_and_fuse_PTB_ex_vivo=True,
                           propagate_and_fuse_PTB_in_vivo=True,
                           propagate_and_fuse_PTB_op_skull=True,
                           propagate_and_fuse_ACS_ex_vivo=True):

    print root_pilot_study_pantopolium
    root_data = jph(root_pilot_study_pantopolium, 'A_data')

    if propagate_and_fuse_PTB_ex_skull:
        pfo_PTB_ex_skull_data = jph(root_data, 'PTB', 'ex_skull')

        tuple_subjects = ()  # can force the input to a predefined input list of subjects if they exists.

        propagate_and_fuse_per_group_over_all_modalities(controller_fuser,
                                                         controller_propagator,
                                                         controller_inter_modality_propagator,
                                                         pfo_PTB_ex_skull_data,
                                                         pfo_templ_subjects,
                                                         list_templ_subjects,
                                                         bypass_subjects=tuple_subjects)

    if propagate_and_fuse_PTB_ex_vivo:
        pfo_PTB_ex_vivo_data = jph(root_data, 'PTB', 'ex_vivo')

        tuple_subjects = ()

        propagate_and_fuse_per_group_over_all_modalities(controller_fuser,
                                                         controller_propagator,
                                                         controller_inter_modality_propagator,
                                                         pfo_PTB_ex_vivo_data,
                                                         pfo_templ_subjects,
                                                         list_templ_subjects,
                                                         bypass_subjects=tuple_subjects)

    if propagate_and_fuse_PTB_in_vivo:
        pfo_PTB_in_vivo_data = jph(root_data, 'PTB', 'in_vivo')

        tuple_subjects = ()

        propagate_and_fuse_per_group_over_all_modalities(controller_fuser,
                                                         controller_propagator,
                                                         controller_inter_modality_propagator,
                                                         pfo_PTB_in_vivo_data,
                                                         pfo_templ_subjects,
                                                         list_templ_subjects,
                                                         bypass_subjects=tuple_subjects)

    if propagate_and_fuse_PTB_op_skull:
        pfo_PTB_op_skull_data = jph(root_data, 'PTB', 'op_skull')

        tuple_subjects = ()

        propagate_and_fuse_per_group_over_all_modalities(controller_fuser,
                                                         controller_propagator,
                                                         controller_inter_modality_propagator,
                                                         pfo_PTB_op_skull_data,
                                                         pfo_templ_subjects,
                                                         list_templ_subjects,
                                                         bypass_subjects=tuple_subjects)

    if propagate_and_fuse_ACS_ex_vivo:
        pfo_ACS_ex_vivo_data = jph(root_data, 'ACS', 'ex_vivo')

        tuple_subjects = ()

        propagate_and_fuse_per_group_over_all_modalities(controller_fuser,
                                                         controller_propagator,
                                                         controller_inter_modality_propagator,
                                                         pfo_ACS_ex_vivo_data,
                                                         pfo_templ_subjects,
                                                         list_templ_subjects,
                                                         bypass_subjects=tuple_subjects)


if __name__ == '__main__':

    if not os.path.isdir('/Volumes/sebastianof/rabbits/'):
        raise IOError('Connect pantopolio!')

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

    controller_propagator_ = {'set header bicommissural'   : True,
                              'rig alignment'              : True,
                              'Propagate aff to segm'      : True,
                              'Propagate aff to mask'      : True,
                              'Smooth'                     : True,
                              'save result'                : True}

    controller_inter_modality_propagator_ = {'rig register to S0'       : True,
                                             'rig propagate to S0'      : True,
                                             'rig register to MSME_up'  : True,
                                             'rig propagate to MSME_up' : True,
                                             'MSME_up to MSME'          : True}

    pfo_templ_subjects_input = jph(root_pilot_study_dropbox, 'A_internal_template')
    list_templ_subjects_input = templ_subjects

    propagate_and_fuse_all(controller_fuser_,
                           controller_propagator_,
                           controller_inter_modality_propagator_,
                           pfo_templ_subjects_input,
                           list_templ_subjects_input,
                           propagate_and_fuse_PTB_ex_skull=True,
                           propagate_and_fuse_PTB_ex_vivo=True,
                           propagate_and_fuse_PTB_in_vivo=True,
                           propagate_and_fuse_PTB_op_skull=True,
                           propagate_and_fuse_ACS_ex_vivo=True)
