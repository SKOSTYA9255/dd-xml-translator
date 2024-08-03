import re
import traceback

from app.common.signal_bus import signalBus

from module.config.internal.app_args import AppArgs
from module.logger import logger
from module.tools.types.general import StrPath


class XMLParser():
    _logger = logger

    def __init__(self) -> None:
        self._sanitized_input = [] # type: list[str]
        self._extracted_text = []  # type: list[str]
        self._parsed_lines = []    # type: list[str]

    def sanitizeXML(self, location: StrPath) -> list[str]:
        self._sanitized_input.clear()
        self._extracted_text.clear()
        self._parsed_lines.clear()
        try:
            raw_input = open(location, "r", encoding="utf-8").read().splitlines()
            sanitized_list = []
            prev_lines = []
            begin_entry_found = False
            prev_line_is_begin_language = False

            for line in raw_input:
                if line.strip() == "":
                    continue

                if re.search(r"(<language id=\")(?!>)", line):
                    prev_line_is_begin_language = True
                elif prev_line_is_begin_language and re.search(r"(<\/language)(?=\>)", line):
                    sanitized_list.append("")
                    prev_line_is_begin_language = False
                else:
                    prev_line_is_begin_language = False

                if re.search(r"(<entry)", line) and re.search(r"(<\/entry>)", line): # This line has <entry and </entry
                    sanitized_list.append(line)
                    continue

                if re.search(r"(<entry)", line): # This line has <entry
                    begin_entry_found = True

                if begin_entry_found: # /entry was found in a previous iteration (not necessarily the last one)
                    if re.search(r"(<\/entry>)", line): # This line has </entry
                        temp_line = ""

                        for prev in prev_lines:
                            temp_line += prev

                        temp_line += line
                        sanitized_list.append(temp_line)
                        prev_lines.clear()
                        begin_entry_found = False
                    else: # This line does not have </entry
                        prev_lines.append(line)
                elif re.search(r"(<\/entry>)", line) is None: # This line is of no concern for sanitizing. Line is e.g. <?xml version="1.0" encoding="UTF-8"?>
                    sanitized_list.append(line)

            # For testing purposes
            #for line in sanitized_list:
            #    open("SANIT.xml", "a", encoding="utf-8").write(line+"\n")
            self._sanitized_input = sanitized_list
            return sanitized_list
        except Exception:
            trace = traceback.format_exc(limit=AppArgs.traceback_limit)
            msg = "An unexpected exception occurred while sanitizing XML"
            self._logger.error(msg + "\n" + trace)
            signalBus.xml_process_exception.emit(msg, trace)

    def _extract(self, line: str) -> None:
        """
        Searches for and extracts a valid substring from the XML input line.

        Args:
            line (str): The current line of the file.
        """
        # TODO: This search does not account for []] in the string (inside CDATA[]])
        match_obj = re.search(r"([^\[]+?)(?=]{2})", line)
        if match_obj: # Find text between "[ and "]]" e.g. [text goes here]]
            self._parsed_lines.append(line)
            self._extracted_text.append(match_obj[0] + "\n") # TODO: Use for extractor reference in ddWrite.

    def parse(self, location: StrPath, extract_lang_tag: str) -> None:
        """
        NOTE: The file must be specified in the config!
        -----
        Reads the input xml file, extracts text using regex to find text between "[ and "]]" e.g. [text goes here]].
        Each extracted text line is written to the specified output txt file.
        """
        sanitized_input = self.sanitizeXML(location)
        try:
            is_extracting = False
            for line in sanitized_input:
                if line.strip() == "":
                    continue

                if is_extracting:
                    if re.search(r"(<\/language)(?=\>)", line): # Found </language> while extracting. Thus, end of language section to extract is reached
                        return
                    else:
                        self._extract(line)

                if re.search(r"(<language id=\")(?!>)", line): # Found a <language id= tag
                    if re.search((f"({extract_lang_tag})(?=\">)"), line): # The language in this tag is what we're looking for
                        is_extracting = True
                    else:
                        is_extracting = False
        except Exception:
            trace = traceback.format_exc(limit=AppArgs.traceback_limit)
            msg = "An unexpected exception occurred while parsing XML"
            self._logger.error(msg + "\n" + trace)
            signalBus.xml_process_exception.emit(msg, trace)

    def getSanitizedInput(self) -> list[str]:
        return self._sanitized_input

    def getExtractedText(self) -> list[str]:
        return self._extracted_text

    def getParsedLines(self) -> list[str]:
        return self._parsed_lines