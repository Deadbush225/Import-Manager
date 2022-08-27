#! python3

import sys
import os
import ctypes
import shutil
import subprocess
from pathlib import *
# from send2trash import send2trash

# def deleteF(path: str):   # use moveToTrash
# 	return path.replace("/", "\\")

def multiCopyHandler(path):
	p = Path(path)
	if p.exists():
		if p.is_file():
			counter = 1
			parent = p.parents[0]
			base = p.stem
			ext = p.suffix

			while p.exists():
				if counter == 1:
					newF = parent / PureWindowsPath(base + " - copy" + ext)
				else:
					newF = parent / PureWindowsPath(base + f" - copy ({counter})" + ext)
				p = Path(newF)
				counter += 1

		if p.is_dir():
			counter = 1
			parent = p.parents[0]
			name = p.name

			while p.exists():
				if counter == 1:
					newF = parent / PureWindowsPath(name + " - copy")
				else:
					newF = parent / PureWindowsPath(name + f" - copy ({counter})")
				p = Path(newF)
				counter += 1
		
		return str(newF)
	else:
		return p.absolute()

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

# notes: ln --recursive --mirror x:\source x:\destination
# notes if you want, you can use os.link then recursively check the tree every 5 secs

# hey if there's a problem, just check if the index is right `mapToSource` and `mapFromSource`

# notes `recursiveFilteringEnabled` 

# -- Types -- #
project_filenames = ["ai","psd"]
project_filenames_as_filter = ["*.ai","*.psd"]
preview_types = [".ai", ".psd", ".jpg", ".png"]

# -- Paths -- #
dir_path           = r'D:/Student - Files/Eliazar'
workstation_files  = r'D:/Student - Files/Eliazar/Workstation Files'
thumbnail          = r"D:/Student - Files/Eliazar/thumbnail"

class MyProxyStyle(QProxyStyle):
	def drawPrimitive(self, element: QStyle.PrimitiveElement, option: 'QStyleOption', painter: QPainter, widget: QWidget) -> None:
		what_el = element == QStyle.PE_IndicatorItemViewItemDrop

		if what_el:
			# print(option.type)
			# if option.type == QStyleOption.SO_ViewItem:
			# focusRectOption = QStyleOptionFocusRect.qstyleoption_cast(QStyleOptionFocusRect)
			# if focusRectOption:
			print(option.type)
			painter.setRenderHint(QPainter.Antialiasing, True)
			# palette = QPalette()
			c = QColor("red")
			pen = QPen(c)
			pen.setWidth(2)
			c.setAlpha(50)
			brush = QBrush(c)

			painter.setPen(pen)
			painter.setBrush(brush)

			# rec = self.sizeFromContents(QStyle.CT_ItemViewItem, option, widget)

			# if option.rect.height() == 0:
			# 	painter.drawEllipse(option.rect.topLeft(), 3, 3)
			# 	painter.drawLine(QPoint(option.rect.topLeft().x()+3, option.rect.topLeft().y()), option.rect.topRight())
			# else:
			# 	painter.drawRoundedRect(option.rect, 5, 5)
			if option.rect.height() == 0:
				painter.drawEllipse(option.rect.topLeft(), 3, 3)
				painter.drawLine(QPoint(option.rect.topLeft().x()+3, option.rect.topLeft().y()), option.rect.topRight())
			else:
				painter.drawRoundedRect(option.rect, 5, 5)
		else:
			return super().drawPrimitive(element, option, painter, widget)

	# def sizeFromContents(self, type: QStyle.ContentsType, option: 'QStyleOption', size: QSize, widget: QWidget) -> QSize:
	# 	print(type)
	# 	if type == QStyle.CT_ItemViewItem:
	# 		# print("sizeFromContents")
	# 		print(f"size {size.height()}, option's top left {option.rect.topLeft().y()}")
			
	# 	return super().sizeFromContents(type, option, size, widget)

