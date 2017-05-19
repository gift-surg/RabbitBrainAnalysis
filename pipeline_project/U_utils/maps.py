from os.path import join as jph
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
# TODO angles for ex_skull, they require some time...!


#
subject = {
    # ------------------------
    # PTB ex skull:
    # ------------------------
    '0104': [['PTB', 'ex_skull'],  # 0: study  - category
             [0, 0, 0, True],  # 1:  bicomm angle, axial angle, sagittal angle in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
             [1, False],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '0209': [['PTB', 'ex_skull'],  # 0: study  - category
             [0, 0, 0, True],  # 1:  bicomm angle, axial angle, sagittal angle in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
             [1, False],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '0303': [['PTB', 'ex_skull'],  # 0: study  - category
             [0, 0, 0, True],  # 1:  bicomm angle, axial angle, sagittal angle in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
             [1, False],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '0307': [['PTB', 'ex_skull'],  # 0: study  - category
             [0, 0, 0, True],  # 1:  bicomm angle, axial angle, sagittal angle in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
             [1, False],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '0308': [['PTB', 'ex_skull'],  # 0: study  - category
             [0, 0, 0, True],  # 1:  bicomm angle, axial angle, sagittal angle in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
             [1, False],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '0309': [['PTB', 'ex_skull'],  # 0: study  - category
             [0, 0, 0, True],  # 1:  bicomm angle, axial angle, sagittal angle in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
             [1, False],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    # ------------------------
    # PTB ex skull:
    # ------------------------
    '1201': [['PTB', 'ex_vivo'],  # 0: study  - category
             [np.pi/6, 0, 0, True],  # 1:  aircraft angles, in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
             [1, False],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '1203': [['PTB', 'ex_vivo'],  # 0: study  - category
             [np.pi / 6, 0, 0, True],  # 1:  aircraft angles, in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
             [1, False],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '1305': [['PTB', 'ex_vivo'],  # 0: study  - category
             [np.pi / 6, 0, 0, True],  # 1:  aircraft angles, in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
             [1, False],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '1404': [['PTB', 'ex_vivo'],  # 0: study  - category
             [np.pi / 6, 0, 0, True],  # 1:  aircraft angles, in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
             [1, False],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '1505': [['PTB', 'ex_vivo'],  # 0: study  - category
             [np.pi / 6, 0, 0, True],  # 1:  aircraft angles, in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
             [1, False],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '1507': [['PTB', 'ex_vivo'],  # 0: study  - category
             [np.pi / 6, 0, 0, True],  # 1:  aircraft angles, in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
             [1, False],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '1510': [['PTB', 'ex_vivo'],  # 0: study  - category
             [np.pi / 12, 0, 0, True],  # 1:  aircraft angles, in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
             [1, False],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '1702': [['PTB', 'ex_vivo'],  # 0: study  - category
             [np.pi / 6, 0, 0, True],  # 1:  aircraft angles, in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
             [1, False],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '1805': [['PTB', 'ex_vivo'],  # 0: study  - category
             [np.pi / 12, 0, 0, True],  # 1:  aircraft angles, in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
             [1, False],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '2002': [['PTB', 'ex_vivo'],  # 0: study  - category
             [np.pi / 12, 0, 0, True],  # 1:  aircraft angles, in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
             [1, False],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '2502': [['PTB', 'ex_vivo'],  # 0: study  - category
             [np.pi /12, 0, 0, True],  # 1:  aircraft angles, in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
             [1, False],  # 4: mask dilation factor, DWI is squeezed,
             ['low_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '2503': [['PTB', 'ex_vivo'],  # 0: study  - category
             [np.pi / 6, 0, 0, True],  # 1:  aircraft angles, in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
             [1, True],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '2608': [['PTB', 'ex_vivo'],  # 0: study  - category
             [np.pi / 6, 0, 0, True],  # 1:  aircraft angles, in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
             [1, True],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '2702': [['PTB', 'ex_vivo'],  # 0: study  - category
             [np.pi / 6, 0, 0, True],  # 1:  aircraft angles, in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
             [1, True],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    # ------------------------
    # PTB in_vivo:
    # ------------------------
    '0802t1': [['PTB', 'in_vivo'],  # 0: study  - category
               [np.pi / 20, 0, 0, True],  # 1:  aircraft angles, in templ
               [300, 1],  # 2: thr, erosion roi mask for T1
               [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
               [1, False],  # 4: mask dilation factor, DWI is squeezed,
               ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
               ],
    '0904t1': [['PTB', 'in_vivo'],  # 0: study  - category
               [np.pi / 6, 0, 0, True],  # 1:  aircraft angles, in templ
               [300, 1],  # 2: thr, erosion roi mask for T1
               [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
               [1, False],  # 4: mask dilation factor, DWI is squeezed,
               ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
               ],
    '1501t1': [['PTB', 'in_vivo'],  # 0: study  - category
               [np.pi / 4, 0, 0, True],  # 1:  aircraft angles, in templ
               [300, 1],  # 2: thr, erosion roi mask for T1
               [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
               [1, False],  # 4: mask dilation factor, DWI is squeezed,
               ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
               ],
    '1504t1': [['PTB', 'in_vivo'],  # 0: study  - category
               [np.pi / 15, 0, 0, True],  # 1:  aircraft angles, in templ
               [300, 1],  # 2: thr, erosion roi mask for T1
               [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
               [1, False],  # 4: mask dilation factor, DWI is squeezed,
               ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
               ],
    '1508t1': [['PTB', 'in_vivo'],  # 0: study  - category
               [np.pi / 4, 0, 0, True],  # 1:  aircraft angles, in templ
               [300, 1],  # 2: thr, erosion roi mask for T1
               [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
               [1, False],  # 4: mask dilation factor, DWI is squeezed,
               ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
               ],
    '1509t1': [['PTB', 'in_vivo'],  # 0: study  - category
               [np.pi / 5, 0, 0, True],  # 1:  aircraft angles, in templ
               [300, 1],  # 2: thr, erosion roi mask for T1
               [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
               [1, False],  # 4: mask dilation factor, DWI is squeezed,
               ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
               ],
    '1511t1': [['PTB', 'in_vivo'],  # 0: study  - category
               [np.pi / 6, 0, 0, True],  # 1:  aircraft angles, in templ
               [300, 1],  # 2: thr, erosion roi mask for T1
               [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
               [1, False],  # 4: mask dilation factor, DWI is squeezed,
               ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
               ],
    '2502bt1': [['PTB', 'in_vivo'],  # 0: study  - category
                [np.pi / 6, 0, 0, True],  # 1:  aircraft angles, in templ
                [300, 1],  # 2: thr, erosion roi mask for T1
                [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
                [1, False],  # 4: mask dilation factor, DWI is squeezed,
                ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
                ],
    '2503t1': [['PTB', 'in_vivo'],  # 0: study  - category
               [np.pi / 6, 0, 0, True],  # 1:  aircraft angles, in templ
               [300, 1],  # 2: thr, erosion roi mask for T1
               [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
               [1, False],  # 4: mask dilation factor, DWI is squeezed,
               ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
               ],
    '2605t1': [['PTB', 'in_vivo'],  # 0: study  - category
               [np.pi / 6, 0, 0, True],  # 1:  aircraft angles, in templ
               [300, 1],  # 2: thr, erosion roi mask for T1
               [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
               [1, False],  # 4: mask dilation factor, DWI is squeezed,
               ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
               ],  # COIL PROBLEM!
    '2702t1': [['PTB', 'in_vivo'],  # 0: study  - category
               [np.pi / 12, 0, 0, True],  # 1:  aircraft angles, in templ
               [300, 1],  # 2: thr, erosion roi mask for T1
               [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
               [1, False],  # 4: mask dilation factor, DWI is squeezed,
               ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
               ],  # COIL PROBLEM!
    # ------------------------
    # PTB OP_skull:
    # ------------------------
    '0602': [['PTB', 'op_skull'],  # 0: study  - category
               [np.pi / 4, 0, 0, True],  # 1:  aircraft angles, in templ
               [300, 1],  # 2: thr, erosion roi mask for T1
               [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
               [1, False],  # 4: mask dilation factor, DWI is squeezed,
               ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
               ],
    '0603': [['PTB', 'op_skull'],  # 0: study  - category
               [np.pi / 4, 0, 0, True],  # 1:  aircraft angles, in templ
               [300, 1],  # 2: thr, erosion roi mask for T1
               [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
               [1, False],  # 4: mask dilation factor, DWI is squeezed,
               ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
               ],
    # ------------------------
    # ACS ex_vivo:
    # ------------------------
    '3103': [['ACS', 'ex_vivo'],  # 0: study  - category
             [np.pi / 20, 0, 0, True],  # 1:  aircraft angles, in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
             [1, True],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '3108': [['ACS', 'ex_vivo'],  # 0: study  - category
             [np.pi / 20, 0, 0, True],  # 1:  aircraft angles, in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
             [1, True],  # 4: mask dilation factor, DWI is squeezed,
             ['high_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '3301': [['ACS', 'ex_vivo'],  # 0: study  - category
             [np.pi / 20, 0, 0, True],  # 1:  aircraft angles, in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
             [1, True],  # 4: mask dilation factor, DWI is squeezed,
             ['mid_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '3307': [['ACS', 'ex_vivo'],  # 0: study  - category
             [np.pi / 20, 0, 0, True],  # 1:  aircraft angles, in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
             [1, True],  # 4: mask dilation factor, DWI is squeezed,
             ['mid_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '3401': [['ACS', 'ex_vivo'],  # 0: study  - category
             [0, 0, 0, True],  # 1:  aircraft angles, in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
             [1, True],  # 4: mask dilation factor, DWI is squeezed,
             ['mid_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '3403': [['ACS', 'ex_vivo'],  # 0: study  - category
             [np.pi / 6, 0, 0, True],  # 1:  aircraft angles, in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
             [1, True],  # 4: mask dilation factor, DWI is squeezed,
             ['mid_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '3404': [['ACS', 'ex_vivo'],  # 0: study  - category
             [np.pi / 25, 0, 0, True],  # 1:  aircraft angles, in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
             [1, True],  # 4: mask dilation factor, DWI is squeezed,
             ['mid_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '3405': [['ACS', 'ex_vivo'],  # 0: study  - category
             [np.pi / 25, 0, 0, True],  # 1:  aircraft angles, in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
             [1, True],  # 4: mask dilation factor, DWI is squeezed,
             ['mid_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '3501': [['ACS', 'ex_vivo'],  # 0: study  - category
             [np.pi / 25, 0, 0, True],  # 1:  aircraft angles, in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
             [1, True],  # 4: mask dilation factor, DWI is squeezed,
             ['mid_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '3505': [['ACS', 'ex_vivo'],  # 0: study  - category
             [np.pi / 4, 0, 0, True],  # 1:  aircraft angles, in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
             [1, True],  # 4: mask dilation factor, DWI is squeezed,
             ['mid_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '3507': [['ACS', 'ex_vivo'],  # 0: study  - category
             [np.pi / 6, 0, 0, True],  # 1:  aircraft angles, in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
             [1, True],  # 4: mask dilation factor, DWI is squeezed,
             ['mid_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '3602': [['ACS', 'ex_vivo'],  # 0: study  - category
             [np.pi / 8, 0, 0, True],  # 1:  aircraft angles, in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
             [1, True],  # 4: mask dilation factor, DWI is squeezed,
             ['mid_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '3604': [['ACS', 'ex_vivo'],  # 0: study  - category
             [np.pi / 6, 0, 0, True],  # 1:  aircraft angles, in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
             [1, True],  # 4: mask dilation factor, DWI is squeezed,
             ['mid_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
    '3606': [['ACS', 'ex_vivo'],  # 0: study  - category
             [np.pi / 6, 0, 0, True],  # 1:  aircraft angles, in templ
             [300, 1],  # 2: thr, erosion roi mask for T1
             [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
             [1, True],  # 4: mask dilation factor, DWI is squeezed,
             ['mid_res', ]  # 5: MSME acquisition - some have the low res protocol even if ex_vivo.
             ],
}

# snake round
propagate_me_level = 2
# subjects of the template
templ_subjects = ['1305', '1702', '1805', '2002', '1201', '1203', '1404', '1507', '1510', '2502']
