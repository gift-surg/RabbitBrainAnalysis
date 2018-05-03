"""
Quality control opener.
"""
import os
from collections import OrderedDict
from os.path import join as jph
import pickle
import time
import subprocess

from main_pipeline.A0_main.main_controller import ListSubjectsManager
from tools.definitions import root_study_rabbits, pfo_subjects_parameters, pfi_labels_descriptor, root_atlas


from LABelsToolkit.main import LABelsToolkit as LaB
from LABelsToolkit.tools.caliber.distances import global_dice_score

segm_suffix = 'MV_P2'


def open_subject(sj, coordinates, check_dice_if_in_atlas=True):

    global segm_suffix

    print('Quality control subject {}, coordinates {}'.format(sj, coordinates))

    sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

    study = sj_parameters['study']
    category = sj_parameters['category']

    in_atlas = sj_parameters['in_atlas']

    root_subject = jph(root_study_rabbits, 'A_data', study, category, sj)

    if coordinates == 'original':

        pfo_sj_mod = jph(root_subject, 'mod')
        pfo_sj_segm = jph(root_subject, 'segm')

        assert os.path.exists(pfo_sj_mod), pfo_sj_mod
        assert os.path.exists(pfo_sj_segm), pfo_sj_segm

        # open T1 in one frame:
        cmd = 'itksnap -g {} -o '.format(jph(pfo_sj_mod, '{}_T1.nii.gz'.format(sj)))
        cmd += ' -s {} '.format(jph(pfo_sj_segm, '{}_T1_segm.nii.gz'.format(sj)))
        cmd += ' -l {}'.format(pfi_labels_descriptor)
        os.system(cmd)

        # open other modalities in the other frame:
        cmd = 'itksnap -g {} -o '.format(jph(pfo_sj_mod, '{}_S0.nii.gz'.format(sj)))
        for m in ['FA', 'MD', 'V1']:
            cmd += ' {} '.format(jph(pfo_sj_mod, '{}_{}.nii.gz'.format(sj, m)))
        cmd += ' -s {} '.format(jph(pfo_sj_segm, '{}_S0_segm.nii.gz'.format(sj)))
        cmd += ' -l {}'.format(pfi_labels_descriptor)
        os.system(cmd)

    elif coordinates == 'stereotaxic':

        pfo_sj_mod = jph(root_subject, 'stereotaxic', 'mod')
        pfo_sj_segm = jph(root_subject, 'stereotaxic', 'segm')

        assert os.path.exists(pfo_sj_mod), pfo_sj_mod
        assert os.path.exists(pfo_sj_segm), pfo_sj_segm

        print pfo_sj_mod
        print pfo_sj_segm

        pfi_segm = jph(pfo_sj_segm, '{}_segm.nii.gz'.format(sj))
        if not os.path.exists(pfi_segm):
            pfi_segm = jph(pfo_sj_segm, 'automatic', '{}_{}.nii.gz'.format(sj, segm_suffix))

        cmd = 'itksnap -g {} -o '.format(jph(pfo_sj_mod, '{}_T1.nii.gz'.format(sj)))
        for m in ['FA', 'MD', 'V1']:
            cmd += ' {} '.format(jph(pfo_sj_mod, '{}_{}.nii.gz'.format(sj, m)))
        cmd += ' -s {} '.format(pfi_segm)
        cmd += ' -l {}'.format(pfi_labels_descriptor)
        os.system(cmd)

    if in_atlas and check_dice_if_in_atlas:

        pfi_segm_strx = jph(root_subject, 'stereotaxic', 'segm', '{}_segm.nii.gz'.format(sj))
        pfi_segm_from_atlas = jph(root_atlas, sj, 'segm', '{}_segm.nii.gz'.format(sj))

        assert os.path.exists(pfi_segm_strx)
        assert os.path.exists(pfi_segm_from_atlas)

        lab = LaB()
        glob_dc = lab.measure.global_dist(pfi_segm_strx, pfi_segm_from_atlas, global_metrics=(global_dice_score, ))

        print('Subject {} in atlas, has a segmentation aligned with the ground truth. Dice as measure of overlap: ')
        print(glob_dc)
        if glob_dc[0] < 0.95:
            print('WARNING!!! Possible bugs!')
    else:
        raise IOError('Input variable - corrdinates - can be only original or stereotaxic. Had {}'.format(coordinates))


def open_from_list_subject(sj_list, coordinates, ask_for_next=True):

    report = OrderedDict()
    for sj in sj_list:
        open_subject(sj, coordinates=coordinates)
        if ask_for_next:
            time.sleep(5)
            note_for_subject = raw_input('Quality assessment: \n\n')
            if note_for_subject in report.keys():
                report[note_for_subject] += [sj]
            else:
                report.update({note_for_subject: [sj]})

    if ask_for_next:
        print('Notes: ')
        print(report)

    return report


if __name__ == '__main__':
    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull  = False
    lsm.execute_PTB_ex_vivo   = False
    lsm.execute_PTB_in_vivo   = False
    lsm.execute_PTB_op_skull  = False
    lsm.execute_ACS_ex_vivo   = False

    # lsm.input_subjects = ['12307', '12308', '12402', '12504', '12505', '12607', '12608', '12609',
    #                       '12610']  # ['13103', '13108', '13301', '13307', '13401', '13403', '13404']
    # lsm.input_subjects = ['13405', '13501', '13505', '13507', '13602', '13604', '13606']

    lsm.input_subjects = ['1201', '1203', '1305', '1404', '1507', '1510', '1702', '1805', '2002', '2502', '3301', '3404']

    lsm.update_ls()

    coordinates_ = 'stereotaxic'
    print('Quality control for subjects \n{}'.format(lsm.ls))

    open_from_list_subject(lsm.ls, coordinates_)
