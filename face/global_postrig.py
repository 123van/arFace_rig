import maya.cmds as cmds

class BaseClass:
    """
    A base class for creating, managing, and connecting nodes using pymel in Maya.
    """
    import pymel.core
    import six
    import re
    import os
    import bardelUtils
    import json
    from pathlib import Path

    pm = pymel.core
    six = six
    re = re
    os = os
    util = bardelUtils
    json = json
    Path = Path

    def __init__(self):
        """
        Initialize the BaseClass with empty dictionaries for nodes and node types,
        and an empty list for connection networks.
        """
        self.nodes = {}
        self.nodeTypes = {}
        self.connectNet = []

    def run(self):
        """
        Execute the sequence of pre-processing, main processing, and post-processing steps.
        """
        self.preProcess()

        if self.main():
            self.postProcess()

    def preProcess(self):
        """
        Perform any necessary steps before the main processing.
        """
        pass

    def main(self):
        pass

    def createNodes(self):
        """
        Create nodes based on the nodeTypes dictionary and store them as PyNode instances.
        """
        for name, nodeType in self.nodeTypes.items():
            try:
                node = self.pm.createNode(
                        nodeType,
                        n=getattr(self, name)
                )
                # Replace string with PyNode instance
                setattr(self, name, node)
            except Exception as e:
                print(f"Failed to create node {getattr(self, name)}: {str(e)}")

    def setupNodes(self):
        """
        Set up nodes with necessary attributes and connections. To be implemented in subclasses.
        """
        pass

    def connectNodes(self):
        """
        Connect nodes based on the connectNet list of source-destination pairs.
        """
        for network in self.connectNet:
            src, dst = network[0], network[1]
            try:
                self.pm.connectAttr(src, dst, f=True)
            except Exception as e:
                self.printStatusMessage(
                        "Skip",
                        f"Failed to connect {src} to {dst}"
                )

    def getConnectionFromNode(self):
        """
        Retrieve connections from a node. To be implemented in subclasses.
        """
        pass

    def addConnection(self):
        """
        Add a connection to the connectNet list. To be implemented in subclasses.
        """
        pass

    def deleteUnusedNodes(self):
        """
        Delete nodes that are no longer in use. To be implemented in subclasses.
        """
        pass

    def postProcess(self):
        """
        Perform any necessary steps after the main processing, such as cleaning up unused nodes.
        """
        self.deleteUnusedNodes()

    def asPyNode(self, obj):
        """Check and convert a given string to Pynode

        If the object is not str or unicode or PyNode will raise type error

        Args:
            obj (str, unicode, PyNode): Object to check and/or convert to PyNode

        Returns:
            PyNode: the pynode object
        """
        if isinstance(obj, str) or isinstance(obj, self.six.string_types):
            obj = self.pm.PyNode(obj)

        if not isinstance(obj, self.pm.PyNode):
            raise TypeError("{} is type {} not str, unicode or PyNode".format(
                    str(obj), type(obj)))

        return obj

    def printStatusMessage(self, status, message):
        # Get the current class name dynamically
        className = type(self).__name__

        status_map = {
            'Done': '✓',
            'Skip': '>>>>',
            'Failed': '✗'
        }
        symbol = status_map.get(status, '?')  # Default to '?' if status not recognized
        formatted_message = f"# {symbol} {status}: [{className}] {message}"
        print(formatted_message)


