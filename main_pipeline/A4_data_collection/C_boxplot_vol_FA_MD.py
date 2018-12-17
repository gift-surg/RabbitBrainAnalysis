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
num_subjects_if_random = 40  # update to sum of data_group_subjects_correspondence

compute    = False  # if False, computed dataframe for step C and D will be loaded from external folder

produce_A = False
produce_B = True
produce_C = False
produce_D = False

save_external = False

# ------------- Parameters ------------- #

pfo_where_to_save = '/Users/sebastiano/Desktop/'  # '/Users/sebastiano/Dropbox/PHD_Thesis/thesis/figures'

dict_data_group_names  = {1 : 'T', 2 : 'PT', 3 : 'LPT', 4 : 'LPT+'}
dict_data_group_colors = {1 : 'blue', 2 : 'green', 3 : 'red', 4 : 'magenta'}

dict_list_regions = {'Hippocampus'      : [31, 32],
                     'Caudate nucleus'  : [69, 70],
                     'Putamen'          : [71, 72],
                     'Thalamus'         : [83, 84],
                     'Hypothalamus'     : [109, 110],
                     'Corpus Callosum'  : [218],
                     'Internal capsule' : [223, 224],
                     'Claustrum'        : [53, 54],
                     'Amygdala'         : [55, 56]}

# sns.set_context('paper', font_scale=1.2)
plt.rc('text', usetex=True)
title_font = {'family' : 'serif', 'size'   : 12}
axis_font = {'family' : 'serif', 'size': 10}
tick_font_size_x = 8
tick_font_size_y = 8
plt.rc('font', **title_font)
dpi = 200

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
    2 : ['1201', '1203', '1305', '1404', '1507', '1510', '2002',  '3301', '3303' , '3404', '4302',  '4304', '4303', '4305'],  # '4406' # '0104', '0209', '0602', '0603', '1505', '4303', '4406'  '1501', '1504', '1507', '1508', '1509', '1511', '2202', '2205', '2206',
    # late preterm 30
    3 : ['12607', '12608', '12609', '12610', '13102', '13111'],  # '0802', '0904','3103', '3108', '3301', '3307', '10502', '10504', '10508', '10708',
    # late preterm 30 + ACS
    4 : ['12307', '12308', '12309', '12402', '12504', '12505', '13201', '13202', '13401', '13402', '13403']  # '1021', '1023', '1024', '1025', '1031', '1035', '1037', '1042', '1044', '1046',
}


num_groups   = len(dict_data_group_names.keys())

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

    print('Producing graph A')

    # ------------- Collect data: (A) ------------- #

    if use_random:
        df_volumes = pd.DataFrame({'volume': np.random.randn(num_subjects_if_random),
                                   'group' : np.random.choice(dict_data_group_names.keys(), num_subjects_if_random)},
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
                # sex = sj_parameters['sex']  TODO
                pfi_data_csv = jph(root_study_rabbits, 'A_data', study, category, sj, 'stereotaxic', 'report', sj + 'stx_vol_regions.csv')
                df_input_volumes = pd.read_csv(pfi_data_csv)
                vol = df_input_volumes.loc[df_input_volumes['Labels'] < 255 ].loc[df_input_volumes['Labels'] > 0]['Volume'].sum(axis=0)
                dat = {'subject': sj, 'group': i, 'volume': vol}
                df_volumes = df_volumes.append(dat, ignore_index=True)

    # ------------- Plot data: (A) ------------- #

    df_volumes_grouped = df_volumes.groupby('group', sort=True)

    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=[5, 3], dpi=dpi, clear=True)

    fig.canvas.set_window_title('Brain volume per subject')

    names, vals, xs = [], [], []

    for i, (name, subdf) in enumerate(df_volumes_grouped):

        names.append(dict_data_group_names[name])
        vals.append(subdf['volume'].tolist())
        xs.append(np.random.normal(i+1, 0.04, subdf.shape[0]))

    ax.boxplot(vals, boxprops=boxprops, flierprops=flierprops, whiskerprops=whiskerprops, capprops=capsprops, medianprops=medianprops)

    for x, val, c in zip(xs, vals, [dict_data_group_colors[k] for k in range(1, 5)]):
        ax.scatter(x, val, c=c, alpha=0.4, s=8)

    for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize(tick_font_size_y)

    ax.set_xticklabels(names, ha="center", size=tick_font_size_x)  # rotation=45
    ax.set_title('Brain volume per subject')
    ax.set_ylabel('vol (mm$^3$)')

    plt.tight_layout()

    if save_external:
        plt.savefig(jph(pfo_where_to_save, 'da_brain_volume_per_subject.pdf'), format='pdf', dpi=dpi)
    else:
        plt.show()
