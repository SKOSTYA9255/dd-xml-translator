from pathlib import Path
from dataclasses import dataclass
import sys

from ddWrite import writeFile
from ddExtract import readFile
import ddFileManager as fm
from ddException import full_stack

def interface(pathOptions):
    while True:
        print("\n")
        printLines("=", 33)
        print("| DD XML Extractor and Inserter |")
        printLines("=", 33)
        print("\n")

        print(f"[r] read from XML file '{pathOptions.xmlInput}' to '{pathOptions.txtOutput}'\n")
        print(f"[w] write to XML file '{pathOptions.xmlOutput}' from txt file '{pathOptions.txtInput}'\n")
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
            print("\n Please enter a valid option, e.g. \"r\" for reading XML file\n")

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
    FilesFolder = "io"
    txtInput = "Translated Input.txt"
    txtOutput = "Extracted Outout.txt"
    xmlInput = "tiebaquirks.string_table.xml" # Get info from user
    xmlOutput = "OUT_tiebaquirks.string_table.xml" # Get info from user

    CWD = Path.cwd() # Get current working directory
    FilesFolderPath = CWD.joinpath(FilesFolder)
    InTXTPath = FilesFolderPath.joinpath(txtInput)
    OutTXTPath = FilesFolderPath.joinpath(txtOutput)
    InXMLPath = FilesFolderPath.joinpath(xmlInput)
    OutXMLPath = FilesFolderPath.joinpath(xmlOutput)

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

    try:
        fm.setup(pathOptions) # Creates folders/files using the FileManager
        interface(pathOptions)
    except Exception as error:
        print(full_stack())
        input("Press Enter to exit...")
        sys.exit()

main()