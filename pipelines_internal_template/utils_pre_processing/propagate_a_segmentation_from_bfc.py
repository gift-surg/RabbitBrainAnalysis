import os
from os.path import join as jph
from definitions import root_pilot_study

from tools.auxiliary.utils import print_and_run

from pipelines_internal_template.A_template_atlas_in_vivo_prelim.a_definitions_regions_subjects import subjects


steps_map = {'Aff alignment'                  : True,
             'Propagate to template aff'      : True,
             'Get differential BFC'           : True,
             'N-rig alignment of BFC'         : True,
             'Propagate to template n-rig'    : True,
             'Create output folder'           : True,
             'Smooth result'                  : True}

safety_on = False

pfo_main = '/Users/sebastiano/Desktop/test_in_vivo_template2'

# input
pfi_subject      = jph(pfo_main, '1504_t1_T1.nii.gz')
pfi_subject_mask = jph(pfo_main, '1504_t1_dummy_mask.nii.gz')
pfi_template     = jph(pfo_main, '1305_prelim_templ.nii.gz')
pfi_atlas        = jph(pfo_main, '1305_propagate_me.nii.gz')
pfi_mask         = jph(pfo_main, '1305_roi_mask.nii.gz')

# intermediate
pfo_dump = jph(pfo_main, 'dump')
pfi_affine_transf            = jph(pfo_dump, 'affine_transf.txt')
pfi_affine_res               = jph(pfo_dump, 'affine_warped.nii.gz')
pfi_atlas_affine_registered  = jph(pfo_dump, 'affine_atlas_propagated.nii.gz')
pfi_diff_bfc_template        = jph(pfo_dump, 'bfc_template.nii.gz')
pfi_diff_bfc_subject         = jph(pfo_dump, 'bfc_subject.nii.gz')
pfi_diff_bfc_n_rig_cpp       = jph(pfo_dump, 'bfc_cpp.nii.gz')
pfi_diff_bfc_n_rig_res       = jph(pfo_dump, 'bfc_res.nii.gz')

# output
pfo_results = jph(pfo_main, 'results')
pfi_propagated_prelim_templ = jph(pfo_results, 'atlas_propagated.nii.gz')

# check input
list_pfi_input = [pfi_subject, pfi_subject_mask, pfi_template, pfi_atlas, pfi_mask]
for p in list_pfi_input:
    if not os.path.exists(p):
        raise IOError('Argh!!')


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
    pfi_affine_res, pfi_subject_mask,              pfi_diff_bfc_template,
    pfi_subject,    pfi_subject_mask,              pfi_diff_bfc_subject)

    print_and_run(cmd, safety_on=safety_on)

if steps_map['N-rig alignment of BFC']:

    cmd = 'reg_f3d -ref {0} -flo {1} -cpp {2} -res {3} -be 0.8 -ln 2 -maxit 250'.format(
        pfi_diff_bfc_subject, pfi_diff_bfc_template,
        pfi_diff_bfc_n_rig_cpp, pfi_diff_bfc_n_rig_res)

    print_and_run(cmd, safety_on=safety_on)

if steps_map['Propagate to template n-rig']:

        cmd = 'reg_resample -ref {0} -flo {1} -cpp {2} -res {3} -inter 0'.format(
                 pfi_subject, pfi_atlas_affine_registered, pfi_diff_bfc_n_rig_cpp, pfi_propagated_prelim_templ)

        print_and_run(cmd, safety_on=safety_on)