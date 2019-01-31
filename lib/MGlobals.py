import maya.api.OpenMaya as om


ndynamic_node_types = ["nucleus", "nCloth", "nRigid", "dynamicConstraint"]

ndynamic_dependency_node_types = [
    # kDependencyNode stands for all DAG nodes
    om.MFn.kNucleus,
    om.MFn.kNCloth,
    om.MFn.kNRigid,
    om.MFn.kDynamicConstraint,
]

attribute_box_height = 18

attr_label_width = 140

map_type_selector_width = 55

box_item_spacing = 4


# THIS WILL BE THE NEW WAY TO DEFINE UI ELEMENTS!
exposed_attrs_based_on_node_type ={


}


exposed_attrs_based_on_node_type = {
    "nucleus": {
        "TEST_NUCLEUS": {
            "gravity": ["gravity", "FloatSliderMapBox"],
        }
    },
    "nCloth": {
        "collision": {
            # niceName (used in UI), Maya-name, WidgetType
            "collideStrength": ["collideStrength", "FloatSliderMapBox"],
            "thickness": ["thickness", "FloatSliderMapBox"],
            "bounce": ["bounce", "FloatSliderMapBox"],
            "friction": ["friction", "FloatSliderMapBox"],
            "stickiness": ["stickiness", "FloatSliderMapBox"],
            # "displayColor": ["displayColor", "SolverDisplayBox"],
        },
        "dynamics": {
            "stretchResistance": ["stretchResistance", "FloatSliderMapBox"],
            "compressionResistance": ["compressionResistance", "FloatSliderMapBox"],
            "bendResistance": ["bendResistance", "FloatSliderMapBox"],
            "bendAngleDropoff": ["bendAngleDropoff", "FloatSliderMapBox"],
            "restitutionAngle": ["restitutionAngle", "FloatSliderMapBox"],
            "rigidity": ["rigidity", "FloatSliderMapBox"],
            "deformResistance": ["deformResistance", "FloatSliderMapBox"],
            "inputMeshAttract": ["inputMeshAttract", "FloatSliderMapBox"],
            "restLengthScale": ["restLengthScale", "FloatSliderMapBox"],
            "damp": ["damp", "FloatSliderMapBox"],
            "pointMass": ["pointMass", "FloatSliderMapBox"],
            "lift": ["lift", "FloatSliderMapBox"],
            "drag": ["drag", "FloatSliderMapBox"],
            "tangentialDrag": ["tangentialDrag", "FloatSliderMapBox"],
            "wrinkleMapScale": ["wrinkleMapScale", "FloatSliderMapBox"],
        },
    },
    "nRigid": {
        "TEST_NRIGID": {
            "collideStrength": ["collideStrength", "FloatSliderMapBox"],
        }
    },
    "dynamicConstraint": {
        "TEST_DYNAMICCONSTRAINT": {
            "strength": ["strength", "FloatSliderMapBox"],
        }
    },
}


