from _subclassed import FileSystemModel
from pathlib import Path, PureWindowsPath
from multipledispatch import dispatch
import os

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


#[Overload] -> OV_mkdir
@dispatch(QFile)
def OV_mkdir(path):
	path.exists()

@dispatch(str)
def OV_mkdir(path):
	os.mkdir(path)

@dispatch(PureWindowsPath)
def OV_mkdir(path):
	os.mkdir(path)

@dispatch(list)
def OV_mkdir(path_list):
	for path in path_list:
		os.mkdir(path)

#[Overload] -> OV_exists
@dispatch(str)
def OV_exists(path :str):
	return os.path.exists(path)

@dispatch(list, str, FileSystemModel)
def OV_exists(index_list, name, model):
	"""adds the name to each item in the list and tests it if it exists

	Args:
		index_list (list): List[QModelIndex], returns None if meets an index pointing to a file
		name (str): file name to check for existence

	Returns:
		None: if meets an index pointing to a file 
		True: if any exists
		list: if none exists, the list contains the valid path
	"""

	if not index_list:
		return OV_exists(model.rootPath() + "/" + name)

	model : FileSystemModel = index_list[0].model() #getting an index sample

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

#[Overload] -> OV_Move:
@dispatch(str, str)
def OV_Move(str_path, str_path):

@dispatch(PureWindowsPath, PureWindowsPath)
def OV_Move(pathlib_path, pathlib_path):

@dispatch(PureWindowsPath, str)
def OV_Move(pathlib_path, str_path):
	
@despatch(str, PureWindowsPath)
def OV_Move(str, PureWindowsPath):
