# https://stackoverflow.com/questions/31502958/drawing-a-bootstrap-sample-from-a-pandas-dataframe
# https://matplotlib.org/gallery/text_labels_and_annotations/annotation_demo.html
# https://matplotlib.org/examples/pylab_examples/fancybox_demo2.html
import os
from os.path import join as jph
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import matplotlib.patches as mpatch
import pandas as pd
import numpy as np
import pickle
import seaborn as sns

pfo_data = '/Users/sebastiano/a_data/TData/rabbits'

# Data-frames:
pfi_df_volume_bup            = jph(pfo_data, 'df_volumes.csv')
pfi_df_volume_per_region_bup = jph(pfo_data, 'df_volumes_per_region.csv')
pfi_df_FA_per_region_bup     = jph(pfo_data, 'df_FA_per_region.csv')
pfi_df_MD_per_region_bup     = jph(pfo_data, 'df_MD_per_region.csv')


for ph in [pfi_df_volume_bup, pfi_df_volume_per_region_bup, pfi_df_FA_per_region_bup, pfi_df_MD_per_region_bup]:
    assert os.path.exists(ph), ph

list_regions = ['Hippocampus',
                'Caudate nucleus',
                'Putamen',
                'Thalamus',
                'Hypothalamus',
                'Corpus Callosum',
                'Internal capsule',
                'Claustrum',
                'Amygdala']

# sns.set()
# plt.rc('text', usetex=True)
# title_font = {'family' : 'serif', 'size'   : 12}
# axis_font = {'family' : 'serif', 'size': 10}
# tick_font_size_x = 8
# tick_font_size_y = 8
# plt.rc('font', **title_font)
dpi = 200

fig, ax = plt.subplots(nrows=1, ncols=1, figsize=[5, 3], dpi=dpi, clear=True)


fig.canvas.set_window_title('Brain volume per subject')


el = Ellipse((2, -1), 0.5, 0.5)

ann = ax.annotate('bubble,\ncontours',
                  xy=(2., 3), xycoords='data',
                  xytext=(0, 0), textcoords='offset points',
                  size=20,
                  bbox=dict(boxstyle="round",
                            fc=(1.0, 0.7, 0.7),
                            ec=(1., .5, .5)),
                  arrowprops=dict(arrowstyle="wedge,tail_width=1.",
                                  fc=(1.0, 0.7, 0.7), ec=(1., .5, .5),
                                  patchA=None,
                                  patchB=el,
                                  relpos=(0.2, 0.8),
                                  connectionstyle="arc3,rad=-0.1"))

#
# styles = mpatch.BoxStyle.get_styles()
# print(styles)
# spacing = 1.2
#
# figheight = (spacing * len(styles) + .5)
# fig1 = plt.figure(1, (4/1.5, figheight/1.5))
# fontsize = 0.3 * 72
#
# for i, stylename in enumerate(sorted(styles.keys())):
#     fig1.text(0.5, (spacing * (float(len(styles)) - i) - 0.5)/figheight, stylename,
#               ha="center",
#               size=fontsize,
#               transform=fig1.transFigure,
#               bbox=dict(boxstyle=stylename, fc="w", ec="k"))
plt.draw()
plt.show()