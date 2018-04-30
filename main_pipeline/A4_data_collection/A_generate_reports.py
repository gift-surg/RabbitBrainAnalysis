"""
Standard measurements on the selected data.
Volume, Volume/tot_volume, FA_i, MD_i, i in regions.

Very direct approach to create the intended data structure.
No ICV or other corrections, no stats, no sigma or outlier removal.
ONLY getting the row data in the report folder for each subject, both in stereotaxic and in the original orientation.
The raw data in the A_data/<study>/<cathegory>/<sj> folder for each subject.
"""
import numpy as np
import pandas as pa
import nibabel as nib
from os.path import join as jph
import pickle

from collections import OrderedDict

from main_pipeline.A0_main.main_controller import ListSubjectsManager

from tools.definitions import root_study_rabbits, pfo_subjects_parameters, pfi_labels_descriptor

from LABelsToolkit.tools.aux_methods.utils_nib import one_voxel_volume
from LABelsToolkit.tools.caliber.volumes_and_values import get_total_num_nonzero_voxels
from LABelsToolkit.tools.descriptions.manipulate_descriptors import LabelsDescriptorManager as LdM
from LABelsToolkit.main import LABelsToolkit as LabT


def collect_data_from_subject_list(sj_list, pfo_storage, controller=None, report_folder='report_stereotaxic', remove_3_sigma=False):
    """
    :param sj_list: list of subjects
    :param pfo_storage: where to save the obtained dataframe per region, per value.
    :param controller: controller values
    :return:
    """

    # Load regions with labels_descriptor_manager:

    pfi_descriptor = '/Users/sebastiano/Dropbox/RabbitEOP-MRI/study/A_atlas/labels_descriptor_abbrev.txt'

    ldm = LdM(pfi_descriptor)
    dict = ldm.get_dict()
    pfi_hwere_to_save = '/Users/sebastiano/Desktop/zzz_lab_abbrev.txt'

    ldm.save_labels_and_abbreviations(pfi_hwere_to_save)

    for d in dict.keys():
        if len(dict[d]) == 4:
            print("{0} : '{1}',".format(d, dict[d][3]))

    # elaborate for each region


    if controller['Volumes_per_regions']:
        """
        Get the files under report, for subject sj, region reg and corresponding label lab as:
        <sj>_vol_<reg>_<lab>.csv
        """
        for k in ptb_related_regions.keys():
            se_vols_region_k = pa.Series(np.array([0, ] * len(sj_list)).astype(np.float64), index=sj_list)

            for sj in sj_list:
                print('\nCollection 3, subject {}, region {}. '.format(sj, k))
                sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

                study = sj_parameters['study']
                category = sj_parameters['category']

                pfo_subject = jph(root_study_rabbits, 'A_data', study, category, sj)
                pfi_segm = jph(pfo_subject, 'segm', '{}_T1_segm.nii.gz'.format(sj))

                im_segm = nib.load(pfi_segm)

                tot_num_voxels = get_total_num_nonzero_voxels(im_segm)
                # load volumes saved in in the report of each subject.
                pfi_report_vols = jph(pfo_subject, report_folder, '{}_volumes.pkl'.format(sj))

                df = pa.read_pickle(pfi_report_vols)

                num_voxel_reg_k = 0
                for k_j in ptb_related_regions[k]:
                    num_voxel_reg_k += df['num_voxels']['[{}]'.format(k_j)]

                net_volume = num_voxel_reg_k / float(tot_num_voxels)
                se_vols_region_k[sj] = net_volume

            print se_vols_region_k

            se_vols_region_k.name = 'Volumes normalised tot brain vol, region {0}'.format(ptb_related_regions[k])
            se_vols_region_k.to_pickle(jph(pfo_storage, 'VolumesRegionOverTotBV{0}.pkl'.format(k)))

    # --> Collection 5: FA per regions
    if controller['FA_per_regions']:
        """
        Get the files under report, for subject sj, region reg and corresponding label lab as
        <sj>_vol_<reg>_<lab>.csv
        """
        ldm = LdM(pfi_labels_descriptor)
        labels_dict = ldm.get_dict()
        for k in ptb_related_regions.keys():
            print('FA per regions, all subjects, region {}'.format(k))
            vals_per_region_k = []
            for sj in sj_list:
                sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

                study = sj_parameters['study']
                category = sj_parameters['category']

                pfo_subject = jph(root_study_rabbits, 'A_data', study, category, sj)
                arrays_FA_k = []
                for k_j in ptb_related_regions[k]:
                    pfi_saved_data_FA = jph(pfo_subject, report_folder, '{}_FA_{}_{}.npy'.format(sj, labels_dict[k_j][-1].replace(' ', ''), k_j))
                    arrays_FA_k.append(np.load(pfi_saved_data_FA))

                unrolled_arrays_FA_k = np.concatenate(arrays_FA_k, axis=0)
                if remove_3_sigma:
                    three_std = 3 * np.std(unrolled_arrays_FA_k)
                    mean = np.mean(unrolled_arrays_FA_k)
                    unrolled_arrays_FA_k = [x for x in unrolled_arrays_FA_k if (x > mean - three_std)]
                    unrolled_arrays_FA_k = [x for x in unrolled_arrays_FA_k if (x < mean + three_std)]

                vals_per_region_k.append(unrolled_arrays_FA_k)

            se_vals_per_region_k = pa.Series(vals_per_region_k, index=sj_list)
            print se_vals_per_region_k
            se_vals_per_region_k.name = 'FA per values, region {0}'.format(ptb_related_regions[k])
            se_vals_per_region_k.to_pickle(jph(pfo_storage, 'FARegion{0}.pkl'.format(k)))

    # --> Collection 6: MD per regions
    if controller['MD_per_regions']:
        ldm = LdM(pfi_labels_descriptor)
        labels_dict = ldm.get_dict()
        for k in ptb_related_regions.keys():
            print('MD per regions, all subjects, region {}'.format(k))
            vals_per_region_k = []
            for sj in sj_list:
                sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

                study = sj_parameters['study']
                category = sj_parameters['category']

                pfo_subject = jph(root_study_rabbits, 'A_data', study, category, sj)
                arrays_MD_k = []
                for k_j in ptb_related_regions[k]:
                    pfi_saved_data_MD = jph(pfo_subject, report_folder,
                                            '{}_MD_{}_{}.npy'.format(sj, labels_dict[k_j][-1].replace(' ', ''), k_j))
                    arrays_MD_k.append(np.load(pfi_saved_data_MD))

                unrolled_arrays_MD_k = np.concatenate(arrays_MD_k, axis=0)
                if remove_3_sigma:
                    three_std = 3 * np.std(unrolled_arrays_MD_k)
                    mean = np.mean(unrolled_arrays_MD_k)
                    unrolled_arrays_MD_k = [x for x in unrolled_arrays_MD_k if (x > mean - three_std)]
                    unrolled_arrays_MD_k = [x for x in unrolled_arrays_MD_k if (x < mean + three_std)]

                vals_per_region_k.append(unrolled_arrays_MD_k)

            se_vals_per_region_k = pa.Series(vals_per_region_k, index=sj_list)
            se_vals_per_region_k.name = 'MD per values, region {0}'.format(ptb_related_regions[k])
            se_vals_per_region_k.to_pickle(jph(pfo_storage, 'MDRegion{0}.pkl'.format(k)))

    # -------- STEREOTAXIC ------



