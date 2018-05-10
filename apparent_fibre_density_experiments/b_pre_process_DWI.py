import os
import numpy as np
import nibabel as nib
import pickle
from os.path import join as jph


from tools.definitions import pfo_subjects_parameters, root_atlas, root_study_rabbits
from apparent_fibre_density_experiments.main import root_DWIs_original, root_MASKs, root_SEGMs, \
    root_DWIs_corrected, root_intermediate

from LABelsToolkit.tools.aux_methods.utils import print_and_run


def denoise_mif_for_subject(sj, controller):

    pfi_DWI  = jph(root_intermediate, '{}_DWI_slope_corrected_to_std.nii.gz'.format(sj))
    pfi_brain_mask = jph(root_MASKs, '{}_brain.nii.gz'.format(sj))

    assert os.path.exists(pfi_DWI)
    assert os.path.exists(pfi_brain_mask)

    if controller['Denoise']:
        pfi_DWI_denoised = jph(root_DWIs_corrected, '{}_DWI.nii.gz'.format(sj))
        pfi_DWI_noise    = jph(root_intermediate, '{}_noise.nii.gz'.format(sj))
        cmd = 'dwidenoise {} {} -noise {} -mask {}'.format(
            pfi_DWI, pfi_DWI_denoised, pfi_DWI_noise, pfi_brain_mask)
        print_and_run(cmd)

    if controller['Get_differences']:
        pfi_DWI_denoised = jph(root_DWIs_corrected, '{}_DWI.nii.gz'.format(sj))
        pfi_DWI_noise = jph(root_intermediate, '{}_noise.nii.gz'.format(sj))
        assert os.path.exists(pfi_DWI_denoised)
        assert os.path.exists(pfi_DWI_noise)
        pfi_residual = jph(root_intermediate, '{}_residual.nii.gz'.format(sj))
        cmd = 'mrcalc {} {} -subtract {}'.format(pfi_DWI, pfi_DWI_denoised, pfi_residual)
        print_and_run(cmd)

    if controller['Quality_control']:
        pfi_residual = jph(root_intermediate, '{}_residual.nii.gz'.format(sj))
        assert os.path.exists(pfi_residual)
        cmd = 'mrview {}'.format(pfi_residual)
        print_and_run(cmd)

    if controller['Eddy_correct']:
        print('- eddy current {}'.format(sj))
        pfi_DWI_denoised = jph(root_DWIs_corrected, '{}_DWI.nii.gz'.format(sj))
        assert os.path.exists(pfi_DWI_denoised)
        pfi_DWI_denoised_eddy = jph(root_DWIs_corrected, '{}_DWI_eddy.nii.gz'.format(sj))
        cmd = 'eddy_correct {0} {1} 0 '.format(pfi_DWI_denoised, pfi_DWI_denoised_eddy)
        print_and_run(cmd)

    if controller['Quality_control_Eddy']:
        pfi_DWI_denoised = jph(root_DWIs_corrected, '{}_DWI.nii.gz'.format(sj))
        pfi_DWI_denoised_eddy = jph(root_DWIs_corrected, '{}_DWI_eddy.nii.gz'.format(sj))
        assert os.path.exists(pfi_DWI_denoised), pfi_DWI_denoised
        assert os.path.exists(pfi_DWI_denoised_eddy), pfi_DWI_denoised_eddy
        cmd = 'mrview -load {0} -load {1}'.format(pfi_DWI_denoised, pfi_DWI_denoised_eddy)
        print_and_run(cmd)

    if controller['Grafting_denoised']:
        pfi_DWI_denoised = jph(root_DWIs_corrected, '{}_DWI.nii.gz'.format(sj))
        pfi_residual = jph(root_intermediate, '{}_residual.nii.gz'.format(sj))

        pass

    if controller['Grafting_denoised_Eddy']:
        pfi_DWI_denoised_eddy = jph(root_DWIs_corrected, '{}_DWI_eddy.nii.gz'.format(sj))
        pfi_residual = jph(root_intermediate, '{}_residual.nii.gz'.format(sj))

        pass


def denoise_mif_for_list(sj_list, controller):

    for sj in sj_list:
        denoise_mif_for_subject(sj, controller)


if __name__ == '__main__':

    subjects = ['1201', ]  # '1203', '1305', '1404', '1507', '1510', '1702', '1805', '2002', '2502', '3301', '3404']

    control = {'Denoise'                : True,
               'Get_differences'        : True,
               'Quality_control'        : True,
               'Eddy_correct'           : True,
               'Quality_control_Eddy'   : True,
               'Grafting_denoised'      : True,
               'Grafting_denoised_Eddy' : True}

    denoise_mif_for_list(subjects, control)
