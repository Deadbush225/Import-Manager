from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys


class ECM(QWidget):

    def __init__(self):
        super(ECM, self).__init__()
        self.setWindowTitle("Extended Context Menu")
        self.lineEdit = QLineEdit()
        self.lineEdit.setContextMenuPolicy(Qt.CustomContextMenu)                            
        self.lineEdit.customContextMenuRequested.connect(self.my_contextMenuEvent)

        layout = QVBoxLayout()
        layout.addWidget(self.lineEdit)
        self.setLayout(layout)

        self.setFixedSize(800,200)

        action = QAction('&Replace', self)
        action.setStatusTip('Replace values')
        action.setShortcut(QKeySequence(Qt.CTRL + Qt.Key_R))
        action.triggered.connect(self.replace)

        self.lineEdit.addAction(action)

        self.show()

    def replace(self):
        print("replace")

    def my_contextMenuEvent(self):                                           
        menu = self.lineEdit.createStandardContextMenu()
        menu.addActions(self.lineEdit.actions())
        menu.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    sender = ECM()
    app.exec_()