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

from _subclassed import *
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
# temp               = r'D:/Student - Files/Eliazar/temp'
# recycle_bin        = r"D:/Student - Files/Eliazar/recycle bin"
# left_main_dirpath  = r"D:/Student - Files/Eliazar/Project Files"
# right_main_dirpath = r"D:/Student - Files/Eliazar/Random Raw Files"

class unCreateFolderPopup(QUndoCommand):
	def __init__(self, newfolder, override=False):
		super().__init__()
		self.new_folder = newfolder
		self.override = override

	def redo(self):
		print('redoing')
		if self.override:

			# -> deleting folder
			file = QFile(self.new_folder)
			self.restore_path = file.fileName()

			dele = file.moveToTrash()
			# print(dele)
			self.recycle_path = file.fileName()

			# deleteF(self.new_folder) #moved | use deleteF
			# -> creating folder
			os.mkdir(self.new_folder) #moved
			return

		os.mkdir(self.new_folder)
	
	def undo(self):
		print('undoing')
		if self.override:
			shutil.move(self.recycle_path, self.restore_path)
		
		QFile(self.new_folder).moveToTrash()


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
		delegate = DisDelegate(self)
		# self.setItemDelegateForColumn(0, delegate)
		self.setItemDelegate(delegate)
		
		self.undostack = QUndoStack()

		self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
		self.setSelectionMode(QAbstractItemView.ExtendedSelection)
		self.customContextMenuRequested.connect(self.context_menu)
		self.setDragDropMode(QAbstractItemView.DragDrop)
		self.setContextMenuPolicy(Qt.CustomContextMenu)
		self.doubleClicked.connect(self.openFile)
		self.setDefaultDropAction(Qt.CopyAction)
		self.viewport().setAcceptDrops(True)
		self.setAlternatingRowColors(True)
		self.setDropIndicatorShown(True)

		self.setModel(model)

		self.header().setSectionResizeMode(0, QHeaderView.ResizeToContents)
		# self.resizeColumnToContents(0)

		# current_palette = self.palette()
		# print(f"State: Normal - alternateBase: {current_palette.brush(QPalette.AlternateBase).color().name()}")
		# print(f"State: Normal - base: {current_palette.brush(QPalette.Base).color().name()}")
		# print(f"State: Normal - text: {current_palette.brush(QPalette.Text).color().name()}")

		# print(f"State: Disabled - alternateBase: {current_palette.brush(QPalette.Disabled, QPalette.AlternateBase).color().name()}")
		# print(f"State: Disabled - base: {current_palette.brush(QPalette.Disabled, QPalette.Base).color().name()}")
		# print(f"State: Disabled - text: {current_palette.brush(QPalette.Disabled, QPalette.Text).color().name()}")

	def keyPressEvent(self, event):
		if event.key() == (Qt.Key_Control and Qt.Key_Y):
			self.undostack.redo()
		if event.key() == (Qt.Key_Control and Qt.Key_Z):
			self.undostack.undo()

	def checkDrag(self):
		modifiers = qApp.queryKeyboardModifiers()
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
		if event.button() == Qt.RightButton:
			self.dragStartPosition = event.pos()

		return super().mousePressEvent(event)

	def mouseMoveEvent(self, event):
		if event.buttons() != Qt.RightButton:
			return
		# elif event.buttons() == Qt.LeftButton:
		#     self.setSelection(QRect(self.selectionStart, event.pos()),QItemSelectionModel.Select)
		if ((event.pos() - self.dragStartPosition).manhattanLength() < QApplication.startDragDistance()):
			return

		print("dragging")
		self.modifiers = qApp.queryKeyboardModifiers()
		# a local timer, it will be deleted when the function returns
		dragTimer = QTimer(interval=500, timeout=self.checkDrag) # 100
		dragTimer.start()
		self.startDrag(Qt.MoveAction|Qt.CopyAction)

	def openFile(self, index):
		
		selected_index = self.selectedIndexes()

		if len(selected_index) > 5:
			msgBox = MessagePopUp(f"Welp! Are you sure you want to open {len(selected_index)} files consecutively?", "This will slow down the prosessing")
			if msgBox.clickedbutton == QMessageBox.No:
				return

		if self.isLeft:  # make the final mechanism
			for indep in selected_index:
				if indep.column() == 0:
					model = index.model()
					fileinfo = model.fileInfo(indep)

					complete_proj_file = fileinfo.absoluteFilePath()

					# temp_project_path = f"{temp}/{self.fileName}"
					
					# if not os.path.exists(temp_project_path):
					# 	os.mkdir(temp_project_path)
					
					# files_list = os.listdir(self.project_dir)
					# print(files_list)
					# for item in files_list:
					# 	print(f"{self.project_dir}{item} {temp_project_path}/{item}")
					# 	os.link(f"{self.project_dir}{item}", f"{temp_project_path}/{item}")
					# 	# print(f"""mklink /h \"{temp_project_path}/{item}\" \"{self.project_dir}{item}\" """)
					# 	# subprocess.run(f"""mklink /h \"{temp_project_path}/{item}\" \"{self.project_dir}{item}\" """)

					# os.link(complete_proj_file, f"{temp_project_path}/{self.fileName}")

					# print(f"""ln --recursive \"{self.project_dir}\" \"{temp_project_path}\"""")
					# subprocess.run(f"""ln --recursive \"{self.project_dir}\" \"{temp_project_path}\"""")
				
					QDesktopServices.openUrl(QUrl.fromLocalFile(complete_proj_file))

				# note if the file is already open, then when a file is dropped on the self.project_dir (.ai folder) we just make a hard link to the tem_project_path
		
		elif self.isRight:
			for indep in selected_index:
				if indep.column() == 0:
					model = index.model()
					fileinfo = model.fileInfo(indep)
					QDesktopServices.openUrl(QUrl.fromLocalFile(fileinfo.absoluteFilePath()))

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
			event.setDropAction(Qt.MoveAction)
		else:
			event.setDropAction(Qt.CopyAction)
		event.accept()

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

	# def canDropMimeData(self, data: QMimeData, action: Qt.DropAction, row: int, column: int, parent: QModelIndex) -> bool:
	# 	print(f"row {row}, col {column}")
	# 	if row < 0 and column < 0:
	# 		target = self.fileInfo(parent)
	# 	else:
	# 		target = self.fileInfo(self.index(row, column, parent))
	# 	return target.isDir() and target.isWritable()

	# context menu #
	# note to fuse the shift mode and non shift mode, just recieve the path and proceed
	def context_menu(self, event):
		# print(f"sender -> {self.tree_sender.sender()}") 
		# self.tree_sender = self.sender()
		# self.model_sender = self.model()

		self.menu = QMenu(self)

		renameAction = QAction('Rename', self)
		renameAction.triggered.connect(lambda event: self.renameFileFolder(event))

		deleteFileAction = QAction('Delete', self)
		deleteFileAction.triggered.connect(lambda event: self.deleteFile(event))
		
		removeOuterFolderAction = QAction('Delete Outer Folder', self)
		removeOuterFolderAction.triggered.connect(lambda event: self.removeOuterFolderPopup(event))

		moveToNewFolderAction = QAction('Move to New Folder', self)
		moveToNewFolderAction.triggered.connect(lambda event: self.MovetoNewFolderPopup(event))

		createFolderAction = QAction('Create Folder', self)
		createFolderAction.triggered.connect(lambda event: self.createFolderPopup(event))
		
		duplicateFileFolderAction = QAction('Duplicate', self)
		duplicateFileFolderAction.triggered.connect(lambda event: self.duplicateFolderPopup(event))

		moveToRootAction = QAction('Move to Root', self)
		moveToRootAction.triggered.connect(lambda event: self.moveToRootPopUp(event))

		self.menu.addAction(renameAction)
		self.menu.addAction(deleteFileAction)
		self.menu.addAction(duplicateFileFolderAction)
		self.menu.addAction(moveToRootAction)
		self.menu.addAction(removeOuterFolderAction)
		self.menu.addSeparator()
		self.menu.addAction(moveToNewFolderAction)
		self.menu.addAction(createFolderAction)

		self.modifier_pressed = qApp.queryKeyboardModifiers()
		if self.modifier_pressed == Qt.ShiftModifier:
			print("Shift Pressed")

		# add other required actions
		self.menu.popup(QCursor.pos())
	
	def createFolderPopup(self, event):
		# note if selected is empty then just create a new folder
		model = self.model()  # proxy model not needed

		popup = MessageBoxwLabel()
		if popup.returned == QDialog.Accepted:
			print("algorithim for creating folders")

			#warning: check if the folder exist

			index_list = self.selectedIndexes()

			if self.modifier_pressed != Qt.ShiftModifier:
				new_folder = model.rootPath() + QDir.separator() + popup.folder_name  # note not root path()
				
				if not os.path.exists(new_folder):
					# os.mkdir(new_folder)
					override = False
					pass
				else:
					# -> Prompt if override or just use that folder
					msgBox = MessagePopUp("The folder with the same name already exists, \n Do you want to Override the old folder?", "If you want to just use the old folder just select No")
					if msgBox.clickedbutton == QMessageBox.Yes:
						inmsgBox = MessagePopUp("Override the folder?", "You can still recover it from the recycle bin")
						# -> Override
						if inmsgBox.clickedbutton == QMessageBox.Yes:
							# -> deleting folder
							# shutil.rmtree(new_folder) #moved
							# -> creating folder
							# os.mkdir(new_folder) #moved
							override = True

						elif inmsgBox.clickedbutton == QMessageBox.No:
							return

					elif msgBox.clickedbutton == QMessageBox.No:
						# -> Don't Override
						counter = 1
						# while os.path.exists(new_folder):
						# 	base_folder = new_folder
							
						# 	new_folder = base_folder + f" (copy {counter})"

						# 	counter += 1

						newfolder = multiCopyHandler(new_folder)

						# os.rename(fileIn.absoluteFilePath(), new_file)
						# os.mkdir(new_folder) #moved

					elif msgBox.clickedbutton == QMessageBox.Cancel:
						# -> Cancel
						pass
					
				unCreateFolder = unCreateFolderPopup(new_folder, override)
				self.undostack.push(unCreateFolder)

					# note convert this to a redo method and just get tje new folder value and delete it
					# note incase cancel was clicked, don't remove its folder and just move the files

			elif self.modifier_pressed == Qt.ShiftModifier:
				print("[createFolderPopup] - Shift Mode")
				for index in index_list:
					if index.column() == 0:
						fileIn = model.fileInfo(index)
						if fileIn.isDir():
							new_folder = fileIn.absoluteFilePath() + QDir.separator() + popup.folder_name

							if not os.path.exists(new_folder):
								# os.mkdir(new_folder)
								pass
							else:
								# -> Prompt if override or just use that folder
								msgBox = MessagePopUp("The folder with the same name already exists, \n Do you want to Override the old folder?", "If you want to just use the old folder just select No", buttons=QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
								if msgBox.clickedbutton == QMessageBox.Yes:
									inmsgBox = MessagePopUp("Override the folder?", "You can still recover it from the recycle bin")
									# -> Override
									if inmsgBox.clickedbutton == QMessageBox.Yes:
										#-> deleting folder
										# shutil.rmtree(new_folder) #moved
										# #-> creating folder
										# os.mkdir(new_folder) #moved
										override = True

									elif inmsgBox.clickedbutton == QMessageBox.No:
										return

								elif msgBox.clickedbutton == QMessageBox.No:
									# -> Don't Override
									counter = 1
									# while os.path.exists(new_folder):
									# 	base_folder = new_folder
										
									# 	new_folder = base_folder + f" (copy {counter})"

									# 	counter += 1

									newfolder = multiCopyHandler(new_folder)

									# os.rename(fileIn.absoluteFilePath(), new_file)
									# os.mkdir(new_folder)  #moved

								elif msgBox.clickedbutton == QMessageBox.Cancel:
									# -> Cancel
									pass
							
							if 'override' in globals():
								unCreateFolder = unCreateFolderPopup(new_folder, override=override)
							else:
								unCreateFolder = unCreateFolderPopup(new_folder)

							self.undostack.push(unCreateFolder)

	def renameFileFolder(self, event):
		# note if selected is empty then do nothing
		model = self.model()

		popup = MessageBoxwLabel()
		if popup.returned == QDialog.Accepted:
			print("algorithim for creating folders")

			#warning: check if the folder exist

			index_list = self.selectedIndexes()

			print(f"Folder Name -> '{popup.folder_name}'")
			for index in index_list:
				if index.column() == 0:
					fileIn = model.fileInfo(index)
					# new_file = os.path.join(model.rootPath(), popup.folder_name)  # note not root path()
					new_file = model.rootPath() + QDir.separator() + popup.folder_name  # note not root path()
					
					if not os.path.exists(new_file):
						# -> just move the folder/files
						os.rename(fileIn.absoluteFilePath(), new_file)
						pass
					else:
						# -> Prompt if override or just use that folder
						msgBox = MessagePopUp("The file/folder with the same name already exists, \n Do you want to Override the old file/folder?", "If you want to just use the old folder just select No", buttons=QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
						if msgBox.clickedbutton == QMessageBox.Yes:
							inmsgBox = MessagePopUp("Override the folder?", "You can still recover it from the recycle bin")
							# -> Override
							if inmsgBox.clickedbutton == QMessageBox.Yes:
								#-> deleting file/folder
								shutil.rmtree(new_file)
								#-> creating file/folder
								os.mkdir(new_file)

								if os.path.isdir(new_file):
									print(f"isDir -> {new_file}")
									shutil.rmtree(new_file)
									
								elif os.path.isfile(new_file):  
									os.remove(new_file)
									print(f"isFile -> {new_file}")
								
								# Move the content
								# source to destination
								os.rename(fileIn.absoluteFilePath(), new_file)

							elif inmsgBox.clickedbutton == QMessageBox.No:
								return

						elif msgBox.clickedbutton == QMessageBox.No:
							# -> Don't Override
							counter = 1
							while os.path.exists(new_file):
								base_file = new_file
								
								new_file = base_file + f" (copy {counter})"

								counter += 1

							os.rename(fileIn.absoluteFilePath(), new_file)

						elif msgBox.clickedbutton == QMessageBox.Cancel:
							# -> Cancel
							pass

	def MovetoNewFolderPopup(self, event):
		# note if selected is empty then do nothing
		model = self.model()
		# model = proxyModel.sourceModel()

		popup = MessageBoxwLabel()
		if popup.returned == QDialog.Accepted:
			print("algorithim for creating folders")

			#warning: check if the folder exist

			index_list = self.selectedIndexes()

			print(f"Folder Name -> '{popup.folder_name}'")
			if index_list:
				if self.modifier_pressed != Qt.ShiftModifier:
					new_folder = model.rootPath() + QDir.separator() + popup.folder_name  # note not root path()
					
					if not os.path.exists(new_folder):
						os.mkdir(new_folder)
					else:
						# -> Prompt if override or just use that folder
						msgBox = MessagePopUp("The folder with the same name already exists, \n Do you want to Override the old folder?", "If you want to just use the old folder just select No")
						if msgBox.clickedbutton == QMessageBox.Yes:
							inmsgBox = MessagePopUp("Override the folder?", "You can still recover it from the recycle bin")
							# -> Override
							if inmsgBox.clickedbutton == QMessageBox.Yes:
								#-> deleting folder
								shutil.rmtree(new_folder)
								#-> creating folder
								os.mkdir(new_folder)

							elif inmsgBox.clickedbutton == QMessageBox.No:
								return
							
						elif msgBox.clickedbutton == QMessageBox.No:
							# -> Don't Override
							counter = 1
							while os.path.exists(new_folder):
								base_folder = new_folder
								
								new_folder = base_folder + f" (copy {counter})"

								counter += 1

							# os.rename(fileIn.absoluteFilePath(), new_file)
							os.mkdir(new_folder)

						elif msgBox.clickedbutton == QMessageBox.Cancel:
							# -> Cancel
							pass

					# note convert this to a redo method and just get tje new folder value and delete it
					# note incase cancel was clicked, don't remove its folder and just move the files
					for index in index_list:
						if index.column() == 0:
							fileIn = model.fileInfo(index)
							# fileIn = model.fileInfo(proxyModel.mapToSource(index))

							#warning: make sure that the folder will actually make the folder inside
				
							# if not fileIn.isDir():
							True_or_False = f"{fileIn.canonicalPath()} == {model.rootPath()} : {fileIn.canonicalPath() == model.rootPath()}"
							True_or_False = f"{model.rootPath()} in {fileIn.canonicalPath()} : {model.rootPath() in fileIn.canonicalPath()}"
							if (fileIn.canonicalPath() == model.rootPath()) or (model.rootPath() in fileIn.canonicalPath()):  #warning: checking if the files are in the same of the rootfolder
								file_to_rename = fileIn.absoluteFilePath()
								print(file_to_rename)
								shutil.move(file_to_rename, new_folder)

				elif self.modifier_pressed == Qt.ShiftModifier:
					print("[MovetoNewFolderPopup] -> Shift Mode")
					fileIn = model.fileInfo(index_list[0])
					new_folder = fileIn.absolutePath() + QDir.separator() + popup.folder_name  # note not root path()
					
					if not os.path.exists(new_folder):
						os.mkdir(new_folder)
					else:
						#warning: Prompt if override or just use that folder
						msgBox = MessagePopUp("The folder with the same name already exists, \n Do you want to Override the old folder?", "If you want to just use the old folder just select No")
						if msgBox.clickedbutton == QMessageBox.Yes:
							inmsgBox = MessagePopUp("Override the folder?", "You can still recover it from the recycle bin")
							# -> Override
							if inmsgBox.clickedbutton == QMessageBox.Yes:
								#-> deleting folder
								shutil.rmtree(new_folder)
								#-> creating folder
								os.mkdir(new_folder)

							elif inmsgBox.clickedbutton == QMessageBox.No:
								return

						elif msgBox.clickedbutton == QMessageBox.No:
							# -> Don't Override
							pass

					for index in index_list:
						if index.column() == 0:
							fileIn = model.fileInfo(index)

							#warning: make sure that the folder will actually make the folder inside
				
							# if not fileIn.isDir():
							True_or_False = f"{fileIn.canonicalPath()} == {model.rootPath()} : {fileIn.canonicalPath() == model.rootPath()}"
							True_or_False = f"{model.rootPath()} in {fileIn.canonicalPath()} : {model.rootPath() in fileIn.canonicalPath()}"
							if (fileIn.canonicalPath() == model.rootPath()) or (model.rootPath() in fileIn.canonicalPath()):  #warning: checking if the files are in the same of the rootfolder
								file_to_rename = fileIn.absoluteFilePath()
								print(file_to_rename)
								shutil.move(file_to_rename, new_folder)

	def deleteFile(self, event):
		# print(f"deleting... {self.tree.currentIndex()}")
		# index_list = [self.tree.currentIndex()]
		
		msgBox = MessagePopUp("Do you want to continue?", "You can still recover the file/folder in the recycle bin")

		print(f"{msgBox} : {QMessageBox.Yes} : {msgBox == QMessageBox.Yes}")

		#warning: not working

		if msgBox.clickedbutton == QMessageBox.Yes:
			index_list = self.selectedIndexes()
			for index in index_list:
				if index.column() == 0:
					# model = index.model()
					model = self.model()
					print(f"model -> {model}")
					fileIn: QFileInfo = model.fileInfo(index)

					path_to_delete = fileIn.absoluteFilePath()
					print(f"deleting ... {path_to_delete}")
					# shutil.move(path_to_delete, recycle_bin)
					# path_to_delete = path_to_delete.replace("/", "\\")

					# deleteF(path_to_delete)
					QFile(path_to_delete).moveToTrash()

	def removeOuterFolderPopup(self, event):
		# note if selected is empty then do nothing
		model = self.model()


		index_list = self.selectedIndexes()


		for index in index_list:
			if index.column() == 0:
				# ->
				fileIn: QFileInfo = model.fileInfo(index)
				filepath = fileIn.absoluteFilePath()
				canon_filepath = fileIn.canonicalPath()
				# ->

				# new_file = os.path.join(model.rootPath(), popup.folder_name)  # note not root path()
				# new_folder = model.rootPath() + QDir.separator() +   # note not root path()
				
				# -> Prompt if they are sure
				inmsgBox = MessagePopUp(f"Delete the folder \n {canon_filepath}", "You can still recover it from the recycle bin")
				if inmsgBox.clickedbutton == QMessageBox.Yes:
					# #-> deleting file/folder
					# shutil.rmtree(new_folder)
					# #-> creating file/folder
					# os.mkdir(new_folder)

					# if os.path.isdir(new_folder):
					# 	print(f"isDir -> {new_folder}")
					# 	shutil.rmtree(new_folder)
						
					# elif os.path.isfile(new_folder):  
					# 	os.remove(new_folder)
					# 	print(f"isFile -> {new_folder}")
					
					# # Move the content
					# # source to destination
					# os.rename(fileIn.absoluteFilePath(), new_folder)
					# -> moving files to the canonnical file path
					p = Path(filepath).absolute()
					parent_dir = p.parents[1]
					p.rename(parent_dir / p.name)
					
					parent_dir.rmdir()
					# shutil.move()

				elif inmsgBox.clickedbutton == QMessageBox.No:
					pass

	def duplicateFolderPopup(self, event):
		# note if selected is empty then do nothing

		model = self.model()

		print("algorithim for creating folders")

		#warning: check if the folder exist

		index_list = self.selectedIndexes()

		for index in index_list:
			if index.column() == 0:
				fileIn: QFileInfo = model.fileInfo(index)

				selected_file = fileIn.absoluteFilePath()
				new_folder = multiCopyHandler(selected_file)
				
				if not os.path.exists(new_folder):  # you can diable this if statement but try to catch an error
					os.mkdir(new_folder)

			# note convert this to a redo method and just get tje new folder value and delete it
			# note incase cancel was clicked, don't remove its folder and just move the files;
				# file_to_rename = fileIn.absoluteFilePath()
				# print(file_to_rename)
				shutil.copytree(selected_file, new_folder)

	def moveToRootPopUp(self, event):
		# note if selected is empty then do nothing

		model: QFileSystemModel = self.model()

		print("algorithim for creating folders")

		#warning: check if the folder exist

		index_list = self.selectedIndexes()

		for index in index_list:
			if index.column() == 0:
				fileIn: QFileInfo = model.fileInfo(index)

				selected_file = fileIn.absoluteFilePath()
				# new_folder = multiCopyHandler(selected_file)
				
				# if not os.path.exists(new_folder):  # you can diable this if statement but try to catch an error
				# 	os.mkdir(new_folder)

			# note convert this to a redo method and just get tje new folder value and delete it
			# note incase cancel was clicked, don't remove its folder and just move the files;
				# file_to_rename = fileIn.absoluteFilePath()
				# print(file_to_rename)
				shutil.move(selected_file, model.rootPath())

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

		self.UI_Init()
	
	def handle_buttons(self, toggle_on, toggle_off):
		button = self.sender()
		# if button is not None:
		text = button.text().strip()
		print(f"'{text}'")
		button.setText(toggle_on if text == toggle_off else toggle_off)

	def showList(self):
		self.main_file_preview.setHidden(not self.main_file_preview.isHidden())
		self.connected_file_preview.setHidden(not self.connected_file_preview.isHidden())
		self.handle_buttons("Hide Preview", "Show Preview")

	def enableHide(self):
		delegate = DisDelegate() if self.model.hideMode else QStyledItemDelegate()
		self.model.hideMode = not self.model.hideMode
		# self.model.invalidateFilter()
		self.tree.setItemDelegate(delegate)

		# need to redo to add QFilterProxyModel, to actually add the functionality to hide
		self.handle_buttons("Disable Hide", "Enable Hide")

	def fileConverter(self, dir):

		iterator_ = QDirIterator(dir)

		while iterator_.hasNext():
			fileIn = QFileInfo(iterator_.next())

			baseName = fileIn.completeBaseName()
			fileName = fileIn.fileName()
			complete_path = fileIn.absoluteFilePath()
			path = fileIn.absolutePath()

			project_filenames = [".ai",".psd"]

			for item in project_filenames:
				if fileName.endswith(item):
					print(f"""\"C:/Program Files/ImageMagick-7.1.0-Q8/convert.exe" -density 20x20 "{complete_path}[0]" "{dir_path}/thumbnail/{baseName}.jpg\"""")
					subprocess.run(f"""\"C:/Program Files/ImageMagick-7.1.0-Q8/convert.exe" -density 20x20 "{complete_path}[0]" "{dir_path}/thumbnail/{baseName}.jpg\"""")
					print(f"[{complete_path}[0]] --> File Converted --> [{dir_path}/thumbnail/{baseName}.jpg]")

	def onClicked(self, index, label):
		# note mabe add a scanner when a directory is clicked then display in the bottom bar
		# produced_path = self.fileConverter(index)

		fileIn = self.sender().model().fileInfo(index)
		if not fileIn.isDir():
			complete_path = fileIn.absoluteFilePath()
			self.sender().fileName = fileIn.fileName()
			baseName = fileIn.completeBaseName()
		
			for type in preview_types:
				if self.sender().fileName.endswith(type):
					if type in project_filenames:
						preview_picture_pixmap = QPixmap(f"{dir_path}/thumbnail/{baseName}.jpg")
					else:
						preview_picture_pixmap = QPixmap(complete_path)

					# preview_picture_pixmap = preview_picture_pixmap.scaledToWidth(self.main_file_preview.width(), Qt.SmoothTransformation)

					width = label.contentsRect().width()
					height = label.contentsRect().height()

					preview_picture_pixmap = preview_picture_pixmap.scaled(width, height, Qt.KeepAspectRatio)
					label.setPixmap(preview_picture_pixmap)
		else:
			return
		
		# print(index.parent())
		# if index.parent() is self.tree
		if self.sender().isLeft: # Note these sender() is for setting the attributes of the Tree
			suffix = fileIn.completeSuffix()
			if fileIn.completeSuffix() in project_filenames:
				self.sender().project_dir = workstation_files + QDir.separator() + self.sender().fileName + " Raw Files"
				print("isleft")
				if not os.path.exists(self.sender().project_dir):
					os.mkdir(self.sender().project_dir)

				self.model2.setRootPath(self.sender().project_dir)
				self.tree2.setRootIndex(self.model2.index(self.sender().project_dir))
				
				# -> expand all
				self.model2.directoryLoaded.connect(lambda : self.tree2.expandAll())

	def UI_Init(self):
		# appWidth = 1000
		# appHeight = 600
		self.setWindowTitle('File System Viewer')
		# self.setGeometry(200, 100, appWidth, appHeight)

		# self.setMinimumWidth(1000)
		
		# dir_path = QFileDialog.getExistingDirectory(self, "Select file folder directory")
		#* Add Combo box for each person
		
		# dir_path = r'D:/Student - Files/Eliazar'

		# -- recycle bin -- #
		# if not os.path.exists(recycle_bin):
		# 	os.mkdir(recycle_bin)

		# -- thumbnail -- #    #warning:Please disable this when debugging
		if not os.path.exists(thumbnail):   #warning: delete the thumbnail folder when the program is finished
			os.mkdir(thumbnail)
			FILE_ATTRIBUTE_HIDDEN = 0x02
			ctypes.windll.kernel32.SetFileAttributesW(thumbnail, FILE_ATTRIBUTE_HIDDEN)

		# -- preview (left) -- #
		effect = QGraphicsDropShadowEffect(offset=QPoint(-3, 3), blurRadius=25, color=QColor("#111"))
		self.main_file_preview = ModifiedQLabel(effect=effect)
		self.main_file_preview.setHidden(True)

		# -- preview (right) -- #
		effect = QGraphicsDropShadowEffect(offset=QPoint(3, 3), blurRadius=25, color=QColor("#111"))
		self.connected_file_preview = ModifiedQLabel(effect=effect)
		self.connected_file_preview.setHidden(True)

		# -- left side pane -- #
		if not os.path.exists(workstation_files):
			os.mkdir(workstation_files)
			# note intro here because new

		# self.model = FileSystemModel()
		self.model = FileSystemModel()
		self.model.setRootPath(workstation_files)
		# self.model.setNameFilters(project_filenames_as_filter) # causes problems in the model file selection
		self.model.conNameFilters = project_filenames_as_filter        # self.dirProxy.dirModel.setNameFilterDisables(False)

		# self.dirProxy.dirModel.setFilter(QDir.Files | QDir.NoDotAndDotDot)

		# self.model2.setReadOnly(False)

		self.tree = Tree(self.model)

		self.tree.isLeft = True
		root_index = self.model.index(workstation_files)
		self.tree.setRootIndex(root_index)

		self.tree.clicked.connect(lambda event: self.onClicked(event, self.main_file_preview))
		# self.tree.setColumnWidth(0, 200)

		# self.dirProxy = DirProxy()
		# self.tree.setModel(self.dirProxy)
		# self.dirProxy.setNameFilters(['*.py'])


		# -- right side pane-- #
		# if not os.path.exists(right_main_dirpath):
		# 	os.mkdir(right_main_dirpath)

		self.model2 = FileSystemModel()
		# self.model2.setRootPath(right_main_dirpath) # note - not set when started only when a project file is clicked
		# self.model2.setReadOnly(False)

		self.tree2 = Tree(self.model2)
		self.tree2.isRight = True
		# self.tree2.setRootIndex(self.model2.index(right_main_dirpath))
		self.tree2.clicked.connect(lambda event: self.onClicked(event, self.connected_file_preview))

		# self.fileConverter(rf"{self.dir_path}/Project Files") #warning: enable this
		
		# -- layout -- #
		self.main_layout = QVBoxLayout()

		self.tree_layout = QHBoxLayout()
		self.tree_layout.addWidget(self.main_file_preview)
		self.tree_layout.addWidget(self.tree)
		self.tree_layout.addWidget(self.tree2)
		self.tree_layout.addWidget(self.connected_file_preview)

		button_layout = QVBoxLayout()
		
		btn_show = QPushButton("Hide Preview")
		btn_show.clicked.connect(self.showList)
		button_layout.addWidget(btn_show)

		btn_hide = QPushButton("Enable Hide")
		btn_hide.clicked.connect(self.enableHide)
		button_layout.addWidget(btn_hide)

		self.main_layout.addLayout(button_layout)
		self.main_layout.addLayout(self.tree_layout)

		self.setLayout(self.main_layout)
		
if __name__ == '__main__':

	app = QApplication.instance()
	if app is None:
		app = QApplication(sys.argv)
	demo = FileSystemView()
	# with open("sty.qss","r") as fh:
	# 	app.setStyleSheet(fh.read())
	# demo.showMaximized()
	demo.show()
	sys.exit(app.exec_())