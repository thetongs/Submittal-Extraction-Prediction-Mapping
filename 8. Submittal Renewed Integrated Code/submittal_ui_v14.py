# Load Libraries
import os
import shutil
import pathlib
from tkinter import *
from tkinter import filedialog,messagebox

from submittal_extraction_v14 import submital_extraction_mapping
from submittal_extraction_v14 import convert_to_production_format
from submittal_extraction_v14 import prediction_model

from combine_individual_spec_preprocessing import combine_spec_data_to_txt
from combine_individual_spec_preprocessing import create_individual_spec_data_dict

import logging
import warnings
warnings.filterwarnings("ignore")


# Custom Log Message 
fmtstr = "%(asctime)s: %(message)s"
datestr = "%m/%d/%Y %I:%M:%S %p"

logging.basicConfig(
    filename="logs.log",
    level=logging.DEBUG,
    filemode = "w",
    format = fmtstr,
    datefmt = datestr
)

logger = logging.getLogger('submittal_ui_v14.py')


# Create UI Window
root = Tk()
root.geometry("255x260")
root.title('Submittal')
root.resizable(0, 0)

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Constants UI Elements
path = resource_path("cloud.png")
img = PhotoImage(file = path, master= root)
img_label = Label(root, image = img)
img_label.place(x = 0, y = 0)

# Global Paths
s_filepath_folder = ""
s_filepath_spec_pdf = ""
d_filepath_folder = ""

# Function 
# Select Source PDF Files Folder
def s_open_folder_file():
    global s_filepath_folder

    s_filepath_folder = filedialog.askdirectory()
    if(s_filepath_folder):
        source_folder_button.configure(bg = 'light green')
    else:
        messagebox.showwarning('Warning','Source Folder Not Selected')
        source_folder_button.configure(bg = 'red')

# Function
# Select Source Combine Spec PDF
def s_open_file():
    global s_filepath_spec_pdf

    file = filedialog.askopenfile(mode='r', filetypes=[('PDF Files', '*.pdf')])
    if file:
        s_filepath_spec_pdf = os.path.abspath(file.name)
        source_button.configure(bg = 'light green')
    else:
        messagebox.showwarning('Warning','File Not Selected')
        source_button.configure(bg = 'red')

# Function
# Select Destination Folder 
def d_open_file():
    global d_filepath_folder

    d_filepath_folder = filedialog.askdirectory()
    if(d_filepath_folder):
        destination_button.configure(bg='light green')
    else:
        messagebox.showwarning('Warning','Destination Folder Not Selected')
        destination_button.configure(bg='red')

# Create Dropdown 
# Options - Combine Spec and Individual Spec Folder 
OPTIONS = [
                "Combine Spec",
                "Individual Specs Folder"
] 
variable = StringVar(root)
variable.set(OPTIONS[0]) 

menu = OptionMenu(root, variable, *OPTIONS)
menu.place(x = 50, y = 8)
menu.config(width = 20)

# Create a Button - 
# Take Source File PDF File
source_button = Button(root, text="Source File", command = s_open_file)
# Take Source Files Folder
source_folder_button = Button(root, text="Source Folder", command = s_open_folder_file)
# Select Destination Path
destination_button = Button(root, text="Destination Folder", command = d_open_file)

source_button.place(x = 70, y = 80)
source_button.config(width = 15)
destination_button.place(x = 70, y = 120)
destination_button.config(width = 15)

# Check and Use Dynamic Value of Dropdown
def callback(*args):
    if(variable.get() == "Combine Spec"):
        source_folder_button.place_forget() # Remove Source Folder 
        source_button.config(width = 15)
        source_button.place(x = 70, y = 80)

        destination_button.config(width = 15)
        destination_button.place(x = 70, y = 120)
    else:
        source_button.place_forget() # Remove Source File
        source_folder_button.config(width = 15)
        source_folder_button.place(x = 70, y = 80)

        destination_button.config(width = 15)
        destination_button.place(x = 70, y = 120)

variable.trace("w", callback)


