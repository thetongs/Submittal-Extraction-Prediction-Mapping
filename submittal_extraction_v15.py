# Load Libraries
import spacy
import itertools
import json
import re
from os import path
import csv
import pickle
import pandas as pd
import numpy as np
import string
import logging
import warnings
from pathlib import Path
warnings.filterwarnings("ignore")
import os
logger = logging.getLogger('submittal_ui_v14.py')

# Find Section Name
# Use Custom NER to Extract
def custom_ner_section_name(section_details):
    nlp2 = spacy.load("Spacy Custom NER Dump/")

    flag1, flag2 = False, False
    section_data = nlp2(section_details)
    for sent in section_data.ents:
        if(sent.label_ == 'section_name'):
            spec_name = str(sent)
            flag1 = True
    
    if(not flag1):
        spec_name = "Not Found"
    
    return spec_name

# Predict Submittal Types
def prediction_model(big_spec_name, d_filepath_folder):
    with open("ML Model/vectorizer.pickle", 'rb+') as file:
        vectorizer_saved = pickle.load(file)
    
    with open("ML Model/label_encoder.pickle", 'rb+') as file:
        encorder_saved = pickle.load(file)

    with open("ML Model/type_classifier.pickle", 'rb+') as file:
        classifier_saved = pickle.load(file)

    updated_big_spac_name = "Prediction_" + big_spec_name  
    
    new_dataset = pd.read_csv(d_filepath_folder + "/" + "Production_" + big_spec_name + ".csv")

    description_vector = vectorizer_saved.transform(new_dataset['DESCRIPTION'])
    predictions = classifier_saved.predict(description_vector)
    new_dataset['TYPE'] = encorder_saved.inverse_transform(predictions)
    new_dataset = new_dataset[["SECTION", "SECTION NAME", "PART", "SUBSECTION", "SUBSECTION NAME", "TYPE", "DESCRIPTION"]]
    new_dataset.loc[(new_dataset.DESCRIPTION == "Not Found"), "TYPE"] = "Not Found"
    new_dataset.to_csv(d_filepath_folder + "/" + updated_big_spac_name + ".csv", index = False)
    
# Convert Mapped Data into Production Uniform Format
def convert_to_production_format(d_filepath_folder, big_spec_name):
    dataset_model = pd.read_csv(d_filepath_folder + "/" + big_spec_name + ".csv")

    # Fresh New DataFrame For Changed Result
    splitted_dataset = pd.DataFrame(columns = ['SECTION', 'SECTION NAME', 'PART', 'SUBSECTION', 'SUBSECTION NAME', 'DESCRIPTION'])

    for spec_number, spec_name, part, subsection, subsection_name, description in zip(dataset_model['SECTION'], dataset_model['SECTION NAME'], dataset_model['PART'], dataset_model['SUBSECTION'], dataset_model['SUBSECTION NAME'], dataset_model['DESCRIPTION']):
        point_flag = False
        # print(spec_number, spec_name, subsection, sub_section_heading, submittal_type, description) 
        if(re.search(r"[0-9]+\.", description.strip()) and len(re.findall(r"[0-9]+\.", description)) > 1):
            flag1, flag2 = True, True
            temp = ""
            for line in description.splitlines():
                if(not re.search(r"^[0-9]+\.", line.strip()) and flag1): # flag1 for keeping first line in temp
                    temp = line
                    splitted_dataset.loc[len(splitted_dataset)] = [spec_number, spec_name, part, subsection, subsection_name, line.strip()]
                    flag1 = False
                elif(re.search(r"^[0-9]+\.", line.strip())):
                    point_flag = True
                    update_subsection = re.search(r"^[0-9]+\.", line.strip()).group(0)[0:-1]
                    if(flag2): # flag2 for adding first point in last record
                        splitted_dataset.loc[len(splitted_dataset) - 1, "DESCRIPTION"] = splitted_dataset.loc[len(splitted_dataset) - 1, "DESCRIPTION"] + "\n" + line.strip() 
                        splitted_dataset.loc[len(splitted_dataset) - 1, "SUBSECTION"] = subsection + "-" + update_subsection
                        flag2 = False
                    else:
                        splitted_dataset.loc[len(splitted_dataset)] = [spec_number, spec_name, part, subsection + "-" + update_subsection, subsection_name, temp + "\n" + line.strip()]
                elif(point_flag):
                    splitted_dataset.loc[len(splitted_dataset) - 1, "DESCRIPTION"] = splitted_dataset.loc[len(splitted_dataset) - 1, "DESCRIPTION"] + line.strip() 
                else:
                    splitted_dataset.loc[len(splitted_dataset) - 1, "DESCRIPTION"] = splitted_dataset.loc[len(splitted_dataset) - 1, "DESCRIPTION"] + line.strip() 
        else:
            splitted_dataset.loc[len(splitted_dataset)] = [spec_number, spec_name, part, subsection, subsection_name, description.strip()]
    
        splitted_dataset.to_csv(d_filepath_folder + "/" + "Production_" + big_spec_name + ".csv", index = False)

        
