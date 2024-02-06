import maya.cmds as cmds
import maya.mel as mel
from twitchScript.face import face_utils
reload(face_utils)

class LipShapeRig(face_utils.Util):

    def __init__(self, numOfCtl, orderedVtx):

        super(LipShapeRig, self).__init__()

        self.numOfCtl = int(numOfCtl)
        self.orderedVerts = orderedVtx
        self.childJntList = []
        self.ctlJnts = {}
        self.mirrorJntPrefix = {}
        self.rollCvs = {}
        self.puffCvs = {}
        self.pocList = []
        self.ctlList = []
        self.detailCtlGrp = None

    def lipShapeRigSetup(self):
        """

        """
        if not cmds.objExists("arFacePanel"):
            raise RuntimeError("import arFacePanel")

        headGeo = cmds.getAttr("helpPanel_grp.headGeo")
        if not headGeo:
            raise RuntimeError("store headGeo string!!")

        #dist = cmds.getAttr("helpPanel_grp.headBBox")
        if not cmds.objExists('lipCrv_grp'):
            cmds.group(n='lipCrv_grp', em=True, p='faceMain|crv_grp')

        shapeCrv =cmds.ls("*_lipBS_crv")
        if shapeCrv:
            raise RuntimeError("lipShape rig already exists!!")

        for upLow in ["up", "lo"]:

            if not cmds.attributeQuery(upLow + "LipVerts", node="lipFactor", exists=1):
                raise RuntimeError("store lip vertices in order first!!")

            vtxNum = len(self.orderedVerts[upLow])
            param = 1.0 / (vtxNum - 1)

            self.mirrorPrefix = self.mirrorOrder_name(vtxNum)

            #create extra curves (jaw drop / free form)
            tempBSCrv = cmds.curve(d=3, p=([0, 0, 0], [0.25, 0, 0], [0.5, 0, 0], [0.75, 0, 0], [1, 0, 0]))
            cmds.rebuildCurve(rebuildType=0, spans=self.numOfCtl-1, keepRange=0, keepControlPoints=0, degree=3)
            bsCrv = cmds.rename(tempBSCrv, upLow + '_lipBS_crv')
            bsCrvShape = cmds.listRelatives(bsCrv, c=True)[0]

            tmplipRollCrv = cmds.curve(d=3, p=([0, 0, 0], [0.25, 0, 0], [0.5, 0, 0], [0.75, 0, 0], [1, 0, 0]))
            cmds.rebuildCurve(rebuildType=0, spans=self.numOfCtl-3, keepRange=0, keepControlPoints=0, degree=3)
            lipRollCrv = cmds.rename(tmplipRollCrv, upLow + '_lipRoll_crv')
            lipRollCrvShape = cmds.listRelatives(lipRollCrv, c=1)[0]

            tmpPuckerCrv = cmds.curve(d=3, p=([0, 0, 1], [0.25, 0, 1], [0.5, 0, 1], [0.75, 0, 1], [1, 0, 1]))
            cmds.rebuildCurve(rebuildType=0, spans=self.numOfCtl - 3, keepRange=0, keepControlPoints=0, degree=3)
            lipPuckerCrv = cmds.rename(tmpPuckerCrv, upLow + '_pucker_crv')
            lipPuckerCrvShape = cmds.listRelatives(lipPuckerCrv, c=True)[0]

            cmds.parent(bsCrv, lipRollCrv, lipPuckerCrv, "lipCrv_grp")
            self.lipBlendShape(upLow)

            for index, prefix in self.mirrorPrefix.items():

                uplo = "" if index == 0 or index == vtxNum - 1 else upLow
                pre = prefix[0]
                order = prefix[1]
                # l_upJawRX_02
                lipJnt = "{}{}{}_{}".format(pre, uplo, "JawRX", order)

                self.childJntList = cmds.listRelatives(lipJnt, ad=1, typ="joint")
                pocName = self.namingMethod(pre, uplo, "lipBS", order, "poc")

                if cmds.objExists(pocName):
                    continue
                poc = self.createPocNode(pocName, bsCrvShape, param * index)

                rollPocName = self.namingMethod(pre, uplo, "lipRoll", order, "poc")
                lipRollPoc = self.createPocNode(rollPocName, lipRollCrvShape, param * index)

                puckerPocName = self.namingMethod(pre, uplo, "lipPucker", order, "poc")
                lipPuffPoc = self.createPocNode(puckerPocName, lipPuckerCrvShape, param * index)

                self.connectLipMinorJnt(poc, lipRollPoc, lipPuffPoc, lipJnt)

    def connectLipMinorJnt(self, poc, lipRollPoc, lipPuffPoc, lipJnt):
        # curve's Poc drive the joint

        rollJnt = self.childJntList[0]
        rotYJnt = self.childJntList[1]

        rotXMult = cmds.shadingNode('multiplyDivide', asUtility=True, n="{}_mult".format(lipJnt))
        rotYMult = cmds.shadingNode('multiplyDivide', asUtility=True, n=rotYJnt.replace("_jnt", "_mult"))

        rotX_plus = cmds.shadingNode('plusMinusAverage', asUtility=True, n="{}_plus".format(lipJnt))
        rotY_plus = cmds.shadingNode('plusMinusAverage', asUtility=True, n= rotYJnt.replace("_jnt", "_plus"))

        rotZ_add = cmds.shadingNode('addDoubleLinear', asUtility=True, n="{}_add".format(lipJnt))
        initialX = cmds.getAttr(poc + '.positionX')
        detailPlus = cmds.shadingNode('plusMinusAverage', asUtility=1, n=rollJnt.replace('_jnt', '_sum'))
        # JotX rotationXY connection
        # ty(input3Dy) / extra ty(input3Dx) seperate out for jawSemi

        cmds.setAttr(rotX_plus + '.operation', 1)
        cmds.connectAttr(poc + '.positionY', rotX_plus + '.input3D[0].input3Dy')
        cmds.connectAttr('mouthMove_ctl.ty', rotX_plus + '.input3D[1].input3Dy')

        cmds.connectAttr(rotX_plus + '.output3Dy', rotXMult + '.input1X')
        cmds.connectAttr("lipFactor.lipJotX_rx", rotXMult + '.input2X')
        cmds.connectAttr(rotXMult + '.outputX', lipJnt + '.rx')

        # 1. curve translateX add up for LipJotX
        cmds.connectAttr('swivel_ctl.tx', rotXMult + '.input1Y')
        cmds.connectAttr("lipFactor.lipJotX_ry", rotXMult + '.input2Y')
        cmds.connectAttr(rotXMult + '.outputY', lipJnt + '.ry')

        # complementary rz movement for ry !!! lower the rz value!!!
        cmds.connectAttr('swivel_ctl.tx', rotXMult + '.input1Z')
        cmds.connectAttr("lipFactor.lipJotX_rz", rotXMult + '.input2Z')
        cmds.connectAttr(rotXMult + '.outputZ', rotZ_add + ".input1")
        cmds.connectAttr('swivel_ctl.rz', rotZ_add + ".input2")
        cmds.connectAttr(rotZ_add + ".output", lipJnt + '.rz')

        cmds.connectAttr('swivel_mult.outputX', lipJnt + '.tx', f=1)
        cmds.connectAttr('swivel_mult.outputY', lipJnt + '.ty', f=1)

        cmds.connectAttr('swivel_mult.outputZ', rotX_plus + '.input3D[0].input3Dz')
        cmds.connectAttr(poc + '.positionZ', rotX_plus + '.input3D[1].input3Dz')
        cmds.connectAttr('mouthMove_ctl.tz', rotX_plus + '.input3D[2].input3Dz')
        cmds.connectAttr(rotX_plus + '.output3Dz', lipJnt + '.tz', f=1)

        # TranslateX(poc + "mouth_move") add up for upLow + 'LipJotY' .ry
        cmds.setAttr(rotY_plus + '.operation', 1)
        cmds.connectAttr(poc + '.positionX', rotY_plus + '.input3D[0].input3Dx')
        cmds.setAttr(rotY_plus + '.input3D[1].input3Dx', -initialX)
        cmds.connectAttr('mouthMove_ctl.tx', rotY_plus + '.input3D[2].input3Dx')
        cmds.connectAttr(rotY_plus + '.output3Dx', rotYMult + '.input1Y')
        cmds.connectAttr("lipFactor.lipJotX_ry", rotYMult + '.input2Y')
        cmds.connectAttr(rotYMult + '.outputY', rotYJnt + '.ry')

        cmds.connectAttr('mouthMove_ctl.rz', rotYJnt + '.rz', f=1)

        # LipRoll_rotationX connection( lipRoll_jnt.rx = lipRoll_poc.ty )
        cmds.connectAttr(lipRollPoc + '.positionY', '{}.input3D[0].input3Dx'.format(detailPlus))
        cmds.connectAttr('{}.output3Dx'.format(detailPlus), rollJnt + '.rx')

        # LipRoll_translateZ connection #12/26/2019
        '''cmds.setAttr ( lipRollTran_plus + '.operation', 1 ) 
        cmds.connectAttr ( lipPuffPoc + '.positionX', lipRollTran_plus + '.input3D[0].input3Dx') 
        cmds.setAttr (lipRollTran_plus + '.input3D[1].input3Dx', -iniX )
        cmds.connectAttr ( lipRollTran_plus + '.output3Dx',  rollJnts[index] + '.tx')

        cmds.setAttr ( jotXTran_plus + '.operation', 1 ) 
        cmds.connectAttr ( lipPuffPoc + '.positionY', lipRollTran_plus + '.input3D[0].input3Dy') 
        cmds.connectAttr ( lipRollTran_plus + '.output3Dy',  rollJnts[index] + '.ty')'''
        cmds.connectAttr(lipPuffPoc + '.positionY', '{}.input3D[0].input3Dy'.format(detailPlus))
        cmds.connectAttr('{}.output3Dy'.format(detailPlus), rollJnt + '.rz')
        cmds.connectAttr(lipPuffPoc + '.positionZ', '{}.input3D[0].input3Dz'.format(detailPlus))
        cmds.setAttr('{}.input3D[1].input3Dz'.format(detailPlus), -1)
        cmds.connectAttr('{}.output3Dz'.format(detailPlus), rollJnt + '.tz')

    def lipBlendShape(self, upLow):

        bsCrv = upLow + "_lipBS_crv"

        if not cmds.objExists('lipCrv_grp'):
            cmds.group(n='lipCrv_grp', em=True, p='faceMain|crv_grp')

        # create blendShape curve
        tgtCrvList = []
        targetList = ["lipWide", "E", "U", "O", "Happy", "Sad"] # "cornerT", "cornerW", "cornerU", "cornerD"]
        for target in targetList:
            LRPair = []
            for idx, LR in enumerate(["l_", "r_"]):

                visibleVal = 1 if LR == "l_" else 0

                targetCrv = cmds.duplicate(bsCrv, n="{}{}_{}".format(LR, upLow, target), rc=1)[0]
                cmds.setAttr("{}.visibility".format(targetCrv), visibleVal)
                LRPair.append(targetCrv)
                tgtCrvList.append(targetCrv)

            face_utils.Util.mirrorCurve(LRPair[0], LRPair[1])

        lipCrvBS = cmds.blendShape(tgtCrvList, bsCrv, n=upLow + 'LipCrvBS')
        weightList = [(x, 1) for x in range(len(targetList)*2)]
        cmds.blendShape(lipCrvBS[0], edit=True, w=weightList)

    def lipJntForBSCrv(self, numOfCtl):

        prefixDict = self.mirrorOrder_name(numOfCtl)

        parameter = 1.0/(numOfCtl-1)

        if not cmds.objExists("lip_jntGrp"):
            cmds.group(n="lip_jntGrp", em=True, p='faceMain|jnt_grp')
        lipJntGrp = "lip_jntGrp"

        upJnts = []
        loJnts = []
        self.ctlJnts = {"up": upJnts, "lo": loJnts}

        for upLow in ["up", "lo"]:

            crv = upLow + "_lipBS_crv"
            crvShape = cmds.listRelatives(crv, c=1, typ="nurbsCurve")[0]

            for index, prefix in prefixDict.items():

                uplo = "" if index == 0 or index == (numOfCtl-1) else upLow
                pre = prefix[0]
                order = prefix[1]
                name = self.namingMethod(pre, uplo, "Lip", order, "jnt")
                if not cmds.objExists(name):

                    poc = self.createPocNode(name.replace("_jnt", "_poc"), crvShape, parameter*index)
                    pointPos = cmds.getAttr(poc + ".result.position")[0]
                    null = cmds.group(em=1, n=name.replace("_jnt", "_jntP"), p=lipJntGrp)
                    cmds.xform(null, ws=1, t=pointPos)
                    cmds.joint(p=pointPos, n=name)
                    cmds.delete(poc)
                jnt = name
                self.ctlJnts[upLow].append(jnt)

            #bindMethod=cloestDistance
            cmds.skinCluster(crv, self.ctlJnts[upLow], bindMethod=0, normalizeWeights=1, weightDistribution=0, mi=3, omi=True, tsb=1)

    def lipFreeCtl(self, numOfCtl, myCtl):

        dist = cmds.getAttr("helpPanel_grp.headBBox")

        if not cmds.objExists("lipCtl_grp"):
            cmds.group(n="lipCtl_grp", em=True)
        lipCtlGrp = "lipCtl_grp"

        if not myCtl:
            temp = self.genericController("genericCtl", (0, 0, 0), dist[1]/120.0, "circle", self.colorIndex["purple"][0])
            myCtl = temp

        for upLow in ["up", "lo"]:

            parameters = []
            polyCrv = cmds.getAttr("lipFactor.{}_lipCtlGuide".format(upLow))

            if not cmds.objExists("{}_lip_guide_crv".format(upLow)):
                raise RuntimeError("create lip_guide_crv first!!")

            tempGuideCrv = cmds.duplicate("{}_lip_guide_crv".format(upLow), n="{}_tempGuide_crv".format(upLow), rc=1)[0]
            cmds.rebuildCurve(tempGuideCrv, rebuildType=0, spans=numOfCtl - 1, keepRange=0, degree=1)

            for cv in cmds.ls("{}.cv[*]".format(tempGuideCrv), fl=1):

                position = cmds.xform(cv, q=1, ws=1, t=1)
                param = self.getUParam(pntPos=position, crv=polyCrv)
                parameters.append(param)

            cmds.delete(tempGuideCrv)

            lipRollCrv = upLow + "_lipRoll_crv"
            lipPuffCrv = upLow + "_pucker_crv"

            self.rollCvs[upLow] = cmds.ls(lipRollCrv + ".cv[*]", fl=1)
            self.puffCvs[upLow] = cmds.ls(lipPuffCrv + ".cv[*]", fl=1)

            offSetVal = dist[1]/100.0
            if upLow == "up":
                colorID = self.ctlColor["green"]
            else:
                colorID = self.ctlColor["darkGreen"]

            prefixList = self.mirrorOrder_name(numOfCtl)
            upLoList = {x: y for x, y in prefixList.items() if not x == 0 and not x == numOfCtl - 1}
            cornerList = {x: y for x, y in prefixList.items() if x == 0 or x == numOfCtl - 1}

            for index, prefix in upLoList.items():
                # up/lo ctl create
                pre = prefix[0]
                order = prefix[1]
                name = self.namingMethod(pre, upLow, "Lip", order, "ctl")
                ctlChain = self.createMidController(name, dist[1] / 50.0, myCtl, param=parameters[index],
                                                    guideCrv=polyCrv, colorID=colorID)
                ctl, offset, null, poc = [ctlChain[0], ctlChain[1], ctlChain[2], ctlChain[3]]

                cmds.setAttr(offset + ".tz", offSetVal)
                cmds.connectAttr(ctl + ".tx", self.ctlJnts[upLow][index] + ".tx")
                cmds.connectAttr(ctl + ".ty", self.ctlJnts[upLow][index] + ".ty")
                cmds.connectAttr(ctl + ".tz", self.ctlJnts[upLow][index] + ".tz")

                cmds.connectAttr(ctl + ".rx", self.rollCvs[upLow][index] + ".yValue")
                cmds.connectAttr(ctl + ".rz", self.puffCvs[upLow][index] + ".yValue")
                cmds.connectAttr(ctl + ".sz", self.puffCvs[upLow][index] + ".zValue")
                cmds.parent(null, lipCtlGrp)

                self.ctlList.append(ctl)
                self.pocList.append(poc)

        #corner ctl connection
        colorID = self.ctlColor["brightGreen"]
        for ID, prefix in cornerList.items():
            pre = prefix[0]
            order = prefix[1]
            # up/lo ctl create
            name = self.namingMethod(pre, "", "Lip", order, "ctl")
            ctlChain = self.createMidController(name, dist[1] / 50.0, myCtl, param=parameters[ID],
                                                guideCrv=polyCrv, colorID=colorID)
            ctl, offset, null, poc = [ctlChain[0], ctlChain[1], ctlChain[2], ctlChain[3]]

            cmds.setAttr(offset + ".tz", offSetVal)
            cmds.connectAttr(ctl + ".tx", self.ctlJnts[upLow][ID] + ".tx")
            cmds.connectAttr(ctl + ".ty", self.ctlJnts[upLow][ID] + ".ty")
            cmds.connectAttr(ctl + ".tz", self.ctlJnts[upLow][ID] + ".tz")
            cmds.parent(null, lipCtlGrp)

            for upLow in ["up", "lo"]:

                cmds.connectAttr(ctl + ".rx", self.rollCvs[upLow][ID] + ".yValue")
                cmds.connectAttr(ctl + ".rz", self.puffCvs[upLow][ID] + ".yValue")
                cmds.connectAttr(ctl + ".sz", self.puffCvs[upLow][ID] + ".zValue")

            self.ctlList.append(ctl)
            self.pocList.append(poc)

        cmds.parent(lipCtlGrp, "attachCtl_grp")

        face_utils.faceFactorData("lip", "ctlList", self.ctlList)
        face_utils.faceFactorData("lip", "pocList", self.pocList)

        # create detail ctrls
        rollJnt = cmds.ls(upLow + "LipRoll*_jnt", typ="joint")

        for index, jnt in enumerate(rollJnt):
            jntP = cmds.listRelatives(jnt, p=1)[0]
            detailCtrl, null = self.arcController(poc.replace("_poc", "_ctl"), [0, 0, 0], dist[1] / 100.0, "sq")
            cmds.connectAttr("{}.worldMatrix".format(jntP), "{}.offsetParentMatrix".format(null))

            cmds.setAttr(null + ".tz", offSetVal)

            cmds.setAttr(detailCtrl + ".overrideColor", 3)
            # get the plusMinusAverage node
            #print (rollJnt[index], ctl[0], poc)
            cnnt = cmds.listConnections(rollJnt + ".tz", s=1, d=0, p=1)
            detailPlus = cnnt[0].split('.')[0]
            cmds.connectAttr(detailCtrl + ".tx", rollJnt + ".tx")
            cmds.connectAttr(detailCtrl + ".ty", rollJnt + ".ty")
            cmds.connectAttr(detailCtrl + ".tz", detailPlus + ".input3D[2].input3Dz")
            cmds.connectAttr(detailCtrl + ".rx", detailPlus + ".input3D[1].input3Dx")
            cmds.connectAttr(detailCtrl + ".rz", detailPlus + ".input3D[1].input3Dy")
            cmds.connectAttr(detailCtrl + ".s", rollJnt[index] + ".s")

            cmds.parent(null, "lip_dtailCtl_grp")

    def lipShapeBuild(self):

        self.lipShapeRigSetup()

        if not cmds.attributeQuery("controller", node="helpPanel_grp", exists=1):
            raise RuntimeError('Store Ctl object first')

        myCtl = cmds.getAttr("helpPanel_grp.controller")

        self.lipJntForBSCrv(self.numOfCtl)
        self.lipFreeCtl(self.numOfCtl, myCtl)











