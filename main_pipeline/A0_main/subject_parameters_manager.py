import os
from os.path import join as jph
import pickle
from collections import OrderedDict

"""
To create load and modify paramters manager and related utils functions.
The actual creation happens in subject_parameters_creator module.

Notes on option_T1:
    

"""


class SubjectParameters(object):
    """
    Simple class container to provide the parameters required to manipulate each element independently.
    """
    def __init__(self, subject_name, study='', category='', angles=(0, 0, 0), translation=(0, 0, 0), threshold=300,
                 T1_window_percentile=(5, 95), S0_window_percentile=(1, 99),
                 T1_mask_dilation=0, S0_mask_dilation=0,
                 erosion_roi_mask=1, DWI_squashed=False,
                 bias_field_parameters=(0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3),
                 MSME_acquisition='high_res', in_atlas=False):
        """

        :param subject_name:
        :param study:
        :param category:
        :param angles: [0, 0, 0] : same angle set for all modalities.
                       [[0, 0, 0], [0, np.pi / 6, 0]] a different angle for each modality.
                       In that order for this pipeline: T1, DWI, MSME.
        :param translation:
        :param threshold:
        :param T1_window_percentile:
        :param S0_window_percentile:
        :param T1_mask_dilation:
        :param S0_mask_dilation:
        :param erosion_roi_mask:
        :param DWI_squashed:
        :param bias_field_parameters:
        :param MSME_acquisition:
        :param in_atlas:
        """
        self.subject_name = subject_name

        self.study                 = study
        self.category              = category
        self.leading_modality      = 'T1'
        self.angles                = angles
        self.translation           = translation
        self.threshold             = threshold
        self.T1_window_percentile  = T1_window_percentile
        self.S0_window_percentile  = S0_window_percentile
        self.T1_mask_dilation      = T1_mask_dilation
        self.S0_mask_dilation      = S0_mask_dilation
        self.erosion_roi_mask      = erosion_roi_mask
        self.DWI_squashed          = DWI_squashed
        self.bias_field_parameters = bias_field_parameters
        self.MSME_acquisition      = MSME_acquisition
        self.comment               = ''
        self.in_atlas              = in_atlas
        self.b0_level              = 0
        self.b0_to_use_in_fsldti   = -1  # -1 default means all the b0 layers. If only one layer is
        self.spotter_tag           = 'P2'
        self.options_T1            = {'roi_mask' : "Pivotal",  # Can be BTMA, MA, Pivotal
                                      'pivot'    : '1305',  # name of a template reference to get the roi mask or a first approximation (if in vivo '1504t1')
                                      'slim'     : False,  # if you want to have the slim mask. 'roi_mask' must be "BTMA" or "MA" for it to be true.
                                      'crop_roi' : False,  # To cut the T1 according to the ROI mask.
                                      'lesion_mask_method' : 0,  # can be the total number of gaussians for a MoG approach, or 0 if you want to use the given percentile
                                      'median_filter' : True  # if 'reg_mask' > 1 as pre-processing before the gaussians.
                                      }

    def get_as_dict(self):
        d = OrderedDict()
        d.update({'study'                 : self.study})
        d.update({'category'              : self.category})
        d.update({'leading_modality'      : self.leading_modality})
        d.update({'angles'                : self.angles})
        d.update({'translation'           : self.translation})
        d.update({'threshold'             : self.threshold})
        d.update({'T1_window_percentile'  : self.T1_window_percentile})
        d.update({'S0_window_percentile'  : self.S0_window_percentile})
        d.update({'T1_mask_dilation'      : self.T1_mask_dilation})
        d.update({'S0_mask_dilation'      : self.S0_mask_dilation})
        d.update({'erosion_roi_mask'      : self.erosion_roi_mask})
        d.update({'DWI_squashed'          : self.DWI_squashed})
        d.update({'bias_field_parameters' : self.bias_field_parameters})
        d.update({'MSME_acquisition'      : self.MSME_acquisition})
        d.update({'comment'               : self.comment})
        d.update({'in_atlas'              : self.in_atlas})
        d.update({'b0_level'              : self.b0_level})
        d.update({'b0_to_use_in_fsldti'   : self.b0_to_use_in_fsldti})
        d.update({'options_T1'            : self.options_T1})
        d.update({'spotter_tag'           : self.spotter_tag})
        return d

    def save_as_txt(self, pfo_where_to_save):
        pfi_txt_file = jph(pfo_where_to_save, self.subject_name + '.txt')
        dict_param = self.get_as_dict()
        text_to_save = ''

        for k in dict_param.keys():
            text_to_save += '{0:<30} : {1}\n'.format(k, dict_param[k])

        with open(pfi_txt_file, "w") as text_file:
            text_file.write(text_to_save)

    def dump_with_pickle(self, pfo_where_to_save):
        pickle.dump(self.get_as_dict(), open(jph(pfo_where_to_save, self.subject_name), "w"))


