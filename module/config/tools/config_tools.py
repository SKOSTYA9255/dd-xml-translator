import os
import shutil
import tomlkit
import tomlkit.exceptions
import json
import traceback

from pathlib import Path
from pydantic import ValidationError
from typing import Any, Callable, Literal, Mapping, Optional

from module.config.internal.app_args import AppArgs
from module.config.tools.ini_file_parser import IniFileParser
from module.exceptions import IniParseError, InvalidMasterKeyError, MissingFieldError
from module.logger import logger
from module.tools.types.general import Model, StrPath, NestedDict
from module.tools.utilities import formatValidationError

_logger_ = logger

def writeConfig(config: dict | Model, dst_path: StrPath, comments: Optional[Any]=None,
                sort: bool=False) -> None:
    """
    Convert and write a Python config object to config files of different types.
    Supports: toml, ini, json.

    Parameters
    ----------
    config : dict | Model
        The Python config object to convert and write to a file.
        Can be an instance of a validation model.

    dst_path : StrPath
        Path-like object pointing to a supported config file.
        Note: the file does not have to exist.

    comments : Any, optional
        Comments associated with the settings in the config which will
        be written to the config file alongside the config.
        Note: Does not currently work.
        By default None.

    sort : bool, optional
        Sort the Python config object by section name before writing.
        By default False.
    """
    dst_dir = Path(os.path.dirname(dst_path))
    file = os.path.split(dst_path)[1]
    extension = os.path.splitext(dst_path)[1].strip(".")
    try:
        if isinstance(config, Model):
            config = config.model_dump()
        if sort and isinstance(config, dict):
            config = dict(sorted(config.items())) # Sort the dictionary by section, i.e. top-level keys
        if not dst_dir.exists():
            dst_dir.mkdir()

        if extension.lower() == "toml":
            _generateTOMLconfig(config, dst_path, comments)
        elif extension.lower() == "ini":
            _generateINIconfig(config, dst_path)
        elif extension.lower() == "json":
            _generateJSONConfig(config, dst_path)
        else:
            _logger_.warn(f"Cannot write unsupported file '{file}'")
    except Exception:
        _logger_.error(f"Failed to write {file} to '{dst_path}'\n" + traceback.format_exc(limit=AppArgs.traceback_limit))
        raise


def _generateTOMLconfig(config: dict, dstPath: StrPath, comments: Any) -> None:
    """Convert a Python config object to the '.toml'-format and write it to a '.toml' file.

    Parameters
    ----------
    config : dict
        A Python config object.

    dstPath : StrPath
        Path-like object pointing to a toml file.
        Note: the file does not have to exist.

    comments : Any
        Comments associated with the settings in the config.
    """
    fileName = os.path.split(dstPath)[1]
    doc = tomlkit.document()
    prevWasComment = False
    for section, keys in config.items():
        table = tomlkit.table()
        for i, key in enumerate(keys):
            if comments:
                if hasattr(comments, key):
                    prevWasComment = True
                    if i != 0: # Do not make newline right after section
                        table.add(tomlkit.nl())
                    for comment in comments.__getattribute__(key): # Write multi-line comments
                        table.add(tomlkit.comment(comment))
                elif prevWasComment:
                    table.add(tomlkit.nl())
            prevWasComment = False
            table.append(key, keys[key])
        doc.append(section, table)

    with open(dstPath, "w", encoding="utf-8") as file:
        _logger_.debug(f"Writing '{fileName}' to '{dstPath}'")
        tomlkit.dump(doc, file)


def _generateINIconfig(config: dict, dstPath: StrPath) -> None:
    """Convert a Python config object to the '.ini'-format and write it to a '.ini' file.

    Parameters
    ----------
    config : dict
        A Python config object.

    dstPath : StrPath
        Path-like object pointing to a ini file.
        Note: the file does not have to exist.
    """
    iniConfig = ""
    fileName = os.path.split(dstPath)[1]
    for section in config:
        keys = config[section]
        table = ""
        for key in keys:
            table += f"{key} = {keys[key]}\n"
        table += "\n"
        iniConfig += f"[{section}]" + "\n" + table

    with open(dstPath, "w", encoding="utf-8") as file:
        _logger_.debug(f"Writing '{fileName}' to '{dstPath}'")
        file.write(iniConfig)


