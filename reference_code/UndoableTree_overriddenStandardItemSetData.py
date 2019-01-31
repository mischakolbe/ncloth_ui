# -*- coding: utf-8 -*-

from PySide import QtGui, QtCore
import sys

class CommandTextEdit(QtGui.QUndoCommand):
    def __init__(self, tree, item, oldText, newText, description):
        QtGui.QUndoCommand.__init__(self, description)
        self.item = item
        self.tree = tree
        self.oldText = oldText
        self.newText = newText

    def redo(self):
        self.item.model().itemDataChanged.disconnect(self.tree.itemDataChangedSlot)
        self.item.setText(self.newText)
        self.item.model().itemDataChanged.connect(self.tree.itemDataChangedSlot)

    def undo(self):
        self.item.model().itemDataChanged.disconnect(self.tree.itemDataChangedSlot)
        self.item.setText(self.oldText)
        self.item.model().itemDataChanged.connect(self.tree.itemDataChangedSlot)


class CommandCheckStateChange(QtGui.QUndoCommand):
    def __init__(self, tree, item, oldCheckState, newCheckState, description):
        QtGui.QUndoCommand.__init__(self, description)
        self.item = item
        self.tree = tree
        self.oldCheckState = QtCore.Qt.Unchecked if oldCheckState == 0 else QtCore.Qt.Checked
        self.newCheckState = QtCore.Qt.Checked if oldCheckState == 0 else QtCore.Qt.Unchecked

    def redo(self): #disoconnect to avoid recursive loop b/w signal-slot
        self.item.model().itemDataChanged.disconnect(self.tree.itemDataChangedSlot)
        self.item.setCheckState(self.newCheckState)
        self.item.model().itemDataChanged.connect(self.tree.itemDataChangedSlot)

    def undo(self):
        self.item.model().itemDataChanged.disconnect(self.tree.itemDataChangedSlot)
        self.item.setCheckState(self.oldCheckState)
        self.item.model().itemDataChanged.connect(self.tree.itemDataChangedSlot)


class StandardItemModel(QtGui.QStandardItemModel):
    itemDataChanged = QtCore.Signal(object, object, object, object)


class StandardItem(QtGui.QStandardItem):
    def setData(self, newValue, role=QtCore.Qt.UserRole + 1):
        if role == QtCore.Qt.EditRole:
            oldValue = self.data(role)
            QtGui.QStandardItem.setData(self, newValue, role)
            model = self.model()
            #only emit signal if newvalue is different from old
            if model is not None and oldValue != newValue:
                model.itemDataChanged.emit(self, oldValue, newValue, role)
            return True
        if role == QtCore.Qt.CheckStateRole:
            oldValue = self.data(role)
            QtGui.QStandardItem.setData(self, newValue, role)
            model = self.model()
            if model is not None and oldValue != newValue:
                model.itemDataChanged.emit(self, oldValue, newValue, role)
            return True
        QtGui.QStandardItem.setData(self, newValue, role)


class UndoableTree(QtGui.QWidget):
    def __init__(self, parent = None):
        QtGui.QWidget.__init__(self, parent = None)
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose)
        self.view = QtGui.QTreeView()
        self.model = self.createModel()
        self.view.setModel(self.model)
        self.view.expandAll()
        self.undoStack = QtGui.QUndoStack(self)
        undoView = QtGui.QUndoView(self.undoStack)
        buttonLayout = self.buttonSetup()
        mainLayout = QtGui.QHBoxLayout(self)
        mainLayout.addWidget(undoView)
        mainLayout.addWidget(self.view)
        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)
        self.makeConnections()

    def makeConnections(self):
        self.model.itemDataChanged.connect(self.itemDataChangedSlot)
        self.quitButton.clicked.connect(self.close)
        self.undoButton.clicked.connect(self.undoStack.undo)
        self.redoButton.clicked.connect(self.undoStack.redo)

    def itemDataChangedSlot(self, item, oldValue, newValue, role):
        if role == QtCore.Qt.EditRole:
            command = CommandTextEdit(self, item, oldValue, newValue,
                "Text changed from '{0}' to '{1}'".format(oldValue, newValue))
            self.undoStack.push(command)
            return True
        if role == QtCore.Qt.CheckStateRole:
            command = CommandCheckStateChange(self, item, oldValue, newValue,
                "CheckState changed from '{0}' to '{1}'".format(oldValue, newValue))
            self.undoStack.push(command)
            return True

    def buttonSetup(self):
        self.undoButton = QtGui.QPushButton("Undo")
        self.redoButton = QtGui.QPushButton("Redo")
        self.quitButton = QtGui.QPushButton("Quit")
        buttonLayout = QtGui.QVBoxLayout()
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.undoButton)
        buttonLayout.addWidget(self.redoButton)
        buttonLayout.addStretch()
        buttonLayout.addWidget(self.quitButton)
        return buttonLayout

    def createModel(self):
        model = StandardItemModel()
        model.setHorizontalHeaderLabels(['Titles', 'Summaries'])
        rootItem = model.invisibleRootItem()
        item0 = [StandardItem('Title0'), StandardItem('Summary0')]
        item00 = [StandardItem('Title00'), StandardItem('Summary00')]
        item01 = [StandardItem('Title01'), StandardItem('Summary01')]
        item0[0].setCheckable(True)
        item00[0].setCheckable(True)
        item01[0].setCheckable(True)
        rootItem.appendRow(item0)
        item0[0].appendRow(item00)
        item0[0].appendRow(item01)
        return model


def main():
    app = QtGui.QApplication(sys.argv)
    newTree = UndoableTree()
    newTree.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
