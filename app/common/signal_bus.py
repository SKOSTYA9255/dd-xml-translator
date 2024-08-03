from PyQt6.QtCore import QObject, pyqtSignal, QCoreApplication


class signalBus(QObject):
    """ pyqtSignal bus """
    # Config
    configStateChange = pyqtSignal(bool, str, str) # success/failure, title, content # Whenever a config changes state
    configValidationError = pyqtSignal(str, str, str) # config_name, title, content # If a pyqtSignal is received here, it means a validation error occured during saving
    configUpdated = pyqtSignal(str, tuple) # configkey, tuple[value]
    doSaveConfig = pyqtSignal(str) # config_name

    # GUI-related
    xml_process_exception = pyqtSignal(str, str) # msg, traceback # Something went wrong during processing
    updateConfigSettings = pyqtSignal(str, tuple) # configkey, tuple[value]

    appShutdown = QCoreApplication.aboutToQuit


signalBus = signalBus()