#!/usr/bin/env python
import sys


from PyQt5.QtWidgets import QApplication
from core import XOCore


application = QApplication(sys.argv)

XO = XOCore()

sys.exit(application.exec())
