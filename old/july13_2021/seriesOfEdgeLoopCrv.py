# -*- coding: utf-8 -*-
#선택한 버텍스들을 주황색으로 mark 
def colorVertices():
    vtxSel = cmds.ls(sl=1, fl=1)
    cmds.polyColorPerVertex(vtxSel, r=1, g=0.3, b=0.3, a=1, cdo=1 )




#make the list of edgeLoop dictionary( { edge: [vert1, vert2]}) 
def edgeVertDict(edgeList):
    edgeVertDict = { }
    for edge in edgeList:
        cmds.select(edge, r =1)
        cmds.ConvertSelectionToVertices()
        edgeVert = cmds.ls(sl=1, fl=1)
        edgeVertDict[edge] = edgeVert
    return edgeVertDict


#select 2 adjasent vertices ( corner and direction vertex)
#edge loop상에 있는 버텍스 순서대로 나열한다( for curves )
import maya.mel as mel
def orderedVerts_edgeLoop():
    
    myVert = cmds.ls( os=1, fl=1 )
    if len(myVert)==2:
        firstVert = myVert[0]
        secondVert = myVert[1]
        
        cmds.select (firstVert,secondVert, r =1)
        mel.eval('ConvertSelectionToContainedEdges')        
        firstEdge = cmds.ls( sl=1 )[0]
        
        cmds.polySelectSp( firstEdge, loop =1 )
        edges = cmds.ls( sl=1, fl=1 )
        edgeDict = edgeVertDict(edges) #{edge: [vert1, vert2], ...}
        ordered = [firstVert, secondVert]
        for i in range( len(edges)-2 ):            
            del edgeDict[firstEdge]
            #print edgeDict
            for x, y in edgeDict.iteritems():
                if secondVert in y:                    
                    xVerts = y
                    xVerts.remove(secondVert)
                    firstEdge = x
        
            secondVert = xVerts[0]
            ordered.append( secondVert )
        return ordered
    
    else:
        print 'select 2 adjasent vertex!!'
        
        




#입술 웨이트 맵을 위한 커브 생성(name = ‘eye’, ’lip’)
import maya.cmds as cmds
def curveOnEdgeLoop(name):
    myList = cmds.ls( os=1, fl=1)
    if name == 'lip':
        allJnts = cmds.ls('*LipRoll*_jnt', fl=1 )
    elif name == 'eye':
        allJnts = cmds.ls('l_*LidTx*_jnt', fl=1 )
    allVerts = orderedVerts_edgeLoop()
    if len(allVerts) == len(allJnts):  
        vertsPos = []
        for v in allVerts:
            pos = cmds.xform( v, q =1, ws =1, t =1 )
            vertsPos.append(pos)    
        
        crv = cmds.curve( n= name + 'loftCurve01', d =1, p = vertsPos )
        cmds.closeCurve( crv, ch=0, ps=True, replaceOriginal=1 )
        cmds.toggle( crv, cv=True )








#입술 코너와 디렉션 2 vertices를 선택하고 나머지 코너 버텍스들을 선택한다.
#select corner vertices for ring start
def seriesOfEdgeLoopCrv(name):
    # find the fist vertex for get ordered vert on edge loop
    myList = cmds.ls( os=1, fl=1 )
    edge1Vert = myList[0]
    edge2Vert = myList[1]
    firstVert = myList[2] 
    myVert = [ j for j in myList if j not in [edge1Vert, edge2Vert ]]
    startVerts = [firstVert]
    for i in range( len(myVert)-1):
        cmds.select(firstVert, r=1)
        mel.eval('PolySelectTraverse 1')
        upVerts = cmds.ls(sl=1, fl=1)
        myVert.remove(firstVert)
        for vtx in myVert:        
            if vtx in upVerts:
                firstVert = vtx
                startVerts.append(firstVert)
    startVerts.insert(0, edge1Vert)
    # find the fist vertex for the curve on edgeLoop
    cmds.select (edge1Vert,edge2Vert, r =1)
    mel.eval('ConvertSelectionToContainedEdges')
    firstEdge = cmds.ls(sl=1)[0]
    cmds.polySelectSp( firstEdge, ring =1 )
    ringEdges = cmds.ls(sl=1, fl=1)
    ringEdgeDict = edgeVertDict(ringEdges)
    
    for k in range( len(startVerts)):
        for c, d in ringEdgeDict.iteritems():
            if startVerts[k] in d:
                d.remove(startVerts[k])
                #print startVerts[k], d[0]
                cmds.select( startVerts[k], r=1 ) 
                cmds.select( d[0], add=1 )         
                curveOnEdgeLoop(name)
        
