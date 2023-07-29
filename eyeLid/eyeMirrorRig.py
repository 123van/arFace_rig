import maya.cmds as cmds
from twitchScript.face import face_utils
reload(face_utils)


def eyeJntLabel(layer):
    """

    Args:
        layer: "Blink" "Wide"

    Returns:

    """
    prefix = ["l_up", "l_lo"]
    for pre in prefix:
        jnts = cmds.ls(pre + 'Lid{}_*'.format(layer), type='joint')
        for i, j in enumerate(jnts):
            lName = j.split("_")
            cmds.setAttr(j + '.side', 1)
            cmds.setAttr(j + '.type', 18)
            cmds.setAttr(j + '.otherType', lName[1] + lName[2], type="string")

            rj = j.replace("l_", "r_")
            rName = rj.split("_")
            cmds.setAttr(rj + '.side', 2)
            cmds.setAttr(rj + '.type', 18)
            cmds.setAttr(rj + '.otherType', rName[1] + rName[2], type="string")
            # l_lidBlink_OutCorner
    for LR, index in {"l_": 1, "r_": 2}.items():
        jnts = cmds.ls(LR + 'lid{}_*'.format(layer), type='joint')
        for jot in jnts:
            name = jot.split("_")

            cmds.setAttr(jot + '.side', index)
            cmds.setAttr(jot + '.type', 18)
            cmds.setAttr(jot + '.otherType', name[1] + name[2], type="string")