def generate_reports(sj_list):

    controller = {'Volumes_per_regions' : True,
                  'FA_per_regions'      : True,
                  'MD_per_regions'      : True}
    collect_data_from_subject_list(sj_list, controller=controller)


if __name__ == '__main__':
    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull = False
    lsm.execute_PTB_ex_vivo = False
    lsm.execute_PTB_in_vivo = False
    lsm.execute_PTB_op_skull = False
    lsm.execute_ACS_ex_vivo = False

    # lsm.input_subjects = ['4302', '4303', '4304', '4305', '4501', '4504']
    # lsm.input_subjects = ['0802t1']  # ['1201', '1203', '1305', '1404', '1507', '1510', '1702', '1805', '2002', '2502', '3301', '3404']  # , '4305']

    # lsm.input_subjects = ['0802t1', ]
    # lsm.input_subjects = ['0904t1']
    # lsm.input_subjects = ['1501t1', ]
    # lsm.input_subjects = ['12001', ]  # ['1201', '4602', '12001']

    # lsm.input_subjects = ['F1Test', ]  # ['1201', '4602', '12001']
    # lsm.input_subjects = ['F2Test', ]  # ['1201', '460A_move_to_stereotaxic_coordinates.pyc2', '12001']
    # lsm.input_subjects = ['12607', ]  # ['1201', '4602', '12001']

    # lsm.input_subjects = ['12307', '12308', '12402']
    # lsm.input_subjects = ['12504', '12505', '12607']
    # lsm.input_subjects = ['12608', '12609', '12610']

    lsm.input_subjects = ['13103', '13108', '13301', '13307', '13401', '13403', '13404']
    # lsm.input_subjects = ['13405', '13501', '13505', '13507', '13602', '13604', '13606']


    lsm.update_ls()

    print(lsm.ls)

    generate_reports(lsm.ls)







