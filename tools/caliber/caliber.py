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

from parse_label_descriptor import parse_label_descriptor_in_a_list
from parse_excel_table import parse_excel_data_to_list


class SegmentationAnalyzer(object):

    def __init__(self, pfi_segmentation='', pfi_scalar_im='', icv_factor=None, return_mm3=True):

        for p in [pfi_segmentation, pfi_scalar_im]:
            if not os.path.exists(p):
                IOError('Input data path {} does not exist.')

        self.pfi_segmentation = pfi_segmentation
        self.return_mm3 = return_mm3
        self.pfi_scalar_im = pfi_scalar_im
        self.icv_factor = icv_factor

    def get_total_volume(self):

        im_seg = nib.load(self.pfi_segmentation)

        num_voxels = np.count_nonzero(im_seg.get_data())

        if self.return_mm3:
            mm_3 = num_voxels * np.abs(np.prod(np.diag(im_seg.get_affine())))
            return mm_3
        else:
            return num_voxels

    def get_volumes_per_label(self, selected_labels, verbose=0):

        if isinstance(selected_labels, int):
            selected_labels = [selected_labels, ]

        im_seg = nib.load(self.pfi_segmentation)

        # get tot volume
        tot_brain_volume = self.get_total_volume()

        # Get volumes per regions:
        voxels = np.zeros(len(selected_labels), dtype=np.uint64)

        for index_label_k, label_k in enumerate(selected_labels):
            places = im_seg.get_data()  == label_k
            voxels[index_label_k] = np.count_nonzero(places)

        vol = np.abs(np.prod(np.diag(im_seg.get_affine()))) * voxels.astype(np.float64)

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

    def get_average_below_labels(self, selected_labels, verbose=1):

        if not os.path.exists(self.pfi_scalar_im):
            IOError('Input pfi_data missing')
        if isinstance(selected_labels, int):
            selected_labels = [selected_labels, ]

        im_seg = nib.load(self.pfi_segmentation)
        data_segmentation = im_seg.get_data()

        im_scalar = nib.load(self.pfi_scalar_im)
        data_scalar = im_scalar.get_data()

        assert data_scalar.shape == data_segmentation.shape

        # Get volumes per regions:
        values = np.zeros(len(selected_labels), dtype=np.float64)

        for index_label_k, label_k in enumerate(selected_labels):
            # ----------
            all_places = np.zeros_like(data_segmentation, dtype=np.bool)
            all_places += data_segmentation == label_k

            masked_scalar_data = all_places.astype(np.float64) * data_scalar.astype(np.float64)
            # remove zero elements from the array:
            non_zero_masked_scalar_data = (masked_scalar_data > 0.00000000001) * masked_scalar_data
            values[index_label_k] = np.mean(non_zero_masked_scalar_data)

            if verbose:
                print('Mean below the labels {0} : {1}'.format(selected_labels[index_label_k], values[index_label_k]))

        return values


