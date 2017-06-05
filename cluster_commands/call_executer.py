import argparse
from pipeline_project.A0_main.main_executer import main_runner


def main():

    parser = argparse.ArgumentParser()

    # pfo_study_bruker_input
    parser.add_argument('-i',
                        dest='str_input',
                        type=str,
                        required=True)

    args = parser.parse_args()

    main_runner([args.str_input, ])

main()
