# -*- coding: utf-8 -*-


import re
import maya.cmds as cmds


'''
*11/13/2017
    1.browWideJnt() update : arface browSetup 에 wide_jnt 추가하는 function
    
눈썹 셋업

1. brow joints 생성 : run browJoints() 

2. create browDetail Controller : run browDetailCtls() --> detail controller 생성

3. load func : browCrvCtlToJnt / LRBlendShapeWeight/ ( CreativeGene\presentation\scripts\twitchScript\brow) 
    controller02 ( CreativeGene\presentation\scripts\twitchScript\face\06_15_2016 )

4. 컨트롤 조인트 연결 : connectBrowCtrls( size, offset )

'''


def browWideJnt():
    browJnts =cmds.listRelatives("eyebrowJnt_grp", c=1)
    browWide = [ x for x in browJnts if "browWide" in x ]
    if browWide:
    	print "browWide_jnts already exist"
    
    else:
    	for bj in browJnts:
    	    jntMult= cmds.listConnections( bj, s=1, d=0, skipConversionNodes=1, type= "multiplyDivide" )
            browCond= cmds.listConnections( jntMult[0], s=1, d=0, skipConversionNodes=1, type="condition" )
            browSum = cmds. listConnections( browCond[0], s=1, d=0, skipConversionNodes=1, type="plusMinusAverage" )
            cmds.connectAttr( browSum[0] + ".output3Dy", jntMult[0] + ".input1Z" )
            if "r_" in bj:
                cmds.connectAttr( 'browFactor.browDown_scale', browCond[0]+".colorIfFalseG" )                
            else:
                cmds.connectAttr( 'browReverse_mult.outputZ', browCond[0]+".colorIfFalseG" )
            cmds.connectAttr( browCond[0]+".outColorG", jntMult[0] + ".input2Z" )
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
        
        
        
        
        

# brow joints create
'''
UI  : controller size, mult.input 2 values
select left brow vertex points and pivot point. run the script
name = centerBrowBase0l, EyeBrowBase01... '''
def browJoints():    

    browRotXPos = cmds.xform( 'rotXPivot', t = True, q = True, ws = True )
    browRotYPos = cmds.xform( 'rotYPivot', t = True, q = True, ws = True )
    if not cmds.objExists("eyebrowJnt_grp"):
	cmds.group(em=1, p="jnt_grp", n = "eyebrowJnt_grp")		
		
    #reorder the vertices in selection list  
    vtxs =cmds.ls(sl=1 , fl=1)
    myList = {}
    index = 0
    for i in vtxs:        
        val = re.findall('\d+', i )
        xyz = cmds.getAttr ("head_REN.vrts[" +val[0]+"]")[0]
        myList[ i ] = xyz[0]
        print myList
    orderedVerts = sorted(myList, key = myList.__getitem__) 
    print orderedVerts
    
    cmds.select(cl = True)
    index = 1
    for x in orderedVerts:
        vertPos = cmds.xform(x, t = True, q = True, ws = True)
        
        if ( vertPos[0] <= 0.05):
            
            baseCntJnt = cmds.joint(n = 'c_browBase_jnt', p = [ 0, browRotXPos[1], browRotXPos[2]])  
            ryCntJnt = cmds.joint(n = 'c_browRotY_jnt', p = [ 0, browRotYPos[1], browRotYPos[2]])           
            parentCntJnt = cmds.joint(n = 'c_browP_jnt', p = vertPos)
            cmds.setAttr ( baseCntJnt+'.rotateOrder', 2)
            cmds.joint(n = 'c_brow'+ str(index).zfill(2)+'_jnt', p = vertPos)
            cmds.select(cl = True)
            cmds.parent ( baseCntJnt, "eyebrowJnt_grp")
        else:
    
            baseJnt = cmds.joint(n = 'l_browBase' + str(index).zfill(2)+'_jnt', p = browRotXPos )
            ryJnt = cmds.joint(n = 'l_browRotY' + str(index).zfill(2)+ '_jnt', p = browRotYPos ) 
            parentJnt = cmds.joint(n = 'l_browP' + str(index).zfill(2)+ '_jnt', p = vertPos)
            cmds.setAttr ( baseJnt+'.rotateOrder', 2)
            cmds.joint(n = 'l_brow' + str(index).zfill(2) + '_jnt', p = vertPos)
            cmds.select(cl = True)
            cmds.parent ( baseJnt, "eyebrowJnt_grp")
           
            cmds.mirrorJoint ( baseJnt, mirrorYZ= True, mirrorBehavior=1, searchReplace=('l', 'r'))
            cmds.select(cl = True)
            index = index + 1
            