def _generateJSONConfig(config: dict, dstPath: StrPath) -> None:
    """Convert a Python config object to the '.json'-format and write it to a '.json' file.

    Parameters
    ----------
    config : dict
        A Python config object
    dstPath : StrPath
        Path-like object pointing to a JSON file.
        Note: the file does not have to exist.
    """
    fileName = os.path.split(dstPath)[1]
    with open(dstPath, "w", encoding="utf-8") as file:
        _logger_.debug(f"Writing '{fileName}' to '{dstPath}'")
        file.write(json.dumps(config, indent=4))


def backupConfig(srcPath: StrPath) -> None:
    """Creates a backup of the file at the supplied path, overwriting any existing backup.

    Parameters
    ----------
    srcPath : StrPath
        Path-like object pointing to a file.
    """
    try:
        srcPath = Path(srcPath)
        file = os.path.split(srcPath)[1]
        if srcPath.exists():
            configDst = Path(f"{srcPath}.bak")
            _logger_.debug(f"Creating backup of '{file}' to '{configDst}'")
            shutil.copyfile(srcPath, configDst)
        else:
            _logger_.warn(f"Cannot create backup of '{file}'. Path '{srcPath}' does not exist")
    except TypeError: # If input path is None
        _logger_.error(f"Failed to create backup of '{srcPath}'\n"
                       + traceback.format_exc(limit=AppArgs.traceback_limit))


def checkMissingFields(raw_config: dict, internal_config: dict) -> None:
    """Compare the raw_config against the internal_config for missing sections/settings and vice versa.

    Parameters
    ----------
    raw_config : dict
        A config read from a file.

    internal_config : dict
        The internal version of the raw config file.

    config_name : str
        The name of the config file.

    Raises
    ------
    MissingFieldError
        If any missing or unknown sections/settings are found.
    """
    allErrors, sectionErrors, fieldErrors = [], [], []
    for section in internal_config: # Check sections
        sectionExistsInConfig = section in raw_config
        if not sectionExistsInConfig:
            sectionErrors.append(f"Missing section '{section}'")
        else:
            for setting in internal_config[section]: # Check settings in a section
                if sectionExistsInConfig and setting not in raw_config[section]:
                    fieldErrors.append(f"Missing setting '{setting}' in section '{section}'")

    for section in raw_config: # Check sections
        sectionShouldExist = section in internal_config
        if not sectionShouldExist:
            if isinstance(raw_config[section], dict):
                sectionErrors.append(f"Unknown section '{section}'")
            else:
                # Sectionless settings are interpreted as sections by the parser
                fieldErrors.append(f"Setting '{section}' does not belong to a section")
        else:
            for setting in raw_config[section]: # Check settings in a section
                if sectionShouldExist and setting not in internal_config[section]:
                    fieldErrors.append(f"Unknown setting '{setting}' in section '{section}'")
    # Ensure all section errors are displayed first
    allErrors.extend(sectionErrors)
    allErrors.extend(fieldErrors)
    if len(allErrors) > 0:
        raise MissingFieldError(allErrors)


def retrieveDictValue(d: dict, key: str, parent_key: Optional[str]=None, default: Any=None,
                      get_parent_key: Optional[bool]=False) -> Any:
    """Return first value found.
    If key does not exists, return default.

    Has support for defining search scope with the parent key.
    A value will only be returned if it is within parent key's scope

    Parameters
    ----------
    d : dict
        The dictionary to search for key.

    key : str
        The key to search for.

    parent_key : str, optional
        Limit the search scope to the children of this key.

    default : Any, optional
        The value to return if the key was not found.
        Defaults to None.

    get_parent_key : bool, optional
        Return the immediate parent of the supplied key.
        Defaults to False.

    Returns
    -------
    Any
        The value mapped to the key, if it exists. Otherwise, default.

    tuple[Any, str]
        If *get_parent_key* is True
        [0]: The value mapped to the key, if it exists. Otherwise, default.
        [1]: The immediate parent of the supplied key, if any. Otherwise, None.
    """
    stack = [iter(d.items())]
    parent_keys = []
    found_value = default
    immediate_parent = None
    while stack:
        for k, v in stack[-1]:
            if k == key:
                if get_parent_key:
                    immediate_parent = parent_keys[-1]
                if parent_key:
                    if parent_key in parent_keys:
                        found_value = v
                        stack.clear()
                        break
                else:
                    found_value = v
                    stack.clear()
                    break
            elif isinstance(v, dict):
                stack.append(iter(v.items()))
                parent_keys.append(k)
                break
        else:
            stack.pop()
            if parent_keys:
                parent_keys.pop()
    return (found_value, immediate_parent) if get_parent_key else found_value


