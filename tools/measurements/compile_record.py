"""
Measurements on labels.
"""
import codecs
import csv
import datetime
import numpy as np
import os
import nibabel as nib
from tabulate import tabulate

from os.path import join as jph
import pickle

from tools.definitions import pfo_subjects_parameters


from tools.auxiliary.parse_excel_tables_and_descriptors import parse_excel_data_to_list, \
    parse_multi_label_descriptor_in_a_list

from labels_manager.tools.aux_methods.utils import print_and_run


# TODO needs to be refactored using labels manager methods.


class SegmentationAnalyzer(object):

    def __init__(self, pfi_segmentation, pfi_scalar_im, icv_factor=None, return_mm3=True):

        for p in [pfi_segmentation, pfi_scalar_im]:
            if not os.path.exists(p):
                raise IOError('Input data path {} does not exist.'.format(p))

        self.pfi_segmentation = pfi_segmentation
        self.return_mm3 = return_mm3
        self.pfi_scalar_im = pfi_scalar_im
        self.icv_factor = icv_factor
        self.labels_to_exclude = None

        self._segmentation = None
        self._scalar_im = None
        self._one_voxel_volume = None

        self.update()

    def update(self):

        self._segmentation = nib.load(self.pfi_segmentation)
        self._scalar_im = nib.load(self.pfi_scalar_im)

        np.testing.assert_array_almost_equal(self._scalar_im.get_affine(), self._segmentation.get_affine())
        np.testing.assert_array_almost_equal(self._scalar_im.shape, self._segmentation.shape)

        self._one_voxel_volume = np.round(np.abs(np.prod(np.diag(self._segmentation.get_affine()))), decimals=6)

    def get_total_volume(self):

        if self.labels_to_exclude is not None:

            seg = np.copy(self._segmentation.get_data())
            for index_label_k, label_k in enumerate(self.labels_to_exclude):
                places = self._segmentation.get_data() != label_k
                seg = seg * places.astype(np.int)

            num_voxels = np.count_nonzero(seg)
        else:
            num_voxels = np.count_nonzero(self._segmentation.get_data())

        if self.return_mm3:
            mm_3 = num_voxels * self._one_voxel_volume
            return mm_3
        else:
            return num_voxels

    def get_volumes_per_label(self, selected_labels, verbose=0):
        """
        :param selected_labels: can be an integer, or a list.
         If it is a list, it can contain sublists.
         If labels are in the sublist, volumes will be computed for all the labels in the list.
        e.g. [1,2,[3,4]] -> volume of label 1, volume of label 2, volume of label 3 and 4.
        :param verbose:
        :return:
        """
        if isinstance(selected_labels, int):
            selected_labels = [selected_labels, ]
        elif isinstance(selected_labels, list):
            pass
        else:
            raise IOError('Input labels must be a list or an int.')

        # get tot volume
        tot_brain_volume = self.get_total_volume()

        # Get volumes per regions:
        voxels = np.zeros(len(selected_labels), dtype=np.uint64)

        for index_label_k, label_k in enumerate(selected_labels):

            if isinstance(label_k, int):
                places = self._segmentation.get_data()  == label_k
            else:
                places = np.zeros_like(self._segmentation.get_data(), dtype=np.bool)
                for label_k_j in label_k:
                    places += self._segmentation.get_data() == label_k_j

            voxels[index_label_k] = np.count_nonzero(places)

        if self.return_mm3:
               vol = self._one_voxel_volume * voxels.astype(np.float64)
        else:
            vol = voxels.astype(np.float64)[:]

        # get volumes over total volume:
        vol_over_tot = vol / float(tot_brain_volume)

        # get volume over ICV estimates
        if self.icv_factor is not None:
            vol_over_icv = vol / float(self.icv_factor)
        else:
            vol_over_icv = np.zeros_like(vol)

        # show a table at console:
        if verbose:
            headers = ['labels', 'Vol', 'Vol/totVol', 'Vol/ICV']
            table = [[r, v, v_t, v_icv] for r, v, v_t, v_icv in zip(selected_labels, vol, vol_over_tot, vol_over_icv)]
            print(tabulate(table, headers=headers))

        return vol, voxels, vol_over_tot, vol_over_icv

    def get_average_below_labels(self, selected_labels, verbose=0):
        """
        :param selected_labels:  can be an integer, or a list.
         If it is a list, it can contain sublists.
         If labels are in the sublist, volumes will be computed for all the labels in the list.
        e.g. [1,2,[3,4]] -> volume of label 1, volume of label 2, volume of label 3 and 4.
        :param verbose:
        :return:
        """
        if isinstance(selected_labels, int):
            selected_labels = [selected_labels, ]
        elif isinstance(selected_labels, list):
            pass
        else:
            raise IOError('Input labels must be a list or an int.')

        # Get volumes per regions:
        values = np.zeros(len(selected_labels), dtype=np.float64)

        for index_label_k, label_k in enumerate(selected_labels):

            if isinstance(label_k, int):
                all_places = self._segmentation.get_data() == label_k
            else:
                all_places = np.zeros_like(self._segmentation.get_data(), dtype=np.bool)
                for label_k_j in label_k:
                    all_places += self._segmentation.get_data() == label_k_j

            masked_scalar_data = np.nan_to_num((all_places.astype(np.float64) * self._scalar_im.get_data().astype(np.float64)).flatten())
            # remove zero elements from the array:
            non_zero_masked_scalar_data = masked_scalar_data[np.where(masked_scalar_data > 1e-6)]  # 1e-6

            if non_zero_masked_scalar_data.size == 0:  # if not non_zero_masked_scalar_data is an empty array.
                non_zero_masked_scalar_data = 0.

            values[index_label_k] = np.mean(non_zero_masked_scalar_data)

            # mean_voxel = np.mean(non_zero_masked_scalar_data)
            # if self.return_mm3:
            #     values[index_label_k] = ( 1 / self._one_voxel_volume ) * mean_voxel
            # else:
            #     values[index_label_k] = mean_voxel

            if verbose:
                print('Mean below the labels for the given image {0} : {1}'.format(selected_labels[index_label_k], values[index_label_k]))
                if isinstance(non_zero_masked_scalar_data, np.ndarray):
                    print 'non zero masked scalar data : ' + str(len(non_zero_masked_scalar_data))
        return values


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
    sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, subject_name), 'r'))

    study = sj_parameters['study']

    excel_tab_list = parse_excel_data_to_list(pfi_excel_table, worksheet_name=study)
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
