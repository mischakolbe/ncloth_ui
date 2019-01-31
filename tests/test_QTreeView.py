from PySide import QtCore
from PySide import QtGui

from shiboken import wrapInstance

from maya import cmds
import maya.OpenMayaUI as omui

from ..ui import MAttributeHolder
reload(MAttributeHolder)
from ..ui import MButton
reload(MButton)


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)


#-------------------------------------------------------------------------------
# my test data
class MyData():
    def __init__(self, txt, parent=None):
        self.txt = txt
        self.parent = parent
        self.child = []
        self.icon = None
        self.index = None

    #---------------------------------------------------------------------------
    def position(self):
        position = 0
        if self.parent is not None:
            count = 0
            children = self.parent.child
            for child in children:
                if child == self:
                    position = count
                    break
                count += 1
        return position

    #---------------------------------------------------------------------------
    # test initialization
    @staticmethod
    def init():
        root = MyData("root")
        for i in range(0, 2):
            child1 = MyData("child %i" % (i), root)
            root.child.append(child1)
            for x in range(0, 2):
                child2 = MyData("child %i %i" % (i, x), child1)
                child1.child.append(child2)

        return root


#-------------------------------------------------------------------------------
class TreeModel(QtCore.QAbstractItemModel):

    #---------------------------------------------------------------------------
    def __init__(self, tree):
        super(TreeModel, self).__init__()
        self.__tree = tree
        self.__current = tree

    #---------------------------------------------------------------------------
    def flags(self, index):
        flag = QtCore.Qt.ItemIsEnabled
        if index.isValid():
            flag |= QtCore.Qt.ItemIsSelectable \
                 | QtCore.Qt.ItemIsUserCheckable \
                 | QtCore.Qt.ItemIsEditable \
                 | QtCore.Qt.ItemIsDragEnabled \
                 | QtCore.Qt.ItemIsDropEnabled
        return flag

    #---------------------------------------------------------------------------
    def index(self, row, column, parent=QtCore.QModelIndex()):
        node = QtCore.QModelIndex()
        if parent.isValid():
            nodeS = parent.internalPointer()
            nodeX = nodeS.child[row]
            node = self.__createIndex(row, column, nodeX)
        else:
            node = self.__createIndex(row, column, self.__tree)
        return node

    #---------------------------------------------------------------------------
    def parent(self, index):
        node = QtCore.QModelIndex()
        if index.isValid():
            nodeS = index.internalPointer()
            parent = nodeS.parent
            if parent is not None:
                node = self.__createIndex(parent.position(), 0, parent)
        return node

    #---------------------------------------------------------------------------
    def rowCount(self, index=QtCore.QModelIndex()):
        count = 1
        node = index.internalPointer()
        if node is not None:
            count = len(node.child)
        return count

    #---------------------------------------------------------------------------
    def columnCount(self, index=QtCore.QModelIndex()):
        return 1

    #---------------------------------------------------------------------------
    def data(self, index, role=QtCore.Qt.DisplayRole):
        data = None
        if role == QtCore.Qt.DisplayRole or role == QtCore.Qt.EditRole:
            node = index.internalPointer()
            data = node.txt

        if role == QtCore.Qt.ToolTipRole:
            node = index.internalPointer()
            data = "ToolTip " + node.txt

        if role == QtCore.Qt.DecorationRole:
            data = QtGui.QIcon("icon.png")
        return data

    #---------------------------------------------------------------------------
    def setData(self, index, value, role=QtCore.Qt.DisplayRole):
        result = True
        if role == QtCore.Qt.EditRole and value != "":
            node = index.internalPointer()
            node.text = value
            result = True
        return result

    #---------------------------------------------------------------------------
    def __createIndex(self, row, column, node):
        if node.index == None:
            index = self.createIndex(row, column, node)
            node.index = index
            icon = QtGui.QIcon("icon.png")
            b = self.setData(index, icon, QtCore.Qt.DecorationRole)
            b = self.setData(index, "ToolTip "+node.txt, QtCore.Qt.ToolTipRole)
        return node.index



