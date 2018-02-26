"""
Standard measurements on the selected data.
Volume, Volume/tot_volume, FA_i, MD_i, i in regions.

Very direct approach to create the intended data structure.

data_st:
data structure defined as:

data_st = OrderedDict()
data_st['title'] = 'vol type, region i'
data_st['12xx'] = ['M/F', 'term/pre-term', value]

"""
import numpy as np
import pandas as pa
import nibabel as nib
import matplotlib.pyplot as plt
from os.path import join as jph
import pickle
import matplotlib

from collections import OrderedDict

from tools.definitions import root_study_rabbits, pfo_subjects_parameters, pfi_labels_descriptor
from main_pipeline.A0_main.subject_parameters_manager import get_list_names_subjects_in_atlas

from labels_manager.tools.aux_methods.utils_nib import one_voxel_volume
from labels_manager.tools.caliber.volumes_and_values import get_total_num_nonzero_voxels
from labels_manager.tools.descriptions.manipulate_descriptors import LabelsDescriptorManager as LdM
from labels_manager.main import LabelsManager as LM


data_set_info = OrderedDict(
           {'1201': ['Preterm', 'Male',   (47.6, 1.70), 'in'],
            '1203': ['Preterm', 'Male',   (54.2, 1.80), 'in'],
            '1305': ['Preterm', 'Male',   (36.7, 1.68), 'in'],
            '1404': ['Preterm', 'Female', (36.6, 1.38), 'in'],
            '1505': ['Preterm', 'Male',   (41.6, 1.34), 'out'],
            '1507': ['Preterm', 'Male',   (31.5, 1.17), 'in'],
            '1510': ['Preterm', 'Male',   (33.1, 1.34), 'in'],
            '1702': ['Term',    'Male',   (47.2, 1.81), 'in'],
            '1805': ['Term',    'Male',   (54.2, 1.78 ), 'in'],
            '2002': ['Preterm', 'Female', (31.8, 1.23), 'in'],
            '2502': ['Term',    'Female', (62.9, 1.65), 'in'],     ##
            '2503': ['Term',    'Female', (66.8, 1.79), 'out'],
            '2702': ['Term',    'Male',   (54.6, 1.79), 'out'],
            '2608': ['Term',    'Female', (54.1, 1.79), 'out'],
            '3301': ['Preterm', 'Female', (47.4, 1.59), 'in'],
            '3303': ['Preterm', 'Male',   (50.3, 1.78), 'out'],
            '3404': ['Term',    'Female', (43.3, 1.60), 'in'],
            })

ptb_related_regions = OrderedDict()
ptb_related_regions['CerebellarHemisphere']  = [179, 180]
ptb_related_regions['Thalamus']               = [83, 84]
ptb_related_regions['Hippocampus']            = [31, 32]
ptb_related_regions['InternalCapsule']       = [223, 224]
ptb_related_regions['CaudateNucleus']              = [69, 70]
ptb_related_regions['CorpusCallosum']              = [218]
ptb_related_regions['MedialPrefrontalAndFrontal']  = [5, 6, 7, 8]


atlas_subjects = get_list_names_subjects_in_atlas(pfo_subjects_parameters)


