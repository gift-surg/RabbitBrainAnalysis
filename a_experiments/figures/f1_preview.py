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
import copy

from matplotlib import pyplot as plt
from scipy.interpolate import splprep, splev

from labels_manager.main import LabelsManager as LM
from labels_manager.tools.aux_methods.utils_nib import set_new_data


pfo_template = '/Users/sebastiano/Dropbox/RabbitEOP-MRI/study/A_internal_template'
pfo_model = '/Users/sebastiano/Dropbox/RabbitEOP-MRI/docs/Atlas_Paper/images/subject_model'
pfo_resulting_images_folder = '/Users/sebastiano/Dropbox/RabbitEOP-MRI/docs/Atlas_Paper/images/f1_preview_b'

chart_name = '1305'

pfi_input_anatomy = jph(pfo_model, '{}_T1.nii.gz'.format(chart_name))
pfi_input_anatomy_FA = jph(pfo_model, '{}_FA.nii.gz'.format(chart_name))
pfi_input_segmentation = jph(pfo_model, '{}_approved.nii.gz'.format(chart_name))
os.path.exists(pfi_input_anatomy)
os.path.exists(pfi_input_anatomy_FA)
os.path.exists(pfi_input_segmentation)

pfi_output_contour_coronal = jph(pfo_resulting_images_folder, '{}_contour_coronal.nii.gz'.format(chart_name))
pfi_output_contour_sagittal = jph(pfo_resulting_images_folder, '{}_contour_sagittal.nii.gz'.format(chart_name))
pfi_labels_descriptor = jph(pfo_resulting_images_folder, 'labels_descriptor_fig1.txt')


# def order_the_point_clouds(cloud, epsilon=2):
#     """
#     Cloud is a 2D list of 1D array [X_coord, Y_coord]. Only 2D allowed.
#     :param cloud:
#     :param epsilon: if the distance is greater than epsilon, the output is splitted into two values.
#     :return:
#     """
#     cloud = copy.deepcopy(cloud)
#     seq = [[cloud[0][0], cloud[1][0]]]
#     while len(cloud[0]) > 0:
#         for x, y in zip(cloud[0][1:], cloud[1][1:]):
#             pass


def exploded_segmentation(im_segm, direction, intercepts, offset, dtype=np.int):
    """
    Damien Hirst like sectioning of an anatomical segmentation.
    :param im_segm: nibabel image segmentation
    :param direction: sectioning direction, can be sagittal, axial or coronal
    (conventional names for images oriented to standard (diagonal affine transformation))
    :param intercepts: list of values of the stack plane in the input segmentation.
    Needs to include the max plane and the min plane
    :param offset: voxel to leave empty between one slice and the other
    :return: nibabel image output as sectioning of the input one.
    """
    if direction.lower() == 'axial':
        block = np.zeros([im_segm.shape[0], im_segm.shape[1], offset]).astype(dtype)
        stack = []
        for j in range(1, len(intercepts)):
            stack += [im_segm.get_data()[:, :, intercepts[j-1]:intercepts[j]].astype(dtype)] + [block]
        return set_new_data(im_segm, np.concatenate(stack, axis=2))

    elif direction.lower() == 'sagittal':
        block = np.zeros([offset, im_segm.shape[1], im_segm.shape[2]]).astype(dtype)
        stack = []
        for j in range(1, len(intercepts)):
            stack += [im_segm.get_data()[intercepts[j - 1]:intercepts[j], :, :].astype(dtype)] + [block]
        return set_new_data(im_segm, np.concatenate(stack, axis=0))

    elif direction.lower() == 'coronal':
        block = np.zeros([im_segm.shape[0], offset, im_segm.shape[2]]).astype(dtype)
        stack = []
        for j in range(1, len(intercepts)):
            stack += [im_segm.get_data()[:, intercepts[j - 1]:intercepts[j], :].astype(dtype)] + [block]
        for st in stack:
            print st.shape
        return set_new_data(im_segm, np.concatenate(stack, axis=1))

    else:
        raise IOError


