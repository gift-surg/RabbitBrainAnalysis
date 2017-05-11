"""
After the study is created you may want to clean it according to some specification.
These specifications are specifically related to my project.
Please edit this code according to your needs and use it separetly
"""
import numpy as np
import os
from os.path import join as jph
import warnings


def clean_a_study(pfo_study):

    if not os.path.exists(pfo_study):
        raise IOError('Cannot clean unexisting studies at {}'.format(pfo_study))

    list_experiments = list(np.sort(list(set(os.listdir(pfo_study)) - {'.DS_Store'})))

    experiments_methods_list = []

    for p in list_experiments:

        pfo_experiment_p = jph(pfo_study, p)
        pfi_name_method = jph(pfo_experiment_p, 'name_method.txt')

        if os.path.exists(pfi_name_method):

            fi_name_method = open(pfi_name_method, 'r')
            name_method = fi_name_method.read()
            fi_name_method.close()

            print name_method

            list_files_in_experiment = list(set(os.listdir(pfo_experiment_p)) - {'.DS_Store', 'name_method.txt'})
            list_nii_gz_in_experiment = [j for j in list_files_in_experiment
                                         if j.endswith('.nii.gz')]

            num_nii = len(list_nii_gz_in_experiment)

            # conversion table for the filenames:
            if name_method == 'FieldMap':
                name_method = 'FM'
            elif name_method == 'FLASH' and num_nii == 3:
                name_method = 'FOV'
            elif name_method == 'FLASH' and not num_nii == 3:
                name_method = '3D'
            elif name_method == 'MSME':
                name_method = 'MSME'
            elif name_method == 'DtiEpi':
                name_method = 'DWI'

            experiments_methods_list.append(name_method)

            if name_method in experiments_methods_list[:-1]:
                name_method += str(experiments_methods_list.count(name_method))

            # fi are the files to be cleaned:
            for fi in list_files_in_experiment:

                if name_method in fi:
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
                        os.system('rm {}'.format(jph(pfo_experiment_p, fi)))
                    else:
                        # replace the second element (experiment number) separated between '_' by the name_method
                        fi_name_components = fi_name.split('_')
                        fi_name_components[1] = name_method
                        # get the stack back:
                        new_fi = ''
                        for c in fi_name_components:
                            new_fi += c + '_'

                        new_fi = new_fi[:-1].replace('_subscan_0', '')
                        new_fi += extension
                        cmd = 'mv {} {}'.format(jph(pfo_experiment_p, fi), jph(pfo_experiment_p, new_fi))
                        os.system(cmd)

            # rename the folder p containing the files:
            new_p = p.split('_')[0] + '_' + name_method
            cmd = 'mv {} {}'.format(pfo_experiment_p, jph(pfo_study, new_p))
            os.system(cmd)

        else:
            if len(list(set(os.listdir(pfo_experiment_p)) - {'.DS_Store'})) == 0:
                # the experiment is an empty folder: get rid of it!
                os.system('rm -r {}'.format(pfo_experiment_p))
            else:
                # the experiment folder is not empty, but there is no name method inside. Raise a warning!
                cmd = 'No name_method.txt in the folder {}'.format(pfo_experiment_p)
                warnings.warn(cmd)

# root = '/Users/sebastiano/Desktop/test_PV/'
# study_out = jph(root, 'nifti')
# assert os.path.isdir(study_out)
#
# for sj in ['1702']:
#
#     clean_a_study(jph(study_out, sj))
