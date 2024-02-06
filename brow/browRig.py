import maya.cmds as cmds
import maya.mel as mel
from twitchScript.face import face_utils, curve_utils
reload(face_utils)
reload(curve_utils)

class BrowRig(face_utils.Util):

    def __init__(self):

        super(BrowRig, self).__init__()

        self.orderedVerts = []
        self.browJntList = []
        self.browJntGrp = None
        self.browGuideCrv = None
        self.mirrorJntPrefix = {}
        self.pocList = []
        self.ctlList = []
        self.browCrvGrp = None
        self.detailCtlGrp = None
        self.browCtlCrv = None
        self.shpPocList = []
        self.torqueList = []

    def browJoints(self, jntMultiple):
        """
        Creates a 'browGuide-curve' based on the stored brow vertex selection,
        then generates joints along the curve, doubling the number of vertex selections.
        Returns: None

        """
        if not cmds.objExists("browJnt_grp"):
            cmds.group(em=True, name='browJnt_grp', p="faceMain|jnt_grp")
        self.browJntGrp = "browJnt_grp"

        self.createGuidesDict()

        # the vertices in order
        browVerts = cmds.getAttr("browFactor.browVerts")
        self.orderedVerts = browVerts

        if jntMultiple == 0:

            browEdges = cmds.getAttr("browFactor.browEdges")
            tempCrv = curve_utils.createPolyToCurve(browEdges, name="temp_crv")

            self.browGuideCrv = cmds.rename(tempCrv, "browGuide_crv")
            cmds.rebuildCurve(self.browGuideCrv, rebuildType=0, keepRange=0, keepControlPoints=1, degree=1, ch=1)

            jntLength = len(browVerts)
            self.mirrorJntPrefix = self.mirrorOrder_name(jntLength)
            parameter = 1.0 / (jntLength - 1)

        else:
            orderPos = []
            for vtx in browVerts:
                vtxPos = cmds.xform(vtx, q=1, ws=1, t=1)
                orderPos.append(vtxPos)
            tempCrv = cmds.curve(d=1, ep=orderPos)
            self.browGuideCrv = cmds.rename(tempCrv, "browGuide_crv")
            cmds.rebuildCurve(self.browGuideCrv, rebuildType=0, keepRange=0, keepControlPoints=1, degree=1, ch=0)

            #how many joints need to created
            multValue = [int(jntMultiple), int(jntMultiple)-1]
            jntLength = len(browVerts)*multValue[0]-multValue[1]
            self.mirrorJntPrefix = self.mirrorOrder_name(jntLength)
            parameter = 1.0/(jntLength-1)

        crvShape = cmds.listRelatives(self.browGuideCrv, c=1, type="nurbsCurve")[0]

        if not cmds.objExists('guideCrv_grp'):
            cmds.group(n='guideCrv_grp', em=True, p='faceMain|crv_grp')

        cmds.parent(self.browGuideCrv, "guideCrv_grp")

        cmds.select(cl=1)

        for index, prefix in self.mirrorJntPrefix.items():

            pre = prefix[0]
            order = prefix[1]
            pocName = BrowRig.namingMethod(pre, "", "browJnt", order, "poc")

            poc = self.createPocNode(pocName, crvShape, parameter*index)
            pointPos = cmds.getAttr(poc + ".result.position")[0]

            downBaseJnt = self.createBrowJointChain(pre, order, pointPos, self.browJntGrp)

            self.browJntList.append(downBaseJnt)
            #cmds.delete(poc)

        face_utils.faceFactorData("brow", "browJntList", self.browJntList)

        if not jntMultiple == 0:
            print("browGuideCurve skinnning")
            skinName = self.browGuideCrv.replace("_crv", "_skin")
            browPJnt = [x for x in cmds.listRelatives(self.browJntList, ad=1) if "browP" in x]
            cmds.skinCluster(self.browGuideCrv, browPJnt, tsb=1, normalizeWeights=1, n=skinName)

    def createBrowJointChain(self, prefix, order, pointPos, browJntGrp):
        rotXPivot = cmds.getAttr("helpPanel_grp.rotXPivot")
        rotYPivot = cmds.getAttr("helpPanel_grp.rotYPivot")
        baseName = BrowRig.namingMethod(prefix, "", "browRX", order, "jnt")
        baseJnt = cmds.joint(n=baseName, p=rotXPivot)

        ryJnt = cmds.joint(n=baseName.replace("browRX", "browRY"), p=rotYPivot)
        setBrowJntLabel(ryJnt)
        cmds.joint(n=baseName.replace("browRX", "browP"), p=pointPos)
        tipJnt = cmds.joint(n=baseName.replace("browRX", "brow"))
        setBrowJntLabel(tipJnt)

        cmds.joint(baseJnt, e=1, oj='zyx', secondaryAxisOrient='yup', ch=1, zso=1)

        baseGrp = face_utils.addOffset(baseJnt, None, "_base")

        cmds.parent(baseGrp[1], browJntGrp)

        return baseJnt


    @classmethod
    def attachCrvs(cls, crvSel):
        cmds.attachCurve(crvSel, ch=0, replaceOriginal=0, keepMultipleKnots=0, method=1, blendBias=0.5,
                         blendKnotInsertion=0, parameter=0.1)

    def browFactorSetup(self):
        """
        create curve group and ctl group
        Returns:None

        """

        # revese 'faceFactors.browRotateX_scale'
        if cmds.objExists('browReverse_mult'):
            cmds.delete('browReverse_mult')
        reverseMult = cmds.shadingNode('multiplyDivide', asUtility=True, n='browReverse_mult')
        cmds.connectAttr('browFactor.browUp_scale', reverseMult + ".input1X", f=1)
        cmds.connectAttr('browFactor.browDown_scale', reverseMult + ".input1Z", f=1)
        cmds.connectAttr('browFactor.browRotateY_scale', reverseMult + '.input1Y', f=1)
        cmds.setAttr(reverseMult + ".input2", -1, -1, -1)

        if not cmds.objExists("browCrv_grp"):
            cmds.group(n="browCrv_grp", em=True, p="faceMain|crv_grp")
        self.browCrvGrp = "browCrv_grp"

        if not cmds.objExists("attachCtl_grp"):
            cmds.group(n="attachCtl_grp", em=True, p="bodyHeadTRS")

        # create group node for brow Ctls
        if not cmds.objExists("browCtl_grp"):
            cmds.group(n="browCtl_grp", em=True, p="attachCtl_grp")
        cmds.xform("browCtl_grp", ws=1, t=(0, 0, 0))

        if not cmds.objExists("browDtailCtl_grp"):
            cmds.group(n="browDtailCtl_grp", em=True, p="attachCtl_grp")
        self.detailCtlGrp = "browDtailCtl_grp"
        cmds.xform(self.detailCtlGrp, ws=1, t=(0, 0, 0))

    def browCtl_onHead(self, numOfCtl, myCtl=None):
        """
        the number of ctls (numOfCtl) are created and connected to browCtl_crv
        create brow curve blendShape (for emotion shapes)
        Args:
            numOfCtl: same or less than a numbers of brow joints
            myCtl: controller sample

        Returns: guide curve

        """
        headGeo = cmds.getAttr("helpPanel_grp.headGeo")
        if not headGeo:
            raise RuntimeError("store headGeo string!!")

        # for ctl size and offset measurement
        dist = cmds.getAttr("helpPanel_grp.headBBox")

        if not myCtl:
            temp = BrowRig.genericController("genericCtl", (0, 0, 0), dist[1]/120.0, "circle", self.colorIndex["purple"][0])
            myCtl = temp

        browCtlGrp = "browCtl_grp"
        parameter = 1.0/(numOfCtl-1)
        # whole amount controllers prefix from right to left
        prefixList = self.mirrorOrder_name(numOfCtl)

        #creat Mid Ctls
        for index, prefix in prefixList.items():
            # namingMethod( prefix, position, title, *args)
            pre = prefix[0]
            order = prefix[1]
            name = self.namingMethod(pre, "", "browMid", order, "ctl")

            ctlChain = self.createMidController(name, dist[1]/50.0, myCtl, param=parameter * index,
                                                browCrv=self.browGuideCrv)
            ctl, offset, null, poc = [ctlChain[0], ctlChain[1], ctlChain[2], ctlChain[3]]

            revertMult = cmds.shadingNode('multiplyDivide', asUtility=True, n=name.replace("_jnt", "_revertMult"))

            if "r_" in prefix:
                cmds.setAttr("{}.input2".format(revertMult), 1, -1, -1)
                cmds.setAttr("{}.sx".format(offset), -1)

            else:
                cmds.setAttr("{}.input2".format(revertMult), -1, -1, -1)

            cmds.connectAttr("{}.tx".format(ctl), "{}.input1X".format(revertMult))
            cmds.connectAttr("{}.ty".format(ctl), "{}.input1Y".format(revertMult))
            cmds.connectAttr("{}.outputX".format(revertMult), "{}.tx".format(offset))
            cmds.connectAttr("{}.outputY".format(revertMult), "{}.ty".format(offset))

            cmds.parent(null, browCtlGrp)

            self.ctlList.append(ctl)
            self.pocList.append(poc)

        face_utils.faceFactorData("brow", "ctlList", self.ctlList)
        face_utils.faceFactorData("brow", "pocList", self.pocList)

        # create browCrv blendShape and midControllers connect to BrowCtlCrv
        crvParam = 2.0 / (numOfCtl - 1)
        position = [[-1 + crvParam * i, 0, 0] for i in range(numOfCtl)]

        browTargets = ["BrowSad", "BrowMad", "Furrow", "Relax", "BrowUp", "BrowDown"]
        browCurves = self.LRBrowCrvBlendShape(position, numOfCtl, browTargets)
        cmds.parent(browCurves, self.browCrvGrp)

        # symmetry setup for browTargets
        # for target in browTargets:
        #     self.symmetryBrowTargetCrv("l_{}_crv".format(target), "r_{}_crv".format(target))
        cmds.delete(myCtl)

    def LRBrowCrvBlendShape(self, position, numOfCtl, browTargets):

        browTargetCrv = []

        tempBrowCrv = cmds.curve(d=1, p=position)
        cmds.rebuildCurve(tempBrowCrv, rebuildType=0, spans=numOfCtl-1, keepRange=0, degree=3)
        browCrv = cmds.rename(tempBrowCrv, 'brow_crv')
        #cmds.setAttr("{}Shape.cv[0].xValue".format(browCrv), lock=1)

        for target in browTargets:
            for idx, LR in enumerate(["l_", "r_"]):
                crv = cmds.duplicate(browCrv, n='{}{}_crv'.format(LR, target), rc=1)[0]
                browTargetCrv.append(crv)

        browBS = cmds.blendShape(browTargetCrv, browCrv, n='browBS')
        weight = [(x, 1) for x in range(len(browTargetCrv))]
        cmds.blendShape(browBS[0], edit=True, w=weight)

        browCtlCrv = cmds.duplicate(browCrv, n='browCtl_crv', rc=1)[0]
        cmds.blendShape(browBS[0], edit=True, target=[browCrv, len(browTargetCrv), browCtlCrv, 1])
        cmds.setAttr("{}.{}".format(browBS[0], browCtlCrv), 1)

        tempTorqueCrv = cmds.curve(d=1, p=position)
        cmds.rebuildCurve(tempTorqueCrv, rebuildType=0, spans=numOfCtl-1, keepRange=0, degree=3)
        torqueCrv = cmds.rename(tempTorqueCrv, 'browTorque_crv')
        browCurves = [browCrv, browCtlCrv, torqueCrv] + browTargetCrv

        self.midControllerToBrowCrv(browCtlCrv, torqueCrv)

        return browCurves

    def createMidController(self, name, offValue=None, myCtl=None, param = None, browCrv=None):

        """
        create POC node on guideCurve and get the myCtl attached
        Args:
            name: for poc and controller
            offValue : offset value
            myCtl: controller with unique name
            kwargs : browCrv / parameter
        Returns: list [pointOnCurveInfo , controller's parent Null]

        """
        null = cmds.group(em=1, n=name.replace("_ctl", "_grp"))
        tmpCtl = cmds.duplicate(myCtl, rc=1)[0]

        newCtl = cmds.rename(tmpCtl, name)
        ctl, offset = face_utils.addOffset(newCtl, name, "_off")

        ctlShape = cmds.listRelatives(ctl, c=1)[0]
        cmds.setAttr("{}.overrideEnabled".format(ctlShape), 1)
        if ctl.startswith("c_"):
            cmds.setAttr("{}.overrideColor".format(ctlShape), self.colorIndex["purple"][0])
        elif ctl.startswith("l_"):
            cmds.setAttr("{}.overrideColor".format(ctlShape), self.colorIndex["blue"][1])
        elif ctl.startswith("r_"):
            cmds.setAttr("{}.overrideColor".format(ctlShape), self.colorIndex["blue"][1])

        cmds.parent(offset, null)
        cmds.setAttr("{}.t".format(offset), 0, 0, offValue)

        crvShape = cmds.listRelatives(browCrv, c=1)[0]
        pointOnCrv = self.createPocNode("{}_poc".format(name), crvShape, param)
        cmds.connectAttr(pointOnCrv + ".position", null + ".t")

        return [ctl, offset, null, pointOnCrv]

    def midControllerToBrowCrv(self, browCtlCrv, torqueCrv):
        """
        full range of Mid Ctls connection to left/right curves
        Args:
            browCtlCrv: free form control
            torqueCrv: jnt rotationZ(torque) control

        Returns:

        """
        ctlDict = self.ctlList

        cvs = cmds.ls("{}.cv[*]".format(browCtlCrv), fl=True)
        torqueCvs = cmds.ls("{}.cv[*]".format(torqueCrv), fl=True)

        # mid brow Ctl and browCtlCrv connection
        for index, ctl in enumerate(ctlDict):
            print(ctl, index)
            if ctl.startswith("c_"):

                cmds.connectAttr('{}.tx'.format(ctl), cvs[index+1] + '.xValue')
                cmds.connectAttr('{}.ty'.format(ctl), cvs[index+1] + '.yValue')
                # cmds.connectAttr('{}.ty'.format(ctl), cvs[index + 1] + '.yValue')
                cmds.connectAttr('{}.tz'.format(ctl), cvs[index+1] + '.zValue')
                # cmds.connectAttr('{}.tz'.format(ctl), cvs[index + 1] + '.zValue')

            elif ctl.startswith("l_"):

                if "corner_" in ctl:
                    print(ctl, cvs[index + 1])
                    plusTX = cmds.shadingNode('plusMinusAverage', asUtility=True, n=ctl.replace("_ctl", "_sumTX"))
                    cmds.connectAttr('{}.tx'.format(ctl), "{}.input2D[0].input2Dx".format(plusTX))
                    cmds.connectAttr('{}.tx'.format(ctl), "{}.input2D[0].input2Dy".format(plusTX))
                    cvTX = cmds.getAttr(cvs[index + 1] + '.xValue')
                    cmds.setAttr("{}.input2D[1].input2Dx".format(plusTX), cvTX)
                    cmds.setAttr("{}.input2D[1].input2Dy".format(plusTX), 1)
                    cmds.connectAttr("{}.output2Dx".format(plusTX), cvs[index + 1] + '.xValue')
                    cmds.connectAttr("{}.output2Dy".format(plusTX), cvs[index + 2] + '.xValue')
                    cmds.connectAttr('{}.ty'.format(ctl), cvs[index + 1] + '.yValue')
                    cmds.connectAttr('{}.ty'.format(ctl), cvs[index + 2] + '.yValue')
                    cmds.connectAttr('{}.tz'.format(ctl), cvs[index + 1] + '.zValue')
                    cmds.connectAttr('{}.tz'.format(ctl), cvs[index + 2] + '.zValue')

                    cmds.connectAttr('{}.rz'.format(ctl), torqueCvs[index + 1] + '.yValue')

                else:
                    sumTX = cmds.shadingNode('addDoubleLinear', asUtility=True, n=ctl.replace("_ctl", "_sumTX"))
                    tranX_val = cmds.getAttr(cvs[index + 1] + '.xValue')
                    cmds.connectAttr('{}.tx'.format(ctl), sumTX + '.input1')
                    cmds.setAttr(sumTX + '.input2', tranX_val)
                    cmds.connectAttr(sumTX + '.output', cvs[index + 1] + '.xValue')
                    cmds.connectAttr('{}.ty'.format(ctl), cvs[index + 1] + '.yValue')
                    cmds.connectAttr('{}.tz'.format(ctl), cvs[index + 1] + '.zValue')

                    cmds.connectAttr('{}.rz'.format(ctl), torqueCvs[index + 1] + '.yValue')

            elif ctl.startswith("r_"):
                unitCon = cmds.shadingNode('unitConversion', asUtility=True, n=ctl.replace("_ctl", "_conversion"))
                cmds.connectAttr('{}.tx'.format(ctl), "{}.input".format(unitCon))
                cmds.setAttr("{}.conversionFactor".format(unitCon), -1)

                if "corner_" in ctl:
                    plusTX = cmds.shadingNode('plusMinusAverage', asUtility=True, n=ctl.replace("_ctl", "_sumTX"))
                    cmds.connectAttr("{}.output".format(unitCon), "{}.input2D[0].input2Dx".format(plusTX))
                    cmds.connectAttr("{}.output".format(unitCon), "{}.input2D[0].input2Dy".format(plusTX))
                    cvTX = cmds.getAttr(cvs[index + 1] + '.xValue')
                    cmds.setAttr("{}.input2D[1].input2Dx".format(plusTX), -1)
                    cmds.setAttr("{}.input2D[1].input2Dy".format(plusTX), cvTX)
                    cmds.connectAttr("{}.output2Dx".format(plusTX), cvs[index] + '.xValue')
                    cmds.connectAttr("{}.output2Dy".format(plusTX), cvs[index + 1] + '.xValue')
                    cmds.connectAttr('{}.ty'.format(ctl), cvs[index] + '.yValue')
                    cmds.connectAttr('{}.ty'.format(ctl), cvs[index + 1] + '.yValue')
                    cmds.connectAttr('{}.tz'.format(ctl), cvs[index] + '.zValue')
                    cmds.connectAttr('{}.tz'.format(ctl), cvs[index + 1] + '.zValue')

                    cmds.connectAttr('{}.rz'.format(ctl), torqueCvs[index + 1] + '.yValue')

                else:
                    sumTX = cmds.shadingNode('addDoubleLinear', asUtility=True, n=ctl.replace("_ctl", "_sumTX"))
                    cmds.connectAttr("{}.output".format(unitCon), sumTX + '.input1')
                    tranX_val = cmds.getAttr(cvs[index + 1] + '.xValue')
                    cmds.setAttr(sumTX + '.input2', tranX_val)

                    cmds.connectAttr(sumTX + '.output', cvs[index + 1] + '.xValue')
                    cmds.connectAttr('{}.ty'.format(ctl), cvs[index + 1] + '.yValue')
                    cmds.connectAttr('{}.tz'.format(ctl), cvs[index + 1] + '.zValue')

                    cmds.connectAttr('{}.rz'.format(ctl), torqueCvs[index + 1] + '.yValue')

    def symmetryBrowTargetCrv(self, lCrv, rCrv):

        lCrvShape = cmds.listRelatives(lCrv, c=1, type="nurbsCurve")[0]
        rCrvShape = cmds.listRelatives(rCrv, c=1, type="nurbsCurve")[0]

        CVs = cmds.ls(lCrv + ".cv[*]", l=1, fl=1)
        length = len(CVs)

        for i in range(length):

            if not i == 0:

                multDouble = cmds.createNode('multDoubleLinear', n="{}{:02d}".format(lCrv.replace("_crv", "_mult"), i))
                cmds.setAttr("{}.input2".format(multDouble), -1)
                cmds.connectAttr("{}.cv[{}].xValue".format(lCrvShape, str(i)), "{}.input1".format(multDouble))
                cmds.connectAttr("{}.output".format(multDouble), "{}.cv[{}].xValue".format(rCrvShape, str(i)))

            cmds.connectAttr("{}.cv[{}].yValue".format(lCrvShape, str(i)), "{}.cv[{}].yValue".format(rCrvShape, str(i)))

            cmds.connectAttr("{}.cv[{}].zValue".format(lCrvShape, str(i)), "{}.cv[{}].zValue".format(rCrvShape, str(i)))

    def rebuildBrowRig(self, numOfCtl, jntMultiple, myCtl=None):
        """
        select left brow vertices for (ctl numbers, position) or just change the numOfCtl
        Returns: controllers' amount and position( paratmeter ) change.

        """
        if jntMultiple == 0:
            jntMultiple = 1

        if not cmds.objExists("helpPanel_grp"):
            raise RuntimeError("create helpPanel_grp first!!")

        if not cmds.objExists("browFactor"):
            raise RuntimeError("create browFactor first!!")

        if not cmds.attributeQuery("headGeo", node="helpPanel_grp", exists=1):
            raise RuntimeError("store headGeo string!!")

        headGeo = cmds.getAttr("helpPanel_grp.headGeo")
        orderedVerts = cmds.getAttr("browFactor.browVerts")
        self.browJntList = cmds.getAttr("browFactor.browJntList")
        self.ctlList = cmds.getAttr("browFactor.ctlList")
        self.browGuideCrv = "browGuide_crv"
        self.browCrvGrp = "browCrv_grp"
        self.browJntGrp = "browJnt_grp"
        self.detailCtlGrp = "browDtailCtl_grp"

        if cmds.objExists(myCtl):
            tempCtl = cmds.duplicate(myCtl, rc=1)[0]
            myCtl = cmds.rename(tempCtl, "temp_ctl")

        else:
            tempCtl = cmds.duplicate(self.ctlList[0], rc=1)[0]
            myCtl = cmds.rename(tempCtl, "temp_ctl")
            cmds.parent(myCtl, w=1)

        if len(self.browJntList) == len(orderedVerts)*int(jntMultiple)-(int(jntMultiple)-1):
            print("changing numOfCtl")

            oldCtlLength = len(self.ctlList)

            newCtlLength = numOfCtl
            if newCtlLength == oldCtlLength:
                raise RuntimeError("select different number of controllers or joint multiple")

            dist = cmds.getAttr("helpPanel_grp.headBBox")
            offValue = dist[1] / 50.0
            parameter = 1.0 / (newCtlLength - 1)

            #kwargs = {"ctlList": self.ctlList, "browGuideCrv": self.browGuideCrv}
            self.cleanUpForBrowRebuild(ctlList=self.ctlList, browGuideCrv=self.browGuideCrv)

            browCrvList = cmds.listRelatives("browCrv_grp", c=1)
            for crv in browCrvList:
                cmds.rename(crv, "{}_old".format(crv))

            # whole amount controllers from right to left
            prefixList = self.mirrorOrder_name(newCtlLength)

            self.ctlList = []
            self.pocList = []
            for index, prefix in prefixList.items():
                # namingMethod( prefix, position, title, *args)
                pre = prefix[0]
                order = prefix[1]
                name = self.namingMethod(pre, "", "browMid", order, "ctl")

                ctlChain = self.createMidController(name, offValue, myCtl, param=parameter*index, browCrv=self.browGuideCrv)
                ctl, offset, null, poc = [ctlChain[0], ctlChain[1], ctlChain[2], ctlChain[3]]

                cmds.parent(null, "browCtl_grp")
                if "r_" in prefix:
                    cmds.setAttr("{}.sx".format(offset), -1)

                self.ctlList.append(ctl)
                self.pocList.append(poc)

            face_utils.faceFactorData("brow", "ctlList", self.ctlList)
            face_utils.faceFactorData("brow", "pocList", self.pocList)

            parameter = 2.0 / (numOfCtl - 1)
            position = [[-1 + parameter * i, 0, 0] for i in range(numOfCtl)]
            tempBrowCrv = cmds.curve(d=1, p=position)
            cmds.rebuildCurve(tempBrowCrv, rebuildType=0, spans=numOfCtl - 1, keepRange=0, degree=3)

            browTargets = ["BrowSad", "BrowMad", "Furrow", "Relax", "BrowUp", "BrowDown"]
            newCrvList = self.LRBrowCrvBlendShape(position, numOfCtl, browTargets)

            # poc node is attached to brow_crv, not browCtl_crv
            newBrowCrv = "brow_crv"
            newBrowCrvShp = cmds.listRelatives(newBrowCrv, c=1, type="nurbsCurve")[0]
            oldCrvShp = cmds.listRelatives("{}_old".format(newBrowCrv), c=1, type="nurbsCurve")[0]
            pocList = cmds.listConnections(oldCrvShp, s=0, d=1, type="pointOnCurveInfo")
            for poc in pocList:
                cmds.connectAttr(newBrowCrvShp + '.worldSpace', poc + '.inputCurve', f=1)

            browCrvList = cmds.listRelatives("browCrv_grp", c=1)
            cmds.delete(browCrvList)
            cmds.parent(newCrvList, "browCrv_grp")

            browPJnt = [x for x in cmds.listRelatives( self.browJntList, ad=1) if "browP" in x]
            skin = cmds.skinCluster("browGuide_crv", browPJnt, tsb=1, normalizeWeights=1, n="browGuide_skin")
            cmds.delete(myCtl)

        else:
            print("changing numOfJnt")
            edgeLoop = BrowRig.checkEdgeLoopWithSelectedVtx(orderedVerts)
            if edgeLoop:
                if len(self.browJntList) == len(orderedVerts):
                    raise RuntimeError("select the different set of vertex ")

            self.cleanUpForBrowRebuild(ctlList=self.ctlList, headGeo=headGeo, browJntList=self.browJntList)
            cmds.delete(self.browGuideCrv)
            orderPos = []

            for vtx in orderedVerts:
                vtxPos = cmds.xform(vtx, q=1, ws=1, t=1)
                orderPos.append(vtxPos)
            tempCrv = cmds.curve(d=1, ep=orderPos)
            self.browGuideCrv = cmds.rename(tempCrv, "browGuide_crv")
            cmds.rebuildCurve(self.browGuideCrv, rebuildType=0, keepRange=0, keepControlPoints=1, degree=1, ch=0)
            cmds.parent(self.browGuideCrv, "guideCrv_grp")
            crvShape = cmds.listRelatives(self.browGuideCrv, c=1)[0]

            self.ctlList = []
            self.pocList = []

            # how many joints need to created
            multValue = [int(jntMultiple), int(jntMultiple) - 1]
            jntLength = len(orderedVerts) * multValue[0] - multValue[1]
            self.mirrorJntPrefix = self.mirrorOrder_name(jntLength)
            parameter = 1.0 / (jntLength - 1)

            cmds.select(cl=1)
            self.browJntList = []
            for index, prefix in self.mirrorJntPrefix.items():
                pre = prefix[0]
                order = prefix[1]
                pocName = BrowRig.namingMethod(pre, "", "browJnt", order, "poc")
                poc = self.createPocNode(pocName, crvShape, parameter * index)
                pointPos = cmds.getAttr(poc + ".result.position")[0]

                downBaseJnt = self.createBrowJointChain(pre, order, pointPos, "browJnt_grp")

                self.browJntList.append(downBaseJnt)
                cmds.delete(poc)

            face_utils.faceFactorData("brow", "browJntList", self.browJntList)

            browPJnt = [x for x in cmds.listRelatives( self.browJntList, ad=1) if "browP" in x]
            skin = cmds.skinCluster("browGuide_crv", browPJnt, tsb=1, normalizeWeights=1, n="browGuide_skin")

            self.browCtl_onHead(numOfCtl, myCtl)
            self.connectBrowCtrls()

    def cleanUpForBrowRebuild(self, **kwargs):
        """
        kwarg : ctlList = [], headGeo = None, browJntList = [], browGuideCrv =None
        """
        if kwargs:
            for key, value in kwargs.items():
                if key == "ctlList":
                    print("delete ctls and poc nodes")
                    nullList = cmds.listRelatives(cmds.listRelatives(value, p=1), p=1)
                    cmds.select(nullList)
                    cmds.delete()
                    AllPoc = cmds.listConnections("browGuide_crv", s=0, d=1, type="pointOnCurveInfo")
                    if AllPoc:
                        cmds.delete(AllPoc)

                if key == "headGeo":
                    print("delete headGeo skinCluster")
                    cmds.select(value, r=1)
                    self.getSkin()
                    if self.skin:
                        cmds.setAttr("{}.envelope".format(self.skin), 0)
                        cmds.select(value)
                        mel.eval("DeleteHistory")

                if key == "browJntList":
                    print("delete browJnts and related nodes")
                    allConnections = set(cmds.listHistory(value, il=0))
                    dump = [x for x in allConnections if x not in ["browFactor", "browReverse_mult"]]
                    shapes = [x for x in dump if "Shape" in x]
                    curveList = set(cmds.listRelatives(shapes, p=1))

                    cmds.delete(dump, curveList)

                    for grp in ["browDtailCtl_grp", "browCrv_grp", "browJnt_grp"]:
                        if cmds.objExists(grp):

                            items = cmds.listRelatives(grp, c=1)
                            if items:
                                cmds.select(items)
                                cmds.delete()

                if key == "browGuideCrv":
                    print("delete {} skinCluster".format(value))
                    if cmds.objExists(value):

                        cmds.select(value, r=1)
                        browSkin = self.getSkin()
                        if browSkin:
                            cmds.setAttr("{}.envelope".format(self.skin), 0)
                            mel.eval("DeleteHistory")

    def connectBrowCtrls(self):
        """
        shpPoc( brow_crv ) / torquePoc( torque_crv ) / detail ctl are created to control joint chain
        Returns: None

        """
        # connection from browCrv-POC and detail-ctls to browJnts
        dist = cmds.getAttr("helpPanel_grp.headBBox")

        jntDict = self.browJntList
        increment = 1.0 / (len(jntDict) - 1)

        shpPocList = []
        torqueList = []
        # attach poc node on l/r_browCrv

        ctlCrvShape = cmds.listRelatives("brow_crv", c=1, type="nurbsCurve")[0]
        torqueCrvShape = cmds.listRelatives("browTorque_crv", c=1, type="nurbsCurve")[0]

        for index, jnt in enumerate(jntDict):

            name = jnt.replace("browRX", "brow")
            shpPoc = self.createPocNode(name.replace("_jnt", "_shpPoc"), ctlCrvShape, increment*index)
            shpPocList.append(shpPoc)

            torquePoc = self.createPocNode(name.replace("_jnt", "_torquePoc"), torqueCrvShape, increment*index)
            torqueList.append(torquePoc)

        self.shpPocList = shpPocList
        self.torqueList = torqueList

        prefixDict = self.mirrorOrder_name(len(self.browJntList))

        browPJnts = []

        # attach detail ctls on the browGuideCrv / connect l/r_browCrv and detail ctls to browJnts
        nullList = cmds.listRelatives(cmds.listRelatives(self.ctlList, p=1), p=1)

        for index, jnt in enumerate(self.browJntList):

            jntP = cmds.listRelatives(cmds.listRelatives(jnt, c=1), c=1)[0]
            dtailCtl = self.browDetailCtl(prefixDict[index], jntP, float(dist[1])/120.0, float(dist[1])/150.0)
            browJntChild = cmds.listRelatives(jnt, ad=1)
            # [u'c_brow00_jnt', u'c_browP00_jnt', u'c_browRY00_jnt']
            browPJnts.append(browJntChild[1])
            attrs = ["rx", "ry", "v"]
            face_utils.limitAttribute(dtailCtl, attrs)
            # connect
            self.browCrvToJnt(jnt, browJntChild, dtailCtl, self.shpPocList[index], self.torqueList[index])

        # for index in range(len(self.orderedVerts)):
        #     print (index)
        #     topJnt = self.browJntList[jntMultiple*index]
        #     jntP = [x for x in cmds.listRelatives(topJnt, ad=1) if "browP" in x][0]
        #     print (jntP, nullList[index])
        #     cmds.connectAttr("{}.worldMatrix".format(jntP), "{}.offsetParentMatrix".format(nullList[index]))

    def browDetailCtl(self, prefix, jntP, offValue, size):

        name = self.namingMethod(prefix[0], "", "detail", prefix[1], "ctl")
        browCtl = self.arcController(name, [0, 0, 0], size/2, 'sq')
        dtailCtl, offNull = [browCtl[0], browCtl[1]]

        #parentCtl = cmds.group(n=name.replace("_ctl", "_prnt"), em=1, p=self.detailCtlGrp)
        cmds.connectAttr("{}.worldMatrix".format(jntP), "{}.offsetParentMatrix".format(offNull))

        cmds.parent(offNull, self.detailCtlGrp)
        if "r_" == prefix[0]:
            cmds.setAttr("{}.sx".format(offNull), -1)

        cmds.setAttr("{}.t".format(offNull), 0, 0, offValue)

        return dtailCtl

    def browCrvToJnt(self, jnt=None, browJntList=[], dtailCtl=None,  shapePOC=None, torquePoc =None):
        """
        browCrv shpPoc translate data to joint rotation
        browCrvCtlToJnt( c_browRX00_jnt, ['c_brow00_jnt'...], browCtlBase, poc )
        """
        # connect browCtrlCurve and controller to the brow joints
        jntMult = cmds.shadingNode('multiplyDivide', asUtility=True, n=browJntList[0].replace("_jnt", "_mult"))
        browXYZSum = cmds.shadingNode('plusMinusAverage', asUtility=True, n=browJntList[0].replace("_jnt", "_sum"))

        # POC TX zero out
        cmds.connectAttr(shapePOC + '.positionX', browXYZSum + '.input3D[0].input3Dx')
        initX = cmds.getAttr(shapePOC + '.positionX')
        cmds.setAttr(browXYZSum + '.input3D[1].input3Dx', -initX)

        # 'browFactor.browUp_scale', ".input1X"
        # 'browFactor.browDown_scale', ".input1Z"
        # 'browFactor.browRotateY_scale','.input1Y'

        # brow up down setup
        cmds.connectAttr('browReverse_mult.outputZ', jntMult + ".input2Z")
        cmds.connectAttr(shapePOC + '.positionY', jntMult + ".input1Z")
        cmds.connectAttr(jntMult + '.outputZ', jnt + '.rx')

        # brow(up, down) Positive for browWide setup
        cmds.connectAttr('{}.positionY'.format(shapePOC), '{}.input1Y'.format(jntMult))
        cmds.connectAttr('browFactor.browDown_scale', '{}.input2Y'.format(jntMult))

        cmds.connectAttr(shapePOC + '.positionZ', browXYZSum + '.input3D[0].input3Dz')
        cmds.connectAttr(dtailCtl + '.tz', browXYZSum + '.input3D[1].input3Dz')

        browJnt = browJntList[0]  # tip joint(end joint of the chain)
        # extra rotate ctrl for browJnt
        cmds.connectAttr(dtailCtl + '.ty', browJnt + '.ty')
        cmds.connectAttr(browXYZSum + '.output3Dz', browJnt + '.tz')
        #joint rotateZ setup
        cmds.connectAttr( '{}.positionY'.format(torquePoc), browXYZSum + '.input3D[0].input3Dy')
        cmds.connectAttr(dtailCtl + '.rz', browXYZSum + '.input3D[1].input3Dy')

        # add browCtl.tx
        rotYJnt = browJntList[-1] #[u'c_brow00_jnt', u'c_browP00_jnt', u'c_browRY00_jnt']
        cmds.connectAttr(browXYZSum + '.output3Dx', jntMult + '.input1X')

        cmds.connectAttr('browFactor.browDown_scale', jntMult + '.input2X')
        cmds.connectAttr(jntMult + '.outputX', rotYJnt + '.ry')

        # detail ctl ty/ rz inverse setup for right side
        if jnt.startswith("r_"):

            ctlMult = cmds.shadingNode('multiplyDivide', asUtility=True, n=browJntList[0].replace("_jnt", "_inverse"))
            cmds.setAttr("{}.input2".format(ctlMult), -1, -1, -1)
            cmds.connectAttr(dtailCtl + '.tx', "{}.input1X".format(ctlMult))
            cmds.connectAttr("{}.outputX".format(ctlMult), browJnt + '.tx')

            cmds.connectAttr(browXYZSum + '.output3Dy', "{}.input1Z".format(ctlMult))
            cmds.connectAttr("{}.outputZ".format(ctlMult), '{}.rz'.format(browJnt))

        else:

            cmds.connectAttr('{}.tx'.format(dtailCtl), '{}.tx'.format(browJnt))
            cmds.connectAttr(browXYZSum + '.output3Dy', browJnt + '.rz')

        cmds.connectAttr(dtailCtl + '.s', browJnt + '.s')

    def build(self, numberOfCtls, jntMultiple, myCtl=None):

        self.browJoints(jntMultiple)
        self.browFactorSetup()
        self.browCtl_onHead(int(numberOfCtls), myCtl)
        self.connectBrowCtrls()

    def browWideJnt(self, uplo, numOfCtl):

        if not cmds.attributeQuery("{}WideRX_follow".format(uplo), node="browFactor", exists=1):
            cmds.addAttr("browFactor", longName='{}WideRX_follow'.format(uplo), attributeType='float', dv=0.8)

        if not cmds.attributeQuery("{}WideRY_follow".format(uplo), node="browFactor", exists=1):
            cmds.addAttr("browFactor", longName='{}WideRY_follow'.format(uplo), attributeType='float', dv=0.8)

        if not cmds.objExists("browCrv_grp"):
            raise RuntimeError('create Hierarchy first!!')

        if not cmds.objExists("browWideCrv_grp"):
            cmds.group(em=1, n='browWideCrv_grp', p='browCrv_grp')

        #l_browRX_06_jnt
        browJnts = cmds.getAttr("browFactor.browJntList")
        if not browJnts:
            raise RuntimeError("create browJoint chain")
        #l_upBrowWide_06_jnt / l_loBrowWide_06_jnt
        browWide = [x.replace("browRX", "{}BrowWide".format(uplo)) for x in browJnts]
        if [jot for jot in browWide if cmds.objExists(jot)]:
            raise RuntimeError(" {}BrowWide joint chain already exists".format(uplo))

        parm = 1.0 / (len(browJnts) - 1)
        #if uplo == "lo":
        parameter = 1.0 / (int(numOfCtl) - 1)

        position = [[-1 + parameter*i*2, 0.5, 0] for i in range(int(numOfCtl))]

        tempBrowCrv = cmds.curve(d=1, p=position)
        cmds.rebuildCurve(tempBrowCrv, rebuildType=0, spans=(int(numOfCtl) - 1), keepRange=0, degree=3)
        upWideCrv = cmds.rename(tempBrowCrv, '{}BrowWideRaise_crv'.format(uplo))
        #symmetrizedCrv(self.upWideCrv)
        upCrvShape = cmds.listRelatives(upWideCrv, c=1)[0]
        cmds.parent(upWideCrv, 'browWideCrv_grp')

        loWideCrv = cmds.duplicate(upWideCrv, n='{}BrowWideLower_crv'.format(uplo), rc=1)[0]
        #symmetrizedCrv(loWideCrv)
        loCrvShape = cmds.listRelatives(loWideCrv, c=1)[0]

        for index, jnt in enumerate(browJnts):

            jntNames = jnt.split("_")
            title = jntNames[1].replace("browRX", "{}_browWide".format(uplo))

            rotXMult = cmds.listConnections(jnt, s=1, d=0, skipConversionNodes=1, type="multiplyDivide")[0]

            if not rotXMult:
                raise RuntimeError("create brow mainRig first!!")

            browRXWide = cmds.duplicate(jnt, n=jnt.replace("browRX", title), rc=1)[0]
            childRYWide = cmds.listRelatives(browRXWide, c=1)[0]
            browRYWide = cmds.rename(childRYWide, browRXWide.replace(title, "{}_browWideRY".format(uplo)))
            cmds.delete(cmds.listRelatives(browRYWide, c=1)[0])

            upBrowPoc = self.createPocNode("{}RaiseCrv_poc{}".format(title, index), upCrvShape, parm*index)

            loBrowPoc = self.createPocNode("{}LowerCrv_poc{}".format(title, index), loCrvShape, parm*index)

            self.connectBrowWideJnt(upBrowPoc, loBrowPoc, rotXMult, browRXWide)
            # l_loBrowWide_04_jnt
            setBrowJntLabel(browRYWide, position=uplo)

        # else:
        #     zWideCrv = cmds.duplicate('loBrowWide_upCrv', n='upBrowWide_zCrv', rc=1)[0]
        #     #symmetrizedCrv(zWideCrv)
        #     zCrvShape = cmds.listRelatives(zWideCrv, c=1)[0]
        #
        #     for index, jnt in enumerate(browJnts):
        #
        #         jntNames = jnt.split("_")
        #         title = jntNames[1].replace("browRX", "up_browWide")
        #
        #         rotXMult = cmds.listConnections(jnt, s=1, d=0, skipConversionNodes=1, type="multiplyDivide")[0]
        #
        #         if not rotXMult:
        #             raise RuntimeError("create brow mainRig first!!")
        #
        #         browRXWide = cmds.duplicate(jnt, n=jnt.replace("browRX", title), rc=1)[0]
        #         childRYWide = cmds.listRelatives(browRXWide, c=1)[0]
        #
        #         browRYWide = cmds.rename(childRYWide, browRXWide.replace(title, "up_browWideRY"))
        #         cmds.delete(cmds.listRelatives(browRYWide, c=1)[0])
        #
        #         zBrowPoc = self.createPocNode("{}UpCrv_poc".format(title, index), zCrvShape, parm*index)
        #
        #         self.connectUpBrowWideJnt(rotXMult, zBrowPoc, browRXWide)
        #
        #         setBrowJntLabel(browRYWide, position=uplo)

    def connectBrowWideJnt(self, browUpPoc, browLoPoc, rotXMult, browWideJnt, **kwargs):

        upTxPlus = cmds.shadingNode('addDoubleLinear', asUtility=True, n=browWideJnt.replace("_jnt", "_upAdd"))
        loTxPlus = cmds.shadingNode('addDoubleLinear', asUtility=True, n=browWideJnt.replace("_jnt", "_loAdd"))
        wideRYJntPlus = cmds.shadingNode('addDoubleLinear', asUtility=True, n=browWideJnt.replace("_jnt", "_RYAdd"))
        multDouble = cmds.shadingNode('multDoubleLinear', asUtility=True, n=browWideJnt.replace("_jnt", "_multDouble"))
        wideUpMult = cmds.shadingNode('multiplyDivide', asUtility=True, n=browWideJnt.replace("_jnt", "_upMult"))
        wideLoMult = cmds.shadingNode('multiplyDivide', asUtility=True, n=browWideJnt.replace("_jnt", "_loMult"))
        wideCond = cmds.shadingNode("condition", asUtility=1, n=browWideJnt.replace("_jnt", "_cond"))
        #wideRotSum = cmds.shadingNode('plusMinusAverage', asUtility=True, n=utilName.replace("_jnt", "_widePlus"))
        upInitialX = cmds.getAttr(browUpPoc + '.positionX')
        loInitialX = cmds.getAttr(browLoPoc + '.positionX')

        # browJnt "rotate-up" connection
        # outputZ : <-- positionY / outputX : <-- positionX
        cmds.connectAttr("{}.outputZ".format(rotXMult), '{}.input1X'.format(wideUpMult))
        cmds.connectAttr("{}.outputY".format(rotXMult), '{}.input1Y'.format(wideUpMult))
        cmds.connectAttr("{}.outputY".format(rotXMult), '{}.input1Z'.format(wideUpMult))
        # tx --> ry pairs
        cmds.connectAttr("{}.positionX".format(browUpPoc), '{}.input1'.format(upTxPlus))
        cmds.setAttr('{}.input2'.format(upTxPlus), -upInitialX)
        cmds.connectAttr('{}.output'.format(upTxPlus), '{}.input2Y'.format(wideUpMult))

        cmds.connectAttr("{}.positionY".format(browUpPoc), '{}.input2X'.format(wideUpMult))
        cmds.connectAttr("{}.positionZ".format(browUpPoc), '{}.input2Z'.format(wideUpMult))

        cmds.connectAttr('{}.outputZ'.format(rotXMult), wideCond + ".firstTerm")
        cmds.setAttr(wideCond + ".secondTerm", 0)
        cmds.setAttr(wideCond + ".operation", 4)

        cmds.connectAttr('{}.outputX'.format(wideUpMult), "{}.colorIfTrueR".format(wideCond))
        cmds.connectAttr('{}.outputY'.format(wideUpMult), "{}.colorIfTrueG".format(wideCond))
        cmds.connectAttr("{}.outputZ".format(wideUpMult), "{}.colorIfTrueB".format(wideCond))

        # browJnt "rotate-down" connection
        cmds.connectAttr("{}.outputZ".format(rotXMult), '{}.input1X'.format(wideLoMult))
        cmds.connectAttr("{}.outputY".format(rotXMult), '{}.input1Y'.format(wideLoMult))
        cmds.connectAttr("{}.outputY".format(rotXMult), '{}.input1Z'.format(wideLoMult))

        cmds.connectAttr("{}.positionX".format(browLoPoc), '{}.input1'.format(loTxPlus))
        cmds.setAttr('{}.input2'.format(loTxPlus), -loInitialX)
        cmds.connectAttr('{}.output'.format(loTxPlus), '{}.input2Y'.format(wideLoMult))
        cmds.connectAttr("{}.positionY".format(browLoPoc), '{}.input2X'.format(wideLoMult))
        cmds.connectAttr("{}.positionZ".format(browLoPoc), '{}.input2Z'.format(wideLoMult))

        cmds.connectAttr('{}.outputX'.format(wideLoMult), "{}.colorIfFalseR".format(wideCond))
        cmds.connectAttr('{}.outputY'.format(wideLoMult), "{}.colorIfFalseG".format(wideCond))
        cmds.connectAttr('{}.outputZ'.format(wideLoMult), "{}.colorIfFalseB".format(wideCond))

        # wideJnt left/right setup (rotation value)
        loWideRYJnt = cmds.listRelatives(browWideJnt, c=1)[0]
        cmds.connectAttr("{}.outColorR".format(wideCond), '{}.rx'.format(browWideJnt))
        cmds.connectAttr("{}.outColorG".format(wideCond), '{}.input1'.format(wideRYJntPlus))
        cmds.connectAttr("{}.outColorB".format(wideCond), '{}.tz'.format(browWideJnt))

        cmds.connectAttr("{}.outputX".format(rotXMult), '{}.input1'.format(multDouble))
        cmds.connectAttr("browFactor.loWideRY_follow", '{}.input2'.format(multDouble))

        cmds.connectAttr("{}.output".format(multDouble), '{}.input2'.format(wideRYJntPlus))

        cmds.connectAttr("{}.output".format(wideRYJntPlus), '{}.ry'.format(loWideRYJnt))

    def connectUpBrowWideJnt(self, rotXMult, zBrowPoc, upWideJnt):

        upWideMult = cmds.shadingNode('multiplyDivide', asUtility=True, n=upWideJnt.replace("_jnt", "_mult"))
        remapVal = cmds.shadingNode('remapValue', asUtility=True, n=upWideJnt.replace("_jnt", "_remap"))
        upWideRYJnt = cmds.listRelatives(upWideJnt, c=1)[0]
        cmds.connectAttr(rotXMult + ".outputZ", upWideMult + ".input1X")
        cmds.connectAttr("{}.positionY".format(zBrowPoc), upWideMult + ".input2X")
        cmds.connectAttr(upWideMult + ".outputX", upWideJnt + ".rx")

        cmds.connectAttr(rotXMult + ".outputX", upWideMult + ".input1Y")
        cmds.connectAttr("browFactor.loWideRY_follow", upWideMult + ".input2Y")
        cmds.connectAttr(upWideMult + ".outputY", upWideRYJnt + ".ry")

        # first term is less 0 == brow rotX up : move upWide tz forward
        lowWideJnt = upWideJnt.replace("up_browWide", "lo_browWide")
        wideCond = cmds.listConnections(lowWideJnt, s=1, d=0, type="condition")[0]
        cmds.connectAttr("{}.colorIfTrueR".format(wideCond), "{}.inputValue".format(remapVal))
        cmds.setAttr("{}.inputMax".format(remapVal), -10)
        cmds.setAttr("{}.outputMax".format(remapVal), -1)
        cmds.connectAttr("{}.outValue".format(remapVal), '{}.input1Z'.format(upWideMult))
        cmds.connectAttr("{}.positionZ".format(zBrowPoc), '{}.input2Z'.format(upWideMult))
        cmds.connectAttr(upWideMult + ".outputZ", upWideJnt + ".tz")

