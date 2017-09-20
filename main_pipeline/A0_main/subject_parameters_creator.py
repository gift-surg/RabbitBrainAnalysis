import os
import numpy as np

from tools.definitions import pfo_subjects_parameters
from main_pipeline.A0_main.subject_parameters_manager import SubjectParameters, get_list_names_subjects_in_template, \
    check_subjects_situation


def reset_parameters_files(pfo_where_to_save):
    """
    Create an instance of SubjectParameter, for each subject of the study with parameters properly setted (MANUALLY),
    and then save them (or replace them) in the appropriate folder ERASING the previous one.
    :param pfo_where_to_save: path to file to the folder. This will be the storage room for each subject in the
    study.

    HERE IS WHERE YOU SET THE PRIVATE PARAMETERS OF EACH SUBJECT.
    (of course there are better ways -sql lite, excel, ...) but this is fast, free and super flexible).

    Bias field parameters order
    -------------
    convergenceThreshold = 0.001
    maximumNumberOfIterations = (50, 50, 50, 50)
    biasFieldFullWidthAtHalfMaximum = 0.15
    wienerFilterNoise = 0.01
    numberOfHistogramBins = 200
    numberOfControlPoints = (4, 4, 4)
    splineOrder = 3

    Angles order
    ----------
    Axial Angle, angle of the axial orientation sign from L to R,
    from initial position to aligned with axis (yaw).
    Bicomm (or coronal) Angle is the opening angle from bicomm to histological in rad (pitch).
    Sagittal Angle sign from L to R from initial position to aligned with axis (roll)

    :return: Storage room filled with the adequate parameters.
    """

    # some parameters:
    bfp_slow = [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3]
    # bfp_fast = [0.01, (50, 40, 30, 20), 0.15, 0.01, 200, (4, 4, 4), 3]

    # eliminate and re-create the folder where to save the data:
    cmd = 'rm -r {0}; mkdir {0}'.format(pfo_where_to_save)
    os.system(cmd)

    # all the subjects

    ''' PTB ex skull: '''

    sp = SubjectParameters('0104')
    sp.study                  = 'PTB'
    sp.category               = 'ex_skull'
    sp.angles                 = [0, 0, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 300
    sp.intensities_percentile = (0.1, 99.9)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = False
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('0209')
    sp.study                  = 'PTB'
    sp.category               = 'ex_skull'
    sp.angles                 = [0, 0, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 300
    sp.intensities_percentile = (0.1, 99.9)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = False
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('0303')
    sp.study                  = 'PTB'
    sp.category               = 'ex_skull'
    sp.angles                 = [0, 0, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 300
    sp.intensities_percentile = (0.1, 99.9)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = False
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('0307')
    sp.study                  = 'PTB'
    sp.category               = 'ex_skull'
    sp.angles                 = [0, 0, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 300
    sp.intensities_percentile = (0.1, 99.9)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = False
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('0308')
    sp.study                  = 'PTB'
    sp.category               = 'ex_skull'
    sp.angles                 = [0, 0, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 300
    sp.intensities_percentile = (0.1, 99.9)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = False
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('0309')
    sp.study                  = 'PTB'
    sp.category               = 'ex_skull'
    sp.angles                 = [0, 0, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 300
    sp.intensities_percentile = (0.1, 99.9)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = False
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    ''' PTB ex vivo: '''

    sp = SubjectParameters('1201')
    sp.study                  = 'PTB'
    sp.category               = 'ex_vivo'
    sp.angles                 = [0, np.pi / 4, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 25
    sp.intensities_percentile = (15, 90)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = False
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.in_template            = True
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('1203')
    sp.study                  = 'PTB'
    sp.category               = 'ex_vivo'
    sp.angles                 = [0, np.pi / 6, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 25
    sp.intensities_percentile = (15, 90)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = False
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.in_template            = True
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('1305')
    sp.study                  = 'PTB'
    sp.category               = 'ex_vivo'
    sp.angles                 = [0, np.pi / 4, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 25
    sp.intensities_percentile = (15, 90)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = False
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.in_template            = True
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('1404')
    sp.study                  = 'PTB'
    sp.category               = 'ex_vivo'
    sp.angles                 = [0, np.pi / 6, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 25
    sp.intensities_percentile = (15, 90)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = False
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.in_template            = True
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('1505')
    sp.study                  = 'PTB'
    sp.category               = 'ex_vivo'
    sp.angles                 = [0, np.pi / 6, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 25
    sp.intensities_percentile = (15, 90)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = False
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = 'Dupmed due to excess of perivascular spaces enlargement.'
    sp.in_template            = False
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('1507')
    sp.study                  = 'PTB'
    sp.category               = 'ex_vivo'
    sp.angles                 = [0, np.pi / 6, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 25
    sp.intensities_percentile = (15, 90)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = False
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.in_template            = True
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('1510')
    sp.study                  = 'PTB'
    sp.category               = 'ex_vivo'
    sp.angles                 = [0, np.pi / 12, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 25
    sp.intensities_percentile = (15, 90)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = False
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.in_template            = True
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('1702')
    sp.study                  = 'PTB'
    sp.category               = 'ex_vivo'
    sp.angles                 = [0, np.pi / 6, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 25
    sp.intensities_percentile = (15, 90)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = False
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.in_template            = True
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('1805')
    sp.study = 'PTB'
    sp.category = 'ex_vivo'
    sp.angles = [0, np.pi / 12, 0]
    sp.translation = [0, 0, 0]
    sp.threshold = 25
    sp.intensities_percentile = (15, 90)
    sp.erosion_roi_mask = 1
    sp.DWI_squashed = False
    sp.bias_field_parameters = bfp_slow
    sp.mask_dilation = 1
    sp.MSME_acquisition = 'high_res'
    sp.comment = ''
    sp.in_template = True
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('2002')
    sp.study = 'PTB'
    sp.category = 'ex_vivo'
    sp.angles = [0, np.pi / 12, 0]
    sp.translation = [0, 0, 0]
    sp.threshold = 25
    sp.intensities_percentile = (15, 90)
    sp.erosion_roi_mask = 1
    sp.DWI_squashed = False
    sp.bias_field_parameters = bfp_slow
    sp.mask_dilation = 1
    sp.MSME_acquisition = 'high_res'
    sp.comment = ''
    sp.in_template = True
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('2502')
    sp.study = 'PTB'
    sp.category = 'ex_vivo'
    sp.angles = [0, np.pi / 12, 0]
    sp.translation = [0, 0, 0]
    sp.threshold = 25
    sp.intensities_percentile = (15, 90)
    sp.erosion_roi_mask = 1
    sp.DWI_squashed = False
    sp.bias_field_parameters = bfp_slow
    sp.mask_dilation = 1
    sp.MSME_acquisition = 'high_res'
    sp.comment = ''
    sp.in_template = True
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('2503')
    sp.study = 'PTB'
    sp.category = 'ex_vivo'
    sp.angles = [0, np.pi / 8, 0]
    sp.translation = [0, 0, 0]
    sp.threshold = 25
    sp.intensities_percentile = (5, 90)
    sp.erosion_roi_mask = 1
    sp.DWI_squashed = True
    sp.bias_field_parameters = bfp_slow
    sp.mask_dilation = 1
    sp.MSME_acquisition = 'high_res'
    sp.comment = ''
    sp.in_template = False
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('2608')
    sp.study = 'PTB'
    sp.category = 'ex_vivo'
    sp.angles = [0, np.pi / 6, 0]
    sp.translation = [0, 0, 0]
    sp.threshold = 0.001
    sp.intensities_percentile = (15, 90)
    sp.erosion_roi_mask = 1
    sp.DWI_squashed = True
    sp.bias_field_parameters = bfp_slow
    sp.mask_dilation = 1
    sp.MSME_acquisition = 'high_res'
    sp.comment = ''
    sp.in_template = False
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('2702')
    sp.study = 'PTB'
    sp.category = 'ex_vivo'
    sp.angles = [0, np.pi / 6, 0]
    sp.translation = [0, 0, 0]
    sp.threshold = 0.001
    sp.intensities_percentile = (15, 90)
    sp.erosion_roi_mask = 1
    sp.DWI_squashed = True
    sp.bias_field_parameters = bfp_slow
    sp.mask_dilation = 1
    sp.MSME_acquisition = 'high_res'
    sp.comment = ''
    sp.in_template = False
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    ''' PTB in-vivo'''

    sp = SubjectParameters('0802t1')
    sp.study                  = 'PTB'
    sp.category               = 'in_vivo'
    sp.angles                 = [0, np.pi / 20, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 25
    sp.intensities_percentile = (10, 98)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = False
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.in_template            = False
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('0904t1')
    sp.study                  = 'PTB'
    sp.category               = 'in_vivo'
    sp.angles                 = [0, np.pi / 6, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 25
    sp.intensities_percentile = (10, 98)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = False
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.in_template            = False
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('1501t1')
    sp.study                  = 'PTB'
    sp.category               = 'in_vivo'
    sp.angles                 = [0, np.pi / 4, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 25
    sp.intensities_percentile = (10, 98)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = False
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.in_template            = False
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('1504t1')
    sp.study                  = 'PTB'
    sp.category               = 'in_vivo'
    sp.angles                 = [0, np.pi / 4, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 25
    sp.intensities_percentile = (10, 98)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = False
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.in_template            = False
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('1508t1')
    sp.study                  = 'PTB'
    sp.category               = 'in_vivo'
    sp.angles                 = [0, np.pi / 4, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 25
    sp.intensities_percentile = (10, 98)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = False
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.in_template            = False
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('1509t1')
    sp.study                  = 'PTB'
    sp.category               = 'in_vivo'
    sp.angles                 = [0, np.pi / 5, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 25
    sp.intensities_percentile = (10, 98)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = False
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.in_template            = False
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('1511t1')
    sp.study                  = 'PTB'
    sp.category               = 'in_vivo'
    sp.angles                 = [0, np.pi / 6, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 25
    sp.intensities_percentile = (10, 98)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = False
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.in_template            = False
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('2202t1')
    sp.study                  = 'PTB'
    sp.category               = 'in_vivo'
    sp.angles                 = [0, np.pi / 6, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 25
    sp.intensities_percentile = (10, 98)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = False
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.in_template            = False
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('2205t1')
    sp.study                  = 'PTB'
    sp.category               = 'in_vivo'
    sp.angles                 = [0, np.pi / 6, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 25
    sp.intensities_percentile = (10, 98)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = False
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.in_template            = False
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('2206t1')
    sp.study                  = 'PTB'
    sp.category               = 'in_vivo'
    sp.angles                 = [0, np.pi / 6, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 25
    sp.intensities_percentile = (10, 98)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = False
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.in_template            = False
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('2502t1')
    sp.study                  = 'PTB'
    sp.category               = 'in_vivo'
    sp.angles                 = [0, np.pi / 6, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 25
    sp.intensities_percentile = (10, 98)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = False
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.in_template            = False
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('2503t1')
    sp.study                  = 'PTB'
    sp.category               = 'in_vivo'
    sp.angles                 = [0, np.pi / 6, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 25
    sp.intensities_percentile = (10, 98)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = False
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.in_template            = False
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('2605t1')
    sp.study                  = 'PTB'
    sp.category               = 'in_vivo'
    sp.angles                 = [0, np.pi / 6, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 25
    sp.intensities_percentile = (10, 98)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = False
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = 'Coil problem'
    sp.in_template            = False
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('2702t1')
    sp.study                  = 'PTB'
    sp.category               = 'in_vivo'
    sp.angles                 = [0, np.pi / 12, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 25
    sp.intensities_percentile = (10, 98)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = False
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = 'Coil problem'
    sp.in_template            = False
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    ''' PTB op-skull'''

    sp = SubjectParameters('0602')
    sp.study                  = 'PTB'
    sp.category               = 'op_skull'
    sp.angles                 = [0, np.pi / 4, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 25
    sp.intensities_percentile = (10, 98)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = False
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.in_template            = False
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('0603')
    sp.study                  = 'PTB'
    sp.category               = 'op_skull'
    sp.angles                 = [0, np.pi / 4, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 25
    sp.intensities_percentile = (10, 98)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = False
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.in_template            = False
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    ''' ACS ex-vivo'''

    sp = SubjectParameters('3103')
    sp.study                  = 'ACS'
    sp.category               = 'ex_vivo'
    sp.angles                 = [0, np.pi / 20, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 18
    sp.intensities_percentile = (5, 98)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = True
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.in_template            = False
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('3108')
    sp.study                  = 'ACS'
    sp.category               = 'ex_vivo'
    sp.angles                 = [0, np.pi / 20, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 18
    sp.intensities_percentile = (5, 98)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = True
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.in_template            = False
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('3301')
    sp.study                  = 'ACS'
    sp.category               = 'ex_vivo'
    sp.angles                 = [0, np.pi / 20, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 18
    sp.intensities_percentile = (5, 98)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = True
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.in_template            = False
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('3307')
    sp.study                  = 'ACS'
    sp.category               = 'ex_vivo'
    sp.angles                 = [0, np.pi / 20, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 18
    sp.intensities_percentile = (5, 98)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = True
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = 'Dumped, too much ghosting in the DWI.'
    sp.in_template            = False
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('3401')
    sp.study                  = 'ACS'
    sp.category               = 'ex_vivo'
    sp.angles                 = [0, 0, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 18
    sp.intensities_percentile = (5, 98)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = True
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.in_template            = False
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('3403')
    sp.study                  = 'ACS'
    sp.category               = 'ex_vivo'
    sp.angles                 = [0, np.pi / 6, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 18
    sp.intensities_percentile = (5, 98)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = True
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.in_template            = False
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('3404')
    sp.study                  = 'ACS'
    sp.category               = 'ex_vivo'
    sp.angles                 = [0, np.pi / 25, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 18
    sp.intensities_percentile = (5, 98)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = True
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.in_template            = False
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('3405')
    sp.study                  = 'ACS'
    sp.category               = 'ex_vivo'
    sp.angles                 = [0, np.pi / 25, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 18
    sp.intensities_percentile = (2, 96)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = True
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.in_template            = False
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('3501')
    sp.study                  = 'ACS'
    sp.category               = 'ex_vivo'
    sp.angles                 = [0, np.pi / 25, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 18
    sp.intensities_percentile = (5, 98)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = True
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.in_template            = False
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('3505')
    sp.study                  = 'ACS'
    sp.category               = 'ex_vivo'
    sp.angles                 = [0, np.pi / 4, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 18
    sp.intensities_percentile = (5, 98)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = True
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.in_template            = False
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('3507')
    sp.study                  = 'ACS'
    sp.category               = 'ex_vivo'
    sp.angles                 = [0, np.pi / 6, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 18
    sp.intensities_percentile = (5, 98)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = True
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.in_template            = False
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('3602')
    sp.study                  = 'ACS'
    sp.category               = 'ex_vivo'
    sp.angles                 = [0, np.pi / 8, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 18
    sp.intensities_percentile = (5, 98)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = True
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.in_template            = False
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('3604')
    sp.study                  = 'ACS'
    sp.category               = 'ex_vivo'
    sp.angles                 = [0, np.pi / 6, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 18
    sp.intensities_percentile = (5, 98)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = True
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.in_template            = False
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp

    sp = SubjectParameters('3606')
    sp.study                  = 'ACS'
    sp.category               = 'ex_vivo'
    sp.angles                 = [0, np.pi / 6, 0]
    sp.translation            = [0, 0, 0]
    sp.threshold              = 18
    sp.intensities_percentile = (5, 98)
    sp.erosion_roi_mask       = 1
    sp.DWI_squashed           = True
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.in_template            = False
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp


if __name__ == '__main__':

    reset_parameters_files(pfo_subjects_parameters)
    sjs = get_list_names_subjects_in_template(pfo_subjects_parameters)

    print('Subjects summary: ')
    check_subjects_situation(pfo_subjects_parameters)
    print('\nTemplate:')
    print sjs