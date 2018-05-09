import os
import numpy as np
import nibabel as nib
import pickle
from os.path import join as jph

from LABelsToolkit.tools.aux_methods.utils import print_and_run

from tools.definitions import pfo_subjects_parameters, root_atlas, root_study_rabbits
from apparent_fibre_density_experiments.main import tmp_folder, root_DWIs_original, root_MASKs, root_SEGMs
from tools.correctors.slope_corrector import slope_corrector_path


def nifti_to_mif_for_subject(sj):
    print('NIFTI to MIF for sj {} started!'.format(sj))

    sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

    study = sj_parameters['study']
    category = sj_parameters['category']

    pfo_sj_nifti = jph(root_study_rabbits, '01_nifti', study, category, sj)
    pfo_sj_data = jph(root_study_rabbits, 'A_data', study, category, sj)

    assert os.path.exists(pfo_sj_nifti), pfo_sj_nifti
    assert os.path.exists(pfo_sj_data), pfo_sj_data

    # Get DWI:
    pfo_DWI = jph(pfo_sj_nifti, '{}_DWI'.format(sj))

    pfi_DWI = jph(pfo_DWI, '{}_DWI.nii.gz'.format(sj))
    pfi_bvects = jph(pfo_DWI, '{}_DWI_DwGradVec.txt'.format(sj))
    pfi_bvals = jph(pfo_DWI, '{}_DWI_DwEffBval.txt'.format(sj))
    pfi_slope = jph(pfo_DWI, '{}_DWI_slope.txt'.format(sj))

    assert os.path.exists(pfi_DWI), pfi_DWI
    assert os.path.exists(pfi_bvects), pfi_bvects
    assert os.path.exists(pfi_bvals), pfi_bvals
    assert os.path.exists(pfi_slope), pfi_slope

    # create and save the grad:
    bvects = np.loadtxt(pfi_bvects)
    bvals = np.loadtxt(pfi_bvals)
    grad = np.hstack([bvects, bvals.reshape(-1, 1)])
    pfi_grad = jph(tmp_folder, '{}_bvals_bvects.txt'.format(sj))
    # np.savetxt(pfi_grad, grad)

    # correct for the slope:
    print('- slope correction for sj {} started'.format(sj))
    slopes = np.loadtxt(pfi_slope)
    pfi_DWI_slope_corrected = jph(tmp_folder, '{}_DWI_slope_corrected.nii.gz'.format(sj))
    # slope_corrector_path(slopes, pfi_DWI, pfi_DWI_slope_corrected)

    # mrconvert
    pfi_DWI_mif = jph(root_DWIs_original, '{}_DWI.mif'.format(sj))
    cmd = 'mrconvert -grad {0} {1} {2}'.format(pfi_grad, pfi_DWI_slope_corrected, pfi_DWI_mif)
    # print_and_run(cmd)

    # Get SEGMs:
    pfi_segm = jph(pfo_sj_data, 'segm', '{}_S0_segm.nii.gz'.format(sj))
    assert os.path.exists(pfi_segm), pfi_segm
    pfi_segm_copy = jph(root_SEGMs, '{}_S0_segm.nii.gz'.format(sj))
    cmd = 'cp {} {}'.format(pfi_segm, pfi_segm_copy)
    # print_and_run(cmd)

    # Get MASKs:
    pfi_brain_mask = jph(root_MASKs, '{}_brain.nii.gz'.format(sj))
    cmd = 'seg_maths {0} -bin {1} '.format(pfi_segm_copy, pfi_brain_mask)
    print_and_run(cmd)
    cmd = 'seg_maths {0} -fill {0} '.format(pfi_brain_mask)
    print_and_run(cmd)
    cmd = 'seg_maths {0} -dil 1 {0} '.format(pfi_brain_mask)
    print_and_run(cmd)
    cmd = 'seg_maths {0} -ero 1 {0} '.format(pfi_brain_mask)
    print_and_run(cmd)

    # Get wide MASKs:
    pfi_brain_mask_wide = jph(root_MASKs, '{}_brain_wide.nii.gz'.format(sj))
    cmd = 'seg_maths {0} -dil 3 {1} '.format(pfi_brain_mask, pfi_brain_mask_wide)
    print_and_run(cmd)


def nifti_to_mif_for_list(sj_list):

    for sj in sj_list:
        nifti_to_mif_for_subject(sj)


if __name__ == '__main__':

    subjects = ['1201', '1203', '1305', '1404', '1507', '1510', '1702', '1805', '2002', '2502', '3301', '3404']
    nifti_to_mif_for_list(subjects)
