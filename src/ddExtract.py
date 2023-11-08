import re

def readFile(pathOptions):
    xml_input = open(pathOptions.InXMLPath, "r", encoding="utf-8").read().splitlines() # splitlines() breaks each line after the newline (and includes it in the line)

    for line in xml_input:
        match_obj = re.search(r"([^\[]+?)(?=]{2})", line) # Search for all text in string
        if match_obj is not None: # Error checking to make sure the regex value is not empty
            open(pathOptions.OutTXTPath, "a", encoding="utf-8").write(str(match_obj.group(0))+"\n")






