import sys
import os
import shutil
import subprocess
import ctypes

from PyQt5.QtWidgets import QApplication, QWidget, QTreeView, QFileSystemModel, QHBoxLayout, \
	QVBoxLayout, QPushButton, QListWidget, QListWidgetItem, QMenu, QAction, QAbstractItemView, \
		QFileDialog, QMessageBox, QLabel, QSizePolicy, QGraphicsDropShadowEffect, QLineEdit, \
			QDialog, qApp
from PyQt5.QtGui import QCursor, QPixmap, QColor, QDesktopServices
from PyQt5.QtCore import QSortFilterProxyModel, Qt, QDir, QFileInfo, QFile, QDirIterator, \
	QPoint, QUrl

# -- Types -- #
project_filenames = [".ai",".psd"]
preview_types = [".ai", ".psd", ".jpg", ".png"]

# -- Paths -- #
dir_path           = r'D:/Student - Files/Eliazar'
recycle_bin        = r"D:/Student - Files/Eliazar/recycle bin"
thumbnail          = r"D:/Student - Files/Eliazar/thumbnail"
left_main_dirpath  = r"D:/Student - Files/Eliazar/Project Files"
right_main_dirpath = r"D:/Student - Files/Eliazar/Random Raw Files"


class MessagePopUp(QMessageBox):
	def __init__(self, text, note):
		super().__init__()
		self.setIcon(QMessageBox.Warning)
		self.setWindowTitle("Confirmation")
		self.setText(f"{text}")
		self.setInformativeText(f"Note: {note}")
		self.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
		self.setDefaultButton(QMessageBox.Cancel)
		# self.buttonClicked.connect(self.ret)
		self.clickedbutton = self.exec()
	
	# def ret(self, button):
	# 	button = self.standardButton(button)		
	# 	return button

class MessageBoxwLabel(QDialog):
	folder_name = None

	def __init__(self):
		super().__init__()

		self.mainlayout = QVBoxLayout()
		# self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)

		self.lineedit = QLineEdit()
		self.mainlayout.addWidget(self.lineedit)

		self.button = QPushButton("Create Folder")
		self.mainlayout.addWidget(self.button)
		self.button.clicked.connect(self.click)

		# self.mainlayout.setSpacing(0)
		self.setMaximumSize(self.minimumSizeHint())

		self.setLayout(self.mainlayout)
		
		self.exec_()
	
	def click(self):
		print("here")

		self.folder_name = self.lineedit.text().strip()
		self.accept()
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
	global recycle_bin
	global thumbnail
	global left_main_dirpath
	global right_main_dirpath

	isLeft  = False
	isRight = False
	current_key = None

	def __init__(self):
		super().__init__()
		# self.setSelectionMode(self.SingleSelection)
		# self.setDragDropMode(QAbstractItemView.InternalMove)
		self.setDragDropMode(QAbstractItemView.DragDrop)
		# self.setDragEnabled(True)
		self.setDropIndicatorShown(True)
		self.setDefaultDropAction(Qt.CopyAction)
		self.viewport().setAcceptDrops(True)

		self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)

		self.doubleClicked.connect(self.openFile)

	def openFile(self, index):
		
		selected_index = self.selectedIndexes()

		for indep in selected_index:
			if indep.column() == 0:
				model = index.model()
				fileinfo = model.fileInfo(indep)
			# QDesktopServices(fileinfo.absoluteFilePath())
				QDesktopServices.openUrl(QUrl.fromLocalFile(fileinfo.absoluteFilePath()))

	def startDrag(self, actions):
		if qApp.keyboardModifiers() & Qt.ControlModifier:
			super().startDrag(Qt.CopyAction)
		elif qApp.keyboardModifiers() & Qt.ShiftModifier:
			super().startDrag(Qt.MoveAction)

	# def keyPressEvent(self, event):

	# 	current_key = event.key()
	# 	print(current_key)

	# 	if current_key == Qt.Key_C: # and event.modifiers() & Qt.ControlModifier:
	# 		print("Pressed -> C")

	# 	return super().keyPressEvent(event)

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
		m = event.mimeData()
		if m.hasUrls():
			event.accept()
			# print("[dropEnterEvent] - event accepted")
			return
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
				destination = QDir(pathDir).filePath(info.fileName())
				source = info.absoluteFilePath()
				if destination == source:
					continue  # means they are in the same folder
				if info.isDir():
					if dropAction == Qt.CopyAction:
						QDir().rename(source, destination)
					elif dropAction == Qt.MoveAction:
						QFile().copy(source, destination)
				else:
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

	def keyPressEvent(self, event):
		self.current_key = event.key()

		QApplication.processEvents()
		# -- #
		current_key = event.key()
		print(current_key)

		if current_key == Qt.Key_C: # and event.modifiers() & Qt.ControlModifier:
			print("Pressed -> C")
		# -- #
		QApplication.processEvents()

		print(self.current_key)
		return super().keyPressEvent(event)

	def keyReleaseEvent(self, event):
		self.current_key = None
		print(self.current_key)
		return super().keyReleaseEvent(event)

