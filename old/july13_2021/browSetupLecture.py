placefaceRig()
import controlPanel
#create rotXPivot/ rotYPivot 
#select vertex
browJoints()
browDetailCtls()
connectBrowCtrls ( size, offset )



def placefaceRig():
    ''' after place the face locators'''
    headSkelPos = cmds.xform( 'headSkelPos', t = True, q = True, ws = True)
    JawRigPos = cmds.xform( 'jawRigPos', t = True, q = True, ws = True)
    lEyePos = cmds.xform( 'lEyePos', t = True, q = True, ws = True)
    
    faceMain = cmds.group (em =1, n = 'faceMain', )    
    clsGroup = cmds.group (em =1, n = 'cls_grp', p = faceMain )
    crvGroup = cmds.group (em =1, n = 'crv_grp', p = faceMain )
    jntGroup = cmds.group (em =1, n = 'jnt_grp', p = faceMain )
    browJnt = cmds.group (em =1, n = 'browJnt_grp', p = jntGroup  )
    faceGeoGroup = cmds.group (em =1, n = 'faceGeo_grp', p = faceMain )
    helpPanel = cmds.group (em =1, n = 'helpPanel_grp', p = faceMain )
    spn = cmds.group (em =1, n = 'spn', p = faceMain )
    headSkel = cmds.group (em =1, n = 'headSkel', p = spn )
    cmds.xform ( headSkel, ws = 1, t = headSkelPos )
    cmds.joint(n = 'headSkel_jnt', p = [ 0, headSkelPos[1], headSkelPos[2]] ) 
    browRig = cmds.group (em =1, n = 'browRig', p = headSkel )
    bodyHeadP = cmds.group (em =1, n = 'bodyHeadTRSP', p = headSkel )
    cmds.xform ( bodyHeadP, ws = 1, t = headSkelPos )    
    bodyHead = cmds.group (em =1, n = 'bodyHeadTRS', p = bodyHeadP )
    cmds.xform ( bodyHead, ws = 1, t = headSkelPos )    
    
    faceFactor = cmds.group (em =1, n = 'faceFactor', p = faceMain )
    browFactor = cmds.group (em =1, n = 'browFactor', p = faceFactor )
    cmds.addAttr( browFactor, ln ="browUp_scale", attributeType='float'  )
    cmds.addAttr( browFactor, ln ="browDown_scale", attributeType='float'  )
    cmds.addAttr( browFactor, ln ="browRotateY_scale", attributeType='float'  )
    cmds.setAttr( browFactor +".browUp_scale", 20.0 )
    cmds.setAttr( browFactor +".browDown_scale", 10.0 )
    cmds.setAttr( browFactor +".browRotateY_scale", 10.0 )
     


def browJoints():
    browRotXPos = cmds.xform( 'rotXPivot', t = True, q = True, ws = True )
    browRotYPos = cmds.xform( 'rotYPivot', t = True, q = True, ws = True )
        
    #reorder the vertices in selection list  
    vtxs =cmds.ls(sl=1 , fl=1)
    myList = {}
    for i in vtxs:        
        xyz = cmds.xform ( i, q=1, ws=1, t=1)
        myList[ i ] = xyz[0]
        print myList
    orderedVerts = sorted(myList, key = myList.__getitem__) 
    
    cmds.select(cl = True)
    index = 1
    for x in orderedVerts:
        vertPos = cmds.xform(x, t = True, q = True, ws = True)
        
        if ( vertPos[0] <= 0.05):
            
            baseCntJnt = cmds.joint(n = 'c_browBase'+ str(index).zfill(2)+'_jnt', p = [ 0, browRotXPos[1], browRotXPos[2]])  
            ryCntJnt = cmds.joint(n = 'c_browRotY_jnt', p = [ 0, browRotYPos[1], browRotYPos[2]])           
            parentCntJnt = cmds.joint(n = 'c_browP'+ str(index).zfill(2)+'_jnt', p = vertPos)
            cmds.setAttr ( baseCntJnt+'.rotateOrder', 2)
            cmds.joint(n = 'c_brow'+ str(index).zfill(2), p = vertPos)
            cmds.joint( ryCntJnt, e=1, oj= 'zyx', secondaryAxisOrient = 'yup', ch=1,  zso=1)
            cmds.select(cl = True)
            cmds.parent ( baseCntJnt, "browJnt_grp")
        else:
    
            baseJnt = cmds.joint(n = 'l_browBase' + str(index).zfill(2)+'_jnt', p = browRotXPos )
            ryJnt = cmds.joint(n = 'l_browRotY' + str(index).zfill(2)+ '_jnt', p = browRotYPos ) 
            parentJnt = cmds.joint(n = 'l_browP' + str(index).zfill(2)+ '_jnt', p = vertPos)
            cmds.setAttr ( baseJnt+'.rotateOrder', 2)
            cmds.joint(n = 'l_brow' + str(index).zfill(2) + '_jnt', p = vertPos)
            cmds.select(cl = True)
            cmds.parent ( baseJnt, "browJnt_grp")
            cmds.joint( ryJnt, e=1, oj= 'zyx', secondaryAxisOrient = 'yup', ch=1,  zso=1)
           
            cmds.mirrorJoint ( baseJnt, mirrorYZ= True, searchReplace=('l', 'r'))
            cmds.select(cl = True)
            index = index + 1
            

