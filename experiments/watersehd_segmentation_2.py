"""
Estrapolate a draft for a mask segmentation draft pipeline.

Create and save markers.
Create and save Sobel filter.
Ask markers to keep.
Manipulate markers to create the initial segmentation.
"""

import numpy as np
import os

import nibabel as nib
from scipy import ndimage as ndi
from skimage.morphology import disk
from skimage.filters import rank, sobel, roberts
from skimage.util import img_as_ubyte

from definitions import root_path_data
from tools.auxiliary.utils import set_new_data
from tools.correctors.label_managements import keep_only_one_label

from tools.visualisers.see_volume import see_array


##############
# Controller #
##############

visualize = False
cleaner = True

step_markers              = True
step_gradient             = True
step_markers_assessment   = True
step_markers_manipulation = True


################
# Path manager #
################

main_path = os.path.join(root_path_data, 'pipelines', 'zz_visual_assessment', 'estrapolate_mask_watershed')

input_image_path = os.path.join(main_path, 'subj_1305.nii.gz')

output_denoised_path = os.path.join(main_path, 'out_1305_denoised.nii.gz')
output_markers_path = os.path.join(main_path, 'out_1305_markers.nii.gz')
output_gradient_path = os.path.join(main_path, 'out_1305_gradient.nii.gz')
output_sobel_path = os.path.join(main_path, 'out_1305_sobel.nii.gz')
output_robert_path = os.path.join(main_path, 'out_1305_robert.nii.gz')

output_labels_from_markers_path = os.path.join(main_path, 'out_1305_labels_from_markers.nii.gz')
output_labels_path = os.path.join(main_path, 'out_1305_RESULT.nii.gz')

###########################
# Create and save markers #
###########################

if step_markers:

    im = nib.load(input_image_path)

    # extract the matrix:
    im_data = im.get_data().astype('float64')
    im_data *= (255 / np.max(im_data))

    im_data = img_as_ubyte(im_data.astype('uint8'))

    # if visualize:
    #    see_array(im_data, block=True, title='initial image')

    # get a denoised image
    denoised = np.zeros_like(im_data)

    for pln, image in enumerate(im_data):
        denoised[pln] = rank.median(image, disk(2))

    # get markers
    markers = np.zeros_like(denoised)

    for pln, image in enumerate(denoised):
        markers[pln] = rank.gradient(image, disk(5)) < 11

    markers = ndi.label(markers)[0]

    # save denoised and markers
    im_denoised = set_new_data(im, denoised)
    nib.save(im_denoised, output_denoised_path)

    markers_im = set_new_data(im, markers)
    nib.save(markers_im, output_markers_path)

    if visualize:
        cmd = 'itksnap -g {0} -s {1} '.format(input_image_path, output_markers_path)
        os.system(cmd)

############################
# Create and save gradient #
############################

if step_gradient:

    if not step_markers:

        im = nib.load(input_image_path)
        im_data = im.get_data().astype('float64')
        im_data *= (255 / np.max(im_data))
        im_data = img_as_ubyte(im_data.astype('uint8'))

        im_denoised = nib.load(output_denoised_path)
        denoised = im_denoised.get_data()

    gradient = np.zeros_like(denoised)
    edges_data_s = np.zeros_like(im_data)
    edges_data_r = np.zeros_like(im_data)

    for pln, image in enumerate(denoised):
        gradient[pln] = rank.gradient(image, disk(2))
        edges_data_s[pln] = sobel(image)
        edges_data_r[pln] = roberts(image)

    # sobel and robert filter needs to work with original data:

    im_data = im.get_data().astype('float64')

    for pln, image in enumerate(im_data):
        edges_data_s[pln] = sobel(image)
        edges_data_r[pln] = roberts(image)

    if visualize:
        see_array(gradient, block=True, title='image gradient, gradient')
        see_array(edges_data_s, block=True, title='image gradient, Sobel')
        see_array(edges_data_r, block=True, title='image gradient, Roberts')

    im_gradient = set_new_data(im, gradient)
    nib.save(im_gradient, output_gradient_path)

    im_sobel = set_new_data(im, edges_data_s)
    nib.save(im_sobel, output_sobel_path)

    im_roberts = set_new_data(im, edges_data_r)
    nib.save(im_roberts, output_robert_path)

    if cleaner:
        del im_gradient
        del im_sobel
        del im_roberts
        del im_data
        del denoised
        del im_denoised

###############################################
# ask for the labels to keep from the markers #
###############################################

if step_markers_assessment:

    if not step_gradient or not step_markers:
        im = nib.load(input_image_path)

    # Open gradient and markers as mask of the gradient
    cmd = 'itksnap -g {0} -s {1} '.format(output_gradient_path, output_markers_path)
    os.system(cmd)

    # Ask what labels to keep at console
    print 'Insert the list of the labels you want to keep and merge, separated by spaces: '
    labels_to_keep = raw_input()

    im_labels = nib.load(output_markers_path)
    labels_data = im_labels.get_data()

    labels_to_keep = labels_to_keep.split(' ')
    labels_to_keep = [int(j) for j in labels_to_keep]
    relevant_labels = keep_only_one_label(labels_data, labels_to_keep)

    # save
    relevant_labels_im = set_new_data(im, relevant_labels)
    nib.save(relevant_labels_im, output_labels_from_markers_path)

    if cleaner:
        del im
        del im_labels
        del labels_to_keep
        del relevant_labels
        del relevant_labels_im

############################################
# elaborate the labels kept in the markers #
############################################

if step_markers_manipulation:

    if not step_markers_assessment:
        relevant_labels_im = nib.load(output_labels_from_markers_path)
        relevant_labels = relevant_labels_im.get_data()

    # copy relevant labels to final mask:
    cmd = 'cp {0} {1}'.format(output_labels_from_markers_path, output_labels_path)
    os.system(cmd)

    # put all the labels to 1:
    print 'Binarisation...'
    cmd = 'seg_maths {0} -bin {1} '.format(output_labels_path, output_labels_path)
    os.system(cmd)

    # dilate
    print 'Dilation...'
    cmd = 'seg_maths {0} -dil 1 {1} '.format(output_labels_path, output_labels_path)
    os.system(cmd)

    # smooth
    print 'Smoothing...'
    cmd = 'seg_maths {0} -smol 1.1 {1} '.format(output_labels_path, output_labels_path)
    os.system(cmd)

    if visualize:
        cmd = 'itksnap -g {0} -s {1} '.format(output_gradient_path, output_labels_path)
