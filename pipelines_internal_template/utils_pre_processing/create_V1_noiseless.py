import os
from os.path import join as jph

from tools.definitions import root_pilot_study
from tools.auxiliary.utils import reproduce_slice_fourth_dimension_path, print_and_run


subjects = ['1201', '1203', '1305', '1404', '1505', '1507', '1510', '1702', '1805', '2002']
# subjects = ['1203', '1404', '1505', '1507', '1510']


step = {'make folder'   : False,
        'get mask'      : False,
        'extend'        : False,
        'final'         : False,
        'delete folder' : True}

for sj in subjects:

    pfo_all_mod = jph(root_pilot_study, 'A_template_atlas_ex_vivo', sj, 'all_modalities')

    # input
    pfi_v1 = jph(pfo_all_mod, sj + '_V1.nii.gz')
    pfi_FA = jph(pfo_all_mod, sj + '_FA.nii.gz')
    pfi_segmentation = jph(root_pilot_study, 'A_template_atlas_ex_vivo', sj, 'segmentations', 'approved', sj + '_propagate_me.nii.gz')

    # intermediate
    pfo_v1_process = jph(pfo_all_mod, 'z_post_processing')
    pfi_v1_mask = jph(pfo_v1_process, sj + '_mask_from_segmentation.nii.gz')
    pfi_FA_3_layers = jph(pfo_v1_process, sj + '_FA_3_layers.nii.gz')
    pfi_v1_mask_3_layers = jph(pfo_v1_process, sj + '_maks_3_layers.nii.gz')

    # output
    pfo_v1_elaborated = jph(pfo_all_mod, sj + '_V1_noiseless.nii.gz')

    # verify input:
    for pfi in [pfi_v1, pfi_FA]:
        if not os.path.exists(pfi):
            raise IOError('Path {0} does not exists.'.format(pfi))

    # check if mask is there:
    segmentation_available = False
    if os.path.exists(pfi_segmentation):
        segmentation_available = True
        print 'Mask available for subject ' + sj
    else:
        print 'Mask NOT available for subject ' + sj

    print '\n\n Subject  {} \n\n'.format(sj)

    # PART 0 MAKE folder
    if step['make folder']:
        cmd_ = 'mkdir -p {}'.format(pfo_v1_process)
        print_and_run(cmd_, safety_on=False)

    # PART 1 get the mask from the tissue segmentation:
    if step['get mask']:
        if segmentation_available:

            cmd0 = 'seg_maths {0} -bin {1}'.format(pfi_segmentation, pfi_v1_mask)
            cmd1 = 'seg_maths {0} -fill {0}'.format(pfi_v1_mask)
            cmd2 = 'seg_maths {0} -smol 0.8 {0}'.format(pfi_v1_mask)

            print_and_run(cmd0, safety_on=False)
            print_and_run(cmd1, safety_on=False)
            print_and_run(cmd2, safety_on=False)

    # PART 2 obtain 3-layers FA and MASK:
    if step['extend']:
        if segmentation_available:
            reproduce_slice_fourth_dimension_path(pfi_v1_mask, pfi_v1_mask_3_layers, num_slices=3, repetition_axis=3)
        reproduce_slice_fourth_dimension_path(pfi_FA, pfi_FA_3_layers, num_slices=3, repetition_axis=3)

    # PART 3 multiply v1 times mask and times FA
    if step['final']:
        if segmentation_available:
            cmd3 = 'seg_maths {0} -mul {1} {2}'.format(pfi_v1, pfi_v1_mask_3_layers, pfo_v1_elaborated)
        else:
            cmd3 = 'cp {0} {1}'.format(pfi_v1, pfo_v1_elaborated)
        print_and_run(cmd3, safety_on=False)

        cmd4 = 'seg_maths {0} -mul {1} {0}'.format(pfo_v1_elaborated, pfi_FA_3_layers, pfo_v1_elaborated)
        print_and_run(cmd4, safety_on=False)

    # PART 4 eliminate intermediate folder

    if step['delete folder']:
        cmd = 'rm -r {}'.format(pfo_v1_process)
        print_and_run(cmd, safety_on=False)
