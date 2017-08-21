"""
Functional for the creation of the template.

Pipeline to process the data for each subject ex_vivo subject in the pilot study.
The processing will orient in histological coordinate all the subjects in the appropriate
places for the folder structure.
Modalities to be processed and oriented:

> T1
> ADC
> FA
> V1 (DTI main eigenvector)
> b0

(MSME_T2 not reasonably usable in histological coordinates without a super resolution approach.)
Dlways process T1 before DWI.

"""
import nibabel as nib
from os.path import join as jph
from tools.definitions import root_pilot_study


from pipelines_internal_template_OLD.A0_template_atlas_in_vivo.pre_process_T1_in_vivo import process_T1
from pipelines_internal_template_OLD.A0_template_atlas_in_vivo.pre_process_DWI_fsl_in_vivo import process_DWI_fsl
from pipelines_internal_template_OLD.A0_template_atlas_in_vivo.pre_process_skull_strip_all import generate_skull_stripped

subjects = ['0802_t1', '0904_t1', '1501_t1', '1504_t1', '1508_t1', '1509_t1', '1511_t1']
# subjects = ['0904_t1', '1501_t1', '1504_t1', '1508_t1', '1509_t1', '1511_t1']
# subjects = ['1509_t1', ]

controller_process_T1 = {'safety_on':                     False,
                         'step_generate_output_folder':   True,
                         'step_thr':                      True,
                         'step_normalise_mean':           True,
                         'step_header_in_histological':   True,
                         'step_reorient_histological':    True,
                         'step_copy_histological_mask':   True,
                         'step_bfc':                      True,
                         'step_cut_masks':                True,
                         'step_save_results':             True,
                         'delete_intermediate_steps':     False}

controller_process_DWI = {'safety_on':                      False,
                          'step_generate_output_folder':    False,
                          'step_squeeze':                   False,
                          'step_extract_bval_bvect_slope':  False,
                          'step_correct_the_slope':         False,
                          'step_eddy_current_corrections':  False,
                          'step_get_roi_mask_in_dwi_coord': False,
                          'step_dwi_analysis_with_fsl':     False,
                          'step_orient_histological':       True,
                          'step_bfc_b0':                    False,  # keep false
                          'step_save_results_histo':        True,
                          'delete_intermediate_steps':      False
                          }

controller_process_skull_stripping = {'safety_on'                   : False,
                                      'step_generate_output_folder' : True,
                                      'generate_mask_brain'         : True,
                                      'skull_strip_all'             : True,
                                      'adjust_V1'                   : True}


print '#### \nPipelines for subjects \n {} \n#### \n'.format(subjects)

for sj in subjects:

    # process_T1(sj, control=controller_process_T1)
    # process_DWI_fsl(sj, control=controller_process_DWI)
    generate_skull_stripped(sj, control=controller_process_skull_stripping)
