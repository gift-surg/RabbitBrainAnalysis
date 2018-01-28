import os
from os.path import join as jph

from tools.measurements.z_old_compile_record import compile_record
from tools.definitions import root_atlas, root_study_rabbits, pfi_excel_table_all_data
from labels_manager.tools.aux_methods.sanity_checks import check_path_validity
'''
Data here are directly collected from the manual segmentation that constitutes the internal template.
This file is not called in the main pipeline but it is important as way of computing the error of
the resampling.
'''


def compile_record_internal_template(bypass=None):

    # folders and data from the architecture:
    pfi_multi_labels_descr = jph(root_atlas, 'LabelsDescriptors', 'multi_labels_descriptor.txt')

    for p in [pfi_multi_labels_descr, pfi_excel_table_all_data]:
        if not check_path_validity(p):
            msg = 'Folder {} of the structure does not exists'.format(p)
            raise IOError(msg)

    if bypass is None:
        subjects = os.listdir(root_atlas)
        subjects = [k for k in subjects if k.isdigit()]
    else:
        subjects = bypass

    for sj in subjects:

        pfo_subject = jph(root_atlas, sj)
        pfo_output_records = jph(root_study_rabbits, 'A_data', 'PTB', 'ex_vivo', sj, 'records_template')

        # grab segmentation
        if os.path.exists(jph(pfo_subject, 'segm', 'approved', sj + '_propagate_me_3.nii.gz')):
            pfi_atlas_sj = jph(pfo_subject, 'segm', 'approved', sj + '_propagate_me_3.nii.gz')
        elif os.path.exists(jph(pfo_subject, 'segm', 'approved', sj + '_propagate_me_2.nii.gz')):
            pfi_atlas_sj = jph(pfo_subject, 'segm', 'approved', sj + '_propagate_me_2.nii.gz')
        else:
            pfi_atlas_sj = jph(pfo_subject, 'segm', 'approved', sj + '_propagate_me_1.nii.gz')

        pfi_T1 = jph(pfo_subject, 'all_modalities', sj + '_T1.nii.gz')
        pfi_FA = jph(pfo_subject, 'all_modalities', sj + '_FA.nii.gz')
        pfi_ADC = jph(pfo_subject, 'all_modalities', sj + '_MD.nii.gz')
        pfi_g_ratio = jph(pfo_subject, 'all_modalities', sj + '_g_ratio.nii.gz')

        print '\n\n DATA PARSING SUBJECT {} \n\n'.format(sj)

        # Compile records
        compile_record(pfi_T1=pfi_T1,
                       pfi_FA=pfi_FA,
                       pfi_ADC=pfi_ADC,
                       pfi_g_ratio=pfi_g_ratio,
                       pfi_multi_lab_descriptor=pfi_multi_labels_descr,
                       pfi_segm_T1=pfi_atlas_sj,
                       pfi_segm_FA=pfi_atlas_sj,
                       pfi_segm_ADC=pfi_atlas_sj,
                       pfi_segm_g_ratio=pfi_atlas_sj,
                       pfi_excel_table=pfi_excel_table_all_data,
                       subject_name=sj,
                       pfo_output=pfo_output_records,
                       save_human_readable=True,
                       create_output_folder_if_not_present=True,
                       verbose=1
                       )

if __name__ == '__main__':
    print('Compile record, local run')

    compile_record_internal_template(['2002', '2502'])
