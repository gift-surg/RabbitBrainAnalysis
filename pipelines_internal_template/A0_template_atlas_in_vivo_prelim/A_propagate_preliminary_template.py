"""
Propagate the preliminary template over all the subjects:
STEPS:
    1) Initial affine registration sj on template.
    2) Propagate atlas on sj.
    3)
"""
import os
from os.path import join as jph

from tools.auxiliary.utils import print_and_run
from tools.definitions import root_pilot_study_dropbox

subjects = ['0802_t1', '0904_t1', '1501_t1', '1504_t1', '1508_t1', '1509_t1', '1511_t1']

pfo_root_main = jph(root_pilot_study_dropbox, 'A_template_atlas_in_vivo')

pfi_template = jph(pfo_root_main, 'Utils', 'preliminary_template', 'in_vivo_template.nii.gz')
pfi_atlas = jph(pfo_root_main, 'Utils', 'preliminary_template', 'in_vivo_atlas_roi.nii.gz')
pfi_dummy_mask = jph(pfo_root_main, 'Utils', 'preliminary_template', 'in_vivo_dummy_mask.nii')

# where to store the intermediate results:
pfo_propagation_data = jph(pfo_root_main, 'Utils', 'preliminary_template', 'propagation_data')


safety_on = False

for sj in subjects:

    print '\n######################\n'
    print 'Pipeline started for subject ' + sj
    print '\n######################\n\n\n'

    # input:
    pfi_subject = jph(root_pilot_study_dropbox, 'A_template_atlas_in_vivo', sj,
                      'all_modalities', sj + '_T1.nii.gz')

    # intermediate steps paths:
    # Step Aff alignment
    pfi_affine_transf = jph(pfo_propagation_data, sj + '_ref_0802_flo_aff.txt')
    pfi_affine_res = jph(pfo_propagation_data, sj + '_ref_0802_flo_aff.nii.gz')
    # Step 1bis
    # pfi_1305_roi_mask_on_subject = jph(pfo_propagation_data, sj + '_1305_roi_registration_mask_on_sj.nii.gz')
    # Step Propagate to template aff:
    pfi_atlas_affine_registered = jph(pfo_propagation_data, sj + '_atlas_affine_registered_on_sj.nii.gz')
    # Step Manipulate registration mask:

    # Step Get differential BFC
    pfi_diff_bfc_0802 = jph(pfo_propagation_data, sj + '_z_bfc_0802.nii.gz')
    pfi_diff_bfc_sj = jph(pfo_propagation_data, sj + '_z_bfc_sj.nii.gz')

    # Step alignment of the BFC corrected:
    pfi_diff_bfc_n_rig_cpp = jph(pfo_propagation_data, sj + '_z_bfc_0802_on_bfc_sj_nrig_cpp.nii.gz')
    pfi_diff_bfc_n_rig_res = jph(pfo_propagation_data, sj + '_z_bfc_0802_on_bfc_sj_nrig.nii.gz')

    # output folder:
    pfo_atuomatic_segmentation = jph(root_pilot_study_dropbox, 'A_template_atlas_in_vivo', sj, 'segmentations',
                                     'automatic')
    # output data:
    test_tag = '_t1'  # t1 :  -be 0.8 -ln 2 -maxit 250 no mask (same as t3_reg_mask temporary...)
    pfi_propagated_prelim_templ = jph(root_pilot_study_dropbox, 'A_template_atlas_in_vivo', sj,
                           'segmentations', 'automatic', 'prelim_' + sj + '_template' + test_tag + '.nii.gz')

    # Step smooth result
    pfi_propagated_prelim_templ_smol = jph(root_pilot_study_dropbox, 'A_template_atlas_in_vivo', sj,
                           'segmentations', 'automatic', 'prelim_' + sj + '_template_smol' + test_tag + '.nii.gz')

    """ Steps manager """

    steps_map = {'Aff alignment'                  : True,
                 'Propagate to template aff'      : True,
                 'Get differential BFC'           : True,
                 'N-rig alignment of BFC'         : True,
                 'Propagate to template n-rig'    : True,
                 'Create output folder'           : True,
                 'Smooth result'                  : True}

    """ PIPELINE   """

    if steps_map['Aff alignment']:

        cmd = 'reg_aladin -ref {0} -flo {1} -aff {2} -res {3} '.format(
               pfi_subject, pfi_template, pfi_affine_transf, pfi_affine_res)

        print_and_run(cmd, safety_on=safety_on)

    if steps_map['Propagate to template aff']:

        cmd = 'reg_resample -ref {0} -flo {1} -aff {2} -res {3} -inter 0'.format(
                 pfi_subject, pfi_atlas, pfi_affine_transf, pfi_atlas_affine_registered)

        print_and_run(cmd, safety_on=safety_on)

    if steps_map['Get differential BFC']:

        bfc_corrector_cmd = '/Applications/niftk-16.1.0/NiftyView.app/Contents/MacOS/niftkMTPDbc '
        cmd = bfc_corrector_cmd + ' {0} {1} {2} {3} {4} {5} '.format(
        pfi_affine_res, pfi_dummy_mask,              pfi_diff_bfc_0802,
        pfi_subject,    pfi_dummy_mask, pfi_diff_bfc_sj)

        print_and_run(cmd, safety_on=safety_on)

    if steps_map['N-rig alignment of BFC']:

        cmd = 'reg_f3d -ref {0} -flo {1} -cpp {2} -res {3} -be 0.8 -ln 2 -maxit 250'.format(
            pfi_diff_bfc_sj, pfi_diff_bfc_0802,
            pfi_diff_bfc_n_rig_cpp, pfi_diff_bfc_n_rig_res)

        print_and_run(cmd, safety_on=safety_on)

    if steps_map['Create output folder']:
        cmd = 'mkdir -p {} '.format(pfo_atuomatic_segmentation)
        os.system(cmd)

    if steps_map['Propagate to template n-rig']:

        cmd = 'reg_resample -ref {0} -flo {1} -cpp {2} -res {3} -inter 0'.format(
                 pfi_subject, pfi_atlas_affine_registered, pfi_diff_bfc_n_rig_cpp, pfi_propagated_prelim_templ)

        print_and_run(cmd, safety_on=safety_on)

    if steps_map['Smooth result']:

        cmd = 'seg_maths {0} -smol 1 {1}'.format(pfi_propagated_prelim_templ, pfi_propagated_prelim_templ_smol)

        print_and_run(cmd, safety_on=safety_on)

    print '\n######################\n'
    print 'Pipeline terminated for subject ' + sj
    print '\n######################\n\n\n'
