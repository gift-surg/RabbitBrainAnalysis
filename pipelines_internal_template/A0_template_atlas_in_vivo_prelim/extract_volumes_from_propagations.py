import os
from os.path import join as jph

import numpy as np
from tabulate import tabulate

from tools.definitions import root_pilot_study
from pipelines_internal_template.A_template_atlas_in_vivo_prelim.a_definitions_regions_subjects import regions, subjects
from tools.measurements.compile_record import SegmentationAnalyzer

pfo_study = jph(root_pilot_study, 'A_template_atlas_in_vivo')

pfi_label_descriptor_prelim_templ = jph(pfo_study, 'Utils',
    'preliminary_template', 'label_descriptor_preliminary_template.txt')

segmentation_tag = '_smol_t3_reg_mask'  # _smol_t1

num_subjects = len(subjects)
num_regions = 21
vol_over_tot_per_subject = np.zeros([num_regions, num_subjects], dtype=np.float64)
tot_vol_per_subject = np.zeros([num_subjects], dtype=np.float64)

for num_sj, sj in enumerate(subjects):
    name_prelim_template = 'prelim_' + sj + '_template' + segmentation_tag + '.nii.gz'
    pfi_template = jph(pfo_study, sj, 'segmentations', 'automatic', name_prelim_template)

    if not os.path.isfile(pfi_template):
        raise IOError('File {} not found.'.format(pfi_template))
    else:
        print '\nData for subject : ' + sj + '\n'

        sa = SegmentationAnalyzer(pfi_template, pfi_description=pfi_label_descriptor_prelim_templ)
        sa.return_mm3 = True
        regions, vol, vol_over_tot, vol_over_icv = sa.get_volumes_per_zone()
        vol_over_tot_per_subject[:, num_sj] = np.asarray(vol_over_tot)
        tot_vol_per_subject[num_sj] = sa.get_total_volume()
    print

save_external = False

# print and save folders:
pfi_data = jph(pfo_study, 'Preliminary', 'outcomes', 'vol_over_tot_per_subject.txt')

if save_external:
    np.savetxt(pfi_data, vol_over_tot_per_subject)

data_as_list = [list(l) for l in list(vol_over_tot_per_subject)]

for num_reg, reg in enumerate(regions):
    data_as_list[num_reg] = [reg] + data_as_list[num_reg]

table = tabulate(data_as_list, headers=['region \ vol/tot', ] + subjects)
print table

if save_external:
    pfi_table = jph(pfo_study, 'Preliminary', 'outcomes', 'vol_over_tot_per_subject_tab.txt')
    f = open(pfi_table, 'w').write(table)

# final sanity check:
for j in xrange(num_subjects):
    np.testing.assert_almost_equal(np.sum(vol_over_tot_per_subject[1:, j]), 1.0)

# print and save volumes only

save_external = True

list_tot_vol_per_subject = [[sj, vol] for sj, vol in zip(subjects, list(tot_vol_per_subject))]

table_tot_vol = tabulate(list_tot_vol_per_subject, headers=['subject', 'tot vol (mm3)', ] + subjects)
print '\n\n'
print table_tot_vol

if save_external:
    pfi_table_tot_vol = jph(pfo_study, 'Preliminary', 'outcomes', 'total_volume_mm3_tab.txt')
    g = open(pfi_table_tot_vol, 'w').write(table_tot_vol)
