import numpy as np
import os
from os.path import join as jph
import warnings

from tools.auxiliary.utils import print_and_run


from tools.definitions import root_study_rabbits
from pipeline_project.A0_main.main_controller import subjects_controller, ListSubjectsManager
# from tools.correctors.path_cleaner import clean_a_study


def clean_a_study(pfo_study):

    if not os.path.exists(pfo_study):
        raise IOError('Cannot clean unexisting studies at {}'.format(pfo_study))

    list_experiments = list(np.sort(list(set(os.listdir(pfo_study)) - {'.DS_Store'})))

    experiments_methods_list = []

    for p in list_experiments:

        pfo_experiment_p = jph(pfo_study, p)
        pfi_acquisition_method = jph(pfo_experiment_p, 'acquisition_method.txt')

        if os.path.exists(pfi_acquisition_method):

            fi_acquisition_method = open(pfi_acquisition_method, 'r')
            acquisition_method = fi_acquisition_method.read()
            fi_acquisition_method.close()

            print acquisition_method

            list_files_in_experiment = list(set(os.listdir(pfo_experiment_p)) - {'.DS_Store', 'acquisition_method.txt'})
            list_nii_gz_in_experiment = [j for j in list_files_in_experiment
                                         if j.endswith('.nii.gz')]

            num_nii = len(list_nii_gz_in_experiment)

            # conversion table for the filenames:
            if acquisition_method == 'FieldMap':
                acquisition_method = 'FM'
            elif (acquisition_method == 'FLASH' or acquisition_method == 'IntraGateFLASH') and num_nii == 3:
                acquisition_method = 'FOV'
            elif (acquisition_method == 'FLASH' or acquisition_method == 'RARE') and not num_nii == 3:
                acquisition_method = '3D'
            elif acquisition_method == 'MSME':
                acquisition_method = 'MSME'
            elif acquisition_method == 'DtiEpi':
                acquisition_method = 'DWI'

            experiments_methods_list.append(acquisition_method)

            if acquisition_method in experiments_methods_list[:-1]:
                acquisition_method += str(experiments_methods_list.count(acquisition_method))

            # fi are the files to be cleaned:
            for fi in list_files_in_experiment:

                if acquisition_method in fi:
                    print('already converted?')
                else:
                    # get filename and extension:
                    fi_split = fi.split('.')
                    fi_name = fi_split[0]
                    if len(fi_split) == 3:
                        extension = '.' + fi_split[1] + '.' + fi_split[2]
                    elif len(fi_split) == 2:
                        extension = '.' + fi_split[1]
                    else:
                        raise IOError

                    if 'subscan_1' in fi_name:
                        print_and_run('rm {}'.format(jph(pfo_experiment_p, fi)))
                    else:
                        # replace the second element (experiment number) separated between '_' by the acquisition_method
                        fi_name_components = fi_name.split('_')
                        fi_name_components[1] = acquisition_method
                        # get the stack back:
                        new_fi = ''
                        for c in fi_name_components:
                            new_fi += c + '_'

                        new_fi = new_fi[:-1].replace('_subscan_0', '')
                        new_fi += extension
                        cmd = 'mv {} {}'.format(jph(pfo_experiment_p, fi), jph(pfo_experiment_p, new_fi))
                        print_and_run(cmd)

            # rename the folder p containing the files:
            new_p = p.split('_')[0] + '_' + acquisition_method
            cmd = 'mv {} {}'.format(pfo_experiment_p, jph(pfo_study, new_p))
            print_and_run(cmd)

            cmd = 'rm {}'.format(jph(pfo_study, new_p, 'acquisition_method.txt'))
            print_and_run(cmd)

        else:
            if len(list(set(os.listdir(pfo_experiment_p)) - {'.DS_Store'})) == 0:
                # the experiment is an empty folder: get rid of it!
                print_and_run('rm -r {}'.format(pfo_experiment_p))
            else:
                # the experiment folder is not empty, but there is no name method inside. Raise a warning!
                cmd = 'No acquisition_method.txt in the folder {} - maybe already cleaned?'.format(pfo_experiment_p)
                warnings.warn(cmd)


def cleaner_converted_data_from_list(subj_list):

    print '\n\n CLEANING CONVERTER SUBJECTS {} \n'.format(subj_list)
    print subj_list

    for sj in subj_list:
        group = subjects_controller[sj][0][0]
        category = subjects_controller[sj][0][1]
        pfo_to_be_cleaned = jph(root_study_rabbits, '01_nifti', group, category, sj)
        assert os.path.exists(pfo_to_be_cleaned)

        print 'Study subject {} cleaning. \n'.format(sj)

        clean_a_study(pfo_to_be_cleaned)


if __name__ == '__main__':

    lsm = ListSubjectsManager()

    lsm.execute_PTB_ex_skull = False
    lsm.execute_PTB_ex_vivo = False
    lsm.execute_PTB_in_vivo = False
    lsm.execute_PTB_op_skull = False
    lsm.execute_ACS_ex_vivo = False

    lsm.input_subjects = ['2702', ]  # [ '2502bt1', '2503t1', '2605t1' , '2702t1', '2202t1',
    # '2205t1', '2206t1', '2502bt1']
    #  '3307', '3404']  # '2202t1', '2205t1', '2206t1' -- '2503', '2608', '2702',
    lsm.update_ls()

    print lsm.ls

    cleaner_converted_data_from_list(lsm.ls)
