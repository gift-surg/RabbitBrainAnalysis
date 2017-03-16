import os.path
import argparse
import numpy as np
import nibabel as nib


def main():

    # Create a parser to accept command line input arguments
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description='Merge 4D images into 5D volume')
    # Input images to compute the groupwise registration
    parser.add_argument('--first_img', dest='first_image',
                        type=str,
                        metavar='first',
                        help='First image to use in the merging',
                        required=True)
    parser.add_argument('--img', dest='input_images',
                        type=str,
                        nargs='+',
                        metavar='images',
                        help='Input images',
                        required=True)
    parser.add_argument('--out', dest='out',
                        type=str,
                        help='Filename of the output image',
                        required=True)

    # Parse the arguments
    args = parser.parse_args()

    print('The number of images to merge is ' + str(len(args.input_images) + 1))

    first_img_name = args.first_image
    first_img_nii = nib.load(first_img_name)
    first_img_data = first_img_nii.get_data()

    merged_img = np.empty([np.size(first_img_data, 0), np.size(first_img_data, 1), np.size(first_img_data, 2),
                           len(args.input_images) + 1, 2])  # number of modalities

    # Read the input images (stack all the images one after the other)
    merged_img[:, :, :, 0, :] = first_img_data
    i = 1
    for image_filename in args.input_images:
        img = nib.load(image_filename)
        data = img.get_data()
        merged_img[:, :, :, i, :] = data
        i += 1

    # merged_img_nii = nib.Nifti1Image(merged_img, first_img_nii.affine, header=first_img_nii.header)

    # if nifty1
    if first_img_nii.header['sizeof_hdr'] == 348:
        merged_img_nii = nib.Nifti1Image(merged_img, first_img_nii.affine, header=first_img_nii.header)
    # if nifty2
    elif first_img_nii.header['sizeof_hdr'] == 540:
        merged_img_nii = nib.Nifti1Image(merged_img, first_img_nii.affine, header=first_img_nii.header)
    else:
        raise IOError



    nib.save(merged_img_nii, args.out)


if __name__ == "__main__":
    main()