from pathlib import Path
from dataclasses import dataclass
import sys
import os
import ctypes

import ddConstants as ddc
import ddFileManager as fm
from ddException import full_stack
from ddUI import interface, initialSetup


@dataclass
class DDPaths:
    FilesFolder: str
    txtInput: str
    txtOutput: str
    xmlInput: str
    xmlOutput: str

    CWD: str
    FilesFolderPath: str
    InTXTPath: str
    OutTXTPath: str
    InXMLPath: str
    OutXMLPath: str
    sanitizedXML: list
    extractedXML: list

@dataclass
class Config:
    ExtractLanguageTag: str
    WriteLanguageTag: str

def main():
    try:
        ctypes.windll.kernel32.SetConsoleTitleW(ddc.APP_TITLE)

        CWD = Path.cwd() # Get current working directory
        FilesFolderPath = CWD.joinpath(ddc.FilesFolder)
        InTXTPath = FilesFolderPath.joinpath(ddc.txtInput)
        OutTXTPath = FilesFolderPath.joinpath(ddc.txtOutput)
        InXMLPath = "" # Get info from user
        OutXMLPath = "" # Get info from user

        pathOptions = DDPaths(
            ddc.FilesFolder,
            ddc.txtInput,
            ddc.txtOutput,
            ddc.xmlInput,
            ddc.xmlOutput,
            CWD,
            FilesFolderPath,
            InTXTPath,
            OutTXTPath,
            InXMLPath,
            OutXMLPath,
            [],
            []
        )

        config = Config("schinese", "english")

        if(pathOptions.xmlInput == "" or pathOptions.xmlOutput == ""):
            initialSetup(pathOptions)

        fm.setup(pathOptions) # Creates folders/files using the FileManager
        interface(pathOptions, config)
    except Exception as error:
        print(full_stack())
        input("Press Enter to exit...")
        sys.exit()

main()