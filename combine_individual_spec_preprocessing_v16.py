# Load Libraries
import re, fitz
from collections import Counter
import configparser
import ast
import json
fitz.TOOLS.mupdf_display_errors(False)
config = configparser.ConfigParser()
config.read('config.ini')

# Function - Get Combine Spec Data
def combine_spec_data_to_txt(path):
    doc = fitz.open(path)

    with open('raw_text.txt', 'a', encoding="utf-8") as file:
    
        for pdf_page, page in enumerate(doc):
            left_space = 0
            page_data = ""
            text_instances = []

            # Check each format of PART 1 GENERAL
            # and Create Rect List
            for word in ast.literal_eval(config['Constants']['first_page_search_term']):
                if (page.search_for(word)):
                    text_instances.extend(page.searchFor(word))
                    left_space = text_instances[0].x0
                    break

            # Get Height and Width of each page for calculation
            width, height = page.rect.width, page.rect.height

            # For normal format PART 1 count is one on main page and
            # for other pages zero.
            # For other format(index wala) we are using location of second
            # occurence and extracting from that point.

            if(len(text_instances) == 1):
                if(page.searchFor("SECTION") and page.searchFor("DOCUMENT ")):
                    section_instances = page.searchFor("SECTION")[0]
                    document_instances = page.searchFor("DOCUMENT ")[0]

                    if(section_instances.y0 < document_instances.y0):
                        section_details = page.get_textbox(
                            fitz.Rect((left_space - 5, section_instances.y0, 0.95 * float(width), section_instances.y0 + 50)))
                        page_data = page_data + "\n" + section_details
                    else:
                        document_details = page.get_textbox(
                            fitz.Rect((left_space - 5, document_instances.y0, 0.95 * float(width), document_instances.y0 + 50)))
                        page_data = page_data + "\n" + document_details

                elif(page.searchFor("SECTION")):
                    section_instances = page.searchFor("SECTION")[0]
                    section_details = page.get_textbox(
                        fitz.Rect((left_space - 5, section_instances.y0, 0.95 * float(width), section_instances.y0 + 50)))
                    page_data = page_data + "\n" + section_details

                elif(page.searchFor("DOCUMENT ")):
                    document_instances = page.searchFor("DOCUMENT ")[0]
                    document_details = page.get_textbox(
                        fitz.Rect((left_space - 5, document_instances.y0, 0.95 * float(width), document_instances.y0 + 50)))
                    page_data = page_data + "\n" + document_details

                page_data = page_data + "\n" + page.get_textbox(
                        fitz.Rect((left_space - 5, text_instances[0].y0, width, 0.90 * float(height))))


            elif(len(text_instances) == 2):
                if(page.searchFor("SECTION") and page.searchFor("DOCUMENT ")):
                    section_instances = page.searchFor("SECTION")[0]
                    document_instances = page.searchFor("DOCUMENT ")[0]

                    if(section_instances.y0 < document_instances.y0):
                        section_details = page.get_textbox(
                            fitz.Rect((left_space - 5, section_instances.y0, 0.91 * float(width), section_instances.y0 + 50)))
                        page_data = page_data + "\n" + section_details
                    else:
                        document_details = page.get_textbox(
                            fitz.Rect((left_space - 5, document_instances.y0, 0.91 * float(width), document_instances.y0 + 50)))
                        page_data = page_data + "\n" + document_details

                elif(page.searchFor("SECTION")):
                    section_instances = page.searchFor("SECTION")[0]
                    section_details = page.get_textbox(
                        fitz.Rect((left_space - 5, section_instances.y0, 0.91 * float(width), section_instances.y0 + 50)))
                    page_data = page_data + "\n" + section_details

                elif(page.searchFor("DOCUMENT")):
                    document_instances = page.searchFor("DOCUMENT")[0]
                    document_details = page.get_textbox(
                        fitz.Rect((left_space - 5, document_instances.y0, 0.91 * float(width), document_instances.y0 + 50)))
                    page_data = page_data + "\n" + document_details

                page_data = page_data + "\n" + page.get_textbox(
                    fitz.Rect((left_space - 5, text_instances[1].y0, width, 0.90 * float(height))))

            elif(page.searchFor("END OF SECTION") or page.searchFor("END OF DOCUMENT")):
                if(page.searchFor("END OF SECTION")):
                    eod_instance = page.searchFor("END OF SECTION")[0]
                    page_data = page_data + "\n" + page.get_textbox(fitz.Rect((left_space - 5, 0.08*float(height), width, eod_instance.y1)))
                elif(page.searchFor("END OF DOCUMENT")):
                    eod_instance1 = page.searchFor("END OF DOCUMENT")[0]
                    page_data = page_data + "\n" + page.get_textbox(fitz.Rect((left_space - 5, 0.08*float(height), width, eod_instance1.y1)))
            elif(page.searchFor("TABLE OF CONTENT") or page.searchFor("END OF TABLE OF CONTENT")):
                pass
            else:
                page_data = page_data + "\n" + page.get_textbox(fitz.Rect((left_space - 5, 0.08*float(height), width, 0.90*float(height))))

            # file.write("PAGE - " + str(pdf_page) + "\n")
            if("SECTION " in page_data[0:100] and not "END OF SECTION" in page_data):
                if(any(line.startswith("SECTION") for line in page_data[0:100].splitlines())):
                    file.write("NEW SECTION STARTS HERE\n")
            elif("DOCUMENT " in page_data[0:100] and not "END OF DOCUMENT" in page_data):
                if(any(line.startswith("DOCUMENT") for line in page_data[0:100].splitlines())):
                    file.write("NEW SECTION STARTS HERE\n")
            elif("PART 1" in page_data[0:100]):
                if(any(line.startswith("PART 1") for line in page_data[0:100].splitlines())):
                    file.write("NEW SECTION STARTS HERE\n")
            elif("1.1 " in page_data[0:50]):
                file.write("NEW SECTION STARTS HERE\n")
            
            file.write(page_data + "\n")