"""
The isDynamic attribute (enable on/off) should be added to outliner as checkbox!
Grey out inactive elements!

Needed per attribute:
- Dependency (only active if another attribute is not equal to a certain value (wind > 0 -> enable wind direction))
- Driven Maya attributes
- Name in UI
- Type of UI element
- Related map-attr
- DropDown Options
- Whether it's expanded by default or not

    "nucleus": {
        "gravityAndWind": {
            "expandedByDefault": "False",
            "attrs": {
                "Gravity": {
                    "attrName": "gravity",
                    "widgetType": "FloatSliderBox",
                    "masterAttr": "xy" (This attr is only active if masterAttr is set to certain value),
                    "masterCondition": (What has to be fulfilled to enable this attr),
                    "mapAttr": "gravityMap",
                    "enums": ["Values", "For", "DropDowns"],
                    "uiElementType": "FloatSliderBox",
                    "uiElementType": "FloatSliderBox",
                    "radian": True/False (for attributes that need conversion; bendAngleDropoff),
                },
                "ATTRS"
            },
        "ATTR GROUPS"


The order of attributes is important!!!
Maybe list of attributes for each type and dict that serves as lookup table for metaData for that attr-type?
"""
exposed_attrs_based_on_node_type_FULL = {
    "nucleus": {
        "gravityAndWind": {
            # niceName (used in UI), Maya-name, WidgetType
            "gravity": ["gravity", "FloatSliderBox"],
            "gravityDirection": ["gravityDirection", "FloatVectorBox"],
            "airDensity": ["airDensity", "FloatSliderBox"],
            "windSpeed": ["windSpeed", "FloatSliderBox"],
            "windDirection": ["windDirection", "FloatVectorBox"],
            "windNoise": ["windNoise", "FloatSliderBox"],
        },
        "gravityAndWind": {
            "usePlane": ["usePlane", "SingleCheckBox"],
            "planeOrigin": ["planeOrigin", "FloatVectorBox"],
            "planeNormal": ["planeNormal", "FloatVectorBox"],
            "planeBounce": ["planeBounce", "FloatSliderBox"],
            "planeFriction": ["planeFriction", "FloatSliderBox"],
            "planeStickiness": ["planeStickiness", "FloatSliderBox"],
        },
        "solver": {
            "subSteps": ["subSteps", "IntSliderBox"],
            "maxCollisionIterations": ["maxCollisionIterations", "IntSliderBox"],
            "collisionLayerRange": ["collisionLayerRange", "FloatSliderBox"],
            "timingOutput": ["timingOutput", "SingleDropDownBox"],
            "useTransform": ["useTransform", "SingleCheckBox"],
        },
        "timeAndScale": {
            "currentTime": ["currentTime", "FloatSliderBox"],
            "startFrame": ["startFrame", "FloatSliderBox"],
            "frameJumpLimit": ["frameJumpLimit", "IntSliderBox"],
            "timeScale": ["timeScale", "FloatSliderBox"],
            "spaceScale": ["spaceScale", "FloatSliderBox"],
        },
    },

    "nCloth": {
        "collisions": {
            "collisionFlags": ["collide/selfCollide(flag)", "DualDropDownBox"],  # Include on/off in this!
            "collideStrength": ["collideStrength", "FloatSliderMapBox"],
            "collisionLayer": ["collisionLayer", "FloatSliderBox"],
            "thickness": ["thickness", "FloatSliderMapBox"],
            "selfCollideWidthScale": ["selfCollideWidthScale", "FloatSliderBox"],
            "solverDisplay": ["solverDisplay(displayColor)", "ColorSingleDropDownBox"],
            "bounce": ["bounce", "FloatSliderMapBox"],
            "friction": ["friction", "FloatSliderMapBox"],
            "stickiness": ["stickiness", "FloatSliderMapBox"],
        },
        "dynamics": {
            "stretchResistance": ["stretchResistance", "FloatSliderMapBox"],
            "compressionResistance": ["compressionResistance", "FloatSliderMapBox"],
            "bendResistance": ["bendResistance", "FloatSliderMapBox"],
            "bendAngleDropoff": ["bendAngleDropoff", "FloatSliderMapBox"],
            "shearResistance": ["shearResistance", "FloatSliderBox"],
            "restitutionAngle": ["restitutionAngle", "FloatSliderBox"],
            "restitutionTension": ["restitutionTension", "FloatSliderBox"],
            "restitutionAngle": ["restitutionAngle", "FloatSliderMapBox"],
            "rigidity": ["rigidity", "FloatSliderMapBox"],
            "deformResistance": ["deformResistance", "FloatSliderMapBox"],
            "usePolygonShells": ["usePolygonShells", "SingleCheckBox"],
            "inputMeshAttract": ["inputMeshAttract", "FloatSliderMapBox"],
            "inputAttractMethod": ["inputAttractMethod", "SingleDropDownBox"],
            "inputAttractDamp": ["inputAttractDamp", "FloatSliderBox"],
            "inputMotionDrag": ["inputMotionDrag", "FloatSliderBox"],
            "restLengthScale": ["restLengthScale", "FloatSliderMapBox"],
            "bendAngleScale": ["bendAngleScale", "FloatSliderBox"],
            "pointMass": ["pointMass", "FloatSliderMapBox"],
            "lift": ["lift", "FloatSliderMapBox"],
            "drag": ["drag", "FloatSliderMapBox"],
            "tangentialDrag": ["tangentialDrag", "FloatSliderMapBox"],
            "damp": ["damp", "FloatSliderMapBox"],
            "stretchDamp": ["stretchDamp", "FloatSliderBox"],
            "scalingRelation": ["scalingRelation", "SingleDropDownBox"],
            "ignoreSolverGravity/Wind": ["ignoreSolverGravity/Wind", "DualCheckBox"],
            "localForce": ["localForce", "FloatVectorBox"],
            "localWind": ["localWind", "FloatVectorBox"],
            "wrinkleMapScale": ["wrinkleMapScale", "FloatSliderMapBox"],
        },
        "wind": {
            "airPushDistance": ["airPushDistance", "FloatSliderBox"],
            "airPushVorticity": ["airPushVorticity", "FloatSliderBox"],
            "windShadowDistance": ["windShadowDistance", "FloatSliderBox"],
            "windShadowDiffusion": ["windShadowDiffusion", "FloatSliderBox"],
            "windSelfShadow": ["windSelfShadow", "SingleCheckBox"],
        },
        "pressure": {
            "pressureMethod": ["pressureMethod", "SingleDropDownBox"],
            "pressure": ["pressure", "FloatSliderBox"],
            "pressureDamping": ["pressureDamping", "FloatSliderBox"],
            "startPressure": ["startPressure", "FloatSliderBox"],
            "pumpRate": ["pumpRate", "FloatSliderBox"],
            "airTightness": ["airTightness", "FloatSliderBox"],
            "incompressibility": ["incompressibility", "FloatSliderBox"],
            "sealHoles": ["sealHoles", "SingleCheckBox"],
        },
        "quality": {
            "maxIterations": ["maxIterations", "IntSliderBox"],
            "maxSelfCollisionIterations": ["maxSelfCollisionIterations", "IntSliderBox"],
            "collideLastThreshold": ["collideLastThreshold", "FloatSliderBox"],
            "addCrossLinks": ["addCrossLinks", "SingleCheckBox"],
            "evaluationOrder": ["evaluationOrder", "SingleDropDownBox"],
            "bendSolver": ["bendSolver", "SingleDropDownBox"],
            "sortLinks": ["sortLinks", "SingleCheckBox"],
            "(self)trappedCheck": ["(self)trappedCheck", "DualCheckBox"],
            "pushOut": ["pushOut", "FloatSliderBox"],
            "pushOutRadius": ["pushOutRadius", "FloatSliderBox"],
            "crossoverPush": ["crossoverPush", "FloatSliderBox"],
            "selfCrossoverPush": ["selfCrossoverPush", "FloatSliderBox"],
        },
    },

    "nRigid": {
        "collisions": {
            "collisionFlag": ["collisionFlag", "SingleDropDownBox"],  # Include on/off in this!
            "collideStrength": ["collideStrength", "FloatSliderMapBox"],
            "collisionLayer": ["collisionLayer", "FloatSliderBox"],
            "thickness": ["thickness", "FloatSliderMapBox"],
            "solverDisplay": ["solverDisplay(displayColor)", "ColorSingleDropDownBox"],
            "bounce": ["bounce", "FloatSliderMapBox"],
            "friction": ["friction", "FloatSliderMapBox"],
            "stickiness": ["stickiness", "FloatSliderMapBox"],
        },
        "wind": {
            "airPushDistance": ["airPushDistance", "FloatSliderBox"],
            "airPushVorticity": ["airPushVorticity", "FloatSliderBox"],
            "windShadowDistance": ["windShadowDistance", "FloatSliderBox"],
            "windShadowDiffusion": ["windShadowDiffusion", "FloatSliderBox"],
        },
        "quality": {
            "trappedCheck": ["trappedCheck", "SingleCheckBox"],
            "pushOut": ["pushOut", "FloatSliderBox"],
            "pushOutRadius": ["pushOutRadius", "FloatSliderBox"],
            "crossoverPush": ["crossoverPush", "FloatSliderBox"],
        },
    },

    "dynamicConstraint": {
        "dynamics": {
            "constraintMethod": ["constraintMethod", "SingleDropDownBox"],
            "constraintRelation": ["constraintRelation", "SingleDropDownBox"],
            "componentRelation": ["componentRelation", "SingleDropDownBox"],
            "displayConnections": ["displayConnections", "SingleCheckBox"],
            "connectionMethod": ["connectionMethod", "SingleDropDownBox"],
            "maxDistance": ["maxDistance", "FloatSliderBox"],
            "connectionUpdate": ["connectionUpdate", "SingleDropDownBox"],
            "connectWithinComponent": ["connectWithinComponent", "SingleCheckBox"],
            "connectionDensity": ["connectionDensity", "FloatSliderBox"],

            "connectionDensityRange": ["connectionDensityRange", "GraphBox"],
            "strength": ["strength", "FloatSliderBox"],
            "tangentStrength": ["tangentStrength", "FloatSliderBox"],
            "glueStrength": ["glueStrength", "FloatSliderBox"],
            "glueStrengthScale": ["glueStrengthScale", "FloatSliderBox"],
            "bend": ["bend", "SingleCheckBox"],
            "bendStrength": ["bendStrength", "FloatSliderBox"],
            "bendBreakAngle": ["bendBreakAngle", "FloatSliderBox"],
            "force": ["force", "FloatSliderBox"],
            "restLengthMethod": ["restLengthMethod", "SingleDropDownBox"],
            "restLength": ["restLength", "FloatSliderBox"],
            "restLengthScale": ["restLengthScale", "FloatSliderBox"],
            "motionDrag": ["motionDrag", "FloatSliderBox"],
            "dropoffDistance": ["dropoffDistance", "FloatSliderBox"],

            "strengthDropoff": ["strengthDropoff", "GraphBox"],
            "excludeCollisions": ["excludeCollisions", "SingleCheckBox"],
            "damp": ["damp", "FloatSliderBox"],
            "localCollide": ["localCollide", "SingleCheckBox"],
            "collideWidthScale": ["collideWidthScale", "FloatSliderBox"],

            "friction": ["friction", "FloatSliderBox"],
            "singleSided": ["singleSided", "SingleCheckBox"],
            "minIterations": ["minIterations", "IntSliderBox"],
            "maxIterations": ["maxIterations", "IntSliderBox"],
        },
    },

}
