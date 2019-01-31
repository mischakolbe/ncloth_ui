from Qt import QtCore
from Qt import QtGui
from Qt import QtWidgets

from maya import cmds

import MAttributeHolder
reload(MAttributeHolder)
import MButton
reload(MButton)
import MIcon
reload(MIcon)
from ..lib import MGlobals
reload(MGlobals)
from ..lib import MUtil
reload(MUtil)
from ..lib import callback
reload(callback)
import MStandardItem
reload(MStandardItem)


class MTreeView(QtWidgets.QTreeView):

    def find_item_by_name(self, name_to_find):
        """
        Find an MStandardItem by its text. This is potentially unreliable.
        Use find_item_by_mobj instead!
        """
        root = self.model().invisibleRootItem()
        for item in self.iter_items(root):
            if item.text() == name_to_find:
                return item

        # If no item was found: return None
        return None

    def find_item_by_mobj(self, mobj_to_find):
        """
        Find & return an MStandardItem by its mobj
        """
        root = self.model().invisibleRootItem()
        for item in self.iter_items(root):
            if item.mobj is mobj_to_find:
                return item

        # If no item was found: return None
        return None

    def find_item_by_mobj_with_path(self, mobj_to_find):
        """
        Find & return an MStandardItem by its mobj, using their long names
        """
        root = self.model().invisibleRootItem()
        for item in self.iter_items(root):
            if MUtil._get_long_name_of_mobj(item.mobj, full=True) == MUtil._get_long_name_of_mobj(mobj_to_find, full=True):
                return item

        # If no item was found: return None
        return None

    @staticmethod
    def iter_items(root):
        """
        Generator that yields the content of every found child of the given root
        """
        if root is not None:
            # Initiate the stack as simply the given root
            stack = [root]
            # As long as the stack is not empty: Continue
            while stack:
                # Remove the first item from the stack-list
                parent = stack.pop(0)
                # Find the number of rows and columns this parent holds
                for row in range(parent.rowCount()):
                    for column in range(parent.columnCount()):
                        # Yield every child found at the given row & column
                        child = parent.child(row, column)
                        yield child
                        # If the found child has children of its own: Add it to the iteration-stack!
                        if child.hasChildren():
                            stack.append(child)


class AttrTree(MTreeView):
    """
    Add right-click feature to color certain rows (to make it easy to find attrs you're working on)
    Try using something like this:
    self._datamodel.setData(self._datamodel.index(i, 3), QtGui.QBrush(QtCore.Qt.red), QtCore.Qt.BackgroundRole)

    """
    def __init__(self, node, num_rows=0, num_columns=1, *args, **kwargs):
        super(AttrTree, self).__init__(*args, **kwargs)

        self._datamodel = QtGui.QStandardItemModel(num_rows, num_columns)
        self.setModel(self._datamodel)
        self.setHeaderHidden(True)
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        # self.setUniformRowHeights(True)

        self.node = node

        ''' Useful snippets
        # expand container
        index = model.indexFromItem(parent1)
        view.expand(index)
        # select row
        index2 = model.indexFromItem(child3)
        selmod = view.selectionModel()
        selmod.select(index2, QtCore.QItemSelectionModel.Select|QtCore.QItemSelectionModel.Rows)
        '''

    def _append_widget_item(self, custom_widgets=None):
        new_row = self._add_widget_item(
            row_index=self._datamodel.rowCount(),
            custom_widgets=custom_widgets,
        )

        return new_row

    def _add_widget_item(self, row_index=0, custom_widgets=None):
        item_children = []
        if custom_widgets is None:
            custom_widgets = []
        if isinstance(custom_widgets, basestring):
            custom_widgets = [custom_widgets]

        for i, custom_widget in enumerate(custom_widgets):
            item_str = ""
            if isinstance(custom_widget, basestring):
                item_str = custom_widget
            new_top_item = QtGui.QStandardItem(item_str)
            self._datamodel.setItem(row_index, i, new_top_item)

            item_children.append(new_top_item)

        for item_child, custom_widget in zip(item_children, custom_widgets):
            if custom_widget is None or isinstance(custom_widget, basestring):
                continue

            qindex_toplevel = self._datamodel.index(row_index, 1, QtCore.QModelIndex())
            self.setIndexWidget(qindex_toplevel, custom_widget)

        return item_children

    def _append_widget_row(self, parent, custom_widgets=None):
        new_row = self._add_widget_row(
            parent=parent,
            row_index=parent.rowCount(),
            custom_widgets=custom_widgets,
        )

        return new_row

    def _add_widget_row(self, parent, row_index=0, custom_widgets=None):
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

    def find_attr_box_by_name(self, name_to_find):
        root = self.model().invisibleRootItem()
        for item in self.iter_items(root):
            index_widget = self.indexWidget(item.index())
            if index_widget:
                if index_widget.attr == name_to_find:
                    return index_widget


