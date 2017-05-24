import os
from os.path import join as jph

from tools.measurements.compile_record import compile_record
from definitions import root_study_dropbox, root_docs_dropbox


def compile_record_internal_template():

    assert os.path.isdir(root_study_dropbox), 'Connect to dropbox!'

    # folders and data from the architecture:
    pfo_internal_template         = jph(root_study_dropbox, 'A_internal_template')
    pfo_internal_template_reports = jph(root_study_dropbox, 'C_records')
    pfi_labels_descriptor         = jph(pfo_internal_template, 'LabelsDescriptors', 'multi_labels_descriptor.txt')
    pfi_excel_table               = jph(root_docs_dropbox, 'REoP_Pilot_MRI_Data.xlsx')

    for p in [pfo_internal_template, pfo_internal_template_reports, pfi_labels_descriptor, pfi_excel_table]:
        if not os.path.exists(p):
            msg = 'Folder {} of the structure does not exists'.format(p)
            raise IOError(msg)

    subjects = os.listdir(pfo_internal_template)
    subjects = [k for k in subjects if k.isdigit()]

    for sj in subjects:

        pfo_subject = jph(pfo_internal_template, sj)
        pfo_output_records = jph(root_study_dropbox, 'C_records', 'internal_template', sj)

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

        print '\n\n DATA PARSING SUBJECT {} \n\n'.format(sj)

        # Compile records
        compile_record(pfi_T1=pfi_T1,
                       pfi_FA=pfi_FA,
                       pfi_ADC=pfi_ADC,
                       pfi_multi_lab_descriptor=pfi_labels_descriptor,
                       pfi_segm_T1=pfi_atlas_sj,
                       pfi_segm_FA=pfi_atlas_sj,
                       pfi_segm_ADC=pfi_atlas_sj,
                       pfi_excel_table=pfi_excel_table,
                       subject_name=sj,
                       pfo_output=pfo_output_records,
                       save_human_readable=True,
                       create_output_folder_if_not_present=True
                       )

if __name__ == '__main__':
    print('Compile record')

    # compile_record_internal_template()