class EyeRig(face_utils.Util):

    def __init__(self):

        super(EyeRig, self).__init__()
        self.blinkJntDict = {"l_up": [], "l_lo": [], "r_up": [], "r_lo": []}
        self.wideJntDict = {"l_up": [], "l_lo": [], "r_up": [], "r_lo": []}
        self.eyeCornerDict = {"l_": [], "r_": []}
        self.eyeWideCornerDict = {"l_": [], "r_": []}
        self.reverseMult = None
        self.parameter = {"up": [], "lo": []}
        self.orderedVerts = {"l_up": [], "l_lo": [], "r_up": [], "r_lo": []}
        self.polyCrvDict = {}
        self.eyeCtlList = []
        self.eyePocList = []

    def eyeJointSetup(self):

        if not cmds.objExists('lEyePos'):
            raise RuntimeError("import the face locators")

        eyeRot = cmds.xform("lEyePos", ws=1, q=1, ro=1)
        eyePos = cmds.getAttr("helpPanel_grp.lEyePos")

        lidFactor = self.faceFactors["eyelid"]
        if not cmds.attributeQuery("l_cornerVerts", node=lidFactor, exists=1):
            raise RuntimeError("store eyeLid vertices first!!")

        if not cmds.objExists('eyeJnt_grp'):
            cmds.group(n='eyeJnt_grp', em=True, p="eyeRig")

        prefixDict = {"l_": 1, "r_": -1}
        for LR, val in prefixDict.items():

            jntGrp = cmds.group(n="{}eyeLid_grp".format(LR), em=True, p="eyeJnt_grp")

            eyeGrpPos = [eyePos[0] * val, eyePos[1], eyePos[2]]
            cmds.xform(jntGrp, ws=1, t=eyeGrpPos)
            cmds.setAttr(jntGrp + '.ry', eyeRot[1]*val)
            cmds.setAttr(jntGrp + '.rz', eyeRot[2]*val)
            prefixDict[LR] = jntGrp

        cmds.select(prefixDict["l_"])
        lBaseJnt = cmds.joint(n="l_eyeBaseJnt")

        self.eyeJntChain(lidFactor, lBaseJnt)
        cmds.parent(lBaseJnt, w=1)
        rBaseJnt = cmds.mirrorJoint(lBaseJnt, mirrorYZ=True, mirrorBehavior=1, searchReplace=('l_', 'r_'))[0]

        cmds.parent(lBaseJnt, prefixDict["l_"])
        cmds.parent(rBaseJnt, prefixDict["r_"])

    def eyeJntChain(self, lidFactor, baseJnt):

        cornerVtx = cmds.getAttr(lidFactor + ".l_cornerVerts")

        for upLow in ["up", "lo"]:

            if not cmds.attributeQuery("l_{}LidVerts".format(upLow), node=lidFactor, exists=1):
                raise RuntimeError("store lid vertices in order first!!")

            self.orderedVerts["l_{}".format(upLow)] = cmds.getAttr("{}.l_{}LidVerts".format(lidFactor, upLow))
            self.orderedVerts["r_{}".format(upLow)] = cmds.getAttr("{}.r_{}LidVerts".format(lidFactor, upLow))

            for LR, val in {"l_": 1, "r_": -1}.items():
                self.polyCrvDict["{}{}".format(LR, upLow)] = self.createPolyToCurve(
                    self.orderedVerts["{}{}".format(LR, upLow)], name="{}{}Eye_guide".format(LR, upLow), direction=val)

                length = len(self.orderedVerts["{}{}".format(LR, upLow)])
                cmds.rebuildCurve(self.polyCrvDict["{}{}".format(LR, upLow)], ch=1, rebuildType=0, spans=length - 1,
                                  keepRange=0, keepControlPoints=1, degree=1)
                cmds.parent(self.polyCrvDict["{}{}".format(LR, upLow)], "guideCrv_grp")

            self.parameter[upLow] = face_utils.paramListFromCvDistance(self.polyCrvDict["{}{}".format("l_", upLow)])
            if not cmds.attributeQuery("{}ParamPolyCrv".format(upLow), node="lidFactor", exists=1):
                cmds.addAttr("lidFactor", ln="{}ParamPolyCrv".format(upLow), dt="stringArray")

            cmds.setAttr("lidFactor.{}ParamPolyCrv".format(upLow), type="stringArray",
                         *([len(self.parameter[upLow])] + self.parameter[upLow]))

            ordered = self.orderedVerts["l_{}".format(upLow)]
            ordered.remove(cornerVtx[0])
            ordered.remove(cornerVtx[1])

            for index, vtx in enumerate(ordered):
                vertPos = cmds.xform(vtx, t=True, q=True, ws=True)

                order = str(index+1).zfill(2)
                baseName = EyeRig.namingMethod("l_", upLow, "LidBase", order)
                blinkJnt, wideJnt = self.eyeJntOnVtx(baseJnt, baseName, vertPos)

                self.blinkJntDict["l_" + upLow].append(blinkJnt)
                self.blinkJntDict["r_" + upLow].append(blinkJnt.replace("l_", "r_"))
                self.wideJntDict["l_" + upLow].append(wideJnt)
                self.wideJntDict["r_" + upLow].append(wideJnt.replace("l_", "r_"))

            if not cmds.attributeQuery("l_{}WideJnt".format(upLow), node="lidFactor", exists=1):
                cmds.addAttr("lidFactor", ln="l_{}WideJnt".format(upLow), dt="stringArray")
                cmds.addAttr("lidFactor", ln="r_{}WideJnt".format(upLow), dt="stringArray")

            cmds.setAttr("lidFactor.l_{}WideJnt".format(upLow), type="stringArray",
                         *([len(self.wideJntDict["l_" + upLow])] + self.wideJntDict["l_" + upLow]))
            cmds.setAttr("lidFactor.r_{}WideJnt".format(upLow), type="stringArray",
                         *([len(self.wideJntDict["r_" + upLow])] + self.wideJntDict["r_" + upLow]))

        inout = ["In", "Out"]
        for index, vtx in enumerate(cornerVtx):
            vertPos = cmds.xform(vtx, t=True, q=True, ws=True)
            position = [vertPos[0], vertPos[1], vertPos[2]]

            order = "{}Corner".format(inout[index])
            cornerBaseName = EyeRig.namingMethod("l_", "", "lidBase", order)
            cornerJnt, cornerWideJnt = self.eyeJntOnVtx(baseJnt, cornerBaseName, position)

            self.eyeCornerDict["l_"].append(cornerJnt)
            self.eyeWideCornerDict["l_"].append(cornerWideJnt)

        if not cmds.attributeQuery("l_wideCornerJnt", node="lidFactor", exists=1):
            cmds.addAttr("lidFactor", ln="l_wideCornerJnt", dt="stringArray")
            cmds.addAttr("lidFactor", ln="r_wideCornerJnt", dt="stringArray")

        cmds.setAttr("lidFactor.l_wideCornerJnt", type="stringArray", *([len(self.eyeWideCornerDict["l_"])] +
                                                                        self.eyeWideCornerDict["l_"]))

        cmds.setAttr("lidFactor.r_wideCornerJnt", type="stringArray", *([len(self.eyeWideCornerDict["r_"])] +
                                                                        self.eyeWideCornerDict["r_"]))

    def eyeJntOnVtx(self, baseJnt, title, position):
        #joint oj = "xyz" x-forward
        cmds.select(baseJnt, r=1)
        cmds.joint(n=title.replace("idBase", "idP"))
        blinkJnt = cmds.joint(n=title.replace("idBase", "idBlink"))
        lidJnt = cmds.joint(n=title.replace("idBase", "index"))
        cmds.xform(lidJnt, ws=1, t=position)
        #cmds.joint(blinkJnt, e=True, zso=True, oj='xyz', sao='yup')

        cmds.joint(n=title.replace("idBase", "idTip"))

        wideJnt = cmds.duplicate(blinkJnt, po=True, n=title.replace("idBase", "idWide"))[0]

        lengthTz = cmds.getAttr("{}.tz".format(lidJnt))
        cmds.setAttr("{}.tz".format(lidJnt), lengthTz * 0.9)

        return [blinkJnt, wideJnt]

    def jntLabel(self, LR, jnt, **kwargs):

        if kwargs["position"]:
            upLow = kwargs["position"]
        elif kwargs["order"]:
            order = kwargs["order"]

        name = "{}{}_{}".format(LR, upLow, order)
        cmds.setAttr(jnt + '.side', 1)
        cmds.setAttr(jnt + '.type', 18)
        cmds.setAttr(jnt + '.otherType', name, type="string")

    def eyeCrvSetup(self, numOfCtl):

        if not cmds.objExists('eyeCrv_grp'):
            cmds.group(n='eyeCrv_grp', em=True, p='faceMain|crv_grp')

        self.reverseMult = cmds.shadingNode('multiplyDivide', asUtility=True, n="lidRotFactor_reverseMult")
        cmds.connectAttr("lidFactor.lidRotateX_scale", '{}.input1X'.format(self.reverseMult))
        cmds.connectAttr("lidFactor.lidRotateY_scale", '{}.input1Y'.format(self.reverseMult))
        cmds.connectAttr("r_lidScale_ctl.tx", "{}.input1Z".format(self.reverseMult))
        cmds.setAttr('{}.input2'.format(self.reverseMult), -1, -1, -1)

        for LR, val in {"l_": 1, "r_": -1}.items():

            baseJnt = "{}eyeBaseJnt".format(LR)
            cmds.connectAttr("{}lidScale_ctl.rz".format(LR), "{}.rz".format(baseJnt))

            for upLow in ["up", "lo"]:

                tempBSCrv = cmds.curve(d=3, p=([0, 0, 0], [0.25*val, 0, 0], [0.5*val, 0, 0], [0.75*val, 0, 0],
                                               [1*val, 0, 0]))
                cmds.rebuildCurve(rebuildType=0, spans=numOfCtl - 1, keepRange=0, keepControlPoints=0, degree=1)
                shapeCrv = cmds.rename(tempBSCrv, '{}{}Shape_crv'.format(LR, upLow))

                tempRollCrv = cmds.curve(d=3, p=([0, 0, 0], [0.25*val, 0, 0], [0.5*val, 0, 0], [0.75*val, 0, 0],
                                                 [1*val, 0, 0]))
                cmds.rebuildCurve(rebuildType=0, spans=numOfCtl - 3, keepRange=0, keepControlPoints=0, degree=3)
                lidRollCrv = cmds.rename(tempRollCrv, '{}{}LidRoll_crv'.format(LR, upLow))
                lidRollCrvShape = cmds.listRelatives(lidRollCrv, c=1)[0]

                tmpSclCrv = cmds.curve(d=3, p=([0, 1, 1], [0.25*val, 1, 1], [0.5*val, 1, 1], [0.75*val, 1, 1],
                                               [1*val, 1, 1]))
                cmds.rebuildCurve(rebuildType=0, spans=numOfCtl - 3, keepRange=0, keepControlPoints=0, degree=3)
                lidScaleCrv = cmds.rename(tmpSclCrv, '{}{}LidScale_crv'.format(LR, upLow))
                lidScaleCrvShape = cmds.listRelatives(lidScaleCrv, c=1)[0]

                # HiCrv setup for blink/open
                length = len(self.orderedVerts["{}{}".format(LR, upLow)])
                # tempPosList = []
                # for idx, param in enumerate(self.parameter[upLow]):
                #     poc = self.createPocNode("paramPoc{}".format(str(idx).zfill(2)), lidRollCrvShape, param)
                #     position = cmds.getAttr("{}.position".format(poc))[0]
                #     tempPosList.append(position)
                #
                # positionList = [[x[0]*val, x[1], x[2]] for x in tempPosList]
                #
                # tempHiCrv = cmds.curve(d=1, p=positionList)
                tempHiCrv = cmds.curve(d=1, p=([0, 0, 0], [0.25 * val, 0, 0], [0.5 * val, 0, 0], [0.75 * val, 0, 0],
                                               [1 * val, 0, 0]))
                cmds.rebuildCurve(rebuildType=0, spans=length - 1, keepRange=0, keepControlPoints=0, degree=1)
                eyeHiCrv = cmds.rename(tempHiCrv, '{}{}Hi_crv'.format(LR, upLow))
                eyeHiCrvShape = cmds.listRelatives(eyeHiCrv, c=1)[0]

                targetList = ["CTL", "ALid", "BLid", "CLid", "DLid", "Squint", "Annoyed"]
                targetCrvs = self.lidBlendShape(shapeCrv, targetList)

                hiCrvWire = cmds.wire(eyeHiCrv, w=shapeCrv, n="{}{}lidBS_wire".format(LR, upLow))
                cmds.setAttr("{}.dropoffDistance[0]".format(hiCrvWire[0]), 2)

                blinkCrv = cmds.duplicate(eyeHiCrv, rc=1, n="{}{}Blink_crv".format(LR, upLow))[0]
                openCrv = cmds.duplicate(eyeHiCrv, rc=1, n="{}{}Open_crv".format(LR, upLow))[0]
                blinkCrvBS = cmds.blendShape(blinkCrv, openCrv, eyeHiCrv, n=eyeHiCrv.replace("_crv", "Crv_BS"))

                cmds.parent(shapeCrv, eyeHiCrv, blinkCrv, openCrv, "eyeCrv_grp")

                if not cmds.objExists("{}{}ShapeCrv_grp".format(LR, upLow)):
                    cmds.group(n="{}{}Crv_grp".format(LR, upLow), em=True, p='eyeCrv_grp')

                crvGrp = "{}{}Crv_grp".format(LR, upLow)
                cmds.parent(targetCrvs, lidRollCrv, lidScaleCrv, crvGrp)

                if not self.parameter[upLow]:
                    self.parameter[upLow] = cmds.getAttr("lidFactor.{}ParamPolyCrv".format(upLow))

                blinkList = self.blinkJntDict["{}{}".format(LR, upLow)]
                wideList = self.wideJntDict["{}{}".format(LR, upLow)]
                for index, jntPair in enumerate(zip(blinkList, wideList)):
                    blinkJnt = jntPair[0]
                    wideJnt = jntPair[1]
                    index += 1
                    pocName = blinkJnt.replace("Blink", "Poc")
                    poc = self.createPocNode(pocName, eyeHiCrvShape, self.parameter[upLow][index])

                    rollPocName = blinkJnt.replace("Blink", "RollPoc")
                    lidRollPoc = self.createPocNode(rollPocName, lidRollCrvShape, self.parameter[upLow][index])

                    scalePocName = blinkJnt.replace("Blink", "ScalePoc")
                    lidScalePoc = self.createPocNode(scalePocName, lidScaleCrvShape, self.parameter[upLow][index])

                    self.connectEyeJoint(poc, lidRollPoc, lidScalePoc, blinkJnt, wideJnt)

            for idx, jntPair in enumerate(zip(self.eyeCornerDict[LR], self.eyeWideCornerDict[LR])):
                crnJnt = jntPair[0]
                crnWideJnt = jntPair[1]
                pocName = crnJnt.replace("Blink", "Poc")
                poc = self.createPocNode(pocName, eyeHiCrv, idx)

                rollPocName = crnJnt.replace("Blink", "RollPoc")
                lidRollPoc = self.createPocNode(rollPocName, lidRollCrvShape, idx)

                scalePocName = crnJnt.replace("Blink", "ScalePoc")
                scalePoc = self.createPocNode(scalePocName, lidScaleCrvShape, idx)

                self.connectEyeJoint(poc, lidRollPoc, scalePoc, crnJnt, crnWideJnt)

            # face_utils.Util.mirrorCurve(LRPair[0], LRPair[1])

    def connectEyeJoint(self, poc, lidRollPoc, lidScalePoc, lidJnt, wideJnt):

        rollJnt = lidJnt.replace("Blink", "Tip")

        rotMult = cmds.shadingNode('multiplyDivide', asUtility=True, n=lidJnt.replace("Blink", "Mult"))
        rotPlus = cmds.shadingNode('plusMinusAverage', asUtility=True, n=lidJnt.replace("Blink", "Plus"))
        wideMult = cmds.shadingNode('multiplyDivide', asUtility=True, n=lidJnt.replace("Blink", "WideMult"))
        wideRXCond = cmds.shadingNode("condition", asUtility=1, n=lidJnt.replace("Blink", "WideCond"))
        wideRotSum = cmds.shadingNode('plusMinusAverage', asUtility=True, n=lidJnt.replace("Blink", "WidePlus"))
        initialX = cmds.getAttr(poc + '.positionX')

        # lidJnt rotationXY connection
        LR = lidJnt[:2]
        cmds.setAttr('{}.operation'.format(rotPlus), 1)
        cmds.connectAttr("{}lidScale_ctl.ty".format(LR), '{}.input3D[0].input3Dy'.format(rotPlus))
        cmds.connectAttr("{}.positionY".format(poc), '{}.input3D[1].input3Dy'.format(rotPlus))

        cmds.connectAttr(rotPlus + '.output3Dy', '{}.input1X'.format(rotMult))
        #'self.reverseMult X == "lidFactor.lidRotateX_scale" * -1
        cmds.connectAttr('{}.outputX'.format(self.reverseMult), '{}.input2X'.format(rotMult))
        cmds.connectAttr('{}.outputX'.format(rotMult), '{}.rx'.format(lidJnt))

        cmds.connectAttr("{}lidScale_ctl.tx".format(LR), '{}.input3D[0].input3Dx'.format(rotPlus))
        cmds.connectAttr("{}.positionX".format(poc), '{}.input3D[1].input3Dx'.format(rotPlus))
        cmds.setAttr('{}.input3D[2].input3Dx'.format(rotPlus), initialX*-1)
        cmds.connectAttr('{}.output3Dx'.format(rotPlus), '{}.input1Y'.format(rotMult))
        cmds.connectAttr("lidFactor.lidRotateY_scale", '{}.input2Y'.format(rotMult))
        cmds.connectAttr('{}.outputY'.format(rotMult), '{}.ry'.format(lidJnt))

        # LidRoll_rotationX connection( lidRoll_jnt.rz = lidRoll_poc.ty )
        cmds.connectAttr("{}.positionY".format(lidRollPoc), rollJnt + '.rx')

        cmds.connectAttr(lidScalePoc + '.positionY', rollJnt + '.sy')
        cmds.connectAttr(lidScalePoc + '.positionZ', rollJnt + '.sz')

        #wideJnt follow setup (greater than)
        cmds.connectAttr("{}.rx".format(lidJnt), "{}.input1X".format(wideMult))
        cmds.connectAttr("{}.ry".format(lidJnt), "{}.input1Y".format(wideMult))
        cmds.connectAttr("{}.rx".format(lidJnt), "{}.input1Z".format(wideMult))
        # followUp = 0.6 / followDown = 0.1
        cmds.connectAttr("lidFactor.eyeWide_followUp", "{}.input2X".format(wideMult))
        cmds.connectAttr("lidFactor.eyeWide_followUp", "{}.input2Y".format(wideMult))
        cmds.connectAttr("lidFactor.eyeWide_followDown", "{}.input2Z".format(wideMult))

        cmds.connectAttr('{}.rx'.format(lidJnt), wideRXCond + ".firstTerm")
        cmds.setAttr(wideRXCond + ".secondTerm", 0)
        cmds.setAttr(wideRXCond + ".operation", 4)

        # wideJnt up/down setup (rotation value)
        cmds.connectAttr('{}.outputX'.format(wideMult), "{}.colorIfTrueR".format(wideRXCond))
        cmds.connectAttr('{}.outputZ'.format(wideMult), "{}.colorIfFalseR".format(wideRXCond))

        cmds.connectAttr("{}.outColorR".format(wideRXCond), "{}.input3D[0].input3Dx".format(wideRotSum))
        cmds.connectAttr("{}.output3Dx".format(wideRotSum), '{}.rx'.format(wideJnt))

        # wideJnt left/right setup (rotation value)
        cmds.connectAttr('{}.outputY'.format(wideMult), "{}.input3D[0].input3Dy".format(wideRotSum))
        cmds.connectAttr("{}.output3Dy".format(wideRotSum), '{}.ry'.format(wideJnt))

    def eyeWideCrvSetup(self):

        if not cmds.attributeQuery("l_upLidVerts", node="lidFactor", exists=1):
            raise RuntimeError("store eyeLid vertices first!!")

        if not cmds.attributeQuery("l_upWideJnt", node="lidFactor", exists=1):
            raise RuntimeError("store wideJoint list first!!")

        for LR, val in {"l_": 1, "r_": -1}.items():
            for upLow in ["up", "lo"]:

                if not self.orderedVerts[LR + upLow]:
                    if LR == "l_":
                        self.orderedVerts["l_{}".format(upLow)] = cmds.getAttr("lidFactor.l_{}LidVerts".format(upLow))
                    elif LR == "r_":
                        self.orderedVerts["r_{}".format(upLow)] = cmds.getAttr("lidFactor.r_{}LidVerts".format(upLow))

                if not self.parameter[upLow]:
                    self.parameter[upLow] = cmds.getAttr("lidFactor.{}ParamPolyCrv".format(upLow))

                tempWideCrv = cmds.curve(d=3, p=([0, 0, 0], [0.25*val, 0, 0], [0.5*val, 0, 0], [0.75*val, 0, 0],
                                                 [1*val, 0, 0]))
                cmds.rebuildCurve(rebuildType=0, spans=2, keepRange=0, keepControlPoints=0, degree=3)
                wideCrv = cmds.rename(tempWideCrv, '{}{}Wide_crv'.format(LR, upLow))
                wideCrvShape = cmds.listRelatives(wideCrv, c=1)[0]

                targetList = ["ALid", "BLid", "CLid", "DLid", "Squint", "Annoyed", "Blink", "Open"]
                wideShpCrvs = self.lidBlendShape(wideCrv, targetList)
                cmds.parent(wideShpCrvs, "{}{}Crv_grp".format(LR, upLow))
                cmds.parent(wideCrv, "eyeCrv_grp")

                if not self.wideJntDict[LR+upLow]:
                    self.wideJntDict[LR+upLow] = cmds.getAttr("lidFactor.{}{}WideJnt".format(LR, upLow))

                for index, wideJnt in enumerate(self.wideJntDict[LR+upLow]):

                    index += 1
                    widePocName = wideJnt.replace("LidWide", "WidePoc")
                    widePoc = self.createPocNode(widePocName, wideCrvShape, float(self.parameter[upLow][index]))

                    self.eyeWideCrvToJoint(widePoc, wideJnt)

            if not self.eyeWideCornerDict[LR]:
                self.eyeWideCornerDict[LR] = cmds.getAttr("lidFactor.{}wideCornerJnt".format(LR))

            cornerList = self.eyeWideCornerDict[LR]

            for idx, cornerJnt in enumerate(cornerList):

                cornerPocName = cornerJnt.replace("LidWide", "WidePoc")
                cornerPoc = self.createPocNode(cornerPocName, wideCrvShape, idx)

                self.eyeWideCrvToJoint(cornerPoc, cornerJnt)

    def eyeWideCrvToJoint(self, widePoc, wideJnt):

        wideMult = cmds.shadingNode('multiplyDivide', asUtility=True, n=wideJnt.replace("LidWide", "WideMult"))
        addDouble = cmds.shadingNode('addDoubleLinear', asUtility=True, n=wideJnt.replace("LidWide", "WideAdd"))
        wideSum = cmds.listConnections(wideJnt, s=1, d=0, t="plusMinusAverage", scn=1)[0]
        initialX = cmds.getAttr(widePoc + '.positionX')

        # wideJnt rotationZ(up/down) connection with curve
        cmds.connectAttr("{}.positionY".format(widePoc), '{}.input1Y'.format(wideMult))
        cmds.connectAttr("lidFactor.lidRotateX_scale", '{}.input2Y'.format(wideMult))
        cmds.connectAttr('{}.outputX'.format(wideMult), "{}.input3D[1].input3Dx".format(wideSum))

        # wideJnt rotationY(left/right) connection with curve
        cmds.connectAttr("{}.positionX".format(widePoc), "{}.input1".format(addDouble))
        cmds.setAttr("{}.input2".format(addDouble), initialX*-1)
        cmds.connectAttr("{}.output".format(addDouble), '{}.input1X'.format(wideMult))
        cmds.connectAttr("lidFactor.lidRotateY_scale", '{}.input2X'.format(wideMult))
        cmds.connectAttr('{}.outputY'.format(wideMult), "{}.input3D[1].input3Dy".format(wideSum))

        cmds.connectAttr("{}.positionZ".format(widePoc), '{}.tz'.format(wideJnt))

    def lidBlendShape(self, ctlCrv, targetList):

        trgCrvList = []
        for target in targetList:  # l_upALid_crv
            dupCrv = cmds.duplicate(ctlCrv, rc=1, n=ctlCrv.replace("crv", target))[0]
            trgCrvList.append(dupCrv)

        lidCrvBS = cmds.blendShape(trgCrvList, ctlCrv, n=ctlCrv.replace("crv", "BS"))
        weightList = [(x, 1) for x in range(len(targetList))]
        cmds.blendShape(lidCrvBS[0], edit=True, w=weightList)

        return trgCrvList

    def eyeRigBuild(self, numOfCtl):

        self.eyeJointSetup()
        self.eyeCrvSetup(numOfCtl)
        self.eyeCtlJntOnCrv()
        self.eyeLidFreeCtl(numOfCtl, "nurbsSphere")
        eyeJntLabel("Blink")
        eyeJntLabel("Wide")

    def eyeWideLayerBuild(self):
        self.eyeWideCrvSetup()
        #self.eyeWideCrvToJoint()

    def eyeCtlJntOnCrv(self):

        if not cmds.objExists("eyeCtl_jntGrp"):
            cmds.group(n="eyeCtl_jntGrp", em=True, p='faceMain|jnt_grp')
        eyeCtlJntGrp = "eyeCtl_jntGrp"

        InOut = {"l_": {"in": 0, "out": 1}, "r_": {"in": 0, "out": -1}}
        for LR, mult in {"l_": 1, "r_": -1}.items():

            eyeJntGrp = cmds.group(n="{}eye_jntGrp".format(LR), em=True, p=eyeCtlJntGrp)
            cornerJnts = []
            for inout, val in InOut[LR].items():

                name = "{}{}CornerCtl_jnt".format(LR, inout)
                null = cmds.group(em=1, n=name.replace("_jnt", "_jntP"), p=eyeJntGrp)
                cmds.xform(null, ws=1, t=(val, 0, 0))
                cornerJnt = cmds.joint(n=name)
                cornerJnts.append(cornerJnt)

            for upLow in ["up", "lo"]:

                crv = "{}{}Shape_crv".format(LR, upLow)
                name = "{}{}CenterCtl_jnt".format(LR, upLow)
                null = cmds.group(em=1, n=name.replace("_jnt", "_jntP"), p=eyeJntGrp)
                cmds.xform(null, ws=1, t=(0.5 * mult, 0, 0))
                jnt = cmds.joint(n=name)

                #bindMethod=cloestDistance
                bindJnt = [jnt] + cornerJnts
                cmds.skinCluster(crv, bindJnt, bindMethod=0, normalizeWeights=1, weightDistribution=0, mi=3, omi=True, tsb=1)

    def eyeLidFreeCtl(self, numOfCtl, myCtl):

        dist = cmds.getAttr("helpPanel_grp.headBBox")

        if not myCtl:
            temp = self.genericController("genericCtl", (0, 0, 0), dist[1]/120.0, "circle", self.colorIndex["purple"][0])
            myCtl = temp

        prefixDict = {"l_": 1, "r_": -1}
        for LR, val in prefixDict.items():

            if not cmds.objExists("{}eyeSticky_grp".format(LR)):
                cmds.group(n="{}eyeSticky_grp".format(LR), em=True)
            lidCtlGrp = "{}eyeSticky_grp".format(LR)

            rollCvs = {}
            puffCvs = {}
            CTLCrvCvs = {}
            for idx, upLow in enumerate(["up", "lo"]):

                polyCrv = self.polyCrvDict[LR + upLow]
                tempGuideCrv = cmds.duplicate(polyCrv, n="{}{}tempGuide_crv".format(LR, upLow), rc=1)[0]
                cmds.rebuildCurve(tempGuideCrv, rebuildType=0, spans=numOfCtl - 1, keepRange=0, degree=3)
                tempGuideCrvSahpe = cmds.listRelatives(tempGuideCrv, c=1)[0]
                parameters = []
                tempParam = 1.0/(numOfCtl-1)
                for i in range(numOfCtl):

                    tempPoc = self.createPocNode("tempPoc{}".format(str(i+1)), tempGuideCrvSahpe, tempParam * i)
                    position = cmds.getAttr("{}.position".format(tempPoc))[0]
                    param = self.getUParam(pntPos=position, crv=polyCrv)
                    parameters.append(param)

                cmds.delete(tempGuideCrv)

                eyeRollCrv = "{}{}LidRoll_crv".format(LR, upLow)
                eyePuffCrv = "{}{}LidScale_crv".format(LR, upLow)
                shapeCTLCrv = "{}{}Shape_CTL".format(LR, upLow)

                rollCvs[LR + upLow] = cmds.ls(eyeRollCrv + ".cv[*]", fl=1)
                puffCvs[LR + upLow] = cmds.ls(eyePuffCrv + ".cv[*]", fl=1)
                CTLCrvCvs[LR + upLow] = cmds.ls(shapeCTLCrv + ".cv[*]", fl=1)

                offSetVal = dist[1]/100.0
                colorID = self.colorIndex["red"][idx]
                prmList = parameters[1:-1]
                centerParam = parameters[(len(parameters)-1)/2]

                for index, prm in enumerate(prmList):

                    index += 1
                    name = self.namingMethod(LR, upLow, "Eye", str(index).zfill(2), "ctl")
                    ctlChain = self.createMidController(name, dist[1] / 50.0, myCtl, param=prm, guideCrv=polyCrv,
                                                        colorID=colorID)
                    ctl, offset, null, poc = [ctlChain[0], ctlChain[1], ctlChain[2], ctlChain[3]]
                    cmds.setAttr(offset + ".tz", offSetVal)
                    cmds.setAttr("{}.sx".format(offset), val)

                    if prm == centerParam:
                        broadCtl = self.genericController("{}{}CenterCtl".format(LR, upLow), (0, 0, 0), dist[1] / 150.0,
                                                          "circle", self.ctlColor["pink"])
                        centerCtl, offCtl = face_utils.addOffset(broadCtl)
                        #cmds.connectAttr("{}.position".format(poc), "{}.t".format(offCtl))
                        ctlJnt = "{}{}CenterCtl_jnt".format(LR, upLow)
                        cmds.parent(offCtl, null)
                        cmds.setAttr(offCtl + ".tx", 0)
                        cmds.setAttr(offCtl + ".ty", 0)
                        cmds.setAttr(offCtl + ".tz", offSetVal*2)
                        cmds.setAttr("{}.sx".format(offCtl), val)
                        cmds.connectAttr("{}.t".format(centerCtl), "{}.t".format(ctlJnt))
                        cmds.connectAttr("{}.r".format(centerCtl), "{}.r".format(ctlJnt))

                    self.eyeCtlToCvs(ctl, CTLCrvCvs[LR + upLow][index], rollCvs[LR + upLow][index],
                                     puffCvs[LR + upLow][index])

                    cmds.parent(null, lidCtlGrp)

                    self.eyeCtlList.append(ctl)
                    self.eyePocList.append(poc)

            #corner ctl connection
            colorIndex = self.ctlColor["pink"]
            cornerCtlDict = {"inCorner": 0, "outCorner": numOfCtl-1}
            for position, value in cornerCtlDict.items():

                name = self.namingMethod(LR, "", "lid", position, "ctl")
                ctlChain = self.createMidController(name, dist[1] / 50.0, myCtl, param=parameters[value],
                                                    guideCrv=polyCrv, colorID=colorIndex)
                ctl, offset, null, poc = [ctlChain[0], ctlChain[1], ctlChain[2], ctlChain[3]]
                cmds.setAttr(offset + ".tz", offSetVal)
                cmds.setAttr("{}.sx".format(offset), val)

                broadCtl = self.genericController("{}{}Ctl".format(LR, position), (0, 0, 0), dist[1] / 150.0,
                                                  "circle", colorIndex)
                cornerCtl, offsetCtl = face_utils.addOffset(broadCtl)
                cmds.parent(offsetCtl, null)
                cmds.setAttr(offsetCtl + ".tx", 0)
                cmds.setAttr(offsetCtl + ".ty", 0)
                cmds.setAttr(offsetCtl + ".tz", offSetVal*2)
                cmds.setAttr("{}.sx".format(offsetCtl), val)

                #cmds.connectAttr("{}.position".format(poc), "{}.t".format(offCtl))
                # broad Ctl connections
                ctlJnt = "{}{}Ctl_jnt".format(LR, position)
                cmds.connectAttr("{}.t".format(cornerCtl), "{}.t".format(ctlJnt))
                cmds.connectAttr("{}.r".format(cornerCtl), "{}.r".format(ctlJnt))

                cmds.parent(null, lidCtlGrp)

                for upLow in ["up", "lo"]:
                    # mid Ctl connections
                    self.eyeCtlToCvs(ctl, CTLCrvCvs[LR + upLow][value], rollCvs[LR + upLow][value], puffCvs[LR + upLow][value])

                self.eyeCtlList.append(ctl)
                self.eyePocList.append(poc)

            cmds.parent(lidCtlGrp, "attachCtl_grp")

    def eyeCtlToCvs(self, ctl, ctlCv, rollCv, puffCv):

        addCtlDouble = cmds.shadingNode('addDoubleLinear', asUtility=True, n=ctl.replace("ctl", "add"))
        ctlTx = cmds.getAttr("{}.xValue".format(ctlCv))
        cmds.setAttr("{}.input2".format(addCtlDouble), ctlTx)
        cmds.connectAttr("{}.tx".format(ctl), "{}.input1".format(addCtlDouble))
        cmds.connectAttr("{}.output".format(addCtlDouble), "{}.xValue".format(ctlCv))
        cmds.connectAttr("{}.ty".format(ctl), "{}.yValue".format(ctlCv))
        cmds.connectAttr("{}.tz".format(ctl), "{}.zValue".format(ctlCv))

        cmds.connectAttr("{}.rx".format(ctl), "{}.yValue".format(rollCv))

        cmds.connectAttr("{}.sy".format(ctl), "{}.yValue".format(puffCv))
        cmds.connectAttr("{}.sz".format(ctl), "{}.zValue".format(puffCv))
