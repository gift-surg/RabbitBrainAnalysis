from main_pipeline.A0_main.main_controller import ListSubjectsManager
from main_pipeline.U_utils.report_generator import ReportGenerator


def generate_report_per_subject(sj):
    print('Generate report subject {}'.format(sj))
    rg = ReportGenerator(sj)
    rg.get_raw_volumes()
    rg.get_raw_FA()
    rg.get_raw_MD()


def generate_reports_from_list(subj_list):
    print '\n\n Generating report subjects from list {} \n'.format(subj_list)
    for sj in subj_list:
        generate_report_per_subject(sj)


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

    generate_reports_from_list(lsm.ls)
