"""
Script to create the brain tissue multi atlas for the skull stripping
based on segmentation propagation and label fusion.
"""
import os
import pickle
from os.path import join as jph

from tools import definitions as defs
from LABelsToolkit.tools.aux_methods.utils import print_and_run
from LABelsToolkit.main import LABelsToolkit


def extract_brain_tissue_in_NI_multi_atlas():
    """
    From the existing multi-atlas with the parcellation, this method the binary mask for the brain tissue.
    This is performed for each subject.
    Multi-atlas considered is the one located at the global variable root_atlas
    :return:
    """

    for atlas_sj in defs.multi_atlas_subjects:

        print('Creating brain tissue for subject {} in NI multi atlas '.format(atlas_sj))

        pfi_segm = jph(defs.root_atlas, atlas_sj, 'segm', '{}_segm.nii.gz'.format(atlas_sj))
        assert os.path.exists(pfi_segm)

        pfi_brain_tissue = jph(defs.root_atlas, atlas_sj, 'masks', '{}_brain_tissue.nii.gz'.format(atlas_sj))

        print_and_run('cp {0} {1}'.format(pfi_segm, pfi_brain_tissue))

        cmd = 'seg_maths {0} -bin {0}; '   \
              'seg_maths {0} -dil 1 {0}; ' \
              'seg_maths {0} -fill {0}; '  \
              'seg_maths {0} -ero 1 {0} '.format(pfi_brain_tissue)

        print_and_run(cmd)


def create_brain_tissue_multi_atlas(sj_list, controller):

    for sj in sj_list:
        print('Adding subject {} to brain tissue multi atlas. \n'.format(sj))

        sj_parameters = pickle.load(open(jph(defs.pfo_subjects_parameters, sj), 'r'))

        study = sj_parameters['study']
        category = sj_parameters['category']

        root_sj = jph(defs.root_study_rabbits, 'A_data', study, category, sj)

        assert os.path.exists(root_sj)

        # input data:
        pfi_T1_sj   = jph(root_sj, 'mod', '{}_T1.nii.gz'.format(sj))
        pfi_T1_segm = jph(root_sj, 'segm', '{}_T1_segm.nii.gz'.format(sj))

        # copy to destination (BT = brain tissue multi atlas):

        root_sj_BT = jph(defs.root_atlas_BT, sj)
        if controller['Delete_first']:
            print_and_run('rm -r {}'.format(root_sj_BT), short_path_output=False)

        print_and_run('mkdir -p {}'.format(root_sj_BT))

        pfi_T1_sj_BT = jph(root_sj_BT, '{}_T1.nii.gz'.format(sj))
        pfi_brain_tissue_sj_BT = jph(root_sj_BT, '{}_brain_tissue.nii.gz'.format(sj))

        print_and_run('cp {0} {1}'.format(pfi_T1_sj, pfi_T1_sj_BT))
        print_and_run('cp {0} {1}'.format(pfi_T1_segm, pfi_brain_tissue_sj_BT))

        # Elaborate data in destination:
        # -- from segmentation to brain tissue:

        cmd = 'seg_maths {0} -bin {0}; '   \
              'seg_maths {0} -dil 1 {0}; ' \
              'seg_maths {0} -fill {0}; '  \
              'seg_maths {0} -ero 1 {0} '.format(pfi_brain_tissue_sj_BT)

        print_and_run(cmd)

        # -- from brain tissue to roi mask (dilated of the brain tissue):
        pfi_roi_mask_BT = jph(root_sj_BT, '{}_roi_mask.nii.gz'.format(sj))
        cmd1 = 'cp {} {}'.format(pfi_brain_tissue_sj_BT, pfi_roi_mask_BT)
        print_and_run(cmd1)

        cmd2 = 'seg_maths {0} -dil 3 {0}'.format(pfi_roi_mask_BT)
        print_and_run(cmd2)



