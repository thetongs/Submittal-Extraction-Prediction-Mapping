import ast
import re, fitz
from collections import Counter
import colorama
from General.directory_path import *
colorama.init()
from colorama import Fore, Back, Style
# import fitz

import configparser

import ast

fitz.TOOLS.mupdf_display_errors(False)

def get_combined_spec_data(path):
    doc = fitz.open(path)
    config = configparser.ConfigParser()

    config.read('config.ini')
    
    with open('raw_text.txt', 'w', encoding="utf-8") as file:
        for pdf_page, page in enumerate(doc):
            page_data = ""
            text_instances = []

            file.write("\n" + "PAGE : " + str(pdf_page) + "\n")
            # Check each format of PART 1 GENERAL
            # and Create Rect List
            for word in ast.literal_eval(config['Constants']['first_page_search_term']):
                if (page.search_for(word)):
                    text_instances.extend(page.searchFor(word))
                    break

            # Get Height and Width of each page for calculation
            width, height = page.rect.width, page.rect.height

            # print(len(text_instances))

            # For normal format PART 1 count is one on main page and
            # for other pages zero.
            # For other format(index wala) we are using location of second
            # occurence and extracting from that point.

            if (len(text_instances) == 1):
                if (page.searchFor("SECTION") and page.searchFor("DOCUMENT")):
                    # print("Both")
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

                    # print(section_details)

                elif (page.searchFor("SECTION")):
                    # print("SECTION")
                    section_instances = page.searchFor("SECTION")[0]
                    section_details = page.get_textbox(
                        fitz.Rect((70, section_instances.y0, 0.95 * float(width), 0.19 * float(height))))
                    page_data = page_data + "\n" + section_details

                    # print(section_details)

                elif (page.searchFor("DOCUMENT")):
                    # print("DOCUMENT")
                    document_instances = page.searchFor("DOCUMENT")[0]
                    document_details = page.get_textbox(
                        fitz.Rect((70, document_instances.y0, 0.95 * float(width), 0.19 * float(height))))
                    page_data = page_data + "\n" + document_details

                    print(document_details)

                page_data = page_data + "\n" + page.get_textbox(
                    fitz.Rect((70, text_instances[0].y0, width, 0.90 * float(height))))

                # print(page_data)
                # break

            elif (len(text_instances) == 2):
                if (page.searchFor("SECTION") and page.searchFor("DOCUMENT")):
                    section_instances = page.searchFor("SECTION")[0]
                    document_instances = page.searchFor("DOCUMENT")[0]

                    if (section_instances.y0 < document_instances.y0):
                        section_details = page.get_textbox(
                            fitz.Rect((70, section_instances.y0, 0.91 * float(width), 0.19 * float(height))))
                        page_data = page_data + "\n" + section_details
                    else:
                        document_details = page.get_textbox(
                            fitz.Rect((70, document_instances.y0, 0.91 * float(width), 0.19 * float(height))))
                        page_data = page_data + "\n" + document_details

                elif (page.searchFor("SECTION")):
                    section_instances = page.searchFor("SECTION")[0]
                    section_details = page.get_textbox(
                        fitz.Rect((70, section_instances.y0, 0.91 * float(width), 0.19 * float(height))))
                    page_data = page_data + "\n" + section_details

                elif (page.searchFor("DOCUMENT")):
                    document_instances = page.searchFor("DOCUMENT")[0]
                    document_details = page.get_textbox(
                        fitz.Rect((70, document_instances.y0, 0.91 * float(width), 0.19 * float(height))))
                    page_data = page_data + "\n" + document_details

                page_data = page_data + "\n" + page.get_textbox(
                    fitz.Rect((70, text_instances[1].y0, width, 0.90 * float(height))))


            else:
                # print("Here")
                page_data = page_data + "\n" + page.get_textbox(
                    fitz.Rect((70, 0.08 * float(height), width, 0.90 * float(height))))
                # print(page_data)
            file.write(page_data)



def individual_spec():
    with open('raw_text.txt', "r", encoding="utf-8") as f:
        list_data = f.readlines()
        str_data = " ".join(list_data)

    return str_data