def symmetrizedCrv(crv):

    crvShape = cmds.listRelatives(crv, c=1, type="nurbsCurve")[0]

    CVs = cmds.ls(crv + ".cv[*]", l=1, fl=1)
    length = len(CVs)

    for i in range((length-1)/2):

        multDouble = cmds.createNode('multDoubleLinear', n="{}{:02d}".format(crv.replace("_crv", "_mult"), i))
        cmds.setAttr("{}.input2".format(multDouble), -1)
        cmds.connectAttr("{}.cv[{}].xValue".format(crv, str(length-1 - i)), "{}.input1".format(multDouble))
        cmds.connectAttr("{}.output".format(multDouble), "{}.cv[{}].xValue".format(crvShape, str(i)))

        cmds.connectAttr("{}.cv[{}].yValue".format(crv, str(length-1 - i)), "{}.cv[{}].yValue".format(crvShape, str(i)))

        cmds.connectAttr("{}.cv[{}].zValue".format(crv, str(length-1 - i)), "{}.cv[{}].zValue".format(crvShape, str(i)))

def setBrowJntLabel(jnt, **kwargs):
    """

    Args:
        jnt: ArcName convention = prefix["l_","r_"] + position["up","lo"] + title + order["corner","01"...]
        kwargs: position = "up","lo"
    Returns:

    """

    if jnt.startswith("l_"):
        cmds.setAttr(jnt + '.side', 1)

    elif jnt.startswith("r_"):
        cmds.setAttr(jnt + '.side', 2)

    elif jnt.startswith("c_"):
        cmds.setAttr(jnt + '.side', 0)

    cmds.setAttr(jnt + '.type', 18)
    if kwargs: #l_browRY_05_jnt
        number = jnt.split("_")[3]
        title = jnt.split("_")[2]
        uplo = kwargs["position"]
        cmds.setAttr(jnt + '.otherType', "{}_{}_{}".format(uplo, title, number), type="string")
    else:
        number = jnt.split("_")[2]
        title = jnt.split("_")[1]
        cmds.setAttr(jnt + '.otherType', "{}_{}".format(title, number), type="string")



