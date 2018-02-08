import os
from os.path import join as jph
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Ellipse


from collections import OrderedDict


data_set = OrderedDict(
           {1201: ['Preterm', 'Male',   (47.6, 1.70), 'in'],
            1203: ['Preterm', 'Male',   (54.2, 1.80), 'in'],
            1305: ['Preterm', 'Male', 	(36.7, 1.68), 'in'],
            1404: ['Preterm', 'Female', (36.6, 1.38), 'in'],
            1505: ['Preterm', 'Male',   (41.6, 1.34), 'out'],
            1507: ['Preterm', 'Male',   (31.5, 1.17), 'in'],
            1510: ['Preterm', 'Male',   (33.1, 1.34), 'in'],
            1702: ['Term',    'Male',   (47.2, 1.81), 'in'],
            1805: ['Term',    'Male', 	(54.2, 1.78 ), 'in'],
            2002: ['Preterm', 'Female', (31.8, 1.23), 'in'],
            2502: ['Term',    'Female', (62.9, 1.65), 'in'],
            2503: ['Term',    'Female', (66.8, 1.79), 'out'],
            2702: ['Term',    'Male', 	(54.6, 1.79), 'out'],
            2608: ['Term',    'Female', (54.1, 1.79), 'out'],
            3301: ['Preterm', 'Female', (47.4, 1.59), 'in'],
            3303: ['Preterm', 'Male',   (50.3, 1.78), 'out'],
            3404: ['Term',    'Female', (43.3, 1.60), 'in'],
            })

interesting_regions = OrderedDict(
          {'Cerebellar Hemispheres' : [1, 2, 3],
           'Thalamus'               : [1, 2, 3],
           'Hippocampi'             : [1, 2, 3],
           'Internal Capsulae'      : [1, 2, 3],
           'Caudate Nucleus'        : [1, 2, 3],
           'Corpus Callosum'        : [1, 2, 3],
           'Prefrontal Cortex'      : [1, 2, 3],
           })


pfo_output = jph()



