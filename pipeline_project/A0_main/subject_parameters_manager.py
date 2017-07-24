import numpy as np
import os
from os.path import join as jph
import pickle

from tools.definitions import pfo_subjects_parameters


class SubjectParameters(object):
    """
    Simple class container to provide the parameters required to manipulate each element independently.
    """
    def __init__(self, subject_name, study='', category='', angles=(0, 0, 0), translation=(0, 0, 0), threshold=300,
                 intensities_percentile =(0,100), erosion_roi_mask=1, DWI_squeezed=False,
                 bias_field_parameters=(0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3),
                 mask_dilation=0, MSME_acquisition='high_res', in_template=False):

        self.subject_name = subject_name

        self.study = study
        self.category = category
        self.angles = angles
        self.translation = translation
        self.threshold = threshold
        self.intensities_percentile = intensities_percentile
        self.erosion_roi_mask = erosion_roi_mask
        self.DWI_squeezed = DWI_squeezed
        self.bias_field_parameters = bias_field_parameters
        self.mask_dilation = mask_dilation
        self.MSME_acquisition = MSME_acquisition
        self.comment = ''
        self.in_template = in_template

    def get_as_dict(self):
        return {'study'                  : self.study,
                'category'               : self.category,
                'angles'                 : self.angles,
                'translation'            : self.translation,
                'threshold'              : self.threshold,
                'intensities_percentile' : self.intensities_percentile,
                'erosion_roi_mask'       : self.erosion_roi_mask,
                'DWI_squeezed'           : self.DWI_squeezed,
                'bias_field_parameters'  : self.bias_field_parameters,
                'mask_dilation'          : self.mask_dilation,
                'MSME_acquisition'       : self.MSME_acquisition,
                'comment'                : self.comment,
                'in_template'            : self.in_template}

    def save_as_txt(self, pfo_where_to_save):
        pfi_txt_file = jph(pfo_where_to_save, self.subject_name + '.txt')
        text_to_save = '''
        study                  : {0} 
        category               : {1} 
        angles                 : {2} 
        translation            : {3} 
        threshold              : {4} 
        intensities_percentile : {5} 
        erosion_roi_mask       : {6} 
        DWI_squeezed           : {7} 
        bias_field_parameters  : {8} 
        mask_dilation          : {9} 
        MSME_acquisition       : {10}
        comment                : {11}
        in_template            : {12}'''.format(self.study,
                                                self.category,
                                                self.angles,
                                                self.translation,
                                                self.threshold,
                                                self.intensities_percentile,
                                                self.erosion_roi_mask,
                                                self.DWI_squeezed,
                                                self.bias_field_parameters,
                                                self.mask_dilation,
                                                self.MSME_acquisition,
                                                self.comment,
                                                self.in_template)

        with open(pfi_txt_file, "w") as text_file:
            text_file.write(text_to_save)

    def dump_with_pickle(self, pfo_where_to_save):
        pickle.dump(self.get_as_dict(), open(jph(pfo_where_to_save, self.subject_name), "w"))


# snake round
propagate_me_level = 2

bfp_slow = [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3]
bfp_fast = [0.01, (50, 40, 30, 20), 0.15, 0.01, 200, (4, 4, 4), 3]


# '0209': [['PTB', 'ex_skull'],  # 0: study  - category
#          [0, 0, 0, False],  # 1:  bicomm angle, axial angle, sagittal angle in templ
#          [300, 1],  # 2: thr, erosion roi mask for T1
#          bfp_fast,  # 3: Bias field parameters T1
#          [1, False],  # 4: mask dilation factor, DWI is squeezed,
#          ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
#          ],

#              [np.pi / 4, 0, 0, True],  # 1:  aircraft angles, in templ
#              [25, 1, (15, 90)],  # 2: thr, erosion roi mask for T1,  percentile
#              bfp_fast,  # 3: Bias field parameters T1
#              [1, False],  # 4: mask dilation factor, DWI is squeezed,
#              ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
#              ],


