import numpy as np
import nibabel as nib
import os
from os.path import join as jph


from definitions import root_pilot_study
from tools.auxiliary.utils import print_and_run

from tools.auxiliary.utils import set_new_data
from tools.correctors.MSME_T2_correctors import corrector_MSME_T2_path
from tools.correctors.coordinates_header_coorectors import adjust_header_from_transformations


# paths:
pfo_in_vivo_analysis = jph(root_pilot_study, 'B_pilot_analysis_in_vivo')


subjects = ['0802_t1', '0904_t1', '1501_t1', '1504_t1', '1508_t1', '1509_t1', '1511_t1']
# subjects = ['0904_t1', '1501_t1', '1504_t1', '1508_t1', '1509_t1', '1511_t1']
# subjects = ['1508_t1', '1509_t1']


control = {'Create folder all modalities'      : True,
           'Correct orienatation and slicing'  : True,
           'Create folder segmentation'        : True,
           'Propagate segmentation'            : True,
           'Safety on'                         : False}

reorientation_map = {'0802_t1' : 'x z -y',
                     '0904_t1' : 'x z -y',  # A-P swapped
                     '1501_t1' : 'x z -y',
                     '1504_t1' : 'x z -y',
                     '1508_t1' : 'x z -y',  # A-P swapped
                     '1509_t1' : 'x z -y',
                     '1511_t1' : 'x z -y'}

initial_rotation_map = {'0802_t1' : [np.pi / float(5), (0, 15, 7)],
                        '0904_t1' : [np.pi / float(5), (0, 15, 7)],
                        '1501_t1' : [np.pi / float(5), (0, 15, 7)],
                        '1504_t1' : [np.pi / float(5), (0, 15, 7)],
                        '1508_t1' : [np.pi / float(4), (0, 15, 7)],  #
                        '1509_t1' : [np.pi / float(5), (0, 15, 7)],
                        '1511_t1' : [np.pi / float(4), (0, 15, 7)]}  #

test_num = 'test3'

for sj in subjects:

    if control['Create folder all modalities']:

        cmd0 = 'mkdir -p {}'.format(jph(pfo_in_vivo_analysis, sj))
        cmd1 = 'mkdir -p {}'.format(jph(pfo_in_vivo_analysis, sj, 'all_modalities'))

        print_and_run(cmd0, safety_on=control['Safety on'])
        print_and_run(cmd1, safety_on=control['Safety on'])

    if control['Correct orienatation and slicing']:

        pfi_original_MSME_T2 = jph(root_pilot_study, '0_original_data', 'in_vivo', sj, 'T2_map', sj + '_MSME_T2.nii.gz')
        pfi_orientation_and_slicing_corrected_MSME_T2 = jph(pfo_in_vivo_analysis, sj, 'all_modalities', sj + '_MSME_T2.nii.gz')

        corrector_MSME_T2_path(pfi_original_MSME_T2, pfi_orientation_and_slicing_corrected_MSME_T2, swap_dim=reorientation_map[sj])

    if control['Create folder segmentation']:

        cmd0 = 'mkdir -p {}'.format(jph(pfo_in_vivo_analysis, sj, 'segmentations'))
        cmd1 = 'mkdir -p {}'.format(jph(pfo_in_vivo_analysis, sj, 'segmentations', 'automatic'))

        print_and_run(cmd0, safety_on=control['Safety on'])
        print_and_run(cmd1, safety_on=control['Safety on'])

    if control['Propagate segmentation']:

        # anatomy + segmentation in histological oriented and propagated in bicommissural with the first slice of
        # the MSME_T2.

        # input
        pfi_anatomy_to_propagate = jph(root_pilot_study, 'A_template_atlas_in_vivo', sj, 'all_modalities', sj + '_T1.nii.gz')
        pfi_segmentation_to_propagate = jph(root_pilot_study, 'A_template_atlas_in_vivo', sj, 'segmentations', 'automatic', 'prelim_' +  sj + '_template_smol_t3_reg_mask.nii.gz')
        pfi_sj_image_MSME_T2 = jph(pfo_in_vivo_analysis, sj, 'all_modalities', sj + '_MSME_T2.nii.gz')

        # intermediate
        pfo_intermediate_steps_MSME_T2 = jph(pfo_in_vivo_analysis, sj, 'segmentations', 'automatic', 'z_propagate_MSME_T2')
        pfi_MSME_T2_image_first_slice = jph(pfo_intermediate_steps_MSME_T2, sj + '_first_slice.nii.gz')
        pfi_anatomy_to_propagate_reoriented = jph(pfo_intermediate_steps_MSME_T2, sj + '_T1_header_reoriented.nii.gz')
        pfi_segmentation_to_propagate_reoriented = jph(pfo_intermediate_steps_MSME_T2, sj + '_segmentation_header_reoriented.nii.gz')

        # output
        pfi_aff_transformation = jph(pfo_intermediate_steps_MSME_T2, sj + '_aff.txt')
        pfi_anatomy_propagated_on_MSME_T2 = jph(pfo_intermediate_steps_MSME_T2, sj + '_anatomy_on_MSME_T2.nii.gz')
        pfi_segmentation_propagated = jph(pfo_in_vivo_analysis, sj, 'segmentations', 'automatic', sj + '_segmentation_roi_' + test_num + '.nii.gz')

        # generate intermediate output folder
        print '\n Creation intermediate steps folder'

        cmd = 'mkdir -p {}'.format(pfo_intermediate_steps_MSME_T2)
        print_and_run(cmd, safety_on=control['Safety on'])

        print '\n Extraction first layer DWI: execution for subject {0}.\n'.format(sj)

        if not control['Safety on']:
            nib_dwi = nib.load(pfi_sj_image_MSME_T2)
            nib_dwi_first_slice_data = nib_dwi.get_data()[..., 0]
            nib_first_slice_dwi = set_new_data(nib_dwi, nib_dwi_first_slice_data)
            nib.save(nib_first_slice_dwi, pfi_MSME_T2_image_first_slice)

        print '\n Reorient initial anatomy and segmentation \n'

        if not control['Safety on']:
            adjust_header_from_transformations(pfi_anatomy_to_propagate, pfi_anatomy_to_propagate_reoriented,
                                               theta=initial_rotation_map[sj][0], trasl=initial_rotation_map[sj][1])
            adjust_header_from_transformations(pfi_segmentation_to_propagate, pfi_segmentation_to_propagate_reoriented,
                                               theta=initial_rotation_map[sj][0], trasl=initial_rotation_map[sj][1])

        print '\n Register and propagate \n'

        cmd0 = 'reg_aladin -ref {0} -flo {1} -aff {2} -res {3} -rigOnly'.format(pfi_MSME_T2_image_first_slice,
                                                                       pfi_anatomy_to_propagate_reoriented,
                                                                       pfi_aff_transformation,
                                                                       pfi_anatomy_propagated_on_MSME_T2)

        cmd1 = 'reg_resample -ref {0} -flo {1} -aff {2} -res {3} -inter 0'.format(pfi_MSME_T2_image_first_slice,
                                                                       pfi_segmentation_to_propagate_reoriented,
                                                                       pfi_aff_transformation,
                                                                       pfi_segmentation_propagated)

        print_and_run(cmd0, safety_on=control['Safety on'])
        print_and_run(cmd1, safety_on=control['Safety on'])

