import os
from definitions import pfi_excel_table_all_data
from tools.auxiliary.parse_excel_tables_and_descriptors import write_header_excel_tabs_from_record


pfi_record = '/Volumes/sebastianof/rabbits/A_data/PTB/ex_vivo/1201/records_template/1201_record.npy'


os.path.exists(pfi_record)
write_header_excel_tabs_from_record(pfi_excel_table_all_data, 'Template', pfi_record)
