from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets

from ..lib import MUtil
reload(MUtil)


class MStandardItemModel(QtGui.QStandardItemModel):
    itemDataChanged = QtCore.Signal(object, object, object, object)


class MStandardItem(QtGui.QStandardItem):
    """
    Standard item to populate the NDynamicOutliner with
    """

    def __init__(self, *args, **kwargs):
        super(MStandardItem, self).__init__(*args, **kwargs)

        self.mobj = None

    def set_mobj(self, mobj):
        self.mobj = mobj

    def setData(self, new_value, role=QtCore.Qt.UserRole + 1):
        """
        Expanding this method to reflect item renaming in Maya
        """
        # Catch renaming case
        if role == QtCore.Qt.EditRole:
            old_value = self.data(role)
            QtGui.QStandardItem.setData(self, new_value, role)
            model = self.model()
            # Only emit signal if new_value is different from old
            if model is not None and old_value != new_value:
                MUtil._rename_mobj(self.mobj, new_value)
                model.itemDataChanged.emit(self, old_value, new_value, role)

            # Make sure changes are noticed by UI
            QtGui.QStandardItem.emitDataChanged(self)
            return True

        # Catch any other setData cases
        QtGui.QStandardItem.setData(self, new_value, role)