# snake round
propagate_me_level = 2

bfp_slow = [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3]
bfp_fast = [0.01, (50, 40, 30, 20), 0.15, 0.01, 200, (4, 4, 4), 3]


def list_all_subjects(pfo_where_parameter_files_are_stored):

    return [file_name for file_name in os.listdir(pfo_where_parameter_files_are_stored)
            if not file_name.endswith(".txt")]


def get_list_names_subjects_in_atlas(pfo_where_parameter_files_are_stored):

    list_subjects = [file_name for file_name in os.listdir(pfo_where_parameter_files_are_stored)
                     if not file_name.endswith(".txt")]

    list_subjects_in_template = []
    for k in list_subjects:
        subj_k_parameters = pickle.load(open(jph(pfo_where_parameter_files_are_stored, k), 'r'))
        if subj_k_parameters['in_atlas']:
            list_subjects_in_template.append(k)
    # list_subjects_in_template.sort(key=float)
    return list_subjects_in_template


def check_subjects_situation(pfo_where_parameter_files_are_stored):

    list_subjects = [file_name for file_name in os.listdir(pfo_where_parameter_files_are_stored)
                     if not file_name.endswith(".txt")]

    list_PTB_ex_skull   = []
    list_PTB_ex_vivo    = []
    list_PTB_in_vivo    = []
    list_PTB_op_skull   = []
    list_ACS_ex_vivo01  = []
    list_ACS_ex_vivo02  = []
    list_TEST_ex_vivo   = []
    list_comments       = []
    list_leftovers      = []
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
            if subj_k_parameters['category'] == 'ex_vivo01':
                list_ACS_ex_vivo01.append(k)
            elif subj_k_parameters['category'] == 'ex_vivo02':
                list_ACS_ex_vivo02.append(k)
            else:
                raise IOError('Unrecognised category for subject {} ACS'.format(k))
        elif subj_k_parameters['study'] == 'TestStudy':
            if subj_k_parameters['category'] == 'ex_vivo':
                list_TEST_ex_vivo.append(k)
        else:
            raise IOError('Unrecognised study attribute for subject {}'.format(k))

        if not subj_k_parameters['comment'] == '':
            list_comments.append(str(k) + ' -> ' + subj_k_parameters['comment'])

    assert len(list_leftovers) == 0
    list_PTB_ex_skull.sort(key=float)
    list_PTB_ex_vivo.sort(key=float)
    list_PTB_in_vivo.sort()
    list_PTB_op_skull.sort(key=float)
    list_ACS_ex_vivo01.sort()
    list_ACS_ex_vivo02.sort(key=float)
    list_TEST_ex_vivo.sort()

    list_comments.sort()

    print('PTB_ex_skull: ')
    print(list_PTB_ex_skull , len(list_PTB_ex_skull))

    print('PTB_ex_vivo: ')
    print(list_PTB_ex_vivo, len(list_PTB_ex_vivo))

    print('PTB_in_vivo: ')
    print(list_PTB_in_vivo, len(list_PTB_in_vivo))

    print('PTB_op_skull: ')
    print(list_PTB_op_skull, len(list_PTB_op_skull))

    print('ACS_ex_vivo 01: ')
    print(list_ACS_ex_vivo01, len(list_ACS_ex_vivo01))

    print('ACS_ex_vivo 02: ')
    print(list_ACS_ex_vivo02, len(list_ACS_ex_vivo02))

    print('TestStudy_ex_vivo: ')
    print(list_TEST_ex_vivo, len(list_TEST_ex_vivo))

