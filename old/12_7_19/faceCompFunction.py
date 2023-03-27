# -*- coding: utf-8 -*-
import maya.cmds as cmds
import maya.mel as mel
from maya import OpenMaya
import re
'''
1. store head info ( head name / brow, eye, lip vertices in order )
a. Brow: manually select brow vertices(left side to mirror ) : stored in browFactor
b. Eye or Lip : 먼저 코너 버텍스들를 선택하고 저장한 후, right corner vert 와 direction vert만 선택해서 실행하면 자연히 lCornerVert,rCornerVert,secndVert가 실수 없이 나온다.( to be stored in lid/lipfactor)   

Aug20 swtichJntToCls / curveOnEdgeLoop fix( checking with stored verts not joints ) / eyeMapSkinning fix ( loLidJnts instead loLidJnts[1:-1]) 
'''
def markVertex( *pArgs ):
    vtxSel = cmds.ls(sl=1, fl=1)
    cmds.polyColorPerVertex(vtxSel, r=1, g=0.3, b=0.3, a=1, cdo=1 )

def removeVertMark():
    myGeo = cmds.ls( sl=1, type = 'transform' )
    history = cmds.listHistory( myGeo[0] )    
    
    for nd in history:
        if cmds.nodeType(nd) == 'polyColorPerVertex':
            print nd
            cmds.delete( nd )            
        else:
            cmds.polyColorPerVertex( myGeo[0], rem=True )

#store head info            
def headGeo():
    faceGeo = cmds.ls(sl=1, type = "transform")[0]
    if cmds.attributeQuery("headGeo", node = "helpPanel_grp", exists=1)==False:
        cmds.addAttr( "helpPanel_grp", ln ="headGeo", dt = "string"  )
    cmds.setAttr("helpPanel_grp.headGeo", faceGeo, type= "string"  ) 

    
#store brow vertices in browFactor( selection order: center to left !! )
def browVerts():
	myVerts = cmds.ls(os=1, fl=1)
	vts = cmds.filterExpand( ex=True, sm=31 )
	vtxNum = len(vts)

	myList = {}
	for i in vts:        
		xyz = cmds.xform ( i, q=1, ws=1, t=1 )
		myList[ i ] = xyz[0]
	ordered = sorted(myList, key = myList.__getitem__)    

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
        
        

# select any 2 adjacent vertex on loop and shaped curve
# get the closest point on curve for each vertex using getUParam
def shapeToCurveX():
    
    mySel = cmds.ls(os=1, fl=1 )
    targetCrv = mySel[-1] 
    sourceVtx = mySel[:-1] 
    cmds.makeIdentity(targetCrv, apply=True, t=1, r=1, s=1, n=0, pn=1)    
    cmds.select( sourceVtx[0],sourceVtx[1])
    orderVtx = orderedVerts_edgeLoop()
    dnNum = len(orderVtx)
    increm = 1.0/dnNum
    
    for i, vtx in enumerate( orderVtx ):
        dnPOC = cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = 'dnPOC'+ str(i+1).zfill(2))
        loc = cmds.spaceLocator ( n = "targetPoc"+ str(i+1).zfill(2))
        cmds.connectAttr (targetCrv + ".worldSpace",  dnPOC + '.inputCurve')
        cmds.setAttr ( dnPOC + '.turnOnPercentage', 1 )
        cmds.setAttr ( dnPOC + '.parameter', increm *i )	    
    
        #cmds.connectAttr( dnPOC + ".position" , loc[0] + ".t")
        pos = cmds.getAttr(dnPOC + ".position" )
        
        cmds.xform( vtx, ws=1, t= pos[0] )


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
        pos = cmds.xform( vtx, q=1, ws=1, t=1) 
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
		
		crv = cmds.curve( n= name + 'loftCurve01', d =1, p = vertsPos )
		cmds.closeCurve( crv, ch=0, ps=True, replaceOriginal=1 )
		cmds.toggle( crv, cv=True )
	else:
		print 'Wrong edgeLoop vertices are selected'

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
            cmds.setAttr("helpPanel_grp.selected_eyeEdges", type= "stringArray", *([len(edges)] + edges) )
    
        elif eyeLip == 'lip':
            cmds.setAttr("helpPanel_grp.selected_lipEdges", type= "stringArray", *([len(edges)] + edges) )
    
    else:
        if numOfJnt-len(edges)>0:
            print "select %s more %s edges!!"%(str(numOfJnt-len(edges)), eyeLip)
        elif numOfJnt-len(edges)<0:
            print "select %s less %s edges!!"%(str(numOfJnt-len(edges)), eyeLip)
        
        


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
            




