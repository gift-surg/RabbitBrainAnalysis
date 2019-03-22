from scipy.stats import norm
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns


def get_histogram_ax(ax, data, observed=None, percentile_annotation=False, title='hist fitted with normal',
                     pearson=True, x_label=None, y_label=None):
    title_font = {'family': 'serif', 'size': 7}
    axis_label_font = {'family': 'serif', 'size': 6}
    annotation_font = {'color': 'k', 'fontsize': 6, 'ha': 'center', 'va': 'bottom', 'family': 'serif', 'alpha': 0.8}

    sns.distplot(data, fit=norm, ax=ax, kde=False, bins=40, hist=True, fit_kws={"color": "b", "lw": 0.6, "label": "KDE"},
                 norm_hist=False)

    if x_label:
        ax.set_xlabel(x_label, **axis_label_font)
    if y_label:
        ax.set_ylabel(y_label, **axis_label_font)

    if title is not None:
        ax.set_title(title, **title_font)

    mu, sigma = norm.fit(data)

    if observed is not None:
        if pearson:
            index = np.abs(observed - mu) / sigma
        else:
            index = observed

        text_style_observed = {'color': 'r', 'fontsize': 7, 'ha': 'center', 'va': 'center', 'family': 'serif', 'rotation': 0}
        y_lim_low, y_lim_high = ax.get_ylim()
        _, x_lim_high = ax.get_xlim()
        ax.plot([observed, observed], [y_lim_low, 0.85 * y_lim_high], color='r', linewidth=0.6)
        ax.text(observed, 0.9 * y_lim_high, str(np.round(index, decimals=1)), text_style_observed.copy())

    if percentile_annotation:

        y_lim_low, y_lim_high = ax.get_ylim()

        offset = 0
        for s, he, annot in zip([1, 2, 3], [0.6, 0.7, 0.8], ['68\%', '95\%', '99.7\%']):

            ax.plot([s * sigma, s * sigma], [y_lim_low, he * y_lim_high], color='grey', linewidth=0.5)
            ax.plot([-s * sigma, -s * sigma], [y_lim_low, he * y_lim_high], color='grey', linewidth=0.5)
            ax.plot([-s * sigma - offset, s * sigma + offset], [he * y_lim_high - offset, he * y_lim_high - offset],
                    color='grey', linewidth=0.5)
            ax.text(mu, he * y_lim_high, annot, annotation_font.copy())


def get_histogram(list_data, list_titles, list_observed, nrows=1, ncols=1, figsize=(5, 3), percentile_annotation=False, dpi=300,
                  x_label=None, y_label=None):

    # ---------- Parameters -------

    plt.rc('text', usetex=True)
    title_font = {'family': 'serif', 'size': 12}
    plt.rc('font', **title_font)

    # --------- Initialise figure ----------

    fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize, dpi=dpi)

    fig.canvas.set_window_title('test fitting normal')

    if len(list_data) == 1:
        get_histogram_ax(ax, list_data[0], title=list_titles[0], observed=list_observed[0],
                         percentile_annotation=percentile_annotation, x_label=x_label, y_label=y_label)
        ax.tick_params(labelsize=6, width=0.5)

    else:
        percentile_annotation_first = False
        for c in range(ncols):
            for r in range(nrows):
                if r == c == 1 :
                    if percentile_annotation:
                        percentile_annotation_first = True

                get_histogram_ax(ax[r][c], list_data[r][c], title=list_titles[r][c],
                                 observed=list_observed[r][c],
                                 percentile_annotation=percentile_annotation_first,
                                 x_label=x_label, y_label=y_label)

                ax[r][c].tick_params(labelsize=6, width=0.5)


if __name__ == '__main__':

    controller = {'create single hist'  : True,
                  'create multiple hist': False}

    if controller['create single hist']:
        xx = np.random.normal(size=1000)
        get_histogram([xx], ['title'], [2.4], percentile_annotation=True)
        sns.plt.tight_layout()
        sns.plt.show()

    if controller['create multiple hist']:
        x = np.random.normal(size=1000)
        get_histogram([[np.random.normal(size=1000), np.random.normal(size=1000), np.random.normal(size=1000)],
                       [np.random.normal(size=1000), np.random.normal(size=1000), np.random.normal(size=1000)],
                       [np.random.normal(size=1000), np.random.normal(size=1000), np.random.normal(size=1000)]],
                      [['a', 'b', 'c'], ['d', 'e', 'f'], ['g', 'h', 'i']], [[1, 2, 3], [1.2, 2.2, 3.3], [0, 0, 0]],
                      nrows=3, ncols=3, figsize=[6.5, 4.5])
        sns.plt.tight_layout()
        sns.plt.show()
