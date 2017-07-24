from tools.definitions import pfo_subjects_parameters


class SubjectParameters(object):
    """
    Simple class container to provide the parameters required to manipulate each element independently.
    """
    def __init__(self, subject_name, study='', category='', angles=(0, 0, 0), translation=(0, 0, 0), threshold=300,
                 erosion_roi_mask=1, DWI_squeezed=False,
                 bias_field_parameters=(0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3),
                 mask_dilation=0, MSME_acquisition='high_res'):

        self.subject_name = subject_name

        self.study = study
        self.category = category
        self.angles = angles
        self.translation = translation
        self.threshold = threshold
        self.erosion_roi_mask = erosion_roi_mask
        self.DWI_squeezed = DWI_squeezed
        self.bias_field_parameters = bias_field_parameters
        self.mask_dilation = mask_dilation
        self.MSME_acquisition = MSME_acquisition
        self.comment = ''

    def get_as_dict(self):
        return {'study'                 : self.study,
                'category'              : self.category,
                'angles'                : self.angles,
                'translation'           : self.translation,
                'threshold'             : self.threshold,
                'erosion_roi_mask'      : self.erosion_roi_mask,
                'DWI_squeezed'          : self.DWI_squeezed,
                'bias_field_parameters' : self.bias_field_parameters,
                'mask_dilation'         : self.mask_dilation,
                'MSME_acquisition'      : self.MSME_acquisition,
                'comment'               : self.comment}

    def save_as_txt(self, pfo_where_to_save):
        pass

    def dump_with_pickle(self, pfo_where_to_save):
        pass


# snake round
propagate_me_level = 2
# subjects of the template
templ_subjects = ['1305', '1702', '1805', '2002', '1201', '1203', '1404', '1507', '1510', '2502']


bfp_slow = [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3]
bfp_fast = [0.01, (50, 40, 30, 20), 0.15, 0.01, 200, (4, 4, 4), 3]




def update_parameters_files(pfo_where_to_save):
    """
    Create an instance of SubjectParameter, for each subject of the study with parameters properly setted (MANUALLY),
    and then save them (or replace them) in the appropriate folder ERASING the previous one.
    :param pfo_where_to_save: path to file to the folder. This will be the storage room for each subject in the
    study.

    THIS IS THE FUNCTION WHERE YOU SET THE PARAMETER OF EACH SUBJECT.

    :return: Storage room filled with the adequate parameters.
    """



    pass


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


a = {'a' : SubjectParameters()}



