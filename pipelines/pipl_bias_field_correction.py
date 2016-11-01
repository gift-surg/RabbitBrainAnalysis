#! /usr/bin/env python

import os
from os.path import isfile, join
import argparse
import textwrap

import SimpleITK as sitk


""" main """

def check_paths(pfo_input, pfo_output):

    if pfo_input == pfo_output:
        return 'bfc_'
    else:
        return ''


def main():
    
    pipeline_usage = textwrap.dedent("""
        Usage: pipl_bias_field_correction -in [path1] -out [path2] [options]
            -in [path1] path to a folder with images of compatible format
            -out [path2] path to a folder where output will be saved
        [options]
            -prefix [string] by default the empty string, add a prefix to the output images names
                             if path1 == path2 by default is 'bfc_' to avoid overwriting.
        If it works, in path2 folder will be stored the images in path1 free of bias field.
        It uses N4BFC from the current version of SimpleItk.
    """)

    pipeline_description = textwrap.dedent("""
        If it works, in the path folder given as output will be stored the images given in the first path 
        free of bias field.
        It is based on the algorithm N4BFC from the current version of SimpleItk.
    """)

    parse = argparse.ArgumentParser(usage=pipeline_usage, description=pipeline_description, version=0.0,
                                    formatter_class=argparse.RawDescriptionHelpFormatter)
    
    # input argument:
    parse.add_argument('-in', '-i',
                       dest='input_image_folder',
                       metavar='input_image_folder',
                       type=str, )


if __name__ == "__main__":
    main()


def phase_bias_field_correction(pfo_input, pfo_output, prefix=''):
    """
    Bias field correction with N4BFC.
    Does what he can to not overwrite the input files.
    """
    if pfo_input == pfo_output:
        prefix='no_bias_' 

    n4b = sitk.N4BiasFieldCorrectionImageFilter()
    bth = sitk.BinaryThresholdImageFilter()

    for name_image in os.listdir(pfo_input):
        if name_image.endswith('.nii') or name_image.endswith('.nii.gz'):
              img = sitk.ReadImage(join(pfo_input, name_image))
              img_mask = bth.Execute(img)  # re-create instead of loading: avoid dangerous mismatches
              img_mask = -1 * (img_mask - 1)
              img_no_bias = n4b.Execute(img, img_mask)
              sitk.WriteImage(img_no_bias, join(pfo_output, prefix + name_image))