#create browDetail Controller (miNum = number of lidJoints )    
'''control parent name should be "browDetailCtrl0" and have the scale value ( 1, 1, 1) '''
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
        increment = 5.0/(jntNum-1)
        cmds.parent (detailCtl[0], detailPlane[0], relative=True )
        cmds.parent (detailPlane[0], ctlP, relative=True )
        cmds.setAttr (detailPlane[0] + '.tx', -3 + increment*index )
        cmds.xform ( detailCtl[0], r =True, s = (0.2, 0.2, 0.2))  
        cmds.setAttr (detailCtl[0] +".overrideEnabled", 1)
        cmds.setAttr (detailCtl[0] +"Shape.overrideEnabled", 1)
        cmds.setAttr( detailCtl[0]+"Shape.overrideColor", 20)        
        
        cmds.transformLimits ( detailCtl[0] , tx = ( -.4, .4), etx=( True, True) )
        cmds.transformLimits ( detailCtl[0], ty = ( -.8, .8), ety=( True, True) )
        
        for att in attTemp:
            cmds.setAttr (detailCtl[0] +"."+ att, lock = True, keyable = False, channelBox =False)
                
        index = index + 1





import re
import maya.cmds as cmds
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
		attachCtlGrp = cmds.group ( n = "attachCtl_grp", em =True, p = "faceMainRig|spn|headSkel|bodyHeadTRSP|bodyHeadTRS|" )
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
    if "r_" in jnt:
        cmds.connectAttr ( 'browReverse_mult.outputY', jntMult+'.input2X')

    else:
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



