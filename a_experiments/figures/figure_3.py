"""
Transparencies labels for the same subject.
"""
import os
from os.path import join as jph

import numpy as np
import nibabel as nib

from labels_manager.main import LabelsManager as LM
from labels_manager.tools.image_colors_manipulations.relabeller import relabeller, assign_all_other_labels_the_same_value
from labels_manager.tools.aux_methods.utils_nib import set_new_data

# --- labels divided by area:

macro_region_labels = {
    'cerebrum'             : [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
                              17, 18, 19, 20, 21, 22, 25, 26, 27, 28, 31,
                              32, 43, 44, 45, 46, 47, 48, 53, 54, 55, 56,
                              69, 70, 71, 72, 75, 76, 77, 78],
    'brainstem_interbrain' : [83, 84, 109, 110, 121],
    'brainstem_midbrain'   : [127, 129, 130, 133, 134, 135, 136, 139, 140,
                              141, 142, 151, 153],
    'cerebellum'           : [161, 179, 180],
    'ventricular_system'   : [201, 211, 212],
    'fibre_tracts'         : [213, 215, 218, 219, 220, 223, 224, 225, 226,
                              227, 228, 229, 230, 233, 237, 239, 240, 241,
                              242, 243, 244, 247, 248, 249, 250, 251, 252,
                              253, 255]
}


macro_region_labels_joints = {
    'cerebrum'             : [5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16,
                              17, 18, 19, 20, 21, 22, 25, 26, 27, 28, 31,
                              32, 43, 44, 45, 46, 47, 48, 53, 54, 55, 56,
                              69, 70, 71, 72, 75, 76, 77, 78],
    'brainstem_interbrain_brainstem_midbrain_cerebellum' : [83, 84, 109, 110, 121] +
                                                           [127, 129, 130, 133, 134, 135, 136, 139, 140,
                                                            141, 142, 151, 153] + [161, 179, 180],
    'ventricular_system_fibre_tracts'   : [201, 211, 212] + [213, 215, 218, 219, 220, 223, 224, 225, 226,
                                                             227, 228, 229, 230, 233, 237, 239, 240, 241,
                                                             242, 243, 244, 247, 248, 249, 250, 251, 252,
                                                             253, 255]
}


macro_region_labels_joints_side_only = {
    'cerebrum_left'             : [5, 7, 9, 11, 13, 15, 17, 19, 21, 25, 27, 31, 32, 43, 45, 47, 53, 55,
                                   69, 71, 75, 77],
    'brainstem_interbrain_brainstem_midbrain_cerebellum_left' : [83, 109, 121] +
                                                           [127, 129, 133, 135, 139, 141, 151, 153] + [161, 179],
    'ventricular_system_fibre_tracts_left'   : [201, 211] + [213, 215, 219, 223, 225, 227, 229, 233, 237, 239, 241,
                                                             243, 247, 249, 250, 251, 253, 255]
}



# Segmentation input

pfo_template = '/Users/sebastiano/Dropbox/RabbitEOP-MRI/study/A_internal_template'
pfo_model = '/Users/sebastiano/Dropbox/RabbitEOP-MRI/docs/Atlas_Paper/images/subject_model'
pfo_resulting_images_folder = '/Users/sebastiano/Dropbox/RabbitEOP-MRI/docs/Atlas_Paper/images/figure_3'

chart_name = '1305'

pfi_input_anatomy = jph(pfo_model, '{}_T1.nii.gz'.format(chart_name))
pfi_input_segmentation = jph(pfo_model, '{}_approved.nii.gz'.format(chart_name))
os.path.exists(pfi_input_anatomy)
os.path.exists(pfi_input_segmentation)

pfi_output_contour = jph(pfo_resulting_images_folder, '{}_contour.nii.gz'.format(chart_name))
pfi_local_labels_descriptor = jph(pfo_resulting_images_folder, 'labels_descriptor_fig3.txt')


if True:
    # for each macro region set all other regions to 255.
    im_segm = nib.load(pfi_input_segmentation)

    labels_in_image = list(np.sort(list(set(im_segm.get_data().astype(np.int).flat))))

    print labels_in_image

    # for mr_key in macro_region_labels_joints_side_only.keys():
    #
    #     pfi_macro_region_output = jph(pfo_resulting_images_folder,
    #                                   '{0}_approved_macro_region_{1}.nii.gz'.format(chart_name, mr_key))
    #
    #     new_data = assign_all_other_labels_the_same_value(im_segm.get_data(),
    #                                                       labels_to_keep=macro_region_labels_joints_side_only[mr_key],
    #                                                       same_value_label=255)
    #
    #     new_im_segm = set_new_data(im_segm, new_data)
    #     nib.save(new_im_segm, pfi_macro_region_output)
    #
    #     cmd = 'itksnap -g {0} -s {1} -l {2}'.format(pfi_input_anatomy,
    #                                                 pfi_macro_region_output,
    #                                                 pfi_local_labels_descriptor)
    #     os.system(cmd)

