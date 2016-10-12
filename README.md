# Frau Brukert
A handful of functions in python and matlab to parse Brukert raw data P.V. 5 to nifti format.


To use parser_brukert_txt.py run (tested Python2.7.1):

    $ python2 parser_brukert_txt.py 0104_DWI.txt 

It saves the required files in the same folder of the input file.

The command

    $ python2 parser_brukert_txt.py 0104_DWI.txt -o path_to_a_folder

It saves the required files in the specified folder if exists. 