#_________old scripts_________#
def createBrowCtl(jntNum, orderJnts):
    """
    create extra controllor for the panel
    """
    ctlP = "browDetailCtrl0"
    kids = cmds.listRelatives(ctlP, ad=True, type='transform')
    if kids:
        cmds.delete(kids)

    attTemp = ['scaleX', 'scaleY', 'scaleZ', 'rotateX', 'rotateY', 'tz', 'visibility']
    index = 0
    for jnt in orderJnts:
        detailCtl = cmds.circle(n='browDetail' + str(index + 1).zfill(2), ch=False, o=True, nr=(0, 0, 1), r=0.2)
        detailPlane = cmds.nurbsPlane(ax=(0, 0, 1), w=0.1, lengthRatio=10, degree=3, ch=False,
                                      n='browDetail' + str(index + 1).zfill(2) + 'P')
        increment = 2.0 / (jntNum - 1)
        cmds.parent(detailCtl[0], detailPlane[0], relative=True)
        cmds.parent(detailPlane[0], ctlP, relative=True)
        cmds.setAttr(detailPlane[0] + '.tx', -2 + increment * index * 2)
        cmds.xform(detailCtl[0], r=True, s=(0.2, 0.2, 0.2))
        cmds.setAttr(detailCtl[0] + ".overrideEnabled", 1)
        cmds.setAttr(detailCtl[0] + "Shape.overrideEnabled", 1)
        cmds.setAttr(detailCtl[0] + "Shape.overrideColor", 20)

        cmds.transformLimits(detailCtl[0], tx=(-.4, .4), etx=(True, True))
        cmds.transformLimits(detailCtl[0], ty=(-.8, .8), ety=(True, True))

        for att in attTemp:
            cmds.setAttr(detailCtl[0] + "." + att, lock=True, keyable=False, channelBox=False)

        index = index + 1


