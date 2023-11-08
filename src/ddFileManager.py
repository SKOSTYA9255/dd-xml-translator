from pathlib import Path
#import os


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

def setup(pathOptions):
    ManageFolders(pathOptions)
    ManageTXT(pathOptions)
    ManageXML(pathOptions)