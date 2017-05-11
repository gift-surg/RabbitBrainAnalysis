"""
Analysis are preformed in bicommissural orientation, but for a better registration of the
latest segmentation, 
"""
import numpy as np
import os
from os.path import join as jph

from definitions import root_pilot_study_dropbox
from tools.auxiliary.utils import print_and_run

"""
After importing the data in proper structure and having them with header properly oriented,
still need to squeeze, to orient according to MNI and to clean q-form and s-form.
"""

# controller
control = {'safety on'                        : False,
           'oversample'                       : True,
           'extract first slice standard'     : True,
           'extract first slice oversampled'  : True,
           'threshold zero'                    : True}


# main paths
root_pilot_study_msme_in_vivo = jph(root_pilot_study_dropbox, 'A_msme_t2_analysis', 'ex_vivo')
pfo_utils = jph(root_pilot_study_dropbox, 'A_msme_t2_analysis', 'ex_vivo', 'Utils')
for p in [root_pilot_study_msme_in_vivo, pfo_utils]:
    if not os.path.exists(p):
        raise IOError('Path {} not defined'.format(p))

# subjects
list_subjects = np.sort(list(set(os.listdir(root_pilot_study_msme_in_vivo)) - {'.DS_Store', 'Utils'}))
print(list_subjects)

# list_subjects = ['2503']

for sj in list_subjects:

    # input
    pfi_sj_standard = jph(root_pilot_study_msme_in_vivo, sj, 'mod', sj + '_MSME.nii.gz')

    if not os.path.exists(pfi_sj_standard):
        raise IOError('Path {} not defined'.format(pfi_sj_standard))

    # utils
    if sj == '2502':
        pfi_resampling_grid = jph(pfo_utils, 'resampling_grid_2502.nii.gz')
    else:
        pfi_resampling_grid = jph(pfo_utils, 'resampling_grid.nii.gz')
    pfi_affine_identity = jph(pfo_utils, 'aff_id.txt')

    for p in [pfi_resampling_grid, pfi_affine_identity]:
        if not os.path.exists(p):
            raise IOError('Path {} not defined'.format(p))

    # output
    pfi_sj_oversampled = jph(root_pilot_study_msme_in_vivo, sj, 'mod', sj + '_MSME_ups.nii.gz')
    pfi_sj_first_layer_standard = jph(root_pilot_study_msme_in_vivo, sj, 'mod', sj + '_MSME_layer1.nii.gz')
    pfi_sj_first_layer_oversampled = jph(root_pilot_study_msme_in_vivo, sj, 'mod', sj + '_MSME_ups_layer1.nii.gz')

    if control['oversample']:
        cmd = 'reg_resample -ref {0} -flo {1} -trans {2} -res {3}'.format(pfi_resampling_grid,
                                                                          pfi_sj_standard,
                                                                          pfi_affine_identity,
                                                                          pfi_sj_oversampled)

        print_and_run(cmd, safety_on=control['safety on'])

    if control['extract first slice standard']:

        cmd = 'seg_maths {0} -tp 0 {1}'.format(pfi_sj_standard, pfi_sj_first_layer_standard)
        print_and_run(cmd, safety_on=control['safety on'])

    if control['extract first slice oversampled']:

        cmd = 'seg_maths {0} -tp 0 {1}'.format(pfi_sj_oversampled, pfi_sj_first_layer_oversampled)
        print_and_run(cmd, safety_on=control['safety on'])

    if control['threshold zero']:

        for p in [pfi_sj_oversampled, pfi_sj_first_layer_oversampled]:
            if not os.path.exists(p):
                raise IOError('Path {} not defined'.format(p))

        cmd0 = 'seg_maths {0} -thr 0 {0}'.format(pfi_sj_oversampled)
        print_and_run(cmd0, safety_on=control['safety on'])
        cmd1 = 'seg_maths {0} -thr 0 {0}'.format(pfi_sj_first_layer_oversampled)
        print_and_run(cmd1, safety_on=control['safety on'])
