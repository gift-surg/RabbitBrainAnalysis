"""
Steps
1) ex_vivo_pre_processing pipeline for the selected subjects
2) manual in-plane reorientation : freesurfer. Saving the reorientation.

--- Barcelona template propagation
3) manual landmark based registration from the barcelona study - upsampled and smoothed - with slicer

--- DTI, FA, V1 elaborations
4) run dwi_analysis for the ex vivo for the selected subjects.
5) resample propagate the thresholded FA, and V1 as masks in the anatomical space

"""
import os
from os.path import join as jph
import numpy as np
import nibabel as nib

from tools.alignment.propagators import register_and_propagate_path
from definitions import root_2_subjects_study_2


###########
# manager #
###########

phase_1     = False
phase_1_bis = False
phase_2     = False
phase_3     = True
phase_4     = True

safety_on = False
suffix = '_affine_only'

#########
# input #
#########

subj_1305_pf   = jph(root_2_subjects_study_2, 'subj_1305.nii.gz')
subj_1702_pf   = jph(root_2_subjects_study_2, 'subj_1702.nii.gz')

av_ex_skull_pf = jph(root_2_subjects_study_2, 'av_ex_skull.nii.gz')
barc_template_pf = jph(root_2_subjects_study_2, 'barc_template.nii.gz')
barc_atlas_pf    = jph(root_2_subjects_study_2, 'barc_template_atlas.nii.gz')

dump_ph = os.path.join(root_2_subjects_study_2, 'dump')

###################################################################
# Phase 1: rigid register average ex-skull on subject 1305 - 1702 #
###################################################################

# output:

av_ex_skull_on_1305_rig_ph        = jph(root_2_subjects_study_2, 'av_ex_skull_on_1305_rig.nii.gz')
av_ex_skull_on_1305_rig_transf_ph = jph(root_2_subjects_study_2, 'av_ex_skull_on_1305_rig_transf.txt')

av_ex_skull_on_1702_rig_ph        = jph(root_2_subjects_study_2, 'av_ex_skull_on_1702_rig.nii.gz')
av_ex_skull_on_1702_rig_transf_ph = jph(root_2_subjects_study_2, 'av_ex_skull_on_1702_rig_transf.txt')


if phase_1:

    cmd_1305 = 'reg_aladin -ref {0} -flo {1} -res {2} -aff {3} -rigOnly '.format(subj_1305_pf,
                                                                                 av_ex_skull_pf,
                                                                                 av_ex_skull_on_1305_rig_ph,
                                                                                 av_ex_skull_on_1305_rig_transf_ph)

    cmd_1702 = 'reg_aladin -ref {0} -flo {1} -res {2} -aff {3} -rigOnly '.format(subj_1702_pf,
                                                                                 av_ex_skull_pf,
                                                                                 av_ex_skull_on_1702_rig_ph,
                                                                                 av_ex_skull_on_1702_rig_transf_ph)

    print cmd_1305
    print cmd_1702

    if not safety_on:
        os.system(cmd_1305)
        os.system(cmd_1702)


###################################################################
# Phase 1 bis: affine register average ex-skull on subject 1305 - 1702 #
###################################################################

# output:

av_ex_skull_on_1305_aff_ph        = jph(root_2_subjects_study_2, 'av_ex_skull_on_1305_aff.nii.gz')
av_ex_skull_on_1305_aff_transf_ph = jph(root_2_subjects_study_2, 'av_ex_skull_on_1305_aff_transf.txt')

av_ex_skull_on_1702_aff_ph        = jph(root_2_subjects_study_2, 'av_ex_skull_on_1702_aff.nii.gz')
av_ex_skull_on_1702_aff_transf_ph = jph(root_2_subjects_study_2, 'av_ex_skull_on_1702_aff_transf.txt')


if phase_1_bis:

    cmd_1305 = 'reg_aladin -ref {0} -flo {1} -res {2} -aff {3} '.format(
                                                                        subj_1305_pf,
                                                                        av_ex_skull_on_1305_rig_ph,
                                                                        av_ex_skull_on_1305_aff_ph,
                                                                        av_ex_skull_on_1305_aff_transf_ph)

    cmd_1702 = 'reg_aladin -ref {0} -flo {1} -res {2} -aff {3}  '.format(
                                                                         subj_1702_pf,
                                                                         av_ex_skull_on_1702_rig_ph,
                                                                         av_ex_skull_on_1702_aff_ph,
                                                                         av_ex_skull_on_1702_aff_transf_ph)

    print cmd_1305
    print cmd_1702

    if not safety_on:
        os.system(cmd_1305)
        os.system(cmd_1702)


#######################################################################
# Phase 2: non-rigid register average ex-skull on subject 1305 - 1702 #
#######################################################################
# From the rigid as it provides a better result.

