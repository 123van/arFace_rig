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

class HeadGeo(object):
    """
    selected headGeo general info
    """
    def __init__(self):

        self.name = self.getName()
        self.boundingBox = None
        self.skin = None
        self.vert_size = None

    def getName(self):

        selection = pm.ls(sl=1, typ='transform')
        if selection:
            return selection[0]

        else:
            raise RuntimeError('select something')

    def getSkin(self):

        self.skin = mel.eval("findRelatedSkinCluster %s" % self.name)

        return self.skin

    def getVertSize(self):

        self.vert_size = cmds.polyEvaluate(self.name, v=1)

        return self.vert_size

    def getBoundBox(self):
        print
        self.name
        browBbox = cmds.exactWorldBoundingBox(self.name)
        xLength = browBbox[3]
        yLength = abs(browBbox[4] - browBbox[1])
        zLength = abs(browBbox[5] - browBbox[2])
        self.bBox = [xLength, yLength, zLength]

        return self.bBox

class Util(object):
    def __init__(self):
        pass

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

    def group(self, children=[], parent=''):
        """
        create parent node and parent children under it
        """
        if not cmds.objExists(parent):
            cmds.createNode('transform', n=parent)
        self.toggleSelect(r=children, tgl=parent)
        cmds.parent()

        return parent

    def parent(self, children=[], parent=''):
        """
        parent children to parent
        """
        cmds.select(children, r=True)
        cmds.select(parent, tgl=True)
        cmds.parent()

        return parent

    def match(self, dest='', source=''):
        """
        dest = thing to match
        run orient, point constraint to match tr and orientation
        """
        self.toggleSelect(source, dest)
        orc = cmds.orientConstraint(mo=False, weight=1)
        self.toggleSelect(source, dest)
        ptc = cmds.pointConstraint(mo=False, weight=1)

        cmds.delete(orc)
        cmds.delete(ptc)

    def toggleSelect(self, r=[], tgl=''):
        """
        toggle select two object
        """
        cmds.select(r, r=True)
        cmds.select(tgl, tgl=True)

    def sortSelected(self, selVerts=[]):
        """
        sorting selected object from -x to x
        """
        for x in range(len(selVerts)):
            for i in range(len(selVerts) - 1):
                vert1 = cmds.xform(selVerts[i], q=True, t=True, ws=True)
                vert2 = cmds.xform(selVerts[i + 1], q=True, t=True, ws=True)
                if vert2[0] < vert1[0]:
                    temp = selVerts[i]
                    selVerts[i] = selVerts[i + 1]
                    selVerts[i + 1] = temp
        return selVerts

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

    @classmethod
    def orderedVert(cls, lipEye):
        """
        select vert: corner vertices and direction vertex in order

        """
        vertSel = cmds.ls(os=1, fl=1)
        if len(vertSel) == 3:

            vert1Pos = cmds.xform(vertSel[0], q=1, ws=1, t=1)
            vert2Pos = cmds.xform(vertSel[1], q=1, ws=1, t=1)
            # vert3Pos = cmds.xform (vertSel[2], q=1, ws=1, t=1 )
            vertDict = {vertSel[0]: vert1Pos[0], vertSel[1]: vert2Pos[0]}
            txPos = vertDict.values()
            for x, y in vertDict.items():
                if y == max(txPos):
                    lCornerVert = x

            vertDict.pop(lCornerVert)
            rCornerVert = vertDict.keys()
            secondVert = vertSel[2]

            cmds.select(rCornerVert, secondVert, r=1)
            # get ordered verts on the edgeLoop
            ordered = cls.orderedVerts_edgeLoop()
            print (ordered)
            # get up/lo verts
            for v, y in enumerate(ordered):
                if y == lCornerVert:
                    endNum = v + 1

            if lipEye == 'eye':
                upVert = ordered[1:endNum - 1]
                loVert = ordered[endNum:]

            elif lipEye == 'lip':
                upVert = ordered[:endNum]
                loVert = ordered[endNum - 1:]
                loVert.append(rCornerVert)

            # store the verts seperately for up / lo
            print("up verts : ", upVert)
            print("low verts : ", loVert[::-1])
        else:
            print('select three points!')


    @classmethod
    def orderedVertUpLo(cls, lipEye):
        """
        lip or eye
        """
        mySel = cmds.ls(sl=1, fl=1)
        vertSel = []
        if lipEye == 'eye':
            for v in mySel:
                vPos = cmds.xform(v, q=1, ws=1, t=1)
                if vPos[0] > 0:
                    vertSel.append(v)
        elif lipEye == 'lip':
            vertSel = mySel

        if len(vertSel) == 3:
            vertPosDict = {}
            for vt in vertSel:
                vertPos = cmds.xform(vt, q=1, ws=1, t=1)
                vertPosDict[vt] = vertPos

            xMaxPos = max(vertPosDict[vertSel[0]][0], vertPosDict[vertSel[1]][0], vertPosDict[vertSel[2]][0])
            for j, x in vertPosDict.items():
                if x[0] == xMaxPos:
                    lCornerVert = j

            vertPosDict.pop(lCornerVert)
            vertSel.remove(lCornerVert)

            yMaxPos = max(vertPosDict[vertSel[0]][1], vertPosDict[vertSel[1]][1])
            for i, y in vertPosDict.items():
                if y[1] == yMaxPos:
                    secndVert = i

            vertSel.remove(secndVert)

            rCornerVert = vertSel[0]

            cmds.select(rCornerVert, secndVert, r=1)
            # get ordered verts on the edgeLoop
            ordered = cls.orderedVerts_edgeLoop()

            # get up/lo verts
            for v, y in enumerate(ordered):
                if y == lCornerVert:
                    endNum = v + 1

            if lipEye == 'eye':
                if cmds.attributeQuery("upLidVerts", node="lidFactor", exists=1) == False:
                    cmds.addAttr("lidFactor", ln="upLidVerts", dt="stringArray")

                if cmds.attributeQuery("loLidVerts", node="lidFactor", exists=1) == False:
                    cmds.addAttr("lidFactor", ln="loLidVerts", dt="stringArray")

                upVert = ordered[1:endNum - 1]
                loVert = ordered[endNum:]
                cmds.setAttr("lidFactor.upLidVerts", type="stringArray", *([len(upVert)] + upVert))
                cmds.setAttr("lidFactor.loLidVerts", type="stringArray", *([len(loVert)] + loVert))

            elif lipEye == 'lip':
                if cmds.attributeQuery("upLipVerts", node="lipFactor", exists=1) == False:
                    cmds.addAttr("lipFactor", ln="upLipVerts", dt="stringArray")
                if cmds.attributeQuery("loLipVerts", node="lipFactor", exists=1) == False:
                    cmds.addAttr("lipFactor", ln="loLipVerts", dt="stringArray")
                upVert = ordered[:endNum]
                loVert = ordered[endNum - 1:]
                loVert.append(rCornerVert)
                cmds.setAttr("lipFactor.upLipVerts", type="stringArray", *([len(upVert)] + upVert))
                cmds.setAttr("lipFactor.loLipVerts", type="stringArray", *([len(loVert)] + loVert))

        else:
            print
            'select 3 vertices on edge loop!'

    @classmethod
    def upVertSel(cls, LidLip):
        """
        #LidLip = "eye" or "lip"
        """
        if LidLip == "eye":
            LidLip = "lid"

        orderVert = cmds.getAttr(LidLip + "Factor.up" + LidLip.title() + "Verts")
        cmds.select(orderVert)

    @classmethod
    def loVertSel(cls, LidLip):
        if LidLip == "eye":
            LidLip = "lid"
        orderVert = cmds.getAttr(LidLip + "Factor.lo" + LidLip.title() + "Verts")
        cmds.select(orderVert)

    @classmethod
    def getEdgeVertDict(cls, edgeList):
        """
        #make the list of edgeLoop dictionary( { edge: [vert1, vert2]})
        """
        edgeVertDict = {}
        for edge in edgeList:
            cmds.select(edge, r=1)
            cmds.ConvertSelectionToVertices()
            edgeVert = cmds.ls(sl=1, fl=1)
            edgeVertDict[edge] = edgeVert
        return edgeVertDict

    @classmethod
    def orderedVerts_edgeLoop(cls, selection =[]):
        """
        #select 2 adjasent vertices ( corner and direction vertex)
        #list vertexes on edge loop( for curves )
        """
        selection = cmds.ls(os=1, fl=1)
        verts = cmds.filterExpand(selection, sm=31)
        if not len(verts) == 2:
            raise runtimeError('select 2 adjasent vertex!!')

        firstVert = verts[0]
        secondVert = verts[1]

        cmds.select(firstVert, secondVert, r=1)
        mel.eval('ConvertSelectionToContainedEdges')
        firstEdge = cmds.ls(sl=1)[0]

        cmds.polySelectSp(firstEdge, loop=1)
        edges = cmds.ls(sl=1, fl=1)
        edgeDict = cls.getEdgeVertDict(edges)  # {edge: [vert1, vert2], ...}
        ordered = [firstVert, secondVert]
        for i in range(len(edges) - 2):
            del edgeDict[firstEdge]
            # print edgeDict
            for x, y in edgeDict.iteritems():
                if secondVert in y:
                    xVerts = y
                    xVerts.remove(secondVert)
                    firstEdge = x

            secondVert = xVerts[0]
            ordered.append(secondVert)
        return ordered

    @classmethod
    def normalizedCurve(cls, name=None):
        if not name:
            name = 'temporary'
        tmpCrv = pm.curve(d=3, p=([0,0,0],[0.33,0,0],[0.66,0,0],[1,0,0]))
        pm.rebuildCurve(tmpCrv, rt=0, d=3, kr=0, s=2)
        normCrv = tmpCrv.rename(name+"Norm_crv")
        return normCrv

print('sukwon shin')