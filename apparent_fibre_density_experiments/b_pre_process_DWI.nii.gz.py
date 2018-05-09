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

    pfi_DWI_mif  = jph(root_DWIs_original, '{}_DWI.mif'.format(sj))
    pfi_brain_mask = jph(root_MASKs, '{}_brain.nii.gz'.format(sj))

    assert os.path.exists(pfi_DWI_mif)
    assert os.path.exists(pfi_brain_mask)

    if controller['Denoise']:
        pfi_DWI_mif_denoised = jph(root_DWIs_corrected, '{}_DWI.mif'.format(sj))
        pfi_DWI_mif_noise    = jph(root_intermediate, '{}_noise.mif'.format(sj))
        cmd = 'dwidenoise {} {} -noise {} -mask {}'.format(
            pfi_DWI_mif, pfi_DWI_mif_denoised, pfi_DWI_mif_noise, pfi_brain_mask)
        print_and_run(cmd)

    if controller['Get_differences']:
        pfi_DWI_mif_denoised = jph(root_DWIs_corrected, '{}_DWI.mif'.format(sj))
        pfi_DWI_mif_noise    = jph(root_intermediate, '{}_noise.mif'.format(sj))
        assert os.path.exists(pfi_DWI_mif_denoised)
        assert os.path.exists(pfi_DWI_mif_noise)
        pfi_residual = jph(root_intermediate, '{}_residual.mif'.format(sj))
        cmd = 'mrcalc {} {} -subtract {}'.format(pfi_DWI_mif, pfi_DWI_mif_denoised, pfi_residual)
        print_and_run(cmd)

    if controller['Quality_control']:
        pfi_residual = jph(root_intermediate, '{}_residual.mif'.format(sj))
        assert os.path.exists(pfi_residual)
        cmd = 'mrview {}'.format(pfi_residual)
        print_and_run(cmd)

    if controller['Eddi_correct']:
        pfi_DWI_mif_denoised = jph(root_DWIs_corrected, '{}_DWI.mif'.format(sj))
        assert os.path.exists(pfi_DWI_mif_denoised), pfi_DWI_mif_denoised
        pfi_DWI_mif_denoised_eddi = jph(root_DWIs_corrected, '{}_DWI_Eddi.mif'.format(sj))
        cmd = 'dwipreproc {} {} -rpe_none -pe_dir AP'.format(pfi_DWI_mif_denoised, pfi_DWI_mif_denoised_eddi)
        print_and_run(cmd)

    if controller['Quality_control_Eddi']:
        pfi_DWI_mif_denoised = jph(root_DWIs_corrected, '{}_DWI.mif'.format(sj))
        pfi_DWI_mif_denoised_eddi = jph(root_DWIs_corrected, '{}_DWI_Eddi.mif'.format(sj))
        assert os.path.exists(pfi_DWI_mif_denoised), pfi_DWI_mif_denoised
        assert os.path.exists(pfi_DWI_mif_denoised_eddi), pfi_DWI_mif_denoised_eddi
        cmd = 'mrview -load {0} -load {1}'.format(pfi_DWI_mif_denoised, pfi_DWI_mif_denoised_eddi)
        print_and_run(cmd)


def denoise_mif_for_list(sj_list, controller):

    for sj in sj_list:
        denoise_mif_for_subject(sj, controller)


if __name__ == '__main__':

    subjects = ['1201', ]  # '1203', '1305', '1404', '1507', '1510', '1702', '1805', '2002', '2502', '3301', '3404']

    control = {'Denoise'                : False,
               'Get_differences'        : False,
               'Quality_control'        : False,
               'Eddi_correct'           : True,
               'Quality_control_Eddi'   : True,
               'Grafting_denoised'      : True,
               'Grafting_denoised_Eddi' : True}

    denoise_mif_for_list(subjects, control)
