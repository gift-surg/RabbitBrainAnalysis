"""
Module to share data on the dropbox folder with Hannes.
Here is the
"""
import os
from os.path import join as jph
import pickle

from LABelsToolkit.tools.aux_methods.utils import print_and_run

from main_pipeline.A0_main.main_controller import ListSubjectsManager
from tools.definitions import root_study_rabbits, pfo_subjects_parameters


def share_subject(sj, pfo_folder_destination, share):
    """
    NOTE: If something is found in the folder destination will be deleted!!
    :param sj: subject id
    :param pfo_folder_destination: where to share
    :param share: what to share
    :return:
    """
    sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

    study = sj_parameters['study']
    category = sj_parameters['category']

    root_subject = jph(root_study_rabbits, 'A_data', study, category, sj)

    if not os.path.exists(root_subject):
        print('Sj {}. Data folder {} does not exist.'.format(sj, root_subject))
        return

    pfo_dest_sj = jph(pfo_folder_destination, sj)

    if os.path.exists(pfo_dest_sj):
        if share['force']:
            os.system('rm -r {}'.format(pfo_dest_sj))
        else:
            print('Sj {} already exists, not to be overwritten.'.format(sj))
            return

    os.system('mkdir {}'.format(pfo_dest_sj))

    if share['folders'] == 'only_reports' :
        print('Sj {} sharing only reports. '.format(sj))
        msg = ''
        pfo_report     = jph(root_subject, 'report')
        pfo_report_stx = jph(root_subject, 'stereotaxic', 'report')

        if not os.path.exists(pfo_report):
            msg += '- Sj {} does not have a report folder\n'.format(sj)
        else:
            pfo_report_destination = jph(pfo_dest_sj, 'report')
            print_and_run('cp -r {} {}'.format(pfo_report, pfo_report_destination), short_path_output=False)

        if share['stereotaxic']:

            if not os.path.exists(pfo_report_stx):
                msg += 'Subject {} does not have a stereotaxic/report folder\n'.format(sj)
            else:
                pfo_report_stx_destination = jph(pfo_dest_sj, 'report_stx')
                print_and_run('cp -r {} {}'.format(pfo_report_stx, pfo_report_stx_destination), short_path_output=False)

        if msg != '':
            print('\n')
            print(msg)

    else:
        print('Sj {} sharing all data. '.format(sj))
        for f in share['folders']:
            pfo_mod_original = jph(root_subject, f)
            print_and_run('cp -r {} {}'.format(pfo_mod_original, pfo_dest_sj), short_path_output=False)

        if share['stereotaxic']:
            pfo_dest_sj_stx = jph(pfo_dest_sj, 'stereotaxic')
            print_and_run('mkdir {}'.format(pfo_dest_sj_stx))

            for f in share['folders']:
                pfo_mod_original_stx = jph(root_subject, 'stereotaxic', f)
                print_and_run('cp -r {} {}'.format(pfo_mod_original_stx, pfo_dest_sj_stx), short_path_output=False)


def share_from_subject_list(sj_list, pfo_folder_destination, share):

    print('Share data of subjects {} with Hannes. \n'.format(sj_list))
    for sj in sj_list:
        share_subject(sj, pfo_folder_destination=pfo_folder_destination, share=share)


if __name__ == '__main__':
    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull = False
    lsm.execute_PTB_ex_vivo  = False
    lsm.execute_PTB_in_vivo  = False
    lsm.execute_PTB_op_skull = False
    lsm.execute_ACS_ex_vivo  = False

    lsm.input_subjects = ['4504', '4501', '4305', '4304', '4302', '5003', '5007']

    lsm.update_ls()

    print lsm.ls

    stuff_to_share = {'stereotaxic' : True,
                      'folders': 'only_reports',  # can be 'only_reports' or list of folders as ['mod', 'segm', 'report']
                      'force' : True
                      }

    destination_folder = '/Users/sebastiano/Dropbox/RabbitEOP-MRI/study/PTBExVivo'
    assert os.path.exists(destination_folder)

    share_from_subject_list(lsm.ls, destination_folder, stuff_to_share)
