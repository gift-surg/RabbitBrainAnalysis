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
from tools.definitions import root_study_rabbits, pfo_subjects_parameters, pfi_labels_descriptor, root_atlas, \
    root_atlas_W8

import nilabels as nis
from nilabels.tools.caliber.distances import global_dice_score


def open_subject(sj, coordinates, check_dice_if_in_atlas=True):

    print('Quality control subject {}, coordinates {}'.format(sj, coordinates))

    sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

    study = sj_parameters['study']
    category = sj_parameters['category']

    in_atlas = sj_parameters['in_atlas']

    segm_suffix = sj_parameters['names_architecture']['suffix_segm']

    if study == 'W8':
        pfo_atlas = root_atlas_W8
        options   = {'Template_chart_path' : jph(root_atlas_W8, '12503'),
                     'Template_name'       : '12503'}
    elif study == 'ACS' or study == 'PTB' or study == 'TestStudy':
        pfo_atlas = root_atlas
        options   = {'Template_chart_path' : jph(root_atlas, '1305'),
                     'Template_name'       : '1305'}
    else:
        raise IOError('Study for subject {} not feasible.'.format(sj))

    root_subject = jph(root_study_rabbits, 'A_data', study, category, sj)

    if coordinates == 'original':

        pfo_sj_mod = jph(root_subject, 'mod')
        pfo_sj_segm = jph(root_subject, 'segm')

        if not os.path.exists(pfo_sj_mod):
            print('\n\n Not existing {}!!'.format(pfo_sj_mod))
        if not os.path.exists(pfo_sj_segm):
            print('\n\n Not existing {}!!'.format(pfo_sj_mod))

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

        if not os.path.exists(pfo_sj_mod):
            print('\n\n Not existing {}!!'.format(pfo_sj_mod))
        if not os.path.exists(pfo_sj_segm):
            print('\n\n Not existing {}!!'.format(pfo_sj_mod))

        print pfo_sj_mod
        print pfo_sj_segm

        pfi_segm = jph(pfo_sj_segm, '{}_segm.nii.gz'.format(sj))
        if not os.path.exists(pfi_segm):
            pfi_segm = jph(pfo_sj_segm, 'automatic', '{}_{}.nii.gz'.format(sj, segm_suffix))

        cmd = 'itksnap -g {} -o '.format(jph(pfo_sj_mod, '{}_T1.nii.gz'.format(sj)))
        for m in ['FA', 'MD', 'V1', 'S0']:
            cmd += ' {} '.format(jph(pfo_sj_mod, '{}_{}.nii.gz'.format(sj, m)))
        cmd += ' -s {} '.format(pfi_segm)
        cmd += ' -l {}'.format(pfi_labels_descriptor)
        os.system(cmd)

        if in_atlas and check_dice_if_in_atlas:

            pfi_segm_strx = jph(root_subject, 'stereotaxic', 'segm', '{}_segm.nii.gz'.format(sj))
            pfi_segm_from_atlas = jph(pfo_atlas, sj, 'segm', '{}_segm.nii.gz'.format(sj))

            if not os.path.exists(pfi_segm_strx):
                print('\n\n Not existing {}!!'.format(pfi_segm_strx))
            if not os.path.exists(pfi_segm_from_atlas):
                print('\n\n Not existing {}!!'.format(pfi_segm_from_atlas))

            nis_app = nis.App()
            glob_dc = nis_app.measure.global_dist(pfi_segm_strx, pfi_segm_from_atlas, global_metrics=(global_dice_score, ))

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
    lsm.execute_W8_all_trials = True
    #
    # lsm.input_subjects = ['14603', ]
    #
    lsm.update_ls()

    coordinates_ = 'stereotaxic'
    print('Quality control for subjects \n{}'.format(lsm.ls))

    # open_from_list_subject(lsm.ls, coordinates_)
