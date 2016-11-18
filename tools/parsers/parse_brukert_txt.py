import numpy as np
import os


def matrix_per_list_of_arrays(in_matrix, in_array):
    """
    given a matrix nxn and another array of dimension mxn, it multiplies the
    nxn matrix times each row of the second array, returning an array of the
    same dimension as in_array.
    :param in_matrix:
    :param in_array:
    :return:
    """
    return np.array([in_matrix.dot(in_array[i,:]) for i in range(in_array.shape[0])])


def parse_brukert_dwi_txt(input_path_txt,
                          output_folder,
                          output_type=np.float,
                          file_to_save=('DwDir=', 'DwEffBval=', 'DwGradVec=', 'VisuCoreDataSlope='),
                          num_col_to_reshape=(1, 1, 3, 1),
                          prefix='',
                          rotation=None,
                          normalize=True):

    for line in open(input_path_txt, 'r'):
        for j in range(len(file_to_save)):

            msg = ''
            if line.startswith(file_to_save[j]):
                in_array_as_string = line.replace(']', '[').split('[')[1]
                in_array = np.array(map(float, in_array_as_string.split(' ')), dtype=output_type)
                len_array = np.prod(in_array.shape)

                # reshape according to num_col_to_reshape
                if len_array % num_col_to_reshape[j] == 0:
                    new_shape = [len_array/num_col_to_reshape[j], num_col_to_reshape[j]]
                    in_array = in_array.reshape(new_shape)

                    # normalise if we are dealing with non-empty b-vectors:
                    if file_to_save[j] == 'DwGradVec=':
                        if normalize:
                            row_sums = in_array.sum(axis=1)
                            # comment next line if you want nan when the mean is zero instead of zero
                            row_sums[row_sums == 0.0] = 1.0
                            in_array = in_array / row_sums[:, np.newaxis]

                            #in_array = np.nan_to_num(in_array)
                            #print row_sums[:, np.newaxis]
                            msg = ' (Normalized)'
                        if rotation is not None:
                            in_array = matrix_per_list_of_arrays(rotation, in_array)
                            msg += ' oriented according to {0}'.format(rotation)


                else:
                    raise IOError('Not compatible num_col_to_reshape in input.')

                filename_path = os.path.join(output_folder, prefix + file_to_save[j][:-1] + '.txt')
                np.savetxt(filename_path, in_array, fmt='%.14f')

                msg = 'Array ' + file_to_save[j][:-1] + ' saved in ' + filename_path + msg
                print(msg)
