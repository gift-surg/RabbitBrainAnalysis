import os
import numpy as np
import nibabel as nib

from definitions import root_ex_vivo_MSME
from tools.correctors.bias_field_corrector4 import bias_field_correction_slicewise
from tools.auxiliary.utils import set_new_data, cut_dwi_image_from_first_slice_mask_path
from tools.correctors.MSME_T2_correctors import corrector_MSME_T2_path


convergenceThreshold = 0.1  # 0.001
maximumNumberOfIterations = (20, 10, 5, 2)
biasFieldFullWidthAtHalfMaximum = 0.15
wienerFilterNoise = 0.01
numberOfHistogramBins = 100
numberOfControlPoints = (4, 4, 4)
splineOrder = 3

sj = '1305'

path_to_cropped = '/Users/sebastiano/Desktop/test_msme_T2/mri/mri/1305_MSME_cropped.nii.gz'
path_to_a_slice = '/Users/sebastiano/Desktop/test_msme_T2/mri/mri/1305_MSME_first_slice.nii.gz'
path_to_a_slice_bfc = '/Users/sebastiano/Desktop/test_msme_T2/mri/mri/1305_MSME_first_slice_bfc.nii.gz'

nib_input = nib.load(path_to_cropped)

data_bfc_corrected = bias_field_correction_slicewise(nib_input.get_data()[...,:10],
                                                     convergenceThreshold=convergenceThreshold,
                      maximumNumberOfIterations=maximumNumberOfIterations,
                      biasFieldFullWidthAtHalfMaximum=biasFieldFullWidthAtHalfMaximum,
                      wienerFilterNoise=wienerFilterNoise,
                      numberOfHistogramBins=numberOfHistogramBins,
                      numberOfControlPoints=numberOfControlPoints,
                      splineOrder=splineOrder)

nib_bfc = set_new_data(nib_input, data_bfc_corrected)
nib.save(nib_bfc, path_to_a_slice_bfc)
