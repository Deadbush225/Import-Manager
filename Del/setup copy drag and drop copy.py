import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class Tree(QTreeView):
	def __init__(self):
		super().__init__()
		self.setDragDropMode(QAbstractItemView.DragDrop)
		self.setDropIndicatorShown(True)
		self.viewport().setAcceptDrops(True)
		self.setDefaultDropAction(Qt.CopyAction)
		self.setSelectionMode(QAbstractItemView.ExtendedSelection)
		self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

	def checkDrag(self):
		modifiers = qApp.queryKeyboardModifiers()
		if self.modifiers != modifiers:
			self.modifiers = modifiers
			pos = QCursor.pos()
			# slightly move the mouse to trigger dragMoveEvent
			QCursor.setPos(pos + QPoint(1, 1))
			# restore the previous position
			QCursor.setPos(pos)

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

	def dragMoveEvent(self, event):
		if not event.mimeData().hasUrls():
			event.ignore()
			return
		if qApp.queryKeyboardModifiers() & Qt.ShiftModifier:
			event.setDropAction(Qt.MoveAction)
		else:
			event.setDropAction(Qt.CopyAction)
		event.accept()

	# -- mouse dragging -- #
	def mousePressEvent(self, event):
		if event.button() == Qt.RightButton:
			self.dragStartPosition = event.pos()

		return super().mousePressEvent(event)

	# def mouseMoveEvent(self, event):
	# 	print(self.defaultDropAction())
	# 	# add the selection mechanism here try cancel()
	# 	if event.buttons() != Qt.RightButton:
	# 		return
	# 	if ((event.pos() - self.dragStartPosition).manhattanLength() < QApplication.startDragDistance()):
	# 		return
		
	# 	drag = ModifiedQDrag(self)
	# 	mimeData = QMimeData()
	# 	mimeData = self.model().mimeData([self.indexAt(event.pos())]) # <- later change it to colAt
	# 	drag.setMimeData(mimeData)

	# 	# dragAction = drag.exec(Qt.CopyAction)
	# 	dragAction = drag.exec(Qt.MoveAction | Qt.CopyAction, Qt.CopyAction)

	# 	return super().mouseMoveEvent(event)

	# def dragMoveEvent(self, event):
	# 	m = event.mimeData()
	# 	if m.hasUrls():
	# 		event.accept()
	# 		return
	
	# 	event.ignore()
		
	def dropEvent(self, event):
		print("[drop event] - dropped")

class FileSystemView(QWidget):
	def __init__(self):
		super().__init__()
		self.setMouseTracking(True)

		# -- left side -- #
		left_side_dir = r"D:\CODING RELATED\IMPORT MANAGER\test copy"

		self.model = QFileSystemModel()
		self.model.setRootPath(left_side_dir)

		self.tree = Tree()
		self.tree.setModel(self.model)
		self.tree.setRootIndex(self.model.index(left_side_dir))

		# -- right side -- #
		right_side_dir = r"D:\CODING RELATED\IMPORT MANAGER\test"

		self.model2 = QFileSystemModel()
		self.model2.setRootPath(right_side_dir)

		self.tree2 = Tree()
		self.tree2.setModel(self.model2)
		self.tree2.setRootIndex(self.model2.index(right_side_dir))
		
		# -- layout -- #
		self.tree_layout = QHBoxLayout()
		self.tree_layout.addWidget(self.tree)
		self.tree_layout.addWidget(self.tree2)

		self.setLayout(self.tree_layout)

app = QApplication(sys.argv)
demo = FileSystemView()
demo.show()
sys.exit(app.exec_())
