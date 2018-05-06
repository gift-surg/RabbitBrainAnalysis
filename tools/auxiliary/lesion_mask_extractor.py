import os
import numpy as np
import nibabel as nib
from scipy.stats import norm
import matplotlib.pyplot as plt
import matplotlib.mlab as mlab
from sklearn.mixture import GaussianMixture
from scipy.signal import medfilt

from LABelsToolkit.tools.aux_methods.utils_nib import set_new_data
from tools.definitions import root_dir
from tools.auxiliary.utils import print_and_run


def filter_connected_components_by_volume(im_input, num_cc_to_filter=10):
    """
    Given a mask image (volex values are integers from 1 to something), it takes the num_cc_to_filter with maximal
    volume and it relabels them from 1 to num_cc_to_filter, where 1 is the component with the biggest volume.
    If components are connected then it will provides the first num_cc_to_filter connected components divided by
    volumes.
    :param im_input: mask
    :param num_cc_to_filter:
    :return:
    """

    im_data = im_input.get_data().astype(np.int32)

    new_data = np.zeros_like(im_data)

    volumes_per_label = [0,] * np.max(im_data)

    print np.max(im_data)

    dim_x, dim_y, dim_z = list(im_data.shape)

    for i in xrange(dim_x):
        for j in xrange(dim_y):
            for k in xrange(dim_z):
                if im_data[i, j, k] > 0:
                    volumes_per_label[im_data[i, j, k] - 1] += 1

    list_volumes_copy = volumes_per_label[:]
    max_volumes = []
    max_labels = []

    for m in range(num_cc_to_filter):
        max_value = max(list_volumes_copy)
        max_index = list_volumes_copy.index(max_value)

        max_volumes += [max_value]
        max_labels += [max_index + 1]

        list_volumes_copy[max_index] = 0
        print
        print m
        print list_volumes_copy

    for i in xrange(dim_x):
        for j in xrange(dim_y):
            for k in xrange(dim_z):
                if im_data[i, j, k] in max_labels:
                    new_data[i, j, k] = max_labels.index(im_data[i, j, k]) + 1

    im_output = set_new_data(im_input, new_data)
    return im_output


def filter_connected_components_by_volume_path(im_input_path, im_output_path, num_cc_to_filter=10):

    im_input = nib.load(im_input_path)
    im_output = filter_connected_components_by_volume(im_input, num_cc_to_filter=num_cc_to_filter)
    nib.save(im_output, im_output_path)


def test_lesion_masks_extractor_for_simple_input():
    # Test for filter_connected_components.
    cmd = 'mkdir -p {0}'.format(os.path.join(root_dir, 'output'))
    print_and_run(cmd)

    dims = [105, 20, 20]

    im_data = np.zeros([dims[1], dims[2], 1])
    intervals = [50, 10, 50, 20, 25]
    weights   = [12, 2, 3, 4, 5]

    for i in range(len(intervals)):
        slice = weights[i] * np.ones([dims[1], dims[2], intervals[i]])
        im_data = np.concatenate((im_data, slice), axis=2)

    im = nib.Nifti1Image(im_data, np.eye(4))
    nib.save(im, os.path.join(root_dir, 'output/test.nii.gz'))

    im_filtered = filter_connected_components_by_volume(im, num_cc_to_filter=3)

    # for the moment visual assessment test!
    nib.save(im_filtered, os.path.join(root_dir, 'output/test_fil.nii.gz'))
    print_and_run('open {}'.format(os.path.join(root_dir, 'output/test_fil.nii.gz')))


def simple_lesion_mask_extractor_path(im_input_path, im_output_path, im_mask_foreground_path, safety_on=False):
    cmd = '''seg_maths {0} -thr 500 {1};
             seg_maths {1} -bin {1};
             seg_maths {1} -add {2} {1};
             seg_maths {1} -replace 2 0 {1};
             seg_maths {1} -fill {1};
             seg_maths {1} -dil 2 {1};
             seg_maths {1} -ero 2 {1};
             seg_maths {1} -smol 1.2 {1};
             seg_maths {1} -dil 1 {1};
             seg_maths {1} -mul {2} {1};
          '''.format(im_input_path, im_output_path, im_mask_foreground_path)

    print cmd

    if not safety_on:
        print_and_run(cmd)


# --- Auxiliaries
def get_percentiles_range(pfi_im_input, percentiles=(15, 95)):
    assert os.path.exists(pfi_im_input)
    im = nib.load(pfi_im_input)
    im_data = im.get_data().flatten()
    non_zero_data = im_data[np.where(np.nan_to_num(im_data) > 1e-6)]
    if len(non_zero_data) > 0:
        low_p = np.percentile(non_zero_data, percentiles[0])
        high_p = np.percentile(non_zero_data, percentiles[1])
        return low_p, high_p
    else:
        print('Warning, image unexpectedly empthy!')
        return 0, 0


def get_normal_interval_range(pfi_im_input, k=1):
    assert os.path.exists(pfi_im_input)
    im = nib.load(pfi_im_input)
    im_data = im.get_data().flatten()
    non_zero_data = im_data[np.where(im_data > 1e-6)]
    mu, std = norm.fit(non_zero_data)
    return mu - k * std,  mu + k * std


def normal_lesion_mask_extractor(im_input_path, im_output_path, im_mask_foreground_path, safety_on=False):
    low_thr, up_thr = get_normal_interval_range(im_input_path)
    cmd = '''seg_maths {0} -thr {3} {1};
             seg_maths {1} -uthr {4} {1};
             seg_maths {1} -bin {1};
             seg_maths {1} -add {2} {1};
             seg_maths {1} -replace 2 0 {1};
             seg_maths {1} -dil 0.5 {1};
             seg_maths {1} -ero 0.5 {1};
             seg_maths {1} -mul {2} {1};
          '''.format(im_input_path, im_output_path, im_mask_foreground_path, low_thr, up_thr)
    print cmd
    if not safety_on:
        print_and_run(cmd)