#select a lip curve for symmetry / delete the history       
#modeling the curve00(outer curve) on left CVs
#select the curve00 and run the script to symmetrize
def symmetrizeLipCrv(direction):

    crvSel = cmds.ls(sl=1, type = "transform")
    cvs = cmds.ls(crvSel[0]+".cv[*]", fl=1 )
    numCv = len(cvs)
    centerCV =[]
    for cv in cvs:
        pos = cmds.xform( cv, q=1, ws=1, t=1 )
        if pos[0]**2 < 0.001 :
            centerCV.append(cv)
            
    print centerCV
    centerNum = int(centerCV[0].split("[")[1][:-1])  
    halfNum = numCv/2
    leftCv = cvs[centerNum:centerNum+halfNum]
    rightCv = cvs[::-1][numCv-centerNum:] + cvs[::-1][:numCv-centerNum-halfNum:]
        
    if direction == 1:
        print "left cv to right cv"
        for i, cv in enumerate(leftCv[1:]):
            pos = cmds.xform( cv, q=1, ws=1, t=1 )
            cmds.xform( rightCv[i], ws=1, t=( -pos[0], pos[1], pos[2] ) )
        
    else:
        print "right cv to left cv"
        for i, cv in enumerate(rightCv[:-1]):
            pos = cmds.xform( cv, q=1, ws=1, t=1 )
            cmds.xform( leftCv[i], ws=1, t=( -pos[0], pos[1], pos[2] ) )


 
       
   
    
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
def browJoints():
    browRotXPos = cmds.xform( 'rotXPivot', t = True, q = True, ws = True )
    browRotYPos = cmds.xform( 'rotYPivot', t = True, q = True, ws = True )
        
    #reorder the vertices in selection list  
    orderedVerts = cmds.getAttr("browFactor.browVerts")
    myList = {}
    for i in orderedVerts:        
        xyz = cmds.xform ( i, q=1, ws=1, t=1)
        myList[ i ] = xyz[0]
    ordered = sorted(myList, key = myList.__getitem__)
    
    #double check the selection order
    id = 0 
    while id<len(ordered) and not orderedVerts[id] == ordered[id]:
        
        print "double check the brow selection order " 
        id+=1

    else:
        print "good selection in order"

    if not cmds.objExists("eyebrowJnt_grp"):
        cmds.group( em=True, name='eyebrowJnt_grp', p= "faceMain|jnt_grp" )
    
    cmds.select(cl = True )
    index = 1
    for x in orderedVerts:
        vertPos = cmds.xform(x, t = True, q = True, ws = True)
        
        if ( vertPos[0] <= 0.05):
            
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
        

             
def connectBrowCtrls ( numOfCtl, size, offset, browCtl ):
       
    jnts = cmds.ls ( '*browBase*_jnt', fl = True, type ='joint') 
    jntNum = len(jnts)
    jnts.sort()
    z = [ jnts[0] ] #center joints
    y = jnts[1:jntNum/2+1] #left joints
    jnts.reverse()
    x = jnts[:jntNum/2] #right joints
    orderJnts = x + z + y

    #revese 'faceFactors.browRotateX_scale' 
    reverseMult = cmds.shadingNode ( 'multiplyDivide', asUtility=True, n = 'browReverse_mult' )
    cmds.connectAttr( 'browFactor.browUp_scale', reverseMult + ".input1X")
    cmds.connectAttr( 'browFactor.browUp_scale', reverseMult + ".input1Z")
    cmds.connectAttr ( 'browFactor.browRotateY_scale', reverseMult + '.input1Y' )
    cmds.setAttr( reverseMult + ".input2", -1,-1,-1 )
   
    if cmds.objExists("browCrv_grp"):
        cmds.delete("browCrv_grp")        
    if not cmds.objExists("attachCtl_grp"):
        attachCtlGrp = cmds.group ( n = "attachCtl_grp", em =True, p = "faceMain|spn|headSkel|bodyHeadTRSP|bodyHeadTRS|" ) 
    if cmds.objExists("browDtailCtl_grp"):
        cmds.delete("browDtailCtl_grp")
        
    browCtlGrp = cmds.group ( n = "browDtailCtl_grp", em =True, p = "faceMain|spn|headSkel|bodyHeadTRSP|bodyHeadTRS|attachCtl_grp|browCtl_grp" )    
    browCrvGrp = cmds.group ( n = "browCrv_grp", em =True, p = "faceMain|crv_grp" ) 
    tempBrowCrv = cmds.curve ( d = 1, p =([-1,0,0],[-0.5,0,0],[0,0,0],[0.5,0,0],[1,0,0]) ) 
    cmds.rebuildCurve ( tempBrowCrv, rebuildType = 0, spans = 10, keepRange = 0, degree = 3 )    
    browCrv = cmds.rename (tempBrowCrv, 'brow_crv')    
    browCrvShape = cmds.listRelatives ( browCrv, c = True )
    cmds.parent ( browCrv, "browCrv_grp")     

    # lipTarget curve shape
    lBrowSadCrv = cmds.duplicate ( browCrv, n= 'lBrowSad_crv')
    rBrowSadCrv = cmds.duplicate ( browCrv, n= 'rBrowSad_crv')
    lBrowMadCrv = cmds.duplicate ( browCrv, n= 'lBrowMad_crv')
    rBrowMadCrv = cmds.duplicate ( browCrv, n= 'rBrowMad_crv')
    lFurrowCrv = cmds.duplicate ( browCrv, n= 'lFurrow_crv')
    rFurrowCrv = cmds.duplicate ( browCrv, n= 'rFurrow_crv')
    lRelaxCrv = cmds.duplicate ( browCrv, n= 'lRelax_crv')
    rRelaxCrv = cmds.duplicate ( browCrv, n= 'rRelax_crv')      
    lCrv = [lBrowSadCrv[0], lBrowMadCrv[0], lFurrowCrv[0], lRelaxCrv[0] ]    
    rCrv = [rBrowSadCrv[0], rBrowMadCrv[0], rFurrowCrv[0], rRelaxCrv[0] ]        
    crvLen = len(lCrv)
    
    browBS = cmds.blendShape ( lBrowSadCrv[0],rBrowSadCrv[0], lBrowMadCrv[0],rBrowMadCrv[0], lFurrowCrv[0],rFurrowCrv[0], lRelaxCrv[0],rRelaxCrv[0], browCrv, n ='browBS')
    cmds.blendShape( browBS[0], edit=True, w=[(0, 1), (1, 1), (2, 1), (3,1),(4, 1), (5,1),(6, 1), (7,1) ])  
    LRBlendShapeWeight( browCrv, browBS[0] )
    
    tempCtlCrv = cmds.curve ( d = 2, p =([-1,0,0],[-0.5,0,0],[0,0,0],[0.5,0,0],[1,0,0]) )
    browCtlCrv = cmds.rename (tempCtlCrv, 'browCtrlCrv' ) 
    cmds.rebuildCurve (browCtlCrv, rebuildType = 0, spans = numOfCtl-1, keepRange = 0, degree = 3 ) 
    browCtlCrvShape = cmds.listRelatives ( browCtlCrv, c = True ) 
    cmds.parent ( browCtlCrv, "browCrv_grp") 
    
    #connect browMain Ctrls to browCrv   
    sequence =['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I' ]
    cvs= cmds.ls("browCtrlCrv.cv[*]", fl=True )    
    centerCtl = (numOfCtl-1)/2
    
    for num in range (1, len(cvs)-1 ):            
        #erase double transform
        if num == centerCtl+1:
       
            cmds.connectAttr ('brow_arc' + sequence[num-1] + '.ty', cvs[num] + '.yValue' )            
            cmds.connectAttr ('brow_arc' + sequence[num-1] + '.tz',  cvs[num] + '.zValue' )        
        else:
            #erase cv's tx value
            sumX = cmds.shadingNode ( 'addDoubleLinear', asUtility =True, n = 'browTX_sum'+ str(num) )
            cvXVal = cmds.getAttr( cvs[num] + '.xValue' )
            cmds.connectAttr ( 'brow_arc%s.tx'%(sequence[num-1]), sumX + '.input1' )
            cmds.setAttr ( sumX + '.input2', cvXVal )
            cmds.connectAttr ( sumX + '.output', cvs[num] + '.xValue' )       
            
            cmds.connectAttr ('brow_arc' + sequence[num-1] + '.ty', cvs[num] + '.yValue' )                           

            cmds.connectAttr ('brow_arc' + sequence[num-1] + '.tz', cvs[num] + '.zValue' )
                   
    increment = 1.0/(jntNum-1)
    index = 0 
    for jnt in orderJnts:
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

            if browCtl:
                rBrowCtrl = customCtl( browCtl , tzJnt.replace("_jnt", "_ctl"), ( jntPos[0], jntPos[1], jntPos[2]+ offset) )
            else:
                rBrowCtrl = controller( tzJnt.replace("_jnt", "_ctl"), ( jntPos[0], jntPos[1], jntPos[2]+ offset), size, 'sq' )
            ctlP = rBrowCtrl[1]
            cmds.setAttr (rBrowCtrl[0] + ".overrideColor", 3 )
            zeroGrp = cmds.duplicate(ctlP, po =1, n = ctlP.replace("_ctlP","_dummy") )
            #up/down reverse for mirror joint
            cmds.setAttr( browJntList[1]+".rx", 180)
            
            cmds.parent(ctlP, zeroGrp[0] )
            rotYGrp = cmds.group( em =1, n = rBrowCtrl[0].replace("_brow","_browRY"), p = "browCtl_grp")
            cmds.xform (rotYGrp, ws = True, t = rotYJntPos ) 
            cmds.parent(zeroGrp[0], rotYGrp) 
            ctlBase = cmds.group( em =1, n = ctlP.replace("_ctlP","_base"), p = browCtlGrp ) 
            cmds.xform (ctlBase, ws = True, t = basePos )            
            cmds.parent(rotYGrp, ctlBase)
            for att in attrs:            
                cmds.setAttr ( rBrowCtrl[0] + ".%s"%att, lock =1, keyable = 0)
                        
            browCrvCtlToJnt( rBrowCtrl[0], jnt, browJntList, ctlBase, rotYGrp, shapePOC, POC, index )
        
        elif jnt in y : #left joints
        
            #detail ctrl on Face
            if cmds.objExists(browCtl):
                lBrowCtrl = customCtl( browCtl, tzJnt.replace("_jnt", "_ctl"), ( jntPos[0], jntPos[1], jntPos[2]+ offset) )
            else:
                lBrowCtrl = controller( tzJnt.replace("_jnt", "_ctl"), ( jntPos[0], jntPos[1], jntPos[2]+ offset), size, 'sq' ) 
            ctlP = lBrowCtrl[1]
            cmds.setAttr (lBrowCtrl[0] + ".overrideColor", 3 )
            zeroGrp = cmds.duplicate(ctlP, po =1, n = ctlP.replace("_ctlP","_dummy") )
            cmds.parent( ctlP, zeroGrp[0] )
            rotYGrp = cmds.group( em =1, n = lBrowCtrl[0].replace("_brow","_browRY"), p = "browCtl_grp")
            cmds.xform (rotYGrp, ws = True, t = rotYJntPos )
            cmds.parent(zeroGrp[0], rotYGrp)
            ctlBase = cmds.group( em =1, n = ctlP.replace("_ctlP","_base"), p = browCtlGrp ) 
            cmds.xform (ctlBase, ws = True, t = basePos )
            cmds.parent(rotYGrp, ctlBase)
            for att in attrs:            
                cmds.setAttr ( lBrowCtrl[0] + ".%s"%att, lock =1, keyable = 0)
            
            browCrvCtlToJnt (lBrowCtrl[0], jnt, browJntList, ctlBase, rotYGrp, shapePOC, POC, index  )
            
        elif jnt == z[0]:
        
            #detail ctrl on Face
            if cmds.objExists(browCtl):
                centerBrowCtrl = customCtl( browCtl, 'c_brow_ctl', ( jntPos[0], jntPos[1], jntPos[2]+ offset) )
            else:
                centerBrowCtrl = controller( 'c_brow_ctl', ( jntPos[0], jntPos[1], jntPos[2]+ offset), size, 'sq' )
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
                cmds.setAttr ( centerBrowCtrl[0] + ".%s"%att, lock =1, keyable = 0 )
                
            browCrvCtlToJnt ( centerBrowCtrl[0], jnt, browJntList, ctlBase, rotYGrp, shapePOC, POC, index )
            
        index = index + 1

#connectBrowCtrls ( .2, .2 )



def browCrvCtlToJnt( browCtrl, jnt, browJntList, ctlBase, rotYCtl, shapePOC, POC, index):
    """
    lots of utility nodes
    """
    #connect browCtrlCurve and controller to the brow joints
    ctrlMult = cmds.shadingNode('multiplyDivide', asUtility=True, n = jnt.split('Base', 1)[0] +'ctrlMult'+ str(index) )
    jntMult = cmds.shadingNode('multiplyDivide', asUtility=True, n = jnt.split('Base', 1)[0] +'JntMult'+ str(index) )
    browXYZSum = cmds.shadingNode('plusMinusAverage', asUtility=True, n = jnt.split('Base', 1)[0] +'BrowXYZSum'+ str(index))
     
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
    cmds.connectAttr(browXYZSum + '.output3Dz', browPCtl[0]+'.tz' )
  
    #browCtrl --> browJnt[0] + ".translate"
    cmds.connectAttr(browXYZSum + '.output3Dz', browDwnJnt + '.tz' )
    
   #extra rotate ctrl for browJnt[0]
    cmds.connectAttr(browCtrl + '.t', browJnt + '.t')   
    cmds.connectAttr(browCtrl + '.r', browJnt + '.r')
    cmds.connectAttr(browCtrl + '.s', browJnt + '.s') 

 



def browCtl_onHead( numOfCtl, offset ):

    #select polyEdgeToCurve
    sel = cmds.ls(sl=1 )
    nCrv = cmds.listRelatives( sel[0], c=1)
    if cmds.nodeType(nCrv)=="nurbsCurve":		    
        crv = sel[0]		    
        crvShape = cmds.listRelatives( crv, c=1, ni = 1)[0]
        numVtx = len(cmds.ls( crvShape + ".cv[*]", fl=1 ) )
        print numVtx
        cvStart = cmds.xform(crvShape + ".cv[0]", q=1, ws=1, t=1 )
        cvEnd = cmds.xform( crvShape + ".cv[%s]"%str(numVtx-1), q=1, ws=1, t=1 )

        if cvStart[0] > cvEnd[0]:
            cmds.reverseCurve( crv, ch= 1, rpo=1 )   

        #create group node for brow Ctls    
        if not cmds.objExists( "browCtl_grp" ):
            browCtlGrp = cmds.group ( n = "browCtl_grp", em =True )
        else:
            browCtlGrp = "browCtl_grp"

        cmds.parent( browCtlGrp, "attachCtl_grp" )
        
        pocs = pocEvenOnCrv( crv, numOfCtl, "brow_arc" )#create brow_arc01_poc, brow_arc02_poc...
        sequence =['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I' ]
        colorNum = [ 2, 2, 12, 12,  2,  6, 6, 2,  2 ] #( grey, greyRed, darkRed, red, grey, blue, darkBlue, greyBlue, grey )
        if numOfCtl == 5:
            colorNum = colorNum[2:-2]
        elif numOfCtl == 7: 
            colorNum = colorNum[1:-1]  
        
        nulls =[]
        for x, p in enumerate(pocs):
            print x, p
            pos = cmds.getAttr( p +".position")[0]
            null = cmds.group( em=1, n = "brow_arc" +sequence[x]+"_null" ) #create brow_arcA_null,brow_arcB_null..
            cmds.connectAttr( p +".position", null +".t" )
            ctl = controller( null.replace( sequence[x]+"_null", sequence[x] ), pos, 0.5, "cc" )
            cmds.setAttr (ctl[0] +"Shape.overrideEnabled", 1)
            cmds.setAttr( ctl[0]+"Shape.overrideColor", colorNum[x])               
            #parent controller to null 
            cmds.parent(ctl[1], null )
            #controller offset
            cmds.setAttr( ctl[1] + ".tz", offset*2 )
            cmds.parent( null, browCtlGrp ) 

    else:
        cmds.confirmDialog( title='Confirm', message='Select "polyEdgeCurve for brow Ctrls"!!' )

        
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
def browDetailCtls():        
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
    cDetailCtl = controller( 'c_browDetail01' , ( 0, 0, 0), .2, 'cc' )
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
        rDetailCtl = controller( 'r_browDetail' + str(index+1).zfill(2) , ( 0, 0, 0), .25, 'sq' )
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
        lDetailCtl = controller( 'l_browDetail' + str(index+1).zfill(2) , ( 0, 0, 0), .2, 'cc' )
        cmds.setAttr (lDetailCtl[0] + ".overrideColor", ctlColor[index] )
        cmds.parent (lDetailCtl[0], lPlane[0], relative=True )
        cmds.parent (lPlane[0], ctlP, relative=True )
        #get rid of parent(null) node
        cmds.delete( lDetailCtl[1])
        cmds.setAttr (lPlane[0] + '.tx', increment*(index+1)*2 )
        cmds.xform ( lDetailCtl[0], r =True, s = (0.2, 0.2, 0.2))  
        for att in attTemp:
            cmds.setAttr (lDetailCtl[0] +"."+ att, lock = True, keyable = False, channelBox =False)
                
        

