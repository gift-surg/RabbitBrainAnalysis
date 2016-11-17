import os 
from tabulate import tabulate
import nibabel as nib
import numpy as np
from tools.auxiliary.squeezer import squeeze_image_from_path


squeeze_as_well = False

path = os.path.abspath(__file__)
dir_path = os.path.split(os.path.dirname(path))[0]

print "Explored folder: "
print dir_path

list_of_infos = []
for (dirpath, dirnames, filenames) in os.walk(dir_path):
    for filename in filenames:
        if filename.endswith('.nii.gz') or filename.endswith('.nii'): 
            img = nib.load(os.path.join(dirpath, filename))
            
            resolution = np.abs(np.diagonal(img.get_affine())[:3])
            if np.isclose(resolution[0], resolution[1], rtol=0.0001) and np.isclose(resolution[1], resolution[2], rtol=0.0001):
                isotropic = True
            else:
                isotropic = False

            if squeeze_as_well:
                print '\nImage' + '/'.join(dirpath.split('/')[-3:]) + ' ' + filename
                squeeze_image_from_path(os.path.join(dirpath, filename), os.path.join(dirpath, filename))

            one_info = [filename[:4], '/'.join(dirpath.split('/')[-3:]), filename, img.shape, resolution, isotropic]
            list_of_infos += [one_info]
            

headers = ['id', 'folder', 'filename', 'shape', 'resolution', 'isotropic?']
print tabulate(list_of_infos, headers=headers)

