import maya.cmds as cmds
from twitchScript.face import face_utils
reload(face_utils)

class EyeRig(face_utils.Util):

    def __init__(self):

        super(EyeRig, self).__init__()
        self.blinkJntDict = {"l_up": [], "l_lo": [], "r_up": [], "r_lo": []}
        self.wideJntDict = {"l_up": [], "l_lo": [], "r_up": [], "r_lo": []}
        self.eyeCornerDict = {"l_": [], "r_": []}
        self.eyeWideCornerDict = {"l_": [], "r_": []}
        self.reverseMult = None
        self.parameter = None
        self.orderedVerts = []
        self.eyeCtlList = []
        self.eyePocList = []

    def eyelidJoints(self, upLowLR ):
        # lEyePos Rotate Order : XZY
        if not cmds.objExists('lEyePos'):
            raise RuntimeError("import the face locators")

        eyeRotY = cmds.getAttr ('lEyePos.ry' )
        eyeRotZ = cmds.getAttr ('lEyePos.rz' )
        eyeCenterPos = cmds.xform( 'lEyePos', t = True, q = True, ws = True)

        lidFactor = self.faceFactors
        mirrorLR = upLowLR.replace("l_" ,"r_")
        if "_up" in upLowLR:
            lEyeLoc = cmds.duplicate( "lEyePos", rr=1, rc=1, n= "l_eyeUp_loc")[0]
            cmds.xform( lEyeLoc, ws=1, t=[eyeCenterPos[0], eyeCenterPos[1 ] *2, eyeCenterPos[2]] )
            rEyeLoc = cmds.duplicate( lEyeLoc, n= lEyeLoc.replace("l_" ,"r_"))[0]
            cmds.xform( rEyeLoc, ws=1, t=[-eyeCenterPos[0], eyeCenterPos[1 ] *2, eyeCenterPos[2]] )

        ordered = []
        if "up" in upLowLR:
            if cmds.attributeQuery("upLidVerts", node = lidFactor, exists=1):
                ordered = cmds.getAttr( lidFactor + ".upLidVerts")
            else:
                cmds.confirmDialog( title='Confirm', message= "store lid vertices in order first!!")
        elif "lo" in upLowLR:
            if cmds.attributeQuery("loLidVerts", node = "lidFactor", exists=1):
                ordered = cmds.getAttr( lidFactor + ".loLidVerts")
                ordered.pop(0), ordered.pop(-1)
            else:
                cmds.confirmDialog( title='Confirm', message="store lid vertices in order first!!" )

        # create parent group for eyelid joints
        if not cmds.objExists('eyeJnt_grp'):
            cmds.group ( n = 'eyeJnt_grp', em =True, p ="jnt_grp" )
        null = cmds.group ( n = upLowLR +'EyeJnt_grp', em =True, p ="eyeJnt_grp" )
        rNull = cmds.group ( n = mirrorLR +'EyeJnt_grp', em=True, p="eyeJnt_grp")
        cmds.select(cl=True)

        lLidGrp = cmds.group(n=upLowLR + 'LidP_grp', em=True, p=null)
        cmds.xform(lLidGrp, ws=1, t=eyeCenterPos)
        cmds.setAttr(lLidGrp + ".rotateOrder", 3)
        cmds.setAttr(lLidGrp + '.ry', eyeRotY)
        cmds.setAttr(lLidGrp + '.rz', eyeRotZ)
        lLidJntP = cmds.joint(n=upLowLR + 'LidP_jnt')

        rLidGrp = cmds.group(n=mirrorLR + 'LidP_grp', em=True, p=rNull)
        cmds.xform(rLidGrp, ws=1, t=[-eyeCenterPos[0], eyeCenterPos[1], eyeCenterPos[2]])
        cmds.setAttr(rLidGrp + ".rotateOrder", 3)
        cmds.setAttr(rLidGrp + '.ry', -eyeRotY)
        cmds.setAttr(rLidGrp + '.rz', -eyeRotZ)
        # rLidJntP = cmds.joint(n = mirrorLR + 'LidP_jnt' )

        cmds.select(cl=1)
        # UI for 'null.rx/ry/rz'?? cmds.setAttr ( null + '.rz', eyeRotZ )
        index = 1
        for v in ordered:
            vertPos = cmds.xform(v, t=True, q=True, ws=True)

            # create constraint locator
            loc = cmds.spaceLocator(n=upLowLR + 'Loc' + str(index).zfill(2))[0]
            cmds.parent(loc, null)
            cmds.xform(loc, ws=1, t=vertPos)
            cmds.setAttr(loc + ".visibility", 0)

            rLoc = cmds.spaceLocator(n=mirrorLR + 'Loc' + str(index).zfill(2))[0]
            cmds.parent(rLoc, rNull)
            cmds.xform(rLoc, ws=1, t=[-vertPos[0], vertPos[1], vertPos[2]])
            cmds.setAttr(rLoc + ".visibility", 0)

            # create eyeJoint chain
            cmds.select(lLidJntP)
            scaleJnt = cmds.joint(n=upLowLR + 'LidScale' + str(index).zfill(2) + '_jnt')
            # cmds.parent ( scaleJnt, lLidJntP )
            blinkJnt = cmds.joint(n=upLowLR + 'LidBlink' + str(index).zfill(2) + '_jnt')
            lidJnt = cmds.joint(n=upLowLR + 'Lid' + str(index).zfill(2) + '_jnt')
            cmds.xform(lidJnt, ws=1, t=vertPos)
            lidJntTX = cmds.joint(n=upLowLR + 'LidTX' + str(index).zfill(2) + '_jnt')

            # cmds.joint ( scaleJnt, e =True, ch=True, zso =True, oj = 'zyx', sao= 'yup')
            wideJnt = cmds.duplicate(blinkJnt, po=True, n=upLowLR + 'LidWide' + str(index).zfill(2) + '_jnt')[0]
            # cmds.parent ( wideJnt, scaleJnt )
            index = index + 1

        cmds.parent(lLidJntP, w=1)
        rLidJntP = cmds.mirrorJoint(lLidJntP, myz=True, mirrorBehavior=1, searchReplace=('l_', 'r_'))[0]
        cmds.parent(lLidJntP, lLidGrp)
        cmds.parent(rLidJntP, rLidGrp)

        vtxLen = len(ordered)
        for i in range(vtxLen):
            lLoc = upLowLR + 'Loc' + str(i + 1).zfill(2)
            rLoc = mirrorLR + 'Loc' + str(i + 1).zfill(2)
            lBlink = upLowLR + 'LidBlink' + str(i + 1).zfill(2) + '_jnt'
            rBlink = mirrorLR + 'LidBlink' + str(i + 1).zfill(2) + '_jnt'
            cmds.aicmdsonstraint(lLoc, lBlink, mo=1, weight=1, aimVector=(0, 0, 1), upVector=(0, 1, 0),
                                 worldUpType="object", worldUpObject="l_eyeUp_loc")
            cmds.aicmdsonstraint(rLoc, rBlink, mo=1, weight=1, aimVector=(0, 0, 1), upVector=(0, 1, 0),
                                 worldUpType="object", worldUpObject="r_eyeUp_loc")

    def eyeJointSetup(self):

        if not cmds.objExists('lEyePos'):
            raise RuntimeError("import the face locators")

        eyeRot = cmds.xform("lEyePos", ws=1, q=1, ro=1)
        eyeCenterPos = cmds.xform( 'lEyePos', t = True, q = True, ws = True)

        lidFactor = self.faceFactors["eyelid"]
        if not cmds.attributeQuery("cornerVerts", node=lidFactor, exists=1):
            raise RuntimeError("store eyeLid vertices first!!")

        prefixDict = {"l_": 1, "r_": -1}
        for LR, val in prefixDict.items():

            eyeUpLoc = cmds.duplicate("lEyePos", rc=1, n="{}eyeUp_loc".format(LR))[0]
            cmds.setAttr("{}.r".format(eyeUpLoc), 0, 0, 0)
            eyeUpPos = [eyeCenterPos[0]*val, eyeCenterPos[1] * 2, eyeCenterPos[2]]
            cmds.xform(eyeUpLoc, ws=1, t=eyeUpPos)

            if not cmds.objExists('eyeJnt_grp'):
                cmds.group(n='eyeJnt_grp', em=True, p="eyeRig")
            jntGrp = cmds.group(n="{}eyeLid_grp".format(LR), em=True, p="eyeJnt_grp")

            eyeLocPos = [eyeCenterPos[0] * val, eyeCenterPos[1], eyeCenterPos[2]]
            cmds.xform(jntGrp, ws=1, t=eyeLocPos)
            cmds.setAttr(jntGrp + ".rotateOrder", 3)
            cmds.setAttr(jntGrp + '.ry', eyeRot[1]*val)
            cmds.setAttr(jntGrp + '.rz', eyeRot[2]*val)
            locGrp = cmds.group(n='{}eyeLoc_grp'.format(LR), em=True, p=jntGrp)
            cmds.setAttr(locGrp + ".visibility", 0)

            self.eyeJntChain(LR, val, lidFactor, jntGrp, locGrp)

    def eyeJntChain(self, LR, val, lidFactor, jntGrp, locGrp):

        cornerVtx = cmds.getAttr(lidFactor + ".cornerVerts")

        for upLow in ["up", "lo"]:

            if not cmds.attributeQuery("{}LidVerts".format(upLow), node=lidFactor, exists=1):
                raise RuntimeError("store lid vertices in order first!!")

            ordered = cmds.getAttr(lidFactor + ".{}LidVerts".format(upLow))
            ordered.remove(cornerVtx[0])
            ordered.remove(cornerVtx[1])

            cmds.select(cl=1)

            for index, vtx in enumerate(ordered):
                vertPos = cmds.xform(vtx, t=True, q=True, ws=True)
                position = [vertPos[0]*val, vertPos[1], vertPos[2]]

                order = str(index+1).zfill(2)
                baseName = EyeRig.namingMethod(LR, upLow, "LidBase", order)
                blinkJnt, wideJnt = self.eyeJntOnVtx(jntGrp, baseName, position)

                self.blinkJntDict[LR + upLow].append(blinkJnt)
                self.wideJntDict[LR + upLow].append(wideJnt)
                # cmds.aimConstraint(loc, blinkJnt, mo=1, weight=1, aimVector=(0, 0, 1), upVector=(0, 1, 0),
                #                    worldUpType="object", worldUpObject="{}eyeUp_loc".format(LR))

            if not cmds.attributeQuery("{}{}WideJnt".format(LR, upLow), node="lidFactor", exists=1):
                cmds.addAttr("lidFactor", ln="{}{}WideJnt".format(LR, upLow), dt="stringArray")

            cmds.setAttr("lidFactor.{}{}WideJnt".format(LR, upLow), type="stringArray",
                         *([len(self.wideJntDict[LR + upLow])] + self.wideJntDict[LR + upLow]))

        inout = ["In", "Out"]

        for index, vtx in enumerate(cornerVtx):
            vertPos = cmds.xform(vtx, t=True, q=True, ws=True)
            position = [vertPos[0] * val, vertPos[1], vertPos[2]]

            order = "{}Corner".format(inout[index])
            cornerBaseName = EyeRig.namingMethod(LR, "", "lidBase", order)
            cornerJnt, cornerWideJnt = self.eyeJntOnVtx(jntGrp, cornerBaseName, position)
            # cmds.aimConstraint(loc, blinkJnt, mo=1, weight=1, aimVector=(0, 0, 1), upVector=(0, 1, 0),
            #                    worldUpType="object", worldUpObject="{}eyeUp_loc".format(LR))

            self.eyeCornerDict[LR].append(cornerJnt)
            self.eyeWideCornerDict[LR].append(cornerWideJnt)

        if not cmds.attributeQuery("{}wideCornerJnt".format(LR), node="lidFactor", exists=1):
            cmds.addAttr("lidFactor", ln="{}wideCornerJnt".format(LR), dt="stringArray")

        cmds.setAttr("lidFactor.{}wideCornerJnt".format(LR), type="stringArray", *([len(self.eyeWideCornerDict[LR])] +
                                                                                   self.eyeWideCornerDict[LR]))

    def eyeJntOnVtx(self, jntGrp, title, position):
        #joint oj = "xyz" x-forward
        cmds.group(n=title, em=1, p=jntGrp)
        blinkJnt = cmds.joint(n=title.replace("idBase", "idBlink"))
        lidJnt = cmds.joint(n=title.replace("idBase", "index"))
        #lid joint oj = "zyx" z-forward(follow parent group(not parent joint) orientation)
        cmds.xform(lidJnt, ws=1, t=position)
        cmds.joint(blinkJnt, e=True, zso=True, oj='xyz', sao='yup')

        cmds.joint(n=title.replace("idBase", "idTip"))

        wideJnt = cmds.duplicate(blinkJnt, po=True, n=title.replace("idBase", "idWide"))[0]
        lengthTz = cmds.getAttr("{}.tx".format(lidJnt))
        cmds.setAttr("{}.tx".format(lidJnt), lengthTz * 0.9)
        #cmds.delete(jntTemp)

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

        for LR in ["l_", "r_"]:
            for upLow in ["up", "lo"]:

                if not cmds.attributeQuery(upLow + "LidVerts", node="lidFactor", exists=1):
                    raise RuntimeError("store lip vertices in order first!!")

                self.orderedVerts = cmds.getAttr("lidFactor.{}LidVerts".format(upLow))

                tempBSCrv = cmds.curve(d=3, p=([0, 0, 0], [0.25, 0, 0], [0.5, 0, 0], [0.75, 0, 0], [1, 0, 0]))
                cmds.rebuildCurve(rebuildType=0, spans=numOfCtl - 1, keepRange=0, keepControlPoints=0, degree=1)
                shapeCrv = cmds.rename(tempBSCrv, '{}{}Shape_crv'.format(LR, upLow))

                lidRollCrv = cmds.duplicate(shapeCrv, rc=1, n='{}{}LidRoll_crv'.format(LR, upLow))[0]
                lidRollCrvShape = cmds.listRelatives(lidRollCrv, c=1)[0]

                tmpSclCrv = cmds.curve(d=3, p=([0, 1, 1], [0.25, 1, 1], [0.5, 1, 1], [0.75, 1, 1], [1, 1, 1]))
                cmds.rebuildCurve(rebuildType=0, spans=numOfCtl - 1, keepRange=0, keepControlPoints=0, degree=1)
                lidScaleCrv = cmds.rename(tmpSclCrv, '{}{}LidScale_crv'.format(LR, upLow))
                lidScaleCrvShape = cmds.listRelatives(lidScaleCrv, c=1)[0]

                # HiCrv setup for blink/open
                length = len(self.orderedVerts)
                tempHiCrv = cmds.curve(d=1, p=([0, 0, 0], [0.25, 0, 0], [0.5, 0, 0], [0.75, 0, 0], [1, 0, 0]))
                cmds.rebuildCurve(rebuildType=0, spans=length - 1, keepRange=0, keepControlPoints=0, degree=1)
                eyeHiCrv = cmds.rename(tempHiCrv, '{}{}Hi_crv'.format(LR, upLow))
                eyeHiCrvShape = cmds.listRelatives(eyeHiCrv, c=1)[0]

                if LR.startswith("r_"):
                    cmds.reverseCurve(shapeCrv, ch=0, rpo=1)
                    cmds.reverseCurve(eyeHiCrv, ch=0, rpo=1)

                targetList = ["CTL", "ALid", "BLid", "CLid", "DLid", "Squint", "Annoyed"]
                targetCrvs = self.lipBlendShape(shapeCrv, targetList)

                hiCrvWire = cmds.wire(eyeHiCrv, w=shapeCrv, n="{}{}lipBS_wire".format(LR, upLow))
                cmds.setAttr("{}.dropoffDistance[0]".format(hiCrvWire[0]), 2)

                blinkCrv = cmds.duplicate(eyeHiCrv, rc=1, n="{}{}Blink_crv".format(LR, upLow))[0]
                openCrv = cmds.duplicate(eyeHiCrv, rc=1, n="{}{}Open_crv".format(LR, upLow))[0]
                blinkCrvBS = cmds.blendShape(blinkCrv, openCrv, eyeHiCrv, n=eyeHiCrv.replace("_crv", "Crv_BS"))

                cmds.parent(shapeCrv, eyeHiCrv, blinkCrv, openCrv, "eyeCrv_grp")

                if not cmds.objExists("{}{}ShapeCrv_grp".format(LR, upLow)):
                    cmds.group(n="{}{}Crv_grp".format(LR, upLow), em=True, p='eyeCrv_grp')

                crvGrp = "{}{}Crv_grp".format(LR, upLow)
                cmds.parent(targetCrvs, lidRollCrv, lidScaleCrv, crvGrp)

                self.parameter = 1.0/(len(self.orderedVerts)-1)

                blinkList = self.blinkJntDict["{}{}".format(LR, upLow)]
                wideList = self.wideJntDict["{}{}".format(LR, upLow)]
                for index, jntPair in enumerate(zip(blinkList, wideList)):
                    blinkJnt = jntPair[0]
                    wideJnt = jntPair[1]
                    index += 1
                    pocName = blinkJnt.replace("Blink", "Poc")
                    poc = self.createPocNode(pocName, eyeHiCrvShape, self.parameter * index)

                    rollPocName = blinkJnt.replace("Blink", "RollPoc")
                    lidRollPoc = self.createPocNode(rollPocName, lidRollCrvShape, self.parameter * index)

                    scalePocName = blinkJnt.replace("Blink", "ScalePoc")
                    lidScalePoc = self.createPocNode(scalePocName, lidScaleCrvShape, self.parameter * index)

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
        cmds.connectAttr("lidFactor.lidRotateX_scale", '{}.input2X'.format(rotMult))
        cmds.connectAttr('{}.outputX'.format(rotMult), '{}.rz'.format(lidJnt))

        cmds.connectAttr("{}.positionX".format(poc), '{}.input3D[1].input3Dx'.format(rotPlus))
        cmds.setAttr('{}.input3D[2].input3Dx'.format(rotPlus), initialX*-1)
        cmds.connectAttr('{}.output3Dx'.format(rotPlus), '{}.input1Y'.format(rotMult))
        cmds.connectAttr("lidFactor.lidRotateY_scale", '{}.input2Y'.format(rotMult))
        cmds.connectAttr('{}.outputY'.format(rotMult), '{}.ry'.format(lidJnt))

        baseGrp = cmds.listRelatives(lidJnt, p=1, type="transform")[0]
        if LR == "l_":
            cmds.connectAttr("{}lidScale_ctl.tx".format(LR), '{}.input3D[0].input3Dx'.format(rotPlus))
            cmds.connectAttr("{}lidScale_ctl.rz".format(LR), "{}.rz".format(baseGrp))

        elif LR == "r_":
            cmds.connectAttr("{}.outputZ".format(self.reverseMult), "{}.input3D[0].input3Dx".format(rotPlus))
            cmds.connectAttr("{}lidScale_ctl.rz".format(LR), '{}.input1Z'.format(rotMult))
            cmds.setAttr('{}.input2Z'.format(rotMult), -1)
            cmds.connectAttr('{}.outputZ'.format(rotMult), "{}.rz".format(baseGrp))

        # LipRoll_rotationX connection( lipRoll_jnt.rz = lipRoll_poc.ty )
        cmds.connectAttr("{}.positionY".format(lidRollPoc), rollJnt + '.rx')
        # rotateX connect (volumn controls )
        cmds.connectAttr("{}.positionZ".format(lidRollPoc), '{}.rx'.format(lidJnt))

        cmds.connectAttr(lidScalePoc + '.positionY', rollJnt + '.sy')
        cmds.connectAttr(lidScalePoc + '.positionZ', rollJnt + '.sz')

        #wideJnt follow setup (greater than)
        cmds.connectAttr("{}.rz".format(lidJnt), "{}.input1X".format(wideMult))
        cmds.connectAttr("{}.ry".format(lidJnt), "{}.input1Y".format(wideMult))
        cmds.connectAttr("{}.rz".format(lidJnt), "{}.input1Z".format(wideMult))
        # followUp = 0.6 / followDown = 0.1
        cmds.connectAttr("lidFactor.eyeWide_followUp", "{}.input2X".format(wideMult))
        cmds.connectAttr("lidFactor.eyeWide_followUp", "{}.input2Y".format(wideMult))
        cmds.connectAttr("lidFactor.eyeWide_followDown", "{}.input2Z".format(wideMult))

        cmds.connectAttr('{}.rz'.format(lidJnt), wideRXCond + ".firstTerm")
        cmds.setAttr(wideRXCond + ".secondTerm", 0)
        cmds.setAttr(wideRXCond + ".operation", 2)

        # wideJnt up/down setup (rotation value)
        cmds.connectAttr('{}.outputX'.format(wideMult), "{}.colorIfTrueR".format(wideRXCond))
        cmds.connectAttr('{}.outputZ'.format(wideMult), "{}.colorIfFalseR".format(wideRXCond))

        cmds.connectAttr("{}.outColorR".format(wideRXCond), "{}.input3D[0].input3Dx".format(wideRotSum))
        cmds.connectAttr("{}.output3Dx".format(wideRotSum), '{}.rz'.format(wideJnt))

        # wideJnt left/right setup (rotation value)
        cmds.connectAttr('{}.outputY'.format(wideMult), "{}.input3D[0].input3Dy".format(wideRotSum))
        cmds.connectAttr("{}.output3Dy".format(wideRotSum), '{}.ry'.format(wideJnt))

    def eyeWideCrvSetup(self):

        if not cmds.attributeQuery("upLidVerts", node="lidFactor", exists=1):
            raise RuntimeError("store eyeLid vertices first!!")

        if not cmds.attributeQuery("l_upWideJnt", node="lidFactor", exists=1):
            raise RuntimeError("store wideJoint list first!!")

        for LR in ["l_", "r_"]:
            for upLow in ["up", "lo"]:

                self.orderedVerts = cmds.getAttr("lidFactor.{}LidVerts".format(upLow))

                tempWideCrv = cmds.curve(d=3, p=([0, 0, 0], [0.25, 0, 0], [0.5, 0, 0], [0.75, 0, 0], [1, 0, 0]))
                cmds.rebuildCurve(rebuildType=0, spans=2, keepRange=0, keepControlPoints=0, degree=3)
                wideCrv = cmds.rename(tempWideCrv, '{}{}Wide_crv'.format(LR, upLow))
                wideCrvShape = cmds.listRelatives(wideCrv, c=1)[0]

                targetList = ["ALid", "BLid", "CLid", "DLid", "Squint", "Annoyed", "Blink", "Open"]
                wideShpCrvs = self.lipBlendShape(wideCrv, targetList)
                cmds.parent(wideShpCrvs, "{}{}Crv_grp".format(LR, upLow))
                cmds.parent(wideCrv, "eyeCrv_grp")

                self.parameter = 1.0/(len(self.orderedVerts)-1)

                if not self.wideJntDict[LR+upLow]:
                    self.wideJntDict[LR+upLow] = cmds.getAttr("lidFactor.{}{}WideJnt".format(LR, upLow))

                wideJntList = self.wideJntDict[LR+upLow]

                for index, wideJnt in enumerate(wideJntList):

                    index += 1
                    widePocName = wideJnt.replace("LidWide", "WidePoc")
                    widePoc = self.createPocNode(widePocName, wideCrvShape, self.parameter * index)

                    self.eyeWideCrvToJoint(widePoc, wideJnt)

            if not self.eyeWideCornerDict[LR]:
                self.eyeWideCornerDict[LR] = cmds.getAttr("lidFactor.{}WideCornerJnt".format(LR))

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

    def lipBlendShape(self, ctlCrv, targetList):

        trgCrvList = []
        for target in targetList:  # l_upALid_crv
            dupCrv = cmds.duplicate(ctlCrv, rc=1, n=ctlCrv.replace("crv", target))[0]
            trgCrvList.append(dupCrv)

        lipCrvBS = cmds.blendShape(trgCrvList, ctlCrv, n=ctlCrv.replace("crv", "BS"))
        weightList = [(x, 1) for x in range(len(targetList))]
        cmds.blendShape(lipCrvBS[0], edit=True, w=weightList)

        return trgCrvList

    def eyeRigBuild(self, numOfCtl):

        self.eyeJointSetup()
        self.eyeCrvSetup(numOfCtl)
        self.eyeWideCrvSetup()

    def eyeCtlJntOnCrv(self):

        parameter = 1.0/4.0

        if not cmds.objExists("eyeCtl_jntGrp"):
            cmds.group(n="eyeCtl_jntGrp", em=True, p='faceMain|jnt_grp')
        eyeCtlJntGrp = "eyeCtl_jntGrp"

        InOut = {"l_": {"in": 0, "out": 1}, "r_": {"in": 1, "out": 0}}
        for index, LR in enumerate(["l_", "r_"]):

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
                cmds.xform(null, ws=1, t=(0.5, 0, 0))
                jnt = cmds.joint(n=name)

                #bindMethod=cloestDistance
                bindJnt = [jnt] + cornerJnts
                cmds.skinCluster(crv, bindJnt, bindMethod=0, normalizeWeights=1, weightDistribution=0, mi=3, omi=True, tsb=1)

    def eyeLidFreeCtl(self, numOfCtl, myCtl):

        dist = cmds.getAttr("helpPanel_grp.headBBox")

        if not cmds.objExists("eyeStickyCtl_grp"):
            cmds.group(n="eyeStickyCtl_grp", em=True)
        lidCtlGrp = "eyeStickyCtl_grp"

        if not myCtl:
            temp = self.genericController("genericCtl", (0, 0, 0), dist[1]/120.0, "circle", self.colorIndex["purple"][0])
            myCtl = temp

        prefixDict = {"l_": 1, "r_": -1}
        for LR, val in prefixDict.items():

            rollCvs = {}
            puffCvs = {}
            CTLCrvCvs = {}
            for idx, upLow in enumerate(["up", "lo"]):

                orderedVerts = cmds.getAttr("lidFactor.{}LidVerts".format(upLow))
                if LR == "r_":
                    orderedVerts = face_utils.mirrorVertices(orderedVerts)

                polyCrv = self.createPolyToCurve(orderedVerts, name="{}{}Eye_guide".format(LR, upLow), direction=val)
                cmds.rebuildCurve(polyCrv, ch=1, rebuildType=0, spans=len(orderedVerts) - 1, keepRange=0,
                                  keepControlPoints=1, degree=1)
                cmds.parent(polyCrv, "guideCrv_grp")

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

                #cmds.delete(tempGuideCrv)

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
                    print(prm, index)
                    name = self.namingMethod(LR, upLow, "Eye", str(index).zfill(2), "ctl")
                    ctlChain = self.createMidController(name, dist[1] / 50.0, myCtl, param=prm, guideCrv=polyCrv,
                                                        colorID=colorID)
                    ctl, offset, null, poc = [ctlChain[0], ctlChain[1], ctlChain[2], ctlChain[3]]
                    cmds.setAttr(offset + ".tz", offSetVal)
                    cmds.setAttr("{}.sx".format(offset), val)

                    if prm == centerParam:
                        broadCtl = self.genericController("{}{}CenterCtl".format(LR, upLow), (0, 0, 0), dist[1] / 100.0,
                                                          "circle", self.colorIndex["purple"][0])
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

                broadCtl = self.genericController("{}{}Ctl".format(LR, position), (0, 0, 0), dist[1] / 100.0,
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
                    print(CTLCrvCvs[LR + upLow][value], rollCvs[LR + upLow][value])
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
        cmds.connectAttr("{}.rz".format(ctl), "{}.zValue".format(rollCv))

        cmds.connectAttr("{}.sy".format(ctl), "{}.yValue".format(puffCv))
        cmds.connectAttr("{}.sz".format(ctl), "{}.zValue".format(puffCv))

def eyeHiCrvX(prefix):
    # get ordered vertices
    if "up" in prefix:
        orderVtx = cmds.getAttr("lidFactor.upLidVerts")

    elif "lo" in prefix:
        orderVtx = cmds.getAttr("lidFactor.loLidVerts")
    leng = len(orderVtx)
    if cmds.objExists("eyeCrv_grp"):
        eyeCrvGrp = "eyeCrv_grp"
    else:
        eyeCrvGrp = cmds.group(em=1, n="eyeCrv_grp", p="crv_grp")

    posOrder = []
    if "l_" in prefix:
        for vx in orderVtx:
            lPos = cmds.xform(vx, q=1, ws=1, t=1)
            posOrder.append(lPos)

    elif "r_" in prefix:
        for vx in orderVtx:
            lPos = cmds.xform(vx, q=1, ws=1, t=1)
            rPos = [-lPos[0], lPos[1], lPos[2]]
            posOrder.append(rPos)

    tmpCrv = cmds.curve(d=1, p=posOrder)  # , n =  prefix  + "TempCrv01"
    # int $nucmdsVs   = $numSpans + $degree
    # cmds.rebuildCurve( tmpCrv, d = 1, rebuildType = 0, s= leng-1, keepRange = 0)
    newHiCrv = cmds.rename(tmpCrv, prefix + "HiCrv01")
    cmds.parent(newHiCrv, eyeCrvGrp)
    blinkCrv = cmds.duplicate(newHiCrv, n=newHiCrv.replace("Hi", "Blink"), rc=1)[0]
    crvShape = cmds.listRelatives(newHiCrv, c=1, ni=1, s=1)

    if "lo" in prefix:
        posOrder = posOrder[1:-1]

    for i, pos in enumerate(posOrder):
        uParam = getUParam(pos, newHiCrv)
        poc = cmds.shadingNode('pointOnCurveInfo', asUtility=True, n=prefix + 'eyePOC' + str(i + 1).zfill(2))
        cmds.connectAttr(crvShape[0] + ".worldSpace", poc + ".inputCurve")
        cmds.setAttr(poc + ".parameter", uParam)
        cmds.connectAttr(poc + ".position", prefix + "Loc" + str(i + 1).zfill(2) + ".t")


####blink / shape "controlPanel" for arface setup!!!!!!!!!!!!!!!!!
''' 
1.up/loHiCrv wire to up/loCtlCrv 
2.BlinkLevelCrv(copy of upCtlCrv) blendshape to loCtlCrv   
3.up/loBlinkCrv wire to BlinkLevel crv 
4.up/loHiCrv blendShape to up/loBlinkCrv for "blinking"
5.up/loHiCrv wire to up/loCtlCrv for "detail control" 

'''


# create "attachCtl_grp" in hierachy
# adjust CTLcrv(master) shape to hiCrv
# place joints for eyeCtls at 20*index% on hi curve
def eyeCtrls(prefix, numEyeCtl, offset):
    headMesh = cmds.getAttr("helpPanel_grp.headGeo")
    lidVerts = cmds.getAttr("lidFactor." + prefix[2:] + "LidVerts")
    cpmNode = cmds.createNode("closestPointOnMesh", n="closestPointM_node")
    cmds.connectAttr(headMesh + ".outMesh", cpmNode + ".inMesh")
    orderedVerts = []
    if "r_" in prefix:
        orderedVerts = mirrorVertice(lidVerts)
        eyeRotY = cmds.getAttr('r_upLidP_grp.ry')
        eyeRotZ = cmds.getAttr('r_upLidP_grp.rz')

    else:
        orderedVerts = lidVerts
        eyeRotY = cmds.getAttr('l_upLidP_grp.ry')
        eyeRotZ = cmds.getAttr('l_upLidP_grp.rz')

    edges = []
    numVtx = len(orderedVerts)
    for v in range(numVtx - 1):
        cmds.select(orderedVerts[v])
        x = cmds.polyListComponentConversion(fv=1, toEdge=1)
        cmds.select(x, r=1)
        edgeA = cmds.ls(sl=1, fl=1)
        cmds.select(orderedVerts[v + 1], r=1)
        y = cmds.polyListComponentConversion(fv=1, toEdge=1)
        cmds.select(y, r=1)
        edgeB = cmds.ls(sl=1, fl=1)

        common = set(edgeA) - (set(edgeA) - set(edgeB))
        edges.append(list(common)[0])
    cmds.select(cl=1)

    # create polyEdgeCurve to follow head geo
    for e in edges:
        cmds.select(e, add=1)

    # create guide_crv
    crv = cmds.polyToCurve(form=2, degree=1, n=prefix + "Eye_guide_Crv")[0]
    cmds.rebuildCurve(crv, rebuildType=0, spans=numEyeCtl - 1, keepRange=0, degree=3)
    cvList = cmds.ls(crv + ".cv[*]", fl=1)
    cvStart = cmds.xform(cvList[0], q=1, ws=1, t=1)[0]
    cvEnd = cmds.xform(cvList[-1], q=1, ws=1, t=1)[0]
    if cvStart ** 2 > cvEnd ** 2:
        cmds.reverseCurve(crv, ch=1, rpo=1)

    if not cmds.objExists('guideCrv_grp'):
        guideCrvGrp = cmds.group(n='guideCrv_grp', em=True, p='faceMain|crv_grp')
    cmds.parent(crv, "guideCrv_grp")

    sequence = string.ascii_uppercase
    leng = cmds.arclen(crv)
    increm = leng / 30
    print
    "ctl size is %s" % increm

    if cmds.objExists("eyeOnCtl_grp"):
        eyeGrp = "eyeOnCtl_grp"
    else:
        eyeGrp = cmds.group(em=1, n="eyeOnCtl_grp", p="ctl_grp")

    if cmds.objExists("eyeCrvJnt_grp"):
        crvJntGrp = "eyeCrvJnt_grp"
    else:
        crvJntGrp = cmds.group(em=1, n="eyeCrvJnt_grp", p="jnt_grp")

        # seperate looping for up / lo( different num of joint)
    if "up" in prefix:
        minV = 0
        maxV = numEyeCtl
    elif "lo" in prefix:
        minV = 1
        maxV = numEyeCtl - 1

    cornerPoc = []
    ctlPoc = []
    temGrp = nullEvenOnCrv(crv, numEyeCtl, prefix + "EyeCtl")  # nulls, pocs
    nulls = temGrp[0]
    pocs = temGrp[1]
    for i in range(minV, maxV):
        x = i - 1

        # create ctl joints grp
        pos = cmds.getAttr(pocs[i] + ".position")[0]
        if i == 0:  # first/last point for in/outCorner
            grp = cmds.rename(nulls[i], prefix[:2] + "InCorner_eye_JntP")
            cornerPoc.append(pocs[i])
        elif i == numEyeCtl - 1:  # first/last point for in/outCorner
            grp = cmds.rename(nulls[i], prefix[:2] + "OutCorner_eye_JntP")
            cornerPoc.append(pocs[i])
        else:
            grp = cmds.rename(nulls[i], prefix + "_" + sequence[x] + "eye_JntP")
            ctlPoc.append(pocs[i])

        cmds.parent(grp, "eyeCrvJnt_grp")
        cmds.setAttr(grp + ".rotateOrder", 3)
        cmds.setAttr(grp + '.ry', eyeRotY)
        cmds.setAttr(grp + '.rz', eyeRotZ)

        jnt = cmds.joint(p=pos, n=grp.replace("eye_JntP", "Eye_jnt"))
        cmds.select(cl=1)
        ctl = arcController(grp.replace("eye_JntP", "ctl"), pos, increm, "cc")
        # create top parent null for ctl
        ctlGrp = cmds.duplicate(ctl[1], po=1, n=ctl[1].replace("ctlP", "_grp"))[0]
        cmds.parent(ctl[1], ctlGrp)
        cmds.connectAttr(pocs[i] + ".position", ctlGrp[0] + ".t")
        cmds.setAttr(ctlGrp[0] + ".rotateOrder", 3)
        cmds.setAttr(ctlGrp[0] + '.ry', eyeRotY)
        cmds.setAttr(ctlGrp[0] + '.rz', eyeRotZ)
        cmds.setAttr(ctl[1] + ".tz", offset)
        cmds.parent(ctlGrp, "eyeOnCtl_grp")

        # print "%s is for %s"%(str(index), ctl)

        cmds.connectAttr(ctl[0] + ".t", jnt + ".t")
        cmds.connectAttr(ctl[0] + ".r", jnt + ".r")
        cmds.connectAttr(ctl[0] + ".s", jnt + ".s")

    if cmds.attributeQuery(prefix + "_eyeCtlPoc", node="lidFactor", exists=1) == False:
        cmds.addAttr("lidFactor", ln=prefix + "_eyeCtlPoc", dt="stringArray")
        cmds.setAttr("lidFactor.%s_eyeCtlPoc" % prefix, type="stringArray", *([len(ctlPoc)] + ctlPoc))

    if cmds.attributeQuery(prefix[:2] + "eyeCornerPoc", node="lidFactor", exists=1) == False:
        cmds.addAttr("lidFactor", ln=prefix[:2] + "eyeCornerPoc", dt="stringArray")

    if cornerPoc:
        cmds.setAttr("lidFactor." + prefix[:2] + "eyeCornerPoc", type="stringArray", *([len(cornerPoc)] + cornerPoc))

    # create eyeCTL-curves ( 5cvs )


def eyeCtlCrv():
    # for arFace Sukwon Shin
    prefix = ["l_up", "l_lo", "r_up", "r_lo"]
    for pre in prefix:
        cornerPoc = cmds.getAttr("lidFactor." + pre[:2] + "eyeCornerPoc")
        ctlPoc = cmds.getAttr("lidFactor.%s_eyeCtlPoc" % pre)
        ctlPoc.insert(0, cornerPoc[0])
        ctlPoc.append(cornerPoc[1])
        posList = []
        for pc in ctlPoc:
            pos = cmds.getAttr(pc + ".position")[0]
            posList.append(pos)

        # create CTLCrv ( l_upCTLCrv01, l_loCTLCrv01.... )
        if cmds.objExists("eyeCrv_grp"):
            eyeCrvGrp = "eyeCrv_grp"
        else:
            eyeCrvGrp = cmds.group(em=1, n="eyeCrv_grp", p="crv_grp")

        ctlCrv = cmds.curve(d=3, ep=posList)
        newCrv = cmds.rename(ctlCrv, pre + "CTLCrv01")
        cmds.parent(newCrv, eyeCrvGrp)


# modeling the "CTLCrvs" BEFORE run it ( blendshape and skinning )
# create blink BS / wire deform for up/lo blinkCurve
# prefix = ["l_","r_"]
def eyeCrvConnect(pre):
    # blink level crv(lo) setup
    upCrv = pre + "upCTLCrv01"
    loCrv = pre + "loCTLCrv01"
    lidFactor = "lidFactor"

    if cmds.objExists("eyeShapeCrv_grp"):
        eyeShapeGrp = "eyeShapeCrv_grp"
    else:
        eyeShapeGrp = cmds.group(em=1, n="eyeShapeCrv_grp", p="eyeCrv_grp")

    for crv in [upCrv, loCrv]:
        titleSplit = crv.split("CTL")
        lidTgtCrvs = []
        for sequence in ["A", "B", "C", "D"]:
            pushCrv = cmds.duplicate(crv, rc=1, n=titleSplit[0] + sequence + "Lid_crv")[0]
            lidTgtCrvs.append(pushCrv)

        squintCrv = cmds.duplicate(crv, rc=1, n=titleSplit[0] + "Squint_crv")[0]
        lidTgtCrvs.append(squintCrv)
        annoyedCrv = cmds.duplicate(crv, rc=1, n=titleSplit[0] + "Annoyed_crv")[0]
        lidTgtCrvs.append(annoyedCrv)
        ctlCrvBS = cmds.blendShape(lidTgtCrvs, crv, n=titleSplit[0] + "Lid_bs")
        cmds.parent(lidTgtCrvs, eyeShapeGrp)

    blinkLevelCrv = cmds.duplicate(upCrv, rc=1, n=pre + "BlinkLevelCrv")[0]

    if not cmds.objExists(pre + "BlinkLevel_bs"):

        blinkBS = cmds.blendShape(pre + "loCTLCrv01", pre + "upCTLCrv01", blinkLevelCrv, n=pre + "BlinkLevel_bs")

    else:
        blinkBS = [pre + "BlinkLevel_bs"]

    cmds.connectAttr(lidFactor + ".%sloBlinkLevel" % (pre), blinkBS[0] + ".%s" % (pre + "upCTLCrv01"))
    cmds.connectAttr(lidFactor + ".%supBlinkLevel" % (pre), blinkBS[0] + ".%s" % (pre + "loCTLCrv01"))

    ctlJnt = []
    corner = cmds.ls(pre + "*Corner_Eye_jnt", typ="joint")
    upDown = {"up": 1, "lo": 0}
    for ud in upDown:

        # wire attach hiCrv to ctlCrv
        ctlCrv = pre + ud + "CTLCrv01"
        hiCrv = pre + ud + "HiCrv01"
        wireNd = cmds.wire(hiCrv, w=ctlCrv, n=pre + ud + "free_wire")
        cmds.setAttr(wireNd[0] + ".scale[0]", 1)
        cmds.setAttr(wireNd[0] + ".rotation", 0)
        cmds.setAttr(wireNd[0] + ".dropoffDistance[0]", 5)
        # eye blinkCrv / wideCrv setup
        wideCrv = cmds.duplicate(hiCrv, rc=1, n=pre + ud + "Wide_crv")[0]
        blinkCrv = pre + ud + "BlinkCrv01"  # hiCrv target when blinking
        if cmds.objExists(blinkCrv):
            # attach blink_Crv(hi) to the blink_level(lo) curve

            cmds.setAttr(lidFactor + "." + pre + "loBlinkLevel", upDown[ud])
            wr = cmds.wire(blinkCrv, w=blinkLevelCrv, n=pre + ud + "Blink_wire")
            cmds.setAttr(wr[0] + ".scale[0]", 0)
            cmds.setAttr(wr[0] + ".dropoffDistance[0]", 5)

            smartBlinkBS = cmds.blendShape(wideCrv, blinkCrv, pre + ud + "HiCrv01", n=pre + ud + "Blink_bs")

        ctlJnt = cmds.ls(pre + ud + "*Eye_jnt", typ="joint")
        eyeCtlJnt = corner + ctlJnt
        ctlCrv = pre + ud + "CTLCrv01"
        if cmds.objExists(ctlCrv):
            cmds.skinCluster(ctlCrv, eyeCtlJnt, toSelectedBones=1, bindMethod=0, nw=1, maximumInfluences=3, omi=1,
                             rui=1)

        # compensate "double transform sticky ctls"


def compensateStickyCtl(grp):
    # get ctls' transform
    eyeCtls = getCtlList(grp)
    for i, ctl in enumerate(eyeCtls):

        ctlP = cmds.listRelatives(ctl, p=1)[0]
        ctlPP = cmds.listRelatives(ctlP, p=1)[0]
        if "compensate" in ctlPP:
            cmds.confirmDialog(title='Confirm', message='compensate grp is already exists!')
            break
        else:
            oldName = ctlPP.split("_")
            grpName = oldName[-1]
            revMult = cmds.shadingNode("multiplyDivide", asUtility=1, n=ctl + "rev_mult")

            compensateGrp = cmds.duplicate(ctlPP, po=1, n=ctlPP.replace("_" + grpName, "_compensate"))
            cmds.parent(ctlP, compensateGrp[0])
            cmds.parent(compensateGrp[0], ctlPP)
            cmds.connectAttr(ctl + ".t", revMult + ".input1")
            cmds.setAttr(revMult + ".input2", -1, -1, -1)
            cmds.connectAttr(revMult + ".output", compensateGrp[0] + ".t")


def getCtlList(grp):
    if cmds.objExists(grp):
        tmpChild = cmds.listRelatives(grp, ad=1, ni=1, type=["nurbsCurve", "mesh", "nurbsSurface"])
        child = [t for t in tmpChild if not "Orig" in t]
        ctls = cmds.listRelatives(child, p=1)
        ctlist = []
        for c in ctls:
            cnnt = cmds.listConnections(c, s=1, d=1, c=1)
            if cnnt:
                attr = cnnt[0].split('.')[1]
                print
                attr
                if attr in ["translate", "rotate", "scale", "translateX", "translateX", "translateY", "rotateZ",
                            "rotateY", "rotateZ", "scaleX", "scaleY", "scaleZ"]:
                    ctlist.append(c)
        return ctlist


# eyeGeoGrp = cmds.ls(sl=1, typ = "transform")[0]
def eyeRigAttachBody(eyeGeoGrp, upVector):
    """
    create Eye Rig"""

    lEyePos = cmds.xform('lEyePos', t=True, q=True, ws=True)
    lEyeRot = cmds.xform('lEyePos', ro=True, q=True, ws=True)

    if cmds.objExists("eyeRig") == False:
        cmds.warning("build the Hierachy first!!")
    else:
        eyeRig = "eyeRig"
    cmds.parent(eyeRig, "bodyHeadTRS")

    if cmds.objExists("eyeTR") == False:
        eyeTR = cmds.group(em=True, n="eyeRig", p="eyeRig")
    else:
        eyeTR = "eyeTR"

    cmds.xform(eyeTR, ws=1, t=(0, lEyePos[1], lEyePos[2]))
    lDMat = cmds.shadingNode('decomposeMatrix', asUtility=1, n='lEyeDecompose')
    multMat = cmds.shadingNode('multMatrix', asUtility=1, n='lEyeMultDCM')
    # ffdSquachLattice = cmds.group(em =1, n = 'ffdSquachLattice', p = 'eyeRigP')
    lEyeP = cmds.group(em=True, n='l_eyeP', p="eyeTR")
    cmds.xform(lEyeP, ws=1, t=(lEyePos[0], lEyePos[1], lEyePos[2]))
    lEyeRP = cmds.group(em=True, n='l_eyeRP', p=lEyeP)
    cmds.setAttr(lEyeRP + ".ry", lEyeRot[1])
    cmds.setAttr(lEyeRP + ".rx", lEyeRot[0])
    lEyeScl = cmds.group(em=True, n='l_eyeScl', p=lEyeRP)
    indieScaleSquach(lEyeScl, upVector)
    lEyeRot = cmds.group(em=True, n='l_eyeRot', p=lEyeScl)
    lEyeballRot = cmds.group(em=True, n='l_eyeballRot', p=lEyeRot)

    '''#under headTRS
    lEyeTransform = cmds.group( em=1, n = "L_eyeTransform", p = lDmNull )
    cmds.xform( lDmNullP, ws =1, t =(lEyePos[0], lEyePos[1], lEyePos[2] ))'''

    eyeGeoP = cmds.listRelatives(eyeGeoGrp, p=1)[0]
    cmds.connectAttr(lEyeballRot + ".worldMatrix", multMat + ".matrixIn[0]")
    cmds.connectAttr(eyeGeoP + ".worldInverseMatrix[0]", multMat + ".matrixIn[1]")
    cmds.connectAttr(multMat + ".matrixSum", lDMat + ".inputMatrix")
    cmds.connectAttr(lDMat + ".outputTranslate", eyeGeoGrp + ".translate")
    cmds.connectAttr(lDMat + ".outputRotate", eyeGeoGrp + ".rotate")
    cmds.connectAttr(lDMat + ".outputScale", eyeGeoGrp + ".scale")
    cmds.connectAttr(lDMat + ".outputShear", eyeGeoGrp + ".shear")
    # "eyeAssembly_GRP" world inverseMatrix * eyeSclera worldMatrix = eye local matrix