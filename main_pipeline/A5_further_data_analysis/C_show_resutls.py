import os
from os.path import join as jph
from scipy.stats import norm

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns




if __name__ == '__main__':

    pfo_data = '/Users/sebastiano/a_data/TData/rabbits'

    # FIGURE 1: histogram total volume group 1 vs group 2 boostrapped with Pearson index and percentile annotation.