# create upVector from EyeLoc

def eyelidJoints ( upLowLR ): 
      
    if not ('lEyePos'):
        print "create the face locators"
          
    else:
        
        eyeRotY = cmds.getAttr ('lEyePos.ry' )
        eyeRotZ = cmds.getAttr ('lEyePos.rz' ) 
        eyeCenterPos = cmds.xform( 'lEyePos', t = True, q = True, ws = True) 
  
    mirrorLR = upLowLR.replace("l_","r_")
    lEyeLoc = cmds.duplicate( "lEyePos", rr=1, rc=1, n= "l_eyeUp_loc")[0]
    cmds.xform( lEyeLoc, ws=1, t=[eyeCenterPos[0], eyeCenterPos[1]+ 5.0, eyeCenterPos[2]] )
    rEyeLoc = cmds.duplicate( lEyeLoc, n= lEyeLoc.replace("l_","r_"))
    cmds.xform( rEyeLoc, ws=1, t=[-eyeCenterPos[0], eyeCenterPos[1]+ 5.0, eyeCenterPos[2]] )
    #reorder the vertices in selection list
    ordered = []
    if "up" in upLowLR:
        if cmds.attributeQuery("upLidVerts", node = "lidFactor", exists=1)==True:
            ordered = cmds.getAttr( "lidFactor.upLidVerts")
        else:
            cmds.warning("store lid vertices in order first!!")
    	
    elif "lo" in upLowLR:
        if cmds.attributeQuery("loLidVerts", node = "lidFactor", exists=1):
    		ordered = cmds.getAttr( "lidFactor.loLidVerts")
    		ordered.pop(0), ordered.pop(-1)
        else:
            cmds.warning( "store lid vertices in order first!!" )
			  		
    # create parent group for eyelid joints
    if not cmds.objExists('eyeLidJnt_grp'): 
        cmds.group ( n = 'eyeLidJnt_grp', em =True, p ="jnt_grp" ) 
                 					
    null = cmds.group ( n = upLowLR+'EyeLidJnt_grp', em =True, p ="eyeLidJnt_grp" )
    #cmds.xform (null, t = eyeCenterPos, ws =1 )
    rNull = cmds.group ( n = mirrorLR +'EyeLidJnt_grp', em =True, p = "eyeLidJnt_grp" ) 
    #cmds.xform (rNull, t = (-eyeCenterPos[0], eyeCenterPos[1], eyeCenterPos[2]) )
    cmds.select(cl = True) 
      
    #create eyeLids parent joint 
    lLidJntP = cmds.joint(n = upLowLR + 'LidP_jnt', p = [eyeCenterPos[0], eyeCenterPos[1], eyeCenterPos[2]]) 
    rLidJntP = cmds.joint(n = mirrorLR + 'LidP_jnt', p = [-eyeCenterPos[0], eyeCenterPos[1], eyeCenterPos[2]])
    #cmds.setAttr ( LidJntP + ".jointOrientY", 0)
    cmds.parent ( lLidJntP, null )
    cmds.parent ( rLidJntP, rNull )
    cmds.setAttr ( lLidJntP + '.ry', eyeRotY ) 
    cmds.setAttr ( lLidJntP + '.rz', eyeRotZ )
    cmds.setAttr ( rLidJntP + '.ry', -eyeRotY )
    cmds.setAttr ( rLidJntP + '.rz', -eyeRotZ )
      
    cmds.select(cl =1)
    #UI for 'null.rx/ry/rz'?? cmds.setAttr ( null + '.rz', eyeRotZ )    
    index = 1
    for v in ordered:
        vertPos = cmds.xform ( v, t = True, q = True, ws = True )
        loc = cmds.spaceLocator( n= upLowLR + 'Loc' + str(index).zfill(2) )
        cmds.xform( loc, ws=1, t = vertPos )
        cmds.parent( loc, null )
        
        rLoc = cmds.spaceLocator( n= mirrorLR + 'Loc' + str(index).zfill(2) )
        cmds.xform( rLoc, ws=1, t = [ -vertPos[0], vertPos[1], vertPos[2]] )
        cmds.parent( rLoc, rNull )        
        
        lidJnt = cmds.joint(n = upLowLR + 'Lid' + str(index).zfill(2) + '_jnt', p = vertPos ) 
        lidJntTX = cmds.joint(n = upLowLR + 'LidTX' + str(index).zfill(2) + '_jnt', p = vertPos )
        cmds.joint ( lidJnt, e =True, zso =True, oj = 'zyx', sao= 'yup')
        blinkJnt = cmds.duplicate ( lidJnt, po=True, n = upLowLR + 'LidBlink' + str(index).zfill(2)+'_jnt' )
        cmds.parent ( blinkJnt[0], lLidJntP )
        cmds.setAttr ( blinkJnt[0] + '.tx' , 0 )
        cmds.setAttr ( blinkJnt[0] + '.ty' , 0 )  
        cmds.setAttr ( blinkJnt[0] + '.tz' , 0 ) 
        cmds.parent ( lidJnt, blinkJnt[0] )     
            
        wideJnt = cmds.duplicate ( blinkJnt, po=True, n = upLowLR + 'LidWide' + str(index).zfill(2) + '_jnt' )  
        scaleJnt = cmds.duplicate ( blinkJnt, po=True, n = upLowLR + 'LidScale' + str(index).zfill(2) + '_jnt' )
        cmds.parent ( blinkJnt, scaleJnt[0] )
        #cmds.joint ( scaleJnt[0], e =True, zso =True, oj = 'xyz', sao= 'yup')
        cmds.parent ( wideJnt[0], scaleJnt[0] )
        
        cmds.parent ( scaleJnt[0], w=1 )
        #mirror joint and aim constraint
        rLidJnt = cmds.mirrorJoint ( scaleJnt[0], mirrorBehavior=True, myz = True, searchReplace = ('l_', 'r_'))
        
        cmds.parent ( scaleJnt[0], lLidJntP )
        cmds.parent ( rLidJnt[0],  rLidJntP )

        rBlink = cmds.listRelatives( rLidJnt[0], c=1 )[0]
        print rBlink 
        cmds.aimConstraint( loc, blinkJnt, mo =1, weight=1, aimVector = (1,0,0), upVector = (0,1,0), worldUpType="object", worldUpObject = "l_eyeUp_loc" )
        cmds.aimConstraint( rLoc, rBlink, mo =1, weight=1, aimVector = (1,0,0), upVector = (0,1,0), worldUpType="object", worldUpObject = "r_eyeUp_loc" )
          
        index = index + 1
        




# run after modeling the "CTLCrvs"
''' 
1.up/loHiCrv wire to up/loCtlCrv 
2.BlinkLevelCrv(copy of upCtlCrv) blendshape to loCtlCrv   
3.up/loBlinkCrv wire to BlinkLevel crv 
4.up/loHiCrv blendShape to up/loBlinkCrv for "blinking"
5.up/loHiCrv wire to up/loCtlCrv for "detail control" 
'''
# create blink BS / wire deform for up/lo blinkCurve      
# pre = ["l_","r_"]        
def eyeCrvConnect( pre ):
    
    #create the blink Level with blendShape
    upCrv = pre  + "upCTLCrv01"
    blinkLevelCrv = cmds.duplicate( upCrv, rc=1, n = pre+ "BlinkLevelCrv" )[0]
    
    if not cmds.objExists ( pre + "Blink_bs"):
        
        blinkBS = cmds.blendShape( pre  + "loCTLCrv01", blinkLevelCrv, n = pre + "Blink_bs" )
    
    else:
        blinkBS =[ pre + "Blink_bs" ]
        
    upDown = { "up": 0 , "lo": 1 }
    for ud in upDown:
        
        blinkCrv = pre + ud  + "BlinkCrv01"
        if cmds.objExists( blinkCrv ):
            #attach blink_hiCrv to the blink_level curve
            cmds.setAttr( blinkBS[0] + "." + pre + "loCTLCrv01", upDown[ud] )
            wr = cmds.wire( blinkCrv, w = blinkLevelCrv, n = pre + ud + "Blink_wire" )
            cmds.setAttr( wr[0] + ".scale[0]", 0 ) 
            cmds.setAttr( wr[0] + ".dropoffDistance[0]", 5 )
            
            smartBlinkBS = cmds.blendShape( blinkCrv, pre+ud+"HiCrv01", n = pre + ud+ "Blink_bs" )
                
                


