"""

"""
import os
from os.path import join as jph
import pickle

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

    assert os.path.exists(root_subject)

    pfo_dest_sj = jph(pfo_folder_destination, sj)

    os.system('rm -r {}'.format(pfo_dest_sj))
    os.system('mkdir {}'.format(pfo_dest_sj))

    for f in share['folders']:
        pfo_mod_original = jph(root_subject, f)
        os.system('cp -r {} {}'.format(pfo_mod_original, pfo_dest_sj))

    if share['stereotaxic']:
        pfo_dest_sj_stx = jph(pfo_dest_sj, 'stereotaxic')
        os.system('mkdir {}'.format(pfo_dest_sj_stx))

        for f in share['folders']:
            pfo_mod_original_stx = jph(root_subject, 'stereotaxic', f)
            os.system('cp -r {} {}'.format(pfo_mod_original_stx, pfo_dest_sj_stx))


def share_from_subject_list(sj_list, pfo_folder_destination, share):

    for sj in sj_list:
        share_subject(sj, pfo_folder_destination=pfo_folder_destination, share=share)


if __name__ == '__main__':
    stuff_to_share = {'folders' : ['mod', 'segm', 'report'],
                      'stereotaxic' : True}

    destination_folder = '/Users/sebastiano/Dropbox/RabbitEOP-MRI/study/0_new_subjects'

    sj_to_share = ['12307', '12308', '12402', '12504', '12505', '12607', '12608', '12609', '12610']

    share_from_subject_list(sj_to_share, destination_folder, stuff_to_share)
