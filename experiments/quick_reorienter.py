import os


# safety
safety_on = False

# path manager
here = os.path.abspath(os.path.dirname(__file__))

im = os.path.join(here, '1305_3D.nii.gz')
im_new = os.path.join(here, '1305_3D_deoriented.nii.gz')

mask = os.path.join(here, '1305_3D_roi_mask_4.nii.gz')
mask_new = os.path.join(here, '1305_3D_roi_mask_4_deoriented.nii.gz')

# from regular coordinates orientation to input DWI coordinates orientation.

# Reorient the DWI image
cmd = ''' cp {0} {1};
fslorient -deleteorient {1};
fslswapdim {1} z y -x {1};
fslorient -setqformcode 1 {1};'''.format(im, im_new)

print cmd

if not safety_on:
    os.system(cmd)



# Reorient the Mask
# Reorient the DWI image
cmd = ''' cp {0} {1};
fslorient -deleteorient {1};
fslswapdim {1} z y -x {1};
fslorient -setqformcode 1 {1};'''.format(mask, mask_new)

print cmd

if not safety_on:
    os.system(cmd)

