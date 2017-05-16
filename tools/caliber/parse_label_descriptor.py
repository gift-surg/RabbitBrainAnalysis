import os


def parse_label_descriptor_in_a_list(pfi_label_descriptor):
    """
    parse the ITK-Snap into a list.
    :param pfi_label_descriptor: path to file to label descriptor.
    :return: list of lists, where each sublist contains the information of each line.
    """
    if not os.path.exists(pfi_label_descriptor):
        msg = 'Label descriptor file {} does not exist'.format(pfi_label_descriptor)
        raise IOError(msg)

    f = open(pfi_label_descriptor, 'r')

    label_descriptor_list = []
    lines = f.readlines()

    for l in lines:
        if not l.startswith('#'):

            parsed_line = [j.strip() for j in l.split('  ') if not j == '']
            for position_element, element in enumerate(parsed_line):
                if element.isdigit():
                    parsed_line[position_element] = int(element)
                if element.startswith('"') or element.endswith('"'):
                    parsed_line[position_element] = element.replace('"', '')

            parsed_line.insert(1, parsed_line[-1])

            label_descriptor_list.append(parsed_line[:-1])

    return label_descriptor_list


def parse_executive_project_in_a_list(pfi_executive_project):
    """
    An executive project is a text file where each row is like
    name_of_the_region & id1 & id2 & id3
    Lines starting with # are considered comments and not parsed.

    :return:
    """
    if not os.path.exists(pfi_executive_project):
        msg = 'Input executive project {} does not exists'.format(pfi_executive_project)
        raise IOError(msg)

    f = open(pfi_executive_project, 'r')

