import numpy as np
import nibabel as nib
import os
import subprocess
import time

from nilabels.tools.aux_methods.utils_nib import set_new_data


# def set_new_data(image, new_data, new_dtype=None, remove_nan=True):
#     """
#     From a nibabel image and a numpy array it creates a new image with
#     the same header of the image and the new_data as its data.
#     :param image: nibabel image
#     :apram new_data:
#     :param new_dtype: numpy array
#     :param remove_nan:
#     :return: nibabel image
#     """
#     if remove_nan:
#         new_data = np.nan_to_num(new_data)
#
#     # update data type:
#     if new_dtype is not None:
#         new_data.astype(new_dtype)
#
#     # if nifty1
#     if image.header['sizeof_hdr'] == 348:
#         new_image = nib.Nifti1Image(new_data, image.affine, header=image.header)
#     # if nifty2
#     elif image.header['sizeof_hdr'] == 540:
#         new_image = nib.Nifti2Image(new_data, image.affine, header=image.header)
#     else:
#         raise IOError('Input image header problem')
#
#     # # update data type:
#     # if new_dtype is None:
#     #     new_image.set_data_dtype(new_data.dtype)
#     # else:
#     #     new_image.set_data_dtype(new_dtype)
#
#     return new_image



def triangular_density_function(x, a, mu, b):

    if a <= x < mu:
        return 2 * (x - a) / float((b - a) * (mu - a))
    elif x == mu:
        return 2 / float(b - a)
    elif mu < x <= b:
        return 2 * (b - x) / float((b - a) * (b - mu))
    else:
        return 0


def set_new_data_path(pfi_target_im, pfi_image_where_the_new_data, pfi_result, new_dtype=None, remove_nan=True):

    # if pfi_image_where_the_new_data == pfi_result:
    #     raise IOError('pfi_image_where_the_new_data must be different from pfi_result to avoid bugs')
    image = nib.load(pfi_target_im)
    new_data = nib.load(pfi_image_where_the_new_data).get_data()
    new_image = set_new_data(image, new_data, new_dtype=new_dtype, remove_nan=remove_nan)
    nib.save(new_image, filename=pfi_result)


def compose_aff_transf_from_paths(pfi_left_aff, pfi_right_aff, pfi_final):
    for pfi in [pfi_left_aff, pfi_right_aff]:
        if not os.path.exists(pfi):
            raise IOError()
    left = np.loadtxt(pfi_left_aff)
    right = np.loadtxt(pfi_right_aff)
    np.savetxt(pfi_final, left.dot(right))


def reproduce_slice_fourth_dimension(nib_image, num_slices=10, repetition_axis=3):

    im_sh = nib_image.shape
    if not (len(im_sh) == 2 or len(im_sh) == 3):
        raise IOError('Methods can be used only for 2 or 3 dim images. No conflicts with existing multi, slices')

    new_data = np.stack([nib_image.get_data(), ] * num_slices, axis=repetition_axis)
    output_im = set_new_data(nib_image, new_data)

    return output_im


def reproduce_slice_fourth_dimension_path(pfi_input_image, pfi_output_image, num_slices=10, repetition_axis=3):
    old_im = nib.load(pfi_input_image)
    new_im = reproduce_slice_fourth_dimension(old_im, num_slices=num_slices, repetition_axis=repetition_axis)
    nib.save(new_im, pfi_output_image)
    print 'New image created and saved in {0}'.format(pfi_output_image)


def grab_a_timepoint(input_4d_im, t=0):
    assert t < input_4d_im.shape[3]
    return set_new_data(input_4d_im, input_4d_im.get_data()[..., t])


def grab_a_timepoint_path(path_input_4d_im, path_output_single_timepoint, t=0):

    im = nib.load(path_input_4d_im)
    im_output = grab_a_timepoint(im, t=t)
    nib.save(im_output, path_output_single_timepoint)


def cut_dwi_image_from_first_slice_mask(input_dwi, input_mask):

    data_masked_dw = np.zeros(input_dwi.shape, dtype=input_dwi.get_data_dtype())
    print data_masked_dw.shape

    for t in range(input_dwi.shape[-1]):
        print 'cut_dwi_image_from_first_slice_mask, slice processed: ' + str(t)
        data_masked_dw[..., t] = np.multiply(input_mask.get_data(), input_dwi.get_data()[..., t])

    # image with header of the dwi and values under the mask for each slice:
    return set_new_data(input_dwi, data_masked_dw)


def cut_dwi_image_from_first_slice_mask_path(path_input_dwi, path_input_mask, path_output_masked_dwi):

    im_dwi = nib.load(path_input_dwi)
    im_mask = nib.load(path_input_mask)

    im_masked = cut_dwi_image_from_first_slice_mask(im_dwi, im_mask)

    nib.save(im_masked, path_output_masked_dwi)


def scan_and_remove_path(msg):
    """
    Take a string with a series of paths separated by a space and keeps only the base-names of each path.
    """
    a = [os.path.basename(p) for p in msg.split(' ')]
    return ' '.join(a)


def print_and_run(cmd, msg=None, safety_on=False, short_path_output=True):
    """
    run the command to console and print the message.
    if msg is None print the command itself.
    :param cmd: command for the terminal
    :param msg: message to show before running the command
    on the top of the command itself.
    :param short_path_output: the message provided at the prompt has only the filenames without the paths.
    :param safety_on: safety, in case you want to see the messages at a first run.
    :return:
    """

    # if len(cmd) > 249:
    #     print(cmd)
    #     raise IOError('input command is too long, this may create problems. Please use shortest names!')
    if short_path_output:
        path_free_cmd = scan_and_remove_path(cmd)
    else:
        path_free_cmd = cmd

    if msg is not None:
        print '\n' + msg + '\n'
    else:
        print '\n-> ' + path_free_cmd + '\n'

    if not safety_on:
        # os.system(cmd)
        subprocess.call(cmd, shell=True)