def split_combined_spec():
    # all_data = ''
    with open('raw_text.txt', "r", encoding="utf-8") as f:
        list_data = f.readlines()
        str_data = " ".join(list_data)

    regex_start = r'(SECTION|DOCUMENT)\s*\d{1,2}\s*\d{1,2}\s*\d{1,2}[i]?[.0-9A-Za-z]*'
    regex_end = r'\bEND\s*OF\s*(SECTION|DOCUMENT)\b'
    hf_regex_start_2 = r'PAGE : '
    hf_regex_start_1 = r'\bEND\s*OF\s*(SECTION|DOCUMENT|TABLE)\b'
    hf_regex_end = r'(SECTION|DOCUMENT)\s*\d{1,2}\s*\d{1,2}\s*\d{1,2}[i]?[.0-9A-Za-z]*'

    individual_specification = {}

    try:
        while str_data:
            section_name = re.search(regex_start, str_data).group()

            if section_name not in individual_specification.keys():

                # hf_start = re.search(hf_regex_start_1, str_data).start()
                # hf_end = re.search(hf_regex_end, str_data).end()
                # if hf_start > hf_end:
                #     hf_start = re.search(hf_regex_start_2, str_data).start()
                #     hf_end = re.search(hf_regex_end, str_data).end()
                #     hf_data = str_data[hf_start:hf_end]
                # else:
                #     hf_data = str_data[hf_start:hf_end]

                section_start = re.search(regex_start, str_data).start()
                section_end = re.search(regex_end, str_data).end()
                if section_start > section_end:
                    str_data = str_data[section_end:]
                    section_start = re.search(regex_start, str_data).start()
                    section_end = re.search(regex_end, str_data).end()
                    str_data_spec = str_data[section_start:section_end]

                else:
                    str_data_spec = str_data[section_start:section_end]

                section = True

                check_section = str_data_spec[1:]
                inside_section = re.search(regex_start, check_section)

                if inside_section:

                    first_part = str_data_spec[:inside_section.start()]
                    second_part = str_data_spec[inside_section.start():]

                    if re.search(r'PART\s*1', second_part[:100]) or re.search(r'TABLE OF CONTENT', second_part[:100]):
                        # print(second_part)
                        section = False
                        individual_specification[re.search(regex_start, first_part).group()] = first_part
                        individual_specification[re.search(regex_start, second_part).group()] = second_part

                if section is True:
                    individual_specification[section_name] = str_data_spec
                    # individual_specification[section_name] = hf_data
                    # individual_specification['hf_lines'] = hf_data

                str_data = str_data[section_end:]


            else:
                clip_section = re.search(regex_start, str_data).end()
                str_data = str_data[clip_section:]

    except Exception as e:
        pass

    return individual_specification


def headerfooterlines():
    with open('raw_text.txt', "r", encoding="utf-8") as f:
        list_data = f.readlines()
        str_data = " ".join(list_data)

    regex_start = r'(SECTION|DOCUMENT)\s*\d{1,2}\s*\d{1,2}\s*\d{1,2}[i]?[.0-9A-Za-z]*'
    regex_end = r'\bEND\s*OF\s*(SECTION|DOCUMENT)\b'
    hf_regex_start_2 = r'PAGE : '
    hf_regex_start_1 = r'\bEND\s*OF\s*(SECTION|DOCUMENT|TABLE)\b'
    hf_regex_end = r'(SECTION|DOCUMENT)\s*\d{1,2}\s*\d{1,2}\s*\d{1,2}[i]?[.0-9A-Za-z]*'

    individual_specification = {}
    hf_spec = {}

    try:
        while str_data:
            section_name = re.search(regex_start, str_data).group()

            if section_name not in hf_spec.keys():

                hf_start = re.search(hf_regex_start_1, str_data).start()
                hf_end = re.search(hf_regex_end, str_data).end()
                if hf_start > hf_end:
                    hf_start = re.search(hf_regex_start_2, str_data).start()
                    hf_end = re.search(hf_regex_end, str_data).end()
                    hf_data = str_data[hf_start:hf_end]

                else:
                    hf_data = str_data[hf_start:hf_end]

                section_start = re.search(regex_start, str_data).start()
                section_end = re.search(regex_end, str_data).end()
                if section_start > section_end:
                    str_data = str_data[section_end:]
                    section_start = re.search(regex_start, str_data).start()
                    section_end = re.search(regex_end, str_data).end()
                    str_data_spec = str_data[section_start:section_end]

                else:
                    str_data_spec = str_data[section_start:section_end]

                section = True

                check_section = str_data_spec[1:]
                inside_section = re.search(regex_start, check_section)

                if inside_section:

                    first_part = str_data_spec[:inside_section.start()]
                    second_part = str_data_spec[inside_section.start():]

                    if re.search(r'PART\s*1', second_part[:100]) or re.search(r'TABLE OF CONTENT', second_part[:100]):
                        # print(second_part)
                        section = False
                        individual_specification[re.search(regex_start, first_part).group()] = first_part
                        individual_specification[re.search(regex_start, second_part).group()] = second_part

                if section is True:
                    individual_specification[section_name] = str_data_spec
                    hf_spec[section_name] = hf_data

                str_data = str_data[section_end:]


            else:
                clip_section = re.search(regex_start, str_data).end()
                str_data = str_data[clip_section:]

    except Exception as e:
        pass

    return hf_spec


