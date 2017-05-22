"""
Propagate and fuse T1
"""

import os
from os.path import join as jph

from definitions import root_pilot_study_pantopolium, root_pilot_study_dropbox
from pipeline_project.A0_main.main_controller import templ_subjects, RunParameters
from propagate_and_fuse_utils import propagate_and_fuse_per_group_over_all_modalities


def execute_propag_and_fuse_all(controller_fuser,
                                controller_propagator,
                                controller_inter_modality_propagator,
                                pfo_templ_subjects,
                                list_templ_subjects,
                                rp):

    assert os.path.isdir(root_pilot_study_pantopolium), 'Connect pantopolio!'
    assert isinstance(rp, RunParameters)

    root_data = jph(root_pilot_study_pantopolium, 'A_data')

    if rp.execute_PTB_ex_skull:
        pfo_PTB_ex_skull_data = jph(root_data, 'PTB', 'ex_skull')

        propagate_and_fuse_per_group_over_all_modalities(controller_fuser,
                                                         controller_propagator,
                                                         controller_inter_modality_propagator,
                                                         pfo_PTB_ex_skull_data,
                                                         pfo_templ_subjects,
                                                         list_templ_subjects,
                                                         bypass_subjects=rp.subjects)

    if rp.execute_PTB_ex_vivo:
        pfo_PTB_ex_vivo_data = jph(root_data, 'PTB', 'ex_vivo')

        propagate_and_fuse_per_group_over_all_modalities(controller_fuser,
                                                         controller_propagator,
                                                         controller_inter_modality_propagator,
                                                         pfo_PTB_ex_vivo_data,
                                                         pfo_templ_subjects,
                                                         list_templ_subjects,
                                                         bypass_subjects=rp.subjects)

    if rp.execute_PTB_in_vivo:
        pfo_PTB_in_vivo_data = jph(root_data, 'PTB', 'in_vivo')

        propagate_and_fuse_per_group_over_all_modalities(controller_fuser,
                                                         controller_propagator,
                                                         controller_inter_modality_propagator,
                                                         pfo_PTB_in_vivo_data,
                                                         pfo_templ_subjects,
                                                         list_templ_subjects,
                                                         bypass_subjects=rp.subjects)

    if rp.execute_PTB_op_skull:
        pfo_PTB_op_skull_data = jph(root_data, 'PTB', 'op_skull')

        propagate_and_fuse_per_group_over_all_modalities(controller_fuser,
                                                         controller_propagator,
                                                         controller_inter_modality_propagator,
                                                         pfo_PTB_op_skull_data,
                                                         pfo_templ_subjects,
                                                         list_templ_subjects,
                                                         bypass_subjects=rp.subjects)

    if rp.execute_ACS_ex_vivo:
        pfo_ACS_ex_vivo_data = jph(root_data, 'ACS', 'ex_vivo')

        propagate_and_fuse_per_group_over_all_modalities(controller_fuser,
                                                         controller_propagator,
                                                         controller_inter_modality_propagator,
                                                         pfo_ACS_ex_vivo_data,
                                                         pfo_templ_subjects,
                                                         list_templ_subjects,
                                                         bypass_subjects=rp.subjects)


if __name__ == '__main__':

    controller_fuser_ = {'set header bicommissural'  : False,
                         'aff alignment'             : False,
                         'Propagate aff to segm'     : False,
                         'Propagate aff to mask'     : False,
                         'Get differential BFC'      : False,
                         'N-rig alignment'           : False,
                         'Propagate to target n-rig' : False,
                         'Smooth result'             : False,
                         'Stack warps and segm'      : False,
                         'Fuse'                      : False,
                         'save result'               : False
                         }

    controller_propagator_ = {'set header bicommissural'   : True,
                              'rig alignment'              : True,
                              'Propagate aff to segm'      : True,
                              'Propagate aff to mask'      : True,
                              'Smooth'                     : True,
                              'save result'                : True}

    controller_inter_modality_propagator_ = {'compensate squeezing'     : True,
                                             'rig register to S0'       : True,
                                             'rig propagate to S0'      : True,
                                             'rig register to MSME_up'  : True,
                                             'rig propagate to MSME_up' : True,
                                             'MSME_up to MSME'          : True}

    pfo_templ_subjects_input = jph(root_pilot_study_dropbox, 'A_internal_template')
    list_templ_subjects_input = templ_subjects

    rpa = RunParameters()

    # rpa.execute_PTB_ex_skull = True
    # rpa.execute_PTB_ex_vivo = True
    # rpa.execute_PTB_in_vivo = True
    # rpa.execute_PTB_op_skull = True
    # rpa.execute_ACS_ex_vivo = True

    # rpa.subjects = ['0802t1']
    # rpa.update_params()
    # rpa.subjects = ['1203', '1305', '1404', '1505', '1507', '1510', '1702', '1805', '2002', '2502', '2503',
    #                 '2608', '2702']
    rpa.subjects = ['2503', ] # '2608', '2702']


    # ['0904t1', '1501t1', '1504t1', '1508t1', '1509t1', '1511t1' ]
                    #  '0904t1', '1501t1', '1504t1', '1508t1', '1509t1', '1511t1', '2502bt1', '2503t1',
                    #'2605t1', '2702t1']  # '0802t1',
    rpa.update_params()

    execute_propag_and_fuse_all(controller_fuser_,
                                   controller_propagator_,
                                   controller_inter_modality_propagator_,
                                   pfo_templ_subjects_input,
                                   list_templ_subjects_input,
                                   rpa)