'''#10/19 2017 - option for seperating brow Up/Down with condition node "browScale_Cond")
#7/05/2016 - add browFactor.browRotateYScale/browRotateXScale
#Function for connecting brow Curve and controller to the brow Joints
def XbrowCrvCtlToJnt (browCtrl, browDetail, jnt, rotYJnt, ctlBase, rotYCtl, shapePOC, POC, initialX, index ):     
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
   if "r_" in rotYJnt:
     cmds.connectAttr ( 'browReverse_mult.outputY', jntMult+'.input2X')
   else:
     cmds.connectAttr ( 'browFactor.browRotateY_scale', jntMult+'.input2X')
  
   cmds.connectAttr ( jntMult+'.outputX', rotYJnt + '.ry' ) 
  
   #brow TY sum 
   #1. POC.ty sum
   cmds.connectAttr ( POC + '.positionY', browXYZSum +'.input3D[0].input3Dy')
   cmds.connectAttr ( shapePOC + '.positionY', browXYZSum + '.input3D[1].input3Dy')
   #2. detail ctl.ty sum
   cmds.connectAttr ( browDetail + '.ty', browXYZSum + '.input3D[2].input3Dy')
   #add browCtl.ty
   browCond = cmds.shadingNode( "condition", asUtility=1, n = "browScale_Cond")
   cmds.connectAttr ( browXYZSum + '.output3Dy', addBrowCtl + '.input3D[0].input3Dy')
   cmds.connectAttr ( browCtrl + '.ty', addBrowCtl + '.input3D[1].input3Dy')     
   cmds.connectAttr(  addBrowCtl + ".output3Dy", browCond + ".firstTerm" )
   cmds.setAttr ( browCond + ".secondTerm", 0 )
   cmds.setAttr( browCond + ".operation", 2 ) #greater than
   cmds.setAttr ( browCond + ".colorIfTrueG", 0 )
   cmds.connectAttr( 'browReverse_mult.outputX', browCond+".colorIfTrueR" )
   cmds.connectAttr( 'browReverse_mult.outputZ', browCond+".colorIfFalseR" )
   cmds.connectAttr( 'browReverse_mult.outputZ', browCond+".colorIfFalseG" )
  
   cmds.connectAttr( addBrowCtl + ".output3Dy", jntMult + ".input1Y" )
   cmds.connectAttr( addBrowCtl + ".output3Dy", jntMult + ".input1Z" )
   cmds.connectAttr( browCond+".outColorR", jntMult + ".input2Y" )
   cmds.connectAttr( browCond+".outColorG", jntMult + ".input2Z" )
   cmds.connectAttr ( jntMult+'.outputY',  jnt + '.rx' )
   #browXYZSum.ty --> ctrlMult.rx
   cmds.connectAttr ( browXYZSum + '.output3Dy', ctrlMult+'.input1Y')
   cmds.connectAttr ( 'browReverse_mult.outputZ', ctrlMult +'.input2Y')
   cmds.connectAttr ( ctrlMult+'.outputY', ctlBase + '.rx' )
  
   #brow TZ sum
   browPCtl =cmds.listRelatives( cmds.listRelatives (rotYCtl, c =1, type = 'transform')[0], c =1, type = 'transform')
   browPJnt = cmds.listRelatives ( rotYJnt, c =1, type = 'joint')
   browJnt = cmds.listRelatives ( browPJnt[0], c =1, type = 'joint')
   cmds.connectAttr ( shapePOC + '.positionZ', browXYZSum + '.input3D[0].input3Dz')
   cmds.connectAttr ( browXYZSum + '.output3Dz', browPCtl[0]+'.tz' )
  
   #addBrowCtl.tz --> browJnt[0] + ".tz"  
   cmds.connectAttr ( browXYZSum + '.output3Dz', addBrowCtl + '.input3D[0].input3Dz')
   cmds.connectAttr ( browCtrl + '.tz', addBrowCtl + '.input3D[1].input3Dz')
  
   #extra rotate ctrl for browJnt[0]
   cmds.connectAttr ( browCtrl + '.rx', browCtlRotSum + '.input3D[0].input3Dx')
   cmds.connectAttr ( browDetail + '.rx', browCtlRotSum + '.input3D[1].input3Dx')
   cmds.connectAttr ( browCtrl + '.ry', browCtlRotSum + '.input3D[0].input3Dy')
   cmds.connectAttr ( browDetail + '.ry', browCtlRotSum + '.input3D[1].input3Dy')
   cmds.connectAttr ( browCtrl + '.rz', browCtlRotSum + '.input3D[0].input3Dz')
   cmds.connectAttr ( browDetail + '.rz', browCtlRotSum + '.input3D[1].input3Dz')
   cmds.connectAttr ( browCtlRotSum + '.output3Dx', browJnt[0] + '.rx')
    
   if "r_" in browJnt[0]:
       invertMult = cmds.shadingNode ( 'multiplyDivide', asUtility=True, n = jnt.split('_j', 1)[0] +'invertMult'+ str(index) )
       cmds.connectAttr ( addBrowCtl + '.output3Dz', invertMult+".input1X" )
       cmds.setAttr(invertMult+".input2", -1,-1,-1 )
       cmds.connectAttr ( invertMult+".outputX", browJnt[0] + '.tz' )
       cmds.connectAttr ( browCtlRotSum + '.output3Dy', invertMult+".input1Y" )
       cmds.connectAttr ( invertMult+".outputY", browJnt[0] + '.ry')
       cmds.connectAttr ( browCtlRotSum + '.output3Dz', invertMult+".input1Z" )
       cmds.connectAttr ( invertMult+".outputZ",browJnt[0] + '.rz')       
      
   else:
       cmds.connectAttr ( addBrowCtl + '.output3Dz', browJnt[0] + '.tz' )
       cmds.connectAttr ( browCtlRotSum + '.output3Dy', browJnt[0] + '.ry')
       cmds.connectAttr ( browCtlRotSum + '.output3Dz', browJnt[0] + '.rz')'''







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
    	    bjMult = cmds.listConnections(bj, s=1, d=0, skipConversionNodes =1, type ="multiplyDivide" )
    	    browWide = cmds.duplicate( bj, po =1, n = bj.replace("Base","Wide") )
    	
    	    #cmds.connectAttr( bjMult + ".outputX", browWide[0]+".ry")
    	    cmds.connectAttr( bjMult[0] + ".outputZ", browWide[0]+".rx")
    	    #cmds.connectAttr ( 'browFactor.browDown_scale', bjMult[0]+'.input2Z')

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
        cmds.setAttr(j + '.otherType', str(i).zfill(2), type = "string")
    for id, k in enumerate(rightJnt):
        cmds.setAttr(k + '.side', 2)
        cmds.setAttr(k + '.type', 18)
        cmds.setAttr(k + '.otherType', str(id).zfill(2), type = "string") 






