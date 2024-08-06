import re
import traceback

from app.common.signal_bus import signalBus

from module.config.internal.app_args import AppArgs
from module.logger import logger
from module.tools.types.config import BaseConfig
from module.xml_tools import XMLParser
from module.xml_tools.regex_patterns import Pattern


class XMLSubstituter():
    _logger = logger

    def __init__(self, config: BaseConfig, parser: XMLParser) -> None:
        self._config = config
        self._parser = parser
        self._preview_XML = [] # type: list[str]
        self._failed_translations = [] # type: list[str]
        self._processColorCodes = True
        self._colorCodeDelim = ""
        self._colorCodeDelimSize = 0

    def substitute(self, write_lang_tag: str, parsed_xml_lines: list[str],
                   extracted_text: list[str], sanitized_xml: list[str],
                   localized_text: list[str]):
        """
        Substitutes data from the translated input file.
        Uses regex to insert input text between "[ and "]]" e.g. [text goes here]].
        The replacement scope is defined by XML language tags.
        """
        self._preview_XML.clear()
        self._failed_translations.clear()
        self._processColorCodes = self._config.getValue("colorCodeSep")
        self._colorCodeDelim = self._config.getValue("colorCodeDelim")
        self._colorCodeDelimSize = self._config.getValue("colorCodeDelimSize")
        try:
            is_substituting = False
            is_skipping = False

            for line in sanitized_xml:
                # Found language start tag "<language id="
                if re.search(Pattern.language_start, line):
                    # The language start tag is the one we're looking for
                    if re.search(f"({write_lang_tag})(?=\">)", line):
                        is_substituting = True
                        self._preview_XML.append(line + "\n") # Add language start tag (the language write tag)

                # Finished substituting. Start skipping lines that where overwritten by substituted text
                if is_skipping:
                    # Found language exit tag "</language"
                    if re.search(Pattern.language_exit, line):
                        is_skipping = False
                        self._preview_XML.append(line + "\n")
                    continue

                # We're inside the language write tag
                if is_substituting:
                    # Create all entries with translated text
                    for j, parsed_line in enumerate(parsed_xml_lines):
                        try:
                            # Handle case where the source text is empty
                            localization = localized_text[0] if extracted_text[j] else ""
                            # Insert translation into the source line
                            line_number = sanitized_xml.index(parsed_line) + 1
                            self._preview_XML.append(re.sub(Pattern.cdata, f"[CDATA[{self._preprocessLine(parsed_line, line_number, localization)}]]", parsed_line) + "\n")
                            # Only pop if the translation was used
                            if localization: localized_text.pop(0)
                        except IndexError:
                            # This should only occur for localized_text but both are present just in case
                            content = f"{"Extracted XML tags" if localized_text else "Localized text"} ran out of lines at {j}/{len(parsed_xml_lines)}"
                            self._logger.critical(content)
                            signalBus.xmlProcessException.emit("PE_OuttaLines", "Critical error", content)
                    is_substituting = False
                    is_skipping = True
                # We're not inside the language write tag. Copy line as-is
                else:
                    self._preview_XML.append(line + "\n")
        except Exception:
            trace = traceback.format_exc(limit=AppArgs.traceback_limit)
            content = "An unexpected exception occurred while translating XML"
            self._logger.error(content + "\n" + trace)
            signalBus.xmlProcessException.emit("PE_Translation", content, trace)

    def _preprocessLine(self, line: str, line_number: int, localization: str) -> str:
        repl = localization
        if self._processColorCodes:
            entry_id = self._parser.formatEntryID(line, line_number)
            entry_color_codes = self._parser.getEntryColorCodes()

            # Only process color codes if the current line has any
            if entry_id in entry_color_codes:
                start_colors = entry_color_codes[entry_id]["start_color"] # type: list[str]
                texts = entry_color_codes[entry_id]["text"] # type: list[str]
                foundTexts = localization.split(f"{self._colorCodeDelim * self._colorCodeDelimSize}")
                end_colors = entry_color_codes[entry_id]["end_color"] # type: list[str]

                if len(texts) != len(foundTexts):
                    self._failed_translations.append(line)
                # Apply color tags to the translated text
                # Note: Enable strict mode on zip to throw error if Iterables are not of equal size
                # (i.e. color codes can't be applied)
                repl = "".join(["".join(item) for item in zip(start_colors, foundTexts, end_colors)])
        return repl

    def getPreviewXML(self) -> list[str]:
        return self._preview_XML

    def getFailedTranslations(self) -> list[str]:
        return self._failed_translations