class NDynamicsOutliner(MTreeView):
    def __init__(self, *args, **kwargs):
        super(NDynamicsOutliner, self).__init__(*args, **kwargs)
        # Set basic attributes
        self.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)  # MultiSelection
        self.setUniformRowHeights(True)
        self.setHeaderHidden(True)

        # Create node_callback-list to keep track of installed callbacks
        self.outliner_node_callbacks = []

        # Create an empty model for the outliner's data and apply it to the QTreeView
        self._datamodel = MStandardItem.MStandardItemModel()
        self.setModel(self._datamodel)

        # Gather data from what nodes are present in scene
        self.ndynamic_mobj_inventory = self._get_ndynamic_mobjs_from_scene()

        # Fill the data model with the
        self.populate_data_model()

        # Select nodes that are selected in the Maya scene
        self.select_ncloth_outliner_items_from_scene_selection()

        self.expandAll()

        self._datamodel.itemChanged.connect(self.set_ndynamic_state_based_on_qt_check_state)

    def keyPressEvent(self, key_event):

        # Ctrl + A: Select all visible nodes in outliner
        if key_event.key() == QtCore.Qt.Key_A and key_event.modifiers() & QtCore.Qt.CTRL:
            self.selectAll()

    def refresh_ndynamic_mobj_inventory(self):
        self.ndynamic_mobj_inventory = self._get_ndynamic_mobjs_from_scene()
        self._datamodel.clear()
        self.populate_data_model()
        self.expandAll()

    def mobjs_from_inventory_value_based_on_type(self, value, node_type):
        # inventory_values = self.ndynamic_mobj_inventory.get(value, None)
        # if inventory_values is None:
        #     cmds.warning("The value {} does not exist in the ndynamic_mobj_inventory!".format(value))
        #     return False

        mobjs = value.get(node_type, None)
        if mobjs is None:
            cmds.warning("This node type does not exist! {}".format(node_type))

        return mobjs

    @property
    def selected_ncloth_outliner_standard_items(self):
        """
        Returns a list of MStandardItems
        """
        selected_outliner_item_indices = self.selectedIndexes()
        selected_outliner_items = []
        for index in selected_outliner_item_indices:
            selected_outliner_items.append(self._datamodel.itemFromIndex(index))
        return selected_outliner_items

    def get_ndynamic_qt_check_state(self, mobj):
        ncloth_node_type = MUtil._get_readable_node_type_of_mobj(mobj)
        if ncloth_node_type == "nucleus" or ncloth_node_type == "dynamicConstraint":
            value = MUtil._get_attr_of_mobj(mobj, "enable")
        else:
            value = MUtil._get_attr_of_mobj(mobj, "isDynamic")

        if value:
            return QtCore.Qt.Checked
        else:
            return QtCore.Qt.Unchecked

    def set_ndynamic_state_based_on_qt_check_state(self, item):
        mobj = item.mobj
        qt_check_state = item.checkState()

        if qt_check_state is QtCore.Qt.Checked:
            value = True
        else:
            value = False

        ncloth_node_type = MUtil._get_readable_node_type_of_mobj(mobj)
        if ncloth_node_type == "nucleus" or ncloth_node_type == "dynamicConstraint":
            value = MUtil._set_mobj_attribute(mobj, "enable", value)
        else:
            value = MUtil._set_mobj_attribute(mobj, "isDynamic", value)

    def populate_data_model(self):
        # _ is just the name of the nucleus but the mobj of that nucleus is stored
        # within ndynamics_of_nucleus!!!
        for _, ndynamics_of_nucleus in self.ndynamic_mobj_inventory.iteritems():

            # The nucleus is always the parent of all other nodes of the same ndynamics-system
            parent = None
            for i, ncloth_node_type in enumerate(MGlobals.ndynamic_node_types):
                mobjs = self.mobjs_from_inventory_value_based_on_type(ndynamics_of_nucleus, ncloth_node_type)

                for mobj in mobjs:
                    child = MStandardItem.MStandardItem()
                    child.setText(MUtil._get_name_of_mobj(mobj))
                    child.setIcon(MIcon.MIcon(ncloth_node_type))
                    child.setCheckable(True)
                    child.setCheckState(self.get_ndynamic_qt_check_state(mobj))
                    child.set_mobj(mobj)
                    self.install_outliner_item_rename_callback(mobj)

                    if ncloth_node_type == "nucleus":
                        # If this node is a nucleus: It should be a "parent" in the outliner
                        # All following child-nodes will be parented underneath this node
                        parent = child
                        self._datamodel.appendRow(parent)
                    else:
                        # Any other data type will be parented underneath the nucleus
                        parent.appendRow(child)

    def install_outliner_item_rename_callback(self, mobj):
        # Add specific callback type with its appropriate function to run when fired
        node_callback = callback.NodeNameChangedCallbackHandler(
            callback.node_rename_closure(self),
            mobj
        )
        node_callback.install()
        self.outliner_node_callbacks.append(node_callback)

    @staticmethod
    def _get_ndynamic_mobjs_from_scene():
        # Get all nucleus mobjs
        nucleus_mobjs = MUtil._get_all_mobjs_of_type(MGlobals.ndynamic_dependency_node_types[0])
        # mobj_lists holds list of mobjs of all: ncloth_nodes, nrigid_nodes, dynamic_constraint_nodes
        mobj_lists = [MUtil._get_all_mobjs_of_type(x) for x in MGlobals.ndynamic_dependency_node_types[1:]]

        # Find all nCloth, nRigid and dynamicConstraint mobjs for each nucleus
        ndynamic_mobj_inventory = {}
        for nucleus_mobj in nucleus_mobjs:
            nucleus_name = MUtil._get_name_of_mobj(nucleus_mobj)
            ndynamic_mobj_inventory[nucleus_name] = {
                "nucleus": [nucleus_mobj],
            }

            nucleus_node = MUtil._get_long_name_of_mobj(nucleus_mobj)
            history_nodes = cmds.listHistory(nucleus_node, allConnections=True)

            history_mobj_list = [MUtil._get_mobj_of_node(x) for x in history_nodes]

            for ncloth_node_type, mobj_list in zip(MGlobals.ndynamic_node_types[1:], mobj_lists):
                # Can't use sets with MObjects, therefore has to be a list comprehension
                mobjs_of_type_and_in_history = [x for x in mobj_list if x in history_mobj_list]

                ndynamic_mobj_inventory[nucleus_name][ncloth_node_type] = mobjs_of_type_and_in_history

        # Test inventory
        # ndynamic_mobj_inventory = {}
        # print ndynamic_mobj_inventory
        return ndynamic_mobj_inventory

    def select_ncloth_outliner_items_from_scene_selection(self):
        """
        Selects nodes in the nclothOutliner that are selected in the Maya scene
        """
        # Get the selection model of the TreeView and initiate an empty item selection
        selection_model = self.selectionModel()
        selection = QtCore.QItemSelection()

        # Go through all mobjs that are currently selected in the Maya scene
        for selected_mobj in MUtil._selected_nodes_in_scene_as_mobjs():
            # Try to match the selected mobj to any outliner item (using their long name)
            ncloth_outliner_item = self.find_item_by_mobj_with_path(selected_mobj)
            if ncloth_outliner_item is None:
                # If the mobj itself couldn't be found: try its shape!
                shape_mobj = MUtil._get_shape_mobj(selected_mobj)
                ncloth_outliner_item = self.find_item_by_mobj_with_path(shape_mobj)

            # If no outliner-item was matched: continue
            if ncloth_outliner_item is None:
                continue

            # Otherwise: Find the index of the found item...
            index = self.model().indexFromItem(ncloth_outliner_item)
            # ...and append the item to the selection model (must be via ItemSelectionRange)
            selected_item = QtCore.QItemSelectionRange(index)
            selection.append(selected_item)

        # Finally: Clear the current selection and select the new itemSelection
        selection_model.select(selection, QtCore.QItemSelectionModel.ClearAndSelect)

    def select_ncloth_outliner_item_from_dock_widget(self, dock_widget):
        """
        Selects nodes in the nclothOutliner that are selected in the Maya scene
        """
        # Get the selection model of the TreeView and initiate an empty item selection
        selection_model = self.selectionModel()
        selection = QtCore.QItemSelection()

        # print "dock_widget_tree_view:", type(dock_widget_tree_view), dock_widget_tree_view
        # dock_widget = dock_widget_tree_view.parent()
        print "dock_widget:", type(dock_widget), dock_widget
        dock_widget_mobj = dock_widget.mobj
        print "dock_widget_mobj:", type(dock_widget_mobj), dock_widget_mobj

        ncloth_outliner_item = self.find_item_by_mobj_with_path(dock_widget_mobj)
        if ncloth_outliner_item is None:
            return False

        # Otherwise: Find the index of the found item...
        index = self.model().indexFromItem(ncloth_outliner_item)
        # ...and append the item to the selection model (must be via ItemSelectionRange)
        selected_item = QtCore.QItemSelectionRange(index)
        selection.append(selected_item)

        # Finally: Clear the current selection and select the new itemSelection
        selection_model.select(selection, QtCore.QItemSelectionModel.ClearAndSelect)

    @staticmethod
    def get_mobjs_from_standard_items(standard_items):
        mobjs = []
        for standard_item in standard_items:
            mobjs.append(standard_item.mobj)
        return mobjs

    def refresh_maya_selection(self):
        mobjs = self.get_mobjs_from_standard_items(self.selected_ncloth_outliner_standard_items)
        MUtil._select_mobjs(mobjs)

    def selectionChanged(self, selected, deselected):
        super(NDynamicsOutliner, self).selectionChanged(selected, deselected)

        self.refresh_maya_selection()
