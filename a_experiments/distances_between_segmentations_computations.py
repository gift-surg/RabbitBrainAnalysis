import os
from os.path import join as jph
from labels_manager.main import LabelsManager as LM


pfo_study = '/Users/sebastiano/a_data/test_segmentaitons_comparisons'
pfo_automatic = jph(pfo_study, 'automatic')
pfo_manual = jph(pfo_study, 'manual')  # not there yet.
pfo_intermediate_files = jph(pfo_study, 'z_tmp')
pfo_output = jph(pfo_study, 'results')

modalities = ['MV_s', 'STAPLE_pr_1_s', 'STEPS_pr_1_s', 'STEPS_pr_2_s', 'STEPS_pr_3_s_smol05', 'STEPS_pr_3_s_smol10',
              'STEPS_pr_3_s', 'STEPS_pr_4_s', 'STEPS_pr_5_s']

m = LM()


for mod in modalities:
    print '\n\n\n---------------'
    print mod
    print '---------------\n'

    # take MV automatic with the manual original
    pfi_automatic_MV = jph(pfo_automatic, 'target1111_T1_segm_{}.nii.gz'.format(mod))
    pfi_manual_1 = jph(pfo_manual, '1111_approved.nii.gz')

    where_to_save = jph(pfo_output, 'distances_approved_{}.pickle'.format(mod))

    m.measure.dist(pfi_automatic_MV, pfi_manual_1, metrics=('dice_score', 'dispersion'),
                   intermediate_files_folder_name=pfo_intermediate_files, where_to_save=where_to_save)
