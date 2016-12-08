import os

from tools.correctors.label_managements import keep_only_one_label_path
from definitions import root_path_data

main_path = os.path.join(root_path_data, 'pipelines', 'zz_visual_assessment', 'compare_in_skull_ex_skull')

im_path = os.path.join(main_path, 'subj_1702_markers.nii.gz')
out_path = os.path.join(main_path, 'subj_1702_markers_useful.nii.gz')


keep_only_one_label_path(im_path, out_path, [18, ])
