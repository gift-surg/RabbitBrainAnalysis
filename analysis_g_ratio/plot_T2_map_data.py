import pandas as pd
import numpy as np
import matplotlib as pyplot
import seaborn as sea


def plot_boxplot_from_data_frame(data_frame, plot_by_first_index=False, annotate=True):
    """
    divides the multi-indexed dataframe in the boxplot (1 row = 1 box) in a reasonable way.
    Inpt like:
    ----------
    WM   Midbrain               -0.681362 -0.681362 -0.681362 -0.681362
         Globus Pallidus         1.748407  1.748407  1.748407  1.748407
         Putamen                 0.809078  0.809078  0.809078  0.809078
         Thalamus               -0.183976 -0.183976 -0.183976 -0.183976
    GM   Frontal                -0.725563 -0.725563 -0.725563 -0.725563
         occipital               1.256128  1.256128  1.256128  1.256128
         Parietal                0.593381  0.593381  0.593381  0.593381
    CSF  Ventricular system     -1.541832 -1.541832 -1.541832 -1.541832
         Periventricular area   -0.654393 -0.654393 -0.654393 -0.654393
    ----------
    :param plot_by_first_index: using the example above, if True plot only three boxes WM, GM and CSF. If False plot
    10 boxes, one for each region.
    :return:
    """
    pass


if __name__ == '__main__':

    # generate the dataframe from all the loaded series.

    # plot the dataframe with external function
    pass