def adjust_header_from_transformations(pfi_input, pfi_output, theta, trasl):

    # transformations parameters
    rot_x = np.array([[1,            0,           0,     trasl[0]],
                     [0,  np.cos(theta),  -np.sin(theta),     trasl[1]],
                     [0,  np.sin(theta), np.cos(theta),   trasl[2]],
                     [0,             0,          0,      1]])

    # Load input image:
    im_input = nib.load(pfi_input)

    # generate new affine transformation (from bicommissural to histological)
    new_transf = rot_x.dot(im_input.get_affine())

    # create output image on the input
    if im_input.header['sizeof_hdr'] == 348:
        new_image = nib.Nifti1Image(im_input.get_data(), new_transf, header=im_input.get_header())
    # if nifty2
    elif im_input.header['sizeof_hdr'] == 540:
        new_image = nib.Nifti2Image(im_input.get_data(), new_transf, header=im_input.get_header())
    else:
        raise IOError

    # print intermediate results
    print 'Affine input image: \n'
    print im_input.get_affine()
    print 'Affine after transformation: \n'
    print new_image.get_affine()

    # sanity check
    np.testing.assert_almost_equal(np.linalg.det(new_transf), np.linalg.det(im_input.get_affine()))

    # save output image
    nib.save(new_image, pfi_output)


def scale_z_values(pfi_input, pfi_output, squeeze_factor=2.218074656188605):
    # the input must be oriented to standard with FSL!
    # we assume and confirm some sort of aniotropcit
    # Load input image:
    im_input = nib.load(pfi_input)

    assert np.count_nonzero(np.diag(im_input.get_affine())) == 4

    # generate new affine transformation (from bicommissural to histological)
    new_transf = np.copy(im_input.get_affine())
    new_transf[2, 2] = new_transf[1, 1] / squeeze_factor

    # create output image on the input
    if im_input.header['sizeof_hdr'] == 348:
        new_image = nib.Nifti1Image(im_input.get_data(), new_transf, header=im_input.get_header())
    # if nifty2
    elif im_input.header['sizeof_hdr'] == 540:
        new_image = nib.Nifti2Image(im_input.get_data(), new_transf, header=im_input.get_header())
    else:
        raise IOError

    # print intermediate results
    print 'Unsquashing z coordinate:'
    print 'Affine input image: \n'
    print im_input.get_affine()
    print 'Affine after transformation: \n'
    print new_image.get_affine()

    # save output image
    nib.save(new_image, pfi_output)


def scale_y_values(pfi_input, pfi_output, squeeze_factor=2.16481481481481):
    # the input must be oriented to standard with FSL!
    # we assume and confirm some sort of aniotropcit
    # Load input image:
    im_input = nib.load(pfi_input)

    assert np.count_nonzero(np.diag(im_input.get_affine())) == 4

    # generate new affine transformation (from bicommissural to histological)
    new_transf = np.copy(im_input.get_affine())
    new_transf[1, 1] = new_transf[0, 0] * squeeze_factor

    # create output image on the input
    if im_input.header['sizeof_hdr'] == 348:
        new_image = nib.Nifti1Image(im_input.get_data(), new_transf, header=im_input.get_header())
    # if nifty2
    elif im_input.header['sizeof_hdr'] == 540:
        new_image = nib.Nifti2Image(im_input.get_data(), new_transf, header=im_input.get_header())
    else:
        raise IOError

    # print intermediate results
    print 'Unsquashing z coordinate:'
    print 'Affine input image: \n'
    print im_input.get_affine()
    print 'Affine after transformation: \n'
    print new_image.get_affine()

    # save output image
    nib.save(new_image, pfi_output)


def scale_y_value_and_trim(pfi_input, pfi_output, squeeze_factor=2):
    # Squeeze factor: as measured : 2.16481481481481 as provided by Willy : 2
    # scale and trim as well.
    im_input = nib.load(pfi_input)

    assert np.count_nonzero(np.diag(im_input.get_affine())) == 4

    # generate new affine transformation (from bicommissural to histological)
    new_transf = np.copy(im_input.get_affine())
    old_resolution = new_transf[0, 0]
    new_resolution = old_resolution * squeeze_factor
    new_transf[1, 1] = new_resolution

    old_y_side = old_resolution * im_input.shape[1]
    num_voxel_to_take = np.floor(old_y_side / float(new_resolution))

    half = int(np.ceil(num_voxel_to_take/float(2)))
    mid_point = int(im_input.shape[1] / float(2))
    # create output image on the input
    if im_input.header['sizeof_hdr'] == 348:
        new_image = nib.Nifti1Image(im_input.get_data()[:, mid_point - half:mid_point + half, ...], new_transf,
                                    header=im_input.get_header())
    # if nifty2
    elif im_input.header['sizeof_hdr'] == 540:
        new_image = nib.Nifti2Image(im_input.get_data()[:, mid_point - half: mid_point + half, ...], new_transf,
                                    header=im_input.get_header())
    else:
        raise IOError

    # print intermediate results
    print 'Unsquashing z coordinate:'
    print 'Affine input image: \n'
    print im_input.get_affine()
    print 'Affine after transformation: \n'
    print new_image.get_affine()

    # save output image
    nib.save(new_image, pfi_output)
