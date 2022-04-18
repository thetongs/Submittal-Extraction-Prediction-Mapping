## Load libraries
#
import spacy
import itertools
import json
import re
from os import path
import csv
import pickle
import pandas as pd
import numpy as np

## Global Variables
#
spec_name = ""
spec_number = ""

## Create JSON Output From Dictionary - Function
#
def create_json_output(dictionary, spec_number, spec_name, file_name):
    output_file = file_name + ".json"

    with open(output_file, "w", encoding = 'utf-8') as outfile:
        json.dump(dictionary, outfile, indent = 4, ensure_ascii = False)

## Create CSV Output From Dictionary - Function
#
def create_csv_output(dictionary1, big_spec_name, spec_number, spec_name):
    headlines = ['SECTION', 'SECTION_NAME', 'PART', 'SUB SECTION', 'SUB SECTION HEADING', 'TYPE','DECRIPTION']

    big_spec_name = big_spec_name + ".csv"
    file_status = path.exists(big_spec_name)

    with open(big_spec_name, 'w', encoding = 'UTF8', newline = '') as file:
        writer = csv.writer(file)
        if(not file_status):
            writer.writerow(headlines)
        for key, item in dictionary1.items():
            if(isinstance(item, list)):
                for dicti in item:
                    writer.writerow([spec_number, spec_name, dicti['Part'], dicti['Sub Section'], dicti['Sub Section Heading '], dicti['Submittal Type '], " \n".join(it for it in dicti['Submittal Description'])])


## Find Section Name and Section Number - Function 
#
def find_section_name_section_number(pre_data):
    global spec_name
    global spec_number

    ## USe Custom NER To Extract Section Number and Section Name
    #
    start_index = re.search(r'SECTION|DOCUMENT', pre_data).start()
    end_index= pre_data.rindex("PART 1")

    section_details = pre_data[start_index:end_index]


    nlp2 = spacy.load("Spacy Custom NER Dump/")

    flag1, flag2 = False, False
    section_data = nlp2(section_details)
    for sent in section_data.ents:
        if(sent.label_ == 'section_number'):
            spec_number = str(sent)
            flag1 = True
        elif(sent.label_ == 'section_name'):
            spec_name = str(sent)
            flag2 = True
        elif(flag1 and flag2):
            break
    
    if(not flag1):
        spec_number = "NA"
    
    if(not flag2):
        spec_name = "NA"
    
    if(not flag1 and not flag2):
        spec_number = "NA"
        spec_name = "NA"

    # print("Section Number - {}".format(spec_number))
    # print("Section Name - {}".format(spec_name))
    

## Prediction On Discriptions - Function
#
def prediction_model(big_spec_name):
    ## Load Saved Model, Vectorizer and Encoder
    #
    with open("ML Model/vectorizer.pickle", 'rb+') as file:
        vectorizer_saved = pickle.load(file)
    
    with open("ML Model/label_encoder.pickle", 'rb+') as file:
        encorder_saved = pickle.load(file)

    with open("ML Model/type_classifier.pickle", 'rb+') as file:
        classifier_saved = pickle.load(file)

    ## Load Prepated Data Data
    #
    updated_big_spac_name = big_spec_name + "_updated" + ".csv"
    big_spec_name = big_spec_name + ".csv"
    
    new_dataset = pd.read_csv(big_spec_name)

    description_vector = vectorizer_saved.transform(new_dataset['DECRIPTION'])
    predictions = classifier_saved.predict(description_vector)
    new_dataset['TYPE'] = encorder_saved.inverse_transform(predictions)
    new_dataset.to_csv(updated_big_spac_name)
    

