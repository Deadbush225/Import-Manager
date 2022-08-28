# -> todo
# / make default at the first index
# / mark button of the default
# / reload to the default workstation
# new button to popup a new Import Manager

import sys
import os
import copy
import ctypes
# import shutil
import subprocess
from pathlib import *
import hashlib
# from preview_generator.manager import PreviewManager
# from send2trash import send2trash

# def deleteF(path: str):   # use moveToTrash
# 	return path.replace("/", "\\")

# from PyQt5.QtWebEngineWidgets import QWebEnginePage, QWebEngineView
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtCore import *
import qdarkstyle

from _subclassed import ModDict, ModPushButton, QHSeparationLine, ReadOnlyDelegate, ModTableWidget, \
	MessageBoxwLabel, MessagePopUp, ModSettings, DisDelegate, ModWebEngineView, ModLabel, FileSystemModel, \
		ModScrollArea

from _mainImplementation import Tree

# notes: ln --recursive --mirror x:\source x:\destination
# notes if you want, you can use os.link then recursively check the tree every 5 secs

# hey if there's a problem, just check if the index is right `mapToSource` and `mapFromSource`
# if a widget just close, maybe it is not connected to the main window

# notes `recursiveFilteringEnabled` 

# add dir btn 
# imperative to enter a alias (try to add name as recommendation) else cancel

PDF_JS = str(Path("./pdfjs-2.15.349-legacy-dist/web/viewer.html").absolute()).replace("\\", "/")