av_ex_skull_on_1305_non_rig_ph        = jph(root_2_subjects_study_2, 'av_ex_skull_on_1305_non_rig.nii.gz')
av_ex_skull_on_1305_non_rig_transf_ph = jph(root_2_subjects_study_2, 'av_ex_skull_on_1305_non_rig_transf.nii.gz')

av_ex_skull_on_1702_non_rig_ph        = jph(root_2_subjects_study_2, 'av_ex_skull_on_1305_non_rig.nii.gz')
av_ex_skull_on_1702_non_rig_transf_ph = jph(root_2_subjects_study_2, 'av_ex_skull_on_1305_non_rig_transf.nii.gz')


if phase_2:

    cmd_1305 = 'reg_f3d -ref {0} -flo {1} -res {2} -cpp {3} -be 0.1 -vel '.format(
                                                                             subj_1305_pf,
                                                                             av_ex_skull_on_1305_rig_ph,
                                                                             av_ex_skull_on_1305_non_rig_ph,
                                                                             av_ex_skull_on_1305_non_rig_transf_ph)

    cmd_1702 = 'reg_f3d -ref {0} -flo {1} -res {2} -cpp {3} -be 0.1 -vel '.format(
                                                                              subj_1702_pf,
                                                                              av_ex_skull_on_1702_rig_ph,
                                                                              av_ex_skull_on_1702_non_rig_ph,
                                                                              av_ex_skull_on_1702_non_rig_transf_ph)

    print cmd_1305
    print cmd_1702

    if not safety_on:
        os.system(cmd_1305)
        os.system(cmd_1702)


#########################################################################
# Phase 3: propagate the barcelona template + atlas on the average skull
#  registered on each subject affine
#########################################################################

barc_template_on_av_on_1305_affine = jph(root_2_subjects_study_2, 'barc_template_on_av_on_1305_aff.nii.gz')
barc_atlas_on_av_on_1305_affine = jph(root_2_subjects_study_2, 'barc_atlas_on_av_on_1305_aff.nii.gz')


barc_template_on_av_on_1702_affine = jph(root_2_subjects_study_2, 'barc_template_on_av_on_1702_aff.nii.gz')
barc_atlas_on_av_on_1702_affine = jph(root_2_subjects_study_2, 'barc_atlas_on_av_on_1702_aff.nii.gz')


if phase_3:

    register_and_propagate_path(av_ex_skull_on_1305_rig_ph,
                                barc_template_pf,
                                barc_atlas_pf,
                                output_template_warped_path=barc_template_on_av_on_1305_affine,
                                output_template_atlas_warped_path=barc_atlas_on_av_on_1305_affine,
                                output_transformations_folder_path=dump_ph,
                                interpolation_order=0,
                                modality='affine',
                                safety_on=safety_on)

    register_and_propagate_path(av_ex_skull_on_1702_rig_ph,
                                barc_template_pf,
                                barc_atlas_pf,
                                output_template_warped_path=barc_template_on_av_on_1702_affine,
                                output_template_atlas_warped_path=barc_atlas_on_av_on_1702_affine,
                                output_transformations_folder_path=dump_ph,
                                interpolation_order=0,
                                modality='affine',
                                safety_on=safety_on)

#########################################################################
# Phase 3: propagate the barcelona template + atlas on the average skull
#  registered on each subject non-rigid
#########################################################################


barc_template_on_av_on_1305_non_rig = jph(root_2_subjects_study_2, 'barc_template_on_av_on_1305_non_rig.nii.gz')
barc_atlas_on_av_on_1305_non_rig = jph(root_2_subjects_study_2, 'barc_atlas_on_av_on_1305_non_rig.nii.gz')

barc_template_on_av_on_1702_non_rig = jph(root_2_subjects_study_2, 'barc_template_on_av_on_1702_non_rig.nii.gz')
barc_atlas_on_av_on_1702_non_rig = jph(root_2_subjects_study_2, 'barc_atlas_on_av_on_1702_non_rig.nii.gz')


if phase_4:

    register_and_propagate_path(av_ex_skull_on_1305_rig_ph,
                                barc_template_on_av_on_1305_affine,
                                barc_atlas_on_av_on_1305_affine,
                                output_template_warped_path=barc_template_on_av_on_1305_non_rig,
                                output_template_atlas_warped_path=barc_atlas_on_av_on_1305_non_rig,
                                output_transformations_folder_path=dump_ph,
                                interpolation_order=0,
                                modality='affine',
                                safety_on=safety_on)

    register_and_propagate_path(av_ex_skull_on_1702_rig_ph,
                                barc_template_on_av_on_1702_affine,
                                barc_atlas_on_av_on_1702_affine,
                                output_template_warped_path=barc_template_on_av_on_1702_non_rig,
                                output_template_atlas_warped_path=barc_atlas_on_av_on_1702_non_rig,
                                output_transformations_folder_path=dump_ph,
                                interpolation_order=0,
                                modality='affine',
                                safety_on=safety_on)


