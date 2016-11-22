import os
import time

from tools.auxiliary.lesion_mask_extractor import simple_lesion_mask_extractor_path
from definitions import root_ex_vivo_template


###############
# controller: #
###############

step_create_image_alias              = True
step_create_registration_masks_alias = True
step_run_iterative_registration      = True

safety_on = False

###############
# parameters: #
###############

list_subjects = ['1201', '1203', '1305', '1404', '1507', '1510', '2002']

##########
# Paths: #
##########

root_iterative_registration = os.path.join(root_ex_vivo_template, 'co_registration')
reg_images_folder_path = os.path.join(root_iterative_registration, 'input_images')
reg_masks_folder_path = os.path.join(root_iterative_registration, 'input_masks')
reg_results_folder_path = os.path.join(root_iterative_registration, 'results')

###############
# Pipeline: #
###############


# create images alias for registration to the right folder
if step_create_image_alias:
    for sj in list_subjects:

        source = os.path.join(root_ex_vivo_template, sj, '3D', sj + '_3D_thr300_masked_bfc_default_.nii.gz')
        target = os.path.join(reg_images_folder_path, sj + '.nii.gz')

        print "Create alias image for subject {} \n".format(sj)
        cmd = '''ln {0} {1} '''.format(source, target)
        print cmd

        if not safety_on:
            os.system(cmd)


# create lesion masks alias
if step_create_registration_masks_alias:

    for sj in list_subjects:
        source = os.path.join(root_ex_vivo_template, sj, 'masks', sj + '_registration_mask.nii.gz')
        target = os.path.join(reg_masks_folder_path, sj + '_reg_mask.nii.gz')

        print "Create registration mask alias for subject {} \n".format(sj)
        cmd = '''ln {0} {1} '''.format(source, target)
        print cmd

        if not safety_on:
            os.system(cmd)

# run iterative registration
if step_run_iterative_registration:

    print "\n Run groupwise registration \n"

    cmd = 'cd {0}; ' \
          './local_groupwise_niftyreg_run.sh local_groupwise_niftyreg_params.sh'.format(root_iterative_registration)

    print cmd

    if not safety_on:
        start = time.clock()
        os.system(cmd)
        res_time = (time.clock() - start)

        print "Iterative registration finished in {} seconds".format(res_time)