# --------------------------------------------- #
# --------------------------------------------- #
# --------------------------------------------- #

if produce_B:

    print('Producing graph B')

    # ------------- Collect data: (B) ------------- #

    if use_random:
        df_volumes_per_region = pd.DataFrame([], columns=['subject', 'group'] + ['vol {}'.format(r) for r in dict_list_regions.keys()])

        for dummy_sj in range(num_subjects_if_random):
            dat = {'subject': int(np.random.randint(100, 999)), 'group': int(np.random.choice(dict_data_group_names.keys()))}
            for reg in dict_list_regions.keys():
                dat.update({'vol {}'.format(reg) : np.random.randn()})
            df_volumes_per_region = df_volumes_per_region.append(dat, ignore_index=True)

    else:
        df_volumes_per_region = pd.DataFrame([], columns=['subject', 'group'] + ['vol {}'.format(r) for r in dict_list_regions.keys()])
        for i in range(1, 5):
            for sj in data_group_subjects_correspondence[i]:
                pfi_sj = jph(pfo_subjects_parameters, sj)
                sj_parameters = pickle.load(open(pfi_sj, 'r'))
                study = sj_parameters['study']
                category = sj_parameters['category']
                pfi_data_csv = jph(root_study_rabbits, 'A_data', study, category, sj, 'stereotaxic', 'report', sj + 'stx_vol_regions.csv')
                df_input_volumes = pd.read_csv(pfi_data_csv)

                dat = {'subject': sj, 'group': i}

                for reg in dict_list_regions.keys():
                    vol_per_region = 0
                    for label in dict_list_regions[reg]:
                        vol_per_region += df_input_volumes.loc[df_input_volumes['Labels'] == label]['Volume'].tolist()[0]

                    dat.update({'vol {}'.format(reg): vol_per_region})

                df_volumes_per_region = df_volumes_per_region.append(dat, ignore_index=True)

    # ------------- Plot data: (B) ------------- #

    dict_df_volumes_per_region_grouped = df_volumes_per_region.groupby('group', sort=True)

    fig, axes = plt.subplots(nrows=3, ncols=3, figsize=[6, 4], dpi=dpi, clear=True)
    fig.canvas.set_window_title('Brain volume per subject per region')

    for ax, region in zip(axes.reshape(9), dict_list_regions.keys()):

        names, vals, xs = [], [], []

        for i, (name, subdf) in enumerate(dict_df_volumes_per_region_grouped):

            names.append(dict_data_group_names[name])
            vals.append(subdf['vol {}'.format(region)].tolist())
            xs.append(np.random.normal(i+1, 0.04, subdf.shape[0]))

        ax.boxplot(vals, boxprops=boxprops, flierprops=flierprops, whiskerprops=whiskerprops, capprops=capsprops, medianprops=medianprops)

        for x, val, c in zip(xs, vals, [dict_data_group_colors[k] for k in range(1, 5)]):
            ax.scatter(x, val, c=c, alpha=0.4, s=4)

        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(tick_font_size_y)

        ax.set_xticklabels(names, ha="center", size=tick_font_size_x)  # rotation=45
        ax.set_title('{}'.format(region), **axis_font)

        if region == dict_list_regions.keys()[0]:
            ax.set_ylabel('vol (mm$^3$)', **axis_font)

    plt.tight_layout()

    if save_external:
        plt.savefig(jph(pfo_where_to_save, 'da_brain_volume_per_subject_per_regions.pdf'), format='pdf', dpi=dpi)
    else:
        plt.show()

# --------------------------------------------- #
# --------------------------------------------- #
# --------------------------------------------- #

