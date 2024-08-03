import re
import logging
import os

from pathlib import Path
from datetime import datetime
from typing import Self

from module.logger.coloredformatter import ColoredFormatter
from module.logger.colorcodefilter import ColorCodeFilter
from module.config.internal.app_args import AppArgs
from module.config.internal.names import ModuleNames


class Logger():
    _instance = None

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._create_logger(cls._instance._getConfigLoglevel(AppArgs.app_config_path))
            cls._instance._create_logger_title()
            cls._instance._writeHeaderToLog()
        return cls._instance

    def _current_datetime(self) -> str:
        # return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return datetime.now().strftime("%Y-%m-%d")

    def _create_logger(self, level) -> logging.Logger:
        self.logger = logging.getLogger(ModuleNames.app_name)
        self.logger.propagate = False
        self.logger.setLevel(level)

        console_handler = logging.StreamHandler()
        console_formatter = ColoredFormatter(AppArgs.log_format_color)
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        if not AppArgs.log_dir.exists():
            AppArgs.log_dir.mkdir()
        file_handler = logging.FileHandler(f"{AppArgs.log_dir}{os.sep}{self._current_datetime()}.log", encoding="utf-8")
        file_formatter = ColorCodeFilter(AppArgs.log_format)
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

        return self.logger

    def _create_logger_title(self, level="INFO") -> logging.Logger:
        self.logger_title = logging.getLogger(f"{ModuleNames.app_name}_title")
        self.logger_title.propagate = False
        self.logger_title.setLevel(level)

        console_handler = logging.StreamHandler()
        console_formatter = logging.Formatter('%(message)s')
        console_handler.setFormatter(console_formatter)
        self.logger_title.addHandler(console_handler)

        if not AppArgs.log_dir.exists():
            AppArgs.log_dir.mkdir()
        file_handler = logging.FileHandler(f"{AppArgs.log_dir}{os.sep}{self._current_datetime()}.log", encoding="utf-8")
        file_formatter = logging.Formatter('%(message)s')
        file_handler.setFormatter(file_formatter)
        self.logger_title.addHandler(file_handler)

        return self.logger_title

    def _writeHeaderToLog(self) -> None:
        padding = 90
        header = "┌" + "─"*padding + "┐" + "\n" + \
                 "│" + f"Starting application".center(padding, " ") + "│" + "\n" + \
                 "└" + "─"*padding + "┘"
        self.logger_title.info(f"\n{header}")

    def _getConfigLoglevel(self, configpath: Path, default="DEBUG") -> str:
        """ Decouple the logger module from the app_config module """
        try:
            with open(configpath, "r", encoding="utf-8") as file:
                lines = file.read().splitlines()
        except FileNotFoundError:
            return default

        pattern = re.compile(r"(?<!.)\[(\w*)\]|(?<!.)(\w+)\s{0,1}=(?(2)\s{0,1}(.*))")
        for line in lines:
            if line == "":
                continue
            match = re.search(pattern, line)
            if match is None:
                continue
            key = match.group(2)
            value = match.group(3)
            if key == "loglevel":
                value = value.strip("\"")
                if value in AppArgs().template_loglevels:
                    return value
        return default

    def get_logger(self) -> logging.Logger:
        return self.logger