class AttributeSwapper(BaseClass):
    """Class for managing and swapping attributes on rig controls."""

    def __init__(self):
        super().__init__()

        # Define lip control attributes and their configurations within a dictionary.
        self.lipSetup = {
            'ctrlName': {
                'lipPrimaryCtl': "C_LipPrimary_01_Ctrl",
                'jawCtl': "C_Jaw_01_Ctrl",
                'cheekCtlL': "L_LowerCheek_01_Ctrl",
                'cheekCtlR': "R_LowerCheek_01_Ctrl",
                'nostrilCtlL': "L_Nostril_01_Ctrl",
                'nostrilCtlR': "R_Nostril_01_Ctrl",
                'noseTipCtl': self._findNoseLastCtl()
            },
            'deleteData': {
                "C_LipPrimary_01_Ctrl": [
                    "noseFollow",
                    "lNostrilFollow",
                    "rNostrilFollow",
                    "lCheekVolume",
                    "lCheekSlide",
                    "rCheekVolume",
                    "rCheekSlide",
                    "jawVolume",
                    "AUTONOSE_ATTRS",
                    "AUTOCHEEK_ATTRS"
                ]
            },
            'data': {
                "L_LowerCheek_01_Ctrl": {"attr": ["cheekVolume", "cheekSlide"], "min": 0, "max": 10},
                "R_LowerCheek_01_Ctrl": {"attr": ["cheekVolume", "cheekSlide"]},
                "L_Nostril_01_Ctrl": {"attr": ["nostrilFollow"]},
                "R_Nostril_01_Ctrl": {"attr": ["nostrilFollow"]},
                "C_Jaw_01_Ctrl": {"attr": ["jawVolume"], "min": 0, "max": 10},
                self._findNoseLastCtl(): {"attr": ["noseFollow"], "min": 0, "max": 10}
            },
            'unusedAttr': (
                "noseFollow", "lNostrilFollow", "rNostrilFollow", "lCheekVolume",
                "lCheekSlide", "rCheekVolume", "rCheekSlide", "jawVolume",
                "AUTONOSE_ATTRS", "AUTOCHEEK_ATTRS"
            ),
            'attrLink': {
                "C_LipPrimary_01_Ctrl.noseFollow": f"{self._findNoseLastCtl()}.noseFollow",
                "C_LipPrimary_01_Ctrl.lNostrilFollow": "L_Nostril_01_Ctrl.nostrilFollow",
                "C_LipPrimary_01_Ctrl.rNostrilFollow": "R_Nostril_01_Ctrl.nostrilFollow",
                "C_LipPrimary_01_Ctrl.lCheekVolume": "L_LowerCheek_01_Ctrl.cheekVolume",
                "C_LipPrimary_01_Ctrl.lCheekSlide": "L_LowerCheek_01_Ctrl.cheekSlide",
                "C_LipPrimary_01_Ctrl.rCheekVolume": "R_LowerCheek_01_Ctrl.cheekVolume",
                "C_LipPrimary_01_Ctrl.rCheekSlide": "R_LowerCheek_01_Ctrl.cheekSlide",
                "C_LipPrimary_01_Ctrl.jawVolume": "C_Jaw_01_Ctrl.jawVolume"
            },
            'outputPlug': {}
        }

        self.upSocketSetup = {
            'ctrlName': {
                'upSocketL': "L_UpperSocket_01_Ctrl",
                'upSocketR': "R_UpperSocket_01_Ctrl",
                'upSquintL': "L_Uppersquint_01_Ctrl",
                'upSquintR': "R_Uppersquint_01_Ctrl"
            },
            'deleteData': {
                "L_Uppersquint_01_Ctrl": [
                    "eye_squint",
                    "smooth"
                ],
                "R_Uppersquint_01_Ctrl": [
                    "eye_squint",
                    "smooth"
                ]
            },
            'data': {
                "L_UpperSocket_01_Ctrl": {"attr": ["eye_squint", "smooth"]},
                "R_UpperSocket_01_Ctrl": {"attr": ["eye_squint", "smooth"]}
            },
            'unusedAttr': (
                "eye_squint", "smooth"
            ),
            'attrLink': {
                "L_Uppersquint_01_Ctrl.eye_squint": "L_UpperSocket_01_Ctrl.eye_squint",
                "L_Uppersquint_01_Ctrl.smooth": "L_UpperSocket_01_Ctrl.smooth",
                "R_Uppersquint_01_Ctrl.eye_squint": "R_UpperSocket_01_Ctrl.eye_squint",
                "R_Uppersquint_01_Ctrl.smooth": "R_UpperSocket_01_Ctrl.smooth",
            },
            'outputPlug': {}
        }

    def main(self):
        """Execute attribute management tasks."""
        self.addAttributes("Lip", "AUTO_ATTRS")
        self.addAttributes("Squint", "EXTRA")

        self.getOutputFromNodes()

        self.reconnect(self.lipSetup)
        self.reconnect(self.upSocketSetup)

        self.deleteAttributes(self.lipSetup['deleteData'])
        self.deleteAttributes(self.upSocketSetup['deleteData'])

        self.hide()
        return True

    def postProcess(self):
        self.printStatusMessage(
            "Done",
            "Swapping attributes and deleted unused attributes"
        )

    def _addAttributes(self, keys, attrName, data):
        for key in keys:
            if key is None:
                continue

            if not cmds.objExists(key):
                self.printStatusMessage(
                    "Skip",
                    f"There is no {key} in the rig"
                )
                continue

            cmds.addAttr(key, ln=attrName, at='enum', en='---------------', k=True)
            cmds.setAttr('{}.{}'.format(key, attrName), lock=True)

            content = data[key]
            for attr in content["attr"]:
                if "min" in content and "max" in content:
                    cmds.addAttr(
                        key,
                        ln=attr,
                        at='float',
                        dv=0,
                        min=content["min"],
                        max=content["max"],
                        k=True
                    )
                else:
                    cmds.addAttr(key, ln=attr, at='float', dv=0, k=True)

    def addAttributes(self, setupType, attrName):
        """Add custom attributes to controls based on defined data."""
        if setupType == "Lip":
            lipAttr = self.lipSetup['ctrlName']
            lipData = self.lipSetup['data']
            self._addAttributes([lipAttr['cheekCtlL'], lipAttr['cheekCtlR']], attrName, lipData)
            self._addAttributes([lipAttr['nostrilCtlL'], lipAttr['nostrilCtlR']], attrName, lipData)
            self._addAttributes([lipAttr['noseTipCtl']], attrName, lipData)
            self._addAttributes([lipAttr['jawCtl']], attrName, lipData)

        elif setupType == "Squint":
            socketAttr = self.upSocketSetup['ctrlName']
            socketData = self.upSocketSetup['data']
            self._addAttributes([socketAttr['upSocketL'], socketAttr['upSocketR']], attrName, socketData)

    def getOutputFromNodes(self):
        self._getOutputFromNode(self.lipSetup, "lipPrimaryCtl")
        self._getOutputFromNode(self.upSocketSetup, "upSquintL")
        self._getOutputFromNode(self.upSocketSetup, "upSquintR")

    def _getOutputFromNode(self, setupData, ctrlAlias):
        """Retrieve output connections from the primary control."""

        def _getOutputPlug(plug):
            return cmds.listConnections(plug, s=False, d=True, p=True)

        for ctrl, attrs in setupData['deleteData'].items():
            for attr in attrs:
                plug = f"{ctrl}.{attr}"
                setupData['outputPlug'][plug] = _getOutputPlug(plug)

    def deleteAttributes(self, deleteData):
        """Delete unused attributes from the primary control."""
        for node, attrs in deleteData.items():
            for attr in attrs:
                plug = f"{node}.{attr}"
                if cmds.getAttr(plug, lock=True):
                    cmds.setAttr(plug, lock=False)
                cmds.deleteAttr(plug)

    def _findNoseLastCtl(self):
        """Find the last control in the nose chain."""
        noseCtls = []
        for i in range(1, 20):
            name = f"C_Nose_0{i}_Ctrl"
            if cmds.objExists(name):
                noseCtls.append(name)

        if not noseCtls:
            self.printStatusMessage(
                "Skip",
                "There is no nose controllers in the rig"
            )
            return None

        return noseCtls[-1]

    def reconnect(self, setupData):
        """Reconnect attributes based on the attribute link map."""
        for plugName, dgPlugs in setupData['outputPlug'].items():
            if dgPlugs is None:
                continue

            plug = setupData['attrLink'].get(plugName, [])
            for dg in dgPlugs:
                if not cmds.objExists(plug):
                    self.printStatusMessage(
                        "Skip",
                        f"There is no {plug} in the scene"
                    )
                    continue
                cmds.connectAttr(plug, dg, f=True)

    def hide(self):
        nodes = cmds.ls(["L_Uppersquint_01_RCtrl_Ancr", "R_Uppersquint_01_RCtrl_Ancr"])
        cmds.hide(nodes)


