doc = fitz.open(path)

## Create Text File
#
with open('raw_text.txt', 'w', encoding="utf-8") as file:
    for pdf_page, page in enumerate(doc):
        page_data = ""
        text_instances = []
        
        file.write("\n" + "PAGE : " + str(pdf_page) + "\n")
        # Check each format of PART 1 GENERAL
        # and Create Rect List
        for word in ast.literal_eval(config['Constants']['first_page_search_term']):
            if(page.search_for(word)):
                text_instances.extend(page.searchFor(word))
                break

        # Get Height and Width of each page for calculation
        width, height = page.rect.width, page.rect.height

        print(len(text_instances))

        # For normal format PART 1 count is one on main page and 
        # for other pages zero.
        # For other format(index wala) we are using location of second 
        # occurence and extracting from that point. 
        
        if(len(text_instances) == 1):
            if(page.searchFor("SECTION") and page.searchFor("DOCUMENT")):
                section_instances = page.searchFor("SECTION")[0]
                document_instances = page.searchFor("DOCUMENT")[0]

                # print(section_instances)
                # print(document_instances)

                if(section_instances.y0 < document_instances.y0):
                    section_details = page.get_textbox(fitz.Rect((70, section_instances.y0, 0.90*float(width), 0.16*float(height))))
                    page_data = page_data + "\n" + section_details 
                else:
                    document_details = page.get_textbox(fitz.Rect((70, document_instances.y0, 0.90*float(width), 0.16*float(height))))
                    page_data = page_data + "\n" + document_details
    

            elif(page.searchFor("SECTION")):
                section_instances = page.searchFor("SECTION")[0]
                section_details = page.get_textbox(fitz.Rect((70, section_instances.y0, 0.90*float(width), 0.16*float(height))))
                page_data = page_data + "\n" + section_details
            
            elif(page.searchFor("DOCUMENT")):
                document_instances = page.searchFor("DOCUMENT")[0]
                document_details = page.get_textbox(fitz.Rect((70, document_instances.y0, 0.90*float(width), 0.16*float(height))))
                page_data = page_data + "\n" + document_details
                       
            page_data = page_data + "\n" + page.get_textbox(fitz.Rect((70, text_instances[0].y0 + 1, width, 0.89*float(height))))

        elif(len(text_instances) == 2):
            if(page.searchFor("SECTION") and page.searchFor("DOCUMENT")):
                section_instances = page.searchFor("SECTION")[0]
                document_instances = page.searchFor("DOCUMENT")[0]

                if(section_instances.y0 < document_instances.y0):
                    section_details = page.get_textbox(fitz.Rect((70, section_instances.y0, 0.90*float(width), 0.16*float(height))))
                    page_data = page_data + "\n" + section_details 
                else:
                    document_details = page.get_textbox(fitz.Rect((70, document_instances.y0, 0.90*float(width), 0.16*float(height))))
                    page_data = page_data + "\n" + document_details

            elif(page.searchFor("SECTION")):
                section_instances = page.searchFor("SECTION")[0]
                section_details = page.get_textbox(fitz.Rect((70, section_instances.y0, 0.90*float(width), 0.16*float(height))))
                page_data = page_data + "\n" + section_details
            
            elif(page.searchFor("DOCUMENT")):
                document_instances = page.searchFor("DOCUMENT")[0]
                document_details = page.get_textbox(fitz.Rect((70, document_instances.y0, 0.90*float(width), 0.16*float(height))))
                page_data = page_data + "\n" + document_details

            page_data = page_data  + "\n" + page.get_textbox(fitz.Rect((70, text_instances[1].y0, width, 0.89*float(height))))
            
        else:
            page_data = page_data + "\n" + page.get_textbox(fitz.Rect((70, 0.10*float(height), width, 0.91*float(height))))

        file.write(page_data)