import os
from pathlib import *

def renameChecker(path):
	p = Path(path)
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
				newF = parent / PureWindowsPath(name + f" - copy")
			else:
				newF = parent / PureWindowsPath(name + f" - copy ({counter})")
			p = Path(newF)
			counter += 1

	return newF

print(renameChecker(r"D:\CODING RELATED\IMPORT MANAGER\test\New folder"))