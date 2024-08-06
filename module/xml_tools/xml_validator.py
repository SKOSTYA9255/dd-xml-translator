import re
import traceback
from typing import Any, Iterable

from app.common.signal_bus import signalBus

from module.config.internal.app_args import AppArgs
from module.logger import logger
from module.tools.types.config import BaseConfig
from module.tools.utilities import formatListForDisplay
from module.xml_tools import XMLParser, XMLSubstituter
from module.xml_tools.regex_patterns import Pattern


class XMLValidator():
    _logger = logger

    def __init__(self, config: BaseConfig, parser: XMLParser,
                 substituter: XMLSubstituter) -> None:
        self._config = config
        self._parser = parser
        self._substituter = substituter

    def _parseEntryIDs(self, preview: list[str], lang_tag: str) -> list[str]:
        entryIDs = [] # type: list[str]
        try:
            begin_search = False
            for line in preview:
                if begin_search:
                    # Found language exit tag "</language". Thus, language extraction is complete
                    if re.search(Pattern.language_exit, line):
                        break
                    else:
                        try:
                            entryIDs.append(self._parser.formatEntryID(line, ""))
                        except TypeError:
                            # No entry ID was found
                            pass

                # Found language start tag "<language id="
                if re.search(Pattern.language_start, line):
                    # The language start tag is the one we're looking for
                    if re.search((f"({lang_tag})(?=\">)"), line):
                        begin_search = True
            return entryIDs
        except Exception:
            trace = traceback.format_exc(limit=AppArgs.traceback_limit)
            msg = "An unexpected exception occurred while validating XML"
            self._logger.error(msg + "\n" + trace)
            signalBus.xmlProcessException.emit("PE_Validation", msg, trace)

    def difference(self, source: Iterable[Any], target: Iterable[Any]) -> list[str]:
        """ Get difference between source and target.
            I.e. find all values in source which are not in target
        """
        diff = []
        for item in source:
            if item not in target:
                diff.append(item)
        return diff

    def validatePreview(self, preview: list[str], extract_lang_tag: str, write_lang_tag: str) -> None:
        try:
            isValid, showErrors = True, False
            extract_entryIDs = self._parseEntryIDs(preview, extract_lang_tag)
            write_entryIDs = self._parseEntryIDs(preview, write_lang_tag)
            diff = self.difference(extract_entryIDs, write_entryIDs)

            # Empty set
            if not extract_entryIDs or not write_entryIDs:
                isValid = False

            # The write_entryIDs are missing entries compared to extract_entryIDs
            if diff:
                isValid, showErrors = False, True
                message_size = self._config.getValue("messageSize")
                entry_grammar = "entries" if len(diff) != 1 else "entry"
                msg = f"Missing {len(diff)} {write_lang_tag} {"(source)" if extract_lang_tag == write_lang_tag else ""}{entry_grammar}"
                self._logger.warning(f"{msg}:\n  {formatListForDisplay(diff, message_size, join_string="\n  ")}")
                signalBus.xmlValidationError.emit("VE_E1_BrokenTranslation", msg, formatListForDisplay(diff, message_size))

            # Failed to translate some entries
            _failed_translations = self._substituter.getFailedTranslations()
            if _failed_translations:
                isValid, showErrors = False, True
                line_positions = self._parser.getInputLinePositions()
                fail_size = len(_failed_translations)
                message_size = self._config.getValue("messageSize")
                entry_grammar = "entries" if fail_size != 1 else "entry"
                msg = f"Failed to translate {fail_size} {entry_grammar}"
                content = [f"Line {line_positions[val]}: {re.search(Pattern.entry_id, val)[1]}" for val in _failed_translations]
                self._logger.warning(f"{msg}:\n  {formatListForDisplay(content, message_size, join_string="\n  ")}")
                signalBus.xmlValidationError.emit("VE_W1_FailTranslation", msg, formatListForDisplay(content, message_size))

            signalBus.xmlPreviewInvalid.emit(isValid, showErrors)
        except Exception:
            trace = traceback.format_exc(limit=AppArgs.traceback_limit)
            msg = "An unexpected exception occurred while validating XML"
            self._logger.error(msg + "\n" + trace)
            signalBus.xmlProcessException.emit("PE_Validate", msg, trace)