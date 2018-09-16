"""
Plot four graphs.
A) Single boxplot with 4 boxes (t, pt, lpt, lpt-acs) with full brain volumes of each subject with no normalisation.
B)
C)
D)
"""
import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from os.path import join as jph
import pickle

from tools.definitions import root_study_rabbits, pfo_subjects_parameters
from main_pipeline.A0_main.subject_parameters_manager import list_all_subjects

# ------------- Controller ------------- #


use_random = False  # for figure benchmarking


produce_A = True
produce_B = False
produce_C = False
produce_D = False

# ------------- Parameters ------------- #

pfo_where_to_save = '/Users/sebastiano/Dropbox/PHD_Thesis/thesis/figures'

data_names_dict = {1 : 'T', 2 : 'PT', 3 : 'LPT', 4 : 'LPT ACS'}
data_colors     = {1 : 'blue', 2 : 'green', 3 : 'red', 4 : 'magenta'}

data_list_regions = ['Hippocampus', 'Caudate nucleus',  'Putamen', 'Thalamus', 'Hypothalamus', 'Corpus callosum',
                     'Internal capsule', 'Claustrum', 'Amigdala']

# sns.set_context('paper', font_scale=1.2)
plt.rc('text', usetex=True)
title_font = {'family' : 'serif', 'size'   : 10}
axis_font = {'family' : 'serif', 'size': 8}
plt.rc('font', **title_font)

boxprops = dict(linewidth=0.5)
flierprops = dict(linewidth=0.5)
whiskerprops = dict(linewidth=0.5)
capsprops = dict(linewidth=0.5)
medianprops = dict(linewidth=0.5, color='g', linestyle='--')

# ------------- Data groupings ------------- #


data_group_subjects_correspondence = {
    # Term 31
    1 : ['1702', '1805', '4501', '4504', '4507', '4601', '4603', '13003', '13004', '13005', '13006'],  # '0303', '0307', '0308','0309', 2608 '2702' '4602', ,excluded '2502', '2503','2605',
    # preterm 28.5
    2 : ['1201', '1203', '1305', '1404', '1507', '1510', '2002',  '3301', '3303' , '3404', '4302',  '4304', '4305'],  # '4303','4406' # '0104', '0209', '0602', '0603', '1505', '4303', '4406'  '1501', '1504', '1507', '1508', '1509', '1511', '2202', '2205', '2206',
    # late preterm 30
    3 : ['12607', '12608', '12609', '12610', '13102', '13111'],  # '0802', '0904','3103', '3108', '3301', '3307', '10502', '10504', '10508', '10708',
    # late preterm 30 + ACS
    4 : ['12307', '12308', '12309', '12402', '12504', '12505', '13201', '13202', '13401', '13402', '13403']  # '1021', '1023', '1024', '1025', '1031', '1035', '1037', '1042', '1044', '1046',
}

num_subjects = 40  # update to sum of data_group_subjects_correspondence
num_groups   = len(data_names_dict.keys())

all_subjects = []
for i in range(1, 5):
    all_subjects += data_group_subjects_correspondence[i]

not_found = []
for sj in all_subjects:
    pfi_sj = jph(pfo_subjects_parameters, sj)
    if not os.path.exists(pfi_sj):
        not_found.append(sj)
    # sj_parameters = pickle.load(open(, 'r'))
    #
    # study = sj_parameters['study']
    # category = sj_parameters['category']

print all_subjects
print not_found

# not_in_table = list(set(list_all_subjects(pfo_subjects_parameters)) - set(all_subjects))
# not_in_table.sort()
# print not_in_table


# --------------------------------------------- #
# --------------------------------------------- #
# --------------------------------------------- #