def insertDictValue(input: dict, key: str, value: Any, parent_key: Optional[str]=None) -> list | None:
    """
    Recursively look for key in input.
    If found, replace the original value with the provided value and return the original value.

    Has support for defining search scope with the parent key.
    Value will only be returned if it is within parent key's scope.

    Causes side-effects!
    ----------
    Modifies input in-place (i.e. does not return input).

    Parameters
    ----------
    input : dict
        The dictionary to search in.

    key : str
        The key to look for.

    value : Any
        The value to insert.

    parent_key : str, optional
        Limit the search scope to the children of this key.
        By default None.

    Returns
    -------
    list | None
        The replaced old value, if found. Otherwise, None.
    """
    old_value = []  # Modified in-place by traverseDict
    parentKeys = []
    def traverseDict(_input: dict, _key, _value, _parent_key) -> list | None:
        for k, v in _input.items():
            if isinstance(v, dict):
                parentKeys.append(k)
                traverseDict(v, _key, _value, _parent_key)
            elif k == _key:
                if parent_key:
                    if _parent_key in parentKeys:
                        _input[k] = _value
                        old_value.append(v)
                        break
                _input[k] = _value
                old_value.clear()
                old_value.append(v)
                break
    traverseDict(input, key, value, parent_key)
    return old_value if len(old_value) > 0 else None


