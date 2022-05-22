from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

# -> undo commands
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

			file.moveToTrash()
			self.recycle_path = file.fileName()

			# -> creating folder
			os.mkdir(self.new_folder)
			return

		os.mkdir(self.new_folder)
	
	def undo(self):
		print('undoing')
		if self.override:
			shutil.move(self.recycle_path, self.restore_path)
		
		QFile(self.new_folder).moveToTrash()

class unMoveToNewFolderPopup(QUndoCommand):
	def __init__(self, newfolder, index_list, model, override=False):
		super().__init__()
		self.model = model
		self.index_list = index_list
		self.override = override
		self.new_folder = newfolder
	
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
			os.mkdir(self.new_folder)
		else:
			os.mkdir(self.new_folder)

		# -> moving files
		for index_fileinfo in self.index_list:
			self.original_folder = index_fileinfo.canonicalPath()

			#warning: make sure that the folder will actually make the folder inside
			if (index_fileinfo.canonicalPath() == self.model.rootPath()) or (self.model.rootPath() in index_fileinfo.canonicalPath()):  #warning: checking if the files are in the same of the rootfolder
				file_to_rename = index_fileinfo.canonicalFilePath()
				print(file_to_rename)
				shutil.move(file_to_rename, self.new_folder)
	
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
	
	def __init__(self, index_list, root_path,override=False):
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

# -> models
# deprecated
class DirProxy(QSortFilterProxyModel):
    nameFilters = ''
    hideMode = False  # false to make it disable instead
    enabled = (Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled | Qt.ItemIsEnabled)
    disabled = (Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled)
    def __init__(self):
        super().__init__()
        self.dirModel = QFileSystemModel()
        self.dirModel.setFilter(QDir.NoDotAndDotDot | QDir.AllDirs | QDir.Files) # <- added QDir.Files to view all files
        self.setSourceModel(self.dirModel)

    def flags(self, index):
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

class FileSystemModel(QFileSystemModel):
    hideMode = False
    conNameFilters = []
    def hasChildren(self, parent):
        file_info = self.fileInfo(parent)
        _dir = QDir(file_info.absoluteFilePath())
        return bool(_dir.entryList(self.filter()))

class DisDelegate(QStyledItemDelegate):
    # hideMode = False
    def initStyleOption(self, option: 'QStyleOptionViewItem', index: QModelIndex) -> None:
        super().initStyleOption(option, index)
        row = index.row()
        model = index.model()
        # sourcemodel = index.model().sourceModel()

        # print(f"row {index.row()}")
        # print(f"model {index.model()}")
        # print(f"source model {index.model().sourceModel()}")
        
        # if not model.hideMode:
        # index = model.mapToSource(index)
        if not index.isValid():
            # return 0
            pass

        # Disable even rows, enable odd rows
        # if index.row() % 2 == 0:
        #     return Qt.NoItemFlags
        # else:
        #     return Qt.ItemIsEnabled
        if model.isDir(index):
            qdir = QDir(model.filePath(index))
            if model.conNameFilters:
                qdir.setNameFilters(model.conNameFilters)
            if bool(qdir.entryInfoList(qdir.NoDotAndDotDot|qdir.AllEntries|qdir.AllDirs)):
                pass
                # return model.enabled
            else:
                # return model.disabled
                # option.palette.setBrush(QPalette.Base, QColor("#eeeeee"))
                # option.palette.setBrush(QPalette.Base, Qt.red)
                option.palette.setBrush(QPalette.Text, QColor("#9a9a9a"))
                # option.backgroundBrush = QColor("red")
                # option.backgroundBrush = QColor("#eeeeee")

        else:  # <- index refers to a file
            if index.column != 0:
                return
            qdir = QDir(model.filePath(index))

            if qdir.match(model.conNameFilters, model.fileName(index)):
                # return model.enabled
                pass
            else:
                # return model.disabled # <- returns true if the file matches the nameFilters
                # option.palette.setBrush(QPalette.Base, QColor("#eeeeee"))
                # option.palette.setBrush(QPalette.Base, Qt.red)
                option.palette.setBrush(QPalette.Text, QColor("#9a9a9a"))
                # option.backgroundBrush = QColor("red")
                # option.backgroundBrush = QColor("#eeeeee")
        # return model.enabled
