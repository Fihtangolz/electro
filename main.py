from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore
import sys
from collections import OrderedDict
import copy
from queue import *


class ToogleButton(QGraphicsItem):
    def mousePressEvent(self, event):
        if self.state:
            self.state = False
            self.parent.outPoints[0] = False
        else:
            self.state = True
            self.parent.outPoints[0] = True
        self.update()

    def __init__(self, center, parent=None, name=None):
        super(ToogleButton, self).__init__()
        self.center = center
        self.setParentItem(parent)
        self.parent = parent
        self.name = name
        self.state = True

        self.connections = []

    def paint(self, painter, option, widget=None):
        painter.setPen(QPen(QtCore.Qt.NoPen))
        if self.state:
            painter.setBrush(QBrush(QColor(0, 255, 0)))
        else:
            painter.setBrush(QBrush(QColor(255, 0, 0)))
        painter.drawRect(-20.0, 20.0, 20.0, 20.0)

    def boundingRect(self):
        return QRectF(-20.0, 20.0, 20.0, 20.0)


class ConnetionsPoint(QGraphicsItem):
    def mousePressEvent(self, event):
        data = history.currentActionsData
        if history.currentAction is "selectElement" and \
           isinstance(data, ConnetionsPoint) and \
           history.currentActionsData is not self:
                self.scene().connectElements(self, history.currentActionsData)
        else:
            history.currentAction = "selectElement"
            history.currentActionsData = self

    def __init__(self, center, parent=None, name=None):
        super(ConnetionsPoint, self).__init__()
        self.center = center
        self.setParentItem(parent)
        self.parent = parent
        self.name = name
        self.connections = []

        # Idicate what type of signal now emmit/get or None
        self.state = None

        self.setParentItem(parent)

    def paint(self, painter, option, widget=None):
        painter.setPen(QPen(QtCore.Qt.NoPen))

        if self.state == None:
            painter.setBrush(QBrush(QColor(130, 130, 130)))
        elif self.state == True:
            painter.setBrush(QBrush(QColor(0, 255, 0)))
        else:
            painter.setBrush(QBrush(QColor(255, 0, 0)))
        painter.drawRect(10.0, 10.0, 10.0, 10.0)

    def boundingRect(self):
        return QRectF(10.0, 10.0, 10.0, 10.0)


class Element(QGraphicsItem):
    def __init__(self, parent=None, inPoints=None, outPoints=None, imgPath=None, name=None, processingFunc=None):
        self.inPoints = []
        self.outPoints = []
        self.name = name
        self.processingFunc = processingFunc
        super(Element, self).__init__()
        for el in inPoints:
            item = ConnetionsPoint(el.point, self, el.name)
            item.setPos(self.boundingRect().topLeft() + el.point)
            self.inPoints.append(item)

        for el in outPoints:
            item = ConnetionsPoint(el.point, self, el.name)
            item.setPos(self.boundingRect().topLeft() + el.point)
            self.outPoints.append(item)

        self.imgPath = imgPath

        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)

    def mousePressEvent(self, event):
        history.currentAction = "selectElement"
        history.currentActionsData = self

        super(Element, self).mousePressEvent(event)

    def paint(self, painter, option, widget=None):
        painter.drawPixmap(QPointF(80.0, 80.0), QPixmap(self.imgPath))

    def boundingRect(self):
        return QRectF(80.0, 80.0, 80.0, 80.0)


class Source(Element):
    def __init__(self, parent=None, inPoints=None, outPoints=None, imgPath=None, name=None):
        super(Source, self).__init__(
            parent, inPoints, outPoints, imgPath, name)
        tooglePos = QPointF(0, 0)
        self.toogleButton = ToogleButton(tooglePos, self, "ToogleButton")
        self.toogleButton.setPos(self.boundingRect().topLeft() + tooglePos)


