import pickle
import os

from tools.definitions import pfo_subjects_parameters


# Bias field parameters order
#
# convergenceThreshold = 0.001
# maximumNumberOfIterations = (50, 50, 50, 50)
# biasFieldFullWidthAtHalfMaximum = 0.15
# wienerFilterNoise = 0.01
# numberOfHistogramBins = 200
# numberOfControlPoints = (4, 4, 4)
# splineOrder = 3

# Axial Angle, angle of the axial orientation sign from L to R,
# from initial position to aligned with axis (yaw).
# Bicomm (or coronal) Angle is the opening angle from histological away from it (bicommissural positive) in rad (pitch).
# Sagittal Angle sign from L to R from initial position to aligned with axis (roll)


class ListSubjectsManager(object):
    def __init__(self, execute_PTB_ex_skull=False, execute_PTB_ex_vivo=False, execute_PTB_in_vivo=False,
                 execute_PTB_op_skull=False, execute_ACS_ex_vivo01=False, execute_ACS_ex_vivo02=False, input_subjects=None):

        self.execute_PTB_ex_skull   = execute_PTB_ex_skull
        self.execute_PTB_ex_vivo    = execute_PTB_ex_vivo
        self.execute_PTB_in_vivo    = execute_PTB_in_vivo
        self.execute_PTB_op_skull   = execute_PTB_op_skull
        self.execute_ACS_ex_vivo01  = execute_ACS_ex_vivo01
        self.execute_ACS_ex_vivo02  = execute_ACS_ex_vivo02

        self.input_subjects = input_subjects
        # sl: subject list is the most important attirbute of the class
        self.ls = []

    def update_ls(self):

        self.ls = []  # re initialise to remove duplicates.
        prod_conditions = self.execute_PTB_ex_skull + self.execute_PTB_ex_vivo + self.execute_PTB_in_vivo + \
                            self.execute_PTB_op_skull + self.execute_ACS_ex_vivo01 + self.execute_ACS_ex_vivo02
        if prod_conditions > 0:

            # Get information from subjects parameters
            list_subjects = [file_name for file_name in os.listdir(pfo_subjects_parameters)
                             if not file_name.endswith(".txt")]
            
            for k in list_subjects:

                subj_k_parameters = pickle.load(open(os.path.join(pfo_subjects_parameters, k), 'r'))
                
                if self.execute_PTB_ex_skull:
                    if subj_k_parameters['study'] == 'PTB' and subj_k_parameters['category'] == 'ex_skull':
                        self.ls.append(k)
                if self.execute_PTB_ex_vivo:
                    if subj_k_parameters['study'] == 'PTB' and subj_k_parameters['category'] == 'ex_vivo':
                        self.ls.append(k)
                if self.execute_PTB_in_vivo:
                    if subj_k_parameters['study'] == 'PTB' and subj_k_parameters['category'] == 'in_vivo':
                        self.ls.append(k)
                if self.execute_PTB_op_skull:
                    if subj_k_parameters['study'] == 'PTB' and subj_k_parameters['category'] == 'op_skull':
                        self.ls.append(k)
                if self.execute_ACS_ex_vivo01:
                    if subj_k_parameters['study'] == 'ACS' and subj_k_parameters['category'] == 'ex_vivo01':
                        self.ls.append(k)
                if self.execute_ACS_ex_vivo02:
                    if subj_k_parameters['study'] == 'ACS' and subj_k_parameters['category'] == 'ex_vivo02':
                        self.ls.append(k)

        if self.input_subjects is not None:
            if isinstance(self.input_subjects, str):
                self.ls.append(self.input_subjects)
            elif isinstance(self.input_subjects, list):
                self.ls += self.input_subjects
        # elim duplicate and reorder:
        if not self.ls == []:
            sorted_ls = list(set(self.ls))
            sorted_ls.sort()
            self.ls = sorted_ls

    def append(self, new_list):
        self.ls += new_list
