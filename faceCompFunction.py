# -*- coding: utf-8 -*-
import maya.cmds as cmds
import maya.mel as mel
from maya import OpenMaya
import string
import re
import os
import math
from twitchScript import twitchPanelConnect
from twitchScript import blendShapeMethods
'''
1. store head info ( head name / brow, eye, lip vertices in order )
a. Brow: manually select brow vertices(left side to mirror ) : stored in browFactor
b. Eye or Lip : 먼저 코너 버텍스들를 선택하고 저장한 후, right corner vert 와 direction vert만 선택해서 실행하면 자연히 lCornerVert,rCornerVert,secndVert가 실수 없이 나온다.( to be stored in lid/lipfactor)   

Aug20 swtichJntToCls / curveOnEdgeLoop fix( checking with stored verts not joints ) / eyeMapSkinning fix ( loLidJnts instead loLidJnts[1:-1]) 
'''


#store head info            
def headGeo():
    faceGeo = cmds.ls(sl=1, type = "transform")[0]
    if cmds.attributeQuery("headGeo", node = "helpPanel_grp", exists=1)==False:
        cmds.addAttr( "helpPanel_grp", ln ="headGeo", dt = "string"  )
    cmds.setAttr("helpPanel_grp.headGeo", faceGeo, type= "string"  ) 


#after place all the face locators
def setupLocator():
    helpPanelGroup = "helpPanel_grp"

    if cmds.objExists("faceLoc_grp"):
        tmpChild = cmds.listRelatives( "allPos", ad=1, ni=1, type = ["nurbsCurve", "locator"] )
        itemSet = [ cmds.listRelatives(x, p=1)[0] for x in tmpChild ]
        locSet = set(itemSet)
        for loc in locSet:
            if "Mirr" not in loc:
                pos = cmds.xform( loc, t = True, q = True, ws = True )
                if cmds.attributeQuery( loc, node = helpPanelGroup, exists=1)==False:
                    cmds.addAttr( helpPanelGroup, sn =loc, dt='doubleArray' )
                #store locator world space 
                cmds.setAttr( helpPanelGroup +"." + loc, pos, type="doubleArray")    
    else: 
        cmds.confirmDialog( title='Confirm', message='create faceLoc_grp first!!' )  
    
    
#store brow vertices in browFactor( selection order: center to left !! )
def browVerts():
	myVerts = cmds.ls(os=1, fl=1)
	vts = cmds.filterExpand( ex=True, sm=31 )
	vtxNum = len(vts)
    
	ordered = vertices_distanceOrder( myVerts )

	if cmds.attributeQuery("browVerts", node = "browFactor", exists=1)==False:
		cmds.addAttr( "browFactor", ln ="browVerts", dt = "stringArray"  )
		cmds.setAttr("browFactor.browVerts", type= "stringArray", *([len(ordered)] + ordered))

	else:
		cmds.setAttr("browFactor.browVerts", type= "stringArray", *([len(ordered)] + ordered))
                    


def selectBrowVerts():    
    if cmds.attributeQuery("browVerts", node = "browFactor", exists=1)==True:
        browVtx = cmds.getAttr("browFactor.browVerts")
        cmds.select(cl=1)
        for bv in browVtx:
            cmds.select(bv, add=1)
        
    else:
        print "set brow vertices first!"    
        
        

#select corner loop verts and direction vert (코너 버텍스들를 선택하고 벡터 버텍스 선택)
#the first vert and last vert are on the edge loop!!!( 첫 코너 버텍스와 벡터 버텍스는 edge loop선 상에 있어야 한다)

#seriesOfEdgeLoopCrv 실행하기 위해서는 
#1. edgeVertDict(ringEdges)( 선택된 엣지링을 딕션어리{엣지: 2버텍스} 로 만들어준다 )
#2. 선택된 입가의 버텍스가 포함된 edge ring에 버텍스 2개를 추출해낸다.  
#2. curveOnEdgeLoop ( 순서대로 선택된 버텍스들을 통해 커브를 만들어준다 ) 실행을 위해서는
# a. orderedVerts_edgeLoop 두개의 버텍스를 통해 엣지룹상에 있는 버텍스들을 순서대로 리스트로 만들어준다.
'''
안될 경우 : check the corner vertices and mark them!!!( you will make this mistake ) 
1. symmetry turn on  
2. selected verts are not on the edge loop
3. selectPref( trackSelectionOrder = 0 ) 
'''
def seriesOfEdgeLoopCrv(lipEye ):
    if not cmds.selectPref( q=1, trackSelectionOrder = 1 ):
        cmds.selectPref( c=1, trackSelectionOrder = 1 )
    myList = cmds.ls( os=1, fl=1)
    posVerts = []
    if lipEye == 'eye':
        for v in myList:
            vPos = cmds.xform(v, q=1, ws=1, t=1 )
            if vPos[0]>0:
                posVerts.append(v)
    elif lipEye == 'lip':
        posVerts = myList

    if len(posVerts)<=2:
        print 'check the vertices selection!!'
    
    else:
        firstVert = posVerts[0]#first corner vert 
        secondVert = posVerts[-1]#direction vert on loop 
        posVerts.remove(secondVert)
        startVerts = [firstVert]
        for i in range( len(posVerts) ):
            cmds.select(firstVert, r=1)
            mel.eval('PolySelectTraverse 1')
            upVerts = cmds.ls(sl=1, fl=1)
            posVerts.remove(firstVert)
            for vtx in posVerts:        
                if vtx in upVerts:
                    firstVert = vtx
                    startVerts.append(firstVert)
    
        #find the fist vertex for the curve on edgeLoop
        cmds.select (startVerts[0], secondVert, r =1)
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
                    curveOnEdgeLoop(lipEye)
        




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
        
        



# to make oh, oo, u shapes 
# select 2vertex(center to left) on loop or select vertices in order and shaped curve last 
# match vertices in edeg loop to the shape curves 
'''
1. freeze the reference curve
2. if vertice on edge loop: select center and next left vertex
   if vertice on none loop: manually select in ordrer to match the curve'''
 
def shapeToCurve():
    mySel = cmds.ls(os=1, fl=1 )
    #freeze curve
    targetCrv = mySel[-1]
    cmds.makeIdentity(targetCrv, apply=True, t=1, r=1, s=1, n=0, pn=1)
    targetCrvShape = cmds.listRelatives( targetCrv, c=1, typ = "nurbsCurve" )
    sourceVtx = mySel[:-1]
    numVtx = len(sourceVtx)    
    if numVtx == 2:
    
        cmds.select( sourceVtx[0], sourceVtx[1])
        orderVtx = orderedVerts_edgeLoop()

    elif numVtx > 2:
        orderVtx = sourceVtx       
            
    for i, vtx in enumerate( orderVtx ):
        pos = cmds.xform( vtx, q=1, ws=1, t=1 ) 
        uParam = getUParam ( pos, targetCrv )
        print uParam        
        dnPOC = cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = 'dnPOC'+ str(i+1).zfill(2))
        #loc = cmds.spaceLocator ( n = "targetPoc"+ str(i+1).zfill(2))
        cmds.connectAttr (targetCrvShape[0] + ".worldSpace",  dnPOC + '.inputCurve')
        #cmds.setAttr ( dnPOC + '.turnOnPercentage', 1 )
        cmds.setAttr ( dnPOC + '.parameter', uParam )        
    
        posOnCrv = cmds.getAttr(dnPOC + ".position" )[0]        
        cmds.xform( vtx, ws=1, t= posOnCrv )


#select corner and direction vertex in that order
#입술 웨이트 맵을 위한 커브 생성(name = ‘eye’, ’lip’)
def curveOnEdgeLoop(name):
    myList = cmds.ls( os=1, fl=1)
    allVerts = orderedVerts_edgeLoop()
    if name == "eye":
    	name = "lid"
    		
    # get the stored vertice for "eye" or "lip"
    if cmds.attributeQuery( "lo%sVerts"%name.title(), node = name + "Factor", exists=1 )==True:
    	upVtx = cmds.getAttr( name+ "Factor.up%sVerts"%name.title() )
    	loVtx = cmds.getAttr( name + "Factor.lo%sVerts"%name.title() )
    	numOfJnt = len(upVtx) + len(loVtx)-2
    else:
    	cmds.confirmDialog( title='Confirm', message='Store "%s vertices" first!!'%name.title() )  
    	    
    if numOfJnt == len(allVerts):
        
        vertsPos = []
        for v in allVerts:
            pos = cmds.xform( v, q =1, ws =1, t =1 )
            vertsPos.append(pos)    
        
        crv = cmds.curve( d =1, p = vertsPos )
        cmds.closeCurve( crv, ch=0, ps=True, replaceOriginal=1 )
        crvName = cmds.rename( crv, name + '_loft_crv01' )
        cmds.toggle( crvName, cv=True )
        
    else:
        cmds.confirmDialog( title='Confirm', message='Wrong edgeLoop vertices are selected' )

''' 
1. Edge loop과 같은 갯수의 근접한 edge들 선택
2. Select eyeLip
3. RUN → selected edges들이 helpPanel_grp 에 attr로 저장된다.
4. Selected edges중 첫번째 엣지의 2 버텍스 선택
'''

#manually select edges and store (loop은 아니어도 연결은 되어있어야 한다)
def edgeSelection( eyeLip ):
    # add attribute on helpPanel_grp 
    if cmds.attributeQuery("selected_eyeEdges", node = "helpPanel_grp", exists=1)==False:
        cmds.addAttr( "helpPanel_grp", ln ="selected_eyeEdges", dt = "stringArray"  )
    elif cmds.attributeQuery("selected_lipEdges", node = "helpPanel_grp", exists=1)==False:
        cmds.addAttr( "helpPanel_grp", ln ="selected_lipEdges", dt = "stringArray"  )
    
    edges = cmds.ls(sl=1, fl=1) 
    if eyeLip == 'eye':
        lidJnt = cmds.ls('l_*LidBlink*_jnt', fl=1, type = 'transform')
        numOfJnt = len(lidJnt)
        print "eyeVerts length is " + str(numOfJnt) 
        
    elif eyeLip =='lip':
        lipJnt = cmds.ls('*LipRollP*', fl=1, type = 'transform')
        numOfJnt = len(lipJnt)
        print "lipVerts number is " + str(numOfJnt) 
        
    if numOfJnt == len(edges):
        if eyeLip == 'eye':
            cmds.setAttr( "helpPanel_grp.selected_eyeEdges", type= "stringArray", *([len(edges)] + edges) )
    
        elif eyeLip == 'lip':
            cmds.setAttr( "helpPanel_grp.selected_lipEdges", type= "stringArray", *([len(edges)] + edges) )
    
    else:
        if numOfJnt-len(edges)>0:
            print "select %s more %s edges!!"%(str(numOfJnt-len(edges)), eyeLip )
        elif numOfJnt-len(edges)<0:
            print "select %s less %s edges!!"%(str(numOfJnt-len(edges)), eyeLip )
        
        


#입술 웨이트 맵을 위한 커브 생성(name = ‘eye’, ’lip’)
#저장된 엣지들 불러오기
def curveOnEdgeSelection( eyeLip ):
    #myList = cmds.ls( os=1, fl=1)
    allVerts = orderedVerts_edgeSel( eyeLip )       
        
    vertsPos = []
    for v in allVerts:
        pos = cmds.xform( v, q =1, ws =1, t =1 )
        vertsPos.append(pos)    
    
    crv = cmds.curve( n= eyeLip + 'loftCurve01', d =1, p = vertsPos )
    cmds.closeCurve( crv, ch=0, ps=True, replaceOriginal=1 )
    cmds.toggle( crv, cv=True )


#for curveOnEdgeSelection
#select 2 adjasent vertices ( corner and direction vertex)
#edge loop상에 있는 버텍스 순서대로 나열한다( for curves )
def orderedVerts_edgeSel( eyeLip ):
    edges = cmds.getAttr( "helpPanel_grp.selected_%sEdges"%eyeLip )
    myVert = cmds.ls( os=1, fl=1 )
    if len(myVert)==2:
        firstVert = myVert[0]
        secondVert = myVert[1]
        
        cmds.select (firstVert,secondVert, r =1)
        mel.eval('ConvertSelectionToContainedEdges')        
        firstEdge = cmds.ls( sl=1 )[0]
        
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
        



# make symmetry for none periodic curve( with no deformer ) 
#select the curve and run
def symmetrizeOpenCrv(direction):
    crvSel = cmds.ls(sl=1, fl=1, long=1, type= "transform")
    crvNum = cmds.ls(crvSel[0]+".cv[*]", l=1, fl=1 )
    leng = len(crvNum )
        
    if direction == 1:
        print "left cv to right cv"
        for i in range(leng/2 ):
            xPos = cmds.getAttr(crvNum[leng-i-1]+".xValue" )
            cmds.setAttr( crvNum[i]+".xValue", -xPos)
            yPos = cmds.getAttr(crvNum[leng-i-1]+".yValue" )
            cmds.setAttr( crvNum[i]+".yValue", yPos)
            zPos = cmds.getAttr(crvNum[leng-i-1]+".zValue" )
            cmds.setAttr( crvNum[i]+".zValue", zPos)

    else:
        print "right cv to left cv"
        for i in range(leng/2 ):
            xPos = cmds.getAttr(crvNum[i]+".xValue" )
            cmds.setAttr( crvNum[leng-i-1]+".xValue", -xPos)
            yPos = cmds.getAttr(crvNum[i]+".yValue" )
            cmds.setAttr( crvNum[leng-i-1]+".yValue", yPos)
            zPos = cmds.getAttr(crvNum[i]+".zValue" )
            cmds.setAttr( crvNum[leng-i-1]+".zValue", zPos)
            




# curve should have center cv[ 0, y, z]
def symmetrizeLipCrv(direction):

    crvSel = cmds.ls(sl=1, long=1, type= "transform")
    crvShp = cmds.listRelatives(crvSel[0], c=1, ni=1, s=1)
    
    if len(cmds.ls(crvShp))==1:
    
        periodic = cmds.getAttr( crvShp[0] + '.form' )
        crvCvs= cmds.ls(crvSel[0]+".cv[*]", l=1, fl=1 )
        numCv = len(crvCvs)
        
        numList = [ x for x in range(numCv) ]
        if periodic in [1, 2]:         
            if numCv%2 == 0:
                halfLen = (numCv-2)/2 
                centerCV =[]
                for cv in crvCvs:
                    pos = cmds.xform( cv, q=1, ws=1, t=1 )
                    if pos[0]**2 < 0.0001 :
                        print cv
                        num = cv.split('[')[1][:-1]
                        centerCV.append(int(num))
                
                if len(centerCV) == 2:
                    startNum = centerCV[0]+1
                    endNum = startNum+halfLen
                    halfNum = numList[startNum:endNum]
                    opphalf = numList[endNum+1:] + numList[:centerCV[0]]
                    # curve direction( --> )    
                    if cmds.xform( crvCvs[startNum], q=1, ws=1, t=1)[0]>0:
                        leftNum = halfNum
                        rightNum = opphalf[::-1]
                    # curve direction( <-- )    
                    elif cmds.xform( crvCvs[startNum], q=1, ws=1, t=1)[0]<0:
                        leftNum = opphalf
                        rightNum = halfNum[::-1]
                                
                    print leftNum, rightNum    
                    if direction == True:
                        print "left cv to right cv"
                        for i in range(halfLen):
                            pos = cmds.xform( crvCvs[leftNum[i]], q=1, ws=1, t=1 )
                            cmds.xform( crvCvs[rightNum[i]], ws=1, t=( -pos[0], pos[1], pos[2] ) )
                        
                    else:
                        print "right cv to left cv"
                        for i in range(halfLen):
                            pos = cmds.xform( crvCvs[rightNum[i]], q=1, ws=1, t=1 )
                            cmds.xform( crvCvs[leftNum[i]], ws=1, t=( -pos[0], pos[1], pos[2] ) )                
                else:
                    cmds.confirmDialog( title='Confirm', message='number of CVs( tx=0 :on center ) of curve should be 2!!!' )      
            
        if periodic == 0:
            if numCv%2 == 1:
                halfLen = (numCv-2)/2 
                centerNum = ''
                for cv in crvCvs:
                    pos = cmds.xform( cv, q=1, ws=1, t=1 )
                    if pos[0]**2 < 0.0001 :
                        num = cv.split('[')[1][:-1]
                        centerNum = int(num)
                    
                if centerNum:
                    halfNum = numList[centerNum+1:]
                    opphalf = numList[:centerNum]            
                    # curve direction( --> )    
                    if cmds.xform( crvCvs[centerNum+1], q=1, ws=1, t=1)[0]>0:
                        leftNum = halfNum
                        rightNum = opphalf[::-1]
                    # curve direction( <-- )    
                    elif cmds.xform( crvCvs[centerNum+1], q=1, ws=1, t=1)[0]<0:
                        leftNum = opphalf
                        rightNum = halfNum[::-1]        
                        
                    if direction == 1:
                        print "left cv to right cv"
                        for i in range( halfLen ):
                            pos = cmds.xform( crvCvs[leftNum[i]], q=1, ws=1, t=1 )
                            cmds.xform( crvCvs[rightNum[i]], ws=1, t=( -pos[0], pos[1], pos[2] ) )
                        
                    else:
                        print "right cv to left cv"
                        for i in range(halfLen ):
                            pos = cmds.xform( crvCvs[rightNum[i]], q=1, ws=1, t=1 )
                            cmds.xform( crvCvs[leftNum[i]], ws=1, t=( -pos[0], pos[1], pos[2] ) )

                else:
                    cmds.confirmDialog( title='Confirm', message='position the curve tx on center!!!' ) 

    else:
        cmds.confirmDialog( title='Confirm', message='more than 1 "%s" matches name!!'%crvShp[0] )
                

 
       
   
    
#select lower curve to high curve for brow map surf
#select outer curve to inner curve for mouth and eye surf
def loftFacePart( facePart ):
    crvSel = cmds.ls( os=1, fl=1, type = 'transform')
    name = facePart + 'Tip_map'
        
    loft_suf = cmds.loft( crvSel, n = name, ch =1, u=1, c=0, ar= 1, d=1, ss= 1, rn= 1, po= 1, rsn = 1  )
    suf_inputs = cmds.listHistory( loft_suf[0] )
    tessel = [ x for x in suf_inputs if cmds.nodeType(x) == 'nurbsTessellate']
    cmds.setAttr (tessel[0]+".format", 3 )




#select corner verts and direction vert on loop 
# return up/low ordered vertices for lipEye ('lip' or 'eye')
# 나중에 개선: 먼저 코너 버텍스들를 선택하고 저장한 후, right corner vert 와 direction vert만 선택해서 실행하면 자연히 lCornerVert,rCornerVert,secndVert가 실수 없이 나온다.   
def orderedVert_upLo(lipEye):

    orderSel= cmds.selectPref( trackSelectionOrder=True, q=1 )
    if orderSel ==False:
        cmds.confirmDialog( title='Confirm', message='turn on "trackSelectionOrder" in Pref!!!' )
        
    mySel = cmds.ls(os=1, fl=1)
    vertSel = []
    if lipEye == 'eye':
        #remove any vertices if they are on minus side
		for v in mySel:
			vPos = cmds.xform(v, q=1, ws=1, t=1 )
			if vPos[0]>0:
				vertSel.append(v)
		eyeLidGeo = mySel[0].split(".")[0]
		if not eyeLidGeo == cmds.getAttr("helpPanel_grp.headGeo"):
			if cmds.attributeQuery("eyelidGeo", node = "lidFactor", exists=1)==False:   
				cmds.addAttr( "lidFactor", ln ="eyelidGeo", dt = "string"  )
				cmds.setAttr("lidFactor.eyelidGeo", eyeLidGeo, type= "string" )
			 
    elif lipEye == 'lip':
		if len(mySel) == 2:
			#mirror selection
			if cmds.attributeQuery("headGeo", node = "helpPanel_grp", exists=1) ==1:
				   
				vtx =cmds.ls( os=1, fl=1 )
				polyHead = cmds.getAttr("helpPanel_grp.headGeo")
				shpSel = cmds.listRelatives( polyHead, c=1, typ = "shape" )
				cpmNode = cmds.createNode("closestPointOnMesh")
				cmds.connectAttr( shpSel[0] + ".outMesh", cpmNode + ".inMesh" )

				vtxPos = cmds.xform( mySel[0], q=1, t=1, ws=1)
				cmds.setAttr( cpmNode + ".inPosition", -vtxPos[0], vtxPos[1], vtxPos[2], type = "double3" )
				vtxInx = cmds.getAttr( cpmNode + ".closestVertexIndex")
				mrrV = polyHead+".vtx[%s]"%vtxInx
				mySel.insert(1, mrrV)
				vertSel = mySel

		elif len(mySel) == 3:
			vertSel = mySel
    else:
        cmds.warning( "select at least 2 vertices ")
						
    
    if len(vertSel) == 3:
        vertPosDict = {}
        for vt in vertSel:
            vertPos = cmds.xform( vt, q =1, ws =1, t=1 )        
            vertPosDict[vt] = vertPos 
        
        xMaxPos = max(vertPosDict[vertSel[0]][0], vertPosDict[vertSel[1]][0], vertPosDict[vertSel[2]][0])
        for j, x in vertPosDict.items():
            if x[0] == xMaxPos:
                lCornerVert = j
        vertPosDict.pop(lCornerVert)
        vertSel.remove(lCornerVert)

        yMaxPos = max(vertPosDict[vertSel[0]][1], vertPosDict[vertSel[1]][1] )
        for i, y in vertPosDict.items():
            if y[1] == yMaxPos:
                secndVert = i
        
        vertSel.remove(secndVert)
        
        rCornerVert = vertSel[0]        
        cmds.select ( rCornerVert, secndVert, r=1)       
        # get ordered verts on the edgeLoop
        ordered = orderedVerts_edgeLoop()
        
        # get up/lo verts    
        for v, y in enumerate(ordered):
            if y == lCornerVert:
                endNum = v+1   
                
        if lipEye == 'eye':
            if cmds.attributeQuery("cornerVerts", node = "lidFactor", exists=1)==False:            
                cmds.addAttr( "lidFactor", ln ="cornerVerts", dt = "stringArray"  )
                
            if cmds.attributeQuery("upLidVerts", node = "lidFactor", exists=1)==False:
                cmds.addAttr( "lidFactor", ln ="upLidVerts", dt = "stringArray"  )
            
            if cmds.attributeQuery("loLidVerts", node = "lidFactor", exists=1)==False:            
                cmds.addAttr( "lidFactor", ln ="loLidVerts", dt = "stringArray"  )
            
            upVert = ordered[1:endNum-1]
            loVert = ordered[endNum:][::-1]
            cmds.setAttr("lidFactor.cornerVerts", 2, rCornerVert,lCornerVert, type= "stringArray" )
            cmds.setAttr("lidFactor.upLidVerts", type= "stringArray", *([len(upVert)] + upVert) )
            cmds.setAttr("lidFactor.loLidVerts", type= "stringArray", *([len(loVert)] + loVert) )
            
        elif lipEye == 'lip':
            if cmds.attributeQuery("upLipVerts", node = "lipFactor", exists=1)==False:
                cmds.addAttr( "lipFactor", ln ="upLipVerts", dt = "stringArray"  )
            if cmds.attributeQuery("loLipVerts", node = "lipFactor", exists=1)==False:
                cmds.addAttr( "lipFactor", ln ="loLipVerts", dt = "stringArray"  )
            upVert = ordered[:endNum]
            loVert = ordered[endNum-1:][::-1]
            loVert.append(rCornerVert)
            cmds.setAttr("lipFactor.upLipVerts", type= "stringArray", *([len(upVert)] + upVert) )
            cmds.setAttr("lipFactor.loLipVerts", type= "stringArray", *([len(loVert)] + loVert) )

    else:
        print 'select 3 vertices on edge loop!'


# select corner verts and directional verts
def rnkOrderedVert_upLo(lipEye):
    
    #selection ordrer not matter( extract lVert using xform )
    orderSel= cmds.selectPref( trackSelectionOrder=True, q=1 )
    if orderSel ==False:
        cmds.confirmDialog( title='Confirm', message='turn on "trackSelectionOrder" in Pref!!!' )
        
    mySel = cmds.ls(os=1, fl=1)
    vertSel = []
    if lipEye == 'eye':
        #remove any vertices if they are on minus side
		for v in mySel:
			vPos = cmds.xform(v, q=1, ws=1, t=1 )
			if vPos[0]>0:
				vertSel.append(v)
		eyeLidGeo = mySel[0].split(".")[0]
		if cmds.attributeQuery("eyelidGeo", node = "lidFactor", exists=1)==False:  
			cmds.addAttr( "lidFactor", ln = "eyelidGeo", dt = "string"  )
			cmds.setAttr("lidFactor.eyelidGeo", eyeLidGeo, type= "string" ) 
    else:
        vertSel = mySel
        
    if len(vertSel) == 3:
        vertPosDict = {}
        for vt in vertSel:
            vertPos = cmds.xform( vt, q =1, ws =1, t=1 )        
            vertPosDict[vt] = vertPos 
        
        xMaxPos = max(vertPosDict[vertSel[0]][0], vertPosDict[vertSel[1]][0], vertPosDict[vertSel[2]][0])
        for j, x in vertPosDict.items():
            if x[0] == xMaxPos:
                lCornerVert = j
        vertPosDict.pop(lCornerVert)
        vertSel.remove(lCornerVert)

        yMaxPos = max(vertPosDict[vertSel[0]][1], vertPosDict[vertSel[1]][1] )
        for i, y in vertPosDict.items():
            if y[1] == yMaxPos:
                secndVert = i
        
        vertSel.remove(secndVert)
        
        rCornerVert = vertSel[0]        
        cmds.select ( rCornerVert, secndVert, r=1 )       
        # get ordered verts on the edgeLoop
        ordered = orderedVerts_edgeLoop()
        
        # get up/lo verts
        endNum = 0       
        for v, y in enumerate(ordered):
            # find the last vertex of the upper lid Vertice 
            if y == lCornerVert:
                endNum = v+1
        if endNum == 0:
            cmds.warning(" 3 vertices are not on the edge loop")
            
        else:        
            if lipEye == 'eye':
                if cmds.attributeQuery("cornerVerts", node = "lidFactor", exists=1)==False:            
                    cmds.addAttr( "lidFactor", ln ="cornerVerts", dt = "stringArray"  )
                    
                if cmds.attributeQuery("upLidVerts", node = "lidFactor", exists=1)==False:
                    cmds.addAttr( "lidFactor", ln ="upLidVerts", dt = "stringArray"  )
                
                if cmds.attributeQuery("loLidVerts", node = "lidFactor", exists=1)==False:            
                    cmds.addAttr( "lidFactor", ln ="loLidVerts", dt = "stringArray"  )
                
                upVert = ordered[0:endNum]
                loVert = ordered[endNum-1:][::-1]
                loVert.insert(0, rCornerVert)
                cmds.setAttr("lidFactor.cornerVerts", 2, rCornerVert,lCornerVert, type= "stringArray" )
                cmds.setAttr("lidFactor.upLidVerts", type= "stringArray", *([len(upVert)] + upVert) )
                cmds.setAttr("lidFactor.loLidVerts", type= "stringArray", *([len(loVert)] + loVert) )
                
            elif lipEye == 'lip':
                if cmds.attributeQuery("upLipVerts", node = "lipFactor", exists=1)==False:
                    cmds.addAttr( "lipFactor", ln ="upLipVerts", dt = "stringArray"  )
                if cmds.attributeQuery("loLipVerts", node = "lipFactor", exists=1)==False:
                    cmds.addAttr( "lipFactor", ln ="loLipVerts", dt = "stringArray"  )
                upVert = ordered[:endNum]
                loVert = ordered[endNum-1:][::-1]
                loVert.insert(0, rCornerVert)
                cmds.setAttr("lipFactor.upLipVerts", type= "stringArray", *([len(upVert)] + upVert) )
                cmds.setAttr("lipFactor.loLipVerts", type= "stringArray", *([len(loVert)] + loVert) )

    else:
        print 'select 3 vertices on edge loop!'



#LidLip = "eye" or "lip"
def upVertSel( LidLip ):
    if LidLip =="eye":
        LidLip ="lid"
        
    orderVert = cmds.getAttr( LidLip+"Factor.up" + LidLip.title()+"Verts")
    cmds.select(cl=1)
    for v in orderVert:
    	cmds.select( v, add=1 )


def loVertSel( LidLip ):
    if LidLip =="eye":
        LidLip ="lid"    
    orderVert = cmds.getAttr( LidLip+"Factor.lo" + LidLip.title()+"Verts")
    cmds.select(cl=1)
    for v in orderVert:
    	cmds.select( v, add=1 )


#create brow joints( up: browBase_jnt[browUp_cls weight]/ down: browDown_jnt and browWide_jnt[ browDwn_cls weight] / leftRight: browRotY_jnt[ browDwn_cls weight ] / bulge : browTZ_jnt [browTZ_cls weight])
def browJoints_old():
    browRotXPos = cmds.xform( 'rotXPivot', t = True, q = True, ws = True )
    browRotYPos = cmds.xform( 'rotYPivot', t = True, q = True, ws = True )
        
    #reorder the vertices in selection list  
    orderedVerts = cmds.getAttr( "browFactor.browVerts" )

    if not cmds.objExists("eyebrowJnt_grp"):
        cmds.group( em=True, name='eyebrowJnt_grp', p= "faceMain|jnt_grp" )
    
    cmds.select(cl = True )
    index = 1
    for x in orderedVerts:
        vertPos = cmds.xform(x, t = True, q = True, ws = True)
        
        if ( math.pow(vertPos[0], 2 ) <= 0.01):
            
            baseCntJnt = cmds.joint(n = 'c_browBase'+ str(index).zfill(2)+'_jnt', p = [ 0, browRotXPos[1], browRotXPos[2]])
            downCntJnt = cmds.joint(n = 'c_browDown'+ str(index).zfill(2)+'_jnt', p = [ 0, browRotXPos[1], browRotXPos[2]])
            #cmds.parent(downCntJnt, baseCntJnt )  
            ryCntJnt = cmds.joint(n = 'c_browRotY_jnt', p = [ 0, browRotYPos[1], browRotYPos[2]])           
            parentCntJnt = cmds.joint(n = 'c_browP'+ str(index).zfill(2)+'_jnt', p = vertPos )
            cmds.setAttr ( baseCntJnt+'.rotateOrder', 2)
            cmds.joint(n = 'c_brow'+ str(index).zfill(2), p = vertPos)
            cmds.joint( parentCntJnt, e=1, oj= 'zyx', secondaryAxisOrient = 'yup', ch=1,  zso=1)
            cmds.select(cl = True)
            cmds.parent ( baseCntJnt, "eyebrowJnt_grp")
        else:
    
            baseJnt = cmds.joint(n = 'l_browBase' + str(index).zfill(2)+'_jnt', p = browRotXPos )
            setBrowLabel(baseJnt)
            downBaseJnt = cmds.joint(n = 'l_browDown' + str(index).zfill(2)+ '_jnt', p = browRotXPos )
            #cmds.parent(downBaseJnt, baseJnt )
            ryJnt = cmds.joint(n = 'l_browRotY' + str(index).zfill(2)+ '_jnt', p = browRotYPos ) 
            setBrowLabel(ryJnt)
            parentJnt = cmds.joint(n = 'l_browP' + str(index).zfill(2)+ '_jnt', p = vertPos)
            cmds.setAttr ( baseJnt+'.rotateOrder', 2)
            cmds.joint(n = 'l_brow' + str(index).zfill(2) + '_jnt', p = vertPos)
            cmds.select(cl = True)
            cmds.parent ( baseJnt, "eyebrowJnt_grp" )
            print parentJnt
            cmds.joint( parentJnt, e=1, oj= 'zyx', secondaryAxisOrient = 'yup', ch=1,  zso=1 )

            mirrBase = cmds.mirrorJoint ( baseJnt, mirrorYZ= True, mirrorBehavior=1, searchReplace=('l', 'r'))
            print mirrBase
            setBrowLabel(mirrBase[0])
            setBrowLabel(mirrBase[2])
            cmds.select(cl = True)
            index = index + 1    
    
    #browDetailCtls()   


    
def browJoints():
    
    eyeRotY = cmds.getAttr ('lEyePos.ry' )
    eyeRotZ = cmds.getAttr ('lEyePos.rz' )
    browRotXPos = cmds.xform( 'rotXPivot', t = True, q = True, ws = True )
    browRotYPos = cmds.xform( 'rotYPivot', t = True, q = True, ws = True )

    if not cmds.objExists("browJnt_grp"):
        browGrp = cmds.group( em=True, name='browJnt_grp', p= "faceMain|jnt_grp" )
    else:
        browGrp = "browJnt_grp"
        
    lBrowGrp = cmds.group ( n = 'l_BrowP_grp', em =True, p = browGrp )
    cmds.xform( lBrowGrp, ws=1, t = browRotXPos )
    cmds.setAttr( lBrowGrp + ".rotateOrder", 3 )
    cmds.setAttr ( lBrowGrp + '.ry', eyeRotY )
    #lBrowJntP = cmds.joint(n = 'lBrowP_jnt' )

    rBrowGrp = cmds.group ( n = 'r_BrowP_grp', em =True, p = browGrp )
    cmds.xform( rBrowGrp, ws=1, t = [-browRotXPos[0], browRotXPos[1], browRotXPos[2]] )
    cmds.setAttr( rBrowGrp + ".rotateOrder", 3 )
    cmds.setAttr ( rBrowGrp + '.ry', -eyeRotY )
    
    #reorder the vertices in selection list  
    orderedVerts = cmds.getAttr( "browFactor.browVerts" )
    cmds.select(cl = True )
    index = 1
    for x in orderedVerts:
        vertPos = cmds.xform(x, t = True, q = True, ws = True)
        
        if ( math.pow(vertPos[0], 2 ) <= 0.01):
            
            baseCntJnt = cmds.joint(n = 'c_browBase'+ str(index).zfill(2)+'_jnt', p = [ 0, browRotXPos[1], browRotXPos[2]])
            downCntJnt = cmds.joint(n = 'c_browDown'+ str(index).zfill(2)+'_jnt', p = [ 0, browRotXPos[1], browRotXPos[2]])
            #cmds.parent(downCntJnt, baseCntJnt )  
            ryCntJnt = cmds.joint(n = 'c_browRotY_jnt', p = [ 0, browRotYPos[1], browRotYPos[2]])           
            parentCntJnt = cmds.joint(n = 'c_browP'+ str(index).zfill(2)+'_jnt', p = vertPos )
            cmds.setAttr ( baseCntJnt+'.rotateOrder', 2)
            cmds.joint(n = 'c_brow'+ str(index).zfill(2), p = vertPos)
            #cmds.joint( parentCntJnt, e=1, oj= 'zyx', secondaryAxisOrient = 'yup', ch=1,  zso=1)
            cmds.select(cl = True)
            cmds.parent ( baseCntJnt, browGrp )
        else:
    
            cmds.select(lBrowGrp)
            baseJnt = cmds.joint(n = 'l_browBase' + str(index).zfill(2)+'_jnt', p = browRotXPos )
            setBrowLabel(baseJnt)
            downBaseJnt = cmds.joint(n = 'l_browDown' + str(index).zfill(2)+ '_jnt', p = browRotXPos )
            #cmds.parent(downBaseJnt, baseJnt )
            ryJnt = cmds.joint(n = 'l_browRotY' + str(index).zfill(2)+ '_jnt', p = browRotYPos ) 
            setBrowLabel(ryJnt)
            parentJnt = cmds.joint(n = 'l_browP' + str(index).zfill(2)+ '_jnt', p = vertPos)
            cmds.setAttr ( baseJnt+'.rotateOrder', 2)
            cmds.joint(n = 'l_brow' + str(index).zfill(2) + '_jnt', p = vertPos)
            cmds.select(cl = True)
            #cmds.parent ( lBrowJntP, "eyebrowJnt_grp" )
            #cmds.joint( parentJnt, e=1, oj= 'zyx', secondaryAxisOrient = 'yup', ch=1,  zso=1 )

            mirrBase = cmds.mirrorJoint ( baseJnt, mirrorYZ= True, mirrorBehavior=1, searchReplace=('l', 'r'))
            print mirrBase #['r_browBase01_jnt', 'r_browDown01_jnt', 'r_browRotY01_jnt', 'r_browP01_jnt', 'r_brow01_jnt']
            setBrowLabel(mirrBase[0])
            setBrowLabel(mirrBase[2])
            cmds.setAttr(mirrBase[3]+ '.rx', 180 )
            cmds.parent( mirrBase[0], rBrowGrp )
            cmds.select(cl = True)
            index = index + 1 

            
   
            
def setBrowLabel(jnt):
    label = jnt.split("_")[1]
    if "c_" == jnt[:2]:
        cmds.setAttr(jnt + '.side', 0)
    elif "l_" == jnt[:2]:
        cmds.setAttr(jnt + '.side', 1)
    elif "r_" == jnt[:2]:
        cmds.setAttr(jnt + '.side', 2)    
        
    cmds.setAttr(jnt + '.type', 18)
    
    cmds.setAttr(jnt + '.otherType', label, type = "string")


def attachCrvs( crvSel ):

    cmds.attachCurve( crvSel, ch=1, replaceOriginal=0, keepMultipleKnots =0, method=1, blendBias=0.5, blendKnotInsertion=0, parameter=0.1 ) 




'''
#main/ dtail_ctls on brow_guide_Crv        
def connectBrowCtrls ( numOfCtl, size, offset, crv, browCtl ):
       
    jnts = cmds.ls ( '*browBase*_jnt', fl = True, type ='joint') 
    jntNum = len(jnts)
    jnts.sort()
    z = [ jnts[0] ] #center joints
    y = jnts[1:jntNum/2+1] #left joints
    jnts.reverse()
    x = jnts[:jntNum/2] #right joints
    orderJnts = x + z + y
    #poc node on ctl_crv
    dtailPoc = pocEvenOnCrv( crv, jntNum, "browDtail" )    
    
    #revese 'faceFactors.browRotateX_scale' 
    reverseMult = cmds.shadingNode ( 'multiplyDivide', asUtility=True, n = 'browReverse_mult' )
    cmds.connectAttr( 'browFactor.browUp_scale', reverseMult + ".input1X")
    cmds.connectAttr( 'browFactor.browUp_scale', reverseMult + ".input1Z")
    cmds.connectAttr ( 'browFactor.browRotateY_scale', reverseMult + '.input1Y' )
    cmds.setAttr( reverseMult + ".input2", -1,-1,-1 )
   
    if cmds.objExists("browDtailCtl_grp"):
        cmds.delete("browDtailCtl_grp")
        
    browCtlGrp = cmds.group ( n = "browDtailCtl_grp", em =True, p = "faceMain|ctl_grp|browCtl_grp" )    
    browCrvGrp = cmds.group ( n = "browCrv_grp", em =True, p = "faceMain|crv_grp" ) 
    tempBrowCrv = cmds.curve ( d = 1, p =([-1,0,0],[-0.5,0,0],[0,0,0],[0.5,0,0],[1,0,0]) ) 
    cmds.rebuildCurve ( tempBrowCrv, rebuildType = 0, spans = 10, keepRange = 0, degree = 3 )    
    browCrv = cmds.rename (tempBrowCrv, 'brow_crv')    
    browCrvShape = cmds.listRelatives ( browCrv, c = True )
    cmds.parent ( browCrv, "browCrv_grp")

    # lipTarget curve shape
    lBrowSadCrv = cmds.duplicate ( browCrv, n= 'l_BrowSad_crv')
    rBrowSadCrv = cmds.duplicate ( browCrv, n= 'r_BrowSad_crv')
    lBrowMadCrv = cmds.duplicate ( browCrv, n= 'l_BrowMad_crv')
    rBrowMadCrv = cmds.duplicate ( browCrv, n= 'r_BrowMad_crv')
    lFurrowCrv = cmds.duplicate ( browCrv, n= 'l_Furrow_crv')
    rFurrowCrv = cmds.duplicate ( browCrv, n= 'r_Furrow_crv')
    lRelaxCrv = cmds.duplicate ( browCrv, n= 'l_Relax_crv')
    rRelaxCrv = cmds.duplicate ( browCrv, n= 'r_Relax_crv')      
    lCrv = [lBrowSadCrv[0], lBrowMadCrv[0], lFurrowCrv[0], lRelaxCrv[0] ]    
    rCrv = [rBrowSadCrv[0], rBrowMadCrv[0], rFurrowCrv[0], rRelaxCrv[0] ]        
    crvLen = len(lCrv)
    
    browBS = cmds.blendShape ( lBrowSadCrv[0],rBrowSadCrv[0], lBrowMadCrv[0],rBrowMadCrv[0], lFurrowCrv[0],rFurrowCrv[0], lRelaxCrv[0],rRelaxCrv[0], browCrv, n ='browBS')
    cmds.blendShape( browBS[0], edit=True, w=[(0, 1), (1, 1), (2, 1), (3,1),(4, 1), (5,1),(6, 1), (7,1) ])  
    LRBlendShapeWeight( browCrv, browBS[0] )
    
    tempCtlCrv = cmds.curve ( d = 1, p =([-1,0,0],[-0.5,0,0],[0,0,0],[0.5,0,0],[1,0,0]) )
    browCtlCrv = cmds.rename (tempCtlCrv, 'browCtrlCrv' ) 
    cmds.rebuildCurve (browCtlCrv, rebuildType = 0, spans = numOfCtl-1, keepRange = 0, degree = 3 ) 
    browCtlCrvShape = cmds.listRelatives ( browCtlCrv, c = True ) 
    cmds.parent ( browCtlCrv, "browCrv_grp") 
    
    #connect browMain Ctrls to browCrv
    centerNum = (numOfCtl+1)/2
    strs = string.ascii_uppercase
    lf=[]
    rt=[]
    for i in range(1, centerNum):
        rName= "R"+ strs[centerNum-i]
        lName= "L"+ strs[i]
        rt.append(rName)
        lf.append(lName)    
    sequence = rt+["A"]+lf
    cvs= cmds.ls("browCtrlCrv.cv[*]", fl=True )
    
    for num in range (len(cvs)):            
        #erase double transform
        cvXVal = cmds.getAttr( cvs[num] + '.xValue' )
        if num == centerNum:
       
            cmds.connectAttr ('brow_arc' + sequence[num-1] + '.ty', cvs[num] + '.yValue' )            
            cmds.connectAttr ('brow_arc' + sequence[num-1] + '.tz',  cvs[num] + '.zValue' )
                    
        elif num == 0 :
            #erase cv's tx value
            sumX = cmds.shadingNode ( 'addDoubleLinear', asUtility =True, n = 'browTX_sum'+ str(num)+'Corner' )            
            cmds.connectAttr ( 'brow_arc%s.tx'%(sequence[num]), sumX + '.input1' )
            cmds.setAttr ( sumX + '.input2', cvXVal )
            
            cmds.connectAttr ( sumX + '.output', cvs[num] + '.xValue' )
            
            cmds.connectAttr ('brow_arc' + sequence[num] + '.ty', cvs[num] + '.yValue' )

            cmds.connectAttr ('brow_arc' + sequence[num] + '.tz', cvs[num] + '.zValue' )        

        elif num == len(cvs)-1:

            #erase cv's tx value
            sumX = cmds.shadingNode ( 'addDoubleLinear', asUtility =True, n = 'browTX_sum'+ str(num)+'Corner' )            
            cmds.connectAttr ( 'brow_arc%s.tx'%(sequence[num-2]), sumX + '.input1' )
            cmds.setAttr ( sumX + '.input2', cvXVal )
            
            cmds.connectAttr ( sumX + '.output', cvs[num] + '.xValue' )
            
            cmds.connectAttr ('brow_arc' + sequence[num-2] + '.ty', cvs[num] + '.yValue' )

            cmds.connectAttr ('brow_arc' + sequence[num-2] + '.tz', cvs[num] + '.zValue' ) 
            
        else:                
            print num-1
            #erase cv's tx value
            sumX = cmds.shadingNode ( 'addDoubleLinear', asUtility =True, n = 'browTX_sum'+ str(num) )            
            cmds.connectAttr ( 'brow_arc%s.tx'%(sequence[num-1]), sumX + '.input1' )
            cmds.setAttr ( sumX + '.input2', cvXVal )
            
            cmds.connectAttr ( sumX + '.output', cvs[num] + '.xValue' )
            
            cmds.connectAttr ('brow_arc' + sequence[num-1] + '.ty', cvs[num] + '.yValue' )

            cmds.connectAttr ('brow_arc' + sequence[num-1] + '.tz', cvs[num] + '.zValue' )
                   
    increment = 1.0/(jntNum-1)
    index = 0 
    for i, jnt in enumerate(orderJnts):
        basePos = cmds.xform( jnt, t = True, q = True, ws = True)
        print jnt
        browJntList = cmds.listRelatives ( jnt, c=True, ad =1 )
        rotYJnt = browJntList[2]
        rotYJntPos = cmds.xform( rotYJnt, t = True, q = True, ws = True)  
        tzJnt = browJntList[0]
        jntPos = cmds.xform( tzJnt, t = True, q = True, ws = True )
        browNames = jnt.replace("Base","Detail" )
        
        #point on shapeCrv l_browDetail01  l_browBase01_jnt c_browDetail01_jnt
        shapePOC = cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = 'browShapePOC'+ str(index+1).zfill(2))
        cmds.connectAttr ( browCrvShape[0] + ".worldSpace",  shapePOC + '.inputCurve')
        cmds.setAttr ( shapePOC + '.turnOnPercentage', 1 )                
        cmds.setAttr ( shapePOC + '.parameter', increment *index )
        #point on freeform crv
        POC = cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = 'eyeBrowPOC'+ str(index+1).zfill(2))
        cmds.connectAttr ( browCtlCrvShape[0] + ".worldSpace",  POC + '.inputCurve')
        cmds.setAttr ( POC + '.turnOnPercentage', 1 )
        cmds.setAttr ( POC + '.parameter', increment *index )
        # browCrv controls browDetail parent 
        
        attrs = ["rx", "ry", "v"]        

        if jnt in x : #right joints           
            
            #detail ctrl on Face
            rBrowCtrl = arcController( tzJnt.replace("_jnt", "_ctl"), ( jntPos[0], jntPos[1], jntPos[2]+ offset), size/2, 'sq' )
            ctlP = rBrowCtrl[1]

            cmds.setAttr (rBrowCtrl[0] + ".overrideColor", 3 )
            zeroGrp = cmds.duplicate(ctlP, po =1, n = ctlP.replace("_ctlP","_dummy") )
            #up/down reverse for mirror joint
            cmds.setAttr( browJntList[1]+".rx", 180 )            
            cmds.parent(ctlP, zeroGrp[0] )
            cmds.setAttr (ctlP + ".tz", offset )
            cmds.parent( zeroGrp[0], browCtlGrp )
            for att in attrs:            
                cmds.setAttr ( rBrowCtrl[0] + ".%s"%att, lock =1, keyable = 0)
            
            cmds.connectAttr(dtailPoc[i]+".position", zeroGrp[0] + ".t" )                        
            browCrvCtlToJnt( rBrowCtrl[0], jnt, browJntList,  shapePOC, POC, index )
        
        elif jnt in y : #left joints
        
            #detail ctrl on Face
            lBrowCtrl = arcController( tzJnt.replace("_jnt", "_ctl"), ( jntPos[0], jntPos[1], jntPos[2]), size/2, 'sq' ) 
            ctlP = lBrowCtrl[1]

            cmds.setAttr (lBrowCtrl[0] + ".overrideColor", 3 )
            zeroGrp = cmds.duplicate(ctlP, po =1, n = ctlP.replace("_ctlP","_dummy") )
            cmds.parent( ctlP, zeroGrp[0] )
            cmds.setAttr (ctlP + ".tz", offset )
            cmds.parent( zeroGrp[0], browCtlGrp )
            for att in attrs:            
                cmds.setAttr ( lBrowCtrl[0] + ".%s"%att, lock =1, keyable = 0)
            
            cmds.connectAttr(dtailPoc[i]+".position", zeroGrp[0] + ".t" )
            browCrvCtlToJnt (lBrowCtrl[0], jnt, browJntList,  shapePOC, POC, index  )
            
        elif jnt == z[0]:
        
            #detail ctrl on Face
            centerBrowCtrl = arcController( 'c_brow_ctl', ( jntPos[0], jntPos[1], jntPos[2]+ offset), size/2, 'sq' )
            ctlP = centerBrowCtrl[1]
          
            cmds.setAttr (centerBrowCtrl[0] + ".overrideColor", 1 )
            zeroGrp = cmds.duplicate(ctlP, po =1, n = ctlP.replace("_ctlP","_dummy") )
            cmds.parent( ctlP, zeroGrp[0] )
            cmds.setAttr (ctlP + ".tz", offset )
            cmds.parent( zeroGrp[0], browCtlGrp )
            for att in attrs:            
                cmds.setAttr ( centerBrowCtrl[0] + ".%s"%att, lock =1, keyable = 0 )
            
            cmds.connectAttr(dtailPoc[i]+".position", zeroGrp[0] + ".t" )    
            browCrvCtlToJnt ( centerBrowCtrl[0], jnt, browJntList, shapePOC, POC, index )
            
        index = index + 1'''

def connectBrowCtrls ( numOfCtl, size, offset, crv ):
       
    jnts = cmds.ls ( '*browBase*_jnt', fl = True, type ='joint') 
    jntNum = len(jnts)
    jnts.sort()
    if 'c_browBase' in jnts[0]: 
        z = [ jnts[0] ] #center joints
        y = jnts[1:jntNum/2+1] #left joints
        jnts.reverse()
        x = jnts[:jntNum/2] #right joints
        orderJnts = x + z + y
    else:
        y = jnts[0:jntNum/2] #left joints
        jnts.reverse()
        x = jnts[:jntNum/2] #right joints
        orderJnts = x + y 
    print len(orderJnts)
    
    #revese 'faceFactors.browRotateX_scale' 
    reverseMult = cmds.shadingNode ( 'multiplyDivide', asUtility=True, n = 'browReverse_mult' )
    cmds.connectAttr( 'browFactor.browUp_scale', reverseMult + ".input1X", f=1)
    cmds.connectAttr( 'browFactor.browUp_scale', reverseMult + ".input1Z", f=1)
    cmds.connectAttr ( 'browFactor.browRotateY_scale', reverseMult + '.input1Y', f=1 )
    cmds.setAttr( reverseMult + ".input2", -1,-1,-1 )
    if cmds.listConnections(reverseMult + ".input1X", s=1, d=0):
        print "reverse mult connected"
   
    if cmds.objExists("browCrv_grp"):
        cmds.delete("browCrv_grp")        
    if not cmds.objExists("attachCtl_grp"):
        attachCtlGrp = cmds.group ( n = "attachCtl_grp", em =True, p = "faceMain|spn|headSkel|bodyHeadTRSP|bodyHeadTRS|" ) 
    if cmds.objExists("browDtailCtl_grp"):
        cmds.delete("browDtailCtl_grp")
        
    browCtlGrp = cmds.group ( n = "browDtailCtl_grp", em =True, p = "faceMain|spn|headSkel|bodyHeadTRSP|bodyHeadTRS|attachCtl_grp" )    
    browCrvGrp = cmds.group ( n = "browCrv_grp", em =True, p = "faceMain|crv_grp" ) 
    tempBrowCrv = cmds.curve ( d = 1, p =([-1,0,0],[-0.5,0,0],[0,0,0],[0.5,0,0],[1,0,0]) ) 
    cmds.rebuildCurve ( tempBrowCrv, rebuildType = 0, spans = 10, keepRange = 0, degree = 3 )    
    browCrv = cmds.rename (tempBrowCrv, 'brow_crv')    
    browCrvShape = cmds.listRelatives ( browCrv, c = True )
    cmds.parent ( browCrv, "browCrv_grp")

    # lipTarget curve shape
    lBrowSadCrv = cmds.duplicate ( browCrv, n= 'l_BrowSad_crv')
    rBrowSadCrv = cmds.duplicate ( browCrv, n= 'r_BrowSad_crv')
    lBrowMadCrv = cmds.duplicate ( browCrv, n= 'l_BrowMad_crv')
    rBrowMadCrv = cmds.duplicate ( browCrv, n= 'r_BrowMad_crv')
    lFurrowCrv = cmds.duplicate ( browCrv, n= 'l_Furrow_crv')
    rFurrowCrv = cmds.duplicate ( browCrv, n= 'r_Furrow_crv')
    lRelaxCrv = cmds.duplicate ( browCrv, n= 'l_Relax_crv')
    rRelaxCrv = cmds.duplicate ( browCrv, n= 'r_Relax_crv')
    lBrowUpCrv = cmds.duplicate ( browCrv, n= 'l_BrowUp_crv')
    rBrowUpCrv = cmds.duplicate ( browCrv, n= 'r_BrowUp_crv') 
    lBrowDownCrv = cmds.duplicate ( browCrv, n= 'l_BrowDown_crv')
    rBrowDownCrv = cmds.duplicate ( browCrv, n= 'r_BrowDown_crv')    
    lCrv = [lBrowSadCrv[0], lBrowMadCrv[0], lFurrowCrv[0], lRelaxCrv[0],lBrowUpCrv[0],lBrowDownCrv[0] ]    
    rCrv = [rBrowSadCrv[0], rBrowMadCrv[0], rFurrowCrv[0], rRelaxCrv[0],rBrowUpCrv[0],rBrowDownCrv[0] ]        
    crvLen = len(lCrv)
    
    browBS = cmds.blendShape ( lBrowSadCrv[0],rBrowSadCrv[0], lBrowMadCrv[0],rBrowMadCrv[0], lFurrowCrv[0],rFurrowCrv[0], lRelaxCrv[0],rRelaxCrv[0],
    lBrowUpCrv[0],rBrowUpCrv[0],lBrowDownCrv[0],rBrowDownCrv[0], browCrv, n ='browBS')
    cmds.blendShape( browBS[0], edit=True, w=[(0, 1), (1, 1), (2, 1), (3,1),(4, 1), (5,1),(6, 1), (7,1),(8, 1), (9,1),(10, 1), (11,1)  ])  
    LRBlendShapeWeight( browCrv, browBS[0] )
    
    tempCtlCrv = cmds.curve ( d = 1, p =([-1,0,0],[-0.5,0,0],[0,0,0],[0.5,0,0],[1,0,0]) )
    browCtlCrv = cmds.rename (tempCtlCrv, 'browCtrlCrv' ) 
    cmds.rebuildCurve (browCtlCrv, rebuildType = 0, spans = numOfCtl-1, keepRange = 0, degree = 3 ) 
    browCtlCrvShape = cmds.listRelatives ( browCtlCrv, c = True ) 
    cmds.parent ( browCtlCrv, "browCrv_grp") 
    
    #connect browMain Ctrls to browCtlCrv
    centerNum = (numOfCtl+1)/2
    strs = string.ascii_uppercase
    lf=[]
    rt=[]
    for i in range(0, centerNum-1):
        rName= "R"+ strs[centerNum-i-2]
        lName= "L"+ strs[i]
        rt.append(rName)
        lf.append(lName)    
    sequence = [rt[0]] + rt+["Mid"]+lf + [lf[-1]]
    cvs= cmds.ls("browCtrlCrv.cv[*]", fl=True )
    
    for num in range ( len(cvs) ):            
        #erase double transform
        if num == centerNum:
            if cmds.objExists('brow_arcMid'):
                cmds.connectAttr ('brow_arcMid.ty', cvs[num] + '.yValue' )            
                cmds.connectAttr ('brow_arcMid.tz',  cvs[num] + '.zValue' )
            else:
                pass
                
        else:
            #erase cv's tx value
            sumX = cmds.shadingNode ( 'addDoubleLinear', asUtility =True, n = 'browTX_sum'+ str(num) )
            cvXVal = cmds.getAttr( cvs[num] + '.xValue' )
            cmds.connectAttr ( 'brow_arc%s.tx'%(sequence[num]), sumX + '.input1' )
            cmds.setAttr ( sumX + '.input2', cvXVal )
            cmds.connectAttr ( sumX + '.output', cvs[num] + '.xValue' )
            
            cmds.connectAttr ('brow_arc' + sequence[num] + '.ty', cvs[num] + '.yValue' )

            cmds.connectAttr ('brow_arc' + sequence[num] + '.tz', cvs[num] + '.zValue' )
                   
    rBrowJntP = cmds.listRelatives( orderJnts[0], p=1 )[0]
    lBrowJntP = cmds.listRelatives( orderJnts[-1], p =1 )[0]
    lDtailCtlP =cmds.duplicate( lBrowJntP, po=1, n = 'lDtail_grp' )[0]
    rDtailCtlP =cmds.duplicate( rBrowJntP, po=1, n = 'rDtail_grp' )[0]
    cmds.parent ( lDtailCtlP, rDtailCtlP, browCtlGrp )    
    
    increment = 1.0/(jntNum-1)
    index = 0
    
    for jnt in orderJnts:
        basePos = cmds.xform( jnt, t = True, q = True, ws = True)
        print jnt
        browJntList = cmds.listRelatives ( jnt, c=True, ad =1 )
        rotYJnt = browJntList[2]
        rotYPos = cmds.xform( rotYJnt, t = True, q = True, ws = True)  
        tzJnt = browJntList[0]
        jntPos = cmds.xform( tzJnt, t = True, q = True, ws = True )
      
        #point on shapeCrv l_browDetail01  l_browBase01_jnt c_browDetail01_jnt
        shapePOC = cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = 'browShapePOC'+ str(index+1).zfill(2))
        cmds.connectAttr ( browCrvShape[0] + ".worldSpace",  shapePOC + '.inputCurve')
        cmds.setAttr ( shapePOC + '.turnOnPercentage', 1 )                
        cmds.setAttr ( shapePOC + '.parameter', increment *index )
        #point on freeform crv
        POC = cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = 'eyeBrowPOC'+ str(index+1).zfill(2))
        cmds.connectAttr ( browCtlCrvShape[0] + ".worldSpace",  POC + '.inputCurve')
        cmds.setAttr ( POC + '.turnOnPercentage', 1 )
        cmds.setAttr ( POC + '.parameter', increment *index )
        # browCrv controls browDetail parent 
       
        attrs = ["rx", "ry", "v"]        
        
        if jnt in x : #right joints           
            
            #detail ctrl on Face
            browRot = cmds.getAttr( rDtailCtlP + ".ry")
            dtailCtls = browDetailCtl( tzJnt, browRot, jntPos, rotYPos, basePos, offset, size, attrs )
            #dtailCtls = #l_brow#_ctl, l_brow#_base, l_browRY#_ctl   
            cmds.parent( dtailCtls[1], rDtailCtlP)
            '''
            rBrowCtrl = arcController( tzJnt.replace("_jnt", "_ctl"), ( jntPos[0], jntPos[1], jntPos[2]+ offset), size/2, 'sq' )
            ctlP = rBrowCtrl[1]
            cmds.setAttr (rBrowCtrl[0] + ".overrideColor", 3 )
            zeroGrp = cmds.duplicate(ctlP, po =1, n = ctlP.replace("_ctlP","_dummy") )
            #up/down reverse for mirror joint
            cmds.setAttr( browJntList[1]+".rx", 180)
            
            cmds.parent(ctlP, zeroGrp[0] )
            rotYGrp = cmds.group( em =1, n = rBrowCtrl[0].replace("_brow","_browRY"), p = "browCtl_grp")
            cmds.xform (rotYGrp, ws = True, t = rotYPos ) 
            cmds.parent(zeroGrp[0], rotYGrp) 
            ctlBase = cmds.group( em =1, n = ctlP.replace("_ctlP","_base"), p = browCtlGrp ) 
            cmds.xform (ctlBase, ws = True, t = basePos )            
            cmds.parent(rotYGrp, ctlBase)
            for att in attrs:            
                cmds.setAttr ( rBrowCtrl[0] + ".%s"%att, lock =1, keyable = 0)'''
                        
            browCrvCtlToJnt( dtailCtls[0], jnt, browJntList, dtailCtls[1], dtailCtls[2], shapePOC, POC, index )
        
        elif jnt in y : #left joints
        
            browRot = cmds.getAttr( lDtailCtlP + ".ry")
            #detail ctrl on Face
            dtailCtls = browDetailCtl( tzJnt, browRot, jntPos, rotYPos, basePos, offset, size, attrs )
            #dtailCtls = #l_brow#_ctl, l_brow#_base, l_browRY#_ctl   
            cmds.parent( dtailCtls[1], lDtailCtlP) #l_brow#_base, lDtail_grp 
            '''
            lBrowCtrl = arcController( tzJnt.replace("_jnt", "_ctl"), ( jntPos[0], jntPos[1], jntPos[2]+ offset), size/2, 'sq' ) 
            ctlP = lBrowCtrl[1]
            cmds.setAttr (lBrowCtrl[0] + ".overrideColor", 3 )
            zeroGrp = cmds.duplicate(ctlP, po =1, n = ctlP.replace("_ctlP","_dummy") )
            cmds.parent( ctlP, zeroGrp[0] )
            rotYGrp = cmds.group( em =1, n = lBrowCtrl[0].replace("_brow","_browRY"), p = "browCtl_grp")
            cmds.xform (rotYGrp, ws = True, t = rotYPos )
            cmds.parent(zeroGrp[0], rotYGrp)
            ctlBase = cmds.group( em =1, n = ctlP.replace("_ctlP","_base"), p = browCtlGrp ) 
            cmds.xform (ctlBase, ws = True, t = basePos )
            cmds.parent(rotYGrp, ctlBase)
            for att in attrs:            
                cmds.setAttr ( lBrowCtrl[0] + ".%s"%att, lock =1, keyable = 0)'''
            
            browCrvCtlToJnt (dtailCtls[0], jnt, browJntList, dtailCtls[1], dtailCtls[2], shapePOC, POC, index  )
            
        elif 'c_browBase' in jnt:
            
            #detail ctrl on Face
            browRot = 0
            dtailCtls = browDetailCtl( tzJnt, browRot, jntPos, rotYPos, basePos, offset, size, attrs )
            cmds.parent( dtailCtls[1], browCtlGrp ) #l_brow#_base, lDtail_grp 
            '''
            centerBrowCtrl = arcController( 'c_brow_ctl', ( jntPos[0], jntPos[1], jntPos[2]+ offset), size/2, 'sq' )
            ctlP = centerBrowCtrl[1]
            cmds.setAttr (centerBrowCtrl[0] + ".overrideColor", 1 )
            zeroGrp = cmds.duplicate(ctlP, po =1, n = ctlP.replace("_ctlP","_dummy") )
            cmds.parent( ctlP, zeroGrp[0] )
            rotYGrp = cmds.group( em =1, n = centerBrowCtrl[0].replace("_brow","_browRY"), p = "browCtl_grp")
            cmds.xform (rotYGrp, ws = True, t = rotYJntPos )
            ctlBase = cmds.group( em =1, n = ctlP.replace("_ctlP","_base"), p = browCtlGrp ) 
            cmds.xform (ctlBase, ws = True, t = basePos )
            cmds.parent(zeroGrp[0], rotYGrp)
            cmds.parent(rotYGrp, ctlBase)
            for att in attrs:            
                cmds.setAttr ( centerBrowCtrl[0] + ".%s"%att, lock =1, keyable = 0 )'''
                
            browCrvCtlToJnt ( dtailCtls[0], jnt, browJntList, dtailCtls[1], dtailCtls[2], shapePOC, POC, index )
            
        index = index + 1

#connectBrowCtrls ( .2, .2 )


def browDetailCtl( tzJnt, browRot, jntPos, rotYPos, basePos, offset, size, attrs ):

    browCtl = arcController( tzJnt.replace("_jnt", "_ctl"), ( jntPos[0], jntPos[1], jntPos[2]+ offset), size/2, 'sq' )
    ctlP = browCtl[1]
    cmds.setAttr ( ctlP + ".ry", browRot )
    cmds.setAttr (browCtl[0] + ".overrideColor", 1 )
    zeroGrp = cmds.duplicate(ctlP, po =1, n = ctlP.replace("_ctlP","_dummy") )[0]
    cmds.parent( ctlP, zeroGrp )
    rotYGrp = cmds.duplicate( zeroGrp, po=1, n = browCtl[0].replace("_brow","_browRY"))[0]
    cmds.xform (rotYGrp, ws = True, t = rotYPos )
    cmds.parent( zeroGrp, rotYGrp )
    ctlBase = cmds.duplicate( rotYGrp, po=1, n = ctlP.replace("_ctlP","_base") )[0] 
    cmds.setAttr( ctlBase + ".rotateOrder", 3 )
    cmds.xform (ctlBase, ws = True, t = basePos )    
    cmds.parent(rotYGrp, ctlBase)
    for att in attrs:            
        cmds.setAttr ( browCtl[0] + ".%s"%att, lock =1, keyable = 0 )
        
    return browCtl[0], ctlBase, rotYGrp #l_brow#_ctl, l_brow#_base, l_browRY#_ctl   


def browCrvCtlToJnt( browCtrl, jnt, browJntList, ctlBase, rotYCtl, shapePOC, POC, index):
    """
    lots of utility nodes
    """
    #connect browCtrlCurve and controller to the brow joints
    ctrlMult = cmds.shadingNode('multiplyDivide', asUtility=True, n = jnt.split('Base', 1)[0] +'ctrlMult'+ str(index) )
    jntMult = cmds.shadingNode('multiplyDivide', asUtility=True, n = jnt.split('Base', 1)[0] +'JntMult'+ str(index) )
    browXYZSum = cmds.shadingNode('plusMinusAverage', asUtility=True, n = jnt.split('Base', 1)[0] +'XYZSum'+ str(index))
     
    #brow TX sum   
    #POC TX zero out 
    cmds.connectAttr(POC + '.positionX', browXYZSum + '.input3D[1].input3Dx')
    initialX = cmds.getAttr( POC + '.positionX')
    cmds.setAttr(browXYZSum + '.input3D[2].input3Dx', -initialX )
    cmds.connectAttr(shapePOC + '.positionX', browXYZSum + '.input3D[3].input3Dx')
    initX = cmds.getAttr(shapePOC + '.positionX')
    cmds.setAttr(browXYZSum + '.input3D[4].input3Dx', -initX )
    #browXYZSum.tx --> ctrlMult.ry 
    cmds.connectAttr(browXYZSum + '.output3Dx', ctrlMult+'.input1X')
    cmds.connectAttr( 'browFactor.browRotateY_scale', ctrlMult +'.input2X')
    cmds.connectAttr(ctrlMult+'.outputX', rotYCtl + '.ry' )    
        
    #add browCtl.tx 
    rotYJnt = browJntList[2]

    cmds.connectAttr(browXYZSum + '.output3Dx', jntMult+'.input1X')
    
    if rotYJnt[0] in ["l", "c"]:
        cmds.connectAttr( 'browFactor.browRotateY_scale', jntMult+'.input2X')
    elif rotYJnt[0] =="r":
        cmds.connectAttr( 'browReverse_mult.outputX', jntMult+'.input2X')    
    cmds.connectAttr(jntMult+'.outputX', rotYJnt + '.ry' )   
            
    #brow TY sum    
    #1.POC.ty sum
    cmds.connectAttr(POC + '.positionY', browXYZSum +'.input3D[0].input3Dy')
    cmds.connectAttr(shapePOC + '.positionY', browXYZSum + '.input3D[1].input3Dy')
      
    #new
    browCond = cmds.shadingNode("condition", asUtility=1, n = "browScale_Cond")     
    
    #add BrowCtl.ty --> jnt.rx      
    cmds.connectAttr(browXYZSum + ".output3Dy", browCond + ".firstTerm" )
    cmds.setAttr(browCond + ".secondTerm", 0 )
    cmds.setAttr(browCond + ".operation", 2 )  #greater than        
    
    #brow up setup
    cmds.connectAttr('browReverse_mult.outputX', browCond+".colorIfTrueR")
    cmds.setAttr(browCond+".colorIfFalseR", 0 )
    cmds.connectAttr(browCond+".outColorR", jntMult + ".input2Y")
    #cmds.connectAttr('browReverse_mult.outputZ', browCond+".colorIfFalseR")
    cmds.connectAttr(browXYZSum + ".output3Dy", jntMult + ".input1Y")
    cmds.connectAttr(jntMult+'.outputY',  jnt + '.rx')
    
    #brow down setup
    browDwnJnt = browJntList[-1] 
    cmds.connectAttr('browReverse_mult.outputZ', browCond+".colorIfFalseG")
    cmds.setAttr(browCond+".colorIfTrueG", 0 )
    cmds.connectAttr(browCond+".outColorG", jntMult + ".input2Z")
    cmds.connectAttr(browXYZSum + ".output3Dy", jntMult + ".input1Z")
    cmds.connectAttr(jntMult+'.outputZ',  browDwnJnt + '.rx')        
    #cmds.connectAttr(jntMult+'.outputZ',  wide + '.rx')
    
    #browDetailctrl follow
    cmds.connectAttr( browXYZSum + '.output3Dy', ctrlMult + ".input1Y" )
    cmds.connectAttr('browReverse_mult.outputX', ctrlMult + ".input2Y" )
    cmds.connectAttr( ctrlMult+'.outputY', ctlBase + '.rx' )
    
    #brow TZ sum( brow detail control: weight test brow Up and browTZ down in face clusters )
    browPCtl =cmds.listRelatives( cmds.listRelatives (rotYCtl, c =1, type = 'transform')[0], c =1, type = 'transform')
    browJnt = browJntList[0]#tip joint( end joint of the chain )
    cmds.connectAttr(shapePOC + '.positionZ', browXYZSum + '.input3D[0].input3Dz') 
    cmds.connectAttr(POC + '.positionZ', browXYZSum + '.input3D[1].input3Dz') #ctlCrv for brow Bulge/Tue Dec  3 17:26:35 2019 
    cmds.connectAttr(browXYZSum + '.output3Dz', browPCtl[0]+'.tz' )
    
    #browCtrl --> browJnt[0] + ".translate"
    if browDwnJnt[0] in ["l", "c"]:
        cmds.connectAttr(browXYZSum + '.output3Dz', browDwnJnt + '.tz' )
    elif browDwnJnt[0] =="r":
        conversion = cmds.shadingNode( "unitConversion", asUtility =1, n = browDwnJnt.split("_")[1] + "_conversion")
        cmds.setAttr( conversion + ".conversionFactor", -1 )
        cmds.connectAttr(browXYZSum + '.output3Dz', conversion + '.input' )
        cmds.connectAttr(conversion + '.output', browDwnJnt + '.tz' )

  
    #browCtrl --> browJnt[0] + ".translate"
    #cmds.connectAttr(browXYZSum + '.output3Dz', browDwnJnt + '.tz' )
    
    #extra rotate ctrl for browJnt[0]
    cmds.connectAttr(browCtrl + '.t', browJnt + '.t')   
    cmds.connectAttr(browCtrl + '.r', browJnt + '.r')
    cmds.connectAttr(browCtrl + '.s', browJnt + '.s')

 

#select "ctl guide curve", "ctl sample"(both or either or none) 
def browCtl_onHead( numOfCtl, offset, radius, polyEdgeCrv, myCtl ):
    
    if polyEdgeCrv:        
        cmds.rename( polyEdgeCrv, "brow_guide_Crv" )
        crv = "brow_guide_Crv"

    else:    
        headMesh = cmds.getAttr("helpPanel_grp.headGeo") 
        browVerts = cmds.getAttr( "browFactor.browVerts" )
        orderedVerts=[]
        mirrorVerts = mirrorVertice( browVerts )
        orderedVerts = mirrorVerts[1:][::-1] + browVerts

        #create guide curve based on lipFactor vtx
        edges =[]
        numVtx = len(orderedVerts)
        for v in range(numVtx-1):
            
            cmds.select( orderedVerts[v] )
            x = cmds.polyListComponentConversion( fv=1, toEdge=1 )
            cmds.select(x, r=1 )
            edgeA= cmds.ls(sl=1, fl=1)
            cmds.select(orderedVerts[v+1], r=1 )
            y =cmds.polyListComponentConversion( fv=1, toEdge=1 )
            cmds.select(y, r=1 )
            edgeB= cmds.ls(sl=1, fl=1)
            
            common = set(edgeA) -(set(edgeA) - set(edgeB))
            if common:
                edges.append(list(common)[0])
            else:
                cmds.confirmDialog( title='Confirm', message='Select "polyEdgeCurve" for brow Ctrls!!' )
                break
                
        cmds.select(cl=1)
        
        for e in edges:
            cmds.select(e, add=1)
            
        crv = cmds.polyToCurve( form=2, degree=1, n = "brow_guide_Crv")[0]
    
    print crv
    cmds.rebuildCurve( crv, rebuildType = 0, spans = numOfCtl-1, keepRange = 0, degree = 1, ch=1 )    
    crvShape = cmds.listRelatives( crv, c=1 )[0]
    
    if not cmds.objExists('guideCrv_grp'):
        guideCrvGrp = cmds.group ( n = 'guideCrv_grp', em =True, p = 'faceMain|crv_grp' )
        cmds.parent( crv, guideCrvGrp )
   
    if cmds.nodeType(crvShape)=="nurbsCurve":
    
        numVtx = len(cmds.ls( crvShape + ".cv[*]", fl=1 ) )
        cvStart = cmds.xform(crvShape + ".cv[0]", q=1, ws=1, t=1 )
        cvEnd = cmds.xform( crvShape + ".cv[%s]"%str(numVtx-1), q=1, ws=1, t=1 )

        if cvStart[0] > cvEnd[0]:
            cmds.reverseCurve( crv, ch= 1, rpo=1 )
            
        #create group node for brow Ctls    
        if not cmds.objExists( "browCtl_grp" ):
            browCtlGrp = cmds.group ( n = "browCtl_grp", em =True, p = "ctl_grp" )
        else:
            browCtlGrp = "browCtl_grp"
        
        pocs = pocEvenOnCrv( crv, numOfCtl, "brow_arc" )#create brow_arc01_poc, brow_arc02_poc...
        leng = (len(pocs)+1)
        sequence = string.ascii_uppercase
        ctlColor = [ 2, 12, 6 ] #,23,22,21,20,19,18,17,16,14,13 red ,12,9,7,6,4,1 ]
        
        #create main ctls
        for i in range(leng/2):
        
            center = leng/2-1                 
            if i == 0:
                #sequence = A, color = 2, pos = pocs[center]
                null = cmds.group( em=1, n = "brow_arcMid_null" ) #create brow_arcA_null,brow_arcB_null..
                cmds.connectAttr( pocs[center] +".position", null +".t" )
                pos = cmds.getAttr( pocs[center] +".position")[0]       
                if myCtl:
                    newCtl = cmds.duplicate( myCtl )[0]  
                    #이름 수정, CtlP null에 페어런트하고 position에 옮겨놓는다.
                    ctl = customCtl(  newCtl, null.replace( "Mid_null", "Mid" ), pos )

                else:
                    ctl = arcController( null.replace( "Mid_null", "Mid"), pos, radius*2, "cc" )
                    
                cmds.setAttr (ctl[0] +"Shape.overrideEnabled", 1)
                cmds.setAttr( ctl[0]+"Shape.overrideColor", 2 )               
                #parent controller to null 
                cmds.parent(ctl[1], null )
                #controller offset
                cmds.setAttr( ctl[1] + ".tz", offset*2 )
                cmds.parent( null, browCtlGrp )
                
            else:
                #sequence = [i], color = (i+1)*2, pos = pocs[center-i], pocs[center+ i]
                LR = { "L":center+i, "R": center-i }
                num = 0
                for k, x in LR.items():
                    null = cmds.group( em=1, n = "brow_arc" + k + sequence[i-1]+"_null" ) #create brow_arcA_null,brow_arcB_null..
                    cmds.connectAttr( pocs[x] +".position", null +".t" )
                    pos = cmds.getAttr( pocs[x] +".position")[0] 
                    if myCtl:
                        newCtl = cmds.duplicate( myCtl )[0]  
                        #이름 수정, CtlP null에 페어런트하고 position에 옮겨놓는다.
                        ctl = customCtl(  newCtl, null.replace( sequence[i-1]+"_null", sequence[i-1] ), pos )
                        cmds.setAttr (ctl[0] +"Shape.overrideEnabled", 1 )
                        cmds.setAttr( ctl[0]+"Shape.overrideColor", ctlColor[num+1] )

                    else:
                        ctl = arcController( null.replace( sequence[i-1]+"_null", sequence[i-1] ), pos, radius*2, "cc" )                    
                        cmds.setAttr (ctl[0] +"Shape.overrideEnabled", 1 )
                        cmds.setAttr( ctl[0]+"Shape.overrideColor", ctlColor[num+1] )
                        
                    #parent controller to null 
                    cmds.parent(ctl[1], null )
                    #controller offset
                    cmds.setAttr( ctl[1] + ".tz", offset*2 )
                    cmds.parent( null, browCtlGrp )
                    num = num+1
        
        if not cmds.objExists('c_browBase*_jnt'):
            cmds.delete("brow_arcMid_null")       
        
        return crv
        
    else:
        cmds.confirmDialog( title='Confirm', message='Select "polyEdgeCurve" for brow Ctrls!!' )


def createBrowCtl( jntNum, orderJnts):
    """
    create extra controllor for the panel
    """
    ctlP = "browDetailCtrl0"
    kids = cmds.listRelatives (ctlP, ad=True, type ='transform')   
    if kids:
        cmds.delete (kids)
        
    attTemp = ['scaleX','scaleY','scaleZ', 'rotateX','rotateY', 'tz', 'visibility' ]  
    index = 0
    for jnt in orderJnts:                            
        detailCtl = cmds.circle ( n = 'browDetail' + str(index+1).zfill(2), ch=False, o =True, nr = ( 0, 0, 1), r = 0.2 )
        detailPlane = cmds.nurbsPlane ( ax = ( 0, 0, 1 ), w = 0.1,  lengthRatio = 10, degree = 3, ch=False, n = 'browDetail'+ str(index+1).zfill(2) + 'P' )
        increment = 2.0/(jntNum-1)
        cmds.parent (detailCtl[0], detailPlane[0], relative=True )
        cmds.parent (detailPlane[0], ctlP, relative=True )
        cmds.setAttr (detailPlane[0] + '.tx', -2 + increment*index*2 )
        cmds.xform ( detailCtl[0], r =True, s = (0.2, 0.2, 0.2))  
        cmds.setAttr (detailCtl[0] +".overrideEnabled", 1)
        cmds.setAttr (detailCtl[0] +"Shape.overrideEnabled", 1)
        cmds.setAttr( detailCtl[0]+"Shape.overrideColor", 20)        
        
        cmds.transformLimits ( detailCtl[0] , tx = ( -.4, .4), etx=( True, True) )
        cmds.transformLimits ( detailCtl[0], ty = ( -.8, .8), ety=( True, True) )
        
        for att in attTemp:
            cmds.setAttr (detailCtl[0] +"."+ att, lock = True, keyable = False, channelBox =False)
                
        index = index + 1


#"browDetail" controls in twitchPanel match up with brow joints          
def browDetailCtls_old():        
    browJnts = cmds.ls ( "*browBase*_jnt", fl = True, type = "joint" )
    jntNum = len(browJnts)

    ctlP = "browDetailCtrl0"
    kids = cmds.listRelatives (ctlP, ad=True, type ='transform')   
    if kids:
        cmds.delete (kids)
        
    attTemp = ['scaleX','scaleY','scaleZ', 'rotateX','rotateY', 'tz', 'visibility' ]  

    #left right mirror
    ctlColor = [ 2, 3, 24,23,22,21,20,19,18,17,16,14,13,9,7,6,4,1 ]
    increment = (2.0 + (jntNum-1)/10)/(jntNum-1)
    
    cPlane = cmds.nurbsPlane ( ax = ( 0, 0, 1 ), w = 0.1,  lengthRatio = 10, degree = 3, ch=False, n = 'c_browDetail01P' )
    cDetailCtl = arcController( 'c_browDetail01' , ( 0, 0, 0), .2, 'cc' )
    cmds.setAttr (cDetailCtl[0] + ".overrideColor", 1 )
    cmds.parent (cDetailCtl[0], cPlane[0], relative=True )
    cmds.parent (cPlane[0], ctlP, relative=True )
    cmds.delete( cDetailCtl[1])
    cmds.setAttr (cPlane[0] + '.tx', 0 )
    cmds.xform ( cDetailCtl[0], r =True, s = (0.2, 0.2, 0.2))  
    for att in attTemp:
        cmds.setAttr (cDetailCtl[0] +"."+ att, lock = True, keyable = False, channelBox =False)
        
        
    for index in range(jntNum/2):

        rPlane = cmds.nurbsPlane ( ax = ( 0, 0, 1 ), w = 0.1,  lengthRatio = 10, degree = 3, ch=False, n = 'r_browDetail'+ str(index+1).zfill(2) + 'P' )
        rDetailCtl = arcController( 'r_browDetail' + str(index+1).zfill(2) , ( 0, 0, 0), .25, 'sq' )
        cmds.setAttr (rDetailCtl[0] + ".overrideColor", ctlColor[index] )
        cmds.parent (rDetailCtl[0], rPlane[0], relative=True )
        cmds.parent (rPlane[0], ctlP, relative=True )
        #get rid of parent(null) node
        cmds.delete( rDetailCtl[1])
        cmds.setAttr (rPlane[0] + '.tx', increment*(index+1)*-2 )
        cmds.xform ( rDetailCtl[0], r =True, s = (0.2, 0.2, 0.2))  
        for att in attTemp:
            cmds.setAttr (rDetailCtl[0] +"."+ att, lock = True, keyable = False, channelBox =False)
    
    
        lPlane = cmds.nurbsPlane ( ax = ( 0, 0, 1 ), w = 0.1,  lengthRatio = 10, degree = 3, ch=False, n = 'l_browDetail'+ str(index+1).zfill(2) + 'P' )
        lDetailCtl = arcController( 'l_browDetail' + str(index+1).zfill(2) , ( 0, 0, 0), .2, 'cc' )
        cmds.setAttr (lDetailCtl[0] + ".overrideColor", ctlColor[index] )
        cmds.parent (lDetailCtl[0], lPlane[0], relative=True )
        cmds.parent (lPlane[0], ctlP, relative=True )
        #get rid of parent(null) node
        cmds.delete( lDetailCtl[1])
        cmds.setAttr (lPlane[0] + '.tx', increment*(index+1)*2 )
        cmds.xform ( lDetailCtl[0], r =True, s = (0.2, 0.2, 0.2))  
        for att in attTemp:
            cmds.setAttr (lDetailCtl[0] +"."+ att, lock = True, keyable = False, channelBox =False)
                
        
# upLowLR = "l_up" / "l_lo"
# create upVector from EyeLoc
def eyelidJoints_old( upLowLR ): 
      
    if not ('lEyePos'):
        print "create the face locators"
          
    else:        
        eyeRotY = cmds.getAttr ('lEyePos.ry' )
        eyeRotZ = cmds.getAttr ('lEyePos.rz' ) 
        eyeCenterPos = cmds.xform( 'lEyePos', t = True, q = True, ws = True)
         
    lidFactor = "lidFactor"  
    mirrorLR = upLowLR.replace("l_","r_")
    if "_up" in upLowLR:
        lEyeLoc = cmds.duplicate( "lEyePos", rr=1, rc=1, n= "l_eyeUp_loc")[0]
        cmds.xform( lEyeLoc, ws=1, t=[eyeCenterPos[0], eyeCenterPos[1]*2, eyeCenterPos[2]] )
        rEyeLoc = cmds.duplicate( lEyeLoc, n= lEyeLoc.replace("l_","r_"))
        cmds.xform( rEyeLoc, ws=1, t=[-eyeCenterPos[0], eyeCenterPos[1]*2, eyeCenterPos[2]] )
    #reorder the vertices in selection list
    ordered = []
    if "up" in upLowLR:

        if cmds.attributeQuery("upLidVerts", node = lidFactor, exists=1)==True:
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
    if not cmds.objExists('eyeLidJnt_grp'): 
        cmds.group ( n = 'eyeLidJnt_grp', em =True, p ="jnt_grp" ) 
                 					
    null = cmds.group ( n = upLowLR+'EyeLidJnt_grp', em =True, p ="eyeLidJnt_grp" )
    rNull = cmds.group ( n = mirrorLR +'EyeLidJnt_grp', em =True, p = "eyeLidJnt_grp" )
    cmds.select(cl = True) 
      
    #create eyeLids parent joint 
    lLidJntP = cmds.joint(n = upLowLR + 'LidP_jnt', p = eyeCenterPos ) 
    lLidGrp = cmds.group ( n = upLowLR+'LidP_grp', em =True, p = null )
    cmds.xform( lLidGrp, ws=1, t = eyeCenterPos )
    
    cmds.setAttr ( lLidGrp + '.ry', eyeRotY ) 
    cmds.setAttr ( lLidGrp + '.rz', eyeRotZ )
    cmds.parent ( lLidJntP, lLidGrp )
    rLidJntP = cmds.joint(n = mirrorLR + 'LidP_jnt', p = [-eyeCenterPos[0], eyeCenterPos[1], eyeCenterPos[2]])
    rLidGrp = cmds.group ( n = mirrorLR + 'LidP_grp', em =True, p = rNull )
    cmds.xform( rLidGrp, ws=1, t = [-eyeCenterPos[0], eyeCenterPos[1], eyeCenterPos[2]] )
    cmds.setAttr ( rLidGrp + '.ry', -eyeRotY ) 
    cmds.setAttr ( rLidGrp + '.rz', -eyeRotZ )
    cmds.parent ( rLidJntP, rLidGrp )    

      
    cmds.select(cl =1)
    #UI for 'null.rx/ry/rz'?? cmds.setAttr ( null + '.rz', eyeRotZ )    
    index = 1
    for v in ordered:
        vertPos = cmds.xform( v, t = True, q = True, ws = True )
        loc = cmds.spaceLocator( n= upLowLR + 'Loc' + str(index).zfill(2) )[0]
        cmds.xform( loc, ws=1, t = vertPos )
        cmds.parent( loc, null )
        cmds.setAttr( loc + ".visibility", 0 )
        
        rLoc = cmds.spaceLocator( n= mirrorLR + 'Loc' + str(index).zfill(2) )[0]
        cmds.xform( rLoc, ws=1, t = [ -vertPos[0], vertPos[1], vertPos[2]] )
        cmds.parent( rLoc, rNull )        
        cmds.setAttr( rLoc + ".visibility", 0 )
                
        lidJnt = cmds.joint(n = upLowLR + 'Lid' + str(index).zfill(2) + '_jnt', p = vertPos )
        cmds.setAttr ( lidJnt + '.rotateOrder', 5 ) 
        lidJntTX = cmds.joint(n = upLowLR + 'LidTX' + str(index).zfill(2) + '_jnt', p = vertPos )
        cmds.setAttr ( lidJntTX + '.rotateOrder', 5 )
        blinkJnt = cmds.duplicate ( lidJnt, po=True, n = upLowLR + 'LidBlink' + str(index).zfill(2)+'_jnt' )[0]
        cmds.parent ( blinkJnt, lLidJntP )
        cmds.setAttr ( blinkJnt + '.tx' , 0 )
        cmds.setAttr ( blinkJnt + '.ty' , 0 )  
        cmds.setAttr ( blinkJnt + '.tz' , 0 ) 
        cmds.parent ( lidJnt, blinkJnt )
        cmds.select(cl=1)        
        scaleJnt = cmds.duplicate ( blinkJnt, po=True, n = upLowLR + 'LidScale' + str(index).zfill(2) + '_jnt' )[0]         
        cmds.parent ( blinkJnt, scaleJnt )
        cmds.joint ( scaleJnt, e =True, ch=True, zso =True, oj = 'zyx', sao= 'yup')
        wideJnt = cmds.duplicate ( blinkJnt, po=True, n = upLowLR + 'LidWide' + str(index).zfill(2) + '_jnt')[0]
        #cmds.parent ( wideJnt, scaleJnt )
                
        cmds.parent ( scaleJnt, w=1 )
        #mirror joint and aim constraint
        rLidJnt = cmds.mirrorJoint ( scaleJnt, myz = True, mirrorBehavior=1, searchReplace = ('l_', 'r_'))
        print rLidJnt
        cmds.joint ( rLidJnt, e =True, ch=True, zso =True, oj = 'zyx', sao= 'yup')        
        cmds.parent ( scaleJnt, lLidJntP )
        cmds.parent ( rLidJnt[0],  rLidJntP )

        rBlink = cmds.listRelatives( rLidJnt[0], c=1 )[0]
        print rBlink
        cmds.aimConstraint( loc, blinkJnt, mo =1, weight=1, aimVector = (0,0,1), upVector = (0,1,0), worldUpType="object", worldUpObject = "l_eyeUp_loc" )
        cmds.aimConstraint( rLoc, rBlink, mo =1, weight=1, aimVector = (0,0,1), upVector = (0,1,0), worldUpType="object", worldUpObject = "r_eyeUp_loc" )                                       
        
        index = index + 1
        

# upLowLR = "l_up" / "l_lo"
# create upVector from EyeLoc
def eyelidJoints( upLowLR ): 
    # lEyePos Rotate Order : XZY
    if not ('lEyePos'):
        print "create the face locators"
          
    else:        
        eyeRotY = cmds.getAttr ('lEyePos.ry' )
        eyeRotZ = cmds.getAttr ('lEyePos.rz' ) 
        eyeCenterPos = cmds.xform( 'lEyePos', t = True, q = True, ws = True)
         
    lidFactor = "lidFactor"  
    mirrorLR = upLowLR.replace("l_","r_")
    if "_up" in upLowLR:
        lEyeLoc = cmds.duplicate( "lEyePos", rr=1, rc=1, n= "l_eyeUp_loc")[0]
        cmds.xform( lEyeLoc, ws=1, t=[eyeCenterPos[0], eyeCenterPos[1]*2, eyeCenterPos[2]] )
        rEyeLoc = cmds.duplicate( lEyeLoc, n= lEyeLoc.replace("l_","r_"))
        cmds.xform( rEyeLoc, ws=1, t=[-eyeCenterPos[0], eyeCenterPos[1]*2, eyeCenterPos[2]] )

    ordered = []
    if "up" in upLowLR:
        if cmds.attributeQuery("upLidVerts", node = lidFactor, exists=1)==True:
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
    if not cmds.objExists('eyeLidJnt_grp'): 
        cmds.group ( n = 'eyeLidJnt_grp', em =True, p ="jnt_grp" )                 					
    null = cmds.group ( n = upLowLR+'EyeLidJnt_grp', em =True, p ="eyeLidJnt_grp" )
    rNull = cmds.group ( n = mirrorLR +'EyeLidJnt_grp', em =True, p = "eyeLidJnt_grp" )
    cmds.select(cl = True)      

    lLidGrp = cmds.group ( n = upLowLR+'LidP_grp', em =True, p = null )
    cmds.xform( lLidGrp, ws=1, t = eyeCenterPos )
    cmds.setAttr( lLidGrp + ".rotateOrder", 3 )
    cmds.setAttr ( lLidGrp + '.ry', eyeRotY ) 
    cmds.setAttr ( lLidGrp + '.rz', eyeRotZ )
    lLidJntP = cmds.joint(n = upLowLR + 'LidP_jnt' )

    rLidGrp = cmds.group ( n = mirrorLR + 'LidP_grp', em =True, p = rNull )
    cmds.xform( rLidGrp, ws=1, t = [-eyeCenterPos[0], eyeCenterPos[1], eyeCenterPos[2]] )
    cmds.setAttr( rLidGrp + ".rotateOrder", 3 )
    cmds.setAttr ( rLidGrp + '.ry', -eyeRotY ) 
    cmds.setAttr ( rLidGrp + '.rz', -eyeRotZ )
    #rLidJntP = cmds.joint(n = mirrorLR + 'LidP_jnt' )

    cmds.select(cl =1)
    #UI for 'null.rx/ry/rz'?? cmds.setAttr ( null + '.rz', eyeRotZ )    
    index = 1
    for v in ordered:
        vertPos = cmds.xform( v, t = True, q = True, ws = True )
        
        #create constraint locator
        loc = cmds.spaceLocator( n= upLowLR + 'Loc' + str(index).zfill(2) )[0]        
        cmds.parent( loc, null )
        cmds.xform( loc, ws=1, t = vertPos )
        cmds.setAttr( loc + ".visibility", 0 )
        
        rLoc = cmds.spaceLocator( n= mirrorLR + 'Loc' + str(index).zfill(2) )[0]        
        cmds.parent( rLoc, rNull )
        cmds.xform( rLoc, ws=1, t = [ -vertPos[0], vertPos[1], vertPos[2]] )        
        cmds.setAttr( rLoc + ".visibility", 0 )
        
        #create eyeJoint chain
        cmds.select(lLidJntP)
        scaleJnt = cmds.joint( n = upLowLR + 'LidScale' + str(index).zfill(2) + '_jnt' )
        #cmds.parent ( scaleJnt, lLidJntP )
        blinkJnt = cmds.joint ( n = upLowLR + 'LidBlink' + str(index).zfill(2)+'_jnt' )
        lidJnt = cmds.joint(  n = upLowLR + 'Lid' + str(index).zfill(2) + '_jnt' )
        cmds.xform( lidJnt, ws=1, t = vertPos )
        lidJntTX = cmds.joint( n = upLowLR + 'LidTX' + str(index).zfill(2) + '_jnt' )   

        #cmds.joint ( scaleJnt, e =True, ch=True, zso =True, oj = 'zyx', sao= 'yup')
        wideJnt = cmds.duplicate ( blinkJnt, po=True, n = upLowLR + 'LidWide' + str(index).zfill(2) + '_jnt')[0]
        #cmds.parent ( wideJnt, scaleJnt )
        index = index + 1    
        
    cmds.parent( lLidJntP, w=1)
    rLidJntP = cmds.mirrorJoint ( lLidJntP, myz = True, mirrorBehavior=1, searchReplace = ('l_', 'r_'))[0]
    cmds.parent ( lLidJntP, lLidGrp )
    cmds.parent ( rLidJntP, rLidGrp )

    vtxLen = len(ordered)
    for i in range(vtxLen):
        lLoc = upLowLR + 'Loc'+str(i+1).zfill(2)
        rLoc = mirrorLR + 'Loc'+str(i+1).zfill(2)
        lBlink = upLowLR + 'LidBlink'+str(i+1).zfill(2)+ '_jnt'
        rBlink = mirrorLR + 'LidBlink'+str(i+1).zfill(2)+ '_jnt'
        cmds.aimConstraint( lLoc, lBlink, mo =1, weight=1, aimVector = (0,0,1), upVector = (0,1,0), worldUpType="object", worldUpObject = "l_eyeUp_loc" )
        cmds.aimConstraint( rLoc, rBlink, mo =1, weight=1, aimVector = (0,0,1), upVector = (0,1,0), worldUpType="object", worldUpObject = "r_eyeUp_loc" )                                       
      


#pre = "l_up"."l_lo"."r_up"."r_lo"
def wideLid_setup(pre):
  
    if "_up" in pre:
        option = 4
    elif "_lo" in pre:
        option = 3
        
    blink = cmds.ls( pre + "LidBlink*_jnt", typ = "joint")
    wide = cmds.ls( pre + "LidWide*_jnt", typ = "joint")

    for j in range(len(blink)):
        
        cond = cmds.shadingNode( "condition", asUtility =1, n = pre + "EyeWide_cond" + str(j+1).zfill(2) )
        mult = cmds.shadingNode( "multiplyDivide", asUtility =1, n = pre + "EyeWide_mult" + str(j).zfill(2) )
        # wide should follow blinkJnt 100%
        xyz = cmds.getAttr( blink[j] + ".r" )[0]
        cmds.setAttr( cond + ".colorIfFalseR", xyz[0] )
                     
        cmds.connectAttr( blink[j] + ".rx", cond + ".firstTerm")
        cmds.setAttr( cond + ".secondTerm", xyz[0]) # blink[j] + ".rx" initial value
        cmds.setAttr( cond + ".operation", option )#up :less than / down:greater than
        cmds.connectAttr( blink[j] + ".rx", cond + ".colorIfTrueR" )
        cmds.connectAttr( cond + ".outColorR", wide[j] + ".rx" )

        cmds.connectAttr( blink[j] + ".ry", mult + ".input1Y" )
        cmds.connectAttr( blink[j] + ".rz", mult + ".input1Z" )
        cmds.setAttr( mult + ".input2Y", 1)
        cmds.setAttr( mult + ".input2Z", 1)
        
        cmds.connectAttr( mult + ".outputY", wide[j] + ".ry" )
        cmds.connectAttr( mult + ".outputZ", wide[j] + ".rz" )        
                


# eyeWide_jnt label setup                
def eyeWideJntLabel():
    prefix = ["l_up", "l_lo"]
    for pre in prefix:
        jnts = cmds.ls ( pre + 'LidWide*_jnt', type ='joint')
        for i, j in enumerate(jnts):
            lName = j.split("_") 
            cmds.setAttr(j + '.side', 1)
            cmds.setAttr(j + '.type', 18)
            cmds.setAttr(j + '.otherType', lName[1], type = "string")
            
            rj = j.replace("l_","r_")
            rName = rj.split("_")
            cmds.setAttr(rj + '.side', 2)
            cmds.setAttr(rj + '.type', 18)
            cmds.setAttr(rj + '.otherType', rName[1], type = "string")    
        
        

def eyeHiCrv( prefix ):

    #get ordered vertices
    if "up" in prefix:
        orderVtx = cmds.getAttr( "lidFactor.upLidVerts" )
    
    elif "lo" in prefix:
        orderVtx = cmds.getAttr( "lidFactor.loLidVerts" )
    leng = len(orderVtx) 
    if cmds.objExists("eyeCrv_grp"):
        eyeCrvGrp = "eyeCrv_grp"            
    else:
        eyeCrvGrp = cmds.group( em=1, n = "eyeCrv_grp", p = "crv_grp"  )            

    posOrder = []    
    if "l_" in prefix:
        for vx in orderVtx:
            lPos = cmds.xform( vx, q=1, ws=1, t=1)
            posOrder.append(lPos)
        
    elif "r_" in prefix:
        for vx in orderVtx:
            lPos = cmds.xform( vx, q=1, ws=1, t=1)
            rPos = [ -lPos[0], lPos[1], lPos[2] ]    
            posOrder.append(rPos)        
   
    tmpCrv = cmds.curve( d= 1, p= posOrder )#, n =  prefix  + "TempCrv01"
    #int $numCVs   = $numSpans + $degree
    #cmds.rebuildCurve( tmpCrv, d = 1, rebuildType = 0, s= leng-1, keepRange = 0)
    newHiCrv = cmds.rename( tmpCrv, prefix  + "HiCrv01" )
    cmds.parent( newHiCrv, eyeCrvGrp )
    blinkCrv = cmds.duplicate( newHiCrv, n = newHiCrv.replace("Hi","Blink"), rc=1 )[0]
    crvShape = cmds.listRelatives( newHiCrv, c=1, ni=1, s=1 )    
    
    if "lo" in prefix:
        posOrder=posOrder[1:-1]        
        
    for i, pos in enumerate( posOrder ):
        
        uParam = getUParam( pos, newHiCrv )
        poc =cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = prefix + 'eyePOC'+ str(i+1).zfill(2) )
        cmds.connectAttr( crvShape[0] + ".worldSpace" , poc + ".inputCurve" )
        cmds.setAttr( poc+".parameter", uParam )
        cmds.connectAttr( poc + ".position", prefix + "Loc"+str(i+1).zfill(2) +".t" )
        


####blink / shape "controlPanel" for arface setup!!!!!!!!!!!!!!!!!
''' 
1.up/loHiCrv wire to up/loCtlCrv 
2.BlinkLevelCrv(copy of upCtlCrv) blendshape to loCtlCrv   
3.up/loBlinkCrv wire to BlinkLevel crv 
4.up/loHiCrv blendShape to up/loBlinkCrv for "blinking"
5.up/loHiCrv wire to up/loCtlCrv for "detail control" 

 "l_upCTLCrv01"이 스킨으로 눈모양을 컨트롤한다 
 "l_upHiCrv01" 는 와이어로 CTLCrv를 따라다니다가 blink만 블렌쉐입으로 핸들한다
 컨트롤러는 hiCrv에 일정한 uParam 간격으로 배치되어 배열이 흉할수 있다.( But 기능적으로 맞다 )
 
'''

#create "attachCtl_grp" in hierachy
# adjust CTLcrv(master) shape to hiCrv
# place joints for eyeCtls at 20*i% on hi curve
def eyeCtrls( prefix, numEyeCtl, offset ):
   
    headMesh = cmds.getAttr( "helpPanel_grp.headGeo")
    lidVerts = cmds.getAttr( "lidFactor." +prefix[2:] + "LidVerts" )
    cpmNode = cmds.createNode("closestPointOnMesh", n = "closestPointM_node")
    cmds.connectAttr( headMesh + ".outMesh", cpmNode + ".inMesh")
    orderedVerts = []
    if "r_" in prefix:   
        orderedVerts = mirrorVertice(lidVerts)
        eyeRotY = cmds.getAttr ('r_upLidP_grp.ry' )
        eyeRotZ = cmds.getAttr ('r_upLidP_grp.rz' ) 
        
    else:
        orderedVerts = lidVerts
        eyeRotY = cmds.getAttr ('l_upLidP_grp.ry' )
        eyeRotZ = cmds.getAttr ('l_upLidP_grp.rz' )
        
    edges =[]
    numVtx = len(orderedVerts)
    for v in range(numVtx-1):
        
        cmds.select( orderedVerts[v] )
        x = cmds.polyListComponentConversion( fv=1, toEdge=1 )
        cmds.select(x, r=1 )
        edgeA= cmds.ls(sl=1, fl=1)
        cmds.select(orderedVerts[v+1], r=1 )
        y =cmds.polyListComponentConversion( fv=1, toEdge=1 )
        cmds.select(y, r=1 )
        edgeB= cmds.ls(sl=1, fl=1)
        
        common = set(edgeA) -(set(edgeA) - set(edgeB))
        edges.append(list(common)[0])
    cmds.select(cl=1)
    
    # create polyEdgeCurve to follow head geo
    for e in edges:
        cmds.select(e, add=1 )
    
    #create guide_crv 
    crv = cmds.polyToCurve( form=2, degree=1, n = prefix + "Eye_guide_Crv")[0]
    cmds.rebuildCurve( crv, rebuildType = 0, spans = numEyeCtl-1, keepRange = 0, degree = 3 )
    cvList = cmds.ls( crv + ".cv[*]", fl=1 )
    cvStart = cmds.xform(cvList[0], q=1, ws=1, t=1)[0]
    cvEnd = cmds.xform( cvList[-1], q=1, ws=1, t=1)[0]
    if cvStart**2 > cvEnd**2:
    	cmds.reverseCurve( crv, ch= 1, rpo=1 )

    if not cmds.objExists('guideCrv_grp'):
        guideCrvGrp = cmds.group ( n = 'guideCrv_grp', em =True, p = 'faceMain|crv_grp' ) 
    cmds.parent( crv, "guideCrv_grp" )
    
    sequence = string.ascii_uppercase 
    leng = cmds.arclen( crv )
    increm = leng / 30
    print "ctl size is %s"%increm
    
    if cmds.objExists("eyeOnCtl_grp"):
        eyeGrp = "eyeOnCtl_grp"            
    else:
        eyeGrp = cmds.group( em=1, n = "eyeOnCtl_grp", p = "ctl_grp"  )

    if cmds.objExists("eyeCrvJnt_grp"):
        crvJntGrp = "eyeCrvJnt_grp"            
    else:
        crvJntGrp = cmds.group( em=1, n = "eyeCrvJnt_grp", p = "jnt_grp"  )                  

    #seperate looping for up / lo( different num of joint) 
    if "up" in prefix:
        minV = 0
        maxV = numEyeCtl
    elif "lo" in prefix:
        minV = 1
        maxV = numEyeCtl-1
    
    cornerPoc = []        
    ctlPoc = []
    temGrp = nullEvenOnCrv( crv, numEyeCtl, prefix +"EyeCtl" ) #nulls, pocs
    nulls = temGrp[0]
    pocs = temGrp[1]
    for i in range( minV, maxV ):
        x = i-1
        
        #create ctl joints grp
        pos = cmds.getAttr( pocs[i]+".position")[0]
        if i == 0:#first/last point for in/outCorner
        	grp = cmds.rename( nulls[i], prefix[:2] + "InCorner_eye_JntP" )
        	cornerPoc.append(pocs[i])
        elif i == numEyeCtl-1 :#first/last point for in/outCorner
        	grp = cmds.rename( nulls[i], prefix[:2] + "OutCorner_eye_JntP" )
        	cornerPoc.append(pocs[i])
        else:
        	grp = cmds.rename( nulls[i], prefix + "_"+ sequence[x] + "eye_JntP" )
        	ctlPoc.append(pocs[i])
       	
        cmds.parent( grp, "eyeCrvJnt_grp" )
        cmds.setAttr( grp + ".rotateOrder", 3 )
        cmds.setAttr ( grp + '.ry', eyeRotY ) 
        cmds.setAttr ( grp + '.rz', eyeRotZ )
        
        jnt = cmds.joint( p = pos,  n = grp.replace("eye_JntP","Eye_jnt") )        
        cmds.select(cl=1)
        ctl = arcController( grp.replace("eye_JntP","ctl"), pos, increm, "cc" )
        #create top parent null for ctl
        ctlGrp = cmds.duplicate( ctl[1], po =1, n = ctl[1].replace("ctlP","_grp")  )
        cmds.parent( ctl[1], ctlGrp )
        cmds.connectAttr( pocs[i]+".position", ctlGrp[0] + ".t" )
        cmds.setAttr( ctlGrp[0] + ".rotateOrder", 3 )
        cmds.setAttr ( ctlGrp[0] + '.ry', eyeRotY ) 
        cmds.setAttr ( ctlGrp[0] + '.rz', eyeRotZ )
        cmds.setAttr( ctl[1] + ".tz", offset )
        cmds.parent( ctlGrp , "eyeOnCtl_grp" )
                    
        #print "%s is for %s"%(str(i), ctl)
        
        cmds.connectAttr( ctl[0] + ".t" , jnt + ".t" )
        cmds.connectAttr( ctl[0] + ".r" , jnt + ".r" )
        cmds.connectAttr( ctl[0] + ".s" , jnt + ".s" )
        
    if cmds.attributeQuery( prefix + "_eyeCtlPoc", node = "lidFactor", exists=1)==False:
        cmds.addAttr( "lidFactor", ln = prefix + "_eyeCtlPoc", dt = "stringArray"  )
        cmds.setAttr("lidFactor.%s_eyeCtlPoc"%prefix, type= "stringArray", *([len(ctlPoc)] + ctlPoc) ) 

    if cmds.attributeQuery( prefix[:2] + "eyeCornerPoc", node = "lidFactor", exists=1)==False:
        cmds.addAttr("lidFactor", ln = prefix[:2] + "eyeCornerPoc", dt = "stringArray"  )
        
    if cornerPoc:
        cmds.setAttr("lidFactor."+prefix[:2]+"eyeCornerPoc", type= "stringArray", *([len(cornerPoc)] +cornerPoc))         
            


#create eyeCTL-curves ( 5cvs )
def eyeCtlCrv():
    #for arFace Sukwon Shin
    prefix = ["l_up", "l_lo", "r_up", "r_lo"]
    for pre in prefix:
        cornerPoc = cmds.getAttr( "lidFactor."+pre[:2] + "eyeCornerPoc" )
        ctlPoc =cmds.getAttr( "lidFactor.%s_eyeCtlPoc"%pre )
        ctlPoc.insert(0, cornerPoc[0])
        ctlPoc.append(cornerPoc[1])
        posList = []
        for pc in ctlPoc:
            pos = cmds.getAttr(pc+".position")[0]
            posList.append(pos)
            
        #create CTLCrv ( l_upCTLCrv01, l_loCTLCrv01.... )
        if cmds.objExists("eyeCrv_grp"):
            eyeCrvGrp = "eyeCrv_grp"            
        else:
            eyeCrvGrp = cmds.group( em=1, n = "eyeCrv_grp", p = "crv_grp"  )
            
        ctlCrv = cmds.curve( d= 3, ep= posList )
        newCrv = cmds.rename( ctlCrv,  pre + "CTLCrv01" )
        cmds.parent( newCrv, eyeCrvGrp )

        




# modeling the "CTLCrvs" BEFORE run it ( blendshape and skinning )
# create blink BS / wire deform for up/lo blinkCurve
# pre = ["l_","r_"]        
def eyeCrvConnect( pre ):

    #blink level crv(lo) setup
    upCrv = pre  + "upCTLCrv01"
    loCrv = pre  + "loCTLCrv01"
    lidFactor = "lidFactor"
    
    if cmds.objExists("eyeShapeCrv_grp"):
        eyeShapeGrp = "eyeShapeCrv_grp"            
    else:
        eyeShapeGrp = cmds.group( em=1, n = "eyeShapeCrv_grp", p = "eyeCrv_grp"  )
        
    for crv in [ upCrv, loCrv ]:
        titleSplit = crv.split("CTL") 
        lidTgtCrvs = []
        for sequence in [ "A","B","C","D"]:
            pushCrv = cmds.duplicate( crv, rc=1, n = titleSplit[0] + sequence + "Lid_crv" )[0]
            lidTgtCrvs.append(pushCrv)        
        
        squintCrv = cmds.duplicate( crv, rc=1, n = titleSplit[0] + "Squint_crv" )[0]
        lidTgtCrvs.append(squintCrv)
        annoyedCrv = cmds.duplicate( crv, rc=1, n = titleSplit[0] + "Annoyed_crv" )[0]
        lidTgtCrvs.append(annoyedCrv)
        ctlCrvBS = cmds.blendShape( lidTgtCrvs, crv, n = titleSplit[0] + "Lid_bs" )
        cmds.parent( lidTgtCrvs, eyeShapeGrp )
        
    blinkLevelCrv = cmds.duplicate( upCrv, rc=1, n = pre+ "BlinkLevelCrv" )[0]    
    
    if not cmds.objExists ( pre + "BlinkLevel_bs"):
        
        blinkBS = cmds.blendShape( pre  + "loCTLCrv01", pre  + "upCTLCrv01", blinkLevelCrv, n = pre + "BlinkLevel_bs" )
        
    else:
        blinkBS =[ pre + "BlinkLevel_bs" ]
        
    cmds.connectAttr( lidFactor + ".%sloBlinkLevel"%(pre), blinkBS[0] + ".%s"%( pre+"upCTLCrv01") )
    cmds.connectAttr( lidFactor + ".%supBlinkLevel"%(pre), blinkBS[0] + ".%s"%( pre+"loCTLCrv01") )        
    
    ctlJnt = []    
    corner =cmds.ls( pre + "*Corner_Eye_jnt", typ = "joint" )        
    upDown = { "up": 1 , "lo": 0 }
    for ud in upDown:
     
        #wire attach hiCrv to ctlCrv 
        ctlCrv = pre  + ud + "CTLCrv01"
        hiCrv = pre+ud+"HiCrv01"
        wireNd = cmds.wire( hiCrv, w = ctlCrv, n = pre + ud + "free_wire" )        
        cmds.setAttr( wireNd[0] + ".scale[0]", 1 )
        cmds.setAttr( wireNd[0] + ".rotation", 0 )         
        cmds.setAttr( wireNd[0] + ".dropoffDistance[0]", 5 )
        #eye blinkCrv / wideCrv setup 
        wideCrv = cmds.duplicate( hiCrv, rc=1, n = pre + ud + "Wide_crv" )[0]        
        blinkCrv = pre + ud  + "BlinkCrv01" #hiCrv target when blinking
        if cmds.objExists( blinkCrv ):
            #attach blink_Crv(hi) to the blink_level(lo) curve
            
            cmds.setAttr( lidFactor + "." + pre + "loBlinkLevel", upDown[ud] )
            wr = cmds.wire( blinkCrv, w = blinkLevelCrv, n = pre + ud + "Blink_wire" )
            cmds.setAttr( wr[0] + ".scale[0]", 0 ) 
            cmds.setAttr( wr[0] + ".dropoffDistance[0]", 5 )          
            
            smartBlinkBS = cmds.blendShape( wideCrv, blinkCrv, pre+ud+"HiCrv01", n = pre + ud+ "Blink_bs" )
    
        ctlJnt =cmds.ls( pre + ud + "*Eye_jnt", typ = "joint" )        
        eyeCtlJnt = corner + ctlJnt
        ctlCrv = pre + ud + "CTLCrv01"
        if cmds.objExists(ctlCrv):
            
            cmds.skinCluster( ctlCrv, eyeCtlJnt, toSelectedBones=1, bindMethod =0, nw =1, maximumInfluences=3, omi=1, rui=1 ) 

          
# compensate "double transform sticky ctls"    
def compensateStickyCtl( grp ):
    
    #get ctls' transform
    eyeCtls = getCtlList( grp )
    for i, ctl in enumerate(eyeCtls):   
        
        ctlP = cmds.listRelatives( ctl, p=1 )[0] 
        ctlPP = cmds.listRelatives( ctlP, p=1 )[0]
        if "compensate" in ctlPP:
            cmds.confirmDialog( title='Confirm', message='compensate grp is already exists!' )
            break
        else:
            oldName = ctlPP.split("_")
            grpName = oldName[-1]      
            revMult = cmds.shadingNode( "multiplyDivide", asUtility=1, n = ctl + "rev_mult" )
            
            compensateGrp = cmds.duplicate( ctlPP, po=1, n = ctlPP.replace( "_"+grpName,"_compensate") )
            cmds.parent( ctlP, compensateGrp[0] )
            cmds.parent( compensateGrp[0], ctlPP )
            cmds.connectAttr ( ctl + ".t", revMult + ".input1" )
            cmds.setAttr( revMult + ".input2", -1,-1,-1 )
            cmds.connectAttr ( revMult + ".output", compensateGrp[0] + ".t" ) 
        

def getCtlList( grp ):
    
    if cmds.objExists( grp ):
        tmpChild = cmds.listRelatives( grp, ad=1, ni=1, type = ["nurbsCurve", "mesh", "nurbsSurface"]  )
        child = [ t for t in tmpChild if not "Orig" in t ]
        ctls = cmds.listRelatives( child, p=1 )
        ctlist = []
        for c in ctls:
            cnnt = cmds.listConnections( c, s=1, d=1, c=1 )
            if cnnt:
                attr = cnnt[0].split('.')[1]
                print attr
                if attr in ["translate","rotate","scale","translateX","translateX","translateY","rotateZ","rotateY","rotateZ","scaleX","scaleY","scaleZ"]:
                    ctlist.append(c)     
        return ctlist

        
        
# eyeGeoGrp = cmds.ls(sl=1, typ = "transform")[0]
def eyeRigAttachBody( eyeGeoGrp, upVector):
    """
    create Eye Rig"""

    lEyePos = cmds.xform('lEyePos', t = True, q = True, ws = True)
    lEyeRot = cmds.xform('lEyePos', ro = True, q = True, ws = True)
    
    if cmds.objExists("eyeRig")==False:
        cmds.warning( "build the Hierachy first!!" )   
    else:
        eyeRig = "eyeRig"
    cmds.parent( eyeRig, "bodyHeadTRS")
    
    if cmds.objExists("eyeTR")==False:
        eyeTR = cmds.group( em=True, n = "eyeRig", p= "eyeRig" )      
    else:
        eyeTR = "eyeTR" 
    
    cmds.xform(eyeTR, ws=1, t = (0, lEyePos[1], lEyePos[2] ))                     
    lDMat = cmds.shadingNode( 'decomposeMatrix', asUtility =1, n = 'lEyeDecompose')
    multMat = cmds.shadingNode( 'multMatrix', asUtility =1, n = 'lEyeMultDCM')  
    #ffdSquachLattice = cmds.group(em =1, n = 'ffdSquachLattice', p = 'eyeRigP')
    lEyeP = cmds.group(em=True, n = 'l_eyeP', p= "eyeTR") 
    cmds.xform(lEyeP, ws =1, t =(lEyePos[0], lEyePos[1], lEyePos[2])) 
    lEyeRP = cmds.group(em=True, n = 'l_eyeRP', p= lEyeP )
    cmds.setAttr( lEyeRP + ".ry", lEyeRot[1] )
    cmds.setAttr( lEyeRP + ".rx", lEyeRot[0] )
    lEyeScl = cmds.group(em=True, n = 'l_eyeScl', p= lEyeRP )
    indieScaleSquach( lEyeScl, upVector )
    lEyeRot = cmds.group(em=True, n = 'l_eyeRot', p= lEyeScl )
    lEyeballRot = cmds.group(em=True, n =  'l_eyeballRot', p= lEyeRot )

    '''#under headTRS
    lEyeTransform = cmds.group( em=1, n = "L_eyeTransform", p = lDmNull )
    cmds.xform( lDmNullP, ws =1, t =(lEyePos[0], lEyePos[1], lEyePos[2] ))'''
    
    eyeGeoP = cmds.listRelatives( eyeGeoGrp , p =1 )[0]
    cmds.connectAttr( lEyeballRot + ".worldMatrix" , multMat +".matrixIn[0]"  )
    cmds.connectAttr( eyeGeoP + ".worldInverseMatrix[0]", multMat +".matrixIn[1]" )
    cmds.connectAttr( multMat +".matrixSum", lDMat + ".inputMatrix" )
    cmds.connectAttr( lDMat + ".outputTranslate",  eyeGeoGrp + ".translate" )    
    cmds.connectAttr( lDMat + ".outputRotate",  eyeGeoGrp + ".rotate" )
    cmds.connectAttr( lDMat + ".outputScale",  eyeGeoGrp + ".scale" )
    cmds.connectAttr( lDMat + ".outputShear",  eyeGeoGrp + ".shear" )         
    # "eyeAssembly_GRP" world inverseMatrix * eyeSclera worldMatrix = eye local matrix   




#RNK Jaw Setup
def mouthJoint( upLow, numCtls ): 
    
    lipEPos = cmds.xform( 'lipEPos', t = True, q = True, ws = True )
    lipWPos = [-lipEPos[0], lipEPos[1], lipEPos[2]] 
    lipNPos = cmds.xform( 'lipNPos', t = True, q = True, ws = True ) 
    lipSPos = cmds.xform( 'lipSPos', t = True, q = True, ws = True ) 
    lipYPos = cmds.xform( 'lipYPos', t = True, q = True, ws = True )
    jawRigPos = cmds.xform( 'jawRigPos', t = True, q = True, ws = True ) 
    
    if not cmds.objExists( upLow + 'Lip_grp' ):
    	lipJntGrp = cmds.group(n = upLow + 'Lip_grp', em =True, p = 'lipJotP')    	
    else:
    	lipJntGrp = upLow + 'Lip_grp'
    cmds.xform( lipJntGrp, ws = 1, t = jawRigPos)
    
    if cmds.attributeQuery( upLow + "LipVerts", node = "lipFactor", exists=1)==True:
    	orderedVerts = cmds.getAttr( "lipFactor." + upLow + "LipVerts" )            
    else:
    	cmds.warning("store lip vertices in order first!!")    
    
    vNum = len( orderedVerts )
    if upLow == "up":
    	lipCntPos = lipNPos            
    elif upLow == "lo":
    	lipCntPos = lipSPos
		#jmax = 1
		#jmax = vNum+1 :: it wont work because the curve length should be from 0 to 1
		
    #create blendShape curves for lip ( jawOpen/ happy / sad....)
    tempCrv = cmds.curve(d= 3, ep= [lipWPos, lipCntPos,lipEPos] ) 
    guideCrv = cmds.rename(tempCrv, upLow + "_guide_crv" )
    guideCrvShape = cmds.listRelatives(guideCrv, c = True) 
    cmds.rebuildCurve( guideCrv, d = 3, rebuildType = 0, keepRange = 0)    
    
    # create extra curves ( jaw drop / free form ) 
    tempflatCrv  = cmds.curve(d = 3, p =([0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0])) 
    cmds.rebuildCurve(rt = 0, d = 3, kr = 0, s = numCtls-1 )
    #cmds.rebuildCurve (browCtlCrv, rebuildType = 0, spans = numOfCtl-1, keepRange = 0, degree = 3 )         
    bsCrv   = cmds.rename( tempflatCrv, upLow + '_lipBS_crv')    
    
    jawTempCrv = cmds.duplicate( bsCrv )
    jawOpenCrv = cmds.rename( jawTempCrv[0], upLow +'_jawOpen_crv' )
    
    jawDropTempCrv = cmds.duplicate( bsCrv )
    jawDropCrv = cmds.rename( jawDropTempCrv[0], upLow +'_jawDrop_crv' )
    
    tmplipRollCrv = cmds.duplicate( bsCrv )
    lipRollCrv = cmds.rename(tmplipRollCrv, upLow + '_lipRoll_crv' )

    tmplipPuffCrv = cmds.curve(d = 3, p =([0,1,0],[0.25,1,0],[0.5,1,0],[0.75,1,0],[1,1,0])) 
    cmds.rebuildCurve(tmplipPuffCrv, rt = 0, d = 3, kr = 0, s = numCtls-1 )
    lipPuffCrv = cmds.rename( tmplipPuffCrv[0], upLow +'_lipScale_crv' )
    
    linearDist = 1.0/(vNum-1)
    lipJnts = [] 
    dropPocs=[]
    rollPocs =[]
    puffPocs = []
    cvPos = []
    increment = 0.0    
    for i in range( vNum ):
    
        guidePoc =cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = upLow +'_lipGuide' + str(i).zfill(2) + '_poc' )
        cmds.connectAttr( guideCrvShape[0] + ".worldSpace" , guidePoc + ".inputCurve" )
        cmds.setAttr( guidePoc + ".turnOnPercentage", 1 )
        cmds.setAttr( guidePoc +".parameter", increment )
        pocPos = cmds.getAttr( guidePoc + ".position")[0]
        
        lipJot = createLipJoint( upLow, jawRigPos, lipYPos, pocPos, lipJntGrp, i )
        lipJnts.append( lipJot )
        
        #tyCrv pointOnCurve
        jawDropPoc =cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = upLow +'_jawDrop' + str(i).zfill(2) + '_poc' )
        cmds.connectAttr( jawDropCrvShape[0] + ".worldSpace" , jawDropPoc + ".inputCurve" )
        cmds.setAttr( jawDropPoc + ".turnOnPercentage", 1 )
        cmds.setAttr( jawDropPoc +".parameter", increment )
        dropPocs.append(jawDropPoc)
        #get position list for hi curve
        pocPos = cmds.getAttr(jawDropPoc + ".position")[0]        
        cvPos.append( pocPos )
        
        #lipRollCrv pointOnCurve
        lipRollPoc =cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = upLow +'_lipRoll' + str(i).zfill(2) + '_poc' )
        cmds.connectAttr( lipRollCrvShape[0] + ".worldSpace" , lipRollPoc + ".inputCurve" )
        cmds.setAttr( lipRollPoc + ".turnOnPercentage", 1 )
        cmds.setAttr( lipRollPoc +".parameter", increment )  
        rollPocs.append(lipRollPoc)
		
        #lipPuffCrv pointOnCurve
        lipPuffPoc =cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = upLow +'_lipPuff' + str(i).zfill(2) + '_poc' )
        cmds.connectAttr( lipPuffCrvShape[0] + ".worldSpace" , lipPuffPoc + ".inputCurve" )
        cmds.setAttr( lipPuffPoc + ".turnOnPercentage", 1 )
        cmds.setAttr( lipPuffPoc +".parameter", increment ) 
        puffPocs.append(lipPuffPoc)
        
        increment = increment + linearDist
				
    bsHiCrv = cmds.curve( d= 1, ep= cvPos )
    newBSHiCrv = cmds.rename( bsHiCrv, upLow  + "_lipBsHiCrv" )
    bsHiCrvShape = cmds.listRelatives( newBSHiCrv, c=1, ni=1, s=1 )
    
    jawOpenHiCrv = cmds.curve( d= 1, ep= cvPos )
    jawHiCrvName = cmds.rename( jawOpenHiCrv, upLow  + "_jawOpenHiCrv" )
    jawOpenHiCrvShape = cmds.listRelatives( jawHiCrvName, c=1, ni=1, s=1 )    
    
    bsWireNode = cmds.wire( newBSHiCrv, w = bsCrv, n = upLow + "_lipBS_wire" )
    cmds.setAttr ( bsWireNode[0] + ".dropoffDistance[0]", 5 )
    jawWireNode = cmds.wire( jawHiCrvName, w = jawOpenCrv, n = upLow + "_jawOpen_wire" )
    cmds.setAttr ( jawWireNode[0] + ".dropoffDistance[0]", 5 )    
    bsPocs = []
    openPocs = [] 
    #BS/JawOpen hiCurve created
    for v in range ( vNum ):
        #get curve U value
        uParam = getUParam( cvPos[v], newBSHiCrv )
        bsHiPoc =cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = upLow +'_bsCrv' + str(v).zfill(2) + '_poc' )
        cmds.connectAttr( bsHiCrvShape[0] + ".worldSpace" , bsHiPoc + ".inputCurve", f=1 )
        cmds.setAttr(bsHiPoc + ".parameter", uParam )
        bsPocs.append(bsHiPoc)
        print uParam, v 
        
        jawOpenPoc =cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = upLow +'_jawOpen' + str(v).zfill(2) + '_poc' )
        cmds.connectAttr( jawOpenHiCrvShape[0] + ".worldSpace" , jawOpenPoc + ".inputCurve" )        
        cmds.setAttr( jawOpenPoc +".parameter", uParam )       
        openPocs.append(jawOpenPoc)

    if upLow == "lo":
        cmds.delete( lipJnts[0], lipJnts[-1], dropPocs[0], dropPocs[-1], rollPocs[0], rollPocs[-1], 
        openPocs[0], openPocs[-1], bsPocs[0], bsPocs[-1]  )#puffPocs[0], puffPocs[-1]
    else:
    	pass
    	      		
    if not cmds.objExists('lipCrv_grp'):
        lipCrvGrp = cmds.group ( n = 'lipCrv_grp', em =True, p = 'faceMain|crv_grp' )    
    cmds.parent( bsCrv, jawOpenCrv, jawDropCrv, lipRollCrv, newBSHiCrv, jawHiCrvName, 'lipCrv_grp' )
    



def setLipJntLabel():
    upJntY = cmds.ls('upLipY*_jnt', fl=1, type = 'joint')
    loJntY = cmds.ls('loLipY*_jnt', fl=1, type = 'joint')
    upJntNum = len(upJntY)
    loJntNum = len(loJntY)
    rightUp = upJntY[0:upJntNum/2]
    leftUp = upJntY[upJntNum/2+1: ]
    rightLo =loJntY[0: loJntNum/2] 
    leftLo = loJntY[loJntNum/2+1: ]
    leftLo.reverse()
    rightUp.reverse()
    leftJnt = leftUp + leftLo
    rightJnt = rightUp + rightLo
    cntJnt =[ upJntY[upJntNum/2], loJntY[loJntNum/2] ]
    for i, j in enumerate(leftJnt):
        cmds.setAttr(j + '.side', 1)
        cmds.setAttr(j + '.type', 18)
        cmds.setAttr(j + '.otherType', "lip"+str(i).zfill(2), type = "string")
    for id, k in enumerate(rightJnt):
        cmds.setAttr(k + '.side', 2)
        cmds.setAttr(k + '.type', 18)
        cmds.setAttr(k + '.otherType', "lip"+ str(id).zfill(2), type = "string")  


        
import math
def distance(inputA=[1,1,1], inputB=[2,2,2]):
    return math.sqrt(pow(inputB[0]-inputA[0], 2) + pow(inputB[1]-inputA[1], 2) + pow(inputB[2]-inputA[2], 2))    
 


def createLipJoint( upLow, jawRigPos, lipYPos, pocPos, lipJntGrp, i):
    
    # create lip joints parent group
    lipJotX  = cmds.group( n = upLow + 'LipJotX' + str(i).zfill(2), em =True, parent = lipJntGrp ) 
    lipJotY  = cmds.group( n = upLow +'LipJotY' + str(i).zfill(2), em =True, parent = lipJotX )
    cmds.xform( lipJotY, ws=1, t = [ 0, lipYPos[1], lipYPos[2]] )     
    lipYJnt  = cmds.joint( n = upLow +'LipY' + str(i).zfill(2) + "_jnt", relative = True, p = [ 0, 0, 0] )
    lipRollT = cmds.group( n = upLow +'LipRollT' + str(i).zfill(2), em =True, parent = lipYJnt )
    #cmds.setAttr ( lipJotY + ".tz", lipYPos[2] )
     
    #lip joint placement on the curve with verts tx        
    lipRollP = cmds.group( n =upLow + 'LipRollP' + str(i).zfill(2), em =True, p = lipRollT ) 
    cmds.xform ( lipRollP, ws = True, t = pocPos ) 

    lipRoll = cmds.joint(n = upLow + 'LipRoll' + str(i).zfill(2) + '_jnt', relative = True, p = [ 0, 0, 0] )
    
    return lipJotX
    


#place the lipYPos locator bigger than mouth ry arc!!  
#LipJotY0.ry = ( LipDetail0.tx + mouth_move.tx )*14
def mouthCrvToJoint( upLow ):

    # curve's Poc drive the joint
    lipJots= cmds.ls ( upLow + 'LipJotX*', fl=True, type ='transform' )
    pocList = cmds.ls ( upLow + '_bsCrv*_poc', fl=True  )
    jawPocList = cmds.ls ( upLow + '_jawOpen*_poc', fl=True, type = 'pointOnCurveInfo'   )
    jawDropPocList = cmds.ls ( upLow +'_jawDrop*_poc', fl=True, type = 'pointOnCurveInfo' )
    lipRollPocList = cmds.ls ( upLow +'_lipRoll*_poc', fl=True, type = 'pointOnCurveInfo' )
    #lipPuffPocList = cmds.ls ( upLow +'_lipPuff*_poc', fl=True, type = 'pointOnCurveInfo' )

    rollJnts = [] 
    ryJnts = []
    adList = lastJntOfChain(lipJots)
    for x, y in zip(*[iter(adList)]*2):
    	rollJnts.append(x)
    	ryJnts.append(y) 
    jotNum = len (lipJots)
    print jotNum	
	# connect with joint name
              
    for i in range ( jotNum ):			
		jotXMult = cmds.shadingNode ( 'multiplyDivide', asUtility=True, n = upLow + 'JotXRot' + str(i+1)+'_mult' )
		jotYMult = cmds.shadingNode ( 'multiplyDivide', asUtility=True, n = upLow + 'JotYRot' + str(i+1)+'_mult' )

		jotXRot_plus  = cmds.shadingNode ( 'plusMinusAverage', asUtility=True, n = upLow + 'JotXRot' + str(i+1) +'_plus' )   
		jotYRotY_plus  = cmds.shadingNode ( 'plusMinusAverage', asUtility=True, n = upLow + 'JotYRot' + str(i+1) +'_plus' )
		jotXTran_plus = cmds.shadingNode ( 'plusMinusAverage', asUtility=True, n = upLow + 'JotXTran' + str(i+1) +'_plus' )
		lipRollTran_plus = cmds.shadingNode ('plusMinusAverage', asUtility=True, n = upLow +'LipRollTran'+str(i+1)+'_plus' )
        
		poc = pocList[i]
		initialX = cmds.getAttr ( poc + '.positionX' )

		jawPoc = jawPocList[i]
		initX = cmds.getAttr ( jawPoc + '.positionX' )

		jawDropPoc = jawDropPocList[i]
		iniX = cmds.getAttr ( jawDropPoc + '.positionX' )

		lipRollPoc = lipRollPocList[i]
		#lipPuffPoc = lipPuffPocList[i]

		#JotX rotationXY connection
		#ty(input3Dy) / extra ty(input3Dx) seperate out for jawSemi
		cmds.setAttr ( jotXRot_plus + '.operation', 1 )
		cmds.connectAttr ( poc + '.positionY', jotXRot_plus + '.input3D[0].input3Dy' )
		cmds.connectAttr ( jawPoc + '.positionY', jotXRot_plus + '.input3D[1].input3Dy' ) 

		#connect translateY plusAvg to joint rotateX Mult        
		cmds.connectAttr ( jotXRot_plus + '.output3Dy', jotXMult + '.input1X' )  
		cmds.connectAttr ( "lipFactor.lipJotX_rx", jotXMult + '.input2X' ) 
		cmds.connectAttr ( jotXMult + '.outputX', lipJots[i] + '.rx' ) 

		#TranslateX( jawPoc + "swivel_ctrl") add up for upLow + 'LipJotx' .ry 
		#1. curve translateX add up for LipJotX  
		cmds.setAttr ( jotXRot_plus + '.operation', 1 ) 
		cmds.connectAttr ( jawPoc + '.positionX', jotXRot_plus + '.input3D[0].input3Dx')
		cmds.setAttr (jotXRot_plus + '.input3D[1].input3Dx', -initX )
		cmds.connectAttr ( jotXRot_plus + '.output3Dx', jotXMult + '.input1Y' ) 
		cmds.connectAttr ( "lipFactor.lipJotX_ry", jotXMult + '.input2Y' )         
		cmds.connectAttr ( jotXMult + '.outputY', lipJots[i] +'.ry' )

		#TranslateX(poc + "mouth_move") add up for upLow + 'LipJotY' .ry     
		#JotY rotationY connection
		cmds.setAttr ( jotYRotY_plus + '.operation', 1 )  
		cmds.connectAttr ( poc + '.positionX', jotYRotY_plus + '.input3D[0].input3Dx' )
		cmds.setAttr (jotYRotY_plus + '.input3D[1].input3Dx', -initialX )
		#connect with jointY + ".ry"	 
		cmds.connectAttr ( jotYRotY_plus + '.output3Dx', jotYMult + '.input1Y' ) 
		cmds.connectAttr ( "lipFactor.lipJotX_ry", jotYMult + '.input2Y' )         
		cmds.connectAttr ( jotYMult + '.outputY', ryJnts[i]+'.ry')  

		# JotX translateXYZ connection
		cmds.setAttr ( jotXTran_plus + '.operation', 1 ) 
		cmds.connectAttr ( jawDropPoc + '.positionX', jotXTran_plus + '.input3D[0].input3Dx') 
		cmds.setAttr (jotXTran_plus + '.input3D[1].input3Dx', -iniX )
		cmds.connectAttr ( jotXTran_plus + '.output3Dx', lipJots[i] +'.tx' )

		cmds.setAttr ( jotXTran_plus + '.operation', 1 ) 
		cmds.connectAttr ( jawDropPoc + '.positionY', jotXTran_plus + '.input3D[0].input3Dy') 
		cmds.connectAttr ( jotXTran_plus + '.output3Dy', lipJots[i] +'.ty' )

		cmds.setAttr ( jotXTran_plus + '.operation', 1 )
		cmds.connectAttr ( poc + '.positionZ', jotXTran_plus + '.input3D[0].input3Dz') 
		cmds.connectAttr ( jawDropPoc + '.positionZ', jotXTran_plus + '.input3D[1].input3Dz')
		cmds.connectAttr ( jawPoc + '.positionZ', jotXTran_plus + '.input3D[2].input3Dz')  
		cmds.connectAttr ( jotXTran_plus + '.output3Dz', lipJots[i] +'.tz' )     
	
		#LipRoll_rotationX connection( lipRoll_jnt.rx = lipRoll_poc.ty )
		cmds.connectAttr ( lipRollPoc+ '.positionY', rollJnts[i] +'.rx')

		#LipRoll_translateZ connection #12/26/2019
		'''cmds.setAttr ( lipRollTran_plus + '.operation', 1 ) 
		cmds.connectAttr ( lipPuffPoc + '.positionX', lipRollTran_plus + '.input3D[0].input3Dx') 
		cmds.setAttr (lipRollTran_plus + '.input3D[1].input3Dx', -iniX )
		cmds.connectAttr ( lipRollTran_plus + '.output3Dx',  rollJnts[i] + '.tx')

		cmds.setAttr ( jotXTran_plus + '.operation', 1 ) 
		cmds.connectAttr ( lipPuffPoc + '.positionY', lipRollTran_plus + '.input3D[0].input3Dy') 
		cmds.connectAttr ( lipRollTran_plus + '.output3Dy',  rollJnts[i] + '.ty')'''

		cmds.setAttr ( jotXTran_plus + '.operation', 1 ) 
		#cmds.connectAttr ( lipPuffPoc + '.positionZ', lipRollTran_plus + '.input1D[0]' )
		cmds.connectAttr ( lipRollTran_plus + '.output1D',  rollJnts[i] + '.tz')
                
        

        
   

# create "lipBS_grp" / crv blendShape
def lipCtlSetup( upLow, numCtls ):

    bsCrv = upLow + "_lipBS_crv"  
    jawOpenCrv = upLow + "_jawOpen_crv"
    jawDropCrv = upLow + "_jawDrop_crv"
    #lipRollCrv = upLow + "_lipRoll_crv"
    #lipPuffCrv = upLow + "_lipPuff_crv"    

    if not cmds.objExists('lipBS_grp'):
        lipBSGrp = cmds.group ( n = 'lipBS_grp', em =True, p = 'faceMain|crv_grp|lipCrv_grp' )
    
    if not cmds.objExists('jawOpen_grp'):
        jawOpenGrp = cmds.group ( n = 'jawOpen_grp', em =True, p = 'faceMain|crv_grp|lipCrv_grp' )
            
    #create blendShape curve
    cmds.parent( bsCrv, 'lipBS_grp' )
    cmds.parent( jawOpenCrv, 'jawOpen_grp' )
    
    lUpLow = "l_"+upLow
    rUpLow = "r_"+upLow

    lLipWideCrv   = cmds.duplicate(bsCrv,  n = lUpLow + '_lipWide', rc=1 )
    rLipWideCrv   = cmds.duplicate(bsCrv,  n = rUpLow + '_lipWide', rc=1 )
    mirrorCurve(lLipWideCrv[0], rLipWideCrv[0] )
    cmds.hide(rLipWideCrv[0] )
    
    lLipECrv    = cmds.duplicate(bsCrv,  n = lUpLow + '_E', rc=1 )
    rLipECrv    = cmds.duplicate(bsCrv,  n = rUpLow + '_E', rc=1 )  
    mirrorCurve(lLipECrv[0], rLipECrv[0])
    cmds.hide(rLipECrv[0])
    
    lUCrv       = cmds.duplicate(bsCrv,  n = lUpLow + '_U', rc=1 )
    rUCrv       = cmds.duplicate(bsCrv,  n = rUpLow + '_U', rc=1 ) 
    mirrorCurve(lUCrv[0], rUCrv[0])
    cmds.hide(rUCrv[0])
    
    lOCrv       = cmds.duplicate(bsCrv,  n = lUpLow + '_O', rc=1 ) 
    rOCrv       = cmds.duplicate(bsCrv,  n = rUpLow + '_O', rc=1 )
    mirrorCurve(lOCrv[0], rOCrv[0])
    cmds.hide(rOCrv[0])
    
    lHappyCrv  = cmds.duplicate(bsCrv,    n = lUpLow + '_Happy', rc=1 ) 
    rHappyCrv  = cmds.duplicate(bsCrv,    n = rUpLow + '_Happy', rc=1 )
    mirrorCurve(lHappyCrv[0], rHappyCrv[0])
    cmds.hide(rHappyCrv[0]) 
    
    lSadCrv  = cmds.duplicate(bsCrv,    n = lUpLow + '_Sad', rc=1 ) 
    rSadCrv  = cmds.duplicate(bsCrv,    n = rUpLow + '_Sad', rc=1 ) 
    mirrorCurve(lSadCrv[0], rSadCrv[0])
    cmds.hide(rSadCrv[0])
    
    lipCrvBS = cmds.blendShape( lLipWideCrv[0],rLipWideCrv[0], lLipECrv[0],rLipECrv[0], lUCrv[0], rUCrv[0],
    lOCrv[0], rOCrv[0], lHappyCrv[0],rHappyCrv[0], lSadCrv[0],rSadCrv[0], bsCrv, n = upLow + 'LipCrvBS' )
    cmds.blendShape(lipCrvBS[0], edit=True, w=[(0, 1),(1, 1),(2, 1),(3, 1),(4, 1),(5, 1),(6, 1),(7, 1),(8, 1),(9, 1),(10, 1),(11, 1)])
    
    #upLow + '_lipBS_crv' / upLow +'_jawOpen_crv'
    jnts = lipCtrlJntForCrv( upLow, bsCrv, "lip", numCtls )
    if upLow == "lo":
    	jntP = cmds.listRelatives( jnts, p = 1 )
    	cmds.delete( jntP[0], jntP[-1])
    	
    jots = lipCtrlJntForCrv( upLow, jawOpenCrv, "jawOpen", 3 )
    if upLow == "lo":
    	jotP = cmds.listRelatives( jots, p = 1 )
    	cmds.delete( jotP[0], jotP[-1]) 
    	    
    js = lipCtrlJntForCrv( upLow, jawDropCrv, "jawDrop", 3 )
    if upLow == "lo":
    	jtP = cmds.listRelatives( js, p = 1 )
    	cmds.delete( jtP[0], jtP[-1]) 

    #rollJnt = lipCtrlJntForCrv( upLow, lipRollCrv, "lipRoll", 5 )
    #cmds.delete( rollJnt[0], rollJnt[-1]) 
    #lipCtrlJntForCrv( upLow, lipPuffCrv, "lipPuff", numDetails )
    
    
    

#mirror left curve(cvs) to right curve(cvs), all left curves are from 0 to +x
def mirrorCurve( lCrv, rCrv):

    lCrvCv = cmds.ls( lCrv + '.cv[*]', fl =1)
    rCrvCv = cmds.ls( rCrv + '.cv[*]', fl =1)
    cvLeng = len(lCrvCv)
    
    for i in range( cvLeng ):
        mirrorAdd = cmds.shadingNode('addDoubleLinear', asUtility=True, n = 'mirror' + str(i) + '_add' )
        cmds.setAttr( mirrorAdd + '.input1', 1 )
        reversMult = cmds.shadingNode('multiplyDivide', asUtility =1, n = 'reverse%s_mult'%str(i).zfill(2))
        cmds.connectAttr( lCrvCv[i] + '.xValue', reversMult+ '.input1X')
        cmds.setAttr ( reversMult+ '.input2X', -1 )
        cmds.connectAttr ( reversMult+ '.outputX', mirrorAdd + '.input2' )
        cmds.connectAttr( mirrorAdd + '.output', rCrvCv[cvLeng-i-1] + '.xValue' )
        cmds.connectAttr( lCrvCv[i] + '.yValue', rCrvCv[cvLeng-i-1] + '.yValue' )
        cmds.connectAttr( lCrvCv[i] + '.zValue', rCrvCv[cvLeng-i-1] + '.zValue' )


     


#joint ctrl evenly on the curve 
def lipCtrlJntForCrv(upLow, crv, name, numCtls ):

    center = (numCtls-1)/2    
    increm = 1.0 / (numCtls-1)
    sequence =symmetryLetter(numCtls)         
    ctlJnts = []
    vertPos = []
    if not cmds.objExists( name+"_jntGrp" ):
        lipJntGrp = cmds.group ( n = name+"_jntGrp", em =True, p = 'faceMain|jnt_grp' )
    else:
        lipJntGrp = name+"_jntGrp"
    
    title = upLow +"_"+ name
    pocs = pocEvenOnCrv( crv, numCtls, title )
    print pocs
    for i in range( numCtls ):
    
        pos = cmds.getAttr( pocs[i] + ".position")[0]
        #create ctl joints grp
        if i == 0 :
            null = cmds.group( em=1, n = "rCorner_" + name + "_jntP", p = lipJntGrp  )
        elif i == numCtls-1 :
            null = cmds.group( em=1, n = "lCorner_" + name + "_jntP", p = lipJntGrp )

        else:
            null = cmds.group( em=1, n = upLow + "%s_"%sequence[i] + name + "_jntP", p = lipJntGrp )        	

        cmds.xform( null, ws=1, t= pos )  
        jnt = cmds.joint( p = pos,  n = null.replace("_jntP",""))
        ctlJnts.append(jnt)

    return ctlJnts





'''
def indieCrvSetup():
    #skin lip Curves 
    crvDict = { "lipBS_crv": "lip_jntGrp",  "lipPuff_crv": "lip_jntGrp", "jawDrop_crv":"jawDrop_jntGrp", "jawOpen_crv":"jawOpen_jntGrp" }
    for crv, grp in crvDict.items():
        
        ctlJnts=lastJntOfChain( grp )
        cornerJnt = [ x for x in ctlJnts if "Corner" in x ]

        if "jaw" in crv:
        	
			upMidJnt = [ y for y in ctlJnts if "up" in y ][0]
			loMidJnt = [ z for z in ctlJnts if "lo" in z ][0]
			cmds.expression( s= '%s.tx = %s.tx*0.5 - %s.ty*0.060'%(cornerJnt[0], loMidJnt, loMidJnt) )                             
			cmds.expression( s= '%s.tx = %s.tx*0.5 + %s.ty*0.060'%(cornerJnt[1], loMidJnt, loMidJnt ) )  
			cmds.expression( s= '%s.ty = %s.ty*0.5'%(cornerJnt[0], loMidJnt ) )
			cmds.expression( s= '%s.tz = %s.tz*0.5'%(cornerJnt[0], loMidJnt ) )  
			cmds.expression( s= '%s.ty = %s.ty*0.5'%(cornerJnt[1], loMidJnt ) )
			cmds.expression( s= '%s.tz = %s.tz*0.6'%(cornerJnt[1], loMidJnt ) ) 
			cmds.expression( s= '%s.tx = %s.tx*0.1'%(upMidJnt, loMidJnt ) ) 
			cmds.expression( s= '%s.ty = %s.ty*0.01'%(upMidJnt, loMidJnt) )
			cmds.expression( s= '%s.tz = %s.tz*0.01'%(upMidJnt, loMidJnt) )
            
        for upLow in ["up","lo"]:            
            
            ctlJot = [ j for j in ctlJnts if upLow in j ]    
            cmds.skinCluster( upLow+"_"+crv, ctlJot+cornerJnt, bm=0, nw=1, weightDistribution=0, mi=3, omi=True, tsb=1 )   
'''


        
def indieCrvSetup():

    #skin lip Curves 
    crvDict = { "lipBS_crv": "lip_jntGrp", "jawDrop_crv":"jawDrop_jntGrp", "jawOpen_crv":"jawOpen_jntGrp" }
    for crv, grp in crvDict.items():
    
        ctlJnts=lastJntOfChain( grp )
        cornerJnt = [ x for x in ctlJnts if "Corner" in x ]
        for upLow in ["up","lo"]:            
            
            ctlJot = [ j for j in ctlJnts if upLow in j ]    
            cmds.skinCluster( upLow+"_"+crv, ctlJot+cornerJnt, bm=0, nw=1, weightDistribution=0, mi=3, omi=True, tsb=1 )
                
        if "jaw" in crv:
            ctlName = crv.split('_')[0]
            ctl = "jaw_" + ctlName[3:].lower()
           
            lCorner_mult =cmds.shadingNode( 'multiplyDivide', asUtility =1, n = cornerJnt[1]+'_mult')
            rCorner_mult =cmds.shadingNode( 'multiplyDivide', asUtility =1, n = cornerJnt[0]+'_mult')
            corner_damp =cmds.shadingNode( 'multiplyDivide', asUtility =1, n = cornerJnt[0].split('_')[1]+'_damp')
            upMid_damp =cmds.shadingNode( 'multiplyDivide', asUtility =1, n = ctlName + 'UpDamp_mult' )
            corner_plus = cmds.shadingNode( 'plusMinusAverage', asUtility =1, n = cornerJnt[0].split('_')[1]+'_plus')
            cmds.setAttr( corner_plus + '.operation', 1 )
            
            upMidJnt = [ y for y in ctlJnts if "up" in y ][0]
            loMidJnt = [ z for z in ctlJnts if "lo" in z ][0]
                            
            #set up cornerJoint.translate damping on midJoint.translate
            if cmds.attributeQuery( "cornerTx", node = ctl, exists=1)==False:
                cmds.addAttr( ctl, ln ="cornerTx", attributeType='float', dv = .5 )
                cmds.setAttr( ctl + ".cornerTx", e =1, keyable=1 )
            
            if cmds.attributeQuery( "cornerTy", node = ctl, exists=1)==False:
                cmds.addAttr( ctl, ln ="cornerTy", attributeType='float', dv = .5 )
                cmds.setAttr( ctl + ".cornerTy", e =1, keyable=1 )
            
            if cmds.attributeQuery( "cornerTz", node = ctl, exists=1)==False:
                cmds.addAttr( ctl, ln ="cornerTz", attributeType='float', dv = .5 )
                cmds.setAttr( ctl + ".cornerTz", e =1, keyable=1 )             
        
            #left corner "jnt.tx" setup
            cmds.connectAttr( loMidJnt+'.tx',  lCorner_mult + '.input1X' )
            # adjust ctl.ornerTx to change the ratio of corner movement
            cmds.connectAttr( ctl + '.cornerTx', lCorner_mult + '.input2X') # default value :0.5   
            cmds.connectAttr( lCorner_mult + '.outputX', corner_plus + '.input2D[0].input2Dx' )
        
            cmds.connectAttr( loMidJnt+'.ty',  corner_damp + '.input1X' )
            cmds.setAttr( corner_damp + '.input2X', 0.06 )
            cmds.connectAttr( corner_damp + '.outputX', corner_plus + '.input2D[1].input2Dx' )    
            cmds.connectAttr( corner_plus + '.output2Dx', cornerJnt[1] + '.tx' )
            
            #left corner "jnt.tx"  setup    
            cmds.connectAttr( loMidJnt+'.tx',  rCorner_mult + '.input1X' )
            # adjust ctl.ornerTx to change the ratio of corner movement
            cmds.connectAttr( ctl + '.cornerTx', rCorner_mult + '.input2X') # default value :0.5
            cmds.connectAttr( rCorner_mult + '.outputX', corner_plus + '.input2D[0].input2Dy' )
            
            cmds.connectAttr( loMidJnt+'.ty',  corner_damp + '.input1Y' )
            cmds.setAttr( corner_damp + '.input2Y', -0.06 )
            cmds.connectAttr( corner_damp + '.outputY', corner_plus + '.input2D[1].input2Dy' )    
            cmds.connectAttr( corner_plus + '.output2Dy', cornerJnt[0] + '.tx' )
        
            #left corner "jnt.ty"  setup      
            cmds.connectAttr( loMidJnt+'.ty',  lCorner_mult + '.input1Y' )
            cmds.connectAttr( ctl + '.cornerTy', lCorner_mult + '.input2Y') # default value :0.5
            cmds.connectAttr( lCorner_mult + '.outputY', cornerJnt[1] + '.ty' )
            #right corner "jnt.ty"  setup             
            cmds.connectAttr( loMidJnt+'.ty',  rCorner_mult + '.input1Y' )
            cmds.connectAttr( ctl + '.cornerTy', rCorner_mult + '.input2Y') # default value :0.5
            cmds.connectAttr( rCorner_mult + '.outputY', cornerJnt[0] + '.ty' )
            #left corner "jnt.tz"  setup            
            cmds.connectAttr( loMidJnt+'.tz',  lCorner_mult + '.input1Z' )
            cmds.connectAttr( ctl + '.cornerTz', lCorner_mult + '.input2Z') # default value :0.5
            cmds.connectAttr( lCorner_mult + '.outputZ', cornerJnt[1] + '.tz' )
            #right corner "jnt.tz"  setup                 
            cmds.connectAttr( loMidJnt+'.tz',  rCorner_mult + '.input1Z' )
            cmds.connectAttr( ctl + '.cornerTz', rCorner_mult + '.input2Z') # default value :0.5      
            cmds.connectAttr( rCorner_mult + '.outputZ', cornerJnt[0] + '.tz' )
            #upMid_jnt setup    
            cmds.connectAttr( loMidJnt+'.tx',  upMid_damp + '.input1X' )
            cmds.setAttr( upMid_damp + '.input2X', 0.1 )
            cmds.connectAttr( upMid_damp + '.outputX', upMidJnt + '.tx' )    
            cmds.connectAttr( loMidJnt+'.ty',  upMid_damp + '.input1Y' )
            cmds.setAttr( upMid_damp + '.input2Y', 0.01 )
            cmds.connectAttr( upMid_damp + '.outputY', upMidJnt + '.ty' )    
            cmds.connectAttr( loMidJnt+'.tz',  upMid_damp + '.input1Z' )
            cmds.setAttr( upMid_damp + '.input2Z', 0.01 )
            cmds.connectAttr( upMid_damp + '.outputZ', upMidJnt + '.tz' )
        

            
 


def returnListLipJnt():

    lipJots= cmds.ls ( '*LipJotX*', type ='transform' )
    rollJnts = [] 
    ryJnts = []
    adList = lastJntOfChain(lipJots)
    jntNum = len(lipJots)
    loJnts= cmds.ls("loLipJotX*", type = "transform" )
    midNum = (len(loJnts)+1)/2
    for x, y in zip(*[iter(adList)]*2):
        rollJnts.append(x)
        ryJnts.append(y)

    return [lipJots, ryJnts, rollJnts]



def jawOpenDrop_setup():

    lipJnts = returnListLipJnt()
    lipJots = lipJnts[0]
    ryJnts = lipJnts[1]
    
    lipJotP = "lipJotP"
    jawSemi	= "jawSemi"
    
    '''1. jawOpen setup'''
    if cmds.objExists("jaw_open"):

        # jawOpen_crv control
        cmds.connectAttr ( 'jaw_open.tx', 'loA_jawOpen.tx' )
        cmds.connectAttr ( 'jaw_open.ty', 'loA_jawOpen.ty' )
        cmds.connectAttr ( 'jaw_open.tz', 'loA_jawOpen.tz' )
                
        jawOpenMult = cmds.shadingNode ( 'multiplyDivide', asUtility= True, n = 'jawOpen_mult' )          
        cmds.connectAttr ( 'jaw_open.tx', jawOpenMult + ".input1X")
        cmds.connectAttr ( "lipFactor.lipJotX_ry", jawOpenMult + '.input2X' )
        cmds.connectAttr ( 'jaw_open.ty', jawOpenMult + ".input1Y")
        cmds.connectAttr ( "lipFactor.lipJotX_rx", jawOpenMult + '.input2Y' )         
        cmds.connectAttr ( 'jaw_open.tz', jawOpenMult + ".input1Z")
        cmds.setAttr ( jawOpenMult + '.input2Z', 1 )  
        
        cmds.connectAttr ( jawOpenMult + ".outputX", 'jawClose_jnt.ry' )
        cmds.connectAttr ( jawOpenMult + ".outputY", 'jawClose_jnt.rx' )
        #cmds.connectAttr ( jawOpenMult + ".outputZ", 'jawClose_jnt.tz' )

    else:        
        print "create jaw_open controller frist!!"     

    if cmds.objExists("jaw_drop"):
        
        jawDropMult = cmds.shadingNode( 'multiplyDivide', asUtility= True, n = 'jawDrop_mult' )    
        
        cmds.connectAttr ( 'jaw_drop.tx', jawDropMult + ".input1X" )
        cmds.connectAttr ( 'jaw_drop.ty', jawDropMult + ".input1Y" )
        cmds.connectAttr ( 'jaw_drop.tz', jawDropMult + ".input1Z" )
        cmds.setAttr( jawDropMult + ".input2", 2, 2, 1 )
        
        #jawDrop_ctl to joint
        cmds.connectAttr ( jawDropMult+".outputX", 'loA_jawDrop.tx' )
        cmds.connectAttr ( jawDropMult+".outputY", 'loA_jawDrop.ty' )
        cmds.connectAttr ( jawDropMult+".outputZ", 'loA_jawDrop.tz' )
        
        #jawClose_jnt movement as jaw dropping 
        cmds.connectAttr ( jawDropMult+".outputX", 'jawClose_jnt.tx' )
        cmds.connectAttr ( jawDropMult+".outputY", 'jawClose_jnt.ty' )
        #cmds.connectAttr ( jawDropMult+".outputZ", 'jawClose_jnt.tz' )                
        
        #jaw_open.tz + jaw_drop.tz = jotX.tz 
        jotXTZ_add  = cmds.shadingNode ( 'addDoubleLinear', asUtility=True, n = 'jawTZ_add' )
        cmds.connectAttr ( jawOpenMult + '.outputZ', jotXTZ_add + ".input1" ) 
        cmds.connectAttr ( jawDropMult+".outputZ",  jotXTZ_add + ".input2" )
        cmds.connectAttr ( jotXTZ_add + ".output", 'jawClose_jnt.tz' )

    else:
        
        print "create jaw_drop controller frist!!"             



def swivel_ctrl_setup():
    
    lipJnts = returnListLipJnt()
    lipJots = lipJnts[0]
 
    jntNum = len(lipJots)
    loJnts= cmds.ls("loLipJotX*", type = "transform" )
    midNum = (len(loJnts)+1)/2
    jotXMults = cmds.ls( '*JotXRot*_mult', type ="multiplyDivide" )   
    jotXRot_plus = cmds.ls('*JotXRot*_plus', type = "plusMinusAverage" )
    jawSemi = "jawSemi"
    lipJotP = "lipJotP"
    
    if cmds.objExists("swivel_ctrl"):

        for i in range(jntNum):
        	        		
        	jotXRotZ_add  = cmds.shadingNode ( 'addDoubleLinear', asUtility=True, n = lipJots[i].replace('JotX','_add') )
        	cmds.connectAttr ( 'swivel_ctrl.tx', jotXRot_plus[i] + '.input3D[2].input3Dx' )
        
        	cmds.connectAttr ( 'swivel_ctrl.tx', jotXMults[i] + '.input1Z' )
        	cmds.connectAttr ( "lipFactor.lipJotX_rz", jotXMults[i] + '.input2Z' )
        	cmds.connectAttr ( jotXMults[i] + '.outputZ', jotXRotZ_add + ".input1" )        	
        	cmds.connectAttr ( 'swivel_ctrl.rz', jotXRotZ_add + ".input2" )
        	cmds.connectAttr ( jotXRotZ_add + ".output", lipJots[i] +'.rz' )
        
        swivelMult = cmds.shadingNode ( 'multiplyDivide', asUtility= True, n = 'swivel_mult' )
    	cmds.connectAttr ( 'swivel_ctrl.tx', swivelMult + '.input1X' )
    	cmds.connectAttr ( 'swivel_ctrl.ty', swivelMult + '.input1Y' )
    	cmds.connectAttr ( 'swivel_ctrl.tz', swivelMult + '.input1Z' )
    	cmds.connectAttr( "lipFactor.swivelMult_tx", swivelMult + '.input2X' )
    	cmds.connectAttr( "lipFactor.swivelMult_ty", swivelMult + '.input2Y' )
    	cmds.connectAttr( "lipFactor.swivelMult_tz", swivelMult + '.input2Z' )
    	cmds.connectAttr ( swivelMult + '.output', jawSemi + '.t' )


    	swivelJawSemiMult = cmds.shadingNode ( 'multiplyDivide', asUtility= True, n = 'swivelJawSemi_mult' )    	    
    	
    	cmds.connectAttr ( swivelMult + '.output', lipJotP +'.t', f=1 )
    	#swivel ctl control jawSemi ry / rz
    	cmds.connectAttr ( 'swivel_ctrl.tx', swivelJawSemiMult + '.input1Y' )
    	cmds.connectAttr ( 'swivel_ctrl.tx', swivelJawSemiMult + '.input1Z' )
    	cmds.connectAttr( "lipFactor.lipJotX_ry", swivelJawSemiMult + '.input2Y' )
    	cmds.connectAttr( "lipFactor.lipJotX_rz", swivelJawSemiMult + '.input2Z' )
    	cmds.connectAttr ( swivelJawSemiMult + '.outputY', jawSemi + '.ry' )
    	cmds.connectAttr ( swivelJawSemiMult + '.outputZ', jawSemi + '.rz' )
		    
    	'''scale controll'''
    	# swivel.ty + jawOpen.ty influence scaleX/Z
    	tranX_add  = cmds.shadingNode ( 'addDoubleLinear', asUtility=True, n = 'ctlX_add' )
    	tranY_plus  = cmds.shadingNode ( 'plusMinusAverage', asUtility=True, n = 'ctlY_plus' )
    	jawScale_ratio = cmds.shadingNode ( 'multiplyDivide', asUtility= True, n = 'jawScale_ratio' ) 
    	lipPcale_sum = cmds.shadingNode ( 'plusMinusAverage', asUtility= True, n = 'lipPScale_sum' )
    	tranYPowerMult = cmds.shadingNode ( 'multiplyDivide', asUtility= True, n = 'tranYPower_mult' )        
    	divideMult = cmds.shadingNode ( 'multiplyDivide', asUtility= True, n = 'tranY_divide' )
    	#lipP scale down as lipP/jawSemi goes down
        cmds.connectAttr( "jawClose_jnt.ty", tranY_plus + ".input1D[0]" )#jaw_drop.ty *1
        cmds.connectAttr( "jawSemi.ty", tranY_plus + ".input1D[1]" )#swivel_ctrl.ty * 1
        cmds.connectAttr( "jaw_open.ty", tranY_plus + ".input1D[2]" )# jaw_open.ty * 1
       
        headGeo = cmds.getAttr( "helpPanel_grp.headGeo")
        tyMax = cmds.getAttr( headGeo+"Shape.boundingBoxMax")[0]
        tyMin = cmds.getAttr( headGeo+"Shape.boundingBoxMin")[0]
        dampTy = (tyMax[1]-tyMin[1])/4
        #jawClose/jawSemi squach setup
        cmds.setAttr(tranYPowerMult + ".operation", 3 )
        cmds.expression( s= '%s.input1Y = -1*(%s.output1D/%s - 1)'%( tranYPowerMult, tranY_plus, dampTy ) )
        cmds.expression( s= '%s.input1Z = -1*(%s.output1D/%s - 1)'%( tranYPowerMult, tranY_plus, dampTy ) )        
        '''
        sqrt(4) = pow(4,0.5) = 4**0.5 // if scaleX stretchRate = 4, scaleX,Y = 1/pow(4, 0.5) = 0.5 
      
        if cmds.attributeQuery( "exponent", node = "swivel_ctrl", exists=1)==False:
            cmds.addAttr( "swivel_ctrl", ln ="exponent", attributeType='float', dv = .2 )
            cmds.setAttr( "swivel_ctrl.exponent", e =1, keyable=1 )'''
                    
        cmds.connectAttr( "lipFactor.jawSX_exponent", tranYPowerMult + ".input2Y" )
        cmds.connectAttr( "lipFactor.jawSZ_exponent", tranYPowerMult + ".input2Z" )
        
        cmds.setAttr(divideMult + ".operation", 2 )
        cmds.setAttr( divideMult + ".input1", 1,1,1 )
      
        cmds.connectAttr( tranYPowerMult + ".outputY", divideMult + ".input2Y" )
        cmds.connectAttr( tranYPowerMult + ".outputZ", divideMult + ".input2Z" )
        cmds.connectAttr( divideMult + ".outputY", lipJotP + ".sx" )
        cmds.connectAttr( divideMult + ".outputZ", lipJotP + ".sz" )
        cmds.connectAttr( divideMult + ".outputY", jawSemi + ".sx" )
        cmds.connectAttr( divideMult + ".outputZ", jawSemi + ".sz" )
        
        cmds.transformLimits(lipJotP, ty =(1, dampTy ), ety=(0,1))
        cmds.transformLimits(jawSemi, ty =(1, dampTy ), ety=(0,1))

    else:
        print "create swivel_ctrl"     


def mouth_move_setup():
    
    lipJnts = returnListLipJnt()
    ryJnts = lipJnts[1]    
    jntNum = len(ryJnts)
    jotXMults = cmds.ls( '*JotXRot*_mult', type ="multiplyDivide" ) 
    jotXRot_plus = cmds.ls('*JotXRot*_plus', type = "plusMinusAverage" )
    jotYRotY_plus = cmds.ls('*JotYRot*_plus', type = "plusMinusAverage" )         
    #mouth_move ctl connect
    if cmds.objExists("mouth_move"):

        jotYMult = cmds.ls('*JotYRot*_mult', type = "multiplyDivide")
        print jotYMult
        for t in range(jntNum):
            cmds.connectAttr ( 'mouth_move.tx', jotYRotY_plus[t] + '.input3D[3].input3Dx' )
            cmds.connectAttr ( 'mouth_move.ty', jotXRot_plus[t] + '.input3D[3].input3Dy' )                    
            jotYRotZ_add  = cmds.shadingNode ( 'addDoubleLinear', asUtility=True, n = ryJnts[t].replace('JotY','_add' ) )
            
            cmds.connectAttr ( jotYMult[t]+ '.outputZ', jotYRotZ_add + ".input1" )        	
            cmds.connectAttr ( 'mouth_move.rz', jotYRotZ_add + ".input2" )
            cmds.connectAttr ( jotYRotZ_add + ".output", ryJnts[t] +'.rz', f=1 )
    else:
        print "create mouth_move ctl"   




#create curve around lip for ctrls and select / run
#check if "*lip_nulP" created on selected curve
#sequence =['A', 'B', 'C', 'D', 'E']
#upLow = [ "up","lo"]
def lipFreeCtl( upLow, numCtls, offset, myCtl ):

    orderedVerts = cmds.getAttr( "lipFactor." + upLow + "LipVerts" )
    #create guide curve based on lipFactor vtx
    edges =[]
    numVtx = len(orderedVerts)
    for v in range(numVtx-1):
        
        cmds.select( orderedVerts[v] )
        x = cmds.polyListComponentConversion( fv=1, toEdge=1 )
        cmds.select(x, r=1 )
        edgeA= cmds.ls(sl=1, fl=1)
        cmds.select(orderedVerts[v+1], r=1 )
        y =cmds.polyListComponentConversion( fv=1, toEdge=1 )
        cmds.select(y, r=1 )
        edgeB= cmds.ls(sl=1, fl=1)
        
        common = set(edgeA) -(set(edgeA) - set(edgeB))
        edges.append(list(common)[0])
    cmds.select(cl=1)
    for e in edges:
        cmds.select(e, add=1)
    crv = cmds.polyToCurve( form=2, degree=1, n = upLow + "Lip_guide_crv")[0]
    cmds.rebuildCurve(crv, rebuildType = 0, keepRange = 0, degree = 3 )
    if not cmds.objExists('guideCrv_grp'):
        guideCrvGrp = cmds.group ( n = 'guideCrv_grp', em =True, p = 'faceMain|crv_grp' )    
    cmds.parent( crv, "guideCrv_grp" )

    cvList = cmds.ls( crv + ".cv[*]", fl=1 )
    cvLen = cmds.arclen( crv )
    cvStart = cmds.xform(cvList[0], q=1, ws=1, t=1)[0]
    cvEnd = cmds.xform( cvList[-1], q=1, ws=1, t=1)[0]
    if cvStart > cvEnd:
    	cmds.reverseCurve( crv, ch= 1, rpo=1 )
    
    if cmds.objExists( "lip_ctl_grp" )==0:
        lipCtlGrp = cmds.group ( n = "lip_ctl_grp", em =True, p = "ctl_grp" )    
    else:
        lipCtlGrp = "lip_ctl_grp"
    
    prntNull = cmds.listRelatives( lipCtlGrp, p=1 )
    if not prntNull:
        cmds.parent( lipCtlGrp, "ctl_grp" )
    
    if cmds.objExists( "lip_mainCtl_grp" ) == False:
        mainCtl_grp = cmds.group ( n = "lip_mainCtl_grp", em =True, p = lipCtlGrp )
        dtailCtl_grp = cmds.group ( n = "lip_dtailCtl_grp", em =True, p = lipCtlGrp )
        
    #curves to connect
    lipRollCrv = upLow + "_lipRoll_crv"

    #create main lip controller connect with the joints on "lipBS_crv"
    myList = symmetrNullOnCrv( upLow, crv, numCtls, "lip" )
    grpList = myList[0]

    rollCvs = cmds.ls( lipRollCrv + ".cv[*]", fl=1 )
    if not len(rollCvs) == numCtls:
    	x =cmds.rebuildCurve( lipRollCrv, rebuildType = 0, spans = numCtls-3, keepRange = 0, degree = 3 )  

    ctlColor = {"darkGrey":2, "green":23, "yellow":22,"orange":21,"pink":20,"brightGreen":19,
    "skyBlue":18, "lemon":17, "white":16, "wasabi":14, "red":13, "darkRed":12, "purple":9, "darkGreen":7,
    "blue":6, "appleRed":4, "black":1 }
    if upLow =="up":
        colorNum = ctlColor["green"]
    else:
        colorNum = ctlColor["darkGreen"]

    #create main ctrls            
    for i, null in enumerate(grpList):
        
        pos = cmds.xform( null, q=1, ws=1, t=1 )
        if myCtl:
            newCtl = cmds.duplicate( myCtl )[0]  
            #이름 수정, CtlP null에 페어런트하고 position에 옮겨놓는다.
            ctrl = customCtl(  newCtl, null.replace( "_nulP", "Ctl" ), pos )
                
        else:
            ctrl = arcController( null.replace("_nulP","Ctl"), pos, cvLen/30, "cc" )
            
        cmds.setAttr (ctrl[0] + ".overrideColor", colorNum )
        damp = cmds.shadingNode( "multiplyDivide", asUtility =1, n = ctrl[0].split("lip")[0]+"dampen"+str(i))
                
        #parent controller to null
        cmds.parent(ctrl[1], null )
        #controller offset
        cmds.setAttr( ctrl[1] + ".tz", offset )
        jnt = null.replace("_nulP","")
        cmds.connectAttr( ctrl[0] + ".tx" , damp + ".input1X" )
        cmds.setAttr( damp + ".input2X", .5 ) 
        cmds.connectAttr( damp + ".outputX", jnt+ ".tx"  )
        cmds.connectAttr( ctrl[0] + ".ty" , damp + ".input1Y" )
        cmds.setAttr( damp + ".input2Y", .5 ) 
        cmds.connectAttr( damp + ".outputY", jnt+ ".ty"  )
        cmds.connectAttr( ctrl[0] + ".tz" , damp + ".input1Z" )
        cmds.setAttr( damp + ".input2Z", .2 ) 
        cmds.connectAttr( damp + ".outputZ", jnt+ ".tz"  )
        cmds.connectAttr( ctrl[0] + ".r" , jnt+ ".r"  )
        cmds.connectAttr( ctrl[0] + ".s" , jnt+ ".s"  )
        cmds.parent( null, "lip_mainCtl_grp" )
        if upLow == "lo":
            x = i+1
        else:
            x = i

        if "Corner" not in ctrl[0]:
            cmds.connectAttr( ctrl[0] + ".rx", lipRollCrv + ".cv[%s].yValue"%str(x) )
     
    #test if it works!! 12/29/2019
    #detail poc on same lipCtl_Guide curve for lipRoll_jnt
    orderedVerts = cmds.getAttr( "lipFactor." + upLow + "LipVerts" )
    numVtx = len(orderedVerts)
    dtailPoc = pocEvenOnCrv( crv, numVtx, upLow + "LipDtail" )
    if upLow =="lo":
        dtailPoc = dtailPoc[1:-1]        
    
    #create detail ctrls
    rollJnt = cmds.ls( upLow + "LipRoll*_jnt", typ = "joint")
    for i, poc in enumerate(dtailPoc):
    	pos = cmds.getAttr( poc + ".position" )[0]
    	ctl = arcController( poc.replace("_poc","_ctl"), pos, cvLen/100, "sq" )        
    	prnt = cmds.duplicate( ctl[1], po=1, n = ctl[0].replace("_ctl","_grp"))[0]
        cmds.parent(ctl[1], prnt )
    	cmds.setAttr( ctl[1] + ".tz", offset/2 )
        cmds.connectAttr( poc + ".position", prnt + ".t" )
        cmds.setAttr (ctl[0] + ".overrideColor", 3 )
        #get the plusMinusAverage node
        print rollJnt[i], ctl[0], poc 
    	cnnt = cmds.listConnections( rollJnt[i] + ".tz", s=1, d=0, p =1 )
    	
    	plus = cnnt[0].split('.')[0]
    	cmds.connectAttr( ctl[0] + ".tx", rollJnt[i] + ".tx" )
    	cmds.connectAttr( ctl[0] + ".ty", rollJnt[i] + ".ty" )
    	cmds.connectAttr( ctl[0] + ".tz", plus + ".input1D[1]" )
    	cmds.connectAttr( ctl[0] + ".r", rollJnt[i] + ".r" )
    	cmds.connectAttr( ctl[0] + ".s", rollJnt[i] + ".s" )    	
    	#cmds.connectAttr( pocList[i] + ".position", grp + ".t" )Tue Nov 26 18:20:07 2019         
    	cmds.parent( prnt, "lip_dtailCtl_grp" ) 
    	




#corner / up / lo ctl connection
#get the "corner ctls" and "up/lo ctls" seperately in order
#connect corner + up with "up_lipPuff_crv.cv[*]"
#connect corner + lo with "lo_lipPuff_crv.cv[*]" 
def lipPuff_crvSetup( numDetails ):

    corners =[]
    for ud in ["up","lo"]:
        pocs = cmds.ls( ud + "_lipDtail*_poc", typ = "pointOnCurveInfo" )
        ctlOrder = []
        for i in range( numDetails ):
        
            cnnt = cmds.listConnections( pocs[i], d=1, type ="transform" )
            print cnnt
            if cnnt:
                child = cmds.listRelatives( cnnt[0], ad=1, type = "nurbsCurve" )[0]
                ctl = cmds.listRelatives( child, p=1)[0]
                if i == 0:
                    corners.append(ctl)
                    
                elif i == numDetails-1:
                    corners.append(ctl)
                 
                else:
                    ctlOrder.append(ctl)
        
        ctlOrder.insert(0,corners[0])
        ctlOrder.append(corners[1])
        print ctlOrder
                
        lipPuffCrv = ud + "_lipPuff_crv"
        for x, ctrl in enumerate(ctlOrder):
    	
        	xVal = cmds.getAttr(lipPuffCrv + ".cv[%s].xValue"%str(x))
        	xValMult = cmds.shadingNode('multi', asUtility=True, n = ud + 'xVal' + str(x) + '_add' )
        	cmds.setAttr( xValAdd + ".input1", xVal )
        	cmds.connectAttr( ctrl + ".tx", xValAdd + ".input2" )
        	cmds.connectAttr( xValAdd + ".output",  lipPuffCrv + ".cv[%s].xValue"%str(x) )
        	cmds.connectAttr( ctrl + ".ty",  lipPuffCrv + ".cv[%s].yValue"%str(x) )
        	#cmds.connectAttr( ctrl + ".tz",  lipPuffCrv + ".cv[%s].zValue"%str(x) )
    
    
    

# r_corner, A, B, C..., l_corner       
#put null(with lip Name) at poc node on curve evenly
def nullEvenOnCrv( crv, numCtls, name ):

    pocs =pocEvenOnCrv( crv, numCtls, name )
    center = (numCtls-1)/2
    
    nulls =[]
    for i in range( numCtls ):
        pos = cmds.getAttr( pocs[i] + ".position")[0]
        #create ctl joints grp
        null = cmds.group( em=1, n = str(i) + name + "_nulP" )        	

        cmds.xform( null, ws=1, t= pos )
        nulls.append(null) 
                
    return nulls, pocs



def symmetryLetter(numCtl): 
  
    center = (numCtl-1)/2
    corner=[]
    left = []
    right = []
    sequence = string.ascii_uppercase
    mid = [ "A" ]
    for i in range(center):        

        left.append("L_" + sequence[i+1])

        right.append("R_" + sequence[i+1])
 
    right = right[::-1]
    
    nulls = right+ mid +left       
    return nulls



# upLow = ["up", "lo", ""(for brows) ]
def symmetrNullOnCrv( upLow, crv, numCtls, name ):
    nName = upLow + "_" + name
    pocs = pocEvenOnCrv( crv, numCtls, nName )
   
    sequence = string.ascii_uppercase
    letters = symmetryLetter(numCtls)
    nulls = []
    
    if upLow in ["up", ""]:
        minNum = 0
        maxNum = numCtls
        center = (numCtls-1)/2
    elif upLow == "lo":
        minNum = 1
        maxNum = numCtls-1
        center = (numCtls-3)/2
               
    for i in range(minNum, maxNum):

        if i == 0:
            rCorner ="rCorner_" + name +"_nulP"        
            rPos = cmds.getAttr( pocs[0] + ".position")[0]
            null = cmds.group( em=1, n = "rCorner_" + name +"_nulP" )       
            cmds.connectAttr( pocs[0] + ".position", null + ".t" )
               
        elif i ==  numCtls-1 :
            lCorner ="lCorner_" + name +"_nulP"          
            lPos = cmds.getAttr( pocs[numCtls-1] + ".position")[0]
            null = cmds.group( em=1, n = "lCorner_" + name +"_nulP" )       
            cmds.connectAttr( pocs[i] + ".position", null + ".t" )
        
        else:      
            pos = cmds.getAttr( pocs[i] + ".position")[0]
            null = cmds.group( em=1, n = upLow + letters[i] + "_"+name +"_nulP"  )
            cmds.connectAttr( pocs[i] + ".position", null + ".t" )
        
        nulls.append(null)
    
    return [ nulls, pocs ]



# pocNum: number of ctls you want / returns pointOnCurve nodes evenly on curve    
def pocEvenOnCrv( crv, pocNum, title ):
    #leng = cmds.arclen( crv )
    increm = 1.0/(pocNum-1)
    crvShape = cmds.listRelatives( crv, c=1, ni=1, s=1 )     
    pocs =[]
    for n in range( pocNum ):
        
        guidePoc =cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = title+ str(n).zfill(2) + '_poc' )
        cmds.connectAttr( crvShape[0] + ".worldSpace", guidePoc + ".inputCurve" )
        cmds.setAttr( guidePoc + ".turnOnPercentage", 1 )
        cmds.setAttr( guidePoc +".parameter", increm*n )
        pocs.append(guidePoc)
    return pocs



    
# cvtxList: selection of vertices(positive) on curve / returns pointOnCurveInfo nodes parameter on curve    
def pocParamOnCrv( crv, posList, title ):

    crvShape = cmds.listRelatives( crv, c=1, ni=1, s=1 )     
    nulls = []
    pocs =[]
    for i, pos in enumerate(posList):
        
        null = cmds.group( em=1, n = title + "_null"+ str(i+1).zfill(2) )
        
        uParam = getUParam( pos, crv )
        print uParam                       
        guidePoc =cmds.shadingNode ( 'pointOnCurveInfo', asUtility= True, n = title+ str(i+1).zfill(2) + '_poc' )
        cmds.connectAttr( crvShape[0] + ".worldSpace", guidePoc + ".inputCurve" )
        #cmds.setAttr( guidePoc + ".turnOnPercentage", 1 )
        cmds.setAttr( guidePoc +".parameter", uParam )
        cmds.connectAttr(guidePoc + ".position", null + ".t" )
		        
        pocs.append(guidePoc)
        nulls.append(null)
        
    return nulls, pocs

        

        
# necessary?
def cheekSetup():

    headSkelPos = cmds.xform( 'headSkelPos', t = True, q = True, ws = True)
    JawRigPos = cmds.xform( 'jawRigPos', t = True, q = True, ws = True)
    lEyePos = cmds.xform( 'lEyePos', t = True, q = True, ws = True)
    cheekPos = cmds.xform( 'cheekPos', t = True, q = True, ws = True)
    cheekRot = cmds.xform( 'cheekPos', ro = True, q = True, ws = True)
    squintPuffPos = cmds.xform( 'squintPuffPos', t = True, q = True, ws = True)
    squintPuffRot = cmds.xform( 'squintPuffPos', ro = True, q = True, ws = True)
    lowCheekPos = cmds.xform( 'lowCheekPos', t = True, q = True, ws = True)
    LEarPos = cmds.xform( 'lEarPos', t = True, q = True, ws = True)
    nosePos = cmds.xform( 'nosePos', t = True, q = True, ws = True)
    
    supportRig = "supportRig"
    cheekPGrp = cmds.group (em =1, n = 'cheekP_grp', p = supportRig ) 
    lCheekGrp = cmds.group (em =1, n = 'l_cheek_grp', p = cheekPGrp )#ctrl by bs_poc: bs_cheek_curve 
    cmds.xform ( lCheekGrp, ws = 1, t = cheekPos )
    rCheekGrp = cmds.group (em =1, n = 'r_cheek_grp', p = cheekPGrp )#ctrl by bs_poc: bs_cheek_curve 
    cmds.xform ( rCheekGrp, ws = 1, t =[ -cheekPos[0], cheekPos[1], cheekPos[2] ] )

    lSquintPuffGrp = cmds.group (em =1, n = 'l_squintPuff_grp', p = cheekPGrp )#ctrl by bs_poc: bs_cheek_curve
    cmds.xform ( lSquintPuffGrp, ws = 1, t = squintPuffPos )
    rSquintPuffGrp = cmds.group (em =1, n = 'r_squintPuff_grp', p = cheekPGrp )#ctrl by bs_poc: bs_cheek_curve
    cmds.xform ( rSquintPuffGrp, ws = 1, t = [ -squintPuffPos[0], squintPuffPos[1], squintPuffPos[2]])
    
    lLowCheek = cmds.group (em =1, n = 'l_lowCheek_grp', p = cheekPGrp ) #ctrl by bs_poc: bs_cheek_curve
    cmds.xform ( lLowCheek, ws = 1, t = lowCheekPos )
    rLowCheek = cmds.group (em =1, n = 'r_lowCheek_grp', p = cheekPGrp ) #ctrl by bs_poc: bs_cheek_curve
    cmds.xform ( rLowCheek, ws = 1, t = [ -lowCheekPos[0], lowCheekPos[1], lowCheekPos[2]] )
    
    # cheek joint - check the cheek/squintPush group and angle
    lCheekP = cmds.group ( n = 'l_cheekP', em =True, p = lCheekGrp ) #ctrl by ctrl 
    cmds.xform (lCheekP, relative = True, t = [ 0, 0, 0] )
    lCheekJnt = cmds.joint(n = 'l_cheek_jnt', relative = True, p = [ 0, 0, 0] )

    rCheekP = cmds.group ( n = 'r_cheekP', em =True, p = rCheekGrp ) #ctrl by ctrl 
    cmds.xform (rCheekP, relative = True, t = [ 0, 0, 0] )
    rCheekJnt = cmds.joint(n = 'r_cheek_jnt', relative = True, p = [ 0, 0, 0] )  
     
    lSqiuntPuff = cmds.group ( n = 'l_squintPuffP', em =True, p = "l_squintPuff_grp" )#ctrl by bs_poc: bs_cheek_curve
    cmds.xform (lSqiuntPuff, relative = True, t = [ 0, 0, 0] )
    lSqiuntPuffJnt = cmds.joint(n = 'l_squintPuff_jnt', relative = True, p = [ 0, 0, 0] )      
    
    rSqiuntPuff = cmds.group ( n = 'r_squintPuffP', em =True, p = "r_squintPuff_grp" )#ctrl by bs_poc: bs_cheek_curve
    cmds.xform (rSqiuntPuff, relative = True, t = [ 0, 0, 0] )
    rSqiuntPuffJnt = cmds.joint(n = 'r_squintPuff_jnt', relative = True, p = [ 0, 0, 0] ) 

    lLowCheek = cmds.group ( n = 'l_lowCheekP', em =True, p = "l_lowCheek_grp" )#ctrl by bs_poc: bs_cheek_curve
    cmds.xform (lLowCheek, relative = True, t = [ 0, 0, 0] ) 
    lLowCheekJnt = cmds.joint(n = 'l_lowCheek_jnt', relative = True, p = [ 0, 0, 0] )     
    
    rLowCheek = cmds.group ( n = 'r_lowCheekP', em =True, p = "r_lowCheek_grp" )#ctrl by bs_poc: bs_cheek_curve
    cmds.xform (rLowCheek, relative = True, t = [ 0, 0, 0] ) 
    rLowCheekJnt = cmds.joint(n = 'r_lowCheek_jnt', relative = True, p = [ 0, 0, 0] )  

#################################################

def lipFactorWIP():

    #swivel factors
    cmds.addAttr('faceFactors', longName= 'swivel_lipJntP_tx', attributeType='float', dv = 1 )
    cmds.addAttr('faceFactors', longName= 'swivel_lipJntP_ty', attributeType='float', dv = 2 )
    cmds.addAttr('faceFactors', longName= 'swivel_lipJntX_ry', attributeType='float', dv =6)
    cmds.addAttr('faceFactors', longName= 'swivel_lipJntX_rz', attributeType='float', dv =15)
    cmds.addAttr('faceFactors', longName= 'swivel_lipJntP_sx', attributeType='float', dv =0.05 )
    cmds.addAttr('faceFactors', longName= 'swivel_lipJntP_sz', attributeType='float', dv =0.02 )
     
    #UDLR   
    cmds.addAttr('faceFactors', longName= 'UDLR_TX_scale', attributeType='float', dv =1 )
    cmds.addAttr('faceFactors', longName= 'UDLR_TY_scale', attributeType='float', dv =1.5 )
    #UDLR drive lip joint and jawClose
    cmds.addAttr('faceFactors', longName= 'txSum_lipJntX_tx', attributeType='float', dv =2 )
    cmds.addAttr('faceFactors', longName= 'tySum_lipJntX_ty', attributeType='float', dv =2 )
    cmds.addAttr('faceFactors', longName= 'UDLR_jawCloseTY', attributeType='float', dv =3 )
    cmds.addAttr('faceFactors', longName= 'UDLR_jawCloseTZ', attributeType='float', dv =2 )
     
    cmds.addAttr('faceFactors', longName= 'tzSum_lipJntX_tz', attributeType='float', dv =1.5 )
    cmds.addAttr('faceFactors', longName= 'tySum_lipJntX_rx', attributeType='float', dv =-20 )
    cmds.addAttr('faceFactors', longName= 'txSum_lipJntX_ry', attributeType='float', dv =6 )
 
     
    #jawOpen
    cmds.addAttr('faceFactors', longName= 'jawOpenTX_scale', attributeType='float', dv =1.5 ) 
    cmds.addAttr('faceFactors', longName= 'jawOpenTY_scale', attributeType='float', dv =2 )  
    cmds.addAttr('faceFactors', longName= 'jawOpen_jawCloseRX', attributeType='float', dv = -36 )
    cmds.addAttr('faceFactors', longName= 'jawOpen_jawCloseRY', attributeType='float', dv = 8 )
     
    #mouth_move : lipJotY* only driven by lipCtrl(freeform) / mouth_move
    cmds.addAttr('faceFactors', longName= 'mouth_lipJntX_rx', attributeType='float', dv =-20 )
    cmds.addAttr('faceFactors', longName= 'mouth_lipJntY_ry', attributeType='float', dv = 14 ) 
    cmds.addAttr('faceFactors', longName= 'mouth_lipJntY_rz', attributeType='float', dv = 7 )
     
    #cmds.addAttr('faceFactors', longName= 'move_RZscale', attributeType='float', dv =1 )
    cmds.addAttr('faceFactors', longName= 'txSum_lipJntY_ry', attributeType='float', dv =14 )
    cmds.addAttr('faceFactors', longName= 'txSum_lipJntY_rz', attributeType='float', dv =7 )

    #lipRoll 
    cmds.addAttr('faceFactors', longName= 'YZPoc_rollJntT_ty', attributeType='float', dv =1.5 )
    cmds.addAttr('faceFactors', longName= 'YZPoc_rollJntT_tz', attributeType='float', dv =2 )
##########################################################

def faceFactorFix():
    if not cmds.objExists("lipFactor"):
        
        lipFactor = cmds.createNode('transform', n = "lipFactor")
    else:
        lipFactor = "lipFactor"
        
	cmds.addAttr(lipFactor, longName= 'lipJotX_tx', attributeType='float', dv =2 )
	cmds.addAttr(lipFactor, longName= 'lipJotX_ty', attributeType='float', dv =2 )        
	cmds.addAttr(lipFactor, longName= 'lipJotX_tz', attributeType='float', dv =1.5 )
	cmds.addAttr(lipFactor, longName= 'lipJotX_rx', attributeType='float', dv =-20  )
	cmds.addAttr(lipFactor, longName= 'lipJotX_ry', attributeType='float', dv =6  )
	cmds.addAttr(lipFactor, longName= 'lipJotX_rz', attributeType='float', dv =12  )

	cmds.addAttr(lipFactor, longName= 'lipJotY_ry', attributeType='float', dv =14 )
	cmds.addAttr(lipFactor, longName= 'lipJotY_rz', attributeType='float', dv =7 )
	 
	cmds.addAttr(lipFactor, longName= 'swivelMult_tx', attributeType='float', dv =.25 )
	cmds.addAttr(lipFactor, longName= 'swivelMult_ty', attributeType='float', dv =.5 )
	cmds.addAttr(lipFactor, longName= 'swivelMult_tz', attributeType='float', dv =.25 )
		    
    cmds.addAttr(lipFactor, longName= 'jawSX_exponent', attributeType='float', dv =.2 )	
    cmds.addAttr(lipFactor, longName= 'jawSZ_exponent', attributeType='float', dv =.05 )    

    if not cmds.objExists("lidFactor"):
        
        lidFactor = cmds.createNode('transform', n = "lidFactor")
    else:
        lidFactor = "lidFactor"
        
    cmds.addAttr(lidFactor, longName= 'wide_rxRatio', attributeType='float', dv = 1 )
    cmds.addAttr(lidFactor, longName= 'wide_ryRatio', attributeType='float', dv =.5 )
    
           
'''
def mouthCtlToCrv():    
     
	#1. swivel setup
	jotXMults = cmds.ls( '*JotXRot*_mult', type ="multiplyDivide" )
	lipJots= cmds.ls ( '*LipJotX*', type ='transform' )
	rollJnts = [] 
	ryJnts = []
	adList = lastJntOfChain(lipJots)
	jntNum = len (lipJots)
	loJnts= cmds.ls("loLipJotX*", type = "transform")
	midNum = (len(loJnts)-1)/2
	for x, y in zip(*[iter(adList)]*2):
		rollJnts.append(x)
		ryJnts.append(y) 

	for i in range(jntNum):        
		if cmds.objExists("swivel_ctrl"):
		
			jotXRotZ_add  = cmds.shadingNode ( 'addDoubleLinear', asUtility=True, n = upLow + 'JotX' + str(i) +'_add' )
			cmds.connectAttr ( 'swivel_ctrl.tx', jotXMults[i] + '.input1Y' )
			cmds.connectAttr ( "lipFactor.lipJotX_ry", jotXMults[i] + '.input2Y' )        	
			cmds.connectAttr ( jotXMults[i]+ '.outputY', lipJots[i] +'.ry')
		
			cmds.connectAttr ( 'swivel_ctrl.tx', jotXMults[i] + '.input1Z' )
			cmds.connectAttr ( "lipFactor.lipJotX_rz", jotXMults[i] + '.input2Z' )
			cmds.connectAttr ( jotXMults[i] + '.outputZ', jotXRotZ_add + ".input1" )        	
			cmds.connectAttr ( 'swivel_ctrl.rz', jotXRotZ_add + ".input2" )
			cmds.connectAttr ( jotXRotZ_add + ".output", lipJots[i] +'.rz' )
			
	cmds.connectAttr ( 'swivel_ctrl.tx', 'jawSemi.tx' )
	cmds.connectAttr ( 'swivel_ctrl.ty', 'jawSemi.ty' )
	cmds.connectAttr ( 'swivel_ctrl.tz', 'jawSemi.tz' )       	
	cmds.connectAttr ( jotXMults[midNum] + '.outputY', 'jawSemi.ry' )
	jotX_add =  'loJotX' + midNum +'_add'
	cmds.connectAttr ( jotX_add + ".output", 'jawSemi.rz' )

	cmds.connectAttr ( 'swivel_ctrl.tx', 'lipJotP.tx', f=1 )
	cmds.connectAttr ( 'swivel_ctrl.ty', 'lipJotP.ty', f=1 )
	cmds.connectAttr ( 'swivel_ctrl.tz', 'lipJotP.tz', f=1 )
		    
	# swivel.ty mainly control lipJotP.ty
	tranX_add  = cmds.shadingNode ( 'addDoubleLinear', asUtility=True, n = 'ctlX_add' )
	tranY_add  = cmds.shadingNode ( 'addDoubleLinear', asUtility=True, n = 'ctlY_add' )
	lipPScale_sum = cmds.shadingNode ( 'plusMinusAverage', asUtility= True, n = 'lipPScale_sum' )
	swivelTranYMult = cmds.shadingNode ( 'multiplyDivide', asUtility= True, n = 'ctlTranYMult' )        
	#lipP scale down as lipP/jawSemi goes down


	cmds.setAttr (lipPScale_sum+'.input2D[0].input2Dx', 1 )
	cmds.setAttr (lipPScale_sum+'.input2D[0].input2Dy', 1 )             
	cmds.connectAttr ("lipFactor.lipJntP_sx", swivelTranYMult + '.input2X' )        
	cmds.connectAttr ("lipFactor.lipJntP_sz", swivelTranYMult + '.input2Z' )
	cmds.connectAttr ( swivelTranYMult + '.outputX', lipPScale_sum+'.input2D[1].input2Dx' )
	cmds.connectAttr ( swivelTranYMult + '.outputZ', lipPScale_sum+'.input2D[1].input2Dy' )
	cmds.connectAttr ( lipPScale_sum + '.output2Dx', 'lipJotP.sx' )
	cmds.connectAttr ( lipPScale_sum + '.output2Dy', 'lipJotP.sz' )
	cmds.connectAttr ( lipPScale_sum + '.output2Dx', 'jawSemi.sx' )
	cmds.connectAttr ( lipPScale_sum + '.output2Dy', 'jawSemi.sz' )
	  
	cmds.connectAttr(UDLRTscaleMult + '.outputX', lipPScaleSum +'.input2D[2].input2Dx')
	cmds.connectAttr(UDLRTscaleMult + '.outputZ', lipPScaleSum +'.input2D[2].input2Dy') 

	##########expression("jawSemi.sx" = 1+ ("swivel_ctrl.ty"*0.05 + "jawOpen_ctrl.ty"*0.05 )
	##########"jawSemi.sz" = 1+ ("swivel_ctrl.ty"*0.02 + "jawOpen_ctrl.ty"*0.02 ))      
         
	#jaw_UDLRIO.ty --> 1.lipJotX0.ty / 2. lipJotP.sx. sz / jaw_UDLRIO.tx --> lipJotX0.tz
	if not cmds.listConnections('lowJaw_dir', d =1 ):   
		jawOpenMult = cmds.shadingNode ('multiplyDivide', asUtility = 1, n = 'jawOpen_mult' )         
		jawOpen_jnt = indiCrvSetup('JawOpen')
		cmds.connectAttr( 'lowJaw_dir.tx',  jawOpenMult + '.input1X' )
		cmds.connectAttr( "faceFactors.jawOpenTX_scale",  jawOpenMult + '.input2X' )
		cmds.connectAttr( jawOpenMult + '.outputX', jawOpen_jnt + '.tx' )
	 
		cmds.connectAttr( 'lowJaw_dir.ty',  jawOpenMult + '.input1Y' )
		cmds.connectAttr( "faceFactors.jawOpenTY_scale",  jawOpenMult + '.input2Y' )
		cmds.connectAttr( jawOpenMult + '.outputY', jawOpen_jnt + '.ty' )

		jawCloseRotMult = cmds.shadingNode ('multiplyDivide', asUtility = 1, n = 'jawCloseRot_mult' )        
		# jawClose_jnt.rx = lowJaw_dir.ty * 36  
		cmds.connectAttr ( 'lowJaw_dir.ty', jawCloseRotMult + '.input1X' )
		cmds.connectAttr ( 'faceFactors.jawOpen_jawCloseRX', jawCloseRotMult + '.input2X' )     
		cmds.connectAttr ( jawCloseRotMult + '.outputX', 'jawClose_jnt.rx' )
		 
		cmds.connectAttr ( 'lowJaw_dir.tx', jawCloseRotMult + '.input1Y' )
		cmds.connectAttr ( 'faceFactors.jawOpen_jawCloseRY', jawCloseRotMult + '.input2Y' )     
		cmds.connectAttr ( jawCloseRotMult + '.outputY', 'jawClose_jnt.ry' )        
     
	if not cmds.listConnections('jaw_UDLR', d =1 ):
		UDLRT_mult = cmds.shadingNode ('multiplyDivide', asUtility = 1, n = 'UDLR_mult')
		UDLRTscale_mult = cmds.shadingNode ('multiplyDivide', asUtility = 1, n = 'UDLRscale_mult')
		jawCloseTranMult = cmds.shadingNode ('multiplyDivide', asUtility = 1, n = 'jawCloseTran_mult' )
		jawUDLR_jnt = indiCrvSetup('TyLip')
		cmds.connectAttr( 'jaw_UDLR.tx',  UDLRT_mult + '.input1X' )
		cmds.connectAttr( "faceFactors.UDLR_TX_scale",  UDLRT_mult + '.input2X' )
		cmds.connectAttr( UDLRT_mult + '.outputX', jawUDLR_jnt + '.tz' )

		cmds.connectAttr( 'jaw_UDLR.ty',  UDLRT_mult + '.input1Y' )
		cmds.connectAttr( "faceFactors.UDLR_TY_scale",  UDLRT_mult + '.input2Y' )
		cmds.connectAttr( UDLRT_mult + '.outputY', jawUDLR_jnt + '.ty' )
		    
		# jaw_UDLRIO.ty --> 1.lipJotX0.ty / 2. lipJotP.sx. sz / jaw_UDLRIO.tx --> lipJotX0.tz                
		cmds.connectAttr ( 'jaw_UDLR.ty', UDLRTscale_mult + '.input1X' )
		cmds.connectAttr ( 'jaw_UDLR.ty', UDLRTscale_mult + '.input1Z' )
		cmds.connectAttr ( "faceFactors.swivel_lipJntP_sx", UDLRTscale_mult + '.input2X')        
		cmds.connectAttr ( "faceFactors.swivel_lipJntP_sz", UDLRTscale_mult + '.input2Z')
		cmds.connectAttr ( UDLRTscale_mult + '.outputX', lipPScale_sum+'.input2D[2].input2Dx' )
		cmds.connectAttr ( UDLRTscale_mult + '.outputZ', lipPScale_sum+'.input2D[2].input2Dy' )        
		 
		# jawClose_jnt.ty = UDLR.ty * 2   / jawClose_jnt.tz = UDLR.tx * 1.1     
		cmds.connectAttr ( 'jaw_UDLR.tx', jawCloseTranMult + '.input1X' )
		cmds.connectAttr ( 'faceFactors.UDLR_jawCloseTZ', jawCloseTranMult + '.input2X' )       
		cmds.connectAttr ( jawCloseTranMult + '.outputX', 'jawClose_jnt.tz' )     
		 
		cmds.connectAttr ( 'jaw_UDLR.ty', jawCloseTranMult + '.input1Y' )
		cmds.connectAttr ( 'faceFactors.UDLR_jawCloseTY', jawCloseTranMult + '.input2Y' )       
		cmds.connectAttr ( jawCloseTranMult + '.outputY', 'jawClose_jnt.ty' )'''





def extraCrvToJoint():
        #tyPoc =cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = upLow +'LipTy' + str(i).zfill(2) + '_poc' )
        TYpoc = upLow +'_jawDrop' + str(i).zfill(2) + '_poc'
        initJawDropX = cmds.getAttr ( TYpoc + '.positionX' )
        initJawDropY = cmds.getAttr ( TYpoc + '.positionY' )
        
        ctlPoc = upLow +'_free' + str(i).zfill(2) + '_poc'
        initialCtlX = cmds.getAttr ( ctlPoc + '.positionX' )
        initialCtlY = cmds.getAttr ( ctlPoc + '.positionY' )
        
        #joint(LipJotX) translateX driven by poc positionX sum
        cmds.connectAttr ( TYpoc + '.positionX', jotXPosAvg + '.input3D[0].input3Dx' ) 
        cmds.setAttr ( jotXPosAvg + '.input3D[1].input3Dx', -initialTYX )        
        cmds.connectAttr ( jotXPosAvg + '.output3Dx', jotXPosMult + '.input1X' )  
        cmds.connectAttr ( 'faceFactors.txSum_lipJnt_tx', jotXPosMult + '.input2X' ) 
        cmds.connectAttr ( jotXPosMult + '.outputX', upLow + 'LipJotX'+ str(i) + '.tx' )
         
        #2. poc positionY,Z sum drive joint("lipJotX") translateY,Z
        cmds.connectAttr ( TYpoc + '.positionY',  jotXPosAvg + '.input3D[0].input3Dy' )
        cmds.connectAttr ( jotXPosAvg + '.output3Dy', jotXPosMult + '.input1Y' )
        cmds.connectAttr ( 'faceFactors.tySum_lipJnt_ty', jotXPosMult + '.input2Y' )  
        cmds.connectAttr ( jotXPosMult + '.outputY', upLow + 'LipJotX'+str(i)+'.ty' )     
        
        # joint(LipJotX) translateZ driven by poc positionZ sum
        cmds.connectAttr ( TYpoc + '.positionZ', jotXPosAvg + '.input3D[0].input3Dz' )
        cmds.connectAttr ( poc + '.positionZ', jotXPosAvg + '.input3D[1].input3Dz' ) 
        cmds.connectAttr ( jotXPosAvg + '.output3Dz', jotXPosMult + '.input1Z' )
        cmds.setAttr ( jotXPosMult + '.input2Z', 2 ) 
        cmds.connectAttr ( jotXPosMult + '.outputZ', upLow + 'LipJotX'+ str(i) + '.tz' )          
        
        #3. LipCtlCrv Poc.positionX + LipDetail.tx for LipJotY 
        # mouth_move.tx --> lipJotY0.ry .rz /mouth_move.rz --> lipJotY0.rz
        cmds.connectAttr ( ctlPoc + '.positionX', plusTXAvg + '.input3D[0].input3Dy' )  
        cmds.setAttr ( plusTXAvg + '.input3D[1].input3Dy', -initialCtlX )  
        cmds.connectAttr ( 'mouth_move.tx' , plusTXAvg + '.input3D[3].input3Dy' )
        cmds.connectAttr (  plusTXAvg + '.output3Dy', jotYMult + '.input1Y' )          
        cmds.connectAttr ( 'faceFactors.txSum_lipJotY_ry', jotYMult + '.input2Y' )   
        cmds.connectAttr ( jotYMult + '.outputY', upLow+'LipJotY'+str(i)+'.ry' ) 
        
        cmds.connectAttr ( 'mouth_move.tx', jotYMult + '.input1Z' )          
        cmds.connectAttr ( 'faceFactors.txSum_lipJotY_rz', jotYMult + '.input2Z' )   
        cmds.connectAttr ( jotYMult + '.outputZ', upLow+'LipJotY'+str(i)+'.rz' )




# place curve at the origin(0,0,0)        
def getUParam( pnt = [], crv = None):

    point = OpenMaya.MPoint(pnt[0],pnt[1],pnt[2])
    curveFn = OpenMaya.MFnNurbsCurve(getDagPath(crv))
    paramUtill=OpenMaya.MScriptUtil()
    paramPtr=paramUtill.asDoublePtr()
    isOnCurve = curveFn.isPointOnCurve(point)
    if isOnCurve == True:
        
        curveFn.getParamAtPoint(point , paramPtr,0.001,OpenMaya.MSpace.kObject )
    else :
        point = curveFn.closestPoint(point, paramPtr,0.001, OpenMaya.MSpace.kObject)
        curveFn.getParamAtPoint(point , paramPtr,0.001, OpenMaya.MSpace.kObject )
    
    param = paramUtill.getDouble(paramPtr)  
    return param
    

            


def getDagPath(objectName):
    '''
    This function let you get an MObject from a string representing the object name
    @param[in] objectName : string , the name of the object you want to work on 
    '''
    if isinstance(objectName, list)==True:
        oNodeList=[]
        for o in objectName:
            selectionList = OpenMaya.MSelectionList()
            selectionList.add(o)
            oNode = OpenMaya.MObject()
            selectionList.getDagPath(0, oNode)
            oNodeList.append(oNode)
        return oNodeList
    else:
        selectionList = OpenMaya.MSelectionList()
        print selectionList, objectName
        selectionList.add(objectName)
        oNode = OpenMaya.MDagPath()
        selectionList.getDagPath(0, oNode)
        return oNode
        
        

#curve rename
def renameCrvShape( crvs ):
    
    for crv in crvs:
        crvChild = cmds.listRelatives( crv, c=1, fullPath=1, typ = "nurbsCurve")[0]
        print crvChild
        shape = crvChild.split("|")[-1]
        if not crv in shape:
            name = cmds.rename( crvChild, crv + "Shape")
        
        if len(cmds.ls(name))>1:
            cmds.confirmDialog( title='Confirm', message="more than 1 %s exists"%name )


#rename, parent Null and place it on the position
#이름 수정, CtlP null에 페어런트하고 position에 옮겨놓는다.
def customCtl(  obj, ctlName, position ):        
    
    nCtl = cmds.rename( obj, ctlName )

    topNd = cmds.duplicate( nCtl, po=1, n= nCtl+"P" )
    cmds.parent( nCtl, topNd[0])     
    cmds.xform (topNd[0], ws = True, t = position )

    ctrl = [nCtl, topNd[0]]
    return ctrl


                
""" create circle controller(l_/r_/c_) and parent group at the position
    shape : circle = cc / square = sq 
    colorNum : 13 = red, 15 = blue, 17 = yellow, 18 = lightBlue, 20 = lightRed, 23 = green
    return [ ctrl, ctrlP ]
24 똥색 / 23:숙색 / 22:밝은 노랑 / 21:밝은 주황 / 20: 밝은 핑크 / 19: 밝은연두 / 18: 하늘색 / 17 yellow / 16 white
15: dark blue / 14: bright green / 13: red / 12: red dark 자두색 / 11: 고동색 / 10: 똥색 / 9: 보라 / 8: 남보라
7: 녹색 / 6: 파랑 / 5 : 남색 / 4 : 주황 / 3 : 회색 / 2: 진회색 / 1: 검정"""
def arcController( ctlName, position, radius, ctlShape ):
    if ctlShape == "cc":

        colorNum = [17, 6, 13, 23]
        ctrl = cmds.circle ( ch=False, nr=(0, 0, 1), c=(0, 0, 0), sw=360, r= radius, d=3, s=8 )[0]
        
    elif ctlShape =="sq" :

        colorNum = [10, 18, 20, 23]
        ctrl = cmds.circle ( ch=False, nr=(0, 0, 1), c=(0, 0, 0), sw=360, r= radius, d=1, s=4 )[0]
        
    else:
        colorNum = [17, 6, 13, 23]
        ctrl = cmds.circle ( ch=False, nr=(0, 0, 1), c=(0, 0, 0), sw=360, r= radius, d=1, s=4 )[0]
        ctlShapeSwap( source, transform ) 
            
    
    if ctlName[:2]=="c_":
        #if center, color override is yellow
        arCtrl = cmds.rename( ctrl, ctlName ) 
        cmds.setAttr ( arCtrl +".overrideEnabled", 1)
        cmds.setAttr ( arCtrl +".overrideShading", 0)
        cmds.setAttr ( arCtrl + ".overrideColor", colorNum[0] )
        null = cmds.group ( arCtrl, w =True, n = arCtrl + "P" )
        cmds.xform (null, ws = True, t = position )
     
    elif ctlName[:2]=="l_":
        #if left, color override is blue
        arCtrl = cmds.rename( ctrl, ctlName )
        cmds.setAttr ( arCtrl +".overrideEnabled", 1)
        cmds.setAttr ( arCtrl +".overrideShading", 0)
        cmds.setAttr ( arCtrl + ".overrideColor", colorNum[1] )
        null = cmds.group ( arCtrl, w =True, n = arCtrl +"P" )
        cmds.xform (null, ws = True, t = position )
     
    elif ctlName[:2]=="r_":
        #if right, color override is red
        arCtrl = cmds.rename( ctrl, ctlName )
        cmds.setAttr ( arCtrl +".overrideEnabled", 1)
        cmds.setAttr ( arCtrl +".overrideShading", 0)
        cmds.setAttr ( arCtrl + ".overrideColor", colorNum[2] )
        null = cmds.group ( arCtrl, w =True, n = arCtrl +"P")
        cmds.xform (null, ws = True, t = position )
 
    else :
        #if none of c_, l_, r_
        arCtrl = cmds.rename( ctrl, ctlName )
        cmds.setAttr ( arCtrl +".overrideEnabled", 1 )
        cmds.setAttr ( arCtrl +".overrideShading", 0 )
        cmds.setAttr ( arCtrl + ".overrideColor", colorNum[3] )
        null = cmds.group ( arCtrl, w =True, n =  arCtrl +"P")
        cmds.xform (null, ws = True, t = position )
    
    ctrl = [ arCtrl, null ] 
    return ctrl








def LRBlendShapeWeight( lipCrv, lipCrvBS):
    cvs = cmds.ls(lipCrv+'.cv[*]', fl =1)
    length = len (cvs)
    
    increment = 1.0/(length-1)
    targets = cmds.aliasAttr( lipCrvBS, q=1)
    tNum = len(targets)   
    
    for t in range(0, tNum, 2):
        if targets[t][0] == 'l' :
            indexL=re.findall('\d+', targets[t+1])
            cmds.setAttr(lipCrvBS + '.inputTarget[0].inputTargetGroup[%s].targetWeights[%s]'%(str(indexL[0]), str(length/2)), .5 ) 
            for i in range(0, length/2):                
                cmds.setAttr(lipCrvBS + '.inputTarget[0].inputTargetGroup[%s].targetWeights[%s]'%(str(indexL[0]), str(i)), 0 ) 
                cmds.setAttr(lipCrvBS + '.inputTarget[0].inputTargetGroup[%s].targetWeights[%s]'%(str(indexL[0]), str(length-i-1)), 1 )   
                
        if targets[t][0] == 'r' :
            indexR=re.findall('\d+', targets[t+1])
            cmds.setAttr(lipCrvBS + '.inputTarget[0].inputTargetGroup[%s].targetWeights[%s]'%(str(indexR[0]), str(length/2)), .5 ) 
            for i in range(0, length/2):                
                cmds.setAttr(lipCrvBS + '.inputTarget[0].inputTargetGroup[%s].targetWeights[%s]'%(str(indexR[0]), str(i)), 1 ) 
                cmds.setAttr(lipCrvBS + '.inputTarget[0].inputTargetGroup[%s].targetWeights[%s]'%(str(indexR[0]), str(length-i-1)), 0 )



# list selected vertices in order( starting with first selected vert )
def loopVertices_inOrder( myVert ):

    firstVert = myVert[0]
    orderedVerts = [firstVert]   
    cmds.select( firstVert, r=1 )
    mel.eval('ConvertSelectionToEdges')
    vtxEdges = cmds.ls(sl=1, fl=1)
    
    while len(myVert)>1:
    
        myVert.remove(firstVert)
        print len(myVert)
               
        for vt in myVert:            
            cmds.select( vt, r=1 )
            mel.eval('ConvertSelectionToEdges')
            tmpEdges = cmds.ls( sl=1, fl=1 )               
            xx = set(vtxEdges) - (set(vtxEdges) - set(tmpEdges))
            if xx:
                firstVert = vt
                print firstVert
                orderedVerts.append(firstVert)
                vtxEdges = tmpEdges
                break # without it, 이미 순서대로 정렬되있는 경우 myVert에서 firstVert를 빼지않고 계속 loop 한다!!                                
                  
    return orderedVerts



# distance로 계산하므로 vtx 간 거리가 불규칙할 경우() 순서대로 선택해야 한다.
def vertices_distanceOrder( myVert ):    
    
    firstVert = myVert[0]
    orderedVerts = [firstVert]   
    
    while len(myVert)>1:
    
        myVert.remove(firstVert)
        firstPos = cmds.xform( firstVert, q=1, ws=1, t=1 )   
        
        vertDist = {}
        for vt in myVert:            
            
            vtPos = cmds.xform( vt, q=1, ws=1, t=1 )
            dist = distance( firstPos, vtPos)
            
            vertDist[ vt ] = dist    
        
        print vertDist
        secondVert = min(vertDist, key= vertDist. get) 
        print secondVert    
    
        orderedVerts.append(secondVert)
        firstVert = secondVert
                                
    return orderedVerts

    
'''create brow curve for browMapSurf'''
#select verices in order to create referece curve/  
#turn off symmetry select / turn on tracking selection 
#select vertices in order(left half) or select start vert first / end vert last
#automatrically select right half in order using browCurve() with "closestPointOnMesh" to complete curve.
def curve_halfVerts( myVert, name, openClose, degree ):
   
    vertNum = len(myVert)
    orderedBrow = []
    if "brow" in name:
        
        orderedBrow = vertices_distanceOrder( myVert )
        
        if orderedBrow:
            
            mapCrv = mapCurve( orderedBrow, name, openClose, degree )
            #mapEPCurve( ordered, name, openClose, degree ) ''' 3degree epCurve create extra 2 CVs'''
        
    else:
        mapCrv = mapCurve( myVert, name, openClose, degree )
        #mapEPCurve( myVert, name, openClose, degree )
              
    # keepRange 0 - reparameterize the resulting curve from 0 to 1
    crvRebuild = cmds.rebuildCurve( mapCrv, ch =0, rpo =1, kr=0, kcp=1, kep=1, d= int(degree), n = name )
    if cmds.listHistory(crvRebuild[0]):
        cmds.delete( crvRebuild[0], ch=1 )


def EPCurve_chordLength():
    vtx = cmds.ls( os=1, fl=1 )
    vt = cmds.xform( vtx[0], q=1, t=1, ws=1)
    orderPos =[]
    # verts selection is only left part
    if vt[0]**2 <0.001:
	    for t in vtx[1:][::-1]:
		    vtxPos = cmds.xform( t, q=1, t=1, ws=1)
		    mrrPos = [-vtxPos[0],vtxPos[1],vtxPos[2]]
		    if vtxPos[0]-mrrPos[0]>0.001:
			    orderPos.append(mrrPos)        
	    print len(orderPos), 
	    for v in vtx:		    
		    vtxPos = cmds.xform( v, q=1, t=1, ws=1)
		    orderPos.append(vtxPos)

    coords = orderPos
    curveFn = OpenMaya.MFnNurbsCurve() 
    arr = OpenMaya.MPointArray() 
    
    for pos in coords: 
        arr.append(*pos) 
    print arr
    curveFn.createWithEditPoints( 
                                  arr, 
                                  3, 
                                  OpenMaya.MFnNurbsCurve.kPeriodic, 
                                  False, 
                                  False, 
                                  True 
                         	    ) 
                         	    
                         	    
#select left vtx
def mapEPCurve( vtx, name, openClose, degree ):
      
    orderPos =[]
    if name in ["brow","lip"]:
        vt = cmds.xform( vtx[0], q=1, t=1, ws=1)
        # verts selection is only left part
        if vt[0]**2 <0.001:
            for t in vtx[1:][::-1]:

                vtxPos = cmds.xform( t, q=1, t=1, ws=1 )
                mrrPos = [-vtxPos[0],vtxPos[1],vtxPos[2]]
                orderPos.append(mrrPos)
                
            for v in vtx:

                vtxPos = cmds.xform( v, q=1, t=1, ws=1 )
                orderPos.append(vtxPos)
                
        # if verts selection in order entire region
        else:
            cmds.confirmDialog( title='Confirm', message='object or first vertex is off from center in X axis' )
            for v in vtx:
                vtxPos = cmds.xform( v, q=1, t=1, ws=1)
                orderPos.append(vtxPos)
    
    elif name == "eye":
    
        for v in vtx:
            vtxPos = cmds.xform( v, q=1, t=1, ws=1)
            orderPos.append(vtxPos)
                   
    if openClose == "open":
        browMapCrv = cmds.curve( d=float(degree), p=orderPos )
        cmds.rename( browMapCrv,  name + "MapCrv01" )
    
    elif openClose == "close":

        coords = orderPos
        curveFn = OpenMaya.MFnNurbsCurve() 
        arr = OpenMaya.MPointArray()
        for pos in coords: 
            arr.append(*pos)            
        
        curveFn.createWithEditPoints( 
                                      arr, 
                                      int(degree), 
                                      OpenMaya.MFnNurbsCurve.kPeriodic, 
                                      False, 
                                      False, 
                                      True 
                                    )
                

#버텍스 반만 순서대로 선택하면 미러한 포지션으로 커프를 만든다./ vtx = 이미 순서대로 정열된 버텍스 리스트
#geo should be symmetrical/ for open curve or curve is part of edge loop  
def mapCurve( vtx, name, openClose, degree ):
      
    orderPos =[]
    mirrOrderPos =[] 
    if name.split("_")[0] in ["brow","lip"]:
        vt = cmds.xform( vtx[0], q=1, t=1, ws=1)
        # verts selection is only left part
        if vt[0]**2 < 0.00001:
            for t in vtx[1:][::-1]:
                vtxPos = cmds.xform( t, q=1, t=1, ws=1)
                mrrPos = [-vtxPos[0],vtxPos[1],vtxPos[2]]
                mirrOrderPos.append(mrrPos)
                
            for v in vtx:
                vtxPos = cmds.xform( v, q=1, t=1, ws=1 )
                orderPos.append(vtxPos)
        # if verts selection in order entire region
        else:
            cmds.confirmDialog( title='Confirm', message='object or first vertex is off from center in X axis' )
            for v in vtx:
                vtxPos = cmds.xform( v, q=1, t=1, ws=1)
                orderPos.append(vtxPos)
                    
    elif name.split("_")[0] == "eye":
    
        for v in vtx:
            vtxPos = cmds.xform( v, q=1, t=1, ws=1)
            orderPos.append(vtxPos)
    
    # "open" / "close"
    if openClose == "open":
        orderPosAll = mirrOrderPos + orderPos
        browMapCrv = cmds.curve( d=float(degree), p= orderPosAll )
        #create unique name
        mapCrv = cmds.ls( name + "_crv*", typ = "transform" )
        if not mapCrv:
            newNum = 01
        else:
            lastNum = re.findall('\d+', mapCrv[-1])[0]
            newNum = int(lastNum)+1
        mapCrv = cmds.rename( browMapCrv,  name + "_crv"+ str(newNum).zfill(2) )
        return mapCrv
        
    elif openClose == "close":

        '''closedOrderPos = orderPos + orderPos[:3]
        numPoint = len(closedOrderPos)
        knots = []
        for i in range(numPoint+2):
            knots.append(i)

        closeCrv = cmds.curve( d=float(degree), per=1, p=closedOrderPos, k = knots )    
        cmds.rename( closeCrv,  name + "MapCrv01" )'''        
        orderPosAll = orderPos + mirrOrderPos[1:] #if mirrOrderPos = []: orderPosAll = orderPos
        #create unique name
        mapCrv = cmds.ls( name + "_crv*", typ = "transform" )
        if not mapCrv:
            newNum = 01
        else:
            number = re.findall('\d+', mapCrv[-1])[0]
            newNum = int(number)+1
            
        circleCrv = cmds.circle( c = (0,0,0), nr = (0,0,1), sw = 360, r=1, d=3, tol = 0.01, s=len(orderPosAll) )
        cmds.reverseCurve( circleCrv[0], ch =1, rpo =1 )
        guideCircle = cmds.rename( circleCrv[0],  name + "_crv"+ str(newNum).zfill(2) )
        
        for i, pos in enumerate(orderPosAll) :
            
            cmds.xform( guideCircle + '.cv[%s]'%str(i+1), ws=1, t = pos )
        cmds.xform( guideCircle + '.cv[0]', ws=1, t = orderPosAll[-1] )
        
        cmds.select( guideCircle, r=1 )
        symmetrizeLipCrv(1)     
        cmds.delete( guideCircle, ch=1)
        
        return guideCircle
# mapCurve(3, "open", "lip" )'''




        
#select lower curve to high curve to creaet brow map surf
def loftMapSurf():
    crvSel = cmds.ls( os=1, fl=1, type = 'transform')
    name = crvSel[0].split("_")[0]
    title=""
    if name =="brow":
        title = "browMapSurf"
    elif name == "lid":
        title = "eyeTip_map"
    elif name == "lip":
        title = "lipTip_map"

    loft_suf = cmds.loft( crvSel, n = title, ch =1, u=1, c=0, ar= 1, d=1, ss= 1, rn= 1, po= 1, rsn = 1  )
    suf_inputs = cmds.listHistory( loft_suf[0] )
    tessel = [ x for x in suf_inputs if cmds.nodeType(x) == 'nurbsTessellate' ]
    cmds.setAttr (tessel[0]+".format", 3 )
    




#browSetup update
'''
current: BrowCtl>0 --> *15 / BrowCtl<0 --> *10 
give the option to seperate eyebrow up/down
눈썹 UP/ DOwn 을 나누어 줘야 할때 
'''
def browWideJntX():
    browJnts =cmds.listRelatives("eyebrowJnt_grp", c=1)
    browWide = [ x for x in browJnts if "browWide" in x ]
    if browWide:
    	print "browWide_jnts already exist"
    
    else:
    	for bj in browJnts:
    	    jntMult= cmds.listConnections( bj, s=1, d=0, skipConversionNodes=1, type= "multiplyDivide" )
            '''browCond= cmds.listConnections( jntMult[0], s=1, d=0, skipConversionNodes=1, type="condition" )
            browSum = cmds. listConnections( browCond[0], s=1, d=0, skipConversionNodes=1, type="plusMinusAverage" )
            cmds.connectAttr( browSum[0] + ".output3Dy", jntMult[0] + ".input1Z" )

            cmds.connectAttr( 'browReverse_mult.outputZ', browCond[0]+".colorIfFalseG" )
            cmds.connectAttr( browCond[0]+".outColorG", jntMult[0] + ".input2Z" )'''
            browWide = cmds.duplicate( bj, po =1, n = bj.replace("Base","Wide") )
            cmds.connectAttr( jntMult[0] + ".outputZ", browWide[0]+".rx")

        setBrowJntLabel()

def browWideJnt():
    
    browBase = cmds.ls( '*_browBase*_jnt', typ = 'joint' )
    browWide = cmds.ls( '*_browWide*_jnt', typ = 'joint' )
    if browWide:
    	print "browWide_jnts already exist"
    
    else:
        unitCov = []
        for i, bj in enumerate(browBase):
            nameList = bj.split('_')
            name = nameList[0] + nameList[1].replace('browBase','brow')
            #create browWide_jnts 
            browWide = cmds.duplicate( bj, po =1, n = bj.replace("Base","Wide") )[0]
            
            jntMult= cmds.listConnections( bj, s=1, d=0, skipConversionNodes=1, type= "multiplyDivide" )[0]
            addD = cmds.shadingNode( 'addDoubleLinear', asUtility =1, n = name + '_addD')
            unitUp = cmds.shadingNode( 'unitConversion', asUtility =1, n = name + '_convert')
            jntDown = cmds.listRelatives( bj, c=1, typ = 'joint')[0]
            jntRotY = cmds.listRelatives( jntDown, c=1, typ = 'joint')[0] 
            unitLR = cmds.shadingNode( 'unitConversion', asUtility =1, n = name + 'LR_convert')   
            
            #browWide follow 30% of browUp 
            cmds.addAttr( "browFactor", shortName="wideFollow_browUp", longName="browWideFollow_browUp", defaultValue=0.3, minValue=0.0, maxValue=1.0, keyable= 1 )
            cmds.connectAttr( jntMult + ".outputY", unitUp + ".input" )
            cmds.connectAttr( "browFactor.wideFollow_browUp",  unitUp + ".conversionFactor", f =1 )
            
            cmds.connectAttr( unitUp + ".output", addD + ".input1" )
            #browWide follow full of browDown 
            cmds.connectAttr( jntMult + ".outputZ", addD + ".input2" )
            #browWide up/down
            cmds.connectAttr( addD + ".output", browWide + '.rx' )
            
            #browWide LR follow half of browL/R
            cmds.connectAttr( jntRotY + ".ry", unitLR + '.input' )
            cmds.setAttr( unitLR + ".conversionFactor", 0.5 )
            cmds.connectAttr( unitLR + '.output',  browWide + '.ry' )
            unitCov.append(unitLR)
        
        for uc in unitCov:
            if '01' in uc:
                print uc
                cmds.setAttr( uc + ".conversionFactor", 0.0 )
            elif '02' in uc:
                print uc
                cmds.setAttr( uc + ".conversionFactor", 0.1 )               
            
        #setBrowJntLabel()    
        jntNum = len(browBase)
        browBase.sort()
        z = [ browBase[0] ]
        leftJnt = browBase[1:jntNum/2+1]
        rightJnt = browBase[jntNum/2+1:]
        for i, j in enumerate(leftJnt):
            cmds.setAttr(j + '.side', 1)
            cmds.setAttr(j + '.type', 18)
            cmds.setAttr(j + '.otherType', "browWide"+str(i).zfill(2), type = "string")
        for id, k in enumerate(rightJnt):
            cmds.setAttr(k + '.side', 2)
            cmds.setAttr(k + '.type', 18)
            cmds.setAttr(k + '.otherType', "browWide"+str(id).zfill(2), type = "string") 


def browWideConversion():
    cmds.addAttr( "browFactor", shortName="wideFollow_browUp", longName="browWideFollow_browUp", defaultValue=0.3, minValue=0.0, maxValue=1.0, keyable= 1 )
    unitUD_brow = cmds.ls("*brow*_convert", type = "unitConversion" )

    for ut in unitUD_brow:
        cmds.connectAttr( "browFactor.wideFollow_browUp",  ut + ".conversionFactor", f =1 )
        

def setBrowJntLabel():
    jnts = cmds.ls ( '*browWide*_jnt', fl = True, type ='joint') 
    jntNum = len(jnts)
    jnts.sort()
    z = [ jnts[0] ]
    leftJnt = jnts[1:jntNum/2+1]
    rightJnt = jnts[jntNum/2+1:]
    for i, j in enumerate(leftJnt):
        cmds.setAttr(j + '.side', 1)
        cmds.setAttr(j + '.type', 18)
        cmds.setAttr(j + '.otherType', "browWide"+str(i).zfill(2), type = "string")
    for id, k in enumerate(rightJnt):
        cmds.setAttr(k + '.side', 2)
        cmds.setAttr(k + '.type', 18)
        cmds.setAttr(k + '.otherType', "browWide"+str(id).zfill(2), type = "string") 




#fix browJnt up/down movement        
def browUpDownReverse():
    browConds = cmds.ls("browScale_Cond*", fl=1)
    revCond = [] 
    for bc in browConds:
        cnnt = cmds.listConnections( bc, c=1, s=1 )
        if "browReverse_mult" not in cnnt:
            revCond.append(bc)
        
    for b in revCond:
        cmds.connectAttr( "browReverse_mult.outputX " , b+".colorIfTrueR", f=1 )
        cmds.connectAttr( "browReverse_mult.outputZ" , b+".colorIfFalseR", f=1 )
        cmds.connectAttr( "browReverse_mult.outputZ" , b+".colorIfFalseG", f=1 )
        
        
    
"""create browMapMesh"""
def browMapSurf():

    faceGeo = cmds.ls(sl =1, type ='transform')[0]
    #xmin ymin zmin xmax ymax zmax (face bounding box)
    facebbox = cmds.xform( faceGeo, q=1, ws=1, boundingBox =1 )
    print faceGeo, facebbox[1]
    sizeX = facebbox[3]*2
    bboxSizeY = facebbox[4] - facebbox[1]
    browJntLen = len (cmds.ls("*_browBase*", type = "joint"))
    browMapSurf = cmds.polyPlane(n= "browMapSurf", w = sizeX, h =bboxSizeY/2, subdivisionsX = browJntLen, subdivisionsY = 2 )
    cmds.xform( browMapSurf, p = 1, rp =(0, 0, bboxSizeY/4))
    
    #place the mapSurf at the upper part of the face
    cmds.setAttr ( browMapSurf[0] + ".rotateX", 90 )
    cmds.xform (browMapSurf[0], ws =1, t = (0, facebbox[1] + bboxSizeY/2, 0))    
    
 
"""
modeling the browSurfMap for the forhead
create function for browSurfMap polyPlane mirroring 
"""
#create brow joints first 
def browMapSkinning():
    if not "browMapSurf":
        print "create browMapSurf first!!"
    else : browMapSurf = "browMapSurf"
    browJnts = cmds.ls ("*_browP*", type ="joint")
    jntNum = len(browJnts)
    browJnts.sort()
    z = [ browJnts[0] ]
    y = browJnts[1:jntNum/2+1]
    browJnts.reverse()
    x = browJnts[:jntNum/2]
    orderJnts = x + z + y
    orderChildren = cmds.listRelatives(orderJnts, c =1, type = "joint")
    
    if not cmds.objExists('headSkel_jnt'):
        headSkelPos = cmds.xform('headSkelPos', q =1, ws =1, t =1 )
        cmds.joint(n = 'headSkel_jnt', p = headSkelPos )
    orderChildren.append("headSkel_jnt")
        
    vrts= cmds.polyEvaluate(browMapSurf, v =1 )
    numVtx = vrts/jntNum
    if vrts%jntNum==0:
        skinCls = cmds.skinCluster(orderChildren , browMapSurf, toSelectedBones=1 )
        # 100% skinWeight to headSkel_jnt
        cmds.skinPercent(skinCls[0], browMapSurf, transformValue = ["headSkel_jnt", 1])
        # skinWeight
        for i in range (0, jntNum):
            vtxs = "browMapSurf.vtx[%s:%s]"%( numVtx*i, numVtx*i+numVtx-1 )
            cmds.skinPercent( skinCls[0], vtxs, transformValue = [ orderChildren[i], 1])
    else:
        print "Number of faces and browJnts are not matching"  
        
        
        
'''
Requirment : all loftCurves, lipTip_map(surf)
'''
def lipMapSkinning():
    
    cvs = cmds.ls('lip_loft_crv01.cv[*]', fl =1)
    cvLen = len(cvs)

    # ordered Joints for skin
    uplipJnt = cmds.ls('upLipRoll*_jnt', fl =1, type = 'joint')
    lolipJnt = cmds.ls('loLipRoll*_jnt', fl =1, type = 'joint')
    lolipJnt.reverse()
    lipTipJnt = uplipJnt + lolipJnt
    jntNum = len(lipTipJnt)
    print cvLen, jntNum
    if not cvLen == jntNum:
        print 'the number of mouth joints is different to the cvs '
    else: 
        loftCrvs = cmds.ls('lip_loft_crv*', type = 'transform')
        crvLen = len(loftCrvs)        
        vrtPerJnt = crvLen
        
        skin = headSkinObj('lipTip_map')
        cmds.skinPercent( skin[0], 'lipTip_map.vtx[0:%s]'%(cvLen*crvLen-1), tv = ['headSkel_jnt',1] )
        index = 0       
        for x in range(0, cvLen*crvLen, vrtPerJnt):        
            cmds.skinPercent( skin[0], 'lipTip_map.vtx[%s:%s]'%(x, x + vrtPerJnt-1), tv = [ lipTipJnt[index], 1] )
            index +=1 
            
            
            
'''
skin the map surface start where the first vertex(rCorner vert) 
'''
def eyeMapSkinning():
    
    surf = 'eyeTip_map'
    if not cmds.objExists(surf):
        cmds.warning( "create eye surface map first!!" )
        
    else:
        faceLen = cmds.polyEvaluate( "eyeTip_map", f=1  )
        vtxLen = cmds.polyEvaluate( "eyeTip_map", v=1  )
        # ordered Joints for skin
        upBlinkJnts = cmds.ls("l_up*Blink*_jnt", type = "joint" )
        upLidJnts = lastJntOfChain( upBlinkJnts )
        loBlinkJnts = cmds.ls("l_lo*Blink*_jnt", type = "joint" )         
        loLidJnt = lastJntOfChain( loBlinkJnts )
        loLidJnts = loLidJnt[::-1]
        
        #uplipJnt.insert(0, 'l_innerLidTxTX_jnt')
        #lolipJnt.insert(0, 'l_outerLidTxTX_jnt')
        orderJnt = upLidJnts + loLidJnts
        jntNum = len(orderJnt)
        print jntNum, faceLen       
        
        if not faceLen%jntNum==0:
        	cmds.warning( 'the number of eyeLid joints is different to the cvs' )
    	else:
    		
    		crvLen = faceLen/jntNum + 1
    		#how many vertices will be weight for each joint = curve length
    		vrtPerJnt = crvLen
    		skin = headSkinObj(surf)
	        #skinWeight 100% to "headSkel_jnt" 
	        cmds.skinPercent( skin[0], surf + '.vtx[0:%s]'%(vtxLen-1), tv = ['headSkel_jnt',1] )
	        index = 0       
	        for x in range(0, vtxLen, vrtPerJnt):        
	            cmds.skinPercent( skin[0], surf + '.vtx[%s:%s]'%(x, x + vrtPerJnt-1), tv = [ orderJnt[index], 1] )
	            index +=1  
                


#get the last child joint of the chain.
def lastJntOfChain( jntList ):
    chlidJnt = cmds.listRelatives( jntList, ad=1, type = "joint" )
    childJntGrp = []
    for jt in chlidJnt:
        child = cmds.listRelatives( jt, c=1, type = "joint" )
        if not child:
            childJntGrp.append(jt)
    
    return (childJntGrp)
    
'''    
grp = cmds.ls(sl=1)
ctlArry = lastJntOfChain(grp)
for ctl in ctlArry:
    print ctl
    cmds.connectAttr( 'decomposeMatrix4.outputRotate', ctl + '.r')'''

def parentCtl_ofChain( list ):
    child = cmds.listRelatives( list, ad=1, type = "nurbsCurve" )
    childGrp = []
    for cv in child:
        prnt = cmds.listRelatives( cmds.listRelatives( cv, p=1 )[0], p =1 )
        if prnt:
            childGrp.append(prnt[0])
    return childGrp
    
    
    

               
'''full skinning module for lipMapSkinning (geometrys for skinning need to have "_" in their name)'''
def headSkinObj(geoName):
    deforms =[nd for nd in cmds.listHistory(geoName) if cmds.nodeType(nd) in ['cluster', 'blendShape', 'ffd'] ]
    for df in deforms:
        if cmds.getAttr( df + '.nodeState')==0:
            #hasNoEffect
            cmds.setAttr( df + '.nodeState', 1)       

    skinJnts = headInfluences()
    skin = cmds.skinCluster ( geoName, skinJnts, tsb =1, n = geoName + 'Skin' )
    return skin
    
    
    
def headInfluences():
    browJnts = cmds.ls('*_browP*_jnt', fl =1, type = 'joint')
    browWide = cmds.ls( '*_browWide*_jnt', fl=1, type="joint" )    
    browAllJnt = cmds.listRelatives( browJnts, c =1, type = 'joint')   
    eyeWideJnts = cmds.ls('*LidWide*_jnt', fl =1, type = 'joint')
    blinkJnts = cmds.ls("*LidBlink*_jnt", type = "joint" )
    eyeJnts = lastJntOfChain( blinkJnts )     
    lipJntP = cmds.ls('*LipRollP*', fl =1, type = 'transform')
    lipJnt = cmds.listRelatives( lipJntP, c =1, type = 'joint')
    lipYJnt = cmds.ls('*LipY*_jnt', fl =1, type = 'transform')
    faceJnts = cmds.listRelatives('supportRig', ad =1, type = 'joint' )
    skinJnts = ['jawClose_jnt', 'headSkel_jnt']
    for ls in [browJnts, browWide, browAllJnt, eyeWideJnts, eyeJnts, lipJnt, lipYJnt, faceJnts ]:
    	if ls is not None:
    		skinJnts+=ls

    return skinJnts


    
#create null between the selected nodes and it's parent
#the selected nodes' transform becomes zero out
def createPntNull( mySelList ):    
     
    grpList =[]
    for nd in mySelList:
        
        pos = cmds.xform(nd, q=1, ws=1, rotatePivot=1 ) 
        
        if cmds.nodeType(nd) =="transform":
            topGrp = cmds.duplicate( nd, po=1, n=nd+"P" )[0]
            cmds.parent(nd, topGrp)
            grpList.append(topGrp)
            
        else: #joint, cluster....
            prnt = cmds.listRelatives( nd, p=1, type ="transform")
            emGrp = cmds.group( em=1, n= nd+"P" )
            cmds.xform( emGrp, ws=1, t=pos )
            cmds.parent( nd, emGrp )    
            grpList.append(emGrp)            
                        
            if prnt:
                cmds.parent( emGrp, prnt[0] )
    
    return grpList  #list of parent group nodes               





                
def connectionCopy():
    tranNode=cmds.ls( os=1, type="transform" )
    if tranNode[0][:2] in ["l_","r_"] and tranNode[1][:2] in ["l_","r_"]:
        scName = tranNode[0][2:]
        tgName = tranNode[1][2:]
        for lr in ["l_","r_"]:
            scCnnt = cmds.listConnections( lr + scName, s=1, d=0, p=1, scn=1, c=1 )
            if scCnnt:
                for dn, sc in zip(*[iter(scCnnt)]*2):
                    attr = dn.split(".")[1]
                    cmds.connectAttr( sc, lr + tgName +"."+ attr, f=1 )     
            
            dnCnnt = cmds.listConnections( lr + scName, s=0, d=1, p=1, scn=1, c=1)
            if dnCnnt:
                for d, s in zip(*[iter(dnCnnt)]*2):
                    scAttr = s.split(".")[1]
                    cmds.connectAttr( lr + tgName + "." + scAttr, d, f=1 )
                 
    else:
    
        scCnnt = cmds.listConnections( tranNode[0], s=1, d=0, p=1, scn=1, c=1 )
        if scCnnt:
            for dn, sc in zip(*[iter(scCnnt)]*2):
                attr = dn.split(".")[1]
                cmds.connectAttr( sc, tranNode[1] + '.'+ attr, f=1 )
                
        dnCnnt = cmds.listConnections( tranNode[0], s=0, d=1, p=1, scn=1, c=1)
        if dnCnnt:
            for s, d in zip(*[iter(dnCnnt)]*2):
                scAttr = s.split(".")[1]
                cmds.connectAttr( tranNode[1] +'.'+ scAttr, d, f=1 )   



  


def twitchTargetsList():
        
    mainTg = [u'E', u'CornerD', u'CornerU', u'BrowMad', u'BrowSad', u'BrowDown',
     u'BrowUp', u'Furrow', u'Happy', u'Sad', u'Cheek', u'Squint', u'SquintPuff',
     u'Sneer', u'U', u'Flare', u'nostrilCompress', u'Puff', u'Suck', u'O', "CornerT","CornerW"]    
    
    mysel = cmds.ls(sl=1, type = "transform")
    child = cmds.listRelatives( mysel, c=1 )
    twichTgList = []
    for mt in mainTg:
        if mt in child:
            twichTgList.append(mt)
                    
        else:
            print mt
             
    



def deleteOrigSel():
    mysel = cmds.ls(sl=1, type = "transform")
    child = cmds.listRelatives( mysel, c=1, s=1 )
    orig = [ x for x in child if "Orig" in x ]
    cmds.delete( orig )



        
        
#select eyeBall with blendShape
def irisPupilSetup():

    eyeBall = cmds.ls(sl=1, type = "transform")
    for pre in ["l_","r_", "lf_", "rt_"]:
        
        if pre in eyeBall[0]:
            LR = pre
  
    if LR:
        eyeGeo = eyeBall[0]
        hist = cmds.listHistory( cmds.listRelatives(eyeGeo, c=1)[0], pruneDagObjects =1, interestLevel= 1 )
        bs = [ x for x in hist if cmds.nodeType(x)=="blendShape"]
        if bs:
            BS = bs[0]
        
        else:
            cmds.confirmDialog(title='Confirm', message='%s should have BlendShape'%eyeGeo )
            
        eyeIrisCtls = [ LR + "irisDial_ctl", LR[0] + "iris_dial" ]
        pupilCtl = ""
        if cmds.objExists( eyeIrisCtls[0] ) :
            irisCtl = eyeIrisCtls[0]

        else:
            if cmds.objExists( eyeIrisCtls[1] ):
                irisCtl = eyeIrisCtls[1]
                pupilCtl = LR[0] + "pupil_dial"
            else:
                cmds.confirmDialog( title='Confirm', message='%s is missing'%eyeIrisCtls[1] )
                
        alias = cmds.aliasAttr( bs[0], q=1 )
        for tgt, wgt in zip(*[iter(alias)]*2):
            if pupilCtl:
                if "iris" in tgt:
                    cmds.connectAttr( irisCtl + ".ty", BS +"."+tgt, f=1 )   
                elif "pupil" in tgt:
                    cmds.connectAttr( pupilCtl + ".ty", BS +"."+tgt, f=1 )
            else:
                if "iris" in tgt:
                    cmds.connectAttr( irisCtl + ".ty", BS +"."+tgt, f=1 )   
                elif "pupil" in tgt:
                    cmds.connectAttr( irisCtl + ".tx", BS +"."+tgt, f=1 )                
    else:
        cmds.confirmDialog(title='Confirm', message='%s name should include "l_" or "l"'%eyeGeo )
        
                
#select cluster and transform node
def changeClsWeightNode():
    mySel = cmds.ls(sl=1 )
    for it in mySel:
        cnnt = cmds.listConnections(it+".worldMatrix", s=0, d=1 )
        if cnnt:
            cls= cnnt[0]
        else:
            handle = it
    cmds.cluster( cls, e=1, bindState =1, wn = ( handle, handle))
    
    
    
def createFollicle( geo, u, v, name ):
    folic = cmds.createNode( 'follicle', n =name + 'Shape')
    geoShape = cmds.listRelatives( geo, ni=1, s =1 )[0]
    folicTran = cmds.listRelatives( folic, p=1 )[0]
    
    cmds.connectAttr( geoShape + '.outMesh', folic + '.inputMesh' )
    cmds.connectAttr( geoShape + '.worldMatrix', folic + '.inputWorldMatrix' )
    
    cmds.connectAttr( folic + '.outRotate', folicTran + '.rotate' )
    cmds.connectAttr( folic + '.outTranslate', folicTran + '.translate' )
    
    cmds.setAttr( folicTran + '.parameterU', u)
    cmds.setAttr( folicTran + '.parameterV', v)    
    
    return folic, folicTran
    


def getGeo_uvParam( geo, obj ):

    geoShape = cmds.listRelatives( geo, ni=1, s =1 )[0]
    closestMesh = cmds.shadingNode('closestPointOnMesh', asUtility =1, n = 'temp_CPOM' )
    decomMtrx = cmds.shadingNode('decomposeMatrix', asUtility =1, n = 'temp_decomMtrx' )
    
    cmds.connectAttr( geoShape + '.worldMesh', closestMesh + '.inMesh' )
    cmds.connectAttr( geo + '.worldMatrix', closestMesh + '.inputMatrix' )
    
    cmds.connectAttr( obj + '.worldMatrix', decomMtrx + '.inputMatrix' )
    cmds.connectAttr( decomMtrx + '.outputTranslate', closestMesh + '.inPosition' )
    
    u = cmds.getAttr( closestMesh + '.parameterU' )
    v = cmds.getAttr( closestMesh + '.parameterV' )
    
    #cmds.delete( closestMesh, decomMtrx )
    
    return u,v 


# select new head and rigged head
def plugNewHeadShape( plugHead, rigHead ):
    
    # delete source curve BS target
    headBS = [ n for n in cmds.listHistory( rigHead, historyAttr=1 ) if n == "twitchBS" ]    
    if headBS:
        aliasAtt = cmds.aliasAttr(headBS[0], q=1)
        for tgt, wgt in zip(*[iter(aliasAtt)]*2):
            if cmds.objExists(tgt):
                cmds.delete(tgt)
    
    #delete squach rig / cleanup
    if cmds.objExists("squachLattice_skin"):
        
        jnts = cmds.listConnections("squachLattice_skin", s=1, d=1 )
        ctls = cmds.listConnections( "squach_skin", s=1, d=1 )
        sqchNodes = set( jnts + ctls )
        sqchNodes.add("stretchPow_crv")
        sqchNodes.add("volumePow_crv")    

        for jnt in sqchNodes:
            if cmds.objExists(jnt):
                nodes = cmds.listHistory( jnt, ac=1 )
                if nodes:
                    for x in nodes:
                        if cmds.objExists(x):
                            if not cmds.nodeType(x) in ["transform","mesh"]:
                                cmds.delete( x )
        
        for nd in sqchNodes:
            if cmds.objExists( nd ):
                cmds.delete( nd )
            
        grps  = ["squachJnt_grp", "squachCtl_grp", "squachCrv_grp", "topSquach_ctlP", "bttmSquach_ctlP " ]
        for gp in grps:
            if cmds.objExists( gp ):
                cmds.delete( gp )   
    
    #shape plug in
    plugHeadShape = cmds.listRelatives( plugHead, c=1 )[0]
    rigHeadShapes = cmds.listRelatives( rigHead, ad=1, type='shape' )
    dfoms = cmds.listHistory(rigHead, il = 1, pdo =1 )
    tweakND = [ x for x in dfoms if cmds.nodeType(x)=="tweak" ]
    if tweakND:
        cnnct = cmds.listHistory(tweakND[0] ) 
        rigHeadOrig = []
        for ct in cnnct:
            if cmds.nodeType(ct)== "mesh":
                if cmds.getAttr(ct + ".intermediateObject"):
                    rigHeadOrig.append(ct)
                    
        if len(rigHeadOrig)==1:
            cmds.connectAttr( plugHeadShape + ".outMesh" , rigHeadOrig[0] + ".inMesh", f=1 )
            
        else:
            cmds.confirmDialog(title='Confirm', message='there are more than one original shapes (%s and %s) '%(rigHeadOrig[0], rigHeadOrig[1]) )
    
    else:
        cmds.confirmDialog(title='Confirm', message='no tweak node, do it manually' )            


    

def updateHierachy():

    """
    run to create default structure containers
    """    
    headSkelPos     = cmds.xform('headSkelPos', t = True, q = True, ws = True)
    jawRigPos       = cmds.xform('jawRigPos', t = True, q = True, ws = True)
    lEyePos         = cmds.xform('lEyePos', t = True, q = True, ws = True)
    cmds.xform( 'headSkel', ws = 1, t = headSkelPos)        
    cmds.xform('jawRig', ws = 1, t = jawRigPos)
    cmds.xform('eyeRig', ws = 1, t = (0, lEyePos[1],lEyePos[2]))

    midCtlGrp= 'midCtl_grp'
    if cmds.objExists( midCtlGrp ):
        midCtls = cmds.listRelatives( midCtlGrp, c=1 )
        for mc in midCtls:
            name = mc.split('_')
            if mc[:2] in [ 'l_', 'r_' ]:
                
                loc = name[1]+'Pos'
                if cmds.objExists( loc ):
                    print mc
                    pos = cmds.xform( loc, q=1, ws=1, t=1 )               
                    if mc[:2] == "l_":
                        cmds.xform( mc, ws = 1, t = pos )
                    elif mc[:2] == "r_":
                        cmds.xform( mc, ws = 1, t =( -pos[0], pos[1], pos[2]) )
            
                elif name[1] == 'ear':
                    lEarPos = cmds.xform('lEarPos', t = True, q = True, ws = True )
                    if mc[:2] == "l_":
                        cmds.xform( mc, ws = 1, t = lEarPos )
                    elif mc[:2] == "r_":
                        cmds.xform( mc, ws = 1, t =( -lEarPos[0], lEarPos[1], lEarPos[2]) )                 
            
            else:
                loc = name[0]+'Pos'
                if cmds.objExists( loc ):
                    print loc
                    pos = cmds.xform( loc, q=1, ws=1, t=1 )
                    cmds.xform( mc, ws = 1, t = pos )    

    clusterDict = { 'jawRigPos': ['jawOpen_cls', 'mouth_cls'], 'lipYPos':'lip_cls', 'lipRollPos':'lipRoll_cls', 'cheekPos':['l_cheek_cls','r_cheek_cls'], 
    'lEyePos':['l_eyeBlink_cls', 'l_eyeWide_cls'], 'rEyePos':['r_eyeBlink_cls', 'r_eyeWide_cls'], 'lowCheekPos': ['l_lowCheek_cls', 'r_lowCheek_cls'], 'squintPuffPos':['l_squintPuff_cls', 'r_squintPuff_cls'], 
    'lEarPos':['l_ear_cls','r_ear_cls'], 'rotXPivot':['browUp_cls','browDn_cls'], 'nosePos': 'nose_cls',  }

    for loc, cls in clusterDict.iteritems():       

        if cmds.objExists( loc ):
            
            if len(cls)==2:                
                handles = [] 
                for i, cl in enumerate(cls):
                    if cmds.objExists(cl):
                        hand = cmds.listConnections(cl +".matrix", s=1, d=0, type="transform")[0]
                        handles.append(hand)
                        newPos = cmds.xform( loc, t = True, q = True, ws = True )
                        oldPos = cmds.xform( handles[0], t = True, q = True, ws = True )                                   
                print handles        
                if len(handles) == 2:
                    if oldPos == newPos:
                        pass
                        
                    else:
                                         
                        if "l_" in cls[0] and "r_" in cls[1]:

                            cmds.xform( handles[0], ws=1, piv = newPos )
                            cmds.xform( handles[0], ws=1, scalePivot = newPos )
                            lClsPrnt = cmds.listRelatives( handles[1], p=1 )[0] 
                            cmds.xform( lClsPrnt, ws=1, piv = newPos )
                            cmds.xform( lClsPrnt, ws=1, scalePivot = newPos )
                                        
                            mirrorPos = [-newPos[0], newPos[1], newPos[2] ]
                            cmds.xform( handles[1], ws=1, piv = mirrorPos )
                            cmds.xform( handles[1], ws=1, scalePivot = mirrorPos )
                            rClsPrnt = cmds.listRelatives( handles[1], p=1 )[0]                 
                            cmds.xform( rClsPrnt, ws=1, piv = mirrorPos )
                            cmds.xform( rClsPrnt, ws=1, scalePivot = mirrorPos )       
        
                        else:                        
                        
                            cmds.xform( handles[i], ws=1, piv = newPos )
                            cmds.xform( handles[i], ws=1, scalePivot = newPos )
                            clsPrnt = cmds.listRelatives( handles[i], p=1 )[0]
                            cmds.xform( clsPrnt, ws=1, piv = newPos )
                            cmds.xform( clsPrnt, ws=1, scalePivot = newPos ) 
                else:
                    cmds.confirmDialog( title='Confirm', message=' %s is missing!'%cl )
                    
            else:
                if cmds.objExists(cls):
                    handle = cmds.listConnections(cls +".matrix", s=1, d=0, type="transform")[0]
                    currentPos = cmds.xform( loc, t = True, q = True, ws = True )
             
                    cmds.xform( handle, ws=1, piv = currentPos )
                    cmds.xform( handle, ws=1, scalePivot = currentPos )
                    clsPrnt = cmds.listRelatives( handle, p=1 )[0]  
                    cmds.xform( clsPrnt, ws=1, piv = currentPos )
                    cmds.xform( clsPrnt, ws=1, scalePivot = currentPos )

        else:
            cmds.confirmDialog( title='Confirm', message='create %s locator first!!'%loc )
                
                
def update_faceMain():
    
    # change locator position after testing faceClusters 
    helpPanelGroup = "helpPanel_grp"
    mainLoc = cmds.listAttr( helpPanelGroup, a =1, userDefined =1 )
    if cmds.objExists("allPos"):
        tmpChild = cmds.listRelatives( "allPos", ad=1, ni=1, type = ["nurbsCurve", "locator"] )
        itemSet = [ cmds.listRelatives(x, p=1)[0] for x in tmpChild ]
        locSet = set(itemSet)
        #put together only locators whose position changed
        changeLoc =[]
        for loc in locSet:
            if loc in mainLoc:
                newPos = cmds.xform( loc, t = True, q = True, ws = True )
                oldPos = cmds.getAttr( helpPanelGroup +"." + loc )
                if oldPos == newPos:
                    pass
                else:
                    print loc
                    changeLoc.append( loc )
                    
                cmds.setAttr( helpPanelGroup +"." + loc, newPos, type="doubleArray" )
                
        if cmds.attributeQuery("changedLocators", node = helpPanelGroup, exists=1)==False:
            cmds.addAttr( helpPanelGroup, ln ="changedLocators", dt = "stringArray" )
        cmds.setAttr( helpPanelGroup + ".changedLocators", type= "stringArray", *([len(changeLoc)] + changeLoc))
        
    else: 
        cmds.confirmDialog( title='Confirm', message='import face Locator first!!' )
                
    headGeo = cmds.getAttr( helpPanelGroup + ".headGeo" )
    headSkinCls =mel.eval("findRelatedSkinCluster %s"%headGeo )
    if headSkinCls:
        if "headSkel_jnt" in cmds.skinCluster( headSkinCls, q=1, wi=1 ):
            cmds.skinCluster( headSkinCls, e=1, mjm =1 )

    #unparent jawRig, eyeRig
    cmds.parent( "jawRig", "eyeRig", "browDtailCtl_grp", "midCtl_grp", w=1 )
    newCurves = []
    runNum = 0
    for loc in changeLoc:
            
        #put skinCluster on move joint mode    
        if loc == "headSkelPos":

            #adjust headSkel location
            newPos = cmds.getAttr( helpPanelGroup +"." + loc )        
            cmds.xform( "headSkel", ws=1, t = newPos )
        
        elif loc in [ "jawRigPos" , "lipYPos" , "lipEPos" ]:
        
            #unparent LipJotY, LipRollP
            lipYGrp = cmds.ls("*LipJotY**")
            lipRollGrp = cmds.ls( "*LipRollP*")
            if lipYGrp and lipRollGrp:
                
                for jnt in lipYGrp + lipRollGrp:
                    cmds.parent( jnt, w=1 )
                    
                #make change based on the locator that has a change in position
                if loc == "jawRigPos":
                    newJPos = cmds.getAttr( helpPanelGroup +"." + loc )      
                    cmds.xform( "jawRig", ws=1, t = newJPos ) # only jawRig(lipJotX) to new position
                    
                    # adjust teenth grp_nodes and joints 
                    teethCtlGrp = "teethCtl_grp"
                    if cmds.objExists(teethCtlGrp):                              
                            
                            cmds.parent( teethCtlGrp, w=1 )
                            cmds.xform( teethCtlGrp, ws=1, t = newJPos )
                                                           
                elif loc == "lipYPos":
                    newYPos = cmds.getAttr( helpPanelGroup +"." + loc )
                    for i, jnt in enumerate(lipYGrp):            
                        cmds.xform( jnt, ws=1, t = newYPos )
                        
                elif loc == "lipEPos":
                    #reposition the "up/loLipRollP" on the new GuideCrv
                    for ud in [ "up", "lo" ]:
                        if cmds.objExists( ud + "_guide_crv"):
                            cmds.delete( ud +"_guide_crv" )

                        orderedVerts = cmds.getAttr( "lipFactor." + ud + "LipVerts" )
                        vNum = len( orderedVerts )
                        lipSPos = cmds.getAttr( helpPanelGroup +".lipSPos" )              
                        lipNPos = cmds.getAttr( helpPanelGroup +".lipNPos" )            
                        lipEPos = cmds.getAttr( helpPanelGroup +".lipEPos" )
                        lipWPos = [-lipEPos[0], lipEPos[1], lipEPos[2]]
                        if ud == "up":
                            lipCntPos = lipNPos            
                        elif ud == "lo":
                            lipCntPos = lipSPos
                            
                        tempCrv = cmds.curve(d= 3, ep= [lipWPos, lipCntPos,lipEPos] ) 
                        guideCrv = cmds.rename(tempCrv, ud + "_guide_crv" )
                        guideCrvShape = cmds.listRelatives(guideCrv, c = True) 
                        cmds.rebuildCurve( guideCrv, d = 3, rebuildType = 0, keepRange = 0)
                         
                        linearDist = 1.0/(vNum-1)
                        increment = 0
                        lipPoc = []
                        for i in range( vNum ):
                        
                            guidePoc =cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = ud +'_lipGuide' + str(i).zfill(2) + '_poc' )
                            cmds.connectAttr( guideCrvShape[0] + ".worldSpace" , guidePoc + ".inputCurve" )
                            cmds.setAttr( guidePoc + ".turnOnPercentage", 1 )
                            cmds.setAttr( guidePoc +".parameter", increment )
                            #pocPos = cmds.getAttr( guidePoc + ".position")[0]        
                            lipPoc.append( guidePoc )
                            increment = increment + linearDist
                        
                        if ud == "lo":
                            lipPoc = lipPoc[1:-1]
                            
                        lipGrp = cmds.ls( ud + "LipRollP*") 
                        for i, poc in enumerate(lipPoc):
                            nPos = cmds.getAttr( poc + ".position")[0]
                            cmds.xform ( lipGrp[i], ws=1, t = nPos )  
                                
                for i, jot in enumerate(lipYGrp):
                    cmds.parent(jot, jot.replace("JotY","JotX"))
                    
                    rollTGrp = lipRollGrp[i].replace("P", "T")
                    cmds.parent( lipRollGrp[i], rollTGrp )            
            
            else:
                if loc == "jawRigPos":
                    newJPos = cmds.getAttr( helpPanelGroup +"." + loc )      
                    cmds.xform( "jawRig", ws=1, t = newJPos ) # only jawRig(lipJotX) to new position
        
        elif loc in ["rotXPivot" , "rotYPivot"]:
            if runNum == 0:
                
                baseJnts = cmds.ls( "*_browBase*_jnt" )
                if baseJnts:
                    rotYJnts = cmds.ls( "*_browRotY*_jnt" )
                    baseCtl =cmds.ls( "*brow*_base", typ = "transform" )            

                    newXPos = cmds.getAttr( helpPanelGroup +".rotXPivot" )
                    newYPos = cmds.getAttr( helpPanelGroup +".rotYPivot" )            

                    browPJnts = cmds.listRelatives( rotYJnts, c=1)
                    center = (len( browPJnts)-1 )/2
                    browJntOrder = browPJnts[center+1:][::-1] + [browPJnts[0]] + browPJnts[1:center+1]
                    baseCtlOrder = baseCtl[center+1:][::-1] + [baseCtl[0]] + baseCtl[1:center+1]
                    dist = cmds.getAttr( browPJnts[0] + ".tz")
                    #new browVerts in order
                    browVerts = cmds.getAttr( "browFactor.browVerts" )    
                    mirrorVerts = mirrorVertice( browVerts )
                    orderedVerts = mirrorVerts[1:][::-1] + browVerts
                    
                    cmds.parent( rotYJnts, w=1 )            
                    cmds.parent( browPJnts, w=1 )
                    for i, jnt in enumerate(baseJnts):
                    
                        #put "*browBase_jnt" on new position of rotXPivot
                        cmds.xform( jnt, ws=1, t= newXPos )
                        cmds.xform( baseCtlOrder[i], ws =1, t = newXPos )
                        
                        rotYCtl = cmds.listRelatives( baseCtlOrder[i], c=1 )[0]
                        #put "*browRotY_jnt" on new position of rotYPivot
                        cmds.xform( rotYJnts[i], ws=1, t= newYPos )
                        cmds.xform( rotYCtl, ws =1, t = newYPos )

                        vtxPos = cmds.xform( orderedVerts[i], q=1, ws=1, t=1 )
                        #put "*browP_jnt" on new position of vertices
                        cmds.xform( browJntOrder[i], ws=1, t= vtxPos )
                        #place brow_dummy on new position of vertices                
                        cmds.xform( cmds.listRelatives( rotYCtl, c=1 )[0], ws=1, t=( vtxPos[0],vtxPos[1], vtxPos[2]+ dist/20  ) )

                        cmds.parent( rotYJnts[i], cmds.listRelatives( baseJnts[i], c=1)[0] )
                        cmds.parent( browPJnts[i], rotYJnts[i] )  
                runNum+=1
    
        elif loc == "lEyePos":
            # reposition up vector (l/r_eyeUp_loc)
            newEyePos = cmds.getAttr( helpPanelGroup +"." + loc )                
            cmds.xform( "eyeRig", ws=1, t = ( 0, newEyePos[1], newEyePos[2]) ) # only eyeRig to new position
            
            if cmds.objExists("l_eyeUp_loc") and cmds.objExists("r_eyeUp_loc"):            

                for i, prefix in enumerate(["l_up", "l_lo","r_up", "r_lo"]):                
                    
                    if i in [0,2]:
                        val = 1
                        if "r_" in prefix:#set lEyeLoc right side value
                            newEyePos = [ -newEyePos[0], newEyePos[1], newEyePos[2] ]
                            val = -1
                        # 1. adjust eye_rig grp nodes position                      
                        if cmds.objExists( prefix[:2] + "eyeBall_jnt"):

                            eyeJntPos = cmds.xform( prefix[:2] + "eyeBall_jnt", q=1, ws=1, t=1)                     
                            if not newEyePos == eyeJntPos: #zero out all eyeRig grp_nodes
                                
                                eyeRigChild = cmds.listRelatives( prefix[:2] + "eyeP", ad=1 )
                                for child in eyeRigChild:
                                    cmds.xform( prefix[:2] + "eyeP", ws=1, t = newEyePos )
                                    cmds.xform( child, ws=1, t = newEyePos )
                           
                            eyeRotY = cmds.getAttr( "lEyePos.ry" )
                            eyePrntRY =cmds.getAttr(  prefix[:2] + "eyeRP.ry" )
                            if not eyePrntRY== eyeRotY*val:
                                eyeConversion = cmds.shadingNode('unitConversion', asUtility =1, n = prefix[:2] + 'eye_conversion' )
                                cmds.connectAttr( "lEyePos.ry", eyeConversion + ".input"  )
                                cmds.setAttr(  eyeConversion + ".conversionFactor", val )
                                cmds.connectAttr( eyeConversion + ".output", prefix[:2] + "eyeRP.ry" )      
                      
                        #place eyeBall_jnts on newEyeloc
                        #1.check if there is decomposeMatrix node
                        eyeDecomposeP = prefix[:2] + "eyeDecomposeP"                        
                        cnnct = cmds.listConnections( eyeDecomposeP, s=1, d=0 )
                        if cnnct:
                            for x in set(cnnct):
                                if cmds.nodeType(x) == "decomposeMatrix":
                                    dMatrix = x
                                   
                                else:
                                    eyeDComp = cmds.shadingNode('decomposeMatrix', asUtility =1, n = prefix[:2] + 'eye_decomMtrx' )
                                    cmds.connectAttr( "headSkel.worldInverseMatrix", eyeDComp + ".inputMatrix" )
                                    cmds.connectAttr( eyeDComp + ".outputTranslate", prefix[:2] + "eyeDecomposeP.translate" )
                                    cmds.connectAttr( eyeDComp + ".outputRotate", prefix[:2] + "eyeDecomposeP.rotate" )
                                    cmds.connectAttr( eyeDComp + ".outputScale", prefix[:2] + "eyeDecomposeP.scale" )
                                    
                                    cmds.xform(  prefix[:2] + "eyeTransform", ws=1, t = newEyePos )
                                    cmds.xform(  prefix[:2] + "eyeBall_jnt", ws=1, t = newEyePos )                    
                                    
                                    #eyeAimNull fix
                                    eyeAimNull = prefix[:2] + "eyeAimNull"
                                    const = cmds.listRelatives( eyeAimNull, c=1, typ = "aimConstraint")
                                    if const:
                                        cmds.delete(const[0])
                                        
                                    cmds.xform(  eyeAimNull, ws=1, t= newEyePos )
                                    cmds.xform(  eyeAimNull,  ws=1, ro=(0,0,0) )                            
                                    const = cmds.aimConstraint( prefix[:2] + "eyeAim_ctl", eyeAimNull, mo=1, aimVector =[0, 0, 1], upVector=[0, 1, 0] )                    
                        
                    # 2. adjust eye joints position
                    blinkJnts = cmds.ls( prefix + "*LidBlink*_jnt" )
                    lidJnts = cmds.listRelatives( blinkJnts, c=1, typ="joint" )
                    lidConst = cmds.listRelatives( blinkJnts, c=1, typ="aimConstraint" )
                    eyeLocs = cmds.ls( prefix + "Loc*", typ = "transform" )
                    cmds.delete( lidConst )
                    cmds.parent( lidJnts, w=1 )
                    
                    ordered = cmds.getAttr( "lidFactor." + prefix[2:] + "LidVerts" )
                    posOrder = []
                    if "r_" in prefix:#set eyeLid verts' right side value
                        ordered = mirrorVertice(ordered)
                        
                    for i, v in enumerate(ordered):
                        nPos = cmds.xform( v, q=1, ws=1, t=1 )
                        posOrder.append(nPos)
               	    
                    cmds.xform( prefix[:2] + "eyeUp_loc", ws=1, t = [newEyePos[0], newEyePos[1]*2, newEyePos[2]]  )                    
                    cmds.xform( prefix + "LidP_jnt", ws=1, t = newEyePos )
                    #cmds.xform( prefix + "LidP_grp", ws=1, t = newEyePos )
                    
                    #create new hiCrv and plug shape                    
                    if cmds.objExists( prefix + "HiCrv01") and cmds.objExists( prefix + "BlinkCrv01"): 
                      
                        tmpCrv = cmds.curve( d= 1, p= posOrder )
                        #create new HiCrv ( based on lid vertices )                                 
                        newHiCrv = cmds.rename( tmpCrv, prefix  + "HiCrv01_new" )
                        cmds.parent( newHiCrv, "eyeCrv_grp" )                                        
                        curveShape_plugIn( newHiCrv, prefix  + "HiCrv01" )
                            
                        #create new prefix + CTLCrv
                        cornerPoc = cmds.getAttr( "lidFactor."+prefix[:2] + "eyeCornerPoc" )
                        ctlPoc =cmds.getAttr( "lidFactor.%s_eyeCtlPoc"%prefix )
                        ctlPoc.insert(0, cornerPoc[0])
                        ctlPoc.append(cornerPoc[1])
                        posList = []
                        for pc in ctlPoc:
                            pos = cmds.getAttr(pc+".position")[0]
                            posList.append(pos)
                     
                        ctlCrv = cmds.curve( d= 3, ep= posList )
                        newCtlCrv = cmds.rename( ctlCrv,  prefix + "CTLCrv_new" )
                        cmds.parent( newCtlCrv, "eyeCrv_grp" )
                        
                        # eyeLid Joints( "l_upLid*_jnt" ) placement ( no corner joints for lower eyelid )
                        if "_lo" in prefix:
                            posOrder = posOrder[1:-1]       
                        
                        for i, vPos in enumerate(posOrder):
    
                            cmds.xform( lidJnts[i], ws=1, t= vPos )
                            #cmds.xform( eyeLocs[i], ws=1, t= vPos )                        
                            cmds.parent ( lidJnts[i], blinkJnts[i] )
                            #cmds.joint ( cmds.listRelatives(blinkJnts[i],p=1)[0], e =True, ch=True, zso =True, oj = 'zyx', sao= 'yup')
                            cmds.aimConstraint( eyeLocs[i], blinkJnts[i], mo =1, weight=1, aimVector = (0,0,1), upVector = (0,1,0), worldUpType="object", worldUpObject = prefix[:2] + "eyeUp_loc", n = blinkJnts[i].replace("jnt", "aimConst" )  )                                    
                        
                        newCurves.append( newHiCrv )
                        newCurves.append( newCtlCrv )                    
         
            else: 
                cmds.confirmDialog( title='Confirm', message='eye rig is not created!!' )              

        
        elif loc in [ "l_eyeUp_loc", "r_eyeUp_loc" , "lipRollPos", "lipZPos" ]:
            pass        
    
    #reparent jnt
    cmds.parent( "jawRig", "eyeRig", "headSkel" )
    cmds.parent( "browDtailCtl_grp", "midCtl_grp", "attachCtl_grp" )
    if cmds.objExists("teethCtl_grp"):      
        if not cmds.listRelatives("teethCtl_grp", p=1):    
            cmds.parent( "teethCtl_grp", "bodyHeadTRS" )
          
    cmds.skinCluster( headSkinCls, e=1, mjm =0 )
        
    cmds.select( cl =1 )
    #select new curves for modeling
    if newCurves:  
        cmds.select(newCurves)        
    
    
    
def update_clsFaceMain():
    
    # change locator position after testing faceClusters 
    helpPanelGroup = "helpPanel_grp"
    mainLoc = cmds.listAttr( helpPanelGroup, a =1, userDefined =1 )
    if cmds.objExists("allPos"):
        tmpChild = cmds.listRelatives( "allPos", ad=1, ni=1, type = ["nurbsCurve", "locator"] )
        itemSet = [ cmds.listRelatives(x, p=1)[0] for x in tmpChild ]
        locSet = set(itemSet)
        #put together only locators whose position changed
        changeLoc =[]
        for loc in locSet:
            if loc in mainLoc:
                newPos = cmds.xform( loc, t = True, q = True, ws = True )
                oldPos = cmds.getAttr( helpPanelGroup +"." + loc )
                if oldPos == newPos:
                    pass
                else:
                    print loc
                    changeLoc.append( loc )
                    
                cmds.setAttr( helpPanelGroup +"." + loc, newPos, type="doubleArray" )
                
        if cmds.attributeQuery("changedLocators", node = helpPanelGroup, exists=1)==False:
            cmds.addAttr( helpPanelGroup, ln ="changedLocators", dt = "stringArray" )
        cmds.setAttr( helpPanelGroup + ".changedLocators", type= "stringArray", *([len(changeLoc)] + changeLoc))
        
    else: 
        cmds.confirmDialog( title='Confirm', message='import face Locator first!!' )
                
    headGeo = cmds.getAttr( helpPanelGroup + ".headGeo" )
    vtxLeng = cmds.polyEvaluate( headGeo, v=1 )
    headSkinCls =mel.eval("findRelatedSkinCluster %s"%headGeo )
    if headSkinCls:
        if "headSkel_jnt" in cmds.skinCluster( headSkinCls, q=1, wi=1 ):
            cmds.skinCluster( headSkinCls, e=1, mjm =1 )

    #unparent jawRig, eyeRig
    cmds.parent( "jawRig", "eyeRig", "browMainCtl_grp","lip_ctl_grp", "browDtailCtl_grp", w=1 )#follow polyEdgecurves on the face
    newCurves = []
    runNum = 0
    for loc in changeLoc:
            
        #put skinCluster on move joint mode    
        if loc == "headSkelPos":

            #adjust headSkel location
            newPos = cmds.getAttr( helpPanelGroup +"." + loc )        
            cmds.xform( "headSkel", ws=1, t = newPos )
        
        elif loc in [ "jawRigPos" , "lipYPos" , "lipEPos" ]:
        
            #unparent LipJotY, LipRollP
            lipYGrp = cmds.ls("*LipJotY**")
            lipRollGrp = cmds.ls( "*LipRollP*")
            if lipYGrp and lipRollGrp:
                
                for jnt in lipYGrp + lipRollGrp:
                    cmds.parent( jnt, w=1 )
                    
                #make change based on the locator that has a change in position
                if loc == "jawRigPos":
                    newJPos = cmds.getAttr( helpPanelGroup +"." + loc )      
                    cmds.xform( "jawRig", ws=1, t = newJPos ) # only jawRig(lipJotX) to new position
                    
                    # adjust teenth/tongue grp_nodes and joints ( except tongue joints because it constraint to jawClose_jnt )
                    extraGrp =[ "teethCtl_grp", "teethJnt_grp" ]
                    for exGrp in extraGrp:
                        if cmds.objExists(exGrp):                              
                                
                            cmds.parent( exGrp, w=1 )
                            cmds.xform( exGrp, ws=1, t = newJPos )
                                                           
                elif loc == "lipYPos":
                
                    newYPos = cmds.getAttr( helpPanelGroup +"." + loc )
                    for i, jnt in enumerate(lipYGrp):            
                        cmds.xform( jnt, ws=1, t = newYPos )
                        
                elif loc == "lipEPos":
                
                    #reposition the "up/loLipRollP" on the new GuideCrv
                    for ud in [ "up", "lo" ]:
                        if cmds.objExists( ud + "_guide_crv"):
                            cmds.delete( ud +"_guide_crv" )

                        orderedVerts = cmds.getAttr( "lipFactor." + ud + "LipVerts" )
                        vNum = len( orderedVerts )
                        lipSPos = cmds.getAttr( helpPanelGroup +".lipSPos" )              
                        lipNPos = cmds.getAttr( helpPanelGroup +".lipNPos" )            
                        lipEPos = cmds.getAttr( helpPanelGroup +".lipEPos" )
                        lipWPos = [-lipEPos[0], lipEPos[1], lipEPos[2]]
                        if ud == "up":
                            lipCntPos = lipNPos            
                        elif ud == "lo":
                            lipCntPos = lipSPos
                            
                        tempCrv = cmds.curve(d= 3, ep= [lipWPos, lipCntPos,lipEPos] ) 
                        guideCrv = cmds.rename(tempCrv, ud + "_guide_crv" )
                        guideCrvShape = cmds.listRelatives(guideCrv, c = True) 
                        cmds.rebuildCurve( guideCrv, d = 3, rebuildType = 0, keepRange = 0)
                         
                        linearDist = 1.0/(vNum-1)
                        increment = 0
                        lipPoc = []
                        for i in range( vNum ):
                        
                            guidePoc =cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = ud +'_lipGuide' + str(i).zfill(2) + '_poc' )
                            cmds.connectAttr( guideCrvShape[0] + ".worldSpace" , guidePoc + ".inputCurve" )
                            cmds.setAttr( guidePoc + ".turnOnPercentage", 1 )
                            cmds.setAttr( guidePoc +".parameter", increment )
                            #pocPos = cmds.getAttr( guidePoc + ".position")[0]        
                            lipPoc.append( guidePoc )
                            increment = increment + linearDist
                        
                        if ud == "lo":
                            lipPoc = lipPoc[1:-1]
                            
                        lipGrp = cmds.ls( ud + "LipRollP*") 
                        for i, poc in enumerate(lipPoc):
                            nPos = cmds.getAttr( poc + ".position")[0]
                            cmds.xform ( lipGrp[i], ws=1, t = nPos )  
                                
                for i, jot in enumerate(lipYGrp):
                    cmds.parent(jot, jot.replace("JotY","JotX"))
                    
                    rollTGrp = lipRollGrp[i].replace("P", "T")
                    cmds.parent( lipRollGrp[i], rollTGrp )            
            
            else:
                if loc == "jawRigPos":
                    newJPos = cmds.getAttr( helpPanelGroup +"." + loc )      
                    cmds.xform( "jawRig", ws=1, t = newJPos ) # only jawRig(lipJotX) to new position
        
        elif loc in ["rotXPivot" , "rotYPivot"]:
            if runNum == 0:
 
                baseJnts = cmds.ls( "*_browBase*_jnt" )
                if baseJnts:
                    rotYJnts = cmds.ls( "*_browRotY*_jnt" )
                    #browDetail ctls
                    baseCtl =cmds.ls( "*brow*_base", typ = "transform" )            

                    newXPos = cmds.getAttr( helpPanelGroup +".rotXPivot" )
                    newYPos = cmds.getAttr( helpPanelGroup +".rotYPivot" )            

                    browPJnts = cmds.listRelatives( rotYJnts, c=1)
                    center = (len( browPJnts)-1 )/2
                    browJntOrder = browPJnts[center+1:][::-1] + [browPJnts[0]] + browPJnts[1:center+1]
                    baseCtlOrder = baseCtl[center+1:][::-1] + [baseCtl[0]] + baseCtl[1:center+1]
                    dist = cmds.getAttr( browPJnts[0] + ".tz")
                    #new browVerts in order
                    browVerts = cmds.getAttr( "browFactor.browVerts" )    
                    mirrorVerts = mirrorVertice( browVerts )
                    orderedVerts = mirrorVerts[1:][::-1] + browVerts
                    
                    cmds.parent( rotYJnts, w=1 )            
                    cmds.parent( browPJnts, w=1 )
                    for i, jnt in enumerate(baseJnts):
                    
                        #put "*browBase_jnt" on new position of rotXPivot
                        cmds.xform( jnt, ws=1, t= newXPos )
                        cmds.xform( baseCtlOrder[i], ws =1, t = newXPos )
                        
                        rotYCtl = cmds.listRelatives( baseCtlOrder[i], c=1 )[0]
                        #put "*browRotY_jnt" on new position of rotYPivot
                        cmds.xform( rotYJnts[i], ws=1, t= newYPos )
                        cmds.xform( rotYCtl, ws =1, t = newYPos )

                        vtxPos = cmds.xform( orderedVerts[i], q=1, ws=1, t=1 )
                        #put "*browP_jnt" on new position of vertices
                        cmds.xform( browJntOrder[i], ws=1, t= vtxPos )
                        #place brow_dummy on new position of vertices                
                        cmds.xform( cmds.listRelatives( rotYCtl, c=1 )[0], ws=1, t=( vtxPos[0],vtxPos[1], vtxPos[2]+ dist/20  ) )

                        cmds.parent( rotYJnts[i], cmds.listRelatives( baseJnts[i], c=1)[0] )
                        cmds.parent( browPJnts[i], rotYJnts[i] )  
                runNum+=1
    
        elif loc == "lEyePos":
            # reposition up vector (l/r_eyeUp_loc)
            newEyePos = cmds.getAttr( helpPanelGroup +"." + loc )                
            cmds.xform( "eyeRig", ws=1, t = ( 0, newEyePos[1], newEyePos[2]) ) # only eyeRig to new position
            
            if cmds.objExists("l_eyeUp_loc") and cmds.objExists("r_eyeUp_loc"):            

                for i, prefix in enumerate(["l_up", "l_lo","r_up", "r_lo"]):                
                    
                    if i in [0,2]:
                        val = 1
                        if "r_" in prefix:#set lEyeLoc right side value
                            newEyePos = [ -newEyePos[0], newEyePos[1], newEyePos[2] ]
                            val = -1
                        # 1. adjust eye_rig grp nodes position                      
                        if cmds.objExists( prefix[:2] + "eyeBall_jnt"):

                            eyeJntPos = cmds.xform( prefix[:2] + "eyeBall_jnt", q=1, ws=1, t=1)                     
                            if not newEyePos == eyeJntPos: #zero out all eyeRig grp_nodes
                                
                                eyeRigChild = cmds.listRelatives( prefix[:2] + "eyeP", ad=1 )
                                for child in eyeRigChild:
                                    cmds.xform( prefix[:2] + "eyeP", ws=1, t = newEyePos )
                                    cmds.xform( child, ws=1, t = newEyePos )
                           
                            eyeRotY = cmds.getAttr( "lEyePos.ry" )
                            eyePrntRY =cmds.getAttr(  prefix[:2] + "eyeRP.ry" )
                            if not eyePrntRY== eyeRotY*val:
                                eyeConversion = cmds.shadingNode('unitConversion', asUtility =1, n = prefix[:2] + 'eye_conversion' )
                                cmds.connectAttr( "lEyePos.ry", eyeConversion + ".input"  )
                                cmds.setAttr(  eyeConversion + ".conversionFactor", val )
                                cmds.connectAttr( eyeConversion + ".output", prefix[:2] + "eyeRP.ry" )      
                      
                        #place eyeBall_jnts on newEyeloc
                        #1.check if there is decomposeMatrix node
                        eyeDecomposeP = prefix[:2] + "eyeDecomposeP"                        
                        cnnct = cmds.listConnections( eyeDecomposeP, s=1, d=0 )
                        if cnnct:
                            for x in set(cnnct):
                                if cmds.nodeType(x) == "decomposeMatrix":
                                    dMatrix = x
                                   
                                else:
                                    eyeDComp = cmds.shadingNode('decomposeMatrix', asUtility =1, n = prefix[:2] + 'eye_decomMtrx' )
                                    cmds.connectAttr( "headSkel.worldInverseMatrix", eyeDComp + ".inputMatrix" )
                                    cmds.connectAttr( eyeDComp + ".outputTranslate", prefix[:2] + "eyeDecomposeP.translate" )
                                    cmds.connectAttr( eyeDComp + ".outputRotate", prefix[:2] + "eyeDecomposeP.rotate" )
                                    cmds.connectAttr( eyeDComp + ".outputScale", prefix[:2] + "eyeDecomposeP.scale" )
                                    
                                    cmds.xform(  prefix[:2] + "eyeTransform", ws=1, t = newEyePos )
                                    cmds.xform(  prefix[:2] + "eyeBall_jnt", ws=1, t = newEyePos )                    
                                    
                                    #eyeAimNull fix
                                    eyeAimNull = prefix[:2] + "eyeAimNull"
                                    const = cmds.listRelatives( eyeAimNull, c=1, typ = "aimConstraint")
                                    if const:
                                        cmds.delete(const[0])
                                        
                                    cmds.xform(  eyeAimNull, ws=1, t= newEyePos )
                                    cmds.xform(  eyeAimNull,  ws=1, ro=(0,0,0) )                            
                                    const = cmds.aimConstraint( prefix[:2] + "eyeAim_ctl", eyeAimNull, mo=1, aimVector =[0, 0, 1], upVector=[0, 1, 0] )                    
                        
                    # 2. adjust eye joints position
                    blinkJnts = cmds.ls( prefix + "*LidBlink*_jnt" )
                    lidJnts = cmds.listRelatives( blinkJnts, c=1, typ="joint" )# l_upLid*_jnt
                    lidConst = cmds.listRelatives( blinkJnts, c=1, typ="aimConstraint" )
                    eyeLocs = cmds.ls( prefix + "Loc*", typ = "transform" )
                    cmds.delete( lidConst )
                    cmds.parent( lidJnts, w=1 )
                    
                    ordered = cmds.getAttr( "lidFactor." + prefix[2:] + "LidVerts" )
                    posOrder = []
                    if "r_" in prefix:#set eyeLid verts' right side value
                        ordered = mirrorVertice(ordered)
                        
                    for i, v in enumerate(ordered):
                        nPos = cmds.xform( v, q=1, ws=1, t=1 )
                        posOrder.append(nPos)
               	    
                    cmds.xform( prefix[:2] + "eyeUp_loc", ws=1, t = [newEyePos[0], newEyePos[1]*2, newEyePos[2]]  )                    
                    cmds.xform( prefix + "LidP_jnt", ws=1, t = newEyePos )
                    #cmds.xform( prefix + "LidP_grp", ws=1, t = newEyePos )
                    
                    #create new hiCrv and plug shape                    
                    if cmds.objExists( prefix + "HiCrv01") and cmds.objExists( prefix + "BlinkCrv01"): 
                      
                        tmpCrv = cmds.curve( d= 1, p= posOrder )
                        #create new HiCrv ( based on lid vertices )                                 
                        newHiCrv = cmds.rename( tmpCrv, prefix  + "HiCrv01_new" )
                        cmds.parent( newHiCrv, "eyeCrv_grp" )                                        
                        curveShape_plugIn( newHiCrv, prefix  + "HiCrv01" )
                            
                        #create new prefix + CTLCrv
                        cornerPoc = cmds.getAttr( "lidFactor."+prefix[:2] + "eyeCornerPoc" )
                        ctlPoc =cmds.getAttr( "lidFactor.%s_eyeCtlPoc"%prefix )
                        ctlPoc.insert(0, cornerPoc[0])
                        ctlPoc.append(cornerPoc[1])
                        posList = []
                        for pc in ctlPoc:
                            pos = cmds.getAttr(pc+".position")[0]
                            posList.append(pos)
                     
                        ctlCrv = cmds.curve( d= 3, ep= posList )
                        newCtlCrv = cmds.rename( ctlCrv,  prefix + "CTLCrv_new" )
                        cmds.parent( newCtlCrv, "eyeCrv_grp" )                       

                        #create null for blinkCls / re-constraint to eyeLoc 
                        for i, Jnt in enumerate(blinkJnts):
                           
                            cmds.xform( lidJnts[i], ws=1, t= posOrder[i] )                       
                            
                            #create null for cls handle
                            scaleJnt = cmds.listRelatives( Jnt, p =1, typ="joint" )[0]
                            handle = cmds.group( em=1, p = scaleJnt, name= Jnt.replace("_jnt","_null") )
                            handlePrnt = cmds.group( handle, p = scaleJnt, name= handle.replace("_null","_grp") )
                            cmds.select( Jnt, handle )
                            twitchPanelConnect.transferConnections( "node", "out" )
                            oldCls = Jnt.replace("_jnt","_cls")
                            
                            valStr = ""
                            for n in range(vtxLeng):
                                
                                copyWgt = cmds.getAttr( oldCls + ".wl[0].w[%s]"%str(n) )
                                valStr += str(copyWgt)+" "                     
                            
                            #aim constraint handle parent node
                            const = cmds.aimConstraint( eyeLocs[i], handlePrnt, mo =0, weight=1, aimVector = (0,0,1), upVector = (0,1,0), worldUpType="object", worldUpObject = prefix[:2] + "eyeUp_loc", n = Jnt.replace("jnt", "aimConst" )  )                                    
                            cmds.delete(const)
                            
                            cmds.aimConstraint( eyeLocs[i], handle, mo =1, weight=1, aimVector = (0,0,1), upVector = (0,1,0), worldUpType="object", worldUpObject = prefix[:2] + "eyeUp_loc", n = Jnt.replace("jnt", "aimConst" )  ) 
                            cls = cmds.cluster( headGeo, n = handle.replace("_null","_nCls") )
                            cmds.cluster( cls[0], e=1, bindState=1, wn = ( handle , handle ) )
                            cmds.parent ( lidJnts[i], handle )
                            
                            cmds.delete(cls[1]) 
                            
                            #copy cls weight before deleting it
                            commandStr = ("setAttr -s " +str(vtxLeng) + " %s.wl[0].w[0:%s] "%(cls[0], str(vtxLeng-1)) + valStr );
                            mel.eval(commandStr)
                            cmds.delete(oldCls, Jnt )
                            
                        newCurves.append( newHiCrv )
                        newCurves.append( newCtlCrv )                    
         
            else: 
                cmds.confirmDialog( title='Confirm', message='eye rig is not created!!' )              

        
        elif loc in [ "l_eyeUp_loc", "r_eyeUp_loc" , "lipRollPos", "lipZPos" ]:
            pass        
    
    #reparent jnt
    cmds.parent( "jawRig", "eyeRig", "headSkel" )
    cmds.parent( "browMainCtl_grp","lip_ctl_grp", "ctl_onFace" )
    cmds.parent( "browDtailCtl_grp", "attachCtl_grp" )
    
    if cmds.objExists("teethCtl_grp"):      
            if not cmds.listRelatives("teethCtl_grp", p=1):    
                cmds.parent( "teethCtl_grp", "attachCtl_grp" )
          
    cmds.skinCluster( headSkinCls, e=1, mjm =0 )
        
    cmds.select( cl =1 )
    #select new curves for modeling
    if newCurves:  
        cmds.select(newCurves)    


#shape CTL_crv to Hi_crv!!! and then plug in
#prefix = ["l_up", "l_lo", "r_up", "r_lo" ]
def update_ctlConnection(prefix):
 
    changeLoc = cmds.getAttr( "helpPanel_grp.changedLocators" )
    if "lEyePos" in changeLoc:
        targetCtlCrv = prefix + "CTLCrv01"
        if cmds.objExists(targetCtlCrv):
            CtlCrvNew = prefix + "CTLCrv_new"
            #delete target shapes 
            cmds.delete( cmds.listRelatives("eyeShapeCrv_grp", c=1 ))
            curveShape_plugIn( CtlCrvNew, targetCtlCrv )

            if cmds.objExists(targetCtlCrv + "BaseWire"):
                curveShape_plugIn( CtlCrvNew, targetCtlCrv + "BaseWire" )
            
            #plug BlinkLevelCrv_new
            if not cmds.objExists(prefix + "BlinkLevelCrv_new"):
                
                blinkLevelCrvNew = cmds.duplicate( CtlCrvNew, rc=1, n = prefix + "BlinkLevelCrv_new" )[0]
                print blinkLevelCrvNew
                if blinkLevelCrvNew in [ "l_upBlinkLevelCrv_new", "r_upBlinkLevelCrv_new" ]:
                    curveShape_plugIn( blinkLevelCrvNew, prefix[:2] + "BlinkLevelCrv" )
                #get the baseWire curve from wireDeformer
                blinkBaseWire = cmds.listConnections( prefix + "Blink_wire.baseWire", s=1, d=0 )
                
                curveShape_plugIn( blinkLevelCrvNew, blinkBaseWire[0] )                    
                print blinkBaseWire
            HiCrvNew = prefix  + "HiCrv01_new" #already pluged in ( HiCrv deleted )
            
            #plug HiCrv to BlinkCrv
            blinkCrv = prefix + "BlinkCrv01"
            curveShape_plugIn( HiCrvNew, blinkCrv )
            #plug HiCrv to WideCrv
            wideCrv = prefix + "Wide_crv"
            if cmds.objExists(wideCrv):
                curveShape_plugIn( HiCrvNew, wideCrv )         
            
            cmds.delete( CtlCrvNew, HiCrvNew )
        
        else:
            cmds.confirmDialog( title='Confirm', message='eyeCtl curves not exist!!' )
        '''break the blendShape connection first!!!
        blendShapeMethods.bakeTarget_reconnect( targetCtlCrv )
        cmds.parent( targetCtlCrv + "_tgtGrp", eyeShapeCrv_grp )
        
        blinkJnts = cmds.ls( prefix + "LidBlink*_jnt" )
        lidConst = cmds.listRelatives( blinkJnts, c=1, typ="aimConstraint" )
        for con in lidConst:
            cmds.setAttr( con + ".nodeState", 0 )
        
        #activate deformers back 
        #activateDeformers( blinkCrv )
        #activateDeformers( targetCtlCrv )'''


        
def update_browCtl(selCrv):
    
    changeLoc = cmds.getAttr( "helpPanel_grp.changedLocators" )
    if "rotXPivot" in changeLoc or "rotYPivot" in changeLoc:
    
        browGuideCrv = [ c for c in cmds.listRelatives("guideCrv_grp", c=1) if "brow" in c ][0]
        oldBrowGuideCrv = cmds.rename( browGuideCrv, "brow_guide_crv_old")        

        browCtls = cmds.listRelatives( "browCtl_grp", c=1 )
        cmds.rebuildCurve( selCrv, rebuildType = 0, spans = len(browCtls)-1, keepRange = 0, degree = 1, ch=1 )    
        newBrowGuideCrv = cmds.rename( selCrv, "brow_guide_crv01" )
        cmds.parent( "brow_guide_crv01", "guideCrv_grp" )
        
        #polyToCurve feed from headGeo ( no orig shape required )
        cmds.select( oldBrowGuideCrv, newBrowGuideCrv )
        twitchPanelConnect.transferConnections( "shape", "out" )
            
        cmds.delete( oldBrowGuideCrv )
        
        
        
        


def curveShape_plugIn( plugCrv, targetCrv ):
    
    plugShape = cmds.listRelatives( plugCrv, c=1, typ = "nurbsCurve" )[0]
    plugPoints = cmds.getAttr( plugShape + ".controlPoints" , mi=1 )
    
    targetOrigShape = getOrigMesh( targetCrv )
    if targetOrigShape:
    
        baseWireAttr =[]
        targetHistory = cmds.listHistory( targetCrv, pruneDagObjects =1, interestLevel= 1 )#for TDs
        dformers = [ x for x in targetHistory if "geometryFilter" in cmds.nodeType( x, inherited =1 )]
        for dform in dformers:
            if cmds.nodeType(dform) == "skinCluster":
                skinCls = dform
                cmds.skinCluster( skinCls, e=1, mjm = 1 )
                
            elif cmds.nodeType(dform) == "blendShape":
                BS = dform
                cmds.setAttr( BS + ".nodeState", 1 )
                
            elif cmds.nodeType(dform) == "wire":
                wireDform = dform                
                cmds.setAttr( wireDform + ".nodeState", 1 )
                
        #plug newCtl crv Shape!!
        for i in range(len(plugPoints)):
        
            cmds.connectAttr( plugShape + ".controlPoints[%s]"%str(i), targetOrigShape + ".controlPoints[%s]"%str(i) )
            
    else:    
        targetShape = cmds.listRelatives( targetCrv, c=1, typ = "nurbsCurve" )[0] 
        for i in range(len(plugPoints)):
            cmds.connectAttr( plugShape + ".controlPoints[%s]"%str(i), targetShape + ".controlPoints[%s]"%str(i) )
            
    #cmds.delete( plugCrv )

                         

def activateDeformers( crv ):
    
    crvHistory = cmds.listHistory( crv, pruneDagObjects =1, interestLevel= 1 )
    dformers = [ x for x in crvHistory if "geometryFilter" in cmds.nodeType( x, inherited =1 )]
    for dform in dformers:
        if cmds.nodeType(dform) == "skinCluster":
            skinCls = dform
            cmds.skinCluster( skinCls, e=1, mjm = 0 )#normal
            print dform + "back"
            
        elif cmds.nodeType(dform) == "blendShape":
            BS = dform
            cmds.setAttr( BS + ".nodeState", 0 )
            print dform + "back"
        elif cmds.nodeType(dform) == "wire":
            wireDform = dform
            cmds.setAttr( wireDform + ".nodeState", 0 )
            print dform + "back"


def getOrigMesh( obj ):

    dfoms = cmds.listHistory(obj, il = 1, pdo =1 )    
    origShp = []
    if dfoms:
    
        tweakND = [ x for x in dfoms if cmds.nodeType(x)=="tweak" ]
        if tweakND:
        
            cnnct = cmds.listHistory(tweakND[0] ) 
            
            for ct in cnnct:
                if cmds.nodeType(ct) in ( "mesh", "nurbsSurface", "nurbsCurve" ):
                    if cmds.getAttr(ct + ".intermediateObject"):
                        origShp.append(ct)
                        
            if len(origShp)==1:
                
                return origShp[0]
            
            elif len(origShp)==0:
                cmds.confirmDialog(title='Confirm', message='%s has no origShapes'%obj ) 
                 
            else:
                cmds.confirmDialog(title='Confirm', message='%s has multiple origShapes (%s and %s), do it manuallye'%(obj, origShp[0], origShp[1]) )  
    
    else:
        cmds.confirmDialog(title='Confirm', message='%s has no deformer'%obj ) 
    


def mirrorVertice( verts ):
    headMesh = cmds.getAttr("helpPanel_grp.headGeo")
    cpmNode = cmds.createNode("closestPointOnMesh", n = "closestPointM_node")
    cmds.connectAttr( headMesh + ".outMesh", cpmNode + ".inMesh")
    cmds.connectAttr( headMesh + ".worldMatrix[0]", cpmNode +".inputMatrix" )
    orderedVerts=[]
    for v in verts:
        
        vPos = cmds.xform( v, q=1, ws=1, t=1)   
        mirrorVPos = vPos
        mirrorVPos[0] *= -1
        
        cmds.setAttr( cpmNode + ".inPosition", mirrorVPos[0],mirrorVPos[1],mirrorVPos[2], type="double3" )
        vtxIndx = cmds.getAttr(cpmNode + ".closestVertexIndex")
        vtx = "{0}.vtx[{1}]".format(headMesh, vtxIndx)
        orderedVerts.append(vtx)
    
    return orderedVerts

    
#miscellaneous_____________________________________________________________________________________________________________
#when final rigging is done
def cleanUp_faceMain( layer ):
    
    #delete clusters for skinWeight calculation 
   
    if layer in [ "cluster", "all" ]:
        
        clusterDict = [ 'jawOpen_cls', 'jawClose_cls','mouth_cls', 'lip_cls', 'lipRoll_cls', 'l_eyeBlink_cls', 'r_eyeBlink_cls', 'browUp_cls', 'browDn_cls', 'browTZ_cls',
         'upLipRoll_cls', 'bttmLipRoll_cls']         
        
        for cls in clusterDict:
            if cmds.objExists(cls):
                #clsHandle, groupPart, ID...
                connects = cmds.listConnections( cls, s=1, d=0 )         
                for cnnt in connects:
                    if cmds.objExists(cnnt):
                        if cmds.nodeType( cnnt ) == "transform":
                            cmds.delete(cmds.listRelatives(cnnt, p =1 )[0])
                        
                        elif not cmds.nodeType( cnnt ) == "blendShape":
                            cmds.delete(cnnt)
                        
    #delete squach rig / cleanup
    elif layer in [ "squach", "all" ]:

        if cmds.objExists("topSquach_ctl"):
            latticeSkin = cmds.getAttr( "topSquach_ctl.latticeSkin")
            boxSkin = cmds.getAttr( "topSquach_ctl.squachBox_skin")
            box = cmds.skinCluster(boxSkin, q=1, g=1 )
            latt = cmds.skinCluster(latticeSkin, q=1, g=1 )
            boxHist = set(cmds.listHistory( box[0], ac=1 ))
            lattHist = set(cmds.listHistory( latt[0], ac=1 ))
             
            unionHist =  boxHist | lattHist
            unionHist.add("squachCtl_grp")
            for un in unionHist:
                if cmds.objExists(un):
                    if not un in ["jnt_grp","faceMain"]:
                        if cmds.nodeType(un) in ["mesh", "nurbsCurve", "lattice" ]:
                            cmds.delete( cmds.listRelatives(un, p=1)[0])
                        else:
                            cmds.delete(un)
                            
    #get rid of blendShape targets
    elif layer in [ "blendShape", "all" ]:
        print layer
         
    

#드라이버와 ctls 의 로테이션이 다를때: 같은 orient를 가진 로케이터 생성 and parent
def faceCtlRotate_toBody( ):
    mySel = cmds.ls(sl=1)
    driverCtl = mySel[0]
    ctlGrps = mySel[1:] 
    DCM = cmds.shadingNode( "decomposeMatrix", asUtility =1, n = 'headCtlDecompose')
    cmds.connectAttr( driverCtl + ".worldMatrix", DCM +".inputMatrix" )
    #if 
    ctlPrnt = []
    for grp in ctlGrps:
        
        ctlNulls = cmds.listRelatives( grp, ad=1, type = "transform" )
        
        for null in ctlNulls:
            if cmds.listConnections( null + ".translate", s=1, d=0 ):
                ctlPrnt.append(null)
                
    for ctlP in ctlPrnt :  
        
        cmds.connectAttr( DCM + ".outputRotateX",  ctlP + ".rotateX" )
        cmds.connectAttr( DCM + ".outputRotateY",  ctlP + ".rotateY" )
        cmds.connectAttr( DCM + ".outputRotateZ",  ctlP + ".rotateZ" )
        
        
        
def renameDuplicates():
    #Find all objects that have the same shortname as another
    #We can indentify them because they have | in the name
    duplicates = [f for f in cmds.ls() if '|' in f]
    #Sort them by hierarchy so that we don't rename a parent before a child.
    duplicates.sort(key=lambda obj: obj.count('|'), reverse=True)
     
    #if we have duplicates, rename them
    if duplicates:
        for name in duplicates:
            # extract the base name
            m = re.compile("[^|]*$").search(name) 
            shortname = m.group(0)
 
            # extract the numeric suffix
            m2 = re.compile(".*[^0-9]").match(shortname) 
            if m2:
                stripSuffix = m2.group(0)
            else:
                stripSuffix = shortname
             
            #rename, adding '#' as the suffix, which tells maya to find the next available number
            newname = cmds.rename(name, (stripSuffix + "#")) 
            print "renamed %s to %s" % (name, newname)
             
        return "Renamed %s objects with duplicated name." % len(duplicates)
    else:
        return "No Duplicates"    
    


def deleteUnknown_plugins():
    unknown_plugins = cmds.unknownPlugin(q=True, list=True) or []
    for up in unknown_plugins:
        print up
        cmds.unknownPlugin(up, remove=True)
        
        
#set keys on all ctrls
def dgTimer():
    dataPath = cmds.fileDialog2(fileMode=3, caption="set directory")
    #cmds.file( filename[0], i=True );
    i = 0
    while os.path.isdir(dataPath[0] + "/dgTimer%s"%i):   
        i += 1
    os.makedirs( dataPath[0]+"/dgTimer"+str(i))
    
    ## Change the path to where you want to output the DGTimer result
    FILENAME = dataPath[0] + '/dgTimer'+str(i)+'/dgTimerOutput.txt'
    
    ## Reset the timer and set it on
    cmds.dgtimer( on=True, reset=True )
    
    ## Play your scene
    cmds.play( wait=True )
    
    ## Turn the timer off
    cmds.dgtimer( off=True )
    
    ## Write the result to a file
    cmds.dgtimer( outputFile=FILENAME, q=True )
    
    
    

# select headGeo(or polyToCurve) and ctls( or parent👈) that are on the skin 
def stickCtlToFace( obj, ctls ):

    objShp = cmds.listRelatives( obj, c=1, ni =1, s=1 )[0]
    if cmds.nodeType(objShp) =='nurbsCurve':
        for ctl in ctls:
            revMult = cmds.shadingNode( "multiplyDivide", asUtility=1, n = ctl + "rev_mult" )
            pos = cmds.xform( ctl, q=1, w=1, t=1 )
            uParam= getUParam( pos, obj )
            poc = cmds.shadingNode( 'pointOnCurveInfo', asUtility =1, n = obj+'_stickyPoc'+str(i) )
            cmds.connectAttr( objShp + ".worldSpace", poc + ".inputCurve")
            cmds.setAttr( poc + ".parameter", prm )
            stickyGrp = cmds.group( ctl, n = ctl + "_stickyGrp")      
            compensateGrp = cmds.group( ctl, n = ctl + "_compensateGrp")
            cmds.connectAttr( poc + ".position", stickyGrp + ".t" )
            cmds.connectAttr ( ctl + ".t", revMult + ".input1" )
            cmds.setAttr( revMult + ".input2", -1,-1,-1 ) 
            cmds.connectAttr ( revMult + ".output", compensateGrp + ".t" )                   

                
    elif cmds.nodeType(objShp) == 'mesh':
        for ctl in ctls:
            childList = cmds.listRelatives( ctl, ad=1 )
            ctlShape = ''
            for child in childList:
                if not cmds.nodeType(child) == 'transform':
                    ctlShape = child                    
            controller = cmds.listRelatives( ctlShape, p=1 )[0] 
            revMult = cmds.shadingNode( "multiplyDivide", asUtility=1, n = ctl + "rev_mult" )
            uv = getGeo_uvParam( obj, ctl )
            folicTran = createFollicle( obj, uv[0], uv[1], ctl + "folic" )
            stickyGrp = cmds.group( ctl, n = ctl + "_stickyGrp")      
            compensateGrp = cmds.group( ctl, n = ctl + "_compensateGrp")
            cmds.parentConstraint( folicTran[1], stickyGrp, mo=1 )
            cmds.connectAttr ( controller + ".t", revMult + ".input1" )
            cmds.setAttr( revMult + ".input2", -1,-1,-1 ) 
            cmds.connectAttr ( revMult + ".output", compensateGrp + ".t" )            
               



# create curve ctl with unique name
def ctlShapeTransfer(): 

    source = cmds.ls(sl=1)[0]
    cmds.setAttr( source + '.t', 0,0,0 )
    transform = cmds.ls(sl=1)[1]
    cmds.xform(source, cp = 1 )
    hiddenPos = cmds.xform( source, q=1, ws=1, piv=1 )
    pos = cmds.xform( source, q=1, ws=1, t=1 )
    
    if hiddenPos[:3] == pos:
        ctlShapeSwap( source, transform)
        
    else: # if crv is freezed or manually created      
        cls = cmds.cluster( source )
        cmds.setAttr( cls[1] + '.t', -hiddenPos[0] ,-hiddenPos[1] ,-hiddenPos[2]  )
        cmds.xform( source, cp = 1 )
        cmds.delete( source, ch=1 )
        print source, transform
        ctlShapeSwap( source, transform)
        



#no freeze. swap in world space
def ctlShapeSwap( source, transform):
    
    scPos = cmds.xform( source, q=1, ws=1, t=1 )
    tranPos = cmds.xform( transform, q=1, ws=1, t=1 )
        
    shp = cmds.listRelatives(source, c=1, ni=1, s=1)
    oldShp = cmds.listRelatives(transform, c=1, ni=1, s=1)
    cmds.parent( shp, transform, s=1, r=1 )
    
    cmds.delete( oldShp, source )
    for s in shp:
        cmds.rename( s, oldShp ) 




#create uniform curve with 32 evenly spaced CVs.
#create curve with same structure( same starting point / number of cvs ) 
def create_uniformCurve( mapCrv, name ):
    
    crvShp = cmds.listRelatives( mapCrv, c=1, ni =1, s=1 )[0]
    print crvShp
    crvFn = OpenMaya.MFnNurbsCurve(getDagPath( crvShp ) )
    crvForm = cmds.getAttr( crvShp + '.form' )
    
    if crvForm == 0: # if crv form is open
            
        posList = []
        increm = 1.0/30
        for i in range(31):           
        
            parameter = crvFn.findParamFromLength(crvFn.length() * increm * i)
            point = OpenMaya.MPoint()
            crvFn.getPointAtParam(parameter, point)
            pos = [point.x, point.y, point.z]
            posList.append(pos)
            
        uniformCrv =[ cmds.curve( d=3, p=posList, n= name + "_uniCrv0" + mapCrv[-1] ) ]
        cmds.xform( uniformCrv[0], cp=1)
            
    if crvForm in [1,2]: # if crv form is close
        
        uniformCrv = cmds.circle( c = (0,0,0), nr = (0,0,1), sw = 360, r=1, d=3, tol = 0.01, s=32, n = name + "_uniCrv0" + mapCrv[-1] )
        cmds.reverseCurve( uniformCrv[0], ch =1, rpo =1 )    
        crvCvs = cmds.ls( uniformCrv[0] + '.cv[*]', fl=1 )
            
        increm = 1.0/32
        for i in range(32): 
        
            parameter = crvFn.findParamFromLength(crvFn.length() * increm * i)
            point = OpenMaya.MPoint()
            crvFn.getPointAtParam(parameter, point)
            pos = [point.x, point.y, point.z]
            print parameter
            cmds.xform( crvCvs[i], ws=1, t= pos )
        
        cmds.xform( uniformCrv[0], cp=1)
    
    return uniformCrv[0]



# joints along the curve (#brais, snake... )
def createJntAlongCrv( numJnt, title ):
    #gather info
    crvSel = cmds.ls(sl=1)[0]
    uniCrv = create_uniformCurve( crvSel, title )  
    increm = 1.0/numJnt
    jnts = []
    for i in range( 0, numJnt+1 ):
        cmds.select(cl=1)
        newJnt = cmds.joint( n = title + str(i) )
        motionPath = cmds.pathAnimation( newJnt, c = uniCrv, fractionMode=1, follow=1, followAxis ="x", upAxis = "y", worldUpType = "vector",  worldUpVector =(0, 1, 0)  )
        cmds.cutKey( motionPath + ".u", time = () )
        cmds.setAttr( motionPath + ".u",  increm*i )
        jnts.append(newJnt)
    
    cmds.select(cl=1)
    #create new name for jnts
    alphabet = string.ascii_uppercase
    order = 0
    for i, A in enumerate(alphabet):
        name = cmds.ls( title + A + "_*" )
        if name:
            order = i+1
        
    ABC = alphabet[order]
    jntList = []
    for i, j in enumerate(jnts):
        xyz = cmds.xform( j, q=1, ws=1, t=1 )
        AJnt = cmds.joint(  p=xyz, a=True, n= title + ABC + "_jnt%s"%str(i+1).zfill(2) )
        if i > 0 :
            BJnt = title + ABC + "_jnt%s"%str(i-1).zfill(2)
            #cmds.parent( AJnt, BJnt )
        jntList.append(AJnt)
        cmds.delete(j)
    cmds.select(jntList)
    cmds.joint( e=1, oj='xyz', ch=True, zso =True, sao= 'yup'  )
    cmds.delete(uniCrv)
    
    hair_system = "hairSystem_grp"
    if not cmds.objExists(hair_system):
        cmds.group(em=1, n = "hairSystem_grp" )
        
    prntGrp = createPntNull( [jntList[0]] )
    print prntGrp
    cmds.parent( prntGrp , hair_system)
    helpPanelGroup = 'helpPanel_grp'
    if not cmds.objExists(helpPanelGroup):
        cmds.group( em=1, w=1, n = 'helpPanel_grp' )
    
    name = jntList[0].split("_")[0]
    if cmds.attributeQuery( name + "_jntList", node = helpPanelGroup, exists=1)==False:
        cmds.addAttr( helpPanelGroup, ln = name + "_jntList", dt = "stringArray" )
    cmds.setAttr( helpPanelGroup + "." + name + "_jntList", type= "stringArray", *([len(jntList)] + jntList))
    

def dyn_hairSetup( jntList, ctlLen ):
    
    name = jntList[0].split("_")[0]    
    ikItems = cmds.ikHandle( sol = 'ikSplineSolver', simplifyCurve = 0, createCurve = 1  )
    ikCrv = ikItems[-1]
    newIkCrv = cmds.rename( ikCrv, name + "_ik_crv" )
    cmds.rebuildCurve( newIkCrv, rebuildType = 0, keepControlPoints=1, keepRange = 0 )    

    manCrv = cmds.duplicate( newIkCrv, rc = 1 )    
    newManCrv = cmds.rename( manCrv[0], name + "_man_crv" )
    #keepRange = 0 : reparameterize the resulting curve from 0 to 1    

    dupCrv = cmds.duplicate( newIkCrv, rc = 1 )
    dyn_crv = cmds.rename( dupCrv[0], name + "_init_crv" )
    cmds.select(dyn_crv)
    mel.eval('makeCurvesDynamicHairs %d %d %d' % (0,0,1))
    follicle = cmds.listConnections( dyn_crv, s=0, d=1 )
    follicleShp = cmds.listRelatives(follicle[0], c=1 )[0]
    cnnts = cmds.listConnections( follicleShp, s =0, d =1 )
    out_crv = cnnts[-1]
    newOut_crv = cmds.rename( out_crv, name + "_out_crv" )
    outCrvP = cmds.listRelatives( newOut_crv, p=1, typ = "transform")
    
    #blendShape man_crv/ dyn_out_crv to ikCrv
    dynBS = cmds.blendShape( newManCrv, newOut_crv, newIkCrv, n = name + "dyn_BS" )
    cmds.setAttr( dynBS[0] + '.%s'%newManCrv, 1 )
    cmds.setAttr( dynBS[0] + '.%s'%newOut_crv, 1 )
    
    #blendShape man_crv to dyn_initial_crv
    shpBS = cmds.blendShape( newManCrv, dyn_crv, n = name + "shapeBS" )
    cmds.setAttr( shpBS[0] + ".%s"%newManCrv, 1 )
    #cmds.setAttr( dyn_crv + ".inheritsTransform",  0 )
    
    hair_system = "hairSystem_grp"
    if not cmds.objExists(hair_system):
        cmds.group(em=1, n = "hairSystem_grp" )
        
    #organize ikHandle, dyn_out_crv to hair_system
    cmds.parent( ikItems[0], outCrvP, hair_system )
    
    ctlJnts = []
    increm = 1.0/( int(ctlLen)-1)
    for i in range( int(ctlLen) ):
        
        dnPOC = cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = name + 'POC'+ str(i+1).zfill(2))
        manCrvShape = cmds.listRelatives( newManCrv, c=1, s=1, ni =1 )[0] 
        cmds.connectAttr ( manCrvShape + ".worldSpace",  dnPOC + '.inputCurve')
        cmds.setAttr ( dnPOC + '.turnOnPercentage', 1 )
        cmds.setAttr ( dnPOC + '.parameter', increm *i )        	
        xyz = cmds.getAttr(dnPOC+".position" )
        
        jnt = cmds.joint( p=xyz[0], a=True, n= name + "_ctlJnt%s"%str(i+1).zfill(2) )        
        
        ctlItems = arcController( name + "_ctl%s"%str(i+1).zfill(2), xyz[0], .5, "cc" )
        cmds.parent( jnt, ctlItems[0] )
        
        #create hierachy by parenting ctrlP
        if i>0:
            cmds.parent( ctlItems[1], name + "_ctl%s"%str(i).zfill(2) )
        else:
            cmds.parent( follicle[0], ctlItems[1] )
            
        ctlJnts.append(jnt)
    
    
    cmds.addAttr( ctlItems[0], ln ="switch_dyn_man", attributeType='float'  )
    cmds.shadingNode( "reverse", asUtility =1, n = name + "_switch" )
    
    cmds.setAttr( follicleShp + ".overrideDynamics", 1 )
    cmds.setAttr( follicleShp + ".pointLock", 1 )
    cmds.setAttr( follicleShp + ".stiffness", 1 )

    cmds.skinCluster( ctlJnts, newManCrv ,tsb=True )
    
    



# select curve ( should be 0,0,0 in worldspace )
# check the script editor for cv, position 
def store_uParam( wireCrv, name ):
    
    wireCrvShp = cmds.listRelatives( wireCrv, c=1 )[0]
    if not cmds.getAttr( wireCrvShp + ".maxValue" )== 1:
        hist = cmds.listHistory( wireCrv, pdo=1, lv=1)
        if hist:
            cmds.rebuildCurve( wireCrv, ch =1, rpo =1, kr=0, kcp=1, kep=1, d=3 )
        else:
            cmds.rebuildCurve( wireCrv, ch =0, rpo =1, kr=0, kcp=1, kep=1, d=3 )
    
    cvs = cmds.ls( wireCrv + '.cv[*]', fl=1 )
    
    uParam = [] 
    for cv in cvs:
        position = cmds.xform( cv, q=1, ws=1, t=1 )
        cmds.spaceLocator( p = position, n = "shit" )
        param = getUParam( position, wireCrv )
        print param
        uParam.append(param)
    
    if cmds.attributeQuery("uParam", node = wireCrv, exists=1)==False:
        cmds.addAttr( wireCrv, ln ="uParam", dt = "stringArray"  )

    cmds.setAttr( wireCrv + ".uParam", type= "stringArray", *([len(uParam)] + uParam))





#select source curve and destintion curve in order
#create wire curve with dnCrv shape and scCrv uParam
# scCrv should have uParam attribute
def dnCrv_srcUParam( scCrv, dnCrv, name):

    dnShp = cmds.listRelatives( dnCrv, c=1, ni =1, s=1 )[0]
    scShp = cmds.listRelatives( scCrv, c=1, ni =1, s=1 )[0]
    if dnShp == scShp:
        cmds.confirmDialog( title='Confirm', message='source and destination curve have same shape name!' )
        
    else:
        uParams = cmds.getAttr( scCrv +'.uParam' )
        numCvs = len(uParams)
        
        dnCrvShp = cmds.listRelatives( dnCrv, c=1 )[0]
        if not cmds.getAttr( dnCrvShp + ".maxValue" )== 1:
            
            hist = cmds.listHistory( dnCrv, pdo=1, lv=1 )
            if hist:
                cmds.rebuildCurve( dnCrv, ch =1, rpo =1, kr=0, kcp=1, kep=1, d=3 )
            else:
                cmds.rebuildCurve( dnCrv, ch =0, rpo =1, kr=0, kcp=1, kep=1, d=3 )
            
        cvPos = []
        for i, prm in enumerate(uParams):

            poc =cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = 'steady'+ str(i+1).zfill(2) )
            cmds.connectAttr( dnShp + ".worldSpace" , poc + ".inputCurve" )
            cmds.setAttr( poc+".parameter", float(prm) )
            pos = cmds.getAttr(poc + ".position")[0]
            
            cvPos.append(pos)    
            
        crvForm = cmds.getAttr( dnShp + '.form' )
        if crvForm == 0: # if crv form is open
            
            openCrv = cmds.curve( d=3, p=cvPos )
            newCrv = cmds.rename( openCrv,  name + "_wireCrv01" )
            
        else:  # if crv form is close or periodic

            closedOrderPos = cvPos + cvPos[:3]
                                               
            numPoint = len(closedOrderPos)
            knots = []
            for i in range(numPoint+2):
                knots.append(i)

            closeCrv = cmds.curve( d=3, per=1, p=closedOrderPos, k = knots )    
            newCrv = cmds.rename( closeCrv,  name + "_wireCrv01" )

            #ep curve is not working because the point position is based on cv's 
            '''epPos = cvPos[1:] + [cvPos[0]]
            closedOrderPos = epPos + [epPos[0]]

            newCrv = OpenMaya.MObject()
            coords = closedOrderPos
            curveFn = OpenMaya.MFnNurbsCurve() 
            arr = OpenMaya.MPointArray()
            for pos in coords: 
                arr.append(*pos)            

            curveFn.createWithEditPoints( 
                                          arr, 
                                          3, 
                                          OpenMaya.MFnNurbsCurve.kPeriodic, 
                                          False, 
                                          False, 
                                          True 
                                        )'''                                                                   
        
        cmds.rebuildCurve( newCrv, ch =0, rpo =1, kr=0, kcp=1, kep=1, d=3 )[0]
        cmds.xform( newCrv, cp=1 )
        return newCrv
    
                    


        
#multi source transform( translate, rotete, scale ) drive the driven node( joint, cls, transform... )
#ctrl name important ( l_name_ctl/jnt/cls/... )
#multiply node, plusMinus node ?? ( ?? ???? attribute ?? : { jawOpen_ctl:[tx, ty, tz], jawSwivel_ctl:[tx, ty, tz] }, drivenNode:[rz, rx, ry] )
def multiInputConnect( tform ):
    
    mySel=cmds.ls(sl=1 )
    source = mySel[:-1]
    target = mySel[-1]
    nameTemp = source[0].split("_")
    if nameTemp[0] in ["l","r","L","R","c","C"]:
        name =nameTemp[0]+ "_" + nameTemp[1]
        
    else:
        name = nameTemp[0]       
    
    print source, target
    if tform == "translate":
        plus= cmds.shadingNode( "plusMinusAverage", asUtility=1, n = name+"Tran_plus" )    
        for i, src in enumerate(source):
            tranMult = cmds.shadingNode( "multiplyDivide", asUtility=1, n = name+"Tran_mult"+str(i+1) )
            cmds.connectAttr( src + ".t" , tranMult + ".input1" )
            cmds.connectAttr( tranMult + ".output", plus + ".input3D[%s]"%str(i) )
         
                   
    elif tform == "rotate":
        plus= cmds.shadingNode( "plusMinusAverage", asUtility=1, n = name +"Rot_plus" )
        for i, src in enumerate(source):
            rotMult = cmds.shadingNode( "multiplyDivide", asUtility=1, n = name+"Rot_mult"+str(i+1) )
            cmds.connectAttr( src + ".r" , rotMult + ".input1" )
            cmds.connectAttr( rotMult + ".output", plus + ".input3D[%s]"%str(i))
                 
    elif tform == "scale":
        plus= cmds.shadingNode( "plusMinusAverage", asUtility=1, n = name +"Scal_plus" )
        leng =len(source) 
        for i, src in enumerate(source):                       
            cmds.connectAttr( src + ".s" , plus + ".input3D[%s]"%str(i) )
                     
    #connect to the target tform
    if tform == "translate":
        cmds.connectAttr( plus + ".output3D", target+".t" )  
    elif tform == "rotate":
        cmds.connectAttr( plus + ".output3D", target+".r" )  
    elif tform == "scale":
        scleMult = cmds.shadingNode( "multiplyDivide", asUtility=1, n = name+"Scal_mult" )
        cmds.setAttr( plus + ".input3D[%s]"%str(leng), -(leng-1),-(leng-1),-(leng-1) )
        cmds.connectAttr( plus + ".output3D",  scleMult + ".input1" )
        cmds.connectAttr( scleMult + ".output", target+".s" )


        
#replace the transform connection
#select the source and destination transform node
def replaceConnection():
    tformNode=cmds.ls( os=1, type="transform" )
    if tformNode[0][:2] in ["l_","r_"] and tformNode[1][:2] in ["l_","r_"]:
        scName = tformNode[0][2:]
        tgName = tformNode[1][2:]
        for lr in ["l_","r_"]:
            scCnnt = cmds.listConnections( lr + scName, s=1, d=0, p=1, c=1 )
            if scCnnt:
                print scCnnt
                for dn, sc in zip(*[iter(scCnnt)]*2):
                    attr = dn.split(".")[1]
                    cmds.disconnectAttr( sc, dn )
                    cmds.connectAttr( sc, lr + tgName +"."+ attr, f=1 )     
            
            dnCnnt = cmds.listConnections( lr + scName, s=0, d=1, p=1, c=1)
            if dnCnnt:
                print dnCnnt
                for s, d in zip(*[iter(dnCnnt)]*2):
                    scAttr = s.split(".")[1]
                    cmds.disconnectAttr( s, d )
                    cmds.connectAttr( lr + tgName + "." + scAttr, d, f=1 )
                 
    else:    
        scCnnt = cmds.listConnections( tformNode[0], s=1, d=0, p=1, c=1 )
        if scCnnt:
            print scCnnt
            for dn, sc in zip(*[iter(scCnnt)]*2):
                attr = dn.split(".")[1]
                cmds.disconnectAttr( sc, dn )
                cmds.connectAttr( sc, tformNode[1] + '.'+ attr, f=1 )
            
        dnCnnt = cmds.listConnections( tformNode[0], s=0, d=1, p=1, c=1)
        if dnCnnt:
            print dnCnnt
            for s, d in zip(*[iter(dnCnnt)]*2):
                scAttr = s.split(".")[1]
                cmds.disconnectAttr( s, d )
                cmds.connectAttr( tformNode[1] +'.'+ scAttr, d, f=1 )   
 
 
        
            
        
        
        
def jaw_UDLRFix():
    #TyLipCorner_mult
    cmds.connectAttr( "cntLoTyLip_jnt.translateZ", "TyLipCorner_mult.input1X", f=1  )
    #fix corner_jnt ty / cntUp_jnt ty --> cntLo_jnt ty* 0.5 / cntLo_jnt ty* 0.03

    #cntUp_jnt ty = cntLo_jnt ty* 0.03
    cmds.connectAttr( "cntLoTyLip_jnt.translateY", "TyLipdamp_mult.input1X", f=1  )
    cmds.setAttr( "TyLipdamp_mult.input2X", 0.03 )
    cmds.connectAttr( "TyLipdamp_mult.outputX", "cntUpTyLip_jnt.translateY" )

    #corner_jnt ty = cntLo_jnt ty* 0.5 
    cmds.connectAttr( "cntLoTyLip_jnt.translateY", "TyLipdamp_mult.input1Y" )
    cmds.setAttr( "TyLipdamp_mult.input2Y", 0.5 )
    cmds.connectAttr( "TyLipdamp_mult.outputY", "l_CornerTyLip_jnt.translateY" )
    cmds.connectAttr( "TyLipdamp_mult.outputY", "r_CornerTyLip_jnt.translateY" )

    #cntUp_jnt tz = cntLo_jnt tz* 0.03 ( )
    cmds.connectAttr( "cntLoTyLip_jnt.translateZ", "TyLipdamp_mult.input1Z", f=1  )
    cmds.setAttr( "TyLipdamp_mult.input2Z", 0.02 )
    cmds.connectAttr( "TyLipdamp_mult.outputZ", "cntUpTyLip_jnt.translateZ", f=1  ) 




#assign shading to Alembic cache (hodong, annette ) 
def getSGfromShader(shader=None):
    if shader:
        if cmds.objExists(shader):
            sgq = cmds.listConnections(shader, d=True, et=True, t='shadingEngine')
            if sgq: 
                return sgq[0]

    return None


def assignObjectListToShader(objList=None, shader=None):
    '''
    Assign the shader to the object list
    arguments:
        objList: list of objects or faces
    '''
    # assign selection to the shader
    shaderSG = getSGfromShader(shader)
    if objList:
        if shaderSG:
            cmds.sets(objList, e=True, forceElement=shaderSG)
        else:
            print 'The provided shader didn\'t returned a shaderSG'
    else:
        print 'Please select one or more objects'


def assignSelectionToShader(shader=None):
    sel = cmds.ls(sl=True, l=True)
    if sel:
        assignObjectListToShader(sel, shader)


def storeShadingSets():
           
    shadingObj = {}
    #get shadingGroups  
    shadingGrp = cmds.listConnections("renderPartition", s=1, d=0 )
    
    for shdGrp in shadingGrp:#shdGrp == shadingGroup
        if "SG" in shdGrp:
        
            shdr = cmds.listConnections( shdGrp + ".surfaceShader", s=1, d=0 )
    
            if shdr:
                cmds.select( shdr[0] )
                cmds.hyperShade(objects="")
                obj = cmds.ls(sl=1)
                shadingObj[shdr[0]] = obj
                
    for shdr, obj in shadingObj.items():
        print shdr, obj
        if not cmds.objExists("shadingHelp_grp"):
            shadingHelpGrp = cmds.group(em=1, n = "shadingHelp_grp" )
        else:
            shadingHelpGrp = "shadingHelp_grp"
            
        if cmds.attributeQuery( shdr, node = shadingHelpGrp, exists=1)==False:
            cmds.addAttr( "shadingHelp_grp", ln = shdr, dt = "stringArray"  )
            cmds.setAttr("shadingHelp_grp." + shdr, type= "stringArray", *([len(obj)] + obj) )

            
def assignShadingSets( shadingHelpGrp ):
    
    #shadingHelpGrp has dict attribute { shader: [objs] }
    shdrs = cmds.listAttr( shadingHelpGrp, ud =1  )
    for shd in shdrs:
        if cmds.objExists(shd):
            objs = cmds.getAttr( shadingHelpGrp + "." + shd )
            for oj in objs:
                if cmds.objExists(oj):
                    cmds.select( oj )
                    assignSelectionToShader( shd )



            

            
#import cache / select arnoldLights and run
def finalizeRenderSetting():
    #turn off opaque option
    opaque= cmds.ls("*Body*", "ribbonMesh*", "*tearMain", l=1, ni=1, type="mesh")
    if opaque:
        for bd in opaque:
            cmds.setAttr( bd +".aiOpaque", 0 )
    else:
        cmds.warning("Turn off opaque option manually")
    
    #head geo smooth render
    head = cmds.ls("head*", l=1, ni=1, type="mesh")
    if head:
        for hd in head:
            cmds.setAttr( hd+".aiSubdivType", 1 )
            cmds.setAttr( hd+".aiSubdivIterations", 1 )
    else:
        cmds.warning("smooth head display manually!")
            
    myLight= cmds.ls("*LightShape*" )
    for light in myLight:        
        if cmds.nodeType(light)=="aiAreaLight":
            cmds.setAttr(light+".aiSamples", 4 )
            cmds.setAttr(light+".aiResolution", 1024 )
            cmds.setAttr(light+ ".aiNormalize", 0 )
            cmds.setAttr(light+".aiCastVolumetricShadows", 0 )
            cmds.setAttr(light+".aiVolumeSamples", 0 )        
        
        elif cmds.nodeType(light)=="aiSkyDomeLight":

            cmds.setAttr(light+ ".aiNormalize", 1 )
            cmds.setAttr(light+".aiSamples", 4 )
            cmds.setAttr(light+".aiCastVolumetricShadows", 0 )
            cmds.setAttr(light+".aiVolumeSamples", 0 )    
            cmds.setAttr(light+ ".camera", 0)
            
        elif cmds.nodeType(light) in ["spotLight", "pointLight" ]:

            cmds.setAttr(light+ ".aiRadius", 1 )
            cmds.setAttr(light+".aiSamples", 4 )

                    
    cmds.setAttr( "defaultArnoldRenderOptions.GIDiffuseSamples", 5)
    cmds.setAttr( "defaultArnoldRenderOptions.GISpecularSamples", 5)
    cmds.setAttr( "defaultArnoldRenderOptions.GITransmissionSamples", 5)
    cmds.setAttr( "defaultArnoldRenderOptions.GISssSamples", 3)

    from twitchScript import faceSkinFunction
    reload(faceSkinFunction)
    faceSkinFunction.deleteUnknown_plugins()
    

    
#instance objects falling    
def selectedObjectFalling( ):
    selObj = cmds.ls( sl=1, type = "transform" )
    ptcl=cmds.ls( type="nParticle")
    cnnPtcl = cmds.listConnections( ptcl, s=1, d=1 )
    cnnt=list(set(cnnPtcl))
    if cnnt:
        inst = [ i for i in cnnt if cmds.nodeType( i ) == "instancer" ]
        print inst
        for ct in cnnt:
            #set 20 falling from Surface
            if "Emitter" in cmds.nodeType( ct ):
                cmds.setAttr( ct+".emitterType", 2)
                cmds.setAttr( ct+".rate", 20 )
                cmds.setAttr( ct+ ".speed", 40 )
                cmds.setAttr( ct + ".speedRandom", 0.1 )
                
            elif cmds.nodeType( ct ) == "nucleus":
                #falling earlier
                cmds.setAttr( ct+".gravity", 2 )
                cmds.setAttr( ct+".maxCollisionIterations", 6 )
                
            elif cmds.nodeType( ct ) == "nParticle":
                #scale random
                cmds.setAttr( ct + ".radiusScaleInput", 1 )
                cmds.setAttr( ct + ".radiusScaleRandomize", 0.1 )
                
                #collision setup
                cmds.setAttr( ct + ".collide", 1 )
                cmds.setAttr( ct + ".selfCollide", 1 )
                cmds.setAttr( ct + ".collideWidthScale", 6 )
                cmds.setAttr( ct + ".selfCollideWidthScale", 2 )
                cmds.setAttr( ct + ".bounce", 0.05 )
                cmds.setAttr( ct + ".friction", 0.1 )
                cmds.setAttr( ct + ".maxSelfCollisionIterations", 8 )
                
                if inst:
                    #rotation setup            
                    cmds.setAttr( ct + ".rotationFriction", 0.9 )
                    cmds.setAttr( ct + ".rotationDamp", 0.2 )
                    cmds.expression( ct, c=1, s='%s.rotationPP=rand(360)'%(ct) )
                    cmds.particleInstancer( ct, e=1, name= inst, rotation= "rotationPP" )   
    
