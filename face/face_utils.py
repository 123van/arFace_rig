#!/bin/env python
###############################################################################
#
#    auto rig  Misc/Util.py
#
#    $HeadURL: $
#    $Revision: $ 1
#    $Author:  $ Sukwon Shin
#    $Date: $ 2016 - 09 - 25
#
import maya.cmds as cmds
import json
import os
import re
import maya.mel as mel
import pymel.core as pm
from maya import OpenMaya
from arFace.Misc import Core
#reload(Core)

import math

def distance(inputA=[1,1,1], inputB=[2,2,2]):
    return math.sqrt(pow(inputB[0]-inputA[0], 2) + pow(inputB[1]-inputA[1], 2) + pow(inputB[2]-inputA[2], 2))

def paramListFromCvDistance(crv):
    """
    create normalized parameters based on the crv cv[*] distance
    Args:
        crv: get cv distance / arcLen of this curve

    Returns: parameter  = cv distance / arcLen(crv)

    """

    crvLength = cmds.arclen(crv)
    crvCvs = cmds.ls("{}.cv[*]".format(crv), fl=1)
    distList = []
    paramList = []
    initPos = cmds.xform(crvCvs[0], q=1, ws=1, t=1)
    for cv in crvCvs:
        cvPos = cmds.xform(cv, q=1, ws=1, t=1)
        dist = distance(initPos, cvPos)
        distList.append(dist)
        initPos = cvPos

    initDist = 0
    for dist in distList:
        dist = initDist + dist
        parm = dist / crvLength
        paramList.append(parm)
        initDist = dist

    return paramList


def trackSelOrder():
    if not cmds.selectPref(q=1, trackSelectionOrder=1):
        cmds.selectPref(trackSelectionOrder=True)


def mirrorVertices(verts):
    headMesh = verts[0].split(".")[0]
    cpmNode = cmds.createNode("closestPointOnMesh", n="closestPointM_node")
    cmds.connectAttr(headMesh + ".outMesh", cpmNode + ".inMesh")
    cmds.connectAttr(headMesh + ".worldMatrix[0]", cpmNode + ".inputMatrix")
    orderedVerts = []
    for v in verts:
        vPos = cmds.xform(v, q=1, ws=1, t=1)
        mirrorVPos = vPos
        mirrorVPos[0] *= -1

        cmds.setAttr(cpmNode + ".inPosition", mirrorVPos[0], mirrorVPos[1], mirrorVPos[2], type="double3")
        vtxIndx = cmds.getAttr(cpmNode + ".closestVertexIndex")
        vtx = "{}.vtx[{}]".format(headMesh, vtxIndx)
        orderedVerts.append(vtx)

    cmds.delete(cpmNode)
    return orderedVerts


def setClosestPointOnMesh(mesh, point):

    CPOMNode = cmds.create("closestPointOnMesh", asUtility=1, n="closestP_mesh01")
    meshShape = cmds.listRelatives(mesh, ni=1, c=1)[0]
    cmds.connectAttr("{}.worldMatrix".format(mesh), "{}.inputMatrix".format(CPOMNode))
    cmds.connectAttr("{}.worldMesh".format(meshShape), "{}.inMesh".format(CPOMNode))
    cmds.setAttr("{}.inPosition".format(CPOMNode), point)

def faceFactorData(facePart, attr, factorList):

    if facePart == "help":
        factorNode = "helpPanel_grp"

    elif facePart == "brow":
        factorNode = "browFactor"

    elif facePart == "lid":
        factorNode = "lidFactor"

    elif facePart == "lip":
        factorNode = "lipFactor"

    if not cmds.objExists(factorNode):
        raise RuntimeError("create face factors first!!")

    if not cmds.attributeQuery(attr, node=factorNode, exists=1):
        cmds.addAttr(factorNode, ln=attr, dt="stringArray")

    cmds.setAttr("{}.{}".format(factorNode, attr), type="stringArray", *([len(factorList)] + factorList))


def addOffset(obj, name =None, suffix='off'):

    if name:
        obj = cmds.rename(obj, name)
    grp_offset = cmds.createNode('transform', n='{}{}'.format(obj, suffix))
    obj_mat = cmds.xform(obj, q=1, t=1, ws=1)
    cmds.xform(grp_offset, t=obj_mat, ws=1)

    obj_parent = cmds.listRelatives(obj, p=1)
    if obj_parent:
        cmds.parent(grp_offset, obj_parent)

    cmds.parent(obj, grp_offset)

    return [obj, grp_offset]

def polyCrvCtlSetup(name, ctl, ctlOffset, offsetVal ):

    cancelingMult = cmds.shadingNode("multiplyDivide", asUtility=True, n="{}Canceling_mult".format(name))
    addDouble = cmds.shadingNode("addDoubleLinear", asUtility=True, n="{}OffVal_add".format(name))
    cmds.connectAttr("{}.t".format(ctl), "{}.input1".format(cancelingMult))
    cmds.setAttr("{}.input2".format(cancelingMult), -1, -1, -1)
    cmds.connectAttr("{}.outputX".format(cancelingMult), "{}.tx".format(ctlOffset))
    cmds.connectAttr("{}.outputY".format(cancelingMult), "{}.ty".format(ctlOffset))
    cmds.connectAttr("{}.outputZ".format(cancelingMult), "{}.input1".format(addDouble))
    cmds.setAttr( "{}.input2".format(addDouble), offsetVal)
    cmds.connectAttr("{}.output".format(addDouble), "{}.tz".format(ctlOffset))

def limitAttribute(ctl, attrs):

    for att in attrs:
        cmds.setAttr("{}.{}".format(ctl, att), lock=1, keyable=0)

def match(destination='', source=''):
    """
    dest = thing to match
    run orient, point constraint to match tr and orientation
    """
    toggleSelect(source, destination)
    orc = cmds.orientConstraint(mo=False, weight=1)
    toggleSelect(source, destination)
    ptc = cmds.pointConstraint(mo=False, weight=1)

    cmds.delete(orc)
    cmds.delete(ptc)


def toggleSelect(r=[], tgl=''):
    """
    toggle select two object
    """
    cmds.select(r, r=True)
    cmds.select(tgl, tgl=True)

def createVertexSet(name, selection):
    """

    Args:
        name: set name
        selection: items in the set

    Returns: set string with selection

    """

    onlyVertices = cmds.filterExpand(selection, sm=31)
    if not onlyVertices:
        raise RuntimeError("select vertices!!")

    wgtSet = '{}Wgt_set'.format(name)
    if cmds.objExists(wgtSet):
        cmds.delete(wgtSet)

    cmds.sets(onlyVertices, n=wgtSet)

    return wgtSet

def clsVertexIndexDict(obj, cls):
    """
    get vertex index ( weight is over 0 )
    Args:
        obj: geo influenced by cls
        cls: cluster with weight

    Returns: vertex index dictionary

    """
    print(cls)
    geometryIndex = geoID_cluster(obj, cls)
    vtxNum = cmds.polyEvaluate(obj, v=1)
    clsVal = cmds.getAttr(cls + '.wl[' + str(geometryIndex) + '].w[0:%s]' % (vtxNum - 1))
    vtxIndexDict = {}
    for x in range(vtxNum):
        val = clsVal[x]
        if val > 0.001:
            vtxIndexDict[x] = val

    return vtxIndexDict


def geoID_cluster(geo, cls):
    """
    to get the geoShapes ID influenced from the cluster
    (Every influenced shapes are stored in clusterSet + ".dagSetMembers[0],[1],[2]...)
    Args:
        geo: selected object
        cls: selected cluster

    Returns: Geo Index for cluster

    """
    clsObj = cmds.cluster(cls, q=1, g=1)
    # get the source geoID for the cluster
    geoID = None
    for i, x in enumerate(clsObj):
        infGeo = cmds.listRelatives(x, p=1)[0]
        if infGeo == geo:
            geoID = i

    if geoID is None:
        cmds.confirmDialog(title='Confirm', message="selected geometry is not in the cluster's objList " )
    else:
        return geoID