def historgram_of_data_st(ax, df, xlabel='', ylabel='Values', factor=1., legend=False):
    """

    :param ax: matplotlib axis object
    :param df: rabbbit-valued-dataframe as defined in the documentation.
    :return:
    """
    # fill each category separately:

    df_F_pre = df.loc[df['cat1'] == 'Female'].loc[df['cat2'] == 'Preterm']
    df_F_ter = df.loc[df['cat1'] == 'Female'].loc[df['cat2'] == 'Term']
    df_M_pre = df.loc[df['cat1'] == 'Male'].loc[df['cat2'] == 'Preterm']
    df_M_ter = df.loc[df['cat1'] == 'Male'].loc[df['cat2'] == 'Term']

    lens = [0, len(df_F_pre.index), len(df_F_ter.index), len(df_M_pre.index), len(df_M_ter.index)]
    cum_lens = [sum(lens[:(l+1)]) for l in range(len(lens))]

    custom_red = np.array([255, 153, 153]) / 255.
    custom_green = np.array([163, 255, 163]) / 255.
    if 'vals' in list(df_F_pre.columns.values):
        ax.bar(range(cum_lens[0], cum_lens[1]), list(df_F_pre['vals']), width=0.4, label="pre-term", align="center", color=custom_red)
        ax.bar(range(cum_lens[1], cum_lens[2]), list(df_F_ter['vals']), width=0.4, label="term", align="center", color=custom_green)
        ax.bar(range(cum_lens[2], cum_lens[3]), list(df_M_pre['vals']), width=0.4, label="pre-term", align="center", color=custom_red)
        ax.bar(range(cum_lens[3], cum_lens[4]), list(df_M_ter['vals']), width=0.4, label="pre-term", align="center", color=custom_green)
    else:
        ax.bar(range(cum_lens[0], cum_lens[1]), list(df_F_pre['vals_mu']), yerr=df_F_pre['vals_std'], width=0.4, label="pre-term", align="center", color=custom_red, ecolor='gray')
        ax.bar(range(cum_lens[1], cum_lens[2]), list(df_F_ter['vals_mu']), yerr=df_F_ter['vals_std'], width=0.4, label="term", align="center", color=custom_green, ecolor='gray')
        ax.bar(range(cum_lens[2], cum_lens[3]), list(df_M_pre['vals_mu']), yerr=df_M_pre['vals_std'], width=0.4, label="pre-term", align="center", color=custom_red, ecolor='gray')
        ax.bar(range(cum_lens[3], cum_lens[4]), list(df_M_ter['vals_mu']), yerr=df_M_ter['vals_std'], width=0.4, label="pre-term", align="center", color=custom_green, ecolor='gray')

    # add vertical line separating males females
    tot_females = sum([len(df_F_pre.index), len(df_F_ter.index)])
    tot_males   = sum([len(df_M_pre.index), len(df_M_ter.index)])
    ax.axvline(x=tot_females - 0.5, color='k', alpha=0.4)

    # add labels and text axis

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(df.name)
    labels = list(df_F_pre.index) + list(df_F_ter.index) + list(df_M_pre.index) + list(df_M_ter.index)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45)

    # annotate male female text:
    y_lim = ax.get_ylim()
    y_hight = 0.1 * (y_lim[1] - y_lim[0])
    ax.annotate('Females', xy=(tot_females/2. - 1, y_hight), color='gray', size=int(factor * 20))
    ax.annotate('Males', xy=(tot_females + tot_males/2. - 0.75, y_hight), color='gray', size=(factor * 20))

    # add legend
    if legend:
        ax.legend()
    # add grid
    ax.grid()
    ax.set_axisbelow(True)


def boxplot_of_data_st(ax, df, xlabel='', ylabel='', factor=1., legend=True):
    df_F_pre = df.loc[df['cat1'] == 'Female'].loc[df['cat2'] == 'Preterm']
    df_F_ter = df.loc[df['cat1'] == 'Female'].loc[df['cat2'] == 'Term']
    df_M_pre = df.loc[df['cat1'] == 'Male'].loc[df['cat2'] == 'Preterm']
    df_M_ter = df.loc[df['cat1'] == 'Male'].loc[df['cat2'] == 'Term']

    lens = [len(df_F_pre.index), len(df_F_ter.index), len(df_M_pre.index), len(df_M_ter.index)]
    custom_red = np.array([255, 153, 153]) / 255.
    custom_green = np.array([163, 255, 163]) / 255.
    colors = [custom_red, ] * lens[0] + [custom_green, ] * lens[1] + [custom_red, ] * lens[2] + [custom_green, ] * lens[3]
    all_data = []
    for se in (df_F_pre['vals'], df_F_ter['vals'], df_M_pre['vals'], df_M_ter['vals']):
        for i in se.index:
            all_data.append(se[i])

    bplot = ax.boxplot(all_data, patch_artist=True)

    for patch, color in zip(bplot['boxes'], colors):
        patch.set_facecolor(color)

    # add vertical line separating males females
    tot_females = sum([len(df_F_pre.index), len(df_F_ter.index)])
    tot_males = sum([len(df_M_pre.index), len(df_M_ter.index)])
    ax.axvline(x=tot_females + 0.5, color='k', alpha=0.4)

    # add labels and text axis

    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(df.name)
    labels = list(df_F_pre.index) + list(df_F_ter.index) + list(df_M_pre.index) + list(df_M_ter.index)
    #ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45)

    # annotate male female text:
    x_lim = ax.get_xlim()
    y_lim = ax.get_ylim()
    y_hight = 0.1 * (y_lim[1] - y_lim[0])
    ax.annotate('Females', xy=(tot_females / 2. - 1, y_hight), color='gray', size=int(factor * 20))
    ax.annotate('Males', xy=(tot_females + tot_males / 2. - 0.75, y_hight), color='gray', size=(factor * 20))

    # add legend
    if legend:
        # Finally, add a basic legend
        ax.annotate('pre-term', xy=(x_lim[0] + 0.5, y_lim[0] + 0.5), backgroundcolor=custom_red, color='black',  size=(factor * 12))
        ax.annotate('term', xy=(x_lim[0] + 0.5, y_lim[0] + 0.1), backgroundcolor=custom_green, color='black', size=(factor * 12))

    # add grid
    ax.grid()
    ax.set_axisbelow(True)