# Function - Create Global Individual Spec Data Dictionary
def create_individual_spec_data_dict():
    str_data = open("raw_text.txt", "r", encoding = "utf-8").read()

    regex_new_section = r'NEW SECTION STARTS HERE'
    regex_start = r'(SECTION|DOCUMENT|Section)\s*\d{1,2}\s*\d{1,2}\s*\d{1,2}[i]?[.0-9A-Za-z]*'
    individual_specification = {}
    section_name_list = []
    individual_specification_start = []

    # Store Start Index of Each Section 
    for match in re.finditer(regex_new_section, str_data):
        individual_specification_start.append(match.end())
        
    first_individual_specification_starts = individual_specification_start
    individual_specification_start.append(len(str_data))
    # Create Pair List Of Start and End Index Of Each Section
    individual_specification_section_start_end = list(zip(first_individual_specification_starts, individual_specification_start[1:]))
    
    # Create Universal Dictionary to Store Each Section 
    unk_cnt = 1
    for(start, end) in individual_specification_section_start_end:
        current_section = str_data[start:end]
        if(re.search(regex_start, current_section[0:100])):
            section = re.search(regex_start, current_section).group().strip()
            section = re.sub(' +', ' ', section.strip())
            if(section not in individual_specification.keys()):
                individual_specification[section] = str_data[start:end] 
        else:
            individual_specification["UNKNOWN {}".format(unk_cnt)] = str_data[start:end]
            unk_cnt = unk_cnt + 1

    # Create JSON File for Checking Mapping Dictionary
    with open("current_spec.json", "w") as f:
        json.dump(individual_specification, f)

    return individual_specification

# combine_spec_data_to_txt("C:\\Users\\KishanT\\Downloads\\Submittal Test Zone\\Freddie Mac_Specs_Combined.pdf")