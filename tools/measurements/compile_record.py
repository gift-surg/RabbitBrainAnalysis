"""
Measurements on labels.
"""
import numpy as np
import os
import nibabel as nib
from tabulate import tabulate
import codecs
import csv
from os.path import join as jph
from labels_manager.caliber.segmentation_analyzer import SegmentationAnalyzer

from parse_excel_tables_and_descriptors import parse_excel_data_to_list, parse_multi_label_descriptor_in_a_list


def compile_record(pfi_T1,
                   pfi_FA,
                   pfi_ADC,
                   pfi_multi_lab_descriptor,
                   pfi_segmentation,
                   pfi_excel_table,
                   subject_name,
                   pfo_output,
                   save_human_readable=True,
                   create_output_folder_if_not_present=True):

    # Sanity check input
    for p in [pfi_segmentation, pfi_multi_lab_descriptor, pfi_T1, pfi_FA, pfi_ADC, pfi_excel_table]:
        if not os.path.exists(p):
            raise IOError('input file {} does not exists'.format(p))

    # Create output folder or check if exists:
    if not os.path.exists(pfo_output):
        if create_output_folder_if_not_present:
            os.system('mkdir -p {}'.format(pfo_output))
        else:
            raise IOError('input file {} does not exists'.format(pfo_output))

    # Get label descriptor data:
    multi_lab_descriptor_list = parse_multi_label_descriptor_in_a_list(pfi_multi_lab_descriptor)
    labels_list = [k[0] for k in multi_lab_descriptor_list]
    values_list = []
    for k in multi_lab_descriptor_list:
        if len(k[1:]) > 1:
            values_list.append([k[1:]])
        else:
            values_list.append(k[1:])

    print multi_lab_descriptor_list
    print labels_list
    print values_list

    # debugging from here!
    return

    ''' Collect data using an instance of Caliber: '''

    # T1 - volume (more accurate the segmentation on the T1 to avoid partial voluming):
    sa = SegmentationAnalyzer(pfi_segmentation=pfi_segmentation,
                              pfi_scalar_im=pfi_T1,
                              icv_factor=None,
                              return_mm3=True)
    vols, voxels, z1, z2 = sa.get_volumes_per_label(labels_list)

    # FA:
    sa = SegmentationAnalyzer(pfi_segmentation=pfi_segmentation,
                              pfi_scalar_im=pfi_FA,
                              icv_factor=None,
                              return_mm3=True)
    FAs = sa.get_average_below_labels(labels_list)

    # ADC:
    sa = SegmentationAnalyzer(pfi_segmentation=pfi_segmentation,
                              pfi_scalar_im=pfi_ADC,
                              icv_factor=None,
                              return_mm3=True)
    ADCs = sa.get_average_below_labels(labels_list)

    ''' Create rabbit record '''

    # Get subjects id from excel spreadsheet:
    excel_tab_list = parse_excel_data_to_list(pfi_excel_table)
    subjects_id_from_excel = [k[0] for k in excel_tab_list[1:]]

    # Generate output folder
    if subject_name in subjects_id_from_excel:
        row_subject_index = subjects_id_from_excel.index(subject_name) + 1
    else:
        msg = 'subject {0} not present in the excel table saved in {1}'.format(subject_name, pfi_excel_table)
        raise IOError(msg)

    # Get preamble data for record:
    subject_info = {}
    for key, value in zip(excel_tab_list[0], excel_tab_list[row_subject_index]):
        subject_info.update({key: value})

    regions = [k[1] for k in lab_descriptor_list]

    # Compile record:
    record = {'Info'      : subject_info,
              'Regions'   : regions,
              'LabelsID'  : labels_list,
              'NumVoxels' : voxels,
              'vols'      : vols,
              'FAs'       : FAs,
              'ADCs'      : ADCs}

    # -- save python dictionary
    np.save(jph(pfo_output, subject_name + '_record.npy') , record)

    # -- save record in csv
    preamble_data = [['ID Number',              subject_info['ID Number']],
                     ['Sex',                    subject_info['Sex']],
                     ['Delivery Gestation (d)', subject_info['Delivery Gestation (d)']],
                     ['Harvest Date',           subject_info['Harvest Date'].strftime('%Y-%m-%d')],
                     ['MRI Date',               subject_info['MRI Date'].strftime('%Y-%m-%d')],
                     ['Weight PND1 (g)',        subject_info['Weight PND1 (g)']],
                     ['Brain Weight (g)',       subject_info['Brain Weight (g)']],
                     ['Acquisition',            subject_info['Acquisition']]
                     ]

    record_tab = []
    for reg, lab, vox, vol, fa, adc in zip(regions, labels_list, voxels, vols, FAs, ADCs):
        record_tab.append([reg, lab, vox, vol, fa, adc])
    headers = ['region', 'label number', 'number of voxels', 'vol (mm)', 'FA', 'ADC']
    table = tabulate(record_tab, headers=headers)

    fi = open(jph(pfo_output, subject_name + '_record.csv'), 'w+')
    writer = csv.writer(fi, delimiter=',')
    writer.writerows(preamble_data + [''] + [headers] + record_tab)
    fi.close()

    # -- save record in a txt tabulate file
    if save_human_readable:

        # generate preamble data
        fi = codecs.open(jph(pfo_output, subject_name + '_record.txt'), 'w+', 'utf-8')
        fi.write('ID Number               : {}\n'.format(subject_info['ID Number']))
        fi.write('Sex                     : {}\n'.format(subject_info['Sex']))
        fi.write('Delivery Gestation (d)  : {}\n'.format(subject_info['Delivery Gestation (d)']))
        fi.write('Harvest Date            : {}\n'.format(subject_info['Harvest Date'].strftime('%Y-%m-%d')))
        fi.write('MRI Date                : {}\n'.format(subject_info['MRI Date'].strftime('%Y-%m-%d')))
        fi.write('Weight PND1 (g)         : {}\n'.format(subject_info['Weight PND1 (g)']))
        fi.write('Brain Weight (g)        : {}\n'.format(subject_info['Brain Weight (g)']))
        fi.write('Acquisition             : {}\n'.format(subject_info['Acquisition']))

        # append empty lines
        fi.write('\n\n')

        # append table region | label number | vol | FA | ADC
        fi.write(table)
        fi.close()

    # -- save record in csv

    return record


# -- TEST HERE:

# from os.path import join as jph

# pfo_subjet = '/Users/sebastiano/Desktop/test/1305_test'
# pfo_output = '/Users/sebastiano/Desktop/test/1305_report'
# sj = '1305'
#
#
# assert os.path.exists(pfo_subject)
#

pfo_subject = '/Users/sebastiano/Desktop/test_main/A_internal_template/1201'
pfo_output = '/Users/sebastiano/Desktop/test/1201_report'
sj = '1201'

compile_record(pfi_T1=jph(pfo_subject, 'all_modalities', sj  + '_T1.nii.gz'),
                   pfi_FA=jph(pfo_subject, 'all_modalities', sj  + '_FA.nii.gz'),
                   pfi_ADC=jph(pfo_subject, 'all_modalities', sj  + '_MD.nii.gz'),
                   pfi_multi_lab_descriptor=jph(pfo_subject, 'labels_descriptor_v8_beta.txt'),
                   pfi_segmentation=jph(pfo_subject, 'segm', 'approved', '1305_propagate_me_2.nii.gz'),
                   pfi_excel_table=jph(pfo_subject, 'REoP_Pilot_MRI_Data.xlsx'),
                   subject_name=sj,
                   pfo_output=pfo_output)