class Tree(QTreeView):
	global project_filenames
	global preview_types
	global dir_path
	global workstation_files
	global thumbnail

	isLeft  = False
	isRight = False
	current_key = None

	def __init__(self, model):
		super().__init__()

		self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
		self.setDragDropMode(QAbstractItemView.DragDrop)
		self.setDefaultDropAction(Qt.CopyAction)
		self.viewport().setAcceptDrops(True)
		self.setAlternatingRowColors(True)
		self.setDropIndicatorShown(True)

		self.setModel(model)

		self.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)


	def dragEnterEvent(self, event):
		self.passed_m = event.mimeData()
		event.accept()

	def dragLeaveEvent(self, event):
		print("leaving")
		if self.passed_m.hasUrls():
			self.leaving_urls = [QFileInfo(url.toLocalFile()).fileName() for url in self.passed_m.urls() if url.isLocalFile()]

			print(self.leaving_urls)

		return super().dragLeaveEvent(event)

	def dragMoveEvent(self, event):
		print("dragMoveEvent")

		if not event.mimeData().hasUrls():
			print("no urls")
			event.ignore()
			return
		if qApp.queryKeyboardModifiers() & Qt.ShiftModifier:
			event.accept()
		event.ignore()

	def dropEvent(self, event):
		print("[drop event] - dropped")

		dropAction = event.dropAction()

		# if event.source():
		ix = self.indexAt(event.pos())
		model = self.model()

		if ix.isValid():
			if not model.isDir(ix):
				ix = ix.parent()
			pathDir = model.filePath(ix)
		else:
			# for empty drag and drop
			pathDir = model.rootPath()

		m = event.mimeData()
		if m.hasUrls():
			urlLocals = [url for url in m.urls() if url.isLocalFile()]
			accepted = False
			for urlLocal in urlLocals:
				path = urlLocal.toLocalFile()
				info = QFileInfo(path)
				destination = QDir(pathDir).filePath(info.fileName()) # <- check if this one exists
				destination_cannonical = QDir(pathDir).path()
				source = info.absoluteFilePath()
				if source == destination:
					continue  # means they are in the same folder
				if info.isDir():
					if dropAction == Qt.CopyAction:
						print(f"QDir -> source: {source} {os.path.exists(source)} | destination: {os.path.exists(destination)} {destination}")
						# rep = QDir().rename(source, destination)
						# print(rep)
						# try: # note try block deprecated
						#     shutil.move(source, destination)
						# except Exception as e:
						#     print(f'[warning droping in the same location] Error: {e}')
						
						destination = multiCopyHandler(destination)
						shutil.copytree(source, destination)
						
						# print(rep)

					elif dropAction == Qt.MoveAction:
						destination = multiCopyHandler(destination)
						shutil.move(source, destination)
				elif info.isFile():
					qfile = QFile(source)
					if QFile(destination).exists():
						n_info = QFileInfo(destination)
						
						# destination = n_info.canonicalPath() + QDir.separator() + n_info.completeBaseName() + " (copy)"
						# if n_info.completeSuffix():   # for moving files without suffix
						# 	destination += "." + n_info.completeSuffix()
						destination = multiCopyHandler(destination)

					if dropAction == Qt.CopyAction:
						# destination = 
						qfile.copy(destination)
					elif dropAction == Qt.MoveAction:
						qfile.rename(destination)
					print(f"added -> {info.fileName()}")  # for debugging

				accepted = True
			if accepted:
				event.acceptProposedAction()

class FileSystemView(QWidget):
	global project_filenames
	global project_filenames_as_filter
	global preview_types
	global dir_path
	global workstation_files
	global thumbnail

	def __init__(self):
		super().__init__()

		# -- stylesheets -- #

		# self.setStyleSheet("ModifiedQLabel { background-color: lightgray }")

		self.setWindowTitle('File System Viewer')
		# self.setGeometry(200, 100, appWidth, appHeight)

		# -- left side pane -- #
		if not os.path.exists(workstation_files):
			os.mkdir(workstation_files)
			# note intro here because new

		# self.model = FileSystemModel()
		self.model = QFileSystemModel()
		self.model.setReadOnly(False)
		self.model.setRootPath(workstation_files)
		# self.model.setNameFilters(project_filenames_as_filter) # causes problems in the model file selection
		self.model.conNameFilters = project_filenames_as_filter        # self.dirProxy.dirModel.setNameFilterDisables(False)

		# self.dirProxy.dirModel.setFilter(QDir.Files | QDir.NoDotAndDotDot)


		self.tree = Tree(self.model)

		self.tree.isLeft = True
		root_index = self.model.index(workstation_files)
		self.tree.setRootIndex(root_index)

		# -- layout -- #
		self.main_layout = QVBoxLayout()

		self.tree_layout = QHBoxLayout()
		self.tree_layout.addWidget(self.tree)

		self.main_layout.addLayout(self.tree_layout)

		self.setLayout(self.main_layout)

if __name__ == '__main__':

	app = QApplication.instance()
	if app is None:
		app = QApplication(sys.argv)
		app.setStyle(MyProxyStyle())
	demo = FileSystemView()
	demo.setStyle(MyProxyStyle())
	demo.show()
	sys.exit(app.exec_())
