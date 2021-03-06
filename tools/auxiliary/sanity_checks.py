import os
import time
import subprocess

from tools.definitions import bfc_corrector_cmd, root_fit_apps


# def check_path(pfi, interval=1, timeout=100):
#     if os.path.exists(pfi):
#         if pfi.endswith('.nii.gz'):
#             mustend = time.time() + timeout
#             while time.time() < mustend:
#                 try:
#                     subprocess.check_output('gunzip -t {}'.format(pfi), shell=True)
#                 except subprocess.CalledProcessError:
#                     print "Caught CalledProcessError"
#                 else:
#                     return True
#                 time.sleep(interval)
#             msg = 'File {0} corrupted after 100 tests. \n'.format(pfi)
#             raise IOError(msg)
#         else:
#             return True
#     else:
#         msg = '{} does not exist!'.format(pfi)
#         raise IOError(msg)


def check_libraries():

    def cmd_exists(cmd, msg):
        if subprocess.call("type " + cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0:
            return True
        else:
            raise EnvironmentError(msg)
    #
    # aa = 'export PATH=/home/ferraris/software_lib/NiftyFit2/niftyfit-build/fit-apps/:${PATH}'
    # os.system(aa)

    assert cmd_exists(bfc_corrector_cmd, 'No Niftk installed')
    assert cmd_exists('seg_maths', 'No Nifty Seg installed')
    assert cmd_exists('reg_aladin', 'No Nifty Reg installed')
    assert cmd_exists('fslhd', 'No fsl installed')
    assert cmd_exists(root_fit_apps + 'fit_maths', 'No Nifty Fit installed')
    assert cmd_exists(root_fit_apps + 'fit_qt2', 'No Nifty Fit fit_qt2 installed')


