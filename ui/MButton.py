"""

"""

from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets

import MTool
reload(MTool)
import MIcon
reload(MIcon)
from ..lib import MGlobals
reload(MGlobals)


class ShyButton(QtWidgets.QToolButton):
    def __init__(self, *args, **kwargs):
        super(ShyButton, self).__init__(*args, **kwargs)

        # Remove weird background once button was clicked once
        self.setStyleSheet("background-color: rgba(255, 255, 255, 0);")

        self.shy_state = False
        self.shy_states = [MIcon.MIcon("visible"), MIcon.MIcon("shy")]

        shy_button_size = 12
        self.setIcon(self.shy_states[self.shy_state])
        self.setIconSize(QtCore.QSize(shy_button_size, shy_button_size))
        self.setFixedSize(shy_button_size, shy_button_size)
        self.setSizePolicy(MTool.FixedHeightPolicy())
        self.setObjectName("shy_switch")
        self.clicked.connect(self.switch_shy_switch)

        self.setContentsMargins(0, 0, 0, 0)

    def switch_shy_switch(self):
        self.shy_state = not self.shy_state

        self.setIcon(self.shy_states[self.shy_state])


class MColorButton(QtWidgets.QPushButton):
    '''

    '''
    def __init__(self, *args, **kwargs):
        super(MColorButton, self).__init__(*args, **kwargs)
        self._color = QtGui.QColor(255, 231, 0)
        self.update_button_color()
        self.clicked.connect(self.open_color_picker)

        self.setMaximumHeight(MGlobals.attribute_box_height)
        self.setContentsMargins(0, 0, 0, 0)

    def update_button_color(self):
        self.setStyleSheet("background-color: {};".format(self._color.name()))

    def color(self):
        return self._color

    def open_color_picker(self):
        '''
        Show color-picker dialog to select color.
        Qt will use the native dialog by default.
        '''
        new_color = QtWidgets.QColorDialog.getColor(self._color)
        # Don't update if the user cancels the dialogue: returns an empty color
        if new_color.isValid():
            self._color = new_color
            self.update_button_color()