#browJoints()




def connectBrowCtrls ( size, offset ):
    
	jnts = cmds.ls ( '*browBase*_jnt', fl = True, type ='joint') 
	jntNum = len(jnts)
	jnts.sort()
	z = [ jnts[0] ]
	y = jnts[1:jntNum/2+1]
	jnts.reverse()
	x = jnts[:jntNum/2]
	orderJnts = x + z + y

	#revese 'browFactor.browRotateX_scale'
	reverseMult = cmds.shadingNode ( 'multiplyDivide', asUtility=True, n = 'browReverse_mult' )
	cmds.connectAttr( 'browFactor.browUp_scale', reverseMult + ".input1X")
	cmds.connectAttr( 'browFactor.browDown_scale', reverseMult + ".input1Z")
	cmds.connectAttr ( 'browFactor.browRotateY_scale', reverseMult + '.input1Y' )
	cmds.setAttr( reverseMult + ".input2", -1,-1,-1 )
	
	if cmds.objExists("browCrv_grp"):
		cmds.delete("browCrv_grp")
	elif not cmds.objExists("attachCtl_grp"):
		attachCtlGrp = cmds.group ( n = "attachCtl_grp", em =True, p = "faceMain|spn|headSkel|bodyHeadTRSP|bodyHeadTRS|" )
	elif cmds.objExists("browCtl_grp"):
		cmds.delete("browCtl_grp")
        
	browCtlGrp = cmds.group ( n = "browCtl_grp", em =True, p = "faceMain|spn|headSkel|bodyHeadTRSP|bodyHeadTRS|attachCtl_grp" )    
	browCrvGrp = cmds.group ( n = "browCrv_grp", em =True, p = "faceMain|crv_grp" ) 
	tempBrowCrv = cmds.curve ( d = 1, p =([-1,0,0],[-0.5,0,0],[0,0,0],[0.5,0,0],[1,0,0]) ) 
	cmds.rebuildCurve ( tempBrowCrv, rebuildType = 0, spans = jntNum-1, keepRange = 0, degree = 1 )    
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
	cmds.rebuildCurve (browCtlCrv, rebuildType = 0, spans = 4, keepRange = 0, degree = 3 ) 
	browCtlCrvShape = cmds.listRelatives ( browCtlCrv, c = True ) 
	cmds.parent ( browCtlCrv, "browCrv_grp") 
	
	sumX = cmds.shadingNode ( 'plusMinusAverage', asUtility =True, n = 'browTX_sum' )
	cmds.setAttr ( sumX + '.operation', 1 )
	
	#connect browMain Ctrls to browCrv
	sequence =['A', 'B', 'C', 'D', 'E']
	cvs= cmds.ls("browCtrlCrv.cv[*]", fl=True )
	cvBX = cmds.getAttr ( cvs[2] + '.xValue' )
	cvDX = cmds.getAttr ( cvs[4] + '.xValue' )
	cmds.connectAttr ( 'brow_arcB.tx', sumX + '.input2D[0].input2Dx' )
	cmds.setAttr ( sumX + '.input2D[1].input2Dx', cvBX )
	cmds.connectAttr ( sumX + '.output2D.output2Dx', cvs[2] + '.xValue' )
	cmds.connectAttr ( 'brow_arcD.tx', sumX + '.input2D[0].input2Dy' )
	cmds.setAttr ( sumX + '.input2D[1].input2Dy', cvDX )
	cmds.connectAttr ( sumX + '.output2D.output2Dy', cvs[4] + '.xValue' )
	cmds.connectAttr ('brow_arcA.ty',  cvs[0] + '.yValue' )
	cmds.connectAttr ('brow_arcE.ty',  cvs[6] + '.yValue' )
    
	for num in range (1, 6):
	    
	    cmds.connectAttr ('brow_arc' + sequence[num-1] + '.ty',  cvs[num] + '.yValue' )
	
	#create browDetail ctls for brow joints
	browDMom = cmds.ls ( 'browDetail*P', fl =True, type = "transform")
	browDetails = cmds.listRelatives ( browDMom, c=True, type = "transform")
	
	index = 0    
	for jnt in orderJnts:

	    basePos = cmds.xform( jnt, t = True, q = True, ws = True)
	    rotYJnt = cmds.listRelatives ( jnt, c=True)
	    rotYJntPos = cmds.xform(rotYJnt[0], t = True, q = True, ws = True)  
	    childJnt = cmds.listRelatives( rotYJnt[0], c =1 )  
	    jntPos = cmds.xform(childJnt[0], t = True, q = True, ws = True)
	    browDetail = browDetails[index]

	    #point on shapeCrv 
	    shapePOC = cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = 'browShapePOC'+ str(index+1).zfill(2))
	    cmds.connectAttr ( browCrvShape[0] + ".worldSpace",  shapePOC + '.inputCurve')
	    cmds.setAttr ( shapePOC + '.turnOnPercentage', 1 )
	    increment = 1.0/(jntNum-1)        
	    cmds.setAttr ( shapePOC + '.parameter', increment *index )
	    #point on freeform crv
	    POC = cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = 'eyeBrowPOC'+ str(index+1).zfill(2))
	    cmds.connectAttr ( browCtlCrvShape[0] + ".worldSpace",  POC + '.inputCurve')
	    cmds.setAttr ( POC + '.turnOnPercentage', 1 )
	    increment = 1.0/(jntNum-1)        
	    cmds.setAttr ( POC + '.parameter', increment *index )
	    # browCrv controls browDetail parent 
	    cmds.connectAttr ( POC + ".positionY", browDMom[index] + ".ty"  )        
	    initialX = cmds.getAttr (POC + '.positionX')
	    index = index + 1
	    attrs = ["sx","sy","sz","v"]

	    if jnt in x:

        	rBrowCtrl = controller( 'r_brow'+ str(re.findall('\d+', jnt)[0]) + "_ctl", ( jntPos[0], jntPos[1], jntPos[2]+ offset), size, 'cc' )
        	ctlP = rBrowCtrl[1]
        	zeroGrp = cmds.duplicate(ctlP, po =1, n = ctlP.replace("_ctlP","_dummy") )
        	cmds.parent(ctlP, zeroGrp[0] )
        	rotYGrp = cmds.group( em =1, n = rBrowCtrl[0].replace("_brow","_browRY"), p = "browCtl_grp")
        	cmds.xform (rotYGrp, ws = True, t = rotYJntPos )
        	cmds.parent(zeroGrp[0], rotYGrp)
        	ctlBase = cmds.group( em =1, n = ctlP.replace("_ctlP","_base"), p = "browCtl_grp")
        	cmds.xform (ctlBase, ws = True, t = basePos )
        	cmds.parent(rotYGrp, ctlBase)
        	browCrvCtlToJnt(rBrowCtrl[0], browDetail, jnt, rotYJnt[0], ctlBase, rotYGrp, shapePOC, POC, initialX, index )
        	
        	for att in attrs:
        		cmds.setAttr ( rBrowCtrl[0] + ".%s"%att, lock =1, keyable = 0)
			
	    
	    elif jnt in y:

	        lBrowCtrl = controller( 'l_brow'+ str(re.findall('\d+', jnt)[0]) + "_ctl", ( jntPos[0], jntPos[1], jntPos[2]+ offset), size, 'cc' )
	        ctlP = lBrowCtrl[1]
	        zeroGrp = cmds.duplicate(ctlP, po =1, n = ctlP.replace("_ctlP","_dummy") )
	        cmds.parent( ctlP, zeroGrp[0] )
	        rotYGrp = cmds.group( em =1, n = lBrowCtrl[0].replace("_brow","_browRY"), p = "browCtl_grp")
	        cmds.xform (rotYGrp, ws = True, t = rotYJntPos )
	        cmds.parent(zeroGrp[0], rotYGrp)
	        ctlBase = cmds.group( em =1, n = ctlP.replace("_ctlP","_base"), p = "browCtl_grp")
	        cmds.xform (ctlBase, ws = True, t = basePos )
	        cmds.parent(rotYGrp, ctlBase)
	        for att in attrs:
	            cmds.setAttr ( lBrowCtrl[0] + ".%s"%att, lock =1, keyable = 0)
	        browCrvCtlToJnt (lBrowCtrl[0], browDetail, jnt, rotYJnt[0], ctlBase, rotYGrp, shapePOC, POC, initialX, index  )
	    
	    elif jnt == z[0]:

	        centerBrowCtrl = controller( 'c_brow_ctl', ( jntPos[0], jntPos[1], jntPos[2]+ offset), size, 'cc' )
	        ctlP = centerBrowCtrl[1]
	        zeroGrp = cmds.duplicate(ctlP, po =1, n = ctlP.replace("_ctlP","_dummy") )
	        cmds.parent( ctlP, zeroGrp[0] )
	        rotYGrp = cmds.group( em =1, n = centerBrowCtrl[0].replace("_brow","_browRY"), p = "browCtl_grp")
	        cmds.xform (rotYGrp, ws = True, t = rotYJntPos )
	        ctlBase = cmds.group( em =1, n = ctlP.replace("_ctlP","_base"), p = "browCtl_grp")
	        cmds.xform (ctlBase, ws = True, t = basePos )
	        cmds.parent(zeroGrp[0], rotYGrp)
	        cmds.parent(rotYGrp, ctlBase)
	        for att in attrs:
	            cmds.setAttr ( centerBrowCtrl[0] + ".%s"%att, lock =1, keyable = 0)
	        browCrvCtlToJnt ( centerBrowCtrl[0], browDetail, jnt, rotYJnt[0], ctlBase, rotYGrp, shapePOC, POC, initialX, index )
	    
	    