def create_cuts_on_segmentation(im_segm, direction, intercepts, offset, dtype=np.int, cuts_label=0):
    """
    Slices of the input segmentation are substituted with black lines.
    :param im_segm:
    :param direction:
    :param intercepts:
    :param offset:
    :param dtype:
    :return:
    """
    new_data = copy.deepcopy(im_segm.get_data())
    where_segmentation = im_segm.get_data() > 0
    where_segmentation = where_segmentation.astype(np.int) * cuts_label

    if direction.lower() == 'axial':
        for j in range(1, len(intercepts) - 1):
            new_data[:, :, intercepts[j]:intercepts[j]+offset] = \
                where_segmentation[:, :, intercepts[j]:intercepts[j]+offset]

    elif direction.lower() == 'sagittal':
        for j in range(1, len(intercepts)):
            new_data[intercepts[j]:intercepts[j]+offset, :, :] = \
                where_segmentation[intercepts[j]:intercepts[j]+offset, :, :]

    elif direction.lower() == 'coronal':
        for j in range(1, len(intercepts)):
            print j
            new_data[:, intercepts[j]:intercepts[j]+offset, :] = \
                where_segmentation[:, intercepts[j]:intercepts[j]+offset, :]

    else:
        raise IOError

    return set_new_data(im_segm, new_data)


def segmentation_disjoint_union(im_segm1, im_segm2):

    assert im_segm1.shape == im_segm2.shape
    where_segmentation_1 = im_segm1.get_data() > 0
    where_segmentation_2 = im_segm2.get_data() > 0
    where_segmentation_1_and_2 = where_segmentation_1 * where_segmentation_2

    new_data = copy.deepcopy(im_segm1.get_data())

    new_data = new_data * np.logical_not(where_segmentation_1_and_2).astype(np.int)
    new_data = new_data + im_segm2.get_data()
    return set_new_data(im_segm1, new_data)


def get_zebra_midplane(im_segm, direction, intercepts, offset, foreground=0, background=254):

    midplane = np.zeros_like(im_segm.get_data())
    if direction.lower() == 'axial':
        midplane[int(midplane.shape[0]/2), :, :] = background * np.ones_like(midplane[int(midplane.shape[0]/2), :, :])
        for j in range(1, len(intercepts) - 1):
            midplane[int(midplane.shape[0]/2), :, intercepts[j]:intercepts[j]+offset] = \
                foreground * np.ones_like(midplane[int(midplane.shape[0]/2), :, intercepts[j]:intercepts[j]+offset])

    elif direction.lower() == 'sagittal':
        midplane[:, int(midplane.shape[1]/2), :] = background * np.ones_like(midplane[:, int(midplane.shape[1]/2), :])
        for j in range(1, len(intercepts) - 1):
            midplane[intercepts[j]:intercepts[j] + offset, int(midplane.shape[1]/2), :] = \
                foreground * np.ones_like(midplane[intercepts[j]:intercepts[j] + offset, int(midplane.shape[1]/2), :])

    elif direction.lower() == 'coronal':
        midplane[int(midplane.shape[0]/2), :, :] = background * np.ones_like(midplane[int(midplane.shape[0]/2), :, :])
        for j in range(1, len(intercepts) - 1):
            midplane[int(midplane.shape[0]/2), intercepts[j]:intercepts[j]+offset, :] = \
                foreground * np.ones_like(midplane[int(midplane.shape[0]/2), intercepts[j]:intercepts[j]+offset, :])
    else:
        raise IOError

    return set_new_data(im_segm, midplane)

# --------------------------------------------------------------------------------------------------------
# ----------------------       CORONAL SECTIONS                -------------------------------------------
# --------------------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------------
# ----------------------       VERSION 0: coronal sections labelled   ------------------------------------
# --------------------------------------------------------------------------------------------------------


