import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

class DirProxy(QSortFilterProxyModel):
	nameFilters = ''
	def __init__(self):
		super().__init__()
		self.dirModel = QFileSystemModel()
		self.dirModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files)
		self.setSourceModel(self.dirModel)

	def setNameFilters(self, filters):
		if not isinstance(filters, (tuple, list)):
			filters = [filters]
		self.nameFilters = filters
		self.invalidateFilter()

	def fileInfo(self, index):
		return self.dirModel.fileInfo(self.mapToSource(index))

	def hasChildren(self, parent):
		sourceParent = self.mapToSource(parent)
		if not self.dirModel.hasChildren(sourceParent):
			return False
		d__path = self.dirModel.filePath(sourceParent)
		qdir = QDir(self.dirModel.filePath(sourceParent))
		d__bo = bool(qdir.entryInfoList(qdir.NoDotAndDotDot|qdir.AllEntries|qdir.AllDirs))
		return d__bo

	# def filterAcceptsRow(self, row, parent):
	# 	source = self.dirModel.index(row, 0, parent)
	# 	if source.isValid():
	# 		qdir = QDir(self.dirModel.filePath(source))
	# 		if self.nameFilters:
	# 			qdir.setNameFilters(self.nameFilters)
	# 		return bool(qdir.entryInfoList(
	# 			qdir.NoDotAndDotDot|qdir.AllEntries|qdir.AllDirs))
	# 	return True
	
	def filterAcceptsRow(self, row, parent):
		source = self.dirModel.index(row, 0, parent)
		path = self.dirModel.filePath(source)
		print(f"row: {row}, isValid: {source.isValid()}, path: {path}")
		
		source = self.dirModel.index(row, 0, parent)
		if source.isValid():
			if self.dirModel.isDir(source):
				qdir = QDir(self.dirModel.filePath(source))
				d__path = path
				if self.nameFilters:
					qdir.setNameFilters(self.nameFilters)
				
				ent_list = qdir.entryInfoList(qdir.NoDotAndDotDot|qdir.AllEntries|qdir.AllDirs)
				d__bo = bool(qdir.entryInfoList(qdir.NoDotAndDotDot|qdir.AllEntries|qdir.AllDirs))
				return d__bo
			else:
				qdir = QDir(self.dirModel.filePath(source))
				d__path = self.dirModel.filePath(source)
				ent_list = qdir.match(self.nameFilters, self.dirModel.fileName(source))
				d__bo = bool(qdir.entryInfoList(qdir.NoDotAndDotDot|qdir.AllEntries|qdir.AllDirs))
				# return d__bo
				return ent_list
		return True
		# return super().filterAcceptsRow(row, parent)

class Test(QWidget):
	def __init__(self):
		super().__init__()
		
		self.dirProxy = DirProxy()
		self.dirProxy.setNameFilters(['*.ai'])
		self.dirProxy.dirModel.setRootPath(r"D:\Student - Files\Eliazar\Workstation Files")

		self.treeView = QTreeView()
		self.treeView.setModel(self.dirProxy)

		root_index = self.dirProxy.dirModel.index(r"D:\Student - Files\Eliazar\Workstation Files")
		proxy_index = self.dirProxy.mapFromSource(root_index)
		self.treeView.setRootIndex(proxy_index)

		self.treeView.show()

app = QApplication(sys.argv)
ex = Test()
sys.exit(app.exec_())