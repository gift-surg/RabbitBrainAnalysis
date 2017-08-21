"""
Very short pipeline to create the template from the ex-skull subjects images.
Subjects must be separated from the background, manually aligned in histological orientation and BF-corrected before
running this code.
Selected subjects to build the template must then be stored in the folder
input_images.

Masks are created here automatically in the appropriate folder, and the
results are stored in the pfo_results folder.
"""

import os
from os.path import join as jph
from tools.definitions import root_pilot_study
from tools.auxiliary.utils import print_and_run


' commands manager '

safety_on = True

step_create_masks = True
step_generate_template = True

' path manager '

study_path = jph(root_pilot_study, 'A_template_atlas_ex_skull')

pfo_images  = jph(study_path, 'input_images')
pfo_masks   = jph(study_path, 'input_masks')
pfo_results = jph(study_path, 'input_results')


' PIPELINE: '

if step_create_masks:

    print_and_run('mkdir -p {}'.format(pfo_masks))

    for (dirpath, dirnames, filenames) in os.walk(pfo_images):
            for filename in filenames:
                if filename.endswith('.nii.gz') or filename.endswith('.nii'):

                    pfi_input = jph(pfo_images, filename)
                    name_new = filename.split('.')[0] + '_mask.nii.gz'
                    pfi_output = jph(pfo_masks, name_new)

                    cmd = 'seg_maths {0} -bin {1} '.format(pfi_input, pfi_output)

                    print cmd + '\n'

                    if not safety_on:
                        print_and_run(cmd)

if step_generate_template:

    print_and_run('mkdir -p {}'.format(pfo_results))

    here = os.getcwd()
    cmd1 = 'cd {0} ; {1}  {2}'.format(study_path,
                                     './local_groupwise_niftyreg_run.sh',
                                     'local_groupwise_niftyreg_params.sh')

    cmd2 = 'cd {}'.format(here)

    print cmd1
    print cmd2

    if not safety_on:
        print_and_run(cmd1)
        print_and_run(cmd2)
