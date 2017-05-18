"""
Propagate and fuse T1
"""

import os
from os.path import join as jph

from propagate_and_fuse_utils import propagate_and_fuse_all

if __name__ == '__main__':

    if not os.path.isdir('/Volumes/sebastianof/rabbits/'):
        raise IOError('Connect pantopolio!')

    controller = {}
    propagate_and_fuse_all()