def getJointIndex(skinCls, jntName):
    print(jntName)
    connections = cmds.listConnections(jntName + '.worldMatrix[0]', p=1)
    skinJntID = ''
    for cnnt in connections:
        if skinCls == cnnt.split('.')[0]:
            skinJntID = cnnt
    jntID = re.findall('\d+', skinJntID)

    return jntID[-1]

def weightedVerts(obj, cls):

    vtxIndexDict = clsVertexIndexDict(obj, cls)
    print(cls)
    if not vtxIndexDict:
        raise RuntimeError("paint weight on the cluster")

    vtxList = [obj + '.vtx[%s]' % v for v in vtxIndexDict.keys()]

    return vtxList

def resetArFaceCtl():
    allchild = []
    for grp in ['attachCtl_grp', 'clsCtl_grp', 'arFacePanel']:
        if cmds.objExists(grp):
            temp = cmds.listRelatives(grp, ni=1, ad=1)
            allchild += temp
    child = [x for x in allchild if cmds.nodeType(x) in ['nurbsCurve', 'nurbsSurface']]
    transformList = set(cmds.listRelatives(child, p=1))
    ctlList = [ctl for ctl in transformList if "_grp" not in ctl]
    cmds.select(ctlList)

    for y in ctlList:
        attrList = [z for z in cmds.listAttr(y, k=1, locked=0) if "scale" not in z and "visibility" not in z]

        reset = [cmds.setAttr('{}.{}'.format(y, attr), 0) for attr in attrList if
                 not cmds.getAttr('{}.{}'.format(y, attr), l=1)]
        scaleList = [z for z in cmds.listAttr(y, k=1, locked=0) if "scale" in z]
        reset = [cmds.setAttr('{}.{}'.format(y, attr), 1) for attr in scaleList if
                 not cmds.getAttr('{}.{}'.format(y, attr), l=1)]


#work in progress
def addAttrStoreData(node, attr, attrDataType, data, dataType):
    """

    Args:
        node: node Name to add attribute
        attr: attribute name
        attrDataType: float, double, vector, doubleArray, stringArray etc.
        data: data to store
        dataType: should be compatible with attributeType

    Returns:None

    """

    if attrDataType in ["string", "double", "float", "integer"]:
        if not cmds.attributeQuery(attr, node=node, exists=1):
            cmds.addAttr(node, ln=attr, dataType=attrDataType)

        cmds.setAttr("{}.{}".format(node, attr), data, type=dataType)

    if attrDataType == "doubleArray":
        if not cmds.attributeQuery(attr, node=node, exists=1):
            cmds.addAttr(node, ln=attr, dt=attrDataType)

        cmds.setAttr("{}.{}".format(node, attr), data, type=dataType)

    if attrDataType == "stringArray":
        if not cmds.attributeQuery(attr, node=node, exists=1):
            cmds.addAttr(node, ln=attr, dt=attrDataType)

        cmds.setAttr("{}.{}".format(node, attr), *([len(data)]+data), type=dataType)

def lastJntOfChain(jntList):
    chlidJnt = cmds.listRelatives(jntList, ad=1, type="joint")
    childJntGrp = []
    for jt in chlidJnt:
        child = cmds.listRelatives(jt, c=1, type="joint")
        if not child:
            childJntGrp.append(jt)

    return childJntGrp


def create_shrink_wrap(target, wraper, **kwargs):
    """
    Check available kwargs with parameters below.
    """
    parameters = [
        ("projection", 4),
        ("closestIfNoIntersection", 1),
        ("reverse", 0),
        ("bidirectional", 1),
        ("boundingBoxCenter", 1),
        ("axisReference", 1),
        ("alongX", 0),
        ("alongY", 0),
        ("alongZ", 1),
        ("offset", 0),
        ("targetInflation", 0),
        ("targetSmoothLevel", 0),
        ("falloff", 0),
        ("falloffIterations", 1),
        ("shapePreservationEnable", 0),
        ("shapePreservationSteps", 1)
    ]

    wraper_shapes = cmds.listRelatives(wraper, fullPath=True, shapes=True, type="mesh", ni=True)
    if not wraper_shapes:
        raise ValueError("The target supplied is not a mesh")
    target_shape = wraper_shapes[0]

    shrink_wrap = cmds.deformer(target, type="shrinkWrap")[0]

    for parameter, default in parameters:
        cmds.setAttr(
            shrink_wrap + "." + parameter,
            kwargs.get(parameter, default))

    connections = [
        ("worldMesh", "targetGeom"),
        ("continuity", "continuity"),
        ("smoothUVs", "smoothUVs"),
        ("keepBorder", "keepBorder"),
        ("boundaryRule", "boundaryRule"),
        ("keepHardEdge", "keepHardEdge"),
        ("propagateEdgeHardness", "propagateEdgeHardness"),
        ("keepMapBorders", "keepMapBorders")
    ]

    for out_plug, in_plug in connections:
        cmds.connectAttr(
            target_shape + "." + out_plug,
            shrink_wrap + "." + in_plug)

    return shrink_wrap

def polySelectEdgeInOrder(selVerts, openClose="close"):
    """
    get list of edges in order (edge loop or edge part)
    working only for symmetrical edge loop
    Args:
        selVerts: vertices for the first edge of the edgeloop
        openClose: open for brows / close for eye, lip

    Returns: edge list in order

    """
    if not selVerts:
        raise RuntimeError("select vertices")

    if not len(selVerts) == 2:
        raise RuntimeError("select 2 connected vertices")

    firstVert, secondVert = selVerts
    geo = firstVert.split(".")[0]
    cmds.select(firstVert, secondVert, r=1)
    mel.eval('ConvertSelectionToContainedEdges')
    firstEdge = cmds.filterExpand(ex=True, sm=32)[0]
    firstID = re.findall('\d+', firstEdge)[-1]

    if openClose == "open":
        endVerts = mirrorVertices(selVerts)
        endVert, preVert = endVerts
        cmds.select(preVert, endVert, r=1)
        mel.eval('ConvertSelectionToContainedEdges')
        endEdge = cmds.filterExpand(ex=True, sm=32)
        endID = re.findall('\d+', endEdge)[-1]

        IDList = cmds.polySelect(edgeLoopPath=[int(firstID), int(endID)])

    else:
        IDList = cmds.polySelect(edgeLoop=int(firstID))

    edgeList = ["{}.e[{}]".format(geo, ID) for ID in IDList]

    return edgeList

def copyOrigMesh(obj, name):
    """

    Args:
        obj:Geometry whose orig shape to duplicate
        name: new object name

    Returns: copied origMesh

    """
    mainOrig = deleteTrashOrigShape(obj)

    # unique origShape duplicated
    objTemp = cmds.duplicate(mainOrig, n=name, renameChildren=1)[0]
    tempShape = cmds.listRelatives(objTemp, ad=1, type='shape')

    for shp in tempShape:

        if 'Orig' in shp:

            tempOrig = shp

        else:
            cmds.delete(shp)

    cmds.setAttr(tempOrig + ".intermediateObject", 0)
    cmds.sets(tempOrig, e=1, forceElement='initialShadingGroup')

    for att in ['x', 'y', 'z']:
        cmds.setAttr('{}.t{}'.format(objTemp, att), lock=0)

    return objTemp

def deleteTrashOrigShape(objSel):

    shapes = cmds.listRelatives(objSel, ad=1, type='shape')
    origShape = [shp for shp in shapes if cmds.getAttr('{}.intermediateObject'.format(shp)) == 1]

    mainOrig = []
    for orig in origShape:
        if cmds.listConnections(orig, s=0, d=1):
            mainOrig.append(orig)
        else:
            cmds.delete(orig)

    return mainOrig


