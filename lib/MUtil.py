import maya.api.OpenMaya as om
from maya import cmds

import MGlobals
reload(MGlobals)


def _get_name_of_mobj(mobj):
    node_fn = om.MFnDependencyNode(mobj)
    node_name = node_fn.name()

    return node_name


def _get_shape_mobj(mobj):
    shape_mdag_path = _get_mdag_path_of_mobj(mobj).extendToShape()
    shape_mobj = _get_mobj_from_mdag_path(shape_mdag_path)
    return shape_mobj


def _get_mdag_path_of_mobj(mobj):
    mdag_path = None
    if mobj.hasFn(om.MFn.kDagNode):
        mdag_path = om.MDagPath.getAPathTo(mobj)
    return mdag_path


def _get_mobj_from_mdag_path(mdag):
    mobj = mdag.node()
    return mobj


def _get_long_name_of_mobj(mobj, full=False):
    """
    full takes precedence - otherwise partial.
    """
    mdag_path = _get_mdag_path_of_mobj(mobj)
    if mdag_path:
        if full:
            dag_path = mdag_path.fullPathName()
        else:
            dag_path = mdag_path.partialPathName()
    else:
        dag_path = None

    return dag_path


def _get_mobj_of_node(node):
    if type(node) is om.MObject:
        return node

    selectionList = om.MSelectionList()
    selectionList.add(node)
    mobj = selectionList.getDependNode(0)

    return mobj


def _get_all_mobjs_of_type(dependency_node_type):
    """
    dependency_node_type must be of "type" OpenMaya.MFn: OpenMaya.MFn.kDependencyNode etc.
    """
    dep_node_iterator = om.MItDependencyNodes(dependency_node_type)
    return_list = []
    while not dep_node_iterator.isDone():
        mobj = dep_node_iterator.thisNode()
        return_list.append(mobj)
        dep_node_iterator.next()

    return return_list


def _get_readable_node_type_of_mobj(mobj):
    """
    This could be WAY nicer!
    Could be mobj.apiTypeStr instead, which would return kNucleus, etc.
    For this a lot of functionality would have to be adjusted. Probably worth it though!
    """
    api_type = mobj.apiType()

    node_type = None
    for node_type_str, node_type_obj in zip(MGlobals.ndynamic_node_types, MGlobals.ndynamic_dependency_node_types):
        if api_type == node_type_obj:
            return node_type_str

    return node_type


def _rename_mobj(mobj, name):
    dag_modifier = om.MDagModifier()
    dag_modifier.renameNode(mobj, name)
    dag_modifier.doIt()


def _set_mobj_attribute(mobj, attr, value):
    # This should be om-only, too!
    # http://austinjbaker.com/mplugs-setting-values
    dag_path = _get_long_name_of_mobj(mobj)
    cmds.setAttr("{}.{}".format(dag_path, attr), value)


def _selected_nodes_in_scene_as_mobjs():
    mobjs = []

    selection_list = om.MGlobal.getActiveSelectionList()
    if selection_list.length() > 0:
        iterator = om.MItSelectionList(selection_list, om.MFn.kDagNode)
        while not iterator.isDone():
            mobj = iterator.getDependNode()
            mobjs.append(mobj)
            iterator.next()

    return mobjs


def _get_attr_of_mobj(mobj, attr):
    # Rewrite this to pure OM!
    path = _get_long_name_of_mobj(mobj)
    value = cmds.getAttr("{}.{}".format(path, attr))

    return value


def _select_mobjs(mobjs):
    """
    For some reason the first (commented out) version of this command that utilizes
    om-methods only selects the node, but it doesn't get selected in the outliner
    or viewport! Therefore using the cmds-version for now.
    """
    # m_selection_list = om.MSelectionList()
    # for mobj in mobjs:
    #     m_selection_list.add(mobj)
    # om.MGlobal.setActiveSelectionList(m_selection_list, om.MGlobal.kReplaceList)
    # return m_selection_list

    select_list = []
    for mobj in mobjs:
        select_list.append(_get_long_name_of_mobj(mobj))
    cmds.select(select_list)
    return select_list
