"""
Propagate the preliminary template over all the subjects:
STEPS:
    1) Initial affine registration sj on template.
    2) Propagate atlas on sj.
    3)
"""
from os.path import join as jph

from pipelines_internal_template.A_template_atlas_ex_vivo_prelim.a_definitions_regions_subjects import subjects

from tools.auxiliary.utils import print_and_run
from tools.definitions import root_pilot_study

pfo_preliminary = jph(root_pilot_study, 'A_template_atlas_ex_vivo', 'Preliminary')
pfo_template_atlas_prelim = jph(pfo_preliminary, 'template_atlas_subregions')
pfo_propagation_data = jph(pfo_preliminary, 'data_propagations')

pfi_template_anatomy = jph(pfo_template_atlas_prelim, '1305_prelim_templ.nii.gz')
pfi_template_atlas = jph(pfo_template_atlas_prelim, '1305_prelim_templ_atlas.nii.gz')
pfi_roi_mask = jph(pfo_template_atlas_prelim, '1305_roi_mask.nii.gz')


safety_on = False

for sj in subjects:

    print '\n######################\n'
    print 'Pipeline started for subject ' + sj
    print '\n######################\n\n\n'

    # input:
    pfi_subject = jph(root_pilot_study, 'A_template_atlas_ex_vivo', sj,
                      'all_modalities', sj + '_T1.nii.gz')

    pfi_subject_roi_masks = jph(root_pilot_study, 'A_template_atlas_ex_vivo', sj,
                           'masks', sj + '_roi_mask.nii.gz')

    pfi_subject_roi_registration_masks = jph(root_pilot_study, 'A_template_atlas_ex_vivo', sj,
                           'masks', sj + '_roi_registration_mask.nii.gz')

    # intermediate steps paths:
    # Step Aff alignment
    pfi_affine_transf = jph(pfo_propagation_data, sj + '_ref_1305_flo_aff.txt')
    pfi_affine_res = jph(pfo_propagation_data, sj + '_ref_1305_flo_aff.nii.gz')
    # Step 1bis
    # pfi_1305_roi_mask_on_subject = jph(pfo_propagation_data, sj + '_1305_roi_registration_mask_on_sj.nii.gz')
    # Step Propagate to template aff:
    pfi_atlas_affine_registered = jph(pfo_propagation_data, sj + '_atlas_affine_registered_on_sj.nii.gz')
    # Step Manipulate registration mask:

    # Step Get differential BFC
    pfi_diff_bfc_1305 = jph(pfo_propagation_data, sj + '_z_bfc_1305.nii.gz')
    pfi_diff_bfc_sj = jph(pfo_propagation_data, sj + '_z_bfc_sj.nii.gz')

    # Step alignment of the BFC corrected:
    pfi_diff_bfc_n_rig_cpp = jph(pfo_propagation_data, sj + '_z_bfc_1305_on_bfc_sj_nrig_cpp.nii.gz')
    pfi_diff_bfc_n_rig_res = jph(pfo_propagation_data, sj + '_z_bfc_1305_on_bfc_sj_nrig.nii.gz')

    # output:
    test_tag = '_t3_reg_mask'  # t2 be 0.9 , t3 be 0.8
    pfi_propagated_prelim_templ = jph(root_pilot_study, 'A_template_atlas_ex_vivo', sj,
                           'segmentations', 'automatic', 'prelim_' + sj + '_template' + test_tag + '.nii.gz')

    # Step smooth result
    pfi_propagated_prelim_templ_smol = jph(root_pilot_study, 'A_template_atlas_ex_vivo', sj,
                           'segmentations', 'automatic', 'prelim_' + sj + '_template_smol' + test_tag + '.nii.gz')

    """ Steps manager """

    steps_map = {'Aff alignment'                  : False,
                 'Propagate to template aff'      : False,
                 'Manipulate registration mask'   : False,
                 'Get differential BFC'           : False,
                 'N-rig alignment of BFC'         : True,
                 'Propagate to template n-rig'    : True,
                 'Smooth result'                  : True}

    """ PIPELINE   """

    if steps_map['Aff alignment']:

        cmd = 'reg_aladin -ref {0} -rmask {1} -flo {2} -fmask {3} -aff {4} -res {5} '.format(
               pfi_subject, pfi_subject_roi_registration_masks,
               pfi_template_anatomy, pfi_roi_mask, pfi_affine_transf, pfi_affine_res)

        print_and_run(cmd, safety_on=safety_on)

    if steps_map['Propagate to template aff']:

        cmd = 'reg_resample -ref {0} -flo {1} -aff {2} -res {3} -inter 0'.format(
                 pfi_subject, pfi_template_atlas, pfi_affine_transf, pfi_atlas_affine_registered)

        print_and_run(cmd, safety_on=safety_on)

    if steps_map['Manipulate registration mask']:
        pass

    if steps_map['Get differential BFC']:

        bfc_corrector_cmd = '/Applications/niftk-16.1.0/NiftyView.app/Contents/MacOS/niftkMTPDbc '
        cmd = bfc_corrector_cmd + ' {0} {1} {2} {3} {4} {5} '.format(
        pfi_affine_res, pfi_subject_roi_masks,              pfi_diff_bfc_1305,
        pfi_subject,    pfi_subject_roi_registration_masks, pfi_diff_bfc_sj)

        print_and_run(cmd, safety_on=safety_on)

    if steps_map['N-rig alignment of BFC']:

        cmd = 'reg_f3d -ref {0} -rmask {1} -flo {2} -fmask {3} -cpp {4} -res {5} -be 0.8 -ln 2 -maxit 250'.format(
            pfi_diff_bfc_sj, pfi_subject_roi_registration_masks, pfi_diff_bfc_1305, pfi_roi_mask,  # Correct here!!
            pfi_diff_bfc_n_rig_cpp, pfi_diff_bfc_n_rig_res)

        print_and_run(cmd, safety_on=safety_on)

    if steps_map['Propagate to template n-rig']:

        cmd = 'reg_resample -ref {0} -flo {1} -cpp {2} -res {3} -inter 0'.format(
                 pfi_subject, pfi_atlas_affine_registered, pfi_diff_bfc_n_rig_cpp, pfi_propagated_prelim_templ)

        print_and_run(cmd, safety_on=safety_on)

    if steps_map['Smooth result']:

        cmd = 'seg_maths {0} -smol 1.5 {1}'.format(pfi_propagated_prelim_templ, pfi_propagated_prelim_templ_smol)

        print_and_run(cmd, safety_on=safety_on)

    print '\n######################\n'
    print 'Pipeline terminated for subject ' + sj
    print '\n######################\n\n\n'
