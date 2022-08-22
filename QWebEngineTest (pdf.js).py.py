from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
import sys
import os



# Inspect in pyqt5: https://stackoverflow.com/a/58892608/15870976
DEBUG_PORT = '5588'
DEBUG_URL = 'http://127.0.0.1:%s' % DEBUG_PORT
os.environ['QTWEBENGINE_REMOTE_DEBUGGING'] = DEBUG_PORT

class Window():
    def __init__(self):
        super().__init__()
        pdfjs = "file:///D:/CODING RELATED/Projects/Import Manager/pdfjs-2.15.349-legacy-dist/web/viewer.html"

        pdf_url = QUrl().fromUserInput(f"{pdfjs}?file=file:///C:/Users/Eliaz/Desktop/qt5cadaquesPart14.pdf")
        # pdf_url = QUrl("https://css-tricks.com/almanac/properties/s/scrollbar-color/")

        self.preview = QWebEngineView()
        self.preview.settings().setAttribute(QWebEngineSettings.WebAttribute.DnsPrefetchEnabled, True)
        # self.preview.loadFinished.connect(self.handle_loaded)

        self.preview.load(pdf_url)
        self.preview.show()

        self.inspector = QWebEngineView()
        self.inspector.setWindowTitle("Web Inspector")
        self.inspector.load(QUrl(DEBUG_URL))

    def handle_loaded(self, ok):
        if ok:
            self.preview.page().setDevToolsPage(self.inspector.page())
            self.inspector.show()

app = QApplication(sys.argv)
window = Window()
sys.exit(app.exec())