# Function
# Perform All Operations After 'Action' Click
def submittal_automation():
    # For Combine Spec
    if(variable.get() == "Combine Spec"):
        if(s_filepath_spec_pdf and d_filepath_folder):
            big_spec_name = pathlib.Path(s_filepath_spec_pdf).stem
            if(len(d_filepath_folder + "/" + big_spec_name + "/" + big_spec_name + ".csv") < 259):

                big_spec_name = pathlib.Path(s_filepath_spec_pdf).stem
                logger.info("{} | Spec Processing Start".format(big_spec_name))

                # Function Call - Combine PDF Spec to Txt with Dynamic Header Footer Removal
                combine_spec_data_to_txt(s_filepath_spec_pdf)
                # Function Call - Create Mapped Dictionary with Individual Spec with Repective Data
                individual_specification = create_individual_spec_data_dict()
            
                # Part Validation Check
                for ind_section_name, pre_data in individual_specification.items():
                    
                    # print(re.findall("PART\s?[1-3]", pre_data))
                    # print(len(re.findall("PART\s?[1-3]", pre_data)))

                    if(re.findall("PART\s?1", pre_data)):
                        part_flag = True
                    else:
                        part_flag = False

                    # Function Call - Submittal Mapping to CSV
                    submital_extraction_mapping(pre_data, part_flag, ind_section_name, big_spec_name, d_filepath_folder)
                
                # Function Call - Convert Into Production Format 
                convert_to_production_format(d_filepath_folder + "/" + big_spec_name + "/", big_spec_name)

                # Function Call - Prediction on Production Format
                prediction_model(big_spec_name, d_filepath_folder + "/" + big_spec_name + "/")
                
                messagebox.showinfo("Status", "Process Completed ")
                # Rename Log File and Store in Destination Folder Selected
                shutil.copy("logs.log", d_filepath_folder + "/" + big_spec_name + "/" + "{}.log".format(big_spec_name))

            else:
                messagebox.showwarning("Warning", "File Path Exceeding 259 Char | Please Select Short Path") 
        else:
            messagebox.showwarning('Warning','Please Select Source PDF File and Destination Folder.')
    else:
        # Fpr Indvidual Specs Folder
        if(s_filepath_folder and d_filepath_folder):
            big_spec_name = pathlib.PurePath(s_filepath_folder).name
            if(len(d_filepath_folder + "/" + big_spec_name + "/" + big_spec_name + ".csv") < 259):
                logger.info("{} | Individual Spec Folder Processing Start".format(big_spec_name))

                for root, dirs, files in os.walk(s_filepath_folder):
                    if(str(file).endswith(".pdf")):
                        i_file_path = os.path.join(root, file)
                        
                        # Function Call - Individual Spec PDF to Txt
                        combine_spec_data_to_txt(i_file_path)
                        # Function Call - Indidual Spec Mapped into Dictionary
                        individual_specification = create_individual_spec_data_dict()
                        
                        # Part Validation For Each Indidual Spec
                        for ind_section_name, pre_data in individual_specification.items():
                            if(len(re.findall("PART\s?[1-3]", pre_data))):
                                part_flag = True
                            else:
                                part_flag = False

                            # Function Call - Submittal Extraction and Mapping into CSV
                            submital_extraction_mapping(pre_data, part_flag, ind_section_name, big_spec_name, d_filepath_folder)            
                
                # Function Call - Convert Into Production Format 
                convert_to_production_format(d_filepath_folder + "/" + big_spec_name + "/", big_spec_name)

                # Function Call - Prediction
                prediction_model(big_spec_name, d_filepath_folder + "/" + big_spec_name + "/")
                
                messagebox.showinfo("Status", "Process Completed.")
                # Rename Log File and Store in Destination Folder Selected
                shutil.copy("logs.log", d_filepath_folder + "/" + big_spec_name + "/" + "{}.log".format(big_spec_name))
            else:
                messagebox.showwarning("Warning", "File Path Exceeding 259 Char | Please Select Short Path") 
        else:
            messagebox.showwarning('Warning','Please Select Source PDF File and Destination Folder.')
    
# Create a Button - Perform Operations
action_button = Button(root, text = "Action", command = submittal_automation, bg = "lightgreen")
action_button.place(x = 105, y = 160)

# Label - Branding
signature = Label(root, text = "vConstruct-DPR")
signature.place(x = 85, y = 220)

# Version Label
version = Label(root, text = "v 2.0.0")
version.place(x = 215, y = 242)


# Tkinter Loop
root.mainloop()