if False:
    # create contour
    lm = LM()
    lm.manipulate.get_contour_from_segmentation(pfi_input_segmentation, pfi_output_contour_coronal, omit_axis='y', verbose=1)

    lm.manipulate.get_contour_from_segmentation(pfi_input_segmentation, pfi_output_contour_sagittal, omit_axis='x', verbose=1)

    # open the images to start the screenshots:
    cmd0 = 'itksnap -g {0} -s {1} -l {2}'.format(pfi_input_anatomy, pfi_output_contour_coronal, pfi_labels_descriptor)
    os.system(cmd0)
    cmd1 = 'itksnap -g {0} -s {1} -l {2}'.format(pfi_input_anatomy, pfi_output_contour_sagittal, pfi_labels_descriptor)
    os.system(cmd1)

# OK PART B
if False:
    # get sliced image on the coronal coordinates (y)
    coronal_coordinates = [106, 117, 130, 151, 162, 172, 185, 197, 212, 228, 247, 266]  # 88,  236, 141, 289, 279, 306
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

    cmd1 = 'itksnap -g {0} -s {1} -l {2}'.format(pfi_input_anatomy, pfi_input_segmentation, pfi_labels_descriptor)
    os.system(cmd1)

if False:
    # Direct interpolation:
    coronal_coordinates = [88, 106, 117, 130, 151, 162, 172, 185, 197, 212, 228, 247, 266, 279, 306]

    im_anatomy = nib.load(pfi_input_anatomy)
    im_segm = nib.load(pfi_output_contour_coronal)

    for c in coronal_coordinates[:2]:

        data_slice_anatomy = im_anatomy.get_data()[:, c, :]
        data_slice_segm = im_segm.get_data()[:, c, :]
        labels_in_slice = list(np.sort(list(set(data_slice_segm.astype(np.int).flat))))

        fig = plt.figure(c)
        ax = plt.subplot(111)

        for l in labels_in_slice[1:]:
            where_l = np.where(data_slice_segm == l)

            ax.imshow(data_slice_anatomy.T, origin='lower')  # extent=[horizontal_min,horizontal_max,vertical_min,vertical_max]
            coords_points = np.stack(where_l, axis=0)

            tck, u = splprep(coords_points, u=None, s=0.0, per=1)
            u_new = np.linspace(u.min(), u.max(), 1000)
            x_new, y_new = splev(u_new, tck, der=0)

            ax.plot(where_l[0], where_l[1], 'ro')  # set color, set line shape
            plt.plot(x_new, y_new, 'b--')  # spline for when the numbers will be ordered.
        plt.show(block=True)

# --------------------------------------------------------------------------------------------------------
# ----------------------     VERSION 1: coronal sections exploded ----------------------------------------
# --------------------------------------------------------------------------------------------------------

if False:
    coronal_intercepts = [0] + [int(k) for k in np.linspace(143, 252, 4)] + [385]
    coronal_intercepts = [0] + [106, 117, 130, 151, 162, 172, 185, 197, 212, 228, 247, 266] + [385]
    direction = 'coronal'
    offset = 10

    im_segm = nib.load(pfi_input_segmentation)

    im_new = exploded_segmentation(im_segm, direction, coronal_intercepts, offset)

    pfi_exploded_coronal = jph(pfo_resulting_images_folder, '{}_exploded_coronal.nii.gz'.format(chart_name))
    nib.save(im_new, pfi_exploded_coronal)

    cmd0 = 'itksnap -g {0} -s {1} -l {2}'.format(pfi_exploded_coronal, pfi_exploded_coronal, pfi_labels_descriptor)
    os.system(cmd0)

    cmd1 = 'itksnap -g {0} -s {1} -l {2}'.format(pfi_input_anatomy, pfi_input_segmentation, pfi_labels_descriptor)
    os.system(cmd1)

# --------------------------------------------------------------------------------------------------------
# ----------------------     VERSION 2: coronal sections planes ------------------------------------------
# --------------------------------------------------------------------------------------------------------

