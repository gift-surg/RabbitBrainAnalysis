import numpy as np
import os
import nibabel as nib
from scipy import ndimage as ndi
from skimage.feature import peak_local_max
from skimage.morphology import watershed, disk
from skimage.filters import rank, sobel
from skimage.util import img_as_ubyte

from definitions import root_path_data
from tools.auxiliary.utils import set_new_data

from tools.visualisers.see_volume import see_array



main_path = os.path.join(root_path_data, 'pipelines', 'zz_visual_assessment', 'compare_in_skull_ex_skull')

input_image_path = os.path.join(main_path, 'subj_1702.nii.gz')
output_image_path = os.path.join(main_path, 'subj_1702_wat.nii.gz')

output_markers_path = os.path.join(main_path, 'subj_1702_markers.nii.gz')


im = nib.load(input_image_path)

# extract the matrix:
im_data = im.get_data().astype('float64')
im_data = (255/np.max(im_data)) * im_data

im_data = img_as_ubyte(im_data.astype('uint8'))

print np.max(im_data)
print np.min(im_data)
print im_data.dtype

#see_array(im_data, block=True, title='initial image')

# denoised image
denoised = np.zeros_like(im_data)

for pln, image in enumerate(im_data):
    denoised[pln] = rank.median(image, disk(2))

#see_array(denoised, block=True, title='image denoised')

# get markers
markers = np.zeros_like(denoised)

for pln, image in enumerate(denoised):
    markers[pln] = rank.gradient(image, disk(5)) < 10

markers = ndi.label(markers)[0]

print 'spam'
print np.max(markers)
print np.min(markers)

markers_im = set_new_data(im, markers)
nib.save(markers_im, output_markers_path)

see_array(markers, block=True, title='image markers')

# get gradient:
gradient = np.zeros_like(denoised)

for pln, image in enumerate(denoised):
    gradient[pln] = rank.gradient(image, disk(2))

#see_array(gradient, block=True, title='image gradient, gradient')


# get gradient with a sobel filter:

edges_data = np.zeros_like(im_data)

# sobel is for 2d only. Need this trick for the 3d case:
for pln, image in enumerate(im_data):
    edges_data[pln] = sobel(image)
    # edges_data[pln] = filters.roberts(image)

#see_array(edges_data, block=True, title='image gradient Sobel')

# process the watershed
wat_data = watershed(edges_data, markers)  # edge data or gradient

see_array(wat_data, block=True, title='watershed')

# Save as external image
new_im = set_new_data(im, wat_data)
nib.save(new_im, output_image_path)