#create "attachCtl_grp" in hierachy
# adjust CTLcrv(master) shape to hiCrv
# place joints for eyeCtls at 20*i% on hi curve
def eyeCtrlCrv( prefix, numEyeCtl ):  

    title = [ "inCorner","in", "mid", "out", "outCorner" ] 
    tmpCrv = prefix + "HiCrv01"
    crvShape = cmds.listRelatives( tmpCrv, c=1, ni=1, s=1 )[0]    
    increm = 1.0 / (numEyeCtl-1)    
   
    vertPos = []
    ctlJnt = []
    ctlList = []
    for i in range( numEyeCtl ):
        
        poc =cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = prefix + '_eyeCtl_poc'+str(i) )   
        cmds.connectAttr( crvShape + ".worldSpace" , poc + ".inputCurve" )    
        cmds.setAttr ( poc + '.turnOnPercentage', 1 )
        cmds.setAttr ( poc + '.parameter', increm*i )
        
        pos = cmds.getAttr( poc + ".position" )[0]
        vertPos.append(pos)
        
        #create ctl joints grp
        if i in [0, numEyeCtl-1 ]:#first/last point for in/outCorner
        	null = cmds.group( em=1, n = prefix[:2] + title[i] + "Eye_JntP"  )
        else:
        	null = cmds.group( em=1, n = prefix + "_"+ title[i] + "Eye_JntP"  )
        	
        #place grp to the point
        cmds.xform( null, ws=1, t= pos )
        if cmds.objExists("attachCtl_grp"):
            if not cmds.objExists("eyeOnCtl_grp"):
                eyeGrp = cmds.group( em=1, n = "eyeOnCtl_grp" )
            
            cmds.parent( null, "eyeOnCtl_grp" )
                    
        else:
            print "create Hierarchy"

        jnt = cmds.joint( p = pos,  n = null.replace("Eye_JntP","Eye_JNT") )
        ctlJnt.append(jnt)      

        ctl = controller( title[i] + "Eye_CTL", pos, increm/5.0, "cc" )
        ctlList.append( ctl[1] )
        
        cmds.connectAttr( ctl + ".t" , jnt + ".t" )
        cmds.connectAttr( ctl + ".r" , jnt + ".r" )
        cmds.connectAttr( ctl + ".s" , jnt + ".s" )
        
    cmds.parent( "eyeOnCtl_grp", "attachCtl_grp" )
    
    #create CTLCrv ( l_upCTLCrv01, l_loCTLCrv01.... )            
    ctlCrv = cmds.curve( d= 3, ep= vertPos, n = prefix  + "CTLCrv01" )		        
            
    if "_lo" in prefix:
		corners = cmds.listRelatives( [ctlJnt[0], ctlJnt[-1]], p=1 )
		cmds.delete( corners, ctlList[0], ctlList[-1] )
		   
        #def controller( ctlName, position, radius, shape):
        #cmds.parent( eyeGrp, "attachCtl_grp" )
        #controller( title[i] + "Eye_CTL", pos, increm/5.0, "cc" )            

    

#create eyeCtls on head  
def eyeCtl_onFace():		   
    #for arFace Sukwon Shin
    prefix = ["l_up", "l_lo", "r_up", "r_lo"]
    for p in prefix:
        ctlCrv = p + "CTLCrv01"
        title = [ "inCorner","in", "mid", "out", "outCorner" ]
        eyeCtlJnt = []         
        for t in title:
            
            if "Corner" in t:
                if cmds.objExists( p[:2] + t+"Eye_JNT"):
                    eyeCtlJnt.append( p[:2] + t+"Eye_JNT")
                    
                else:
                    cmds.promptDialog("create ")
                
            else:
                if cmds.objExists( p + "_" + t+"Eye_JNT" ):
                    eyeCtlJnt.append( p + "_" + t+"Eye_JNT")

        print eyeCtlJnt
        if cmds.objExists(ctlCrv):
            
            cmds.skinCluster( ctlCrv, eyeCtlJnt, toSelectedBones=1, bindMethod =0, nw =1, maximumInfluences=3, omi=1, rui=1 )
        


    
def eyeHiCrv( prefix ):

    #get ordered vertices
    if "up" in prefix:
        orderVtx = cmds.getAttr( "lidFactor.upLidVerts" )
    
    elif "lo" in prefix:
        orderVtx = cmds.getAttr( "lidFactor.loLidVerts" )
            
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
        
    tmpCrv = cmds.curve( d= 1, p= posOrder, n = prefix  + "HiCrv01" )
    blinkCrv = cmds.duplicate( tmpCrv, n = tmpCrv.replace("Hi","Blink"), rc=1 )[0]
    crvShape = cmds.listRelatives( tmpCrv, c=1, ni=1, s=1 )    
    
    if "lo" in prefix:
        posOrder=posOrder[1:-1]
        
    else:
        pass
        
    for i, pos in enumerate( posOrder ):
        
        uParam = getUParam( pos, tmpCrv )
        poc =cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = prefix + 'eyePOC'+ str(i+1).zfill(2) )
        cmds.connectAttr( crvShape[0] + ".worldSpace" , poc + ".inputCurve" )
        cmds.setAttr( poc+".parameter", uParam )
        cmds.connectAttr( poc + ".position", prefix + "Loc"+str(i+1).zfill(2) +".t" )
        


def switchJntToCls(prefix):
    eyeGeo = cmds.getAttr( "lidFactor.eyelidGeo")
    eyeSkin = mel.eval("findRelatedSkinCluster %s"%eyeGeo ) 
    jnts =cmds.ls( pre + "LidBlink*_jnt", type = "joint" )
    vtxLeng = cmds.polyEvaluate( eyeGeo, v=1 )
    val = []
    for v in range(vtxLeng):
        val.append( 0 )    
     
    for j in jnts:
        if cmds.objExists(j.replace("_jnt","_cls")):
            cmds.warning( "eye clusters already created" )
        
        else:        
            cls = cmds.cluster( eyeGeo, n = j.replace("_jnt","_cls") )
            cmds.cluster( cls[0], e=1, bindState=1, wn = ( j , j ) )
            cmds.setAttr( eyeSkin + ".wl[0].w[0:%s]"%(vtxLeng -1 ), *val )
            cmds.delete(cls[1])       
    
    child = lastJntOfChain( jnts )
    for i, j in enumerate(child):
        
        jID = getJointIndex( eyeSkin, j )
        cmds.skinCluster( eyeSkin, e=1, selectInfluenceVerts = j )
        vtx = cmds.ls(sl=1, fl=1 )
        clsVal = []
        for v in range( vtxLeng ):
    
            if eyeGeo+ ".vtx[%s]"%v in vtx:
                wgt = cmds.getAttr( eyeSkin + ".weightList[%s].weights[%s]"%( v, jID))
                clsVal.append(wgt)
                            
            else:
                clsVal.append(0)
                
        eyeCls = jnts[i].replace("_jnt","_cls")        
        cmds.setAttr( eyeCls + ".wl[0].w[0:%s]"%str(vtxLeng-1),  *clsVal , s=vtxLeng )





        
#RNK Jaw Setup
def mouthJoint( upLow ): 
    
    lipEPos = cmds.xform( 'lipEPos', t = True, q = True, ws = True )
    lipWPos = [-lipEPos[0], lipEPos[1], lipEPos[2]] 
    lipNPos = cmds.xform( 'lipNPos', t = True, q = True, ws = True ) 
    lipSPos = cmds.xform( 'lipSPos', t = True, q = True, ws = True ) 
    lipYPos = cmds.xform( 'lipYPos', t = True, q = True, ws = True )
    jawRigPos = cmds.xform( 'jawRigPos', t = True, q = True, ws = True ) 
    cheekPos = cmds.xform( 'cheekPos', t = True, q = True, ws = True)
    squintPuffPos = cmds.xform( 'squintPuffPos', t = True, q = True, ws = True)
    lowCheekPos = cmds.xform( 'lowCheekPos', t = True, q = True, ws = True)
    
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
    cmds.rebuildCurve(rt = 0, d = 3, kr = 0, s = 6 )    
    bsCrv   = cmds.rename( tempflatCrv, upLow + '_lipBS_crv')
    bsCrvShape  = cmds.listRelatives( bsCrv, c = True )    
    
    jawTempCrv = cmds.duplicate( bsCrv )
    jawOpenCrv = cmds.rename( jawTempCrv[0], upLow +'_jawOpen_crv' )
    jawOpenCrvShape = cmds.listRelatives( jawOpenCrv, c = True)
    
    jawDropTempCrv = cmds.duplicate( bsCrv )
    jawDropCrv = cmds.rename( jawDropTempCrv[0], upLow +'_jawDrop_crv' )
    jawDropCrvShape = cmds.listRelatives( jawDropCrv, c = True)
    
    tmplipRollCrv = cmds.curve(d = 3, p =([0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0])) 
    cmds.rebuildCurve(rt = 0, d = 3, kr = 0, s = 4 )
    lipRollCrv = cmds.rename(tmplipRollCrv, upLow + '_lipRoll_crv' )
    lipRollCrvShape = cmds.listRelatives(lipRollCrv, c =1 )    

    tmplipPuffCrv = cmds.duplicate( lipRollCrv )
    lipPuffCrv = cmds.rename( tmplipPuffCrv[0], upLow +'_lipPuff_crv' )
    lipPuffCrvShape = cmds.listRelatives( lipPuffCrv, c = True )
    
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
        loc = cmds.spaceLocator( n= upLow + 'Loc' + str(i).zfill(2) )[0]
        jawDropPoc =cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = upLow +'_jawDrop' + str(i).zfill(2) + '_poc' )
        cmds.connectAttr( jawDropCrvShape[0] + ".worldSpace" , jawDropPoc + ".inputCurve" )
        cmds.setAttr( jawDropPoc + ".turnOnPercentage", 1 )
        cmds.setAttr( jawDropPoc +".parameter", increment )
        dropPocs.append(jawDropPoc)
        #get position list for hi curve
        pocPos = cmds.getAttr(jawDropPoc + ".position")[0]        
        cvPos.append( pocPos )
        cmds.connectAttr( jawDropPoc + ".position", loc + ".t" )        
        
        #lipRollCrv pointOnCurve
        lipRollPoc =cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = upLow +'_lipRoll' + str(i).zfill(2) + '_poc' )
        cmds.connectAttr( lipRollCrvShape[0] + ".worldSpace" , lipRollPoc + ".inputCurve" )
        cmds.setAttr( lipRollPoc + ".turnOnPercentage", 1 )
        cmds.setAttr( lipRollPoc +".parameter", increment )  
        rollPocs.append(lipRollPoc)
		
        #lipRollCrv pointOnCurve
        lipPuffPoc =cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = upLow +'_lipPuff' + str(i).zfill(2) + '_poc' )
        cmds.connectAttr( lipPuffCrvShape[0] + ".worldSpace" , lipPuffPoc + ".inputCurve" )
        cmds.setAttr( lipPuffPoc + ".turnOnPercentage", 1 )
        cmds.setAttr( lipPuffPoc +".parameter", increment ) 
        puffPocs.append(lipPuffPoc)
        
        increment = increment + linearDist
				
    bsHiCrv = cmds.curve( d= 1, ep= cvPos, n = upLow  + "_lipBsHiCrv" )
    bsHiCrvShape = cmds.listRelatives( bsHiCrv, c=1, ni=1, s=1 )
    
    jawOpenHiCrv = cmds.curve( d= 1, ep= cvPos, n = upLow  + "_jawOpenHiCrv" )
    jawOpenHiCrvShape = cmds.listRelatives( jawOpenHiCrv, c=1, ni=1, s=1 )    

    bsWireNode = cmds.wire( bsHiCrv, w = bsCrv, n = upLow + "_lipBS_wire" )
    cmds.setAttr ( bsWireNode[0] + ".dropoffDistance[0]", 5 )
    jawWireNode = cmds.wire( jawOpenHiCrv, w = jawOpenCrv, n = upLow + "_jawOpen_wire" )
    cmds.setAttr ( jawWireNode[0] + ".dropoffDistance[0]", 5 )    
    bsPocs = []
    openPocs = []
    #BS/JawOpen hiCurve created
    for v in range ( vNum ):
        #get curve U value
        uParam = getUParam( cvPos[v], bsHiCrv )
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
        cmds.delete( lipJnts[0], lipJnts[-1], dropPocs[0], dropPocs[-1], rollPocs[0], rollPocs[-1], puffPocs[0], puffPocs[-1],
        openPocs[0], openPocs[-1], bsPocs[0], bsPocs[-1]  )
    else:
    	pass
    	      		
    if not cmds.objExists('lipCrv_grp'):
        lipCrvGrp = cmds.group ( n = 'lipCrv_grp', em =True, p = 'faceMain|crv_grp' )    
    cmds.parent( bsCrv, jawOpenCrv, jawDropCrv, lipRollCrv, bsHiCrv, jawOpenHiCrv, lipPuffCrv, 'lipCrv_grp' )
    



   
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
    lipPuffPocList = cmds.ls ( upLow +'_lipPuff*_poc', fl=True, type = 'pointOnCurveInfo' )

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
		lipRollTran_plus = cmds.shadingNode ('plusMinusAverage', asUtility=True, n = upLow +'lipRollTran'+str(i+1)+'_plus' )
        
		poc = pocList[i]
		initialX = cmds.getAttr ( poc + '.positionX' )

		jawPoc = jawPocList[i]
		initX = cmds.getAttr ( jawPoc + '.positionX' )

		jawDropPoc = jawDropPocList[i]
		iniX = cmds.getAttr ( jawDropPoc + '.positionX' )

		lipRollPoc = lipRollPocList[i]
		lipPuffPoc = lipPuffPocList[i]

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

		#LipRoll_translateXYZ connection
		cmds.setAttr ( lipRollTran_plus + '.operation', 1 ) 
		cmds.connectAttr ( lipPuffPoc + '.positionX', lipRollTran_plus + '.input3D[0].input3Dx') 
		cmds.setAttr (lipRollTran_plus + '.input3D[1].input3Dx', -iniX )
		cmds.connectAttr ( lipRollTran_plus + '.output3Dx',  rollJnts[i] + '.tx')

		cmds.setAttr ( jotXTran_plus + '.operation', 1 ) 
		cmds.connectAttr ( lipPuffPoc + '.positionY', lipRollTran_plus + '.input3D[0].input3Dy') 
		cmds.connectAttr ( lipRollTran_plus + '.output3Dy',  rollJnts[i] + '.ty')

		cmds.setAttr ( jotXTran_plus + '.operation', 1 ) 
		cmds.connectAttr ( lipPuffPoc + '.positionZ', lipRollTran_plus + '.input3D[0].input3Dz')
		cmds.connectAttr ( lipRollTran_plus + '.output3Dz',  rollJnts[i] + '.tz')
                
        

        
   

