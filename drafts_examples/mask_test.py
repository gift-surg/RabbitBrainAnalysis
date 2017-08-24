import os
import nibabel as nib

from labels_manager.tools.aux_methods.utils_nib import set_new_data
from tools.auxiliary.lesion_mask_extractor import percentile_lesion_mask_extractor_only_from_image

pfi_im_test = '/Users/sebastiano/Desktop/test_im/3405_MSME_bfc_tp0.nii.gz'
pfi_im_mask_1 = '/Users/sebastiano/Desktop/test_im/3405_MSME_bfc_tp0_mask_MoG.nii.gz'
pfi_im_mask_2 = '/Users/sebastiano/Desktop/test_im/3405_MSME_bfc_tp0_mask_Perc.nii.gz'

im = nib.load(pfi_im_test)

new_data_2 = percentile_lesion_mask_extractor_only_from_image(im.get_data(), percentile_range=(30, 95))
new_im_2 = set_new_data(im, new_data=new_data_2)
nib.save(new_im_2, filename=pfi_im_mask_2)

os.system('seg_maths {0} -fill {1}'.format(pfi_im_mask_2, pfi_im_mask_2))
os.system('seg_maths {0} -ero 1 {1}'.format(pfi_im_mask_2, pfi_im_mask_2))
os.system('seg_maths {0} -dil 1 {1}'.format(pfi_im_mask_2, pfi_im_mask_2))
os.system('seg_maths {0} -smol 2 {1}'.format(pfi_im_mask_2, pfi_im_mask_2))
