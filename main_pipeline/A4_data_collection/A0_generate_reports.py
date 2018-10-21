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

import nilabels as nis
from nilabels.tools.caliber.volumes_and_values import get_volumes_per_label
from nilabels.tools.aux_methods.label_descriptor_manager import LabelsDescriptorManager as LdM

from main_pipeline.A0_main.tag_collector import TagCollector
from tools.definitions import root_study_rabbits, pfo_subjects_parameters, pfi_labels_descriptor
from main_pipeline.A0_main.main_controller import ListSubjectsManager


def create_eroded_segmentations_if_not_already_created(pfi_segm_non_eroded, pfi_contour, pfi_segm_eroded):

    if os.path.exists(pfi_segm_eroded):
        print('eroded segmentation for {} already created.'.format(pfi_segm_eroded))
    else:

        print('Getting contour segmentation {}'.format(pfi_segm_non_eroded))

        nis_app = nis.App()
        nis_app.manipulate_intensities.get_contour_from_segmentation(pfi_segm_non_eroded, pfi_contour, verbose=1)

        cmd = 'seg_maths {} -sub {} {}'.format(pfi_segm_non_eroded, pfi_contour, pfi_segm_eroded)

        print('Getting eroded segmentation {}'.format(pfi_segm_non_eroded))
        print(cmd)
        os.system(cmd)


def generate_reports_for_subject(sj, controller, options, ldm):
    """
    :param sj: list of subjects
    :param ldm: instance of the class LabelsDescriptorManager from LABelsToolkit. This contains the informations
    from the label descriptors.
    :param controller: controller values
    :return:
    """
    # labels
    label_descriptor_dict = ldm.get_dict_itk_snap()

    labels_list = label_descriptor_dict.keys()
    labels_names = [label_descriptor_dict[k][2].replace(' ', '') for k in label_descriptor_dict.keys()]

    # --- paths to parameters and folders

    print('\nCollect report for subject {} started.\n'.format(sj))

    sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

    study    = sj_parameters['study']
    category = sj_parameters['category']

    folder_selected_segmentation = sj_parameters['names_architecture']['final_segm_strx']  # default 'automatic'
    suffix_selected_segmentation = sj_parameters['names_architecture']['suffix_segm']  # default 'MV_P2'

    root_subject  = jph(root_study_rabbits, 'A_data', study, category, sj)
    pfo_sj_mod    = jph(root_subject, 'mod')
    pfo_sj_segm   = jph(root_subject, 'segm')
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

        df_volumes.to_csv(pfi_sj_vol_regions, index=False)

        print('Vols all regions saved under {}'.format(pfi_sj_vol_regions))

    if controller['FA_per_region']:
        """
        Get the files under report, for subject sj, region reg and corresponding label lab as
        <sj>_FA_<reg>_<lab>.csv
        """
        im_segm = nib.load(pfi_segm_S0)
        im_anat = nib.load(pfi_anat_FA)

        assert im_segm.shape == im_anat.shape

        for k, reg in zip(labels_list[1:], labels_names[1:]):

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

        for k, reg in zip(labels_list[1:], labels_names[1:]):
            coords = np.where(im_segm.get_data() == k)
            MD_region_k = im_anat.get_data()[coords].flatten()

            pfi_sj_MD_regions = jph(pfo_sj_report, '{}_MD_{}_{}.csv'.format(sj, k, reg))
            np.savetxt(pfi_sj_MD_regions, MD_region_k)

            print('MD region {}, saved under {}'.format(k, pfi_sj_MD_regions))

        del im_anat, im_segm

    # ---------------------------
    # -------- STEREOTAXIC ------
    # ---------------------------  Eroded version of the segmentation can be done only in stereotaxic.

    # Path to file input:

    pfo_sj_mod_stx = jph(root_subject, 'stereotaxic', 'mod')
    pfo_sj_segm_stx = jph(root_subject, 'stereotaxic', 'segm')

    pfo_sj_report_stx = jph(root_subject, 'stereotaxic', 'report')

    if controller['Force_reset']:
        os.system('rm -r {}'.format(pfo_sj_report_stx))

    os.system('mkdir {}'.format(pfo_sj_report_stx))

    # --- Select manually the input segmentation:

    pfi_segm_stx = jph(pfo_sj_segm_stx, '{}_segm.nii.gz'.format(sj))

    if options['erosion']:
        print('Creating eroded segmentation if not already there\n')
        pfi_segm_stx_contour = jph(pfo_sj_segm_stx, '{}_segm_contour.nii.gz'.format(sj))
        pfi_segm_stx_eroded = jph(pfo_sj_segm_stx, '{}_segm_eroded.nii.gz'.format(sj))
        create_eroded_segmentations_if_not_already_created(pfi_segm_stx, pfi_segm_stx_contour, pfi_segm_stx_eroded)

    if folder_selected_segmentation == 'automatic':
        pfo_segmentation_strx = jph(pfo_sj_segm_stx, 'automatic')
    else:
        pfo_segmentation_strx = pfo_sj_segm_stx

    pfi_segm_stx = jph(pfo_segmentation_strx, '{}_{}.nii.gz'.format(sj, suffix_selected_segmentation))

    assert os.path.exists(pfi_segm_stx), pfi_segm_stx

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
        df_volumes.to_csv(pfi_sj_vol_regions, index=False)

        print('Vols stereotaxic all regions saved under {}'.format(pfi_sj_vol_regions))

    if controller['FA_per_region_stx']:
        """
        Get the files under report, for subject sj, region reg and corresponding label lab as
        <sj>_FA_<reg>_<lab>.csv
        """

        im_anat = nib.load(pfi_anat_FA_stx)

        if options['erosion']:
            im_segm = nib.load(pfi_segm_stx_eroded)
        else:
            im_segm = nib.load(pfi_segm_stx)

        assert im_segm.shape == im_anat.shape

        for k, reg in zip(labels_list[1:], labels_names[1:]):
            coords = np.where(im_segm.get_data() == k)
            FA_region_k = im_anat.get_data()[coords].flatten()

            if options['erosion']:
                pfi_sj_FA_regions_stx = jph(pfo_sj_report_stx, '{}stx_FA_{}_{}_eroded.csv'.format(sj, k, reg))
            else:
                pfi_sj_FA_regions_stx = jph(pfo_sj_report_stx, '{}stx_FA_{}_{}.csv'.format(sj, k, reg))

            np.savetxt(pfi_sj_FA_regions_stx, FA_region_k)

            print('FA stereotaxic region {}, saved under {}'.format(k, pfi_sj_FA_regions_stx))

        del im_anat, im_segm

    if controller['MD_per_region_stx']:
        """
        Get the files under report, for subject sj, region reg and corresponding label lab as
        <sj>_MD_<reg>_<lab>.csv
        """
        im_anat = nib.load(pfi_anat_MD_stx)

        if options['erosion']:
            im_segm = nib.load(pfi_segm_stx_eroded)
        else:
            im_segm = nib.load(pfi_segm_stx)

        assert im_segm.shape == im_anat.shape

        for k, reg in zip(labels_list[1:], labels_names[1:]):
            coords = np.where(im_segm.get_data() == k)
            MD_region_k = im_anat.get_data()[coords].flatten()

            if options['erosion']:
                pfi_sj_MD_regions_stx = jph(pfo_sj_report_stx, '{}stx_MD_{}_{}_eroded.csv'.format(sj, k, reg))
            else:
                pfi_sj_MD_regions_stx = jph(pfo_sj_report_stx, '{}stx_MD_{}_{}.csv'.format(sj, k, reg))

            np.savetxt(pfi_sj_MD_regions_stx, MD_region_k)

            print('MD stereotaxic region {}, saved under {}.'.format(k, pfi_sj_MD_regions_stx))

        del im_anat, im_segm

    # ---------------------------
    # -------- Generate TAG -----
    # ---------------------------
    if controller['Generate_tag']:
        pfi_to_tag                = jph(root_subject, '{}_tag.txt'.format(sj))
        pfi_to_sj_param_file      = jph(pfo_subjects_parameters, sj + '.txt')
        pfi_to_spotter_param_file = jph(root_subject, 'stereotaxic', 'z_SPOT_{}'.format(sj_parameters['spotter_tag']),
                                        'SPOT_parameters_records.txt')
        tg = TagCollector(pfi_to_tag)
        tg.update_tag(pfi_to_sj_param_file, pfi_to_spotter_param_file)