# create "lipBS_grp" / crv blendShape
def lipCtlSetup( upLow ):

    bsCrv = upLow + "_lipBS_crv"  
    jawOpenCrv = upLow + "_jawOpen_crv"
    jawDropCrv = upLow + "_jawDrop_crv"
    #lipRollCrv = upLow + "_lipRoll_crv"
    lipPuffCrv = upLow + "_lipPuff_crv"    

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
    jnts = lipCtrlJntForCrv( upLow, bsCrv, "lipCtl", 7 )
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
    
    
    

#mirror left curve(cvs) to right curve(cvs), all curves are from 0 to +x
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
    sequence =['A', 'B', 'C', 'D', 'E', 'F', 'G' ]         
    ctlJnts = []
    vertPos = []
    if not cmds.objExists( name+"_jntGrp" ):
        lipJntGrp = cmds.group ( n = name+"_jntGrp", em =True, p = 'faceMain|jnt_grp' )
    else:
        lipJntGrp = name+"_jntGrp"
    
    title = upLow +"_"+ name
    pocs = pocEvenOnCrv( crv, numCtls, title )

    for i in range( numCtls ):
    
        pos = cmds.getAttr( pocs[i] + ".position")[0]
        #create ctl joints grp
        if i == 0 :
            null = cmds.group( em=1, n = "rCorner_" + name + "_jntP" , p = lipJntGrp )
        elif i == numCtls-1 :
            null = cmds.group( em=1, n = "lCorner_" + name + "_jntP", p = lipJntGrp )
        elif i == center:
            null = cmds.group( em=1, n = upLow + "Mid_" + name + "_jntP", p = lipJntGrp )
        else:
            if i < center:
                null = cmds.group( em=1, n = upLow + "R_%s_"%sequence[i-1] + name + "_jntP", p = lipJntGrp )        	
            elif i > center:
                null = cmds.group( em=1, n = upLow + "L_%s_"%sequence[numCtls-i-2] + name + "_jntP", p = lipJntGrp )             

        cmds.xform( null, ws=1, t= pos )
        jnt = cmds.joint( p = pos,  n = null.replace("_jntP"," ") )
        ctlJnts.append(jnt)

    return ctlJnts






def indieCrvSetup():
    #skin lip Curves 
    crvDict = { "lipBS_crv": "lipCtl_jntGrp", "jawDrop_crv":"jawDrop_jntGrp", "jawOpen_crv":"jawOpen_jntGrp" }
    for crv, grp in crvDict.items():
        
        ctlJnts=lastJntOfChain( grp )
        cornerJnt = [ x for x in ctlJnts if "Corner" in x ]

        if "jaw" in crv:
        	
			upMidJnt = [ y for y in ctlJnts if "up" in y ][0]
			loMidJnt = [ z for z in ctlJnts if "lo" in z ][0]
			cmds.expression( s= '%s.tx = %s.tx*0.5 + %s.ty*0.060'%(cornerJnt[0], loMidJnt, loMidJnt) )                             
			cmds.expression( s= '%s.tx = %s.tx*0.5 - %s.ty*0.060'%(cornerJnt[1], loMidJnt, loMidJnt ) )  
			cmds.expression( s= '%s.ty = %s.ty*0.5'%(cornerJnt[0], loMidJnt ) )
			cmds.expression( s= '%s.tz = %s.tz*0.5'%(cornerJnt[0], loMidJnt ) )  
			cmds.expression( s= '%s.ty = %s.ty*0.5'%(cornerJnt[1], loMidJnt ) )
			cmds.expression( s= '%s.tz = %s.tz*0.5'%(cornerJnt[1], loMidJnt ) ) 
			cmds.expression( s= '%s.tx = %s.tx*0.1'%(upMidJnt, loMidJnt ) ) 
			cmds.expression( s= '%s.ty = %s.ty*0.01'%(upMidJnt, loMidJnt) )                      
           
        for upLow in ["up","lo"]:            
            
            ctlJot = [ j for j in ctlJnts if upLow in j ]    
            cmds.skinCluster( upLow+"_"+crv, ctlJot+cornerJnt, bm=0, nw=1, weightDistribution=0, mi=3, omi=True, tsb=1 )   

        
