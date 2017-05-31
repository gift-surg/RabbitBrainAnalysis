import os
import numpy as np
from os.path import join as jph

from definitions import root_study_rabbits
from tools.auxiliary.utils import print_and_run
from pipeline_project.A0_main.main_controller import subject, RunParameters


def transpose_matrix_in_txt(pfi_input, pfi_output):
    m = np.loadtxt(pfi_input)
    np.savetxt(fname=pfi_output, X=m.T)


def process_g_ratio_per_subject(sj, pfo_input_sj_DWI, pfo_input_sj_MSME, pfo_output_sj, controller):

    print('\nProcessing MSME {} started.\n'.format(sj))

    # input sanity check:

    if sj not in subject.keys():
        raise IOError('Subject parameters not known')
    if not os.path.exists(pfo_input_sj_DWI):
        raise IOError('Input folder DWI does not exist.')
    if not os.path.exists(pfo_input_sj_MSME):
        raise IOError('Input folder MSME does not exist.')

    # --  Generate intermediate and output folder

    pfo_mod = jph(pfo_output_sj, 'mod')
    pfo_segm = jph(pfo_output_sj, 'segm')
    pfo_mask = jph(pfo_output_sj, 'z_mask')
    pfo_tmp = jph(pfo_output_sj, 'z_tmp', 'z_g_ratio')

    os.system('mkdir -p {}'.format(pfo_output_sj))
    os.system('mkdir -p {}'.format(pfo_mod))
    os.system('mkdir -p {}'.format(pfo_segm))
    os.system('mkdir -p {}'.format(pfo_mask))
    os.system('mkdir -p {}'.format(pfo_tmp))

    # --

    if controller['transpose b-vals b-vects']:
        pfi_bvals = jph(pfo_input_sj_DWI, sj + '_DWI_DwEffBval.txt')
        pfi_bvects = jph(pfo_input_sj_DWI, sj + '_DWI_DwGradVec.txt')
        assert os.path.exists(pfi_bvals)
        assert os.path.exists(pfi_bvects)
        pfi_transposed_bvals = jph(pfo_tmp, sj + '_DWI_DwEffBval_T.txt')
        pfi_transposed_vects = jph(pfo_tmp, sj + '_DWI_DwGradVec_T.txt')
        m = np.loadtxt(pfi_bvals)
        np.savetxt(fname=pfi_transposed_bvals, X=m.T, delimiter=' ', newline=' ', fmt='%10.8f')
        m = np.loadtxt(pfi_bvects)
        np.savetxt(fname=pfi_transposed_vects, X=m.T, fmt='%10.8f')

    if controller['noddi']:

        # check if there is a DWI already processed in the TMP folder of the same subject:
        pfo_tmp_dwi = jph(pfo_output_sj, 'z_tmp', 'z_DWI')
        pfi_dwi_eddy_corrected = jph(pfo_tmp_dwi, sj + '_DWI_eddy.nii.gz')
        pfi_transposed_bvals = jph(pfo_tmp, sj + '_DWI_DwEffBval_T.txt')
        pfi_transposed_vects = jph(pfo_tmp, sj + '_DWI_DwGradVec_T.txt')
        pfi_roi_mask = jph(pfo_mask, sj + '_b0_roi_mask.nii.gz')
        assert os.path.exists(pfi_dwi_eddy_corrected), 'Need to run process_DWI first?'
        assert os.path.exists(pfi_transposed_bvals)
        assert os.path.exists(pfi_transposed_vects)
        assert os.path.exists(pfi_roi_mask)
        pfi_output_noddi = jph(pfo_tmp, sj + '_noddi.nii.gz')
        cmd = 'fit_dwi -source {0} -mask {1} -bval {2} -bvec {3} -mcmap {4} -nod'.format(
            pfi_dwi_eddy_corrected, pfi_roi_mask, pfi_transposed_bvals, pfi_transposed_vects, pfi_output_noddi)
        print_and_run(cmd)

    if controller['save T2_times']:
        if subject[sj][0][1] == 'ex_vivo':
            t2_times = (15, 80, 110)
        elif subject[0][1] == 'in_vivo':
            t2_times = (15, 80, 110)
        else:
            t2_times = (15, 80, 110)
        pfi_T2_times = jph(pfo_tmp, sj + '_t2_times.txt')
        np.savetxt(fname=pfi_T2_times, X=np.array(t2_times), fmt='%10.10f', newline=' ')

    if controller['get acquisition echo time']:
        pfi_visu_pars = jph(pfo_input_sj_MSME, sj + '_MSME_visu_pars.npy')
        assert os.path.exists(pfi_visu_pars)
        pfi_echo_times = jph(pfo_tmp, sj + '_echo_times.txt')
        visu_pars_dict = np.load(pfi_visu_pars)
        np.savetxt(fname=pfi_echo_times, X=visu_pars_dict.item().get('VisuAcqEchoTime'), fmt='%10.2f', newline=' ')

    if controller['fit msme']:
        pfi_msme_up = jph(pfo_mod, sj + '_MSME_up.nii.gz')
        pfi_roi_mask = jph(pfo_mask, sj + '_b0_roi_mask.nii.gz')
        pfi_echo_times = jph(pfo_tmp, sj + '_echo_times.txt')
        pfi_T2_times = jph(pfo_tmp, sj + '_t2_times.txt')
        assert os.path.exists(pfi_msme_up), 'Need to run process_MSME first?'
        assert os.path.exists(pfi_roi_mask)
        assert os.path.exists(pfi_echo_times)
        assert os.path.exists(pfi_T2_times)
        pfi_output_mwf = jph(pfo_tmp, sj + '_vmwf.nii.gz')
        cmd = 'fit_qt2 -source {0} -mask {1} -nc 3 -TElist {2} -T2list {3} -mwf {4}'.format(
            pfi_msme_up, pfi_roi_mask, pfi_echo_times, pfi_T2_times, pfi_output_mwf)
        print_and_run(cmd)

    if controller['extract first tp noddi']:
        pfi_noddi = jph(pfo_tmp, sj + '_noddi.nii.gz')
        assert os.path.exists(pfi_noddi)
        pfi_vin = jph(pfo_tmp, sj + '_vin.nii.gz')
        cmd = 'seg_maths {0} -tp 0 {1}'.format(pfi_noddi, pfi_vin)
        print_and_run(cmd)

    if controller['compute g-ratio']:
        pfi_mwf = jph(pfo_tmp, sj + '_vmwf.nii.gz')
        pfi_vin = jph(pfo_tmp, sj + '_vin.nii.gz')
        assert os.path.exists(pfi_mwf)
        assert os.path.exists(pfi_vin)
        pfi_tmp = jph(pfo_tmp, sj + '_tmp_g_ratio.nii.gz')
        pfi_g_ratio = jph(pfo_tmp, sj + '_g_ratio.nii.gz')
        cmd1 = 'fit_maths {0} -mul -1. {1}'.format(pfi_mwf, pfi_tmp)
        cmd2 = 'fit_maths {0} -add 1.0 {0}'.format(pfi_tmp)
        cmd3 = 'fit_maths {0} -mul {1} {0}'.format(pfi_tmp, pfi_vin)
        cmd4 = 'fit_maths {0} -div {1} {1}'.format(pfi_mwf, pfi_tmp)
        cmd5 = 'fit_maths {0} -add 1.0 {0}'.format(pfi_tmp)
        cmd6 = 'fit_maths {0} -recip {0}'.format(pfi_tmp)
        cmd7 = 'fit_maths {0} -sqrt {0}'.format(pfi_tmp)
        cmd8 = 'seg_maths {0} -uthr 0.999999999 {1}'.format(pfi_tmp, pfi_g_ratio)
        print_and_run(cmd1)
        print_and_run(cmd2)
        print_and_run(cmd3)
        print_and_run(cmd4)
        print_and_run(cmd5)
        print_and_run(cmd6)
        print_and_run(cmd7)
        print_and_run(cmd8)


