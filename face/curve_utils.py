import maya.cmds as cmds
import re
import maya.mel as mel
from maya import OpenMaya
from collections import OrderedDict
from twitchScript.face import face_utils
reload(face_utils)

print("top10")
def orderedVerts_selection(vtxSel):
    """
    first vertex selection is important
    Args:
        vtxSel: vertex list on edge row(the first of the list should be the first selection : trackSelOrder)

    Returns: list of selected vertex in order
    """

    firstVtx = vtxSel[0]
    ordered = [firstVtx]
    for i in range(len(vtxSel) - 1):

        vtxSel.remove(firstVtx)
        for vtx in vtxSel:
            print(firstVtx, vtx)
            cmds.select(firstVtx, vtx, r=1)
            mel.eval('ConvertSelectionToContainedEdges')
            contEdge = cmds.filterExpand(ex=True, sm=32)

            if contEdge:
                firstVtx = vtx
                ordered.append(firstVtx)
                break

    return ordered

def orderedEdges_edgeLoop(selVerts):
    """
    Args:
        selVerts: select 2 vertices in order!!! ( the second vertex is the direction )

    Returns: list of edges in order (on edge loop / always clockwise direction!!)

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
    IDList = cmds.polySelect(firstEdge, edgeBorder=int(firstID))
    if not IDList:
        IDList = cmds.polySelect(firstEdge, edgeLoop=int(firstID))

    edgeList = ["{}.e[{}]".format(geo, ID) for ID in IDList]
    edgeLength = len(edgeList)

    if edgeLength < 4 and not edgeLength % 2 == 0:
        raise RuntimeError("Check if vertices are in edge loop")

    # if loop is closed
    firstEdgeVtxPair = edgeToVertexPair(edgeList[0])
    lastEdgeVtxPair = edgeToVertexPair(edgeList[-1])
    sharedItem = [item for item in firstEdgeVtxPair if item in lastEdgeVtxPair]
    if sharedItem:

        if edgeList[0] == edgeList[-1]:

            edgeList = edgeList[:-1]
            nextVtxList = cmds.polyListComponentConversion(edgeList[1], fromEdge=1, toVertex=1)
            secondPair = cmds.ls(nextVtxList, fl=1)
            if firstVert in secondPair:
                edgeList = [edgeList[0]] + edgeList[1:][::-1]

        else:
            firstEdgeID = edgeList.index(firstEdge)
            edgeList = edgeList[firstEdgeID:] + edgeList[:firstEdgeID]
            secondPair = edgeToVertexPair(edgeList[1])
            if firstVert in secondPair:
                edgeList = [edgeList[0]] + edgeList[1:][::-1]

    else:
        startNum = [x for x, edge in enumerate(edgeList) if edge == firstEdge][0]
        # if nextEdge is inside of range
        if startNum+1 <= edgeLength:

            nextEdge = edgeList[startNum+1]
            nextVtxList = cmds.polyListComponentConversion(nextEdge, fromEdge=1, toVertex=1)
            nextPair = cmds.ls(nextVtxList, fl=1)
            # if next edge in opposite direction
            if firstVert in nextPair:
                edgeList = edgeList[:startNum+1][::-1]
            else:
                edgeList = edgeList[startNum:]
        # if nextEdge is out of range
        else:
            edgeList = edgeList[::-1]

    return edgeList

def orderedVerts_edgeLoop(vtxSelection):
    """
    select 2 or 3 vertices for ordered vertex-list on the edge loop
    open : using the last vertex selected
    Returns: vertex list on edgeLoop (if edgeLoop is open, the last vertex would not include)

    """
    if not len(vtxSelection) in [2, 3]:
        raise RuntimeError("select 2 or 3 vertices")

    if len(vtxSelection) == 2:

        orderedList = vtxSelection
        edgeList = orderedEdges_edgeLoop(orderedList)
        endVert = None

    elif len(vtxSelection) == 3:

        orderedList = vtxSelection[:-1]
        edgeList = orderedEdges_edgeLoop(orderedList)
        endVert = vtxSelection[2]

    # [[vert1, vert2], ...]
    vtxPairList = [edgeToVertexPair(x) for x in edgeList[1:-1]]
    sumVtx = sum(vtxPairList, [])
    if endVert:
        if endVert not in sumVtx:
            raise RuntimeError("the last vtx is not on the edgeLoop")

    secondVert = orderedList[-1]

    for index, vtxPair in enumerate(vtxPairList):

        vtxPair.remove(secondVert)
        orderedList.append(vtxPair[0])
        secondVert = vtxPair[0]
        if secondVert == endVert:
            endNum = index
            break

    if endVert:
        edgeList = edgeList[:(endNum+2)] # range is edgeList[1:-1]

    return [orderedList, edgeList]

def orderedVerts_2forLoop(selVtx):
    """
    list vertices in order on the edge loop starting from selection
    Returns:

    """
    if len(selVtx) == 2:

        endVert = None

    elif len(selVtx) == 3:
        orderedList = orderedTrioVert(selVtx)
        selVtx = orderedList[:-1]
        endVert = orderedList[2]

    firstVert = selVtx[0]
    secondVert = selVtx[1]
    cmds.select(firstVert, secondVert, r=1)
    mel.eval('ConvertSelectionToContainedEdges')
    firstEdge = cmds.ls(sl=1)[0]
    cmds.polySelectSp(firstEdge, loop=1)
    edges = cmds.ls(sl=1, fl=1)
    edgeDict = edgeToVertDict(edges)  # {edge: [vert1, vert2], ...}

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
        if secondVert == endVert:
            break

    return ordered


def edgeToVertDict(edgeList):
    edgeVertDict = OrderedDict()
    for edge in edgeList:

        edgeVert = edgeToVertexPair(edge)
        edgeVertDict[edge] = edgeVert

    return edgeVertDict


def edgeToVertexPair(edge):

    cmds.select(edge, r=1)
    cmds.ConvertSelectionToVertices()
    edgeVert = cmds.ls(sl=1, fl=1)

    return edgeVert

def orderedVert_upLo(lipEye, vertSel):
    """
    select 3 vertex (corner vertices and directional vertex)
    script should work as long as the last selection be directional vertex
    Args:
        lipEye: "eye" , "lip"
        vertSel: 3 vertices selection
    Returns:

    """

    rCornerVert, secondVert, lCornerVert = orderedTrioVert(vertSel)

    selVtx = [rCornerVert, secondVert]
    # get ordered vtx list on the edgeLoop
    orderedVtx, orderedEdge = orderedVerts_edgeLoop(selVtx)
    # get up/lo verts
    endNum = 0
    for v, y in enumerate(orderedVtx):
        # find lCornerVert in the upper lid Vertices
        if y == lCornerVert:
            endNum = v

    if endNum == 0:
        raise RuntimeError(" 3 vertices are not on the edge loop")

    upVert = orderedVtx[:endNum + 1]
    loVert = [rCornerVert] + orderedVtx[endNum:][::-1]
    upEdges = orderedEdge[:endNum]
    loEdges = orderedEdge[endNum:][::-1]

    if lipEye == 'eye':
        rCornerVerts = face_utils.mirrorVertices([rCornerVert, lCornerVert])
        rUpVert = face_utils.mirrorVertices(upVert)
        rLoVert = face_utils.mirrorVertices(loVert)
        if not cmds.attributeQuery("l_cornerVerts", node="lidFactor", exists=1):
            cmds.addAttr("lidFactor", ln="l_cornerVerts", dt="stringArray")
        if not cmds.attributeQuery("r_cornerVerts", node="lidFactor", exists=1):
            cmds.addAttr("lidFactor", ln="r_cornerVerts", dt="stringArray")

        if not cmds.attributeQuery("l_upLidVerts", node="lidFactor", exists=1):
            cmds.addAttr("lidFactor", ln="l_upLidVerts", dt="stringArray")
        if not cmds.attributeQuery("l_upLidEdges", node="lidFactor", exists=1):
            cmds.addAttr("lidFactor", ln="l_upLidEdges", dt="stringArray")

        if not cmds.attributeQuery("r_upLidVerts", node="lidFactor", exists=1):
            cmds.addAttr("lidFactor", ln="r_upLidVerts", dt="stringArray")

        if not cmds.attributeQuery("l_loLidVerts", node="lidFactor", exists=1):
            cmds.addAttr("lidFactor", ln="l_loLidVerts", dt="stringArray")
        if not cmds.attributeQuery("l_loLidEdges", node="lidFactor", exists=1):
            cmds.addAttr("lidFactor", ln="l_loLidEdges", dt="stringArray")

        if not cmds.attributeQuery("r_loLidVerts", node="lidFactor", exists=1):
            cmds.addAttr("lidFactor", ln="r_loLidVerts", dt="stringArray")

        cmds.setAttr("lidFactor.l_cornerVerts", 2, rCornerVert, lCornerVert, type="stringArray")
        cmds.setAttr("lidFactor.r_cornerVerts", 2, rCornerVerts[0], rCornerVerts[1], type="stringArray")

        cmds.setAttr("lidFactor.l_upLidVerts", type="stringArray", *([len(upVert)] + upVert))
        cmds.setAttr("lidFactor.l_upLidEdges", type="stringArray", *([len(upEdges)] + upEdges))
        cmds.setAttr("lidFactor.r_upLidVerts", type="stringArray", *([len(rUpVert)] + rUpVert))

        cmds.setAttr("lidFactor.l_loLidVerts", type="stringArray", *([len(loVert)] + loVert))
        cmds.setAttr("lidFactor.l_loLidEdges", type="stringArray", *([len(loEdges)] + loEdges))
        cmds.setAttr("lidFactor.r_loLidVerts", type="stringArray", *([len(rLoVert)] + rLoVert))

    elif lipEye == 'lip':
        if not cmds.attributeQuery("upLipVerts", node="lipFactor", exists=1):
            cmds.addAttr("lipFactor", ln="upLipVerts", dt="stringArray")
        if not cmds.attributeQuery("upLipEdges", node="lipFactor", exists=1):
            cmds.addAttr("lipFactor", ln="upLipEdges", dt="stringArray")

        if not cmds.attributeQuery("loLipVerts", node="lipFactor", exists=1):
            cmds.addAttr("lipFactor", ln="loLipVerts", dt="stringArray")
        if not cmds.attributeQuery("loLipEdges", node="lipFactor", exists=1):
            cmds.addAttr("lipFactor", ln="loLipEdges", dt="stringArray")

        cmds.setAttr("lipFactor.upLipVerts", type="stringArray", *([len(upVert)] + upVert))
        cmds.setAttr("lipFactor.upLipEdges", type="stringArray", *([len(upEdges)] + upEdges))
        cmds.setAttr("lipFactor.loLipVerts", type="stringArray", *([len(loVert)] + loVert))
        cmds.setAttr("lipFactor.loLipEdges", type="stringArray", *([len(loEdges)] + loEdges))

    return [upVert, loVert]


def orderedTrioVert(trioVert):
    """
    Not working in - side
    the last selection should be the directional vertex
    Args:
        trioVert: 3 vertices selected

    Returns:[rCornerVert, secondVert, lCornerVert]

    """

    if not len(trioVert) == 3:
        raise RuntimeError("'select 3 vertices on edge loop!'")

    vertPosDict = {}
    for vt in trioVert:
        vertPos = cmds.xform(vt, q=1, ws=1, t=1)
        vertPosDict[vt] = vertPos

    # returns list[ ("vert1",[x,y,z]), ("vert2",[x,y,z]), ("vert3",[x,y,z])....]
    vertOrder = sorted(vertPosDict.items(), key=lambda x: x[1][0])  # x[1] = [x,y,x]
    lCornerVert = vertOrder[-1][0]
    trioVert.remove(lCornerVert)

    secondVert = trioVert[-1]
    rCornerVert = trioVert[0]

    orderedTrio = [rCornerVert, secondVert, lCornerVert]

    return orderedTrio


# store brow vertices in browFactor( selection order: center to left !! )
def browOrderedVertices(vertSel):
    """
    select 3 vertices
    derivative from def orderedVerts_edgeLoop()
    get the list of browVertices in order
    """
    face_utils.trackSelOrder()

    rCornerVert, secondVert, lastVert = orderedTrioVert(vertSel)
    selVtx = [rCornerVert, secondVert, lastVert]

    orderedVtx, orderedEdge = orderedVerts_edgeLoop(selVtx)

    if not cmds.attributeQuery("browVerts", node="browFactor", exists=1):
        cmds.addAttr("browFactor", ln="browVerts", dt="stringArray")
    if not cmds.attributeQuery("browEdges", node="browFactor", exists=1):
        cmds.addAttr("browFactor", ln="browEdges", dt="stringArray")

    cmds.setAttr("browFactor.browVerts", type="stringArray", *([len(orderedVtx)] + orderedVtx))
    cmds.setAttr("browFactor.browEdges", type="stringArray", *([len(orderedEdge)] + orderedEdge))

    return [orderedVtx, orderedEdge]


def createPolyToCurve(orderedEdges, name=None, **kwargs):
    """
    if first and the last vertex is same, it will close it
    vertices no need to be on the edge loop (manually select continuous vertices)
    Args:
        orderedEdges: vertices on edgeLoop in order
        name: browGuide_crv
        kwargs: direction: 1 or -1 (+ or - direction) / degree = 1,2,3
    Returns: polyEdgeToCurve degree 1

    """

    if not orderedEdges:
        raise RuntimeError("provide orderedEdges on edgeLoop")

    cmds.select(orderedEdges)

    #form = 2 : best guess (whether open or close)
    polyCrv = cmds.polyToCurve(form=2, degree=1, n="{}_crv".format(name))[0]

    polyCrvShp = cmds.listRelatives(polyCrv, c=1, type="nurbsCurve")[0]

    form = cmds.getAttr("{}.f".format(polyCrvShp))
    cvList = cmds.ls(polyCrv + ".cv[*]", fl=1)
    cvStart = cmds.xform(cvList[0], q=1, ws=1, t=1)
    cvEnd = cmds.xform(cvList[-1], q=1, ws=1, t=1)
    if not kwargs:
        if form == 0:
            if cvStart[0] > cvEnd[0]:
                cmds.reverseCurve(polyCrv, ch=1, rpo=1)
    else:

        if kwargs["direction"] == 1:
            if form == 0:
                if cvStart[0] > cvEnd[0]:
                    cmds.reverseCurve(polyCrv, ch=1, rpo=1)

        elif kwargs["direction"] == -1:
            if form == 0:
                if cvStart[0] < cvEnd[0]:
                    cmds.reverseCurve(polyCrv, ch=1, rpo=1)

    return polyCrv


def curveOnEdgeLoop(name, nature, selVtx, degree):

    if not cmds.objExists("surfaceMap_grp"):
        cmds.group(em=1, n="surfaceMap_grp")

    if not len(selVtx) in [2, 3]:
        raise RuntimeError("select 2 or 3 vertices")

    allVerts = orderedVerts_2forLoop(selVtx)
    # curve needs minimum 4vertices
    if len(allVerts) <= 3:

        raise RuntimeError("Wrong edgeLoop are selected'")

    vertsPos = []
    for v in allVerts:
        pos = cmds.xform(v, q=1, ws=1, t=1)
        vertsPos.append(pos)

    crv = cmds.curve(d=int(degree), p=vertsPos)
    if len(selVtx) == 2:
        cmds.closeCurve(crv, ch=0, ps=True, replaceOriginal=1)
    crvName = cmds.rename(crv, '{}{}_crv01'.format(name, nature))
    cmds.parent(crvName, "surfaceMap_grp")
    cmds.toggle(crvName, cv=True)


def checkEdgeLoopWithSelectedVtx(orderedVtx):
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


def createCurveOnPointPos(name, nature, selVtx=[], degree=1):
    """
    For creating surfMap (select 2 vertex for closedCrv / 3 vertex for openCrv)
    select corner and direction vertex in that order
    Returns: curve with position of ordered vertices( contains selected Vertices)

    Args:
        degree: curve degree
        name: "eye" or "lip"
        nature:"guide", "loft", "test", "map".....
        selVtx: selected Vertices( corner and vector)
    Returns:curves for surfaceMap

    """
    if not len(selVtx) in [2, 3]:
        raise RuntimeError("Select 2 or 3 vertices of the edge")

    print("selected vtx for orderVerts are {}".format(selVtx))
    vtxListOnLoop = orderedVerts_edgeLoop(selVtx)[0]

    storedVtx = []
    if name == "eye":
        vtxUp = cmds.getAttr("lidFactor.l_upLidVerts")
        vtxLo = cmds.getAttr("lidFactor.l_loLidVerts")
        storedVtx = vtxUp[:-1] + vtxLo[:-1]
    elif name == "lip":
        vtxUp = cmds.getAttr("lipFactor.upLipVerts")
        vtxLo = cmds.getAttr("lipFactor.loLipVerts")
        storedVtx = vtxUp[:-1] + vtxLo[:-1]

    elif name == "brow":
        vtxList = cmds.getAttr("browFactor.browVerts")
        storedVtx = vtxList

    numOfJnt = len(storedVtx)
    print(numOfJnt, len(vtxListOnLoop))
    if not numOfJnt == len(vtxListOnLoop):
        raise RuntimeError('check if it looping or selection is matching with vertices stored')

    vertsPos = []
    for v in vtxListOnLoop:
        pos = cmds.xform(v, q=1, ws=1, t=1)
        vertsPos.append(pos)

    crv = cmds.curve(d=degree, p=vertsPos)
    if not len(selVtx) == 3:
        cmds.closeCurve(crv, ch=0, preserveShape=True, replaceOriginal=1)

    crvName = cmds.rename(crv, '{}{}_crv01'.format(name, nature))
    cmds.toggle(crvName, cv=True)

    cmds.parent(crvName, "surfaceMap_grp")

    return crvName

def curve_halfVerts(orderedVertices, name, openClose, degree, suffix):
    """
    1. create a curve with manual selection
    2. select center vert first and left half
    3. turn off symmetry select / turn on tracking selection
    create brow curve for browMapSurf
    Args:
        orderedVertices: center vert first and left half in order
        name:
        openClose:
        degree:
        suffix:
    Returns:

    """

    mapCrv = mapEPCurve(orderedVertices, name, openClose, degree, suffix)
    #mapEPCurve( ordered, name, openClose, degree ) ''' 3degree epCurve create extra 2 CVs'''

    #keepRange 0 - reparameterize the resulting curve from 0 to 1
    crvRebuild = cmds.rebuildCurve(mapCrv, ch=0, rpo=1, kr=0, kcp=1, kep=1, d=int(degree), n=name)
    if cmds.listHistory(crvRebuild[0]):
        cmds.delete(crvRebuild[0], ch=1)


def mapEPCurve(orderedVertices, name, openClose, degree, suffix):

    """
    1. create a curve with manual selection
    2. select center first, and left half
    3. Based on the key muscles( brow: center muscle / deprreser / corrigator)
    4. usage - creating prototype curve
    Args:
        orderedVertices:
        name: "brow","eye","lip"
        openClose: "open", "close"
        degree: 1, 2, 3
        suffix: "_guide"
    Returns:

    """
    orderPos = []
    leftPos = []
    rightPos = []
    if name in ["brow", "lip"]:
        vt = cmds.xform(orderedVertices[0], q=1, t=1, ws=1)
        if vt[0] ** 2 > 0.001:
            raise RuntimeError('object or first vertex is not on center')

        for t in orderedVertices[1:][::-1]:
            vtxPos = cmds.xform(t, q=1, t=1, ws=1)
            mrrPos = [-vtxPos[0], vtxPos[1], vtxPos[2]]
            rightPos.append(mrrPos)

        for v in orderedVertices:
            vtxPos = cmds.xform(v, q=1, t=1, ws=1)
            leftPos.append(vtxPos)

    elif name == "eye":
        for v in orderedVertices:
            vtxPos = cmds.xform(v, q=1, t=1, ws=1)
            orderPos.append(vtxPos)

    #create unique name
    nameCheck = cmds.ls("{}Crv{}01".format(name, suffix))
    if nameCheck:
        num = len(nameCheck)
        rename = "{}Crv{}{}".format(name, suffix, str(num+1).zfill(2))
    else:
        rename = "{}Crv{}01".format(name, suffix)

    # curve Open / Close
    if openClose == "open":
        if name == "eye":
            orderedPos = orderPos
        else:
            orderedPos = rightPos + leftPos

        browMapCrv = cmds.curve(d=float(degree), ep=orderedPos)
        cmds.rename(browMapCrv, rename)

    elif openClose == "close":
        if name == "eye":
            orderedPos = orderPos
        else:
            orderedPos = leftPos[:-1] + rightPos + [leftPos[0]]

        coords = orderedPos
        curveFn = OpenMaya.MFnNurbsCurve()
        arr = OpenMaya.MPointArray()
        for pos in coords:
            arr.append(*pos)

        mObject = curveFn.createWithEditPoints(
            arr,
            int(degree),
            OpenMaya.MFnNurbsCurve.kPeriodic,
            False,
            False,
            True            )

        mod = OpenMaya.MDagModifier()
        mod.renameNode(mObject, rename)
        mod.doIt()

    return rename

def browMapCurve(orderSel, numOfVtx, nature):
    """
    if vertex selected == joints on every vertices of edgeLoop : create polyEdgeCrv
    else: use existing poc node(*_browJnt_*_poc)
    Returns: brow curves

    """
    if not cmds.objExists("surfaceMap_grp"):
        cmds.group(em=1, n="surfaceMap_grp", p="dumpBin_grp")

    headGeo = cmds.getAttr("helpPanel_grp.headGeo")
    headBBox = cmds.getAttr("helpPanel_grp.headBBox")

    moveUnit = headBBox[1]/100

    if numOfVtx == "Every":
        vtx_xVal = [cmds.xform(x, q=1, ws=1, t=1)[0] for x in orderSel]
        if max(vtx_xVal) > 0:
            raise RuntimeError("select the vertices brows rightCorner")

        firstVtx = cmds.getAttr("browFactor.browVerts")[0]
        print("first Vtx is {}".format(firstVtx))
        if firstVtx not in orderSel:
            raise RuntimeError("selection on wrong edge loop")

        loftCrvList = seriesOfEdgeBrowCrv(orderSel, nature)

    else:
        browPocList = cmds.getAttr("browFactor.pocList")
        posList = []
        for poc in browPocList:
            pos = cmds.getAttr("{}.position".format(poc))[0]
            posList.append(pos)
        tempCrv = cmds.curve(d=1, ep=posList)
        baseCrv = cmds.rename(tempCrv, "brow_{}_crv01".format(nature))
        cmds.parent(baseCrv, "surfaceMap_grp")
        upCrv = cmds.duplicate(baseCrv, rc=1, n="brow_{}_crv02".format(nature))[0]
        loCrv = cmds.duplicate(baseCrv, rc=1, n="brow_{}_crv03".format(nature))[0]
        face_utils.create_shrink_wrap(upCrv, headGeo)
        face_utils.create_shrink_wrap(loCrv, headGeo)
        cmds.setAttr("{}.ty".format(upCrv), moveUnit*10)
        cmds.setAttr("{}.ty".format(loCrv), moveUnit*-4)
        loftCrvList = [loCrv, baseCrv, upCrv]

    #surfShape = loftFacePart("brow", loftCrvList)

    return loftCrvList


def seriesOfEdgeBrowCrv(selection, nature):

    if len(selection) <= 2:
        raise RuntimeError('check the vertex selection!!')

    if not selection[0].split(".")[0] == cmds.getAttr("helpPanel_grp.headGeo"):
        raise RuntimeError('wrong geo selected')

    if not cmds.objExists("surfaceMap_grp"):
        cmds.group(em=1, n="surfaceMap_grp", p="dumpBin_grp")

    # re-arrange the selection based on topology
    orderSel = orderedVerts_selection(selection)
    posVerts = {}
    endVerts = face_utils.mirrorVertices(orderSel)
    for index, vtx in enumerate(orderSel):
        posVerts[vtx] = endVerts[index]

    orderedEdges = cmds.getAttr("browFactor.browEdges")

    storedVtx = cmds.getAttr("browFactor.browVerts")
    if not storedVtx[0] in orderSel:
        raise RuntimeError("check the vertex selection!!, missing stored brow vertex")

    #orderSelVerts.remove(storedVtx[0])

    firstEdge = orderedEdges[0]
    geo = firstEdge.split(".")[0]
    cmds.select(firstEdge)
    firstID = re.findall('\d+', firstEdge)[-1]
    IDList = cmds.polySelect(edgeRing=int(firstID))
    edgeList = ["{}.e[{}]".format(geo, ID) for ID in IDList]
    ringEdges = cmds.ls(edgeList, fl=1)

    #get only rings for selected vertices
    selEdges = cmds.polyListComponentConversion(orderSel, fv=True, te=True)
    rings = [x for x in cmds.ls(selEdges, fl=1) if x in ringEdges]

    loftCrvList = []
    for index, vtx in enumerate(orderSel):
        print( index, vtx)
        if vtx == storedVtx[0]:
            mainCrv = createPolyToCurve(orderedEdges, name="brow_{}".format(nature), direction=1)
            loftCrvList.append(mainCrv)
            continue

        edges = cmds.polyListComponentConversion(vtx, fv=True, te=True)
        ring = [x for x in cmds.ls(edges, fl=1) if x in rings]

        vtxPair = edgeToVertexPair(ring[0])
        vtxPair.remove(vtx)
        trioVtx = [vtx, vtxPair[0], posVerts[vtx]]

        edgeLoop = orderedVerts_edgeLoop(trioVtx)[1]
        loftCrv = createPolyToCurve(edgeLoop, "brow_{}".format(nature))
        loftCrvList.append(loftCrv)

    cmds.parent(loftCrvList, "surfaceMap_grp")

    return loftCrvList


def seriesOfEdgeLoopCrv(lipEye, nature, vtxList):
    """
    # the first vert and last vert are on the edge loop!!!
    # !!seriesOfEdgeLoopCrv condition!!
    # 1. edgeVertDict(ringEdges)
    # 2. get the vertex belongs to edge ring
    # 2. curveOnEdgeLoop
    # a. orderedVerts_edgeLoop

    if not working : check the corner vertices and mark them!!!( you will make this mistake )
    1. symmetry turn on
    2. selected verts are not on the edge loop
    3. selectPref( trackSelectionOrder = 0 )
    Args:
        lipEye: "lip" "eye"
        nature: "guide", "loft", "test", "map".....
        vtxList :selected vertex list

    Returns: closed curve

    """
    if not cmds.objExists("surfaceMap_grp"):
        cmds.group(em=1, n="surfaceMap_grp", p="dumpBin_grp")

    if lipEye == 'eye':
        part = "lid"
        attrList = ["l_upLid", "l_loLid"]

    elif lipEye == 'lip':
        part = "lip"
        attrList = ["upLip", "loLip"]

    if len(vtxList) <= 1:
        raise RuntimeError('check the vertices selection!!')

    # if not vtxList[0].split(".")[0] == cmds.getAttr("helpPanel_grp.headGeo"):
    #     raise RuntimeError('wrong geo selected')

    orderSel = orderedVerts_selection(vtxList)

    # get orderedVtxList with store vtx data!!!
    storedVtx = []
    for att in attrList:

        uploList = cmds.getAttr("{}Factor.{}Verts".format(part, att))
        storedVtx += uploList[:-1]

    firstEdge = cmds.getAttr("{}Factor.{}Edges".format(part, attrList[0]))[0]
    cmds.polySelectSp(firstEdge, ring=1)
    ringEdges = cmds.ls(sl=1, fl=1)
    selEdges = cmds.polyListComponentConversion(orderSel, fv=True, te=True)
    rings = [x for x in cmds.ls(selEdges, fl=1) if x in ringEdges]
    ringEdgeDict = face_utils.Util.edgeVertDict(rings)

    crvList = []
    for vrt in orderSel:

        for edge, vtxPair in ringEdgeDict.iteritems():

            if vrt in vtxPair:

                vtxPair.remove(vrt)
                selVtx = [vrt, vtxPair[0]]
                crv = createCurveOnPointPos(lipEye, nature, selVtx, degree=1)
                crvList.append(crv)
                break

    return crvList


def symmetrizeOpenCrv(crvSel, direction):

    cvList = cmds.ls(crvSel + ".cv[*]", l=1, fl=1)
    cvLength = len(cvList)

    if direction == 1:
        print("left cv to right cv")

        for i in range(cvLength / 2):
            cv = cvList[cvLength - i - 1]

            cvPos = cmds.xform(cv, os=1, q=1, t=1)

            cmds.xform(cvList[i], os=1, t=(-cvPos[0], cvPos[1], cvPos[2]))

    else:
        print("right cv to left cv")

        for i in range(cvLength / 2):
            cv = cvList[i]
            cvPos = cmds.xform(cv, os=1, q=1, t=1)

            cmds.xform(cvList[cvLength - i - 1], os=1, t=(-cvPos[0], cvPos[1], cvPos[2]))


# curve should have center cv[ 0, y, z]
def symmetrizeCloseCrv(crvSel, direction):

    if not cmds.objExists(crvSel):
        raise RuntimeError('select a curve first!!')

    crvShp = cmds.listRelatives(crvSel, c=1, ni=1, s=1)

    if not len(cmds.ls(crvShp)) == 1:
        raise RuntimeError('more than 1 "%s" matches name!!' % crvShp[0])

    crvCvs = cmds.ls("{}.cv[*]".format(crvSel), fl=1)
    fullLength = len(crvCvs)

    numList = [x for x in range(fullLength)]

    if not fullLength % 2 == 0:
        raise RuntimeError("wrong number of cvs")

    halfLength = (fullLength - 2) / 2
    cvPlus = []
    centerCV = []
    for cv in crvCvs:
        cvID = cv.split('[')[1][:-1]
        pos = cmds.xform(cv, q=1, ws=1, t=1)
        if pos[0] ** 2 < 0.0001:
            centerCV.append(cvID)

        elif pos[0] > 0.01:
            cvPlus.append(cvID)

    if not len(centerCV) == 2:
        raise RuntimeError("must have 2 center cvs in order to symmetrize")

    if int(centerCV[0]) < halfLength:
        startNum = int(centerCV[0]) + 1
        endNum = startNum + halfLength
        halfNum = numList[startNum:endNum]
        opphalf = numList[endNum + 1:] + numList[:int(centerCV[0])]

        # curve direction( --> )
        if cmds.xform(crvCvs[startNum], q=1, os=1, t=1)[0] > 0:
            leftNum = halfNum
            rightNum = opphalf[::-1]
        # curve direction( <-- )
        elif cmds.xform(crvCvs[startNum], q=1, os=1, t=1)[0] < 0:
            leftNum = opphalf
            rightNum = halfNum[::-1]

    else:
        startNum = int(centerCV[1]) + 1
        endNum = int(centerCV[0])
        halfNum = numList[int(centerCV[1])+1:] + numList[startNum:endNum]
        opphalf = numList[endNum + 1:int(centerCV[0])]

        # curve direction( --> )
        if cmds.xform(crvCvs[startNum], q=1, os=1, t=1)[0] > 0:
            leftNum = opphalf[::-1]
            rightNum = halfNum
        # curve direction( <-- )
        elif cmds.xform(crvCvs[startNum], q=1, os=1, t=1)[0] < 0:
            leftNum = halfNum
            rightNum = opphalf[::-1]

    print(endNum)
    if direction:
        print("left cv to right cv")

        for i in range(halfLength):
            pos = cmds.xform(crvCvs[leftNum[i]], q=1, ws=1, t=1)
            cmds.xform(crvCvs[rightNum[i]], os=1, t=(-pos[0], pos[1], pos[2]))

    else:
        print("right cv to left cv")

        for i in range(halfLength):
            pos = cmds.xform(crvCvs[rightNum[i]], q=1, ws=1, t=1)
            cmds.xform(crvCvs[leftNum[i]], os=1, t=(-pos[0], pos[1], pos[2]))

def resetBStargetCrv(selCrvList):

    for selCrv in selCrvList:

        selCrvShp = cmds.listRelatives(selCrv, c=1)[0]
        BS = cmds.listConnections(selCrvShp, d=1, s=0, type="blendShape")[0]

        if not BS:
            raise RuntimeError("select blendShape target curve")

        tweak = [x for x in cmds.listHistory(BS, pdo=1) if cmds.nodeType(x) == 'tweak'][0]
        origShp = [x for x in cmds.listHistory(tweak) if cmds.nodeType(x) == 'nurbsCurve'][0]

        origCvs = cmds.ls('{}.cv[*]'.format(origShp), fl=1)
        cvs = cmds.ls('{}.cv[*]'.format(selCrv), fl=1)
        for cv, origCv in zip(cvs, origCvs):
            print(cv, origCv)
            xVal = cmds.getAttr('{}.xValue'.format(origCv))
            yVal = cmds.getAttr('{}.yValue'.format(origCv))
            zVal = cmds.getAttr('{}.zValue'.format(origCv))

            xCnnt = cmds.listConnections('{}.xValue'.format(cv), s=1)
            yCnnt = cmds.listConnections('{}.yValue'.format(cv), s=1)
            zCnnt = cmds.listConnections('{}.zValue'.format(cv), s=1)
            if xCnnt or yCnnt or zCnnt:
                raise RuntimeError('{} value have connections!!'.format(cv))
            else:
                cmds.setAttr('{}.xValue'.format(cv), xVal)
                cmds.setAttr('{}.yValue'.format(cv), yVal)
                cmds.setAttr('{}.zValue'.format(cv), zVal)


# select source curve first and target curve
# mirror A crv for B crv
def copyCurveShape(crvSel):

    scCrv = crvSel[0]
    tgtCrv = crvSel[1]

    scCvs = cmds.ls(scCrv + ".cv[*]", l=1, fl=1)
    dnCvs = cmds.ls(tgtCrv + ".cv[*]", l=1, fl=1)

    scStart = cmds.xform(scCvs[0], q=1, os=1, t=1)
    scEnd = cmds.xform(scCvs[-1], q=1, os=1, t=1)
    # get sc curve u direction
    scDirection = scEnd[0] - scStart[0]

    dnStart = cmds.xform(dnCvs[0], q=1, os=1, t=1)
    dnEnd = cmds.xform(dnCvs[-1], q=1, os=1, t=1)
    # get curve u direction
    dnDirection = dnEnd[0] - dnStart[0]

    scLeng = len(scCvs)
    dnLeng = len(dnCvs)

    if not scLeng == dnLeng:
        raise RuntimeError('select curves with same number of cvs')

    if not scDirection * dnDirection > 0:
        cmds.confirmDialog(title='Confirm', message="selected curves u-direction are opposite")

    for i in range(scLeng):
        scPos = cmds.xform(scCvs[i], q=1, os=1, t=1)
        print(scPos[0])
        cmds.setAttr(dnCvs[i] + ".xValue", scPos[0])
        cmds.setAttr(dnCvs[i] + ".yValue", scPos[1])
        cmds.setAttr(dnCvs[i] + ".zValue", scPos[2])

def mirrorCurveShape(crvSel):

    scCrv = crvSel[0]
    tgtCrv = crvSel[1]
    scCvs = cmds.ls(scCrv + ".cv[*]", l=1, fl=1)
    dnCvs = cmds.ls(tgtCrv + ".cv[*]", l=1, fl=1)

    scStart = cmds.xform(scCvs[0], q=1, os=1, t=1)
    scEnd = cmds.xform(scCvs[-1], q=1, os=1, t=1)
    # get sc curve u direction
    scDirection = scEnd[0] - scStart[0]

    dnStart = cmds.xform(dnCvs[0], q=1, os=1, t=1)
    dnEnd = cmds.xform(dnCvs[-1], q=1, os=1, t=1)
    # get curve u direction
    dnDirection = dnEnd[0] - dnStart[0]

    scLeng = len(scCvs)
    dnLeng = len(dnCvs)

    if scDirection * dnDirection > 0:
        if scLeng == dnLeng:
            for i in range(scLeng):
                scPos = cmds.xform(scCvs[i], q=1, os=1, t=1)

                cmds.setAttr(dnCvs[dnLeng - i - 1] + ".xValue", -scPos[0])
                cmds.setAttr(dnCvs[dnLeng - i - 1] + ".yValue", scPos[1])
                cmds.setAttr(dnCvs[dnLeng - i - 1] + ".zValue", scPos[2])

        else:
            cmds.confirmDialog(title='Confirm', message='select curves with same number of cvs')

    elif scDirection * dnDirection < 0:

        if scLeng == dnLeng:
            for i in range(scLeng):
                scPos = cmds.xform(scCvs[i], q=1, os=1, t=1)

                cmds.setAttr(dnCvs[i] + ".xValue", -scPos[0])
                cmds.setAttr(dnCvs[i] + ".yValue", scPos[1])
                cmds.setAttr(dnCvs[i] + ".zValue", scPos[2])

        else:
            cmds.confirmDialog(title='Confirm', message='select curves with same number of cvs')


def copyCrvs_fromReference(crvSelList):
    """
    copy from referenced curves to the seleccted curves by name
    """
    crvs = cmds.ls(sl=1, type="transform")
    for crv in crvs:

        sourceCrv = cmds.ls("*:{}".format(crv))

        if sourceCrv:
            cmds.select(sourceCrv[0], r=1)
            cmds.select(crv, add=1)
            crvSel = cmds.ls(os=1 )
            print(crvSel)
            UnlockAll(crvSel)
            copyCurveShape(crvSel)

#arFace specific function( mirror the selected left crv to right)
def mirrorCrvLeftToRight(crvSelList):

    crvs = cmds.ls(sl=1, type="transform")
    for crv in crvs:
        '''
        sourceCrv = cmds.ls("*:{}".format(crv))
    
        if sourceCrv:    
            cmds.select(sourceCrv[0], r=1)
            cmds.select(crv, add=1)
            crvSel = cmds.ls(os=1 )
            print(crvSel)
            UnlockAll(crvSel)
            curve_utils.copyCurveShape(crvSel)'''

        if crv.startswith('l_'):
            cmds.select(crv, r=1)
            cmds.select(crv.replace('l_', 'r_'), add=1)
            crvSel = cmds.ls(os=1, type="transform")
            mirrorCurveShape(crvSel)

        elif crv.startswith('r_'):
            cmds.select(crv, r=1)
            cmds.select(crv.replace('r_', 'l_'), add=1)
            crvSel = cmds.ls(os=1, type="transform")
            mirrorCurveShape(crvSel)


def UnlockAll(objs):
    locked = []
    for obj in objs:
        attrs = cmds.listAttr(obj)
        for attr in attrs:
            try:
                attrObj = "{0}.{1}".format(obj, attr)
                if cmds.getAttr(attrObj, lock=True):
                    cmds.setAttr(attrObj, lock=0)
                    locked.append(attrObj)
            except ValueError:
                continue
    print(locked)

