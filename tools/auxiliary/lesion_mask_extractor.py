import os
import numpy as np

from tools.auxiliary.connected_components import filter_connected_components_by_volume_path


def simple_lesion_mask_extractor_path(im_input_path, im_output_path, im_mask_foreground_path, safety_on=False):
    cmd = '''seg_maths {0} -thr 500 {1};
             seg_maths {1} -bin {1};
             seg_maths {1} -add {2} {1};
             seg_maths {1} -replace 2 0 {1};
             seg_maths {1} -fill {1};
             seg_maths {1} -dil 2 {1};
             seg_maths {1} -ero 2 {1};
             seg_maths {1} -smol 1.2 {1};
             seg_maths {1} -dil 1 {1};
             seg_maths {1} -mul {2} {1};
          '''.format(im_input_path, im_output_path, im_mask_foreground_path)

    print cmd

    if not safety_on:
        os.system(cmd)


def lesion_masks_extractor_cc_based_path(im_input_path, im_output_path, im_mask_foreground_path, safety_on=False):
    """
    Lesion masks are extracted before filtering for connected components.
    :return:
    """
    save_intermediate = True
    cmd1 = '''seg_maths {0} -thr 500 {1};
             seg_maths {1} -bin {1};
             seg_maths {1} -add {2} {1};
             seg_maths {1} -replace 2 0 {1};
             seg_maths {1} -fill {1};
             seg_maths {1} -dil 2 {1};
             seg_maths {1} -ero 2 {1};
             seg_maths {1} -concomp6 {1};
          '''.format(im_input_path, im_output_path, im_mask_foreground_path)
    print cmd1
    if not safety_on:
        os.system(cmd1)

    print "filtering connected components"
    filter_connected_components_by_volume_path(im_input_path, im_output_path, num_cc_to_filter=10)

    if save_intermediate:
        im_output_path_intermediate = os.path.join(os.path.dirname(im_output_path), 'z_intermediate.nii.gz')
        cmd_mid = 'cp {0} {1}'.format(im_output_path, im_output_path_intermediate)

    cmd2 = '''seg_maths  {0} -smol 1.2 {0};
             seg_maths {0} -dil 1 {0};
             seg_maths {0} -mul {1} {0};
          '''.format(im_output_path, im_mask_foreground_path)

    print cmd2
    if not safety_on:
        os.system(cmd2)
    pass