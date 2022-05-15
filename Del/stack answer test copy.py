import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class DirProxy(QSortFilterProxyModel):
	nameFilters = ''
	def __init__(self):
		super().__init__()
		self.dirModel = QFileSystemModel()
		self.dirModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files) # <- added QDir.Files to view all files
		self.setSourceModel(self.dirModel)

	def setNameFilters(self, filters):
		if not isinstance(filters, (tuple, list)):
			filters = [filters]
		self.nameFilters = filters
		self.invalidateFilter()

	def hasChildren(self, parent):
		sourceParent = self.mapToSource(parent)
		if not self.dirModel.hasChildren(sourceParent):
			return False
		qdir = QDir(self.dirModel.filePath(sourceParent))
		return bool(qdir.entryInfoList(qdir.NoDotAndDotDot|qdir.AllEntries|qdir.AllDirs))
	
	def filterAcceptsRow(self, row, parent):
		source = self.dirModel.index(row, 0, parent)
		if source.isValid():
			if self.dirModel.isDir(source):
				qdir = QDir(self.dirModel.filePath(source))
				if self.nameFilters:
					qdir.setNameFilters(self.nameFilters)
				return bool(qdir.entryInfoList(qdir.NoDotAndDotDot|qdir.AllEntries|qdir.AllDirs))

			else:  # <- index refers to a file
				qdir = QDir(self.dirModel.filePath(source))
				return qdir.match(self.nameFilters, self.dirModel.fileName(source)) # <- returns true if the file matches the nameFilters
		return True

class Test(QWidget):
	def __init__(self):
		super().__init__()
		
		self.dirProxy = DirProxy()
		self.dirProxy.dirModel.directoryLoaded.connect(lambda : self.treeView.expandAll())
		self.dirProxy.setNameFilters(['*.ai'])  # <- filtering all files and folders with "*.ai"
		self.dirProxy.dirModel.setRootPath(r"<Dir>")

		self.treeView = QTreeView()
		self.treeView.setModel(self.dirProxy)

		root_index = self.dirProxy.dirModel.index(r"<Dir>")
		proxy_index = self.dirProxy.mapFromSource(root_index)
		self.treeView.setRootIndex(proxy_index)

		self.treeView.show()

app = QApplication(sys.argv)
ex = Test()
sys.exit(app.exec_())