#!/usr/bin/python3
import sys,os
import colorama
from colorama import Fore,Style,Back
colorama.init()

def process_argument_path():

    print(Style.BRIGHT)
    print("1. Combined Specification Present " + Fore.CYAN + "(Yes/No) "+ Fore.WHITE+ ": " + Fore.CYAN , end='')
    combined_spec_choice=input()

    if combined_spec_choice.lower() in ['yes','y']:

        print(Fore.RESET + "2. Enter Combined Specification Name : "+ Fore.CYAN, end='')
        input_path=input()
        print(Fore.RESET)

        if input_path.endswith('.pdf'):
            pass

        elif input_path.endswith('.PDF'):
            input_path=input_path.replace('.PDF','.pdf')
        else:
            input_path=input_path+'.pdf'

        application_path = os.path.dirname(os.path.abspath(input_path))
        spec_path=os.path.join(application_path,input_path)
        # location=os.path.join(application_path,'master.xlsx')
    
        # if os.path.exists(location):
        #     pass
        # else:
        #     print(Back.RED+Style.BRIGHT+Fore.WHITE+"\nmaster.xlsx not found: \n\nProbable Reason : \n1. master file not present in the same folder as exe application.\n2. Spelling of master file has been modified. \n"+Back.RESET+Fore.WHITE+Back.GREEN+"\nCorrect format for master : \n   "+"Filename - master\n   Extension - .xlsx"+Style.RESET_ALL+Style.BRIGHT)
        #     print(Fore.RED+"\nCLOSE THE APPLICATION AND TRY AGAIN")
        #     input()
        #     sys.exit()

        if os.path.exists(spec_path):
            return spec_path,application_path,"yes",input_path
        
        else:
            print(Back.RED+Style.BRIGHT+Fore.WHITE+"\nFile not found : {}\n\nProbable Reason : \n1. Spelling of file is incorrect. \n2. File not present alongside exe application. \n3. You have given folder name instead of specification".format(input_path)+Style.RESET_ALL+Style.BRIGHT)
            print(Fore.RED+"\nCLOSE THE APPLICATION AND TRY AGAIN")
            input()
            sys.exit()
        
    elif combined_spec_choice.lower() in ['no','n']:

        print(Fore.RESET + "2. Enter Folder Name : "+ Fore.CYAN, end='')
        input_path=input()
        print(Fore.RESET)

        application_path = os.path.dirname(os.path.abspath(input_path))
        folder_path=os.path.join(application_path,input_path)

        # location=os.path.join(application_path,'master.xlsx')
    
        # if os.path.exists(location):
        #     pass
        # else:
        #     print(Back.RED+Style.BRIGHT+Fore.WHITE+"\nmaster.xlsx not found: \n\nProbable Reason : \n1. master file not present in the same folder as exe application.\n2. Spelling of master file has been modified. \n"+Back.RESET+Fore.WHITE+Back.GREEN+"\nCorrect format for master : \n   "+"Filename - master\n   Extension - .xlsx"+Style.RESET_ALL+Style.BRIGHT)
        #     print(Fore.RED+"\nCLOSE THE APPLICATION AND TRY AGAIN")
        #     input()
        #     sys.exit()

        if not os.path.exists(folder_path):
            print(Back.RED+Style.BRIGHT+Fore.WHITE+"\nFolder not found : {}\n\nProbable Reason : \n1. Spelling of folder is incorrect. \n2. Folder not present alongside exe application. \n3. You have given specification name instead of folder".format(folder_path)+Style.RESET_ALL+Style.BRIGHT)
            print(Fore.RED+"\nCLOSE THE APPLICATION AND TRY AGAIN")
            input()
            sys.exit()

        list_of_specs=[]

        for i in os.listdir(folder_path):
            if i.endswith('.pdf'):
                list_of_specs.append(os.path.join(folder_path,i))

        return list_of_specs,application_path,"no",input_path

    else:
        print(Back.RED+Style.BRIGHT+Fore.WHITE+"\nInvalid choice for 'yes' or 'no'."+Style.RESET_ALL+Style.BRIGHT)
        print(Fore.RED+"\nCLOSE THE APPLICATION AND TRY AGAIN")
        input()
        sys.exit()
    


