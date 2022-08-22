from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from _subclassed import DisDelegate, FileSystemModel, Tree
import sys

class Test(QWidget):
	def __init__(self):
		super().__init__()
		self.project_filenames_as_filter = ["*.ai","*.psd"]
		self.workstation_files = r"C:\Users\Eliaz\Desktop\SandBox"

		self.model = FileSystemModel()
		self.model.hideMode = True
		self.model.setRootPath(self.workstation_files)
		self.model._nameFilters = self.project_filenames_as_filter
		# self.model.setNameFilters(self.project_filenames_as_filter)
		# self.model.setNameFilters(project_filenames_as_filter) #-> causes problems in the model file selection
		# -> default self.model.conNameFilters = self.project_filenames_as_filter        # self.dirProxy.dirModel.setNameFilterDisables(False)

		# self.dirProxy.dirModel.setFilter(QDir.Files | QDir.NoDotAndDotDot)

		# self.model2.setReadOnly(False)

		self.tree = Tree(self.model)

		self.tree.isLeft = True
		root_index = self.model.index(self.workstation_files)
		self.tree.setRootIndex(root_index)

		# self.tree.clicked.connect(lambda event: self.onClicked(event, self.main_file_preview))
		# self.tree.setColumnWidth(0, 200)

		# enable hide
		delegate = DisDelegate() if self.model.hideMode else QStyledItemDelegate()
		self.model.hideMode = not self.model.hideMode
		# self.model.invalidateFilter()
		self.tree.setItemDelegate(delegate)

		self.tree.show()

		# need to redo to add QFilterProxyModel, to actually add the functionality to hide
		# self.handle_buttons("Disable Hide", "Enable Hide")

qApp = QApplication(sys.argv)
ex = Test()
sys.exit(qApp.exec())
