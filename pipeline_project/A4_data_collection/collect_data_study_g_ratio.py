import os

from pipeline_project.A0_main.main_controller import ListSubjectsManager
from definitions import root_study_rabbits


def compile_record_g_ratio_from_subject_list(subj_list):
    # pfi_visu_pars = jph(pfo_input_sj_MSME, sj + '_MSME_visu_pars.npy')
    # assert os.path.exists(pfi_visu_pars)
    # pfi_echo_times = jph(pfo_tmp, sj + '_echo_times.txt')
    # visu_pars_dict = np.load(pfi_visu_pars)
    # visu_pars_dict.item().get('VisuAcqEchoTime')
    print subj_list
