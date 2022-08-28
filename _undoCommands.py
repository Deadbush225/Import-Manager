from PyQt6.QtWidgets import QTreeView
from PyQt6.QtGui import QUndoCommand, QFileSystemModel
from PyQt6.QtCore import QFile, QModelIndex

from _helpers import *

from pathlib import Path
import shutil
import os

# -> undo commands
class doCreateFolder(QUndoCommand):
	def __init__(self, newfolder=str, override=False, newfolder_list=[], model=QFileSystemModel):
		super().__init__()
		#-> both index_list and mode is partners

		# self.index_list = index_list
		# index_list = [model.filePath(index) for index in index_list]
		#-> OV_mkdir() takes str or list[str]
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
			OV_mkdir(self.new_folder)
			return

		OV_mkdir(self.new_folder)
	
	def undo(self):
		print('undoing')
		if self.override:
			shutil.move(self.recycle_path, self.restore_path)
		
		QFile(self.new_folder).moveToTrash()

class doRenamePopup(QUndoCommand):
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
					new_path = index_fileinfo.absolutePath() + "/" + self.new_file + "." + index_fileinfo.suffix()
				elif index_fileinfo.isDir():
					new_path = index_fileinfo.absolutePath() + "/" + self.new_file
				
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
		
		self.parent.OV_expand(self.model.index(self.new_folder, 0))
	
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