def PartFlag(str_data, hf_spec, input_path):
    section_name_regex = r'(SECTION|DOCUMENT)\s*\d{1,2}\s*\d{1,2}\s*\d{1,2}[i]?[.0-9A-Za-z]*'
    section_name = re.search(section_name_regex, str_data).group()
    spec_name = input_path
    # print(type(hf_spec))
    extra_lines = []
    parts = re.findall("PART\s?[1-3]", str_data)
    if parts:
        parts_flag = True
    else:
        parts_flag = False

    for hf_key, hf_value in hf_spec.items():
        if section_name == hf_key:
            extra_lines = hf_value.splitlines()

            final_index = [index for index, x in enumerate(extra_lines) if re.search('PAGE', x)]
            extra_lines = extra_lines[final_index[-1]:]
            extra_lines = [item for item in extra_lines if (len(str(item).strip()) != 0)]
    
    return str_data, parts_flag, section_name, extra_lines, spec_name


def PartsDivisionString(str_data):
    parts = re.findall("PART\s?[1-3]", str_data)

    if len(parts) == 3:

        part1_start = re.search(parts[0], str_data).start()
        part2_start = re.search(parts[1], str_data).start()
        part3_start = re.search(parts[2], str_data).start()

    elif len(parts) == 4:

        n = [k for k, v in Counter(parts).items() if v > 1]
        k = [k for k, v in Counter(parts).items() if v == 1]

        for i in k:

            if "1" in i:
                part1_start = re.search(parts[0], str_data).start()
            elif "2" in i:
                part2_start = re.search(parts[1], str_data).start()
            elif "3" in i:
                part3_start = re.search(parts[2], str_data).start()

        for i in n:

            number = i[-1]

            if number == "1":
                for m in re.finditer(i, str_data):
                    small_part = str_data[m.end():m.end() + 30]
                    if re.search(r"\b%s.\d{1,2}\b" % number, small_part):
                        part1_start = m.start()

            elif number == "2":
                for m in re.finditer(i, str_data):
                    small_part = str_data[m.end():m.end() + 30]
                    if re.search(r"\b%s.\d{1,2}\b" % number, small_part):
                        part2_start = m.start()
            elif number == "3":
                for m in re.finditer(i, str_data):
                    small_part = str_data[m.end():m.end() + 30]
                    if re.search(r"\b%s.\d{1,2}\b" % number, small_part):
                        part3_start = m.start()
    else:

        if "1" in parts[0] and "2" in parts[1]:
            part1_start = re.search(parts[0], str_data).start()
            part2_start = re.search(parts[1], str_data).start()

            part1 = str_data[part1_start:part2_start]
            part2 = str_data[part2_start:]
            part3 = ""

        elif "2" in parts[0] and "3" in parts[1]:
            part2_start = re.search(parts[0], str_data).start()
            part3_start = re.search(parts[1], str_data).start()

            part1 = ""
            part2 = str_data[part2_start:part3_start]
            part3 = str_data[part3_start:]

        elif "1" in parts[0] and "3" in parts[1]:
            part1_start = re.search(parts[0], str_data).start()
            part3_start = re.search(parts[1], str_data).start()

            part1 = str_data[part1_start:part3_start]
            part2 = ""
            part3 = str_data[part3_start:]

        return [part1, part2, part3]

    part1 = str_data[part1_start:part2_start]
    part2 = str_data[part2_start:part3_start]
    part3 = str_data[part3_start:]
    # print(part1)
    return [part1, part2, part3]


