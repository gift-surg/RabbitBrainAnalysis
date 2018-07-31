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

        cmd = 'seg_maths {0} -bin {0}; ' \
              'seg_maths {0} -dil 1 {0}; ' \
              'seg_maths {0} -fill {0}; ' \
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

        cmd = 'seg_maths {0} -bin {0}; ' \
              'seg_maths {0} -dil 1 {0}; ' \
              'seg_maths {0} -fill {0}; ' \
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
    # parameters target:

    # input target:
    pfi_target_sj_T1        = ''
    pfi_target_sj_reg_mask  = ''

    # list of final intermediate output:
    list_pfi_brain_mask_registered_on_target = []

    for atlas_sj in multi_atlas_list:

        # input selected atlas_sj
        if atlas_sj in defs.multi_atlas_subjects:
            pfi_atlas_sj_T1         = jph()
            pfi_atlas_sj_reg_mask   = jph()
            pfi_atlas_sj_brain_mask = jph()
        elif atlas_sj in defs.multi_atlas_BT_subjects:
            pfi_atlas_sj_T1         = jph()
            pfi_atlas_sj_reg_mask   = jph()
            pfi_atlas_sj_brain_mask = jph()
        else:
            raise IOError('subject {} is not in a known multi-atlas'.format(atlas_sj))

        assert os.path.exists(pfi_target_sj_T1),       pfi_target_sj_T1
        assert os.path.exists(pfi_target_sj_reg_mask), pfi_target_sj_reg_mask

        assert os.path.exists(pfi_atlas_sj_T1),         pfi_atlas_sj_T1
        assert os.path.exists(pfi_atlas_sj_reg_mask),   pfi_atlas_sj_reg_mask
        assert os.path.exists(pfi_atlas_sj_brain_mask), pfi_atlas_sj_brain_mask

        # intermediate output: AFFINE
        pfi_affine_transformation_ref_on_subject = jph()
        pfi_affine_warped_ref_on_subject         = jph()

        # AFFINE step
        cmd = 'reg_aladin -ref {0} -rmask {1} -flo {2} -fmask {3} -aff {4} -res {5} -omp {6} -speeeeed '.format(
            pfi_target_sj_T1,
            pfi_target_sj_reg_mask,
            pfi_atlas_sj_T1,
            pfi_atlas_sj_reg_mask,
            pfi_affine_transformation_ref_on_subject,
            pfi_affine_warped_ref_on_subject,
            defs.num_cores_run)
        print_and_run(cmd)

        # intermediate output: NON-RIGID
        pfi_nrig_cpp_ref_on_subject    = jph()
        pfi_nrig_warped_ref_on_subject = jph()

        # NON-RIGID step
        cmd = 'reg_f3d -ref {0} -rmask {1} -flo {2} -fmask {3} -aff {4} -cpp {5} -res {6} -omp'

        print_and_run(cmd)

        print('- Propagate registration to brain tissue mask, subject {} over the target {}'.format(atlas_sj, target_name))

        # Output brain tissue after affine trasformation, must include the atlas_sj name in the naming.
        pfi_brain_tissue_from_multi_atlas_sj = jph(pfo_tmp, '{0}_T1_brain_tissue_from_atlas{1}.nii.gz'.format(
            target_name, atlas_sj))
        cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
            pfi_target_sj_T1,
            pfi_atlas_sj_brain_mask,
            pfi_nrig_cpp_ref_on_subject,
            pfi_brain_tissue_from_multi_atlas_sj)
        print_and_run(cmd)

        list_pfi_brain_mask_registered_on_target.append(pfi_brain_tissue_from_multi_atlas_sj)

    print('- Create stack over the target {} and merge with MV. '.format(target_name))

    pfi_stack_brain_tissue = jph(pfo_tmp, '{0}_T1_brain_tissues_from_all_multi_atlas_{1}_stack.nii.gz'.format(
        target_name, options['roi_mask']))

    lt = LABelsToolkit()
    lt.manipulate_shape.stack_list_pfi_images(list_pfi_brain_mask_registered_on_target, pfi_stack_brain_tissue)

    # merge the roi masks in one:
    cmd = 'seg_LabFusion  -in {0} -out {1} -MV '.format(pfi_stack_brain_tissue, pfi_output_brain_mask)
    print_and_run(cmd)