class EditingArea(QGraphicsScene):
    def mouseReleaseEvent(self, event):
        if history.currentAction is "createElement":
            item = self.elements[history.currentActionsData](self)
            item.setPos(event.buttonDownScenePos(
                Qt.LeftButton) - QPointF(80, 80))
            self.addItem(item)
            history.currentAction = None

        super(EditingArea, self).mouseReleaseEvent(event)

    def __init__(self, parent=None):
        super(EditingArea, self).__init__(parent)
        self.elements = {}

        class elContainer():
            def __init__(self, point, name):
                self.point = point
                self.name = name

        self.elements["Output"] = lambda self: Element(
            self,
            [elContainer(QPointF(-10, 15), "0")],
            [],
            "./res/toolbar/output.png",
            "Output"
        )

        self.elements["Source"] = lambda self: Source(
            self,
            [],
            [elContainer(QPointF(45, 15), "0")],
            "./res/toolbar/input.png",
            "Source"
        )

        self.elements["DTrigger"] = lambda self: Element(
            self,
            [elContainer(QPointF(-15, -5), "0"),
             elContainer(QPointF(-15, 35), "1")],
            [elContainer(QPointF(45, -5), "2"),
             elContainer(QPointF(45, 35), "3")],
            "./res/toolbar/dtrigger.png",
            "DTrigger"
        )
        self.elements["RSTrigger"] = lambda self: Element(
            self,
            [elContainer(QPointF(-15, -5), "0"),
             elContainer(QPointF(-15, 35), "1")],
            [elContainer(QPointF(45, -5), "2"),
             elContainer(QPointF(45, 35), "3")],
            "./res/toolbar/rs.png",
            "RSTrigger"
        )
        self.elements["AND"] = lambda self: Element(
            self,
            [elContainer(QPointF(-15, -5), "4"),
             elContainer(QPointF(-15, 35), "5")],
            [elContainer(QPointF(45, 15), "6")],
            "./res/toolbar/and.png",
            "AND"
        )
        self.elements["NOT"] = lambda self: Element(
            self,
            [elContainer(QPointF(-15, 16), "7")],
            [elContainer(QPointF(45, 16), "8")],
            "./res/toolbar/not.png",
            "NOT"
        )
        self.elements["Resistor"] = lambda self: Element(
            self,
            [elContainer(QPointF(-15, -5), "9")],
            [elContainer(QPointF(45, -5), "10")],
            "./res/toolbar/resistor.png",
            "Resistor"
        )

            # petry elements
        def petryRSTrigger_TF(obj):
            if obj.inPoints[0].state and obj.inPoints[1].state is False:
                obj.outPoints[0].state = True
                obj.outPoints[1].state = False
            elif obj.inPoints[1].state and obj.inPoints[0].state is False:
                obj.outPoints[0].state = False
                obj.outPoints[1].state = True
            else:
                obj.outPoints[0].state = None
                obj.outPoints[1].state = None

        self.elements["petryRSTrigger"] = lambda self: Element(
            self,
            [elContainer(QPointF(-2, -5), "0"),
             elContainer(QPointF(-2, 35), "1")],
            [elContainer(QPointF(30, -5), "2"),
             elContainer(QPointF(30, 35), "3")],
            "./res/toolbar/petryrstrigger.png",
            "petryRSTrigger",
            petryRSTrigger_TF
        )

        def petryDTrigger_TF(obj):
            if obj.inPoints[1].state:
                if obj.outPoints[0].state is not obj.inPoints[0].state:
                    obj.outPoints[1].state = True
                else:
                    obj.outPoints[1].state = None
                obj.outPoints[0].state = obj.inPoints[0].state
        self.elements["petryDTrigger"] = lambda self: Element(
            self,
            [elContainer(QPointF(-2, -5), "0"),
             elContainer(QPointF(-2, 35), "1")],
            [elContainer(QPointF(30, -5), "2"),
             elContainer(QPointF(30, 35), "3")],
            "./res/toolbar/petrydtrigger.png",
            "petryDTrigger",
            petryDTrigger_TF
        )

        def petryAND_TF(obj):
            print("IN0 ", obj.inPoints[0].state)
            print("IN1 ", obj.inPoints[1].state)
            print(obj.inPoints[0].state and obj.inPoints[1].state)
            obj.outPoints[0].state = (
                obj.inPoints[0].state and obj.inPoints[1].state)
        self.elements["petryAND"] = lambda self: Element(
            self,
            [elContainer(QPointF(-2, -5), "4"),
             elContainer(QPointF(-2, 35), "5")],
            [elContainer(QPointF(30, 15), "6")],
            "./res/toolbar/petryand.png",
            "petryAND",
            petryAND_TF
        )

        def PNTF(obj):
            obj.outPoints[0].state = not obj.inPoints[0].state
        self.elements["petryNOT"] = lambda self: Element(
            self,
            [elContainer(QPointF(-2, 15), "7")],
            [elContainer(QPointF(30, 15), "8")],
            "./res/toolbar/petrynot.png",
            "petryNOT",
            PNTF
        )

        def PRTF(obj): obj.outPoints[0].state = obj.inPoints[0].state
        self.elements["petryResistor"] = lambda self: Element(
            self,
            [elContainer(QPointF(-15, -5), "9")],
            [elContainer(QPointF(45, -5), "10")],
            "./res/toolbar/petryresistor.png",
            "petryResistor",
            PRTF
        )
        self.elements["petryIn"] = lambda self: Source(
            self,
            [],
            [elContainer(QPointF(45, 15), "0")],
            "./res/toolbar/circleIn.png",
            "petryIn"
        )
        self.elements["petryOut"] = lambda self: Element(
            self,
            [elContainer(QPointF(-10, 15), "0")],
            [],
            "./res/toolbar/circleOut.png",
            "petryOut",
            lambda self: print(self.name)
        )

    def connectElements(self, connectionPoint1, connectionPoint2):
        self.addLine(QLineF(connectionPoint1.scenePos() + QPoint(15,
                     15), connectionPoint2.scenePos() + QPoint(15, 15)))

        connectionPoint1.connections.append(connectionPoint2)
        connectionPoint2.connections.append(connectionPoint1)

        history.currentAction = None
        history.currentActionsData = None

    def delete(self):
        if history.currentAction is not "selectElement":
            print("element not selected")
            return
        else:
            if history.currentActionsData in self.items():
                history.currentActionsData.scene().removeItem(history.currentActionsData)

                history.currentAction = None
                history.currentActionsData = None
            else:
                print("another scene")
                return

    def flip():
        print("flip")
        if history.currentAction is not "selectElement":
            print("element not selected")
            return

    def rotate():
        print("rotate")
        if history.currentAction is not "selectElement":
            print("element not selected")
            return
        else:
            print(history.currentActionsData)

    def startCreateElementAction(self, element):
        print("startCreateElementAction: ", element)
        history.currentAction = "createElement"
        history.currentActionsData = element

    def build(self):
        print("build")
        self.clear()
        swithTo = {
            'Source': 'petryIn',
            'Output':  'petryOut',
            'Resistor':  'petryResistor',
            'AND':  'petryAND',
            'NOT':  'petryNOT',
            'DTrigger':  'petryDTrigger',
            'RSTrigger': 'petryRSTrigger'
        }

        bindMap = {}

        for item in self.schemsArea.items():
            if isinstance(item, Element):
                transfItem = self.elements[swithTo[item.name]](self)
                transfItem.setPos(item.pos())
                self.addItem(transfItem)
                bindMap[item] = transfItem

        def switchPoints(container, point):
            for el in container.childItems():
                if el.name is point.name:
                    return el.scenePos()

        def switchPointsPtr(container, point):
            for el in container.childItems():
                if el.name is point.name:
                    return el

        for oldItem, transfItem in bindMap.items():
            for conPoint in oldItem.childItems():
                startPoint = switchPointsPtr(transfItem, conPoint)

                endPoints = []
                for connect in conPoint.connections:
                    tmp = switchPointsPtr(bindMap[connect.parentItem()],connect)
                    endPoints.append(tmp)

                for point in endPoints:
                    startPoint.connections.append(point)
                    point.connections.append(startPoint)

        for oldItem, transfItem in bindMap.items():
            for conPoint in oldItem.childItems():
                startLinePos = switchPoints(transfItem, conPoint)

                endLinePoss = []
                for connect in conPoint.connections:
                    tmp = switchPoints(bindMap[connect.parentItem()],connect)
                    endLinePoss.append(tmp)

                for pos in endLinePoss:
                    self.addLine(QLineF(startLinePos+QPoint(15,15), pos+QPoint(15,15)))

        history.currentAction = None

    def nextStep(self):
        print("nextStep")

        def findSS(parent, queue2):
            for elem in list(queue2.queue):
                if elem is parent:
                    return True
            return False

        sources = []
        for item in self.items():
            if isinstance(item,Element) and item.name is "petryIn":
                sources.append(item)

        print("sources: ", sources)
        queue2 = Queue()
        for source in sources:
            for point in source.childItems():
                for con in point.connections:
                    con.state = source.outPoints[0]
                    parent = con.parentItem()
                    if not findSS(parent, queue2):
                        print("ADD ITEM")
                        queue2.put(parent)

        print("queue2.empty()",queue2.empty())

        while not queue2.empty():
            tmp = queue2.get()
            print("Call processingFunc from:",tmp.name)
            tmp.processingFunc(tmp)
            for point in tmp.outPoints:
                for point2 in point.connections:
                    point2.state = point.state
                    parent = point2.parentItem()
                    if not findSS(parent, queue2):
                        queue2.put(parent)

        self.update()

