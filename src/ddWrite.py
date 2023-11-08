import re



def writeFile(pathOptions):
    xml_input = open(pathOptions.InXMLPath, "r", encoding="utf-8").read().splitlines() # splitlines() breaks each line after the newline (and includes it in the line)
    xml_output = open(pathOptions.OutXMLPath, "r", encoding="utf-8").read().splitlines()
    txt_input = open(pathOptions.InTXTPath, "r", encoding="utf-8").read().splitlines() 
    txt_output = open(pathOptions.OutTXTPath, "r", encoding="utf-8").read().splitlines() 

    i = 0
    for line in xml_input:
        if(i < len(txt_input)):
            match_obj = re.search(r"([^\[]+?)(?=]{2})", line) # Search for all text in string

            if match_obj is not None: # Error checking to make sure the regex value is not empty
                match_obj_sub = re.sub(r"([^\[]+?)(?=]{2})", txt_input[i], line)
                # print(match_obj_sub) # For testing purposes

                if(i == len(txt_input)):
                    open(pathOptions.OutXMLPath, "a", encoding="utf-8").write(match_obj_sub)
                else:
                    open(pathOptions.OutXMLPath, "a", encoding="utf-8").write(match_obj_sub+"\n")
            #print(f"{i} + {i < len(txt_input)}") # For testing purposes
                i += 1
            else:
                if(i == len(txt_input)):
                    open(pathOptions.OutXMLPath, "a", encoding="utf-8").write(line)
                else:
                    open(pathOptions.OutXMLPath, "a", encoding="utf-8").write(line+"\n")
    # Compare lines in txt_input vs text_output and send warning if they differ