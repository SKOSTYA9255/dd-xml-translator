from PyQt6.QtCore import QObject, pyqtSignal


class SignalBus(QObject):
    """ pyqtSignal bus """
    # Config
    configStateChange = pyqtSignal(bool, str, str) # success/failure, title, content # Whenever a config changes state
    configValidationError = pyqtSignal(str, str, str) # config_name, title, content # If a pyqtSignal is received here, it means a validation error occured during saving
    configUpdated = pyqtSignal(str, tuple) # configkey, tuple[value]
    doSaveConfig = pyqtSignal(str) # config_name

    # GUI-related
    xmlProcessException = pyqtSignal(str, str, str) # errorType, msg, traceback # Something went wrong during processing
    xmlValidationError = pyqtSignal(str, str, str) # errorType, title, content# A validation error occured in the XML
    xmlPreviewInvalid = pyqtSignal(bool, bool) # isValid, showErrors
    updateConfigSettings = pyqtSignal(str, tuple) # configkey, tuple[value]

signalBus = SignalBus()