def extract_brain_tissue_from_multi_atlas(target_name,
                                          pfi_target_T1,
                                          pfi_output_brain_mask,
                                          options,
                                          pfi_target_pre_mask=None,
                                          pfo_tmp='.z_tmp', alpha=0):
    """
    ---
    OLD  moved in stereotaxic coordinates in the new version:
     extract_brain_tissue_from_multi_atlas_list_stereotaxic
    ---
    sj: subjects in the multi-atlas. Target: element to be segmented.
    The multi atlas can ben the main one or a customised one!
    :param target_name:
    :param pfi_target_T1:
    :param pfi_output_brain_mask:
    :param pfi_target_pre_mask:
    :param pfo_tmp:
    :param alpha: angle to rotate the sj in the template
    :return:
    """
    pri_target_param = jph(defs.pfo_subjects_parameters, target_name)

    if options['modality'] == 'MA':
        mutli_atlas_subject_list = defs.multi_atlas_subjects
    elif options['modality'] == 'BTMA':
        mutli_atlas_subject_list = defs.multi_atlas_BT_subjects
    elif options['modality'] == 'BTMA_MA' or options['modality'] == 'MA_BTMA':
        mutli_atlas_subject_list = defs.multi_atlas_BT_subjects + defs.multi_atlas_subjects
    else:
        raise IOError

    list_brain_mask_registered_on_target = []

    for sj in mutli_atlas_subject_list:

        pfi_sj_T1_hd_oriented = jph(pfo_tmp, '{}_T1_header_oriented_on_{}.nii.gz'.format(sj, target_name))
        pfi_sj_brain_tissue_hd_oriented = jph(pfo_tmp, '{}_brain_tissue_header_oriented_on_{}.nii.gz'.format(sj, target_name))
        pfi_sj_roi_hd_oriented = jph(pfo_tmp, '{}_roi_mask_header_oriented_on_{}.nii.gz'.format(sj, target_name))
        pfi_sj_reg_hd_oriented = jph(pfo_tmp, '{}_reg_mask_header_oriented_on_{}.nii.gz'.format(sj, target_name))

        print('- Orient header subject {} over the target {}'.format(sj, target_name))
        
        if options['roi_mask'] == 'MA':
            pfi_sj_T1           = jph(defs.root_atlas, sj, 'mod', '{}_T1.nii.gz'.format(sj))
            pfi_sj_brain_tissue = jph(defs.root_atlas, sj, 'masks', '{}_brain_tissue.nii.gz'.format(sj))
            pfi_sj_roi          = jph(defs.root_atlas, sj, 'masks', '{}_roi_mask.nii.gz'.format(sj))
            pfi_sj_reg          = jph(defs.root_atlas, sj, 'masks', '{}_reg_mask.nii.gz'.format(sj))

            lm = LABelsToolkit()
            lm.header.apply_small_rotation(pfi_sj_T1, pfi_sj_T1_hd_oriented,
                                           angle=alpha, principal_axis='pitch')
            lm.header.apply_small_rotation(pfi_sj_brain_tissue, pfi_sj_brain_tissue_hd_oriented,
                                           angle=alpha, principal_axis='pitch')
            lm.header.apply_small_rotation(pfi_sj_roi, pfi_sj_roi_hd_oriented,
                                           angle=alpha, principal_axis='pitch')
            lm.header.apply_small_rotation(pfi_sj_reg, pfi_sj_reg_hd_oriented,
                                           angle=alpha, principal_axis='pitch')

            if options['slim']:
                pfi_reg_mask_for_registration_sj = jph(pfo_tmp, '{}_over_{}_reg_mask_for_reg_hd_oriented_slim.nii.gz'.format(sj, target_name))
                    
                cmd = 'seg_maths {0} -mul {1} {2}'.format(pfi_sj_brain_tissue_hd_oriented,
                                                          pfi_sj_reg_hd_oriented,
                                                          pfi_reg_mask_for_registration_sj)
            else:
                pfi_reg_mask_for_registration_sj = jph(pfo_tmp,
                                                       '{}_over_{}_reg_mask_for_reg_hd_oriented_slim.nii.gz'.format(sj, target_name))
            
                cmd = 'seg_maths {0} -mul {1} {2}'.format(pfi_sj_roi_hd_oriented,
                                                          pfi_sj_reg_hd_oriented,
                                                          pfi_reg_mask_for_registration_sj)
            print_and_run(cmd)

        elif options['roi_mask'] == 'BTMA':
            
            pfi_sj_T1           = jph(defs.root_atlas_BT, sj, '{}_T1.nii.gz'.format(sj))
            pfi_sj_brain_tissue = jph(defs.root_atlas_BT, sj, '{}_brain_tissue.nii.gz'.format(sj))
            pfi_sj_roi          = jph(defs.root_atlas_BT, sj, '{}_roi_mask.nii.gz'.format(sj))

            assert os.path.exists(pfi_sj_T1), pfi_sj_T1
            assert os.path.exists(pfi_sj_brain_tissue), pfi_sj_brain_tissue
            assert os.path.exists(pfi_sj_roi), pfi_sj_roi

            lm = LABelsToolkit()
            lm.header.apply_small_rotation(pfi_sj_T1, pfi_sj_T1_hd_oriented,
                                           angle=alpha, principal_axis='pitch')
            lm.header.apply_small_rotation(pfi_sj_brain_tissue, pfi_sj_brain_tissue_hd_oriented,
                                           angle=alpha, principal_axis='pitch')
            lm.header.apply_small_rotation(pfi_sj_roi, pfi_sj_roi_hd_oriented,
                                           angle=alpha, principal_axis='pitch')
            if options['slim']:
                pfi_reg_mask_for_registration_sj = pfi_sj_brain_tissue_hd_oriented
            else:
                pfi_reg_mask_for_registration_sj = pfi_sj_roi_hd_oriented
        else:
            raise IOError

        print('- Register subject {} over the target {}'.format(sj, target_name))
        pfi_affine_transformation_ref_on_subject = jph(pfo_tmp, 'aff_ref_{0}_on_{1}.txt'.format(target_name, sj))
        pfi_3d_warped_ref_on_subject = jph(pfo_tmp, 'warp_ref_{0}_on_{1}.nii.gz'.format(target_name, sj))

        if pfi_target_pre_mask is None:
            cmd = 'reg_aladin -ref {0} -flo {1} -fmask {2} -aff {3} -res {4} -omp {5} -speeeeed '.format(
                pfi_target_T1,
                pfi_sj_T1_hd_oriented,
                pfi_reg_mask_for_registration_sj,
                pfi_affine_transformation_ref_on_subject,
                pfi_3d_warped_ref_on_subject,
                defs.num_cores_run)
            print cmd

        else:
            cmd = 'reg_aladin -ref {0} -rmask {1} -flo {2} -fmask {3} -aff {4} -res {5} -omp {6} -speeeeed '.format(
                pfi_target_T1,
                pfi_target_pre_mask,
                pfi_sj_T1_hd_oriented,
                pfi_reg_mask_for_registration_sj,
                pfi_affine_transformation_ref_on_subject,
                pfi_3d_warped_ref_on_subject,
                defs.num_cores_run)
            print cmd

        print_and_run(cmd)

        print('- Propagate registration to brain tissue mask, subject {} over the target {}'.format(sj, target_name))

        pfi_brain_tissue_from_multi_atlas_sj = jph(pfo_tmp, '{0}_T1_brain_tissue_from_atlas{1}.nii.gz'.format(
            target_name, sj))
        cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3} -inter 0'.format(
            pfi_target_T1,
            pfi_sj_brain_tissue_hd_oriented,
            pfi_affine_transformation_ref_on_subject,
            pfi_brain_tissue_from_multi_atlas_sj)
        print_and_run(cmd)

        list_brain_mask_registered_on_target.append(pfi_brain_tissue_from_multi_atlas_sj)

    print('- Create stack over the target {} and merge with MV. '.format(target_name))

    pfi_stack_brain_tissue = jph(pfo_tmp, '{0}_T1_brain_tissues_from_all_multi_atlas_{1}_stack.nii.gz'.format(
        target_name, options['roi_mask']))

    lt = LABelsToolkit()
    lt.manipulate_shape.stack_list_pfi_images(list_brain_mask_registered_on_target, pfi_stack_brain_tissue)

    # merge the roi masks in one:
    # output_brain_mask = jph(pfo_tmp, sj + '_T1_brain_tissue_MV.nii.gz')
    cmd = 'seg_LabFusion  -in {0} -out {1} -MV '.format(pfi_stack_brain_tissue, pfi_output_brain_mask)
    print_and_run(cmd)


