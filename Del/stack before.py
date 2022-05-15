import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class Test(QWidget):
	def __init__(self):
		super().__init__()
		
		self.model = QFileSystemModel()
		self.model.setNameFilters(['*.ai'])  # <- filtering all files and folders with "*.ai"
		self.model.setRootPath(r"D:\Student - Files\Eliazar\Workstation Files")
		self.model.directoryLoaded.connect(lambda : self.treeView.expandAll())

		self.treeView = QTreeView()
		self.treeView.setModel(self.model)

		index = self.model.index(r"D:\Student - Files\Eliazar\Workstation Files")
		self.treeView.setRootIndex(index)

		self.treeView.show()

app = QApplication(sys.argv)
ex = Test()
sys.exit(app.exec_())