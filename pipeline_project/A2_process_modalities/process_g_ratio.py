import os
import numpy as np
from os.path import join as jph

from tools.definitions import root_study_rabbits
from tools.auxiliary.utils import print_and_run
from pipeline_project.A0_main.main_controller import subject, ListSubjectsManager


def transpose_matrix_in_txt(pfi_input, pfi_output):
    m = np.loadtxt(pfi_input)
    np.savetxt(fname=pfi_output, X=m.T)


def process_g_ratio_per_subject(sj, controller):

    print('\nProcessing g-ratio {} started.\n'.format(sj))

    group = subject[sj][0][0]
    category = subject[sj][0][1]
    pfo_input_sj_DWI = jph(root_study_rabbits, '01_nifti', group, category, sj, sj + '_DWI')
    pfo_input_sj_MSME = jph(root_study_rabbits, '01_nifti', group, category, sj, sj + '_MSME')
    pfo_output_sj = jph(root_study_rabbits, 'A_data', group, category, sj)

    # input sanity check:
    if sj not in subject.keys():
        raise IOError('Subject parameters not known')
    if not os.path.exists(pfo_input_sj_DWI):
        raise IOError('Input folder DWI does not exist.')
    if not os.path.exists(pfo_input_sj_MSME):
        raise IOError('Input folder MSME does not exist.')
    if not os.path.exists(pfo_output_sj):
        raise IOError('Output folder MSME does not exist.')

    # --  Generate intermediate and output folder

    pfo_mod = jph(pfo_output_sj, 'mod')
    pfo_segm = jph(pfo_output_sj, 'segm')
    pfo_mask = jph(pfo_output_sj, 'z_mask')
    pfo_tmp = jph(pfo_output_sj, 'z_tmp', 'z_gr')

    print_and_run('mkdir -p {}'.format(pfo_output_sj))
    print_and_run('mkdir -p {}'.format(pfo_mod))
    print_and_run('mkdir -p {}'.format(pfo_segm))
    print_and_run('mkdir -p {}'.format(pfo_mask))
    print_and_run('mkdir -p {}'.format(pfo_tmp))

    # --

    if controller['transpose b-vals b-vects']:
        print('- Transpose b-vals and b-vects')
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
        print('- Noddi execution')
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
        pfi_output_noddi = jph(pfo_tmp, sj + '_nod.nii.gz')
        cmd = 'fit_dwi -source {0} -mask {1} -bval {2} -bvec {3} -mcmap {4} -nod'.format(
            pfi_dwi_eddy_corrected, pfi_roi_mask, pfi_transposed_bvals, pfi_transposed_vects, pfi_output_noddi)
        print_and_run(cmd)

    if controller['save T2_times']:
        if subject[sj][0][1] == 'ex_vivo':
            t2_times = (14, 70, 100)  # (15, 80, 110) - proposed 3, 16, 22
        elif subject[sj][0][1] == 'in_vivo':
            t2_times = (14, 70, 100)
        else:
            t2_times = (14, 70, 100)
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
        pfi_mwf = jph(pfo_tmp, sj + '_vmvf.nii.gz')
        cmd = 'fit_qt2 -source {0} -mask {1} -nc 3 -TElist {2} -T2list {3} -mwf {4}'.format(
            pfi_msme_up, pfi_roi_mask, pfi_echo_times, pfi_T2_times, pfi_mwf)
        print cmd
        print_and_run(cmd)

        if not os.path.exists(pfi_mwf):
            raise IOError('Something went wrong in using fit_qt2...')

    if controller['extract first tp noddi']:
        pfi_noddi = jph(pfo_tmp, sj + '_nod.nii.gz')
        assert os.path.exists(pfi_noddi)
        pfi_vin = jph(pfo_tmp, sj + '_vin.nii.gz')
        cmd = 'seg_maths {0} -tp 0 {1}'.format(pfi_noddi, pfi_vin)
        print_and_run(cmd)

    if controller['compute g-ratio']:
        pfi_mwf = jph(pfo_tmp, sj + '_vmvf.nii.gz')
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

    if controller['save results']:
        pfi_g_ratio = jph(pfo_tmp, sj + '_g_ratio.nii.gz')
        assert os.path.exists(pfi_g_ratio)
        pfi_g_ratio_final = jph(pfo_mod, sj + '_g_ratio.nii.gz')
        cmd = 'cp {} {} '.format(pfi_g_ratio, pfi_g_ratio_final)
        print_and_run(cmd)


def process_g_ratio_from_list(subj_list, controller):

    print '\n\n Processing g-ratio subjects from list {0} \n'.format(subj_list)

    for sj in subj_list:
        process_g_ratio_per_subject(sj, controller)


if __name__ == '__main__':
    print('process g-ratio, local run. ')

    controller_steps = {'transpose b-vals b-vects'  : False,
                        'noddi'                     : False,
                        'save T2_times'             : True,
                        'get acquisition echo time' : True,
                        'fit msme'                  : True,
                        'extract first tp noddi'    : True,
                        'compute g-ratio'           : True,
                        'save results'              : True}

    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull = False
    lsm.execute_PTB_ex_vivo = False
    lsm.execute_PTB_in_vivo = False
    lsm.execute_PTB_op_skull = False
    lsm.execute_ACS_ex_vivo = False

    lsm.input_subjects = ['3103', ]


    lsm.update_ls()

    process_g_ratio_from_list(lsm.ls, controller_steps)
