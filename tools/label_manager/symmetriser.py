import os
import numpy as np

import nibabel as nib

from tools.auxiliary.utils import set_new_data
from tools.label_manager.relabeller import relabeller_path


def flip_data(in_data, axis='x'):

    msg = 'Input array must be 3-dimensional.'
    assert len(in_data.shape) == 3, msg

    msg = 'axis variable must be one of the following: {}.'.format(['x', 'y', 'z'])
    assert axis in ['x', 'y', 'z'], msg

    if axis == 'x':
        out_data = in_data[:, ::-1, :]
    if axis == 'y':
        out_data = in_data[:, :, ::-1]
    if axis == 'z':
        out_data = in_data[::-1, :, :]

    return out_data


def flip_data_path(input_im_path, output_im_path, axis='x'):

    if not os.path.isfile(input_im_path):
        raise IOError('input image file does not exist.')

    im_labels = nib.load(input_im_path)
    data_labels = im_labels.get_data()
    data_flipped = flip_data(data_labels, axis=axis)

    im_relabelled = set_new_data(im_labels, data_flipped)
    nib.save(im_relabelled, output_im_path)


def sym_labels(pfi_anatomy,
               pfi_segmentation,
               pfo_results,
               pfi_result_segmentation,
               list_labels_input,
               list_labels_transformed=None,
               reuse_registration=False,
               coord='z'):

    # side A is the input, side B is the one where we want to symmetrise.

    # --- Initialisation  --- #

    # check input:
    if not os.path.isfile(pfi_anatomy):
        raise IOError('input image file {} does not exist.'.format(pfi_anatomy))
    if not os.path.isfile(pfi_segmentation):
        raise IOError('input segmentation file {} does not exist.'.format(pfi_segmentation))

    # erase labels that are not in the list from image and descriptor

    out_labels_side_A_path = os.path.join(pfo_results, 'z_labels_side_A.nii.gz')
    labels_im = nib.load(pfi_segmentation)
    labels_data = labels_im.get_data()
    labels_to_erase = list(set(labels_data.flat) - set(list_labels_input))
    relabeller_path(pfi_segmentation, out_labels_side_A_path,
                    list_old_labels=labels_to_erase,
                    list_new_labels=[0, ] * len(labels_to_erase))

    # --- Create side B  --- #

    # flip anatomical image and register it over the non flipped
    out_anatomical_flipped_path = os.path.join(pfo_results, 'z_anatomical_flipped.nii.gz')
    flip_data_path(pfi_anatomy, out_anatomical_flipped_path, axis=coord)

    # flip the labels
    out_labels_flipped_path = os.path.join(pfo_results, 'z_labels_flipped.nii.gz')
    flip_data_path(out_labels_side_A_path, out_labels_flipped_path, axis=coord)

    # register anatomical flipped over non flipped
    out_anatomical_flipped_warped_path = os.path.join(pfo_results, 'z_anatomical_flipped_warped.nii.gz')
    out_affine_transf_path = os.path.join(pfo_results, 'z_affine_transformation.txt')

    if not reuse_registration:
        cmd = 'reg_aladin -ref {0} -flo {1} -aff {2} -res {3}'.format(pfi_anatomy,
                                                                      out_anatomical_flipped_path,
                                                                      out_affine_transf_path,
                                                                      out_anatomical_flipped_warped_path)
        print('Registration started!\n')
        os.system(cmd)

        # propagate the registration to the flipped labels
        out_labels_side_B_path = os.path.join(pfo_results, 'z_labels_side_B.nii.gz')
        cmd = 'reg_resample -ref {0} -flo {1} ' \
          '-res {2} -trans {3} -inter {4}'.format(out_labels_side_A_path,
                                                   out_labels_flipped_path,
                                                   out_labels_side_B_path,
                                                   out_affine_transf_path,
                                                   0)

        print('Resampling started!\n')
        os.system(cmd)
    else:
        out_labels_side_B_path = os.path.join(pfo_results, 'z_labels_side_B.nii.gz')

    # update labels of the side B if necessarily
    if list_labels_transformed is not None:

        print('relabelling step!')

        assert len(list_labels_transformed) == len(list_labels_input)
        relabeller_path(out_labels_side_B_path, out_labels_side_B_path,
                        list_old_labels=list_labels_input,
                        list_new_labels=list_labels_transformed)

    # --- Merge side A and side B in a single volume according to a criteria --- #
    # out_labels_side_A_path,  out_labels_side_B_path --> result_path.nii.gz

    nib_side_A = nib.load(out_labels_side_A_path)
    nib_side_B = nib.load(out_labels_side_B_path)

    data_side_A = nib_side_A.get_data()
    data_side_B = nib_side_B.get_data()

    symmetrised_data = np.zeros_like(data_side_A)

    # vectorize later!
    dims = data_side_A.shape

    print('Pointwise symmetrisation started!')

    for z in xrange(dims[0]):
        for x in xrange(dims[1]):
            for y in xrange(dims[2]):
                if (data_side_A[z, x, y] == 0 and data_side_B[z, x, y] != 0) or \
                   (data_side_A[z, x, y] != 0 and data_side_B[z, x, y] == 0):
                    symmetrised_data[z, x, y] = np.max([data_side_A[z, x, y], data_side_B[z, x, y]])
                elif data_side_A[z, x, y] != 0 and data_side_B[z, x, y] != 0:
                    if data_side_A[z, x, y] == data_side_B[z, x, y]:
                        symmetrised_data[z, x, y] = data_side_A[z, x, y]
                    else:
                        symmetrised_data[z, x, y] = 255  # devil label!

    im_symmetrised = set_new_data(nib_side_A, symmetrised_data)
    nib.save(im_symmetrised, pfi_result_segmentation)
