import re

def get_specification_name(str_data):

    # if "PART" in 
    # if "<Image:" in spec_name:
    #     spec_name=spec_name.split("<Image:")[0]

    regex=r'SECTION\s*\d{2}\s*\d{2}\s*\d{2}[i]?[.0-9A-Za-z]*'
    _,start=re.search(regex,str_data).span()
    end,_=re.search("\s*PART",str_data).span()
    spec_name=str_data[start:end].strip()

    for i,j in enumerate(spec_name):
        if j.isalpha():
            break
    spec_name=spec_name[i:]
    
    return spec_name.strip().title()