#connectBrowCtrls ( .4, .4 )




""" create circle controller(l_/r_/c_) and parent group at the position
    shape : circle = cc / square = sq 
    colorNum : 13 = red, 15 = blue, 17 = yellow, 18 = lightBlue, 20 = lightRed, 23 = green
    return [ ctrl, ctrlP ]"""

def controller( ctlName, position, radius, shape):
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






#create browDetail Controller (miNum = number of lidJoints )    
'''control parent name should be "browDetailCtrl0" and have the scale value ( 1, 1, 1) '''
import maya.cmds as cmds
def browDetailCtls():        
    browJnts = cmds.ls ( "*browBase*_jnt", fl = True, type = "joint" )
    jntNum = len(browJnts)
    browJnts.sort()
    z = [ browJnts[0] ]
    y = browJnts[1:jntNum/2+1]
    browJnts.reverse()
    x = browJnts[:jntNum/2]
    orderJnts = x + z + y    
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



#BrowCrv BlendShape mirror Weight
import re
import maya.cmds as cmds
def LRBlendShapeWeight( lipCrv, lipCrvBS ):
    cvs = cmds.ls ( lipCrv+'.cv[*]', fl =1)
    length = len (cvs)
    
    increment = 1.0/(length-1)
    targets = cmds.aliasAttr( lipCrvBS, q=1)
    tNum = len(targets)   
    
    for t in range(0, tNum, 2):
        if targets[t][0] == 'l' :
            indexL=re.findall('\d+', targets[t+1])
            cmds.setAttr ( lipCrvBS + '.inputTarget[0].inputTargetGroup[%s].targetWeights[%s]'%(str(indexL[0]), str(length/2)), .5 ) 
            for i in range(0, length/2):                
                cmds.setAttr ( lipCrvBS + '.inputTarget[0].inputTargetGroup[%s].targetWeights[%s]'%(str(indexL[0]), str(i)), 0 ) 
                cmds.setAttr ( lipCrvBS + '.inputTarget[0].inputTargetGroup[%s].targetWeights[%s]'%(str(indexL[0]), str(length-i-1)), 1 )   
                
        if targets[t][0] == 'r' :
            indexR=re.findall('\d+', targets[t+1])
            cmds.setAttr ( lipCrvBS + '.inputTarget[0].inputTargetGroup[%s].targetWeights[%s]'%(str(indexR[0]), str(length/2)), .5 ) 
            for i in range(0, length/2):                
                cmds.setAttr ( lipCrvBS + '.inputTarget[0].inputTargetGroup[%s].targetWeights[%s]'%(str(indexR[0]), str(i)), 1 ) 
                cmds.setAttr ( lipCrvBS + '.inputTarget[0].inputTargetGroup[%s].targetWeights[%s]'%(str(indexR[0]), str(length-i-1)), 0 )     





