import os
from os.path import join as jph
import numpy as np
import nibabel as nib
import copy

from matplotlib import pyplot as plt
from scipy.interpolate import splprep, splev

from labels_manager.main import LabelsManager as LM
from labels_manager.tools.aux_methods.utils_nib import set_new_data


pfo_template = '/Users/sebastiano/Dropbox/RabbitEOP-MRI/study/A_internal_template'
pfo_model = '/Users/sebastiano/Dropbox/RabbitEOP-MRI/docs/Atlas_Paper/images/subject_model'
pfo_images_folder = '/Users/sebastiano/Dropbox/RabbitEOP-MRI/docs/Atlas_Paper/images/f5_multimodal'

slice_to_consider = 162

pfi_input_segmentation = jph(pfo_images_folder, '1702_approved.nii.gz')
pfi_input_label_descriptor = jph(pfo_images_folder, 'labels_descriptor_v9.txt')

pfi_input_T1 = jph(pfo_images_folder, '1702_T1.nii.gz')
pfi_input_FA = jph(pfo_images_folder, '1702_FA.nii.gz')
pfi_input_MD = jph(pfo_images_folder, '1702_MD.nii.gz')

os.path.exists(pfi_input_T1)
os.path.exists(pfi_input_FA)
os.path.exists(pfi_input_MD)

pfi_output_contour_coronal = jph(pfo_images_folder, '1702_approved_contour_coronal.nii.gz')

chart_name = '1702'


if True:
    # create contour
    lm = LM()
    lm.manipulate.get_contour_from_segmentation(pfi_input_segmentation, pfi_output_contour_coronal, omit_axis='y', verbose=1)

    # open the images to start the screenshots:
    cmd0 = 'itksnap -g {0} -s {1} -l {2}'.format(pfi_input_T1, pfi_output_contour_coronal, pfi_input_label_descriptor)
    os.system(cmd0)
    cmd0 = 'itksnap -g {0} -s {1} -l {2}'.format(pfi_input_FA, pfi_output_contour_coronal, pfi_input_label_descriptor)
    os.system(cmd0)

    cmd0 = 'itksnap -g {0} -s {1} -l {2}'.format(pfi_input_MD, pfi_output_contour_coronal, pfi_input_label_descriptor)
    os.system(cmd0)




