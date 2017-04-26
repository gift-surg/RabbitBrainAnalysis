import os
import nibabel as nib
from os.path import join as jph

from tools.auxiliary.utils import set_new_data


def take_first_slice(pfi_in, pfi_out):
    nib_dwi = nib.load(pfi_in)
    nib_dwi_first_slice_data = nib_dwi.get_data()[..., 0]
    nib_first_slice_dwi = set_new_data(nib_dwi, nib_dwi_first_slice_data)
    nib.save(nib_first_slice_dwi, pfi_out)

root_subjects = '/Users/sebastiano/Dropbox/RabbitEncephalopathyofPrematurity-MRI/pilot_study/0_original_data/ex_vivo/prelim_conversions/'
subjects = ['2502', '2503', '2608', '2702']
fname = ['HVDM_2502_6March2017_3', '2503_DWI', 'HVDM_2608_7March2017_4', 'HVDM_2702_9March2017_4']
ids = ['0', '1']
safety = False

for sj, sj_name in zip(subjects, fname):

    if sj in ['2502', '2608', '2702']:
        for id in ids:

            pfi_dwi = jph(root_subjects, sj, 'DWI', sj_name + id + '.nii.gz')
            pfi_b0 = jph(root_subjects, sj, 'DWI', sj_name + id + '_b0.nii.gz')

            print pfi_dwi
            print pfi_b0

            if not safety:
                os.system('seg_maths {0} -tp 0 {1}'.format(pfi_dwi, pfi_b0))
                # take_first_slice(pfi_dwi, pfi_b0)

    else:
        pfi_dwi = jph(root_subjects, sj, 'DWI', sj_name + '.nii.gz')
        pfi_b0 = jph(root_subjects, sj, 'DWI', sj_name + '_b0.nii.gz')

        print pfi_dwi
        print pfi_b0

        assert os.path.exists(pfi_dwi) == True

        if not safety:
            os.system('seg_maths {0} -tp 0 {1}'.format(pfi_dwi, pfi_b0))
            # take_first_slice(pfi_dwi, pfi_b0)
