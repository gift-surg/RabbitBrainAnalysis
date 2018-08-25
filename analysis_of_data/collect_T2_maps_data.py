import numpy as np
import pandas as pd
from os.path import join as jph
import nibabel as nib
import os
import pickle

from nilabels.agents.measurer import LabelsMeasure
from tools.definitions import root_study_rabbits, pfo_subjects_parameters
from nilabels.tools.aux_methods.label_descriptor_manager import LabelsDescriptorManager as LdM
from tools.auxiliary.utils import set_new_data_path


''' INPUT structures '''


# subjects selection
subjects_ACS = [13103, 13108, 13301, 13401, 13403, 13404, 13405, 13501, 13505, 13507, 13602, 13606]  # 3604, 3606]
subjects_template = []  # [1201, 1203, 1305, 1404, 1505, 1507, 1510, 1702, 1805, 2002, 2502, 2503, 2608, 2702]
subjects_in_vivo = []

# multi label description
labels_per_group = {'WM'  : ['Midbrain', 'Globus Pallidus', 'Putamen', 'Thalamus'],  # In-prograss myelination
                    'GM'  : ['Frontal', 'Occipital', 'Parietal'],
                    'CSF' : ['Ventricular system', 'Periventricular area']}   # PBS for the ex - vivo rather than CSF

cdm = LdM(jph('/Users/sebastiano/Dropbox/RabbitEOP-MRI/study/A_internal_template/LabelsDescriptors',
              'labels_descriptor_v8.txt'))
ld_dict = cdm.get_multi_label_dict()

