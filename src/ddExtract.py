import re

def readFile(pathOptions, config):
    """Reads the input xml file, extracts text using regex to find text between "[ and "]]" e.g. [text goes here]].
    Each extracted text line is written to the specified output txt file. 

    Args:
        pathOptions (dataclass): A dataclass (struct) containing all paths and path names used in the program.
    """
    
    def Extract(line):
        """Helper function for readFile. 
        Searches for and extracts a valid substring from the XML input line.

        Args:
            line (str) The current line of the file.
        """
        
        match_obj = re.search(r"([^\[]+?)(?=]{2})", line) # Find text between "[ and "]]" e.g. [text goes here]]
        if match_obj is not None: # Found a valid string to extract
            open(pathOptions.OutTXTPath, "a", encoding="utf-8").write(str(match_obj.group(0))+"\n")
            pathOptions.extractedXML.append(line)

    lang = config.ExtractLanguageTag

    if(lang == ""): # Extract whole document
        for line in pathOptions.sanitizedXML:
            Extract(line)

    else: # Extract only within XML language tag belonging to "lang"
        is_extracting = False

        for line in pathOptions.sanitizedXML:
            if(is_extracting): 
                if(re.search(r"(<\/language)(?=\>)", line) is not None): # Found </language> while extracting. Thus, end of language section to extract is eached
                    return
                else:
                    Extract(line)

            if(re.search(r"(<language id=\")(?!>)", line) is not None): # Found a <language id= tag
                if(re.search((f"({lang})(?=\">)"), line) is not None): # The language in this tag is what we're looking for
                    is_extracting = True
                else:
                    is_extracting = False