class SquashFixing(BaseClass):
    """
    This class involves the top squash controller, which includes volume attributes
    to adjust the scaling of the squash. This class is for a bug fix that affects the default shape
    when the controller is zeroed out and adjust the attributes.
    """

    def __init__(self):
        self.topSquashCtl = "C_TopSqSt_01_Ctrl"
        self.topSquashJnt = "C_TopSqSt_01_Wjnt"

        # Initialize as strings and later replace with PyNode instances
        self.envelopeMult = "scaleFactor_multiply_envelope"
        self.restEnvelope = "preEnvelope_minus"
        self.distanceZero = "distanceZero_minus"
        self.conditionValue = "conditionValue_multiply"
        self.resultPlus = "finalizeResult_plus"
        self.resultCondX = "resultCondX_condition"
        self.resultCondZ = "resultCondZ_condition"

        self.nodes = {}

        self.nodeTypes = {
            'envelopeMult': "multiplyDivide",
            'conditionValue': "multiplyDivide",
            'restEnvelope': "plusMinusAverage",
            'distanceZero': "plusMinusAverage",
            'resultPlus': "plusMinusAverage",
            'resultCondX': "condition",
            'resultCondZ': "condition",
        }

        self.connectNet = [
            [f"{self.topSquashCtl}.volumeX", f"{self.envelopeMult}.input2X"],
            [f"{self.topSquashCtl}.volumeZ", f"{self.envelopeMult}.input2Z"],
            [f"{self.resultCondX}.outColorR", f"{self.topSquashJnt}.scaleX"],
            [f"{self.resultCondZ}.outColorB", f"{self.topSquashJnt}.scaleZ"],
            [f"{self.distanceZero}.output1D", f"{self.envelopeMult}.input1X"],
            [f"{self.distanceZero}.output1D", f"{self.envelopeMult}.input1Z"],
            [f"{self.topSquashCtl}.volumeX", f"{self.restEnvelope}.input3D[1].input3Dx"],
            [f"{self.topSquashCtl}.volumeZ", f"{self.restEnvelope}.input3D[1].input3Dz"],
            [f"{self.restEnvelope}.output3Dx", f"{self.resultPlus}.input3D[0].input3Dx"],
            [f"{self.restEnvelope}.output3Dz", f"{self.resultPlus}.input3D[0].input3Dz"],
            [f"{self.resultPlus}.output3D.output3Dx", f"{self.resultCondX}.colorIfFalse.colorIfFalseR"],
            [f"{self.resultPlus}.output3D.output3Dz", f"{self.resultCondZ}.colorIfFalse.colorIfFalseB"],
            [f"{self.envelopeMult}.outputX", f"{self.resultPlus}.input3D[1].input3Dx"],
            [f"{self.envelopeMult}.outputZ", f"{self.resultPlus}.input3D[1].input3Dz"],
            [f"{self.distanceZero}.output1D", f"{self.conditionValue}.input1X"],
            [f"{self.distanceZero}.output1D", f"{self.conditionValue}.input1Y"],
            [f"{self.conditionValue}.outputX", f"{self.resultCondX}.firstTerm"],
            [f"{self.conditionValue}.outputY", f"{self.resultCondZ}.firstTerm"],
            [f"{self.topSquashCtl}.volumeX", f"{self.conditionValue}.input2X"],
            [f"{self.topSquashCtl}.volumeZ", f"{self.conditionValue}.input2Y"],
        ]

    def preProcess(self):
        self.getConnectionFromNode()

    def main(self):
        self.createNodes()
        self.setupNodes()
        self.addConnection()
        self.connectNodes()
        self.deleteUnusedNodes()

        # Fix ear squash behaviour if ear controller exists
        #EarSquashFixing().run()

        return True

    def postProcess(self):
        self.printStatusMessage(
                "Done",
                "Fixed squash values properly"
        )

    def setupNodes(self):
        # Setup nodes directly using PyNode instances
        try:
            self.envelopeMult.attr("operation").set(1)
            self.restEnvelope.attr("operation").set(2)
            self.restEnvelope.attr("input3D[0].input3Dx").set(1)
            self.restEnvelope.attr("input3D[0].input3Dz").set(1)
            self.resultCondX.attr("colorIfTrueR").set(1)
            self.resultCondZ.attr("colorIfTrueB").set(1)

            self.distanceZero.attr("operation").set(2)
            self.distanceZero.attr("input1D[1]").set(1)
            self.conditionValue.attr("operation").set(1)
            self.resultPlus.attr("operation").set(1)
        except Exception as e:
            self.printStatusMessage(
                    "Failed",
                    f"Failed to setup node attributes: {str(e)}"
            )

    def getConnectionFromNode(self):
        """Retrieve output connections from the lip primary control."""
        blendColorX = self.pm.listConnections(
                f"{self.topSquashCtl}.volumeX",
                d=True)
        blendColorZ = self.pm.listConnections(
                f"{self.topSquashCtl}.volumeZ",
                d=True)
        scaleResult = self.pm.listConnections(
                f"{blendColorX[0].name()}.color1",
                s=True)
        plusResult = self.pm.listConnections(
                f"{scaleResult[0].name()}.input1Y",
                s=True)
        divideResult = self.pm.listConnections(
                f"{plusResult[0].name()}.input3D[2].input3Dy",
                s=True)
        distanceResult = self.pm.listConnections(
                f"{divideResult[0].name()}.input1X",
                s=True)

        self.nodes["blendColorX"] = blendColorX[0].name()
        self.nodes["blendColorZ"] = blendColorZ[0].name()
        self.nodes["scaleResult"] = scaleResult[0].name()
        self.nodes["distanceResult"] = distanceResult[0].name()

    def addConnection(self):
        self.connectNet.extend([
            ["{}.outputX".format(self.nodes["scaleResult"]), f"{self.envelopeMult}.input1X"],
            ["{}.outputZ".format(self.nodes["scaleResult"]), f"{self.envelopeMult}.input1Z"],
            ["{}.outputY".format(self.nodes["distanceResult"]), f"{self.distanceZero}.input1D[0]"],
        ])

    def deleteUnusedNodes(self):
        self.pm.delete(
                self.nodes["blendColorX"],
                self.nodes["blendColorZ"]
        )


