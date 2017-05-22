import numpy as np
import nibabel as nib
import os


def set_new_data(image, new_data, new_dtype=None, remove_nan=True):
    """
    From a nibabel image and a numpy array it creates a new image with
    the same header of the image and the new_data as its data.
    :param image: nibabel image
    :param new_data: numpy array
    :return: nibabel image
    """
    if remove_nan:
        new_data = np.nan_to_num(new_data)

    # if nifty1
    if image.header['sizeof_hdr'] == 348:
        new_image = nib.Nifti1Image(new_data, image.affine, header=image.header)
    # if nifty2
    elif image.header['sizeof_hdr'] == 540:
        new_image = nib.Nifti2Image(new_data, image.affine, header=image.header)
    else:
        raise IOError('Input image header problem')

    # update data type:
    if new_dtype is None:
        new_image.set_data_dtype(new_data.dtype)
    else:
        new_image.set_data_dtype(new_dtype)

    return new_image


def set_new_data_path(pfi_target_im, pfi_image_where_the_new_data, pfi_result, new_dtype=None, remove_nan=True):

    image = nib.load(pfi_target_im)
    new_data = nib.load(pfi_image_where_the_new_data).get_data()
    new_image = set_new_data(image, new_data, new_dtype=new_dtype, remove_nan=remove_nan)
    nib.save(new_image, filename=pfi_result)


def set_new_dtype_path(pfi_in, pfi_out, new_dtype):

    im = nib.load(pfi_in)
    im_new_type = set_new_data(im, im.get_data(), new_dtype=new_dtype)
    print im_new_type.shape
    print im_new_type.get_data_dtype()
    nib.save(im_new_type, pfi_out)
    print('image {0} saved to {1} with new datatype {2}'.format(pfi_in, pfi_out, new_dtype))


def change_something_in_the_header(pfi_input, pfi_output, something='datatype', new_value_for_something=np.array(512, dtype=np.int16)):
    """
    default values to have the data converted in uint16
    """
    im_input = nib.load(pfi_input)
    im_header= im_input.header
    im_header[something] = new_value_for_something
    nib.save(im_input, pfi_output)


def compose_aff_transf_from_paths(pfi_left_aff, pfi_right_aff, pfi_final):
    for pfi in [pfi_left_aff, pfi_right_aff]:
        if not os.path.exists(pfi):
            raise IOError()
    left = np.loadtxt(pfi_left_aff)
    right = np.loadtxt(pfi_right_aff)
    np.savetxt(pfi_final, left.dot(right))


def compare_two_nib(im1, im2, toll=1e-3):
    """
    :param im1: one nibabel image
    :param im2: another nibabel image
    :param toll: tolerance to the dissimilarity in the data - if headers are different images are different.
    :return: true false and plot to console if the images are the same or not (up to a tollerance in the data)
    """

    im1_name = 'First argument'
    im2_name = 'Second argument'

    hd1 = im1.header
    hd2 = im1.header

    images_are_equals = True

    # compare nifty version:
    if not hd1['sizeof_hdr'] == hd2['sizeof_hdr']:

        if hd1['sizeof_hdr'] == 348:
            msg = '{0} is nifty1\n{1} is nifty2.'.format(im1_name, im2_name)
        else:
            msg = '{0} is nifty2\n{1} is nifty1.'.format(im1_name, im2_name)
        print msg

        images_are_equals = False

    # Compare headers:

    for k in hd1.keys():
        if k not in ['scl_slope', 'scl_inter']:
            val1, val2 = hd1[k], hd2[k]
            are_different = val1 != val2
            if isinstance(val1, np.ndarray):
                are_different = are_different.any()

            if are_different:
                images_are_equals = False
                print(k, hd1[k])

        elif not np.isnan(hd1[k]) and np.isnan(hd2[k]):
            images_are_equals = False
            print(k, hd1[k])

    '''
    # Compare values and type:

    im1_data = im1.get_data()
    im2_data = im2.get_data()

    if not im1_data.dtype == im2_data.dtype:
        images_are_equals = False

    # Compare values
    if np.max(im1_data - im2_data) > toll:
        images_are_equals = False
    '''

    return images_are_equals


def compare_two_nifti(path_img_1, path_img_2):
    """
    ... assuming nibabel take into account all the information in the nifty header properly!
    :param path_img_1:
    :param path_img_2:
    :return:
    """
    im1 = nib.load(path_img_1)
    im2 = nib.load(path_img_2)

    return compare_two_nib(im1, im2)


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


def eliminates_consecutive_duplicates(input_list):
    output_list = [input_list[0], ]
    for i in range(1, len(input_list)):
        if not input_list[i] == input_list[i-1]:
            output_list.append(input_list[i])

    return output_list


def scan_and_remove_path(msg):
    """
    Take a string with paths and removes all the paths.
    """
    a = [os.path.basename(p) for p in msg.split(' ')]
    return ' '.join(a)


def print_and_run(cmd, msg=None, safety_on=True):
    """
    run the command to console and print the message.
    if msg is None print the command itself.
    :param cmd: command for the terminal
    :param msg: message to show before running the command
    on the top of the command itself.
    :param safety_on: safety, in case you want to see the messages at a first run.
    :return:
    """

    # if len(cmd) > 249:
    #     print(cmd)
    #     raise IOError('input command is too long, this may create problems. Please use shortest names!')

    path_free_cmd = scan_and_remove_path(cmd)
    if msg is not None:
        print '\n' + msg + '\n'
    else:
        print '\n' + path_free_cmd + '\n'

    if not safety_on:
        os.system(cmd)


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
    new_transf[1, 1] = new_transf[0, 0] / squeeze_factor

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
