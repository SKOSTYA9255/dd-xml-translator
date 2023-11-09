import re



def writeFile(pathOptions):
    """Writes data from the translated input file to the specified output XML file. 
    Uses regex to insert input text between "[ and "]]" e.g. [text goes here]].

    Args:
        pathOptions (dataclass): A dataclass (struct) containing all paths and path names used in the program.

    """
    xml_input = open(pathOptions.InXMLPath, "r", encoding="utf-8").read().splitlines() # splitlines() breaks each line after the newline (and includes it in the line)
    txt_input = open(pathOptions.InTXTPath, "r", encoding="utf-8").read().splitlines() 


    def backslashToString(match_obj: object)->str:
        """Simple toString function to prevent re.sub from interpretating backslashes in the replacement string as escape characters.\n
        The argument "match_obj" is a requirement for this function, although it's unused.
        To see why this is the case, view the docs: https://docs.python.org/3/library/re.html#re.sub

        Args:
            match_obj (object): The match object as returned by re.

        Returns:
            str: The string from the translated input file (casted to string to be safe)
        """
        return str(txt_input[i])

    i = 0
    for line in xml_input:
        match_obj = re.search(r"([^\[]+?)(?=]{2})", line) # Search for all text in string

        if match_obj is not None: # Error checking to make sure the regex value is not empty
            match_obj_sub = re.sub(r"([^\[]+?)(?=]{2})", backslashToString, line)
            # print(match_obj_sub) # For testing purposes

            if(i == len(txt_input)):
                open(pathOptions.OutXMLPath, "a", encoding="utf-8").write(match_obj_sub)
            else:
                open(pathOptions.OutXMLPath, "a", encoding="utf-8").write(match_obj_sub+"\n")
        #print(f"{i} + {i < len(txt_input)}") # For testing purposes
            i += 1
        else:
            if(i > len(txt_input)):
                open(pathOptions.OutXMLPath, "a", encoding="utf-8").write(line)
            else:
                open(pathOptions.OutXMLPath, "a", encoding="utf-8").write(line+"\n")
    # Compare lines in txt_input vs text_output and send warning if they differ


