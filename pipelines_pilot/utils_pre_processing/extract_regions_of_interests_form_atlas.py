import os
import nibabel as nib

from definitions import root_pilot_study
from tools.auxiliary.utils import set_new_data
from tools.label_manager.relabeller import assign_all_other_labels_the_same_value


path_to_atlas = os.path.join()

# load data:
root_data = '/Users/sebastiano/Desktop/cropping_tests'
path_atlas = os.path.join(root_data, 'barcelona_atlas_on_1305_170112_trimmed_then_smoothed1_1_TEST.nii.gz')
path_atlas_new = os.path.join(root_data, 'selected_labels.nii.gz')

input_atlas_nib = nib.load(path_atlas)
data_atlas = input_atlas_nib.get_data()

# set parameters
# corpus callosum, hippocampi, sibiculi, periventricular white matter, thalami
labels_to_keep = [51, 31, 32, 63, 64, 33, 34, 25, 26]
same_value_label = 255

# apply function
new_data = assign_all_other_labels_the_same_value(data_atlas,
                                                labels_to_keep=labels_to_keep,
                                                same_value_label=same_value_label)

# save results
print(new_data.shape)
im_new = set_new_data(input_atlas_nib, new_data)
print(im_new.files_types)
nib.save(im_new, path_atlas_new)
