import maya.cmds as cmds
import maya.mel as mel
import os
from functools import partial
import xml.etree.ElementTree as ET
import re
from maya import OpenMaya
from twitchScript.face import face_utils
reload(face_utils)

def faceClsMirrorWgt(targetCls, option, direction):

    headGeo = cmds.getAttr("helpPanel_grp.headGeo")
    pairCls = ["eyeWide_cls", "eyeBlink_cls", "squintPuff_cls", "cheek_cls", "lowCheek_cls", "ear_cls"]

    singleCls = ['jawOpen_cls', 'jawClose_cls', 'mouth_cls', 'lip_cls', 'lipRoll_cls', 'browUp_cls', 'browDn_cls',
                 'browTZ_cls', 'nose_cls', 'lipRoll_cls', 'bttmLipRoll_cls', 'jawFat_cls', 'chin_cls']

    if option == "all":
        # pair clusters( blink, cheek...) weight mirror
        for cls in pairCls:
            lCluster = "l_{}".format(cls)
            rCluster = "r_{}".format(cls)
            if cmds.objExists(lCluster) and cmds.objExists(rCluster):
                cmds.copyDeformerWeights(sd=lCluster, ss=headGeo, ds=headGeo, dd=rCluster, mirrorMode="YZ",
                                         surfaceAssociation="closestPoint")

        # single cluster( nose, brow...) weight mirror
        for sCls in singleCls:
            if cmds.objExists(sCls):
                cmds.copyDeformerWeights(sd=sCls, ss=headGeo, ds=headGeo, mirrorMode="YZ",
                                         surfaceAssociation="closestPoint")

    else:
        if targetCls in pairCls:
            print(direction)
            if direction == 1:
                srcCls = "l_{}".format(targetCls)
                destCls = "r_{}".format(targetCls)
                if cmds.objExists(srcCls) and cmds.objExists(destCls):
                    cmds.copyDeformerWeights(sd=srcCls, ss=headGeo, ds=headGeo, dd=destCls, mirrorMode="YZ",
                                             surfaceAssociation="closestPoint")
                print('{} wgt mirrored to {} wgt'.format(srcCls, destCls))
            else:
                srcCls = "r_{}".format(targetCls)
                destCls = "l_{}".format(targetCls)
                if cmds.objExists(srcCls) and cmds.objExists(destCls):
                    cmds.copyDeformerWeights(sd=srcCls, ss=headGeo, ds=headGeo, dd=destCls, mirrorMode="YZ", mi=1,
                                             surfaceAssociation="closestPoint")
                print('{} wgt mirrored to {} wgt'.format(srcCls, destCls))

        else:
            # single cluster( nose, brow...) weight mirror
            if cmds.objExists(targetCls):
                cmds.copyDeformerWeights(sd=targetCls, ss=headGeo, ds=headGeo, mirrorMode="YZ",
                                         surfaceAssociation="closestPoint")


def loftFacePart(factor, facePart, crvList):
    """
    select the curves in order
    Args:
        factor : "brow", "lid", "lip"
        facePart: "brow", "eye", "lip"
        crvList: list of curves for loft

    Returns:

    """
    name = facePart + 'Surf_map01'

    loft_suf = cmds.loft(crvList, n=name, ch=1, uniform=1, close=0, ar=1, d=1, ss=1, rn=1, po=1, rsn=1)[0]
    suf_inputs = cmds.listHistory(loft_suf)
    tessel = [x for x in suf_inputs if cmds.nodeType(x) == 'nurbsTessellate']
    cmds.setAttr(tessel[0] + ".format", 3)
    loftSufShape = cmds.listRelatives(loft_suf, c=1, type="mesh")[0]
    cmds.setAttr("{}.overrideEnabled".format(loftSufShape), 1)
    cmds.setAttr("{}.overrideDisplayType".format(loftSufShape), 1)

    cmds.parent(loft_suf, "surfaceMap_grp")

    face_utils.addAttrStoreData("{}Factor".format(factor), "{}Surf_map".format(facePart), "string", loft_suf, "string")

    return loft_suf

def deformerNodeStateOnOff(geoName, OnOff):
    """
    on / off deformers other than SkinCluster
    Args:
        geoName: geo with deformer
        OnOff: "on", "off"

    Returns:None

    """

    deformList = [nd for nd in cmds.listHistory(geoName) if cmds.nodeType(nd) in ['cluster', 'blendShape', 'ffd', 'wire', 'tweak']]
    if deformList:
        for df in deformList:
            if OnOff == "off":
                # hasNoEffect
                cmds.setAttr(df + '.nodeState', 1)

            elif OnOff == "on":
                # normal
                cmds.setAttr(df + '.nodeState', 0)


def toggleDeformer(geoName):

    if not cmds.objExists(geoName[0]):
        raise RuntimeError("{} doesn't exists".format(geoName[0]))
    deformList = [nd for nd in cmds.listHistory(geoName[0]) if cmds.nodeType(nd) in ['cluster', 'blendShape', 'ffd', 'wire', 'tweak'] ]
    if deformList:
        for df in deformList:
            boolValue = cmds.getAttr(df + '.nodeState')
            if boolValue == 1:
                cmds.setAttr(df + '.nodeState', 0)
                print(df + "   ON!!")
            elif boolValue == 0:
                cmds.setAttr(df + '.nodeState', 1)
                print(df + "  OFF!!")


def getDirectoryPath():

    projectDirectory = cmds.workspace(q=True, rd=True)
    dataPath = cmds.fileDialog2(fileMode=3, caption="set directory", dir=projectDirectory)[0]

    # index = 1
    # while os.path.isdir(dataPath + "/{}{}".format(createDir, str(index).zfill(2))):
    #     index += 1
    # os.makedirs(dataPath + "/{}".format(createDir) + str(index).zfill(2))
    # subDirPath = dataPath + "/{}".format(createDir) + str(index).zfill(2)

    return dataPath

