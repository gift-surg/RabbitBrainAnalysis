import os
import numpy as np
import pickle

from tools.definitions import pfo_subjects_parameters
from os.path import join as jph
from tools.auxiliary.utils import print_and_run

from main_pipeline.A0_main.subject_parameters_manager import list_all_subjects

def transpose_matrix_in_txt(pfi_input, pfi_output):
    m = np.loadtxt(pfi_input)
    np.savetxt(fname=pfi_output, X=m.T)


def process_MSME_per_subject(sj, pfo_input_sj_MSME, pfo_output_sj, controller):

    print('\nProcessing MSME {} started.\n'.format(sj))

    # input sanity check:
    all_sj = list_all_subjects(pfo_subjects_parameters)
    if sj not in all_sj:
        raise IOError('Subject parameters not known')
    if not os.path.exists(pfo_input_sj_MSME):
        raise IOError('Input folder T1 does not exist.')

    # --  Generate intermediate and output folder

    pfo_mod = jph(pfo_output_sj, 'mod')
    pfo_segm = jph(pfo_output_sj, 'segm')
    pfo_mask = jph(pfo_output_sj, 'masks')
    pfo_tmp = jph(pfo_output_sj, 'z_tmp', 'z_MSME')

    print_and_run('mkdir -p {}'.format(pfo_output_sj))
    print_and_run('mkdir -p {}'.format(pfo_mod))
    print_and_run('mkdir -p {}'.format(pfo_segm))
    print_and_run('mkdir -p {}'.format(pfo_mask))
    print_and_run('mkdir -p {}'.format(pfo_tmp))

    # --

    if controller['transpose b-vals b-vects']:
        pfi_bvals = ''
        pfi_vects = ''
        assert os.path.exists(pfi_bvals)
        assert os.path.exists(pfi_vects)
        pfi_transpose_bvals = ''
        pfi_transpose_vects = ''
        m = np.loadtxt(pfi_bvals)
        np.savetxt(fname=pfi_transpose_bvals, X=m.T)
        m = np.loadtxt(pfi_vects)
        np.savetxt(fname=pfi_transpose_vects, X=m.T)

    if controller['noddi']:
        pfi_dwi = ''
        pfi_mask = ''
        pfi_bval_in_row = ''
        pfi_bvec_in_row = ''
        pfi_output_noddi = ''
        cmd = 'fit_dwi -source {0} -mask {1} -bval {2} -bvec {3} -mcmap {4} -nod'.format(
            pfi_dwi, pfi_mask, pfi_bval_in_row, pfi_bvec_in_row, pfi_output_noddi)
        print_and_run(cmd)

    if controller['save T2_times']:

        sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

        if sj_parameters['category'] == 'ex_vivo':
            t2_times = (0, 0, 0)  # myelin, GM, CSF default
        elif sj_parameters['category'] == 'in_vivo':
            t2_times = (0, 0, 0)
        else:
            t2_times = (0, 0, 0)
        pfi_T2_times = ''
        np.savetxt(fname=pfi_T2_times, X=np.array(t2_times))

    if controller['fit msme']:
        pfi_msme_up = ''
        pfi_masks = ''
        pfi_echo_times = ''
        pfi_T2_times = ''
        pfi_output_mwf = ''
        cmd = 'fit_qt2 -source {0} -mask {1} -nc 3 -TElist {2} -T2list {3} -mwf {4}'.format(
            pfi_msme_up, pfi_masks, pfi_echo_times, pfi_T2_times, pfi_output_mwf)
        print_and_run(cmd)

    if controller['extract first tp noddi']:
        pfi_noddi = ''
        assert os.path.exists(pfi_noddi)
        pfi_vin = ''
        cmd = 'seg_maths {0} -tp 0 {1}'.format(pfi_noddi, pfi_vin)
        print_and_run(cmd)

    if controller['compute g-ratio']:
        pfi_mwf = ''
        pfi_vin = ''
        assert os.path.exists(pfi_mwf)
        assert os.path.exists(pfi_vin)
        pfi_tmp = ''
        pfi_g_ratio = ''
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



