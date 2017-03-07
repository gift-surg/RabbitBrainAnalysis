import numpy as np
import nibabel as nib
import os
from os.path import join as jph

from tools.auxiliary.utils import set_new_data

from tools.correctors.MSME_T2_correctors import corrector_MSME_T2_path

# load data:

pfi_root = '/Users/sebastiano/Desktop/test_manual_sort'
fin_subject = '0802_t1_MSME_T2.nii.gz'
fin_output = '0802_res.nii.gz'
pfi_subject = jph(pfi_root, fin_subject)
pfi_output = jph(pfi_root, fin_output)

corrector_MSME_T2_path(pfi_subject, pfi_output, modality=None)


pfi_root = '/Users/sebastiano/Desktop/test_manual_sort'
fin_subject = '0904_t1_MSME_T2.nii.gz'
fin_output = '0904_res.nii.gz'
pfi_subject = jph(pfi_root, fin_subject)
pfi_output = jph(pfi_root, fin_output)

corrector_MSME_T2_path(pfi_subject, pfi_output, modality=None)



# extract slices:
#
# manual_sort_MSME_path(jph(subject_folder_path, subject_input_name), jph(subject_folder_path, subject_reshuffled_name))
#
# # reorient reshuffled data:
# cmd = 'cp {0} {1} ' \
#       'fslorient -deleteorient {1}; ' \
#       'fslswapdim {1} x z -y {1}; ' \
#       'fslorient -setqformcode 1 {1}; '.format(jph(subject_folder_path, subject_reshuffled_name),
#                                         jph(subject_folder_path, subject_reoriented_name))
#
# os.system(cmd)
