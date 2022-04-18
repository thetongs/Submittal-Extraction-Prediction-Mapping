import re 

def get_specification_number(str_data):

    regex=r'SECTION\s*\d{2}\s*\d{2}\s*\d{2}[i]?[.0-9A-Za-z]*'
    spec_num=re.search("\s*\d{2}\s*\d{2}\s*\d{2}[i]?[.0-9A-Za-z]*",re.search(regex,str_data,re.IGNORECASE).group()).group()
    return spec_num.strip()
