import os
import numpy as np
import time

import SimpleITK as sitk
from tools.auxiliary.utils import set_new_data_path


def bias_field_correction_slicewise(volume_input,
                                    convergenceThreshold=0.001,
                                    maximumNumberOfIterations=(50,50,50,50),
                                    biasFieldFullWidthAtHalfMaximum=0.15,
                                    wienerFilterNoise=0.01,
                                    numberOfHistogramBins=200,
                                    numberOfControlPoints=(4, 4, 4),
                                    splineOrder=3,
                                    print_only=False):
    # works on volumes

    four_d_volume_output = np.zeros_like(volume_input[:])

    n4b = sitk.N4BiasFieldCorrectionImageFilter()
    bth = sitk.BinaryThresholdImageFilter()

    # parameters selection:
    n4b.SetConvergenceThreshold(convergenceThreshold)
    n4b.SetMaximumNumberOfIterations(maximumNumberOfIterations)
    n4b.SetBiasFieldFullWidthAtHalfMaximum(biasFieldFullWidthAtHalfMaximum)
    n4b.SetWienerFilterNoise(wienerFilterNoise)
    n4b.SetNumberOfHistogramBins(numberOfHistogramBins)
    n4b.SetNumberOfControlPoints(numberOfControlPoints)
    n4b.SetSplineOrder(splineOrder)

    print 'ConvergenceThreshold             : ' + str(n4b.GetConvergenceThreshold())
    print 'MaximumNumberOfIterations        : ' + str(n4b.GetMaximumNumberOfIterations())
    print 'BiasFieldFullWidthAtHalfMaximum  : ' + str(n4b.GetBiasFieldFullWidthAtHalfMaximum())
    print 'WienerFilterNoise                : ' + str(n4b.GetWienerFilterNoise())
    print 'NumberOfHistogramBins            : ' + str(n4b.GetNumberOfHistogramBins())
    print 'NumberOfControlPoints            : ' + str(n4b.GetNumberOfControlPoints())
    print 'SplineOrder                      : ' + str(n4b.GetSplineOrder())

    # compute BFC slicewise (with a silly chain of conversions and re-conversions...):

    if not print_only:

        four_dims = volume_input.shape[3]

        for t in xrange(four_dims):

            a_slice_of_input = volume_input[..., t]
            a_slice_of_input_img = sitk.GetImageFromArray(a_slice_of_input)

            a_slice_of_input_img = sitk.Cast(a_slice_of_input_img, sitk.sitkFloat32)

            a_slice_of_mask_img = bth.Execute(a_slice_of_input_img)
            a_slice_of_mask_img = -1 * (a_slice_of_mask_img - 1)

            print 'bfc started for slice t = ' + str(t)
            img_no_bias = n4b.Execute(a_slice_of_input_img, a_slice_of_mask_img)

            four_d_volume_output[..., t] = sitk.GetArrayFromImage(img_no_bias)

        return four_d_volume_output


