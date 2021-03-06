from os.path import join as jph
import pickle
from collections import OrderedDict
import time
import os

from nilabels.tools.aux_methods.utils import print_and_run

from tools.definitions import root_study_rabbits, root_atlas, pfo_subjects_parameters, bfc_corrector_cmd, \
    num_cores_run, multi_atlas_subjects, multi_atlas_W8_subjects, root_atlas_W8
from main_pipeline.A0_main.main_controller import ListSubjectsManager

from spot.spotter import SpotDS


def spot_a_list_of_rabbits(subjects_list):

    for sj_target in subjects_list:
        print('\nAutomatic segmentation with SPOT-A-NeonatalRabbit - subject {} started.\n'.format(sj_target))

        sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj_target), 'r'))

        study = sj_parameters['study']
        category = sj_parameters['category']

        pfo_target = jph(root_study_rabbits, 'A_data', study, category, sj_target, 'stereotaxic')

        # Parameter tag z-SPOT_<TAG>
        if study == 'W8':
            parameters_tag = 'P3'
            multi_atlas_subjects_list = multi_atlas_W8_subjects
            pfo_sj_atlas = jph(root_study_rabbits, 'A_MultiAtlas_W8', sj_target)
            root_multi_atlas = root_atlas_W8
        elif study == 'ACS' or study == 'PTB' or study == 'TestStudy':
            parameters_tag = 'P2'
            multi_atlas_subjects_list = multi_atlas_subjects
            pfo_sj_atlas = jph(root_study_rabbits, 'A_MultiAtlas', sj_target)
            root_multi_atlas = root_atlas
        else:
            raise IOError('Study for subject {} not feasible.'.format(sj_target))

        # parameters_tag = 'P2'

        if sj_parameters['in_atlas']:
            # SPOT only the rabbits not already in the atlas.
            print('Subject {} already in atlas. No automatic segmentation needed'.format(sj_target))
            pfi_T1_segm_from_atlas = jph(pfo_sj_atlas, 'segm', '{}_segm.nii.gz'.format(sj_target))
            assert os.path.exists(pfi_T1_segm_from_atlas)
            cmd0 = 'mkdir -p {}'.format(jph(pfo_target, 'segm'))
            cmd1 = 'cp {} {}'.format(pfi_T1_segm_from_atlas, jph(pfo_target, 'segm', '{}_segm.nii.gz'.format(sj_target)))
            print_and_run(cmd0)
            print_and_run(cmd1)

            return

        # --- initialise the class spot:
        spot_sj = SpotDS(atlas_pfo=root_multi_atlas,
                         target_pfo=pfo_target,
                         target_name=sj_target,
                         parameters_tag=parameters_tag)
        """
        Parameters tag -> correspondence:
        'P1' -> Mono modal T1 + BFC on T1.
        'P2' -> Multi modal T1 affine only.
        """
        # Template parameters:
        spot_sj.atlas_name                    = 'MANRround3'  # Multi Atlas Newborn Rabbit
        spot_sj.atlas_list_charts_names       = multi_atlas_subjects_list
        spot_sj.atlas_list_suffix_modalities  = ['T1', 'S0', 'V1', 'MD', 'FA']
        spot_sj.atlas_list_suffix_masks       = ['roi_mask', 'roi_reg_mask', 'brain_mask']
        spot_sj.atlas_segmentation_suffix     = 'segm'

        # Architecture names - default 'automatic'.
        spot_sj.arch_automatic_segmentations_name_folder = sj_parameters['names_architecture']['final_segm_strx']

        # --- target parameters
        spot_sj.target_list_suffix_modalities = ['T1', 'S0', 'V1', 'MD', 'FA']
        spot_sj.target_name                   = sj_target

        # --- Utils
        spot_sj.bfc_corrector_cmd = bfc_corrector_cmd
        spot_sj.num_cores_run     = num_cores_run

        if sj_parameters['options_brain_mask']['method'] is None:
            use_slim_mask = False
        else:
            use_slim_mask = True

        if sj_parameters['category'] == 'ex_vivo' or sj_parameters['category'] == 'ex_vivo01' or sj_parameters['category'] == 'ex_vivo02':
            # --- Propagator option
            spot_sj.atlas_reference_chart_name = '1305'

            spot_sj.propagation_options['Affine_modalities']        = ('T1', 'FA')
            spot_sj.propagation_options['Affine_reg_masks']         = ('T1', 'S0')  # if (), there is a single mask for all modalities
            spot_sj.propagation_options['Affine_parameters']        = ' -speeeeed '
            spot_sj.propagation_options['Affine_slim_reg_mask']     = use_slim_mask
            spot_sj.propagation_options['N_rigid_modalities']       = ()  # ('T1', 'FA')  # if empty, no non-rigid step.
            spot_sj.propagation_options['N_rigid_reg_masks']        = ()  #('T1', 'S0')  # if [], same mask for all modalities
            spot_sj.propagation_options['N_rigid_slim_reg_mask']    = use_slim_mask
            spot_sj.propagation_options['N_rigid_mod_diff_bfc']     = ('T1', )  # empty list no diff bfc. - PUT A COMMA IF ONLY ONE SUBJECT!!
            spot_sj.propagation_options['N_rigid_parameters']       = ' -be 0.9 -ln 6 -lp 1  -smooR 0.07 -smooF 0.07 '
            spot_sj.propagation_options['N_rigid_same_mask_moving'] = False
            spot_sj.propagation_options['N_reg_mask_target']        = 0  # 0 roi_mask, 1 reg_mask
            spot_sj.propagation_options['N_reg_mask_moving']        = 1  # 0 roi_mask, 1 reg_mask
            spot_sj.propagation_options['Final_smoothing_factor']   = 0

        elif sj_parameters['category'] == 'in_vivo':
            # --- Propagator option
            spot_sj.atlas_reference_chart_name = '1305'

            spot_sj.propagation_options['Affine_modalities']        = ('T1',)
            spot_sj.propagation_options['Affine_reg_masks']         = ('T1',)  # if (), there is a single mask for all modalities
            spot_sj.propagation_options['Affine_parameters']        = ' -speeeeed '
            spot_sj.propagation_options['Affine_slim_reg_mask']     = use_slim_mask
            spot_sj.propagation_options['N_rigid_modalities']       = ()  # if empty, no non-rigid step. - first attempt with only an affine step.
            spot_sj.propagation_options['N_rigid_reg_masks']        = ()  # if [], same mask for all modalities
            spot_sj.propagation_options['N_rigid_slim_reg_mask']    = use_slim_mask
            spot_sj.propagation_options['N_rigid_mod_diff_bfc']     = ()  # empty list no diff bfc. - PUT A COMMA IF ONLY ONE SUBJECT!!
            spot_sj.propagation_options['N_rigid_parameters']       = ' -be 0.9 -ln 6 -lp 1  -smooR 0.07 -smooF 0.07 '
            spot_sj.propagation_options['N_rigid_same_mask_moving'] = False
            spot_sj.propagation_options['N_reg_mask_target']        = 0  # 0 roi_mask, 1 reg_mask
            spot_sj.propagation_options['N_reg_mask_moving']        = 1  # 0 roi_mask, 1 reg_mask
            spot_sj.propagation_options['Final_smoothing_factor']   = 1

        elif sj_parameters['category'] == 'first_trial' or sj_parameters['category'] == 'second_trial' or sj_parameters['category'] == 'third_trial':
            # --- Propagator option
            spot_sj.atlas_reference_chart_name = '12503'

            spot_sj.propagation_options['Affine_modalities']        = ('T1', 'FA')
            spot_sj.propagation_options['Affine_reg_masks']         = ('T1', 'S0')  # if (), there is a single mask for all modalities
            spot_sj.propagation_options['Affine_parameters']        = ' -speeeeed '
            spot_sj.propagation_options['Affine_slim_reg_mask']     = use_slim_mask
            spot_sj.propagation_options['N_rigid_modalities']       = ('T1', )  # if empty, no non-rigid step.
            spot_sj.propagation_options['N_rigid_reg_masks']        = ('T1', )  # if [], same mask for all modalities
            spot_sj.propagation_options['N_rigid_slim_reg_mask']    = use_slim_mask
            spot_sj.propagation_options['N_rigid_mod_diff_bfc']     = ( )  # empty list no diff bfc. - PUT A COMMA EVEN IF ONLY ONE SUBJECT!!
            spot_sj.propagation_options['N_rigid_parameters']       = ' -be 0.8 -vel -smooR 0.07 -smooF 0.07 '
            spot_sj.propagation_options['N_rigid_same_mask_moving'] = False
            spot_sj.propagation_options['N_reg_mask_target']        = 0  # 0 roi_mask, 1 reg_mask
            spot_sj.propagation_options['N_reg_mask_moving']        = 1  # 0 roi_mask, 1 reg_mask
            spot_sj.propagation_options['Final_smoothing_factor']   = 0

        else:
            raise IOError('Given subject category not recognised for subject {} and category {}.'.format(
                sj_target, sj_parameters['category']))

        # --- Propagator controller
        spot_sj.propagation_controller['Aff_alignment']          = True
        spot_sj.propagation_controller['Propagate_aff_to_segm']  = True
        spot_sj.propagation_controller['Propagate_aff_to_mask']  = True
        spot_sj.propagation_controller['Get_N_rigid_slim_mask']  = True
        spot_sj.propagation_controller['Get_differential_BFC']   = True
        spot_sj.propagation_controller['N_rigid_alignment']      = True
        spot_sj.propagation_controller['Propagate_n_rigid']      = True
        spot_sj.propagation_controller['Smooth_results']         = True
        spot_sj.propagation_controller['Stack_warps_and_segms']  = True

        # --- Fuser option
        spot_sj.fuser_options['Fusion_methods']  = ['MV', 'STAPLE', 'STEPS',]  # ['STAPLE', 'STEPS', ]  # 'STAPLE', 'STEPS'
        spot_sj.fuser_options['STAPLE_params']   = OrderedDict([('pr1', None)])
        spot_sj.fuser_options['STEPS_params']    = OrderedDict([('pr{0}.{1}'.format(k, n), [k, n, 4])
                                                                for n in [9] for k in [5, 11]])
        # --- Fuser controller
        spot_sj.fuser_controller['Fuse']         = True
        spot_sj.fuser_controller['Save_results'] = True

        spot_sj.spot_on_target_initialise()

        t = time.time()

        spot_sj.propagate()
        spot_sj.fuse()

        elapsed = time.time() - t

        print('Time to spot subject {} is : {}'.format(sj_target, elapsed))

if __name__ == '__main__':

    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull = False
    lsm.execute_PTB_ex_vivo  = False
    lsm.execute_PTB_in_vivo  = False
    lsm.execute_PTB_op_skull = False
    lsm.execute_ACS_ex_vivo  = False

    # lsm.input_subjects = ['Test67']

    # lsm.input_subjects = ['0802t1', ]
    # lsm.input_subjects = ['0904t1']
    # lsm.input_subjects = ['1501t1', ]
    # lsm.input_subjects = ['11806']
    # lsm.input_subjects = ['F1Test']

    # lsm.input_subjects = ['13102', '13201', '13202', '13401', '13402', '13403']
    # lsm.input_subjects = ['13201', '13202', '13401', '13402', '13403', '13403retest']

    lsm.input_subjects = ['5510', ] #'5508', '55BW', '5303']

    lsm.update_ls()

    spot_a_list_of_rabbits(lsm.ls)
