import cPickle as Pickle
from os.path import join as jph

from main_pipeline.A0_main.main_controller import ListSubjectsManager
from main_pipeline.U_utils.report_generator import ReportGenerator
from tools.definitions import pfo_subjects_parameters, pfi_labels_descriptor, root_study_rabbits


def generate_report_per_subject(sj, selected_segmentation_suffix):

    sj_parameters = Pickle.load(open(jph(pfo_subjects_parameters, sj), 'r'))
    study = sj_parameters['study']
    category = sj_parameters['category']

    pfo_data_sj = jph(root_study_rabbits, 'A_data', study, category, sj)

    rg = ReportGenerator()

    rg.sj_name = sj
    rg.pfo_report = jph(pfo_data_sj, 'report')
    rg.pfo_pre_report = jph(pfo_data_sj, 'report', 'z_pre_report')

    pfi_T1 = jph(pfo_data_sj, 'mod', '{}_T1.nii.gz'.format(sj))
    pfi_g_ratio = jph(pfo_data_sj, 'mod', '{}_g_ratio.nii.gz'.format(sj))
    pfi_FA = jph(pfo_data_sj, 'mod', '{}_FA.nii.gz'.format(sj))
    pfi_MD = jph(pfo_data_sj, 'mod', '{}_MD.nii.gz'.format(sj))
    pfi_T2map = jph(pfo_data_sj, 'mod', '{}_T2map.nii.gz'.format(sj))

    rg.list_pfi_anatomies     = [pfi_T1, pfi_g_ratio, pfi_FA, pfi_MD, pfi_T2map]

    pfo_automatic_segm = jph(pfo_data_sj, 'segm', 'automatic')
    pfi_T1_segm = jph(pfo_automatic_segm, '{0}_T1_segm{1}.nii.gz'.format(sj, selected_segmentation_suffix))
    pfi_g_ratio_segm = jph(pfo_automatic_segm, '{0}_S0_segm{1}.nii.gz'.format(sj, selected_segmentation_suffix))
    pfi_FA_segm = pfi_g_ratio_segm
    pfi_MD_segm = pfi_g_ratio_segm
    pfi_T2map_segm = pfi_g_ratio_segm

    rg.list_pfi_segmentations = [pfi_T1_segm, pfi_g_ratio_segm, pfi_FA_segm, pfi_MD_segm, pfi_T2map_segm]
    rg.modalities = ['T1', 'g_ratio', 'FA', 'MD', 'T2map']

    rg.pfi_labels_descriptor = pfi_labels_descriptor
    rg.pfi_info_excel_table = jph(root_study_rabbits, 'A_data', 'DataSummary.xlsx')
    rg.pfo_subjects_param = pfo_subjects_parameters
    rg.tot_volume_prior = None
    rg.verbose = 1

    rg.check_attributes()
    rg.generate_structure()

    rg.generate_pre_report_each_mod()
    rg.pre_report2report()
    rg.save_report_human_readable()


def process_T1_from_list(subj_list, selected_segmentation_suffix):

    print '\n\n Generating report subjects from list {} \n'.format(subj_list)
    for sj in subj_list:
        generate_report_per_subject(sj, selected_segmentation_suffix)


if __name__ == '__main__':
    print('Generate report, local run. ')
    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull = False
    lsm.execute_PTB_ex_vivo = False
    lsm.execute_PTB_in_vivo = False
    lsm.execute_PTB_op_skull = False
    lsm.execute_ACS_ex_vivo = False

    lsm.input_subjects = ['1201', ]
    lsm.update_ls()

    process_T1_from_list(lsm.ls, '_IN_TEMPLATE')