def collect_data_from_subject_list(sj_list, pfo_storage, controller=None, report_folder='report_stereotaxic'):
    """
    :param sj_list: list of subjects
    :param pfo_storage: where to save the obtained dataframe per region, per value.
    :param controller: controller values
    :return:
    """

    # --> Collection 1: total volume, no normalisation
    if controller['Collection1']:
        """
        Pandas series as:
        1201    vols
        1203    vols
        1305    vols
        1404    vols
        1507    vols
        1510    vols
        1702    vols
        1805    vols
        2002    vols
        2502    vols
        3301    vols
        3404    vols
        """
        se_vols = pa.Series(np.array([0, ] * len(sj_list)).astype(np.float64), index=sj_list)
        print('\n -- ')
        for sj in sj_list:
            print('\nCollection 1, subject {}. '.format(sj))

            sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

            study = sj_parameters['study']
            category = sj_parameters['category']

            pfo_subject = jph(root_study_rabbits, 'A_data', study, category, sj)
            pfi_segm = jph(pfo_subject, 'segm', '{}_T1_segm.nii.gz'.format(sj))

            im_segm = nib.load(pfi_segm)

            num_voxels = get_total_num_nonzero_voxels(im_segm)
            vol_mm3 = num_voxels * one_voxel_volume(im_segm)

            se_vols[sj] = vol_mm3

        se_vols.to_pickle(jph(pfo_storage, 'Volumes.pkl' ))

    # --> Collection 2: tot volume normalised by the body weight
    if controller['Collection2']:
        """
        Pandas series as:
        1201    vols / vol tot
        1203    vols / vol tot
        1305    vols / vol tot
        1404    vols / vol tot
        1507    vols / vol tot
        1510    vols / vol tot
        ...
        """
        se_vols = pa.Series(np.array([0, ] * len(sj_list)).astype(np.float64), index=sj_list)
        print('\n -- ')
        for sj in sj_list:
            print('\nCollection 2, subject {}. '.format(sj))

            sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

            study = sj_parameters['study']
            category = sj_parameters['category']

            pfo_subject = jph(root_study_rabbits, 'A_data', study, category, sj)
            pfi_segm = jph(pfo_subject, 'segm', '{}_T1_segm.nii.gz'.format(sj))

            im_segm = nib.load(pfi_segm)

            num_voxels = get_total_num_nonzero_voxels(im_segm)
            vol_mm3 = num_voxels * one_voxel_volume(im_segm)

            se_vols[sj] = vol_mm3 / float(data_set_info[sj][2][0])

        se_vols.to_pickle(jph(pfo_storage, 'VolumesNormalised.pkl'))

    # --> Collection 3: volumes per regions normalised total brain volume
    if controller['Collection3']:
        """
        """
        for k in ptb_related_regions.keys():
            se_vols_region_k = pa.Series(np.array([0, ] * len(sj_list)).astype(np.float64), index=sj_list)

            for sj in sj_list:
                print('\nCollection 3, subject {}, region {}. '.format(sj, k))
                sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

                study = sj_parameters['study']
                category = sj_parameters['category']

                pfo_subject = jph(root_study_rabbits, 'A_data', study, category, sj)
                pfi_segm = jph(pfo_subject, 'segm', '{}_T1_segm.nii.gz'.format(sj))

                im_segm = nib.load(pfi_segm)

                tot_num_voxels = get_total_num_nonzero_voxels(im_segm)
                # load volumes saved in in the report of each subject.
                pfi_report_vols = jph(pfo_subject, report_folder, '{}_volumes.pkl'.format(sj))

                df = pa.read_pickle(pfi_report_vols)

                num_voxel_reg_k = 0
                for k_j in ptb_related_regions[k]:
                    num_voxel_reg_k += df['num_voxels']['[{}]'.format(k_j)]

                net_volume = num_voxel_reg_k / float(tot_num_voxels)
                se_vols_region_k[sj] = net_volume

            print se_vols_region_k

            se_vols_region_k.name = 'Volumes normalised tot brain vol, region {0}'.format(ptb_related_regions[k])
            se_vols_region_k.to_pickle(jph(pfo_storage, 'VolumesRegionOverTotBV{0}.pkl'.format(k)))

    # --> Collection 4: volumes per regions normalised by the body weight of the interesting regions
    if controller['Collection4']:
        for k in ptb_related_regions.keys():
            se_vols_region_k = pa.Series(np.array([0, ] * len(sj_list)).astype(np.float64), index=sj_list)

            for sj in sj_list:
                print('\nCollection 4, subject {}, region {} (normalisation by body weight). '.format(sj, k))
                sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

                study = sj_parameters['study']
                category = sj_parameters['category']

                pfo_subject = jph(root_study_rabbits, 'A_data', study, category, sj)

                pfi_report_vols = jph(pfo_subject, report_folder, '{}_volumes.pkl'.format(sj))

                df = pa.read_pickle(pfi_report_vols)

                num_voxel_reg_k = 0
                for k_j in ptb_related_regions[k]:
                    num_voxel_reg_k += df['num_voxels']['[{}]'.format(k_j)]

                pfi_segm = jph(pfo_subject, 'segm', '{}_T1_segm.nii.gz'.format(sj))
                im_segm = nib.load(pfi_segm)  # use the vol in mm instead of other measures.
                vol_reg_k_mm = num_voxel_reg_k * one_voxel_volume(im_segm)

                net_volume = vol_reg_k_mm / float(data_set_info[sj][2][0])
                se_vols_region_k[sj] = net_volume

            se_vols_region_k.name = 'Volumes normalised tot body weight, region {0}'.format(ptb_related_regions[k])
            se_vols_region_k.to_pickle(jph(pfo_storage, 'VolumesRegionOverBodyWeight{0}.pkl'.format(k)))

    # --> Collection 5: FA per regions
    if controller['Collection5']:
        ldm = LdM(pfi_labels_descriptor)
        labels_dict = ldm.get_dict()
        for k in ptb_related_regions.keys():
            print('FA per regions, all subjects, region {}'.format(k))
            vals_per_region_k = []
            for sj in sj_list:
                sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

                study = sj_parameters['study']
                category = sj_parameters['category']

                pfo_subject = jph(root_study_rabbits, 'A_data', study, category, sj)
                arrays_FA_k = []
                for k_j in ptb_related_regions[k]:
                    pfi_saved_data_FA = jph(pfo_subject, report_folder, '{}_FA_{}_{}.npy'.format(sj, labels_dict[k_j][-1].replace(' ', ''), k_j))
                    arrays_FA_k.append(np.load(pfi_saved_data_FA))

                vals_per_region_k.append(np.concatenate(arrays_FA_k, axis=0))

            se_vals_per_region_k = pa.Series(vals_per_region_k, index=sj_list)
            print se_vals_per_region_k
            se_vals_per_region_k.name = 'FA per values, region {0}'.format(ptb_related_regions[k])
            se_vals_per_region_k.to_pickle(jph(pfo_storage, 'FARegion{0}.pkl'.format(k)))

    # --> Collection 6: MD
    if controller['Collection6']:
        ldm = LdM(pfi_labels_descriptor)
        labels_dict = ldm.get_dict()
        for k in ptb_related_regions.keys():
            print('MD per regions, all subjects, region {}'.format(k))
            vals_per_region_k = []
            for sj in sj_list:
                sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

                study = sj_parameters['study']
                category = sj_parameters['category']

                pfo_subject = jph(root_study_rabbits, 'A_data', study, category, sj)
                arrays_MD_k = []
                for k_j in ptb_related_regions[k]:
                    pfi_saved_data_MD = jph(pfo_subject, report_folder,
                                            '{}_MD_{}_{}.npy'.format(sj, labels_dict[k_j][-1].replace(' ', ''), k_j))
                    arrays_MD_k.append(np.load(pfi_saved_data_MD))

                vals_per_region_k.append(np.concatenate(arrays_MD_k, axis=0))

            se_vals_per_region_k = pa.Series(vals_per_region_k, index=sj_list)
            se_vals_per_region_k.name = 'MD per values, region {0}'.format(ptb_related_regions[k])
            se_vals_per_region_k.to_pickle(jph(pfo_storage, 'MDRegion{0}.pkl'.format(k)))


