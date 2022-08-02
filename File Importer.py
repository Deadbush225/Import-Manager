import sys
import os
import copy
import ctypes
# import shutil
import subprocess
from pathlib import *
# from send2trash import send2trash

# def deleteF(path: str):   # use moveToTrash
# 	return path.replace("/", "\\")

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from _subclassed import *

# notes: ln --recursive --mirror x:\source x:\destination
# notes if you want, you can use os.link then recursively check the tree every 5 secs

# hey if there's a problem, just check if the index is right `mapToSource` and `mapFromSource`
# if a widget just close, maybe it is not connected to the main window

# notes `recursiveFilteringEnabled` 

# add dir btn 
# imperative to enter a alias (try to add name as recommendation) else cancel

class ModDict():
	current_group = None
	
	def __init__(self):
		super().__init__()

		self._dict = dict()
		self.current_group_map = list()

	# @property
	# def current_group(self):
	# 	print("getting value")
	# 	return self._current_group
	# 	# print(self.current_group)

	# @current_group.setter
	# def current_group(self, value):
	# 	print("setting value")
	# 	# print(self.current_group)
	# 	self._current_group = value
	def __eq__(self, other):
		return self._dict == other._dict

	def __str__(self):
		return str(self._dict)

	def __repr__(self):
		return "< ModDict object >"

	def __getitem__(self, index: str):
		# if "/" in index:
		# 	return ModDict.get_inner_group()[index]
		x = self.existing_group_checker()[index]
		return x
		# return self.current_group[index] if self.current_group is not None else self._dict[index]

	def __setitem__(self, index, value):
		# if "/" in index:
		# 	ModDict.get_inner_group()[index] = value
		# 	return

		self.existing_group_checker()[index] = value

	def convert_to_settings(self): #-> ModSettings:
		
		# x = self._dict.keys()

		def get_groups(dict_: dict, output=None):
			if output is None:
				output = ModSettings("Import Manager", "Settings")

			keys_groups = dict_.keys()

			for key_group in keys_groups:
				if isinstance(dict_[key_group], dict):
					# self.beginGroup(key_group)
					output.beginGroup(key_group)
					get_groups(dict_[key_group], output=output)
					output.endGroup()
					# self.endGroup(key_group)
				else: # -> not inside a group
					if dict_[key_group] == True:
						output.setValue(key_group, 1)
					elif dict_[key_group] == False:
						output.setValue(key_group, 0)
					else:
						output.setValue(key_group, dict_[key_group])
			
			return output

			# get_groups(groups, output)
		

		return get_groups(self._dict)

	def existing_group_checker(self) -> dict:
		"""_summary_

		Returns:
			dict: sets the current group if existing else the self._dict
		"""
		
		x = self.current_group if self.current_group is not None else self._dict
		return x

	def beginGroup(self, keys: str):
		self.current_group_map += keys.split("/") # convert to list
		self.reevaluateCurrentGroup()
		# self.current_group = ModDict.get_inner_group(self._dict, self.current_group_map)
		# map the current group as the dict

	def endGroup(self, keynum=1):
		self.current_group_map = self.current_group_map[:0-keynum]
		self.reevaluateCurrentGroup()

	def clearGroup(self):
		self.current_group_map.clear()
		self.reevaluateCurrentGroup()
	
	def reevaluateCurrentGroup(self) -> None:
		self.current_group = ModDict.get_inner_group(self._dict, self.current_group_map)

	@staticmethod
	def get_inner_group(dict_: dict, keys :list) -> dict:
		if keys:
			first, rest = keys[0], keys[1:]
			try:
				if rest:
					return ModDict.get_inner_group(dict_[first], rest)
				else:
					return dict_[first]
			except Exception as e:
				print(e)
				return dict()
		else: # means that no keys
			return dict_

			
	# @staticmethod
	def get_list_from_settings(self, group = "") -> list:
		list_ = list()

		try:
			if group:
				keys = group.split("/")

				list_ = ModDict.get_inner_group(self._dict, keys)
			
			else:
				list_ = list(self._dict.keys())
		except Exception as e:
			print(e)
		
		return list_		

	# @staticmethod
	def get_dict_from_settings(self, group = "") -> dict:
		# aliases = FileSystemView.get_list_from_settings(settings, group)
		# alias_path = {alias, aliases[alias]}
		return self.get_inner_group(self._dict, group.split("/"))

	# -> exclusive for Import Manager
	def get_default_workstation(self) -> list:
		"""_summary_

		Returns:
			list: returns the alias and path for the default workstations
		"""

		return self._dict["Workstation Paths"]["Workstations"][0]

	def get_workstations(self) -> list:
		"""_summary_

		Returns:
			dict: returns the list all of workstations (including the default)
			first is the default workstation
		"""

		# dict_ = []

		# default_workstation = self.get_default_workstation()
		# dict_[default_workstation[0]] = default_workstation[1]

		workstations = self._dict["Workstation Paths"]["Workstations"]

		# dict_ |= workstations

		return workstations
	
	def get_workstations_aliases(self) -> list:
		workstations = [item[0] for item in self._dict["Workstation Paths"]["Workstations"]]
		return workstations

