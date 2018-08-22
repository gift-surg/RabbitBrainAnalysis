import os
import pandas as pa
import numpy as np
import nibabel as nib
from collections import OrderedDict
from matplotlib import pyplot as plt
import pickle

from os.path import join as jph
import cPickle as Pickle

from nilabel.tools.aux_methods.label_descriptor_manager import LabelsDescriptorManager as LdM
from nilabel.tools.caliber.volumes_and_values import get_total_num_nonzero_voxels, \
    get_num_voxels_from_labels_list, get_values_below_labels_list
from nilabel.tools.aux_methods.utils_nib import one_voxel_volume
from tools.definitions import pfi_labels_descriptor
from tools.definitions import root_study_rabbits, pfo_subjects_parameters


class ReportGeneratorInStereotaxic(object):
    """
    Genearet minimal reports (volumetric, FA, MD) with raw data.
    Any further elaborations are done elsewhere.
    Here is the starting point to collect extra data such as MSME-T2, g-ratio, T2map, partial voluming,
    and other DWI parameters.
    A new method-class will be created for each of this, with the consequent file generation.
    """
    def __init__(self, subject_name):
        self.subject_name = subject_name
        self.pfo_subjects_parameters = pfo_subjects_parameters
        self._initialise_paths()
        self._create_report_folder()
        self._initialise_lables()

    def _initialise_paths(self):
        sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, self.subject_name), 'r'))
        study = sj_parameters['study']
        category = sj_parameters['category']
        self.pfo_subject = jph(root_study_rabbits, 'A_data', study, category, self.subject_name)
        self.pfo_report = jph(self.pfo_subject, 'report_stereotaxic')

    def _create_report_folder(self):
        os.system('rm -rf {}'.format(self.pfo_report))
        os.system('mkdir -p {}'.format(self.pfo_report))

    def _initialise_lables(self):
        ldm = LdM(pfi_labels_descriptor)
        self.multi_label_dict = ldm.get_multi_label_dict(keep_duplicate=True, combine_right_left=True)
        self.single_label_dict = ldm.get_multi_label_dict(keep_duplicate=True, combine_right_left=False)

    def get_raw_volumes(self):
        labels_list = [self.multi_label_dict[l] for l in self.multi_label_dict.keys()]
        labels_names_list = self.multi_label_dict.keys()
        im_segm = nib.load(jph(self.pfo_subject, 'stereotaxic', 'segm', '{0}_approved_round3.nii.gz'.format(self.subject_name)))
        num_voxels = [0] + get_num_voxels_from_labels_list(im_segm, labels_list)
        df_raw_volumes = pa.DataFrame({'region_names': labels_names_list, 'num_voxels' : num_voxels}, index=[str(a) for a in labels_list], columns=['region_names', 'num_voxels'])
        df_raw_volumes.to_pickle(jph(self.pfo_report, '{}_volumes.pkl'.format(self.subject_name)))
        df_raw_volumes.to_csv(jph(self.pfo_report, '{}_volumes.csv'.format(self.subject_name)))

    def get_raw_FA(self):
        labels_names_list = self.single_label_dict.keys()
        labels_list = [self.single_label_dict[l][0] for l in labels_names_list]
        im_segm = nib.load(jph(self.pfo_subject, 'stereotaxic', 'segm', '{0}_approved_round3.nii.gz'.format(self.subject_name)))
        im_anat = nib.load(jph(self.pfo_subject, 'stereotaxic', 'mod', '{0}_FA.nii.gz'.format(self.subject_name)))
        FA_values = get_values_below_labels_list(im_segm, im_anat, labels_list)
        for i, (label_name, label_id) in enumerate(zip(labels_names_list, labels_list)) :
            if i == 0:
                pass
            else:
                fin = '{0}_FA_{1}_{2}'.format(sj, label_name.replace(' ', '').strip(), label_id)
                np.save(jph(self.pfo_report, fin + '.npy'), FA_values[i])
                np.savetxt(jph(self.pfo_report, fin + '.csv'), FA_values[i], delimiter=",")

    def get_raw_MD(self):
        labels_names_list = self.single_label_dict.keys()
        labels_list = [self.single_label_dict[l][0] for l in labels_names_list]
        im_segm = nib.load(jph(self.pfo_subject, 'stereotaxic', 'segm', '{0}_approved_round3.nii.gz'.format(self.subject_name)))
        im_anat = nib.load(jph(self.pfo_subject, 'stereotaxic', 'mod', '{0}_MD.nii.gz'.format(self.subject_name)))
        FA_values = get_values_below_labels_list(im_segm, im_anat, labels_list)
        for i, (label_name, label_id) in enumerate(zip(labels_names_list, labels_list)) :
            if i == 0:
                pass
            else:
                fin = '{0}_MD_{1}_{2}'.format(sj, label_name.replace(' ', '').strip(), label_id)
                np.save(jph(self.pfo_report, fin + '.npy'), FA_values[i])
                np.savetxt(jph(self.pfo_report, fin + '.csv'), FA_values[i], delimiter=",")


if __name__ == '__main__':
    sj_atlas = ['1201', '1203', '1305', '1404', '1507', '1510', '1702', '1805', '2002', '2502', '3301', '3404']
    for sj in sj_atlas:
        print('Generate report subject {} in stereotaxic coordinates'.format(sj))
        rg = ReportGeneratorInStereotaxic(sj)
        rg.get_raw_volumes()
        rg.get_raw_FA()
        rg.get_raw_MD()
