import os
import numpy as np
import nibabel as nib

from definitions import root_ex_vivo_template
from tools.auxiliary.utils import set_new_data


path_experiments = os.path.join(root_ex_vivo_template, 'zz_experiments')

path_subject  = os.path.join(path_experiments, '1203_3D.nii.gz')
path_ciccione = os.path.join(path_experiments, 'ciccione_1203_3D.nii.gz')

path_lesions_mask = os.path.join(path_experiments, '1203_lesions.nii.gz')


im = nib.load(path_subject)
mask = nib.load(path_ciccione)

im_data   = im.get_data()
mask_data = mask.get_data()

lesion_data = np.zeros_like(im.get_data())

dim_x, dim_y, dim_z = list(lesion_data.shape)

for i in range(dim_x):
    for j in range(dim_y):
        for k in range(dim_z):
            if mask_data[i, j, k] == 1:
                if im_data[i, j, k] == 0:
                    lesion_data[i, j, k] = 1
                if 0 < im_data[i, j, k] < 500:
                    lesion_data[i, j, k] = 2
                if im_data[i, j, k] > 11000:
                    lesion_data[i, j, k] = 3

im_lesion = set_new_data(im, lesion_data)
nib.save(im_lesion, path_lesions_mask)
