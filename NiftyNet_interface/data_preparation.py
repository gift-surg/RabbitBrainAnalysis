import os
from os.path import join as jph
import numpy as np
from collections import OrderedDict

from tools.definitions import root_study_rabbits, multi_atlas_subjects, root_atlas
from tools.auxiliary.sanity_checks import check_libraries


"""
Initial step:
Mono modal registration.
The subjects are in the template space (histological).
The data analysis cannot be performed in the bicommissural for the moment.
"""


def prepare_data_subject_list(sj_list, sj_left_out_list, controller):

    check_libraries()
    assert os.path.exists(root_study_rabbits)

    pfo_nifty_net_data = jph(root_study_rabbits, 'D_nifty_net')
    pfo_nifty_net_data_template = jph(pfo_nifty_net_data, 'template')
    pfo_nifty_net_data_target = jph(pfo_nifty_net_data, 'target')

    if controller['Update_data_folders']:

        if os.path.exists(pfo_nifty_net_data):
            os.system('rm -r {}'.format(pfo_nifty_net_data_template))
            os.system('rm -r {}'.format(pfo_nifty_net_data_target))
        os.system('mkdir {}'.format(pfo_nifty_net_data_template))
        os.system('mkdir {}'.format(pfo_nifty_net_data_target))

        # create template
        if controller['Modality'] == 'Mono':



            # create template folder
            for sj in sj_list:
                pfo_sj_original = jph(root_atlas, sj)

                # cp T1
                pfi_original_T1 = jph(pfo_sj_original, 'mod', sj + '_T1.nii.gz')
                assert os.path.exists(pfi_original_T1), pfi_original_T1
                pfi_new = jph(pfo_nifty_net_data_template, 'T1_{}.nii.gz'.format(sj))
                os.system('cp {0} {1}'.format(pfi_original_T1, pfi_new))

                # cp atlas
                pfi_original_segm = jph(pfo_sj_original, 'segm',  sj + '_approved.nii.gz')
                assert os.path.exists(pfi_original_segm), pfi_original_segm
                pfi_new = jph(pfo_nifty_net_data_template, 'Atlas_{}.nii.gz'.format(sj))
                os.system('cp {0} {1}'.format(pfi_original_segm, pfi_new))

                # cp mask
                pfi_original_segm = jph(pfo_sj_original, 'masks', sj + '_roi_mask.nii.gz')
                assert os.path.exists(pfi_original_segm), pfi_original_segm
                pfi_new = jph(pfo_nifty_net_data_template, 'Mask_{}.nii.gz'.format(sj))
                os.system('cp {0} {1}'.format(pfi_original_segm, pfi_new))

            # create template folder
            for sj in sj_left_out_list:
                pfo_sj_original = jph(root_atlas, sj)

                # cp T1
                pfi_original_T1 = jph(pfo_sj_original, 'mod', sj + '_T1.nii.gz')
                assert os.path.exists(pfi_original_T1), pfi_original_T1
                pfi_new = jph(pfo_nifty_net_data_target, 'T1_{}.nii.gz'.format(sj))
                os.system('cp {0} {1}'.format(pfi_original_T1, pfi_new))

        elif controller['Modality'] == 'Multi':
            print('See TODO list')
            return
        else:
            raise IOError


if __name__ == '__main__':
    print('process T1, local run. ')

    controller_ = OrderedDict({'Modality'                    : 'Mono',
                               'Update_data_folders'          : False})

    list_subjects_in_template = multi_atlas_subjects
    print list_subjects_in_template

    # cross validation
    left_out = ['1702']
    list_subjects_in_template = list(np.sort(set(list_subjects_in_template)  - set(left_out)))

    prepare_data_subject_list(list_subjects_in_template, left_out, controller_)
