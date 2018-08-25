import os
import numpy as np
import nibabel as nib
import pickle
from os.path import join as jph

from nilabels.tools.aux_methods.utils import print_and_run

from tools.definitions import pfo_subjects_parameters, root_study_rabbits
from apparent_fibre_density_experiments.main import root_tmp, root_intermediate, root_DWIs_original, root_MASKs, root_SEGMs
from tools.correctors.slope_corrector import slope_corrector_path
from tools.auxiliary.squeezer import squeeze_image_from_path
from tools.auxiliary.reorient_images_header import orient2std
from tools.auxiliary.utils import scale_y_value_and_trim


def data_to_folder_structure_for_subject(sj):
    print('Get data for sj {} started!'.format(sj))

    sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

    study = sj_parameters['study']
    category = sj_parameters['category']

    pfo_sj_nifti = jph(root_study_rabbits, '02_nifti', study, category, sj)
    pfo_sj_data = jph(root_study_rabbits, 'A_data', study, category, sj)

    assert os.path.exists(pfo_sj_nifti), pfo_sj_nifti
    assert os.path.exists(pfo_sj_data), pfo_sj_data

    # Get DWI:
    pfo_DWI = jph(pfo_sj_nifti, '{}_DWI'.format(sj))

    pfi_DWI    = jph(pfo_DWI, '{}_DWI.nii.gz'.format(sj))
    pfi_bvects = jph(pfo_DWI, '{}_DWI_DwGradVec.txt'.format(sj))
    pfi_bvals  = jph(pfo_DWI, '{}_DWI_DwEffBval.txt'.format(sj))
    pfi_slope  = jph(pfo_DWI, '{}_DWI_slope.txt'.format(sj))

    assert os.path.exists(pfi_DWI), pfi_DWI
    assert os.path.exists(pfi_bvects), pfi_bvects
    assert os.path.exists(pfi_bvals), pfi_bvals
    assert os.path.exists(pfi_slope), pfi_slope

    print('- create and save the grad for sj {} started'.format(sj))
    bvects = np.loadtxt(pfi_bvects)
    bvals = np.loadtxt(pfi_bvals)
    grad = np.hstack([bvects, bvals.reshape(-1, 1)])
    pfi_grad = jph(root_tmp, '{}_bvals_bvects.txt'.format(sj))
    np.savetxt(pfi_grad, grad)

    print('- slope correction for sj {} started'.format(sj))
    slopes = np.loadtxt(pfi_slope)
    pfi_DWI_slope_corrected = jph(root_tmp, '{}_DWI_slope_corrected.nii.gz'.format(sj))
    slope_corrector_path(slopes, pfi_DWI, pfi_DWI_slope_corrected)

    print('- squeeze {}'.format(sj))
    squeeze_image_from_path(pfi_DWI_slope_corrected, pfi_DWI_slope_corrected)

    print('- Orient to standard {}'.format(sj))
    assert os.path.exists(pfi_DWI_slope_corrected)
    pfi_dwi_std = jph(root_intermediate, '{}_DWI_slope_corrected_to_std.nii.gz'.format(sj))
    orient2std(pfi_DWI_slope_corrected, pfi_dwi_std)
    if sj_parameters['DWI_squashed']:
        scale_y_value_and_trim(pfi_dwi_std, pfi_dwi_std, squeeze_factor=2.218074656188605)

    print('- GetSegm {}'.format(sj))
    pfi_segm = jph(pfo_sj_data, 'segm', '{}_S0_segm.nii.gz'.format(sj))
    assert os.path.exists(pfi_segm), pfi_segm
    pfi_segm_copy = jph(root_SEGMs, '{}_S0_segm.nii.gz'.format(sj))
    cmd = 'cp {} {}'.format(pfi_segm, pfi_segm_copy)
    print_and_run(cmd)

    print('- GetBrainMask {}'.format(sj))
    pfi_brain_mask = jph(root_MASKs, '{}_brain.nii.gz'.format(sj))
    cmd = 'seg_maths {0} -bin {1} '.format(pfi_segm_copy, pfi_brain_mask)
    print_and_run(cmd)
    cmd = 'seg_maths {0} -fill {0} '.format(pfi_brain_mask)
    print_and_run(cmd)
    cmd = 'seg_maths {0} -dil 1 {0} '.format(pfi_brain_mask)
    print_and_run(cmd)
    cmd = 'seg_maths {0} -ero 1 {0} '.format(pfi_brain_mask)
    print_and_run(cmd)

    print('- GetBrainMask - Wider {}'.format(sj))
    pfi_brain_mask_wide = jph(root_MASKs, '{}_brain_wide.nii.gz'.format(sj))
    cmd = 'seg_maths {0} -dil 3 {1} '.format(pfi_brain_mask, pfi_brain_mask_wide)
    print_and_run(cmd)


def data_to_folder_structure_for_list(sj_list):
    print('Run data_to_folder_structure for list {} '.format(sj_list))
    for sj in sj_list:
        data_to_folder_structure_for_subject(sj)


if __name__ == '__main__':

    subjects = ['1201', '1203', '1305', '1404', '1507', '1510', '1702', '1805', '2002', '2502', '3301', '3404']
    data_to_folder_structure_for_list(subjects)


