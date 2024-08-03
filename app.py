# Nuitka Compilation mode
# nuitka-project: --onefile
# nuitka-project: --standalone
# nuitka-project: --include-data-dir={MAIN_DIRECTORY}/assets=assets

# Windows Controls
# nuitka-project: --windows-icon-from-ico={MAIN_DIRECTORY}/assets/logo/logo.png

# Binary Version Information
# nuitka-project: --product-name=Darkest Dungeon Localization Helper
# nuitka-project: --product-version=0.0.1

# Plugin: Enable PyQt6 support and disable terminal
# nuitka-project: --enable-plugin=PyQt6
# nuitka-project: --windows-console-mode=disable

# Plugin: Enable anti-bloat to remove dependency-heavy imports
# nuitka-project: --enable-plugin=anti-bloat


import os
import sys
from pathlib import Path

##########################
### Initial Path Setup ###
##########################
# Set initial CWD
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Running in a Nuitka onefile binary
if Path(sys.argv[0]) != Path(__file__):
    setattr(sys, "nuitka", True)

# Running in a PyInstaller bundle
elif getattr(sys, 'frozen', False):
    # Set CWD to extracted PyInstaller dir
    os.chdir(os.path.dirname(sys.executable))

# Running in a normal python process
else:
    pass
##########################

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication
from app.main_window import MainWindow

# enable dpi scale
QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setAttribute(Qt.ApplicationAttribute.AA_DontCreateNativeWidgetSiblings)

    w = MainWindow()
    sys.exit(app.exec())