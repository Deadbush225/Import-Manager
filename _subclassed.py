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
# from pathlib import Path, PureWindowsPath
# from functools import singledispatch
# from multipledispatch import dispatch

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
		
		overridePopup = MessagePopUp("The folder with the same name already OV_exists, \n Do you want to Override the old folder?", "If you want to just use the old folder just select No")

		if overridePopup.clickedbutton == QMessageBox.StandardButton.Yes:
			self.confirmOverride = MessageOverrideConfirmationPopUp().confirmOverride
			self.override = self.confirmOverride.confirmOverride
			
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

# -> extensions
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

class ModPushButton(QPushButton):
	def __init__(self, icon, str_):
		super().__init__(icon, str_)

		self.setFixedWidth(30)

class ModAction(QAction):
	def __init__(self, name: str, key_sequence: Qt.Key, parent: QWidget = None):
		# if error try self as parent
		super().__init__(name, parent=parent)
		self.setShortcutVisibleInContextMenu(True)
		self.setShortcut(key_sequence)
		self.setShortcutContext(Qt.ShortcutContext.WidgetWithChildrenShortcut)

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
	txtBeforeDblClick = None
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
		self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents | QHeaderView.ResizeMode.Interactive)
		self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
		self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
		# self.horizontalHeader().setStretchLastSection(True)
		self.horizontalHeader().setMinimumSectionSize(30)
		# self.setColumnWidth(0, 100)

		self.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)

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

	def addItem(self, alias, path, checked=False, row=-1):
		last_row_index = self.rowCount() if row == -1 else row
		self.insertRow(last_row_index)

		folder_alias_item = QTableWidgetItem()
		folder_alias_item.setText(alias)
		folder_alias_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)

		self.setItem(last_row_index, 0, folder_alias_item)

		folder_path_item = QTableWidgetItem()
		folder_path_item.setText(path)
		folder_path_item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)

		self.setItem(last_row_index, 1, folder_path_item)

		# wrapper = QWidget()
		# layout = QHBoxLayout()
		# layout.setContentsMargins(0, 0, 0, 0)

		is_default_icon = QIcon(r"Icons\home.png")
		is_default_btn = QPushButton(is_default_icon, "")
		is_default_btn.setMaximumWidth(30)
		is_default_btn.setFlat(True)
		is_default_btn.setCheckable(True)
		is_default_btn.setChecked(checked)
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
		if item.column() == 0 and self.txtBeforeDblClick: # alias column
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

# -> MVD - (Model View Delegate)

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

# -> wrappers
class QFilewList():
	def __init__(self, file):
		if isinstance(file, QFile):
			self.file = file
			self.type = QFile
		elif isinstance(file, list):
			self.file = [QFile(item) for item in file]
			self.type = list
	
	def fileName():
		if self.type == QFile:
			return self.file.fileName()
		elif self.type == list:
			return [file.fileName() for file in self.file]
	
	def moveToTrash(sself:
		if self.type == QFile:
			return self.file.moveToTrash()
		elif self.type == list:
			return [file.moveToTrash() for file in self.file]