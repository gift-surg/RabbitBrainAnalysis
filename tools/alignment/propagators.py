"""
Input:
    (template atlas, template label)
    (fixed)
    (parameters)
Output:
    (template atlas and label propagated on the target)

"""


import os
import numpy as np
import nibabel as nib

from tools.auxiliary.utils import print_and_run


def register_and_propagate_path(fixed_path, template_path, template_atlas_path,
                                output_template_warped_path=None,
                                output_template_atlas_warped_path=None,
                                output_transformations_folder_path=None,
                                suffix='',
                                modality='rigid',
                                interpolation_order=3,
                                extra_commands_reg='',
                                safety_on=False):
    """
        Nifty reg based registration and propagation
    -----
    Input:
        (template atlas, template label)
        (fixed)
        (parameters)
    Output:
        (template atlas and label propagated on the target)

    :param fixed_path:
    :param template_path:
    :param template_atlas_path:
    :param output_transformations_folder_path: Folder where transformations and intermediate warped are stored.
    :param output_template_warped_path:
    :param output_template_atlas_warped_path:
    :param suffix: additional suffix for the transformation.
    :param modality: 'rigid', 'affine', 'non-rigid' 'affine non-rigid' 'rigid non-rigid'
    :param interpolation_order:
    :param extra_commands_reg: extra commands, nifty-reg compatible.
    :param safety_on:
    :return:
    """

    # -- sanity check inputs: -- #

    if not os.path.isfile(fixed_path):
        raise IOError('{} file does not exist.'.format(fixed_path))
    if not os.path.isfile(template_path):
        raise IOError('{} file does not exist.'.format(template_path))
    if not os.path.isfile(template_atlas_path):
        raise IOError('{} file does not exist.'.format(template_atlas_path))
    if not os.path.isdir(output_transformations_folder_path):
        raise IOError('{} is not a folder.'.format(output_transformations_folder_path))

    available_modalities = ['rigid', 'affine', 'non-rigid', 'affine non-rigid', 'rigid non-rigid']

    if modality not in available_modalities:
        raise IOError('Modality not available. available modalities are {0}.'.format(available_modalities))

    # -- commands constructions -- #

    if modality == 'rigid':

        # register:

        final_transformation_path = os.path.join(output_transformations_folder_path,
                                                    'fixed_on_template_atlas_rig_only_trans' + suffix + '.txt')

        cmd_reg = 'reg_aladin -ref {0} -flo {1} ' \
                  '-res {2} -aff {3} -rigOnly {4}'.format(fixed_path,
                                                          template_path,
                                                          output_template_warped_path,
                                                          final_transformation_path,
                                                          extra_commands_reg)

        # propagate:

        cmd_prop = 'reg_resample -ref {0} -flo {1} ' \
                   '-res {2} -trans {3} -inter {4}'.format(fixed_path,
                                                           template_atlas_path,
                                                           output_template_atlas_warped_path,
                                                           final_transformation_path,
                                                           interpolation_order)

    elif modality == 'affine':

        # register:

        final_transformation_path = os.path.join(output_transformations_folder_path,
                                                    'fixed_on_template_atlas_aff_trans' + suffix + '.txt')

        cmd_reg = 'reg_aladin -ref {0} -flo {1} ' \
                  '-res {2} -aff {3} {4}'.format(fixed_path,
                                                 template_path,
                                                 output_template_warped_path,
                                                 final_transformation_path,
                                                 extra_commands_reg)

        # propagate:

        cmd_prop = 'reg_resample -ref {0} -flo {1} ' \
                   '-res {2} -trans {3} -inter {4}'.format(fixed_path,
                                                           template_atlas_path,
                                                           output_template_atlas_warped_path,
                                                           final_transformation_path,
                                                           interpolation_order)

    elif modality == 'non-rigid':

        # register:

        final_transformation_path = os.path.join(output_transformations_folder_path,
                                                 'fixed_on_template_atlas_non_rig_trans' + suffix + '.nii.gz')

        cmd_reg = 'reg_f3d -ref {0} -flo {1} ' \
                  '-res {2} -cpp {3} {4}'.format(fixed_path,
                                                 template_path,
                                                 output_template_warped_path,
                                                 final_transformation_path,
                                                 extra_commands_reg)

        # propagate:

        cmd_prop = 'reg_resample -ref {0} -flo {1} ' \
                   '-res {2} -trans {3} -inter {4}'.format(fixed_path,
                                                           template_atlas_path,
                                                           output_template_atlas_warped_path,
                                                           final_transformation_path,
                                                           interpolation_order)

    elif modality == 'affine non-rigid':

        # register:

        template_on_fixed_atlas_rig_path = os.path.join(output_transformations_folder_path,
                                                    'fixed_on_template_atlas_aff_warp' + suffix + '.nii.gz')
        intermediate_affine_transformation_path = os.path.join(output_transformations_folder_path,
                                                    'fixed_on_template_atlas_aff_trans' + suffix + '.txt')

        cmd_reg = 'reg_aladin -ref {0} -flo {1} ' \
                  '-res {2} -aff {3} {4}'.format(fixed_path,
                                                 template_path,
                                                 template_on_fixed_atlas_rig_path,
                                                 intermediate_affine_transformation_path,
                                                 extra_commands_reg)

        final_transformation_path = os.path.join(output_transformations_folder_path,
                                                 'fixed_on_template_atlas_non_rig_trans' + suffix + '.nii.gz')

        cmd_reg += '\nreg_f3d -ref {0} -flo {1} ' \
                   '-res {2} -cpp {3} {4}'.format(fixed_path,
                                                  template_on_fixed_atlas_rig_path,
                                                  output_template_warped_path,
                                                  final_transformation_path,
                                                  extra_commands_reg)

        # propagate:

        cmd_prop = 'reg_resample -ref {0} -flo {1} ' \
                   '-res {2} -trans {3} -inter {4}'.format(fixed_path,
                                                           template_atlas_path,
                                                           output_template_atlas_warped_path,
                                                           intermediate_affine_transformation_path,
                                                           interpolation_order)

        cmd_prop += '\nreg_resample -ref {0} -flo {1} ' \
                    '-res {2} -trans {3} -inter {4}'.format(fixed_path,
                                                            output_template_atlas_warped_path,
                                                            output_template_atlas_warped_path,
                                                            final_transformation_path,
                                                            interpolation_order)

    elif modality == 'rigid non-rigid':

        # Register:

        template_on_fixed_atlas_rig_path = os.path.join(output_transformations_folder_path,
                                                    'fixed_on_template_atlas_rig_only_warp' + suffix + '.nii.gz')
        intermediate_rigid_transformation_path = os.path.join(output_transformations_folder_path,
                                                    'fixed_on_template_atlas_rig_only_trans' + suffix + '.txt')

        cmd_reg = 'reg_aladin -ref {0} -flo {1} ' \
                  '-res {2} -aff {3} -rigOnly {4}'.format(fixed_path,
                                                          template_path,
                                                          template_on_fixed_atlas_rig_path,
                                                          intermediate_rigid_transformation_path,
                                                          extra_commands_reg)


        final_transformation_path = os.path.join(output_transformations_folder_path,
                                                 'fixed_on_template_atlas_non_rig_trans' + suffix + '.nii.gz')

        cmd_reg += '\nreg_f3d -ref {0} -flo {1} ' \
                   '-res {2} -cpp {3} {4}'.format(fixed_path,
                                                  template_on_fixed_atlas_rig_path,
                                                  output_template_atlas_warped_path,
                                                  final_transformation_path,
                                                  extra_commands_reg)

        # Propagate:

        cmd_prop = 'reg_resample -ref {0} -flo {1} ' \
                   '-res {2} -trans {3} -inter {4}'.format(fixed_path,
                                                           template_atlas_path,
                                                           output_template_atlas_warped_path,
                                                           intermediate_rigid_transformation_path,
                                                           interpolation_order)

        cmd_prop += '\nreg_resample -ref {0} -flo {1} ' \
                    '-res {2} -trans {3} -inter {4}'.format(fixed_path,
                                                            output_template_atlas_warped_path,
                                                            output_template_atlas_warped_path,
                                                            final_transformation_path,
                                                            interpolation_order)

    else:
        raise IOError

    # -- commands view -- #

    print 'Registration command \n{}'.format(cmd_reg)
    print 'Propagation command \n{}'.format(cmd_prop)

    # -- command execution -- #

    if not safety_on:
        print_and_run(cmd_reg)
        print_and_run(cmd_prop)