#-------------------------------------------------------------------------------
class TreeView(QtGui.QTreeView):
    #---------------------------------------------------------------------------
    def __init__(self, model, parent=None):
        super(TreeView, self).__init__(parent)
        self.__model = model
        self.setModel(model)


        self.setCurrentIndex(self.__model.index(0, 0))
        return




#-------------------------------------------------------------------------------
class MyTree(QtGui.QMainWindow):
    def __init__(self, parent=maya_main_window()):
        super(MyTree, self).__init__(parent)

        data = MyData.init()
        treeModel = TreeModel(data)
        treeView = TreeView(treeModel)

        self.setCentralWidget(treeView)


class AttrTree(QtGui.QTreeView):
    def __init__(self, num_rows, num_columns, *args, **kwargs):
        super(AttrTree, self).__init__(*args, **kwargs)

        # row can be 0 even when it's more than 0.
        self._datamodel = QtGui.QStandardItemModel(num_rows, num_columns)
        # if row_labels:
        #     self._datamodel.setHorizontalHeaderLabels(row_labels)
        self.setModel(self._datamodel)
        self.setHeaderHidden(True)
        # self.setUniformRowHeights(True)

        ''' Useful snippets
        # expand container
        index = model.indexFromItem(parent1)
        view.expand(index)
        # select row
        index2 = model.indexFromItem(child3)
        selmod = view.selectionModel()
        selmod.select(index2, QtGui.QItemSelectionModel.Select|QtGui.QItemSelectionModel.Rows)
        '''

    def _append_row_widgets(self, parent=None, custom_widgets=None):
        if parent is None:
            row_index = self._datamodel.rowCount()
        elif type(parent) is QtGui.QStandardItem:
            row_index = parent.rowCount()
        else:
            print "parent:", parent
            print "type(parent):", type(parent)

        new_row = self._add_row_widgets(
            parent=parent,
            row_index=row_index,
            custom_widgets=custom_widgets,
        )

        return new_row

    def _add_row_widgets(self, parent=None, row_index=0, custom_widgets=None):
        if parent is None:
            return self._add_top_item(row_index, custom_widgets)
        else:
            return self._add_sub_item(parent, row_index, custom_widgets)

    def _add_top_item(self, row_index=0, custom_widgets=None):
        item_toplevel = QtGui.QStandardItem('{}th item'.format(row_index))
        self._datamodel.setItem(row_index, 0, item_toplevel)

        widget_toplevel = QtGui.QLabel("Lalala {}".format(row_index))
        qindex_toplevel = self._datamodel.index(row_index, 1, QtCore.QModelIndex())
        self.setIndexWidget(qindex_toplevel, widget_toplevel)
        return item_toplevel

    def _add_sub_item(self, parent=None, row_index=0, custom_widgets=None):
        item_children = []
        if custom_widgets is None:
            custom_widgets = []

        for i, custom_widget in enumerate(custom_widgets):
            item_str = ""
            if isinstance(custom_widget, basestring):
                item_str = custom_widget
            item_child = QtGui.QStandardItem(item_str)
            item_children.append(item_child)

        parent.insertRow(row_index, item_children)

        # Seems to need this extra loop, otherwise instertRow gets confused...?
        for item_child, custom_widget in zip(item_children, custom_widgets):
            if custom_widget is None or isinstance(custom_widget, basestring):
                continue
            qindex_child = item_child.index()
            self.setIndexWidget(qindex_child, custom_widget)

        return item_children


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

        self.test_tree = AttrTree(0, 1)

        for i in range(4):
            item_toplevel = self.test_tree._append_row_widgets()
            print item_toplevel
            sub_item = self.test_tree._append_row_widgets(item_toplevel, [MAttributeHolder.AttributeBox("ASS")])
            sub_sub_item = self.test_tree._append_row_widgets(sub_item[0], [MAttributeHolder.AttributeBox("ASS_sub")])
            self.test_tree._append_row_widgets(sub_sub_item[0], [MAttributeHolder.AttributeBox("ASS_sub_sub")])


        self.central_layout.addWidget(self.test_tree)


def launch_ui():
    # my_data = MyData.init()

    # print my_data
    # print my_data.parent
    # print my_data.index

    ui = TestUI()
    ui.show()
