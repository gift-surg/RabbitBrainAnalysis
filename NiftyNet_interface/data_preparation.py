import os
from os.path import join as jph
from collections import OrderedDict

from main_pipeline.A0_main.subject_parameters_manager import get_list_names_subjects_in_template
from tools.definitions import root_study_rabbits, pfo_subjects_parameters, root_internal_template
from tools.auxiliary.sanity_checks import check_libraries


"""
Initial step:
Mono modal registration.
The subjects are in the template space (histological).
The data analysis cannot be performed in the bicommissural for the moment.
"""


def prepare_data_subject_list(sj_list, controller):

    check_libraries()
    assert os.path.exists(root_study_rabbits)

    pfo_nifty_net_data = jph(root_study_rabbits, 'D_nifty_net')

    if controller['Update_data_folder']:

        if os.path.exists(pfo_nifty_net_data):
            os.system('rm -r {}'.format(pfo_nifty_net_data))
        os.system('mkdir {}'.format(pfo_nifty_net_data))

        if controller['Modality'] == 'Mono':
            for sj in sj_list:

                pfo_sj_original = jph(root_internal_template, sj)

                # cp T1
                pfi_original_T1 = jph(pfo_sj_original, 'mod', sj + '_T1.nii.gz')
                assert os.path.exists(pfi_original_T1), pfi_original_T1
                pfi_new = jph(pfo_nifty_net_data, 'T1_{}.nii.gz'.format(sj))
                os.system('cp {0} {1}'.format(pfi_original_T1, pfi_new))

                # cp atlas
                pfi_original_segm = jph(pfo_sj_original, 'segm',  sj + '_approved.nii.gz')
                assert os.path.exists(pfi_original_segm), pfi_original_segm
                pfi_new = jph(pfo_nifty_net_data, 'Atlas_{}.nii.gz'.format(sj))
                os.system('cp {0} {1}'.format(pfi_original_segm, pfi_new))

                # cp mask
                pfi_original_segm = jph(pfo_sj_original, 'masks', sj + '_roi_mask.nii.gz')
                assert os.path.exists(pfi_original_segm), pfi_original_segm
                pfi_new = jph(pfo_nifty_net_data, 'Mask_{}.nii.gz'.format(sj))
                os.system('cp {0} {1}'.format(pfi_original_segm, pfi_new))

        elif controller['Modality'] == 'Multi':
            print('See TODO list')
            return
        else:
            raise IOError

    if controller['Copy_data_folder_to_cluster']:
        pfo_in_cluster_data = '/cluster/project0/fetalsurgery/Data/MRI/KUL_preterm_rabbit_model/data/D_nifty_net'
        cmd = "rsync -rov --exclude '.DS_Store' {0} ferraris@comic100.cs.ucl.ac.uk:{1}".format(pfo_nifty_net_data,
                                                                                               pfo_in_cluster_data)
        os.system(cmd)


if __name__ == '__main__':
    print('process T1, local run. ')

    controller_ = OrderedDict({'Modality'                    : 'Mono',
                               'Update_data_folder'          : True,
                               'Copy_data_folder_to_cluster' : False})

    list_subjects_in_template = get_list_names_subjects_in_template(pfo_subjects_parameters)
    print list_subjects_in_template
    prepare_data_subject_list(list_subjects_in_template, controller_)
