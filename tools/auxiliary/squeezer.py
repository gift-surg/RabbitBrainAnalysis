import numpy as np
import nibabel as nib
import os 

from tools.auxiliary.utils import set_new_data


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
        nib.save(new_im, path_output_image)
        print('New image dimensions: ' + str(new_im.shape) + ', saved in ' + str(path_output_image))
    else:
        print('No need to squeeze the input image.')