# "browDetail" controls in twitchPanel match up with brow joints
def browDetailCtls_old():
    browJnts = cmds.ls("*browBase*_jnt", fl=True, type="joint")
    jntNum = len(browJnts)

    ctlP = "browDetailCtrl0"
    kids = cmds.listRelatives(ctlP, ad=True, type='transform')
    if kids:
        cmds.delete(kids)

    attTemp = ['scaleX', 'scaleY', 'scaleZ', 'rotateX', 'rotateY', 'tz', 'visibility']

    # left right mirror
    ctlColor = [2, 3, 24, 23, 22, 21, 20, 19, 18, 17, 16, 14, 13, 9, 7, 6, 4, 1]
    increment = (2.0 + (jntNum - 1) / 10) / (jntNum - 1)

    cPlane = cmds.nurbsPlane(ax=(0, 0, 1), w=0.1, lengthRatio=10, degree=3, ch=False, n='c_browDetail01P')
    cDetailCtl = arcController('c_browDetail01', (0, 0, 0), .2, 'cc')
    cmds.setAttr(cDetailCtl[0] + ".overrideColor", 1)
    cmds.parent(cDetailCtl[0], cPlane[0], relative=True)
    cmds.parent(cPlane[0], ctlP, relative=True)
    cmds.delete(cDetailCtl[1])
    cmds.setAttr(cPlane[0] + '.tx', 0)
    cmds.xform(cDetailCtl[0], r=True, s=(0.2, 0.2, 0.2))
    for att in attTemp:
        cmds.setAttr(cDetailCtl[0] + "." + att, lock=True, keyable=False, channelBox=False)

    for index in range(jntNum / 2):

        rPlane = cmds.nurbsPlane(ax=(0, 0, 1), w=0.1, lengthRatio=10, degree=3, ch=False,
                                 n='r_browDetail' + str(index + 1).zfill(2) + 'P')
        rDetailCtl = arcController('r_browDetail' + str(index + 1).zfill(2), (0, 0, 0), .25, 'sq')
        cmds.setAttr(rDetailCtl[0] + ".overrideColor", ctlColor[index])
        cmds.parent(rDetailCtl[0], rPlane[0], relative=True)
        cmds.parent(rPlane[0], ctlP, relative=True)
        # get rid of parent(null) node
        cmds.delete(rDetailCtl[1])
        cmds.setAttr(rPlane[0] + '.tx', increment * (index + 1) * -2)
        cmds.xform(rDetailCtl[0], r=True, s=(0.2, 0.2, 0.2))
        for att in attTemp:
            cmds.setAttr(rDetailCtl[0] + "." + att, lock=True, keyable=False, channelBox=False)

        lPlane = cmds.nurbsPlane(ax=(0, 0, 1), w=0.1, lengthRatio=10, degree=3, ch=False,
                                 n='l_browDetail' + str(index + 1).zfill(2) + 'P')
        lDetailCtl = arcController('l_browDetail' + str(index + 1).zfill(2), (0, 0, 0), .2, 'cc')
        cmds.setAttr(lDetailCtl[0] + ".overrideColor", ctlColor[index])
        cmds.parent(lDetailCtl[0], lPlane[0], relative=True)
        cmds.parent(lPlane[0], ctlP, relative=True)
        # get rid of parent(null) node
        cmds.delete(lDetailCtl[1])
        cmds.setAttr(lPlane[0] + '.tx', increment * (index + 1) * 2)
        cmds.xform(lDetailCtl[0], r=True, s=(0.2, 0.2, 0.2))
        for att in attTemp:
            cmds.setAttr(lDetailCtl[0] + "." + att, lock=True, keyable=False, channelBox=False)

