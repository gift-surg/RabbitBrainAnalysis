import nibabel as nib
import numpy as np

from tools.auxiliary.utils import set_new_data


def normalise_image_for_the_median(pfi_in_image, pfi_out_iamge, exclude_zeros=True):

    im = nib.load(pfi_in_image)
    im_data = im.get_data()

    if exclude_zeros:
        median = np.median(np.array([i for i in np.trim_zeros(im_data.flatten()) if i != 0]))
    else:
        median = np.median(im_data.flatten())

    print median
    normalised_data = (1 / float(median)) * im_data

    out_im = set_new_data(im, normalised_data)
    nib.save(out_im, pfi_out_iamge)
