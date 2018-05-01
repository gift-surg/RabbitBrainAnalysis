"""
Standard measurements on the selected data.
Volume, Volume/tot_volume, FA_i, MD_i, i in regions.

Very direct approach to create the intended data structure.
No ICV or other corrections, no stats, no sigma or outlier removal.
ONLY getting the row data in the report folder for each subject, both in stereotaxic and in the original orientation.
The raw data in the A_data/<study>/<cathegory>/<sj> folder for each subject.
"""
import os
import numpy as np
import nibabel as nib
from os.path import join as jph
import pickle

from LABelsToolkit.tools.caliber.volumes_and_values import get_volumes_per_label
from LABelsToolkit.tools.descriptions.manipulate_descriptors import LabelsDescriptorManager as LdM

from tools.definitions import root_study_rabbits, pfo_subjects_parameters, pfi_labels_descriptor
from main_pipeline.A0_main.main_controller import ListSubjectsManager


def generate_reports_for_subject(sj, controller, ldm):
    """
    :param sj: list of subjects
    :param ldm: instance of the class LabelsDescriptorManager from LABelsToolkit. This contains the informations
    from the label descriptors.
    :param controller: controller values
    :return:
    """
    # labels
    label_descriptor_dict = ldm.get_dict()

    labels_list = label_descriptor_dict.keys()
    labels_names = [label_descriptor_dict[k][2].replace(' ', '') for k in label_descriptor_dict.keys()]

    # --- paths to parameters and folders

    print('\nCollect report for subject {} started.\n'.format(sj))

    sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

    study = sj_parameters['study']
    category = sj_parameters['category']

    root_subject = jph(root_study_rabbits, 'A_data', study, category, sj)

    pfo_sj_mod = jph(root_subject, 'mod')
    pfo_sj_segm = jph(root_subject, 'segm')

    pfo_sj_report = jph(root_subject, 'report')

    if controller['Force_reset']:
        os.system('rm -r {}'.format(pfo_sj_report))

    os.system('mkdir {}'.format(pfo_sj_report))

    # --- Path to file input

    pfi_segm_T1 = jph(pfo_sj_segm, '{}_T1_segm.nii.gz'.format(sj))
    pfi_segm_S0 = jph(pfo_sj_segm, '{}_S0_segm.nii.gz'.format(sj))

    pfi_anat_FA = jph(pfo_sj_mod, '{}_FA.nii.gz'.format(sj))
    pfi_anat_MD = jph(pfo_sj_mod, '{}_MD.nii.gz'.format(sj))

    assert os.path.exists(pfi_segm_T1)
    assert os.path.exists(pfi_segm_S0)

    if controller['Volumes_per_region']:
        """
        Get the files under report, for subject sj, region reg and corresponding label lab as:
        <sj>_vol_regions.csv
        """
        im_segm = nib.load(pfi_segm_T1)
        df_volumes = get_volumes_per_label(im_segm, labels=labels_list, labels_names=labels_names)

        pfi_sj_vol_regions = jph(pfo_sj_report, '{}_vol_regions.csv'.format(sj))
        df_volumes.to_csv(pfi_sj_vol_regions)

        print('Vols all regions saved under {}'.format(pfi_sj_vol_regions))

    if controller['FA_per_region']:
        """
        Get the files under report, for subject sj, region reg and corresponding label lab as
        <sj>_FA_<reg>_<lab>.csv
        """
        im_segm = nib.load(pfi_segm_S0)
        im_anat = nib.load(pfi_anat_FA)

        assert im_segm.shape == im_anat.shape

        for k, reg in zip(labels_list, labels_names):

            coords = np.where(im_segm.get_data() == k)
            FA_region_k = im_anat.get_data()[coords].flatten()

            pfi_sj_FA_regions = jph(pfo_sj_report, '{}_FA_{}_{}.csv'.format(sj, k, reg))
            np.savetxt(pfi_sj_FA_regions, FA_region_k)

            print('FA region {}, saved under {}'.format(k, pfi_sj_FA_regions))

        del im_anat, im_segm

    if controller['MD_per_region']:
        """
        Get the files under report, for subject sj, region reg and corresponding label lab as
        <sj>_MD_<reg>_<lab>.csv
        """
        im_segm = nib.load(pfi_segm_S0)
        im_anat = nib.load(pfi_anat_MD)

        assert im_segm.shape == im_anat.shape

        for k, reg in zip(labels_list, labels_names):
            coords = np.where(im_segm.get_data() == k)
            MD_region_k = im_anat.get_data()[coords].flatten()

            pfi_sj_MD_regions = jph(pfo_sj_report, '{}_MD_{}_{}.csv'.format(sj, k, reg))
            np.savetxt(pfi_sj_MD_regions, MD_region_k)

            print('MD region {}, saved under {}'.format(k, pfi_sj_MD_regions))

        del im_anat, im_segm

    # ---------------------------
    # -------- STEREOTAXIC ------
    # ---------------------------

    # Path to file input:

    pfo_sj_mod_stx = jph(root_subject, 'stereotaxic', 'mod')
    pfo_sj_segm_stx = jph(root_subject, 'stereotaxic', 'segm')

    pfo_sj_report_stx = jph(root_subject, 'stereotaxic', 'report')

    if controller['Force_reset']:
        os.system('rm -r {}'.format(pfo_sj_report_stx))

    os.system('mkdir {}'.format(pfo_sj_report_stx))

    pfi_segm_stx = jph(pfo_sj_segm_stx, '{}_segm.nii.gz'.format(sj))
    if not os.path.exists(pfi_segm_stx):
        pfi_segm_stx = jph(pfo_sj_segm_stx, 'automatic', '{}_{}.nii.gz'.format(sj, 'MV_P2'))

    assert os.path.exists(pfi_segm_stx)

    pfi_anat_FA_stx = jph(pfo_sj_mod_stx, '{}_FA.nii.gz'.format(sj))
    pfi_anat_MD_stx = jph(pfo_sj_mod_stx, '{}_MD.nii.gz'.format(sj))

    assert os.path.exists(pfi_segm_T1)
    assert os.path.exists(pfi_segm_S0)

    if controller['Volumes_per_region_stx']:
        """
        Get the files under report, for subject sj, region reg and corresponding label lab as:
        <sj>_vol_regions.csv
        """
        im_segm = nib.load(pfi_segm_stx)
        df_volumes = get_volumes_per_label(im_segm, labels=labels_list, labels_names=labels_names)

        pfi_sj_vol_regions = jph(pfo_sj_report_stx, '{}stx_vol_regions.csv'.format(sj))
        df_volumes.to_csv(pfi_sj_vol_regions)

        print('Vols stereotaxic all regions saved under {}'.format(pfi_sj_vol_regions))

    if controller['FA_per_region_stx']:
        """
        Get the files under report, for subject sj, region reg and corresponding label lab as
        <sj>_FA_<reg>_<lab>.csv
        """
        im_segm = nib.load(pfi_segm_stx)
        im_anat = nib.load(pfi_anat_FA_stx)

        assert im_segm.shape == im_anat.shape

        for k, reg in zip(labels_list, labels_names):
            coords = np.where(im_segm.get_data() == k)
            FA_region_k = im_anat.get_data()[coords].flatten()

            pfi_sj_FA_regions_stx = jph(pfo_sj_report_stx, '{}stx_FA_{}_{}.csv'.format(sj, k, reg))
            np.savetxt(pfi_sj_FA_regions_stx, FA_region_k)

            print('FA stereotaxic region {}, saved under {}'.format(k, pfi_sj_FA_regions_stx))

        del im_anat, im_segm

    if controller['MD_per_region_stx']:
        """
        Get the files under report, for subject sj, region reg and corresponding label lab as
        <sj>_MD_<reg>_<lab>.csv
        """
        im_segm = nib.load(pfi_segm_stx)
        im_anat = nib.load(pfi_anat_MD_stx)

        assert im_segm.shape == im_anat.shape

        for k, reg in zip(labels_list, labels_names):
            coords = np.where(im_segm.get_data() == k)
            MD_region_k = im_anat.get_data()[coords].flatten()

            pfi_sj_MD_regions_stx = jph(pfo_sj_report_stx, '{}stx_MD_{}_{}.csv'.format(sj, k, reg))
            np.savetxt(pfi_sj_MD_regions_stx, MD_region_k)

            print('MD stereotaxic region {}, saved under {}.'.format(k, pfi_sj_MD_regions_stx))

        del im_anat, im_segm


