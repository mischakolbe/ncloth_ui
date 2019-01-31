"""

"""
from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets


class NodePlayGround(QtWidgets.QMainWindow):
    DOCK_OPTIONS = QtWidgets.QMainWindow.AnimatedDocks
    DOCK_OPTIONS |= QtWidgets.QMainWindow.AllowNestedDocks
    DOCK_OPTIONS |= QtWidgets.QMainWindow.AllowTabbedDocks

    def __init__(self, *args, **kwargs):
        """

        """
        super(NodePlayGround, self).__init__(*args, **kwargs)

        # Indicate this is a Widget, not a MainWindow
        self.setWindowFlags(QtCore.Qt.Widget)

        # Define how DockWidgets behave
        self.setDockOptions(self.DOCK_OPTIONS)
        # Set the tabs of the DockWidgets to the top (are at the bottom by default)
        self.setTabPosition(
            QtCore.Qt.RightDockWidgetArea,
            QtWidgets.QTabWidget.North
        )


class MDockWidget(QtWidgets.QDockWidget):
    def __init__(self, double_click_event_function, *args, **kwargs):
        """

        """
        super(MDockWidget, self).__init__(*args, **kwargs)

        self.mobj = None
        self.double_click_event_function = double_click_event_function
        self.installEventFilter(self)

    # def eventFilter(self, obj, event):

    #     if event.type() == QtCore.QEvent.Wheel:
    #         print("HERE! IMPLEMENT THIS EVENT FILTER BETTER! MOUSE WHEEL IS NOT VERY NICE!")
    #         self.double_click_event_function(self)
    #         return True

    #     super(MDockWidget, self).eventFilter(obj, event)

    def mouseDoubleClickEvent(self, event):
        pass

    def set_mobj(self, mobj):
        self.mobj = mobj
