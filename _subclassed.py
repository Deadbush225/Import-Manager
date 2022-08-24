# -> todo
# clean tree subclass
# / fix selection bug in the "disabled items"

from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
import os
import shutil
from pathlib import Path, PureWindowsPath
# from functools import singledispatch
from multipledispatch import dispatch

# class overload:
#     def __init__(self, f):
#         self.cases = {}

#     def args(self, *args):
#         def store_function(f):
#             self.cases[tuple(args)] = f
#             return self
#         return store_function

#     def __call__(self, *args):
#         function = self.cases[tuple(type(arg) for arg in args)]
#         return function(*args)
@dispatch(str)
def Mmkdir(path):
	os.mkdir(path)

@dispatch(PureWindowsPath)
def Mmkdir(path):
	os.mkdir(path)

@dispatch(list)
def Mmkdir(path_list):
	for path in path_list:
		os.mkdir(path)

@dispatch(str)
def exists(path :str):
	return os.path.exists(path)

@dispatch(list, str)
def exists(index_list, name):
	"""_summary_

	Args:
		index_list (list): List[QModelIndex], returns None if meets an index pointing to a file
		name (str): file name to check for existence

	Returns:
		None: if meets an index pointing to a file 
		True: if any exists
		False: if none exists
	"""

	model : QFileSystemModel = index_list[0].model() #getting an index sample

	folder_list = []

	for index in index_list:
		fileInfo = model.fileInfo(index)
		if fileInfo.isDir():
			folder = Path(fileInfo.filePath(), name)
			if folder.exists():
				return True
			else:
				folder_list.append(folder)
				continue
			
		return 
	return folder_list
	
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

		elif p.is_dir():
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

# -> undo commands
class doCreateFolder(QUndoCommand):
	def __init__(self, newfolder=str, override=False, newfolder_list=[], model=QFileSystemModel):
		super().__init__()
		#-> both index_list and mode is partners

		# self.index_list = index_list
		# index_list = [model.filePath(index) for index in index_list]
		#-> Mmkdir() takes str or list[str]
		self.new_folder = [multiCopyHandler(newfolder) for newfolder in newfolder_list] if newfolder_list else multiCopyHandler(newfolder)
		self.override = override

	def redo(self):
		print('redoing')
		if self.override:

			# -> deleting folder
			file = QFile(self.new_folder)
			self.restore_path = file.fileName()

			file.moveToTrash()
			self.recycle_path = file.fileName()

			# -> creating folder
			Mmkdir(self.new_folder)
			return

		Mmkdir(self.new_folder)
	
	def undo(self):
		print('undoing')
		if self.override:
			shutil.move(self.recycle_path, self.restore_path)
		
		QFile(self.new_folder).moveToTrash()

class unMoveToNewFolderPopup(QUndoCommand):
	def __init__(self, parent, newfolder, index_list, model, override=False):
		super().__init__()
		self.model : QFileSystemModel= model
		self.index_list : list[QModelIndex] = index_list
		self.override : bool = override
		self.new_folder = newfolder
		self.parent : QTreeView = parent
	
	def redo(self):
		# -> creating folder
		print('redoing')
		if self.override:
			# -> deleting folder
			file = QFile(self.new_folder)
			self.restore_path = file.fileName()

			file.moveToTrash()
			self.recycle_path = file.fileName()

			# -> creating folder
			self.model.mkdir(self.parent.rootIndex(), self.new_folder)
		else:
			self.model.mkdir(self.parent.rootIndex(), self.new_folder)

		# -> moving files
		for index_fileinfo in self.index_list:
			self.original_folder = index_fileinfo.canonicalPath()

			#warning: make sure that the folder will actually make the folder inside
			if (index_fileinfo.canonicalPath() == self.model.rootPath()) or (self.model.rootPath() in index_fileinfo.canonicalPath()):  #warning: checking if the files are in the same of the rootfolder
				file_to_rename = index_fileinfo.canonicalFilePath()
				print(file_to_rename)
				shutil.move(file_to_rename, self.new_folder)
		
		self.parent.Mexpand(self.model.index(self.new_folder, 0))
	
	def undo(self):
		# -> moving files
		src_path = self.new_folder
		trg_path = self.original_folder

		for src_file in Path(src_path).glob('*.*'):
			shutil.move(src_file, trg_path)

		# -> delete the folder
		print('undoing')
		if self.override:
			shutil.move(self.recycle_path, self.restore_path)
		
		QFile(self.new_folder).moveToTrash()

class unRenamePopup(QUndoCommand):
	def __init__(self, newfolder, index_list: list, onefile=False):
		"""_summary_

		Args:
			newfolder (str): the text inputed in the popup
			index_list (list): _description_
			onefile (bool, optional): set to true if there's only 1 file selected. Defaults to False.
		"""		
		super().__init__()
		self.new_file = newfolder
		self.one_file = onefile
		self.index_list = index_list
		self.converted = []

	def redo(self):
		if self.one_file:
			for index_fileinfo in self.index_list:
				# -> removing the folder/file
				file = QFile(self.new_file)
				self.restore_path = file.fileName()

				file.moveToTrash()
				self.recycle_path = file.fileName()

				# -> renaming the folder/file
				self.original_name = index_fileinfo.absoluteFilePath()
				os.rename(self.original_name, self.new_file)

		elif not self.one_file:
			for index_fileinfo in self.index_list:
				if index_fileinfo.isFile():
					new_path = index_fileinfo.absolutePath() + QDir.separator() + self.new_file + "." + index_fileinfo.suffix()
				elif index_fileinfo.isDir():
					new_path = index_fileinfo.absolutePath() + QDir.separator() + self.new_file
				
				proofed_name = multiCopyHandler(new_path)
				
				self.converted.append([index_fileinfo.absoluteFilePath(), proofed_name])
				os.rename(index_fileinfo.absoluteFilePath(), proofed_name)
	
	def undo(self):
		if self.one_file:
			shutil.move(self.recycle_path, self.restore_path)

			os.rename(self.new_file, self.original_name)

		elif not self.one_file:
			for item in range(len(self.index_list)):
				os.rename(self.converted[item][1], self.converted[item][0])

