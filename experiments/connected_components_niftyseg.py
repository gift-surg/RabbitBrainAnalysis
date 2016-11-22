import os
import numpy as np
import nibabel as nib

from definitions import root_ex_vivo_template
from tools.auxiliary.utils import set_new_data


path_experiments = os.path.join(root_ex_vivo_template, 'zz_experiments')

path_subject  = os.path.join(path_experiments, '1203_3D.nii.gz')
path_ciccione = os.path.join(path_experiments, 'ciccione_1203_3D.nii.gz')

path_lesions_mask = os.path.join(path_experiments, '1203_lesions.nii.gz')

path_great_component = os.path.join(path_experiments, '1203_connected_components.nii.gz')


path_cc = os.path.join(path_experiments, 'res_c.nii.gz')
path_cc_filtered = os.path.join(path_experiments, 'res_c_fil.nii.gz')



#
#


# prendi le prime 10 componenti connesse e poi rifai le componenti connesse (con nan come background?):


