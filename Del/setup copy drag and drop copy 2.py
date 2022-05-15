import sys
import os
import shutil
import subprocess
import ctypes
from send2trash import send2trash

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

# notes: ln --recursive --mirror x:\source x:\destination
# notes if you want, you can use os.link then recursively check the tree every 5 secs

# fetch button to copy the files but better to just use the drag and drop

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


class MessagePopUp(QMessageBox):
	def __init__(self, text, note, buttons = QMessageBox.Yes | QMessageBox.No):
		super().__init__()
		self.setIcon(QMessageBox.Warning)
		self.setWindowTitle("Confirmation")
		self.setText(f"{text}")
		self.setInformativeText(f"Note: {note}")
		self.setStandardButtons(buttons)
		self.setDefaultButton(QMessageBox.No)

		# you can also use self.clickedButton() to access
		self.clickedbutton = self.exec()

class MessageBoxwLabel(QDialog):
	folder_name = None

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
		
		self.returned = self.exec_()
	
	def click(self):
		print("here")

		self.folder_name = self.lineedit.text().strip()
		# self.close()
		self.done(1)

class ModifiedQLabel(QLabel):
	def __init__(self, effect=None):
		super().__init__()
		
		self.setMinimumWidth(300)
		self.setMaximumWidth(400)

		# self.setSizePolicy(QSizePolicy.Ma, QSizePolicy.Preferred)
		self.setSizePolicy(QSizePolicy.Expanding ,QSizePolicy.Expanding)
		# self.sizeIncrement().setWidth(0)
		# self.setFixedSize(self.size())

		self.setGraphicsEffect(effect)

		self.setStyleSheet("border: 1px solid black;")

class Tree(QTreeView):
	global project_filenames
	global preview_types
	global dir_path
	global workstation_files
	global thumbnail

	isLeft  = False
	isRight = False
	current_key = None

	def __init__(self):
		super().__init__()
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
		self.setColumnWidth(0, 250)

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
		if event.button() == Qt.RightButton:
			self.dragStartPosition = event.pos()

		return super().mousePressEvent(event)

	def mouseMoveEvent(self, event):
		if event.buttons() != Qt.RightButton:
			return
		if ((event.pos() - self.dragStartPosition).manhattanLength() < QApplication.startDragDistance()):
			return

		self.modifiers = qApp.queryKeyboardModifiers()
		# a local timer, it will be deleted when the function returns
		dragTimer = QTimer(interval=100, timeout=self.checkDrag)
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
		if not event.mimeData().hasUrls():
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
				if destination == source:
					continue  # means they are in the same folder
				if info.isDir():
					if dropAction == Qt.CopyAction:
						print(f"QDir -> source: {source} {os.path.exists(source)} | destination: {os.path.exists(destination)} {destination}")
						# rep = QDir().rename(source, destination)
						# print(rep)
						shutil.move(source, destination)
						# print(rep)

					elif dropAction == Qt.MoveAction:
						shutil.copy(source, destination_cannonical)
				elif info.isFile():
					qfile = QFile(source)
					if QFile(destination).exists():
						n_info = QFileInfo(destination)
						
						destination = n_info.canonicalPath() + QDir.separator() + n_info.completeBaseName() + " (copy)"
						if n_info.completeSuffix():   # for moving files without suffix
							destination += "." + n_info.completeSuffix()

					if dropAction == Qt.CopyAction:
						qfile.copy(destination)
					elif dropAction == Qt.MoveAction:
						qfile.rename(destination)
					print(f"added -> {info.fileName()}")  # for debugging

				accepted = True
			if accepted:
				event.acceptProposedAction()

	# context menu #
	def context_menu(self, event):
		# print(f"sender -> {self.tree_sender.sender()}") 
		# self.tree_sender = self.sender()
		# self.model_sender = self.model()

		self.menu = QMenu(self)

		renameAction = QAction('Rename', self)
		renameAction.triggered.connect(lambda event: self.renameFileFolder(event))

		deleteFileAction = QAction('Delete', self)
		deleteFileAction.triggered.connect(lambda event: self.deleteFile(event))
		
		moveToNewFolderAction = QAction('Move to New Folder', self)
		moveToNewFolderAction.triggered.connect(lambda event: self.MovetoNewFolderPopup(event))

		createFolderAction = QAction('Create Folder', self)
		createFolderAction.triggered.connect(lambda event: self.createFolderPopup(event))

		self.menu.addAction(renameAction)
		self.menu.addAction(deleteFileAction)
		self.menu.addAction(moveToNewFolderAction)
		self.menu.addAction(createFolderAction)

		self.modifier_pressed = qApp.queryKeyboardModifiers()
		if self.modifier_pressed == Qt.ShiftModifier:
			print("Shift Pressed")

		# add other required actions
		self.menu.popup(QCursor.pos())
	
	def createFolderPopup(self, event):
		# note if selected is empty then just create a new folder
		model = self.model()

		popup = MessageBoxwLabel()
		if popup.returned == QDialog.Accepted:
			print("algorithim for creating folders")

			#warning: check if the folder exist

			index_list = self.selectedIndexes()

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
							# -> deleting folder
							shutil.rmtree(new_folder)
							# -> creating folder
							os.mkdir(new_folder)

						elif inmsgBox.clickedbutton == QMessageBox.No:
							return

					elif msgBox.clickedbutton == QMessageBox.No:
						# -> Don't Override
						pass

			elif self.modifier_pressed == Qt.ShiftModifier:
				print("[createFolderPopup] - Shift Mode")
				for index in index_list:
					if index.column() == 0:
						fileIn = model.fileInfo(index)
						if fileIn.isDir():
							new_folder = fileIn.absoluteFilePath() + QDir.separator() + popup.folder_name

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
									pass

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
					fileIn = model.fileInfo(index)

					path_to_delete = fileIn.absoluteFilePath()
					print(f"deleting ... {path_to_delete}")
					# shutil.move(path_to_delete, recycle_bin)
					path_to_delete = path_to_delete.replace("/", "\\")

					send2trash(path_to_delete)

