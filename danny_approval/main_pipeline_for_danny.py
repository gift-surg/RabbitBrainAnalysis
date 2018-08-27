import os
from os.path import join as jph
import collections

from tools.auxiliary.sanity_checks import check_libraries

from main_pipeline.A0_main.subject_parameters_creator import reset_parameters_files
from main_pipeline.A0_main.subject_parameters_manager import check_subjects_situation

from tools.definitions import pfo_subjects_parameters, multi_atlas_subjects

from main_pipeline.A0_main.main_executer import main_runner
from main_pipeline.A0_main.main_controller import ListSubjectsManager


if __name__ == '__main__':

    ''' Set parameters per subjects or per group '''

    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull  = False
    lsm.execute_PTB_ex_vivo   = False
    lsm.execute_PTB_in_vivo   = False
    lsm.execute_PTB_op_skull  = False
    lsm.execute_ACS_ex_vivo   = False

    # lsm.input_subjects = ['12503']
    lsm.input_subjects = ['13111', ]  # '5302', '5303'] '5302', '5303'
    # lsm.input_subjects = ['13111', ]
    # lsm.input_subjects = ['5302', '5303']
    # lsm.input_subjects = ['5303']

    lsm.update_ls()

    print(lsm.ls)

    # Set steps
    steps = collections.OrderedDict()

    steps.update({'reset_parameters'   : False  })
    steps.update({'step_A1'            : False  })
    steps.update({'step_A2_T1'         : False  })
    steps.update({'step_A2_DWI'        : False  })
    steps.update({'step_A2_MSME'       : False  })
    steps.update({'step_A2_T2maps'     : False  })
    steps.update({'step_A2_g_ratio'    : False  })
    steps.update({'step_A3_move'       : True  })
    steps.update({'step_A3_brain_mask' : True  })
    steps.update({'step_A3_segment'    : True  })
    steps.update({'step_A3_move_back'  : True  })
    steps.update({'step_A4'            : False  })

    main_runner(lsm.ls, steps)