class EarSquashFixing(BaseClass):
    """
    A class to manage and fix ear rigging by creating, setting up, and connecting nodes.
    Inherits from BaseClass.
    """

    def __init__(self):
        # Initialize as strings and later replace with PyNode instances
        self.decMatrix = "C_TopSqSt_01_WjntScale_decomposeMatrix"
        self.scaleBlend = "C_TopSqSt_01_WjntScale_blendMatrix"
        self.decMatrixSq = "C_squash_decomposeMatrix"

        self.nodes = {}

        # Dictionary data for createNodes method
        self.nodeTypes = {
            "scaleBlend": "blendMatrix",
            "decMatrix": "decomposeMatrix",
            "decMatrixSq": "decomposeMatrix",
        }

        # Local attributes
        self.topSquashJnt = self.asPyNode("C_TopSqSt_01_Wjnt")
        self.topSquashJntParent = self.topSquashJnt.getParent()
        self.tfmGrp = {
            "L": "ANCR_TFM_Drvr_Ear_01_L_Tfm1",
            "R": "ANCR_TFM_Drvr_Ear_01_L_Tfm1"
        }

        self.baseOffset = {
            "L": "L_EarBase_01_Ctrl_Ofst",
            "R": "R_EarBase_01_Ctrl_Ofst",
        }

        self.earBaseCtrl = {
            "L": "L_EarBase_01_Ctrl",
            "R": "R_EarBase_01_Ctrl",
        }

        self.squashCtrls = {
            "top": "C_TopSqSt_01_Ctrl",
            "mid": "C_MidSqSt_01_Ctrl",
            "low": "C_LowerSqSt_01_Ctrl"
        }

        self.earDriver = {
            "L": "ANCR_TFM_Drvr_Ear_01_L",
            "R": "ANCR_TFM_Drvr_Ear_01_R",
        }

        self.targets = 'ancr_wjnt_EarBase_01_{}'

        self.connectNet = [
            [f"{self.topSquashJnt.name()}.matrix", f"{self.scaleBlend}.inputMatrix"],
            [f"{self.topSquashJntParent.name()}.matrix", f"{self.scaleBlend}.target[0].targetMatrix"],
            [f"{self.scaleBlend}.outputMatrix", f"{self.decMatrix}.inputMatrix"],
            ["{}.matrix".format(self.squashCtrls["top"]), f"{self.decMatrixSq}.inputMatrix"],
        ]

    def main(self):
        for ctrl in self.earBaseCtrl.values():
            if not self.pm.objExists(ctrl):
                self.printStatusMessage(
                        "Skip",
                        "Ear Controllers doesn't exist, Skip the process"
                )
                return False

        self.createNodes()
        self.setupNodes()

        for side in ['L', 'R']:
            # Parent the joints under the ear master
            self.pm.parent(f"{side}_IkStr_Ear_01_Mstr",
                           f"{side}_Ear_01_Mstr")

        self.addConnection()
        self.connectNodes()
        return True

    def postProcess(self):
        self.printStatusMessage(
                "Done",
                "Fixed the ear squash properly"
        )

    def addConnection(self):
        for side in ["L", "R"]:
            self.connectNet.extend([
                [f"{self.decMatrixSq}.outputTranslate", "{}.translate".format(self.baseOffset[side])],
                [f"{self.decMatrixSq}.outputRotate", "{}.rotate".format(self.baseOffset[side])],
                [f"{self.decMatrixSq}.outputShear", "{}.shear".format(self.baseOffset[side])],
                [f"{self.decMatrix}.outputScale", "{}.scale".format(self.baseOffset[side])],
                ["{}.matrix".format(self.squashCtrls["mid"]), "{}.offsetParentMatrix".format(self.earDriver[side])],
            ])

    def setupNodes(self):
        self.pm.setAttr(f"{self.scaleBlend}.envelope", 0.5)


