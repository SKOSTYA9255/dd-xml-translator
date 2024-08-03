from module.config.internal.app_args import AppArgs
from module.tools.utilities import iterToString

def validateLoglevel(loglevel: str) -> str:
    """Validate loglevel which must confirm to the Pixiv Manager loglevel specification

    Parameters
    ----------
    loglevel : str
        The loglevel, e.g. "DEBUG"

    Returns
    -------
    str
        The loglevel, if valid

    Raises
    ------
    AssertionError
        The loglevel is invalid
    """
    loglevel = loglevel.upper()
    if not loglevel in AppArgs.template_loglevels:
        err_msg = (f"Invalid log level '{loglevel}'. "
                   + f"Expected one of '{iterToString(AppArgs.template_loglevels, separator=", ")}'")
        raise AssertionError(err_msg)
    return loglevel


def validateTheme(theme: str) -> str:
    """Ensure the theme is a valid argument for the app

    Parameters
    ----------
    theme : str
        The theme, e.g. "Dark"

    Returns
    -------
    str
        The theme, if valid

    Raises
    ------
    AssertionError
        The theme is invalid
    """
    if not theme in AppArgs.template_themes:
        err_msg = (f"Invalid theme '{theme}'. Expected one of '{iterToString(AppArgs.template_themes, separator=", ")}'")
        raise AssertionError(err_msg)
    return theme


def validateLangTag(tag: str) -> str:
    """Ensure the XML language tag is a valid argument for XML tools

    Parameters
    ----------
    tag : str
        The XML language tag, e.g. "english"

    Returns
    -------
    str
        The XML language tag, if valid

    Raises
    ------
    AssertionError
        The XML language tag is invalid
    """
    if not tag in AppArgs.template_langTags:
        err_msg = (f"Invalid XML language tag '{tag}'. Expected one of '{iterToString(AppArgs.template_langTags, separator=", ")}'")
        raise AssertionError(err_msg)
    return tag