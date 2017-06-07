import os
import nibabel as nib

from tools.definitions import root_pilot_study
from tools.auxiliary.utils import set_new_data
from tools.label_manager.relabeller import assign_all_other_labels_the_same_value


# load data:
root_data = '/Users/sebastiano/Desktop/preliminary_template_construction'
path_atlas = os.path.join(root_data, '1305_seg_half.nii.gz')
path_atlas_new = os.path.join(root_data, '1305_seg_half_ROI.nii.gz')

input_atlas_nib = nib.load(path_atlas)
data_atlas = input_atlas_nib.get_data()

# set parameters
# corpus callosum, hippocampi, sibiculi, periventricular white matter, thalami
labels_to_keep = [277,  # 278,  # caudate nuclei
                  305,  # 306,  # Cerbellar hemispheres
                  281,  # thalamus
                  309,  # hypothalamus
                  287,  # Hippocampi
                  257,  # Frontal cortex
                  291,  # internal capsule
                  307,  # corpus callosum
                  295,  # Fimbria of hippocampi
                  308   # anterior commissure
                  ]
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