if produce_A:

    # ------------- Collect data: (A) ------------- #

    if use_random:
        df_volumes = pd.DataFrame({'volume': np.random.randn(num_subjects),
                                   'group' : np.random.choice(data_names_dict.keys(), num_subjects)},
                                  columns=['group', 'volume'])

    else:
        df_volumes = pd.DataFrame([], columns=['subject', 'group', 'volume'])
        for i in range(1, 5):
            print i
            for sj in data_group_subjects_correspondence[i]:

                # get volumes for each subject:
                pfi_sj = jph(pfo_subjects_parameters, sj)
                sj_parameters = pickle.load(open(pfi_sj, 'r'))
                study = sj_parameters['study']
                category = sj_parameters['category']
                pfi_data_csv = jph(root_study_rabbits, 'A_data', study, category, sj, 'stereotaxic', 'report', sj + 'stx_vol_regions.csv')
                df_input_volumes = pd.read_csv(pfi_data_csv)
                vol = df_input_volumes.loc[df_input_volumes['Labels'] < 255 ].loc[df_input_volumes['Labels'] > 0]['Volume'].sum(axis=0)
                dat = {'subject': sj, 'group': i, 'volume': vol}
                df_volumes = df_volumes.append(dat, ignore_index=True)

    # ------------- Plot data: (A) ------------- #

    df_volumes_grouped = df_volumes.groupby('group', sort=True)

    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=[5, 3], dpi=200, clear=True)

    fig.canvas.set_window_title('Brain volume per subject')

    names, vals, xs = [], [], []

    for i, (name, subdf) in enumerate(df_volumes_grouped):

        names.append(data_names_dict[name])
        vals.append(subdf['volume'].tolist())
        xs.append(np.random.normal(i+1, 0.04, subdf.shape[0]))

    ax.boxplot(vals, boxprops=boxprops, flierprops=flierprops, whiskerprops=whiskerprops, capprops=capsprops, medianprops=medianprops)

    for x, val, c in zip(xs, vals, [data_colors[k] for k in range(1, 5)]):
        ax.scatter(x, val, c=c, alpha=0.4, s=8)

    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(4)

    ax.set_xticklabels(names, ha="center", size=6)  # rotation=45
    ax.set_title('Brain volume per subject')
    ax.set_ylabel('vol (mm$^3$)')

    plt.tight_layout()
    plt.savefig(jph(pfo_where_to_save, 'da_brain_volume_per_subject.pdf'), format='pdf', dpi=600)

# --------------------------------------------- #
# --------------------------------------------- #
# --------------------------------------------- #

if produce_B:

    # ------------- Collect data: (B) ------------- #

    if use_random:
        list_df_volumes_per_region = [pd.DataFrame({'data': np.random.randn(num_subjects),
                                                   'sample' : np.random.choice(data_names_dict.keys(), num_subjects)},
                                                   columns=['sample', 'data']) for _ in data_list_regions]

    else:
        list_df_volumes_per_region = []

    # ------------- Plot data: (B) ------------- #

    dict_df_volmes_per_region_grouped = {}

    for df_name, df in zip(data_list_regions, list_df_volumes_per_region):
        dict_df_volmes_per_region_grouped.update({df_name : df.groupby('sample', sort=True)})

    fig, axes = plt.subplots(nrows=3, ncols=3, figsize=[6, 4], dpi=200, clear=True)
    fig.canvas.set_window_title('Brain volume per subject per region')

    for ax, region in zip(axes.reshape(9), data_list_regions):

        names, vals, xs = [], [], []

        for i, (name, subdf) in enumerate(dict_df_volmes_per_region_grouped[region]):

            names.append(data_names_dict[name])
            vals.append(subdf['data'].tolist())
            xs.append(np.random.normal(i+1, 0.04, subdf.shape[0]))

        ax.boxplot(vals, boxprops=boxprops, flierprops=flierprops, whiskerprops=whiskerprops, capprops=capsprops, medianprops=medianprops)

        for x, val, c in zip(xs, vals, [data_colors[k] for k in range(1, 5)]):
            ax.scatter(x, val, c=c, alpha=0.4, s=4)

        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(4)

        ax.set_xticklabels(names, ha="center", size=6)  # rotation=45
        ax.set_title('{}'.format(region), **axis_font)

        if region == data_list_regions[0]:
            ax.set_ylabel('vol (mm$^3$)', **axis_font)

    plt.tight_layout()
    plt.savefig(jph(pfo_where_to_save, 'da_brain_volume_per_subject_per_regions.pdf'), format='pdf', dpi=400)


# --------------------------------------------- #
# --------------------------------------------- #
# --------------------------------------------- #