# 9/29/ 2017 seperate "browUp_cls", "browDn_cls" 
def faceClusters():
        
    #xmin ymin zmin xmax ymax zmax (face bounding box)
    facebbox = cmds.xform( "head_REN", q=1, boundingBox =1 )
    rad = facebbox[3]/20.0
    
    #faceCls ctl panel
    xMin = facebbox[0]
    yMin = facebbox[1]
    
    xMax = facebbox[3]
    yMax = facebbox[4]
    zDepth = (facebbox[5] + facebbox[2])/2 
    
    line = cmds.curve( d=1, p = [ ( xMin, yMin, zDepth ), ( xMin, yMax, zDepth), (xMax, yMax, zDepth), (xMax, yMin, zDepth), ( xMin, yMin, zDepth )] )
    cmds.rename( line, "faceClsFrame" )
    cmds.parent( "faceClsFrame", "faceLoc_grp" )    

    upLip = cmds.xform('lipNPos', q=1, t=1, ws =1 )
    loLip = cmds.xform('lipSPos', q=1, t=1, ws =1 )
    lipRollPos = [ 0, (upLip[1]+loLip[1])/2, upLip[2] ]
    lipRollLoc = cmds.spaceLocator(n='lipRollPos')
    cmds.parent(lipRollLoc, 'allPos')
    cmds.xform ( lipRollLoc, ws=1, t= lipRollPos )    
    
    #temporaly hide face joints for
    clusterDict = { 'jawRigPos': ['jawOpen_cls', 'jawClose_cls' ], 'lipYPos':'lip_cls', 'lipRollPos':'lipRoll_cls', 'cheekPos':['l_cheek_cls','r_cheek_cls'], 
    'lEyePos':['eyeBlink_cls', 'eyeWide_cls'], 'lowCheekPos': ['l_lowCheek_cls', 'r_lowCheek_cls'], 'squintPuffPos':['l_squintPuff_cls', 'r_squintPuff_cls'], 
    'lEarPos':['l_ear_cls','r_ear_cls'], 'rotXPivot':['browUp_cls','browDn_cls'], 'rotYPivot':'browTZ_cls', 'nosePos': 'nose_cls' }
    
    locators = cmds.listRelatives('allPos', ad =1, type = 'transform' )
    for k in clusterDict.keys():
        if not k in locators:
            print "there is a faceLocators naming problem"   
    
    cls = cmds.cluster( 'head_REN', n= 'mouth_cls', bindState =1, wn = ( 'lipZPos', 'lipZPos') )
    cmds.select('head_REN', r=1)
    cmds.percent( cls[0], v=0.0 )
    
    null = cmds.group( em =1, name = "midCtl_grp", parent='attachCtl_grp' )

    for pos, clsName in clusterDict.items():
        ctlPos = cmds.xform ( pos, q= 1, ws =1 , t=1 )
        distance = facebbox[5]- ctlPos[2]
        tranZ = (facebbox[5]-facebbox[2])/20
        index =4
        if len(clsName) == 2:
            #clusters to be included for face rig
            if pos in [ 'lowCheekPos', 'cheekPos', 'squintPuffPos' ]:
                mirrPos = [ -ctlPos[0], ctlPos[1], ctlPos[2]]
                mirrLoc = cmds.spaceLocator(  n= pos.replace("Pos","Mirr") )
                cmds.parent(mirrLoc, 'allPos')
                cmds.xform ( mirrLoc, ws=1, t= mirrPos )
                offsetOnFace = [ 0,0,tranZ ]
             
                lCtlJnt = clusterOnJoint( pos, clsName[0], "midCtl_grp", offsetOnFace, rad, 8 )
                rCtlJnt = clusterOnJoint( mirrLoc, clsName[1], "midCtl_grp", offsetOnFace, rad, 8 )               

                for at in [ "t","r","s"]:
                    cmds.connectAttr( lCtlJnt[0] + "." + at, lCtlJnt[1] + "."+ at ) 
                    cmds.connectAttr( rCtlJnt[0] + "." + at, rCtlJnt[1] + "."+ at )                            
                
            elif pos == "lEarPos":
                mirrPos = [ -ctlPos[0], ctlPos[1], ctlPos[2]]
                mirrLoc = cmds.spaceLocator(  n= pos.replace("Pos","Mirr") )
                cmds.parent(mirrLoc, 'allPos')
                cmds.xform ( mirrLoc, ws=1, t= mirrPos )
                lOffset = [ tranZ, 0,0 ]
                rOffset = [ -tranZ, 0,0 ]
             
                lCtlJnt = clusterOnJoint( pos, clsName[0], "midCtl_grp", lOffset, rad, 8 )
                rCtlJnt = clusterOnJoint( mirrLoc, clsName[1], "midCtl_grp", rOffset, rad, 8 )               

                for at in [ "t","r","s"]:
                    cmds.connectAttr( lCtlJnt[0] + "." + at, lCtlJnt[1] + "."+ at ) 
                    cmds.connectAttr( rCtlJnt[0] + "." + at, rCtlJnt[1] + "."+ at )
                    
            elif pos == "rotXPivot": #browUD_cls
            	print "shit is :%s, %s "%(clsName[0], clsName[1]) 
            	ctlUpJnt = clusterForSkinWeight( pos, zDepth, clsName[0], "faceClsFrame", rad*2, 4 )
            	tranToRot_mult( ctlUpJnt, 10 )
            	ctlDnJnt = clusterForSkinWeight( pos, zDepth, clsName[1], "faceClsFrame", rad*3, 6 )
            	tranToRot_mult( ctlDnJnt, 10 )
                
            else:
                #print clsName
                for cls in clsName: #'jawOpen_cls', 'jawClose_cls' 'eyeBlink_cls', 'eyeWide_cls'
                	print "the rest:" + cls
                	ctlJnt =  clusterForSkinWeight( pos, zDepth, cls, "faceClsFrame", rad*index, 4 )
                	tranToRot_mult( ctlJnt, 30 )
                	index-=1             
      
        else:

            if pos == 'lipYPos': #'lip_cls'

                ctlJnt = clusterForSkinWeight( pos, zDepth, clsName, "faceClsFrame", rad*2, 4 )
                tranToRot_mult( ctlJnt, 10 )
         
            elif pos =='rotYPivot': #'browTZ_cls'

                ctlJnt = clusterForSkinWeight( pos, zDepth, clsName, "faceClsFrame", rad, 8 )                
                for at in [ "t","r","s"]:
                    cmds.connectAttr( ctlJnt[0] + "." + at, ctlJnt[1] + "."+ at )
                cmds.setAttr( cmds.listRelatives(ctlJnt[0], p=1, type='transform')[0] + '.tx', 0 )
            
            elif pos =='nosePos' : # 'nose_cls'
                offset = [ 0,0, distance*1.2 ]
                ctlJnt = clusterOnJoint( pos, clsName, "midCtl_grp", offset, rad, 8 )                
                for at in [ "t","r","s"]:
                    cmds.connectAttr( ctlJnt[0] + "." + at, ctlJnt[1] + "."+ at )
            else:
                print "the single cls: "+ clsName
                ctlJnt = clusterForSkinWeight( pos, zDepth, clsName, "faceClsFrame", rad, 8 )                
                for att in [ "t","r","s"]:
                    cmds.connectAttr( ctlJnt[0] + "." + att, ctlJnt[1] + "."+ att ) 
    
    cmds.setAttr( "faceClsFrame.tx", xMax*2 )




