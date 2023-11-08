from pathlib import Path
from dataclasses import dataclass
import sys
import os
import ctypes

from ddWrite import writeFile
from ddExtract import readFile
import ddFileManager as fm
from ddException import full_stack


APP_TITLE = "DD XML Extractor and Inserter"


def initialSetup(pathOptions):
    fm.ManageFolders(pathOptions)
    printHeader()
    while True:
        print(f"Please put the XML file you want extracted into the folder '{pathOptions.FilesFolder}'")
        input("When done, press Enter to continue.")

        file = fm.findFile(pathOptions.FilesFolderPath, "xml")
        if(file is False):
            printLines("─", 40)
            print(f"\nError: Could not find an XML file in '{pathOptions.FilesFolderPath}'\n")
        else:
            fm.setXMLFiles(pathOptions, file, "OUT")
            return

def interface(pathOptions):
    while True:
        printHeader()
        print(f"[r] read from XML file '{pathOptions.xmlInput}' to '{pathOptions.txtOutput}'")
        print(f"[w] write to XML file '{pathOptions.xmlOutput}' from txt file '{pathOptions.txtInput}'")
        print("[x] Exit\n")
        choice = input("Enter desired action: ")

        if choice == "r":
            print("Reading files...")
            readFile(pathOptions)
            print("Done!")
        elif choice == "w":
            print("Writing files...")
            writeFile(pathOptions)
            print("Done!")
        elif choice == "x":
            sys.exit()
        else:
            print("\nPlease enter a valid option, e.g. \"r\" for reading XML file\n")

def printHeader():
    print("\n")
    printLines("=", 33)
    print(f"| {APP_TITLE} |") # TODO: Implement dynamic character counting to adjust printLines size automatically
    printLines("=", 33)
    print("\n")

def printLines(type: str, count: int)->None:
    print(f"{type}"*count)

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

def main():
    try:
        ctypes.windll.kernel32.SetConsoleTitleW(APP_TITLE)
        FilesFolder = "io"
        txtInput = "Translated Input.txt"
        txtOutput = "Extracted Outout.txt"
        xmlInput = "" # Get info from user
        xmlOutput = "" # Get info from user

        CWD = Path.cwd() # Get current working directory
        FilesFolderPath = CWD.joinpath(FilesFolder)
        InTXTPath = FilesFolderPath.joinpath(txtInput)
        OutTXTPath = FilesFolderPath.joinpath(txtOutput)
        InXMLPath = "" # Get info from user
        OutXMLPath = "" # Get info from user

        pathOptions = DDPaths(
            FilesFolder,
            txtInput,
            txtOutput,
            xmlInput,
            xmlOutput,
            CWD,
            FilesFolderPath,
            InTXTPath,
            OutTXTPath,
            InXMLPath,
            OutXMLPath
        )

        if(pathOptions.xmlInput == "" or pathOptions.xmlOutput == ""):
            initialSetup(pathOptions)

        fm.setup(pathOptions) # Creates folders/files using the FileManager
        print(pathOptions.xmlInput)
        interface(pathOptions)
    except Exception as error:
        print(full_stack())
        input("Press Enter to exit...")
        sys.exit()

main()