def generate_reports_from_list(sj_list, controller):
    # Load regions with labels_descriptor_manager:

    ldm = LdM(pfi_labels_descriptor)
    label_descriptor_dict = ldm.get_dict()

    print label_descriptor_dict.keys()

    for d in label_descriptor_dict.keys():
        print("{0} : '{1}',".format(d, label_descriptor_dict[d][2]))

    for sj_id in sj_list:
        generate_reports_for_subject(sj_id, controller=controller, ldm=ldm)


if __name__ == '__main__':
    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull = False
    lsm.execute_PTB_ex_vivo = False
    lsm.execute_PTB_in_vivo = False
    lsm.execute_PTB_op_skull = False
    lsm.execute_ACS_ex_vivo = False

    # lsm.input_subjects = ['12307', '12308', '12402']
    # lsm.input_subjects = ['12504', '12505', '12607']
    # lsm.input_subjects = ['12608', '12609', '12610']

    lsm.input_subjects   = ['12307', '12308', '12402', '12504', '12505', '12607', '12608', '12609', '12610']  # ['13103', '13108', '13301', '13307', '13401', '13403', '13404']
    # lsm.input_subjects = ['13405', '13501', '13505', '13507', '13602', '13604', '13606']

    lsm.update_ls()

    print(lsm.ls)

    controller_ = {'Force_reset'              : True,
                   'Volumes_per_region'       : True,
                   'FA_per_region'            : True,
                   'MD_per_region'            : True,
                   'Volumes_per_region_stx'   : True,
                   'FA_per_region_stx'        : True,
                   'MD_per_region_stx'        : True,
                   }

    generate_reports_from_list(lsm.ls, controller_)