def extract_brain_tissue_from_multi_atlas_list_stereotaxic(target_name,
                                                           multi_atlas_list,
                                                           pfo_tmp,
                                                           pfi_output_brain_mask,
                                                           options):
    """
    :param target_name:
    :param multi_atlas_list:
    :param pfo_tmp:
    :param pfi_output_brain_mask:
    :param options:
    :return:
    """
    # controller:
    affine_only = True
    nrig_options = ' -be 0.98 -jl 0.5 '
    steps = {'register'    : True,
             'propagate'   : True,
             'stack'       : True,
             'fuse'        : True}

    assert os.path.exists(pfo_tmp)

    # parameters target:
    sj_parameters = pickle.load(open(jph(defs.pfo_subjects_parameters, target_name), 'r'))

    study    = sj_parameters['study']
    category = sj_parameters['category']

    # input target:
    root_target_sj = jph(defs.root_study_rabbits, 'A_data', study, category, target_name)

    pfi_target_sj_T1        = jph(root_target_sj, 'stereotaxic', 'mod', '{}_T1.nii.gz'.format(target_name))
    pfi_target_sj_reg_mask  = jph(root_target_sj, 'stereotaxic', 'masks', '{}_T1_reg_mask.nii.gz'.format(target_name))

    assert os.path.exists(pfi_target_sj_T1), pfi_target_sj_T1
    assert os.path.exists(pfi_target_sj_reg_mask), pfi_target_sj_reg_mask

    # list of final intermediate output:
    list_pfi_brain_mask_registered_on_target = []
    list_pfi_T1_registered_on_target         = []

    for atlas_sj in multi_atlas_list:

        # input selected atlas_sj
        if atlas_sj in defs.multi_atlas_subjects:
            root_atlas_sj = jph(defs.root_atlas, atlas_sj)
            pfi_atlas_sj_T1         = jph(root_atlas_sj, 'mod', '{}_T1.nii.gz'.format(atlas_sj))
            pfi_atlas_sj_reg_mask   = jph(root_atlas_sj, 'masks', '{}_reg_mask.nii.gz'.format(atlas_sj))
            pfi_atlas_sj_brain_mask = jph(root_atlas_sj, 'masks', '{}_brain_mask.nii.gz'.format(atlas_sj))
        elif atlas_sj in defs.multi_atlas_BT_subjects:
            root_atlas_name_BT = jph(defs.root_atlas_BT, atlas_sj)
            pfi_atlas_sj_T1         = jph(root_atlas_name_BT, '{}_T1.nii.gz'.format(atlas_sj))
            pfi_atlas_sj_reg_mask   = jph(root_atlas_name_BT, '{}_reg_mask.nii.gz'.format(atlas_sj))
            pfi_atlas_sj_brain_mask = jph(root_atlas_name_BT, '{}_brain_mask.nii.gz'.format(atlas_sj))
        else:
            raise IOError('Subject {} is not in a known or provided multi-atlas.'.format(atlas_sj))

        assert os.path.exists(pfi_atlas_sj_T1),         pfi_atlas_sj_T1
        assert os.path.exists(pfi_atlas_sj_reg_mask),   pfi_atlas_sj_reg_mask
        assert os.path.exists(pfi_atlas_sj_brain_mask), pfi_atlas_sj_brain_mask

        # intermediate output: AFFINE
        pfi_affine_transformation_ref_on_subject = jph(pfo_tmp, 'target{}_floating{}_aff_transformation.txt'.format(target_name, atlas_sj))
        pfi_affine_warped_ref_on_subject         = jph(pfo_tmp, 'target{}_floating{}_aff_warped.nii.gz'.format(target_name, atlas_sj))

        # AFFINE step
        cmd = 'reg_aladin -ref {0} -rmask {1} -flo {2} -fmask {3} -aff {4} -res {5} -omp {6} -speeeeed '.format(
            pfi_target_sj_T1, pfi_target_sj_reg_mask, pfi_atlas_sj_T1, pfi_atlas_sj_reg_mask,
            pfi_affine_transformation_ref_on_subject,
            pfi_affine_warped_ref_on_subject,
            defs.num_cores_run)
        if steps['register']:
            print_and_run(cmd)

        pfi_final_transformation = pfi_affine_transformation_ref_on_subject

        # intermediate output: NON-RIGID
        pfi_nrig_cpp_ref_on_subject    = jph(pfo_tmp, 'target{}_floating{}_nrigid_cpp.nii.gz'.format(target_name, atlas_sj))
        pfi_nrig_warped_ref_on_subject = jph(pfo_tmp, 'target{}_floating{}_nrigid_warped.nii.gz'.format(target_name, atlas_sj))

        # NON-RIGID step
        if not affine_only:
            cmd = 'reg_f3d -ref {0} -rmask {1} -flo {2} -fmask {3} -aff {4} -cpp {5} -res {6} {7} -omp {8}'.format(
                pfi_target_sj_T1, pfi_target_sj_reg_mask,
                pfi_atlas_sj_T1, pfi_atlas_sj_reg_mask,
                pfi_affine_transformation_ref_on_subject,
                pfi_nrig_cpp_ref_on_subject,
                pfi_nrig_warped_ref_on_subject,
                nrig_options,
                defs.num_cores_run)
            if steps['register']:
                print_and_run(cmd)

            pfi_final_transformation = pfi_nrig_cpp_ref_on_subject

        print('- Propagate registration to brain tissue mask, subject {0} over the target {1}'.format(
            atlas_sj, target_name))

        # Output brain tissue after affine trasformation, must include the atlas_sj name in the naming.
        pfi_brain_tissue_from_multi_atlas_sj = jph(pfo_tmp, 'target{0}_floating{1}_final_warped_brain_mask.nii.gz'.format(
            target_name, atlas_sj))
        cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
            pfi_target_sj_T1,
            pfi_atlas_sj_brain_mask,
            pfi_final_transformation,
            pfi_brain_tissue_from_multi_atlas_sj)
        if steps['propagate']:
            print_and_run(cmd)

        # Append path to output files ot the respective lists.
        list_pfi_brain_mask_registered_on_target.append(pfi_brain_tissue_from_multi_atlas_sj)

        if affine_only:
            list_pfi_T1_registered_on_target.append(pfi_affine_warped_ref_on_subject)
        else:
            list_pfi_T1_registered_on_target.append(pfi_nrig_warped_ref_on_subject)

    print('\n- Create stack of the brain masks warped over the target {} and merge with MV. '.format(target_name))

    pfi_stack_brain_mask = jph(pfo_tmp, 'a_stack_brain_tissues_target{0}_multiAtlas{1}.nii.gz'.format(
        target_name, options['method']))
    pfi_stack_T1 = jph(pfo_tmp, 'a_stack_T1_target{0}_multiAtlas{1}.nii.gz'.format(
        target_name, options['method']))

    if steps['stack']:
        # Create stack of warped brain mask
        lt = LABelsToolkit()
        lt.manipulate_shape.stack_list_pfi_images(list_pfi_brain_mask_registered_on_target, pfi_stack_brain_mask)
        del lt

        # Create stack of warped T1
        lt = LABelsToolkit()
        lt.manipulate_shape.stack_list_pfi_images(list_pfi_T1_registered_on_target, pfi_stack_T1)
        del lt

    if steps['fuse']:
        print('\n\n-Labels Fusion')
        # merge the roi masks in one (Majority voting for now):
        cmd = 'seg_LabFusion -in {0} -out {1} -MV '.format(pfi_stack_brain_mask, pfi_output_brain_mask)
        # cmd = 'seg_LabFusion -in {0} -STEPS 3 5 {1} {2} -out {3}'.format(pfi_stack_brain_mask, pfi_target_sj_T1,
        #                                                                  pfi_stack_T1, pfi_output_brain_mask)
        print_and_run(cmd)