class ModSettings(QSettings):
	# def save_list_to_settings(self, list) -> None:
	# 	i = 0
	# 	for item in list:
	# 		i += 1
	# 		self.setValue(f"workstation {i}", item)
	
	def __str__(self):
		return str(self.allKeys())

	def __repr__(self):
		return "< ModDict object >"

	def get_list_from_settings(self, group = "") -> list:
		
		if group:
			self.beginGroup(group)

		keys = self.allKeys()
		
		if group:
			self.endGroup()

		print(keys)
		return keys
	
	def get_dict_from_settings(self, group = "") -> dict:
		
		if group:
			self.beginGroup(group)

		aliases = self.get_list_from_settings()
		alias_path = {alias: self.value(alias) for alias in aliases} 
		
		if group:
			self.endGroup()
		
		return alias_path
	
	def convert_to_dict(self) -> ModDict:
		groups = self.childGroups()
		keys = self.childKeys()
		
		# output = dict()
		
		def get_group(groups: list, output = None):
			if output is None:
				output = ModDict()

			for group in groups:
				self.beginGroup(group)
				
				sub_groups = self.childGroups()
				sub_keys = self.childKeys()
				
				group_dict = {}
				
				for sub_key in sub_keys:
					val = self.value(sub_key)
					if val in [1, 'true']:
						group_dict[sub_key] = True
					elif val in [0, 'false']:
						group_dict[sub_key] = False
					else:
						group_dict[sub_key] = val

					# reconvert back to 1 and 0

				#output[setting.group().rsplit("/")[-1]] = group_dict
				
				output[self.group()] = group_dict
				
				#setting.endGroup()
				
				get_group(sub_groups, group_dict)
				
				self.endGroup()
			
			return output
		
		partial = get_group(groups)
		
		for key in keys:
			partial[key] = self.value(key)
		
		return partial