def generate_reports_from_list(sj_list, controller, options):
    # Load regions with labels_descriptor_manager:

    ldm = LdM(pfi_labels_descriptor)
    label_descriptor_dict = ldm.get_dict_itk_snap()

    print label_descriptor_dict.keys()

    for d in label_descriptor_dict.keys():
        print("{0} : '{1}',".format(d, label_descriptor_dict[d][2]))

    for sj_id in sj_list:
        generate_reports_for_subject(sj_id, controller=controller, ldm=ldm, options=options)


if __name__ == '__main__':

    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull  = False
    lsm.execute_PTB_ex_vivo   = False
    lsm.execute_PTB_in_vivo   = False
    lsm.execute_PTB_op_skull  = False
    lsm.execute_ACS_ex_vivo   = False

    # lsm.input_subjects = ['12307', '12308', '12402']
    # lsm.input_subjects = ['12504', '12505', '12607']
    # lsm.input_subjects = ['12608', '12609', '12610']

    # lsm.input_subjects   = ['4601', '4603']  # ['5009']  # '12308', '12402', '12504', '12505', '12607', '12608', '12609', '12610']  # ['13103', '13108', '13301', '13307', '13401', '13403', '13404']
    # lsm.input_subjects = ['13405', '13501', '13505', '13507', '13602', '13604', '13606']


    # '1501', '1504' '1508', '1509', '1511', '2013', '2202', '2205', '2206' : in vivo and not in subjects parameters.
    # '4303','4406', :  rejected.

    # term = ['1702', '1805', '2502', '2503', '2608', '4501', '4504', '4507', '4601', '4603', '13003', '13004', '13005',
    #         '13006']

    # preterm = ['1305', '1404', '1505', '1507', '1510', '2002', '3301', '3303', '3404', '4302', '4304',
    #            '4305', '4901', '4903', '5001']  # '1201', '1203',


    # lsm.input_subjects = preterm + term

    lsm.input_subjects = ['13601', '13603', '13604', '13605', '13610', '13706', '13707']  # ['13102', ] #  '13201', '13202', '13401', '13402', '13403']


    lsm.update_ls()

    print(lsm.ls)

    controller_ = {'Force_reset'                  : False,
                   'Volumes_per_region'           : True,
                   'FA_per_region'                : True,
                   'MD_per_region'                : True,
                   'Volumes_per_region_stx'       : True,
                   'FA_per_region_stx'            : True,
                   'MD_per_region_stx'            : True,
                   'Generate_tag'                 : False}

    options_ = {'erosion': False}

    generate_reports_from_list(lsm.ls, controller_, options_)