import numpy as np
import os


def parse_brukert_txt(input_path_txt,
                      output_folder,
                      output_type=np.float,
                      file_to_save=('DwDir=', 'DwEffBval=', 'DwGradVec=', 'VisuCoreDataSlope='),
                      num_col_to_reshape=(1, 1, 3, 1)):

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
                        row_sums = in_array.sum(axis=1)
                        # comment next line if you want nan when the mean is zero instead of zero
                        row_sums[row_sums == 0.0] = 1.0
                        in_array = in_array / row_sums[:, np.newaxis]

                        #in_array = np.nan_to_num(in_array)
                        #print row_sums[:, np.newaxis]
                        msg = ' (Normalized)'
                else:
                    raise IOError('Not compatible num_col_to_reshape in input.')

                filename_path = os.path.join(output_folder, file_to_save[j][:-1] + '.txt')
                np.savetxt(filename_path, in_array, fmt='%.14f')

                msg = 'Array ' + file_to_save[j][:-1] + ' saved in ' + filename_path + msg
                print(msg)
