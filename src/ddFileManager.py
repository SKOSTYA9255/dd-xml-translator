from pathlib import Path
import os
import re

# TODO: Find better way to handle illegal names than raising universal exceptions
def ManageFolders(pathOptions):
    """Creates the required folder if it doesn't exist. 
    The folder name is specified in pathOptions.

    Args:
        pathOptions (dataclass): A dataclass (struct) containing all paths and path names used in the program.

    Raises:
        Exception: When the folder name is illegal. Currently only checks "". 
    """
    if(pathOptions.FilesFolder == ""): # TODO: Use regex pattern for better resilience.
        raise Exception(f"Illegal name. Must not be '{pathOptions.FilesFolder}'")
    else:
        if(not pathOptions.FilesFolderPath.exists()):
            pathOptions.FilesFolderPath.mkdir()

def ManageXML(pathOptions):
    """Creates the required XML file or overwrites an existing file with an empty file.

    Args:
        pathOptions (dataclass): A dataclass (struct) containing all paths and path names used in the program.

    Raises:
        Exception: When the file name is illegal. Currently only checks "". 
    """
    if(pathOptions.xmlInput == ""): # TODO: Use regex pattern for better resilience.
        raise Exception(f"Illegal name. Must not be '{pathOptions.xmlInput}'")
    elif(pathOptions.xmlOutput == ""):
        raise Exception(f"Illegal name. Must not be '{pathOptions.xmlOutput}'")
    else:
        open(pathOptions.OutXMLPath, "w", encoding="utf-8")   

def ManageTXT(pathOptions):
    """Creates the required txt files or overwrites existing files with empty files.
    Creates both input txt and output txt.

    Args:
        pathOptions (dataclass): A dataclass (struct) containing all paths and path names used in the program.

    Raises:
        Exception: When the file name is illegal. Currently only checks "". 
    """
    if(pathOptions.txtInput == ""): # TODO: Use regex pattern for better resilience.
        raise Exception(f"Illegal name. Must not be '{pathOptions.txtInput}'")
    elif(pathOptions.txtOutput == ""):
        raise Exception(f"Illegal name. Must not be '{pathOptions.txtOutput}'")
    else:
        open(pathOptions.InTXTPath, "w", encoding="utf-8")
        open(pathOptions.OutTXTPath, "w", encoding="utf-8")

def findFile(dir: str, type: str, exclude: str="")->str:
    """Finds all files of "type" in directory "dir" (non-recursive).
    Optional string "exclude" to exclude all files of "type" with a name containing "exclude".
    Args:
        dir (str): The directory to search in.
        type (str): The file type to search for. E.g. "xml". Case sensitive
        exclude (str): Optional. Exclude all "type" files whose name contains "exclude".

    Raises:
        IndexError: No file of "type" was found in the directory.
        FileNotFoundError: A file of "type" was found, but its name contains "exclude".

    Returns:
        str: The filepath of the found file.
    """
    file_list = sorted(Path(dir).glob(f"*.{type}"))

    if(len(file_list) < 1):
        raise IndexError() # No file of "type" was found in the directory. TODO: Make this a custom exception.
    elif(exclude == ""):
        return file_list[0] # Take first file found.
    else:
        for file in file_list:
            if(re.match(exclude, os.path.basename(file)) is None): # A valid file was found. (Its name does not contain "exclude").
                return file
        raise FileNotFoundError() # A file of "type" was found, but its name contains "exclude". Thus, no valid file was found. TODO: Make this a custom exception.


def setXMLFiles(pathOptions, file: str, output_prefix: str):
    """Sets the names and file paths of the XML files in pathOptions.
    Should be run after obtaining the before-mentioned data from the user.

    Args:
        pathOptions (dataclass): A dataclass (struct) containing all paths and path names used in the program.
        file (str): The file path of the input XML file.
        output_prefix (str): Prefix the name of the output XML with this. (Since the output file takes the name of the input file).
    """
    pathOptions.xmlInput = os.path.basename(file)
    pathOptions.xmlOutput = f"{output_prefix}{os.path.basename(file)}"
    pathOptions.InXMLPath = pathOptions.FilesFolderPath.joinpath(pathOptions.xmlInput)
    pathOptions.OutXMLPath = pathOptions.FilesFolderPath.joinpath(pathOptions.xmlOutput)

def setup(pathOptions):
    """Calls all functions required for proper setup in the correct order (folders before files).

    Args:
        pathOptions (dataclass): A dataclass (struct) containing all paths and path names used in the program.
    """
    ManageFolders(pathOptions)
    ManageTXT(pathOptions)
    ManageXML(pathOptions)

def sanitizeXML(xmlPath: str)->list:
    xml_input = open(xmlPath, "r", encoding="utf-8").read().splitlines() # splitlines() breaks each line after the newline
    sanitized_list = []
    prev_lines = []

    begin_entry_found = False
    end_entry_found = False # This one's added for clarity but not technically used

    for line in xml_input:
        if(re.search(r"(<entry)", line) is not None and re.search(r"(<\/entry>)", line) is not None): # This line has <entry and </entry
            sanitized_list.append(line)
            continue

        if(re.search(r"(<entry)", line) is not None): # This line has <entry
            begin_entry_found = True
            if(re.search(r"(<\/entry>)", line) is None): # This line does not have </entry
                end_entry_found = False
                prev_lines.append(line)
                continue

        if(begin_entry_found): # /entry was found in a previous iteration (not necessarily the last one)
            if(re.search(r"(<\/entry>)", line) is not None): # This line has </entry
                end_entry_found = True
                temp_line = ""

                for prev in prev_lines:
                    temp_line += prev

                temp_line += line
                sanitized_list.append(temp_line)
                prev_lines.clear()
                begin_entry_found, end_entry_found = False, False
            else: # This line does not have </entry
                prev_lines.append(line)
        elif(re.search(r"(<\/entry>)", line) is None): # This line is of no concern for sanitizing. Line is e.g. <?xml version="1.0" encoding="UTF-8"?>
            sanitized_list.append(line)

    #for line in sanitized_list:
    #    open("SANIT.xml", "a", encoding="utf-8").write(line+"\n")
    
    return sanitized_list