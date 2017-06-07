import os
from os.path import join as jph

import numpy as np
from tabulate import tabulate

from definitions import root_pilot_study
from pipelines_internal_template.A_template_atlas_ex_vivo_prelim.a_definitions_regions_subjects import subjects, regions_values
from tools.measurements.compile_record import SegmentationAnalyzer

pfo_study = jph(root_pilot_study, 'A_template_atlas_ex_vivo')

pfi_label_descriptor_prelim_templ = jph(pfo_study, 'Preliminary',
    'template_atlas_subregions', 'label_descriptor_preliminary_template.txt')

segmentation_tag = '_smol_t3'
regions = [j[0] for j in regions_values]

# prepare output:
num_regions = len(regions)
num_subjects = len(subjects)

adc_per_regions_per_subject = np.zeros([num_regions, num_subjects], dtype=np.float64)

for num_sj, sj in enumerate(subjects):
    name_prelim_mask = 'prelim_' + sj + '_template' + segmentation_tag + '.nii.gz'
    pfi_mask = jph(pfo_study, sj, 'segmentations', 'automatic', name_prelim_mask)
    name_adc = sj + '_MD.nii.gz'
    pfi_adc = jph(pfo_study, sj, 'all_modalities', name_adc)

    if not os.path.isfile(pfi_mask):
        print('File {} not found.'.format(pfi_mask))
    elif not os.path.isfile(pfi_adc):
        print('File {} not found.'.format(pfi_adc))
    else:
        print('\nRegional mean ADC extraction for subject : ' + sj + '\n')

        sa = SegmentationAnalyzer(pfi_mask,
                                  pfi_description=pfi_label_descriptor_prelim_templ,
                                  pfi_scalar_im=pfi_adc,
                                  return_mm3=True)  # mm3 or voxels

        for num_v, v in enumerate(regions_values):
            av_adc = sa.get_average_below_labels(selected_labels=v[1])
            print('region {0}, labels {1}, average ADC {2} '.format(v[0], v[1], av_adc))
            adc_per_regions_per_subject[num_v, num_sj] = av_adc

pfi_data = jph(pfo_study, 'Preliminary', 'outcomes', 'adc_per_regions_per_subject_no15.txt')
np.savetxt(pfi_data, adc_per_regions_per_subject)

data_as_list = [list(l) for l in list(adc_per_regions_per_subject)]

for num_reg, reg in enumerate(regions):
    data_as_list[num_reg] = [reg] + data_as_list[num_reg]

table = tabulate(data_as_list, headers=['region \ average adc', ] + subjects)
print table

pfi_table = jph(pfo_study, 'Preliminary', 'outcomes', 'adc_per_regions_per_subject_tab_no15.txt')
f = open(pfi_table, 'w').write(table)