def browCrvCtlToJnt (browCtrl, browDetail, jnt, rotYJnt, ctlBase, rotYCtl, shapePOC, POC, initialX, index ):        
    #connect browCtrlCurve and controller to the brow joints
    ctrlMult = cmds.shadingNode ( 'multiplyDivide', asUtility=True, n = jnt.split('Base', 1)[0] +'CtrlMult'+ str(index) )
    jntMult = cmds.shadingNode ( 'multiplyDivide', asUtility=True, n = jnt.split('Base', 1)[0] +'JntMult'+ str(index) )
    browXYZSum = cmds.shadingNode ( 'plusMinusAverage', asUtility=True, n = jnt.split('Base', 1)[0] +'BrowXYZSum'+ str(index))
    browCtlRotSum = cmds.shadingNode ( 'plusMinusAverage', asUtility=True, n = jnt.split('Base', 1)[0] +'CtlRotSum'+ str(index))
    addBrowCtl = cmds.shadingNode ( 'plusMinusAverage', asUtility=True, n = jnt.split('Base', 1)[0] +'AddBrowCtl'+ str(index))
     
    #brow TX sum      
    cmds.connectAttr ( browDetail + '.tx', browXYZSum + '.input3D[0].input3Dx')
    #POC TX zero out 
    cmds.connectAttr ( POC + '.positionX', browXYZSum + '.input3D[1].input3Dx')
    cmds.setAttr ( browXYZSum + '.input3D[2].input3Dx', -initialX )
    cmds.connectAttr ( shapePOC + '.positionX', browXYZSum + '.input3D[3].input3Dx')
    cmds.setAttr ( browXYZSum + '.input3D[4].input3Dx', -initialX )
    #browXYZSum.tx --> ctrlMult.ry 
    cmds.connectAttr ( browXYZSum + '.output3Dx', ctrlMult+'.input1X')
    cmds.connectAttr ( 'browFactor.browRotateY_scale', ctrlMult +'.input2X')
    cmds.connectAttr ( ctrlMult+'.outputX', rotYCtl + '.ry' )    
    
    #add browCtl.tx 
    cmds.connectAttr ( browXYZSum + '.output3Dx', addBrowCtl + '.input3D[0].input3Dx')
    cmds.connectAttr ( browCtrl + '.tx', addBrowCtl + '.input3D[1].input3Dx')    
    #addBrowCtl.tx --> jntMult.ry 
    cmds.connectAttr ( addBrowCtl + '.output3Dx', jntMult+'.input1X')
    cmds.connectAttr ( 'browFactor.browRotateY_scale', jntMult+'.input2X')
    cmds.connectAttr ( jntMult+'.outputX', rotYJnt + '.ry' )    
    
    
    #brow TY sum    
    #1. POC.ty sum
    cmds.connectAttr ( POC + '.positionY', browXYZSum +'.input3D[0].input3Dy')
    cmds.connectAttr ( shapePOC + '.positionY', browXYZSum + '.input3D[1].input3Dy')
    #2. detail ctl.ty sum
    cmds.connectAttr ( browDetail + '.ty', browXYZSum + '.input3D[2].input3Dy')
    #browXYZSum.ty --> ctrlMult.rx 
    cmds.connectAttr ( browXYZSum + '.output3Dy', ctrlMult+'.input1Y')
    cmds.connectAttr ( 'browReverse_mult.outputX', ctrlMult +'.input2Y')
    cmds.connectAttr ( ctrlMult+'.outputY', ctlBase + '.rx' )
    
    #add browCtl.ty
    browCond = cmds.shadingNode( "condition", asUtility=1, n = "browScale_Cond") 
    cmds.connectAttr ( browXYZSum + '.output3Dy', addBrowCtl + '.input3D[0].input3Dy')
    cmds.connectAttr ( browCtrl + '.ty', addBrowCtl + '.input3D[1].input3Dy')        
    #add BrowCtl.ty --> jntMult.rx 

    cmds.connectAttr(  addBrowCtl + ".output3Dy", browCond + ".firstTerm" )
    cmds.setAttr ( browCond + ".secondTerm", 0 )
    cmds.setAttr( browCond + ".operation", 2 )  #greater than
    cmds.setAttr ( browCond + ".colorIfTrueG", 0 )    

    cmds.connectAttr( 'browReverse_mult.outputX', browCond+".colorIfTrueR" )
    cmds.connectAttr( 'browReverse_mult.outputZ', browCond+".colorIfFalseR" )
    cmds.connectAttr( 'browReverse_mult.outputZ', browCond+".colorIfFalseG" )
     
    cmds.connectAttr( addBrowCtl + ".output3Dy", jntMult + ".input1Y" )
    cmds.connectAttr( addBrowCtl + ".output3Dy", jntMult + ".input1Z" )
    cmds.connectAttr( browCond+".outColorR", jntMult + ".input2Y" )
    cmds.connectAttr( browCond+".outColorG", jntMult + ".input2Z" )
    cmds.connectAttr ( jntMult+'.outputY',  jnt + '.rx' )
 
      
    #brow TZ sum
    browPCtl =cmds.listRelatives( cmds.listRelatives (rotYCtl, c =1, type = 'transform')[0], c =1, type = 'transform')
    browPJnt = cmds.listRelatives ( rotYJnt, c =1, type = 'joint')
    browJnt = cmds.listRelatives ( browPJnt[0], c =1, type = 'joint')
    cmds.connectAttr ( shapePOC + '.positionZ', browXYZSum + '.input3D[0].input3Dz')
    cmds.connectAttr ( browXYZSum + '.output3Dz', browPCtl[0]+'.tz' )
     
    #addBrowCtl.tz --> browJnt[0] + ".tz"   
    cmds.connectAttr ( browXYZSum + '.output3Dz', addBrowCtl + '.input3D[0].input3Dz')
    cmds.connectAttr ( browCtrl + '.tz', addBrowCtl + '.input3D[1].input3Dz')  
    cmds.connectAttr ( addBrowCtl + '.output3Dz', browJnt[0] + '.tz' ) 
    
    #extra rotate ctrl for browJnt[0]   
    cmds.connectAttr ( browCtrl + '.rx', browCtlRotSum + '.input3D[0].input3Dx') 
    cmds.connectAttr ( browDetail + '.rx', browCtlRotSum + '.input3D[1].input3Dx') 
    cmds.connectAttr ( browCtrl + '.ry', browCtlRotSum + '.input3D[0].input3Dy') 
    cmds.connectAttr ( browDetail + '.ry', browCtlRotSum + '.input3D[1].input3Dy')  
    cmds.connectAttr ( browCtrl + '.rz', browCtlRotSum + '.input3D[0].input3Dz') 
    cmds.connectAttr ( browDetail + '.rz', browCtlRotSum + '.input3D[1].input3Dz') 

    cmds.connectAttr ( browCtlRotSum + '.output3Dx', browJnt[0] + '.rx')
    cmds.connectAttr ( browCtlRotSum + '.output3Dy', browJnt[0] + '.ry')
    cmds.connectAttr ( browCtlRotSum + '.output3Dz', browJnt[0] + '.rz')