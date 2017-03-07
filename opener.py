import os
from os.path import join as jph
from definitions import root_pilot_study

root_dir = os.path.abspath(os.path.dirname(__file__))


def open_in_vivo():

    pfo_root_main = jph(root_pilot_study, 'A_template_atlas_in_vivo')
    subjects = ['0802_t1', '0904_t1', '1501_T1', '1504_T1', '1508_t1', '1509_T1', '1511_t1']

    pri_first_image = jph(pfo_root_main, subjects[0], 'all_modalities', subjects[0] + '_T1.nii.gz')

    pfi_final_result_all = ''

    for sj in subjects[1:]:
        pri_final_result = jph(pfo_root_main, sj, 'all_modalities', sj + '_T1.nii.gz')
        pfi_final_result_all += ' ' + pri_final_result + ' '

    cmd = 'itksnap -g {0} -o {1}'.format(pri_first_image, pfi_final_result_all)
    os.system(cmd)


def open_in_vivo_subjects_masked():

    pfo_root_main = jph(root_pilot_study, 'A_template_atlas_in_vivo')
    subjects = ['0802_t1', '0904_t1', '1501_t1', '1504_t1', '1508_t1', '1509_t1', '1511_t1']
    suffix_results_to_open = ['FA', 'MD', 'V1', 'S0']
    suffix_image = '_no_skull'

    for sj in subjects:

        pfi_first_image = jph(pfo_root_main, sj, 'all_modalities_no_skull', sj + '_T1' + suffix_image + '.nii.gz')

        pfi_list_mod_per_sj = ''

        for mod in suffix_results_to_open:
            pfi_modality_per_subject = jph(pfo_root_main, sj, 'all_modalities_no_skull', sj + '_' + mod + suffix_image + '.nii.gz')
            pfi_list_mod_per_sj += ' ' + pfi_modality_per_subject + ' '

        pfi_seg = jph(pfo_root_main, sj, 'segmentations', 'automatic',
                      'prelim_' + sj + '_template_smol_t3_reg_mask.nii.gz')

        cmd = 'itksnap -g {0} -o {1} -s {2}'.format(pfi_first_image, pfi_list_mod_per_sj, pfi_seg)
        print
        print cmd
        print
        os.system(cmd)


def open_in_vivo_subjects():

    pfo_root_main = jph(root_pilot_study, 'A_template_atlas_in_vivo')
    subjects = ['0802_t1', '0904_t1', '1501_t1', '1504_t1', '1508_t1', '1509_t1', '1511_t1']
    suffix_results_to_keep = ['FA', 'MD', 'V1', 'S0']

    for sj in subjects:

        pfi_first_image = jph(pfo_root_main, sj, 'all_modalities', sj + '_T1.nii.gz')

        pfi_list_mod_per_sj = ''

        for mod in suffix_results_to_keep:
            pfi_modality_per_subject = jph(pfo_root_main, sj, 'all_modalities', sj + '_' + mod + '.nii.gz')
            pfi_list_mod_per_sj += ' ' + pfi_modality_per_subject + ' '

        pfi_seg = jph(pfo_root_main, sj, 'segmentations', 'automatic',
                      'prelim_' + sj + '_template_smol_t3_reg_mask.nii.gz')

        cmd = 'itksnap -g {0} -o {1} -s {2}'.format(pfi_first_image, pfi_list_mod_per_sj, pfi_seg)
        os.system(cmd)


def open_in_vivo_MSME_T2_bicommissural():

    pfo_root_main = jph(root_pilot_study, 'B_pilot_analysis_in_vivo')
    subjects = ['0802_t1', '0904_t1', '1501_t1', '1504_t1', '1508_t1', '1509_t1', '1511_t1']

    pri_first_image = jph(pfo_root_main, subjects[0], 'all_modalities', subjects[0] + '_MSME_T2.nii.gz')

    pfi_final_result_all = ''

    for sj in subjects[1:]:
        pri_final_result = jph(pfo_root_main, sj, 'all_modalities', sj + '_MSME_T2.nii.gz')
        pfi_final_result_all += ' ' + pri_final_result + ' '

    cmd = 'itksnap -g {0} -o {1}'.format(pri_first_image, pfi_final_result_all)
    os.system(cmd)


def open_in_vivo_MSME_T2_bicommissural_separate_with_segmentation():

    pfo_root_main = jph(root_pilot_study, 'B_pilot_analysis_in_vivo')
    subjects = ['0802_t1', '0904_t1', '1501_t1', '1504_t1', '1508_t1', '1509_t1', '1511_t1']

    for sj in subjects:

        pfi_anatomical = jph(pfo_root_main, sj, 'all_modalities', sj + '_MSME_T2.nii.gz')
        pfi_segmentation = jph(pfo_root_main, sj, 'segmentations', 'automatic', sj + '_segmentation_roi_test3.nii.gz')

        cmd = 'itksnap -g {0} -s {1}'.format(pfi_anatomical, pfi_segmentation)
        os.system(cmd)