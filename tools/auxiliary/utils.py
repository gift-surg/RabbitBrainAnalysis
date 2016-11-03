import numpy as np
import nibabel as nib
import os 


def set_new_data(image, new_data):
    """
    From a nibabel image and a numpy array it creates a new image with
    the same header of the image and the new_data as its data.
    :param image: nibabel image
    :param new_data: numpy array 
    :return: nibabel image
    """
    # if nifty1
    if image.header['sizeof_hdr'] == 348:
        new_image = nib.Nifti1Image(new_data, image.affine, header=image.header)
    # if nifty2
    elif image.header['sizeof_hdr'] == 540:
        new_image = nib.Nifti2Image(new_data, image.affine, header=image.header)
    else:
        raise IOError('input_image_problem')
    # update data type:
    new_image.set_data_dtype(new_data.dtype)

    return new_image


def label_selector(path_input_image, path_output_image, labels_to_keep, binarize=True):
    """
    Given an label of image and a list of labels to keep, a new image with only the labels to keep will be created.
    New image can still have the original labels, or can binarize them.
    :param path_input_image: 
    :param path_output_image:
    :param labels to keep: list of labels
    :param binarize: True if you want the output to be a binary images. Original labels are otherwise kept.  
    """
    im = nib.load(path_input_image)
    im_data = im.get_data()[:]
    new_data = np.zeros_like(im_data)

    for i in range(im_data.shape[0]):
        for j in range(im_data.shape[1]):
            for k in range(im_data.shape[2]):   
                if im_data[i,j,k] in labels_to_keep:
                    if binarize:
                        new_data[i,j,k] = 1
                    else:
                        new_data[i,j,k] = im_data[i,j,k]

    new_im = set_new_data(im, new_data)
    nib.save(new_im, path_output_image)
    print('Output image saved in ' + str(path_output_image))


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
