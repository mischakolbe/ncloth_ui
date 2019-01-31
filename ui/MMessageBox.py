"""

"""

from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets

import MTool
reload(MTool)

class AboutNClothUiMessageBox(QtWidgets.QMessageBox):
    def __init__(self, *args, **kwargs):
        super(AboutNClothUiMessageBox, self).__init__(*args, **kwargs)

        msg_box_title = "THIS IS GREAT"
        msg_box_content = "IS IT NOT?!"

        MTool.center_to_screen(self)

        # This is effectively the function call(!) All initialization should
        # happen before this point!
        self.about(self, msg_box_title, msg_box_content)