## Submittal Extraction 
#
def submital_extraction_mapping(pre_data, process_flag, file_name, big_spec_name):
    # try:
    if(process_flag):
        start_index = re.search(r'SECTION|DOCUMENT', pre_data).start()
        end_index= pre_data.rindex("PART 1")

        section_details = pre_data[start_index:end_index]

        
        ## Function Call - Find Section Name and Section Number
        #
        find_section_name_section_number(section_details)

        section_details = list(filter(None, section_details.splitlines()))
        data = pre_data[end_index:]

        ## Remove Empty Lines and End Of Section/Document
        #
        final_data = ""
        head_flag = True
        for index, line in enumerate(data.splitlines()):
            if("END OF SECTION" in line or "END OF DOCUMENT" in line):
                continue
            elif(len(line.strip()) == 0):
                continue
            elif([ele for ele in section_details if(ele in line)]):
                continue
            else:
                final_data = final_data + line + "\n"

        ## Find Index Of PART
        #
        start = 0
        for i, l in enumerate(final_data.splitlines()):
            if(l.upper().startswith("PART")):
                start = i
                break

        # print("PART Starts At - {}".format(start))


        ## Remove wrong newlines and create a final lines
        #
        final_lines = []
        index = -1
        for line in final_data.splitlines()[start:]:
            if(line.strip().startswith("PART")):
                final_lines.append(line)
                index = index + 1
            elif(re.search(r"^[0-9]+\.[0-9]+", line.strip())):
                final_lines.append(line)
                index = index + 1
            elif(re.search(r"^[A-Za-z]{1,2}\s*\.\s*", line.strip())):
                final_lines.append(line)
                index = index + 1
            elif(re.search(r"^[0-9]+\.", line.strip())):
                final_lines.append(line)
                index = index + 1
            elif(re.search(r"^[0-9]+\)", line.strip())):
                final_lines.append(line)
                index = index + 1
            elif(re.search(r"^[a-z]+\)", line.strip())):
                final_lines.append(line)
                index = index + 1
            else:
                final_lines[index] = final_lines[index] + " " + line

        ## Capture All Heading
        #
        heading = []
        flag = True
        for line in final_lines:
            if(re.search(r"^[0-9]+\.[0-9]+\s", line) or line.strip().startswith("PART")):
                heading.append(line)
                flag = False
            elif(re.search(r"^[A-Z]\.", line) and flag):
                heading.append(line)

        ## Capture and Arange Those Heading Which Has SUBMITTAL In It and Create A Pair 
        #
        res = list(map(list, zip(heading, heading[1:])))
        index_data = []
        heading_list = []
        for i, data in enumerate(res):
            if(i == 0):
                heading_list.append("PART 1 - GENERAL")
            if("SUBMITTAL" in data[0]): 
                heading_list.append(data)
            if("PART" in data[1]):
                heading_list.append(data[1])
        
        ## Create Index List Of Start Index and End Index Of Submittal Headinga Including PART
        #
        data_lines = []
        if(len(heading_list) == 0):
            final_lines = []
        else:
            for item in heading_list:
                if("SUMMITAL" in item or "SUBMITTAL" in item[0] or "SUBMITTALS" in item[0]):
                    x, y = final_lines.index(item[0]), final_lines.index(item[1])
                    data_lines.append((x, y))
                elif("PART " in item):
                    data_lines.append(item)
        
        ## Generate Final Lines For Mapping Into Dictionary
        #
        dataset = []
        for pos in data_lines:
            if("PART" in pos):
                dataset.append(pos)
            else:
                for ll in range(pos[0], pos[1]):
                    dataset.append(final_lines[ll])

        ## Check If Heading Are Present
        #
        flag_of_section = False
        for item in heading:
            if "1.1" in item:
                flag_of_section = True
                break

        ## Mapping the result into dictionary
        #
        if(flag_of_section):
            ## Map Text Data Into Dictionary
            #
            dictionary = {}
            part_name = ""
            cnt = 0
            cnt2 = 0

            for index, line in enumerate(itertools.chain(final_data.splitlines()[start : start + 1], dataset)): 
                if(index == 0):
                    dictionary["SECTION"] = spec_name
                    head = "SECTION_NAME"
                    dictionary[head] = spec_number
                    head = "Submittals"
                    dictionary[head] = []
                    if(line.startswith("PART ")):
                        part_name = line
                elif(line.startswith("PART ")):
                    part_name = line
                elif(re.search(r"^[0-9]+\.[0-9]+", line)):
                    subsection_name = line.split()[0]
                    subsection_heading = " ".join(line.split()[1:])
                elif(re.search(r"^[A-Z]\.", line.strip())):
                    dictionary[head].append({"Part" : part_name})
                    dictionary[head][cnt]["Sub Section"] = subsection_name + " " + line.split(".")[0]
                    dictionary[head][cnt]["Sub Section Heading "] = subsection_heading
                    try:
                        dictionary[head][cnt]["Submittal Type "] = line.split(":")[0].split(".")[1]
                        if(len(line.split(":")[1].strip()) == 0):
                            dictionary[head][cnt]["Submittal Description"] = []
                        else:
                            dictionary[head][cnt]["Submittal Description"] = [" ".join(line.split(":")[1:])]
                    except Exception as e:
                        dictionary[head][cnt]["Submittal Type "] = line.split(".")[0]
                        dictionary[head][cnt]["Submittal Description"] = [line.strip()]
                    cnt2 = cnt
                    cnt = cnt + 1
                elif(re.search(r"^[0-9]+\.", line.strip())):
                    try:
                        dictionary[head][cnt2]["Submittal Description"].append(line.strip())   
                    except Exception as e:
                        cnt2 = cnt
                        cnt = cnt + 1
                        dictionary[head].append({"Part" : part_name})
                        dictionary[head][cnt2]["Sub Section"] = subsection_name
                        dictionary[head][cnt2]["Sub Section Heading "] = subsection_heading
                        dictionary[head][cnt2]["Submittal Type "] = "NA"
                        dictionary[head][cnt2]["Submittal Description"] = [line.strip()]
                elif(re.search(r"^[a-z]\.", line.strip())):    
                    dictionary[head][cnt2]["Submittal Description"].append(line.strip())
                elif(re.search(r"^[0-9]+\)", line.strip())):     
                    dictionary[head][cnt2]["Submittal Description"].append(line.strip())
                elif(re.search(r"^[a-z]+\)", line.strip())):
                    dictionary[head][cnt2]["Submittal Description"].append(line.strip())
                elif(len(line.strip()) > 0):
                    dictionary[head][cnt2]["Submittal Description"].append(line.strip())
                else:
                    pass


            # print(dictionary)

        

            ## Function Call - Generate JSON Output With Data
            # 
            create_json_output(dictionary, spec_number, spec_name, file_name)

            dictionary1 = dictionary
            
            ## Function Call - Generate CSV Output With Data
            #
            create_csv_output(dictionary1, big_spec_name, spec_number, spec_name)

            ## Function Call - Prediction Of Discription
            #
            prediction_model(big_spec_name)

            ## END - If

        else:
            ## Function Call - Find Section Name and Section Number
            #
            find_section_name_section_number(pre_data)

            ## Function Call - Generate JSON Output As Empty
            # 
            dictionary = {
                        "SECTION": spec_number,
                        "SECTION_NAME": spec_name,
                        "Submittals": [{
                                        "Part": "NA",
                                        "Sub Section": "NA",
                                        "Sub Section Heading ": "NA",
                                        "Submittal Type ": "NA",
                                        "Submittal Description": ["NA"]
                                        }]
                            }

            create_json_output(dictionary, spec_number, spec_name, file_name)

            dictionary1 = dictionary

            ## Function Call - Generate CSV Output As Empty
            #
            create_csv_output(dictionary1, big_spec_name, spec_number, spec_name)

            ## Function Call - Prediction Of Discription
            #
            prediction_model(big_spec_name)

            ## END - Else 1
    else:
        ## Function Call - Find Section Name and Section Number
        #
        find_section_name_section_number(pre_data)

        ## Function Call - Generate JSON Output As Empty
        # 
        dictionary = {
                        "SECTION": spec_number,
                        "SECTION_NAME": spec_name,
                        "Submittals": [{
                                        "Part": "NA",
                                        "Sub Section": "NA",
                                        "Sub Section Heading ": "NA",
                                        "Submittal Type ": "NA",
                                        "Submittal Description": ["NA"]
                                        }]
                            }

        ## Function Call - JSON Generate JSON Output
        #
        create_json_output(dictionary, spec_number, spec_name, file_name)

        dictionary1 = dictionary

        ## Function Call - Generate CSV Output
        #
        create_csv_output(dictionary1, big_spec_name, spec_number, spec_name)

        ## END - Else 2

    # except Exception as e:
    #         ## Function Call - Find Section Name and Section Number
    #         #
    #         find_section_name_section_number(pre_data)


    #         dictionary = {
    #                         "SECTION": spec_number,
    #                         "SECTION_NAME": spec_name,
    #                         "Submittals": [{
    #                                         "Part": "NA",
    #                                         "Sub Section": "NA",
    #                                         "Sub Section Heading ": "NA",
    #                                         "Submittal Type ": "NA",
    #                                         "Submittal Description": ["NA"]
    #                                         }]
    #                          }

    #         ## Function Call - Generate JSON Output
    #         #
    #         create_json_output(dictionary, spec_number, spec_name, file_name)

    #         dictionary1 = dictionary

    #         ## Function Call - Generate CSV Output
    #         #
    #         create_csv_output(dictionary1, big_spec_name, spec_number, spec_name)

    #         ## END - Exception