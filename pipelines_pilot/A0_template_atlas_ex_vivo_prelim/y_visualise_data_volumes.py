import os
import copy
import numpy as np
from os.path import join as jph
from tabulate import tabulate
import matplotlib.pyplot as plt
from definitions import root_pilot_study

from pipelines_pilot.A_template_atlas_ex_vivo_prelim.a_definitions_regions_subjects import regions, regions_lr, subjects


pfo_study = jph(root_pilot_study, 'A_template_atlas_ex_vivo')
pfi_data = jph(pfo_study, 'Preliminary', 'outcomes', 'vol_over_tot_per_subject_no15.txt')
pfi_tab = jph(pfo_study, 'Preliminary', 'outcomes', 'vol_over_tot_per_subject_no15.txt')

dat = np.loadtxt(pfi_data)


num_regions, num_subjects = dat.shape

print len(regions)
print num_regions -2


plt.close('all')

## Print data all regions:

fig = plt.figure(1, figsize=(12, 8), dpi=100)
ax = fig.add_subplot(111)
ax.set_position([0.1, 0.18, 0.85, 0.75])

for j in xrange(num_subjects):
    if subjects[j] in ['1702', '1805']:
        ax.scatter(range(len(regions)), dat[1:-1, j], marker='.', label='subj ' + subjects[j]) #ls='dashed'
    else:
        ax.scatter(range(len(regions)), dat[1:-1, j], marker='x', label='subj ' + subjects[j]) #ls='dotted'

ax.grid(which='both', alpha=0.2)
ax.set_title('Volumes per region visualised for each subject')
ax.set_xbound(-1,20)
ax.set_xticks(range(len(regions)))
ax.set_xticklabels(regions, rotation=45, ha='right')
ax.set_xlabel('Regions')
ax.set_ylabel('volumes (mm3)')
ax.legend()
plt.show(block=False)


### sum regions left/right:

dat_left_right = np.zeros([len(regions_lr),len(subjects)], dtype=np.float64)

for i in range(1,10):
    dat_left_right[i-1, :] = dat[2*i - 1, :] + dat[2*i, :]
dat_left_right[9, :] = dat[-2, :]


## Print data averages:

male_term       = ['1702', ]
female_term     = ['1805', ]
male_pre_term   = ['1201', '1203', '1505', '1507', '1510', '2002']
female_pre_term = ['1305', '1404']

fig = plt.figure(2, figsize=(12, 8), dpi=100)
ax = fig.add_subplot(111)
ax.set_position([0.1, 0.18, 0.85, 0.75])

for j in xrange(num_subjects):
    if subjects[j] in male_term:
        ax.scatter(range(len(regions_lr)), dat_left_right[:, j], marker='^', label='subj ' + subjects[j]) #ls='dashed'
    elif subjects[j] in female_term:
        ax.scatter(range(len(regions_lr)), dat_left_right[:, j], marker='v', label='subj ' + subjects[j]) #ls='dashed'
    elif subjects[j] in male_pre_term:
        ax.scatter(range(len(regions_lr)), dat_left_right[:, j], marker='x', label='subj ' + subjects[j]) #ls='dashed'
    elif subjects[j] in female_pre_term:
        ax.scatter(range(len(regions_lr)), dat_left_right[:, j], marker='d', label='subj ' + subjects[j]) #ls='dotted'

ax.grid(which='both', alpha=0.2)
ax.set_title('Volumes per region (left right averaged) visualised for each subject')
ax.set_xbound(-1,10)
ax.set_xticks(range(len(regions_lr)))
ax.set_xticklabels(regions_lr, rotation=45, ha='right')
ax.set_xlabel('Regions')
ax.set_ylabel('volumes (mm3)')
ax.legend()
plt.show(block=False)
