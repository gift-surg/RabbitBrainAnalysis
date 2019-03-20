from scipy.stats import norm
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


def get_histogram_ax(ax, data, observed=None, percentile_annotation=None, title='hist fitted with normal'):
    title_font = {'family': 'serif', 'size': 7}

    sns.distplot(data, fit=norm, ax=ax, kde=False, fit_kws={"color": "b", "lw": 0.6, "label": "KDE"})

    if title is not None:
        ax.set_title(title, **title_font)

    if observed is not None:
        text_style_observed = {'color': 'r', 'fontsize': 7, 'ha': 'left', 'va': 'bottom', 'family': 'serif', 'rotation': 0}
        y_lim_low, y_lim_high = ax.get_ylim()
        ax.plot([observed, observed], [y_lim_low, y_lim_high], color='r', linewidth=0.6)
        ax.text(observed + 0.1, 0.8 * y_lim_high, str(observed), text_style_observed.copy())

    if percentile_annotation is not None:
        mu, sigma = norm.fit(x)
        y_lim_low, y_lim_high = ax.get_ylim()


        print(mu)


def get_histogram(list_data, list_titles, list_observed, nrows=1, ncols=1, figsize=(5, 3)):

    # ---------- Parameters -------

    plt.rc('text', usetex=True)
    title_font = {'family': 'serif', 'size': 12}
    # axis_font = {'family': 'serif', 'size': 10}
    # tick_font_size_x = 8
    # tick_font_size_y = 8
    plt.rc('font', **title_font)

    # --------- Initialise figure ----------

    fig, ax = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize, dpi=200)

    fig.canvas.set_window_title('test fitting normal')

    if len(list_data) == 1:
        get_histogram_ax(ax, list_data[0], title=list_titles[0], observed=list_observed[0])
        ax.tick_params(labelsize=6, width=0.5)

    else:
        for c in range(ncols):
            for r in range(nrows):
                if r == c == 1:
                    percentile_annotation = True
                else:
                    percentile_annotation = None

                get_histogram_ax(ax[r][c], list_data[r][c], title=list_titles[r][c],
                                 observed=list_observed[r][c],
                                 percentile_annotation=percentile_annotation)

                ax[r][c].tick_params(labelsize=6, width=0.5)


if __name__ == '__main__':

    # create an histogram
    x = np.random.normal(size=1000)
    get_histogram([x], ['title'], [2.4])
    sns.plt.tight_layout()
    sns.plt.show()

    # create Multiples histogram
    x = np.random.normal(size=1000)
    get_histogram([[np.random.normal(size=1000), np.random.normal(size=1000), np.random.normal(size=1000)],
                   [np.random.normal(size=1000), np.random.normal(size=1000), np.random.normal(size=1000)],
                   [np.random.normal(size=1000), np.random.normal(size=1000), np.random.normal(size=1000)]],
                  [['a', 'b', 'c'], ['d', 'e', 'f'], ['g', 'h', 'i']], [[1, 2, 3], [1.2, 2.2, 3.3], [0, 0, 0]],
                  nrows=3, ncols=3, figsize=[6.5, 4.5])
    sns.plt.tight_layout()
    sns.plt.show()
