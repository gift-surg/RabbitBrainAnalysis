#! /usr/bin/env python

import numpy as np
import argparse
import textwrap
import os

from tools.parsers.parse_brukert_txt import parse_brukert_txt

"""
Module to parse the .txt bruker data into b_values and b_vectors.
"""


def main():

    """
    Parser from terminal
    The command:

    $ python2 parser_brukert_txt.py 0104_DWI.txt

    saves the required files in the same folder of the input file.

    With the command

    $ python2 parser_brukert_txt.py 0104_DWI.txt -o path_to_a_folder

    """

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

    parse_brukert_txt(args.input_path_txt, file_path,
                      output_type=output_type,
                      file_to_save=file_to_save,
                      num_col_to_reshape=num_col_to_reshape)

if __name__ == "__main__":
    main()