if False:

    # Generate coronal cutting planes
    coronal_coordinates = [int(k) for k in np.linspace(143, 252, 6)]

    print len(coronal_coordinates)
    pfi_output_slicing_planes = jph(pfo_resulting_images_folder, '{}_slicing_planes_coronal.nii.gz'.format(chart_name))

    im_segm = nib.load(pfi_input_segmentation)

    vol_slices = np.zeros_like(im_segm.get_data())
    for c in coronal_coordinates:
        vol_slices[:, c, :] = 255 * np.ones_like(vol_slices[:, c, :]).astype(np.int)

    im_slices = set_new_data(im_segm, vol_slices)
    nib.save(im_slices, pfi_output_slicing_planes)

    pfi_segmentation_and_planes = jph(pfo_resulting_images_folder,
                                      '{}_approved_and_planes_coronal.nii.gz'.format(chart_name))


    im_intersection = segmentation_disjoint_union(im_segm, im_slices)
    nib.save(im_intersection, pfi_segmentation_and_planes)

    # See:
    cmd1 = 'itksnap -g {0} -s {1} -l {2}'.format(pfi_input_anatomy, pfi_segmentation_and_planes, pfi_labels_descriptor)
    os.system(cmd1)
    cmd1 = 'itksnap -g {0} -s {1} -l {2}'.format(pfi_input_anatomy, pfi_output_contour_coronal, pfi_labels_descriptor)
    os.system(cmd1)


# --------------------------------------------------------------------------------------------------------
# ----------------------     VERSION 3: coronal sections cuts ------------------------------------------
# --------------------------------------------------------------------------------------------------------

# OK PART A - B
if False:
    coronal_intercepts = [0] + [int(k) for k in np.linspace(143, 252, 4)] + [385]
    coronal_intercepts = [0] + [106, 117, 130, 151, 162, 172, 185, 197, 212, 228, 247, 266] + [385]
    direction = 'coronal'
    offset = 2

    im_segm = nib.load(pfi_input_segmentation)

    im_new = create_cuts_on_segmentation(im_segm, direction, coronal_intercepts, offset, cuts_label=2)

    pfi_cutted_coronal = jph(pfo_resulting_images_folder, '{}_approved_and_sliced_coronal.nii.gz'.format(chart_name))
    nib.save(im_new, pfi_cutted_coronal)

    cmd0 = 'itksnap -g {0} -s {1} -l {2}'.format(pfi_cutted_coronal, pfi_cutted_coronal, pfi_labels_descriptor)
    os.system(cmd0)

# --------------------------------------------------------------------------------------------------------
# ----------------------     VERSION 4: coronal sections cuts + background -------------------------------
# --------------------------------------------------------------------------------------------------------


if False:
    coronal_intercepts = [0] + [int(k) for k in np.linspace(143, 252, 4)] + [385]
    direction = 'coronal'
    offset = 1

    im_segm = nib.load(pfi_input_segmentation)

    im_zebra = get_zebra_midplane(im_segm, direction, coronal_intercepts, offset, foreground=2, background=1)
    im_cuts = create_cuts_on_segmentation(im_segm, direction, coronal_intercepts, offset, cuts_label=2)
    im_final = segmentation_disjoint_union(im_cuts, im_zebra)  #set_new_data(im_segm, im_cuts.get_data() + im_zebra.get_data())

    pfi_zebra_midplane = jph(pfo_resulting_images_folder, '{}_approved_and_sliced_coronal_zebra.nii.gz'.format(chart_name))
    nib.save(im_zebra, pfi_zebra_midplane)

    pfi_segm_cuts = jph(pfo_resulting_images_folder, '{}_approved_and_sliced_coronal_cuts.nii.gz'.format(chart_name))
    nib.save(im_cuts, pfi_segm_cuts)

    pfi_final_midplane = jph(pfo_resulting_images_folder, '{}_approved_and_sliced_coronal_cuts_and_zebra.nii.gz'.format(chart_name))
    nib.save(im_final, pfi_final_midplane)

    # cmd0 = 'itksnap -g {0} -s {1} -l {2}'.format(pfi_zebra_midplane, pfi_zebra_midplane, pfi_labels_descriptor)
    # os.system(cmd0)
    #
    # cmd0 = 'itksnap -g {0} -s {1} -l {2}'.format(pfi_segm_cuts, pfi_segm_cuts, pfi_labels_descriptor)
    # os.system(cmd0)

    cmd0 = 'itksnap -g {0} -s {1} -l {2}'.format(pfi_final_midplane, pfi_final_midplane, pfi_labels_descriptor)
    os.system(cmd0)


