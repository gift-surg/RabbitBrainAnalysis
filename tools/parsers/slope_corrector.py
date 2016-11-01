#! /usr/bin/env python

import numpy as np
import argparse
import textwrap
import os
import nibabel as nib
from utils import set_new_data


def main():

    ''' Parser '''

    script_description = textwrap.dedent("""
    To have memory-smaller DWI images, the format of each image is kept to int16. 
    To have the actual float value obtained at the acquisition, each DWI slice 
    (5th dimensional index for nifti-format) must be multiplied for a number
    (called image scale or data slope) stored in a txt file (VisuCoreDataSlope.txt 
    in Brukert after parsing).

    This script take as input the DWI image, the file that should accompanies each DWI image and
    provides the DWI with the actual DWI with the float values.  
    """)

    parser = argparse.ArgumentParser(version=0.0, description=script_description)

    # input arguments:
    parser.add_argument('input_image',
                        type=str,
                        help='DWI image file (nifti).')

    parser.add_argument('input_scaling_factors',
                        type=str,
                        help='Image scale array - 1d column of the size of the DWI directions (txt).')

    parser.add_argument("-o", "--output", 
                        action="store", 
                        dest="output_path_filename", 
                        help='output folder/filename or filename where to store the resulting image.',
                        type=str)

    # Parse the input arguments
    args = parser.parse_args()

    ''' Check the input variables '''

    # First argument existence
    if not os.path.isfile(args.input_image):
        err_msg = 'ERROR: input image is not specified or do not exists.'
        raise IOError(err_msg) 

    # First argument extention
    if not (args.input_image.endswith('.nii') or args.input_image.endswith('.nii.gz')):
        err_msg = 'ERROR: input file is not in nifti format (.nii or .nii.gz).'
        raise IOError(err_msg) 

    # Second argument existence
    if not os.path.isfile(args.input_scaling_factors):
        err_msg = 'ERROR: input scaling factors is not specified or do not exists.'
        raise IOError(err_msg) 

    # Second argument extention 
    if not args.input_scaling_factors.endswith('.txt'):
        err_msg = 'ERROR: input scaling factors is not in txt format.'
        raise IOError(err_msg) 

    # Third argument
    if args.output_path_filename is not None:
        output_path = os.path.dirname(args.output_path_filename)
        output_filename = os.path.basename(args.output_path_filename)
        
        # check if the path has a valid folder path or set to the current if not exists.
        if output_path == '':
            output_path = os.getcwd() 
        elif not os.path.isdir(output_path):    
            err_msg = 'ERROR: output folder specified is not a folder or does not exists.'
            raise IOError(err_msg)
        
        # check if the name is a nifti file
        if not (output_filename.endswith('.nii') or output_filename.endswith('.nii.gz')):
            err_msg = 'ERROR: output filename is not in nifti format (.nii or .nii.gz).'
            raise IOError(err_msg) 

    # If third argument is not defined, save it in the same folder with a similar name as the input_file
    else:
        output_path = os.path.dirname(os.path.realpath(__file__))
        output_filename = os.path.basename(args.input_image).split('.')[0] + '_scaled.nii.gz'

    ''' CORE '''

    slopes = np.loadtxt(args.input_scaling_factors).astype(np.float64)
    im_input = nib.load(args.input_image)
    im_data = im_input.get_data().astype(np.float64)
    num_directions = len(slopes)
    
    if not (im_data.shape[3] == num_directions or im_data.shape[4] == num_directions):
        err_msg = 'ERROR: Dimension of the given image scale not coherent with the given image.'
        raise IOError(err_msg)
    
    for j in range(num_directions):
        im_data[...,j] *=  slopes[j]

    nib.save(set_new_data(im_input, im_data), os.path.join(output_path, output_filename))
    
    msg = 'Scaled image saved in ' + os.path.join(output_path, output_filename)
    print(msg)


if __name__ == "__main__":
    main()
