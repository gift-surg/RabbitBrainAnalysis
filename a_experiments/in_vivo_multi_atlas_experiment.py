import os
from os.path import join as jph

from nilabel.main import Nilabel as NiL

from tools.correctors.bias_field_corrector4 import bias_field_correction
from tools.definitions import root_study_rabbits

pfo_root = '/Volumes/sebastianof/rabbits/C_in_vivo_study'
pfo_tmp = jph(pfo_root, 'z_tmp')

subjects_list = ['0802t1', '0904t1', '1501t1', '1509t1']
segmentation_suffix_list = ['MV_P2', 'STEPS_pr5.9_P2', 'STEPS_pr11.9_P2']
bfp_fast = [0.01, (50, 40, 30, 20), 0.15, 0.01, 200, (4, 4, 4), 3]

# os.system('mkdir {}'.format(pfo_tmp))

# for sj in subjects_list:
#
#     # Register stereotaxical over original
#     pfi_T1_original = jph(pfo_root, sj, 'original', '{}_to_std.nii.gz'.format(sj))
#     pfi_T1_original_mask = jph(pfo_root, sj, 'original', '{}_T1_roi_mask.nii.gz'.format(sj))
#
#     pfi_T1_histo = jph(pfo_root, sj, 'mod', '{}_T1.nii.gz'.format(sj))
#     pfi_T1_histo_mask = jph(pfo_root, sj, 'masks', '{}_T1_roi_mask.nii.gz'.format(sj))
#
#     assert os.path.exists(pfi_T1_original)
#     assert os.path.exists(pfi_T1_original_mask)
#     assert os.path.exists(pfi_T1_histo)
#     assert os.path.exists(pfi_T1_histo_mask)
#
#     pfi_rigid_transf = jph(pfo_tmp, '{}_histo_to_original.txt'.format(sj))
#     pfi_res = jph(pfo_tmp, '{}_histo_to_original.nii.gz'.format(sj))
#
#     cmd = 'reg_aladin -ref {}  -rmask {} -flo {} -fmask {} -aff {} -res {} --rigOnly '.format(
#         pfi_T1_original, pfi_T1_original_mask, pfi_T1_histo, pfi_T1_histo_mask, pfi_rigid_transf, pfi_res
#     )
#     print cmd
#     os.system(cmd)
#
#     # propagate the registration to the selected segmentations
#     for suff in segmentation_suffix_list:
#
#         pfi_segm = jph(pfo_root, sj, 'segm', 'automatic', '{}_{}.nii.gz'.format(sj, suff))
#
#         assert os.path.exists(pfi_segm)
#
#         pfi_segm_in_original = jph(pfo_root, sj, 'original', '{}_{}_original.nii.gz'.format(sj, suff))
#
#         cmd = 'reg_resample -ref {} -flo {} -trans {} -res {} -inter 0'.format(
#             pfi_T1_original, pfi_segm, pfi_rigid_transf, pfi_segm_in_original
#         )
#         print cmd
#         os.system(cmd)
#
#         # get the three possible contour of the selected segmentation when in original space
#
#         lt = LabT()
#
#         pfi_segm_in_original_contour_x = jph(pfo_root, sj, 'original', '{}_{}_original_CONTX.nii.gz'.format(sj, suff))
#
#         lt.manipulate_intensities.get_contour_from_segmentation(pfi_segm_in_original, pfi_segm_in_original_contour_x,
#                                                                 omit_axis='x', verbose=1)
#
#         pfi_segm_in_original_contour_y = jph(pfo_root, sj, 'original', '{}_{}_original_CONTY.nii.gz'.format(sj, suff))
#
#         lt.manipulate_intensities.get_contour_from_segmentation(pfi_segm_in_original, pfi_segm_in_original_contour_y,
#                                                                 omit_axis='y', verbose=1)
#
#         pfi_segm_in_original_contour_z = jph(pfo_root, sj, 'original', '{}_{}_original_CONTZ.nii.gz'.format(sj, suff))
#
#         lt.manipulate_intensities.get_contour_from_segmentation(pfi_segm_in_original, pfi_segm_in_original_contour_z,
#                                                                 omit_axis='z', verbose=1)
#
#     # Bias field correct the original below the mask
#
#     pfi_3d_bias_field_corrected = jph(pfo_root, sj, 'original', sj + '_BFC.nii.gz')
#
#     bias_field_correction(pfi_T1_original, pfi_3d_bias_field_corrected,
#                           pfi_mask=pfi_T1_original_mask,
#                           prefix='',
#                           convergenceThreshold=bfp_fast[0],
#                           maximumNumberOfIterations=bfp_fast[1],
#                           biasFieldFullWidthAtHalfMaximum=bfp_fast[2],
#                           wienerFilterNoise=bfp_fast[3],
#                           numberOfHistogramBins=bfp_fast[4],
#                           numberOfControlPoints=bfp_fast[5],
#                           splineOrder=bfp_fast[6],
#                           print_only=False)
#
# # open the results with the segmentation and the label descriptor
#
# for sj in subjects_list:
#
#     suff = segmentation_suffix_list[0]
#
#     pfi_3d_bias_field_corrected = jph(pfo_root, sj, 'original', sj + '_BFC.nii.gz')
#     pfi_segm_in_original_contour = jph(pfo_root, sj, 'original', '{}_{}_original_CONTX.nii.gz'.format(sj, suff))
#     pfi_segm_in_original_contour = jph(pfo_root, sj, 'original', '{}_{}_original_CONTY.nii.gz'.format(sj, suff))
#     pfi_segm_in_original_contour = jph(pfo_root, sj, 'original', '{}_{}_original_CONTZ.nii.gz'.format(sj, suff))
#
#     pfi_label_descriptor = jph(root_study_rabbits, 'A_MultiAtlas', 'labels_descriptor.txt')
#     assert os.path.exists(pfi_label_descriptor)
#
#     cmd = 'itksnap -g {0} -s {1} -l {2}'.format(pfi_3d_bias_field_corrected, pfi_segm_in_original_contour, pfi_label_descriptor)
#     os.system(cmd)
#
#     a = raw_input('press 1 to continue to the next subject.')


# get the contour segmentations in the stereotaxic coordinates:


for sj in subjects_list:

    pfi_segm = jph(pfo_root, sj, 'segm', 'automatic', '{}_{}.nii.gz'.format(sj, 'MV_P2'))

    assert os.path.exists(pfi_segm)

    pfi_segm_contour_y_stereotaxic = jph(pfo_root, sj, 'segm', '{}_{}_stereotaxic_CONTY.nii.gz'.format(sj, 'MV_P2'))

    if False:
        nil = NiL()
        nil.manipulate_intensities.get_contour_from_segmentation(pfi_segm, pfi_segm_contour_y_stereotaxic,
                                                                 omit_axis='y', verbose=1)

    # Open

    pfi_3d = jph(pfo_root, sj, 'mod', '{}_T1.nii.gz'.format(sj))
    pfi_label_descriptor = jph(root_study_rabbits, 'A_MultiAtlas', 'labels_descriptor.txt')
    cmd = 'itksnap -g {0} -s {1} -l {2}'.format(pfi_3d, pfi_segm_contour_y_stereotaxic, pfi_label_descriptor)
    if True:
        os.system(cmd)

    a = raw_input('press 1 to continue to the next subject.')
