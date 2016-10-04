import numpy as np
import nibabel as nib
import os 


def set_new_data(image, new_data):
    """
    From an image and a numpy array it creates a new image with
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
        new_image = nib.Nifti12mage(new_data, image.affine, header=image.header)
    # update data type:
    new_image.set_data_dtype(new_data.dtype)
    
    return new_image


def squeeze_image(path_input_image, path_output_image):
    """
    copy the image in a new one with the dimension of the data squeezed.
    :param path_input_image: 
    :param path_output_image:
    """
    im = nib.load(path_input_image)
    print('Input image dimensions: ' + str(im.shape))

    if 1 in list(im.shape):
        new_im = set_new_data(im, np.squeeze(im.get_data()[:]))
        nib.save(new_im, path_new_image)
        print('New image dimensions: ' + new_im.shape + ', saved in ' + str(path_output_image))
    else:
    	print('No need to squeeze the input image.')


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