def local_experiments():

    if False:

        if False:
            extract_brain_tissue_in_NI_multi_atlas()

        if False:
            controller_creator = {'Delete_first' : True}
            create_brain_tissue_multi_atlas(defs.multi_atlas_BT_subjects, controller_creator)

        if True:
            target_name_ = 'tt5007'
            pfi_target_T1_ = '/Volumes/sebastianof/rabbits/A_MultiAtlas_BT/tt5007/tt5007_T1.nii.gz'
            output_brain_mask_ = '/Volumes/sebastianof/rabbits/A_MultiAtlas_BT/tt5007/z_tmp/A_brain_mask.nii.gz'
            pfo_tmp_ = '/Volumes/sebastianof/rabbits/A_MultiAtlas_BT/tt5007/z_tmp'

            extract_brain_tissue_from_multi_atlas(target_name_, pfi_target_T1_, output_brain_mask_,
                                                  pfi_target_pre_mask=None,
                                                  pfo_tmp=pfo_tmp_, alpha=0)


    if False:

        root_atlas_special = jph(defs.root_study_rabbits, 'A_MultiAtlas_BT_new')
        assert os.path.exists(root_atlas_special)
        for sj in ['2503', '2608', '2702', '4504', '4903', '4905', '5001', '5007']:

            print('Creating brain tissue for subject {} in NI multi atlas '.format(sj))

            pfi_segm = jph(root_atlas_special, sj, '{}_segm.nii.gz'.format(sj))
            assert os.path.exists(pfi_segm)

            pfi_brain_tissue = jph(root_atlas_special, sj, '{}_brain_mask.nii.gz'.format(sj))

            print_and_run('cp {0} {1}'.format(pfi_segm, pfi_brain_tissue))

            cmd = 'seg_maths {0} -bin {0}; ' \
                  'seg_maths {0} -dil 1 {0}; ' \
                  'seg_maths {0} -fill {0}; ' \
                  'seg_maths {0} -ero 1 {0} '.format(pfi_brain_tissue)

            print_and_run(cmd)

if __name__ == '__main__':
    local_experiments()