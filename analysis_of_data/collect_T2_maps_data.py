import numpy as np
import pandas as pd
from os.path import join as jph

from tools.definitions import root_study_rabbits, root_utils
from labels_manager.caliber.segmentation_analyzer import SegmentationAnalyzer
from pipeline_project.A0_main.main_controller import subject
from tools.auxiliary.parse_excel_tables_and_descriptors import parse_multi_label_descriptor_in_a_dict


''' INPUT structures '''

# subjects selection
subjects_ACS = [3103]  #, 3108, 3301, 3307, 3401, 3403, 3404, 3405, 3501, 3505, 3507, 3602, 3604, 3606]
subjects_template = []  #[1201, 1203, 1305, 1404, 1505, 1507, 1510, 1702, 1805, 2002, 2502, 2503, 2608, 2702]
subjects_in_vivo = []

# multi label description
labels = {'WM'  : ['Midbrain', 'Globus Pallidus', 'Putamen', 'Thalamus'],  # In-prograss myelination
          'GM'  : ['Frontal', 'Occipital', 'Parietal'],
          'CSF' : ['Ventricular system', 'Periventricular area']}   # PBS for the ex - vivo rather than CSF

ld_dict = parse_multi_label_descriptor_in_a_dict(jph(root_utils, 'multi_label_descriptor.txt'))


if __name__ == '__main__':

    ''' OUTPUT structures '''

    indexes = [np.array(['WM'] * len(labels['WM']) + ['GM'] * len(labels['GM']) + ['CSF'] * len(labels['CSF'])),
               np.array(labels['WM'] + labels['GM'] + labels['CSF'])]

    num_regions = len(labels['WM']) + len(labels['GM']) + len(labels['CSF'])

    se_T2_maps_original      = pd.Series(np.zeros(num_regions), index=indexes)
    se_T2_maps_original_bfc  = pd.Series(np.zeros(num_regions), index=indexes)
    se_T2_maps_upsampled     = pd.Series(np.zeros(num_regions), index=indexes)
    se_T2_maps_upsampled_bfc = pd.Series(np.zeros(num_regions), index=indexes)

    se = pd.Series(np.zeros(num_regions), index=indexes)

    ''' COMPUTATIONS '''

    for sj in subjects_ACS + subjects_template:

        print('Collecting T2 values for subject {}'.format(sj))

        sj = str(sj)

        group = subject[sj][0][0]
        category = subject[sj][0][1]
        pfo_input_data = jph(root_study_rabbits, 'A_data', group, category)

        pfo_sj_T2 = jph(pfo_input_data, sj, 'mod', 'T2_maps')

        pfi_T2_maps_original     = jph(pfo_sj_T2, sj + '_T2map.nii.gz')
        pfi_T2_maps_original_bfc = jph(pfo_sj_T2, sj + '_T2map_bfc.nii.gz')

        pfi_T2_maps_upsampled     = jph(pfo_sj_T2, sj + '_T2map_up.nii.gz')
        pfi_T2_maps_upsampled_bfc = jph(pfo_sj_T2, sj + '_T2map_bfc_up.nii.gz')

        pfi_T2_map_segm_original  = jph(pfo_input_data, sj, 'segm', sj + '_MSME_segm.nii.gz')
        pfi_T2_map_segm_upsampled = jph(pfo_input_data, sj, 'segm', sj + '_S0_segm.nii.gz')

        sa_original      = SegmentationAnalyzer(pfi_T2_map_segm_original, pfi_scalar_im=pfi_T2_maps_original)
        sa_original_bfc  = SegmentationAnalyzer(pfi_T2_map_segm_original, pfi_scalar_im=pfi_T2_maps_original_bfc)
        sa_upsampled     = SegmentationAnalyzer(pfi_T2_map_segm_upsampled, pfi_scalar_im=pfi_T2_maps_upsampled)
        sa_upsampled_bfc = SegmentationAnalyzer(pfi_T2_map_segm_upsampled, pfi_scalar_im=pfi_T2_maps_upsampled_bfc)

        for k in labels.keys():
            for region in labels[k]:
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

        print se_T2_maps_original
        print se_T2_maps_original_bfc
        print se_T2_maps_upsampled
        print se_T2_maps_upsampled_bfc
        # save the structures in the report folder:
        se_T2_maps_original.     to_pickle(jph(pfo_input_data, sj, 'records', sj + '_T2_maps_original.pkl'))
        se_T2_maps_original_bfc. to_pickle(jph(pfo_input_data, sj, 'records', sj + '_T2_maps_original_bfc.pkl'))
        se_T2_maps_upsampled.    to_pickle(jph(pfo_input_data, sj, 'records', sj + '_T2_maps_upsampled.pkl'))
        se_T2_maps_upsampled_bfc.to_pickle(jph(pfo_input_data, sj, 'records', sj + '_T2_maps_upsampled_bfc.pkl'))