def percentile_lesion_mask_extractor(im_input_path, im_output_path, im_mask_foreground_path, percentiles,
                                     safety_on=False, median_filter=False, pfo_tmp=None):
    if median_filter:
        im_input_name = os.path.basename(im_input_path).split('.')[0]
        im_input_path_filtered = os.path.join(pfo_tmp, '{}_filtered.nii.gz'.format(im_input_name))
        im = nib.load(im_input_path)
        im_fil = set_new_data(im, medfilt(im.get_data()))
        nib.save(im_fil, im_input_path_filtered)
        im_input_path = im_input_path_filtered

    low_thr, up_thr = get_percentiles_range(im_input_path, percentiles=percentiles)
    cmd = '''seg_maths {0} -thr {3} {1};
             seg_maths {1} -uthr {4} {1};
             seg_maths {1} -bin {1};
             seg_maths {1} -add {2} {1};
             seg_maths {1} -replace 2 0 {1};
             seg_maths {1} -ero 0.7 {1};
             seg_maths {1} -dil 2 {1};
             seg_maths {1} -mul {2} {1};
          '''.format(im_input_path, im_output_path, im_mask_foreground_path, low_thr, up_thr)
    print cmd
    if not safety_on:
        print_and_run(cmd)


def lesion_masks_extractor_cc_based_path(im_input_path, im_output_path, im_mask_foreground_path, safety_on=False):
    """
    Lesion masks are extracted before filtering for connected components.
    :return:
    """
    save_intermediate = True
    cmd1 = '''seg_maths {0} -thr 500 {1};
             seg_maths {1} -bin {1};
             seg_maths {1} -add {2} {1};
             seg_maths {1} -replace 2 0 {1};
             seg_maths {1} -dil 2 {1};
             seg_maths {1} -ero 2 {1};
             seg_maths {1} -concomp6 {1};
          '''.format(im_input_path, im_output_path, im_mask_foreground_path)
    print cmd1
    if not safety_on:
        print_and_run(cmd1)

    print "filtering connected components"
    filter_connected_components_by_volume_path(im_input_path, im_output_path, num_cc_to_filter=10)

    if save_intermediate:
        im_output_path_intermediate = os.path.join(os.path.dirname(im_output_path), 'z_intermediate.nii.gz')
        cmd_mid = 'cp {0} {1}'.format(im_output_path, im_output_path_intermediate)

    cmd2 = '''seg_maths  {0} -smol 1.2 {0};
             seg_maths {0} -dil 1 {0};
             seg_maths {0} -mul {1} {0};
          '''.format(im_output_path, im_mask_foreground_path)

    print cmd2
    if not safety_on:
        print_and_run(cmd2)
    pass


def MoG_segmentation_by_max_std(data_array, plot_graph=False):

    hist, bin_edges = np.histogram(data_array, bins=60)
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])

    classif = GaussianMixture(n_components=3)
    classif.fit(data_array.reshape((data_array.size, 1)))

    thresholds_mu = classif.means_.flatten()
    thresholds_std = classif.covariances_.flatten()

    index_max_std = np.argmax(thresholds_std)

    if plot_graph:
        plt.figure(1, figsize=(8, 8))
        plt.subplot(111)
        plt.plot(bin_centers, hist / float(np.sum(hist)), lw=1, color='k')
        colors = ['r', 'g', 'b']
        for i in range(3):
            x = np.linspace(thresholds_mu[i] - 3*np.sqrt(thresholds_std[i]),
                            thresholds_mu[i] + 3*np.sqrt(thresholds_std[i]), 300)
            if i == index_max_std:
                ls = '--'
            else:
                ls = ':'
            plt.axvline(thresholds_mu[i], color=colors[i], ls=ls, lw=1)
            plt.plot(x, mlab.normpdf(x, thresholds_mu[i], np.sqrt(thresholds_std[i])), color=colors[i])
        plt.show(block=True)

    return (data_array > thresholds_mu[index_max_std] - np.sqrt(thresholds_std[index_max_std])) * \
            (data_array < thresholds_mu[index_max_std] + np.sqrt(thresholds_std[index_max_std]))


def percentile_lesion_mask_extractor_only_from_image(data_array, percentile_range):
    p_a = np.percentile(data_array.flatten(), percentile_range[0])
    p_b = np.percentile(data_array.flatten(), percentile_range[1])

    return (data_array > p_a) * (data_array < p_b)


def percentile_lesion_mask_extractor_only_from_image_path(pfi_input_anatomical_image, pfi_output_segmentation,
                                                          percentile_range=(5, 95)):
    """
    :param pfi_input_anatomical_image:
    :param pfi_output_segmentation:
    :param percentile_range:
    :return:
    """
    im = nib.load(pfi_input_anatomical_image)

    new_data_2 = percentile_lesion_mask_extractor_only_from_image(im.get_data(), percentile_range=percentile_range)
    new_im_2 = set_new_data(im, new_data=new_data_2, new_dtype=np.int16)
    nib.save(new_im_2, filename=pfi_output_segmentation)

    cmd = '''seg_maths {0} -fill {0};
             seg_maths {0} -ero 1 {0};
             seg_maths {0} -dil 1 {0};
             seg_maths {0} -smol 2 {0};
          '''.format(pfi_output_segmentation)

    print_and_run(cmd)