#create joint for cluster and ctrl
#place ctlP for easy grab ( "faceLoc_grp| "faceClsFrame" or "attachCtl_grp"|"midCtl_grp" )
def clusterForSkinWeight( pos, zDepth, clsName, ctlP, rad, sect ):       
     
    clsPos = cmds.xform ( pos, q= 1, ws =1 , t=1 )
    ctl = cmds.circle( d =1, n = clsName.replace( 'cls', 'ctl') )
    cmds.parent( ctl[0], ctlP )
    cmds.xform( ctl[0], ws =1, t= (clsPos[0], clsPos[1], zDepth) )
    null = cmds.duplicate( ctl[0], po=1, n = clsName.replace( 'cls', 'ctlP') )
    cmds.setAttr (ctl[0] +".overrideEnabled", 1)
    cmds.setAttr( ctl[0] +".overrideColor", 4)  
    cmds.parent( ctl[0], null[0] )
    cmds.setAttr ( ctl[1] + '.radius', rad )
    cmds.setAttr ( ctl[1] + '.sections', sect )
    cmds.select(cl=1)
    #create joint for cluster
    clsP = cmds.group( n= clsName.replace("cls","clsP"), em=1, p = "faceMain|cls_grp" )
    cmds.xform(clsP,  ws=1, t = clsPos )
    jnt = cmds.joint( radius = 1, name= clsName + 'Handle' )     
    clsNode = cmds.cluster( 'head_REN', n= clsName, bindState =1, wn = ( jnt, jnt))
    cmds.select('head_REN', r=1)
    cmds.percent( clsNode[0], v=0.0 )
    return [ctl[0], jnt]