def loadConfig(config_name: str, config_path: StrPath, validator: Callable[[Mapping], dict[str, Any]],
                internal_config: Optional[dict[str, Any]]=None, doWriteConfig: bool=True,
                retries: int=1) -> tuple[dict[str, Any] | None, bool]:
    """Read and validate the config file residing at the supplied config path.

    Parameters
    ----------
    config_name : str
        The name of the config

    config_path : StrPath
        Path-like object pointing to a config file.

    validator : Callable[[Mapping], dict]
        A callable that validates the specific config.
        Must take the raw config as input and return a validated dict instance.

    internal_config : dict[str, Any] | None, optional
        A validated config created by the supplied validation model.
        By default None.

    writeBackup : bool, optional
        Manipulate with files on the file system to recover from soft errors
        (e.g. overwrite the config file with the internal config).
        By default True.

    retries : int, optional
        Reload the config X times if soft errors occur.
        Note: This has no effect if writeBackup is False.
        By default 1.

    Returns
    -------
    tuple[dict[str, Any] | None, bool]
        Returns a tuple of values:
        * [0]: The config file converted to a Python object (dict)
        * [1]: True if the config failed to load. Otherwise, False

    Raises
    ------
    NotImplementedError
        If the file at the config path is not supported
    """
    isError, failure = False, False
    config = None
    filename = os.path.split(config_path)[1]
    extension = os.path.splitext(filename)[1].strip(".")
    try:
        with open(config_path, "rb") as file:
            if extension.lower() == "toml":
                raw_config = tomlkit.load(file)
            elif extension.lower() == "ini":
                raw_config = IniFileParser.load(file)
            elif extension.lower() == "json":
                raw_config = json.load(file)
            else:
                err_msg = f"{config_name}: Cannot load unsupported file '{config_path}'"
                raise NotImplementedError(err_msg)
        config = validator(raw_config)
    except ValidationError as err:
        isError, isRecoverable = True, True
        _logger_.warn(f"{config_name}: Could not validate '{filename}'")
        _logger_.debug(formatValidationError(err))
        if doWriteConfig:
            backupConfig(config_path)
            writeConfig(internal_config, config_path)
    except MissingFieldError as err:
        isError, isRecoverable = True, True
        err_msg = f"{config_name}: Detected incorrect fields in '{filename}':\n"
        for item in err.args[0]:
            err_msg += f"  {item}\n"
        _logger_.warn(err_msg)
        _logger_.info(f"{config_name}: Repairing config")
        if doWriteConfig:
            repairedConfig = upgradeConfig(raw_config, internal_config)
            writeConfig(repairedConfig, config_path)
    except (InvalidMasterKeyError, AssertionError) as err:
        isError, isRecoverable = True, True
        logger.warn(f"{config_name}: {err.args[0]}")
        if doWriteConfig:
            backupConfig(config_path)
            writeConfig(internal_config, config_path)
    except (tomlkit.exceptions.ParseError, IniParseError) as err:
        isError, isRecoverable = True, True
        _logger_.warn(f"{config_name}: Failed to parse '{filename}':\n"
                      + f"  {err.args[0]}\n")
        if doWriteConfig:
            backupConfig(config_path)
            writeConfig(internal_config, config_path)
    except FileNotFoundError:
        isError, isRecoverable = True, True
        _logger_.info(f"{config_name}: Creating '{filename}'")
        if doWriteConfig:
            writeConfig(internal_config, config_path)
    except Exception:
        isError, isRecoverable = True, False
        _logger_.error(f"{config_name}: An unexpected error occurred while loading '{filename}'\n"
                       + traceback.format_exc(limit=AppArgs.traceback_limit))
    finally:
        if isError:
            if doWriteConfig and retries > 0 and isRecoverable:
                _logger_.info(f"{config_name}: Reloading '{filename}'")
                config, failure = loadConfig(
                    config_name=config_name,
                    config_path=config_path,
                    validator=validator,
                    internal_config=internal_config,
                    doWriteConfig=doWriteConfig,
                    retries=retries-1
                )
            else:
                failure = True
                load_failure_msg = f"{config_name}: Failed to load '{filename}'"
                if internal_config:
                    load_failure_msg += ". Switching to internal config"
                    config = internal_config # Use internal config if all else fails
                    _logger_.warn(load_failure_msg)
                else:
                    _logger_.error(load_failure_msg)
        else:
            _logger_.info(f"{config_name}: Config '{filename}' loaded!")
        return config, failure


def validateValue(config_name: str, config: dict, validator: Callable[[dict], dict],
              setting: str, value: Any, parent_key: Optional[str]=None) -> tuple[bool, Literal[1] | None]:
    """Validate a value in the supplied config.

    Parameters
    ----------
    config : dict
        A Python config object.

    validator : Callable[[dict], dict]
        The validator callable which validates the config.

    key : str
        The key whose value should be updated.

    value : Any
        The value whose should be saved.

    Returns
    -------
    tuple[bool, Literal[1] | None]
        Returns a tuple of values:
        * [0]: True if an error occured. Otherwise, False.
        * [1]: 1 if a validation error occurred. Otherwise, None.
    """
    isError, isValid = False, True
    try:
        old_value = insertDictValue(config, setting, value, parent_key=parent_key)
        if old_value is None:
            error_msg = f"{config_name}: Could not find setting '{setting}'"
            raise KeyError(error_msg)

        validator(config, config_name)
    except ValidationError as err:
        isError, isValid = True, False
        insertDictValue(config, setting, old_value[0]) # Restore value
        _logger_.warn(f"{config_name}: Unable to save value '{value}' for setting '{setting}': "
                      + formatValidationError(err))
    except Exception:
        isError = True
        _logger_.error(f"{config_name}: An unexpected error occurred while saving value '{value}' using key '{setting}'\n"
                       + traceback.format_exc(limit=AppArgs.traceback_limit))
    finally:
        return isError, isValid


def upgradeConfig(loadedConfig: NestedDict, internalConfig: NestedDict) -> NestedDict:
    newConfig = {}
    for section_name, section in internalConfig.items():
        newConfig |= {section_name: {}}
        for setting, options in section.items():
            if section_name in loadedConfig and setting in loadedConfig[section_name]:
                 newConfig[section_name] |= {setting: loadedConfig[section_name][setting]}
            else:
                 newConfig[section_name] |= {setting: options}
    return newConfig