if produce_C:

    print('Producing graph C')

    # ------------- Collect data: (C) ------------- #

    if use_random:
        df_FA_per_region = pd.DataFrame([], columns=['subject', 'group'] + ['FA {}'.format(r) for r in dict_list_regions.keys()])

        for dummy_sj in range(num_subjects_if_random):
            dat = {'subject': int(np.random.randint(100, 999)), 'group': int(np.random.choice(dict_data_group_names.keys()))}
            for reg in dict_list_regions.keys():
                dat.update({'FA {}'.format(reg) : np.random.randn()})
            df_FA_per_region = df_FA_per_region.append(dat, ignore_index=True)

    else:

        if compute:

            df_FA_per_region = pd.DataFrame([], columns=['subject', 'group'] + ['FA {}'.format(r) for r in dict_list_regions.keys()])
            for i in range(1, 5):
                for sj in data_group_subjects_correspondence[i]:
                    print '\n FA {}'.format(sj)
                    pfi_sj = jph(pfo_subjects_parameters, sj)
                    sj_parameters = pickle.load(open(pfi_sj, 'r'))
                    study = sj_parameters['study']
                    category = sj_parameters['category']

                    dat = {'subject': sj, 'group': i}

                    for reg in dict_list_regions.keys():
                        print reg
                        FA_per_region = []
                        for label in dict_list_regions[reg]:
                            pfo_reports_sj = jph(root_study_rabbits, 'A_data', study, category, sj, 'stereotaxic', 'report')
                            # looks for the report starting with input.
                            for fin_report in os.listdir(pfo_reports_sj):
                                if fin_report.startswith('{}stx_FA_{}'.format(sj, label)):
                                    pfi_FA_data_csv = jph(pfo_reports_sj, fin_report)
                                    break
                            FA_per_region += [np.loadtxt(pfi_FA_data_csv)]
                        FA_per_region_median = np.median(np.hstack(FA_per_region))
                        dat.update({'FA {}'.format(reg): FA_per_region_median})

                    df_FA_per_region = df_FA_per_region.append(dat, ignore_index=True)

            df_FA_per_region.to_pickle(jph(pfo_where_to_save, 'df_FA_per_region.pickle'))

        else:
            pfi_FA_pickled = jph(pfo_where_to_save, 'df_FA_per_region.pickle')
            if not os.path.exists(pfi_FA_pickled):
                raise IOError('Run again with compte flag = True')
            df_FA_per_region = pd.read_pickle(pfi_FA_pickled)
    # ------------- Plot data: (C) ------------- #

    df_FA_per_region_grouped = df_FA_per_region.groupby('group', sort=True)

    fig, axes = plt.subplots(nrows=3, ncols=3, figsize=[6, 4], dpi=dpi, clear=True)
    fig.canvas.set_window_title('FA value per subject per region')

    for ax, region in zip(axes.reshape(9)[:len(dict_list_regions.keys())], dict_list_regions.keys()):

        names, vals, xs = [], [], []

        for i, (name, subdf) in enumerate(df_FA_per_region_grouped):

            names.append(dict_data_group_names[name])
            vals.append(subdf.loc[subdf['subject'] != '3303']['FA {}'.format(region)].tolist())
            xs.append(np.random.normal(i+1, 0.04, subdf.loc[subdf['subject'] != '3303'].shape[0]))

        ax.boxplot(vals, boxprops=boxprops, flierprops=flierprops, whiskerprops=whiskerprops, capprops=capsprops, medianprops=medianprops)

        for x, val, c in zip(xs, vals, [dict_data_group_colors[k] for k in range(1, 5)]):
            ax.scatter(x, val, c=c, alpha=0.4, s=4)

        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(tick_font_size_y)

        ax.set_xticklabels(names, ha="center", size=tick_font_size_x)  # rotation=45
        ax.set_title('{}'.format(region), **axis_font)

        if region == dict_list_regions.keys()[0]:
            ax.set_ylabel('FA', **axis_font)

    plt.tight_layout()

    if save_external:
        plt.savefig(jph(pfo_where_to_save, 'da_FA_per_subject_per_regions.pdf'), format='pdf', dpi=dpi)
    else:
        plt.show()

# --------------------------------------------- #
# ------------- Collect data: (D) ------------- #
# --------------------------------------------- #

