import numpy as np
import os
import nibabel as nib
from skimage import filters

from definitions import root_path_data
from tools.auxiliary.utils import set_new_data


main_path = os.path.join(root_path_data, 'pipelines', 'zz_visual_assessment', 'compare_in_skull_ex_skull')

input_image_path = os.path.join(main_path, 'subj_1702.nii.gz')
output_image_path = os.path.join(main_path, 'subj_1702_edges.nii.gz')

im = nib.load(input_image_path)

im_data = im.get_data().astype('float64')

edges_data = np.zeros_like(im_data)

# sobel is for 2d only. Need this trick for the 3d case:
for pln, image in enumerate(im_data):
    edges_data[pln] = filters.sobel(image)
    # edges_data[pln] = filters.roberts(image)

new_im = set_new_data(im, edges_data)

nib.save(new_im, output_image_path)
