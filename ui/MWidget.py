"""

"""

from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets


class MainWidget(QtWidgets.QWidget):
    """
    The main widget that provides the 3 core areas: Outliner, Playground and Buttons
    """
    def __init__(self, top_left_widget, bot_left_widget=None, right_widget=None, *args, **kwargs):
        super(MainWidget, self).__init__(*args, **kwargs)

        self.top_left_widget = top_left_widget
        self.bot_left_widget = bot_left_widget
        self.right_widget = right_widget

        self._init_main_widget()

    def _init_main_widget(self):
        self.setContentsMargins(0, 0, 0, 0)

        main_layout = QtWidgets.QHBoxLayout(self)

        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Widget that should be added to main main_layout layout
        top_widget = self.top_left_widget

        if self.bot_left_widget is not None:
            self.left_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
            self.left_splitter.addWidget(self.top_left_widget)
            self.left_splitter.addWidget(self.bot_left_widget)

            # Make the upper part of the splitter not stretch
            self.left_splitter.setStretchFactor(0, 0)
            # All stretching happens on the lower part
            self.left_splitter.setStretchFactor(1, 1)

            top_widget = self.left_splitter

        if self.right_widget is not None:
            self.main_splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
            self.main_splitter.addWidget(top_widget)
            self.main_splitter.addWidget(self.right_widget)

            # Make the left part of the splitter not stretch
            self.main_splitter.setStretchFactor(0, 0)
            # All stretching happens on the right side
            self.main_splitter.setStretchFactor(1, 1)
            # Make the left part of the splitter as narrow as possible
            # self.main_splitter.moveSplitter(150, 0)

            top_widget = self.main_splitter

        main_layout.addWidget(top_widget)
