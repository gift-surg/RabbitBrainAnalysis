import numpy as np
import nibabel as nib

from LABelsToolkit.tools.aux_methods.utils import eliminates_consecutive_duplicates
from LABelsToolkit.tools.aux_methods.utils_nib import set_new_data
from bruker2nifti._utils import data_corrector


# def slope_corrector_old(slopes, im_input, eliminate_consec_duplicates=False):
#     """
#     Correct from the slopes from the slope array and the image.
#     :param slopes:
#     :param im_input:
#     :return:
#     """
#
#     if eliminate_consec_duplicates:
#         slopes = eliminates_consecutive_duplicates(list(np.loadtxt(slopes)))
#
#     im_data = im_input.get_data().astype(np.float64)
#     num_directions = len(slopes)
#
#     if not (im_data.shape[3] == num_directions):  #  or im_data.shape[4] == num_directions
#         err_msg = 'ERROR: Dimension of the given image scale not coherent with the given image.'
#         raise IOError(err_msg)
#
#     for j in xrange(num_directions):
#         print j
#         im_data[..., j] *= slopes[j]
#
#     im_output = set_new_data(im_input, im_data)
#     return im_output


def slope_corrector_path(slopes_array, path_im_input, path_im_output, eliminate_consec_duplicates=False):
    """
    Correct for the slope from the path of the elements
    :param slopes_array:
    :param path_im_input:
    :param path_im_output:
    :param eliminate_consec_duplicates:
    :return:
    """
    im_input = nib.load(path_im_input)
    # slopes = np.loadtxt(slopes_txt_path)
    if eliminate_consec_duplicates:
        slopes_array = np.array(eliminates_consecutive_duplicates(list(slopes_array)))
    data_output = data_corrector(im_input.get_data(), slopes_array, kind='slope')
    im_output = set_new_data(im_input, data_output)
    nib.save(im_output, path_im_output)
    msg = 'Scaled image saved in ' + path_im_output
    print(msg)