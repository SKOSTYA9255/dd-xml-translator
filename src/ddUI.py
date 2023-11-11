import sys

from ddWrite import writeFile
from ddExtract import readFile
import ddFileManager as fm
import ddConstants as ddc


def printHeader(title):
    padding = 4
    title_lenght = len(title)
    repeat_times = padding + title_lenght

    print("\n")
    printLines("=", repeat_times)
    print(f" | {title} |")
    printLines("=", repeat_times)
    print("\n")

def printLines(type: str, count: int):
    print(" "+f"{type}"*count)

def initialSetup(pathOptions):
    """Generates required files/folders on startup and asks the user to insert
    an input XML in the program's working directory (as specified in pathOptions)

    Args:
        pathOptions (dataclass): A dataclass (struct) containing all paths and path names used in the program.
    """
    fm.ManageFolders(pathOptions)
    printHeader("Initial Setup")
    while True:
        print(f" Please put the XML file you want extracted into the folder '{pathOptions.FilesFolder}'")
        input(" When done, press Enter to continue.")

        try:
            file = fm.findFile(pathOptions.FilesFolderPath, "xml", ddc.FILE_PREFIX)
        except IndexError:
            printLines("─", 40)
            print(f"\n Error: Could not find an XML file in '{pathOptions.FilesFolderPath}'\n")
            continue
        except FileNotFoundError:
            printLines("─", 40)
            print(f"\n Error: Could not find a valid XML file in '{pathOptions.FilesFolderPath}'")
            print(f" Any XML file with the prefix {ddc.FILE_PREFIX} is not valid for extraction!\n")
            continue

        fm.setXMLFiles(pathOptions, file, ddc.FILE_PREFIX)
        pathOptions.sanitizedXML = fm.sanitizeXML(pathOptions.InXMLPath)
        return

def setLanguageTag(config, type: int):
    # 1 = Extract
    # 2 = Write
    
    lang_tag = ""
    name = ""
    if(type == 1):
        name = "Extracting"
    elif(type == 2):
        name = "Writing"
    else:
        raise Exception(f"Invalid type for language tag. Expected range int: 1,2. Got: {type} of {type.__class__}")
    printHeader(f"Set {name} XML Language Tag")
    print(" INFO:")
    print("   An XML language tag could be \"english\".")
    print("   Please check your XML file for the specific language tag you wish to use.")
    print("   To reset language tag, simply press enter without typing anything.")
    printLines("─", 10)
    tag = input(" Set XML language tag to: ")
    
    if(type == 1):
        config.ExtractLanguageTag = str(tag)
    elif(type == 2):
        config.WriteLanguageTag = str(tag)

def interface(pathOptions, config):
    while True:
        printHeader(ddc.APP_TITLE)
        # Main options
        print(f" [r] Read from XML file '{pathOptions.xmlInput}' to '{pathOptions.txtOutput}'")
        print(f" [w] Write to XML file '{pathOptions.xmlOutput}' from txt file '{pathOptions.txtInput}'")

        # Tools
        print("\n")
        printLines("─", 20)
        print(" Toolbox\n")
        print(" [1] Set extracting XML language tag.")
        if(config.ExtractLanguageTag == ""):
            print("     Extracting language tag not set. The entire file will be extracted. This is NOT recommended!")            
        else:
            print(f"     Extracting language tag is currently: {config.ExtractLanguageTag}")
        print("\n [2] Set writing XML language tag")
        if(config.ExtractLanguageTag != "" and config.WriteLanguageTag == ""):
            print("     Warning: Cannot write to the XML file! Either set a writing language tag or reset the extracting language tag.")            
        elif(config.WriteLanguageTag == ""):
             print("     Writing language tag not set. The entire file will be replaced. This is NOT recommended!")
        else:
            print(f"     Writing language tag is currently: {config.WriteLanguageTag}")
        
        # Exit
        print("\n")
        printLines("─", 20)
        print(" [x] Exit\n")
        
        # Choice processing
        choice = input(" Enter desired action: ")

        if choice == "r":
            print("  Reading files...")
            readFile(pathOptions, config)
            print("  Done!")
        elif choice == "w":
            print("  Writing files...")
            writeFile(pathOptions, config)
            print("  Done!")
        elif choice == "1":
            setLanguageTag(config, 1)
        elif choice == "2":
            setLanguageTag(config, 2)
        elif choice == "x":
            sys.exit()
        else:
            print("\n Please enter a valid option, e.g. \"r\" for reading the XML file.\n")