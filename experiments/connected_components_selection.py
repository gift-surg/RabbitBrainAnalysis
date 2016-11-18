import os
import numpy as np
import nibabel as nib

from definitions import root_ex_vivo_template
from tools.auxiliary.utils import set_new_data


path_experiments = os.path.join(root_ex_vivo_template, 'zz_experiments')

path_subject  = os.path.join(path_experiments, '1203_3D.nii.gz')
path_ciccione = os.path.join(path_experiments, 'ciccione_1203_3D.nii.gz')

path_lesions_mask = os.path.join(path_experiments, '1203_lesions.nii.gz')

path_great_component = os.path.join(path_experiments, '1203_connected_components.nii.gz')


class Neighbour:

    def __init__(self, dimension=3, radius=1, shape='sphere'):
        self.dimension = dimension
        self.radius = radius
        self.shape = shape

    def return_neighbour(self):
        """
        A neighbour is a list of tuples, centered in 0
        :return:
        """
        possible_shapes = ['sphere', 'square']
        nn = [(0,) * self.dimension]

        if self.shape in possible_shapes:

            if self.shape == 'sphere':
                pass

            elif self.shape == 'square':
                pass

        else:
            raise IOError('Attributes shape of the class must be a string in {0}'.format(str(possible_shapes)))

        return nn


class ConnectedComponentTools:

    def __init__(self, data_input, data_output, data_foreground=None):

        self.data_input = data_input
        self.data_output = data_output
        self.data_foreground = data_foreground  # Mask of the region of interest.
        # nn = Neighbour()
        # self.neighbour = nn.return_neighbour()
        self.neighbour = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1), (-1, 0, 0), (0, -1, 0), (0, 0, -1)]

    def return_connected_components(self, save=False):

        dim_x, dim_y, dim_z = list(self.data_input.shape)
        if self.data_foreground is None:

            for i in range(dim_x):
                for j in range(dim_y):
                    for k in range(dim_z):
                        pass
        else:

            for i in range(dim_x):
                for j in range(dim_y):
                    for k in range(dim_z):
                        pass

    def take_the_biggest_connected_component(self, save=False):
        pass

    def take_the_smallest_connected_component(self, save=False):
        pass

    def take_the_biggest_connected_component_connected_to_the_background(self, save=False):
        pass

    def take_components_by_radius(self, save=False):
        pass

    def take_non_convex_components(self, save=False):
        pass

    def dilate_components(self):
        pass

    def erode_components(self):
        pass
