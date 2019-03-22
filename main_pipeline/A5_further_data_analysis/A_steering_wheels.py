import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib as mpl
from matplotlib import rcParams

import numpy as np


def multiple_testing_axis(ax, vals, cmap=mpl.cm.autumn_r, norm=mpl.colors.Normalize(vmin=0, vmax=3),
                          axis_title='axis title'):
    """
    vals = {'Zero' : <label zero>,
                'One'  : <label one>,
                'Two'  : <label two>,
                'Three': <label three>,
                'Zero_One'   : <value from zero to one>,
                'Zero_Two'   : <value from zero to two>,
                'Zero_Three' : <value from zero to Three>,
                'One_Two'    : <value from one to two>,
                'Two_Three'  : <value from two to three>,
                'Three_one'  : <value from three to one>,
                }
    :param ax:
    :param vals:
    :param cmap:
    :param norm:
    :param axis_title:
    :param pearson:
    :return:
    """

    # ----- Local parameters  -------------

    text_style_centre = {'color': 'k', 'fontsize': 9, 'ha': 'center', 'va': 'center', 'family' : 'serif',
                         'bbox': dict(boxstyle="round",
                                      ec=(0, 0, 0, 0.8),
                                      fc=(1, 1, 1))}

    text_style_sides = {'color': 'k', 'fontsize': 7, 'ha': 'center', 'va': 'center', 'family' : 'serif',
                        'bbox': dict(boxstyle="round",
                                     ec=(0, 0, 0, 0.8),
                                     fc=(1, 1, 1))}

    text_style_between = {'color': 'k', 'fontsize': 6, 'ha': 'center', 'va': 'center', 'family' : 'serif'}

    title_font = {'family': 'serif', 'size': 6}

    # ----- auxiliary function --------

    def deg2rad(deg):
        return float(deg * 2 * np.pi / 360)

    # ------- TEXT centre and sides --------

    # Zero
    ax.text(0, 0, vals['Zero'], text_style_centre.copy())
    # One
    ax.text(deg2rad(30), 0.8, vals['One'], text_style_sides.copy())
    # Two
    ax.text(deg2rad(150), 0.8, vals['Two'], text_style_sides.copy())
    # Three
    ax.text(deg2rad(270), 0.8, vals['Three'], text_style_sides.copy())

    # ------- Graphics Circular --------

    # From One to Two
    ax.add_patch(Rectangle((deg2rad(30), 0.75), width=deg2rad(120), height=0.1, color=cmap(norm(vals['One_Two'])),
                           alpha=0.5, linewidth=0))
    # From One to Three
    ax.add_patch(Rectangle((deg2rad(270), 0.75), width=deg2rad(120), height=0.1, color=cmap(norm(vals['One_Three'])),
                           alpha=0.5, linewidth=0))
    # From Two to Three
    ax.add_patch(Rectangle((deg2rad(150), 0.75), width=deg2rad(120), height=0.1, color=cmap(norm(vals['Two_Three'])),
                           alpha=0.5, linewidth=0))
    # hack for the rectangles in polar coordinates.
    ax.bar(0, 1).remove()

    # ------- Graphics Radial --------

    # From Zero to One
    ax.bar(deg2rad(30), 0.8, deg2rad(12), bottom=0, color=cmap(norm(vals['Zero_One'])), alpha=0.5)
    # From Zero to Two
    ax.bar(deg2rad(150), 0.8, deg2rad(12), bottom=0, color=cmap(norm(vals['Zero_Two'])), alpha=0.5)
    # From Zero to Two
    ax.bar(deg2rad(270), 0.8, deg2rad(12), bottom=0, color=cmap(norm(vals['Zero_Three'])), alpha=0.5)

    # ------- Annotation Circular --------

    # From One to Two
    ax.text(deg2rad(90), 0.8, vals['One_Two'], text_style_between.copy())
    # From Two to Three
    ax.text(deg2rad(210), 0.8, vals['Two_Three'], text_style_between.copy())
    # From Three to One
    ax.text(deg2rad(-30), 0.8, vals['One_Three'], text_style_between.copy())

    # ------- Annotation Radial --------

    # From Zero to One
    ax.text(deg2rad(30), 0.4, vals['Zero_One'], text_style_between.copy())
    # From Zero to Two
    ax.text(deg2rad(150), 0.4, vals['Zero_Two'], text_style_between.copy())
    # From Zero to Three
    ax.text(deg2rad(270), 0.4, vals['Zero_Three'], text_style_between.copy())
    # Hack again:
    ax.set_rmax(1)

    # --------- Final set up ----------

    ax.grid(False)
    ax.set_ylim([0, 1])
    ax.set_yticklabels([])
    ax.set_xticklabels([])
    ax.axis("off")

    ax.set_title(axis_title, **title_font)


def visualise_multiple_testing(vals_list, cmap=mpl.cm.autumn_r, add_colorbar=True, window_title='Prototype',
                               titles=('title', ), nrows=1, ncols=1, figsize=(3, 3)):
    # ---- Color manager ----

    norm = mpl.colors.Normalize(vmin=0, vmax=3)
    plt.rc('text', usetex=True)
    title_font = {'family': 'serif', 'size': 12}
    # axis_font = {'family': 'serif', 'size': 10}
    # tick_font_size_x = 8
    # tick_font_size_y = 8
    plt.rc('font', **title_font)
    # ---------- Parameters --------- #

    dpi = 200

    # ----- initialise figure  -------------
    # plt.rc('text', usetex=True)

    fig, axes = plt.subplots(nrows=nrows, ncols=ncols, figsize=figsize, dpi=dpi, subplot_kw=dict(projection='polar'))

    fig.canvas.set_window_title(window_title)

    # ----- Fill axis  -------------

    if len(vals_list) == 1:
        multiple_testing_axis(axes, vals_list[0], cmap=mpl.cm.autumn_r, axis_title=titles[0], norm=norm)

    else:
        for c in range(ncols):
            for r in range(nrows):
                multiple_testing_axis(axes[r][c], vals_list[r][c], cmap=mpl.cm.autumn_r, axis_title=titles[r][c], norm=norm)

    # ----- Colorbar ----

    if add_colorbar:
        axl = fig.add_axes([0.85, 0.15, 0.02, 0.7])
        cb1 = mpl.colorbar.ColorbarBase(axl, cmap=cmap, norm=norm, orientation='vertical', alpha=0.5)
        cb1.ax.set_ylabel('sigma', rotation=-90, va="bottom", size=8)

        cb1.ax.tick_params(labelsize=6, width=0.5)


if __name__ == '__main__':

    vals = {'Zero' : 'T',
            'One'  : 'PT',
            'Two'  : 'LPT',
            'Three': 'LPT+',
            'Zero_One'   : 0.1,
            'Zero_Two'   : 0.2,
            'Zero_Three' : 0.3,
            'One_Two'    : 1.2,
            'One_Three'  : 1.3,
            'Two_Three'  : 2.3,
            }

    # visualise a single graph with the colorbar
    rcParams['axes.titlepad'] = -5
    visualise_multiple_testing([vals], titles=['single window title'], figsize=(3, 2.5))
    plt.tight_layout()
    plt.show()

    # visualise a multiple graph with no colorbar
    rcParams['axes.titlepad'] = -2
    visualise_multiple_testing([[vals, vals, vals], [vals, vals, vals], [vals, vals, vals]],
                               titles=[['a', 'b', 'c'], ['d', 'e', 'f'], ['g', 'h', 'i']], nrows=3, ncols=3,
                               add_colorbar=False, figsize=(5.5, 4.5))
    plt.tight_layout()
    plt.show()