class unDeleteFilePopup(QUndoCommand):
	def __init__(self, index_list: list):
		"""_summary_

		Args:
			newfolder (str): the text inputed in the popup
			index_list (list): _description_
			onefile (bool, optional): set to true if there's only 1 file selected. Defaults to False.
		"""		
		super().__init__()
		self.index_list = index_list
		self.converted = []

	def redo(self):
		for index_fileinfo in self.index_list:
			path_to_delete = index_fileinfo.absoluteFilePath()
			print(f"deleting ... {path_to_delete}")

			file = QFile(path_to_delete)
			file.moveToTrash()
			recyclebin_path = file.fileName()
			
			self.converted.append([recyclebin_path, path_to_delete])
	
	def undo(self):
		for item in range(len(self.converted)):
			os.rename(self.converted[item][0], self.converted[item][1])
		
		self.converted = []

class unRemoveOuterFolderPopup(QUndoCommand):
	def __init__(self, index_list, override=False):
		super().__init__()
		self.index_list = index_list
		self.override = override
		self.converted = {}
	
	def redo(self):
		# -> creating folder
		print('redoing')
		for index_fileinfo in self.index_list:
			selected_dir = Path(index_fileinfo.absolutePath())
			selected_dir_str = str(selected_dir)
			parent_dir = selected_dir.parents[0]

			file_data_list = []
			for file in selected_dir.iterdir():
				isNameChanged = False
				beforeNameChanged = None

				# if os.path.exists(file):
				transfer_file_name = parent_dir / file.name
				if transfer_file_name.exists():
					isNameChanged = True
					beforeNameChanged = file

					transfer_file_name = multiCopyHandler(transfer_file_name)

				shutil.move(file, transfer_file_name)

				file_data = {"file": file, 
							"destination": transfer_file_name, 
							"isNameChanged": isNameChanged, 
							"beforeChangedName": beforeNameChanged}
				file_data_list.append(file_data)
			self.converted[selected_dir_str] = file_data_list

			file = QFile(selected_dir_str)
			file.moveToTrash()
			self.recycle_path = file.fileName()

	def undo(self):
		# creating the folders
		for item in self.converted:
			# recovering the folder
			shutil.move(self.recycle_path, item)
			
			counter = 0
			for item1 in range(len(self.converted[item])):
				file = self.converted[item][counter]["file"]
				destination = self.converted[item][counter]["destination"]
				isNameChanged = self.converted[item][counter]["isNameChanged"]
				beforeChangedName = self.converted[item][counter]["beforeChangedName"]

				if isNameChanged:
					shutil.move(destination, beforeChangedName)
				
				shutil.move(destination, file)
				counter += 1

class unDuplicateFolderPopup(QUndoCommand):
	def __init__(self, index_list):
		super().__init__()
		self.index_list = index_list
		self.duplicated = []
	
	def redo(self):

		for index_fileinfo in self.index_list:
			selected_file = index_fileinfo.absoluteFilePath()
			selected_file_obj = Path(selected_file)
			new_folder = multiCopyHandler(selected_file)
			
			file = Path(new_folder)
			
			if selected_file_obj.is_dir():
				shutil.copytree(selected_file, new_folder)
			elif selected_file_obj.is_file():
				shutil.copyfile(selected_file, new_folder)
			
			self.duplicated.append(new_folder)
	
	def undo(self):
		
		for item in self.duplicated:
			file = QFile(item)
			file.moveToTrash()
		
		self.duplicated = []

class unMoveToRootPopup(QUndoCommand):
	file_data_list = []
	
	def __init__(self, index_list, root_path, override=False):
		super().__init__()
		self.index_list = index_list
		self.root_path = root_path
		self.override = override
	
	def redo(self):
		for index_fileinfo in self.index_list:
			file_name = index_fileinfo.absoluteFilePath()
			file = Path(file_name)

			isNameChanged = False
			beforeNameChanged = None

			transfer_file_name = Path(self.root_path, file.name)
			if transfer_file_name.exists():
				isNameChanged = True
				beforeNameChanged = file

				transfer_file_name = multiCopyHandler(transfer_file_name)

			shutil.move(file, transfer_file_name)

			file_data = {"file": file, 
							"destination": transfer_file_name, 
							"isNameChanged": isNameChanged, 
							"beforeChangedName": beforeNameChanged}
			self.file_data_list.append(file_data)
	
	def undo(self):
		for item in self.file_data_list:

			file = item["file"]
			destination = item["destination"]
			isNameChanged = item["isNameChanged"]
			beforeChangedName = item["beforeChangedName"]

			if isNameChanged:
				shutil.move(destination, beforeChangedName)
			
			shutil.move(destination, file)
		
		self.file_data_list = []

# -> message popups
class MessagePopUp(QMessageBox):
	def __init__(self, text, note, buttons = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No):
		super().__init__()
		self.setIcon(QMessageBox.Icon.Warning)
		self.setWindowTitle("Confirmation")
		self.setText(f"{text}")
		self.setInformativeText(f"Note: {note}")
		self.setStandardButtons(buttons)
		self.setDefaultButton(QMessageBox.StandardButton.No)

		# you can also use self.clickedButton() to access
		self.clickedbutton = self.exec()
		# self.m_exec = self.exec()

