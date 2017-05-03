"""
Analysis are preformed in bicommissural orientation, but for a better registration of the
latest segmentation,
"""
import numpy as np
import os
from os.path import join as jph

from definitions import root_pilot_study_dropbox
from tools.auxiliary.utils import print_and_run, adjust_header_from_transformations

"""
After importing the data in proper structure and having them with header properly oriented,
still need to squeeze, to orient according to MNI and to clean q-form and s-form.
"""

# controller
control = {'safety on'                        : True,
           'create interm folder'             : True,
           'header bicommissural'             : False,  # create the image with bicomm header
           'get roi segmentation'             : True,
           'propagate to oversampled'         : False,
           'undersample the propagated '      : False}

# main paths
root_pilot_study_msme_ex_vivo = jph(root_pilot_study_dropbox, 'A_msme_t2_analysis', 'ex_vivo')
pfo_utils = jph(root_pilot_study_dropbox, 'A_msme_t2_analysis', 'ex_vivo', 'Utils')
pfo_masks = jph(pfo_utils, 'masks')

pfi_msme_1201_ups = jph(root_pilot_study_msme_ex_vivo, '1201', 'mod', '1201_MSME_ups_layer1.nii.gz')
pfi_reg_mask_1201_standard  = jph(pfo_masks, '1201_registration_mask.nii.gz')
pfi_reg_mask_1201_upsampled = jph(pfo_masks, '1201_registration_mask_ups.nii.gz')

pfi_msme_2502_ups = jph(root_pilot_study_msme_ex_vivo, '2502', 'mod', '2502_MSME_ups_layer1.nii.gz')
pfi_reg_mask_2502_standard  = jph(pfo_masks, '2502_registration_mask.nii.gz')
pfi_reg_mask_2502_upsampled = jph(pfo_masks, '2502_registration_mask_ups.nii.gz')

for p in [root_pilot_study_msme_ex_vivo, pfo_utils, pfo_masks, pfi_reg_mask_1201_standard, pfi_reg_mask_1201_upsampled,
          pfi_reg_mask_2502_standard, pfi_reg_mask_2502_upsampled, pfi_msme_1201_ups, pfi_msme_2502_ups]:
    if not os.path.exists(p):
        raise IOError('Path {} not defined'.format(p))

# subjects
list_subjects = np.sort(list(set(os.listdir(root_pilot_study_msme_ex_vivo)) - {'.DS_Store', 'Utils'}))
print(list_subjects)


for sj in list_subjects:

    ''' Input - ONLY FIRST LAYERS ARE CONSIDERED: '''

    # target MSME
    pfi_sj_standard = jph(root_pilot_study_msme_ex_vivo, sj, 'mod', sj + '_MSME.nii.gz')
    pfi_sj_oversampled = jph(root_pilot_study_msme_ex_vivo, sj, 'mod', sj + '_MSME_ups.nii.gz')
    pfi_T1_sj = ''

    # manually adjusted segmentations
    pfo_source = jph(root_pilot_study_dropbox, sj)
    if os.path.exists(jph(pfo_source, 'segm', 'approved', sj + '_propagate_me_3.nii.gz')):
        pfi_segm_sj = jph(pfo_source, 'segm', 'approved', sj + '_propagate_me_3.nii.gz')
    elif os.path.exists(jph(pfo_source, 'segm', 'approved', sj + '_propagate_me_2.nii.gz')):
        pfi_segm_sj = jph(pfo_source, 'segm', 'approved', sj + '_propagate_me_2.nii.gz')
    else:
        pfi_segm_sj = jph(pfo_source, 'segm', 'approved', sj + '_propagate_me_1.nii.gz')

    for p in [pfi_sj_standard, pfi_sj_oversampled, pfi_segm_sj, pfi_T1_sj]:
        if not os.path.exists(p):
            raise IOError('Path {} not defined'.format(p))

    ''' Intermediate data '''

    pfo_intermediate_folder   = jph(root_pilot_study_msme_ex_vivo, sj, 'segm', 'z_interm_data')
    pfi_T1_sj_bicomm_header   = ''
    pfi_segm_sj_bicomm_header = ''
    pfi_reg_mask_ups_sj = jph(pfo_source, 'segm', sj + '_roi_reg_mask_ups.nii.gz')

    ''' Output '''

    pfi_propagated_segmentation_std = jph(root_pilot_study_msme_ex_vivo, sj, 'segm', sj + '_segm.nii.gz')
    pfi_propagated_segmentation_ups = jph(root_pilot_study_msme_ex_vivo, sj, 'segm', sj + '_segm_ups.nii.gz')

    ''' PIPELINE '''

    if control['create interm folder']:
        cmd = 'mkdir -p {}'.format(pfo_intermediate_folder)
        print_and_run(cmd, safety_on=control['safety on'])

    if control['set header bicommissural']:

        cmd0 = 'cp {0} {1}'.format(pfi_T1_sj, pfi_T1_sj_bicomm_header)
        cmd1 = 'cp {0} {1}'.format(pfi_segm_sj, pfi_segm_sj_bicomm_header)
        print_and_run(cmd0, safety_on=control['safety_on'])
        print_and_run(cmd1, safety_on=control['safety_on'])

        if sj not in ['1805', '2002', '2502']:  # change orientations of all the others

            theta = np.pi / float(3)
            if not control['safety_on']:
                adjust_header_from_transformations(pfi_T1_sj_bicomm_header, pfi_T1_sj_bicomm_header,
                                                   theta=theta, trasl=(0, 0, 0))
                adjust_header_from_transformations(pfi_segm_sj_bicomm_header, pfi_segm_sj_bicomm_header,
                                                   theta=theta, trasl=(0, 0, 0))

    if control['get roi segmentation']:

        if sj == '1201':
            cmd = 'cp {0} {1}'.format(pfi_reg_mask_1201_upsampled, pfi_reg_mask_ups_sj)
            print_and_run(cmd, safety_on=control['safety on'])
        elif sj == '2502':
            cmd = 'cp {0} {1}'.format(pfi_reg_mask_2502_upsampled, pfi_reg_mask_ups_sj)
            print_and_run(cmd, safety_on=control['safety on'])
        else:
            cmd0 = 'reg_aladin -ref {} -flo '
