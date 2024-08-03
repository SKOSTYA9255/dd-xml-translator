from copy import deepcopy
import re
import traceback

from app.common.signal_bus import signalBus

from module.config.internal.app_args import AppArgs
from module.logger import logger


class XMLSubstituter():
    _logger = logger

    def __init__(self) -> None:
        self._preview_XML = [] # type: list[str]

    def substitute(self, write_lang_tag: str, parsed_xml_lines: list[str],
                   sanitized_xml: list[str], localized_text: list[str]):
        """
        Substitutes data from the translated input file.
        Uses regex to insert input text between "[ and "]]" e.g. [text goes here]].
        The replacement scope is defined by XML language tags.
        """
        self._preview_XML.clear()
        try:
            parsed_xml_lines = deepcopy(parsed_xml_lines) # Prevent reference object from being emptied
            is_substituting = False
            is_skipping = False

            for line in sanitized_xml:
                if re.search(r"(<language id=\")(?!>)", line): # Found a <language id= tag.
                    if re.search(f"({write_lang_tag})(?=\">)", line): # The language in that tag is what we're looking for
                        is_substituting = True
                        self._preview_XML.append(line + "\n") # Writes the <language associated with the writing language tag
                        continue
                    else:
                        is_substituting = False

                if is_skipping: # Iterate over all the elements that where overwritten by text from extracting language tag
                    if re.search(r"(<\/language)(?=\>)", line):
                        is_skipping = False
                        self._preview_XML.append(line + "\n") # Write </language> associated with the writing language tag
                        continue # Prevents duplication of </language>
                    else:
                        continue # Line is still within writing language tag from the original XML file

                if is_substituting:
                    # Keep writing until all lines in Translated Input have been used
                    # (measured by number of lines produced by the extraction procedure)
                    while parsed_xml_lines:
                        try:
                            # TODO: This sub does not account for []] in the string (inside CDATA[]])
                            substitute = re.sub(r"([^\[]+?)(?=]{2})", localized_text[0], parsed_xml_lines[0])
                            if substitute:
                                self._preview_XML.append(substitute + "\n")
                                parsed_xml_lines.pop(0)
                                localized_text.pop(0)
                        except IndexError:
                            # This should only occur for localized_text but both are present just in case
                            msg = f"{"extracted_xml_tags" if localized_text else "localized_text"} ran out of lines!"
                            self._logger.critical(msg)
                            signalBus.xml_process_exception.emit("Critical error", msg)
                            return
                    is_substituting = False
                    is_skipping = True # Finished substituting. Start skipping lines within writing language tag from the original XML file
                else:
                    # Writes everything except what's contained in the writing language tag scope (including the <language and </language>)
                    self._preview_XML.append(line + "\n")
        except Exception:
            trace = traceback.format_exc(limit=AppArgs.traceback_limit)
            msg = "An unexpected exception occurred while translating XML"
            self._logger.error(msg + "\n" + trace)
            signalBus.xml_process_exception.emit(msg, trace)

    def getPreviewXML(self) -> list[str]:
        return self._preview_XML