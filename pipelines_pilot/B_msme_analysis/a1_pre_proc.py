"""
High anisotropicity of the MSME_T2 makes it not useful when oriented in
histological coordinates.
Analysis are preformed in bicommissural orientation
"""
import numpy as np
import os
from os.path import join as jph

from definitions import root_pilot_study_dropbox
from tools.auxiliary.squeezer import squeeze_image_from_path, sform_qform_cleaner

"""
After importing the data in proper structure and having them with header properly oriented,
still need to squeeze, to orient according to MNI and to clean q-form and s-form.
"""


root_pilot_study_msme_in_vivo = jph(root_pilot_study_dropbox, 'A_msme_t2_analysis', 'ex_vivo')

list_subjects = np.sort(list(set(os.listdir(root_pilot_study_msme_in_vivo)) - {'.DS_Store'}))

control = {'squeeze'       : False,
           'fsl reorient'  : False,
           'set 0 transl'  : False,
           'store and delete intemediate' : True}

print(list_subjects)

for sj in list_subjects:

    pfi_initial = jph(root_pilot_study_msme_in_vivo, sj, 'mod', sj + '_MSME.nii.gz')
    pfi_oriented = jph(root_pilot_study_msme_in_vivo, sj, 'mod', sj + '_MSME_sq_and_or.nii.gz')
    pfi_zero_translation = jph(root_pilot_study_msme_in_vivo, sj, 'mod', sj + '_MSME_zero_t.nii.gz')

    print('\n\n Subject {} \n\n'.format(sj))

    if control['squeeze']:
        squeeze_image_from_path(pfi_initial, pfi_initial)

    if control['fsl reorient']:
        os.system('fslreorient2std {0} {1} '.format(pfi_initial, pfi_initial))

    if control['set 0 transl']:
        sform_qform_cleaner(pfi_initial, pfi_zero_translation)

    if control['store and delete intemediate']:
        os.system('cp {0} {1}'.format(pfi_zero_translation, pfi_initial))
        os.system('rm {0}'.format(pfi_zero_translation))