'''#using utility
def indieCrvSetup():
jawOpenMult = cmds.shadingNode ( 'multiplyDivide', asUtility= True, n = 'open_cornerRatio_mult' )
jawOpenMult = cmds.shadingNode ( 'multiplyDivide', asUtility= True, n = 'open_midRatio_mult' )
jawDropMult = cmds.shadingNode ( 'multiplyDivide', asUtility= True, n = 'drop_Ratio_mult' )
reverseMult = cmds.shadingNode ( 'multiplyDivide', asUtility= True, n = 'jawTx_reverse' )  
#set up cornerJoint.ty damp on midJoint.ty
if cmds.attributeQuery( "cornerTy", node = "jaw_open", exists=1)==False:
    cmds.addAttr( "jaw_open", ln ="cornerTy", attributeType='float', dv = .5 )
    cmds.setAttr( "jaw_open.cornerTy", e =1, keyable=1 )
elif cmds.attributeQuery( "cornerTx", node = "jaw_open", exists=1)==False:
    cmds.addAttr( "jaw_open", ln ="cornerTx", attributeType='float', dv = .5 )
    cmds.setAttr( "jaw_open.cornerTx", e =1, keyable=1 )
elif cmds.attributeQuery( "cornerTz", node = "jaw_open", exists=1)==False:
    cmds.addAttr( "jaw_open", ln ="cornerTz", attributeType='float', dv = .5 )
    cmds.setAttr( "jaw_open.cornerTz", e =1, keyable=1 )
             
cmds.connectAttr( loMidJnt+ ".ty",  jawOpenMult + ".input1Y" )
cmds.connectAttr( "jaw_open.cornerTy", jawOpenMult + ".input2Y" )
cmds.connectAttr( jawOpenMult + ".outputY",  )

cmds.connectAttr( loMidJnt+ ".tx",  jawOpenMult + ".input1X" )
cmds.connectAttr( "jaw_open.cornerTx", jawOpenMult + ".input2X" )

cmds.connectAttr( loMidJnt+ ".tz",  jawOpenMult + ".input1Z" )
cmds.connectAttr( "jaw_open.cornerTz", jawOpenMult + ".input2Z" )


if cmds.attributeQuery( "cornerTy", node = "jaw_drop", exists=1)==False:
    cmds.addAttr( "jaw_drop", ln ="cornerTy", attributeType='float', dv = .5 )
    cmds.setAttr( "jaw_drop.cornerTy", e =1, keyable=1 )
elif cmds.attributeQuery( "cornerTx", node = "jaw_drop", exists=1)==False:
    cmds.addAttr( "jaw_drop", ln ="cornerTx", attributeType='float', dv = .08 )
    cmds.setAttr( "jaw_drop.cornerTx", e =1, keyable=1 )
elif cmds.attributeQuery( "cornerTz", node = "jaw_drop", exists=1)==False:
    cmds.addAttr( "jaw_drop", ln ="cornerTz", attributeType='float', dv = .08 )
    cmds.setAttr( "jaw_drop.cornerTz", e =1, keyable=1 )
'''

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
        print "shit"
        # jawOpen_crv control
        cmds.connectAttr ( 'jaw_open.tx', 'loMid_jawOpen.tx' )
        cmds.connectAttr ( 'jaw_open.ty', 'loMid_jawOpen.ty' )
        cmds.connectAttr ( 'jaw_open.tz', 'loMid_jawOpen.tz' )
                
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
        cmds.connectAttr ( jawDropMult+".outputX", 'loMid_jawDrop.tx' )
        cmds.connectAttr ( jawDropMult+".outputY", 'loMid_jawDrop.ty' )
        cmds.connectAttr ( jawDropMult+".outputZ", 'loMid_jawDrop.tz' )
        
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
        	#cmds.connectAttr ( jotXMults[i]+ '.outputY', lipJots[i] +'.ry' )
        
        	cmds.connectAttr ( 'swivel_ctrl.tx', jotXMults[i] + '.input1Z' )
        	cmds.connectAttr ( "lipFactor.lipJotX_rz", jotXMults[i] + '.input2Z' )
        	cmds.connectAttr ( jotXMults[i] + '.outputZ', jotXRotZ_add + ".input1" )        	
        	cmds.connectAttr ( 'swivel_ctrl.rz', jotXRotZ_add + ".input2" )
        	cmds.connectAttr ( jotXRotZ_add + ".output", lipJots[i] +'.rz' )
        
        swivelMult = cmds.shadingNode ( 'multiplyDivide', asUtility= True, n = 'swivel_mult' )
    	cmds.connectAttr ( 'swivel_ctrl.t', swivelMult + '.input1' )
    	cmds.setAttr( swivelMult + '.input2',  1, 1, 1 )
    	cmds.connectAttr ( swivelMult + '.output', jawSemi + '.t' )

    	# center of loLip_joints control jawSemi       	
    	cmds.connectAttr ( jotXMults[midNum] + '.outputY', jawSemi + '.ry' )
    	jotX_add = 'loLip_add'+ str(midNum).zfill(2)
    	cmds.connectAttr ( jotX_add + ".output", jawSemi + '.rz' )
    
    	cmds.connectAttr ( swivelMult + '.output', lipJotP +'.t', f=1 )
		    
    	'''scale controll'''
    	# swivel.ty + jawOpen.ty influence scaleX/Z
    	tranX_add  = cmds.shadingNode ( 'addDoubleLinear', asUtility=True, n = 'ctlX_add' )
    	tranY_add  = cmds.shadingNode ( 'addDoubleLinear', asUtility=True, n = 'ctlY_add' )
    	lipPcale_sum = cmds.shadingNode ( 'plusMinusAverage', asUtility= True, n = 'lipPScale_sum' )
    	tranYPowerMult = cmds.shadingNode ( 'multiplyDivide', asUtility= True, n = 'tranYPower_mult' )        
    	divideMult = cmds.shadingNode ( 'multiplyDivide', asUtility= True, n = 'tranY_divide' )
    	#lipP scale down as lipP/jawSemi goes down
        cmds.connectAttr( "jawClose_jnt.ty", tranY_add + ".input1" )
        cmds.connectAttr( "jawSemi.ty", tranY_add + ".input2" )
        headGeo = cmds.getAttr( "helpPanel_grp.headGeo")
        tyMax = cmds.getAttr( headGeo+"Shape.boundingBoxMax")[0]
        tyMin = cmds.getAttr( headGeo+"Shape.boundingBoxMin")[0]
        dampTy = (tyMax[1]-tyMin[1])/4
        cmds.setAttr(tranYPowerMult + ".operation", 3 )
        cmds.expression( s= '%s.input1Y = -1*(%s.output/%s - 1)'%( tranYPowerMult, tranY_add, dampTy ) )        
        
        #stretch control power = value ** exponent ( x = pow(4, 3) )
        if cmds.attributeQuery( "exponent", node = "swivel_ctrl", exists=1)==False:
            cmds.addAttr( "swivel_ctrl", ln ="exponent", attributeType='float', dv = .2 )
            cmds.setAttr( "swivel_ctrl.exponent", e =1, keyable=1 )        
        cmds.connectAttr( "swivel_ctrl.exponent", tranYPowerMult + ".input2Y" )
        cmds.setAttr(divideMult + ".operation", 2 )
        cmds.setAttr( divideMult + ".input1", 1,1,1 )
      
        cmds.connectAttr( tranYPowerMult + ".outputY", divideMult + ".input2Y" )
        #cmds.connectAttr( tranYPowerMult + ".outputZ", divideMult + ".input2Z" )
        cmds.connectAttr( divideMult + ".outputY", lipJotP + ".sx" )
        cmds.connectAttr( divideMult + ".outputY", lipJotP + ".sz" )
        cmds.connectAttr( divideMult + ".outputY", jawSemi + ".sx" )
        #cmds.connectAttr( divideMult + ".outputZ", jawSemi + ".sz" )
        
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
    	print "crab"

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
def lipFreeCtl( upLow, numDetail, offset ):

	sel = cmds.ls(sl=1 )
	if not sel:		    
		if cmds.attributeQuery( upLow + "LipVerts", node = "lipFactor", exists=1)==True:
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
		crv = cmds.polyToCurve( form=2, degree=1, n = upLow + "_ctlGuide_Crv")[0]
		          
	else:
		nCrv = cmds.listRelatives( sel[0], c=1)
		if cmds.nodeType(nCrv)=="nurbsCurve":		    
		    myCrv = sel[0]
		    crv = cmds.rename( myCrv, upLow + "_lipCtl_Guide" )		    
		else:
		    cmds.confirmDialog( title='Confirm', message='Select "guide Curve for lip Ctrls"!!' )
	
	cvList = cmds.ls( crv + ".cv[*]", fl=1 )
	cvStart = cmds.getAttr(cvList[0] + ".xValue")
	cvEnd = cmds.getAttr( cvList[-1] + ".xValue" )
	if cvStart > cvEnd:
		cmds.reverseCurve( crv, ch= 1, rpo=1 ) 
    
	if not cmds.objExists( "lip_ctl_grp" ):
		lipCtlGrp = cmds.group ( n = "lip_ctl_grp", em =True )
	else:
		lipCtlGrp = "lip_ctl_grp"
    
    if not cmds.listRelatives( lipCtlGrp, p=1 ) == "attachCtl_grp":
	cmds.parent( lipCtlGrp, "attachCtl_grp" )
	#curves to connect
	lipRollCrv = upLow + "_lipRoll_crv"
	lipPuffCrv = upLow + "_lipPuff_crv"
		
	#create main lip controller connect with the joints on "lipBS_crv"
	myList = nullEvenOnCrv( crv, 7, crv[:3]+"Lip" )
	nulls = myList[0]
	pocs = myList[1]                 
	if upLow == "lo":
		nulls.pop(0), nulls.pop(-1), pocs.pop(0), pocs.pop(-1)
    	
	for i, n in enumerate(nulls):
	
		pos = cmds.getAttr( pocs[i] +".position")[0]
		#connect null to poc 
		cmds.connectAttr( pocs[i] +".position", n +".t" )
		ctrl = controller( n.replace("_nulP","_ctl"), pos, 0.10, "sq" )
		#parent controller to null 
		cmds.parent(ctrl[1], n )
		#controller offset
		cmds.setAttr( ctrl[1] + ".tz", offset )
		jnt = n.replace("_nulP","Ctl")
		cmds.connectAttr( ctrl[0] + ".t" , jnt+ ".t"  )
		cmds.parent( n, lipCtlGrp )
		if "Corner" not in ctrl[0]:
			cmds.connectAttr( ctrl[0] + ".rx", lipRollCrv + ".cv[%s].yValue"%str(i) )
					    	
	#rebuild puff/roll curve
	cvs = cmds.ls( lipPuffCrv + ".cv[*]", fl=1 )
	if not len(cvs) == numDetail+2:
		cmds.rebuildCurve( lipPuffCrv, rebuildType = 0, spans = numDetail-1, keepRange = 0, degree = 3 )
    
	cvList =[]
	for x in range(numDetail +2):
		if x == 1 or x== numDetail:
		    pass
		else:
		    cvList.append(x) 	
	
	#create detail locator on poc 
	tmplist = nullEvenOnCrv( crv, numDetail, crv[:3]+"Tail" )     
	grpList = tmplist[0]
	pocList = tmplist[1]
	if upLow == "lo":
		grpList.pop(0), grpList.pop(-1), pocList.pop(0), pocList.pop(-1), cvList[0], cvList[-1]
	
	print cvList 
	print grpList 
	for i, grp in enumerate(grpList):
		pos = cmds.getAttr( pocList[i] +".position" )[0]
		#prnt = cmds.group(  n = grp.replace("_nulP","_prn"), em=1, p = grp )
		ctl = controller( grp.replace("_nulP","_ctl"), pos, 0.05, "cc" )
		#loc = cmds.spaceLocator( n = grp.replace("_nulP", "loc"), p = pos )
		cmds.parent(ctl[1], grp )
		cmds.setAttr( ctl[1] + ".tz", offset/2.0 )
		
		cmds.connectAttr( pocList[i] + ".position", grp + ".t" )        
		cmds.parent( grp, lipCtlGrp )        
		
		if upLow == "lo":
			x = i+1
		else:
			x = i	
		xVal = cmds.getAttr(lipPuffCrv + ".cv[%s].xValue"%str(cvList[x]))
		xValAdd = cmds.shadingNode('addDoubleLinear', asUtility=True, n = upLow + 'xVal' + str(x) + '_add' )
		cmds.setAttr( xValAdd + ".input1", xVal )
		cmds.connectAttr( ctl[0] + ".tx", xValAdd + ".input2" )
		cmds.connectAttr( xValAdd + ".output",  lipPuffCrv + ".cv[%s].xValue"%str(cvList[x]) )
		cmds.connectAttr( ctl[0] + ".ty",  lipPuffCrv + ".cv[%s].yValue"%str(cvList[x]) )
		cmds.connectAttr( ctl[0] + ".tz",  lipPuffCrv + ".cv[%s].zValue"%str(cvList[x]) )
		print  pocList[i], ctl, lipPuffCrv + ".cv[%s]"%str(cvList[x])   


        
