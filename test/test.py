# import sys
# from PyQt5.QtCore import *
# from PyQt5.QtWidgets import *
# from PyQt5.QtGui import *
# # Subclass QMainWindow to customize your application's main window 

# class Window(QWidget):
#     def __init__(self):
#         super().__init__()
#         self.button = QPushButton("Press Me!")
#         self.button.setEnabled(True)

#         self.label_layout = QHBoxLayout(self)
#         self.label_layout.addWidget(self.button)

#         self.show()

# app = QApplication(sys.argv)
# ex = Window()
# sys.exit(app.exec_())


# for item in range(len([1,2,3,4,5,6,7,8,9,0])):
#     print(item)

empty_tuple = ('', '')

print(bool(empty_tuple))