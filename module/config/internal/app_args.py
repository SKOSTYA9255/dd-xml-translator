import os
import sys
from pathlib import Path


def getRuntimeMode() -> str:
    """ Returns whether we are frozen via PyInstaller, Nuitka or similar
    This will affect how we find out where we are located.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, '_MEIPASS'):
        #print("Running in a PyInstaller bundle")
        return "PYI"
    elif getattr(sys, "nuitka", False):
        #print("Running in a Nuitka onefile binary")
        return "NUI"
    #print("Running in a normal Python process")


def getAppPath() -> Path:
    """ This will get us the program's directory,
    even if we are frozen using PyInstaller, Nuitka or similar """
    mode = getRuntimeMode()
    if mode == "PYI":
        return os.path.dirname(sys.argv[0]) # The original path to the PyInstaller bundle
    elif mode == "NUI":
        return os.path.dirname(sys.argv[0]) # The original path to the binary executable
    return Path.cwd()  # cwd must be set elsewhere. Preferably in the main '.py' file (e.g. app.py)


def getAssetsPath() -> Path:
    """ This will get us the program's asset directory,
    even if we are frozen using PyInstaller, Nuitka or similar """
    mode = getRuntimeMode()
    if mode == "PYI":
        return Path.cwd()
        #return Path(sys._MEIPASS).resolve() # PyInstaller-specific way of getting path to extracted dir
    elif mode == "NUI":
        return Path.cwd() # The temporary or permanent path the bootstrap executable unpacks to (i.e. the temp data folder created by Nuitka onefile binaries at runtime)
    return Path.cwd()  # cwd must be set elsewhere. Preferably in the main '.py' file (e.g. app.py)


class AppArgs():
    # General
    app_version = "0.0.1"
    link_github = "https://github.com/TheRealMorgenfrue/dd-xml-extractor"
    is_release = False
    traceback_limit = 0 if is_release else None
    app_dir = getAppPath()
    assets_dir = getAssetsPath()

    # Files
    app_toml = "app_config.toml"

    # Logging
    log_dir = Path(app_dir, "logs")
    log_format = "%(asctime)s - %(module)s - %(lineno)s - %(levelname)s - %(message)s" # %(asctime)s - %(name)s - %(levelname)s - %(message)s'
    log_format_color = "%(asctime)s - %(module)s - %(lineno)s - %(levelname)s - %(message)s" # %(asctime)s - %(module)s - %(lineno)s - %(levelname)s - %(message)s'

    # Template Settings
    config_units = {
        "character": "characters",
        "line": "lines"
    }

    # Configs
    config_dir  = Path(app_dir, "configs")
    app_config_path = Path(config_dir, app_toml).resolve()

    # Assets
    assets_dir = Path(assets_dir, "assets")
    logo_dir = Path(assets_dir, "logo")
    app_assets_dir = Path(assets_dir, "app")
    asset_images_dir = Path(app_assets_dir, "images")
    qss_dir = Path(app_assets_dir, "qss")

    # Data
    data_dir = Path(app_dir, "data")

    # Template values - these are present to decouple several modules (logger, validators) from
    # the app template to prevent circular imports. NOT ideal, but a workaround for now
    template_loglevels = [
        "INFO", "WARN",
        "ERROR", "CRITICAL",
        "DEBUG"
    ]
    template_themes = [
        "Light",
        "Dark",
        "System"
    ]
    template_langTags = [
        "english",
        "schinese"
    ]