import numpy as np
import argparse
import textwrap
import os
import nibabel as nib
from tools.auxiliary.utils import set_new_data



def slope_corrector(slopes_txt_file, im_input, im_output):
    """
    Core of the slope correction.
    :param slopes_file:
    :param im_input:
    :return:
    """
    slopes = np.loadtxt(slopes_txt_file)
    im_data = im_input.get_data().astype(np.float64)
    num_directions = len(slopes)

    if not (im_data.shape[3] == num_directions or im_data.shape[4] == num_directions):
        err_msg = 'ERROR: Dimension of the given image scale not coherent with the given image.'
        raise IOError(err_msg)

    for j in range(num_directions):
        im_data[...,j] *=  slopes[j]

    nib.save(set_new_data(im_input, im_data), im_output)

    msg = 'Scaled image saved in ' + im_output
    print(msg)
