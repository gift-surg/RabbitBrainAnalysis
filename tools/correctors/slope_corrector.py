import numpy as np
import argparse
import textwrap
import os
import nibabel as nib
from tools.auxiliary.utils import set_new_data


def slope_corrector(slopes, im_input):
    """
    Correct from the slopes from the slope array and the image.
    :param slopes:
    :param im_input:
    :return:
    """
    im_data = im_input.get_data().astype(np.float64)
    num_directions = len(slopes)

    if not (im_data.shape[3] == num_directions or im_data.shape[4] == num_directions):
        err_msg = 'ERROR: Dimension of the given image scale not coherent with the given image.'
        raise IOError(err_msg)

    for j in range(num_directions):
        im_data[..., j] *= slopes[j]

    im_output = set_new_data(im_input, im_data)
    return im_output


def slope_corrector_path(slopes_txt_path, path_im_input, path_im_output):
    """
    Correct for the slope from the path of the elements
    :param slopes_txt_path:
    :param path_im_input:
    :param path_im_output:
    :return:
    """
    im_input = nib.load(path_im_input)
    slopes = np.loadtxt(slopes_txt_path)

    im_output = slope_corrector(slopes, im_input)

    nib.save(im_output, path_im_output)

    msg = 'Scaled image saved in ' + path_im_output
    print(msg)
