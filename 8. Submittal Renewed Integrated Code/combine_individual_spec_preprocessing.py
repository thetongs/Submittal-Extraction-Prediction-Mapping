# Load Libraries
import re, fitz
from collections import Counter
import configparser
import ast
fitz.TOOLS.mupdf_display_errors(False)
config = configparser.ConfigParser()
config.read('config.ini')

# Function - Get Combine Spec Data
def combine_spec_data_to_txt(path):
    doc = fitz.open(path)

    with open('raw_text.txt', 'w', encoding="utf-8") as file:
        for pdf_page, page in enumerate(doc):
            page_data = ""
            text_instances = []
            # file.write("\n" + "PAGE : " + str(pdf_page) + "\n")

            # Check each format of PART 1 GENERAL
            # and Create Rect List
            for word in ast.literal_eval(config['Constants']['first_page_search_term']):
                if (page.search_for(word)):
                    text_instances.extend(page.searchFor(word))
                    break

            # Get Height and Width of each page for calculation
            width, height = page.rect.width, page.rect.height

            # For normal format PART 1 count is one on main page and
            # for other pages zero.
            # For other format(index wala) we are using location of second
            # occurence and extracting from that point.

            if (len(text_instances) == 1):
                if (page.searchFor("SECTION") and page.searchFor("DOCUMENT")):
                    section_instances = page.searchFor("SECTION")[0]
                    document_instances = page.searchFor("DOCUMENT")[0]

                    if (section_instances.y0 < document_instances.y0):
                        section_details = page.get_textbox(
                            fitz.Rect((70, section_instances.y0, 0.95 * float(width), 0.19 * float(height))))
                        page_data = page_data + "\n" + section_details
                    else:
                        document_details = page.get_textbox(
                            fitz.Rect((70, document_instances.y0, 0.95 * float(width), 0.19 * float(height))))
                        page_data = page_data + "\n" + document_details

                elif (page.searchFor("SECTION")):
                    section_instances = page.searchFor("SECTION")[0]
                    section_details = page.get_textbox(
                        fitz.Rect((70, section_instances.y0, 0.95 * float(width), 0.19 * float(height))))
                    page_data = page_data + "\n" + section_details

                elif (page.searchFor("DOCUMENT")):
                    document_instances = page.searchFor("DOCUMENT")[0]
                    document_details = page.get_textbox(
                        fitz.Rect((70, document_instances.y0, 0.95 * float(width), 0.19 * float(height))))
                    page_data = page_data + "\n" + document_details

                page_data = page_data + "\n" + page.get_textbox(
                    fitz.Rect((70, text_instances[0].y0, width, 0.90 * float(height))))

            elif(len(text_instances) == 2):
                if (page.searchFor("SECTION") and page.searchFor("DOCUMENT")):
                    section_instances = page.searchFor("SECTION")[0]
                    document_instances = page.searchFor("DOCUMENT")[0]

                    if(section_instances.y0 < document_instances.y0):
                        section_details = page.get_textbox(
                            fitz.Rect((70, section_instances.y0, 0.91 * float(width), 0.19 * float(height))))
                        page_data = page_data + "\n" + section_details
                    else:
                        document_details = page.get_textbox(
                            fitz.Rect((70, document_instances.y0, 0.91 * float(width), 0.19 * float(height))))
                        page_data = page_data + "\n" + document_details

                elif(page.searchFor("SECTION")):
                    section_instances = page.searchFor("SECTION")[0]
                    section_details = page.get_textbox(
                        fitz.Rect((70, section_instances.y0, 0.91 * float(width), 0.19 * float(height))))
                    page_data = page_data + "\n" + section_details

                elif(page.searchFor("DOCUMENT")):
                    document_instances = page.searchFor("DOCUMENT")[0]
                    document_details = page.get_textbox(
                        fitz.Rect((70, document_instances.y0, 0.91 * float(width), 0.19 * float(height))))
                    page_data = page_data + "\n" + document_details

                page_data = page_data + "\n" + page.get_textbox(
                    fitz.Rect((70, text_instances[1].y0, width, 0.90 * float(height))))


            else:
                page_data = page_data + "\n" + page.get_textbox(
                    fitz.Rect((70, 0.08 * float(height), width, 0.90 * float(height))))

            file.write(page_data)

# Function - Create Global Individual Spec Data Dictionary
def create_individual_spec_data_dict():
    with open('raw_text.txt', "r", encoding="utf-8") as f:
        str_data = f.read()

        regex_start = r'(SECTION|DOCUMENT)\s*\d{1,2}\s*\d{1,2}\s*\d{1,2}[i]?[.0-9A-Za-z]*'
        regex_end = r'\bEND\s*OF\s*(SECTION|DOCUMENT)\b'
        individual_specification = {}
        section_name_list = []
        individual_specification_start = []

        # Store Start Index of Each Section 
        for match in re.finditer(regex_start, str_data):
            individual_specification_start.append(match.start())
            section_name_list.append(match.group())
        
        first_individual_specification_starts = individual_specification_start
        individual_specification_start.append(len(str_data))
        # Create Pair List Of Start and End Index Of Each Section
        individual_specification_section_start_end = list(zip(first_individual_specification_starts, individual_specification_start[1:]))
        
        # Create Universal Dictionary to Store Each Section 
        for section, (start, end) in list(zip(section_name_list, individual_specification_section_start_end)):
            if(section not in individual_specification.keys()):
                individual_specification[section] = str_data[start:end]
    
    # print(individual_specification["SECTION 055000"])
    return individual_specification