# only delete is on tha cotextmenu
class ModTableWidget(QTableWidget):
	def __init__(self, row, column, parent=None):
		super().__init__(row, column, parent)
		self._parent = parent

		# self.setStyleSheet(r"""
		# QPushButton {
		# 	background-color: #eeeeee
		# }
		# """)

		self.setHorizontalHeaderLabels(["Alias", "Path", ""])
		
		# self.horizontalHeader().setDefaultSectionSize(40)

		# self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Interactive)
		self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents | QHeaderView.Interactive)
		self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
		self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
		# self.horizontalHeader().setStretchLastSection(True)
		self.horizontalHeader().setMinimumSectionSize(30)
		# self.setColumnWidth(0, 100)

		self.setSelectionBehavior(QAbstractItemView.SelectRows)

		self.is_default_group = QButtonGroup()

		self.itemDoubleClicked.connect(self._doubleClick)
		self.itemChanged.connect(self._itemChanged)
		# DEBUG
		# for item in range(10):
			# self.addItem(str(item), str(item))
		# DEBUG

		# self.customContextMenuRequested.connect(self.context_menu)
		# self.setContextMenuPolicy(Qt.CustomContextMenu)

		# self.deleteItemAction = QAction('Delete', self)
		# self.deleteItemAction.setShortcutVisibleInContextMenu(True)
		# self.deleteItemAction.setShortcut(QKeySequence(Qt.Key_Delete))
		# self.deleteItemAction.setShortcutContext(Qt.WidgetWithChildrenShortcut)
		# self.deleteItemAction.triggered.connect(lambda event: self.deleteItem(event))
	# def delete_row(self, row):

	def addItem(self, alias, path):
		last_row_index = self.rowCount()
		self.insertRow(last_row_index)

		folder_alias_item = QTableWidgetItem()
		folder_alias_item.setText(alias)
		folder_alias_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

		self.setItem(last_row_index, 0, folder_alias_item)

		folder_path_item = QTableWidgetItem()
		folder_path_item.setText(path)
		folder_path_item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

		self.setItem(last_row_index, 1, folder_path_item)

		# wrapper = QWidget()
		# layout = QHBoxLayout()
		# layout.setContentsMargins(0, 0, 0, 0)

		is_default_icon = QIcon(r"Icons\home.png")
		is_default_btn = QPushButton(is_default_icon, "")
		is_default_btn.setMaximumWidth(30)
		is_default_btn.setFlat(True)
		is_default_btn.setCheckable(True)
		is_default_btn.clicked.connect(self._parent.set_as_default)
		# layout.addWidget(is_default_btn)

		# print("Button Text: " + is_default_btn.palette().color(QPalette.Disabled, QPalette.ButtonText).name())
		# print("Button: " + is_default_btn.palette().color(QPalette.Disabled, QPalette.Button).name())
		# print("Highlight: " + is_default_btn.palette().color(QPalette.Disabled, QPalette.Highlight).name())
		# print("Highlighted Text: " + is_default_btn.palette().color(QPalette.Disabled, QPalette.HighlightedText).name())

		# is_default_btn.palette().setColor(QPalette.ButtonText, QColor("#9a9a9a"))
		# is_default_btn.palette().setColor(QPalette.Button, QColor("#eeeeee"))
		# is_default_btn.palette().setColor(QPalette.Highlight, QColor("#3778f6"))
		# is_default_btn.palette().setColor(QPalette.HighlightedText, QColor("#ffffff"))

		# wrapper.setLayout(layout)

		self.is_default_group.addButton(is_default_btn)
		self.setCellWidget(last_row_index, 2, is_default_btn)

		
		# self.model().setData(self.model().index(last_row_index, 2), Qt.AlignCenter, Qt.TextAlignmentRole)

	def get_updated_workstations_list(self) -> list:
		output = []

		row_cnt = self.rowCount()
		for row in range(row_cnt):
			per_row = []
			for column in range(self.columnCount() - 1): # exclude last column
				item_txt = self.item(row, column).text()

				per_row.append(item_txt)

			output.append(per_row)
		
		return output

	def get_updated_workstations_alias_list(self) -> list:
		output = [self.item(row, 0).text() for row in range(self.rowCount())]
		return output
		# for row in range(self.rowCount()):

	def _doubleClick(self, item):
		if item.column() == 0: # alias column
			self.txtBeforeDblClick = item.text()
	
	def _itemChanged(self, item):
		if item.column() == 0: # alias column
			text = item.text()

			alias_list = self.get_updated_workstations_alias_list()
			alias_list.pop(item.row())

			if text in alias_list:
				self._parent.showMessage("Alias already exists", "Error")
				item.setText(self.txtBeforeDblClick)

			# for i in range(self.rowCount()):
			# 	chkTxt = self.item(i, 0).text()
			# 	if chkTxt == text:
			# 		item.setText("Error")


