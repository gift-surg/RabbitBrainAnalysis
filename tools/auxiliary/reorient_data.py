import os
import numpy as np

import nibabel as nib
from tools.auxiliary.utils import set_new_data

"""
Basic rotations of a 3d matrix.
----------
Example:

cube = array([[[0, 1],
               [2, 3]],

              [[4, 5],
               [6, 7]]])

axis 0: perpendicular to the face [[0,1],[2,3]] (front-rear)
axis 1: perpendicular to the face [[1,5],[3,7]] (lateral right-left)
axis 2: perpendicular to the face [[0,1],[5,4]] (top-bottom)
----------
Note: the command m[:, ::-1, :].swapaxes(0, 1)[::-1, :, :].swapaxes(0, 2) rotates the cube m
around the diagonal axis 0-7.
----------
Note: avoid reorienting the data if you can reorient the header instead.
"""


def basic_rot_ax(m, ax=0):
    """
    :param m: 3d matrix
    :return: rotate the cube around axis ax, perpendicular to the face [[0,1],[2,3]]
    """

    ax %= 3

    if ax == 0:
        return np.rot90(m[:, ::-1, :].swapaxes(0, 1)[::-1, :, :].swapaxes(0, 2), 3)
    if ax == 1:
        return m.swapaxes(0, 2)[::-1, :, :]
    if ax == 2:
        return np.rot90(m, 1)


def axial_rotations(m, rot=1, ax=2):
    """
    :param m: 3d matrix
    :param rot: number of rotations
    :param ax: axis of rotation
    :return: m rotate rot times around axis ax, according to convention.
    """

    if len(m.shape) is not 3:
        assert IOError

    rot %= 4

    if rot == 0:
        return m

    for _ in range(rot):
        m = basic_rot_ax(m, ax=ax)

    return m


def flip_data():
    # TODO
    pass


def symmetrise_data(in_data, axis='x', plane_intercept=10, side_to_copy='below', keep_in_data_dimensions=True):
    """
    Symmetrise the input_array according to the axial plane
      axis = plane_intercept
    the copied part can be 'below' or 'above' the axes, following the ordering.

    :param in_data: (Z, X, Y) C convention input data
    :param axis:
    :param plane_intercept:
    :param side_to_copy:
    :param keep_in_data_dimensions:
    :return:
    """

    # Sanity check:

    msg = 'Input array must be 3-dimensional.'
    assert len(in_data.shape) == 3, msg

    msg = 'side_to_copy must be one of the two {}.'.format(['below', 'above'])
    assert side_to_copy in ['below', 'above'], msg

    msg = 'axis variable must be one of the following: {}.'.format(['x', 'y', 'z'])
    assert axis in ['x', 'y', 'z'], msg

    # step 1: find the block to symmetrise.
    # step 2: create the symmetric and glue it to the block.
    # step 3: add or remove a patch of slices if required to keep the in_data dimension.

    out_data = 0

    if axis == 'x':

        if side_to_copy == 'below':

            s_block = in_data[:, :plane_intercept, :]
            s_block_symmetric = s_block[:, ::-1, :]
            out_data = np.concatenate((s_block, s_block_symmetric), axis=1)

            if keep_in_data_dimensions:
                pass

        if side_to_copy == 'above':

            s_block = in_data[:, plane_intercept:, :]
            s_block_symmetric = s_block[:, ::-1, :]
            out_data = np.concatenate((s_block_symmetric, s_block), axis=1)

            if keep_in_data_dimensions:
                pass

    if axis == 'y':

        if side_to_copy == 'below':

            s_block = in_data[:, :, :plane_intercept]
            s_block_symmetric = s_block[:, :, ::-1]
            out_data = np.concatenate((s_block, s_block_symmetric), axis=2)

            if keep_in_data_dimensions:
                pass

        if side_to_copy == 'above':

            s_block = in_data[:, :, plane_intercept:]
            s_block_symmetric = s_block[:, :, ::-1]
            out_data = np.concatenate((s_block_symmetric, s_block), axis=2)

            if keep_in_data_dimensions:
                pass

    if axis == 'z':

        if side_to_copy == 'below':

            s_block = in_data[:plane_intercept, :, :]
            s_block_symmetric = s_block[::-1, :, :]
            out_data = np.concatenate((s_block, s_block_symmetric), axis=0)

            if keep_in_data_dimensions:
                pass

        if side_to_copy == 'above':

            s_block = in_data[plane_intercept:, :, :]
            s_block_symmetric = s_block[::-1, :, :]
            out_data = np.concatenate((s_block_symmetric, s_block), axis=0)

            if keep_in_data_dimensions:
                pass

    return out_data


def symmetrise_image_path(input_im_path, output_im_path,
                          axis='x', plane_intercept=10, side_to_copy='below', keep_in_data_dimensions=True):

    if not os.path.isfile(input_im_path):
        raise IOError('input image file does not exist.')
    if not os.path.isfile(output_im_path):
        raise IOError('input image file does not exist.')

    im_labels = nib.load(input_im_path)
    input_data = im_labels.get_data()

    symmetrised_data = symmetrise_data(input_data,
                                       axis=axis,
                                       plane_intercept=plane_intercept,
                                       side_to_copy=side_to_copy,
                                       keep_in_data_dimensions=keep_in_data_dimensions)

    im_relabelled = set_new_data(im_labels, symmetrised_data)
    nib.save(im_relabelled, output_im_path)

    print 'Symmetrised image from \n{0} \n saved in \n{1}'.format(input_im_path, output_im_path)
