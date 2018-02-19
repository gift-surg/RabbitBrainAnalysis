"""
Standard measurements on the selected data.
Volume, Volume/tot_volume, FA_i, MD_i, i in regions.

data_st:
data structure defined as:

data_st = OrderedDict()
data_st['title'] = 'vol type, region i'
data_st['12xx'] = ['M/F', 'term/pre-term', value]

"""
import numpy as np
import pandas as pa
import matplotlib.pyplot as plt


def historgram_of_data_st(ax, df):
    """

    :param ax: matplotlib axis object
    :param df: rabbbit-valued-dataframe as defined in the documentation.
    :return:
    """
    # fill each category separately:

    df_F_pre = df.loc[df['cat1'] == 'F'].loc[df['cat2'] == 'pre-term']
    df_F_ter = df.loc[df['cat1'] == 'F'].loc[df['cat2'] == 'term']
    df_M_pre = df.loc[df['cat1'] == 'M'].loc[df['cat2'] == 'pre-term']
    df_M_ter = df.loc[df['cat1'] == 'M'].loc[df['cat2'] == 'term']

    lens = [0, len(df_F_pre.index), len(df_F_ter.index), len(df_M_pre.index), len(df_M_ter.index)]
    cum_lens = [sum(lens[:(l+1)]) for l in range(len(lens))]

    custom_red = np.array([255, 153, 153]) / 255.
    custom_green = np.array([163, 255, 163]) / 255.

    ax.bar(range(cum_lens[0], cum_lens[1]), list(df_F_pre['vals']), width=0.4, label="pre-term", align="center", color=custom_red)
    ax.bar(range(cum_lens[1], cum_lens[2]), list(df_F_ter['vals']), width=0.4, label="term", align="center", color=custom_green)
    ax.bar(range(cum_lens[2], cum_lens[3]), list(df_M_pre['vals']), width=0.4, label="pre-term", align="center", color=custom_red)
    ax.bar(range(cum_lens[3], cum_lens[4]), list(df_M_ter['vals']), width=0.4, label="pre-term", align="center", color=custom_green)

    # add vertical line separating males females
    tot_females = sum([len(df_F_pre.index), len(df_F_ter.index)])
    tot_males   = sum([len(df_M_pre.index), len(df_M_ter.index)])
    ax.axvline(x=tot_females - 0.5, color='k', alpha=0.4)

    # add labels and text axis
    xlabel = 'subject'
    ylabel = 'vals'
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_title(df.name)
    labels = list(df_F_pre.index) + list(df_F_ter.index) + list(df_M_pre.index) + list(df_M_ter.index)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45)

    # annotate male female text:
    y_lim = ax.get_ylim()
    y_hight = 0.4 * (y_lim[1] - y_lim[0])
    ax.annotate('Female', xy=(tot_females/2. - 1, y_hight), color='gray', size=20)
    ax.annotate('Male', xy=(tot_females + tot_males/2. - 0.75, y_hight), color='gray', size=20)

    # add legend
    ax.legend()
    # add grid
    ax.grid()
    ax.set_axisbelow(True)


def collect_vols(sj_list, regions='tot', normalise=False):
    return


def collect_vols_normalised(sj_list, regions='tot'):
    return


def collect_under_labels(sj_list, regions, map='FA'):
    pass


def collector_subject_list(sj_list, pfo_storage):
    """
    :param sj_list: list of subjects
    :param pfo_dump: where to save the obtained dataframe per region, per value.
    :return:
    """
    pass


def plot_collected(pfo_storage):
    """
    Plots all the dataframe that it finds in the storage folder.
    :param pfo_storage: path to folder where data are stored.
    :return:
    """
    pass


if __name__ == '__main__':

    if True:
        # example of rabbbit-valued-dataframe:
        names = ['12xx', '12yy', '12zz', '12aa', '14xx', '14yy', '14zz', '14aa']
        cat1 = pa.Series(['F', 'F', 'F', 'F', 'M', 'M', 'M', 'M'], index=names)
        cat2 = pa.Series(['pre-term', 'pre-term', 'term', 'term', 'pre-term', 'pre-term', 'term', 'term'], index=names)
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