#put null(with lip Name) at poc node on curve evenly
#name = ["up_bsCtl", "up_jawOpen", "jawDrop"... ]
def nullEvenOnCrv( crv, numCtls, name ):

    pocs =pocEvenOnCrv( crv, numCtls, name )
    center = (numCtls-1)/2
    
    nulls =[]
    for i in range( numCtls ):
    
        pos = cmds.getAttr( pocs[i] + ".position")[0]
        #create ctl joints grp
        if i == 0 :
            null = cmds.group( em=1, n = "rCorner_" + name + "_nulP" )
        elif i == numCtls-1 :
            null = cmds.group( em=1, n = "lCorner_" + name + "_nulP" )
        elif i == center:
            null = cmds.group( em=1, n = "mid_" + name + "_nulP" )
        else:
            if i < center:
                null = cmds.group( em=1, n = "r_" + name + "_nulP%s"%str(i) )        	
            elif i > center:
                null = cmds.group( em=1, n = "l_" + name + "_nulP%s"%str(numCtls-i-1) )             

        cmds.xform( null, ws=1, t= pos )
        nulls.append(null) 
                
    return nulls, pocs


def symmetryLetter(numCtl): 
  
    center = (numCtl-1)/2
    corner=[]
    left = []
    right = []
    sequence = string.ascii_uppercase
    mid = "mid" 
    for i in range(numCtl):
        
        if i>center:
            left.append(sequence[i-center-1])

        elif i<center:
            right.append(sequence[i])
 
    right = right[::-1]
    
    nulls = right+[mid]+left       
    return nulls

   
def symmetrNullOnCrv( upLow, crv, numCtls, name ):

    pocs =pocEvenOnCrv( upLow, crv, numCtls, name )
    center = (numCtls-1)/2
    
    sequence = string.ascii_uppercase
    RL = symmetryCtlNum(numCtls)

    for rl in RL:
        print rl
        for i, n in enumerate(rl): #rightside list number
            
            pos = cmds.getAttr( pocs[n] + ".position")[0]
            null = cmds.group( em=1, n = upLow + name + sequence[i]+"_nulP" )
            cmds.xform( null, ws=1, t= pos )
                       
            
    midPos = cmds.getAttr( pocs[center] + ".position")[0]
    mid = cmds.group( em=1, n = upLow + "Mid_" + name + "_nulP" )       
    cmds.xform( mid, ws=1, t= midPos )  
    
    if not cmds.objExists("rCorner_" + name + "_nulP"):
        rPos = cmds.getAttr( pocs[0] + ".position")[0]
        rCorner = cmds.group( em=1, n = "rCorner_" + name + "_nulP" )       
        cmds.xform( rCorner, ws=1, t= rPos )     

    if not cmds.objExists("lCorner_" + name + "_nulP"):
        print "shit"
        lPos = cmds.getAttr( pocs[numCtls-1] + ".position")[0]
        lCorner = cmds.group( em=1, n = "lCorner_" + name + "_nulP" )       
        cmds.xform( lCorner, ws=1, t= lPos )                     
    
    nulls = [ rCorner, mid, lCorner]
    return nulls



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

        
def getUParam( pnt = [], crv = None):

    point = OpenMaya.MPoint(pnt[0],pnt[1],pnt[2])
    curveFn = OpenMaya.MFnNurbsCurve(getDagPath(crv))
    paramUtill=OpenMaya.MScriptUtil()
    paramPtr=paramUtill.asDoublePtr()
    isOnCurve = curveFn.isPointOnCurve(point)
    if isOnCurve == True:
        
        curveFn.getParamAtPoint(point , paramPtr,0.001,OpenMaya.MSpace.kObject )
    else :
        point = curveFn.closestPoint(point,paramPtr,0.001,OpenMaya.MSpace.kObject)
        curveFn.getParamAtPoint(point , paramPtr,0.001,OpenMaya.MSpace.kObject )
    
    param = paramUtill.getDouble(paramPtr)  
    return param
    
    



