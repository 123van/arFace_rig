#create eyeLid controller in panel ( lidJntsLen = number of lidJoints )    
import maya.cmds as cmds
def lidDetailCtl():
    if not cmds.objExists ('eyeLidCrv_grp'):
        eyeLidCrvGrp = cmds.group (em =1, n = 'eyeLidCrv_grp', p = 'faceMainRig|crv_grp' ) 
    #delete existing curves
    if cmds.objExists( '*Ctl_crv*') :
        cmds.delete ( '*Ctl_crv*')
    elif cmds.objExists( '*CornerCrv*'):
        cmds.delete ( '*CornerCrv*')
         
    LRUpLow = ['l_up','r_up', 'l_lo', 'r_lo' ]
    for updn in LRUpLow:
             
        ctlP = updn + "Ctrl0"
        kids = cmds.listRelatives (ctlP, ad=True, type ='transform')   
        if kids:
            cmds.delete (kids)
        lidJnts = cmds.ls( updn + "LidBlink*_jnt", type = 'joint')
        lidJntsLen = len(lidJnts)
        print lidJntsLen
             
        cntPos = cmds.xform (ctlP, q=1, ws =1, t = 1 )
        cntCtl = controller( updn + "Center", cntPos, 0.1, "cc" )
        cntCtlP = cntCtl[1]
        cmds.parent(cntCtlP, ctlP)
     
        inCorner = controller( updn + "InCorner", cntPos, 0.1, "cc" )
        inCornerP = inCorner[1]
        cmds.parent( inCornerP, ctlP)
        cmds.setAttr (inCornerP +'.tx', -1 )
         
        outCorner = controller( updn + "OutCorner", cntPos, 0.1, "cc" )
        outCornerP = outCorner[1] 
        cmds.parent( outCornerP, ctlP)    
        cmds.setAttr (outCornerP +'.tx', 1 )
             
        attTemp = ['scaleX','scaleY','scaleZ', 'rotateX','rotateY','rotateZ', 'tz', 'visibility' ]  
        for x in attTemp:
            cmds.setAttr (cntCtl[0] +"."+ x, lock = True, keyable = False, channelBox =False)
            cmds.setAttr (inCorner[0] +"."+ x, lock = True, keyable = False, channelBox =False ) 
            cmds.setAttr (outCorner[0]+"."+ x, lock = True, keyable = False, channelBox =False ) 
        
        details = []
        for i in range(1, lidJntsLen+1):
     
            detailCtl = controller( updn + 'Detail'+ str(i).zfill(2), [0,0,0], 0.06, "sq" )
            details.append(detailCtl[0])
            detailCtlP = detailCtl[1]
            cmds.parent (detailCtlP, ctlP )
            increment = 2.0 /(lidJntsLen+1)
            cmds.setAttr (detailCtlP + ".tx", increment*i - 1.0 )
            cmds.setAttr (detailCtlP + ".ty", 0 )
            cmds.setAttr (detailCtlP + ".tz", 0 )
            #cmds.xform ( detailCtl, r =True, s = (0.1, 0.1, 0.1))
            for y in attTemp:
                cmds.setAttr (detailCtl[0] +"."+ y, lock = True, keyable = False, channelBox =False)    
        
        #eyelids controller curve shape ( different number of points )         
        tempCtlCrv = cmds.curve ( d = 3, p =([0,0,0],[0.33,0,0],[0.66,0,0],[1,0,0])) 
        cmds.rebuildCurve (tempCtlCrv, rt = 0, d = 3, kr = 0, s = 2 )   
        lidCtlCrv = cmds.rename (tempCtlCrv, updn +'Ctl_crv')
        cmds.parent (lidCtlCrv, 'eyeLidCrv_grp') 
        ctlCrvCv = cmds.ls ( lidCtlCrv + '.cv[*]', fl =True )#!!check same curve exist if Error : list index out of range
                
        ##corner twist curves setup (curves for corner Adjust 06/23/2016)
        cornerCrv = cmds.duplicate (lidCtlCrv, n = updn +'CornerCrv' )
        cornerCrvCv = cmds.ls ( cornerCrv[0] + '.cv[*]', fl =True )
        if '_up' in updn:
            inCls = cmds.cluster (cornerCrvCv[0:2], n = updn[:2] +'inTwistCls')
            cmds.percent (inCls[0], cornerCrvCv[1],  v = 0.3 )    
            outCls = cmds.cluster (cornerCrvCv[3:5], n = updn[:2] +'outTwistCls')
            cmds.percent (outCls[0], cornerCrvCv[3], v = 0.3 ) 
    
        elif '_lo' in updn:
            cmds.sets( cornerCrvCv[0:2], add= updn[:2] +'inTwistClsSet' )
            cmds.percent ( updn[:2] +'inTwistCls', cornerCrvCv[1],  v = 0.3 ) 
            cmds.sets( cornerCrvCv[3:5], add= updn[:2] +'outTwistClsSet' )
            cmds.percent ( updn[:2] +'outTwistCls', cornerCrvCv[3],  v = 0.3 )
            #corner twist setup (no need to use ClsHandle.rotateZ )
            cmds.connectAttr ( updn[:2] + "innerLidTwist.tx" , updn[:2] +'inTwistClsHandle.tx' )
            cmds.connectAttr ( updn[:2] + "innerLidTwist.ty" , updn[:2] +'inTwistClsHandle.ty' )
            
            cmds.connectAttr ( updn[:2] + "outerLidTwist.tx" , updn[:2] +'outTwistClsHandle.tx' )
            cmds.connectAttr ( updn[:2] + "outerLidTwist.ty" , updn[:2] +'outTwistClsHandle.ty' )
             
        # lidCtl drive the center controlPoints on ctlCrv
        if not ( cmds.objExists(updn + "Center") and cmds.objExists(updn +"InCorner") and cmds.objExists(updn + "OutCorner")):
            print "create lid main controllers"
        else :
            #corner ctls setup                    
            cmds.connectAttr ( updn + "InCorner.ty" , ctlCrvCv[0] + ".yValue" )
            cmds.connectAttr ( updn + "InCorner.ty" , ctlCrvCv[1] + ".yValue" )
            cmds.setAttr ( ctlCrvCv[0] + ".xValue" , lock = True )     
            cmds.setAttr ( ctlCrvCv[1] + ".xValue" , lock = True ) 

            cmds.connectAttr ( updn + "OutCorner.ty" , ctlCrvCv[3] + ".yValue" )
            cmds.connectAttr ( updn + "OutCorner.ty" , ctlCrvCv[4] + ".yValue" )
            cmds.setAttr ( ctlCrvCv[3] + ".xValue", lock = True  )  
            cmds.setAttr ( ctlCrvCv[4] + ".xValue", lock = True  )
                                 
            cntAddD = cmds.shadingNode ( 'addDoubleLinear', asUtility=True, n= updn + "Cnt_AddD" )    
            if "l_" in updn :
                # center ctrl.tx drives center point (lidCtl_crv) 
                lCntMult = cmds.shadingNode ( 'multiplyDivide', asUtility=True, n = updn +'Cnt_mult' ) 
                cmds.connectAttr ( updn + "Center.tx", cntAddD + ".input1" )
                cmds.setAttr (cntAddD + ".input2", 0.5 ) 
                cmds.connectAttr ( cntAddD + ".output" , ctlCrvCv[2] + ".xValue" )
                #center ctrl.ty drives ctlCrv center cv[2].yValue
                cmds.connectAttr ( updn + "Center.ty" , lCntMult + ".input1Y" )
                cmds.setAttr (lCntMult + ".input2Y", 2 ) 
                cmds.connectAttr ( lCntMult + ".outputY", ctlCrvCv[2] + ".yValue" )                
                
            if "r_" in updn :
                #center ctrl.tx drives ctlCrv center cv[2].xValue 
                rCntMult = cmds.shadingNode ( 'multiplyDivide', asUtility=True, n = updn +'Cnt_mult' )
                cmds.connectAttr ( updn + "Center.tx" , rCntMult + ".input1X" ) 
                cmds.setAttr ( rCntMult + ".input2X", -1 )
                cmds.connectAttr ( rCntMult + ".outputX", cntAddD + ".input1" )
                cmds.setAttr (cntAddD + ".input2", 0.5 ) 
                cmds.connectAttr ( cntAddD + ".output" , ctlCrvCv[2] + ".xValue" )            
                #center ctrl.ty drives ctlCrv center cv[2].yValue 
                cmds.connectAttr ( updn + "Center.ty" , rCntMult + ".input1Y" )
                cmds.setAttr (rCntMult + ".input2Y", 2 ) 
                cmds.connectAttr ( rCntMult + ".outputY", ctlCrvCv[2] + ".yValue" ) 
        
        detailPCtls = cmds.ls ( updn + "Detail*P", type = 'transform')
        incrementYPoc = 1.0/(lidJntsLen +1)
        incrementXPoc = 1.0/(lidJntsLen -1)    
        for i in range (1, lidJntsLen+1):
            
            #POC for positionX on the eyelids ctl curve 
            ctlXPOC = cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = updn + 'CtlXPoc' + str(i).zfill(2)) 
            cmds.connectAttr ( updn + "Ctl_crvShape.worldSpace", ctlXPOC + '.inputCurve')   
            cmds.setAttr ( ctlXPOC + '.turnOnPercentage', 1 )        
            cmds.setAttr ( ctlXPOC + '.parameter', incrementXPoc *(i-1) )
            
            #POC for positionY on the eyelids ctl curve
            ctlYPOC = cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = updn + 'CtlYPoc' + str(i).zfill(2)) 
            cmds.connectAttr ( updn + "Ctl_crvShape.worldSpace", ctlYPOC + '.inputCurve')   
            cmds.setAttr ( ctlYPOC + '.turnOnPercentage', 1 )        
            cmds.setAttr ( ctlYPOC + '.parameter', incrementYPoc *i )
            
            # POC on ctlCrv drive detail control parent  
            cntRemoveX = cmds.shadingNode ( 'addDoubleLinear', asUtility=True, n= updn +"RemoveX"+ str(i).zfill(2) )
            momMult = cmds.shadingNode ( 'multiplyDivide', asUtility=True, n = updn +'Mom'+ str(i).zfill(2)+'_mult')
            cmds.connectAttr ( ctlYPOC +".positionY", detailPCtls[i-1] + ".ty" )
            
            #Xvalue match between POC and CtrlP ( detailPCtls[i] = 2*ctlPoc -1 )
            cmds.connectAttr ( ctlXPOC +".positionX", momMult + ".input1X" )
            cmds.setAttr ( momMult + ".input2X", 2 )        
            cmds.connectAttr ( momMult + ".outputX", cntRemoveX + ".input1" )            
            cmds.setAttr (  cntRemoveX  + ".input2", -1 ) 
            cmds.connectAttr ( cntRemoveX +".output", detailPCtls[i-1] + ".tx" )
            
            #curves for corner Adjust 06/23/2016
            cornerPOC = cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = updn + 'CornerPoc' + str(i).zfill(2)) 
            cmds.connectAttr ( updn +"CornerCrv.worldSpace", cornerPOC + '.inputCurve' )   
            cmds.setAttr ( cornerPOC + '.turnOnPercentage', 1 )        
            cmds.setAttr ( cornerPOC + '.parameter', incrementXPoc*(i-1) )           
  
     
#lidDetailCtl()