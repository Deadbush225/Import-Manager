import sys
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class MQTreeView(QTreeView):
    def __init__(self, model):
        super().__init__()
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        # self.view1.setDragDropMode(QAbstractItemView.InternalMove)
        self.setModel(model)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        self.setDefaultDropAction(Qt.MoveAction)
        self.viewport().setAcceptDrops(True)

# class MyProxyStyle : public QProxyStyle
# {
# public:
#     void drawPrimitive(PrimitiveElement element, const QStyleOption *option, QPainter *painter, const QWidget *widget) const
#     {
#         if(element == QStyle::PE_IndicatorItemViewItemDrop)
#         {
#             painter->setRenderHint(QPainter::Antialiasing, true);
    
#             QPalette palette;
#             //QColor(90,108,217)
#             QColor c(palette.highlightedText().color());
#             QPen pen(c);
#             pen.setWidth(2);
#             c.setAlpha(50);
#             QBrush brush(c);
    
#             painter->setPen(pen);
#             painter->setBrush(brush);
#             if(option->rect.height() == 0)
#             {
#                 painter->drawEllipse(option->rect.topLeft(), 3, 3);
#                 painter->drawLine(QPoint(option->rect.topLeft().x()+3, option->rect.topLeft().y()), option->rect.topRight());
#             } else {
#                 painter->drawRoundedRect(option->rect, 5, 5);
#             }
#         } else {
#             QProxyStyle::drawPrimitive(element, option, painter, widget);
#         }
    
    
#     }
# };

class MyProxyStyle(QProxyStyle):
    def drawPrimitive(self, element: QStyle.PrimitiveElement, option: 'QStyleOption', painter: QPainter, widget: QWidget) -> None:
        if element == QStyle.PE_IndicatorItemViewItemDrop:
            painter.setRenderHint(QPainter.Antialiasing, True)
            palette = QPalette()
            c = QColor("red")
            pen = QPen(c)
            pen.setWidth(2)
            c.setAlpha(50)
            brush = QBrush(c)

            painter.setPen(pen)
            painter.setBrush(brush)

            print(option.type)
            print(widget)

            if option.rect.height() == 0:
                painter.drawEllipse(option.rect.topLeft(), 3, 3)
                painter.drawLine(QPoint(option.rect.topLeft().x()+3, option.rect.topLeft().y()), option.rect.topRight())
            else:
                painter.drawRoundedRect(option.rect, 5, 5)
        else:
            return super().drawPrimitive(element, option, painter, widget)
            

class AppDemo(QWidget):
    def __init__(self):
        super().__init__()
        # -- right -- #
        self.model1 = QStandardItemModel()
        self.model1.setRowCount(10)
        self.model1.setColumnCount(1)

        for i in range(0, 10):
            self.model1.setData(self.model1.index(i, 0), f'Row {i}', Qt.DisplayRole)

        self.view1 = MQTreeView(self.model1)

        # -- left -- #
        self.model2 = QStandardItemModel()
        self.model2.setRowCount(15)
        self.model2.setColumnCount(1)

        for i in range(0, 15):
            self.model2.setData(self.model2.index(i, 0), f'Row {i}', Qt.DisplayRole)

        self.view2 = MQTreeView(self.model2)

        # -- layout -- #
        layout = QHBoxLayout(self)
        layout.addWidget(self.view1)
        layout.addWidget(self.view2)

app = QApplication(sys.argv)
app.setStyle(MyProxyStyle())
main = AppDemo()
main.show()
app.exec_()