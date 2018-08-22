import os
from os.path import join as jph

from nilabel.main import Nilabel as NiL
from nilabel.tools.aux_methods.label_descriptor_manager import LabelsDescriptorManager as LDM


# ---- PATH MANAGER ----

# Input
root = '/Users/sebastiano/Dropbox/RabbitEOP-MRI/study/A_MultiAtlas_W8/12503/segm/automatic'
pfi_input_segmentation = jph(root, '12503_pre_sym.nii.gz')
pfi_labels_descriptor  = '/Users/sebastiano/Dropbox/RabbitEOP-MRI/study/A_MultiAtlas_W8/labels_descriptor.txt'

# Output
log_file_before_cleaning          = jph(root, 'log_before_cleaning.txt')
pfi_output_cleaned_segmentation   = jph(root, '12503_pre_sym_cleaned.nii.gz')
log_file_after_cleaning           = jph(root, 'log_after_cleaning.txt')
pfi_differece_cleaned_non_cleaned = jph(root, 'difference_half_cleaned_uncleaned.nii.gz')


# ---- PROCESS ----

nil = NiL()
ldm = LDM(pfi_labels_descriptor)

print '---------------------------'
print '---------------------------'
print 'Cleaning segmentation {}'.format(pfi_input_segmentation)
print '---------------------------\n\n'

# get the report before
nil.check.number_connected_components_per_label(pfi_input_segmentation,
                                                where_to_save_the_log_file=log_file_before_cleaning)

# get the labels_correspondences - do not clean the 0, get 2 components for the 201
labels = ldm.get_dict_itk_snap().keys()
correspondences_lab_comps  = []
for l in labels:
    if l == 201:
        correspondences_lab_comps.append([l, 3])
    elif l == 229:
        correspondences_lab_comps.append([l, 2])
    elif l == 230:
        correspondences_lab_comps.append([l, 2])
    elif l == 127:
        correspondences_lab_comps.append([l, 2])
    elif l == 0:
        pass
    else:
        correspondences_lab_comps.append([l, 1])

print('Wanted final number of components per label:')
print(correspondences_lab_comps)

# get the cleaned segmentation
nil.manipulate_labels.clean_segmentation(pfi_input_segmentation, pfi_output_cleaned_segmentation,
                                         labels_to_clean=correspondences_lab_comps)

# get the report of the connected components afterwards
nil.check.number_connected_components_per_label(pfi_output_cleaned_segmentation,
                                                where_to_save_the_log_file=log_file_after_cleaning)

# get the differences between the non-liceaned and the cleaned:

cmd = 'seg_maths {0} -sub {1} {2}'.format(pfi_input_segmentation, pfi_output_cleaned_segmentation,
                                          pfi_differece_cleaned_non_cleaned)
os.system(cmd)
cmd = 'seg_maths {0} -bin {0}'.format(pfi_differece_cleaned_non_cleaned)
os.system(cmd)