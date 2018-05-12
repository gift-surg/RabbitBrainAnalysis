import os
from os.path import join as jph
from tools.definitions import root_study_rabbits


list_subjects_to_process = ['1201', '1203', '1305', '1404', '1507', '1510', '1702', '1805', '2002', '2502', '3301', '3404']

root_main_AFD_analysis = jph(root_study_rabbits, 'B_AFD_analysis')

root_DWIs_original   = jph(root_main_AFD_analysis, 'DWIs_original')
root_DWIs_corrected  = jph(root_main_AFD_analysis, 'DWIs_corrected')
root_MASKs           = jph(root_main_AFD_analysis, 'MASKs')
root_SEGMs           = jph(root_main_AFD_analysis, 'SEGMs')
root_intermediate    = jph(root_main_AFD_analysis, 'intermediate')
root_output          = jph(root_main_AFD_analysis, 'output')
root_tmp             = jph(root_main_AFD_analysis, 'z_tmp')
root_fod             = jph(root_main_AFD_analysis, 'FODs')
root_fod_template    = jph(root_main_AFD_analysis, 'FODs_template')


if __name__ == '__main__':
    os.system('mkdir {}'.format(root_DWIs_original))
    os.system('mkdir {}'.format(root_DWIs_corrected))
    os.system('mkdir {}'.format(root_MASKs))
    os.system('mkdir {}'.format(root_SEGMs))
    os.system('mkdir {}'.format(root_intermediate))
    os.system('mkdir {}'.format(root_output))
    os.system('mkdir {}'.format(root_tmp))
    os.system('mkdir {}'.format(root_fod))
    os.system('mkdir {}'.format(root_fod_template))
