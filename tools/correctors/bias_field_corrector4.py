import os
from os.path import isfile, join
import argparse
import textwrap
import time

import SimpleITK as sitk


def bias_field_correction(pfi_input, pfi_output=None, pfi_mask=None, prefix='',
                          convergenceThreshold=0.001,
                          maximumNumberOfIterations=(50,50,50,50),
                          biasFieldFullWidthAtHalfMaximum=0.15,
                          wienerFilterNoise=0.01,
                          numberOfHistogramBins=200,
                          numberOfControlPoints=(4, 4, 4),
                          splineOrder=3):
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
    :return:
    """

    if pfi_input == pfi_output or pfi_output is None:
        prefix='_bf_correct'
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

    print 'Proposed output image name: ' + pfi_output + '\n'

    print 'ConvergenceThreshold             : ' + str(n4b.GetConvergenceThreshold())
    print 'MaximumNumberOfIterations        : ' + str(n4b.GetMaximumNumberOfIterations())
    print 'BiasFieldFullWidthAtHalfMaximum  : ' + str(n4b.GetBiasFieldFullWidthAtHalfMaximum())
    print 'WienerFilterNoise                : ' + str(n4b.GetWienerFilterNoise())
    print 'NumberOfHistogramBins            : ' + str(n4b.GetNumberOfHistogramBins())
    print 'NumberOfControlPoints            : ' + str(n4b.GetNumberOfControlPoints())
    print 'SplineOrder                      : ' + str(n4b.GetSplineOrder())

    if pfi_input.endswith('.nii') or pfi_input.endswith('.nii.gz'):
        img = sitk.ReadImage(pfi_input)

        # re-create bin if the mask is not defined
        if pfi_mask is None:
            img_mask = bth.Execute(img)
            img_mask = -1 * (img_mask - 1)
        else:
          img_mask = sitk.ReadImage(pfi_mask)

        print '\nComputations started ...'
        t0 = time.clock()

        img_no_bias = n4b.Execute(img, img_mask)

        t1 = time.clock()
        print 'Computations terminated in ' + str(t1 - t0) + ' sec.'

        sitk.WriteImage(img_no_bias, pfi_output)
        print 'Image saved in ' + pfi_output

    else:
        raise IOError('input image must be in .nii or .nii.gz format.')


def bias_field_correction_list(list_pfi_input, list_pfi_mask=None, prefix='_bfc_',
                                convergenceThreshold=0.001,
                                maximumNumberOfIterations=(50,50,50,50),
                                biasFieldFullWidthAtHalfMaximum=0.15,
                                wienerFilterNoise=0.01,
                                numberOfHistogramBins=200,
                                numberOfControlPoints=(4, 4, 4),
                                splineOrder=3):

    if list_pfi_mask is not None:
        if not len(list_pfi_input) == len(list_pfi_mask):
            raise IOError('List of input images and masks must be the same.')

    for j in range(len(list_pfi_input)):
        if list_pfi_mask is not None:
            mask_path = list_pfi_mask[j]

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
                              splineOrder=splineOrder)