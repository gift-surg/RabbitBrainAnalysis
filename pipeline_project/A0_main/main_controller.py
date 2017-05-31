import numpy as np

# Bias field parameters order
#
# convergenceThreshold = 0.001
# maximumNumberOfIterations = (50, 50, 50, 50)
# biasFieldFullWidthAtHalfMaximum = 0.15
# wienerFilterNoise = 0.01
# numberOfHistogramBins = 200
# numberOfControlPoints = (4, 4, 4)
# splineOrder = 3

# Bicomm Angle is the opening angle from bicomm to histological in rad (pitch).
# Axial Angle, angle of the axial orientation sign from L to R,
# from initial position to aligned with axis (yaw).
# Sagittal Angle sign from L to R from initial position to aligned with axis (roll)


# class RunParameters(object):
#     """
#     one instance of the controller parameter has all the parameters to run the
#     whole pipeline. If to process in group, or if to process a single subject.
#     """
#
#     def __init__(self, execute_PTB_ex_skull=False, execute_PTB_ex_vivo=False, execute_PTB_in_vivo=False,
#                  execute_PTB_op_skull=False, execute_ACS_ex_vivo=False, subjects=None):
#
#         self.execute_PTB_ex_skull = execute_PTB_ex_skull
#         self.execute_PTB_ex_vivo = execute_PTB_ex_vivo
#         self.execute_PTB_in_vivo = execute_PTB_in_vivo
#         self.execute_PTB_op_skull = execute_PTB_op_skull
#         self.execute_ACS_ex_vivo = execute_ACS_ex_vivo
#
#         self.subjects = subjects
#
#         self._check_sj()
#
#     def _check_sj(self):
#         if isinstance(self.subjects, str):
#             if str == 'all':
#                 self.execute_PTB_ex_skull = True
#                 self.execute_PTB_ex_vivo = True
#                 self.execute_PTB_in_vivo = True
#                 self.execute_PTB_op_skull = True
#                 self.execute_ACS_ex_vivo = True
#             else:
#                 self.subjects = [self.subjects, ]
#                 self.update_params()
#
#     def update_params(self):
#         # Turn on flags of the groups where the parameters are.
#         for sj in self.subjects:
#             assert sj in subject.keys(), '{} Not in the subject list'.format(sj)
#             group, category = subject[sj][0]
#             if group == 'PTB':
#                 if category == 'ex_skull':
#                     self.execute_PTB_ex_skull = True
#                 if category == 'ex_vivo':
#                     self.execute_PTB_ex_vivo = True
#                 if category == 'in_vivo':
#                     self.execute_PTB_in_vivo = True
#                 if category == 'op_skull':
#                     self.execute_PTB_op_skull = True
#             elif group == 'ACS':
#                 if category == 'ex_vivo':
#                     self.execute_ACS_ex_vivo = True