class FileSystemView(QWidget):
	global project_filenames
	global project_filenames_as_filter
	global preview_types
	global dir_path
	global workstation_files
	global thumbnail

	json_dict = {}
	def __init__(self):
		super().__init__()

		# -- stylesheets -- #

		# self.setStyleSheet("ModifiedQLabel { background-color: lightgray }")

		self.UI_Init()
		
	def showList(self):
		self.main_file_preview.setHidden(not self.main_file_preview.isHidden())
		self.connected_file_preview.setHidden(not self.connected_file_preview.isHidden())

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
		
		# -- preview (right) -- #
		effect = QGraphicsDropShadowEffect(offset=QPoint(3, 3), blurRadius=25, color=QColor("#111"))
		self.connected_file_preview = ModifiedQLabel(effect=effect)

		# -- left side pane -- #
		if not os.path.exists(workstation_files):
			os.mkdir(workstation_files)
			# note intro here because new

		self.model = QFileSystemModel()
		self.model.setRootPath(workstation_files)

		self.model.setNameFilterDisables(False)
		self.model.setNameFilters(project_filenames_as_filter)
		# self.model2.setReadOnly(False)

		self.tree = Tree()
		self.tree.isLeft = True
		self.tree.setModel(self.model)
		self.tree.setRootIndex(self.model.index(workstation_files))
		self.tree.clicked.connect(lambda event: self.onClicked(event, self.main_file_preview))

		# -- right side pane-- #
		# if not os.path.exists(right_main_dirpath):
		# 	os.mkdir(right_main_dirpath)

		self.model2 = QFileSystemModel()
		# self.model2.setRootPath(right_main_dirpath) # note - not set when started only when a project file is clicked
		# self.model2.setReadOnly(False)

		self.tree2 = Tree()
		self.tree2.isRight = True
		self.tree2.setModel(self.model2)
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
		btn_show = QPushButton("Show")
		btn_show.clicked.connect(self.showList)
		button_layout.addWidget(btn_show)

		self.main_layout.addLayout(button_layout)
		self.main_layout.addLayout(self.tree_layout)

		self.setLayout(self.main_layout)
		
		# self.showFullScreen()

if __name__ == '__main__':
	app = QApplication(sys.argv)
	demo = FileSystemView()
	# with open("sty.qss","r") as fh:
	# 	app.setStyleSheet(fh.read())
	# demo.showMaximized()
	demo.show()
	sys.exit(app.exec_())