class AdditionalSettings(QDialog):

	save_now = pyqtSignal(ModDict)

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

		self.statusBar = QStatusBar()
		self.statusBar.setSizeGripEnabled(False)

		main_layout.addWidget(self.enable_hide_Chkbx)
		main_layout.addWidget(self.hide_preview_Chkbx)
		main_layout.addWidget(horizontal_line)
		main_layout.addWidget(self.pathtable)
		main_layout.addLayout(edit_layout)
		# main_layout.addWidget(add_folder_btn)
		main_layout.addWidget(horizontal_line2)
		main_layout.addWidget(save_settings)
		main_layout.addWidget(self.statusBar)

		self.setLayout(main_layout)

		# self.show()

	def populate_table(self, alias_path_list: list):
		for alias_path in alias_path_list:
			alias = alias_path[0]
			path = alias_path[1]

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

		path_item = self.pathtable.item(selected_rows[-1], 1)
		alias_item = self.pathtable.item(selected_rows[-1], 0)

		selected_path = path_item.text()
		selected_alias = alias_item.text()
		
		self.temp_settings["Workstation Paths"]["Default Workstation"] = [selected_path, selected_alias]
		# if selected_path != self.temp_settings.value('Workstation Paths/Default Workstation'):
		print(f"text: {selected_path}, settings: {self.temp_settings['Workstation Paths']['Default Workstation']}")

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
				item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
		
		self.showMessage(f"Locked rows {selected_rows}", "COM")
				
	def unlock_row(self):
		selected_rows = self.get_selected_rows()

		for col in range(self.pathtable.columnCount()):
			for row in selected_rows:
				item = self.pathtable.item(row, col)

				if item is None:
					continue
				item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable)
		
		self.showMessage(f"Unlocked rows {selected_rows}", "COM")

	def addPathItem_custom(self, alias, path):
		self.pathtable.addItem(alias, path)

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
		self.statusBar.showMessage(prefix + " : " + str_, timeout)

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
		self.save_now.emit(self.temp_settings)
		# self.parent_settings.sync()
		sync = self.temp_settings.convert_to_settings()
		print(sync.convert_to_dict())
		sync.sync()

		self.showMessage("Settings saved successfully", "COM")

	def closeEvent(self, event) -> None:
		if self.check_changes():
			event.accept()
		else:
			confirmation = MessagePopUp("You have unsaved changes", "Do you want to discard all of it?", buttons=QMessageBox.Discard | QMessageBox.Save)
			# ret = confirmation.exec()
			# print(confirmation.clickedbutton)
			clickedbutton = confirmation.clickedbutton
			if clickedbutton == QMessageBox.Save:
				self.save_settings()
			elif clickedbutton == QMessageBox.Discard:
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
		self.project_filenames_as_filter = ["*.ai","*.psd"]
		self.preview_types = [".ai", ".psd", ".jpg", ".png"]

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
		self.thumbnail = self.workstation_files + r"\thumbnail"	

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
					print(f"""\"C:/Program Files/ImageMagick-7.1.0-Q8/convert.exe" -density 20x20 "{self.thumbnail}[0]" "{self.thumbnail}/thumbnail/{baseName}.jpg\"""")
					subprocess.run(f"""\"C:/Program Files/ImageMagick-7.1.0-Q8/convert.exe" -density 20x20 "{self.thumbnail}[0]" "{self.thumbnail}/thumbnail/{baseName}.jpg\"""")
					print(f"[{complete_path}[0]] --> File Converted --> [{self.thumbnail}/thumbnail/{baseName}.jpg]")

	def onClicked(self, index, label):
		# note mabe add a scanner when a directory is clicked then display in the bottom bar
		# produced_path = self.fileConverter(index)

		fileIn = self.sender().model().fileInfo(index)
		if not fileIn.isDir():
			complete_path = fileIn.absoluteFilePath()
			self.sender().fileName = fileIn.fileName()
			baseName = fileIn.completeBaseName()
		
			for type in self.preview_types:
				if self.sender().fileName.endswith(type):
					if type in self.project_filenames:
						preview_picture_pixmap = QPixmap(f"{self.thumbnail}/thumbnail/{baseName}.jpg")
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
			if fileIn.completeSuffix() in self.project_filenames:
				self.sender().project_dir = self.workstation_files + QDir.separator() + self.sender().fileName + " Raw Files"
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

		# self.setMinimumWidth(1000)
		
		# dir_path = QFileDialog.getExistingDirectory(self, "Select file folder directory")
		#* Add Combo box for each person
		
		# dir_path = r'D:/Student - Files/Eliazar'

		# -- workstation -- #
		# not each user will have a workstation
		# if not os.path.exists(workstation_files):
		# 	os.mkdir(workstation_files)

		# -- recycle bin -- #
		# if not os.path.exists(recycle_bin):
		# 	os.mkdir(recycle_bin)

		# -- thumbnail -- #    #warning:Please disable this when debugging
		if not os.path.exists(self.thumbnail):   #warning: delete the thumbnail folder when the program is finished
			os.mkdir(self.thumbnail)
			FILE_ATTRIBUTE_HIDDEN = 0x02
			ctypes.windll.kernel32.SetFileAttributesW(self.thumbnail, FILE_ATTRIBUTE_HIDDEN)

		# -- preview (left) -- #
		effect = QGraphicsDropShadowEffect(offset=QPoint(-3, 3), blurRadius=25, color=QColor("#111"))
		self.main_file_preview = ModifiedQLabel(effect=effect)
		self.main_file_preview.setHidden(True)

		# -- preview (right) -- #
		effect = QGraphicsDropShadowEffect(offset=QPoint(3, 3), blurRadius=25, color=QColor("#111"))
		self.connected_file_preview = ModifiedQLabel(effect=effect)
		self.connected_file_preview.setHidden(True)

		# -- left side pane -- #
		if not os.path.exists(self.workstation_files):
			os.mkdir(self.workstation_files)
			# note intro here because new

		# self.model = FileSystemModel()
		self.model = FileSystemModel()
		self.model.setRootPath(self.workstation_files)
		# self.model.setNameFilters(project_filenames_as_filter) # causes problems in the model file selection
		self.model.conNameFilters = self.project_filenames_as_filter        # self.dirProxy.dirModel.setNameFilterDisables(False)

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
		
		btn_show = QPushButton("Hide Preview")
		btn_show.clicked.connect(self.showList)
		button_layout.addWidget(btn_show)

		btn_hide = QPushButton("Enable Hide")
		btn_hide.clicked.connect(self.enableHide)
		button_layout.addWidget(btn_hide)

		self.workstationComboBox = QComboBox(self)
		self.workstationComboBox.currentIndexChanged.connect(self.set_root_path)
		# workstationComboBox.addItems(self.app_settings.get_list_from_settings(group="Workstation Paths"))
		self.populate_combobox()
		# for user in self.userlist:
		# 	user_path = Path(self.workstation_files, user)
		# 	if not user_path.exists():
		# 		os.mkdir(user_path)
		# 	workstationComboBox.addItem(user) # note you can also set an icon
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
		self.tree.isLeft = True
		root_index = self.model.index(self.app_settings["Workstation Paths"]["Workstations"][index][1])
		self.tree.setRootIndex(root_index)

	def populate_combobox(self):
		self.workstationComboBox.clear()
		# self.workstationComboBox.addItem(self.app_settings.get_default_workstation()[0])
		# self.workstationComboBox.addItem(self.app_settings.)
		self.workstationComboBox.addItems(self.app_settings.get_workstations_aliases())

	def open_additional_settings(self):
		self.additional_settings = AdditionalSettings(self, self.app_settings)
		self.additional_settings.save_now.connect(self.save_settings)
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
	# with open("sty.qss","r") as fh:
	# 	app.setStyleSheet(fh.read())
	# demo.showMaximized()
	demo.show()
	sys.exit(app.exec_())