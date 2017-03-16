import os
from os.path import join as jph
import numpy as np

from tools.label_management.caliber import SegmentationAnalyzer
from definitions import root_pilot_study
from tabulate import tabulate

from pipelines_pilot.A_template_atlas_in_vivo_prelim.a_definitions_regions_subjects import regions, regions_lr, subjects, regions_values


pfo_study = jph(root_pilot_study, 'A_template_atlas_in_vivo')

pfi_label_descriptor_prelim_templ = jph(pfo_study, 'Utils',
    'preliminary_template', 'label_descriptor_preliminary_template.txt')

segmentation_tag = '_smol_t3_reg_mask'

regions = [j[0] for j in regions_values]

# prepare output:
num_regions = len(regions)
num_subjects = len(subjects)

fa_per_regions_per_subject = np.zeros([num_regions, num_subjects], dtype=np.float64)

for num_sj, sj in enumerate(subjects):
    name_prelim_mask = 'prelim_' + sj + '_template' + segmentation_tag + '.nii.gz'
    pfi_mask = jph(pfo_study, sj, 'segmentations', 'automatic', name_prelim_mask)
    name_fa = sj + '_FA.nii.gz'
    pfi_fa = jph(pfo_study, sj, 'all_modalities', name_fa)

    if not os.path.isfile(pfi_mask):
        print('File {} not found.'.format(pfi_mask))
    elif not os.path.isfile(pfi_fa):
        print('File {} not found.'.format(pfi_fa))
    else:
        print('\nRegional mean FA extraction for subject : ' + sj + '\n')

        sa = SegmentationAnalyzer(pfi_mask,
                                  pfi_description=pfi_label_descriptor_prelim_templ,
                                  pfi_scalar_im=pfi_fa,
                                  return_mm3=False)  # mm3 or voxels

        for num_v, v in enumerate(regions_values):
            av_fa = sa.get_average_below_labels(selected_labels=v[1])
            print('region {0}, labels {1}, average fa {2} '.format(v[0], v[1], av_fa))
            fa_per_regions_per_subject[num_v, num_sj] = av_fa

pfi_data = jph(pfo_study, 'Preliminary', 'outcomes', 'fa_per_regions_per_subject.txt')
np.savetxt(pfi_data, fa_per_regions_per_subject)

data_as_list = [list(l) for l in list(fa_per_regions_per_subject)]

for num_reg, reg in enumerate(regions):
    data_as_list[num_reg] = [reg] + data_as_list[num_reg]

table = tabulate(data_as_list, headers=['region \ average fa', ] + subjects)
print table

pfi_table = jph(pfo_study, 'Preliminary', 'outcomes', 'fa_per_regions_per_subject_tab.txt')
f = open(pfi_table, 'w').write(table)
