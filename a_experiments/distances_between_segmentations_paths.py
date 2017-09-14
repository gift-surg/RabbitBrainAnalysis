from os.path import join as jph

pfo_study = '/Users/sebastiano/a_data/test_segmentations_comparisons'
pfo_automatic = jph(pfo_study, 'automatic')
pfo_manual = jph(pfo_study, 'manual')  # not there yet.
pfo_intermediate_files = jph(pfo_study, 'z_tmp')
pfo_output = jph(pfo_study, 'results_new')

modalities = ['MV_s', 'STAPLE_pr_1_s', 'STEPS_pr_1_s', 'STEPS_pr_2_s', 'STEPS_pr_3_s_smol05', 'STEPS_pr_3_s_smol10',
              'STEPS_pr_3_s', 'STEPS_pr_4_s', 'STEPS_pr_5_s']

# modalities = ['STEPS_pr_3_s_smol05', 'STEPS_pr_3_s_smol10',
#               'STEPS_pr_3_s', 'STEPS_pr_4_s', 'STEPS_pr_5_s']