class History:
    currentAction = None
    currentActionsData = None
    serfActionsCursor = None

    actionsHistory = []

    class elContainer:
        def __init__(self, undo=None, data=None):
            self.data = data
            self.undo = undo
    actions = {
        "createElement": None,
        "deleteElement": None,
        "moveElement": None,
        "bindElement": None,
        "flipElement": None,
        "rotateElement": None,
        "loadFileElement": None,
        "selectElement": None,
    }

    def undo():
        actionsHistory[-1]
        if not serfActionsCursor:
            pass
            # TODO отключение кнопки undo

    def redo():
        print("action redo")
        serfActionsCursor = serfActionsCursor + 1
        if serfActionsCursor:
            pass
            # TODO отключение кнопки redo


global history
history = History()


class App(QMainWindow):
    def __init__(self, parent=None):
        super(App, self).__init__(parent)
        # TODO Debug
        # self.setStyleSheet("background-color: rgb(255,0,0);\
        #                     margin:5px;\
        #                     border:1px solid rgb(0, 255, 0);")

        self.title = ""
        self.width = 500
        self.height = 500

        class elContainer:
            def __init__(self, img, action=None):
                self.img = img
                self.action = action

        # TOP menu actirons
        elementsVars = {"area":None}#TODO костыль
        Elements = OrderedDict([
            # ("Save Scheme", elContainer("./res/toolbar/save.png",
            #                             lambda: QFileDialog.getSaveFileName(self, 'Save file', '/home')[0])),
            # ("Load Scheme", elContainer("./res/toolbar/load.png",
            #                             lambda: QFileDialog.getOpenFileName(self, 'Open file', '/home')[0])),
            # ("Undo",        elContainer("./res/toolbar/undo.png",
            #                             history.undo)),
            # ("Redo",        elContainer("./res/toolbar/redo.png",
            #                             history.redo)),
            ("Delete",     elContainer("./res/toolbar/delete.png",
                                       lambda: elementsVars["area"].delete())),
            # TODO Release version
            # ("Rotate",      elContainer("./res/toolbar/rotate.png",
            #                             EditingArea.rotate)),
            ("Input",        elContainer("./res/toolbar/input.png",
                                        lambda: elementsVars["area"].startCreateElementAction("Source"))),
            ("Output",        elContainer("./res/toolbar/output.png",
                                        lambda: elementsVars["area"].startCreateElementAction("Output"))),

            ("DTrigger",    elContainer("./res/toolbar/dtrigger.png",
                                        lambda: elementsVars["area"].startCreateElementAction("DTrigger"))),
            ("RSTrigger",    elContainer("./res/toolbar/rs.png",
                                        lambda: elementsVars["area"].startCreateElementAction("RSTrigger"))),
            ("AND",         elContainer("./res/toolbar/and.png",
                                        lambda: elementsVars["area"].startCreateElementAction("AND"))),
            ("NOT",         elContainer("./res/toolbar/not.png",
                                        lambda: elementsVars["area"].startCreateElementAction("NOT"))),
            ("Resistor",    elContainer("./res/toolbar/resistor.png",
                                        lambda: elementsVars["area"].startCreateElementAction("Resistor")))
        ])

        petrysVars = {"area":None}
        petryAction = OrderedDict([
            # ("Save Graph",  elContainer("./res/toolbar/save.png",
            #                             lambda: QFileDialog.getSaveFileName(self, 'Save file', '/home')[0])),
            # ("Load Graph",  elContainer("./res/toolbar/load.png",
            #                             lambda: QFileDialog.getOpenFileName(self, 'Open file', '/home')[0])),
            ("Build",       elContainer(
                "./res/toolbar/build.png", lambda: petrysVars["area"].build())),
            ("Next Step", elContainer("./res/toolbar/next.png", lambda: petrysVars["area"].nextStep())),
            # ("Undo",        elContainer("./res/toolbar/undo.png",     History.undo)),
            # ("Redo",        elContainer("./res/toolbar/redo.png",     History.redo)),
            ("DTrigger",    elContainer("./res/toolbar/petrydtrigger.png",
                                        lambda: elementsVars["area"].startCreateElementAction("petryDTrigger"))),
            ("RSTrigger",    elContainer("./res/toolbar/petryrstrigger.png",
                                        lambda: elementsVars["area"].startCreateElementAction("petryRSTrigger"))),
            ("AND",         elContainer("./res/toolbar/petryand.png",
                                        lambda: elementsVars["area"].startCreateElementAction("petryAND"))),
            ("NOT",         elContainer("./res/toolbar/petrynot.png",
                                        lambda: elementsVars["area"].startCreateElementAction("petryNOT"))),
            ("Resistor",    elContainer("./res/toolbar/petryresistor.png",
                                        lambda: elementsVars["area"].startCreateElementAction("petryResistor")))
        ])

        schemsArea = self.createEditingArea("Schemes Editor", Elements, elementsVars)
        graphsArea = self.createEditingArea("Graphs Editor", petryAction, petrysVars)

        graphsArea.schemsArea = schemsArea

        self.setWindowTitle(self.title)
        self.resize(self.width, self.height)
        self.show()

    def createEditingArea(self, areaName, menuElements, bindArray):
        self.docWid = QDockWidget(areaName, self)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.docWid)
        self.contents = QWidget(self)
        layout = QVBoxLayout(self.contents)
        self.docWid.setWidget(self.contents)

        self.menu(self.addToolBar('Elements'),
                  menuElements, self.contents.layout())

        self.scene = EditingArea()
        self.view = QGraphicsView(self.scene)
        layout.addWidget(self.view)

        bindArray["area"] = self.scene
        return self.scene

    def menu(self, toolbar, elements, layout):
        for key, value in elements.items():
            tmp = QAction(QIcon(value.img), key, self)
            tmp.triggered.connect(value.action)
            toolbar.addAction(tmp)
        layout.addWidget(toolbar)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
