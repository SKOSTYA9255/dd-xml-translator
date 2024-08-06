import os
import re
import traceback

from app.common.signal_bus import signalBus

from module.config.internal.app_args import AppArgs
from module.logger import logger
from module.tools.types.general import StrPath
from module.tools.types.config import BaseConfig
from module.tools.utilities import formatListForDisplay
from module.xml_tools.regex_patterns import Pattern


class XMLParser():
    _logger = logger

    def __init__(self, config: BaseConfig) -> None:
        self._config = config
        # The input file sanitized
        self._sanitized_input = [] # type: list[str]
        # Extracted part of the full line parsed
        self._extracted_text = []  # type: list[str]
        # Full line extracted
        self._parsed_lines = []    # type: list[str]
        # Keep track of malformed CDATA entries
        self._malformed_entries = {} # type: dict[str, list[str]]
        # Keep track of line positions of malformed CDATA entries in input
        self._input_line_positions = {} # type: dict[str, str]
        # Used to extract color codes from CDATA entries
        self._entry_color_codes = {} # type: dict[str, dict[str: list[str]]]

    def sanitizeXML(self, location: StrPath) -> list[str]:
        self._sanitized_input.clear()
        self._extracted_text.clear()
        self._parsed_lines.clear()
        self._malformed_entries = {"fixed": [], "failed": []}
        self._input_line_positions.clear()

        xml_file = os.path.split(location)[1]
        try:
            raw_input = open(location, "r", encoding="utf-8").read().splitlines()
            sanitized_list = [] # type: list[str]
            multiple_line_entry = [] # type: list[str]
            begin_entry_found = False
            end_entry_found = False
            begin_entry_line = 0

            for i, line in enumerate(raw_input):
                if line.strip() == "":
                    continue

                # Found entry start tag "<entry"
                if re.search(Pattern.entry_start, line):
                    begin_entry_found = True

                # Found entry exit tag "</entry"
                if re.search(Pattern.entry_exit, line):
                    end_entry_found = True

                # We're inside an entry tag
                if begin_entry_found:
                    if not begin_entry_line: begin_entry_line = i+1
                    if end_entry_found:
                        multiple_line_entry.append(line)
                        # Construct the entire line (in case of multi-line entry)
                        # Remove whitespaces on subsequent lines in multi-line entries
                        completed_line = "".join([val if i == 0 else val.strip() for i, val in enumerate(multiple_line_entry)])

                        # Record the line's position in the input XML
                        self._input_line_positions |= {completed_line: f"{begin_entry_line}" if begin_entry_line == i+1 else f"{begin_entry_line}-{i+1}"}

                        # Ensure line is well-formed and add to list
                        sanitized_list.append(self._ensureWellformedLine(completed_line))

                        # Cleanup
                        multiple_line_entry.clear()
                        begin_entry_found = False
                        end_entry_found = False
                        begin_entry_line = 0
                    # This line does not have an exit entry tag on this line (this entry spans multiple lines!)
                    else:
                        multiple_line_entry.append(line)
                # We're not inside an entry tag. Copy line as-is
                elif not end_entry_found:
                    sanitized_list.append(line)

            ### TESTING ###
            if self._config.getValue("debugXML"):
                from pathlib import Path
                with open(Path(AppArgs.app_dir, "SANIT.xml"), "w", encoding="utf-8") as file:
                    file.writelines("\n".join(sanitized_list))
            ###############

            # Show any detected malformed entries
            if self._malformed_entries["fixed"]:
                message_size = self._config.getValue("messageSize")
                entry_grammar = "entries" if len(self._malformed_entries["fixed"]) != 1 else "entry"
                msg = f"Fixed {len(self._malformed_entries["fixed"])} malformed {entry_grammar} in '{xml_file}'"
                content = [f"Line {self._input_line_positions[val]}: {re.search(Pattern.entry_id, val)[1]}" for val in self._malformed_entries["fixed"]]
                signalBus.xmlValidationError.emit("MALFIX_Sanitize", msg, formatListForDisplay(content, message_size))
                self._logger.info(f"{msg}:\n  {formatListForDisplay(content, message_size, join_string="\n  ")}")
            elif self._malformed_entries["failed"]:
                message_size = self._config.getValue("messageSize")
                entry_grammar = "entries" if len(self._malformed_entries["failed"]) != 1 else "entry"
                msg = f"Failed to fix {len(self._malformed_entries["failed"])} malformed {entry_grammar} in '{xml_file}'"
                content = [f"Line {self._input_line_positions[val]}: {re.search(Pattern.entry_id, val)[1]}" for val in self._malformed_entries["failed"]]
                signalBus.xmlValidationError.emit("MAL_Sanitize", msg, formatListForDisplay(content, message_size))
                self._logger.warning(f"{msg}:\n  {formatListForDisplay(content, message_size, join_string="\n  ")}")

            self._sanitized_input = sanitized_list
            return sanitized_list
        except Exception:
            trace = traceback.format_exc(limit=AppArgs.traceback_limit)
            msg = "An unexpected exception occurred while sanitizing XML"
            self._logger.error(msg + "\n" + trace)
            signalBus.xmlProcessException.emit("PE_Sanitize", msg, trace)

    def _ensureWellformedLine(self, line: str) -> str:
        if re.search(Pattern.cdata, line):
            # Well-formed
            return line

        malformed_cdata = re.search(Pattern.malformed_cdata, line)
        if malformed_cdata:
            # MALFORMED!
            self._malformed_entries["fixed"].append(line)
            return re.sub(Pattern.cdata_fix, f"><![CDATA[{malformed_cdata[1]}]]", line)

        # FAILED TO FIX MALFORMED LINE!
        self._malformed_entries["failed"].append(line)
        return line

    def _extract(self, line: str, line_number: int, colorCodeOptions: tuple) -> None:
        """
        Searches for and extracts a valid substring from the XML input line.

        Args:
            line (str): The current line of the file.
        """
        match_obj = re.search(Pattern.cdata, line)
        if match_obj:
            text = match_obj[1]

            # Enable color code exclusion
            if colorCodeOptions[0]:
                entry_id = self.formatEntryID(line, line_number)

                # Split text and color code tags
                matches = [val for val in re.finditer(Pattern.color_codes, text)]
                for match in matches:
                    start_color = match.group("start_color")
                    text_ = match.group("text")
                    end_color = match.group("end_color")

                    # Only add text longer than this. Except if only 1 tag exists, then add regardless.
                    # Smaller sized delimitors (or the values themselves) get lost in translation (literally)
                    if len(matches) == 1 or len(text_) >= colorCodeOptions[1]:
                        if entry_id not in self._entry_color_codes:
                            self._entry_color_codes |= {entry_id: {"start_color": [], "text": [], "end_color": []}}
                        self._entry_color_codes[entry_id]["start_color"].append(start_color)
                        self._entry_color_codes[entry_id]["text"].append(text_)
                        self._entry_color_codes[entry_id]["end_color"].append(end_color)

                if entry_id in self._entry_color_codes and self._entry_color_codes[entry_id]["text"]:
                    text = f" {colorCodeOptions[2] * colorCodeOptions[3]} ".join(self._entry_color_codes[entry_id]["text"])
            self._parsed_lines.append(line)
            self._extracted_text.append(text)

    def parse(self, location: StrPath, extract_lang_tag: str) -> None:
        """
        NOTE: The file must be specified in the config!
        -----
        Reads the input xml file, extracts text using regex to find text between "[ and "]]" e.g. [text goes here]].
        Each extracted text line is written to the specified output txt file.
        """
        self._entry_color_codes = {}
        sanitized_input = self.sanitizeXML(location)
        colorCodeOptions = (
            self._config.getValue("colorCodeSep"),
            self._config.getValue("colorCodeSepLength"),
            self._config.getValue("colorCodeDelim"),
            self._config.getValue("colorCodeDelimSize")
        )
        try:
            is_extracting = False
            for i, line in enumerate(sanitized_input):
                if line.strip() == "":
                    continue

                if is_extracting:
                    # Found language exit tag "</language". Thus, language extraction is complete
                    if re.search(Pattern.language_exit, line):
                        break
                    else:
                        self._extract(
                            line=line,
                            line_number=i + 1,
                            colorCodeOptions=colorCodeOptions
                        )

                # Found language start tag "<language id="
                if re.search(Pattern.language_start, line):
                    # The language start tag is the one we're looking for
                    if re.search((f"({extract_lang_tag})(?=\">)"), line):
                        is_extracting = True
        except Exception:
            trace = traceback.format_exc(limit=AppArgs.traceback_limit)
            msg = "An unexpected exception occurred while parsing XML"
            self._logger.error(msg + "\n" + trace)
            signalBus.xmlProcessException.emit("PE_Parsing", msg, trace)

    def formatEntryID(self, line: str, identifier: int | str) -> str:
        prep = f"{identifier}_" if identifier != "" else ""
        return f"{prep}{re.search(Pattern.entry_id, line)[1]}"

    def getSanitizedInput(self) -> list[str]:
        return self._sanitized_input

    def getExtractedText(self) -> list[str]:
        return self._extracted_text

    def getParsedLines(self) -> list[str]:
        return self._parsed_lines

    def getInputLinePositions(self) -> dict[str, str]:
        return self._input_line_positions

    def getEntryColorCodes(self) -> dict[str, dict[str: list[str]]]:
        return self._entry_color_codes