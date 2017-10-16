"""
CREATE CONTOUR SEGMENTATIONS:
Images are axial screenshots of the resulting files at coronal coordinates.
https://stackoverflow.com/questions/31464345/fitting-a-closed-curve-to-a-set-of-points
https://stackoverflow.com/questions/42124192/how-to-centre-the-origin-in-the-centre-of-an-imshow-plot
https://stackoverflow.com/questions/6999621/how-to-use-extent-in-matplotlib-pyplot-imshow
"""

import os
from os.path import join as jph
import numpy as np
import nibabel as nib

from matplotlib import pyplot as plt
from scipy.interpolate import splprep, splev

from labels_manager.main import LabelsManager as LM
from labels_manager.tools.aux_methods.utils_nib import set_new_data
from labels_manager.tools.aux_methods.utils_nib import replace_translational_part


pfo_template = '/Users/sebastiano/Dropbox/RabbitEOP-MRI/study/A_internal_template'
pfo_model = '/Users/sebastiano/Dropbox/RabbitEOP-MRI/docs/Atlas_Paper/images/subject_model'
pfo_resulting_images_folder = '/Users/sebastiano/Dropbox/RabbitEOP-MRI/docs/Atlas_Paper/images/figure_6'

chart_name = '1305'

pfi_input_anatomy = jph(pfo_model, '{}_T1.nii.gz'.format(chart_name))
pfi_input_segmentation = jph(pfo_model, '{}_approved.nii.gz'.format(chart_name))
os.path.exists(pfi_input_anatomy)
os.path.exists(pfi_input_segmentation)

pfi_output_contour = jph(pfo_resulting_images_folder, '{}_contour.nii.gz'.format(chart_name))
pfi_labels_descriptor = jph(pfo_template, 'LabelsDescriptors', 'labels_descriptor_v8.txt')


pfo_temporary_template = '/Users/sebastiano/Desktop/temporary_template'
assert os.path.exists(pfo_temporary_template)

if True:
    # get sliced image on the coronal coordinates (y)
    coronal_coordinates = [int(a) for a in np.linspace(120, 260, 5)]
    print len(coronal_coordinates)
    pfi_output_slicing_planes = jph(pfo_resulting_images_folder, '{}_slicing_planes.nii.gz'.format(chart_name))

    im_segm = nib.load(pfi_input_segmentation)

    vol_slices = np.zeros_like(im_segm.get_data())
    for c in coronal_coordinates:
        vol_slices[:, c, :] = np.ones_like(vol_slices[:, c, :])

    im_slices = set_new_data(im_segm, vol_slices)
    nib.save(im_slices, pfi_output_slicing_planes)

    cmd0 = 'itksnap -g {0} -s {1} -l {2}'.format(pfi_input_anatomy, pfi_output_slicing_planes, pfi_labels_descriptor)
    os.system(cmd0)

if True:
    # open each subject of the atlas/segmentation, with the segmentation itself as its segmentation.
    # Take screenshot of the default zoom to fit view of the Coronal slices according to the selected slices previously
    # obtained. Black screens for the subjects not yet insterted.

    for sj in ['1201', '1203', '1305', '1404', '1507', '1510', '1702', '1805', '2002', '2502']:
        pfi_sj_segm = jph(pfo_temporary_template, sj + '_approved.nii.gz')

        # Set translational part to 0 in case.
        # im_seg = nib.load(pfi_sj_segm)
        # new_im = replace_translational_part(im_seg, np.array([0, 0, 0]))
        # nib.save(new_im, pfi_sj_segm)

        cmd0 = 'itksnap -g {0} -s {1} -l {2}'.format(pfi_sj_segm, pfi_sj_segm, pfi_labels_descriptor)
        os.system(cmd0)