def createVtxSet(selectedCluster):

    vtxSel = cmds.ls(sl=1)
    clsSet = "{}_set".format(selectedCluster)
    if cmds.attributeQuery(clsSet, node="helpPanel_grp", exists=1):
        if cmds.objExists(clsSet):
            cmds.delete(clsSet)
            selectVtxSet = face_utils.createVertexSet(selectedCluster, vtxSel)
        else:
            selectVtxSet = face_utils.createVertexSet(selectedCluster, vtxSel)

    else:
        selectVtxSet = face_utils.createVertexSet(selectedCluster, vtxSel)
        face_utils.addAttrStoreData("helpPanel_grp", "{}_set".format(selectedCluster), "string", selectVtxSet,
                                    "string")

    wideClsDict = {"browUp_cls": "browTZ_cls", "eyeWide_cls": "eyeBlink_cls", "lip_cls": "lipRoll_cls"}
    wideClsList = sorted(wideClsDict.keys())

    if selectedCluster in wideClsList:

        for cls, removeCls in wideClsDict.items():
            print(cls)
            if selectedCluster == cls:
                if not cmds.attributeQuery("{}_set".format(removeCls), node="helpPanel_grp", exists=1):
                    raise RuntimeError("create {}_set first!!".format(removeCls))

                removeSet = cmds.getAttr("helpPanel_grp.{}_set".format(removeCls))
                removeVtxList = cmds.ls(cmds.sets(removeSet, q=1), fl=1)
                selectVtxSet = cmds.sets(removeVtxList, rm=selectVtxSet)

def exportClsWgt(mesh):

    #dataPath = cmds.fileDialog2(fileMode=3, caption="set directory")
    if not cmds.objExists(mesh):
        raise RuntimeError("select geo to with cluster!!")

    dataPath = getDirectoryPath()
    index = 1
    while os.path.isdir(os.path.join(dataPath, "clusterWeight{}".format(str(index).zfill(2)))):
        index += 1

    clsWgtPath = os.path.join(dataPath, "clusterWeight{}".format(str(index).zfill(2)))
    os.makedirs(clsWgtPath)

    size = cmds.polyEvaluate(mesh, v=1)
    clsList = [c for c in cmds.listHistory(mesh) if cmds.nodeType(c) == "cluster"]
    for cls in clsList:
        clsWgt = cmds.getAttr("{}.wl[0].w[0:{}]".format(cls, str(size - 1)))
        if max(clsWgt) > 0:
            cmds.deformerWeights(cls.replace("cls", "wgt") + ".xml", deformer=cls, ex=1, path=clsWgtPath)


def importClsWgt(mesh):

    if not cmds.objExists(mesh):
        raise RuntimeError("select geo to with cluster!!")

    # pathProject = cmds.workspace(  q=True, rd = True )
    projectDirectory = cmds.workspace(q=True, rd=True)
    dataPath = cmds.fileDialog2(fileMode=3, caption="set directory", dir=projectDirectory)

    clsList = [c for c in cmds.listHistory(mesh) if cmds.nodeType(c) == "cluster"]
    for cls in clsList:
        wgt = cls.replace("cls", "wgt")
        if os.path.exists(dataPath[0] + "/" + wgt + ".xml"):
            cmds.deformerWeights(wgt + ".xml", im=1, method="index", deformer=cls, path=dataPath[0])
        else:
            print("%s.xml file doesn't exist" % wgt)