class Util(Core.Core):
    def __init__(self):
        """
        boundingBoxData = boundingBox , distances
        """
        #super(Util, self).__init__()
        Core.Core.__init__(self)

        self.guideData = {}
        self.boundingBoxData = []
        self.skin = None
        self.colorIndex = {"grey": [2,3], "yellow": [21, 17], "blue": [6, 18], "red": [13, 12], "purple": [30, 31],
                           "green":[27, 26]}
        self.ctlColor = {"darkGrey": 2, "green": 23, "yellow": 22, "orange": 21, "pink": 20, "brightGreen": 19,
                    "skyBlue": 18, "lemon": 17, "white": 16, "wasabi": 14, "red": 13, "darkRed": 12, "purple": 9,
                    "darkGreen": 7, "blue": 6, "appleRed": 4, "black": 1}
    def getSkin(self):
        selection = cmds.ls(sl=1, typ='transform')
        if not selection:
            raise RuntimeError('select something')

        self.skin = mel.eval("findRelatedSkinCluster %s" % selection[0])

        return self.skin

    def getBoundBox(self):
        selection = cmds.ls(sl=1, typ='transform')
        if not selection:
            raise RuntimeError('select headGeo')

        bBox = cmds.exactWorldBoundingBox(selection[0])
        minPoint = [bBox[0],bBox[1],bBox[2]]
        maxPoint = [bBox[3],bBox[4],bBox[5]]
        xLength = abs(maxPoint[0] - minPoint[0])
        yLength = abs(maxPoint[1] - minPoint[1])
        zLength = abs(maxPoint[2] - minPoint[2])
        dist = [xLength, yLength, zLength]
        self.boundingBoxData = [minPoint, maxPoint, dist]


    def createGuidesDict(self):
        """

        Returns: example {u'allPos': [0.0, 50.848, 0.0],
          u'browPos': [0.0, 62.16123070494293, 0.9556314467764292],
          u'cheekPos': [x,y,z],
          u'headSkelPos': [x,y,z],
          u'jawRigPos': [x,y,z],
          u'lEarPos': [x,y,z],
          u'lEyePos': [x,y,z],
          u'lipEPos': [x,y,z],
          u'lipNPos': [x,y,z],
          u'lipSPos': [x,y,z],
          u'lipYPos': [x,y,z],
          u'lipZPos': [x,y,z],
          u'lowCheekPos': [x,y,z],
          u'nosePos': [x,y,z],
          u'rotXPivot': [x,y,z],
          u'rotYPivot': [x,y,z],
          u'squintPuffPos': [x,y,z]}

        """

        if not cmds.objExists("faceLoc_grp"):
            raise RuntimeError("import faceLoc_grp!!")

        if cmds.objExists("allPos"):

            currentGuides = cmds.listRelatives("allPos", ad=1, ni=1, type="transform")

        for guide in currentGuides:

            if guide in ["headSkelPos", "jawRigPos", "lipZPos", "lipYPos", "lipSPos", "lipNPos", "nosePos", "rotXPivot",
                         "rotYPivot", "chinPos"]:
                cmds.setAttr("{}.tx".format(guide), 0)

            guidePos = cmds.xform(guide, q=1, ws=1, t=1)

            self.guideData[guide] = guidePos

    def mirrorOrder_name(self, length, *args):
        """
        unpact the number in range(browLength) into list of number ( right center left )
        Args:
            name: lipJnt/browJnt....
            length:
            *args:

        Returns:

        """
        if int(length) % 2 == 0 or int(length) < 3:
            raise RuntimeError("browLength should be odd number and more than 5!!")

        nameOrder = {}
        center = (length - 1) / 2
        nameOrder[0] = ["r_", "corner"]
        for x in range(center - 1):
            nameOrder[center - x - 1] = ["r_", "{:02d}".format(x + 1)]
        nameOrder[center] = ["c_", "00"]
        for y in range(center):
            nameOrder[center+y+1] = ["l_", "{:02d}".format(y+1)]
        nameOrder[length-1] = ["l_", "corner"]

        # lookup = {}
        # lookup["c_"] = ["{}00".format(self.cPrefix)]
        # lookup["r_corner"] = ["{}corner".format(self.prefix[1])]
        # lookup["l_corner"] = ["{}corner".format(self.prefix[0])]
        # lookup["r_"] = ["{}{:02d}".format(self.prefix[1], (y + 1)) for y in range(center - 1)]
        # lookup["r_"].reverse()
        # lookup["l_"] = ["{}{:02d}".format(self.prefix[0], (x + 1)) for x in range(center - 1)]

        return nameOrder


    @classmethod
    def namingMethod(cls, prefix =None, position = None, title =None, *args):
        """
        breakDown the name and rearrange them
        Args:
            prefix: "l_", "r_", "c_"
            position: "up", "lo"
            title: "Jaw", "Lid", "Brow"
            args: order or suffix or both

        Returns: string like 'l_upJaw_05_grp'
         """

        # args = order or suffix or both
        length = len(args)
        x = "{}"
        bracket = x * 3
        if length:
            for index in range(length):
                bracket += "_{}"
        name = bracket.format(prefix, position, title, *args)

        return name

    def mirrorJoints(self, topJoint='', prefix=['l_', 'r_']):
        """
        mirroring joint, top node needs to contain 'l_' as prefix
        """

        lPrefix = prefix[0]
        rPrefix = prefix[1]

        cmds.select(cl=True)
        cmds.joint(n='temp_jnt')
        cmds.select(topJoint, r=True)
        cmds.select('temp_jnt', tgl=True)
        self.toggleSelect(topJoint, 'temp_jnt')
        cmds.parent()

        cmds.select(topJoint, r=True)
        cmds.mirrorJoint(mirrorYZ=True, mirrorBehavior=True, myz=True, searchReplace=prefix)

        rJoint = rPrefix + topJoint.split(lPrefix)[-1]
        cmds.select(topJoint, rJoint)
        cmds.parent(w=True)

        cmds.delete('temp_jnt')

        return rJoint


    def createPocNode(self, name, crvShape, parameter):
        """
        create Point on Curve node
        """
        pocNode = cmds.shadingNode('pointOnCurveInfo', asUtility=True, n=name)
        cmds.connectAttr(crvShape + '.worldSpace', pocNode + '.inputCurve')
        cmds.setAttr(pocNode + '.turnOnPercentage', 1)
        cmds.setAttr(pocNode + '.parameter', parameter)

        return pocNode


    @classmethod
    def writeJsonFile(cls, jsonFile, data):
        """
        writing json file
        """
        # - create json if not exists
        if not os.path.exists(jsonFile):
            with open(jsonFile, 'a') as outfile:
                json.dump({}, outfile)
            outfile.close()

        with open(jsonFile, 'w+') as outfile:
            json.dump(data, outfile)
        outfile.close()

    @classmethod
    def readJsonFile(cls, jsonFile):
        """
        read json file and return data
        """
        jsonData = json.load(open(jsonFile))

        return jsonData

    @classmethod
    def findSkinCluster(cls, seletion=''):
        """
        finding skin cluster of sl object
        """
        if cmds.objectType(seletion) == 'transform':
            seletion = cmds.listRelatives(seletion)[0]
        sels = cmds.listConnections(seletion)
        for sel in sels:
            if cmds.objectType(sel) == 'skinCluster':
                skinCls = sel
        return skinCls

    @classmethod
    def copyCrvSkinWeight(cls, src, dst):
        """
        copy cv weight from surface to curve
        src = surface
        dst = curve
        """
        srcSkinCls = cls.findSkinCluster(src)
        dstSkinCls = cls.findSkinCluster(dst)
        allJnts = set(cmds.listConnections(srcSkinCls, type='joint'))

        dstCvs = cmds.ls(dst + '.cv[*]', fl=True)
        lenCvs = len(dstCvs)
        for i in range(lenCvs):
            transVal = []
            for jnt in allJnts:
                eachTransVal = (str(jnt), cmds.skinPercent(srcSkinCls, src + '.cv[%s][0]' % i, t=jnt, q=True))
                transVal.append(eachTransVal)

            cmds.skinPercent(dstSkinCls, dstCvs[i], tv=transVal)

    @classmethod
    def regexMatch(cls, expression='', source=[]):
        """
        doing a regex match for list
        return matching element
        """
        result = []
        for ctl in source:
            regex = re.match(expression, ctl)
            if regex:
                result.append(str(regex.group()))
        return result

    # store brow vertices in browFactor( selection order: center to left !! )
    def browOrderedVertices(self):
        """
        get the list of browVertices in order
        """

        trackSelOrder()
        vertSel = cmds.ls(os=1, fl=1)
        if not len(vertSel) == 3:
            raise RuntimeError("'select 3 vertices on edge loop!'")
        vertPosDict = {}
        for vt in vertSel:
            vertPos = cmds.xform(vt, q=1, ws=1, t=1)
            vertPosDict[vt] = vertPos

        vertOrder = sorted(vertPosDict.items(), key=lambda x: x[1][0])  # x[1] = [x,y,x]

        lCornerVert = vertOrder[-1][0]
        vertSel.remove(lCornerVert)

        rCornerVert = vertSel[0]
        secondVert = vertSel[-1]

        selVtx = [rCornerVert, secondVert]
        ordered = Util.orderedVerts_edgeLoop(selVtx)
        startNum = 0
        endNum = 0

        for idx, vtx in enumerate(ordered):
            if vtx == rCornerVert:
                startNum = idx

            elif vtx == lCornerVert:
                endNum = idx
                break

        if not endNum:
            raise RuntimeError("sorry, vertices are not on edge loop. manually select left half vertices!!")

        ordered = ordered[startNum:endNum + 1]

        if not cmds.attributeQuery("browVerts", node="browFactor", exists=1):
            cmds.addAttr("browFactor", ln="browVerts", dt="stringArray")

        cmds.setAttr("browFactor.browVerts", type="stringArray", *([len(ordered)] + ordered))

        return ordered

    def setManualSelection(self, selectedVtx, EyeLipBrow):

        if not selectedVtx:
            raise RuntimeError("manually select left vertices in order")

        orderedVerts = []
        if EyeLipBrow == "brow":
            mirrorVerts = mirrorVertices(selectedVtx)
            orderedVerts = mirrorVerts[1:][::-1] + selectedVtx

            if not cmds.attributeQuery("browVerts", node="browFactor", exists=1):
                cmds.addAttr("browFactor", ln="browVerts", dt="stringArray")

            cmds.setAttr("browFactor.browVerts", type="stringArray", *([len(orderedVerts)] + orderedVerts))

        else:
            self.upLowInput(EyeLipBrow, selectedVtx)

        return orderedVerts

    def upLowInput(self, currentName, selectedVtx):
        """
        for the manual selection
        Args:
            currentName: "lip" or "eye"
            selectedVtx: manually select the vertices

        Returns:WIP

        """

        window = cmds.window()
        form = cmds.formLayout(numberOfDivisions=100)
        b1 = cmds.button(label='upper')
        b2 = cmds.button(label='lower')
        column = cmds.columnLayout(columnWidth=20)
        cmds.text(label="")
        cmds.text(label="      {}".format(currentName))
        cmds.formLayout(form, edit=True,
                        attachForm=[(column, 'top', 5), (column, 'left', 5), (b1, 'top', 5), (b1, 'right', 5),
                                    (b2, 'right', 5), (b2, 'bottom', 5)])

        cmds.showWindow(window)

    @classmethod
    def normalizedCurve(cls, name=None):
        if not name:
            name = 'temporary'
        tmpCrv = pm.curve(d=3, p=([0, 0, 0], [0.25, 0, 0], [0.5, 0, 0], [0.75, 0, 0], [1, 0, 0]))
        pm.rebuildCurve(tmpCrv, rt=0, d=3, kr=0, s=2)
        normCrv = tmpCrv.rename(name + "_normalized_crv")
        return normCrv

    @classmethod
    def create_pointOnCurve(cls, name, curve, pointLength, locator=False):
        """
        create_pointOnCurve(self, name, curve, pointLength, locator = None)
        Args:
            name: curve name
            curve: pymel normalizedCurve(param =1 / cvs = 5)
            pointLength: how many poc nodes you want to create
            locator: for visual purpose
        Returns: list of pointOnCurveInfo nodes

        """
        parameter = 1.0 / (pointLength - 1)
        if isinstance(curve, str):
            curve = pm.PyNode(curve)
        crvShape = curve.getShape()
        pocList = []
        for i in range(pointLength):

            POC_info = pm.shadingNode('pointOnCurveInfo', asUtility=True, n=name + '_poc' + str(i).zfill(2))
            pm.connectAttr(crvShape + ".worldSpace", POC_info + '.inputCurve')
            # setAttr(POC_info + '.turnOnPercentage', 1)
            POC_info.turnOnPercentage.set(1)
            # setAttr(POC_info + '.parameter', parameter*index)
            POC_info.parameter.set(parameter * i)
            if locator:
                LOC = pm.spaceLocator(n=name + "_loc" + str(i).zfill(2))
                pm.connectAttr('{}.result.position'.format(POC_info), '{}.t'.format(LOC))
                LOC.localScale.set(0.2, 0.2, 0.2)

            pocList.append(POC_info)

        return pocList

    @classmethod
    def pocEvenOnCrv(cls, crv, pocNum, title):
        # leng = cmds.arclen( crv )
        increment = 1.0 / (pocNum - 1)
        crvShape = cmds.listRelatives(crv, c=1, ni=1, s=1)
        pocs = []
        for n in range(pocNum):
            guidePoc = cmds.shadingNode('pointOnCurveInfo', asUtility=True, n=title + str(n).zfill(2) + '_poc')
            cmds.connectAttr(crvShape[0] + ".worldSpace", guidePoc + ".inputCurve")
            cmds.setAttr(guidePoc + ".turnOnPercentage", 1)
            cmds.setAttr(guidePoc + ".parameter", increment * n)
            pocs.append(guidePoc)
        return pocs



    @classmethod
    def matrixParentConstraint(cls, prnt, child_list):
        """
        object local matrix = object world matrix * parent inverse matrix using multMatrix : object in parent space
        object world matrix = object local matrix * parent world matrix using multMatrix
        Args:
            prnt:
            child_list:

        Returns:

        """
        if not type(child_list) == list:
            child_list = [child_list]

        name_split = prnt.split('_')
        name = name_split[0] + '_' + name_split[1]
        for child in child_list:

            offset_matrix = cmds.createNode('multMatrix', n=name + "_off_matrix")
            mult_matrix = cmds.createNode('multMatrix', n=name + "_mult_matrix")
            decompose_matrix = cmds.createNode('decomposeMatrix', n=name + "_decompose")

            #object localMatrix = object WorldMatrix * Parent InverseMatrix
            #object worldMatrix = Parent WorldMatrix * object localMatrix
            cmds.connectAttr(child + '.worldMatrix', offset_matrix + '.matrixIn[0]')
            cmds.connectAttr(prnt + '.worldInverseMatrix', offset_matrix + '.matrixIn[1]')

            loca_mat = cmds.getAttr(offset_matrix + '.matrixSum')
            cmds.setAttr(mult_matrix + '.matrixIn[0]', loca_mat, type="matrix")
            #cmds.connectAttr(offset_matrix + '.matrixSum', helpNode + '.offsetMat_attr')
            #cmds.connectAttr(helpNode + '.offsetMat_attr', mult_matrix + '.matrixIn[0]')
            cmds.connectAttr(prnt + '.worldMatrix', mult_matrix + '.matrixIn[1]')

            child_prnt = cmds.listRelatives(child, p=1)
            if child_prnt:
                cmds.connectAttr(child_prnt[0] + '.worldInverseMatrix', mult_matrix + '.matrixIn[2]')

            #disconnect to prevent any cycle
            #cmds.disconnectAttr(offset_matrix + '.matrixSum', helpNode + '.offsetMat_attr')
            # mult_matrix to decompose_matrix
            cmds.connectAttr(mult_matrix + '.matrixSum', decompose_matrix + '.inputMatrix')

            # connect child transform. t.r.s
            cmds.connectAttr(decompose_matrix + '.outputTranslate', child + '.translate')
            cmds.connectAttr(decompose_matrix + '.outputRotate', child + '.rotate')
            #cmds.connectAttr(decompose_matrix + '.outputScale', child + '.scale')

            # clean up
            cmds.delete(offset_matrix)

    @classmethod
    def matrixMultParentConstraint(cls, prnt_list, child):
        """
        child local matrix = child world matrix * inverse parent matrix
        child world matrix = child local matrix * parent world matrix
        Args:
            prnt_list: list of parent
            child: a child follows parents

        Returns:

        """
        if not type(prnt_list) == list:
            prnt_list = [prnt_list]

        wtAddMatrix = cmds.createNode('wtAddMatrix', n=child + "_wtAddMatrix")
        paramDriver = cmds.shadingNode("lightInfo", asUtility=True, name="{}_ratio".format(child))

        for i, prnt in enumerate(prnt_list):

            offset_matrix = cmds.createNode('multMatrix', n=child + "_off_matrix")
            mult_matrix = cmds.createNode('multMatrix', n=child + "_mult_matrix")
            decompose_matrix = cmds.createNode('decomposeMatrix', n=child + "_decompose")

            #get child's offset matrix from parent space (= maintain offset)
            cmds.connectAttr(child + '.worldMatrix', offset_matrix + '.matrixIn[0]')
            cmds.connectAttr(prnt + '.worldInverseMatrix', offset_matrix + '.matrixIn[1]')

            local_mat = cmds.getAttr(offset_matrix + '.matrixSum')
            cmds.setAttr(mult_matrix + '.matrixIn[0]', local_mat, type="matrix")

            # child worldMatrix = parent worldMatrix * child offset Matrix
            cmds.connectAttr(prnt + '.worldMatrix', mult_matrix + '.matrixIn[1]')

            child_prnt = cmds.listRelatives(child, p=1)
            if child_prnt:
                cmds.connectAttr(child_prnt[0] + '.worldInverseMatrix', mult_matrix + '.matrixIn[2]')

            #disconnect to prevent any cycle
            # clean up
            #cmds.delete(offset_matrix)

            cmds.connectAttr(mult_matrix + '.matrixSum', wtAddMatrix + '.wtMatrix[%s].matrixIn' % str(i))

            ratio = 1.0/float(len(prnt_list))

            # connect paramDriver to addMatirx weight
            cmds.addAttr(paramDriver, ln="{}W{:01d}".format(prnt, i), at="double", min=0, max=1, dv=ratio)
            cmds.connectAttr("{}.{}W{:01d}".format(paramDriver, prnt, i), (wtAddMatrix + '.wtMatrix[%s].weightIn' % str(i)))

        # wtAddMatrix to decompose_matrix
        cmds.connectAttr(wtAddMatrix + '.matrixSum', decompose_matrix + '.inputMatrix')

        # connect child transform. t.r.s
        cmds.connectAttr(decompose_matrix + '.outputTranslate', child + '.translate')
        cmds.connectAttr(decompose_matrix + '.outputRotate', child + '.rotate')

        return paramDriver


    # select corner verts and directional vertex
    @classmethod
    def orderedVert_upLo(cls, lipEye):
        """
        select corner vertices and directional vertex
        script should work as long as the last selection be directional vertex
        Args:
            lipEye: "eye" , "lip"

        Returns:

        """
        orderSel = cmds.selectPref(trackSelectionOrder=True, q=1)
        if not orderSel:
            cmds.confirmDialog(title='Confirm', message='turn on "trackSelectionOrder" in Pref!!!')

        vertSel = cmds.ls(os=1, fl=1)
        if not len(vertSel) == 3:
            raise RuntimeError("'select 3 vertices on edge loop!'")

        vertPosDict = {}
        for vt in vertSel:
            vertPos = cmds.xform(vt, q=1, ws=1, t=1)
            vertPosDict[vt] = vertPos

            # returns list[ ("vert1",[x,y,z]), ("vert2",[x,y,z]), ("vert3",[x,y,z])....]
        vertOrder = sorted(vertPosDict.items(), key=lambda x: x[1][0])  # x[1] = [x,y,x]
        lCornerVert = vertOrder[-1][0]
        vertSel.remove(lCornerVert)

        rCornerVert = vertSel[0]
        secondVert = vertSel[-1]

        selVtx = [rCornerVert, secondVert]
        # get ordered verts on the edgeLoop
        ordered = Util.orderedVerts_edgeLoop(selVtx)

        # get up/lo verts
        endNum = 0
        for v, y in enumerate(ordered):
            # find lCornerVert in the upper lid Vertice
            if y == lCornerVert:
                endNum = v

        if endNum == 0:
            raise RuntimeError(" 3 vertices are not on the edge loop")

        upVert = ordered[:endNum + 1]
        loVert = [rCornerVert] + ordered[endNum:][::-1]

        if lipEye == 'eye':
            rCornerVerts = mirrorVertices([rCornerVert, lCornerVert])
            rUpVert = mirrorVertices(upVert)
            rLoVert = mirrorVertices(loVert)
            if not cmds.attributeQuery("l_cornerVerts", node="lidFactor", exists=1):
                cmds.addAttr("lidFactor", ln="l_cornerVerts", dt="stringArray")
            if not cmds.attributeQuery("r_cornerVerts", node="lidFactor", exists=1):
                cmds.addAttr("lidFactor", ln="r_cornerVerts", dt="stringArray")

            if not cmds.attributeQuery("l_upLidVerts", node="lidFactor", exists=1):
                cmds.addAttr("lidFactor", ln="l_upLidVerts", dt="stringArray")
            if not cmds.attributeQuery("r_upLidVerts", node="lidFactor", exists=1):
                cmds.addAttr("lidFactor", ln="r_upLidVerts", dt="stringArray")

            if not cmds.attributeQuery("l_loLidVerts", node="lidFactor", exists=1):
                cmds.addAttr("lidFactor", ln="l_loLidVerts", dt="stringArray")
            if not cmds.attributeQuery("r_loLidVerts", node="lidFactor", exists=1):
                cmds.addAttr("lidFactor", ln="r_loLidVerts", dt="stringArray")

            cmds.setAttr("lidFactor.l_cornerVerts", 2, rCornerVert, lCornerVert, type="stringArray")
            cmds.setAttr("lidFactor.r_cornerVerts", 2, rCornerVerts[0], rCornerVerts[1], type="stringArray")

            cmds.setAttr("lidFactor.l_upLidVerts", type="stringArray", *([len(upVert)] + upVert))
            cmds.setAttr("lidFactor.r_upLidVerts", type="stringArray", *([len(rUpVert)] + rUpVert))

            cmds.setAttr("lidFactor.l_loLidVerts", type="stringArray", *([len(loVert)] + loVert))
            cmds.setAttr("lidFactor.r_loLidVerts", type="stringArray", *([len(rLoVert)] + rLoVert))

        elif lipEye == 'lip':
            if not cmds.attributeQuery("upLipVerts", node="lipFactor", exists=1):
                cmds.addAttr("lipFactor", ln="upLipVerts", dt="stringArray")
            if not cmds.attributeQuery("loLipVerts", node="lipFactor", exists=1):
                cmds.addAttr("lipFactor", ln="loLipVerts", dt="stringArray")

            cmds.setAttr("lipFactor.upLipVerts", type="stringArray", *([len(upVert)] + upVert))
            cmds.setAttr("lipFactor.loLipVerts", type="stringArray", *([len(loVert)] + loVert))

        return [upVert, loVert]


    @classmethod
    def orderedVerts_edgeLoop(cls, selVtx=[]):
        """
        select 2 vertices for a edge loop /select 3 vertices for a edge part
        Returns: vertex list on edgeLoop

        """
        if not len(selVtx) in [2, 3]:
            raise RuntimeError("select 2 or 3 vertices")

        firstVert = selVtx[0]
        secondVert = selVtx[1]
        endVert = None
        if len(selVtx) == 3:
            endVert = selVtx[2]

        cmds.select(firstVert, secondVert, r=1)
        mel.eval('ConvertSelectionToContainedEdges')
        firstEdge = cmds.ls(sl=1)[0]
        cmds.polySelectSp(firstEdge, loop=1)
        edges = cmds.ls(sl=1, fl=1)
        edgeDict = Util.edgeVertDict(edges)  # {edge: [vert1, vert2], ...}
        ordered = [firstVert, secondVert]
        del edgeDict[firstEdge]

        for i in range(len(edges) - 2):

            for edge, vtxList in edgeDict.iteritems():
                if secondVert in vtxList:
                    vtxList.remove(secondVert)
                    del edgeDict[edge]
                    break
            secondVert = vtxList[0]
            ordered.append(secondVert)
            if endVert:
                if secondVert == endVert:
                    break

        return ordered


    # make the list of edgeLoop dictionary( { edge: [vert1, vert2]})
    @classmethod
    def edgeVertDict(cls, edgeList):
        edgeVertDict = {}
        for edge in edgeList:
            cmds.select(edge, r=1)
            cmds.ConvertSelectionToVertices()
            edgeVert = cmds.ls(sl=1, fl=1)
            edgeVertDict[edge] = edgeVert

        return edgeVertDict


    @classmethod
    def mirrorVertice(cls, verts):
        headMesh = verts[0].split(".")[0]
        cpmNode = cmds.createNode("closestPointOnMesh", n="closestPointM_node")
        cmds.connectAttr(headMesh + ".outMesh", cpmNode + ".inMesh")
        cmds.connectAttr(headMesh + ".worldMatrix[0]", cpmNode + ".inputMatrix")
        orderedVerts = []
        for v in verts:
            vPos = cmds.xform(v, q=1, ws=1, t=1)
            mirrorVPos = vPos
            mirrorVPos[0] *= -1

            cmds.setAttr(cpmNode + ".inPosition", mirrorVPos[0], mirrorVPos[1], mirrorVPos[2], type="double3")
            vtxIndx = cmds.getAttr(cpmNode + ".closestVertexIndex")
            vtx = "{0}.vtx[{1}]".format(headMesh, vtxIndx)
            orderedVerts.append(vtx)

        return orderedVerts

    @classmethod
    def createPolyToCurve(cls, orderedVerts, name=None, **kwargs):
        """
        if first and the last vertex is same, it will close it
        vertices no need to be on the edge loop (manually select continuous vertices)
        Args:
            orderedVerts: vertices on edgeLoop in order
            name: browGuide_crv
            kwargs: direction: 1 or -1 (+ or - direction)
        Returns: polyEdgeToCurve degree 1

        """
        # create guide curve based on lipFactor orderedVertices
        edges = []
        numVtx = len(orderedVerts)
        for idx in range(numVtx - 1):
            cmds.select(orderedVerts[idx], orderedVerts[idx + 1], r=1)
            mel.eval('ConvertSelectionToContainedEdges')
            edge = cmds.filterExpand(ex=True, sm=32)
            if edge:
                edges.append(edge)

        cmds.select(cl=1)

        for e in edges:
            cmds.select(e, add=1)
        #form = 2 : best guess ( whether open or close )
        polyCrv = cmds.polyToCurve(form=2, degree=1, n="{}_crv".format(name))[0]

        polyCrvShp = cmds.listRelatives(polyCrv, c=1, type="nurbsCurve")[0]

        form = cmds.getAttr("{}.f".format(polyCrvShp))
        numVtx = len(cmds.ls(polyCrv + ".cv[*]", fl=1))
        cvStart = cmds.xform(polyCrv + ".cv[0]", q=1, ws=1, t=1)
        cvEnd = cmds.xform(polyCrv + ".cv[%s]" % str(numVtx - 1), q=1, ws=1, t=1)
        if not kwargs:
            if form == 0:
                if cvStart[0] > cvEnd[0]:
                    cmds.reverseCurve(polyCrv, ch=1, rpo=1)
        else:

            if kwargs["direction"] == 1:
                if form == 0:
                    if cvStart[0] > cvEnd[0]:
                        cmds.reverseCurve( polyCrv, ch= 1, rpo=1 )

            elif kwargs["direction"] == -1:
                if form == 0:
                    if cvStart[0] < cvEnd[0]:
                        cmds.reverseCurve(polyCrv, ch=1, rpo=1)

        return polyCrv

    @classmethod
    def checkEdgeLoopWithSelectedVtx(cls, orderedVtx):
        """
        check if the selected vertices are on the edgeLoop
        Args:
            orderedVtx: vertices on edgeLoop in order

        Returns:True or False

        """

        vtxLength =len(orderedVtx)
        edges = []
        for index in range(vtxLength - 1):
            cmds.select(orderedVtx[index], orderedVtx[index + 1])
            mel.eval('ConvertSelectionToContainedEdges')
            edge = cmds.filterExpand(ex=True, sm=32)
            if edge:
                edges.append(edge)

        if len(edges) == (len(orderedVtx) - 1):
            return True
        else:
            return False

    @classmethod
    def genericController(cls, ctlName, position, radius, shape, colorId):

        if shape in ["cc", "circle"]:
            degree = 3  # cubic
            section = 8  # smooth circle

        elif shape in ["sq", "square"]:
            degree = 1  # linear
            section = 4  # straight line

        else:
            print('shape = either "cc"(circle) or "sq"(square)')

        # if none of c_, l_, r_
        circleCtrl = cmds.circle(n= ctlName, ch=False, nr=(0, 0, 1), c=(0, 0, 0), sw=360, r=radius, d=degree, s=section)
        cmds.setAttr(circleCtrl[0] + ".overrideEnabled", 1)
        cmds.setAttr(circleCtrl[0] + ".overrideShading", 0)
        cmds.setAttr(circleCtrl[0] + ".overrideColor", colorId)

        cmds.xform(circleCtrl[0], ws=True, t=position)
        ctrl = circleCtrl[0]
        return ctrl

    def createMidController(self, name, offValue, myCtl, param, guideCrv, colorID):

        """
        create POC node on guideCurve and get the myCtl attached
        Args:
            name: for poc and controller
            offValue : offset value
            myCtl: controller with unique name
            param:
            guideCrv:
            colorID:
        Returns: list [ctl, offset, offset's Null, pointOnCurveInfo]

        """
        null = cmds.group(em=1, n=name.replace("_ctl", "_grp"))
        tmpCtl = cmds.duplicate(myCtl, rc=1)[0]
        newCtl = cmds.rename(tmpCtl, name)
        print(tmpCtl, newCtl)
        ctl, offset = addOffset(newCtl, name, "_off")

        ctlShape = cmds.listRelatives(ctl, c=1)[0]
        cmds.setAttr("{}.overrideEnabled".format(ctlShape), 1)

        cmds.setAttr("{}.overrideColor".format(ctlShape), colorID)

        cmds.parent(offset, null)
        cmds.setAttr("{}.t".format(offset), 0, 0, offValue)

        crvShape = cmds.listRelatives(guideCrv, c=1)[0]
        pointOnCrv = self.createPocNode("{}_poc".format(name), crvShape, param)
        cmds.connectAttr(pointOnCrv + ".position", null + ".t")

        return [ctl, offset, null, pointOnCrv]


    @classmethod
    def symmetrizeLipCrv(cls, crvSel, direction):

        if not crvSel:
            raise RuntimeError('select a curve!!')

        crvShp = cmds.listRelatives(crvSel[0], c=1, ni=1, s=1)[0]

        if not len(cmds.ls(crvShp)) == 1:
            raise RuntimeError('more than 1 "%s" matches name!!' % crvShp[0])

        periodic = cmds.getAttr(crvShp[0] + '.form')
        crvCvs = cmds.ls(crvSel[0] + ".cv[*]", l=1, fl=1)
        numOfCvs = len(crvCvs)

        numList = [x for x in range(numOfCvs)]
        if periodic in [1, 2]:
            if numOfCvs % 2 == 0:
                halfLen = (numOfCvs - 2) / 2
                centerCV = []
                for cv in crvCvs:
                    pos = cmds.xform(cv, q=1, ws=1, t=1)
                    if pos[0] ** 2 < 0.0001:
                        print (cv)
                        num = cv.split('[')[1][:-1]
                        centerCV.append(int(num))

                if len(centerCV) == 2:
                    startNum = centerCV[0] + 1
                    endNum = startNum + halfLen
                    halfNum = numList[startNum:endNum]
                    opphalf = numList[endNum + 1:] + numList[:centerCV[0]]
                    # curve direction( --> )
                    if cmds.xform(crvCvs[startNum], q=1, ws=1, t=1)[0] > 0:
                        leftNum = halfNum
                        rightNum = opphalf[::-1]
                    # curve direction( <-- )
                    elif cmds.xform(crvCvs[startNum], q=1, ws=1, t=1)[0] < 0:
                        leftNum = opphalf
                        rightNum = halfNum[::-1]

                    print(leftNum, rightNum)
                    if direction:
                        print("left cv to right cv")
                        for i in range(halfLen):
                            pos = cmds.xform(crvCvs[leftNum[i]], q=1, ws=1, t=1)
                            cmds.xform(crvCvs[rightNum[i]], ws=1, t=(-pos[0], pos[1], pos[2]))

                    else:
                        print("right cv to left cv")
                        for i in range(halfLen):
                            pos = cmds.xform(crvCvs[rightNum[i]], q=1, ws=1, t=1)
                            cmds.xform(crvCvs[leftNum[i]], ws=1, t=(-pos[0], pos[1], pos[2]))
                else:
                    cmds.confirmDialog(title='Confirm',
                                       message='number of CVs( tx=0 :on center ) of curve should be 2!!!')

        if periodic == 0:
            if numOfCvs % 2 == 1:
                halfLen = (numOfCvs - 2) / 2
                centerNum = ''
                for cv in crvCvs:
                    pos = cmds.xform(cv, q=1, ws=1, t=1)
                    if pos[0] ** 2 < 0.0001:
                        num = cv.split('[')[1][:-1]
                        centerNum = int(num)

                if centerNum:
                    halfNum = numList[centerNum + 1:]
                    opphalf = numList[:centerNum]
                    # curve direction( --> )
                    if cmds.xform(crvCvs[centerNum + 1], q=1, ws=1, t=1)[0] > 0:
                        leftNum = halfNum
                        rightNum = opphalf[::-1]
                    # curve direction( <-- )
                    elif cmds.xform(crvCvs[centerNum + 1], q=1, ws=1, t=1)[0] < 0:
                        leftNum = opphalf
                        rightNum = halfNum[::-1]

                    if direction == 1:
                        print
                        "left cv to right cv"
                        for i in range(halfLen):
                            pos = cmds.xform(crvCvs[leftNum[i]], q=1, ws=1, t=1)
                            cmds.xform(crvCvs[rightNum[i]], ws=1, t=(-pos[0], pos[1], pos[2]))

                    else:
                        print
                        "right cv to left cv"
                        for i in range(halfLen):
                            pos = cmds.xform(crvCvs[rightNum[i]], q=1, ws=1, t=1)
                            cmds.xform(crvCvs[leftNum[i]], ws=1, t=(-pos[0], pos[1], pos[2]))

                else:
                    cmds.confirmDialog(title='Confirm', message='position the curve tx on center!!!')


    @classmethod
    def getUParam(cls, pntPos=[], crv=None):
        """
        get the parameter of curve on the selected point
        Args:
            crv: curve must be at the origin(0,0,0)

        Returns:

        """
        point = OpenMaya.MPoint(pntPos[0], pntPos[1], pntPos[2])
        curveFn = OpenMaya.MFnNurbsCurve(Util.getDagPath(crv))
        paramUtill = OpenMaya.MScriptUtil()
        paramPtr = paramUtill.asDoublePtr()
        isOnCurve = curveFn.isPointOnCurve(point)
        if isOnCurve:
            curveFn.getParamAtPoint(point, paramPtr, 0.001, OpenMaya.MSpace.kObject)
        else:
            point = curveFn.closestPoint(point, paramPtr, 0.001, OpenMaya.MSpace.kObject)
            curveFn.getParamAtPoint(point, paramPtr, 0.001, OpenMaya.MSpace.kObject)

        param = paramUtill.getDouble(paramPtr)
        return param

    @classmethod
    def getDagPath(cls, objectName):
        '''
        This function let you get an MObject from a string representing the object name
        @param[in] objectName : string , the name of the object you want to work on
        '''
        if isinstance(objectName, list):
            oNodeList = []
            for o in objectName:
                selectionList = OpenMaya.MSelectionList()
                selectionList.add(o)
                oNode = OpenMaya.MObject()
                selectionList.getDagPath(0, oNode)
                oNodeList.append(oNode)
            return oNodeList
        else:
            selectionList = OpenMaya.MSelectionList()
            print(selectionList, objectName)
            selectionList.add(objectName)
            oNode = OpenMaya.MDagPath()
            selectionList.getDagPath(0, oNode)
            return oNode

    def arcController(self, ctlName=None, position=[], radius = None, ctlShape="cc"):
        if ctlShape == "cc":

            ctrl = cmds.circle(ch=False, nr=(0, 0, 1), c=(0, 0, 0), sw=360, r=radius, d=3, s=8)[0]

        elif ctlShape == "sq":

            ctrl = cmds.circle(ch=False, nr=(0, 0, 1), c=(0, 0, 0), sw=360, r=radius, d=1, s=4)[0]

        if ctlName[:2] == "c_":
            # if center, color override is yellow
            arCtrl = cmds.rename(ctrl, ctlName)
            cmds.setAttr(arCtrl + ".overrideEnabled", 1)
            cmds.setAttr(arCtrl + ".overrideShading", 0)
            cmds.setAttr(arCtrl + ".overrideColor", self.colorIndex["purple"][1])
            null = cmds.group(arCtrl, w=True, n=arCtrl + "Off")
            cmds.xform(null, ws=True, t=position)

        elif ctlName[:2] == "l_":
            # if left, color override is blue
            arCtrl = cmds.rename(ctrl, ctlName)
            cmds.setAttr(arCtrl + ".overrideEnabled", 1)
            cmds.setAttr(arCtrl + ".overrideShading", 0)
            cmds.setAttr(arCtrl + ".overrideColor", self.colorIndex["blue"][0])
            null = cmds.group(arCtrl, w=True, n=arCtrl + "Off")
            cmds.xform(null, ws=True, t=position)

        elif ctlName[:2] == "r_":
            # if right, color override is red
            arCtrl = cmds.rename(ctrl, ctlName)
            cmds.setAttr(arCtrl + ".overrideEnabled", 1)
            cmds.setAttr(arCtrl + ".overrideShading", 0)
            cmds.setAttr(arCtrl + ".overrideColor", self.colorIndex["red"][1])
            null = cmds.group(arCtrl, w=True, n=arCtrl + "Off")
            cmds.xform(null, ws=True, t=position)

        else:
            # if none of c_, l_, r_
            arCtrl = cmds.rename(ctrl, ctlName)
            cmds.setAttr(arCtrl + ".overrideEnabled", 1)
            cmds.setAttr(arCtrl + ".overrideShading", 0)
            cmds.setAttr(arCtrl + ".overrideColor", self.colorIndex["yellow"][1])
            null = cmds.group(arCtrl, w=True, n=arCtrl + "Off")
            cmds.xform(null, ws=True, t=position)

        ctrl = [arCtrl, null]
        return ctrl

    @classmethod
    def ctlShapeSwap(cls, source, transform):

        shp = cmds.listRelatives(source, c=1, ni=1, s=1)
        oldShp = cmds.listRelatives(transform, c=1, ni=1, s=1)
        cmds.parent(shp, transform, s=1, r=1)

        cmds.delete(oldShp, source)
        for s in shp:
            cmds.rename(s, oldShp)

    @classmethod
    def mirrorCurve(cls, lCrv, rCrv):

        lCrvCv = cmds.ls(lCrv + '.cv[*]', fl=1)
        rCrvCv = cmds.ls(rCrv + '.cv[*]', fl=1)
        cvLeng = len(lCrvCv)

        for i in range(cvLeng):
            mirrorReverse = cmds.shadingNode('reverse', asUtility=True, n='mirror{}_reverse'.format(str(i)))
            cmds.connectAttr(lCrvCv[i] + '.xValue', mirrorReverse + '.inputX')
            cmds.connectAttr(mirrorReverse + '.outputX', rCrvCv[cvLeng - i - 1] + '.xValue')
            cmds.connectAttr(lCrvCv[i] + '.yValue', rCrvCv[cvLeng - i - 1] + '.yValue')
            cmds.connectAttr(lCrvCv[i] + '.zValue', rCrvCv[cvLeng - i - 1] + '.zValue')

    def LRBlendShapeWeight(self, BSCrv, lipCrvBS):
        cvs = cmds.ls(BSCrv + '.cv[*]', fl=1)
        length = len(cvs)

        increment = 1.0 / (length - 1)
        targets = cmds.aliasAttr(lipCrvBS, q=1)
        tNum = len(targets)

        for t in range(0, tNum, 2):
            if targets[t][0] == 'l':
                indexL = re.findall('\d+', targets[t + 1])
                cmds.setAttr(
                    lipCrvBS + '.inputTarget[0].inputTargetGroup[%s].targetWeights[%s]' % (
                    str(indexL[0]), str(length / 2)),
                    .5)
                for i in range(0, length / 2):
                    cmds.setAttr(
                        lipCrvBS + '.inputTarget[0].inputTargetGroup[%s].targetWeights[%s]' % (str(indexL[0]), str(i)),
                        0)
                    cmds.setAttr(lipCrvBS + '.inputTarget[0].inputTargetGroup[%s].targetWeights[%s]' % (
                        str(indexL[0]), str(length - i - 1)), 1)

            if targets[t][0] == 'r':
                indexR = re.findall('\d+', targets[t + 1])
                cmds.setAttr(
                    lipCrvBS + '.inputTarget[0].inputTargetGroup[%s].targetWeights[%s]' % (
                    str(indexR[0]), str(length / 2)),
                    .5)
                for i in range(0, length / 2):
                    cmds.setAttr(
                        lipCrvBS + '.inputTarget[0].inputTargetGroup[%s].targetWeights[%s]' % (str(indexR[0]), str(i)),
                        1)
                    cmds.setAttr(lipCrvBS + '.inputTarget[0].inputTargetGroup[%s].targetWeights[%s]' % (
                        str(indexR[0]), str(length - i - 1)), 0)


    def shapeToCurve(self):
        """
        to make oh, oo, u shapes
        select 2vertex(center to left) on loop or select vertices in order and shaped curve last
        match vertices in edeg loop to the shape curves
        1. freeze the reference curve
        2. if vertice on edge loop: select center and next left vertex
           if vertice on none loop: manually select in ordrer to match the curve'''

        Returns:

        """
        mySel = cmds.ls(os=1, fl=1)
        # freeze curve
        targetCrv = mySel[-1]
        cmds.makeIdentity(targetCrv, apply=True, t=1, r=1, s=1, n=0, pn=1)
        targetCrvShape = cmds.listRelatives(targetCrv, c=1, typ="nurbsCurve")
        sourceVtx = mySel[:-1]
        numVtx = len(sourceVtx)
        if numVtx == 2:

            selVtx = [sourceVtx[0], sourceVtx[1]]
            orderVtx = Util.orderedVerts_edgeLoop(selVtx)

        elif numVtx > 2:
            orderVtx = sourceVtx

        for i, vtx in enumerate(orderVtx):
            pos = cmds.xform(vtx, q=1, ws=1, t=1)
            uParam = Util.getUParam(pos, targetCrv)
            print(uParam)
            dnPOC = cmds.shadingNode('pointOnCurveInfo', asUtility=True, n='dnPOC' + str(i + 1).zfill(2))
            # loc = cmds.spaceLocator ( n = "targetPoc"+ str(index+1).zfill(2))
            cmds.connectAttr(targetCrvShape[0] + ".worldSpace", dnPOC + '.inputCurve')
            # cmds.setAttr ( dnPOC + '.turnOnPercentage', 1 )
            cmds.setAttr(dnPOC + '.parameter', uParam)

            posOnCrv = cmds.getAttr(dnPOC + ".position")[0]
            cmds.xform(vtx, ws=1, t=posOnCrv)


    # individual axis
    @classmethod
    def indieScaleSquach(cls, inputAttr, outputAttr, exponent):
        """

        Args:
            inputAttr: "pSphere1.scaleY"
            outputAttr : ["pSphere1.scaleX","pSphere1.scaleZ"]
            exponent: [0.2, 0.1] **[0.5,0.5] == squash & stretch
        Returns:

        """

        tranPowerMult = cmds.shadingNode('multiplyDivide', asUtility=True, n='{}_pow_mult'.format(inputAttr.split(".")[0]))
        divideMult = cmds.shadingNode('multiplyDivide', asUtility=True, n='{}_pow_divide'.format(inputAttr.split(".")[0]))
        ratioMult = cmds.shadingNode('multiplyDivide', asUtility=True, n='{}_divisionRatio'.format(inputAttr.split(".")[0]))

        #divide operation
        cmds.setAttr('{}.operation'.format(ratioMult), 2)
        baseScaleValue = cmds.getAttr(inputAttr)
        cmds.connectAttr(inputAttr, '{}.input1X'.format(ratioMult))
        cmds.connectAttr(inputAttr, '{}.input1Y'.format(ratioMult))
        cmds.setAttr('{}.input2X'.format(ratioMult), baseScaleValue)
        cmds.setAttr('{}.input2Y'.format(ratioMult), baseScaleValue)

        cmds.connectAttr("{}.outputX".format(ratioMult), '{}.input1X'.format(tranPowerMult))
        cmds.connectAttr("{}.outputY".format(ratioMult), '{}.input1Y'.format(tranPowerMult))

        if not isinstance(exponent, list):
            exponent = [exponent]

        axis = ["X", "Y"]
        axisList = axis*(len(outputAttr))
        # power operation
        cmds.setAttr(tranPowerMult + '.operation', 3)

        for index, exp in enumerate(exponent):
            if isinstance(exp, (int, float)):
                cmds.setAttr('{}.input2{}'.format(tranPowerMult, axis[index]), exp)

            elif isinstance(exp, str):
                cmds.connectAttr(exp, '{}.input2{}'.format(tranPowerMult, axis[index]))

        # divide operation
        cmds.setAttr('{}.operation'.format(divideMult), 2)
        if not isinstance(outputAttr, list):
            outputAttr = [outputAttr]

        for index, attr in enumerate(outputAttr):
            cmds.setAttr('{}.input1{}'.format(divideMult, axisList[index]), 1)
            if not cmds.listConnections('{}.input2{}'.format(divideMult, axisList[index]), s=1, d=0 ):
                cmds.connectAttr('{}.output{}'.format(tranPowerMult, axisList[index]), '{}.input2{}'.format(divideMult, axisList[index]))
            cmds.connectAttr( '{}.output{}'.format(divideMult, axisList[index]), attr)


    def mouthSquach_setup(cls, head, ctl):

        bend = cmds.nonLinear(head, type='bend', curvature=0)

        # place "bend_locator" on "bendHandle" position / connect ctl
        xyz = cmds.xform(bend[1], q=1, ws=1, t=1)
        bendLoc = cmds.spaceLocator(n=bend[0] + "_loc")[0]
        locPlus = cmds.shadingNode("plusMinusAverage", asUtility=1, n=bend[0] + "Loc_plus")

        cmds.connectAttr(ctl + ".tx", locPlus + ".input3D[0].input3Dx")
        # cmds.connectAttr( ctl + ".ty", locPlus + ".input3D[0].input3Dy" )
        cmds.connectAttr(ctl + ".tz", locPlus + ".input3D[0].input3Dz")
        cmds.setAttr(locPlus + ".input3D[1].input3Dx", xyz[0])
        cmds.setAttr(locPlus + ".input3D[1].input3Dy", xyz[1])
        cmds.setAttr(locPlus + ".input3D[1].input3Dz", xyz[2])
        cmds.connectAttr(locPlus + ".output3D.output3Dx", bendLoc + ".tx")
        cmds.connectAttr(locPlus + ".output3D.output3Dy", bendLoc + ".ty")
        cmds.connectAttr(locPlus + ".output3D.output3Dz", bendLoc + ".tz")

        # aimConstraint "bendHandle" to "bend_locator"
        cmds.aimConstraint(bendLoc, bend[1], mo=0, weight=1, aimVector=(1, 0, 0), upVector=(0, 1, 0),
                           n=bend[0] + "aimConst")

        distNode = cmds.shadingNode("distanceBetween", asUtility=1, n=bend[0] + "dist")
        cmds.connectAttr(bend[1] + ".t", distNode + ".point1")
        cmds.connectAttr(bendLoc + ".t", distNode + ".point2")

        cmds.connectAttr(distNode + ".distance", bend[0] + ".curvature")
        # change the distance rate
        unitC = cmds.listConnections(bend[0] + ".curvature", s=1, d=0)
        print(unitC)




