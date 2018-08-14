"""

We extract a T2 map for each of the MSME T2 processed.
Images are kept whole and not trimmed by any mask, as the eye information is fundamental.

Input are 4 different MSME processing output:
> original, no corrections -> <id>_MSME.nii.gz
> original BFC             -> <id>_MSME_bfc.nii.gz
> upsampled to S0          -> <id>_MSME_up.nii.gz
> upsampled to S0 BFC      -> <id>_MSME_bfc_up.nii.gz

And the TE during the acquisition.

OUTPUT are the four corresponding estimated T2maps.


> from original, no corrections -> <id>_T2ma.nii.gz
> form original BFC             -> <id>_T2ma_bfc.nii.gz
> from upsampled to S0          -> <id>_T2ma_up.nii.gz
> from upsampled to S0 BFC      -> <id>_T2ma_bfc_up.nii.gz
"""

import os
from os.path import join as jph
import numpy as np
import nibabel as nib
import pickle

from tools.definitions import root_study_rabbits, pfo_subjects_parameters
from main_pipeline.A0_main.main_controller import ListSubjectsManager
from main_pipeline.A0_main.subject_parameters_manager import list_all_subjects

from LABelsToolkit.tools.aux_methods.utils import print_and_run
from LABelsToolkit.tools.aux_methods.utils_nib import set_new_data
from LABelsToolkit.tools.aux_methods.sanity_checks import check_path_validity
from tools.definitions import root_fit_apps


def process_T2_map_per_subject(sj, controller):

    print('\nProcessing T2 map {} started.\n'.format(sj))

    sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

    study = sj_parameters['study']
    category = sj_parameters['category']

    pfo_input_sj_MSME = jph(root_study_rabbits, '02_nifti', study, category, sj, sj + '_MSME')
    pfo_output_sj     = jph(root_study_rabbits, 'A_data', study, category, sj)
    pfo_mod           = jph(pfo_output_sj, 'mod')

    # input sanity check:
    if sj not in list_all_subjects(pfo_subjects_parameters):
        raise IOError('Subject parameters not known')
    if not os.path.exists(pfo_input_sj_MSME):
        raise IOError('Input folder MSME does not exist.')
    if not os.path.exists(pfo_output_sj):
        raise IOError('Output folder MSME does not exist.')
    if not os.path.exists(pfo_mod):
        raise IOError('Output folder MSME does not exist.')

    # --  Generate intermediate and output folder
    pfo_tmp = jph(pfo_output_sj, 'z_tmp', 'z_T2map')

    print_and_run('mkdir -p {}'.format(pfo_tmp))

    suffix = ['', 'inS0']

    if controller['get_acquisition_echo_time']:
        pfi_visu_pars = jph(pfo_input_sj_MSME, sj + '_MSME_visu_pars.npy')
        assert check_path_validity(pfi_visu_pars)
        pfi_echo_times = jph(pfo_tmp, sj + '_echo_times.txt')
        visu_pars_dict = np.load(pfi_visu_pars)
        np.savetxt(fname=pfi_echo_times, X=visu_pars_dict.item().get('VisuAcqEchoTime'), fmt='%10.2f', newline=' ')

    if controller['process_each_MSME_input']:
        pfi_echo_times = jph(pfo_tmp, '{}_echo_times.txt'.format(sj))
        assert os.path.exists(pfi_echo_times)
        TE = np.loadtxt(pfi_echo_times)
        echo_delta = TE[2] - TE[1]
        # original
        for s in suffix:
            pfi_original_MSME = jph(pfo_mod, '{}_MSME{}.nii.gz'.format(sj, s))
            check_path_validity(pfi_original_MSME)
            pfi_T2map = jph(pfo_tmp, '{}_T2map{}.nii.gz'.format(sj, s))
            cmd1 = root_fit_apps + 'fit_qt2 -source {0} -TE {1} -t2map {2}'.format(pfi_original_MSME,
                                                                                   echo_delta, pfi_T2map)
            print cmd1
            print_and_run(cmd1)

    if controller['correct_origin']:  # some versions of niftyfit for fit_qt2 are dividing by 0 in the origin.
        for s in suffix:
            pfi_T2map = jph(pfo_tmp, sj + '_T2map{}.nii.gz'.format(s))
            check_path_validity(pfi_T2map)
            pfi_T2map_corrected = jph(pfo_tmp, sj + '_corrected_T2map{}.nii.gz'.format(s))
            # clean upper outliers (Mean + 2 * StandardDeviation) ... They are more than outliers!
            im_s = nib.load(pfi_T2map)
            places_not_outliers = im_s.get_data() < 1000  # np.mean(im_s.get_data()) + 2 * np.std(im_s.get_data())
            im_s.get_data()[:] = places_not_outliers * im_s.get_data()
            im_corrected = set_new_data(im_s, places_not_outliers * im_s.get_data())
            nib.save(im_corrected, pfi_T2map_corrected)

    if controller['save_results']:
        # Save the bias field corrected '', and '_up' in the name _T2map and _T2map_up
        for s in suffix:
            pfi_source    = jph(pfo_tmp, sj + '_corrected_T2map{}.nii.gz'.format(s))
            pfi_destination    = jph(pfo_mod, sj + '_T2map.nii.gz')
            cmd = 'cp {0} {1}'.format(pfi_source, pfi_destination)
            print_and_run(cmd)


def process_t2_maps_from_list(subj_list, controller):

    print '\n\n Processing t2 subjects from list {0} \n'.format(subj_list)

    for sj in subj_list:
        process_T2_map_per_subject(sj, controller)


if __name__ == '__main__':

    print('process T2Maps, local run. ')

    controller_steps = {'get_acquisition_echo_time'  : True,
                        'process_each_MSME_input'    : True,
                        'correct_origin'             : True,
                        'save_results'               : True}

    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull = False
    lsm.execute_PTB_ex_vivo = False
    lsm.execute_PTB_in_vivo = False
    lsm.execute_PTB_op_skull = False
    lsm.execute_ACS_ex_vivo = False

    lsm.input_subjects = ['12610', ]

    lsm.update_ls()

    process_t2_maps_from_list(lsm.ls, controller_steps)
