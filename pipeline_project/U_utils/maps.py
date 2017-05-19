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

# Bicomm angle is the opening angle from bicomm to histological in rad.


#
subject = {'1201': [['PTB', 'ex_vivo'],  # 0: study  - category
                    [np.pi/12, 0, True],  # 1:  bicomm angle, in templ
                    [300, 1],  # 2: thr, erosion roi mask for T1
                    [0.001, (50, 50, 50, 50), 0.15, 0.01, 200, (4, 4, 4), 3],  # 3: Bias field parameters T1
                    [1, False],  # 4: mask dilation factor, DWI is squeezed,
                    ['high_res', ]  # 5: MSME
                    ],
           '2502' : [[],
                     [np.pi/12],
                     [],
                     [],
                     ['low_res', ]  # 5 : MSME some have the low res protocol even if ex_vivo.
                     ],
           '1805' : [[],
                     [np.pi/12],
                     [],
                     [],
                     ['high_res', ]  # 5 : MSME some have the low res protocol even if ex_vivo.
                     ],
           '2002' : [[],
                     [np.pi/12],
                     [],
                     [],
                     ['high_res', ]  # 5 : MSME some have the low res protocol even if ex_vivo.
                     ],
           '1510' : [[],
                     [np.pi/12],
                     [],
                     [],
                     ['high_res', ]  # 5 : MSME some have the low res protocol even if ex_vivo.
                     ],
           'zzz' : [[],
                     [],
                     [],
                     [],
                     ['low_res', ]  # 5 : MSME some have the low res protocol even if ex_vivo.
                     ],
           'zzzz' : [[],
                     [],
                     [],
                     [],
                     ['low_res', ]  # 5 : MSME some have the low res protocol even if ex_vivo.
                     ],
           'xxxx' : [[],
                     [],
                     [],
                     [],
                     ['low_res', ]  # 5 : MSME some have the low res protocol even if ex_vivo.
                     ]
           }


# snake round
propagate_me_level = 2

templ_subjects = ['1305', '1702', '1805', '2002', '1201', '1203', '1404', '1507', '1510', '2502']