#
subjects_controller = {
    # ------------------------
    # PTB ex skull:
    # ------------------------
    '0104': {'study'                 : 'PTB',
             'category'              : 'ex_skull',
             'angles'                : [0, 0, 0],
             'translation'           : [0, 0, 0],
             'threshold'             : 300,
             'erosion_roi_mask'      : 1,
             'DWI_squeezed'          : False,
             'bias_field_parameters' : [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],
             'mask_dilation'         : 1,
             'MSME_acquisition'      : 'high_res'},

    '0209': {'study'                 : 'PTB',
             'category'              : 'ex_skull',
             'angles'                : [0, 0, 0],
             'translation'           : [0, 0, 0],
             'threshold'             : 300,
             'erosion_roi_mask'      : 1,
             'DWI_squeezed'          : False,
             'bias_field_parameters' : [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],
             'mask_dilation'         : 1,
             'MSME_acquisition'      : 'high_res'},

    '0303': {'study'                 : 'PTB',
             'category'              : 'ex_skull',
             'angles'                : [0, 0, 0],
             'translation'           : [0, 0, 0],
             'threshold'             : 300,
             'erosion_roi_mask'      : 1,
             'DWI_squeezed'          : False,
             'bias_field_parameters' : [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],
             'mask_dilation'         : 1,
             'MSME_acquisition'      : 'high_res'},

    '0307': {'study'                 : 'PTB',
             'category'              : 'ex_skull',
             'angles'                : [0, 0, 0],
             'translation'           : [0, 0, 0],
             'threshold'             : 300,
             'erosion_roi_mask'      : 1,
             'DWI_squeezed'          : False,
             'bias_field_parameters' : [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],
             'mask_dilation'         : 1,
             'MSME_acquisition'      : 'high_res'},

    '0308': {'study'                 : 'PTB',
             'category'              : 'ex_skull',
             'angles'                : [0, 0, 0],
             'translation'           : [0, 0, 0],
             'threshold'             : 300,
             'erosion_roi_mask'      : 1,
             'DWI_squeezed'          : False,
             'bias_field_parameters' : [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],
             'mask_dilation'         : 1,
             'MSME_acquisition'      : 'high_res'},

    '0309': {'study'                 : 'PTB',
             'category'              : 'ex_skull',
             'angles'                : [0, 0, 0],
             'translation'           : [0, 0, 0],
             'threshold'             : 300,
             'erosion_roi_mask'      : 1,
             'DWI_squeezed'          : False,
             'bias_field_parameters' : [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],
             'mask_dilation'         : 1,
             'MSME_acquisition'      : 'high_res'},
    # ------------------------
    # PTB ex vivo:
    # ------------------------
    '1201': {'study'                 : 'PTB',
             'category'              : 'ex_skull',
             'angles'                : [0, np.pi / 4, 0],
             'translation'           : [0, 0, 0],
             'threshold'             : 300,
             'erosion_roi_mask'      : 1,
             'percentile'            : ,
             'DWI_squeezed'          : False,
             'bias_field_parameters' : [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],
             'mask_dilation'         : 1,
             'MSME_acquisition'      : 'high_res'}[['PTB', 'ex_vivo'],  # 0: study  - category
             [np.pi / 4, 0, 0, True],  # 1:  aircraft angles, in templ
             [25, 1, (15, 90)],  # 2: thr, erosion roi mask for T1,  percentile
             bfp_fast,  # 3: Bias field parameters T1
             [1, False],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '1203': [['PTB', 'ex_vivo'],  # 0: study  - category
             [np.pi / 6, 0, 0, True],  # 1:  aircraft angles, in templ
             [25, 1, (15, 90)],  # 2: thr, erosion roi mask for T1
             bfp_fast,  # 3: Bias field parameters T1
             [1, False],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '1305': [['PTB', 'ex_vivo'],  # 0: study  - category
             [np.pi / 4, 0, 0, True],  # 1:  aircraft angles, in templ
             [25, 1, (10, 90)],  # 2: thr, erosion roi mask for T1
             bfp_fast,  # 3: Bias field parameters T1
             [1, False],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '1404': [['PTB', 'ex_vivo'],  # 0: study  - category
             [np.pi / 6, 0, 0, True],  # 1:  aircraft angles, in templ
             [25, 1, (15, 90)],  # 2: thr, erosion roi mask for T1
             bfp_fast,  # 3: Bias field parameters T1
             [1, False],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '1505': [['PTB', 'ex_vivo'],  # 0: study  - category
             [np.pi / 6, 0, 0, False],  # 1:  aircraft angles, in templ
             [25, 1, (15, 90)],  # 2: thr, erosion roi mask for T1
             bfp_fast,  # 3: Bias field parameters T1
             [1, False],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '1507': [['PTB', 'ex_vivo'],  # 0: study  - category
             [np.pi / 6, 0, 0, True],  # 1:  aircraft angles, in templ
             [25, 1, (15, 90)],  # 2: thr, erosion roi mask for T1
             bfp_fast,  # 3: Bias field parameters T1
             [1, False],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '1510': [['PTB', 'ex_vivo'],  # 0: study  - category
             [np.pi / 12, 0, 0, True],  # 1:  aircraft angles, in templ
             [25, 1, (15, 90)],  # 2: thr, erosion roi mask for T1
             bfp_fast,  # 3: Bias field parameters T1
             [1, False],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '1702': [['PTB', 'ex_vivo'],  # 0: study  - category
             [np.pi / 6, 0, 0, True],  # 1:  aircraft angles, in templ
             [25, 1, (15, 90)],  # 2: thr, erosion roi mask for T1
             bfp_fast,  # 3: Bias field parameters T1
             [1, False],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '1805': [['PTB', 'ex_vivo'],  # 0: study  - category
             [np.pi / 12, 0, 0, True],  # 1:  aircraft angles, in templ
             [25, 1, (15, 90)],  # 2: thr, erosion roi mask for T1
             bfp_fast,  # 3: Bias field parameters T1
             [1, False],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '2002': [['PTB', 'ex_vivo'],  # 0: study  - category
             [np.pi / 12, 0, 0, True],  # 1:  aircraft angles, in templ
             [25, 1, (15, 90)],  # 2: thr, erosion roi mask for T1
             bfp_fast,  # 3: Bias field parameters T1
             [1, False],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '2502': [['PTB', 'ex_vivo'],  # 0: study  - category
             [np.pi / 12, 0, 0, False],  # 1:  aircraft angles, in templ
             [25, 1, (15, 90)],  # 2: thr, erosion roi mask for T1
             bfp_fast,  # 3: Bias field parameters T1
             [1, False],  # 4: mask dilation factor, DWI is squeezed,
             ['low_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '2503': [['PTB', 'ex_vivo'],  # 0: study  - category
             [np.pi / 6, 0, 0, False],  # 1:  aircraft angles, in templ
             [0.001, 1, (15, 90)],  # 2: thr, erosion roi mask for T1
             bfp_fast,  # 3: Bias field parameters T1
             [1, True],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '2608': [['PTB', 'ex_vivo'],  # 0: study  - category
             [np.pi / 6, 0, 0, False],  # 1:  aircraft angles, in templ
             [0.001, 1, (15, 90)],  # 2: thr, erosion roi mask for T1
             bfp_fast,  # 3: Bias field parameters T1
             [1, True],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '2702': [['PTB', 'ex_vivo'],  # 0: study  - category
             [np.pi / 6, 0, 0, False],  # 1:  aircraft angles, in templ
             [0.001, 1, (15, 90)],  # 2: thr, erosion roi mask for T1
             bfp_slow,  # 3: Bias field parameters T1
             [1, True],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    # ------------------------
    # PTB in_vivo:
    # ------------------------
    '0802t1': [['PTB', 'in_vivo'],  # 0: study  - category
               [np.pi / 20, 0, 0, False],  # 1:  aircraft angles, in templ
               [25, 1, (10, 98)],  # 2: thr, erosion roi mask for T1
               bfp_fast,  # 3: Bias field parameters T1
               [1, False],  # 4: mask dilation factor, DWI is squeezed,
               ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
               ],
    '0904t1': [['PTB', 'in_vivo'],  # 0: study  - category
               [np.pi / 6, 0, 0, False],  # 1:  aircraft angles, in templ
               [25, 1, (10, 98)],  # 2: thr, erosion roi mask for T1
               bfp_fast,  # 3: Bias field parameters T1
               [1, False],  # 4: mask dilation factor, DWI is squeezed,
               ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
               ],
    '1501t1': [['PTB', 'in_vivo'],  # 0: study  - category
               [np.pi / 4, 0, 0, False],  # 1:  aircraft angles, in templ
               [25, 1, (10, 98)],  # 2: thr, erosion roi mask for T1
               bfp_fast,  # 3: Bias field parameters T1
               [1, False],  # 4: mask dilation factor, DWI is squeezed,
               ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
               ],
    '1504t1': [['PTB', 'in_vivo'],  # 0: study  - category
               [np.pi / 15, 0, 0, False],  # 1:  aircraft angles, in templ
               [25, 1, (10, 98)],  # 2: thr, erosion roi mask for T1
               bfp_fast,  # 3: Bias field parameters T1
               [1, False],  # 4: mask dilation factor, DWI is squeezed,
               ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
               ],
    '1508t1': [['PTB', 'in_vivo'],  # 0: study  - category
               [np.pi / 4, 0, 0, False],  # 1:  aircraft angles, in templ
               [25, 1, (10, 98)],  # 2: thr, erosion roi mask for T1
               bfp_fast,  # 3: Bias field parameters T1
               [1, False],  # 4: mask dilation factor, DWI is squeezed,
               ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
               ],
    '1509t1': [['PTB', 'in_vivo'],  # 0: study  - category
               [np.pi / 5, 0, 0, False],  # 1:  aircraft angles, in templ
               [25, 1, (10, 98)],  # 2: thr, erosion roi mask for T1
               bfp_fast,  # 3: Bias field parameters T1
               [1, False],  # 4: mask dilation factor, DWI is squeezed,
               ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
               ],
    '1511t1': [['PTB', 'in_vivo'],  # 0: study  - category
               [np.pi / 6, 0, 0, False],  # 1:  aircraft angles, in templ
               [25, 1, (10, 98)],  # 2: thr, erosion roi mask for T1
               bfp_fast,  # 3: Bias field parameters T1
               [1, False],  # 4: mask dilation factor, DWI is squeezed,
               ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
               ],
    '2202t1': [['PTB', 'in_vivo'],  # 0: study  - category
               [np.pi / 6, 0, 0, False],  # 1:  aircraft angles, in templ
               [25, 1, (10, 98)],  # 2: thr, erosion roi mask for T1
               bfp_fast,  # 3: Bias field parameters T1
               [1, False],  # 4: mask dilation factor, DWI is squeezed,
               ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
               ],
    '2205t1': [['PTB', 'in_vivo'],  # 0: study  - category
               [np.pi / 6, 0, 0, False],  # 1:  aircraft angles, in templ
               [25, 1, (10, 98)],  # 2: thr, erosion roi mask for T1
               bfp_fast,  # 3: Bias field parameters T1
               [1, False],  # 4: mask dilation factor, DWI is squeezed,
               ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
               ],
    '2206t1': [['PTB', 'in_vivo'],  # 0: study  - category
               [np.pi / 6, 0, 0, False],  # 1:  aircraft angles, in templ
               [25, 1, (10, 98)],  # 2: thr, erosion roi mask for T1
               bfp_fast,  # 3: Bias field parameters T1
               [1, False],  # 4: mask dilation factor, DWI is squeezed,
               ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
               ],
    '2502t1': [['PTB', 'in_vivo'],  # 0: study  - category
                [np.pi / 6, 0, 0, False],  # 1:  aircraft angles, in templ
                [25, 1, (10, 98)],  # 2: thr, erosion roi mask for T1
                bfp_fast,  # 3: Bias field parameters T1
                [1, False],  # 4: mask dilation factor, DWI is squeezed,
                ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
                ],
    '2503t1': [['PTB', 'in_vivo'],  # 0: study  - category
               [np.pi / 6, 0, 0, False],  # 1:  aircraft angles, in templ
               [25, 1, (10, 98)],  # 2: thr, erosion roi mask for T1
               bfp_fast,  # 3: Bias field parameters T1
               [1, False],  # 4: mask dilation factor, DWI is squeezed,
               ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
               ],
    '2605t1': [['PTB', 'in_vivo'],  # 0: study  - category
               [np.pi / 6, 0, 0, False],  # 1:  aircraft angles, in templ
               [25, 1, (10, 98)],  # 2: thr, erosion roi mask for T1
               bfp_fast,  # 3: Bias field parameters T1
               [1, False],  # 4: mask dilation factor, DWI is squeezed,
               ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
               ],  # COIL PROBLEM!
    '2702t1': [['PTB', 'in_vivo'],  # 0: study  - category
               [np.pi / 12, 0, 0, False],  # 1:  aircraft angles, in templ
               [25, 1, (10, 98)],  # 2: thr, erosion roi mask for T1
               bfp_fast,  # 3: Bias field parameters T1
               [1, False],  # 4: mask dilation factor, DWI is squeezed,
               ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
               ],  # COIL PROBLEM!
    # ------------------------
    # PTB OP_skull:
    # ------------------------
    '0602': [['PTB', 'op_skull'],  # 0: study  - category
             [np.pi / 4, 0, 0, False],  # 1:  aircraft angles, in templ
             [25, 1],  # 2: thr, erosion roi mask for T1
             bfp_fast,  # 3: Bias field parameters T1
             [1, False],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '0603': [['PTB', 'op_skull'],  # 0: study  - category
             [np.pi / 4, 0, 0, False],  # 1:  aircraft angles, in templ
             [25, 1],  # 2: thr, erosion roi mask for T1
             bfp_fast,  # 3: Bias field parameters T1
             [1, False],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    # ------------------------
    # ACS ex_vivo:
    # ------------------------
    '3103': [['ACS', 'ex_vivo'],  # 0: study  - category
             [np.pi / 20, 0, 0, False],  # 1:  aircraft angles, in templ
             [18, 0, (5, 98)],  # 2: thr, erosion roi mask for T1
             bfp_slow,  # 3: Bias field parameters T1
             [1, True],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '3108': [['ACS', 'ex_vivo'],  # 0: study  - category
             [np.pi / 20, 0, 0, False],  # 1:  aircraft angles, in templ
             [18, 0, (5, 98)],  # 2: thr, erosion roi mask for T1
             bfp_slow,  # 3: Bias field parameters T1
             [1, True],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '3301': [['ACS', 'ex_vivo'],  # 0: study  - category
             [np.pi / 20, 0, 0, False],  # 1:  aircraft angles, in templ
             [18, 0, (5, 98)],  # 2: thr, erosion roi mask for T1
             bfp_slow,  # 3: Bias field parameters T1
             [1, True],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    # DUMPED - desperately low quality DWI.
    # '3307': [['ACS', 'ex_vivo'],  # 0: study  - category
    #          [np.pi / 20, 0, 0, False],  # 1:  aircraft angles, in templ
    #          [18, 0, (10, 90)],  # 2: thr, erosion roi mask for T1
    #          bfp_slow,  # 3: Bias field parameters T1
    #          [1, True],  # 4: mask dilation factor, DWI is squeezed,
    #          ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
    #          ],
    '3401': [['ACS', 'ex_vivo'],  # 0: study  - category
             [0, 0, 0, True],  # 1:  aircraft angles, in templ
             [18, 0, (5, 98)],  # 2: thr, erosion roi mask for T1
             bfp_slow,  # 3: Bias field parameters T1
             [1, True],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '3403': [['ACS', 'ex_vivo'],  # 0: study  - category
             [np.pi / 6, 0, 0, False],  # 1:  aircraft angles, in templ
             [18, 0, (5, 98)],  # 2: thr, erosion roi mask for T1
             bfp_slow,  # 3: Bias field parameters T1
             [1, True],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '3404': [['ACS', 'ex_vivo'],  # 0: study  - category
             [np.pi / 25, 0, 0, False],  # 1:  aircraft angles, in templ
             [18, 0, (5, 98)],  # 2: thr, erosion roi mask for T1
             bfp_slow,  # 3: Bias field parameters T1
             [1, True],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '3405': [['ACS', 'ex_vivo'],  # 0: study  - category
             [np.pi / 25, 0, 0, False],  # 1:  aircraft angles, in templ
             [18, 0, (5, 98)],  # 2: thr, erosion roi mask for T1
             bfp_slow,  # 3: Bias field parameters T1
             [1, True],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '3501': [['ACS', 'ex_vivo'],  # 0: study  - category
             [np.pi / 25, 0, 0, False],  # 1:  aircraft angles, in templ
             [18, 0, (5, 98)],  # 2: thr, erosion roi mask for T1
             bfp_slow,  # 3: Bias field parameters T1
             [1, True],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '3505': [['ACS', 'ex_vivo'],  # 0: study  - category
             [np.pi / 4, 0, 0, False],  # 1:  aircraft angles, in templ
             [18, 0, (5, 98)],  # 2: thr, erosion roi mask for T1
             bfp_slow,  # 3: Bias field parameters T1
             [1, True],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '3507': [['ACS', 'ex_vivo'],  # 0: study  - category
             [np.pi / 6, 0, 0, False],  # 1:  aircraft angles, in templ
             [18, 0, (5, 98)],  # 2: thr, erosion roi mask for T1
             bfp_slow,  # 3: Bias field parameters T1
             [1, True],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '3602': [['ACS', 'ex_vivo'],  # 0: study  - category
             [np.pi / 8, 0, 0, False],  # 1:  aircraft angles, in templ
             [18, 0, (5, 98)],  # 2: thr, erosion roi mask for T1
             bfp_slow,  # 3: Bias field parameters T1
             [1, True],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '3604': [['ACS', 'ex_vivo'],  # 0: study  - category
             [np.pi / 6, 0, 0, False],  # 1:  aircraft angles, in templ
             [18, 0, (5, 98)],  # 2: thr, erosion roi mask for T1
             bfp_slow,  # 3: Bias field parameters T1
             [1, True],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '3606': [['ACS', 'ex_vivo'],  # 0: study  - category
             [np.pi / 6, 0, 0, False],  # 1:  aircraft angles, in templ
             [18, 0, (5, 98)],  # 2: thr, erosion roi mask for T1
             bfp_slow,  # 3: Bias field parameters T1
             [1, True],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
}