def plot_and_save_collected(pfo_storage, show=True, controller=None):
    """
    Create required plots based on data-frames saved in the storage folder with the given suffix.
    (extension '.pickle')
    :param pfo_storage: path to folder where data are stored.
    :param suffix: to identify the experiment.
    :param show: if False, saves only the corresponding graphs. Else graphs are shown as well.
    :return:
    """
    cat1 = pa.Series([data_set_info[k][1] for k in atlas_subjects], index=atlas_subjects)
    cat2 = pa.Series([data_set_info[k][0] for k in atlas_subjects], index=atlas_subjects)

    # --> Collection 1: tot volume.
    if controller['Collection1']:
        pfi_file = jph(pfo_storage, 'Volumes.pkl')
        se_vol = pa.read_pickle(pfi_file)
        d = {'cat1': cat1,
             'cat2': cat2,
             'vals': se_vol}
        df = pa.DataFrame(data=d, index=atlas_subjects)
        df.name = 'Total volume'
        fig, ax = plt.subplots(figsize=(12, 8), nrows=1, ncols=1)
        fig.canvas.set_window_title('Total volume')
        historgram_of_data_st(ax, df, ylabel='Volume mm^3')
        print 'Total volumes'
        print df
        # save dataframe as txt:
        df.to_csv(jph(pfo_storage, 'Volumes.txt'))
        # save figure:
        plt.savefig(jph(pfo_storage, 'Volumes.png'))
        if show:
            plt.show()

    # --> Collection 2: tot volume normalised by the body weight.
    if controller['Collection2']:
        pfi_file = jph(pfo_storage, 'VolumesNormalised.pkl')
        se_vol = pa.read_pickle(pfi_file)
        d = {'cat1': cat1,
             'cat2': cat2,
             'vals': se_vol}
        df = pa.DataFrame(data=d, index=atlas_subjects)
        df.name = 'Total volume normalised'
        fig, ax = plt.subplots(figsize=(12, 8), nrows=1, ncols=1)
        fig.canvas.set_window_title('Total volume Normalised')
        historgram_of_data_st(ax, df, ylabel='Volume (mm^3) / body weight (g)')
        print 'tot volumes normalised'
        print df
        # save dataframe as txt:
        df.to_csv(jph(pfo_storage, 'VolumesNormalised.txt'))
        # save figure:
        plt.savefig(jph(pfo_storage, 'VolumesNormalised.png'))
        if show:
            plt.show()

    # --> Collection 3: volumes per regions normalised total brain volume
    if controller['Collection3']:
        matplotlib.rcParams.update({'font.size': 10})
        fig, ax = plt.subplots(figsize=(12, 8), nrows=2, ncols=4)
        fig.canvas.set_window_title('Volumes per region notmalised tot brain volume')

        for k_id, k in enumerate(ptb_related_regions.keys()):
            pfi_vol_region = jph(pfo_storage, 'VolumesRegionOverTotBV{0}.pkl'.format(k))
            se_vol = pa.read_pickle(pfi_vol_region)
            d = {'cat1': cat1,
                 'cat2': cat2,
                 'vals': se_vol}
            df = pa.DataFrame(data=d, index=atlas_subjects)
            df.name = '{0}'.format(k)
            if k_id == 0:
                ylabel = 'Volume (mm^3)'
            else:
                ylabel = ''

            historgram_of_data_st(ax[k_id // 4, k_id % 4 ], df, ylabel=ylabel, factor=1/3., legend=False)

        ax[1, 3].set_axis_off()
        ax[1, 2].legend(bbox_to_anchor=(1.5, 0.5), loc=2, borderaxespad=0.)
        plt.tight_layout()
        # save figure:
        plt.savefig(jph(pfo_storage, 'VolumesRegionNormalisedTotBrainVol.png'))
        if show:
            plt.show()

    # --> Collection 4: volumes per regions normalised by the body weight of the interesting regions.
    if controller['Collection4']:
        matplotlib.rcParams.update({'font.size': 10})
        fig, ax = plt.subplots(figsize=(12, 8), nrows=2, ncols=4)
        fig.canvas.set_window_title('Volumes per region normalised body weight')

        for k_id, k in enumerate(ptb_related_regions.keys()):
            pfi_vol_region = jph(pfo_storage, 'VolumesRegionOverBodyWeight{0}.pkl'.format(k))
            se_vol = pa.read_pickle(pfi_vol_region)
            d = {'cat1': cat1,
                 'cat2': cat2,
                 'vals': se_vol}
            df = pa.DataFrame(data=d, index=atlas_subjects)
            df.name = '{0}'.format(k)
            if k_id == 0:
                ylabel = 'Volume (mm^3) / body weight (g)'
            else:
                ylabel = ''

            historgram_of_data_st(ax[k_id // 4, k_id % 4 ], df, ylabel=ylabel, factor=1/3., legend=False)

        ax[1, 3].set_axis_off()
        ax[1, 2].legend(bbox_to_anchor=(1.5, 0.5), loc=2, borderaxespad=0.)
        plt.tight_layout()
        # save figure:
        plt.savefig(jph(pfo_storage, 'VolumesNormalisedBodyWeight.png'))
        if show:
            plt.show()

    # --> Collection 5: FA per regions normalised by the body weight of the interesting regions.
    if controller['Collection5']:
        matplotlib.rcParams.update({'font.size': 10})
        fig, ax = plt.subplots(figsize=(14, 8), nrows=2, ncols=4)
        fig.canvas.set_window_title('Volumes per region Normalised')

        for k_id, k in enumerate(ptb_related_regions.keys()):
            pfi_vol_region = jph(pfo_storage, 'FARegion{0}.pkl'.format(k))
            se_FA = pa.read_pickle(pfi_vol_region)
            d = {'cat1': cat1,
                 'cat2': cat2,
                 'vals': se_FA}
            df = pa.DataFrame(data=d, index=atlas_subjects)
            df.name = 'FA {0}'.format(k)
            if k_id == 0:
                ylabel = 'FA'
            else:
                ylabel = ''

            boxplot_of_data_st(ax[k_id // 4, k_id % 4], df, ylabel=ylabel, factor=1 / 2., legend=False)

        ax[1, 3].set_axis_off()
        custom_red = np.array([255, 153, 153]) / 255.
        custom_green = np.array([163, 255, 163]) / 255.
        plt.figtext(0.80, 0.1, 'pre-term', backgroundcolor=custom_red, color='black', weight='roman', size='x-small')
        plt.figtext(0.80, 0.15, 'term', backgroundcolor=custom_green, color='black', weight='roman', size='x-small')
        plt.tight_layout()
        # save figure:
        plt.savefig(jph(pfo_storage, 'FARegion.png'))
        if show:
            plt.show()

    # --> Collection 6: MD per regions normalised by the body weight of the interesting regions.
    if controller['Collection6']:
        matplotlib.rcParams.update({'font.size': 10})
        fig, ax = plt.subplots(figsize=(14, 8), nrows=2, ncols=4)
        fig.canvas.set_window_title('Volumes per region Normalised')

        for k_id, k in enumerate(ptb_related_regions.keys()):
            pfi_vol_region = jph(pfo_storage, 'MDRegion{0}.pkl'.format(k))
            se_FA = pa.read_pickle(pfi_vol_region)
            d = {'cat1': cat1,
                 'cat2': cat2,
                 'vals': se_FA}
            df = pa.DataFrame(data=d, index=atlas_subjects)
            df.name = 'MD {0}'.format(k)
            if k_id == 0:
                ylabel = 'MD'
            else:
                ylabel = ''

            boxplot_of_data_st(ax[k_id // 4, k_id % 4], df, ylabel=ylabel, factor=1 / 2., legend=False)

        ax[1, 3].set_axis_off()
        custom_red = np.array([255, 153, 153]) / 255.
        custom_green = np.array([163, 255, 163]) / 255.
        plt.figtext(0.80, 0.1, 'pre-term', backgroundcolor=custom_red, color='black', weight='roman', size='x-small')
        plt.figtext(0.80, 0.15, 'term', backgroundcolor=custom_green, color='black', weight='roman', size='x-small')
        plt.tight_layout()
        # save figure:
        plt.savefig(jph(pfo_storage, 'MDRegion.png'))
        if show:
            plt.show()


def simple_data_analysis_by_subjects_list(sj_list):

    pfo_storage = '/Volumes/sebastianof/rabbits/B_stats/simple_analysis'
    controller = {'Collection1'     : True,
                  'Collection2'     : True,
                  'Collection3'     : True,
                  'Collection4'     : True,
                  'Collection5'     : True,
                  'Collection6'     : True}
    collect_data_from_subject_list(sj_list, pfo_storage, controller=controller)
    plot_and_save_collected(pfo_storage,  show=True, controller=controller)


if __name__ == '__main__':

    if False:
        # EXAMPLE of rabbbit-valued-dataframe:
        names = ['12xx', '12yy', '12zz', '12aa', '14xx', '14yy', '14zz', '14aa']
        cat1 = pa.Series(['Female', 'Female', 'Female', 'Female', 'Male', 'Male', 'Male', 'Male'], index=names)
        cat2 = pa.Series(['Preterm', 'Preterm', 'Term', 'Term', 'Preterm', 'Preterm', 'Term', 'Term'], index=names)
        vals = pa.Series([1.5, 1.4, 1.3, 1.2, 1.1, 1.0, 0.9, 0.8], index=names)
        d = {'cat1' : cat1,
             'cat2' : cat2,
             'vals' : vals}
        df = pa.DataFrame(data=d)
        df.name = 'vol type, region i'

        print df

        df_F_pre = df.loc[df['cat1'] == 'F'].loc[df['cat2'] == 'pre-term']
        df_F_ter = df.loc[df['cat1'] == 'F'].loc[df['cat2'] == 'term']
        num_M_pre = df.loc[df['cat1'] == 'M'].loc[df['cat2'] == 'pre-term']
        num_M_ter = df.loc[df['cat1'] == 'M'].loc[df['cat2'] == 'term']

        fig, ax = plt.subplots(figsize=(12, 8), nrows=1, ncols=1)
        fig.canvas.set_window_title('zzz')
        historgram_of_data_st(ax, df)

        plt.show()

    if False:
        # EXAMPLE of rabbbit-valued-dataframe:
        names = ['12xx', '12yy', '12zz', '12aa', '14xx', '14yy', '14zz', '14aa']
        cat1 = pa.Series(['Female', 'Female', 'Female', 'Female', 'Male', 'Male', 'Male', 'Male'], index=names)
        cat2 = pa.Series(['Preterm', 'Preterm', 'Term', 'Term', 'Preterm', 'Preterm', 'Term', 'Term'], index=names)
        vals = pa.Series([np.random.randn(1000) for _ in range(len(names))], index=names)
        d = {'cat1': cat1,
             'cat2': cat2,
             'vals': vals}
        df = pa.DataFrame(data=d)
        df.name = 'vol type, region i'

        print df

        fig, ax = plt.subplots(figsize=(12, 8), nrows=1, ncols=1)
        fig.canvas.set_window_title('zzz')
        boxplot_of_data_st(ax, df)

        plt.show()

    if True:

        controller = {'Collection1'     : False,
                      'Collection2'     : False,
                      'Collection3'     : False,
                      'Collection4'     : False,
                      'Collection5'     : True,
                      'Collection6'     : False}

        pfo_storage = '/Volumes/sebastianof/rabbits/B_stats/simple_analysis'
        collect_data_from_subject_list(atlas_subjects, pfo_storage, controller=controller, report_folder='report_stereotaxic')
        plot_and_save_collected(pfo_storage, controller=controller)






