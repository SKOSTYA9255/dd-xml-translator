import traceback
from typing import Any, Mapping, Optional, Self, override
from time import time

from app.common.signal_bus import signalBus

from module.config.abstract_config import BaseConfig
from module.config.internal.app_args import AppArgs
from module.config.tools.config_tools import checkMissingFields, loadConfig, validateValue, retrieveDictValue, writeConfig
from module.config.tools.validation_model_gen import ValidationModelGenerator
from module.config.templates.app_template import AppTemplate
from module.logger import logger


class AppConfig(BaseConfig):
    _instance = None
    _logger = logger
    _validation_model = ValidationModelGenerator().getGenericModel(
        model_name=AppTemplate().getTemplateName(),
        template=AppTemplate().getTemplate()
    )

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._config_name = AppTemplate().getTemplateName()
            cls._load_failure = False # The config failed to load
            cls._is_modified = False # A modified config needs to be written to disk
            cls._lastSaveTime = time()
            cls._config_path = AppArgs.app_config_path
            cls._internal_config = cls._validation_model.model_construct().model_dump()
            cls._config = cls._instance._initConfig()
        return cls._instance

    @override
    def _initConfig(self) -> dict[str, Any] | None:
        """Load the App's main config file.

        Returns
        -------
        dict[str, Any] | None
            The config file as a Python object
        """
        config, self._load_failure = loadConfig(
            config_name=self._validation_model.__name__,
            config_path=self._config_path,
            validator=self._validateLoad,
            internal_config=self._internal_config
        )
        return config

    @override
    def _validateLoad(self, raw_config: Mapping) -> dict[str, Any]:
        validated_config = self._validation_model.model_validate(raw_config)
        config = validated_config.model_dump()
        checkMissingFields(raw_config, config)
        return config

    @override
    def _validate(self, save_config: dict, config_name: str) -> dict[str, Any]:
        self._config = self._validation_model.model_validate(save_config).model_dump()

    @override
    def getConfig(self) -> dict[str, Any] | None:
        return self._config

    @override
    def getConfigName(self) -> str:
        return self._config_name

    @override
    def getFailureStatus(self) -> bool:
        return self._load_failure

    @override
    def getValue(self, key: str, parent_key: Optional[str]=None, default: Any=None,
                 use_internal_config: bool=False) -> Any:
        """
        Return first value found. If there is no item with that key, return
        default.
        """
        config = self._internal_config if use_internal_config else self._config
        value = retrieveDictValue(
            d=config,
            key=key,
            default=default
        )
        if value is None:
            self._logger.warn(f"Could not find key '{key}' in the config. "
                              + f"Returning default: '{default}'")
        return value

    @override
    def setValue(self, key: str, value: Any, config_name: str) -> None:
        """ Update config with value """
        isError, isInvalid = validateValue(
            config_name=config_name,
            config=self._config,
            validator=self._validate,
            setting=key,
            value=value
        )
        if isError:
            signalBus.configStateChange.emit(False, "Failed to save setting", "")
        else:
            signalBus.configUpdated.emit(key, (value,))
            self._is_modified = True
        return isInvalid

    @override
    def saveConfig(self) -> None:
        """ Write config to disk """
        try:
            if self._is_modified and (self._lastSaveTime + 1) < time():
                self._lastSaveTime = time()
                writeConfig(self.getConfig(), self._config_path)
                self._is_modified = False
        except Exception:
            msg = "Failed to save the config"
            self._logger.error(f"{msg}\n" + traceback.format_exc(limit=AppArgs.traceback_limit))
            signalBus.configStateChange.emit(False, msg, "Check the log for details")