def compile_record(pfi_T1,
                   pfi_FA,
                   pfi_ADC,
                   pfi_lab_descriptor,
                   pfi_segmentation,
                   pfi_excel_table,
                   subject_name,
                   pfo_output,
                   save_human_readable=True,
                   create_output_folder_if_not_present=True):

    # Sanity check input
    for p in [pfi_segmentation, pfi_lab_descriptor, pfi_T1, pfi_FA, pfi_ADC, pfi_excel_table]:
        if not os.path.exists(p):
            raise IOError('input file {} does not exists'.format(p))

    # Create output folder or check if exists:
    if not os.path.exists(pfo_output):
        if create_output_folder_if_not_present:
            os.system('mkdir -p {}'.format(pfo_output))
        else:
            raise IOError('input file {} does not exists'.format(pfo_output))

    # Get label descriptor data:
    lab_descriptor_list = parse_label_descriptor_in_a_list(pfi_lab_descriptor)
    labels_list = [k[0] for k in lab_descriptor_list]

    ''' Collect data using an instance of Caliber: '''

    sa = SegmentationAnalyzer(pfi_segmentation=pfi_segmentation,
                              pfi_scalar_im='',
                              icv_factor=None,
                              return_mm3=True)
    # T1 - volume (more accurate the segmentation on the T1 to avoid partial voluming):
    sa.pfi_scalar_im = pfi_T1
    vols, voxels, z1, z2 = sa.get_volumes_per_label(labels_list)

    # FA:
    sa.pfi_scalar_im = pfi_FA
    FAs = sa.get_average_below_labels(labels_list)

    # ADC:
    sa.pfi_scalar_im = pfi_ADC
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

    preamble_data = [['ID Number', subject_info['ID Number']],
                     ['Sex', subject_info['Sex']],
                     ['Delivery Gestation (d)', subject_info['Delivery Gestation (d)']],
                     ['Harvest Date', subject_info['Harvest Date'].strftime('%Y-%m-%d')],
                     ['MRI Date', subject_info['MRI Date'].strftime('%Y-%m-%d')],
                     ['Weight PND1 (g)', subject_info['Weight PND1 (g)']],
                     ['Brain Weight (g)', subject_info['Brain Weight (g)']],
                     ['Acquisition', subject_info['Acquisition']]
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
# assert os.path.exists(pfo_subjet)
#
# compile_record(pfi_T1=jph(pfo_subjet, 'all_modalities', sj  + '_T1.nii.gz'),
#                    pfi_FA=jph(pfo_subjet, 'all_modalities', sj  + '_FA.nii.gz'),
#                    pfi_ADC=jph(pfo_subjet, 'all_modalities', sj  + '_MD.nii.gz'),
#                    pfi_lab_descriptor=jph(pfo_subjet, 'labels_descriptor_v8_beta.txt'),
#                    pfi_segmentation=jph(pfo_subjet, 'segm', 'approved', '1305_propagate_me_2.nii.gz'),
#                    pfi_excel_table=jph(pfo_subjet, 'REoP_Pilot_MRI_Data.xlsx'),
#                    subject_name=sj,
#                    pfo_output=pfo_output)


















'''

    def get_total_volume(self):
        """
        :return:
        """
        num_voxels = np.count_nonzero(self.seg_data)

        if self.return_mm3:
            mm_3 = num_voxels * np.abs(np.prod(np.diag(self.seg_affine)))
            return mm_3
        else:
            return num_voxels

    def get_volumes_per_zone(self):

        # get regions:
        if self.pfi_description is not None:
            regions = []
            f = open(self.pfi_description, 'r')
            for line in f:
                if not line.startswith('#'):
                    last = line.split('  ')
                    last = last[-1][1:-2]
                    regions.append(last)
        else:
            regions = ['label ' + str(j) for j in self.list_labels]

        # get tot volume
        tot_brain_volume = self.get_total_volume()

        # Get volumes per regions:
        vol = np.zeros(len(self.list_labels), dtype=np.uint64)

        for index_label_k, label_k in enumerate(self.list_labels):
            places = self.seg_data  == label_k
            vol[index_label_k] = np.count_nonzero(places)

        if self.return_mm3:
            vol = vol.astype(np.float64)
            vol = np.abs(np.prod(np.diag(self.seg_affine))) * vol

        np.testing.assert_almost_equal(np.sum(vol[1:]), tot_brain_volume,
                                       err_msg='Data not normalised correctly! Debug!')

        # get volumes over total volue:
        vol_over_tot = vol / float(tot_brain_volume)

        # get volume over ICV estimates
        if self.icv_factor is not None:
            vol_over_icv = vol / float(self.icv_factor)
        else:
            vol_over_icv = np.zeros_like(vol)

        headers = ['Regions', 'Vol', 'Vol/totVol', 'Vol/ICV']
        table = [[r, v, v_t, v_icv] for r, v, v_t, v_icv in zip(regions, vol, vol_over_tot, vol_over_icv)]

        print(tabulate(table, headers=headers))

        return regions, vol, vol_over_tot, vol_over_icv

'''