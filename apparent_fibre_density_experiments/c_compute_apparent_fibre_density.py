import os
import numpy as np
import nibabel as nib
import pickle
from os.path import join as jph

from LABelsToolkit.tools.aux_methods.utils import print_and_run

from tools.definitions import pfo_subjects_parameters, root_atlas, root_study_rabbits
from apparent_fibre_density_experiments.main import root_tmp, root_intermediate, root_DWIs_original, root_MASKs, root_SEGMs
from tools.correctors.slope_corrector import slope_corrector_path
from tools.auxiliary.squeezer import squeeze_image_from_path
from tools.auxiliary.reorient_images_header import orient2std
from tools.auxiliary.utils import scale_y_value_and_trim


def compute_AFD(sj, controller, options):

    # Fibre Orientation Distribution estimation

    if controller['FOD_estimation']:
        # dwiextract <input_upsampled_dwi> - | dwi2fod msmt_csd - <group_average_response_text_file> <output_fod_image> -mask <input_upsampled_mask>

        pfi_dwi = jph()


        pass

    if controller['Generate_FOD_template']:
        # population_template <input_folder_of_FOD_images> -mask_dir <input_mask_folder> <output_fod_template_image>
        pass

    if controller['Register_to_FOD_template']:
        # mrregister <input_fod_image> -mask1 <input_subject_mask> <input_fod_template_image> -nl_warp <subject2template_warp> <template2subject_warp>
        pass

    if controller['Warp_masks']:
        # mrtransform <input_upsampled_mask_image> -warp <subject2template_warp> -interp nearest <output_warped_mask>
        pass

    if controller['Intersect_masks']:
        # mrmath <input_all_warped_masks_multiple_inputs> min <output_template_mask_intersection>
        pass

    if controller['Warp_segms']:
        # mrtransform <input_upsampled_mask_image> -warp <subject2template_warp> -interp nearest <output_warped_mask>
        pass

    # Compute a white matter template analysis fixel mask
    # fod2fixel <input_fod_template_image> -mask <input_template_mask_intersection> -peak <template_peaks_image.msf>
    # fixelthreshold -crop <template_peaks_image.msf> 0.33 <analysis_fixel_mask.msf>
    # fixel2voxel <analysis_fixel_mask.msf> count - | mrthreshold - - -abs 0.5 | mrfilter - median <output_analysis_voxel_mask>
    # fod2fixel -mask <input_analysis_voxel_mask> <input_fod_template_image> -peak <output_temp.msf>
    # fixelthreshold <input_temp.msf> -crop 0.2 <output_analysis_fixel_mask.msf> -force
    # rm <temp.msf>

    # Transform FOD images to template space
    # mrtransform <input_subject_fod_image> -warp <subject2template_warp> -noreorientation <output_warped_fod_image>

    # Segment FOD images to estimate fixels and their fibre density (FD)
    # fod2fixel <input_warped_fod_image> -mask <input_analysis_voxel_mask> -afd <output_fd_not_reoriented.msf>

    # Reorient fixel orientations
    # fixelreorient <input_fd_not_reoriented.msf> <subject2template_warp> <output_fd_reoriented.msf>

    # Assign subject fixels to template fixels
    # fixelcorrespondence <input_fd_reoriented.msf> <input_analysis_fixel_mask.msf> <output_fd.msf>

    # Compute fibre cross-section (FC) metric
    # warp2metric <subject2template_warp> -fc <input_analysis_fixel_mask.msf> <output_fc.msf>
    # fixellog <input_fc.msf> <output_log_fc.msf>

    # Compute a combined measure of fibre density and cross-section (FDC)
    # fixelcalc <input_fd.msf> mult <input_fc.msf> <output_fdc.msf>

    # Perform whole-brain fibre tractography on the FOD template
    # tckgen -angle 22.5 -maxlen 250 -minlen 10 -power 1.0 <input_fod_template_image> -seed_image <input_analysis_voxel_mask> -mask <input_analysis_voxel_mask> -number 20000000 <output_tracks_20_million.tck>

    # Reduce biases in tractogram densities
    # tcksift <input_tracks_20_million.tck> <input_fod_template_image> <output_tracks_2_million_sift.tck> -term_number 2000000

    # Perform statistical analysis of FD, FC, and FDC
    # fixelcfestats <input_files> <input_analysis_fixel_mask.msf> <input_design_matrix.txt> <output_contrast_matrix.txt> <input_tracks_2_million_sift.tck> <output_prefix>



def compute_ADF_for_list(sj_list, controller, options):
    print('Run compute_ADF for list'.fomat(sj_list))

    for sj in sj_list:
        compute_AFD(sj, controller, options)

if __name__ == '__main__':

    controller_ = {'FOD_estimation'           : True,
                   'Generate_FOD_template'    : True,
                   'Register_to_FOD_template' : True,
                   'Warp_masks'               : True,
                   'Intersect_masks'          : True,
                   'Warp_segms'               : True,


                  }
    options_ = {'suffix': ''}  # can be empty or '_eddy'

    subjects = ['1201', '1203', '1305', '1404', '1507', '1510', '1702', '1805', '2002', '2502', '3301', '3404']
    compute_ADF_for_list(subjects, controller_, options_)
