import os


def parse_label_descriptor_in_a_list(pfi_label_descriptor):

    if not os.path.exists(pfi_label_descriptor):
        raise IOError('Label descriptor file {} does not exist'.format(pfi_label_descriptor))

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
