from random import randint

from PySide import QtCore
from PySide import QtGui

from shiboken import wrapInstance

from maya import cmds
import maya.OpenMayaUI as omui
from ..ui import MDockWidget
reload(MDockWidget)


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)


# Set to False - Standard docking of widgets around the main content area
# Set to True - Sub MainWindows each with their own private docking
DO_SUB_DOCK_CREATION = True


_DOCK_OPTS = QtGui.QMainWindow.AnimatedDocks
_DOCK_OPTS |= QtGui.QMainWindow.AllowNestedDocks
_DOCK_OPTS |= QtGui.QMainWindow.AllowTabbedDocks

_DOCK_COUNT = 0
_DOCK_POSITIONS = (
    QtCore.Qt.LeftDockWidgetArea,
    QtCore.Qt.TopDockWidgetArea,
    QtCore.Qt.RightDockWidgetArea,
    QtCore.Qt.BottomDockWidgetArea
)


def main():
    mainWindow = QtGui.QMainWindow(parent=maya_main_window())
    mainWindow.resize(1024,768)
    mainWindow.setDockOptions(_DOCK_OPTS)

    widget = QtGui.QLabel("MAIN APP CONTENT AREA")
    widget.setMinimumSize(300,200)
    widget.setFrameStyle(widget.Box)
    mainWindow.setCentralWidget(widget)

    addDocks(mainWindow, "Main Dock")

    mainWindow.show()
    mainWindow.raise_()

    return mainWindow


def addDocks(window, name, subDocks=True):
    global _DOCK_COUNT

    for pos in _DOCK_POSITIONS:

        for _ in xrange(2):
            _DOCK_COUNT += 1

            sub = QtGui.QMainWindow()
            sub.setWindowFlags(QtCore.Qt.Widget)
            sub.setDockOptions(_DOCK_OPTS)

            color = tuple(randint(20, 230) for _ in xrange(3))

            label = QtGui.QLabel("%s %d content area" % (name, _DOCK_COUNT), sub)
            label.setMinimumHeight(25)
            label.setStyleSheet("background-color: rgb(%d, %d, %d)" % color)
            sub.setCentralWidget(label)

            dock = QtGui.QDockWidget("%s %d title bar" % (name, _DOCK_COUNT))
            dock.setWidget(sub)

            if DO_SUB_DOCK_CREATION and subDocks:
                addDocks(sub, "Sub Dock", subDocks=False)

            window.addDockWidget(pos, dock)


def launch_ui():

    # ui = TestUI()
    # ui.show()
    main()