# Submittal Extraction and Mapping
def submital_extraction_mapping(pre_data, ind_section_name, big_spec_name, d_filepath_folder):
    # print(pre_data, ind_section_name, big_spec_name, d_filepath_folder)

    # First Checkpoint 
    # Whether we need to process given individual spec ? 
    # True - Section/Document and End of Section/Document present in individual spec
    # False - Section/Document and End of Section/Document not present in individual spec
    
    # Remove Extra Spaces
    pre_data = re.sub(' +', ' ', pre_data)
    regex_end = r'END\s*OF\s*(SECTION|DOCUMENT)|NEW SECTION STARTS HERE'
    if(re.search(regex_end, pre_data)):
        pre_data = pre_data[0: re.search(regex_end, pre_data).end():]
        
    # Section Name and Number If Not There
    if("UNKNOWN" in ind_section_name):
        section_number = "".join(filter(lambda i: not i.isalpha(), ind_section_name)).strip()
        section_name = "UNKNOWN"
    else:
        section_number = "".join(filter(lambda i: not i.isalpha(), ind_section_name)).strip()

    # Store Section Details
    point_flag = True
    if(re.search(r'SECTION|DOCUMENT|Section', pre_data)):
        start_index = re.search(r'SECTION|DOCUMENT|Section', pre_data).start()
    else:
        start_index = 0
    if(re.search(r'PART 1|1\.1 |1\.01 ', pre_data)):
        end_index = re.search(r'PART 1|1\.1 |1\.01 ', pre_data).start()
    else:
        end_index = 0
        point_flag = False

    section_details = pre_data[start_index : end_index]
    if(len(section_details) > 500):
        section_details == "Not Found"

    # Preprocess on Section Details
    # Remove Extra Spaces and Replace \n
    section_details = re.sub(' +', ' ', section_details.replace("\n", ""))

    # Skip Data
    # Section Detail Need to Skip From All Data
    section_details_to_skip = [item.strip() for item in section_details.split("\n") if item.strip() != ""]

    # Find Section Name - Function Call
    # Pass Section Details to Expect Section Name
    section_name = custom_ner_section_name(section_details)

    if(point_flag == True):
        # Actual Data Collection
        try:
            end_index_part = pre_data.rindex("PART 1")
            data = pre_data[end_index_part:]
        except Exception:
            try:
                end_index_part = pre_data.index("1.1 ")
                data = pre_data[end_index_part:]
            except Exception:
                end_index_part = pre_data.index("1.01 ")
                data = pre_data[end_index_part:]

        # Filter Data
        # Remove Unwanted Items and Section Details to Skip
        # Mapp into Final Data String
        final_data = ""

        for index, line in enumerate(data.splitlines()):
            if("END OF SECTION" in line or "END OF DOCUMENT" in line.strip()):
                continue
            if("PART " in line):
                continue
            elif(len(line.strip()) == 0):
                continue
            elif([ele for ele in section_details_to_skip if(line.strip().startswith(ele))]):
                continue
            else:
                final_data = final_data + line.strip() + "\n"

        # Arrange Items in Proper Position
        final_lines = []
        index = -1
        for i, line in enumerate(final_data.splitlines()):
            line = line.strip()
            if(re.search(r"^[0-9]+\.[0-9]+", line)):
                final_lines.append(line)
                index = index + 1        
            elif(re.search(r"^[A-Za-z]\.", line)):
                final_lines.append(line)
                index = index + 1
            elif(re.search(r"^[0-9]+\.", line)):
                final_lines.append(line)
                index = index + 1
            elif(re.search(r"^[0-9]+\)", line)):
                final_lines.append(line)
                index = index + 1
            elif(re.search(r"^[a-z]+\)", line)):
                final_lines.append(line)
                index = index + 1
            elif(len(final_lines) == 0):
                pass
            elif(re.search(r"^[0-9]+\.[0-9]+", final_lines[index].strip())):
                final_lines[index] = final_lines[index] + " " + line
            else:
                final_lines[index] = final_lines[index] + " " + line

        # Find All Headings and Part
        heading = []
        flag = True
        for line in final_lines:
            if(re.search(r"^[0-9]+\.[0-9]+", line.strip())):
                heading.append(line)
                flag = False
            elif(re.search(r"^[A-Z]\.", line.strip()) and flag):
                heading.append(line)

        # Heading Pair
        res = list(map(list, zip(heading, heading[1:])))
        heading_list = []
        for i, data in enumerate(res):
            if("SUBMITTAL" in data[0]): 
                heading_list.append(data)
    
        # Find Index of Submittal Start and End
        # Check if Submittal Present in Data
        submittal_present_flag = False
        data_lines = []
        if(len(heading_list) == 0):
            final_lines = []
        else:
            for item in heading_list:
                if("SUMMITAL" in item or "SUBMITTAL" in item[0] or "SUBMITTALS" in item[0]):
                    submittal_present_flag = True
                    x, y = final_lines.index(item[0]), final_lines.index(item[1])
                    data_lines.append((x, y))

        # If Submittal Present Then Proceed Normally
        # Store Submittal Related Data Only
        if(submittal_present_flag):
            dataset = []
            for pos in data_lines:
                for ll in range(pos[0], pos[1]):
                    dataset.append(final_lines[ll])

            # Check Heading Present 
            flag_of_section = False
            for item in heading:
                if re.search(r"^[0-9]+\.[0-9]+", item.strip()):
                    flag_of_section = True
                    break

            # If Headings Present
            if(flag_of_section):    
                section_number = "".join(filter(lambda i: not i.isalpha(), ind_section_name)).strip()
                mapp_dataset = pd.DataFrame(columns = ["SECTION", "SECTION NAME", "PART", "SUBSECTION", "SUBSECTION NAME", "DESCRIPTION"])
                
                subsection_flag = False
                heading_flag = False
                subsection = "Not Found"
                subsection1 = ""
                subsection_name = "Not Found"
                part_name = "Not Found"

                # Map Records Into CSV
                for index, line in enumerate(dataset):
                    if(re.search(r"^[0-9]+\.[0-9]+", line.strip())):
                        subsection = line.split()[0]
                        if(subsection.strip().endswith(".")):
                            subsection = subsection[:3]
                        subsection_name = " ".join(line.split()[1:])
                        subsection_name = subsection_name.translate(str.maketrans('', '', string.punctuation))
                        subsection_flag = True

                        point = int(float(re.search(r"^[0-9]+\.[0-9]+", line.strip()).group()))
                        if(point == 1):
                            part_name = "PART 1 - GENERAL"
                        elif(point == 2):
                            part_name = "PART 2 - PRODUCT"
                        elif(point == 3):
                            part_name = "PART 3 - EXECUTION"

                    elif(re.search(r"^[A-Z]\.", line.strip())):
                        heading_flag = True
                        subsection1 = line.strip()[0]
                        mapp_dataset.loc[len(mapp_dataset)] = [section_number, section_name, part_name, subsection +"-"+ subsection1, subsection_name, line.strip()]
                    elif(heading_flag):
                        if(re.search(r"^[0-9]+\.", line.strip())):
                            mapp_dataset.loc[len(mapp_dataset) - 1, "DESCRIPTION"] = mapp_dataset.loc[len(mapp_dataset) - 1, "DESCRIPTION"] + " \n" + line.strip()
                        else:
                            mapp_dataset.loc[len(mapp_dataset) - 1, "DESCRIPTION"] = mapp_dataset.loc[len(mapp_dataset) - 1, "DESCRIPTION"] + " " + line.strip()
                    else:
                        if(subsection_flag):
                            mapp_dataset.loc[len(mapp_dataset)] = [section_number, section_name, part_name, subsection, subsection_name, "\n" + line.strip()]
                            subsection_flag = False
                        elif(r"^[0-9]+\.[0-9]+", line.strip()):
                            mapp_dataset.loc[len(mapp_dataset) - 1, "DESCRIPTION"] = mapp_dataset.loc[len(mapp_dataset) - 1, "DESCRIPTION"] + "\n" + line.strip()
                        else:
                            mapp_dataset.loc[len(mapp_dataset) - 1, "DESCRIPTION"] = mapp_dataset.loc[len(mapp_dataset) - 1, "DESCRIPTION"] + " " + line.strip()

                # Keep Preceeding Zero
                mapp_dataset.SECTION = mapp_dataset.SECTION.apply('="{}"'.format)
                
                store_path = d_filepath_folder + "/" + big_spec_name + "/" + big_spec_name + ".csv"

                if(os.path.exists(store_path)):
                    dataset = pd.read_csv(store_path)
                    dataset = dataset.append(mapp_dataset)
                    dataset.to_csv(store_path, index = False)
                else:
                    os.mkdir(d_filepath_folder + "/" + big_spec_name + "/")
                    mapp_dataset.to_csv(store_path, index = False)
                
                logger.info("{} | Success ".format(ind_section_name))

            # If Headings Not Present
            else:
                logger.info("{} | Not Applicable | Heading Format Not Matching ".format(ind_section_name))
                section_number = "".join(filter(lambda i: not i.isalpha(), ind_section_name)).strip()
                mapp_dataset = pd.DataFrame(columns = ["SECTION", "SECTION NAME", "PART", "SUBSECTION", "SUBSECTION NAME", "DESCRIPTION"])
                mapp_dataset.loc[len(mapp_dataset)] = [section_number, section_name, "Not Found", "Not Found", "Not Found", "Not Found"]
                mapp_dataset.SECTION = mapp_dataset.SECTION.apply('="{}"'.format)

                store_path = d_filepath_folder + "/" + big_spec_name + "/" + big_spec_name + ".csv"

                if(os.path.exists(store_path)):
                    dataset = pd.read_csv(store_path)
                    dataset = dataset.append(mapp_dataset)
                    dataset.to_csv(store_path, index = False)
                else:
                    os.mkdir(d_filepath_folder + "/" + big_spec_name + "/")
                    mapp_dataset.to_csv(store_path, index = False)

        # If Not Then Generate Empty Record with Section Number
        else:
            logger.info("{} | Not Applicable | Submittals Missing".format(ind_section_name))
            section_number = "".join(filter(lambda i: not i.isalpha(), ind_section_name)).strip()
        
            mapp_dataset = pd.DataFrame(columns = ["SECTION", "SECTION NAME", "PART", "SUBSECTION", "SUBSECTION NAME", "DESCRIPTION"])
            mapp_dataset.loc[len(mapp_dataset)] = [section_number, section_name, "Not Found", "Not Found", "Not Found", "Not Found"]
            mapp_dataset.SECTION = mapp_dataset.SECTION.apply('="{}"'.format)

            store_path = d_filepath_folder + "/" + big_spec_name + "/" + big_spec_name + ".csv"

            if(os.path.exists(store_path)):
                dataset = pd.read_csv(store_path)
                dataset = dataset.append(mapp_dataset)
                dataset.to_csv(store_path, index = False)
            else:
                os.mkdir(d_filepath_folder + "/" + big_spec_name + "/")
                mapp_dataset.to_csv(store_path, index = False)
        
    else:
        logger.info("{} | Not Applicable | Points Missing".format(ind_section_name))
        section_number = "".join(filter(lambda i: not i.isalpha(), ind_section_name)).strip()
    
        mapp_dataset = pd.DataFrame(columns = ["SECTION", "SECTION NAME", "PART", "SUBSECTION", "SUBSECTION NAME", "DESCRIPTION"])
        mapp_dataset.loc[len(mapp_dataset)] = [section_number, section_name, "Not Found", "Not Found", "Not Found", "Not Found"]
        mapp_dataset.SECTION = mapp_dataset.SECTION.apply('="{}"'.format)

        store_path = d_filepath_folder + "/" + big_spec_name + "/" + big_spec_name + ".csv"

        if(os.path.exists(store_path)):
            dataset = pd.read_csv(store_path)
            dataset = dataset.append(mapp_dataset)
            dataset.to_csv(store_path, index = False)
        else:
            os.mkdir(d_filepath_folder + "/" + big_spec_name + "/")
            mapp_dataset.to_csv(store_path, index = False)