import os
import nibabel as nib
from os.path import join as jph


from apparent_fibre_density_experiments.main import root_DWIs_original, root_MASKs, root_SEGMs, \
    root_DWIs_corrected, root_intermediate, root_tmp

from nilabel.tools.aux_methods.utils import print_and_run
from nilabel.main import Nilabel as NiL


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

    if controller['Create_multi_timepoints_mask']:
        im_dwi = nib.load(pfi_DWI)
        pfi_brain_mask_multi_timepoint = jph(root_tmp, '{}_brain_multi_timepoints.nii.gz'.format(sj))
        nil = NiL()
        nil.manipulate_shape.extend_slice_new_dimension(pfi_brain_mask, pfi_output=pfi_brain_mask_multi_timepoint,
                                                        new_axis=3, num_slices=im_dwi.shape[-1])

        del im_dwi, nil

    if controller['Grafting_denoised']:
        print('- grafting')
        pfi_DWI_denoised = jph(root_DWIs_corrected, '{}_DWI.nii.gz'.format(sj))
        pfi_residual = jph(root_intermediate, '{}_residual.nii.gz'.format(sj))
        pfi_brain_mask_multi_timepoint = jph(root_tmp, '{}_brain_multi_timepoints.nii.gz'.format(sj))
        assert os.path.exists(pfi_DWI_denoised)
        assert os.path.exists(pfi_residual)
        assert os.path.exists(pfi_brain_mask_multi_timepoint)

        pfi_DWI_denoised_grafted = jph(root_DWIs_corrected, '{}_DWIg.nii.gz'.format(sj))
        nil = NiL()
        nil.manipulate_intensities.get_grafting(pfi_residual, pfi_DWI_denoised, pfi_DWI_denoised_grafted,
                                                pfi_brain_mask_multi_timepoint)

    if controller['Grafting_denoised_Eddy']:
        print('- grafting eddy')
        pfi_DWI_denoised_eddy = jph(root_DWIs_corrected, '{}_DWI_eddy.nii.gz'.format(sj))
        pfi_residual = jph(root_intermediate, '{}_residual.nii.gz'.format(sj))
        pfi_brain_mask_multi_timepoint = jph(root_tmp, '{}_brain_multi_timepoints.nii.gz'.format(sj))
        assert os.path.exists(pfi_DWI_denoised_eddy)
        assert os.path.exists(pfi_residual)
        assert os.path.exists(pfi_brain_mask_multi_timepoint)
        pfi_DWI_denoised_grafted_eddy = jph(root_DWIs_corrected, '{}_DWIg_eddy.nii.gz'.format(sj))
        nil = NiL()
        nil.manipulate_intensities.get_grafting(pfi_residual, pfi_DWI_denoised_eddy, pfi_DWI_denoised_grafted_eddy,
                                                pfi_brain_mask_multi_timepoint)


def denoise_mif_for_list(sj_list, controller):

    for sj in sj_list:
        denoise_mif_for_subject(sj, controller)


if __name__ == '__main__':

    subjects = ['1201', '1203', '1305', '1404', '1507', '1510', '1702', '1805', '2002', '2502', '3301', '3404']
    control = {'Denoise'                      : True,
               'Get_differences'              : True,
               'Quality_control'              : False,
               'Eddy_correct'                 : False,
               'Quality_control_Eddy'         : False,
               'Create_multi_timepoints_mask' : False,
               'Grafting_denoised'            : False,
               'Grafting_denoised_Eddy'       : False}

    denoise_mif_for_list(subjects, control)