class AdditionalSettings(QDialog):

	saving = pyqtSignal(ModDict)

	def __init__(self, parent, parent_settings: ModDict):
		super().__init__()
		self.setFixedSize(650, 410)

		# Use parent_settings on reflected settings
		self.parent_settings = parent_settings
		self.temp_settings = copy.deepcopy(self.parent_settings)
		print(self.temp_settings)

		main_layout = QVBoxLayout()

		# self.temp_settings.beginGroup("General Settings")
		self.temp_settings.beginGroup("General Settings")
		self.enable_hide_Chkbx = QCheckBox("Enable Hide")
		self.enable_hide_Chkbx.setChecked(self.temp_settings["Enable Hide"])
		self.enable_hide_Chkbx.clicked.connect(parent.showList)

		self.hide_preview_Chkbx = QCheckBox("Hide Preview")
		self.hide_preview_Chkbx.setChecked(self.temp_settings["Hide Preview"])
		self.hide_preview_Chkbx.clicked.connect(parent.enableHide)
		self.temp_settings.endGroup()
		# self.temp_settings.endGroup()

		horizontal_line = QHSeparationLine()

		# self.pathlist = ModTableWidget()
		# button_delegates = ModPushButton_Delegate()

		delegate = ReadOnlyDelegate()

		self.pathtable = ModTableWidget(0, 3, parent=self)
		self.pathtable.setItemDelegate(delegate)

		# self.pathtable.itemDoubleClicked.connect(self._doubleClick)
		# self.pathtable.itemChanged.connect(self._itemChanged)

		# self.pathtable.setItemDelegateForColumn(2, button_delegates)
		self.populate_table(self.temp_settings.get_workstations())

		edit_layout = QHBoxLayout()

		browse_icon = QIcon(r"Icons\open folder.png")
		add_folder_btn = QPushButton(browse_icon, " Add Folder")
		add_folder_btn.clicked.connect(self.addPathItem_browse)
		edit_layout.addWidget(add_folder_btn)

		delete_icon = QIcon(r"Icons\trash.png")
		delete_button = ModPushButton(delete_icon, "")
		delete_button.clicked.connect(self.remove_row)
		edit_layout.addWidget(delete_button)

		# home_icon = QIcon(r"Icons\home.png")
		# home_button = ModPushButton(home_icon, "")
		# home_button.clicked.connect(self.set_as_default)
		# edit_layout.addWidget(home_button)

		edit_icon = QIcon(r"Icons\locked.png")
		edit_button = ModPushButton(edit_icon, "")
		edit_button.clicked.connect(self.lock_row)
		edit_layout.addWidget(edit_button)

		lock_icon = QIcon(r"Icons\unlock.png")
		lock_button = ModPushButton(lock_icon, "")
		lock_button.clicked.connect(self.unlock_row)
		edit_layout.addWidget(lock_button)

		horizontal_line2 = QHSeparationLine()

		save_icon = QIcon(r"Icons\save.png")
		save_settings = QPushButton(save_icon, " Save Settings")
		save_settings.setIconSize(QSize(15, 15))
		save_settings.clicked.connect(self.save_settings)

		self.statusbar = QStatusBar()
		self.statusbar.setSizeGripEnabled(False)

		main_layout.addWidget(self.enable_hide_Chkbx)
		main_layout.addWidget(self.hide_preview_Chkbx)
		main_layout.addWidget(horizontal_line)
		main_layout.addWidget(self.pathtable)
		main_layout.addLayout(edit_layout)
		# main_layout.addWidget(add_folder_btn)
		main_layout.addWidget(horizontal_line2)
		main_layout.addWidget(save_settings)
		main_layout.addWidget(self.statusbar)

		self.setLayout(main_layout)

		# self.show()

	def populate_table(self, alias_path_list: list):
		for alias_path in alias_path_list:
			alias = alias_path[0]
			path = alias_path[1]

			if alias == self.temp_settings["Workstation Paths"]["Workstations"][0][0]:
				self.addPathItem_custom(alias, path, checked = True)
			else:
				self.addPathItem_custom(alias, path)

	def get_selected_rows(self) -> list:
		selected_rows = self.pathtable.selectionModel().selectedRows(0)
		selected_rows = [row.row() for row in selected_rows]
		selected_rows.sort(reverse=True)

		return selected_rows

	def set_as_default(self):
		selected_rows = self.get_selected_rows()

		# if len(selected_rows) > 1:
		# 	message = QMessageBox(self)
		# 	message.setText("You've selected more than one row.")
		# 	message.setInformativeText("Only the first selected row will be set as default. \n Do You want to continue?")
		# 	message.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)

		# 	ret = message.exec()
			
		# 	match ret:
		# 		case QMessageBox.Yes:
		# 			pass
		# 		case QMessageBox.Cancel:
		# 			return

		selected_rows_first_item = selected_rows[-1]

		path_item = self.pathtable.item(selected_rows_first_item, 1)
		alias_item = self.pathtable.item(selected_rows_first_item, 0)

		selected_path = path_item.text()
		selected_alias = alias_item.text()
		
		# -> no need to move the item inside the list of workstations
		# workstation_list: list = self.temp_settings["Workstation Paths"]["Workstations"]
		# workstation_list.insert(0, workstation_list.pop(selected_rows_first_item))

		self.pathtable.addItem(selected_alias, selected_path, checked = True, row = 0)
		self.pathtable.removeRow(selected_rows_first_item + 1)


		# -> move default row top #problem table only allows 1 instance of child cellWidget
		# if selected_rows_first_item > 0:
		# 	self.pathtable.insertRow(0)
		# 	for col in range(self.pathtable.columnCount()-1):
		# 		self.pathtable.setItem(0, col, self.pathtable.takeItem(selected_rows_first_item + 1, col))
			
		# 	self.pathtable.setCellWidget(0, 2, self.pathtable.cellWidget(selected_rows_first_item, 2))

		# 	self.pathtable.removeRow(selected_rows_first_item + 1)

		# self.temp_settings["Workstation Paths"]["Workstations"] = workstation_list

		# self.temp_settings["Workstation Paths"]["Default Workstation"] = [selected_path, selected_alias]
		# if selected_path != self.temp_settings.value('Workstation Paths/Default Workstation'):
		# print(f"text: {selected_path}, settings: {self.temp_settings['Workstation Paths']['Default Workstation']}")

		self.showMessage(f"Configured \"{selected_alias}\" as default", "COM")
		# alias_item.setText(f"(Default) {selected_alias}")

	def remove_row(self):
		selected_rows = self.get_selected_rows()

		for row in selected_rows:
			self.pathtable.removeRow(row)

		self.showMessage(f"Removed rows {selected_rows}", "COM")

	def lock_row(self):
		selected_rows = self.get_selected_rows()

		for col in range(self.pathtable.columnCount()):
			for row in selected_rows:
				item = self.pathtable.item(row, col)
				
				if item is None:
					continue
				item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
		
		self.showMessage(f"Locked rows {selected_rows}", "COM")
				
	def unlock_row(self):
		selected_rows = self.get_selected_rows()

		for col in range(self.pathtable.columnCount()):
			for row in selected_rows:
				item = self.pathtable.item(row, col)

				if item is None:
					continue
				item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsEditable | Qt.ItemFlag.ItemIsSelectable)
		
		self.showMessage(f"Unlocked rows {selected_rows}", "COM")

	def addPathItem_custom(self, alias, path, checked=False):
		self.pathtable.addItem(alias, path, checked)

	def addPathItem_browse(self):
		self.selected_dir = self.browse_folder()

		if self.selected_dir:
			message_boxw_label = MessageBoxwLabel()
			if message_boxw_label.returned: # returns 0 if exitted, 1 otherwise
				# note: check if the alias is existing
				
				print(f"Text: '{message_boxw_label.text}'")
				
				if message_boxw_label.text:
					self.pathtable.addItem(message_boxw_label.text, self.selected_dir)
					self.showMessage("New workstation added!")

	def showMessage(self, str_, prefix = "", timeout=3000):
		self.statusbar.showMessage(prefix + " : " + str_, timeout)

	def browse_folder(self):
		return QFileDialog.getExistingDirectory(self, "Browse to your Obsidian Vault", "<Dir>")
		# print(self.selected_dir)
	
	def gather_state(self):
		# self.gathered_setting = QSettings('Import Manager', 'Temp')
		self.temp_settings.beginGroup("General Settings")
		self.temp_settings["Enable Hide"] = self.enable_hide_Chkbx.isChecked()
		self.temp_settings["Hide Preview"] = self.hide_preview_Chkbx.isChecked()
		self.temp_settings.endGroup()

		self.temp_settings.beginGroup("Workstation Paths")
		self.temp_settings["Workstations"] = self.pathtable.get_updated_workstations_list()
		self.temp_settings.endGroup()
		# self.app_settings.beginGroup("Workstation Paths")
		# self.app_settings.setValue('Default Workstation', desktop)
		# self.app_settings.endGroup()

		# self.app_settings.beginGroup("General Settings")
		# self.app_settings.setValue('Enable Hide', 1)
		# self.app_settings.setValue('Hide Preview', 0)
		# self.app_settings.endGroup()

	def check_changes(self) -> bool:
		"""_summary_

		Returns:
			bool: returns True if the workstation is the self.temp_settings
			and self.parent_settings are equal, otherwise False
		"""
		self.gather_state()
		return self.temp_settings == self.parent_settings

	def save_settings(self):
		self.gather_state()

		# if self.check_changes():
		self.parent_settings = self.temp_settings # for check check_changes
		self.saving.emit(self.temp_settings)
		# self.parent_settings.sync()
		sync = self.temp_settings.convert_to_settings()
		print(sync.convert_to_dict())
		sync.sync()

		self.showMessage("Settings saved successfully", "COM")

	def closeEvent(self, event) -> None:
		if self.check_changes():
			event.accept()
		else:
			confirmation = MessagePopUp("You have unsaved changes", "Do you want to discard all of it?", buttons=QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Save)
			# ret = confirmation.exec()
			# print(confirmation.clickedbutton)
			clickedbutton = confirmation.clickedbutton
			if clickedbutton == QMessageBox.StandardButton.Save:
				self.save_settings()
			elif clickedbutton == QMessageBox.StandardButton.Discard:
				event.accept()

		# return super().closeEvent(event)