class ControlSpeedFixer(BaseClass):

    def __init__(self):
        super().__init__()
        self.nodesData = [
            {
                "function": "setDefaultAttributeValues",
                "prefix": "Primary_UpperLip_00_Ctrl",
                "attributes": ['falloffA', 'falloffB'],
                "defaultValue": 0
            },
            {
                "function": "setDefaultAttributeValues",
                "prefix": "Primary_LowerLip_00_Ctrl",
                "attributes": ['falloffA', 'falloffB'],
                "defaultValue": 0
            },
            {
                "function": "setDefaultAttributeValues",
                "prefix": "Primary_UpperLip_00_Ctrl",
                "attributes": ['smooth'],
                "defaultValue": 0.1
            },
            {
                "function": "setDefaultAttributeValues",
                "prefix": "Primary_LowerLip_00_Ctrl",
                "attributes": ['smooth'],
                "defaultValue": 0.1
            }
        ]

        self.specificNodesData = [
            {
                "nodeName": "C_Oft_Tonguebase_01_Ctrl",
                "attributes": ['follow01', 'follow02'],
                "defaultValue": 1
            },
            {
                "nodeName": "C_Primary_UpperLip_00_Ctrl",
                "attributes": ['falloffA', 'falloffB'],
                "defaultValue": 0
            },
            {
                "nodeName": "C_Primary_LowerLip_00_Ctrl",
                "attributes": ['falloffA', 'falloffB'],
                "defaultValue": 0
            },
            {
                "nodeName": "C_Primary_UpperLip_00_Ctrl",
                "attributes": ['smooth'],
                "defaultValue": 0.1
            },
            {
                "nodeName": "C_Primary_LowerLip_00_Ctrl",
                "attributes": ['smooth'],
                "defaultValue": 0.1
            }
        ]

    def _checkNodeExists(self, nodeName):
        if not cmds.objExists(nodeName):
            self.printStatusMessage(
                    "Failed",
                    f"Node '{nodeName}' not found."
            )
            return False
        return True

    def setOffsetValues(self, nodeName, value, attributeType='scale'):
        if not self._checkNodeExists(nodeName):
            return

        for axis in 'XYZ':
            cmds.setAttr(f"{nodeName}.{attributeType}{axis}", value)

    def setDefaultAttributeValues(self, nodeName, attributeNames, defaultValue):
        if not self._checkNodeExists(nodeName):
            return

        for attrName in attributeNames:
            if cmds.attributeQuery(attrName, node=nodeName, exists=True):
                cmds.setAttr(f"{nodeName}.{attrName}", defaultValue)
            else:
                self.printStatusMessage(
                        "Failed",
                        f"Attribute '{attrName}' not found on node '{nodeName}'."
                )

    def main(self):
        sides = ['L', 'R']
        for nodeData in self.nodesData:
            functionName = nodeData["function"]
            prefix = nodeData["prefix"]

            for side in sides:
                nodeName = f"{side}_{prefix}"

                if functionName == "setOffsetValues":
                    value = nodeData["value"]
                    attributeType = nodeData["attributeType"]
                    self.setOffsetValues(nodeName, value, attributeType)
                elif functionName == "setDefaultAttributeValues":
                    attributeNames = nodeData["attributes"]
                    defaultValue = nodeData["defaultValue"]
                    self.setDefaultAttributeValues(nodeName, attributeNames, defaultValue)

        for nodeData in self.specificNodesData:
            nodeName = nodeData["nodeName"]
            attributeNames = nodeData["attributes"]
            defaultValue = nodeData["defaultValue"]

            self.setDefaultAttributeValues(nodeName, attributeNames, defaultValue)

        return True

    def postProcess(self):
        self.printStatusMessage(
                "Done",
                "Fixed the movement speed of the specific controllers"
        )

    def expandControlRange(self, value=0.1):
        dictNodes = {
            "L_LowerCheek_01_Ctrl": {
                "jnt": "L_Tran_LowerCheek_01_Wjnt",
                "scaleConst": "L_LowerCheek_01_RCtrl_scaleConstraint1"
            },
            "R_LowerCheek_01_Ctrl": {
                "jnt": "R_Tran_LowerCheek_01_Wjnt",
                "scaleConst": "R_LowerCheek_01_RCtrl_scaleConstraint1"
            }
        }

        for side in ["L", "R"]:
            ctrlNode = self.pm.ls(f"{side}_LowerCheek_01_Ctrl")[0]
            jntNode = self.pm.ls(dictNodes[f"{side}_LowerCheek_01_Ctrl"]["jnt"])
            jntAncr = jntNode[0].getParent()
            jntAdj = self.util.createInitSpace(jntNode, suffix="Adj")
            jntDriven = self.util.createInitSpace(jntNode, suffix="Driven")

            ctrlAdj = ctrlNode.getParent()
            ctrlWorld = ctrlNode.getParent(3)

            scaleCnst = dictNodes[f"{side}_LowerCheek_01_C