#setup for cluster ctrl to control cluster rotation( jawOpen, jawClose, lip...)
def tranToRot_mult( ctlJnt, ratio ):
    
    maskClsMult = cmds.shadingNode('multiplyDivide', asUtility =1, n = 'tranToRot_mult' )
    cmds.connectAttr( ctlJnt[0] + '.tx', maskClsMult + '.input1X')
    cmds.setAttr (maskClsMult + '.input2X', ratio )
    cmds.connectAttr( maskClsMult + '.outputX', ctlJnt[1] + '.ry')

    cmds.connectAttr( ctlJnt[0] + '.ty', maskClsMult + '.input1Y')
    cmds.setAttr (maskClsMult + '.input2Y', -ratio )
    cmds.connectAttr( maskClsMult + '.outputY', ctlJnt[1] + '.rx')
    
    cmds.connectAttr( ctlJnt[0] + '.tz', maskClsMult + '.input1Z')
    cmds.setAttr (maskClsMult + '.input2Z', 1 )
    cmds.connectAttr( maskClsMult + '.outputZ', ctlJnt[1] + '.tz')
    
    cmds.connectAttr( ctlJnt[0]+'.sx', ctlJnt[1]+'.sx')
    cmds.connectAttr( ctlJnt[0]+'.sy', ctlJnt[1]+'.sy')
    cmds.connectAttr( ctlJnt[0]+'.sz', ctlJnt[1]+'.sz')
                
                
                
                
                
                
#create joint for cluster and ctrl
#place ctlP for easy grab ( "faceLoc_grp"|"faceClsFrame" or "attachCtl_grp"|"midCtl_grp" )
def clusterOnJoint( pos, clsName, ctlP, offset, rad, sect ):         
     
    clsPos = cmds.xform ( pos, q= 1, ws =1 , t=1 )
    ctl = cmds.circle( d =1, n = clsName.replace( 'cls', 'onCtl') )
    null = cmds.duplicate( ctl[0], po=1, n = clsName.replace( 'cls', 'ctlP') )
    cmds.parent( ctl[0], null[0] )
    clsGrp = cmds.group( null[0], n = clsName.replace( 'cls', 'ctlGrp') )
    cmds.parent( clsGrp, ctlP ) 
    cmds.xform( clsGrp, ws =1, t= clsPos )
    cmds.setAttr (ctl[0] +".overrideEnabled", 1)
    cmds.setAttr( ctl[0] +".overrideColor", 4)  
    
    cmds.setAttr( null[0]+".t", offset[0], offset[1], offset[2] )
    cmds.setAttr ( ctl[1] + '.radius', rad )
    cmds.setAttr ( ctl[1] + '.sections', sect )
    cmds.select(cl=1)
    #create joint for cluster
    clsP = cmds.group( n= clsName.replace("cls","clsP"), em=1, p = "faceMain|cls_grp" )
    cmds.xform(clsP,  ws=1, t = clsPos )
    jnt = cmds.joint( radius = 1, name= clsName + 'Handle' )     
    clsNode = cmds.cluster( 'head_REN', n= clsName, bindState =1, wn = ( jnt, jnt))
    cmds.select('head_REN', r=1)
    cmds.percent( clsNode[0], v=0.0 )
    return [ctl[0], jnt]


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
