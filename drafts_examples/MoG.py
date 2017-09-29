import numpy as np
from scipy import ndimage
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from sklearn.mixture import GaussianMixture

from skimage import data


# np.random.seed(1)
# n = 10
# l = 256
# im = np.zeros((l, l))
# points = l*np.random.random((2, n**2))
# im[(points[0]).astype(np.int), (points[1]).astype(np.int)] = 1
# points = l*np.random.random((2, n**2))
# im[(points[0]).astype(np.int), (points[1]).astype(np.int)] = 2
#
# im = ndimage.gaussian_filter(im, sigma=l/(4.*n))
#
# #mask = (im > im.mean()).astype(np.float)
#
#
# img = im  # mask + 0.3*np.random.randn(*mask.shape)

img = data.camera()


hist, bin_edges = np.histogram(img, bins=60)
bin_centers = 0.5*(bin_edges[:-1] + bin_edges[1:])

classif = GaussianMixture(n_components=2)
classif.fit(img.reshape((img.size, 1)))

thresholds_mu = classif.means_.flatten()
thresholds_std = classif.covariances_.flatten()

thresholds_mu_sorted = np.sort(thresholds_mu)
binary_img1 = img < thresholds_mu_sorted[0]
comp_1 = img > thresholds_mu_sorted[0]
comp_2 = img < thresholds_mu_sorted[1]
binary_img2 = comp_1 * comp_2
# binary_img3 = img > thresholds_mu_sorted[2]

plt.figure(1, figsize=(15, 4))

plt.subplot(151)
plt.imshow(img)
plt.axis('off')
plt.subplot(152)
plt.plot(bin_centers, hist, lw=2)
plt.axvline(thresholds_mu[0], color='r', ls='--', lw=2)
plt.axvline(thresholds_mu[1], color='b', ls='--', lw=2)
# plt.axvline(thresholds_mu[2], color='g', ls='--', lw=2)
plt.text(0.57, 0.8, 'histogram', fontsize=20, transform=plt.gca().transAxes)
plt.yticks([])
plt.subplot(153)
plt.imshow(binary_img1, cmap=plt.cm.gray, interpolation='nearest')
plt.axis('off')
plt.subplot(154)
plt.imshow(binary_img2, cmap=plt.cm.gray, interpolation='nearest')
plt.axis('off')
# plt.subplot(155)
# plt.imshow(binary_img3, cmap=plt.cm.gray, interpolation='nearest')
plt.axis('off')
plt.subplots_adjust(wspace=0.02, hspace=0.3, top=1, bottom=0.1, left=0, right=1)
# plt.show(block=False)


image_1 = (img > thresholds_mu[0] - np.sqrt(thresholds_std[0])) * (img > thresholds_mu[0] - np.sqrt(thresholds_std[0]))
image_2 = (img > thresholds_mu[1] - np.sqrt(thresholds_std[1])) * (img > thresholds_mu[1] - np.sqrt(thresholds_std[1]))
# image_3 = (img > thresholds_mu[2] - np.sqrt(thresholds_std[2])) * (img > thresholds_mu[2] - np.sqrt(thresholds_std[2]))

plt.figure(2, figsize=(15, 4))
plt.subplot(151)
plt.imshow(img)
plt.axis('off')
plt.subplot(152)
x = np.linspace(0, 256, 256)
colors = ['r', 'g', 'b']
for i in range(2):
    plt.axvline(thresholds_mu[i], color=colors[i], ls='--', lw=1)
    plt.plot(x, mlab.normpdf(x, thresholds_mu[i], np.sqrt(thresholds_std[i])), color=colors[i])
plt.plot(bin_centers, hist / float(np.sum(hist)), lw=1, color='k')
plt.subplot(153)
plt.imshow(image_1, cmap=plt.cm.gray, interpolation='nearest')
plt.axis('off')
plt.subplot(154)
plt.imshow(image_2, cmap=plt.cm.gray, interpolation='nearest')
plt.axis('off')
# plt.subplot(155)
# plt.imshow(image_3, cmap=plt.cm.gray, interpolation='nearest')
plt.axis('off')
plt.subplots_adjust(wspace=0.02, hspace=0.3, top=1, bottom=0.1, left=0, right=1)
plt.show(block=True)

