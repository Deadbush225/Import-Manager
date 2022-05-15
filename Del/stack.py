import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class ModifiedQDrag(QDrag):
	def __init__(self, source):
		super().__init__(source)
		self.timer = QTimer(self)
		self.timer.timeout.connect(self.process_event)
		self.timer.setInterval(100)
		self.timer.start()

	def process_event(self):
		if qApp.keyboardModifiers() & Qt.ControlModifier:
			self.source().setDefaultDropAction(Qt.CopyAction)

		elif qApp.keyboardModifiers() & Qt.ShiftModifier:
			print("shift pressed")
			self.source().setDefaultDropAction(Qt.MoveAction)

class Tree(QTreeView):
	def __init__(self):
		super().__init__()
		self.setDragDropMode(QAbstractItemView.DragDrop)
		self.setDropIndicatorShown(True)
		self.viewport().setAcceptDrops(True)
		self.setSelectionMode(QAbstractItemView.ExtendedSelection)
		self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

	# -- mouse dragging -- #
	def mousePressEvent(self, event):
		if event.button() == Qt.RightButton:
			self.dragStartPosition = event.pos()

		return super().mousePressEvent(event)

	def mouseMoveEvent(self, event):
		if event.buttons() != Qt.RightButton:
			return
		if ((event.pos() - self.dragStartPosition).manhattanLength() < QApplication.startDragDistance()):
			return
		
		drag = ModifiedQDrag(self)
		mimeData = QMimeData()
		mimeData = self.model().mimeData([self.indexAt(event.pos())])
		drag.setMimeData(mimeData)

		dragAction = drag.exec(Qt.MoveAction | Qt.CopyAction, Qt.CopyAction)
		return super().mouseMoveEvent(event)

	def dragMoveEvent(self, event):
		m = event.mimeData()
		if m.hasUrls():
			event.accept()
			return
	
		event.ignore()
		
	def dropEvent(self, event):
		print("[drop event] - dropped")

class FileSystemView(QWidget):
	def __init__(self):
		super().__init__()

		# -- left side -- #
		left_side_dir = r"<Dir>"

		self.model = QFileSystemModel()
		self.model.setRootPath(left_side_dir)

		self.tree = Tree()
		self.tree.setModel(self.model)
		self.tree.setRootIndex(self.model.index(left_side_dir))

		# -- right side -- #
		right_side_dir = r"<Dir>"

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
