from pathlib import Path
import os
import re


def ManageFolders(pathOptions):
    if(pathOptions.FilesFolder == ""): # TODO: Use regex pattern for better resilience
        raise Exception(f"Illegal name. Must not be {pathOptions.FilesFolder}")
    else:
        if(not pathOptions.FilesFolderPath.exists()):
            pathOptions.FilesFolderPath.mkdir()

def ManageXML(pathOptions):
    if(pathOptions.xmlInput == ""): # TODO: Use regex pattern for better resilience
        raise Exception(f"Illegal name. Must not be '{pathOptions.xmlInput}'")
    elif(pathOptions.xmlOutput == ""):
        raise Exception(f"Illegal name. Must not be '{pathOptions.xmlOutput}'")
    else:
        open(pathOptions.OutXMLPath, "w", encoding="utf-8")   

def ManageTXT(pathOptions):
    if(pathOptions.txtInput == ""): # TODO: Use regex pattern for better resilience
        raise Exception(f"Illegal name. Must not be '{pathOptions.txtInput}'")
    elif(pathOptions.txtOutput == ""):
        raise Exception(f"Illegal name. Must not be '{pathOptions.txtOutput}'")
    else:
        open(pathOptions.InTXTPath, "w", encoding="utf-8")
        open(pathOptions.OutTXTPath, "w", encoding="utf-8")

def findFile(dir, type, exclude):
    file_list = sorted(Path(dir).glob(f"*.{type}"))

    if(len(file_list) < 1):
        raise IndexError()
    else:
        for file in file_list:
            if(re.match(exclude, os.path.basename(file)) is None): # A valid XML file was found 
                return file
        raise FileNotFoundError() # No valid XML file was found


def setXMLFiles(pathOptions, file, output_prefix):
    pathOptions.xmlInput = os.path.basename(file)
    pathOptions.xmlOutput = f"{output_prefix}{os.path.basename(file)}"
    pathOptions.InXMLPath = pathOptions.FilesFolderPath.joinpath(pathOptions.xmlInput)
    pathOptions.OutXMLPath = pathOptions.FilesFolderPath.joinpath(pathOptions.xmlOutput)

def setup(pathOptions):
    ManageFolders(pathOptions)
    ManageTXT(pathOptions)
    ManageXML(pathOptions)