class FileSystemView(QWidget):
	# global base_workstation_folder
	# global thumbnail

	# userlist = [""]
	
	# self.thumbnail = ""
	
	def __init__(self):
		super().__init__()

		# -- stylesheets -- #
		# self.setStyleSheet("ModifiedQLabel { background-color: lightgray }")

		# -- Types -- #
		self.project_filenames = ["ai","psd"]
		# self.project_filenames_as_filter = ["*.ai","*.psd"]
		self.project_filenames_as_filter = ["*." + filter_ for filter_ in self.project_filenames]
		self.preview_types = [["ai", "psd", "jpg", "png", "bmp", "gif", "svg"],			# images
							  ["pdf"],													# pdf
							  ["doc", "docx", "xls", "xlsx", "ppt", "pptx"],			# office files
							  ["txt", "rtf"]] 											# plain text

		# -- Paths -- #
		# dir_path           = r'D:\Local Database\Eliazar'
		# workstation_files  = r'D:\Local Database\Eliazar\Workstations'
		# thumbnail          = r"D:\Local Database\Eliazar"
		# temp               = r'D:/Student - Files/Eliazar/temp'
		# recycle_bin        = r"D:/Student - Files/Eliazar/recycle bin"
		# left_main_dirpath  = r"D:/Student - Files/Eliazar/Project Files"
		# right_main_dirpath = r"D:/Student - Files/Eliazar/Random Raw Files"

		# SETTING DEFAULTS
		# TEST 

		# self.app_settings = QSettings('Test', 'Settings')
		self.set_settings()

		# print(setting_to_Dict(self.app_settings))

		# self.app_settings.sync()
		# SETTING DEFAULTS

		# workstation_files = r""
		self.workstation_files = self.app_settings.get_default_workstation()[1]
		self.thumbnail_path = self.workstation_files + r"\thumbnail"
		# self.set_root_path(0) # for the default	

		# self.manager = PreviewManager('/cache/', create_folder= True)

		self.UI_Init()
	
	def set_settings(self):
		#setting default settings
		self.app_settings = ModSettings('Import Manager', 'Settings')

		self.app_settings.beginGroup("Workstation Paths")
		desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
		# None if self.app_settings.value('Default Workstation') else self.app_settings.setValue('Default Workstation', ["Default", desktop]) 
		# None if self.app_settings.value('Workstations') else self.app_settings.setValue('Workstations', [{"Favorites" : r"C:\Users\Eliaz\Favorites", "Pictures" : r"C:\Users\Eliaz\Pictures"}])
		# -> first item is the default
		# -> can't use dict as container
		default_workstation = [["Default_Workstation", desktop], ["Favorites", r"C:\Users\Eliaz\Favorites"], ["Pictures", r"C:\Users\Eliaz\Pictures"]]
		None if self.app_settings.value('Workstations') else self.app_settings.setValue('Workstations', default_workstation)

		# self.workstation_files = fm_default_workstation if fm_default_workstation else desktop
		
		# self.app_settings = ModSettings('Import Manager', 'Settings')
		# self.app_settings = QSettings(QSettings.IniFormat, QSettings.UserScope, 'Import Manager', 'Settings')
		
		# self.app_settings.setValue('Default Workstation', desktop)
		self.app_settings.endGroup()

		self.app_settings.beginGroup("General Settings")
		None if self.app_settings.value('Enable Hide') else self.app_settings.setValue('Enable Hide', 1)
		None if self.app_settings.value('Hide Preview') else self.app_settings.setValue('Hide Preview', 0)
		self.app_settings.endGroup()
		
		# self.app_settings.sync()
		self.app_settings = self.app_settings.convert_to_dict()
		print(self.app_settings)

