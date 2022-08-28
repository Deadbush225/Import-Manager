from PyQt6.QtWidgets import QTreeView, QAbstractItemView, QSizePolicy, QHeaderView, QApplication, \
	QMessageBox, QMenu, QDialog
from PyQt6.QtGui import QUndoStack, QKeySequence, QCursor, QDesktopServices
from PyQt6.QtCore import Qt, QPoint, QTimer, QUrl, QFileInfo, QDir

from _subclassed import DisDelegate, ModAction, MessagePopUp, MessageBoxwLabel, MessageOverridePopUp

from _helpers import multiCopyHandler, 

from _undoCommands import *

import shutil
import os

class Tree(QTreeView):

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
		if event.buttons() == Qt.MouseButton.NoButton:
			return

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
				destination = QDir(pathDir).filePath(info.fileName()) # <- check if this one OV_exists
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

	#[Overload] - OV_expand
	@dispatch(QModelIndex)
	def OV_expand(self, index: QModelIndex):
		self.expand(index)
	
	@dispatch(list)
	def OV_expand(self, index_list: list[QModelIndex]):
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
			#> Intended Behavior:
			#>		If no item is selected, folder will be created inside the root
			#>		If [1|+] is selected, folder will be created inside the selected folders
			
			print("algorithim for creating folders")

			#warning: check if the folder exist

			index_list = self.selectedIndexes()
			index_list = [index for index in index_list if index.column() == 0]

			
			ret = OV_exists(index_list, popup.text, model)
				
			newfolder_list = []
			new_folder = model.rootPath() + QDir.separator() + popup.text
			override = False if ret != True else MessageOverridePopUp().override
			
			print(f"override: {override}")

			if isinstance(ret, list): # -> multiple item is selected
				newfolder_list = ret

			elif ret == None: #-> one of the selections are not a folder (don't include 'True')
				return MessagePopUp("Please only select a folder", "The folder will be created inside the selected folders", buttons=QMessageBox.StandardButton.Ok)

			unCreateFolder = doCreateFolder(new_folder, override, newfolder_list, model)
			self.undostack.push(unCreateFolder)
			

			# note convert this to a redo method and just get tje new folder value and delete it
			# note incase cancel was clicked, don't remove its folder and just move the files

			#-> When there is selected folder, just create folder inside it
				
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
					msgBox = MessagePopUp("The file/folder with the same name already OV_exists, \n Do you want to Override the old file/folder?", "If you want to just use the old folder just select No", buttons=QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel)
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

				unRename = doRenamePopup(new_file, index_list, onefile=True)
				self.undostack.push(unRename)

			elif len(index_list) > 1:
				unRename = doRenamePopup(popup.text, index_list, onefile=False)
				self.undostack.push(unRename)
				
			#> need move mutlifile dndler in Undoable

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
				
				ret = OV_exists(index_list, popup.text)
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
				# 		msgBox = MessagePopUp("The folder with the same name already OV_exists, \n Do you want to Override the old folder?", "If you want to just use the old folder just select No")
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
