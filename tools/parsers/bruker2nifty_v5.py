import os
import sys
import numpy as np
import nibabel as nib


def indian_file_parser(s, sh=None):
    """
    An indian file is a string whose shape needs to be changed, according to its content.
    It can be provided with an additional provided shape.
    This function transform the indian file in an hopefully meaningful data structure,
    according to the information that can be parsed in the file:
    A - list of vectors
    B - list of numbers, transformed as a np.ndarray, or single number stored as a single float
    C - list of words separated by <>
    D - everything else becomes a string.

    :param s: string indian file
    :param sh: shape related
    :return: parsed indian file of adequate output.
    """

    s = s.strip()  # removes initial and final spaces.

    if ('(' in s) and (')' in s):
        s = s[1:-1]  # removes initial and final ( )
        a = ['(' + v + ')' for v in s.split(') (')]
    elif s.replace('-', '').replace('.', '').replace(' ', '').replace('e', '').isdigit():
        if ' ' in s:
            a = np.array([float(x) for x in s.split()])
            if sh is not None:
                a = a.reshape(sh)
        else:
            a = float(s)
    elif ('<' in s) and ('>' in s):
        s = s[1:-1]  # removes initial and final < >
        a = [v for v in s.split('> <')]
    else:
        a = s[:]

    return a


def get_bruker_version(data_path):

    if not os.path.isdir(data_path):
        raise IOError('Input folder does not exists.')

    f = open(os.path.join(data_path, 'AdjStatePerStudy'), 'r')
    first_line = f.readline()

    if 'ParaVision' in first_line:
        version = first_line.split('ParaVision')[1].strip()
    else:
        raise IOError('Version not detectable')

    return version


def var_name_clean(line_in):
    """
    Removes #, $ and PVM_ from line_in
    :param line_in: input string
    :return: output string cleaned from #, $ and PVM_
    """
    line_out = line_in.replace('#', '').replace('$', '').replace('PVM_', '').strip()
    return line_out


def bruker_read_files(param_file, data_path, reco_num=1):
    """
    Based on BMS Matlab code, available at CABI UCL.

    Reads parameters files of from Bruckert raw data imaging format.
    It parses the files 'acqp' 'method' and 'reco'
    :param param_file: file parameter.
    :param data_path: path to data.
    :param reco_num: number of the folder where reco is stored.
    :return: dict_info dictionary with the parsed informations from the input file.
    """

    if param_file.lower() == 'reco':
        f = open(os.path.join(data_path, 'pdata', str(reco_num), 'reco'), 'r')
    elif param_file.lower() == 'acqp':
        f = open(os.path.join(data_path, 'acqp'), 'r')
    elif param_file.lower() == 'method':
        f = open(os.path.join(data_path, 'method'), 'r')
    else:
        raise IOError('param_file should be the string reco, acqp or method')

    dict_info = {}
    lines = f.readlines()

    for line_num in range(len(lines)):
        '''
        Relevant information are in the lines with '##'.
        A: for the parameters that have arrays values specified between (), with values in the next line.
           Values in the next line can be parsed in lists or np.ndarray, if they contains also characters
           or only numbers.
        '''

        line_in = lines[line_num]

        if '##' in line_in:

            # A:
            if ('$' in line_in) and ('(' in line_in):

                splitted_line = line_in.split('=')
                # name of the variable contained in the row, and shape:
                var_name = var_name_clean(splitted_line[0][3:])
                sh = splitted_line[1].replace('(', '').replace(')', '').replace('\n', '').strip()

                done = False
                indian_file = ''
                pos = line_num

                if '.' in sh:
                    # method.ExcPulse has not integer values as argument.
                    # in this case add the value to the argument
                    indian_file += sh
                else:
                    sh = [int(num) for num in sh.split(',')]

                while not done:

                    pos += 1

                    # collect the indian file: info related to the same variables that can appears on multiple rows.
                    line_to_explore = lines[pos]  # tell seek does not work in the line iterators...

                    if ('##' in line_to_explore) or ('$$' in line_to_explore):
                        # indian file is over
                        done = True

                    else:
                        # we store the rows in the indian file all in the same string.
                        indian_file += line_to_explore.replace('\n', '').strip() + ' '

                dict_info[var_name] = indian_file_parser(indian_file, sh)

            if ('$' in line_in) and ('(' not in line_in):
                splitted_line = line_in.split('=')
                var_name = var_name_clean(splitted_line[0][3:])
                indian_file = splitted_line[1]

                dict_info[var_name] = indian_file_parser(indian_file)

            if ('$' not in line_in) and ('(' in line_in):

                splitted_line = line_in.split('=')
                var_name = var_name_clean(splitted_line[0][2:])

                done = False
                indian_file = splitted_line[1].strip() + ' '
                pos = line_num

                while not done:

                    pos += 1

                    # collect the indian file: info related to the same variables that can appears on multiple rows.
                    line_to_explore = lines[pos]  # tell seek does not work in the line iterators...

                    if ('##' in line_to_explore) or ('$$' in line_to_explore):
                        # indian file is over
                        done = True

                    else:
                        # we store the rows in the indian file all in the same string.
                        indian_file += line_to_explore.replace('\n', '').strip() + ' '

                dict_info[var_name] = indian_file_parser(indian_file)

            if ('$' not in line_in) and ('(' not in line_in):
                splitted_line = line_in.split('=')
                var_name = var_name_clean(splitted_line[0])
                indian_file = splitted_line[1].replace('=', '').strip()
                dict_info[var_name] = indian_file_parser(indian_file)

    return dict_info