class FileSystemView(QWidget):
	global project_filenames
	global preview_types
	global dir_path
	global recycle_bin
	global thumbnail
	global left_main_dirpath
	global right_main_dirpath

	json_dict = {}
	def __init__(self):
		super().__init__()

		# -- stylesheets -- #

		# self.setStyleSheet("ModifiedQLabel { background-color: lightgray }")

		self.UI_Init()

	def context_menu(self, event):
		print(f"sender -> {self.sender()}")
		self.tree_sender = self.sender()
		# self.model_sender = self.tree_sender.model()

		self.menu = QMenu(self)

		deleteFileAction = QAction('Delete', self)
		deleteFileAction.triggered.connect(lambda event: self.deleteFile(event))
		
		moveToNewFolderAction = QAction('Move to New Folder', self)
		moveToNewFolderAction.triggered.connect(lambda event: self.MovetoNewFolderPopup(event))

		createFolderAction = QAction('Create Folder', self)
		createFolderAction.triggered.connect(lambda event: self.createFolderPopup(event))

		self.menu.addAction(deleteFileAction)
		self.menu.addAction(moveToNewFolderAction)
		self.menu.addAction(createFolderAction)
		# add other required actions
		self.menu.popup(QCursor.pos())
	
	def createFolderPopup(self, event):
		model = self.tree_sender.model()
		print(f"model -> {model}")
		print(f"{self.tree_sender.current_key} + click")

		# quit()

		popup = MessageBoxwLabel()
		# popup.accepted.connect(self.createFolder)
		if popup.Accepted == 1:
			print("algorithim for creating folders")
			
			#* B1 check if folder exists

			#warning: check if the folder exist

			index_list = self.tree_sender.selectedIndexes()


			if self.tree_sender.current_key != Qt.Key_Shift:
				#* B1
				# print(f"Folder Name -> '{popup.folder_name}'") 
				new_folder = model.rootPath() + QDir.separator() + popup.folder_name  #warning: not root path()
				
				if not os.path.exists(new_folder):
					os.mkdir(new_folder)
				else:
					#warning: Prompt if override or just use that folder
					msgBox = MessagePopUp("The folder with the same name already exists, \n Do you want to Override the old folder?", "If you want to just use the old folder just select Cancel")
					# print(msgBox)
					# msgBox = msgBox.standardButton(msgBox)
					if msgBox.clickedbutton == QMessageBox.Ok:
						inmsgBox = MessagePopUp("Override the folder?", "You can still recover it from the recycle bin")
						# print("Override")
						if inmsgBox.clickedbutton == QMessageBox.Ok:
							#-> deleting folder
							shutil.rmtree(new_folder)
							#-> creating folder
							os.mkdir(new_folder)

						elif inmsgBox.clickedbutton == QMessageBox.Cancel:
							return

					elif msgBox.clickedbutton == QMessageBox.Cancel:
						# print("Don't Override")
						pass

			elif self.tree_sender.current_key == Qt.Key_Shift:
				print("inner")
				for index in index_list:
					if index.column() == 0:
						fileIn = model.fileInfo(index)
						if fileIn.isDir():
							new_folder = fileIn.absoluteFilePath() + QDir.separator() + popup.folder_name

							if not os.path.exists(new_folder):
								os.mkdir(new_folder)
							else:
								#warning: Prompt if override or just use that folder
								msgBox = MessagePopUp("The folder with the same name already exists, \n Do you want to Override the old folder?", "If you want to just use the old folder just select Cancel")
								# print(msgBox)
								# msgBox = msgBox.standardButton(msgBox)
								if msgBox.clickedbutton == QMessageBox.Ok:
									inmsgBox = MessagePopUp("Override the folder?", "You can still recover it from the recycle bin")
									# print("Override")
									if inmsgBox.clickedbutton == QMessageBox.Ok:
										#-> deleting folder
										shutil.rmtree(new_folder)
										#-> creating folder
										os.mkdir(new_folder)

									elif inmsgBox.clickedbutton == QMessageBox.Cancel:
										return

								elif msgBox.clickedbutton == QMessageBox.Cancel:
									# print("Don't Override")
									pass
							# file_to_rename = fileIn.absolutePath()
							# print(file_to_rename) 
							# shutil.move(file_to_rename, new_folder)


	
	# -- -- #
	def MovetoNewFolderPopup(self, event):
		model = self.tree_sender.model()
		print(f"model -> {model}")

		popup = MessageBoxwLabel()
		# popup.accepted.connect(self.createFolder)
		if popup.Accepted == 1:
			print("algorithim for creating folders")
			
			#* B1 - When there is selected move the selected into the folder
				#* add a confirmation to move the selected files
				
				#* B3 - If the selected is Dir make folder inside that dir

			#* B2 - When there is empty just create the folder

			#warning: check if the folder exist

			index_list = self.tree_sender.selectedIndexes()

			#* B1
			print(f"Folder Name -> '{popup.folder_name}'")
			if self.tree_sender.current_key != Qt.Key_Shift:
				# for item in index_list:
					# index_list = [item.fileInfo(item.index()) for item in index_list]
				new_folder = model.rootPath() + QDir.separator() + popup.folder_name  #warning: not root path()
				
				if not os.path.exists(new_folder):
					os.mkdir(new_folder)
				else:
					#warning: Prompt if override or just use that folder
					msgBox = MessagePopUp("The folder with the same name already exists, \n Do you want to Override the old folder?", "If you want to just use the old folder just select Cancel")
					if msgBox.clickedbutton == QMessageBox.Ok:
						inmsgBox = MessagePopUp("Override the folder?", "You can still recover it from the recycle bin")
						# print("Override")
						if inmsgBox.clickedbutton == QMessageBox.Ok:
							#-> deleting folder
							shutil.rmtree(new_folder)
							#-> creating folder
							os.mkdir(new_folder)

						elif inmsgBox.clickedbutton == QMessageBox.Cancel:
							return

					elif msgBox.clickedbutton == QMessageBox.Cancel:
						# print("Don't Override")
						pass

				for index in index_list:
					if index.column() == 0:
						# model = index.model()
						# model = self.tree_sender.model()
						# print(f"model -> {model}")
						fileIn = model.fileInfo(index)

						#warning: make sure that the folder will actually make the folder inside
			
						# if not fileIn.isDir():
						True_or_False = f"{fileIn.canonicalPath()} == {model.rootPath()} : {fileIn.canonicalPath() == model.rootPath()}"
						True_or_False = f"{model.rootPath()} in {fileIn.canonicalPath()} : {model.rootPath() in fileIn.canonicalPath()}"
						if (fileIn.canonicalPath() == model.rootPath()) or (model.rootPath() in fileIn.canonicalPath()):  #warning: checking if the files are in the same of the rootfolder
							# print(f"filein -> {fileIn}")
							file_to_rename = fileIn.absoluteFilePath()
							print(file_to_rename)
							shutil.move(file_to_rename, new_folder)

			elif self.tree_sender.current_key == Qt.Key_Shift:
				print("inner")
				# for index in index_list:
				# 	if index.column() == 0:
				# 		fileIn = model.fileInfo(index)
						# for item in index_list:
							# index_list = [item.fileInfo(item.index()) for item in index_list]
				fileIn = model.fileInfo(index_list[0])
				new_folder = fileIn.absolutePath() + QDir.separator() + popup.folder_name  #warning: not root path()
				
				if not os.path.exists(new_folder):
					os.mkdir(new_folder)
				else:
					#warning: Prompt if override or just use that folder
					msgBox = MessagePopUp("The folder with the same name already exists, \n Do you want to Override the old folder?", "If you want to just use the old folder just select Cancel")
					if msgBox.clickedbutton == QMessageBox.Ok:
						inmsgBox = MessagePopUp("Override the folder?", "You can still recover it from the recycle bin")
						# print("Override")
						if inmsgBox.clickedbutton == QMessageBox.Ok:
							#-> deleting folder
							shutil.rmtree(new_folder)
							#-> creating folder
							os.mkdir(new_folder)

						elif inmsgBox.clickedbutton == QMessageBox.Cancel:
							return

					elif msgBox.clickedbutton == QMessageBox.Cancel:
						# print("Don't Override")
						pass

				for index in index_list:
					if index.column() == 0:
						# model = index.model()
						# model = self.tree_sender.model()
						# print(f"model -> {model}")
						fileIn = model.fileInfo(index)

						#warning: make sure that the folder will actually make the folder inside
			
						# if not fileIn.isDir():
						True_or_False = f"{fileIn.canonicalPath()} == {model.rootPath()} : {fileIn.canonicalPath() == model.rootPath()}"
						True_or_False = f"{model.rootPath()} in {fileIn.canonicalPath()} : {model.rootPath() in fileIn.canonicalPath()}"
						if (fileIn.canonicalPath() == model.rootPath()) or (model.rootPath() in fileIn.canonicalPath()):  #warning: checking if the files are in the same of the rootfolder
							# print(f"filein -> {fileIn}")
							file_to_rename = fileIn.absoluteFilePath()
							print(file_to_rename)
							shutil.move(file_to_rename, new_folder)
	# -- -- #

	def deleteFile(self, event):
		# print(f"deleting... {self.tree.currentIndex()}")
		# index_list = [self.tree.currentIndex()]
		
		msgBox = MessagePopUp("Do you want to continue?", "You can still recover the file/folder in the recycle bin")

		print(f"{msgBox} : {QMessageBox.Ok} : {msgBox == QMessageBox.Ok}")

		#warning: not working

		if msgBox == QMessageBox.Ok:
			index_list = self.tree_sender.selectedIndexes()
			for index in index_list:
				if index.column() == 0:
					# model = index.model()
					model = self.tree_sender.model()
					print(f"model -> {model}")
					fileIn = model.fileInfo(index)
		
					# if not fileIn.isDir():
					# if fileIn.canonicalPath() == model.rootPath(): #warning: try to disable this if so it can also delete folder
					# print(f"filein -> {fileIn}")

					# if fileIn.isDir():
					path_to_delete = fileIn.absoluteFilePath()
					print(path_to_delete)
					shutil.move(path_to_delete, recycle_bin)
		
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
		# produced_path = self.fileConverter(index)

		fileIn = self.sender().model().fileInfo(index)
		if not fileIn.isDir():
			complete_path = fileIn.absoluteFilePath()
			fileName = fileIn.fileName()
			baseName = fileIn.completeBaseName()
		
			for type in preview_types:
				if fileName.endswith(type):
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
		if self.sender().isLeft:
			project_dir = right_main_dirpath + QDir.separator() + fileName + QDir.separator()
			if not os.path.exists(project_dir):
				os.mkdir(project_dir)

			self.model2.setRootPath(project_dir)
			self.tree2.setRootIndex(self.model2.index(project_dir))

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
		if not os.path.exists(recycle_bin):
			os.mkdir(recycle_bin)

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
		if not os.path.exists(left_main_dirpath):
			os.mkdir(left_main_dirpath)

		self.model = QFileSystemModel()
		self.model.setRootPath(left_main_dirpath)
		# self.model2.setReadOnly(False)

		self.tree = Tree()
		self.tree.isLeft = True
		self.tree.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.tree.setModel(self.model)
		self.tree.setRootIndex(self.model.index(left_main_dirpath))
		self.tree.setColumnWidth(0, 250)
		self.tree.setAlternatingRowColors(True)
		self.tree.setSelectionMode(QAbstractItemView.ExtendedSelection)
		self.tree.clicked.connect(lambda event: self.onClicked(event, self.main_file_preview))
		self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
		self.tree.customContextMenuRequested.connect(self.context_menu)

		# -- right side pane-- #
		if not os.path.exists(right_main_dirpath):
			os.mkdir(right_main_dirpath)

		self.model2 = QFileSystemModel()
		self.model2.setRootPath(right_main_dirpath)
		# self.model2.setReadOnly(False)

		self.tree2 = Tree()
		self.tree2.isRight = True
		self.tree2.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		self.tree2.setModel(self.model2)
		self.tree2.setRootIndex(self.model2.index(right_main_dirpath))
		self.tree2.setColumnWidth(0, 250)
		self.tree2.setAlternatingRowColors(True)
		self.tree2.setSelectionMode(QAbstractItemView.ExtendedSelection)
		self.tree2.clicked.connect(lambda event: self.onClicked(event, self.connected_file_preview))
		self.tree2.setContextMenuPolicy(Qt.CustomContextMenu)
		self.tree2.customContextMenuRequested.connect(self.context_menu)

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
