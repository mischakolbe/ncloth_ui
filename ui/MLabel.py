"""

"""
from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets

import MTool
reload(MTool)
from ..lib import MGlobals
reload(MGlobals)


class AttrLabel(QtWidgets.QLabel):

    def __init__(
            self,
            *args,
            **kwargs
    ):
        super(AttrLabel, self).__init__(*args, **kwargs)

        # Create label
        self.setSizePolicy(MTool.FixedHeightPolicy())
        self.setMinimumSize(QtCore.QSize(MGlobals.attr_label_width, 0))
