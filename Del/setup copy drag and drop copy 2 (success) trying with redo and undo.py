#! python3

import sys
import os
import shutil
import subprocess
import ctypes
from send2trash import send2trash

def deleteF(path: str):
    return path.replace("/", "\\")


from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from _subclassed import *

# notes: ln --recursive --mirror x:\source x:\destination
# notes if you want, you can use os.link then recursively check the tree every 5 secs

# hey if there's a problem, just check if the index is right `mapToSource` and `mapFromSource`

# todo: operation undo
# todo: make workstation for each person

# notes `recursiveFilteringEnabled` 

# -- Types -- #
project_filenames = ["ai","psd"]
project_filenames_as_filter = ["*.ai","*.psd"]
preview_types = [".ai", ".psd", ".jpg", ".png"]

# -- Paths -- #
dir_path           = r'D:/Student - Files/Eliazar'
workstation_files  = r'D:/Student - Files/Eliazar/Workstation Files'
thumbnail          = r"D:/Student - Files/Eliazar/thumbnail"
# temp               = r'D:/Student - Files/Eliazar/temp'
# recycle_bin        = r"D:/Student - Files/Eliazar/recycle bin"
# left_main_dirpath  = r"D:/Student - Files/Eliazar/Project Files"
# right_main_dirpath = r"D:/Student - Files/Eliazar/Random Raw Files"

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


class Tree(QTreeView):
    global project_filenames
    global preview_types
    global dir_path
    global workstation_files
    global thumbnail

    isLeft  = False
    isRight = False
    current_key = None

    def __init__(self):
        super().__init__()
        delegate = DisDelegate(self)
        # self.setItemDelegateForColumn(0, delegate)
        self.setItemDelegate(delegate)

        self.undostack = QUndoStack()

        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Expanding)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDefaultDropAction(Qt.CopyAction)
        self.viewport().setAcceptDrops(True)
        self.setAlternatingRowColors(True)
        self.setDropIndicatorShown(True)
        self.setColumnWidth(0, 250)

    def keyPressEvent(self, event):
        if event.key() == (Qt.Key_Control and Qt.Key_Y):
            self.undostack.redo()
        if event.key() == (Qt.Key_Control and Qt.Key_Z):
            self.undostack.undo()

    def checkDrag(self):
        modifiers = qApp.queryKeyboardModifiers()
        if self.modifiers != modifiers:
            self.modifiers = modifiers
            pos = QCursor.pos()
            # slightly move the mouse to trigger dragMoveEvent
            QCursor.setPos(pos + QPoint(1, 1))
            # restore the previous position
            QCursor.setPos(pos)

    def mousePressEvent(self, event):
        # print(self.indexAt(event.pos()).row())
        # if event.button() == Qt.LeftButton:
            # self.setCurrentIndex(self.indexAt(event.pos()))
            # self.selectionStart = event.pos
        if event.button() == Qt.RightButton:
            self.dragStartPosition = event.pos()

        return super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() != Qt.RightButton:
            return
        # elif event.buttons() == Qt.LeftButton:
        #     self.setSelection(QRect(self.selectionStart, event.pos()),QItemSelectionModel.Select)
        if ((event.pos() - self.dragStartPosition).manhattanLength() < QApplication.startDragDistance()):
            return

        print("dragging")
        self.modifiers = qApp.queryKeyboardModifiers()
        # a local timer, it will be deleted when the function returns
        dragTimer = QTimer(interval=500, timeout=self.checkDrag) # 100
        dragTimer.start()
        self.startDrag(Qt.MoveAction|Qt.CopyAction)

    def dragEnterEvent(self, event):
        self.passed_m = event.mimeData()
        event.accept()

    def dragLeaveEvent(self, event):
        print("leaving")
        if self.passed_m.hasUrls():
            self.leaving_urls = [QFileInfo(url.toLocalFile()).fileName() for url in self.passed_m.urls() if url.isLocalFile()]

            print(self.leaving_urls)

        return super().dragLeaveEvent(event)

    def dragMoveEvent(self, event):
        print("dragMoveEvent")
        if not event.mimeData().hasUrls():
            print("no urls")
            event.ignore()
            return
        if qApp.queryKeyboardModifiers() & Qt.ShiftModifier:
            event.setDropAction(Qt.MoveAction)
        else:
            event.setDropAction(Qt.CopyAction)
        event.accept()

    def dropEvent(self, event):
        print("[drop event] - dropped")

        dropAction = event.dropAction()

        # if event.source():
        ix = self.indexAt(event.pos())
        model = self.model()

        if ix.isValid():
            if not model.isDir(ix):
                ix = ix.parent()
            pathDir = model.filePath(ix)
        else:
            # for empty drag and drop
            pathDir = model.rootPath()

        m = event.mimeData()
        if m.hasUrls():
            urlLocals = [url for url in m.urls() if url.isLocalFile()]
            accepted = False
            for urlLocal in urlLocals:
                path = urlLocal.toLocalFile()
                info = QFileInfo(path)
                destination = QDir(pathDir).filePath(info.fileName()) # <- check if this one exists
                destination_cannonical = QDir(pathDir).path()
                source = info.absoluteFilePath()
                if source in destination:
                    continue  # means they are in the same folder
                if info.isDir():
                    if dropAction == Qt.CopyAction:
                        print(f"QDir -> source: {source} {os.path.exists(source)} | destination: {os.path.exists(destination)} {destination}")
                        # rep = QDir().rename(source, destination)
                        # print(rep)
                        # try: # note try block deprecated
                        #     shutil.move(source, destination)
                        # except Exception as e:
                        #     print(f'[warning droping in the same location] Error: {e}')
                        shutil.copytree(source, destination)

                        
                        # print(rep)

                    elif dropAction == Qt.MoveAction:
                        shutil.move(source, destination)
                elif info.isFile():
                    qfile = QFile(source)
                    if QFile(destination).exists():
                        n_info = QFileInfo(destination)
                        
                        destination = n_info.canonicalPath() + QDir.separator() + n_info.completeBaseName() + " (copy)"
                        if n_info.completeSuffix():   # for moving files without suffix
                            destination += "." + n_info.completeSuffix()

                    if dropAction == Qt.CopyAction:
                        qfile.copy(destination)
                    elif dropAction == Qt.MoveAction:
                        qfile.rename(destination)
                    print(f"added -> {info.fileName()}")  # for debugging

                accepted = True
            if accepted:
                event.acceptProposedAction()

    # context menu #
    # note to fuse the shift mode and non shift mode, just recieve the path and proceed

