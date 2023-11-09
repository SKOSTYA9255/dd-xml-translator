import re

# TODO: Make this function universally applicable by changing parameters to something like "inputfile" "outputfile"
def readFile(pathOptions):
    """Reads the input xml file, extracts text using regex to find text between "[ and "]]" e.g. [text goes here]].
    Each extracted text line is written to the specified output txt file. 

    Args:
        pathOptions (dataclass): A dataclass (struct) containing all paths and path names used in the program.
    """
    xml_input = open(pathOptions.InXMLPath, "r", encoding="utf-8").read().splitlines() # splitlines() breaks each line after the newline (and includes it in the line)

    for line in xml_input:
        match_obj = re.search(r"([^\[]+?)(?=]{2})", line) # Search for all text in string
        if match_obj is not None: # Error checking to make sure the regex value is not empty
            open(pathOptions.OutTXTPath, "a", encoding="utf-8").write(str(match_obj.group(0))+"\n")






