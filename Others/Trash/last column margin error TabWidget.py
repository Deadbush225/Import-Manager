from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys

# class Buttons_Delegate(QStyledItemDelegate):
# 	def paint(self, painter, option, index):
# 		button = QStyleOptionButton()
# 		r = option.rect

# 		x = r.left() + r.width() - 30
# 		y = r.top()
# 		w = 30
# 		h = 30

# 		button.rect = QRect(x,y,w,h)
# 		button.text = "Please?"
# 		button.state = QStyle.State_Enabled
		
# 		QApplication.style().drawControl( QStyle.CE_PushButton, button, painter)

# 	def editorEvent(event, model, option, index):
# 		if event.type() == QEvent.MouseButtonRelease:
# 			e = QMouseEvent(event)
# 			clickY = e.y()
# 			clickX = e.x()

# 			r = option.rect
# 			x = r.left() + r.width() - 30
# 			y = r.top()
# 			w = 30
# 			h = 30

# 			if (clickX > x) and (clickX < x + w):
# 				if (clickY > y) and (clickY < y + h):
# 					d = QDialog()
# 					d.setGeometry(0, 0, 100, 100)
# 					d.show()



class ModTableWidget(QTableWidget):
	def __init__(self):
		super().__init__(0, 3)
		self.setHorizontalHeaderLabels(["Alias", "Path", ""])
		
		self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
		self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
		self.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents) # Does not work
		self.setSelectionBehavior(QAbstractItemView.SelectRows)
		
		print(self.horizontalHeader().minimumSectionSize())
		self.horizontalHeader().setMinimumSectionSize(30)
		# self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

		self.is_default_group = QButtonGroup()

		for item in range(10):
			self.addItem(str(item), str(item))

	def addItem(self, alias, path):
		last_row_index = self.rowCount()
		self.insertRow(last_row_index)

		alias_item = QTableWidgetItem()
		alias_item.setText(alias)
		self.setItem(last_row_index, 0, alias_item)

		path_item = QTableWidgetItem()
		path_item.setText(path)
		self.setItem(last_row_index, 1, path_item)

		is_default_btn = QPushButton("Btn")
		is_default_btn.setMaximumWidth(30)
		is_default_btn.setCheckable(True)

		self.is_default_group.addButton(is_default_btn)
		self.setCellWidget(last_row_index, 2, is_default_btn)

if __name__ == '__main__':
	app = QApplication(sys.argv)

	tablewidget = ModTableWidget()
	tablewidget.show()

	sys.exit(app.exec_())