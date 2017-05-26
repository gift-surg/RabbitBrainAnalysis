import os

from pipeline_project.A0_main.main_controller import RunParameters
from definitions import root_study_pantopolium


def compile_record_MSME(rp):
    assert os.path.isdir(root_study_pantopolium), 'Connect pantopolio!'
    assert isinstance(rp, RunParameters)