class ListSubjectsManager(object):
    def __init__(self, execute_PTB_ex_skull=False, execute_PTB_ex_vivo=False, execute_PTB_in_vivo=False,
                 execute_PTB_op_skull=False, execute_ACS_ex_vivo=False, input_subjects=None):

        self.execute_PTB_ex_skull = execute_PTB_ex_skull
        self.execute_PTB_ex_vivo = execute_PTB_ex_vivo
        self.execute_PTB_in_vivo = execute_PTB_in_vivo
        self.execute_PTB_op_skull = execute_PTB_op_skull
        self.execute_ACS_ex_vivo = execute_ACS_ex_vivo

        self.input_subjects = input_subjects
        # sl: subject list is the most important attirbute of the class
        self.ls = []

    def update_ls(self):

        self.ls = []  # re initialise to remove duplicates.
        prod_conditions = self.execute_PTB_ex_skull + self.execute_PTB_ex_vivo + self.execute_PTB_in_vivo + self.execute_PTB_op_skull + self.execute_ACS_ex_vivo

        if prod_conditions > 0:
            for k in subject.keys():
                if self.execute_PTB_ex_skull:
                    if subject[k][0][0] == 'PTB' and subject[k][0][1] == 'ex_skull':
                        self.ls.append(k)
                if self.execute_PTB_ex_vivo:
                    if subject[k][0][0] == 'PTB' and subject[k][0][1] == 'ex_vivo':
                        self.ls.append(k)
                if self.execute_PTB_in_vivo:
                    if subject[k][0][0] == 'PTB' and subject[k][0][1] == 'in_vivo':
                        self.ls.append(k)
                if self.execute_PTB_op_skull:
                    if subject[k][0][0] == 'PTB' and subject[k][0][1] == 'op_skull':
                        self.ls.append(k)
                if self.execute_ACS_ex_vivo:
                    if subject[k][0][0] == 'ACS' and subject[k][0][1] == 'ex_vivo':
                        self.ls.append(k)
        if self.input_subjects is not None:
            if isinstance(self.input_subjects, str):
                self.ls.append(self.input_subjects)
            elif isinstance(self.input_subjects, list):
                self.ls += self.input_subjects
        # elim duplicate and reorder:
        if not self.ls == []:
            sorted_ls = list(set(self.ls))
            sorted_ls.sort()
            self.ls = sorted_ls


# snake round
propagate_me_level = 2
# subjects of the template
templ_subjects = ['1305', '1702', '1805', '2002', '1201', '1203', '1404', '1507', '1510', '2502']


# TODO angles for ex_skull, they require some time...!

bfp_slow = [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3]
bfp_fast = [0.01, (50, 40, 30, 20), 0.15, 0.01, 200, (4, 4, 4), 3]

#
subject = {
    # ------------------------
    # PTB ex skull:
    # ------------------------
    '0104': [['PTB', 'ex_skull'],  # 0:
             [0, 0, 0, False],  # 1:  bicomm angle, axial angle, sagittal angle, in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             bfp_fast,  # 3: Bias field parameters T1
             [1, False],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '0209': [['PTB', 'ex_skull'],  # 0: study  - category
             [0, 0, 0, False],  # 1:  bicomm angle, axial angle, sagittal angle in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             bfp_fast,  # 3: Bias field parameters T1
             [1, False],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '0303': [['PTB', 'ex_skull'],  # 0: study  - category
             [0, 0, 0, False],  # 1:  bicomm angle, axial angle, sagittal angle in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             bfp_fast,  # 3: Bias field parameters T1
             [1, False],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '0307': [['PTB', 'ex_skull'],  # 0: study  - category
             [0, 0, 0, False],  # 1:  bicomm angle, axial angle, sagittal angle in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             bfp_fast,  # 3: Bias field parameters T1
             [1, False],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '0308': [['PTB', 'ex_skull'],  # 0: study  - category
             [0, 0, 0, False],  # 1:  bicomm angle, axial angle, sagittal angle in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             bfp_fast,  # 3: Bias field parameters T1
             [1, False],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '0309': [['PTB', 'ex_skull'],  # 0: study  - category
             [0, 0, 0, False],  # 1:  bicomm angle, axial angle, sagittal angle in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             bfp_fast,  # 3: Bias field parameters T1
             [1, False],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    # ------------------------
    # PTB ex vivo:
    # ------------------------
    '1201': [['PTB', 'ex_vivo'],  # 0: study  - category
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
             [np.pi /12, 0, 0, False],  # 1:  aircraft angles, in templ
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
             bfp_fast,  # 3: Bias field parameters T1
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
    '2502bt1': [['PTB', 'in_vivo'],  # 0: study  - category
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
    '3307': [['ACS', 'ex_vivo'],  # 0: study  - category
             [np.pi / 20, 0, 0, False],  # 1:  aircraft angles, in templ
             [18, 0, (5, 98)],  # 2: thr, erosion roi mask for T1
             bfp_slow,  # 3: Bias field parameters T1
             [1, True],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
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

