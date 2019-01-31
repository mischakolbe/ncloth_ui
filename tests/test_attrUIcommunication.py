from PySide import QtCore
from PySide import QtGui

from shiboken import wrapInstance

from maya import cmds
import pymel.core as pm
import maya.OpenMayaUI as omui
from ui import widgets
reload(widgets)


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtGui.QWidget)


class SexyPyNode(pm.PyNode):
    def __setAttr__(self, val):
        super(SexyPyNode, self).__setAttr__()
        print val


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

        self.test_widget = QtGui.QSlider()

        self.maya_node = pm.PyNode("pCube1")
        self.test_widget.setValue(self.maya_node.tx.get())

        self.test_widget.valueChanged.connect(self.slider_update)

        # Add to central layout
        self.central_layout.addWidget(self.test_widget)

        cmds.scriptJob(runOnce=False, attributeChange=['pCube1.tx', self.detectNewTagAttr])

    def slider_update(self):
        self.maya_node.tx.set(self.test_widget.value())

    def detectNewTagAttr(self):
        self.test_widget.setValue(self.maya_node.tx.get())



def launch_ui():

    ui = TestUI()
    ui.show()






# import pymel.core as pm
# from pymel.internal.factories import virtualClasses


# class SexyPyNode(pm.nt.Transform):
#     _jointClassID = 'schnitzelKlass!'

#     @classmethod
#     def _isVirtual( cls, obj, name ):
#         """This is the callback for determining if a Joint should become a "virtual" LegJoint or JawJoint, etc.
#         Notice that this method is a classmethod, which means it gets passed the class as "cls" instead of an instance as "self".

#         PyMEL code should not be used inside the callback, only API and maya.cmds.
#         """
#         # obj is either an MObject or an MDagPath, depending on whether this class is a subclass of DependNode or DagNode, respectively.
#         # we use MFnDependencyNode below because it works with either and we only need to test attribute existence.
#         fn = pm.api.MFnDependencyNode(obj)
#         try:
#             # NOTE: MFnDependencyNode.hasAttribute fails if the attribute does not exist, so we have to try/except it.
#             # the _jointClassID is stored on subclass of CustomJointBase
#             return fn.hasAttribute( cls._jointClassID )
#         except: pass
#         return False

#     @classmethod
#     def _preCreateVirtual(cls, **kwargs ):
#         """
#         This class method is called prior to node creation and gives you a
#         chance to modify the kwargs dictionary that is passed to the creation
#         command.  If it returns two dictionaries, the second is used passed
#         as the kwargs to the postCreate method

#         this method must be a classmethod or staticmethod
#         """
#         if 'name' not in kwargs and 'n' not in kwargs:
#             # if no name is passed, then use the joint Id as the name.
#             kwargs['name'] = cls._jointClassID
#         # be sure to return the modified kwarg dictionary

#         postKwargs = {}

#         if 'rotate' in kwargs:
#             postKwargs['rotate'] = kwargs.pop('rotate')
#         return kwargs, postKwargs

#     @classmethod
#     def _postCreateVirtual(cls, newNode, **kwargs ):
#         """
#         This method is called after creating the new node, and gives you a
#         chance to modify it.  The method is passed the PyNode of the newly
#         created node, and the second dictionary returned by the preCreate, if
#         it returned two items. You can use PyMEL code here, but you should
#         avoid creating any new nodes.

#         this method must be a classmethod or staticmethod
#         """
#         # add the identifying attribute. the attribute name will be set on subclasses of this class
#         newNode.addAttr( cls._jointClassID )
#         rotate = kwargs.get('rotate')
#         if rotate is not None:
#             newNode.attr('rotate').set(rotate)

#     """
#     def __setAttr__(self, val):
#         super(SexyPyNode, self).__setAttr__()
#         print val
#     """
#     def kick(self):
#         print "%s is kicking" % self.name()
#         return "kiyaah!"

# virtualClasses.register( SexyPyNode, nameRequired=False )

# a = SexyPyNode("pCube1")


# a.tx.set(1)





# class LegJoint(CustomJointBase):
#     _jointClassID = 'joint_leg'



# class JawJoint(CustomJointBase):
#     _jointClassID = 'joint_jaw'
#     def munch(self):
#         print "%s is munching" % self.name()
#         return "nom nom nom..."

# # we don't need to register CustomJointBase because it's just an abstract class to help us easily make our other virtual nodes
# virtualClasses.register( LegJoint, nameRequired=False )
# virtualClasses.register( JawJoint, nameRequired=False )

# def testJoint():
#     # make some regular joints
#     pm.nt.Joint()
#     pm.nt.Joint()
#     # now make some of our custom joints
#     LegJoint(name='leftLeg')
#     JawJoint(rotate=(90,45,0))

#     # now list the joints and see which ones are our special joints
#     res = pm.ls(type='joint')
#     for x in res:
#         if isinstance(x, LegJoint ):
#             x.kick()
#         elif isinstance(x, JawJoint ):
#             x.munch()



# from maya.api import OpenMaya as om


# # function that returns a node object given a name
# def nameToNode( name ):
#     selectionList = om.MSelectionList()
#     selectionList.add( name )
#     node = om.MObject()
#     selectionList.getDependNode( 0 )
#     return node

# # function that finds a plug given a node object and plug name
# def nameToNodePlug( attrName, nodeObject ):
#     depNodeFn = om.MFnDependencyNode( nodeObject )
#     attrObject = depNodeFn.attribute( attrName )
#     plug = om.MPlug( nodeObject, attrObject )
#     return plug


# def testDef():

#     print nameToNode("pCube1")
#     # MObject myNode = this->thisMObject();
#     # myCBID = MNodeMessage::addAttributeChangedCallback(myNode, AttrChangedCB, NULL, &stat);
# testDef()




# def detectNewTagAttr():
#     print "Moved in x!"

# cmds.scriptJob( runOnce=True, attributeChange=['mySphere.tx',detectNewTagAttr] )