if produce_C:

    # ------------- Collect data: (C) ------------- #

    if use_random:
        list_df_FA_per_region = [pd.DataFrame({'data': np.random.randn(num_subjects),
                                                   'sample' : np.random.choice(data_names_dict.keys(), num_subjects)},
                                                   columns=['sample', 'data']) for _ in data_list_regions]

        list_df_FA_per_region[2] = pd.DataFrame({'data': np.random.randn(num_subjects) + 1,
                                                   'sample' : np.random.choice(data_names_dict.keys(), num_subjects)},
                                                   columns=['sample', 'data'])

    else:
        list_df_FA_per_region = []

    # ------------- Plot data: (C) ------------- #

    dict_df_FA_per_region_grouped = {}

    for df_name, df in zip(data_list_regions, list_df_FA_per_region):
        dict_df_FA_per_region_grouped.update({df_name : df.groupby('sample', sort=True)})

    fig, axes = plt.subplots(nrows=3, ncols=3, figsize=[6, 4], dpi=200, clear=True)
    fig.canvas.set_window_title('FA value per subject per region')

    for ax, region in zip(axes.reshape(9), data_list_regions):

        names, vals, xs = [], [], []

        for i, (name, subdf) in enumerate(dict_df_FA_per_region_grouped[region]):

            names.append(data_names_dict[name])
            vals.append(subdf['data'].tolist())
            xs.append(np.random.normal(i+1, 0.04, subdf.shape[0]))

        ax.boxplot(vals, boxprops=boxprops, flierprops=flierprops, whiskerprops=whiskerprops, capprops=capsprops, medianprops=medianprops)

        for x, val, c in zip(xs, vals, [data_colors[k] for k in range(1, 5)]):
            ax.scatter(x, val, c=c, alpha=0.4, s=4)

        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(4)

        ax.set_xticklabels(names, ha="center", size=6)  # rotation=45
        ax.set_title('{}'.format(region), **axis_font)

        if region == data_list_regions[0]:
            ax.set_ylabel('vol (mm$^3$)', **axis_font)

    plt.tight_layout()
    plt.savefig(jph(pfo_where_to_save, 'da_FA_per_subject_per_regions.pdf'), format='pdf', dpi=400)


# --------------------------------------------- #
# ------------- Collect data: (D) ------------- #
# --------------------------------------------- #

if produce_D:

    # ------------- Collect data: (D) ------------- #

    if use_random:
        list_df_MD_per_region = [pd.DataFrame({'data': np.random.randn(num_subjects),
                                                   'sample' : np.random.choice(data_names_dict.keys(), num_subjects)},
                                                   columns=['sample', 'data']) for _ in data_list_regions]
    else:
        list_df_MD_per_region = []

    # ------------- Plot data: (D) ------------- #

    dict_df_MD_per_region_grouped = {}

    for df_name, df in zip(data_list_regions, list_df_MD_per_region):
        dict_df_MD_per_region_grouped.update({df_name : df.groupby('sample', sort=True)})

    fig, axes = plt.subplots(nrows=3, ncols=3, figsize=[6, 4], dpi=200, clear=True)
    fig.canvas.set_window_title('MD value per subject per region')

    for ax, region in zip(axes.reshape(9), data_list_regions):

        names, vals, xs = [], [], []

        for i, (name, subdf) in enumerate(dict_df_MD_per_region_grouped[region]):

            names.append(data_names_dict[name])
            vals.append(subdf['data'].tolist())
            xs.append(np.random.normal(i+1, 0.04, subdf.shape[0]))

        ax.boxplot(vals, boxprops=boxprops, flierprops=flierprops, whiskerprops=whiskerprops, capprops=capsprops, medianprops=medianprops)

        for x, val, c in zip(xs, vals, [data_colors[k] for k in range(1, 5)]):
            ax.scatter(x, val, c=c, alpha=0.4, s=4)

        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(4)

        ax.set_xticklabels(names, ha="center", size=6)  # rotation=45
        ax.set_title('{}'.format(region), **axis_font)

        if region == data_list_regions[0]:
            ax.set_ylabel('vol (mm$^3$)', **axis_font)

    plt.tight_layout()
    plt.savefig(jph(pfo_where_to_save, 'da_MD_per_subject_per_regions.pdf'), format='pdf', dpi=400)