class FileSystemView(QWidget):
    global project_filenames
    global project_filenames_as_filter
    global preview_types
    global dir_path
    global workstation_files
    global thumbnail

    def __init__(self):
        super().__init__()

        # -- stylesheets -- #

        # self.setStyleSheet("ModifiedQLabel { background-color: lightgray }")

        self.UI_Init()
    
    def handle_buttons(self, toggle_on, toggle_off):
        button = self.sender()
        # if button is not None:
        text = button.text().strip()
        print(f"'{text}'")
        button.setText(toggle_on if text == toggle_off else toggle_off)

    def showList(self):
        self.main_file_preview.setHidden(not self.main_file_preview.isHidden())
        self.connected_file_preview.setHidden(not self.connected_file_preview.isHidden())
        self.handle_buttons("Hide Preview", "Show Preview")

    def enableHide(self):
        self.model.hideMode = not self.model.hideMode
        self.model.invalidateFilter()
        # self.dirProxy.dirModel.directoryLoaded.emit(workstation_files)
        # self.dirProxy.dirModel.sort(0, 0)
        self.handle_buttons("Disable Hide", "Enable Hide")

    def fileConverter(self, dir):

        iterator_ = QDirIterator(dir)

        while iterator_.hasNext():
            fileIn = QFileInfo(iterator_.next())

            baseName = fileIn.completeBaseName()
            fileName = fileIn.fileName()
            complete_path = fileIn.absoluteFilePath()
            path = fileIn.absolutePath()

            project_filenames = [".ai",".psd"]

            for item in project_filenames:
                if fileName.endswith(item):
                    print(f"""\"C:/Program Files/ImageMagick-7.1.0-Q8/convert.exe" -density 20x20 "{complete_path}[0]" "{dir_path}/thumbnail/{baseName}.jpg\"""")
                    subprocess.run(f"""\"C:/Program Files/ImageMagick-7.1.0-Q8/convert.exe" -density 20x20 "{complete_path}[0]" "{dir_path}/thumbnail/{baseName}.jpg\"""")
                    print(f"[{complete_path}[0]] --> File Converted --> [{dir_path}/thumbnail/{baseName}.jpg]")

    def onClicked(self, index, label):
        # note mabe add a scanner when a directory is clicked then display in the bottom bar
        # produced_path = self.fileConverter(index)

        fileIn = self.sender().model().fileInfo(index)
        if not fileIn.isDir():
            complete_path = fileIn.absoluteFilePath()
            self.sender().fileName = fileIn.fileName()
            baseName = fileIn.completeBaseName()
        
            for type in preview_types:
                if self.sender().fileName.endswith(type):
                    if type in project_filenames:
                        preview_picture_pixmap = QPixmap(f"{dir_path}/thumbnail/{baseName}.jpg")
                    else:
                        preview_picture_pixmap = QPixmap(complete_path)

                    # preview_picture_pixmap = preview_picture_pixmap.scaledToWidth(self.main_file_preview.width(), Qt.SmoothTransformation)

                    width = label.contentsRect().width()
                    height = label.contentsRect().height()

                    preview_picture_pixmap = preview_picture_pixmap.scaled(width, height, Qt.KeepAspectRatio)
                    label.setPixmap(preview_picture_pixmap)
        else:
            return
        
        # print(index.parent())
        # if index.parent() is self.tree
        if self.sender().isLeft: # Note these sender() is for setting the attributes of the Tree
            suffix = fileIn.completeSuffix()
            if fileIn.completeSuffix() in project_filenames:
                self.sender().project_dir = workstation_files + QDir.separator() + self.sender().fileName + " Raw Files"
                print("isleft")
                if not os.path.exists(self.sender().project_dir):
                    os.mkdir(self.sender().project_dir)

                self.model2.setRootPath(self.sender().project_dir)
                self.tree2.setRootIndex(self.model2.index(self.sender().project_dir))
                
                # -> expand all
                self.model2.directoryLoaded.connect(lambda : self.tree2.expandAll())

    def UI_Init(self):
        # appWidth = 1000
        # appHeight = 600
        self.setWindowTitle('File System Viewer')
        # self.setGeometry(200, 100, appWidth, appHeight)

        # self.setMinimumWidth(1000)
        
        # dir_path = QFileDialog.getExistingDirectory(self, "Select file folder directory")
        #* Add Combo box for each person
        
        # dir_path = r'D:/Student - Files/Eliazar'

        # -- recycle bin -- #
        # if not os.path.exists(recycle_bin):
        # 	os.mkdir(recycle_bin)

        # -- thumbnail -- #    #warning:Please disable this when debugging
        if not os.path.exists(thumbnail):   #warning: delete the thumbnail folder when the program is finished
            os.mkdir(thumbnail)
            FILE_ATTRIBUTE_HIDDEN = 0x02
            ctypes.windll.kernel32.SetFileAttributesW(thumbnail, FILE_ATTRIBUTE_HIDDEN)

        # -- preview (left) -- #
        effect = QGraphicsDropShadowEffect(offset=QPoint(-3, 3), blurRadius=25, color=QColor("#111"))
        self.main_file_preview = ModifiedQLabel(effect=effect)
        
        # -- preview (right) -- #
        effect = QGraphicsDropShadowEffect(offset=QPoint(3, 3), blurRadius=25, color=QColor("#111"))
        self.connected_file_preview = ModifiedQLabel(effect=effect)

        # -- left side pane -- #
        if not os.path.exists(workstation_files):
            os.mkdir(workstation_files)
            # note intro here because new

        # self.model = QFileSystemModel()
        self.model = QFileSystemModel()
        self.model.setRootPath(workstation_files)
        self.model.setNameFilters(project_filenames_as_filter)
        self.model.conNameFilters = project_filenames_as_filter
        # self.dirProxy.dirModel.setNameFilterDisables(False)

        # self.dirProxy.dirModel.setFilter(QDir.Files | QDir.NoDotAndDotDot)

        # self.model2.setReadOnly(False)

        self.tree = Tree()
        self.tree.setModel(self.model)

        self.tree.isLeft = True
        root_index = self.model.index(workstation_files)
        self.tree.setRootIndex(root_index)
        self.tree.clicked.connect(lambda event: self.onClicked(event, self.main_file_preview))

        # self.dirProxy = DirProxy()
        # self.tree.setModel(self.dirProxy)
        # self.dirProxy.setNameFilters(['*.py'])


        # -- right side pane-- #
        # if not os.path.exists(right_main_dirpath):
        # 	os.mkdir(right_main_dirpath)

        self.model2 = QFileSystemModel()
        # self.model2.setRootPath(right_main_dirpath) # note - not set when started only when a project file is clicked
        # self.model2.setReadOnly(False)

        self.tree2 = Tree()
        self.tree2.isRight = True
        self.tree2.setModel(self.model2)
        # self.tree2.setRootIndex(self.model2.index(right_main_dirpath))
        self.tree2.clicked.connect(lambda event: self.onClicked(event, self.connected_file_preview))

        # self.fileConverter(rf"{self.dir_path}/Project Files") #warning: enable this
        
        # -- layout -- #
        self.main_layout = QVBoxLayout()

        self.tree_layout = QHBoxLayout()
        self.tree_layout.addWidget(self.main_file_preview)
        self.tree_layout.addWidget(self.tree)
        self.tree_layout.addWidget(self.tree2)
        self.tree_layout.addWidget(self.connected_file_preview)

        button_layout = QVBoxLayout()
        
        btn_show = QPushButton("Hide Preview")
        btn_show.clicked.connect(self.showList)
        button_layout.addWidget(btn_show)

        btn_hide = QPushButton("Enable Hide")
        btn_hide.clicked.connect(self.enableHide)
        button_layout.addWidget(btn_hide)

        self.main_layout.addLayout(button_layout)
        self.main_layout.addLayout(self.tree_layout)

        self.setLayout(self.main_layout)
        
        # self.showFullScreen()

if __name__ == '__main__':

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    demo = FileSystemView()
    # with open("sty.qss","r") as fh:
    # 	app.setStyleSheet(fh.read())
    # demo.showMaximized()
    demo.show()
    sys.exit(app.exec_())