class MessageOverrideConfirmationPopUp():
	def __init__(self):
		
		overrideConfirmationPopup = MessagePopUp("Override the folder?", "You can still recover it from the recycle bin")

		if overrideConfirmationPopup.clickedbutton == QMessageBox.StandardButton.Yes:
			self.confirmOverride = True
		elif overrideConfirmationPopup.clickedbutton == QMessageBox.StandardButton.No:
			self.confirmOverride = False

class MessageOverridePopUp():
	def __init__(self):
		
		overridePopup = MessagePopUp("The folder with the same name already exists, \n Do you want to Override the old folder?", "If you want to just use the old folder just select No")

		if overridePopup.clickedbutton == QMessageBox.StandardButton.Yes:
			self.override = True
			self.confirmOverride = MessageOverrideConfirmationPopUp().confirmOverride
			
		elif overridePopup.clickedbutton == QMessageBox.StandardButton.No:
			self.override = False

class MessageBoxwLabel(QDialog):
	text = None

	def __init__(self):
		super().__init__()

		self.mainlayout = QVBoxLayout()
		# self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
		# self.setMinimumSize(self.sizeHint())

		self.lineedit = QLineEdit()
		self.mainlayout.addWidget(self.lineedit)

		self.button = QPushButton("Create Folder")
		self.mainlayout.addWidget(self.button)
		self.button.clicked.connect(self.click)

		# self.mainlayout.setSpacing(0)
		# self.setMaximumSize(self.minimumSizeHint())

		self.setLayout(self.mainlayout)
		
		self.returned = self.exec()
	
	def click(self):
		print("here")

		self.text = self.lineedit.text().strip()
		# self.close()
		self.done(1)

class ModScrollArea(QScrollArea):
	def __init__(self):
		super().__init__()
		# self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		# self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
		# self.setWidgetResizable(True)
		# self.setStyleSheet("border: 1px solid black")
		self.setAlignment(Qt.AlignmentFlag.AlignVCenter)
		# self.horizontalScrollBar().setEnabled(False)
	
	def setWidgetLayout(self, w: QWidget or QLayout) -> None:
		if isinstance(w, QWidget):
			self.setWidget(w)
		elif isinstance(w, QVBoxLayout):
			self.setLayout(w)

class ModLabel(QLabel):
	def __init__(self):
		super().__init__()

		self.setScaledContents(True)

# class ModifiedQLabel(QLabel):
# 	def __init__(self, effect=None):
# 		super().__init__()
		
# 		self.setMinimumWidth(300)
# 		self.setMaximumWidth(400)

# 		# self.setSizePolicy(QSizePolicy.Ma, QSizePolicy.Preferred)
# 		self.setSizePolicy(QSizePolicy.Expanding ,QSizePolicy.Expanding)
# 		# self.sizeIncrement().setWidth(0)
# 		# self.setFixedSize(self.size())

# 		self.setGraphicsEffect(effect)

# 		self.setStyleSheet("border: 1px solid black;")

# -> extensions

class ModPushButton(QPushButton):
	def __init__(self, icon, str_):
		super().__init__(icon, str_)

		self.setFixedWidth(30)

# -> separation
class QHSeparationLine(QFrame):
	"""
	a horizontal separation line\n
	"""

	def __init__(self):
		super().__init__()
		# self.setMinimumWidth(1)
		self.setFixedHeight(2)
		self.setFrameShape(QFrame.Shape.HLine)
		self.setFrameShadow(QFrame.Shadow.Sunken)
		self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

# -> models
# deprecated (needs to be ported to pyqt6)
class DirProxy(QSortFilterProxyModel):
	nameFilters = ''
	hideMode = False  # false to make it disable instead
	def __init__(self):
		super().__init__()
		self.dirModel = QFileSystemModel()
		self.dirModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files) # <- added QDir.Files to view all files
		self.setSourceModel(self.dirModel)

	def flags(self, index):
		enabled = (Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsEnabled)
		disabled = (Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)
		if not self.hideMode:
			index = self.mapToSource(index)
			if not index.isValid():
				return 0

			# Disable even rows, enable odd rows
			# if index.row() % 2 == 0:
			#     return Qt.NoItemFlags
			# else:
			#     return Qt.ItemIsEnabled
			if self.dirModel.isDir(index):
				qdir = QDir(self.dirModel.filePath(index))
				if self.nameFilters:
					qdir.setNameFilters(self.nameFilters)
				if bool(qdir.entryInfoList(qdir.NoDotAndDotDot|qdir.AllEntries|qdir.AllDirs)):
					return self.enabled
				else:
					return self.disabled

			else:  # <- index refers to a file
				qdir = QDir(self.dirModel.filePath(index))

				if qdir.match(self.nameFilters, self.dirModel.fileName(index)):
					return self.enabled
				else:
					return self.disabled # <- returns true if the file matches the nameFilters
		return self.enabled

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
		if self.hideMode:
			source = self.dirModel.index(row, 0, parent)
			if source.isValid():
				if self.dirModel.isDir(source):
					qdir = QDir(self.dirModel.filePath(source))
					if self.nameFilters:
						qdir.setNameFilters(self.nameFilters)
					return bool(qdir.entryInfoList(qdir.NoDotAndDotDot|qdir.AllEntries|qdir.AllDirs))

				elif self.nameFilters:  # <- index refers to a file
					qdir = QDir(self.dirModel.filePath(source))
					return qdir.match(self.nameFilters, self.dirModel.fileName(source)) # <- returns true if the file matches the nameFilters
			return True
		return True

	# -> reimplementation <- #
	def fileInfo(self, index):
		return self.dirModel.fileInfo(self.mapToSource(index))

	def rootPath(self):
		return self.dirModel.rootPath()

	def filePath(self, index):
		return self.dirModel.filePath(self.mapToSource(index))
	
	def isDir(self, index):
		return self.dirModel.isDir(self.mapToSource(index))
	# -> reimplementation <- #
