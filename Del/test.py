def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.origin = event.pos()
            self.rubberBand.setGeometry(QRect(self.origin, QSize()))
            self.rectChanged.emit(self.rubberBand.geometry())
            self.rubberBand.show()
            self.changeRubberBand = True
            return
            # QGraphicsView.mousePressEvent(self,event)

        super().mousePressEvent(event)

def mouseReleaseEvent(self, event):
    if event.button() == Qt.LeftButton:
        self.changeRubberBand = False
        if self.rubberBand.isVisible():
            self.rubberBand.hide()
            rect = self.rubberBand.geometry()
            # rect_scene = self.mapToScene(rect).boundingRect()
            # selected = self.scene().items(rect_scene)

            # if selected:
            #     print(
            #         "".join("Item: %s\n" % child.name for child in selected)
            #     )
            # else:
            #     print(" Nothing\n")
        # QGraphicsView.mouseReleaseEvent(self, event)
    super().mouseReleaseEvent(event)

def mouseMoveEvent(self, event):
    if self.changeRubberBand:
        self.rubberBand.setGeometry(
            QRect(self.origin, event.pos()).normalized()
        )
        self.rectChanged.emit(self.rubberBand.geometry())
        # QGraphicsView.mouseMoveEvent(self, event)
    super().mouseMoveEvent(event)

if __name__ == "main":
    quit()