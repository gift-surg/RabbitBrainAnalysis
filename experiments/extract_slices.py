import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, RadioButtons

import nibabel as nib
import SimpleITK as sitk

from tools.auxiliary.utils import set_new_data
from definitions import root_ex_vivo_template

from tools.visualisers.see_volume import see_array

folder_test = os.path.join(root_ex_vivo_template, 'zz_experiments/slices')

x_slice_a, x_slice_b = 144, 173
y_slice_a, y_slice_b = 0, 305
z_slice_a, z_slice_b = 0, 320

im_input_pth = os.path.join(folder_test, '1404_3D_proc.nii.gz')
im_input = nib.load(im_input_pth)


im_data_new = im_input.get_data()[x_slice_a:x_slice_b, y_slice_a:y_slice_b, z_slice_a:z_slice_b]

see_array(im_data_new)

'''
img = sitk.GetImageFromArray(im_data_new)
sigma=img.GetSpacing()[0]
level=4

feature_img = sitk.GradientMagnitude(img)

#print type(feature_img)
see_array(sitk.GetArrayFromImage(feature_img), num_fig=1)


#ws_img = sitk.MorphologicalWatershed(feature_img, level=10, markWatershedLine=True, fullyConnected=False)
#see_array(sitk.GetArrayFromImage(sitk.LabelToRGB(ws_img)), num_fig=2)


im_new = set_new_data(im_input, sitk.GetArrayFromImage(feature_img))

nib.save(im_new, os.path.join(folder_test, 'sliced_im_wat.nii.gz'))
'''