#warning: dpr
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
#warning: dpr

	def toPDFConverter(self, dir_of_file) -> QUrl:
		file_name_ = self.cacheName(dir_of_file, suffix="pdf")
		print(subprocess.run(["pandoc", dir_of_file, "-o", f"{file_name_}"]))
		return file_name_

	def cacheName(self, complete_file_name, suffix=None):
		# 	project_filenames = [".ai",".psd"]
		info = QFileInfo(complete_file_name)
		# fileBaseName = info.completeBaseName()
		modifiedTime = info.lastModified().toString("dd;MM;yyyy-hh;mm;ss;z")
		extension = suffix if suffix else info.suffix()

		md5 = hashlib.md5(complete_file_name.encode('utf-8')).hexdigest()

		# cache_name = f"{md5}-[({page})]-[{density}]-[{modifiedTime}].jpg"
		cache_name = f"{md5}-[{modifiedTime}].{extension}"

		output_path = f"{self.thumbnail_path}\\{cache_name}"

		return output_path

	def thumbnailConverter(self, dir :str, density :str="50x50") -> str or list:

		# iterator_ = QDirIterator(dir)

		# while iterator_.hasNext():
		# 	fileIn = QFileInfo(iterator_.next())

		# 	baseName = fileIn.completeBaseName()
		# 	fileName = fileIn.fileName()
		# 	complete_path = fileIn.absoluteFilePath()
		# 	path = fileIn.absolutePath()

		# # 	project_filenames = [".ai",".psd"]
		# info = QFileInfo(dir)
		# # fileBaseName = info.completeBaseName()
		# modifiedTime = info.lastModified().toString("dd;MM;yyyy-hh;mm;ss;z")
		# # extension = info.suffix()

		# md5 = hashlib.md5(dir.encode('utf-8')).hexdigest()

		# # cache_name = f"{md5}-[({page})]-[{density}]-[{modifiedTime}].jpg"
		# cache_name = f"{md5}-[{modifiedTime}].jpg"

		# # output_path = f"{self.thumbnail_path}\\{cache_name}"

		output_path = self.cacheName(dir)

		# 	for item in project_filenames:
		# 		if fileName.endswith(item):
		# 			print(f"""\"C:/Program Files/ImageMagick-7.1.0-Q8/convert.exe" -density 20x20 "{self.thumbnail}[0]" "{self.thumbnail}/thumbnail/{baseName}.jpg\"""")
		if not os.path.exists(output_path):
			# subprocess.run(f"""\"C:/Program Files/ImageMagick-7.1.0-Q8/convert.exe" -density 50x50 "{dir}" {output_path}""")
	
			# print(["C:/Program Files/ImageMagick-7.1.0-Q8/convert.exe", "-density", "50x50", f"{dir}", f"{output_path}"])
			subprocess.run(["C:\\Program Files\\ImageMagick-7.1.0-Q8\\convert.exe", "-density", f"{density}", f"{dir}", f"{output_path}"])
		# 			print(f"[{complete_path}[0]] --> File Converted --> [{self.thumbnail}/thumbnail/{baseName}.jpg]")

		# thumbnail_path = self.manager.get_jpeg_preview(dir)

		# if "-" in page:
		# 	ranges = page.split("-")
		# 	return [f"{md5}-[({page})]-[{density}]-[{modifiedTime}].jpg" for page in range(int(ranges[0]), int(ranges[1]) + 1)]	
		# return output_path
		return output_path