def process_g_ratio_per_group(controller, pfo_input_group_category, pfo_output_group_category, bypass_subjects=None):

    assert os.path.exists(pfo_input_group_category)
    assert os.path.exists(pfo_output_group_category)

    subj_list = np.sort(list(set(os.listdir(pfo_input_group_category)) - {'.DS_Store'}))

    # allow to force the subj_list to be the input tuple bypass subject, chosen by the user.
    if bypass_subjects is not None:

        if set(bypass_subjects).intersection(set(subj_list)) == {}:
            raise IOError
        else:
            subj_list = bypass_subjects

    print '\n\n Processing T1 subjects  from {0} to {1} :\n {2}\n'.format(pfo_input_group_category,
                                                                          pfo_output_group_category,
                                                                          subj_list)
    for sj in subj_list:
        process_g_ratio_per_subject(sj,
                                    jph(pfo_input_group_category, sj, sj + '_DWI'),
                                    jph(pfo_input_group_category, sj, sj + '_MSME'),
                                    jph(pfo_output_group_category, sj),
                                    controller)


def execute_processing_g_ratio(controller, rp):

    assert isinstance(rp, RunParameters)

    root_nifti = jph(root_study_rabbits, '01_nifti')
    root_data = jph(root_study_rabbits, 'A_data')

    if rp.execute_PTB_ex_skull:
        pfo_PTB_ex_skull = jph(root_nifti, 'PTB', 'ex_skull')
        assert os.path.exists(pfo_PTB_ex_skull), pfo_PTB_ex_skull
        pfo_PTB_ex_skull_data = jph(root_data, 'PTB', 'ex_skull')
        process_g_ratio_per_group(controller, pfo_PTB_ex_skull, pfo_PTB_ex_skull_data, bypass_subjects=rp.subjects)

    if rp.execute_PTB_ex_vivo:
        pfo_PTB_ex_vivo = jph(root_nifti, 'PTB', 'ex_vivo')
        assert os.path.exists(pfo_PTB_ex_vivo), pfo_PTB_ex_vivo
        pfo_PTB_ex_vivo_data = jph(root_data, 'PTB', 'ex_vivo')
        process_g_ratio_per_group(controller, pfo_PTB_ex_vivo, pfo_PTB_ex_vivo_data, bypass_subjects=rp.subjects)

    if rp.execute_PTB_in_vivo:
        pfo_PTB_in_vivo = jph(root_nifti, 'PTB', 'in_vivo')
        assert os.path.exists(pfo_PTB_in_vivo), pfo_PTB_in_vivo
        pfo_PTB_in_vivo_data = jph(root_data, 'PTB', 'in_vivo')
        process_g_ratio_per_group(controller, pfo_PTB_in_vivo, pfo_PTB_in_vivo_data, bypass_subjects=rp.subjects)

    if rp.execute_PTB_op_skull:
        pfo_PTB_op_skull = jph(root_nifti, 'PTB', 'op_skull')
        assert os.path.exists(pfo_PTB_op_skull), pfo_PTB_op_skull
        pfo_PTB_op_skull_data = jph(root_data, 'PTB', 'op_skull')
        process_g_ratio_per_group(controller, pfo_PTB_op_skull, pfo_PTB_op_skull_data, bypass_subjects=rp.subjects)

    if rp.execute_ACS_ex_vivo:
        pfo_ACS_ex_vivo = jph(root_nifti, 'ACS', 'ex_vivo')
        assert os.path.exists(pfo_ACS_ex_vivo), pfo_ACS_ex_vivo
        pfo_ACS_ex_vivo_data = jph(root_data, 'ACS', 'ex_vivo')
        process_g_ratio_per_group(controller, pfo_ACS_ex_vivo, pfo_ACS_ex_vivo_data, bypass_subjects=rp.subjects)


if __name__ == '__main__':
    print('process g-ratio, local run. ')

    controller_steps = {'transpose b-vals b-vects'  : True,
                        'noddi'                     : True,
                        'save T2_times'             : True,
                        'get acquisition echo time' : True,
                        'fit msme'                  : True,
                        'extract first tp noddi'    : True,
                        'compute g-ratio'           : True,
                        'save results'              : True}

    rpa = RunParameters()

    # rpa.execute_PTB_ex_skull = True
    # rpa.execute_PTB_ex_vivo = True
    # rpa.execute_PTB_in_vivo = False
    # rpa.execute_PTB_op_skull = True
    rpa.execute_ACS_ex_vivo = True

    # rpa.subjects = ['3103']
    # rpa.update_params()

    execute_processing_g_ratio(controller_steps, rpa)
