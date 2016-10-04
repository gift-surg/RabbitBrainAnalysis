#! /usr/bin/env python

import numpy as np
import argparse
import textwrap
import os


def main():

    ''' Parser '''

    parser = argparse.ArgumentParser(version=0.0)

    # input arguments:
    parser.add_argument('input_path_txt',
                        type=str,
                        help='txt file to parse')

    parser.add_argument("-o", "--output", 
                        action="store", 
                        dest="input_folder_where_to_save_the_output", 
                        type=str)

    # Parse the input arguments
    args = parser.parse_args()

    ''' Check the input variables '''

    # first argument
    if not os.path.isfile(args.input_path_txt):
        err_msg = 'ERROR: input file is not specified or do not exists.'
        raise IOError(err_msg) 

    # first argument extention
    if not args.input_path_txt.endswith('.txt'):
        err_msg = 'ERROR: input file is not a txt file.'
        raise IOError(err_msg) 

    # second argument
    file_path = args.input_folder_where_to_save_the_output
    if file_path is None:
        # check if the dirname is a folder or is not empyt.
        file_path = os.path.dirname(args.input_path_txt)
        if file_path == '' or not os.path.isdir(file_path):
            # if not saves in the current work directory.
            file_path = os.getcwd()

    else:
        if not os.path.isdir(args.input_folder_where_to_save_the_output):
            err_msg = 'ERROR: optional input is not a folder or do not exists.'
            raise IOError(err_msg)

    ''' 
    CORE:
    Load file into and store arrays with the name in the 
    list array_to_save  in external files.
    Corresponding number of column to reshape the output file is in the list num_col_to_reshape.
    '''
    output_type = np.float
    file_to_save = ['DwDir=', 'DwEffBval=', 'DwGradVec=', 'VisuCoreDataSlope=']
    num_col_to_reshape = [1, 1, 3, 1]
    
    for line in open(args.input_path_txt, 'r'):
        for j in range(len(file_to_save)):

            msg = ''
            if line.startswith(file_to_save[j]):
                in_array_as_string = line.replace(']', '[').split('[')[1]
                in_array = np.array(map(float, in_array_as_string.split(' ')),dtype=np.float)
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
                
                filename_path = os.path.join(file_path, file_to_save[j][:-1] + '.txt')
                np.savetxt(filename_path, in_array, fmt='%.14f')
                
                msg = 'Array ' + file_to_save[j][:-1] + ' saved in ' + filename_path + msg
                print(msg)

if __name__ == "__main__":
    main()