def connectBrowCtrls_old(self):

    numOfCtl = len(self.ctlList)
    position = [[-1.0+2.0/(numOfCtl-1)*i, 0, 0]for i in range(numOfCtl)]
    tempBrowCrv = cmds.curve(d=1, p=position)
    cmds.rebuildCurve(tempBrowCrv, rebuildType=0, spans=numOfCtl - 3, keepRange=0, degree=3)
    browCrv = cmds.rename(tempBrowCrv, 'brow_crv')
    browCrvShape = cmds.listRelatives(browCrv, c=True)
    cmds.parent(browCrv, self.browCrvGrp)

    browTargets = ["BrowSad", "BrowMad", "Furrow", "Relax", "BrowUp", "BrowDown"]
    crvTargets = []
    for target in browTargets:

        lCrv = cmds.duplicate(browCrv, n='l_{}_crv'.format(target), rc=1)[0]
        rCrv = cmds.duplicate(browCrv, n='r_{}_crv'.format(target), rc=1)[0]
        crvTargets.append(lCrv)
        crvTargets.append(rCrv)

    browBS = cmds.blendShape(crvTargets, browCrv, n='browBS')
    weight = [(x, 1) for x in range(len(browTargets)*2)]
    cmds.blendShape(browBS[0], edit=True, w=weight)

    self.LRBlendShapeWeight(browCrv, browBS[0])

    browCtlCrv = cmds.duplicate(browCrv, n='browCtl_crv', rc=1)[0]
    cmds.blendShape(browBS[0], edit=True, target=[browCrv, len(browTargets)*2, browCtlCrv, 1])
    cmds.setAttr("{}.{}".format(browBS[0], browCtlCrv), 1)

    cvs = cmds.ls("{}.cv[*]".format(browCtlCrv), fl=True)

    # mid brow Ctl and browCtlCrv connection
    for index, ctlGrp in enumerate(self.ctlList):
        ctl = cmds.listRelatives(cmds.listRelatives(ctlGrp, ad=1, type=("nurbsCurve", "mesh"))[0], p=1)[0]
        if ctl.startswith("c_"):
            #cmds.connectAttr('{}.tx'.format(ctl), cvs[index] + '.xValue')
            cmds.connectAttr('{}.ty'.format(ctl), cvs[index] + '.yValue')
            cmds.connectAttr('{}.tz'.format(ctl), cvs[index] + '.zValue')
        elif ctl.startswith("l_"):
            sumTX = cmds.shadingNode('addDoubleLinear', asUtility=True, n=ctl.replace("_ctl", "_sumTX"))
            tranX_val = cmds.getAttr(cvs[index] + '.xValue')
            cmds.connectAttr('{}.tx'.format(ctl), sumTX + '.input1')
            cmds.setAttr(sumTX + '.input2', tranX_val)
            cmds.connectAttr(sumTX + '.output', cvs[index] + '.xValue')
            cmds.connectAttr('{}.ty'.format(ctl), cvs[index] + '.yValue')
            cmds.connectAttr('{}.tz'.format(ctl), cvs[index] + '.zValue')

        elif ctl.startswith("r_"):
            sumTX = cmds.shadingNode('addDoubleLinear', asUtility=True, n=ctl.replace("_ctl", "_sumTX"))
            tranX_val = cmds.getAttr(cvs[index] + '.xValue')
            cmds.setAttr(sumTX + '.input2', tranX_val)

            unitCon = cmds.shadingNode('unitConversion', asUtility=True, n=ctl.replace("_ctl", "_conversion"))
            cmds.connectAttr('{}.tx'.format(ctl), "{}.input".format(unitCon))
            cmds.setAttr( "{}.conversionFactor".format(unitCon), -1)
            cmds.connectAttr("{}.output".format(unitCon), sumTX + '.input1')

            cmds.connectAttr(sumTX + '.output', cvs[index] + '.xValue')
            cmds.connectAttr('{}.ty'.format(ctl), cvs[index] + '.yValue')
            cmds.connectAttr('{}.tz'.format(ctl), cvs[index] + '.zValue')

    # connection from browCrv-POC and detail-ctls to browJnts
    dist = self.boundingBoxData[2]
    increment = 1.0 / (len(self.browJntList) - 1)

    for index, jnt in enumerate(self.browJntList):

        browJntChild = cmds.listRelatives(jnt, ad=1)
        #[u'c_brow00_jnt', u'c_browP00_jnt', u'c_browRY00_jnt']

        shapePOC = cmds.shadingNode('pointOnCurveInfo', asUtility=True, n=browJntChild[0].replace("_jnt", "_shpPoc"))
        cmds.connectAttr(browCrvShape[0] + ".worldSpace", shapePOC + '.inputCurve')
        cmds.setAttr(shapePOC + '.turnOnPercentage', 1)
        cmds.setAttr(shapePOC + '.parameter', increment * index)

        cvList = cmds.ls("{}.cv[*]".format(self.browGuideCrv), fl=1)
        dtailCtl = self.browDetailCtl(self.mirrorJntPrefix[index], cvList[index], dist[1]/120.0, dist[1]/150.0)

        attrs = ["rx", "ry", "v"]
        face_utils.limitAttribute(dtailCtl, attrs)
        #(  c_browMid00_grp, c_browRX00_jnt, [ad=1], browCtlBase, poc )
        self.browCrvCtlToJnt(jnt, browJntChild, dtailCtl, shapePOC)

