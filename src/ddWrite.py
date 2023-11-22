import re

substitutions = 0 # Tracks number of substitutions made. Essential for backslashToString
txt_input = [] # List containing lines from the translated txt file

def writeFile(pathOptions, config):
    """Writes data from the translated input file to the specified output XML file. 
    Uses regex to insert input text between "[ and "]]" e.g. [text goes here]].
    The replacement scope is defined by XML language tags.

    Args:
        pathOptions (dataclass): A dataclass (struct) containing all paths and path names used in the program.

    """
    global txt_input
    txt_input = open(pathOptions.InTXTPath, "r", encoding="utf-8").read().splitlines() # splitlines() breaks each line after the newline
    
    extracted_xml = pathOptions.extractedXML
    lang = config.WriteLanguageTag

    if(lang == ""): # Extract and write whole document
        WriteAll(pathOptions)
    else: # Extract only within XML language tag belonging to "lang"
        is_substituting = False
        is_skipping = False
        
        for line in pathOptions.sanitizedXML:
            if(re.search(r"(<language id=\")(?!>)", line) is not None): # Found a <language id= tag.
                if(re.search(f"({lang})(?=\">)", line) is not None): # The language in that tag is what we're looking for
                    is_substituting = True
                    Write(pathOptions, line) # Writes the <language associated with the writing language tag
                    continue
                else:
                    is_substituting = False

            if(is_skipping): # Iterate over all the elements that where overwritten by text from extracting language tag
                if(re.search(r"(<\/language)(?=\>)", line) is not None):
                    is_skipping = False
                    Write(pathOptions, line) # Write </language> associated with the writing language tag
                    continue # Prevents duplication of </language>
                else:  
                    continue # Line is still within writing language tag from the original XML file
            
            if(is_substituting):
                while(len(extracted_xml) >= 1): # Keep writing until all lines in Translated Input have been used (measured by number of lines produced by the extraction procedure)
                    Write(pathOptions, extracted_xml[0], is_substituting)
                is_substituting = False
                is_skipping = True # Finished substituting. Start skipping lines within writing language tag from the original XML file
            else: # Writes everything except what's contained in the writing language tag scope (including the <language and </language>) 
                Write(pathOptions, line)

def Write(pathOptions, line: str, is_substituting: bool=False):
    """Helper function for writeFile. 
    If substituting, takes a string from the txt input line, replaces parts of it with a string, 
    and writes it to the output XML file. Otherwise, write the line unchanged.

    Args:
        pathOptions (dataclass): A dataclass (struct) containing all paths and path names used in the program.
        line (str): The XML line to write or substitute parts of with a string.
        is_substituting (bool): Defines whether the line should be substituted or not. Defaults to False.

    """
    # print(f"{len(pathOptions.extractedXML)} | {is_substituting} | {line}") For testing purposes
    if(is_substituting):
        if(re.search(r"([^\[]+?)(?=]{2})", line) is not None): # <entry id to substitute within writing language tag scope. (Found a string between "[" and "]]" to substitute)   
            match_obj_sub = re.sub(r"([^\[]+?)(?=]{2})", backslashToString, line) # Substitute found string with the equivalent, translated string
            open(pathOptions.OutXMLPath, "a", encoding="utf-8").write(match_obj_sub + "\n")
            pathOptions.extractedXML.pop(0) # Remove the string that has just been substituted.
        else: # Writes whitespace only
            open(pathOptions.OutXMLPath, "a", encoding="utf-8").write(line + "\n")
    else: # Writes everything that isn't an <entry id to substitute or whitespace
        open(pathOptions.OutXMLPath, "a", encoding="utf-8").write(line + "\n")


def WriteAll(pathOptions):
    """Writes from the entire input XML to the output XML, 
    substituting using the Translated Input txt file

    Args:
        pathOptions (dataclass): A dataclass (struct) containing all paths and path names used in the program.
    """
    i = 0
    for line in pathOptions.sanitizedXML:
        if(re.search(r"([^\[]+?)(?=]{2})", line) is not None): 
            match_obj_sub = re.sub(r"([^\[]+?)(?=]{2})", backslashToString, line) # Substitute this line 

            if(i == len(txt_input)):
                open(pathOptions.OutXMLPath, "a", encoding="utf-8").write(match_obj_sub) # End of document. Do not add newline
            else:
                open(pathOptions.OutXMLPath, "a", encoding="utf-8").write(match_obj_sub+"\n") # Not end of document. Add newline
            i += 1
        else:
            if(i > len(txt_input)):
                open(pathOptions.OutXMLPath, "a", encoding="utf-8").write(line) # End of document. Do not add newline
            else:
                open(pathOptions.OutXMLPath, "a", encoding="utf-8").write(line+"\n") # Not end of document. Add newline

def backslashToString(match_obj: object)->str:
    """Helper function for writeFile. 
    Simple toString function to prevent re.sub from interpretating backslashes in the replacement string as escape characters.\n
    The argument "match_obj" is a requirement for this function, although it's unused.
    To see why this is the case, view the docs: https://docs.python.org/3/library/re.html#re.sub

    Args:
        match_obj (object): The match object as returned by re.

    Returns:
        str: The string from the translated input file (casted to string to be safe)
    """
    global substitutions
    if(substitutions < len(txt_input)):
        #print(f"{substitutions}: {txt_input[substitutions]}") # For testing purposes
        string = str(txt_input[substitutions])
        substitutions += 1
        return string
    else:
        print(f"Warning: substitutions ({substitutions}) < len(txt_input) ({len(txt_input)}) is {substitutions < len(txt_input)}. This will have unintended consequences!")
        return ""