if __name__ == '__main__':

    ''' OUTPUT structures '''

    indexes = [np.array(['WM'] * len(labels_per_group['WM']) + ['GM'] * len(labels_per_group['GM']) +
               ['CSF'] * len(labels_per_group['CSF'])),
               np.array(labels_per_group['WM'] + labels_per_group['GM'] + labels_per_group['CSF'])]

    num_regions = len(labels_per_group['WM']) + len(labels_per_group['GM']) + len(labels_per_group['CSF'])

    se_T2_maps_original      = pd.Series(np.zeros(num_regions), index=indexes)
    se_T2_maps_original_bfc  = pd.Series(np.zeros(num_regions), index=indexes)
    se_T2_maps_upsampled     = pd.Series(np.zeros(num_regions), index=indexes)
    se_T2_maps_upsampled_bfc = pd.Series(np.zeros(num_regions), index=indexes)

    ''' COMPUTATIONS '''

    for sj in subjects_ACS + subjects_template:

        print('\n\nCollecting T2 values for subject {}'.format(sj))

        sj = str(sj)

        sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

        study = sj_parameters['study']
        category = sj_parameters['category']

        pfo_input_data = jph(root_study_rabbits, 'A_data', study, category)

        pfo_sj_T2 = jph(pfo_input_data, sj, 'mod', 'T2_maps')

        pfi_T2_maps_original     = jph(pfo_sj_T2, sj + '_T2map.nii.gz')
        pfi_T2_maps_original_bfc = jph(pfo_sj_T2, sj + '_T2map_bfc.nii.gz')

        pfi_T2_maps_up           = jph(pfo_sj_T2, sj + '_T2map_up.nii.gz')
        pfi_T2_maps_up_bfc        = jph(pfo_sj_T2, sj + '_T2map_bfc_up.nii.gz')

        pfi_T2_map_segm_original  = jph(pfo_input_data, sj, 'segm', sj + '_MSME_segm.nii.gz')
        pfi_T2_map_segm_up        = jph(pfo_input_data, sj, 'segm', sj + '_S0_segm.nii.gz')

        # HEADERS needs to be corrected in the whole code. Here we try at least to have consistencies between
        # segmentation and anatomical headers

        im = nib.load(pfi_T2_maps_original)
        im.set_qform(im.get_qform(), code=2)
        nib.save(im, pfi_T2_maps_original)

        pfi_tmp = jph(pfo_input_data, sj, 'segm', 'z_' + sj + '_TMP_segm.nii.gz')
        set_new_data_path(pfi_target_im=pfi_T2_maps_original, pfi_image_where_the_new_data=pfi_T2_map_segm_original,
                          pfi_result=pfi_tmp, new_dtype=np.uint8, remove_nan=True)
        os.system('mv {0} {1}'.format(pfi_tmp, pfi_T2_map_segm_original))

        set_new_data_path(pfi_target_im=pfi_T2_maps_original, pfi_image_where_the_new_data=pfi_T2_maps_original_bfc,
                          pfi_result=pfi_tmp, new_dtype=np.uint8, remove_nan=True)
        os.system('mv {0} {1}'.format(pfi_tmp, pfi_T2_maps_original_bfc))

        set_new_data_path(pfi_target_im=pfi_T2_map_segm_up, pfi_image_where_the_new_data=pfi_T2_maps_up,
                          pfi_result=pfi_tmp, new_dtype=np.uint8, remove_nan=True)
        os.system('mv {0} {1}'.format(pfi_tmp, pfi_T2_maps_up))
        set_new_data_path(pfi_target_im=pfi_T2_map_segm_up, pfi_image_where_the_new_data=pfi_T2_maps_up_bfc,
                          pfi_result=pfi_tmp, new_dtype=np.uint8, remove_nan=True)
        os.system('mv {0} {1}'.format(pfi_tmp, pfi_T2_maps_up_bfc))

        lmm = LabelsMeasure(return_mm3=True, verbose=1)
        lmm_original_bfc = LabelsMeasure(return_mm3=True, verbose=1)

        # original:
        lmm.volume(pfi_T2_map_segm_original, labels='all', tot_volume_prior=None,
                   where_to_save=jph(pfo_input_data, sj, 'records', sj + '_T2_maps_original.pkl'))
        # original bias field corrected:
        lmm.volume(pfi_T2_map_segm_original, labels='all',  tot_volume_prior=None,
                   where_to_save=jph(pfo_input_data, sj, 'records', sj + '_T2_maps_original_bfc.pkl'))
        # upsampled:
        lmm.volume(pfi_T2_map_segm_up, labels='all', tot_volume_prior=None,
                   where_to_save=jph(pfo_input_data, sj, 'records', sj + '_T2_maps_upsampled.pkl'))
        # upsampled_bfc
        lmm.volume(pfi_T2_map_segm_up, labels='all', tot_volume_prior=None,
                   where_to_save=jph(pfo_input_data, sj, 'records', sj + '_T2_maps_upsampled_bfc.pkl'))

        # above still need to be corrected...
        '''
        sa_original      = SegmentationAnalyzer(pfi_T2_map_segm_original, pfi_scalar_im=pfi_T2_maps_original)
        sa_original_bfc  = SegmentationAnalyzer(pfi_T2_map_segm_original, pfi_scalar_im=pfi_T2_maps_original_bfc)
        sa_upsampled     = SegmentationAnalyzer(pfi_T2_map_segm_up, pfi_scalar_im=pfi_T2_map_segm_up)
        sa_upsampled_bfc = SegmentationAnalyzer(pfi_T2_map_segm_up, pfi_scalar_im=pfi_T2_maps_up_bfc)

        for k in labels_per_group.keys():
            for region in labels_per_group[k]:
                region_id = ld_dict[region]
                if len(region_id) > 1:
                    region_id = [region_id]
                # original
                av = sa_original.get_average_below_labels(region_id)
                assert len(av) == 1
                se_T2_maps_original.ix[k, region] = av[0]
                # original bfc
                av = sa_original_bfc.get_average_below_labels(region_id)
                assert len(av) == 1
                se_T2_maps_original_bfc.ix[k, region] = av[0]
                # upsampled
                av = sa_upsampled.get_average_below_labels(region_id)
                assert len(av) == 1
                se_T2_maps_upsampled.ix[k, region] = av[0]
                # upsampled bfc
                av = sa_upsampled_bfc.get_average_below_labels(region_id)
                assert len(av) == 1
                se_T2_maps_upsampled_bfc.ix[k, region] = av[0]

        print '\n original'
        print se_T2_maps_original
        print '\n original bfc'
        print se_T2_maps_original_bfc
        print '\n updsampled'
        print se_T2_maps_upsampled
        print '\n upsampled bfc'
        print se_T2_maps_upsampled_bfc

        # save the structures in the report folder:
        se_T2_maps_original.     to_pickle(jph(pfo_input_data, sj, 'records', sj + '_T2_maps_original.pkl'))
        se_T2_maps_original_bfc. to_pickle(jph(pfo_input_data, sj, 'records', sj + '_T2_maps_original_bfc.pkl'))
        se_T2_maps_upsampled.    to_pickle(jph(pfo_input_data, sj, 'records', sj + '_T2_maps_upsampled.pkl'))
        se_T2_maps_upsampled_bfc.to_pickle(jph(pfo_input_data, sj, 'records', sj + '_T2_maps_upsampled_bfc.pkl'))
        '''
