import os
import numpy as np
import nibabel as nib

from tools.auxiliary.utils import set_new_data


def squeeze_image_from_path(path_input_image, path_output_image, copy_anyway=False):
    """
    copy the image in a new one with the dimension of the data squeezed.
    :param path_input_image: 
    :param path_output_image:
    :param copy_anyway: if the image does not need to be squeezed, it is anyway copied in the
    path_output_image. Option that can be useful in some pipeline
    """
    im = nib.load(path_input_image)
    print('Input image dimensions: {0}.'.format(str(im.shape)))

    if 1 in list(im.shape):
        new_im = set_new_data(im, np.squeeze(im.get_data()[:]))
        nib.save(new_im, path_output_image)
        print('New image dimensions: {0}, saved in {1}'.format(str(new_im.shape), str(path_output_image)))
    else:
        print('No need to squeeze the input image.')
        if copy_anyway:
            cmd = 'cp {0} {1} '.format(path_input_image, path_output_image)
            os.system(cmd)
            return 'Already squeezed image copied in {0} '.format(path_output_image)
