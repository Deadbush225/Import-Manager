from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

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
