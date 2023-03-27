#create brow controllers and browCurve
'''
select base joints and run the script 
12/15/2015 change browCrv degree 1
not working : check if the brow ctl crv exists / number of detail ctls
number of brow crv CVs = 7  /  main controller (arc ABC...) = 5   
'''
import maya.cmds as cmds
def connectBrowCtrls ( size, offset, RotateScale ):
    
    jnts = cmds.ls ( os = True, fl = True, type ='joint') 
    jntNum = len(jnts)
    jnts.sort()
    z = [ jnts[0] ]
    y = jnts[1:jntNum/2+1]
    jnts.reverse()
    x = jnts[:jntNum/2]
    orderJnts = x + z + y 
    
    if not cmds.objExists("browCrv_grp"):
        browCrvGrp = cmds.group ( n = "browCrv_grp", em =True, p = "faceMain|crv_grp" ) 
        
    attachCtlGrp = cmds.group ( n = "attachCtl_grp", em =True, p = "faceMain|spn|headSkel|bodyHeadTRSP|bodyHeadTRS|" ) 
    browCtlGrp = cmds.group ( n = "browCtl_grp", em =True, p = "faceMain|spn|headSkel|bodyHeadTRSP|bodyHeadTRS|attachCtl_grp" ) 
    
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
    
    browDMom = cmds.ls ( 'browDetail*P', fl =True, type = "transform")
    browDetails = cmds.listRelatives ( browDMom, c=True, type = "transform") 
    index = 0 
    for jnt in orderJnts:
        
        childJnt = cmds.listRelatives ( jnt, c=True) 
        jntPos = cmds.xform(childJnt[0], t = True, q = True, ws = True) 
        madPOC = cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = 'browMadPOC'+ str(index))
        cmds.connectAttr ( browCrvShape[0] + ".worldSpace",  madPOC + '.inputCurve')
        cmds.setAttr ( madPOC + '.turnOnPercentage', 1 )
        increment = 1.0/(jntNum-1)        
        cmds.setAttr ( madPOC + '.parameter', increment *index ) 
        initialMadX = cmds.getAttr (madPOC + '.positionX')

        POC = cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = 'eyeBrowPOC'+ str(index))
        cmds.connectAttr ( browCtlCrvShape[0] + ".worldSpace",  POC + '.inputCurve')
        cmds.setAttr ( POC + '.turnOnPercentage', 1 )
        increment = 1.0/(jntNum-1)        
        cmds.setAttr ( POC + '.parameter', increment *index )
        #browCrv controls browDetail parent 
        cmds.connectAttr ( POC + ".positionY", browDMom[index] + ".ty"  )
        
        initialX = cmds.getAttr (POC + '.positionX')
        attrs = ["sx","sy","sz","v"]        
       
        if jnt in x :
            
            browDetail = browDetails[index]
            basePos = cmds.xform( jnt, t = True, q = True, ws = True)
            rBrowCtrl = circleCtrl( 'r_brow'+ jnt.split('browBaseJnt', 1)[1]+ "_ctl", ( jntPos[0], jntPos[1], jntPos[2]+ offset), size )
            null = cmds.listRelatives ( rBrowCtrl, p = 1, type = "transform" ) 
            ctlGrp = cmds.group( em =1, n = null[0].replace("P","_grp"), p = browCtlGrp) 
            cmds.xform (ctlGrp, ws = True, t = basePos )
            cmds.parent(null[0], ctlGrp)
            for att in attrs:            
                cmds.setAttr ( rBrowCtrl + ".%s"%att, lock =1, keyable = 0)
            browCrvCtlToJnt  (rBrowCtrl, browDetail, jnt, ctlGrp, madPOC, POC, initialMadX, initialX, RotateScale, index )
            
        elif jnt in y :
            browDetail = browDetails[index]
            basePos = cmds.xform( jnt, t = True, q = True, ws = True)
            lBrowCtrl = circleCtrl( 'l_brow'+ jnt.split('browBaseJnt', 1)[1]+ "_ctl", ( jntPos[0], jntPos[1], jntPos[2]+ offset), size ) 
            null = cmds.listRelatives ( lBrowCtrl, p = 1, type = "transform" ) 
            ctlGrp = cmds.group( em =1, n = null[0].replace("P","_grp"), p = browCtlGrp) 
            cmds.xform (ctlGrp, ws = True, t = basePos )
            cmds.parent(null[0], ctlGrp)
            for att in attrs:            
                cmds.setAttr ( lBrowCtrl + ".%s"%att, lock =1, keyable = 0)
            browCrvCtlToJnt (lBrowCtrl, browDetail, jnt, ctlGrp, madPOC, POC, initialMadX, initialX, RotateScale, index  )
            
        elif jnt == z[0] :
            browDetail = browDetails[index] 
            basePos = cmds.xform( jnt, t = True, q = True, ws = True)            
            centerBrowCtrl = circleCtrl( 'c_brow'+ jnt.split('browBaseJnt', 1)[1]+ "_ctl", ( jntPos[0], jntPos[1], jntPos[2]+ offset), size )
            null = cmds.listRelatives ( centerBrowCtrl, p = 1, type = "transform" )
            ctlGrp = cmds.group( em =1, n = null[0].replace("P","_grp"), p = browCtlGrp) 
            cmds.xform (ctlGrp, ws = True, t = basePos )
            cmds.parent(null[0], ctlGrp)
            for att in attrs:            
                cmds.setAttr ( centerBrowCtrl + ".%s"%att, lock =1, keyable = 0)
            browCrvCtlToJnt ( centerBrowCtrl, browDetail, jnt, ctlGrp, madPOC, POC, initialMadX, initialX, RotateScale, index )
            
        index = index + 1

#connectBrowCtrls ( .2, .2, 10 )