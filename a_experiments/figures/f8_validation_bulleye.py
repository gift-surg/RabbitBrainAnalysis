"""
Inspired by
https://matplotlib.org/examples/pylab_examples/leftventricle_bulleye.html
"""
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt


from a_experiments.figures.bulleye_utils import bulls_eye


if __name__ == '__main__':

    # TEST bull-eye three-fold
    if True:
        # Very dummy data:
        data = np.array(range(29)) + 1

        # Make a figure and axes with dimensions as desired.
        fig, ax = plt.subplots(figsize=(12, 8), nrows=1, ncols=3,
                               subplot_kw=dict(projection='polar'))
        fig.canvas.set_window_title('Left Ventricle Bulls Eyes (AHA)')

        # First one:
        cmap = mpl.cm.viridis
        norm = mpl.colors.Normalize(vmin=1, vmax=29)

        bulls_eye(ax[0], data, cmap=cmap, norm=norm)
        ax[0].set_title('Bulls Eye (AHA)')

        axl = fig.add_axes([0.14, 0.15, 0.2, 0.05])
        cb1 = mpl.colorbar.ColorbarBase(axl, cmap=cmap, norm=norm, orientation='horizontal')
        cb1.set_label('Some Units')

        # Second one
        cmap2 = mpl.cm.cool
        norm2 = mpl.colors.Normalize(vmin=1, vmax=29)

        bulls_eye(ax[1], data, cmap=cmap2, norm=norm2)
        ax[1].set_title('Bulls Eye (AHA)')

        axl2 = fig.add_axes([0.41, 0.15, 0.2, 0.05])
        cb2 = mpl.colorbar.ColorbarBase(axl2, cmap=cmap2, norm=norm2, orientation='horizontal')
        cb2.set_label('Some other units')

        # Third one
        cmap3 = mpl.cm.winter
        norm3 = mpl.colors.Normalize(vmin=1, vmax=29)

        bulls_eye(ax[2], data, cmap=cmap3, norm=norm3)
        ax[2].set_title('Bulls Eye third')

        axl3 = fig.add_axes([0.69, 0.15, 0.2, 0.05])
        cb3 = mpl.colorbar.ColorbarBase(axl3, cmap=cmap3, norm=norm3, orientation='horizontal')
        cb3.set_label('Some more units')

        plt.show()
