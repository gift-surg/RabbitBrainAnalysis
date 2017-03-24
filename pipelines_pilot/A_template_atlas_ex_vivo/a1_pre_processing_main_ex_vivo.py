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

from pipelines_pilot.A_template_atlas_ex_vivo.pre_process_T1_ex_vivo import process_T1
from pipelines_pilot.A_template_atlas_ex_vivo.pre_process_DWI_fsl_ex_vivo_new import process_DWI_fsl


# all:
# subjects = ['1201', '1203', '1305', '1404', '1505', '1507', '1510', '1702', '1805', '2002']

# subjects = ['1305', '1404', '1505', '1507', '1510', '1702', '1805', '2002']
# subjects = ['1201', '1203', '1305', '1404', '1505', '1507', '1702', '1805', '2002']

subjects = ['2002', ]  # '1805', '2002'

controller_process_T1 = {'safety_on':                     False,
                         'step_generate_output_folder':   False,
                         'step_reorient':                 False,
                         'step_thr':                      False,
                         'step_register_masks':           False,
                         'step_cut_masks':                False,
                         'step_bfc':                      False,
                         'step_orient_histological':      True,
                         'step_compute_lesion_masks':     True,
                         'step_compute_reg_masks':        True,
                         'step_save_results':             True,
                         'step_save_bicommissural':       True,
                         'delete_intermediate_steps':     False}

controller_process_DWI = {'safety_on':                     False,
                          'step_generate_output_folder':   False,
                          'step_squeeze':                  False,
                          'step_extract_bval_bvect_slope': False,
                          'step_extract_first_timepoint':  False,
                          'step_grab_the_roi_mask':        False,
                          'step_dilate_mask':              False,
                          'step_cut_to_mask_dwi':          False,
                          'step_correct_the_slope':        False,
                          'step_eddy_current_corrections': False,
                          'step_dwi_analysis_with_fsl':    False,
                          'step_orient_directions_bicomm': False,
                          'step_set_header_histo'        : True,
                          'step_orient_histo':             True,
                          'step_final_adjustment':         True,
                          'step_bfc_b0':                   False,
                          'step_save_results_histo':       False,
                          'delete_intermediate_steps':     False
                          }

print '#### \nPipelines for subjects \n {} \n#### \n'.format(subjects)
print subjects
print controller_process_T1
print controller_process_DWI


for sj in subjects:
    # process_T1(sj, control=controller_process_T1)
    process_DWI_fsl(sj, control=controller_process_DWI)
    pass
