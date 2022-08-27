import sys
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *

from _subclassed import MessageOverridePopUp
# Subclass QMainWindow to customize your application's main window 

class Window(QWidget):
    def __init__(self):
        super().__init__()
        
        popup = MessageOverridePopUp()
        print(popup.override)

app = QApplication(sys.argv)
ex = Window()
sys.exit(app.exec())