def get_list_names_subjects_in_template(pfo_where_parameter_files_are_stored):

    list_subjects = [file_name for file_name in os.listdir(pfo_where_parameter_files_are_stored)
                     if not file_name.endswith(".txt")]

    list_subjects_in_template = []
    for k in list_subjects:
        subj_k_parameters = pickle.load(open(jph(pfo_where_parameter_files_are_stored, k), 'r'))
        if subj_k_parameters['in_template']:
            list_subjects_in_template.append(k)
    list_subjects_in_template.sort(key=float)
    return list_subjects_in_template


def check_subjects_situation(pfo_where_parameter_files_are_stored):

    list_subjects = [file_name for file_name in os.listdir(pfo_where_parameter_files_are_stored)
                     if not file_name.endswith(".txt")]

    list_PTB_ex_skull = []
    list_PTB_ex_vivo  = []
    list_PTB_in_vivo  = []
    list_PTB_op_skull = []
    list_ACS_ex_vivo  = []
    list_comments     = []
    list_leftovers    = []
    for k in list_subjects:
        subj_k_parameters = pickle.load(open(jph(pfo_where_parameter_files_are_stored, k), 'r'))
        if subj_k_parameters['study'] == 'PTB':
            if subj_k_parameters['category'] == 'ex_skull':
                list_PTB_ex_skull.append(k)
            elif subj_k_parameters['category'] == 'ex_vivo':
                list_PTB_ex_vivo.append(k)
            elif subj_k_parameters['category'] == 'in_vivo':
                list_PTB_in_vivo.append(k)
            elif subj_k_parameters['category'] == 'op_skull':
                list_PTB_op_skull.append(k)
            else:
                raise IOError('Unrecognised category for subject {}'.format(k))
        elif subj_k_parameters['study'] == 'ACS':
            if subj_k_parameters['category'] == 'ex_vivo':
                list_ACS_ex_vivo.append(k)
            else:
                raise IOError('Unrecognised category for subject {}'.format(k))
        else:
            raise IOError('Unrecognised study attribute for subject {}'.format(k))

        if not subj_k_parameters['comment'] == '':
            list_comments.append(str(k) + ' -> ' + subj_k_parameters['comment'])

    assert len(list_leftovers) == 0
    list_PTB_ex_skull.sort(key=float)
    list_PTB_ex_vivo.sort(key=float)
    list_PTB_in_vivo.sort()
    list_PTB_op_skull.sort(key=float)
    list_ACS_ex_vivo.sort(key=float)
    list_comments.sort()

    print('PTB_ex_skull: ')
    print(list_PTB_ex_skull , len(list_PTB_ex_skull))

    print('PTB_ex_vivo: ')
    print(list_PTB_ex_vivo, len(list_PTB_ex_vivo))

    print('PTB_in_vivo: ')
    print(list_PTB_in_vivo, len(list_PTB_in_vivo))

    print('PTB_op_skull: ')
    print(list_PTB_op_skull, len(list_PTB_op_skull))

    print('ACS_ex_vivo: ')
    print(list_ACS_ex_vivo, len(list_ACS_ex_vivo))


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
    bfp_fast = [0.01, (50, 40, 30, 20), 0.15, 0.01, 200, (4, 4, 4), 3]

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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed = False
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
    sp.DWI_squeezed = False
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
    sp.DWI_squeezed = False
    sp.bias_field_parameters = bfp_slow
    sp.mask_dilation = 1
    sp.MSME_acquisition = 'high_res'
    sp.comment = ''
    sp.in_template = True
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
    sp.DWI_squeezed = True
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
    sp.DWI_squeezed = True
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.intensities_percentile = (5, 98)
    sp.erosion_roi_mask       = 1
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
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
    sp.DWI_squeezed           = False
    sp.bias_field_parameters  = bfp_slow
    sp.mask_dilation          = 1
    sp.MSME_acquisition       = 'high_res'
    sp.comment                = ''
    sp.in_template            = False
    sp.save_as_txt(pfo_where_to_save)
    sp.dump_with_pickle(pfo_where_to_save)
    del sp


if __name__ == '__main__':
    print 'ARGH!'
    reset_parameters_files(pfo_subjects_parameters)
    sjs = get_list_names_subjects_in_template(pfo_subjects_parameters)

    print('Subjects summary: ')
    check_subjects_situation(pfo_subjects_parameters)
    print('\nTemplate:')
    print sjs
