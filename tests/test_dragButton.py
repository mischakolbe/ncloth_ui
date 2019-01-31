from PySide import QtCore
from PySide import QtGui

from shiboken import wrapInstance

from maya import cmds
import maya.OpenMayaUI as omui
from ui import widgets
reload(widgets)


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)


class DragButton(QtGui.QPushButton):

    def mousePressEvent(self, event):
        self.__mousePressPos = None
        self.__mouseMovePos = None
        print event.globalPos() # Global as in display-pixel!
        if event.button() == QtCore.Qt.LeftButton:
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()

        super(DragButton, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            # adjust offset from clicked point to origin of widget
            currPos = self.mapToGlobal(self.pos())
            globalPos = event.globalPos()
            diff = globalPos - self.__mouseMovePos
            newPos = self.mapFromGlobal(currPos + diff)
            self.move(newPos)

            self.__mouseMovePos = globalPos

        super(DragButton, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.__mousePressPos is not None:
            moved = event.globalPos() - self.__mousePressPos
            if moved.manhattanLength() > 3:
                event.ignore()
                return
            else:
                mouse_realase_pos = event.globalPos()
                print mouse_realase_pos
                if self.__mousePressPos.x > mouse_realase_pos.x:
                    print "OPTION A"
                else:
                    print "OPTION B"

        super(DragButton, self).mouseReleaseEvent(event)


class TestUI(QtGui.QMainWindow):

    def __init__(self, parent=maya_main_window(), *args, **kwargs):
        super(TestUI, self).__init__(parent, *args, **kwargs)

        self.create_ui()

    def create_ui(self):
        """
        Create the UI
        """
        self.setWindowTitle("TestUI")
        self.setMinimumWidth(300)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)

        self.central_widget = QtGui.QWidget()
        self.central_widget.setObjectName("central_widget")
        self.setCentralWidget(self.central_widget)

        # Create main layout. Everything goes within this main layout within the central widget
        self.central_layout = QtGui.QVBoxLayout(self.central_widget)
        self.setLayout(self.central_layout)
        self.central_layout.setAlignment(QtCore.Qt.AlignTop)
        self.central_layout.setSpacing(0)
        self.central_layout.setContentsMargins(0, 0, 0, 0)
        self.central_layout.setObjectName("central_layout")
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        # Add widgets to central_layout
        # self.menu_box = QtGui.QPushButton("N")
        # self.menu_box.pressed.connect(lambda: self.buttonClick(self.menu_box))

        self.menu_box = DragButton("Drag")
        self.menu_box.clicked.connect(self.do_magic)

        # Add to central layout
        self.central_layout.addWidget(self.menu_box)

    def buttonClick(self, button):
        print button.pos()
        print button.height()

        self.option_a = QtGui.QPushButton("A")
        self.central_layout.addWidget(self.option_a)
        self.option_a.released.connect(self.do_magic)

    def do_magic(self):
        print "ASS"

def testDef():

    ui = TestUI()
    ui.show()


testDef()
