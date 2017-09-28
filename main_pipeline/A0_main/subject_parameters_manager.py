import os
from os.path import join as jph
import pickle
from collections import OrderedDict

"""
To create load and modify paramters manager and related utils functions.
The actual creation happens in subject_parameters_creator module.
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
                 MSME_acquisition='high_res', in_template=False):

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
        self.in_template           = in_template
        self.b0_level              = 0

    def get_as_dict(self):
        return OrderedDict({'study'                  : self.study,
                            'category'               : self.category,
                            'leading_modality'       : self.leading_modality,
                            'angles'                 : self.angles,
                            'translation'            : self.translation,
                            'threshold'              : self.threshold,
                            'T1_window_percentile'   : self.T1_window_percentile,
                            'S0_window_percentile'   : self.S0_window_percentile,
                            'T1_mask_dilation'       : self.T1_mask_dilation,
                            'S0_mask_dilation'       : self.S0_mask_dilation,
                            'erosion_roi_mask'       : self.erosion_roi_mask,
                            'DWI_squashed'           : self.DWI_squashed,
                            'bias_field_parameters'  : self.bias_field_parameters,
                            'MSME_acquisition'       : self.MSME_acquisition,
                            'comment'                : self.comment,
                            'in_template'            : self.in_template,
                            'b0_level'               : self.b0_level})

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