def PartsDivisionList(list_data):
    part1_list, part2_list, part3_list = list_data

    part1_list = part1_list.splitlines(True)
    part2_list = part2_list.splitlines(True)
    part3_list = part3_list.splitlines(True)

    # print(part1_list)
    return [part1_list, part2_list, part3_list]


def SectionHeading(parts):
    part1, part2, part3 = parts
    # print(part1)
    section_heading = r"\b[123][.]\d{1,2}[\s]*[A-Za-z-\t ():),/.&']+\b"

    part1_section_ = re.findall(section_heading, part1, re.M)
    part2_section_ = re.findall(section_heading, part2, re.M)
    part3_section_ = re.findall(section_heading, part3, re.M)

    part1_section = [i for i in part1_section_ if i.isupper() and ("\n" in i or " " in i)]
    part2_section = [i for i in part2_section_ if i.isupper() and ("\n" in i or " " in i)]
    part3_section = [i for i in part3_section_ if i.isupper() and ("\n" in i or " " in i)]

    return [part1_section, part2_section, part3_section]


def sub_section(three_parts, headings):
    part1_list, part2_list, part3_list = three_parts
    part1_heading_full, part2_heading_full, part3_heading_full = headings

    part1_heading, part2_heading, part3_heading = [], [], []

    for heads in part1_heading_full:
        part1_heading.append(heads.splitlines(True)[0])
    for heads in part2_heading_full:
        part2_heading.append(heads.splitlines(True)[0])
    for heads in part3_heading_full:
        part3_heading.append(heads.splitlines(True)[0])

    main = []
    for sub_list, sub_heading in zip([part1_list, part2_list, part3_list],
                                     [part1_heading, part2_heading, part3_heading]):

        checks = {i: False for i in sub_heading}
        l1 = []

        for new_search in sub_heading:
            for i, ok in enumerate(sub_list):
                if new_search in ok.lstrip() and checks[new_search] is not True:
                    # print(new_search)
                    checks[new_search] = True
                    l1.append(i)

        l1.append(len(sub_list))
        # for i in l1:
        #     sub_list[i]
        # print(l1)
        master = {}
        for i in range(len(l1)):
            try:
                individual_list = sub_list[l1[i]:l1[i + 1]]
                # print(individual_list)
                section_found = False
                in_section = False
                result = {}
                items = []
                current_section = ''
                for s in individual_list:

                    if not s.strip():
                        continue

                    if re.match(r'[A-Z]\s*\.\s*', s.lstrip()):
                        # print("here")
                        in_section = True
                        if current_section:  # not the first time found
                            # print("current section")
                            result[current_section] = items
                            items = []
                        current_section = s.rstrip()
                        section_found = True
                    elif section_found and re.match(r'\d{1,2}\s*\.', s.lstrip()):
                        # print("number found")
                        in_section = False
                        items.append(s.rstrip())
                    elif section_found:
                        if in_section:
                            current_section += f' {s.rstrip()}'
                        else:
                            if items:
                                items[-1] += f' {s.rstrip()}'

                if current_section:
                    try:
                        result[current_section] = items
                        full_section = "".join(individual_list)
                        find_heading = re.search(r'\s*A.\s*\n', full_section).start()
                        heading = full_section[:find_heading].replace('\n', "").strip()

                        master[heading] = result

                    except Exception as e:
                        continue

            except IndexError as e:
                pass
        # print(master.keys())
        main.append(master)

    return main
