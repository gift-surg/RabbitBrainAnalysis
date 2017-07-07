"""
Measurements on labels.
"""
import codecs
import csv
import datetime
import os
from os.path import join as jph

import numpy as np
from labels_manager.caliber.segmentation_analyzer import SegmentationAnalyzer
from tabulate import tabulate

from pipeline_project.A0_main.main_controller import subject
from tools.auxiliary.parse_excel_tables_and_descriptors import parse_excel_data_to_list, \
    parse_multi_label_descriptor_in_a_list

from tools.auxiliary.utils import print_and_run


def compile_record(pfi_T1,
                   pfi_FA,
                   pfi_ADC,
                   pfi_g_ratio,
                   pfi_multi_lab_descriptor,
                   pfi_segm_T1,
                   pfi_segm_FA,
                   pfi_segm_ADC,
                   pfi_segm_g_ratio,
                   pfi_excel_table,
                   subject_name,
                   pfo_output,
                   save_human_readable=True,
                   create_output_folder_if_not_present=True,
                   verbose=0):

    # Sanity check input
    for p in [pfi_multi_lab_descriptor, pfi_excel_table]:
        if not os.path.exists(p):
            raise IOError('input file {} does not exists'.format(p))

    # Create output folder or check if exists:
    if not os.path.exists(pfo_output):
        if create_output_folder_if_not_present:
            print_and_run('mkdir -p {}'.format(pfo_output))
        else:
            raise IOError('input file {} does not exists'.format(pfo_output))

    # Get label descriptor data:
    multi_lab_descriptor_list = parse_multi_label_descriptor_in_a_list(pfi_multi_lab_descriptor)

    values_list = []
    # strip:
    for k in multi_lab_descriptor_list:
        if len(k[1:]) > 1:
            values_list.append(k[1:])
        else:
            values_list.append(k[1:][0])

    ''' Collect rabbit data from excel files'''

    # Parse excel table
    group = subject[subject_name][0][0]
    excel_tab_list = parse_excel_data_to_list(pfi_excel_table, worksheet_name=group)
    # Get subjects ID Number from excel table
    pos_id_number = excel_tab_list[0].index('ID Number')
    subjects_id_from_excel = [k[pos_id_number].replace('.', '') for k in excel_tab_list[1:]]

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

    regions = [k[0] for k in multi_lab_descriptor_list]

    ''' Collect data using an instance of Caliber: '''

    # T1 - volume (more accurate the segmentation on the T1 to avoid partial voluming):
    if verbose > 0:
        print('T1 - volume')
    if os.path.exists(pfi_segm_T1) and os.path.exists(pfi_T1):
        sa = SegmentationAnalyzer(pfi_segmentation=pfi_segm_T1,
                                  pfi_scalar_im=pfi_T1,
                                  icv_factor=None,
                                  return_mm3=True)
        sa.labels_to_exclude = [153, ]
        vols, voxels, z1, z2 = sa.get_volumes_per_label(values_list)
        tot_vol_T1 = sa.get_total_volume()
    else:
        vols, voxels = np.array([0, ] * len(regions)), np.array([0, ] * len(regions))
        tot_vol_T1 = -1

    # FA:
    if verbose > 0:
        print('FA - get_average_below_labels')
    if os.path.exists(pfi_segm_FA) and os.path.exists(pfi_FA):
        sa = SegmentationAnalyzer(pfi_segmentation=pfi_segm_FA,
                                  pfi_scalar_im=pfi_FA,
                                  icv_factor=None,
                                  return_mm3=True)
        sa.labels_to_exclude = [153, ]
        FAs = sa.get_average_below_labels(values_list)
        tot_vol_FA = sa.get_total_volume()
    else:
        FAs = np.array([0, ] * len(regions))
        tot_vol_FA = -1

    # ADC:
    if verbose > 0:
        print('ADC - get_average_below_labels')
    if os.path.exists(pfi_segm_ADC) and os.path.exists(pfi_ADC):
        sa = SegmentationAnalyzer(pfi_segmentation=pfi_segm_ADC,
                                  pfi_scalar_im=pfi_ADC,
                                  icv_factor=None,
                                  return_mm3=True)
        sa.labels_to_exclude = [153, ]
        ADCs = sa.get_average_below_labels(values_list)
        tot_vol_ADC = sa.get_total_volume()
    else:
        ADCs = np.array([0, ] * len(regions))
        tot_vol_ADC = -1

    # g-ratio:
    if verbose > 0:
        print('g-ratio - get_average_below_labels')
    if os.path.exists(pfi_segm_g_ratio) and os.path.exists(pfi_g_ratio):
        sa = SegmentationAnalyzer(pfi_segmentation=pfi_segm_g_ratio,
                                  pfi_scalar_im=pfi_g_ratio,
                                  icv_factor=None,
                                  return_mm3=True)
        sa.labels_to_exclude = [153, ]  # exclude also olfactory bulbs for the g_ratios
        g_ratios = sa.get_average_below_labels(values_list)
        tot_vol_g_ratio = sa.get_total_volume()
    else:
        g_ratios = np.array([0, ] * len(regions))
        tot_vol_g_ratio = -1

    # T2_map
    # if verbose > 0:
    #     print('T2 map - get_average_below_labels')
    # if os.path.exists(pfi_segm_T2_map) and os.path.exists(pfi_T2_map):
    #     sa = SegmentationAnalyzer(pfi_segmentation=pfi_segm_T2_map,
    #                               pfi_scalar_im=pfi_T2_map,
    #                               icv_factor=None,
    #                               return_mm3=True)
    #     sa.labels_to_exclude = [153, ]
    #     T2_maps = sa.get_average_below_labels(values_list)
    #     tot_vol_T2_maps = sa.get_total_volume()
    # else:
    #     T2_maps = np.array([0, ] * len(regions))
    #     tot_vol_T2_maps = -1

    # Add total volume to the subjects info
    if False:  # if the ICV is stored somewhere, grab it...
        pass
    else:
        subject_info.update({'totVol T1': tot_vol_T1})
        subject_info.update({'totVol FA': tot_vol_FA})
        subject_info.update({'totVol ADC': tot_vol_ADC})
        subject_info.update({'totVol g_ratio': tot_vol_g_ratio})
        # subject_info.update({'totVol T2_maps': tot_vol_T2_maps})

    # Add ICV estimation to the subject info
    if False:  # if the ICV is stored somewhere, grab it...
        pass
    else:
        subject_info.update({'ICV': -1})

    ''' Create rabbit data from excel files'''

    # Compile record:
    record = {'Info'      : subject_info,
              'Regions'   : regions,
              'LabelsID'  : values_list,
              'NumVoxels' : voxels,
              'vols'      : vols,
              'FAs'       : FAs,
              'ADCs'      : ADCs,
              'g_ratios'  : g_ratios,
              # 'T2_maps'   : T2_maps
              }

    # -- save python dictionary
    np.save(jph(pfo_output, subject_name + '_record.npy') , record)

    # -- save record in csv
    list_keys = ['ID Number', 'Sex', 'Delivery Gestation (d)', 'Harvest Date', 'MRI Date', 'Weight PND1 (g)',
                 'Brain Weight (g)', 'Acquisition', 'Brain Vol (ml)']
    preamble_data = []
    for k in list_keys:
        if k in subject_info.keys():
            if isinstance(subject_info[k], datetime.datetime):
                preamble_data.append([k, subject_info[k].strftime('%Y-%m-%d')])
            else:
                preamble_data.append([k, subject_info[k]])

    record_tab = []
    for reg, lab, vox, vol, fa, adc, gr in zip(regions, values_list, voxels, vols, FAs, ADCs, g_ratios):
        record_tab.append([reg, lab, vox, vol, fa, adc, gr])
    headers = ['region', 'label number', 'number of voxels', 'vol (mm)', 'FA', 'ADC', 'g-ratio']
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
        fi.write('Delivery Gestation (d)  : {}\n'.format(subject_info['Delivery Gestation (g)']))
        fi.write('Harvest Date            : {}\n'.format(subject_info['Harvest Date'].strftime('%Y-%m-%d')))
        fi.write('MRI Date                : {}\n'.format(subject_info['MRI Date'].strftime('%Y-%m-%d')))
        fi.write('Weight PND1 (g)         : {}\n'.format(subject_info['Weight PND1 (g)']))
        fi.write('Brain Weight (g)        : {}\n'.format(subject_info['Brain Weight (g)']))
        fi.write('Brain Vol (ml)          : {}\n'.format(subject_info['Brain Volume (ml)']))
        fi.write('Acquisition             : {}\n'.format(subject_info['Acquisition']))
        fi.write('totVol T1               : {}\n'.format(subject_info['totVol T1']))
        fi.write('totVol FA               : {}\n'.format(subject_info['totVol FA']))
        fi.write('totVol ADC              : {}\n'.format(subject_info['totVol ADC']))
        fi.write('totVol g_ratio          : {}\n'.format(subject_info['totVol g_ratio']))
        # fi.write('totVol T2 map           : {}\n'.format(subject_info['totVol T2_maps']))
        fi.write('Estimated ICV           : {}\n'.format(subject_info['ICV']))

        # append empty lines
        fi.write('\n\n')

        # append table region | label number | vol | FA | ADC
        fi.write(table)
        fi.close()

    # -- save record in csv

    return record


# -- TEST HERE:
#
# pfo_subject = '/Users/sebastiano/Desktop/test_main/A_internal_template/1201'
# pfo_output = '/Users/sebastiano/Desktop/test_main/1201_report'
# sj = '1201'
#
# assert os.path.exists(pfo_subject)
# assert os.path.exists(pfo_output)
#
# compile_record(pfi_T1=jph(pfo_subject, 'all_modalities', sj  + '_T1.nii.gz'),
#                pfi_FA=jph(pfo_subject, 'all_modalities', sj  + '_FA.nii.gz'),
#                pfi_ADC=jph(pfo_subject, 'all_modalities', sj  + '_MD.nii.gz'),
#                pfi_multi_lab_descriptor=jph('/Users/sebastiano/Desktop/test_main/A_internal_template/Utils',
#                                             'multi_labels_descriptor.txt'),
#                pfi_segmentation=jph(pfo_subject, 'segm', 'approved', sj + '_propagate_me_2.nii.gz'),
#                pfi_excel_table=jph('/Users/sebastiano/Dropbox/RabbitEOP-MRI/docs', 'REoP_Pilot_MRI_Data.xlsx'),
#                subject_name=sj,
#                pfo_output=pfo_output)