# --------------------------------------------------------------------------------------------------------
# ----------------------       SAGITTAL SECTIONS                ------------------------------------------
# --------------------------------------------------------------------------------------------------------


# --------------------------------------------------------------------------------------------------------
# ----------------------     VERSION 1: sagittal sections exploded ----------------------------------------
# --------------------------------------------------------------------------------------------------------


if False:
    coronal_intercepts = [0] + [int(k) for k in np.linspace(163, 219, 3)] + [385]
    sagittal_intercepts = [0] + [176, 219] + [320]
    direction = 'sagittal'
    offset = 20

    im_segm = nib.load(pfi_input_segmentation)

    im_new = exploded_segmentation(im_segm, direction, coronal_intercepts, offset)

    pfi_exploded_sagittal = jph(pfo_resulting_images_folder, '{}_exploded_sagittal.nii.gz'.format(chart_name))
    nib.save(im_new, pfi_exploded_sagittal)

    cmd0 = 'itksnap -g {0} -s {1} -l {2}'.format(pfi_exploded_sagittal, pfi_exploded_sagittal, pfi_labels_descriptor)
    os.system(cmd0)

# --------------------------------------------------------------------------------------------------------
# ----------------------     VERSION 2: sagittal sections planes ------------------------------------------
# --------------------------------------------------------------------------------------------------------

if False:

    # Generate coronal cutting plane
    sagittal_coordinates = [int(k) for k in np.linspace(163, 219, 3)]

    print len(sagittal_coordinates)
    pfi_output_slicing_planes = jph(pfo_resulting_images_folder, '{}_3_slicing_planes_sagittal.nii.gz'.format(chart_name))

    im_segm = nib.load(pfi_input_segmentation)

    vol_slices = np.zeros_like(im_segm.get_data())
    for s in sagittal_coordinates:
        vol_slices[s, :, :] = np.ones_like(vol_slices[s, :, :])

    im_slices = set_new_data(im_segm, vol_slices)
    nib.save(im_slices, pfi_output_slicing_planes)

    cmd0 = 'itksnap -g {0} -s {1} -l {2}'.format(pfi_input_anatomy, pfi_output_slicing_planes, pfi_labels_descriptor)
    os.system(cmd0)

# OK PART A - C
if True:

    sagittal_intercepts = [0] + [176, 219] + [320]
    direction = 'sagittal'
    offset = 2

    im_segm = nib.load(pfi_input_segmentation)

    im_new = create_cuts_on_segmentation(im_segm, direction, sagittal_intercepts, offset, cuts_label=2)

    pfi_cutted_sagittal = jph(pfo_resulting_images_folder, '{}_approved_and_sliced_coronal.nii.gz'.format(chart_name))
    nib.save(im_new, pfi_cutted_sagittal)

    cmd0 = 'itksnap -g {0} -s {1} -l {2}'.format(pfi_cutted_sagittal, pfi_cutted_sagittal, pfi_labels_descriptor)
    os.system(cmd0)

    # Open T1
    cmd1 = 'itksnap -g {0} -s {1} -l {2}'.format(pfi_input_anatomy, pfi_output_contour_sagittal, pfi_labels_descriptor)
    os.system(cmd1)

    # open FA
    cmd1 = 'itksnap -g {0} -s {1} -l {2}'.format(pfi_input_anatomy_FA, pfi_output_contour_sagittal, pfi_labels_descriptor)
    os.system(cmd1)