def bruker_data_parser(data_path):
    # Get information from method file
    acqp = bruker_read_files('acqp', data_path)
    method = bruker_read_files('method', data_path)
    reco = bruker_read_files('reco', data_path)

    # get dimensions
    if method['SpatDimEnum'] == '2D':
        dimensions = [0] * 3
        dimensions[0:2] = reco['RECO_size'][0:2]
        dimensions[2] = acqp['NSLICES']
    elif method['SpatDimEnum'] == '3D':
        dimensions = method['Matrix'][0:3]
    else:
        raise IOError('Unknown imaging acquisition dimensionality.')

    dimensions = [int(k) for k in dimensions] + [int(acqp['NR'])]

    # get datatype
    if reco['RECO_wordtype'] == '_32BIT_SGN_INT':
        dt = np.int32
    elif reco['RECO_wordtype'] == '_16BIT_SGN_INT':
        dt = np.int16
    elif reco['RECO_wordtype'] == '_8BIT_UNSGN_INT':
        dt = np.uint8
    elif reco['RECO_wordtype'] == '_32BIT_FLOAT':
        dt = np.float32
    else:
        raise IOError('Unknown data type.')

    # get data endian_nes - # default is big!!
    if reco['RECO_byte_order'] == 'littleEndian':
        data_endian_ness = 'little'
    elif reco['RECO_byte_order'] == 'bigEndian':
        data_endian_ness = 'big'
    else:
        data_endian_ness = 'big'

    # get system endian_nes
    system_endian_nes = sys.byteorder

    # get image data from the 2d-seq file
    im = np.fromfile(os.path.join(data_path, 'pdata/1/2dseq'), dtype=dt)

    if not data_endian_ness == system_endian_nes:
        im.byteswap(True)

    # reshape the array according to the dimension: - See Bruckert manual and note that matlab uses the Fortran ordering
    # while matlab uses the 'C' ordering convention.
    if method['SpatDimEnum'] == '2D':
        im = im.reshape(dimensions, order='F')
    elif method['SpatDimEnum'] == '3D':
        im = im.reshape([dimensions[1], dimensions[0], dimensions[2], dimensions[3]], order='F')
        im = np.transpose(im, axes=[1, 0, 2, 3])

    # From dictionary of frozenset to have them as an immutable:
    # to read them as dictionaries they must be casted to a new dictionary with dict(info['acqp'])
    info = {'acqp': acqp, 'method': method, 'reco': reco}

    return [info, im]  # future header information and image values


def bruker2nifti(input_data_path, output_data_path):
    """
    Conversion method, from bruckert row-data to nifti.

    Preliminary version - essential data only!

    :param input_data_path: path to the Bruckert data folder structure
    :param output_data_path: folder where to store the converted image
    :return:
    """

    if not os.path.isdir(input_data_path):
        raise IOError('Input folder does not exists.')
    if not os.path.isdir(output_data_path):
        raise IOError('Output folder does not exists.')

    try:
        [info, im] = bruker_data_parser(input_data_path)
    except:
        raise IOError('Input folder does not contain any Bruckert format image.')

    acqp = info['acqp']
    method = info['method']
    reco = info['reco']

    pt, in_name = os.path.split(input_data_path)

    nifti_im = nib.Nifti1Image(im, np.eye(4))  # For the moment only the data are parsed.

    nib.save(nifti_im, os.path.join(output_data_path, in_name + '.nii.gz'))
