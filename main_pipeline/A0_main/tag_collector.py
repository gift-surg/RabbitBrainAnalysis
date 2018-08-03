"""
A tag is .txt file where to each processing phase of a subject is associated a text section
reporting the phase and the date.

It contains:

Date.
Subject parameter.
Segmentation parameter.
----
NOTE: parameter files may be out of date if only parts of the pipeline are launched after changes.
Anything more robust may determine a too rigid and unmodifiable structure of the whole code.
"""
import os
import time


class TagCollector(object):
    def __init__(self, path_to_tag):
        self.pfi_tag = path_to_tag
        self.subject = os.path.dirname(path_to_tag).split('_')[0]

    def update_tag(self, pfi_param_sj, pfi_param_segm):

        assert os.path.exists(pfi_param_sj)
        assert os.path.exists(pfi_param_segm)

        if os.path.exists(self.pfi_tag):
            os.system('rm {}'.format(self.pfi_tag))

        os.system('touch {}'.format(self.pfi_tag))
        timestr = time.strftime("%Y%m%d-%H%M%S")

        with open(self.pfi_tag, 'w+') as tag_file:
            tag_file.write('Created : {}\n\n'.format(timestr))

            with open(pfi_param_sj, 'r') as param_file:
                tag_file.write(param_file.read())

            with open(pfi_param_segm, 'r') as param_file:
                tag_file.write(param_file.read())