#C:\\Users\\Eliaz\\Desktop\\thumbnails\\img20220805_12594061 (2)-006d339542fd08ea162270db925154f2.jpg

	def onClicked(self, index, previewArea :QScrollArea):
		# note mabe add a scanner when a directory is clicked then display in the bottom bar
		# produced_path = self.fileConverter(index)

		fileIn : QFileInfo = self.sender().model().fileInfo(index)
		if not fileIn.isDir():
			complete_img_path = fileIn.absoluteFilePath()
			fileName :str= fileIn.fileName()
			# baseName = fileIn.completeBaseName()
		
			# for type in self.preview_types:
			# 	if self.sender().fileName.endswith(type):
			# 		if type in self.project_filenames:
			# 			preview_picture_pixmap = QPixmap(f"{self.thumbnail}/thumbnail/{baseName}.jpg")
			# 		else: # its a picture
			# 			preview_picture_pixmap = QPixmap(complete_path)

			suffix = fileName.rsplit(".")[-1] # no *.
			
			# convention 
			# preview is a QLabel/QLayout that serves as the preview to be added in the scrollArea

			if suffix in self.preview_types[0]:
				self.preview = ModLabel()
				preview_picture_pixmap = QPixmap(self.thumbnailConverter(complete_img_path))
				#try using fast transformation
				preview_picture_pixmap = preview_picture_pixmap.scaledToWidth(self.main_file_preview.contentsRect().width(), Qt.TransformationMode.SmoothTransformation)
				self.preview.setPixmap(preview_picture_pixmap)
			elif suffix in self.preview_types[2]:
				if fileIn.size() < 8000000: # 8mb max
					pdf_path = self.toPDFConverter(complete_img_path)

					pdf_url = QUrl(fr"file:///{PDF_JS}?file=file:///{pdf_path}")

					self.preview = ModWebEngineView(previewArea)
					self.preview.load(pdf_url)
			elif suffix in self.preview_types[1]:
				if fileIn.size() < 8000000: # 8mb max
					pdf_path = QUrl(fr"file:///{PDF_JS}?file=file:///{complete_img_path}")

					# pdf_url = QUrl().fromUserInput(f"file://{PDF_JS}?file=file://{pdf_path}")
					
					self.preview = ModWebEngineView(previewArea)
					self.preview.load(pdf_path)
				# pages_paths = self.thumbnailConverter(complete_img_path, page = "0-19")
				
				# preview = QVBoxLayout()
				# for page_path in pages_paths:
				# 	lbl_page = QLabel()
				# 	page_pixmap = QPixmap(page_path)
				# 	page_pixmap = page_pixmap.scaledToWidth(self.main_file_preview.contentsRect().width(), Qt.SmoothTransformation)
				# 	lbl_page.setPixmap(page_pixmap)
				# 	preview.addWidget(lbl_page)
					pass



			# width = label.contentsRect().width()
			# height = label.contentsRect().height()

			# preview_picture_pixmap = preview_picture_pixmap.scaled(width, height, Qt.KeepAspectRatio)
			# label.setPixmap(preview_picture_pixmap)
			previewArea.setWidget(self.preview)
			# scrollArea.setAlignment(Qt.AlignVCenter)
		else:
			return
		
		# print(index.parent())
		# if index.parent() is self.tree
		if self.sender().isLeft: # Note these sender() is for setting the attributes of the Tree
			suffix = fileIn.completeSuffix()
			if suffix in self.project_filenames:
				self.sender().project_dir = self.workstation_files + QDir.separator() + fileName + " Raw Files"
				print("isleft")
				if not os.path.exists(self.sender().project_dir):
					os.mkdir(self.sender().project_dir)

				self.model2.setRootPath(self.sender().project_dir)
				self.tree2.setRootIndex(self.model2.index(self.sender().project_dir))
				
				# -> expand all
				self.model2.directoryLoaded.connect(lambda : self.tree2.expandAll())

	def save_settings(self):
		pass

	def UI_Init(self):
		# appWidth = 1000
		# appHeight = 600
		self.setWindowTitle('File System Viewer')
		# self.setGeometry(200, 100, appWidth, appHeight)

		# # -- thumbnail -- #    #warning:Please disable this when debugging
		# if not os.path.exists(self.thumbnail):   #warning: delete the thumbnail folder when the program is finished
		# 	os.mkdir(self.thumbnail)
		# 	FILE_ATTRIBUTE_HIDDEN = 0x02
		# 	ctypes.windll.kernel32.SetFileAttributesW(self.thumbnail, FILE_ATTRIBUTE_HIDDEN)

		# -- preview (left) -- #
		set_hide = self.app_settings["General Settings"]["Hide Preview"]

		# effect = QGraphicsDropShadowEffect(offset=QPoint(-3, 3), blurRadius=25, color=QColor("#111"))
		# self.main_file_preview = ModifiedQLabel(effect=effect)
		# self.main_file_preview.setHidden(set_hide)
		self.main_file_preview = ModScrollArea()
		# self.main_file_preview = QLayout()

		# -- preview (right) -- #
		self.connected_file_preview = ModScrollArea()
		# self.connected_file_preview = QLayout()
		# effect = QGraphicsDropShadowEffect(offset=QPoint(3, 3), blurRadius=25, color=QColor("#111"))
		# self.connected_file_preview = ModifiedQLabel(effect=effect)
		# self.connected_file_preview.setHidden(set_hide)

		# -- left side pane -- #
		# if not os.path.exists(self.workstation_files):
		# 	os.mkdir(self.workstation_files)
		# 	# note intro here because new

		# self.model = FileSystemModel()
		self.model = FileSystemModel()
		self.model.setRootPath(self.workstation_files)
		self.model._nameFilters = self.project_filenames_as_filter
		# self.model.setNameFilters(self.project_filenames_as_filter) 	#-> causes problems in the model file selection
		# self.model.conNameFilters = self.project_filenames_as_filter  # self.dirProxy.dirModel.setNameFilterDisables(False)

		# self.dirProxy.dirModel.setFilter(QDir.Files | QDir.NoDotAndDotDot)

		# self.model2.setReadOnly(False)

		self.tree = Tree(self.model)

		self.tree.isLeft = True
		root_index = self.model.index(self.workstation_files)
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

		button_layout = QHBoxLayout()
		
		# btn_show = QPushButton("Hide Preview")
		# btn_show.clicked.connect(self.showList)
		# button_layout.addWidget(btn_show)

		# btn_hide = QPushButton("Enable Hide")
		# btn_hide.clicked.connect(self.enableHide)
		# button_layout.addWidget(btn_hide)

		self.workstationComboBox = QComboBox(self)
		self.workstationComboBox.currentIndexChanged.connect(self.set_root_path)
		
		self.populate_combobox()
		button_layout.addWidget(self.workstationComboBox)

		settings_icon = QIcon(r"Icons\cogwheel.png")
		extended_settings_btn = QPushButton(settings_icon, "")
		extended_settings_btn.setFixedWidth(30)
		extended_settings_btn.clicked.connect(self.open_additional_settings) #show settings
		button_layout.addWidget(extended_settings_btn)

		self.main_layout.addLayout(button_layout)
		self.main_layout.addLayout(self.tree_layout)

		self.setLayout(self.main_layout)
	
	def set_root_path(self, index):

		self.currentPath = self.app_settings["Workstation Paths"]["Workstations"][index][1]

		self.model.setRootPath(self.currentPath)

		self.tree.isLeft = True
		root_index = self.model.index(self.currentPath)
		self.tree.setRootIndex(root_index)

		# -- thumbnail -- #    #warning:Please disable this when debugging
		self.thumbnail_path = os.path.join(self.currentPath, "thumbnails")
		if not os.path.exists(self.thumbnail_path):   #warning: delete the thumbnail folder when the program is finished
			os.mkdir(self.thumbnail_path)
			FILE_ATTRIBUTE_HIDDEN = 0x02
			ctypes.windll.kernel32.SetFileAttributesW(self.thumbnail_path, FILE_ATTRIBUTE_HIDDEN)

	def populate_combobox(self):
		self.workstationComboBox.clear()
		self.workstationComboBox.addItems(self.app_settings.get_workstations_aliases())

	def open_additional_settings(self):
		self.additional_settings = AdditionalSettings(self, self.app_settings)
		self.additional_settings.saving.connect(self.save_settings)
		self.additional_settings.exec_()

	def save_settings(self, dict_):
		print(f"Before saving: {self.app_settings}")
		self.app_settings = dict_
		print(f"After saving: {self.app_settings}")

		# apply settings
		self.populate_combobox()
	

if __name__ == '__main__':

	app = QApplication.instance()
	if app is None:
		app = QApplication(sys.argv)
	demo = FileSystemView()
	app.setStyleSheet(qdarkstyle.load_stylesheet())
	# with open("sty.qss","r") as fh:
	# 	app.setStyleSheet(fh.read())
	# demo.showMaximized()
	demo.show()
	sys.exit(app.exec())