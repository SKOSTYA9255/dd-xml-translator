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
        raise Exception(f"Illegal name. Must not be {pathOptions.FilesFolder}")
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