import os
import numpy as np
import nibabel as nib
import pickle
from os.path import join as jph
import seaborn as sns
import matplotlib.pyplot as plt
from collections import OrderedDict

from main_pipeline.A0_main.main_controller import ListSubjectsManager
from tools.definitions import root_study_rabbits, pfo_subjects_parameters


root_output = jph(root_study_rabbits, 'B_stats', 'S0Comparison_denoised')
S0_timepoints = 7


def get_values_below_S0_in_DWI_for_subject(sj):
    print('get_values_below_S0_in_DWI_for_subject {}'.format(sj))

    sj_parameters = pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))

    study = sj_parameters['study']
    category = sj_parameters['category']

    root_subject = jph(root_study_rabbits, 'A_data', study, category, sj)

    pfo_sj_segm = jph(root_subject, 'segm')

    pfi_DWI_Eddi_corrected = jph(root_subject, 'z_tmp', 'z_DWI', '{}_DWI_eddy.nii.gz'.format(sj))
    pfi_segm = jph(pfo_sj_segm, '{}_S0_segm.nii.gz'.format(sj))

    assert os.path.exists(pfi_DWI_Eddi_corrected)
    assert os.path.exists(pfi_segm)

    im_dwi = nib.load(pfi_DWI_Eddi_corrected)
    im_segm = nib.load(pfi_segm)

    values_below_S0_tps = OrderedDict()

    for tp in range(S0_timepoints):
        print('--- timepoint {}'.format(tp))
        vals_below = im_dwi.get_data()[im_segm.get_data() == 218, tp].flatten()

        values_below_S0_tps.update({'tp{}'.format(tp) : vals_below})

    pfi_output_pickled = jph(root_output, '{}_below_S0_values.pickle'.format(sj))
    with open(pfi_output_pickled, 'wb') as handle:
        pickle.dump(values_below_S0_tps, handle)


def from_values_below_S0_in_DWI_to_struct_per_sj(sj):
    """
    strcut is a 3 x timepoints vector with
    [ upper quartile_tp ]_tp
    [ median_tp         ]_tp
    [ lower quartile_tp ]_tp

    :param sj: subject_id
    :return:
    """
    print('from_values_below_S0_in_DWI_to_struct_per_sj {}'.format(sj))
    pfi_input_values = jph(root_output, '{}_below_S0_values.pickle'.format(sj))
    with open(jph(pfi_input_values), 'r') as handle:
        data_sj = pickle.load(handle)
    timepoints = len(data_sj.keys())

    struct = np.zeros([3, timepoints])

    for k_id, k in enumerate(data_sj.keys()):
        print('--- {}'.format(k))
        struct[0, k_id] = np.percentile(data_sj[k], 75)
        struct[1, k_id] = np.median(data_sj[k])
        struct[2, k_id] = np.percentile(data_sj[k], 25)

    pfi_output = jph(root_output, '{}_struct.txt'.format(sj))
    np.savetxt(pfi_output, struct)


def from_sj_list_to_S0_graphs_via_structs(sj_list):
    print('Graph visualisation subjects list {}'.format(sj_list))

    fig, ax = plt.subplots(figsize=(12, 4))
    fig.canvas.set_window_title('S0 values brain tissue')
    sns.set(color_codes=True)

    k = 0
    k_ticks = []
    for sj in sj_list:
        k_ticks.append(k)
        pfi_struct = jph(root_output, '{}_struct.txt'.format(sj))
        struct_sj = np.loadtxt(pfi_struct)
        num_tp = struct_sj.shape[1]

        # ax.errorbar(range(k, k + num_tp), struct_sj[1, :], yerr=[struct_sj[2, :], struct_sj[0, :]], fmt='--o')

        ax.errorbar(range(k, k + num_tp), struct_sj[1, :], fmt='--o')

        k += num_tp

    # xticks_minor = [1, 5, 7, 9, 11]
    # xlbls = ['background', '5 year statistical summary', 'future build',
    #          'maximum day', '90th percentile day', 'average day']

    xticks = [j + 3.5 for j in k_ticks]
    ax.set_xticks(xticks)
    ax.set_xticklabels(sj_list)

    ax.set_title('Median (quartiles) S0 below CC in DWI')
    ax.set_xlabel('Subject Id')
    ax.set_ylabel('S0 values')

    plt.tight_layout()

    plt.show()

    # ax.boxplot([tot_data_distribution[k] for k in sj_list])
    #
    # if subjects_grouping is not None:
    #     assert np.sum(subjects_grouping) == len(subjects)
    #     medians = [np.median(tot_data_distribution[k]) for k in sj_list]
    #     cumulative_grouping = np.cumsum([0] + subjects_grouping)
    #     medians_grouped = [[medians[l] for l in range(cumulative_grouping[k], cumulative_grouping[k+1])] for k in range(len(cumulative_grouping) - 1)]
    #     medians_of_medians_grouped = [np.median(li) for li in medians_grouped]
    #
    #     for i, m in enumerate(medians_of_medians_grouped):
    #         ax.hlines(y=m, xmin=cumulative_grouping[i] + 1, xmax=cumulative_grouping[i+1], color='r', alpha=0.5, linestyles='dashed')
    #
    # ax.set_title('{} per region {}'.format(mod, macro_label_name))
    # ax.set_ylabel('{}'.format(mod))
    # ax.set_xlabel('Subject Id')
    # ax.set_xticks(range(1, len(tot_data_distribution.keys())+1))
    # ax.set_xticklabels(sj_list, ha='center', rotation=45, fontsize=10)
    # ax.xaxis.labelpad = 20
    #
    # plt.tight_layout()
    #
    # # plt.show()
    #
    # plt.savefig(jph(root_output, '{}region{}_{}.pdf'.format(mod, macro_label_name, coord_system)), format='pdf',
    #             dpi=200)
    # plt.close()


if __name__ == '__main__':

    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull = False
    lsm.execute_PTB_ex_vivo  = False
    lsm.execute_PTB_in_vivo  = False
    lsm.execute_PTB_op_skull = False
    lsm.execute_ACS_ex_vivo  = False

    # lsm.input_subjects = ['12307', '12308', '12309', '12402', '12504', '12505', '12607', '12608', '12609', '12610']

    # lsm.input_subjects = ['12402', '12607', '12307', '12608', '12504', '12609', '12308', '12610', '12505', '12309',]
    # lsm.input_subjects = ['12402', '12607', '12307', '12608', '12504', '12609', '12308', '12610', '12505', '12309'] + ['13103', '13108', '13301', '13307', '13401', '13403', '13404'] + ['13405', '13501', '13505', '13507', '13602', '13604', '13606']
    lsm.input_subjects = ['12308', '12308666']
    lsm.update_ls()

    print(lsm.ls)

    # subjects = ['12402', '12607', '12307', '12608', '12504', '12609', '12308', '12610', '12505', '12309']

    for sj_ in lsm.ls:
        if False:
            get_values_below_S0_in_DWI_for_subject(sj_)
        if False:
            from_values_below_S0_in_DWI_to_struct_per_sj(sj_)
    if True:
        from_sj_list_to_S0_graphs_via_structs(lsm.ls)