# deprecated

class ModWebEngineView(QWebEngineView):
	def __init__(self, scrollArea):
		super().__init__()
		self.scrollArea :QScrollArea = scrollArea

		self.settings().setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
		self.settings().setAttribute(QWebEngineSettings.WebAttribute.PdfViewerEnabled, True)

		self.resize()

	def resize(self):
		# self.setGeometry(QRect(0, 0, self.scrollArea.width() - 2, self.scrollArea.height() - 2)) #exclude Margin
		self.setGeometry(QRect(0, 0, self.scrollArea.contentsRect().width(), self.scrollArea.contentsRect().height())) #exclude Margin
		# print(f"Size: {self.size()}, Rect: {self.rect()}")
		# print(f"Geometry: {self.frameGeometry()}")

class ModAction(QAction):
	def __init__(self, name: str, key_sequence: Qt.Key, parent: QWidget = None):
		# if error try self as parent
		super().__init__(name, parent=parent)
		self.setShortcutVisibleInContextMenu(True)
		self.setShortcut(key_sequence)
		self.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)

class Tree(QTreeView):
	# global project_filenames
	# global preview_types
	# global dir_path
	# global workstation_files
	# global thumbnail

	isLeft  = False
	isRight = False
	current_key = None

	def __init__(self, model):
		super().__init__()
		delegate = DisDelegate(self)
		# self.setItemDelegateForColumn(0, delegate)
		self.setItemDelegate(delegate)
		
		self.undostack = QUndoStack()

		self.setSizePolicy(QSizePolicy.Policy.Expanding,QSizePolicy.Policy.Expanding)
		self.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
		self.customContextMenuRequested.connect(self.context_menu)
		self.setDragDropMode(QAbstractItemView.DragDropMode.DragDrop)
		self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
		self.doubleClicked.connect(self.openFile)
		self.setDefaultDropAction(Qt.DropAction.CopyAction)
		self.viewport().setAcceptDrops(True)
		self.setAlternatingRowColors(True)
		self.setDropIndicatorShown(True)

		self.setModel(model)

		# self.resizeColumnToContents(0)
		self.header().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)

		self.renameAction = ModAction('Rename', Qt.Key.Key_F2, parent=self)
		self.renameAction.triggered.connect(lambda event: self.renameFileFolder(event))

		self.deleteFileAction = ModAction('Delete', Qt.Key.Key_Delete, parent=self)
		self.deleteFileAction.triggered.connect(lambda event: self.deleteFile(event))
		
		self.removeOuterFolderAction = ModAction('Delete Outer Folder', QKeySequence(Qt.Modifier.SHIFT | Qt.Key.Key_Delete), parent=self)
		self.removeOuterFolderAction.triggered.connect(lambda event: self.removeOuterFolderPopup(event))

		self.moveToNewFolderAction = ModAction('Move to New Folder', QKeySequence(Qt.Modifier.ALT | Qt.Modifier.SHIFT | Qt.Key.Key_N), self)
		# self.moveToNewFolderAction.setShortcut(QKeySequence("Alt+Shift+N"))
		self.moveToNewFolderAction.triggered.connect(lambda event: self.MovetoNewFolderPopup(event))

		self.createFolderAction = ModAction('Create Folder', QKeySequence(Qt.Modifier.CTRL | Qt.Modifier.SHIFT | Qt.Key.Key_N), parent=self)
		self.createFolderAction.triggered.connect(lambda event: self.createFolderPopup(event))
		
		self.duplicateFileFolderAction = ModAction('Duplicate', QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_J), parent=self)
		self.duplicateFileFolderAction.triggered.connect(lambda event: self.duplicateFolderPopup(event))

		self.moveToRootAction = ModAction('Move to Root', QKeySequence(Qt.Modifier.CTRL | Qt.Modifier.SHIFT | Qt.Key.Key_Up), parent=self)
		self.moveToRootAction.triggered.connect(lambda event: self.moveToRootPopUp(event))

		self.addAction(self.renameAction)
		self.addAction(self.deleteFileAction)
		self.addAction(self.duplicateFileFolderAction)
		self.addAction(self.moveToRootAction)
		self.addAction(self.removeOuterFolderAction)
		self.addAction(self.moveToNewFolderAction)
		self.addAction(self.createFolderAction)

	def keyPressEvent(self, event):
		#try Key_Control if problem occurs
		if event.key() == (Qt.Key.Key_Control and Qt.Key.Key_Y):
			self.undostack.redo()
		if event.key() == (Qt.Key.Key_Control and Qt.Key.Key_Z):
			self.undostack.undo()

	def checkDrag(self):
		modifiers = QApplication.instance().queryKeyboardModifiers()
		if self.modifiers != modifiers:
			self.modifiers = modifiers
			pos = QCursor.pos()
			# slightly move the mouse to trigger dragMoveEvent
			QCursor.setPos(pos + QPoint(1, 1))
			# restore the previous position
			QCursor.setPos(pos)

	def mousePressEvent(self, event):
		# print(self.indexAt(event.pos()).row())
		# if event.button() == Qt.LeftButton:
			# self.setCurrentIndex(self.indexAt(event.pos()))
			# self.selectionStart = event.pos
		# if event.button() == Qt.MouseButton.RightButton:
		self.dragStartPosition = event.pos()

		return super().mousePressEvent(event)

	def mouseMoveEvent(self, event):
		# if event.buttons() != Qt.MouseButton.RightButton:
			# return

		# elif event.buttons() == Qt.LeftButton:
		#     self.setSelection(QRect(self.selectionStart, event.pos()),QItemSelectionModel.Select)
		if ((event.pos() - self.dragStartPosition).manhattanLength() < QApplication.startDragDistance()):
			return

		print("dragging")
		self.modifiers = QApplication.instance().queryKeyboardModifiers()
		# a local timer, it will be deleted when the function returns
		dragTimer = QTimer(interval=500, timeout=self.checkDrag) # 100
		dragTimer.start()
		self.startDrag(Qt.DropAction.MoveAction|Qt.DropAction.CopyAction)

	def openFile(self, index):
		print("opening")
		selected_index = [index] if len(self.selectedIndexes()) == 0 else [index_ if index_.column() == 0 else None for index_ in self.selectedIndexes()]

		if len(selected_index) > 5:
			msgBox = MessagePopUp(f"Welp! Are you sure you want to open {len(selected_index)} files consecutively?", "This will slow down the prosessing")
			if msgBox.clickedbutton == QMessageBox.StandardButton.No:
				return

		# if self.isLeft:  # make the final mechanism
		# 	for indep in selected_index:
		# 		if indep.column() == 0:
		# 			model = index.model()
		# 			fileinfo = model.fileInfo(indep)

		# 			complete_proj_file = fileinfo.absoluteFilePath()

		# 			# temp_project_path = f"{temp}/{self.fileName}"
					
		# 			# if not os.path.exists(temp_project_path):
		# 			# 	os.mkdir(temp_project_path)
					
		# 			# files_list = os.listdir(self.project_dir)
		# 			# print(files_list)
		# 			# for item in files_list:
		# 			# 	print(f"{self.project_dir}{item} {temp_project_path}/{item}")
		# 			# 	os.link(f"{self.project_dir}{item}", f"{temp_project_path}/{item}")
		# 			# 	# print(f"""mklink /h \"{temp_project_path}/{item}\" \"{self.project_dir}{item}\" """)
		# 			# 	# subprocess.run(f"""mklink /h \"{temp_project_path}/{item}\" \"{self.project_dir}{item}\" """)

		# 			# os.link(complete_proj_file, f"{temp_project_path}/{self.fileName}")

		# 			# print(f"""ln --recursive \"{self.project_dir}\" \"{temp_project_path}\"""")
		# 			# subprocess.run(f"""ln --recursive \"{self.project_dir}\" \"{temp_project_path}\"""")
				
		# 			QDesktopServices.openUrl(QUrl.fromLocalFile(complete_proj_file))

		# 		# note if the file is already open, then when a file is dropped on the self.project_dir (.ai folder) we just make a hard link to the tem_project_path
		
		# elif self.isRight:
		# 	for indep in selected_index:
		# 		if indep.column() == 0:
		# 			model = index.model()
		# 			fileinfo = model.fileInfo(indep)
		# 			QDesktopServices.openUrl(QUrl.fromLocalFile(fileinfo.absoluteFilePath()))

		# same opem mechanism for both tree
		for indep in selected_index:
			model = self.model()
			fileinfo = model.fileInfo(indep)
			path = fileinfo.absoluteFilePath()

			QDesktopServices.openUrl(QUrl.fromLocalFile(path))

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
		if QApplication.instance().queryKeyboardModifiers() & Qt.KeyboardModifier.ShiftModifier:
			event.setDropAction(Qt.DropAction.MoveAction)
		else:
			event.setDropAction(Qt.DropAction.CopyAction)
		event.accept()

	def dropEvent(self, event):
		print("[drop event] - dropped")

		dropAction = event.dropAction()

		# if event.source():
		ix = self.indexAt(event.position().toPoint())
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
					if dropAction == Qt.DropAction.CopyAction:
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

					elif dropAction == Qt.DropAction.MoveAction:
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

					if dropAction == Qt.DropAction.CopyAction:
						# destination = 
						qfile.copy(destination)
					elif dropAction == Qt.DropAction.MoveAction:
						qfile.rename(destination)
					print(f"added -> {info.fileName()}")  # for debugging

				accepted = True
			if accepted:
				event.acceptProposedAction()

		# def canDropMimeData(self, data: QMimeData, action: Qt.DropAction, row: int, column: int, parent: QModelIndex) -> bool:
		# 	print(f"row {row}, col {column}")
		# 	if row < 0 and column < 0:
		# 		target = self.fileInfo(parent)
		# 	else:
		# 		target = self.fileInfo(self.index(row, column, parent))
		# 	return target.isDir() and target.isWritable()

		# context menu #
		pass

	@dispatch(QModelIndex)
	def Mexpand(self, index: QModelIndex):
		self.expand(index)
	
	@dispatch(list)
	def _(self, index_list: list[QModelIndex]):
		for index in index_list:
			self.expand(index)

	# note to fuse the shift mode and non shift mode, just recieve the path and proceed
	def context_menu(self, event):
		# print(f"sender -> {self.tree_sender.sender()}") 
		# self.tree_sender = self.sender()
		# self.model_sender = self.model()

		self.menu = QMenu(self)

		# self.addAction(renameAction)

		self.menu.addAction(self.renameAction)
		self.menu.addAction(self.deleteFileAction)
		self.menu.addAction(self.duplicateFileFolderAction)
		self.menu.addAction(self.moveToRootAction)
		self.menu.addAction(self.removeOuterFolderAction)
		self.menu.addSeparator()
		self.menu.addAction(self.moveToNewFolderAction)
		self.menu.addAction(self.createFolderAction)

		# self.modifier_pressed = QApplication.instance().queryKeyboardModifiers()
		# if self.modifier_pressed == Qt.KeyboardModifier.ShiftModifier:
			# print("Shift Pressed")

		# add other required actions
		self.menu.popup(QCursor.pos())
	
	#-> do file operations
	def createFolderPopup(self, event):
		# note if selected is empty then just create a new folder
		model = self.model()  # proxy model not needed

		popup = MessageBoxwLabel()
		if popup.returned == QDialog.DialogCode.Accepted:
			print("algorithim for creating folders")

			#warning: check if the folder exist

			index_list = self.selectedIndexes()
			index_list = [index for index in index_list if index.column() == 0]

			if index_list:
				#-> try to detect if any folders to be created is already existing
				ret = exists(index_list, popup.text)
				if ret == True:
					override = MessageOverridePopUp().override
				elif isinstance(ret, list):
					override = False
					newfolder_list = ret
				else: #-> one is not a folder
					return MessagePopUp("Please only select a folder", "The folder will be created inside the selected folders", buttons=QMessageBox.StandardButton.Ok)

				unCreateFolder = doCreateFolder("", override, newfolder_list, model)
				self.undostack.push(unCreateFolder)

			else:
				# if self.modifier_pressed != Qt.KeyboardModifier.ShiftModifier:
				new_folder = model.rootPath() + QDir.separator() + popup.text  # note not root path()
				
				if not exists(new_folder):
					# os.mkdir(new_folder)
					override = False
				else:
					# -> Prompt if override or just use that folder
					override = MessageOverridePopUp().override
					# > if no , need after verification of multi copy handler
					
				unCreateFolder = doCreateFolder(new_folder, override)
				self.undostack.push(unCreateFolder)

				# note convert this to a redo method and just get tje new folder value and delete it
				# note incase cancel was clicked, don't remove its folder and just move the files

				#-> When there is selected folder, just create folder inside it
				# elif self.modifier_pressed == Qt.KeyboardModifier.ShiftModifier:
				# 	print("[createFolderPopup] - Shift Mode")
				# 	for index in index_list:
				# 		if index.column() == 0:
				# 			fileIn = model.fileInfo(index)
				# 			if fileIn.isDir():
				# 				new_folder = fileIn.absoluteFilePath() + QDir.separator() + popup.text

				# 				if not os.path.exists(new_folder):
				# 					# os.mkdir(new_folder)
				# 					pass
				# 				else:
				# 					# -> Prompt if override or just use that folder
				# 					override = MessageOverridePopUp().override
				# 					# > if no , need after verification of multi copy handler
								
				# 				if 'override' in globals():
				# 					unCreateFolder = doCreateFolder(new_folder, override=override)
				# 				else:
				# 					unCreateFolder = doCreateFolder(new_folder)

				# 				self.undostack.push(unCreateFolder)

	def renameFileFolder(self, event):
		print("renaming")
		# note if selected is empty then do nothing
		# note if only one is selected propmt the override
		# then if multiple is selected just take a way around the renaming
		model = self.model()

		popup = MessageBoxwLabel()
		if popup.returned == QDialog.DialogCode.Accepted:
			print("algorithim for creating folders")

			#warning: check if the folder exist

			index_list = self.selectedIndexes()

			print(f"Folder Name -> '{popup.text}'")
			# for index in index_list:
			# 	if index.column() == 0:
			# 		fileIn = model.fileInfo(index)
			# 		# new_file = os.path.join(model.rootPath(), popup.folder_name)  # note not root path()
			# 		new_file = fileIn.absolutePath() + QDir.separator() + popup.folder_name  # note not root path()
			index_list = [model.fileInfo(index) for index in index_list if index.column() == 0]
			
			if len(index_list) == 1:
				new_file = index_list[0].absolutePath() + QDir.separator() + popup.text + "." + index_list[0].suffix()
				if not os.path.exists(new_file):
					# -> just move the folder/files
					# os.rename(fileIn.absoluteFilePath(), new_file)
					override = False
					pass
				else:
					# -> Prompt if override or just use that folder
					msgBox = MessagePopUp("The file/folder with the same name already exists, \n Do you want to Override the old file/folder?", "If you want to just use the old folder just select No", buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
					if msgBox.clickedbutton == QMessageBox.StandardButton.Yes:
						inmsgBox = MessagePopUp("Override the folder?", "You can still recover it from the recycle bin")
						# -> Override
						if inmsgBox.clickedbutton == QMessageBox.StandardButton.Yes:
							# #-> deleting file/folder
							# shutil.rmtree(new_file)
							# #-> creating file/folder
							# os.mkdir(new_file)
							override = True

							if os.path.isdir(new_file):
								print(f"isDir -> {new_file}")
								shutil.rmtree(new_file)
								
							elif os.path.isfile(new_file):  
								os.remove(new_file)
								print(f"isFile -> {new_file}")
							
							# Move the content
							# source to destination
							# os.rename(fileIn.absoluteFilePath(), new_file)

						elif inmsgBox.clickedbutton == QMessageBox.StandardButton.No:
							return

					elif msgBox.clickedbutton == QMessageBox.StandardButton.No:
						# -> Don't Override
						# counter = 1
						# while os.path.exists(new_file):
						# 	base_file = new_file
							
						# 	new_file = base_file + f" (copy {counter})"

						# 	counter += 1
						new_file = multiCopyHandler(new_file)

						# os.rename(fileIn.absoluteFilePath(), new_file)
						override = False

					elif msgBox.clickedbutton == QMessageBox.StandardButton.Cancel:
						# -> Cancel
						pass

				unRename = unRenamePopup(new_file, index_list, onefile=True)
				self.undostack.push(unRename)

			elif len(index_list) > 1:
				unRename = unRenamePopup(popup.text, index_list, onefile=False)
				self.undostack.push(unRename)

	def MovetoNewFolderPopup(self, event):
		# note if selected is empty then do nothing
		model = self.model()
		# model = proxyModel.sourceModel()

		popup = MessageBoxwLabel()
		if popup.returned == QDialog.DialogCode.Accepted:
			print("algorithim for moving to new folders")

			#warning: check if the folder exist

			index_list = self.selectedIndexes()
			index_list = [index for index in index_list if index.column() == 0]

			print(f"Folder Name -> '{popup.text}'")
			if index_list:
				# if self.modifier_pressed != Qt.KeyboardModifier.ShiftModifier:
				new_folder = model.rootPath() + QDir.separator() + popup.text  # note not root path()
				
				ret = exists(index_list, popup.text)
				if ret == True:
					override = MessageOverridePopUp().override
				elif isinstance(ret, list):
					override = False
					newfolder_list = ret
				else:
					return MessagePopUp("Please only select a folder", " The folder will be created inside the selected folders", buttons=QMessageBox.StandardButton.Ok)
				
				#-> need preprocessing of multiCopyHandler
				unMoveToNewFolder = unMoveToNewFolderPopup(self, new_folder, index_list, model, override=override)
				self.undostack.push(unMoveToNewFolder)

					# note convert this to a redo method and just get tje new folder value and delete it
					# note incase cancel was clicked, don't remove its folder and just move the files
					# for index in index_list:
					# 	if index.column() == 0:
					# 		fileIn = model.fileInfo(index)
					# 		# fileIn = model.fileInfo(proxyModel.mapToSource(index))

					# 		#warning: make sure that the folder will actually make the folder inside
				
					# 		# if not fileIn.isDir():
					# 		# True_or_False = f"{fileIn.canonicalPath()} == {model.rootPath()} : {fileIn.canonicalPath() == model.rootPath()}"
					# 		# True_or_False = f"{model.rootPath()} in {fileIn.canonicalPath()} : {model.rootPath() in fileIn.canonicalPath()}"
					# 		if (fileIn.canonicalPath() == model.rootPath()) or (model.rootPath() in fileIn.canonicalPath()):  #warning: checking if the files are in the same of the rootfolder
					# 			file_to_rename = fileIn.absoluteFilePath()
					# 			print(file_to_rename)
					# 			shutil.move(file_to_rename, new_folder)

				# elif self.modifier_pressed == Qt.KeyboardModifier.ShiftModifier:
				# 	print("[MovetoNewFolderPopup] -> Shift Mode")
				# 	fileIn = model.fileInfo(index_list[0])
				# 	new_folder = fileIn.absolutePath() + QDir.separator() + popup.text  # note not root path()
					
				# 	if not os.path.exists(new_folder):
				# 		os.mkdir(new_folder)
				# 	else:
				# 		#warning: Prompt if override or just use that folder
				# 		msgBox = MessagePopUp("The folder with the same name already exists, \n Do you want to Override the old folder?", "If you want to just use the old folder just select No")
				# 		if msgBox.clickedbutton == QMessageBox.StandardButton.Yes:
				# 			inmsgBox = MessagePopUp("Override the folder?", "You can still recover it from the recycle bin")
				# 			# -> Override
				# 			if inmsgBox.clickedbutton == QMessageBox.StandardButton.Yes:
				# 				#-> deleting folder
				# 				shutil.rmtree(new_folder)
				# 				#-> creating folder
				# 				os.mkdir(new_folder)

				# 			elif inmsgBox.clickedbutton == QMessageBox.StandardButton.No:
				# 				return

				# 		elif msgBox.clickedbutton == QMessageBox.StandardButton.No:
				# 			# -> Don't Override
				# 			pass

				# 	for index in index_list:
				# 		if index.column() == 0:
				# 			fileIn = model.fileInfo(index)

				# 			#warning: make sure that the folder will actually make the folder inside
				
				# 			# if not fileIn.isDir():
				# 			True_or_False = f"{fileIn.canonicalPath()} == {model.rootPath()} : {fileIn.canonicalPath() == model.rootPath()}"
				# 			True_or_False = f"{model.rootPath()} in {fileIn.canonicalPath()} : {model.rootPath() in fileIn.canonicalPath()}"
				# 			if (fileIn.canonicalPath() == model.rootPath()) or (model.rootPath() in fileIn.canonicalPath()):  #warning: checking if the files are in the same of the rootfolder
				# 				file_to_rename = fileIn.absoluteFilePath()
				# 				print(file_to_rename)
				# 				shutil.move(file_to_rename, new_folder)

	def deleteFile(self, event):
		# print(f"deleting... {self.tree.currentIndex()}")
		# index_list = [self.tree.currentIndex()]
		
		msgBox = MessagePopUp("Do you want to continue?", "You can still recover the file/folder in the recycle bin")

		print(f"{msgBox} : {QMessageBox.StandardButton.Yes} : {msgBox == QMessageBox.StandardButton.Yes}")

		#warning: not working

		if msgBox.clickedbutton == QMessageBox.StandardButton.Yes:
			model = self.model()

			index_list = self.selectedIndexes()

			index_list = [model.fileInfo(index) for index in index_list if index.column() == 0]

			unDeleteFile = unDeleteFilePopup(index_list)
			self.undostack.push(unDeleteFile)

	def removeOuterFolderPopup(self, event):
		# note if selected is empty then do nothing

		model = self.model()

		index_list = self.selectedIndexes()
		index_list = [model.fileInfo(index) for index in index_list if index.column() == 0]
		folder_to_be_deleted_list = [index.canonicalPath() for index in index_list]
	
		list_of_to_be_deleted = "\n".join(folder_to_be_deleted_list)

		# for index_fileinfo in index_list:
		# 	# ->
		# 	filepath = index_fileinfo.absoluteFilePath()
		# 	canon_filepath = index_fileinfo.canonicalPath()
			# ->

		# new_file = os.path.join(model.rootPath(), popup.folder_name)  # note not root path()
		# new_folder = model.rootPath() + QDir.separator() +   # note not root path()
		
		# -> Prompt if they are sure
		inmsgBox = MessagePopUp(f"Delete the folder \n {list_of_to_be_deleted}", "You can still recover it from the recycle bin")
		if inmsgBox.clickedbutton == QMessageBox.StandardButton.Yes:
			
			# parent_dir.rmdir()
			# shutil.move()
			# index_list = [model.fileInfo(index) for index in index_list if index.column() == 0]
			unRemoveOuterFolder = unRemoveOuterFolderPopup(index_list, override=False)
			self.undostack.push(unRemoveOuterFolder)

		elif inmsgBox.clickedbutton == QMessageBox.StandardButton.No:
			pass

	def duplicateFolderPopup(self, event):
		# note if selected is empty then do nothing

		model = self.model()

		print("algorithim for creating folders")

		#warning: check if the folder exist

		index_list = self.selectedIndexes()
		index_list = [model.fileInfo(index) for index in index_list if index.column() == 0]

		unDuplicateFolder = unDuplicateFolderPopup(index_list)
		self.undostack.push(unDuplicateFolder)

		# for index in index_list:
		# 	if index.column() == 0:
		# 		fileIn: QFileInfo = model.fileInfo(index)

		# 		selected_file = fileIn.absoluteFilePath()
		# 		new_folder = multiCopyHandler(selected_file)
				
		# 		if not os.path.exists(new_folder):  # you can diable this if statement but try to catch an error
		# 			os.mkdir(new_folder)

		# 	# note convert this to a redo method and just get tje new folder value and delete it
		# 	# note incase cancel was clicked, don't remove its folder and just move the files;
		# 		# file_to_rename = fileIn.absoluteFilePath()
		# 		# print(file_to_rename)
		# 		shutil.copytree(selected_file, new_folder)

	def moveToRootPopUp(self, event):
		# note if selected is empty then do nothing

		model: QFileSystemModel = self.model()

		print("algorithim for creating folders")

		#warning: check if the folder exist

		index_list = self.selectedIndexes()
		index_list = [model.fileInfo(index) for index in index_list if index.column() == 0]

		# for index in index_list:
		# 	if index.column() == 0:
		# 		fileIn: QFileInfo = model.fileInfo(index)

		# 		selected_file = fileIn.absoluteFilePath()
		# 		# new_folder = multiCopyHandler(selected_file)
				
		# 		# if not os.path.exists(new_folder):  # you can diable this if statement but try to catch an error
		# 		# 	os.mkdir(new_folder)

		# 	# note convert this to a redo method and just get tje new folder value and delete it
		# 	# note incase cancel was clicked, don't remove its folder and just move the files;
		# 		# file_to_rename = fileIn.absoluteFilePath()
		# 		# print(file_to_rename)
		# 		shutil.move(selected_file, model.rootPath())

		unMoveToRoot = unMoveToRootPopup(index_list, model.rootPath(),override=False)
		self.undostack.push(unMoveToRoot)

class FileSystemModel(QFileSystemModel):
	# hideMode = False
	_nameFilters = []
	def __init__(self):
		super().__init__()
		# self.setNameFilterDisables(False)

	def hasChildren(self, parent):
		# flags = [1, 1024, 2, 4, 8, 8192, 16384, 16, 32, 64, 128, 256, 512, 2048]
		# flgs = self.filter()
		# print([flag if flgs & flag == 0 else None for flag in flags])

		_dir = QDir(self.filePath(parent))
		return bool(_dir.entryList(self.filter()))

class DisDelegate(QStyledItemDelegate):
	# hideMode = False
	def initStyleOption(self, option: 'QStyleOptionViewItem', index: QModelIndex) -> None:
		super().initStyleOption(option, index)
		# row = index.row()
		model = index.model()
		
		if not index.isValid():
			return
		
		qdir = model.filePath(index)
		
		if model.isDir(index):
			qdir = QDir(model.filePath(index))
			qdir.setNameFilters(model._nameFilters)

			bl = qdir.entryList(qdir.Filter.NoDotAndDotDot | qdir.Filter.AllEntries)

			if bool(bl):
				pass
			else:
				# option.palette.setBrush(QPalette.Base, Qt.red)
				option.palette.setBrush(QPalette.ColorRole.Text, QColor("#9a9a9a"))
				# option.backgroundBrush = QColor("#eeeeee")
		else:  # <- index refers to a file

			# looks like the color in the column 0, will be the colum of the row
			# if index.column() != 0:
				# return super().initStyleOption(option, index)
				# pass

			qdir = QDir(model.fileName(index))

			c = qdir.match(model._nameFilters, model.fileName(index))
			if c:
				pass
			else:
				# option.palette.setBrush(QPalette.Base, Qt.red)
				option.palette.setBrush(QPalette.ColorRole.Text, QColor("#9a9a9a"))
				# option.backgroundBrush = QColor("#eeeeee")

class ReadOnlyDelegate(QStyledItemDelegate):
	def initStyleOption(self, option: QStyleOptionViewItem, index: QModelIndex) -> None:
		super().initStyleOption(option, index)

		if index.flags() & Qt.ItemFlag.ItemIsEditable:
			option.palette.setBrush(QPalette.Text, QColor("#dc0f14"))
			# option.backgroundBrush = QBrush(QColor("#dc0f14"))
		else:
			option.palette.setBrush(QPalette.Text, QColor("#3daa33"))
			# option.backgroundBrush = QBrush(QColor("#3daa33"))