def getDagPath(objectName):
    '''
    This function let you get an MObject from a string rappresenting the object name
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
        selectionList.add(objectName)
        oNode = OpenMaya.MDagPath()
        selectionList.getDagPath(0, oNode)
        return oNode
        
        


def resetCtl( grp ):
    
    if cmds.objExists( grp ):
        tmpChild = cmds.listRelatives( grp, ad=1, ni=1, type = ["nurbsCurve", "mesh", "nurbsSurface"]  )
        child = [ t for t in tmpChild if not "Orig" in t ]
        ctls = cmds.listRelatives( child, p=1 )
        for ct in ctls:
    		attrs = cmds.listAttr( ct, k=1, unlocked = 1, inUse=0 )
    		if attrs:
    			for at in attrs:
    				cnntList = cmds.listConnections( ct + "."+ at, s=1, d=0, type = "animCurve" )
    				if cnntList:
    					if 'scale' in at or "visibility" in at:
    						cmds.setAttr( ct+"."+at, 1 )
    					else:
    						cmds.setAttr( ct+"."+at, 0 )                                     
                    
    				else:
    					if 'scale' in at or "visibility" in at:
    						cmds.setAttr( ct+"."+at, 1 )
    					else:
    						cmds.setAttr( ct+"."+at, 0 )
    						
    else:
        print "find the top ctls group node"
        

def customCtl(  obj, ctlName, position ):        
    
    if cmds.objExists( obj ):
        dup = cmds.duplicate( obj )
        nCtl = cmds.rename( dup[0], ctlName )
        
        topNd = cmds.duplicate( nCtl, po=1, n= nCtl+"P" )
        cmds.parent( nCtl, topNd[0])     
        cmds.xform (topNd[0], ws = True, t = position )
        
        ctrl = [nCtl, topNd[0]]
        return ctrl
    else:
        cmds.promptDialog("select %s object"%obj )

                
""" create circle controller(l_/r_/c_) and parent group at the position
    shape : circle = cc / square = sq 
    colorNum : 13 = red, 15 = blue, 17 = yellow, 18 = lightBlue, 20 = lightRed, 23 = green
    return [ ctrl, ctrlP ]
24 똥색 / 23:숙색 / 22:밝은 노랑 / 21:밝은 주황 / 20: 밝은 핑크 / 19: 밝은연두 / 18: 하늘색 / 17 yellow / 16 white
15: dark blue / 14: bright green / 13: red / 12: red dark 자두색 / 11: 고동색 / 10: 똥색 / 9: 보라 / 8: 남보라
7: 녹색 / 6: 파랑 / 5 : 남색 / 4 : 주황 / 3 : 회색 / 2: 진회색 / 1: 검정"""
def controller( ctlName, position, radius, shape ):
    if shape == "cc":
        degree = 3 # cubic
        section = 8 # smooth circle
        colorNum = [17, 6, 13, 23]
        
    elif shape =="sq" :
        degree = 1 # linear
        section = 4 # straight line
        colorNum = [10, 18, 20, 23]
        
    else:
        print 'shape = either "cc"(circle) or "sq"(square)'
    
    if ctlName[:2]=="c_":
        #if center, color override is yellow
        circleCtrl = cmds.circle (n = ctlName, ch=False, nr=(0, 0, 1), c=(0, 0, 0), sw=360, r= radius, d=degree, s=section )
        cmds.setAttr (circleCtrl[0] +".overrideEnabled", 1)
        cmds.setAttr (circleCtrl[0] +".overrideShading", 0)
        cmds.setAttr (circleCtrl[0] + ".overrideColor", colorNum[0] )
        null = cmds.group (circleCtrl[0], w =True, n = circleCtrl[0]+"P" )
        cmds.xform (null, ws = True, t = position )
     
    elif ctlName[:2]=="l_":
        #if left, color override is blue
        circleCtrl = cmds.circle (n = ctlName, ch=False, nr=(0, 0, 1), c=(0, 0, 0), sw=360, r= radius, d=degree, s=section )
        cmds.setAttr (circleCtrl[0] +".overrideEnabled", 1)
        cmds.setAttr (circleCtrl[0] +".overrideShading", 0)
        cmds.setAttr (circleCtrl[0] + ".overrideColor", colorNum[1] )
        null = cmds.group (circleCtrl[0], w =True, n = circleCtrl[0]+"P" )
        cmds.xform (null, ws = True, t = position )
     
    elif ctlName[:2]=="r_":
        #if right, color override is red
        circleCtrl = cmds.circle (n = ctlName, ch=False, nr=(0, 0, 1), c=(0, 0, 0), sw=360, r= radius, d=degree, s=section )
        cmds.setAttr (circleCtrl[0] +".overrideEnabled", 1)
        cmds.setAttr (circleCtrl[0] +".overrideShading", 0)
        cmds.setAttr (circleCtrl[0] + ".overrideColor", colorNum[2] )
        null = cmds.group (circleCtrl[0], w =True, n = circleCtrl[0]+"P")
        cmds.xform (null, ws = True, t = position )
 
    else :
        #if none of c_, l_, r_
        circleCtrl = cmds.circle (n = ctlName, ch=False, nr=(0, 0, 1), c=(0, 0, 0), sw=360, r= radius, d=degree, s=section )
        cmds.setAttr (circleCtrl[0] +".overrideEnabled", 1 )
        cmds.setAttr (circleCtrl[0] +".overrideShading", 0 )
        cmds.setAttr (circleCtrl[0] + ".overrideColor", colorNum[3] )
        null = cmds.group (circleCtrl[0], w =True, n = circleCtrl[0]+"P")
        cmds.xform (null, ws = True, t = position )
    
    ctrl = [circleCtrl[0], null]
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



             
'''create brow curve for browMapSurf'''
#select verices in order to create referece curve/  
#turn off symmetry select / turn on tracking selection
#select vertices in order(left half) or select start vert first / end vert last
#automatrically select right half in order using browCurve() with "closestPointOnMesh" to complete curve.
def curve_halfVerts( name, openClose, degree ):

    myVert = cmds.ls( os=1, fl=1 )    
    vertNum = len(myVert)    

    if name == "brow":
        if cmds.attributeQuery("browVerts", node = "browFactor", exists=1)==True:
            jntNum = len(cmds.getAttr("browFactor.browVerts"))
            if not vertNum == jntNum:
                cmds.confirmDialog( title='Confirm', message='the number of verts different from the number of joints' )
                
        myList = {}
        for i in myVert:        
            xyz = cmds.xform ( i, q=1, ws=1, t=1 )
            myList[ i ] = xyz[0]
        ordered = sorted(myList, key = myList.__getitem__)
        mapCurve( ordered, name, openClose, degree )
        
    else:
    
        mapCurve( myVert, name, openClose, degree )
              
 
            
                

            
#geo should be symmetrical/ for open curve or curve is part of edge loop  
def mapCurve( vtx, name, openClose, degree ):
      
    orderPos =[]
    if name in ["brow","lip"]:
		vt = cmds.xform( vtx[0], q=1, t=1, ws=1)
		# verts selection is only left part
		if vt[0]**2 <0.0001:
			for t in vtx[1:][::-1]:
				vtxPos = cmds.xform( t, q=1, t=1, ws=1)
				mrrPos = [-vtxPos[0],vtxPos[1],vtxPos[2]]
				if vtxPos[0]-mrrPos[0]>0.001:
					orderPos.append(mrrPos)        
			print len(orderPos)
			for v in vtx:		    
				vtxPos = cmds.xform( v, q=1, t=1, ws=1)
				orderPos.append(vtxPos)
        # if verts selection in order entire region
		else:
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

        closedOderPos = orderPos + orderPos[:3]
        print closedOderPos
        numPoint = len(closedOderPos)
        knots = []
        for i in range(numPoint+2):
            knots.append(i)
        print knots
        closeCrv = cmds.curve( d=float(degree), per=1, p=closedOderPos, k = knots )    
        cmds.rename( closeCrv,  name + "MapCrv01" )

#mapCurve(3, "open", "lip")




        
#select lower curve to high curve to creaet brow map surf
def loftMapSurf(name):
    title=""
    if name =="brow":
        title = "browMapSurf"
    elif name == "eye":
        title = "eyeTip_map"
    elif name == "lip":
        title = "lipTip_map"
    crvSel = cmds.ls( os=1, fl=1, type = 'transform')
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
def browWideJnt():
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
    
    cvs = cmds.ls('liploftCurve01.cv[*]', fl =1)
    cvLen = len(cvs)
    # ordered Joints for skin
    uplipJnt = cmds.ls('upLipRoll*_jnt', fl =1, type = 'joint')
    lolipJnt = cmds.ls('loLipRoll*_jnt', fl =1, type = 'joint')
    lolipJnt.reverse()
    lipTipJnt = uplipJnt + lolipJnt
    jntNum = len(lipTipJnt)
    if not cvLen == jntNum:
        print 'the number of mouth joints is different to the cvs '
    else: 
        loftCrvs = cmds.ls('liploftCurve*', type = 'transform')
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
    

#RNK skinWeighting
def rnkBrowMapSkinning():
    if not "browMapSurf":
        print "create browMapSurf first!!"
    else : browMapSurf = "browMapSurf"
    lBrowJnts = cmds.ls ("L_*Eyebrow*", type ="joint")
    rBrowJnts = cmds.ls ("R_*Eyebrow*", type ="joint")
    
    x = rBrowJnts[::-1]
    y = lBrowJnts
    orderJnts = x + y
    jntNum = len(orderJnts)    
    if not cmds.objExists('C_jnt_fineTune_Head_JNT'):
        headSkelPos = cmds.xform('headSkelPos', q =1, ws =1, t =1 )
        cmds.joint(n = 'C_jnt_fineTune_Head_JNT', p = headSkelPos )
    orderJnts.insert( jntNum/2, "C_jnt_fineTune_Head_JNT" )
    jntNum = len(orderJnts)
    vrts= cmds.polyEvaluate(browMapSurf, v =1 )
    numVtx = vrts/jntNum
    if vrts%jntNum==0:
        skinCls = cmds.skinCluster(orderJnts , browMapSurf, toSelectedBones=1 )
        # 100% skinWeight to C_jnt_fineTune_Head_JNT
        cmds.skinPercent(skinCls[0], browMapSurf, transformValue = ["C_jnt_fineTune_Head_JNT", 1])
        # skinWeight
        for i in range (0, jntNum):
            vtxs = "browMapSurf.vtx[%s:%s]"%( numVtx*i, numVtx*i+numVtx-1 )
            cmds.skinPercent( skinCls[0], vtxs, transformValue = [ orderJnts[i], 1])
    else:
        print "Number of faces and browJnts are not matching"  



def rnkEyeMapSkinning():

    if not "eyeTip_map":
        print "create eyeTip_map first!!"
    else : eyeMapSurf = "eyeTip_map"
    orderJnts=['L_jnt_fineTune_Eyelid_InCorner_JNT' ,'L_jnt_fineTune_Eyelid_Top_in_JNT', 'L_jnt_fineTune_Eyelid_Top_mid_JNT','L_jnt_fineTune_Eyelid_Top_out_JNT',
    'L_jnt_fineTune_Eyelid_OutCorner_JNT', 'L_jnt_fineTune_Eyelid_Bot_out_JNT', 'L_jnt_fineTune_Eyelid_Bot_mid_JNT', 'L_jnt_fineTune_Eyelid_Bot_in_JNT' ]
    
    if cmds.objExists('L_jnt_fineTune_Eyelid_scale_JNT'):

        orderJnts.append( 'L_jnt_fineTune_Eyelid_scale_JNT' )
        
    else:
        print "L_Eyelid_scale_JNT is missing"
    
    jntNum = len(orderJnts[:-1])    
    vrts= cmds.polyEvaluate(eyeMapSurf, v =1 )
    numVtx = vrts/jntNum
    print vrts, jntNum
    if vrts%jntNum==0:
        skinCls = cmds.skinCluster(orderJnts , eyeMapSurf, toSelectedBones=1 )
        # skinWeight
        for i in range (0, jntNum):
            vtxs = "eyeTip_map.vtx[%s:%s]"%( numVtx*i, numVtx*i+numVtx-1 )
            cmds.skinPercent( skinCls[0], vtxs, transformValue = [ orderJnts[i], 1])
    else:
        print "Number of faces and eyeJnts are not matching"      


def rnkLipMapSkinning():

    if not "lipTip_map":
        print "create lipTip_map first!!"
    else : lipMapSurf = "lipTip_map"

    orderJnts = [ 'R_jnt_fineTune_Lips_Bot_JNT', 'R_jnt_fineTune_Lips_Corner_JNT','R_jnt_fineTune_Lips_Top_JNT', 'C_jnt_fineTune_Lips_Top_JNT',
     'L_jnt_fineTune_Lips_Top_JNT', 'L_jnt_fineTune_Lips_Corner_JNT', 'L_jnt_fineTune_Lips_Bot_JNT', 'C_jnt_fineTune_Lips_Bot_JNT' ]

    jntNum = len(orderJnts)    
    vrts= cmds.polyEvaluate(lipMapSurf, v =1 )
    numVtx = vrts/jntNum
    print vrts, jntNum
    if vrts%jntNum==0:
        skinCls = cmds.skinCluster(orderJnts , lipMapSurf, toSelectedBones=1 )

        # skinWeight
        for i in range (0, jntNum):
            vtxs = "lipTip_map.vtx[%s:%s]"%( numVtx*i, numVtx*i+numVtx-1 )
            cmds.skinPercent( skinCls[0], vtxs, transformValue = [ orderJnts[i], 1])
    else:
        print "Number of faces and lipJnts are not matching"  



               
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


    
#create null between the selected node and it's parent
#the selected node's transform becomes zero out
def createPntNull():
    
    mySel =cmds.ls(sl=1)       
    
    for nd in mySel:
        
        pos = cmds.xform(nd, q=1, ws=1, rotatePivot=1 ) 
        
        if cmds.nodeType(nd) =="transform":
            topGrp = cmds.duplicate( nd, po=1, n=nd+"P" )
            cmds.parent(nd, topGrp)
            
        else:
            prnt = cmds.listRelatives( nd, p=1, type ="transform")
            emGrp = cmds.group( em=1, n= nd+"P" )
            cmds.xform( emGrp, ws=1, t=pos )
            cmds.parent( nd, emGrp )    
            
            if prnt:
                cmds.parent( emGrp, prnt[0] ) 





                
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
    for eye in eyeBall:
        hist = cmds.listHistory( cmds.listRelatives(eye, c=1)[0] )
        bs = [ x for x in hist if cmds.nodeType(x)=="blendShape"] 
    
        alias = cmds.aliasAttr( bs[0], q=1 )
        for tgt, wgt in zip(*[iter(alias)]*2):
            if "iris" in tgt:
                cmds.connectAttr( eye[0]+"iris_dial.ty", bs[0]+"."+tgt )   
            elif "pupil" in tgt:
                cmds.connectAttr( eye[0]+"pupil_dial.ty", bs[0]+"."+tgt )
                
                
                
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
    """ 
    Assign the shader to the object list
    arguments:
        objList: list of objects or faces
    """
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

def assignShader():
    #assign shader to hodong objects
    shadingDict={ "ai_airShdr":["invisibleBody"], "ai_hdSkin_shdr":["visibleBody","head_main" ], "ai_hd_iris":["l_eyeBall_main", "r_eyeBall_main"], "aiStandardHair":["hodong_hair2", "sweatHead_mustach","eyeBrow_geo","goatTee"], 
    "ai_hiphopCap":["Snapback"],"cornea_mtlf":["l_cornea_main","r_cornea_main"],"gum_Mtl":["gum_upper_main","gum_bttm_main", "ffd_tongue_main"], "hd_Jacket":["jacket"], "hd_pants":["pants"],"teeth_mtl":["upr_teeth_main","lwr_teeth_main"] }
    
    #select shaders
    for k, v in shadingDict.items():
        if cmds.objExists(k):
            if len(v)>1:
                for i in v:
                    if cmds.objExists(i):
                        cmds.select(i)
                        assignSelectionToShader( k )
                    
                    else:
                        cmds.warning("there is no %s geo!!"%i )                                        
                    
               
            else:
                if cmds.objExists(v[0]):
                    cmds.select( v[0] )
                    assignSelectionToShader( k )                
    
    
        else:
            cmds.warning("import %s shaders!!"%k )  



            

            
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
    
