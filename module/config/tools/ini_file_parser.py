import re
from typing import IO

from module.exceptions import IniParseError
from module.tools.utilities import decodeInput


class IniFileParser():
    @classmethod
    def _getBool(self, value: str):
        if value.lower() == "true":
            return True
        elif value.lower() == "false":
            return False
        return None

    @classmethod
    def _getInt(self, value: str) -> int | str:
        """ Returns value if not int """
        try:
            value = int(value)
        except ValueError:
            pass
        return value

    @classmethod
    def load(self, fp: IO[str] | IO[bytes]) -> dict:
        """Read a .ini file and convert it to a Python object.

        Parameters
        ----------
        fp : IO[str] | IO[bytes]
            An IO file pointer.

        Returns
        -------
        dict
            The content of the file converted to a Python object.
        """
        file_content = decodeInput(fp.read()).splitlines()
        config = {}
        kv_list, sections, keys, values = [], [], [], []
        current_section = None
        #                         Contains 3 capture groups: Section, Key, Value
        pattern = re.compile(r"(?<!.)\[(\w*)\]|(?<!.)(\w+)\s{0,1}=(?(2)\s{0,1}(.*))")
        for i, line in enumerate(file_content):
            if line == "":
                continue
            match = re.search(pattern, line)
            #          Full match           Section             Key                 Value
            #print(f"{match.group(0)} | {match.group(1)} | {match.group(2)} | {match.group(3)}")
            if match is None:
                err_msg = f"Unexpected input '{line}' at line {i+1}"
                raise IniParseError(err_msg)

            found_section = match.group(1)
            key = match.group(2)
            value = match.group(3)

            if key is not None:
                keys.append(key)
                boolVal = self._getBool(value)
                values.append(boolVal if boolVal is not None else self._getInt(value))

            if found_section is not None:
                # Save the current section's key/value pairs
                if current_section is not None:
                    kv_list.append(dict(zip(keys, values)))
                    keys.clear()
                    values.clear()
                # Sectionless key/value pairs
                else:
                    config |= dict(zip(keys, values))
                    keys.clear()
                    values.clear()
                # Prepare the new section
                current_section = found_section
                sections.append(current_section)
        else:
            # Save the final section's key/value pairs
            if current_section is not None:
                kv_list.append(dict(zip(keys, values)))
            # Sectionless ini file
            else:
                config |= dict(zip(keys, values))

        config |= dict(zip(sections, kv_list))
        return config