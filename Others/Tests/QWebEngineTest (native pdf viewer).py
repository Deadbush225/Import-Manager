import sys
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *

from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings

app = QApplication(sys.argv)

webView = QWebEngineView()
webView.setGeometry(300, 200, 500, 400)
webView.settings().setAttribute(QWebEngineSettings.WebAttribute.PluginsEnabled, True)
webView.settings().setAttribute(QWebEngineSettings.WebAttribute.PdfViewerEnabled, True)

url = QUrl.fromLocalFile(r"C:/Users/Eliaz/Desktop/qt5cadaquesPart14.pdf")
webView.setUrl(url)

webView.show()

sys.exit(app.exec())
