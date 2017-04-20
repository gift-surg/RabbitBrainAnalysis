import numpy as np
import nibabel as nib
from os.path import join as jph
import os

from tools.auxiliary.utils import set_new_data


subjects = []
pfo_study = 'zzz'

for sj in subjects:

    # paths:
    pfo_subject = jph(pfo_study, str(sj))
    pfi_T1 = jph(pfo_subject, '3D', str(sj) + '_3D.nii.gz')
    pfi_DWI = jph(pfo_subject, 'DWI', str(sj) + '_DWI.nii.gz')

    pfi_working_folder = jph(pfo_subject, 'z_desqueeze')

    # create working folder:
    os.system('mkdir -p {}'.format(pfi_working_folder))

    #


