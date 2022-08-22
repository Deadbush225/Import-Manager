    from PyQt6.QtCore import QUrl
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    import sys

    class Window():
        def __init__(self):
            super().__init__()
            pdfjs = "file:///D:/CODING RELATED/Projects/Import Manager/pdfjs-2.15.349-legacy-dist/web/viewer.html"

            pdf_url = QUrl().fromUserInput(f"{pdfjs}?file=file:///C:/Users/Eliaz/Desktop/qt5cadaquesPart14.pdf")

            self.preview = QWebEngineView()
            self.preview.load(pdf_url)
            self.preview.show()

    app = QApplication(sys.argv)
    window = Window()
    sys.exit(app.exec())