if produce_D:

    print('Producing graph D')

    # ------------- Collect data: (D) ------------- #

    if use_random:
        df_MD_per_region = pd.DataFrame([], columns=['subject', 'group'] + ['MD {}'.format(r) for r in dict_list_regions.keys()])

        for dummy_sj in range(num_subjects_if_random):
            dat = {'subject': int(np.random.randint(100, 999)), 'group': int(np.random.choice(dict_data_group_names.keys()))}
            for reg in dict_list_regions.keys():
                dat.update({'MD {}'.format(reg) : np.random.randn()})
            df_MD_per_region = df_MD_per_region.append(dat, ignore_index=True)

    else:
        if compute:

            df_MD_per_region = pd.DataFrame([], columns=['subject', 'group'] + ['FA {}'.format(r) for r in dict_list_regions.keys()])
            for i in range(1, 5):
                for sj in data_group_subjects_correspondence[i]:
                    print '\n MD {}'.format(sj)
                    pfi_sj = jph(pfo_subjects_parameters, sj)
                    sj_parameters = pickle.load(open(pfi_sj, 'r'))
                    study = sj_parameters['study']
                    category = sj_parameters['category']

                    dat = {'subject': sj, 'group': i}

                    for reg in dict_list_regions.keys():
                        print reg
                        MD_per_region = []
                        for label in dict_list_regions[reg]:
                            pfo_reports_sj = jph(root_study_rabbits, 'A_data', study, category, sj, 'stereotaxic', 'report')
                            # looks for the report starting with input.
                            for fin_report in os.listdir(pfo_reports_sj):
                                if fin_report.startswith('{}stx_MD_{}'.format(sj, label)):
                                    pfi_MD_data_csv = jph(pfo_reports_sj, fin_report)
                                    break
                        MD_per_region += [np.loadtxt(pfi_MD_data_csv)]
                        MD_per_region_median = np.median(np.hstack(MD_per_region))
                        dat.update({'MD {}'.format(reg): MD_per_region_median})

                    df_MD_per_region = df_MD_per_region.append(dat, ignore_index=True)

            df_MD_per_region.to_pickle(jph(pfo_where_to_save, 'df_MD_per_region.pickle'))

        else:
            pfi_MD_pickled = jph(pfo_where_to_save, 'df_MD_per_region.pickle')
            if not os.path.exists(pfi_MD_pickled):
                raise IOError('Run again with compte flag = True')
            df_MD_per_region = pd.read_pickle(pfi_MD_pickled)

    # ------------- Plot data: (D) ------------- #

    df_MD_per_region_grouped = df_MD_per_region.groupby('group', sort=True)

    fig, axes = plt.subplots(nrows=3, ncols=3, figsize=[6, 4], dpi=dpi, clear=True)
    fig.canvas.set_window_title('MD value per subject per region')

    for ax, region in zip(axes.reshape(9)[:len(dict_list_regions.keys())], dict_list_regions.keys()):

        names, vals, xs = [], [], []

        for i, (name, subdf) in enumerate(df_MD_per_region_grouped):
            names.append(dict_data_group_names[name])
            vals.append(subdf.loc[subdf['subject'] != '3303']['MD {}'.format(region)].tolist())
            xs.append(np.random.normal(i + 1, 0.04, subdf.loc[subdf['subject'] != '3303'].shape[0]))

        ax.boxplot(vals, boxprops=boxprops, flierprops=flierprops, whiskerprops=whiskerprops, capprops=capsprops, medianprops=medianprops)

        for x, val, c in zip(xs, vals, [dict_data_group_colors[k] for k in range(1, 5)]):
            ax.scatter(x, val, c=c, alpha=0.4, s=4)

        for tick in ax.yaxis.get_major_ticks():
            tick.label.set_fontsize(tick_font_size_y)

        ax.set_xticklabels(names, ha="center", size=tick_font_size_x)  # rotation=45
        ax.set_title('{}'.format(region), **axis_font)

        if region == dict_list_regions.keys()[0]:
            ax.set_ylabel('MD', **axis_font)

    plt.tight_layout()

    if save_external:
        plt.savefig(jph(pfo_where_to_save, 'da_MD_per_subject_per_regions.pdf'), format='pdf', dpi=dpi)
    else:
        plt.show()