def bias_field_correction(pfi_input, pfi_output=None, pfi_mask=None, prefix='',
                          convergenceThreshold=0.001,
                          maximumNumberOfIterations=(50,50,50,50),
                          biasFieldFullWidthAtHalfMaximum=0.15,
                          wienerFilterNoise=0.01,
                          numberOfHistogramBins=200,
                          numberOfControlPoints=(4, 4, 4),
                          splineOrder=3,
                          print_only=False,
                          use_original_header=True):
    """
    Bias field correction with N4BFC.
    Does what he can to not overwrite the input files.
    :param pfi_input:
    :param pfi_output:
    :param pfi_mask:
    :param prefix:
    :param convergenceThreshold:
    :param maximumNumberOfIterations:
    :param biasFieldFullWidthAtHalfMaximum:
    :param wienerFilterNoise:
    :param numberOfHistogramBins:
    :param numberOfControlPoints:
    :param splineOrder:
    :param print_only: only print the command to console instead of executing it
    :return:
    """
    # works on images paths.

    if pfi_input == pfi_output or pfi_output is None:
        prefix=''
        pfi_output = os.path.join(os.path.dirname(pfi_input),
                                  os.path.basename(pfi_input).split('.')[0] + prefix + '.nii.gz')

    n4b = sitk.N4BiasFieldCorrectionImageFilter()
    bth = sitk.BinaryThresholdImageFilter()

    # parameters selection:
    n4b.SetConvergenceThreshold(convergenceThreshold)
    n4b.SetMaximumNumberOfIterations(maximumNumberOfIterations)
    n4b.SetBiasFieldFullWidthAtHalfMaximum(biasFieldFullWidthAtHalfMaximum)
    n4b.SetWienerFilterNoise(wienerFilterNoise)
    n4b.SetNumberOfHistogramBins(numberOfHistogramBins)
    n4b.SetNumberOfControlPoints(numberOfControlPoints)
    n4b.SetSplineOrder(splineOrder)

    print 'input image name: ' + pfi_input + '\n'
    print 'Output image name: ' + pfi_output + '\n'

    print 'ConvergenceThreshold             : ' + str(n4b.GetConvergenceThreshold())
    print 'MaximumNumberOfIterations        : ' + str(n4b.GetMaximumNumberOfIterations())
    print 'BiasFieldFullWidthAtHalfMaximum  : ' + str(n4b.GetBiasFieldFullWidthAtHalfMaximum())
    print 'WienerFilterNoise                : ' + str(n4b.GetWienerFilterNoise())
    print 'NumberOfHistogramBins            : ' + str(n4b.GetNumberOfHistogramBins())
    print 'NumberOfControlPoints            : ' + str(n4b.GetNumberOfControlPoints())
    print 'SplineOrder                      : ' + str(n4b.GetSplineOrder())

    if pfi_input.endswith('.nii') or pfi_input.endswith('.nii.gz'):
        img = sitk.ReadImage(pfi_input)

        img = sitk.Cast(img, sitk.sitkFloat64)

        # re-create bin if the mask is not defined
        if pfi_mask is None:
            img_mask = bth.Execute(img)
            img_mask = -1 * (img_mask - 1)
        else:
            img_mask = sitk.ReadImage(pfi_mask)
            img_mask = sitk.Cast(img_mask, sitk.sitkInt8)

        if not print_only:

            print '\nComputations started ...'
            t0 = time.clock()

            img_no_bias = n4b.Execute(img, img_mask)

            t1 = time.clock()
            print 'Computations terminated in ' + str(t1 - t0) + ' sec.'

            sitk.WriteImage(img_no_bias, pfi_output)
            print 'Image saved in ' + pfi_output

            if use_original_header:
                set_new_data_path(pfi_target_im=pfi_input, pfi_image_where_the_new_data=pfi_output,
                                  pfi_result=pfi_output)

    else:
        raise IOError('input image must be in .nii or .nii.gz format.')


def bias_field_correction_list(list_pfi_input, list_pfi_mask=None, prefix='_bfc_',
                                convergenceThreshold=0.001,
                                maximumNumberOfIterations=(50,50,50,50),
                                biasFieldFullWidthAtHalfMaximum=0.15,
                                wienerFilterNoise=0.01,
                                numberOfHistogramBins=200,
                                numberOfControlPoints=(4, 4, 4),
                                splineOrder=3,
                               use_original_header=True):

    if list_pfi_mask is not None:
        if not len(list_pfi_input) == len(list_pfi_mask):
            raise IOError('List of input images and masks must be the same.')

    for j in range(len(list_pfi_input)):
        if list_pfi_mask is not None:
            mask_path = list_pfi_mask[j]
        else:
            mask_path = None

        print '\n----------------------'
        print 'Element of the list ' + str(j+1) + ' / ' + str(len(list_pfi_input))
        print '\n----------------------'

        bias_field_correction(list_pfi_input[j], pfi_output=None, pfi_mask=mask_path, prefix=prefix,
                              convergenceThreshold=convergenceThreshold,
                              maximumNumberOfIterations=maximumNumberOfIterations,
                              biasFieldFullWidthAtHalfMaximum=biasFieldFullWidthAtHalfMaximum,
                              wienerFilterNoise=wienerFilterNoise,
                              numberOfHistogramBins=numberOfHistogramBins,
                              numberOfControlPoints=numberOfControlPoints,
                              splineOrder=splineOrder,
                              use_original_header=use_original_header)

if __name__ == '__main__':
    pfi_in = '/Users/sebastiano/Desktop/test/3103_msme_tp0.nii.gz'
    pri_out = '/Users/sebastiano/Desktop/test/3103_msme_bfc.nii.gz'
    pfi_mask = '/Users/sebastiano/Desktop/test/3103_segm.nii.gz'
    bias_field_correction(pfi_in, pri_out, pfi_mask=pfi_mask)