class FaceSkin(face_utils.Util):

    def __init__(self, guideData):

        super(FaceSkin, self).__init__()
        self.guideData = guideData
        self.skinJnts = []
        self.browRYJnt = []
        self.browJnt = []
        self.upBrowWide = []
        self.loBrowWide = []
        self.eyeWideJnt = []
        self.eyeLidJnt = []
        self.eyeBlinkJnt = []
        self.lipJnt = []
        self.lipYJnt = []
        self.helpClsList = []
        self.geo = None
        self.size = None
        self.lipWgt = []
        self.lipRollWgt = []
        self.jawOpenWgt = []
        self.chinWgt = []
        self.browUpWgt = []
        self.browDnWgt = []
        self.browTZWgt = []
        self.eyeWideWgt = []
        self.eyeBlinkWgt = []
        self.jcValStr = None

    def faceClusters(self):

        headGeo = cmds.getAttr("helpPanel_grp.headGeo")
        headBbox = cmds.getAttr("helpPanel_grp.headBBox")
        unit = (headBbox[2] / 20.0)
        # add jawFat_cls, chin_cls (11_16_2023)
        helpCluster = {'rotXPivot': ['browUp_cls', 'browDn_cls'], 'rotYPivot': ['browTZ_cls'],
                       'lEyePos': ['eyeWide_cls', 'eyeBlink_cls'], 'jawRigPos': ['jawOpen_cls', 'jawClose_cls'],
                       'lipYPos': ['lip_cls'], 'lipNPos': ['lipRoll_cls'], 'lipSPos': ['bttmLipRoll_cls']}

        for cls in helpCluster.values():
            self.helpClsList += cls

        self.helpClsList += ["jawFat_jnt", "chin_jnt"]

        face_utils.addAttrStoreData("helpPanel_grp", "helperCluster", "stringArray", self.helpClsList, "stringArray")

        deformCluster = {'squintPuffPos': ['l_squintPuff_cls', 'r_squintPuff_cls'], 'chinPos': ['chin_cls'],
                         'cheekPos': ['l_cheek_cls', 'r_cheek_cls'], 'lipYPos': ['jawFat_cls'],
                         'lowCheekPos': ['l_lowCheek_cls', 'r_lowCheek_cls'], 'lEarPos': ['l_ear_cls', 'r_ear_cls'],
                         'nosePos': ['nose_cls', 'sneer_cls']}

        myCtl = cmds.getAttr("helpPanel_grp.controller")
        if not myCtl:
            # arg = ctlName, position, radius, shape, colorId
            tempCtl = self.genericController("genericCtl", (0, 0, 0), headBbox[2]/50.0, "circle", self.colorIndex["purple"][1])
            myCtl = tempCtl

        cmds.group(em=1, name="clsCtl_grp", parent='arFacePanel')

        if not cmds.objExists("faceCls_panel"):
            raise RuntimeError("import faceCls_panel first!!")

        for loc, clsList in helpCluster.items():

            for cls in clsList:
                self.helperClusterSetup(loc, cls, headGeo, "rotate")

        prefixDict = [1, -1]
        for locator, clusterList in deformCluster.items():

            extraClsDict = {"nosePos": 3, "lipYPos": 4, "chinPos": 4}
            if locator in extraClsDict.keys():

                offsetVal = unit * extraClsDict[locator]
                for index, cluster in enumerate(clusterList):

                    prefixVal = prefixDict[index]
                    clsCtl, clsHandle = self.clusterForSkinWeight(locator, prefixDict[index], offsetVal, cluster, myCtl, headGeo)
                    ctlOffset = cmds.listRelatives(clsCtl, p=1)[0]

                    cmds.connectAttr("{}.t".format(clsCtl), "{}.t".format(clsHandle))
                    cmds.connectAttr("{}.r".format(clsCtl), "{}.r".format(clsHandle))
                    cmds.connectAttr("{}.s".format(clsCtl), "{}.s".format(clsHandle))

                    if cluster == "jawFat_cls":

                        cmds.setAttr("{}.ty".format(ctlOffset), (offsetVal*-1.5))

                    else:
                        cmds.setAttr("{}.ty".format(ctlOffset), (offsetVal/-5.0)*prefixVal)

            else:

                offsetVal = unit
                for index, cluster in enumerate(clusterList):

                    prefixVal = prefixDict[index]
                    if prefixVal == -1:

                        reverseMult = cmds.shadingNode("multiplyDivide", asUtility=1, n=cluster.replace("cls", "mult"))
                        cmds.setAttr("{}.input2".format(reverseMult), -1, -1, -1)
                        clsCtl, clsHandle = self.clusterForSkinWeight(locator, prefixVal, offsetVal, cluster, myCtl,
                                                                      headGeo)
                        cmds.connectAttr("{}.tx".format(clsCtl), "{}.input1X".format(reverseMult))
                        cmds.connectAttr("{}.outputX".format(reverseMult), "{}.tx".format(clsHandle))
                        cmds.connectAttr("{}.ty".format(clsCtl), "{}.ty".format(clsHandle))
                        cmds.connectAttr("{}.tz".format(clsCtl), "{}.tz".format(clsHandle))

                        cmds.connectAttr("{}.rx".format(clsCtl), "{}.rx".format(clsHandle))
                        cmds.connectAttr("{}.ry".format(clsCtl), "{}.input1Y".format(reverseMult)),
                        cmds.connectAttr("{}.outputY".format(reverseMult), "{}.ry".format(clsHandle))
                        cmds.connectAttr("{}.rz".format(clsCtl), "{}.input1Z".format(reverseMult))
                        cmds.connectAttr("{}.outputZ".format(reverseMult), "{}.rz".format(clsHandle))

                        cmds.connectAttr("{}.sx".format(clsCtl), "{}.sx".format(clsHandle))
                        cmds.connectAttr("{}.sy".format(clsCtl), "{}.sy".format(clsHandle))
                        cmds.connectAttr("{}.sz".format(clsCtl), "{}.sz".format(clsHandle))

                    else:
                        clsCtl, clsHandle = self.clusterForSkinWeight(locator, prefixVal, offsetVal, cluster, myCtl, headGeo)
                        cmds.connectAttr("{}.t".format(clsCtl), "{}.t".format(clsHandle))
                        cmds.connectAttr("{}.r".format(clsCtl), "{}.r".format(clsHandle))
                        cmds.connectAttr("{}.s".format(clsCtl), "{}.s".format(clsHandle))

    def clusterForSkinWeight(self, loc, prefixVal, offsetVal, cluster, myCtl, headGeo):
        """

        Args:
            loc: locator
            prefixVal: value for left / right
            offsetVal: ctl offset
            cluster: cluster name
            myCtl : controller created
            headGeo: headGeo name

        Returns:

        """

        locPos = self.guideData[loc]

        position = (locPos[0]*prefixVal, locPos[1], locPos[2])
        ctlP = cmds.group(n=cluster.replace("cls", "ctlP"), em=1, p="clsCtl_grp")
        ctlName = cluster.replace('cls', 'ctl')
        clsCtl = cmds.duplicate(myCtl, rc=1, n=ctlName)[0]
        cmds.parent(clsCtl, ctlP)
        cmds.xform(ctlP, ws=1, t=position)
        offset = face_utils.addOffset(clsCtl, "", "_off")[1]
        cmds.setAttr("{}.tx".format(offset), 0)
        cmds.setAttr("{}.ty".format(offset), 0)
        cmds.setAttr("{}.tz".format(offset), offsetVal)
        cmds.setAttr("{}.sx".format(offset), prefixVal)

        cmds.select(cl=1)
        clsP = cmds.group(n=cluster.replace("cls", "clsP"), em=1, p="faceMain|cls_grp")
        cmds.xform(clsP, ws=1, t=position)
        clsHandle = cmds.group(em=1, p=clsP, name='{}Handle'.format(cluster))
        clsNode = cmds.cluster(headGeo, n=cluster, bindState=1, wn=(clsHandle, clsHandle))
        cmds.select(headGeo, r=1)
        cmds.percent(clsNode[0], v=0.0)

        return [clsCtl, clsHandle]

    def helperClusterSetup(self, loc, clsName, headGeo, attr):

        clsPos = self.guideData[loc]
        ctl = "{}_ctl".format(clsName)

        clsP = cmds.group(n=clsName.replace("cls", "clsP"), em=1, p="faceMain|cls_grp")
        cmds.xform(clsP, ws=1, t=clsPos)
        handle = cmds.group(em=1, p=clsP, name='{}Handle'.format(clsName))
        clsNode = cmds.cluster(headGeo, n=clsName, bindState=1, wn=(handle, handle))

        cmds.select(headGeo, r=1)
        cmds.percent(clsNode[0], v=0.0)

        if attr == "rotate":
            clsMult = cmds.shadingNode("multiplyDivide", asUtility=1, n=clsName.replace("cls", "mult"))
            cmds.connectAttr("{}.t".format(ctl), "{}.input1".format(clsMult))
            cmds.setAttr("{}.input2".format(clsMult), 10, -20, 1)
            cmds.connectAttr("{}.outputX".format(clsMult), "{}.rz".format(handle))
            cmds.connectAttr("{}.outputX".format(clsMult), "{}.ry".format(handle))
            cmds.connectAttr("{}.outputY".format(clsMult), "{}.rx".format(handle))
            cmds.connectAttr("{}.outputZ".format(clsMult), "{}.tz".format(handle))
            cmds.connectAttr("{}.s".format(ctl), "{}.s".format(handle))

        elif attr == "translate":
            cmds.connectAttr("{}.t".format(ctl), "{}.t".format(handle))
            cmds.connectAttr("{}.r".format(ctl), "{}.r".format(handle))
            cmds.connectAttr("{}.s".format(ctl), "{}.s".format(handle))

        return [ctl, handle]

    def surfMapSkinning(self, factor, facePart, orderedJnt):
        """
        skin the map surface start where the first vertex(rCorner vert)
        Returns:

        """

        surfMap = cmds.getAttr("{}Factor.{}Surf_map".format(factor, facePart))
        if not cmds.objExists(surfMap):
            raise RuntimeError("create {} surface map first!!".format(facePart))

        surfMapSkin = mel.eval('findRelatedSkinCluster {}'.format(surfMap))
        if surfMapSkin:
            raise RuntimeError('{} already has SkinCluster'.format(surfMap))

        vtxLen = cmds.polyEvaluate(surfMap, v=1)

        orderJnt = orderedJnt
        jntNum = len(orderJnt)
        skin = ""
        if not vtxLen % jntNum == 0:
            cmds.warning('the number of joints is different to the cvs')
        else:

            crvLen = vtxLen / jntNum
            # how many vertices will be weight for each joint = curve browLength
            vrtPerJnt = crvLen
            skin = self.headSkinObj(surfMap)
            # skinWeight 100% to "headSkel_jnt"
            cmds.skinPercent(skin, surfMap + '.vtx[0:%s]' % (vtxLen - 1), tv=['headSkel_jnt', 1])
            index = 0
            for x in range(0, vtxLen, vrtPerJnt):
                print(crvLen, orderJnt[index])
                cmds.skinPercent(skin, surfMap + '.vtx[%s:%s]' % (x, x + vrtPerJnt - 1), tv=[orderJnt[index], 1])
                index += 1

        return [surfMap, skin]

    def headSkinObj(self, geoName):

        self.headInfluences()

        skin = cmds.skinCluster(geoName, self.skinJnts, tsb=1, nw=1, n='{}_skin'.format(geoName))[0]

        return skin

    def headInfluences(self):
        """
        if there is no wide jnt, the parent joint would be used.
        Returns: all the joints with weight

        """

        browBase = cmds.getAttr("browFactor.browJntList")
        #brow upper part
        self.browRYJnt = cmds.listRelatives(browBase, c=1)
        self.browJnt = cmds.listRelatives(cmds.listRelatives(self.browRYJnt, c=1), c=1)
        # brow lower part
        for jot in self.browRYJnt:
            upJnt = jot.replace("browRY", "up_browWideRY")
            if cmds.objExists(upJnt):
                self.upBrowWide.append(upJnt)

            loJnt = jot.replace("browRY", "lo_browWideRY")
            if cmds.objExists(loJnt):
                self.loBrowWide.append(loJnt)

        wideUp = cmds.getAttr("lidFactor.l_upWideJnt")
        wideLo = cmds.getAttr("lidFactor.l_loWideJnt")
        wideCorner = cmds.getAttr("lidFactor.l_wideCornerJnt")
        self.eyeWideJnt = [wideCorner[0]] + wideUp + [wideCorner[-1]] + wideLo[::-1]
        rEyeWideJnt = [jot.replace("l_", "r_") for jot in self.eyeWideJnt]
        self.eyeLidJnt = [j.replace("idWide_", "idTip_") for j in self.eyeWideJnt]
        rEyeLidJnt = [jnt.replace("l_", "r_") for jnt in self.eyeLidJnt]

        upLipJnt = cmds.getAttr("lipFactor.upLipJnt")
        loLipJnt = cmds.getAttr("lipFactor.loLipJnt")
        cornerLipJnt = cmds.getAttr("lipFactor.cornerLipJnt")
        lipJntBase = [cornerLipJnt[0]] + upLipJnt + [cornerLipJnt[1]] + loLipJnt[::-1]
        self.lipJnt = [y.replace("JawP_", "JawRoll_") + "_jnt" for y in lipJntBase]
        self.lipYJnt = [z.replace("JawP_", "JawY_") + "_jnt" for z in lipJntBase]

        supportJnt = cmds.listRelatives('supportRig', ad=1, type='joint')
        baseJnts = ['jawClose_jnt', 'headSkel_jnt']

        for infList in [self.browRYJnt, self.browJnt, self.upBrowWide, self.loBrowWide, self.eyeWideJnt, self.eyeLidJnt,
                        self.lipJnt, self.lipYJnt, rEyeWideJnt, rEyeLidJnt, supportJnt, baseJnts]:
            if infList:

                self.skinJnts += infList

        face_utils.addAttrStoreData("helpPanel_grp", "skinJnts", "stringArray", self.skinJnts, "stringArray")

    def arFaceHeadSkin(self, geoName, facePart):
        """
        duplicate main headGeo for brow and eye/ and headSkin for skin data
        Args:
            geoName: HeadGeo to duplicate
            facePart: 'brow','eye','lip'

        Returns: None

        """

        # surfMap = cmds.getAttr("{}Factor.{}Surf_map".format(factor, facePart))
        # geoName = cmds.getAttr("helpPanel_grp.headGeo")

        if not cmds.objExists(geoName):
            raise RuntimeError('check head geo name')

        if facePart == "lip":

            deformerNodeStateOnOff(geoName, "off")
            #activate again
            cmds.setAttr('jawOpen_cls.nodeState', 0)
            self.mapHead = geoName

        else:
            self.mapHead = face_utils.copyOrigMesh(geoName, name='{}MapHead'.format(facePart))
            cmds.parent(self.mapHead, "surfaceMap_grp")

        vtxLen = cmds.polyEvaluate(self.mapHead, v=1)

        #facePartHead skinWeight (normalizeWeight???)
        self.skinCls = self.headSkinObj(self.mapHead)
        cmds.skinPercent(self.skinCls, self.mapHead + '.vtx[0:{}]'.format(vtxLen - 1), tv=['headSkel_jnt', 1], normalize=1)

    def copyClusterWgt(self, scCls, ddCls):
        """
        select geo influenced by scCls, ddCls / or it will get the head
        Args:
            scCls: arFaceUI optionMenu 'clusterName'
            ddCls: arFaceUI optionMenu 'targetClusterName'

        Returns: nothing

        """

        myGeo = cmds.ls(sl=1, typ="transform")
        if myGeo:
            self.geo = myGeo[0]
        else:
            self.geo = cmds.getAttr("helpPanel_grp.headGeo")

        self.size = cmds.polyEvaluate(self.geo, v=1)

        if scCls == ddCls:
            raise RuntimeError("select different target cluster")

        else:
            pairCluster = ["squintPuff_cls", "cheek_cls", "lowCheek_cls", "ear_cls"]
            if scCls in pairCluster:
                sdID = face_utils.geoID_cluster(self.geo, "l_{}".format(scCls))
                ddID = face_utils.geoID_cluster(self.geo, "l_{}".format(ddCls))
                valStr = ""
                for i in range(self.size):
                    copyWgt = cmds.getAttr(scCls + ".wl[%s].w[%s]" % (str(sdID), str(i)))
                    valStr += str(copyWgt) + " "

                commandStr = ("setAttr -s " + str(self.size) + " %s.wl[%s].w[0:%s] " % (
                ddCls, str(ddID), str(self.size - 1)) + valStr);
                mel.eval(commandStr)

            else:

                if scCls == "browUp_cls" and ddCls == "browDn_cls":
                    self.assignBrowClsWgt()

                elif scCls == "lipRoll_cls" and ddCls == "bttmLipRoll_cls":
                    self.assginBttmLipRollWgt()

                else:
                    sdID = face_utils.geoID_cluster(self.geo, scCls)
                    ddID = face_utils.geoID_cluster(self.geo, ddCls)
                    valStr = ""
                    for i in range(self.size):
                        copyWgt = cmds.getAttr(scCls + ".wl[%s].w[%s]" % (str(sdID), str(i)))
                        valStr += str(copyWgt) + " "

                    commandStr = ("setAttr -s " + str(self.size) + " %s.wl[%s].w[0:%s] " % (
                    ddCls, str(ddID), str(self.size - 1)) + valStr);
                    mel.eval(commandStr)

    def assignBrowClsWgt(self):

        self.headInfluences()
        if not self.loBrowWide:
            raise RuntimeError("no need for browDn_cls")

        if not cmds.attributeQuery("browDn_cls_set", node="helpPanel_grp", exists=1):
            raise RuntimeError("create browDn_cls set first!!")

        browDnClsSet = cmds.getAttr("helpPanel_grp.browDn_cls_set")
        if not cmds.objExists(browDnClsSet):
            raise RuntimeError("create browDn_cls set first!!")

        self.size = cmds.polyEvaluate(self.geo, v=1)
        browDnSet = cmds.sets(browDnClsSet, q=1)
        browDnVtx = cmds.ls(browDnSet, fl=1)
        browUpWgt = cmds.getAttr("browUp_cls.wl[0].w[0:" + str(self.size - 1) + "]")
        browTZWgt = cmds.getAttr("browTZ_cls.wl[0].w[0:" + str(self.size - 1) + "]")

        for i in range(self.size):
            val = browUpWgt[i] - browTZWgt[i]
            if val < 0:
                cmds.setAttr("browTZ_cls.wl[0].w[%s]" % str(i), browUpWgt[i])
                browTZWgt[i] = browUpWgt[i]

            if "{}.vtx[{}]".format(self.geo, str(i)) in browDnVtx:
                cmds.setAttr("browDn_cls.wl[0].w[%s]" % str(i), (browUpWgt[i] - browTZWgt[i]))

            else:
                cmds.setAttr("browDn_cls.wl[0].w[%s]" % str(i), 0)

        print("brow_cls weight is assigned!!")

    def assginBttmLipRollWgt(self):

        if not cmds.attributeQuery("lipRoll_cls_set", node="helpPanel_grp", exists=1):
            raise RuntimeError("create lipRoll_cls_set first!!")

        loLipVerts = cmds.getAttr("lipFactor.loLipVerts")
        length = len(loLipVerts)
        centerVtx = (length-1)/2
        cmds.select(loLipVerts[centerVtx], r=1)
        for t in range(centerVtx-1):
            mel.eval('PolySelectTraverse 1')

        loLipVtxList = cmds.ls(sl=1, fl=1)
        for vtx in loLipVtxList:
            ID = vtx.split('[')[1][:-1]
            lipRollVal = cmds.getAttr('lipRoll_cls.weightList[0].weights[{}]'.format(ID))
            cmds.setAttr('bttmLipRoll_cls.weightList[0].weights[{}]'.format(ID), lipRollVal)

        cmds.select(loLipVtxList, r=1)
        createVtxSet("bttmLipRoll_cls")

    def copySkinWeight(self, surfMap, mapHead):

        #['lipTip_map', headGeo, 'headSkin']
        if cmds.objExists(surfMap) and cmds.objExists(mapHead):

            cmds.select(surfMap, r=1)

            cmds.select(mapHead, add=1)
            cmds.copySkinWeights(sa='closestPoint', ia='closestJoint', sm=0, normalize=1, noMirror=1)

    def copyTrioSkinWeights(self):
        """
        # export surf map(eye, brow, lip) skinWeight value
        # set up the project first!!
        # jawClose/mouth cluster weight update: calExtraClsWgt()
        # improve: copy all the map surf and export them all
        Args:
            self:

        Returns:

        """
        # set only the jawOpen_cls.ty, 1
        headGeo = cmds.getAttr("helpPanel_grp.headGeo")
        cls = [nd for nd in cmds.listHistory(headGeo) if cmds.nodeType(nd) in ['cluster', 'blendShape', 'ffd']]
        for c in cls:
            # has no effect
            cmds.setAttr(c + '.nodeState', 1)
        cmds.setAttr('jawOpen_cls.nodeState', 0)

        tempHeadMap = {'lip_cls': ['lipTip_map', headGeo, 'headSkin'],
                       'eyeWide_cls': ['eyeTip_map', 'eyeLidMapHead', 'eyeLidMapSkin'],
                       'browDn_cls': ['browMapSurf', 'browMapHead', 'browMapSkin']}

        # copy skinWeight from map_surf to map_head and export skinWeight

        for x, y in tempHeadMap.iteritems():
            if cmds.objExists(y[0]) and cmds.objExists(y[1]):
                self.copySkinWeightInClsVerts(x, y[1], y[0], y[2])
                # cmds.deformerWeights ( y[2]+'.xml', export =1, deformer=y[2], path= trioWgtPath )
                # cmds.skinPercent( y[2], y[1]+'.vtx[0:%s]'%(vertNum-1), tv = ['headSkel_jnt',1] )
            else:
                print('create %s map_surf and map_head!!!' % x)

                # jawOpenCls back to 0
        cmds.setAttr('jawOpen_ctl.t', 0, 0, 0)

        for c in cls:
            cmds.setAttr(c + '.nodeState', 0)

    def exportMapHeadSkinWgt(self, mapSkin):

        #mapSkinPath = createSubDirectory("mapSkinWeight")
        mapSkinPath = getDirectoryPath()
        print(mapSkinPath)
        # index = 1
        # while os.path.isdir(os.path.join(dataPath, "mapSkinWeight{}".format(str(index).zfill(2)))):
        #     index += 1
        #
        # clsWgtPath = os.path.join(dataPath, "mapSkinWeight{}".format(str(index).zfill(2)))
        # os.makedirs(clsWgtPath)
        cmds.deformerWeights(mapSkin + '.xml', export=1, deformer=mapSkin, path=mapSkinPath)

    def copySkinWeightInClsVerts(self, tempSkinHead, clsMapSurf):

        skinCls = mel.eval("findRelatedSkinCluster {}".format(tempSkinHead))

        vertNum = cmds.polyEvaluate(tempSkinHead, v=1)
        vertLen = cmds.polyEvaluate(clsMapSurf, v=1)
        cmds.setAttr(skinCls+'.normalizeWeights', 1)
        cmds.skinPercent(skinCls, tempSkinHead + '.vtx[0:{}]'.format(vertNum-1), tv=['headSkel_jnt', 1], normalize=1)

        cmds.select(clsMapSurf+'.vtx[0:%s]'%(vertLen-1))
        # select target vtx
        cmds.select(tempSkinHead, add=1)
        cmds.copySkinWeights(sa='closestPoint', ia='closestJoint', sm=0, normalize=1, noMirror=1)

    def skinBuild(self, geo, factor, facePart, orderedJnt):

        surfMap, surfSkin = self.surfMapSkinning(factor, facePart, orderedJnt)
        # dupicate headGeo(self.mapHead) and create headSkin
        self.arFaceHeadSkin(geo, facePart=facePart)
        self.copySkinWeight(surfMap, self.mapHead)
        self.exportMapHeadSkinWgt(self.skinCls)

    def updateSurfMap(self, infAddList):
        """
        add extra joint( browWide, cheek, nose, ear ) / add influence to the skin
            infAddList = influence objects list to add
        Returns:

        """

        headGeo = cmds.getAttr("helpPanel_grp.headGeo")
        cls = [nd for nd in cmds.listHistory(headGeo) if cmds.nodeType(nd) in ['cluster', 'blendShape', 'ffd']]
        for c in cls:
            # has no effect
            cmds.setAttr(c + '.nodeState', 1)
        cmds.setAttr('jawOpen_cls.nodeState', 0)

        tempHeadMap = {'lipSurf_map01': [headGeo, 'headSkin'],
                       'eyeSurf_map01': ['eyeMapHead', 'eyeLidMapSkin'],
                       'browSurf_map01': ['browMapHead', 'browMapSkin']}

        cmds.skinCluster(addInfluenc=infAddList)
        self.exportMapHeadSkinWgt(self.skinCls)

    def calExtraClsWgt(self):
        """
        # normalize clusters weight( calculate with the stored weight value : not care of cls position )
        Returns:

        """

        if not self.helpClsList:
            self.helpClsList = cmds.getAttr("helpPanel_grp.helperCluster")

        for cls in self.helpClsList:
            pass
            # if not cmds.objExists(cls):
            #     raise RuntimeError('{} is missing'.format(cls))

        self.geo = cmds.getAttr("helpPanel_grp.headGeo")
        size = cmds.polyEvaluate(self.geo, v=1)
        self.lipWgt = cmds.getAttr("lip_cls.wl[0].w[0:" + str(size - 1) + "]")
        self.lipRollWgt = cmds.getAttr("lipRoll_cls.wl[0].w[0:" + str(size - 1) + "]")
        self.bttmRollWgt = cmds.getAttr("bttmLipRoll_cls.wl[0].w[0:" + str(size - 1) + "]")
        self.jawOpenWgt = cmds.getAttr("jawOpen_cls.wl[0].w[0:" + str(size - 1) + "]")
        self.chinWgt = cmds.getAttr("chin_cls.wl[0].w[0:" + str(size - 1) + "]")
        self.browUpWgt = cmds.getAttr("browUp_cls.wl[0].w[0:" + str(size - 1) + "]")
        self.browDnWgt = cmds.getAttr("browDn_cls.wl[0].w[0:" + str(size - 1) + "]")
        self.browTZWgt = cmds.getAttr("browTZ_cls.wl[0].w[0:" + str(size - 1) + "]")
        self.eyeWideWgt = cmds.getAttr("eyeWide_cls.wl[0].w[0:" + str(size - 1) + "]")
        self.eyeBlinkWgt = cmds.getAttr("eyeBlink_cls.wl[0].w[0:" + str(size - 1) + "]")

        clsWgtList = [self.lipWgt, self.lipRollWgt, self.bttmRollWgt, self.jawOpenWgt, self.chinWgt, self.browUpWgt,
                      self.browDnWgt, self.browTZWgt, self.eyeWideWgt, self.eyeBlinkWgt]

        if max(self.browDnWgt) == 0.0:
            self.assignBrowClsWgt()

        for wgtList in clsWgtList:
            maxWgt = max(wgtList)
            if maxWgt > 1:
                for i, wgt in enumerate(wgtList):
                    if wgt > 1:
                        wgtList[i] = 1

        cleanUp_browOverlap = partial(self.cleanUpBrowEyeOverlap, self.browDnWgt)

        for i in range(size):

            # browUp wgt should be bigger than browTz wgt
            vtxVal = self.browUpWgt[i] - self.browTZWgt[i]
            if vtxVal < 0:
                cmds.setAttr("browTZ_cls.wl[0].w[%s]" % str(i), self.browUpWgt[i])
                self.browTZWgt[i] = self.browUpWgt[i]
                self.browDnWgt[i] = 0

            cleanUp_browOverlap(i)
            '''
            if self.browDnWgt:

                self.browUpWgt[i] -= self.browDnWgt[i]
                totalVal = (self.browTZWgt[i] + self.browDnWgt[i] + self.eyeWideWgt[i])
                if totalVal > 1:

                    self.eyeWideWgt[i] -= (totalVal-1)/2.0
                    self.browDnWgt[i] -= (totalVal-1)/2.0
                    print("fixing index is {} off value {}".format(i, (totalVal-1)/2.0))
                    cmds.setAttr("eyeWide_cls.wl[0].w[%s]" % str(i), self.eyeWideWgt[i])
                    cmds.setAttr("browDn_cls.wl[0].w[%s]" % str(i), self.browDnWgt[i])

                lipOverlap = self.eyeWideWgt[i] + self.browDnWgt[i] + self.lipWgt[i]
                if lipOverlap > 1:
                    self.lipWgt[i] *= 1.0/lipOverlap
                    print("lipWgt overValue is {} : {}".format(i, lipOverlap))'''

            overlapTotl = self.eyeWideWgt[i] + self.browUpWgt[i]
            if overlapTotl > 1:
                print("browDn overlap value over 1 is {} : {}".format(i, overlapTotl))

            eyeVtxVal = self.eyeWideWgt[i] - self.eyeBlinkWgt[i]
            if eyeVtxVal < 0:
                cmds.setAttr("eyeBlink_cls.wl[0].w[%s]" % str(i), self.eyeWideWgt[i])
                self.eyeBlinkWgt[i] = self.eyeWideWgt[i]

            lipRollVtxVal = self.lipRollWgt[i] - self.bttmRollWgt[i]
            if lipRollVtxVal < 0:
                self.lipRollWgt[i] = self.bttmRollWgt[i]

            lipVtxVal = self.lipWgt[i] - self.lipRollWgt[i]
            if lipVtxVal < 0:
                self.lipRollWgt[i] = self.lipWgt[i]

            # to create gradient jawClose map / filter out lip area by multiple (1 - mouth)
            # jaw open * inverse_lipWgt (= inverse black&white image)
            self.jawOpenWgt[i] *= (1 - self.lipWgt[i])

        cmds.setAttr("browUp_cls.wl[0].w[0:{}]".format(str(size - 1)), *self.browUpWgt, s=size)
        cmds.setAttr("browTZ_cls.wl[0].w[0:{}]".format(str(size - 1)), *self.browTZWgt, s=size)
        cmds.setAttr("browDn_cls.wl[0].w[0:{}]".format(str(size - 1)), *self.browDnWgt, s=size)
        cmds.setAttr("lipRoll_cls.wl[0].w[0:{}]".format(str(size - 1)), *self.lipRollWgt, s=size)

        self.jcValStr = ''
        mouthValStr = ''
        for j in range(size):

            tmpVal = self.jawOpenWgt[j]
            self.jcValStr += str(tmpVal) + " "

        # commandStr = ("setAttr -s {} mouth_cls.wl[0].w[0:{}] {}".format(str(size), str(size - 1), mouthValStr));
        # mel.eval(commandStr)

        jcCmmdStr = ("setAttr -s {} jawClose_cls.wl[0].w[0:{}] {}".format(str(size), str(size - 1), self.jcValStr));
        mel.eval(jcCmmdStr)

    #partial command
    def cleanUpBrowEyeOverlap(self, browDnWeight, index):
        """
        fix brow & eyeLid overlap weight value
        Args:
            browDn: if browDnJnt exists
            index: overlap vertex index

        Returns:None

        """

        if browDnWeight:

            # self.browUpWgt[index] -= self.browDnWgt[index]
            #
            # totalVal = (self.browTZWgt[index] + self.browDnWgt[index] + self.eyeWideWgt[index])
            # if totalVal > 1:
            #     self.eyeWideWgt[index] -= (totalVal - 1) / 2.0
            #     self.browDnWgt[index] -= (totalVal - 1) / 2.0
            #     print("fixing index is {} off value {}".format(index, (totalVal - 1) / 2.0))
            #
            # lipOverlap = self.eyeWideWgt[index] + self.browDnWgt[index] + self.lipWgt[index]
            # if lipOverlap > 1:
            #     self.lipWgt[index] *= 1.0 / lipOverlap
            #     print("lipWgt overValue is {} : {}".format(i, lipOverlap))

            totalVal = self.browUpWgt[index] + self.eyeWideWgt[index]
            if totalVal > 1:
                self.eyeWideWgt[index] -= (totalVal - 1) / 2.0
                self.browUpWgt[index] -= (totalVal - 1) / 2.0

                print(index)

            browDnOff = self.browUpWgt[index] - self.browTZWgt[index] - self.browDnWgt[index]
            if browDnOff < 0:
                #print("fixing browDnVtx is {} shaveOff value {}".format(index, browDnOff))
                self.browDnWgt[index] += browDnOff

            lipOverlap = self.eyeWideWgt[index] + self.browUpWgt[index] + self.lipWgt[index]
            if lipOverlap > 1:
                self.lipWgt[index] *= 1.0 / lipOverlap

        else:
            totalVal = self.browUpWgt[index] + self.eyeWideWgt[index]
            if totalVal > 1:
                self.eyeWideWgt[index] -= (totalVal - 1) / 2.0
                self.browUpWgt[index] -= (totalVal - 1) / 2.0
                #print("fixing index is {} takeOut value {}".format(index, (totalVal - 1) / 2.0))

            lipOverlap = self.eyeWideWgt[index] + self.browUpWgt[index] + self.lipWgt[index]
            if lipOverlap > 1:
                self.lipWgt[index] *= 1.0 / lipOverlap

    def faceWeightCalculate(self):

        skinCls = mel.eval("findRelatedSkinCluster %s" % self.geo)
        size = cmds.polyEvaluate(self.geo, v=1)

        upCheekStr = ''
        midCheekStr = ''
        headSkelID = face_utils.getJointIndex(skinCls, 'headSkel_jnt')
        jawCloseID = face_utils.getJointIndex(skinCls, 'jawClose_jnt')

        # set weight back to 1 on the headSkel_jnt
        cmds.skinPercent(skinCls, self.geo + '.vtx[0:%s]' % (size - 1), nrm=1, tv=['headSkel_jnt', 1])
        cmds.setAttr(skinCls + '.normalizeWeights', 0)
        valList = []
        for x in range(size):

            # jawClose_jnt weight
            #tempVal = jawCloseWgt[x] - lipWgt[x]
            '''#take cheek weight inside jawCloseWgt out of cheek weight
            upCheekVal = max( cheekWgt[x]- tempVal, 0)
            upCheekStr +=str(upCheekVal) + " "  
    
            midCheekVal = cheekWgt[x] - upCheekVal
            midCheekStr +=str(midCheekVal) + " "'''

            #jcValStr += str(tempVal) + " "

            tmpVal = 1 - (self.jawOpenWgt[x] + self.lipWgt[x] + self.eyeWideWgt[x] + self.browUpWgt[x])
            valList.append(tmpVal)
            if tmpVal < 0:
                print("total weight over 1 is {} : {}".format(x, tmpVal))

        cmds.setAttr("{}.wl[0:{}].w[{}]".format(skinCls, str(size - 1), headSkelID), *valList, s=size)
        # commandStr = ("setAttr -s " + str(size) + " %s.wl[0:" % skinCls + str(
        #     size - 1) + "].w[" + headSkelID + "] " + valStr);
        # mel.eval(commandStr)

        cmmdStr = ("setAttr -s {} {}.wl[0:{}].w[{}] {}".format(str(size), skinCls, str(size - 1), jawCloseID, self.jcValStr));
        mel.eval(cmmdStr)

        # get the xml file for skinWeight ( brow/ eyeLid / lip )
        projectDirectory = cmds.workspace(q=True, rd=True)
        dataPath = cmds.fileDialog2(fileMode=3, caption="set directory", dir=projectDirectory)

        if os.path.exists(dataPath[0] + '/{}_skin.xml'.format(self.geo)):

            headSkinWeight = ET.parse(dataPath[0] + '/{}_skin.xml'.format(self.geo))
            # represent of list of dictionaries
            rootHeadSkin = headSkinWeight.getroot()

            for index in range(2, len(rootHeadSkin)):
                jntName = rootHeadSkin[index].attrib['source']
                if 'JawRoll' in jntName:
                    lipYJnt = jntName.replace('Roll', 'Y')

                    lipYJntID = face_utils.getJointIndex(skinCls, lipYJnt)
                    print(lipYJnt, lipYJntID)
                    rollJntID = face_utils.getJointIndex(skinCls, jntName)

                    for point in rootHeadSkin[index]:
                        vtxIndex = int(point.attrib['index'])
                        wgtVal = float(point.attrib['value'])

                        cmds.setAttr("{}.wl[{}].w[{}]".format(skinCls, str(vtxIndex), str(rollJntID)),
                                     self.lipRollWgt[vtxIndex] * wgtVal)

                        # if vertNum in lipVertNum:
                        cmds.setAttr("{}.wl[{}].w[{}]".format(skinCls, str(vtxIndex), str(lipYJntID)),
                                     (self.lipWgt[vtxIndex] - self.lipRollWgt[vtxIndex]) * wgtVal)

        else:
            print("%s.xml(lipWeight file) does not exists" % skinCls)

        if os.path.exists(dataPath[0] + '/eyeMapHead_skin.xml'):
            eyeLidSkinWeight = ET.parse(dataPath[0] + '/eyeMapHead_skin.xml')
            rootEyeLidSkin = eyeLidSkinWeight.getroot()

            for c in range(2, len(rootEyeLidSkin) - 2):
                infJnt = rootEyeLidSkin[c].attrib['source']

                if "idTip_" in infJnt:
                    eyeTipJnt = infJnt
                    #blinkJnt = eyeTipJnt.replace("Tip", "Blink")
                    eyeWideJnt = eyeTipJnt.replace("Tip", "Wide")

                    eyeTipJntID = face_utils.getJointIndex(skinCls, eyeTipJnt)
                    wideJntID = face_utils.getJointIndex(skinCls, eyeWideJnt)
                    print("eyeTipJnt and wideJnt ID are {} {}".format(eyeTipJntID, wideJntID))
                    for point in rootEyeLidSkin[c]:
                        vertID = int(point.attrib['index'])
                        weight = float(point.attrib['value'])
                        cmds.setAttr("{}.wl[{}].w[{}]".format(skinCls, str(vertID), str(eyeTipJntID)),
                                     self.eyeBlinkWgt[vertID] * weight)

                        cmds.setAttr("{}.wl[{}].w[{}]".format(skinCls, str(vertID), str(wideJntID)),
                                     (self.eyeWideWgt[vertID] - self.eyeBlinkWgt[vertID]) * weight)
        else:
            print("eyeMapHead_skin.xml(EyeWeight file) does not exists")

        if os.path.exists(dataPath[0] + '/browMapHead_skin.xml'):
            browSkinWeight = ET.parse(dataPath[0] + '/browMapHead_skin.xml')
            rootBrowSkin = browSkinWeight.getroot()

            browJnts = cmds.listRelatives(cmds.ls("*_browP*_jnt", type="joint"), c=1, type="joint")
            for num in range(2, len(rootBrowSkin) - 2):
                browJnt = rootBrowSkin[num].attrib['source']

                if browJnt in browJnts:
                    print(browJnt)
                    rotYJnt = browJnt.replace("brow_", "browRY_")
                    upWideJnt = rotYJnt.replace("browRY", "up_browWideRY")
                    loWideJnt = rotYJnt.replace("browRY", "lo_browWideRY")
                    rotYJntID = face_utils.getJointIndex(skinCls, rotYJnt)
                    childJntID = face_utils.getJointIndex(skinCls, browJnt)
                    loWideID = face_utils.getJointIndex(skinCls, loWideJnt)
                    print('{} ID is {} and weightValue is browDnWgt'.format(loWideJnt, loWideID))
                    if cmds.objExists(upWideJnt):
                        upWideID = face_utils.getJointIndex(skinCls, upWideJnt)

                    for point in rootBrowSkin[num]:
                        vtxIndex = int(point.attrib['index'])
                        wgtValue = float(point.attrib['value'])

                        cmds.setAttr("{}.wl[{}].w[{}]".format(skinCls, str(vtxIndex), str(childJntID)),
                                     self.browTZWgt[vtxIndex] * wgtValue)

                        cmds.setAttr("{}.wl[{}].w[{}]".format(skinCls, str(vtxIndex), str(loWideID)),
                                     self.browDnWgt[vtxIndex] * wgtValue)

                        upWideWgt = (self.browUpWgt[vtxIndex] - self.browTZWgt[vtxIndex] - self.browDnWgt[vtxIndex])

                        if cmds.objExists(upWideJnt):

                            cmds.setAttr("{}.wl[{}].w[{}]".format(skinCls, str(vtxIndex), str(upWideID)),
                                         upWideWgt * wgtValue)

                        else:
                            cmds.setAttr("{}.wl[{}].w[{}]".format(skinCls, str(vtxIndex), str(rotYJntID)),
                                         upWideWgt * wgtValue)
        else:
            print("browMapHead_skin.xml(BrowWeight file) does not exists")

        cmds.setAttr(skinCls + '.normalizeWeights', 1)
        cmds.skinPercent(skinCls, self.geo, nrm=1)
        #mirror weight : normalize 0=none, 1=interactive, 2=post !!not use post normalize/ keep it interactive
        # The Closest point on surface setting the most accurate.
        cmds.copySkinWeights(ss=skinCls, ds=skinCls, mirrorMode='YZ', sa='closestPoint',
                             influenceAssociation='label', ia='oneToOne', normalize=1)

    def calculateBuild(self):

        self.calExtraClsWgt()
        deformerNodeStateOnOff(self.geo, "off")
        self.faceWeightCalculate()


