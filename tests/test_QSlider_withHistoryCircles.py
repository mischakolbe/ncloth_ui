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


class TestSlider(QtGui.QWidget):

    brightest_color = (0, 156, 255)
    darkest_color = (24, 90, 150)
    min_circle_dia = 1
    max_circle_dia = 3
    max_num_circles = 3

    def __init__(self, orientation=QtCore.Qt.Horizontal, *args, **kwargs):
        super(TestSlider, self).__init__(*args, **kwargs)
        # self.setSpacing(0)
        self.setContentsMargins(0, 0, 0, 0)

        self.slider = QtGui.QSlider()
        self.slider.setOrientation(orientation)

        layout = QtGui.QFormLayout()
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.slider)
        self.setLayout(layout)

        self.slider.sliderReleased.connect(self.update_circle_percentages)
        self.slider.valueChanged.connect(self.slider_changed)

        self.circle_percentages = [self.slider.value()]

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        pen = QtGui.QPen(QtGui.QColor(255, 255, 255), 1)

        for i, circle_percentage in enumerate(self.circle_percentages[:-1]):

            rate = (i+1) / float(len(self.circle_percentages)-1)

            color = [d+(b-d)*rate for d, b in zip(self.darkest_color, self.brightest_color)]

            pen.setColor(QtGui.QColor(*color))
            painter.setPen(pen)
            dia = self.min_circle_dia + (self.max_circle_dia - self.min_circle_dia)*rate

            # Define min and max pixel values of slider. values 5 and 4 empirically determined
            min_slider_pos = 5
            max_slider_pos = self.slider.size().width() - 4
            # Determine x-position of circle
            pos = circle_percentage * (max_slider_pos-min_slider_pos) + min_slider_pos

            painter.drawEllipse(QtCore.QPoint(pos, self.slider.height()), dia, dia)

    def slider_changed(self):
        # Force a repaint of the widget to make sure paintEvent is up to date
        self.update()

    def update_circle_percentages(self):
        """
        """

        # Add the current slider percentage (how close it is to the max)
        slider_percentage = self.slider.value() / float(self.slider.maximum())
        # Append the new percentage and ...
        self.circle_percentages.append(slider_percentage)
        # ... if the list is longer than max_num_circles...
        # (+1 because list must store current percentage as well, which does not get a circle)
        if len(self.circle_percentages) > self.max_num_circles + 1:
            # ... drop the currently first entry
            self.circle_percentages.pop(0)

        self.update()



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
        self.central_layout.setObjectName("central_layout")
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        self.test_widget = TestSlider()

        # Add to central layout
        self.central_layout.addWidget(self.test_widget)


def launch_ui():

    ui = TestUI()
    ui.show()
