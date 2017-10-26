"""
Inspired by
https://matplotlib.org/examples/pylab_examples/leftventricle_bulleye.html
"""

import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt



def bullseye_plot(ax, data, segBold=None, cmap=None, norm=None,
                  raidal_subdivisions=(2, 8, 8, 11),
                  centered=(True, False, False, True),
                  add_nomenclatures=False):
    """
    Clockwise, from smaller radius to bigger radius.
    """
    if segBold is None:
        segBold = []

    line_width = 1.5
    data = np.array(data).ravel()

    if cmap is None:
        cmap = plt.cm.viridis

    if norm is None:
        norm = mpl.colors.Normalize(vmin=data.min(), vmax=data.max())

    theta = np.linspace(0, 2*np.pi, 768)
    r = np.linspace(0, 1, len(raidal_subdivisions)+1)

    if isinstance(add_nomenclatures, bool):
        if add_nomenclatures:
            nomenclatures = range(sum(raidal_subdivisions))
    elif isinstance(add_nomenclatures, list) or isinstance(add_nomenclatures, tuple):
        assert len(add_nomenclatures) == sum(raidal_subdivisions)
        nomenclatures = add_nomenclatures[:]
        add_nomenclatures = True

    for rs_id, rs in enumerate(raidal_subdivisions):
        for i in range(rs):
            theta_i = i * 2 * np.pi / rs + np.pi / 2
            if not centered[rs_id]:
                theta_i += (2 * np.pi / rs) / 2

            # Create colour fillings for each cell:
            cell_resolution = 128
            theta_interval = np.linspace(theta_i, theta_i + 2 * np.pi / rs, cell_resolution)
            r_interval = np.array([r[rs_id], r[rs_id+1]])
            angle  = np.repeat(theta_interval[:, np.newaxis], 2, axis=1)
            radius = np.repeat(r_interval[:, np.newaxis], cell_resolution, axis=1).T
            z = np.ones((cell_resolution, 2))*data[rs_id + i]
            ax.pcolormesh(angle, radius, z, cmap=cmap, norm=norm)

            # Create radial bounds
            ax.plot([theta_i, theta_i], [r[rs_id], r[rs_id+1]], '-k', lw=line_width)
            if add_nomenclatures:
                cell_center = (theta_i + (2 * np.pi / rs) / 2, (r[rs_id] + r[rs_id+1] / 2.0))
                pass


    # Create the circular bounds
    line_width_circular = line_width
    for i in range(r.shape[0]):
        if i == -1:
            line_width_circular = int(line_width / 2.)
        ax.plot(theta, np.repeat(r[i], theta.shape), '-k', lw=line_width_circular)



    ax.grid(False)
    ax.set_ylim([0, 1])
    ax.set_yticklabels([])
    ax.set_xticklabels([])


# Create the fake data
data = np.array(range(17)) + 1


# Make a figure and axes with dimensions as desired.
fig, ax = plt.subplots(figsize=(12, 8), nrows=1, ncols=3,
                       subplot_kw=dict(projection='polar'))
fig.canvas.set_window_title('Left Ventricle Bulls Eyes (AHA)')

# Create the axis for the colorbars
axl = fig.add_axes([0.14, 0.15, 0.2, 0.05])
axl2 = fig.add_axes([0.41, 0.15, 0.2, 0.05])
axl3 = fig.add_axes([0.69, 0.15, 0.2, 0.05])


# Set the colormap and norm to correspond to the data for which
# the colorbar will be used.
cmap = mpl.cm.viridis
norm = mpl.colors.Normalize(vmin=1, vmax=17)

# ColorbarBase derives from ScalarMappable and puts a colorbar
# in a specified axes, so it has everything needed for a
# standalone colorbar.  There are many more kwargs, but the
# following gives a basic continuous colorbar with ticks
# and labels.
cb1 = mpl.colorbar.ColorbarBase(axl, cmap=cmap, norm=norm,
                                orientation='horizontal')
cb1.set_label('Some Units')


# Set the colormap and norm to correspond to the data for which
# the colorbar will be used.
cmap2 = mpl.cm.cool
norm2 = mpl.colors.Normalize(vmin=1, vmax=17)

# ColorbarBase derives from ScalarMappable and puts a colorbar
# in a specified axes, so it has everything needed for a
# standalone colorbar.  There are many more kwargs, but the
# following gives a basic continuous colorbar with ticks
# and labels.
cb2 = mpl.colorbar.ColorbarBase(axl2, cmap=cmap2, norm=norm2,
                                orientation='horizontal')
cb2.set_label('Some other units')


# The second example illustrates the use of a ListedColormap, a
# BoundaryNorm, and extended ends to show the "over" and "under"
# value colors.
cmap3 = mpl.colors.ListedColormap(['r', 'g', 'b', 'c'])
cmap3.set_over('0.35')
cmap3.set_under('0.75')

# If a ListedColormap is used, the length of the bounds array must be
# one greater than the length of the color list.  The bounds must be
# monotonically increasing.
bounds = [2, 3, 7, 9, 15]
norm3 = mpl.colors.BoundaryNorm(bounds, cmap3.N)
cb3 = mpl.colorbar.ColorbarBase(axl3, cmap=cmap3, norm=norm3,
                                # to use 'extend', you must
                                # specify two extra boundaries:
                                boundaries=[0]+bounds+[18],
                                extend='both',
                                ticks=bounds,  # optional
                                spacing='proportional',
                                orientation='horizontal')
cb3.set_label('Discrete intervals, some other units')


# Create the 17 segment model
bullseye_plot(ax[0], data, cmap=cmap, norm=norm)
ax[0].set_title('Bulls Eye (AHA)')

bullseye_plot(ax[1], data, cmap=cmap2, norm=norm2)
ax[1].set_title('Bulls Eye (AHA)')

bullseye_plot(ax[2], data, segBold=[3, 5, 6, 11, 12, 16],
              cmap=cmap3, norm=norm3)
ax[2].set_title('Segments [3,5,6,11,12,16] in bold')

plt.show()