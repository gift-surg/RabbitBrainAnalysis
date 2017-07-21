import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as seb
from os.path import join as jph

from analysis_of_data.collect_T2_maps_data import subjects_ACS, subjects_template
from tools.definitions import root_study_rabbits
from pipeline_project.A0_main.main_controller import subject
from tools.auxiliary.utils import eliminates_consecutive_duplicates


def plot_boxplot_from_data_frame(data_frame, plot_by_first_index=False, annotate=True, title='', fig_id=0,
                                 graph_title=None, pfi_save=None):
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
    print
    print title
    print data_frame
    print

    if graph_title is None:
        graph_title = title

    dic_columns = {"level_0": "Compartment", "level_1": "Region", "level_2": "Subject", 0: "T2"}
    df = data_frame.stack().reset_index().rename(index=str, columns=dic_columns)
    fig = plt.figure(fig_id, figsize=(14, 7), dpi=80, facecolor='w', edgecolor='k')
    fig.subplots_adjust(left=0.075, right=0.95, top=0.9, bottom=0.25)
    # set title
    fig.canvas.set_window_title(title)
    # boxplot
    ax0 = fig.add_subplot(121)
    bp1 = seb.boxplot(x="Region", y="T2", hue="Compartment", data=df, palette="Set3", ax=ax0)
    regions_list = eliminates_consecutive_duplicates(list(df['Region']))
    bp1.set_xticklabels(regions_list, rotation=30)

    ax1 = fig.add_subplot(122)
    bp2 = seb.boxplot(x="Compartment", y="T2", data=df, palette="Set3", ax=ax1)
    compartments_list = eliminates_consecutive_duplicates(list(df['Compartment']))
    bp2.set_xticklabels(compartments_list, rotation=30)

    fig.suptitle(graph_title)

    if pfi_save is not None:
        fig.savefig(pfi_save)

    plt.show(block=False)


if __name__ == '__main__':

    ''' Output values '''

    df_dict_T2_maps_original      = {}
    df_dict_T2_maps_original_bfc  = {}
    df_dict_T2_maps_upsampled     = {}
    df_dict_T2_maps_upsampled_bfc = {}

    ''' Computation: created the dataframe '''

    for sj in subjects_ACS + subjects_template:
        print('Collecting T2 values for subject {}'.format(sj))

        sj = str(sj)

        group = subject[sj][0][0]
        category = subject[sj][0][1]
        pfo_input_data = jph(root_study_rabbits, 'A_data', group, category)

        pfi_se_T2_maps_original     = jph(pfo_input_data, sj, 'records', sj + '_T2_maps_original.pkl')
        pfi_se_T2_maps_original_bfc = jph(pfo_input_data, sj, 'records', sj + '_T2_maps_original_bfc.pkl')
        pfi_T2_maps_upsampled       = jph(pfo_input_data, sj, 'records', sj + '_T2_maps_upsampled.pkl')
        pfi_T2_maps_upsampled_bfc   = jph(pfo_input_data, sj, 'records', sj + '_T2_maps_upsampled_bfc.pkl')

        ok = True
        for p in [pfi_se_T2_maps_original, pfi_se_T2_maps_original_bfc, pfi_T2_maps_upsampled,
                  pfi_T2_maps_upsampled_bfc]:
            if not os.path.exists(p):
                print('WARNING: series {} does not exists'.format(p))
                ok = False

        if ok:
            se_T2_maps_original      = pd.read_pickle(pfi_se_T2_maps_original)
            se_T2_maps_original_bfc  = pd.read_pickle(pfi_se_T2_maps_original_bfc)
            se_T2_maps_upsampled     = pd.read_pickle(pfi_T2_maps_upsampled)
            se_T2_maps_upsampled_bfc = pd.read_pickle(pfi_T2_maps_upsampled_bfc)

            df_dict_T2_maps_original.      update({sj : se_T2_maps_original})
            df_dict_T2_maps_original_bfc.  update({sj : se_T2_maps_original_bfc})
            df_dict_T2_maps_upsampled.     update({sj : se_T2_maps_upsampled})
            df_dict_T2_maps_upsampled_bfc. update({sj : se_T2_maps_upsampled_bfc})

    df_T2_maps_original      = pd.DataFrame(df_dict_T2_maps_original)
    df_T2_maps_original_bfc  = pd.DataFrame(df_dict_T2_maps_original_bfc)
    df_T2_maps_upsampled     = pd.DataFrame(df_dict_T2_maps_upsampled)
    df_T2_maps_upsampled_bfc = pd.DataFrame(df_dict_T2_maps_upsampled_bfc)

    # plot the dataframe with external function
    pfo_results = jph('/Users/sebastiano/Desktop')
    plot_boxplot_from_data_frame(df_T2_maps_original,      title='T2 maps original',      fig_id=0,
                                 pfi_save=jph(pfo_results, 'T2_maps_original.png'))
    plot_boxplot_from_data_frame(df_T2_maps_original_bfc,  title='T2 maps original bfc',  fig_id=1,
                                 pfi_save=jph(pfo_results, 'T2_maps_original_bfc.png'))
    plot_boxplot_from_data_frame(df_T2_maps_upsampled,     title='T2 maps upsampled',     fig_id=2,
                                 pfi_save=jph(pfo_results, 'T2_maps_upsampled.png'))
    plot_boxplot_from_data_frame(df_T2_maps_upsampled_bfc, title='T2 maps upsampled bfc', fig_id=3,
                                 pfi_save=jph(pfo_results, 'T2_maps_upsampled_bfc.png'))

