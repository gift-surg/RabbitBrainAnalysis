"""
Propagate and fuse T1
"""

from os.path import join as jph

from definitions import root_study_rabbits
from pipeline_project.A0_main.main_controller import RunParameters
from propagate_and_fuse_utils import propagate_and_fuse_per_group_over_all_modalities


def execute_propag_and_fuse_all(controller_fuser,
                                controller_propagator,
                                controller_inter_modality_propagator,
                                pfo_templ_subjects,
                                list_templ_subjects,
                                rp):

    assert isinstance(rp, RunParameters)

    root_data = jph(root_study_rabbits, 'A_data')

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
    print('Propagate and fuse, local run. ')
