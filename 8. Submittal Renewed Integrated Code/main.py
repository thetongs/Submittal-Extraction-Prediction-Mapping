# Load Libraries
from text_extraction import *
from General.directory_path import *
from submittal_extraction_v14 import submital_extraction_mapping
import os, shutil


def generate(spec_path, app_path, combined_spec_choice, input_path):
    if combined_spec_choice == "yes":
        folder_create = os.path.join(app_path, "Outputs - {}".format(input_path.split('.pdf')[0]))
    else:
        folder_create = os.path.join(app_path, "Outputs - {}".format(input_path))

    if os.path.exists(folder_create):
        shutil.rmtree(folder_create)
    os.makedirs(folder_create)

    if combined_spec_choice == "no":

        os.makedirs(os.path.join(folder_create, "Highlighted PDFs"))
        os.makedirs(os.path.join(folder_create, "Highlighted Problems"))

        data_closeout = []

        print("Generating Individual Specifications..\n")

        for i in spec_path:

            data_insert = []
            get_combined_spec_data(i)
            specs = split_combined_spec()
            # mapping = get_section_mapping_from_pdf(specs)

            for section, str_data in specs.items():
                try:
                    data, flag, filename = PartFlag(str_data)
                    # calling submittal extraction
                    submital_extraction_mapping(data, flag, filename)
                    parts_string = PartsDivisionString(str_data)
                    parts_list = PartsDivisionList(parts_string)
                    headings = SectionHeading(parts_string)
                    data = sub_section(parts_list, headings)

                except Exception as e:
                    print(Fore.RED + "{}".format(section) + Fore.RESET)
                    continue

                descriptions = [(desc[2], desc[4], desc[5], desc[6]) for desc in data_insert]
                # Show Sections On Terminal
                print(Fore.GREEN + "{}".format(section) + Fore.RESET)

        try:
            os.remove(os.path.join(app_path, 'raw_text.txt'))
        except Exception as e:
            pass

    else:

        data_insert = []
        print("\nGenerating Combined Specification..\n")
        get_combined_spec_data(spec_path)
        print("\n")
        specs = split_combined_spec()
        header_footer_data = headerfooterlines()

        for section, str_data in specs.items():
            try:
                data, flag, filename, hf_list_data, spec_name = PartFlag(str_data, header_footer_data, input_path)
                # Function Call - Submittal Extraction Individual
                submital_extraction_mapping(data, flag, filename, spec_name.split('.pdf')[0])
                
                parts_string = PartsDivisionString(str_data)
                parts_list = PartsDivisionList(parts_string)
                headings = SectionHeading(parts_string)
                data = sub_section(parts_list, headings)

            except Exception as e:
                print(Fore.RED + "{}".format(section) + Fore.RESET)
                continue

            # Show Sections On Terminal
            print(Fore.GREEN + "{}".format(section) + Fore.RESET)
        try:
            os.remove(os.path.join(app_path, 'raw_text.txt'))
        except Exception as e:
            pass


if __name__ == "__main__":
    try:
        spec_path, app_path, combined_spec_choice, input_path = process_argument_path()
        data_found = generate(spec_path, app_path, combined_spec_choice, input_path)
        print(Style.RESET_ALL)
        print(Back.BLUE + "\n\nFINISHED SUCCESSFULLY" + Style.RESET_ALL)
        input()
    except Exception as e:
        print(e)
        input("Some Error Occured.")
