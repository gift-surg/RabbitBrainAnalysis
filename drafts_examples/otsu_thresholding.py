import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np

from skimage import data
try:
    from skimage import filters
except ImportError:
    from skimage import filter as filters
from skimage import exposure


def otsu_multi(image, classes=3, no_of_bins=256):

    hist, bin_edges = np.histogram(image.ravel(), no_of_bins)
    total_voxel = np.prod(image.shape)

    bin_centers = list(0.5 * (bin_edges[:-1] + bin_edges[1:]))

    intra_class_variances = []

    for threshold in range(0, no_of_bins):
        # first we try to find the weight and variance on the background
        sum_background = float(sum(hist[0:threshold]))
        weight_background = sum_background / total_voxel
        mean_background = 0.0
        variance_background = 0.0

        if sum_background > 0.0:  # avoid division by zero
            for x in range(0, threshold):
                mean_background += x * hist[x]
            mean_background /= sum_background

            for x in range(0, threshold):
                variance_background += (x - mean_background) ** 2 * hist[x]
            variance_background /= sum_background

        # then we do it for the foreground
        sum_foreground = float(sum(hist[threshold:no_of_bins]))
        weight_foreground = sum_foreground / total_voxel
        mean_foreground = 0.0
        variance_foreground = 0.0

        if sum_foreground > 0.0:
            for x in range(threshold, no_of_bins):
                mean_foreground += x * hist[x]
            mean_foreground /= sum_foreground

            for x in range(threshold, no_of_bins):
                variance_foreground += (x - mean_foreground) ** 2 * hist[x]
            variance_foreground /= sum_foreground

        # find the variances within these two classes
        intra_class_variances.append(weight_background * variance_background + weight_foreground * variance_foreground)

    # use the threshold that has the minimum intra class variance
    return bin_centers[np.argmin(intra_class_variances) -1]


camera = data.camera()
val = filters.threshold_otsu(camera)

hist, bins_center = exposure.histogram(camera)

plt.figure(figsize=(9, 4))
plt.subplot(131)
plt.imshow(camera, cmap='gray', interpolation='nearest')
plt.axis('off')
plt.subplot(132)
plt.imshow(camera < val, cmap='gray', interpolation='nearest')
plt.axis('off')
plt.subplot(133)
plt.plot(bins_center, hist, lw=2)
plt.axvline(val, color='k', ls='--')

plt.tight_layout()
# plt.show(block=False)

pfi_im_test = '/Users/sebastiano/Desktop/3301_DWI_S0_to_std.nii.gz'

im = nib.load(pfi_im_test)
val = filters.threshold_otsu(im.get_data())
print val

val2 = otsu_multi(im.get_data())
print val2

