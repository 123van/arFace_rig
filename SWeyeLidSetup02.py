# -*- coding: utf-8 -*-

import re
import maya.cmds as cmds

'''
from swFace_setup import SWeyeLidSetup02
reload(SWeyeLidSetup02)
SWeyeLidSetup02.createEyeRig() :
눈리깅 자리깔기(create “l_eyeballRot” :driver of )

SWeyeLidSetup02.jumperPanel() : 
눈알 움직임에 따른 리드 푸쉬 셋업( Jump Panel.l_lidPushX/Y )
Connect  “l_eyeballRot”( /20 : lidFactor.eyeBallRotY_scale ) to Jump Panel.l_lidPushX/Y 

SWeyeLidSetup02.lidDetailCtl() : 컨트롤/코너 커브에 pointOnCurve 노드 달기
l_upCtl_crv / l_upCornerCrv 생성
Twitch panel 눈꺼플 디테일 컨트롤 갯수 fix

SWeyeLidSetup02.eyeLidsCrvs( 1 ) : 
눈꺼플 관련 쉐입(lidPush/ MinMax/ Squint Annoy) 생성( create pushMath,)
눈꺼플 컨트롤 on body

SWeyeLidSetup02.eyeCtl_EXP() : 
Connect twitchPanel ctrls to nodes 
blink/eyeballRot/squint/eyeTwist 컨트롤과 노드 연결 (create l/r_inner/outerCornerPoc )

SWeyeLidSetup02.eyeCrvToJnt() :
  
SWeyeLidSetup02.blinkRemap()

'''
def createEyeRig():
    if not ('lEyePos'):
        print "create the face locators"        
    else:         
        lEyePos = cmds.xform( 'lEyePos', t = True, q = True, ws = True)
     
    if not ('eyeRigP'):
        eyeRigP = cmds.group (em=True, n = 'eyeRigP', p= 'eyeRig' )      
 
    eyeRigTR = cmds.group (em=True, n = 'eyeRigTR', p= 'eyeRigP' ) 
    ffdSquachLattice = cmds.group (em =1, n = 'ffdSquachLattice', p = 'eyeRigP' )
    lEyeP = cmds.group (em=True, n = 'l_eyeP', p= eyeRigTR ) 
    cmds.xform ( lEyeP, ws =1, t = (lEyePos[0], lEyePos[1], lEyePos[2])) 
    lEyeRP = cmds.group (em=True, n = 'l_eyeRP', p= lEyeP )
    lEyeScl = cmds.group (em=True, n = 'l_eyeScl', p= lEyeRP )
    lEyeRot = cmds.group (em=True, n = 'l_eyeRot', p= lEyeScl )
    lEyeballRot = cmds.group (em=True, n = 'l_eyeballRot', p= lEyeRot )
 
     
    rEyeP = cmds.group (em=True, n = 'r_eyeP', p= eyeRigTR ) 
    cmds.xform ( rEyeP, ws =1, t = (-lEyePos[0], lEyePos[1], lEyePos[2])) 
    rEyeRP = cmds.group (em=True, n = 'r_eyeRP', p= rEyeP ) 
    rEyeScl = cmds.group (em=True, n = 'r_eyeScl', p= rEyeRP )
    rEyeRot = cmds.group (em=True, n = 'r_eyeRot', p= rEyeScl )
    rEyeballRot = cmds.group (em=True, n = 'r_eyeballRot', p= rEyeRot )




#upLowLR = ["l_up", "l_lo"]
def eyelidJoints ( upLowLR ): 
      
    if not ('lEyePos'):
        print "create the face locators"
          
    else:    
        eyeRotY = cmds.getAttr ('lEyePos.ry' )
        eyeRotZ = cmds.getAttr ('lEyePos.rz' ) 
        eyeCenterPos = cmds.xform( 'lEyePos', t = True, q = True, ws = True) 
      
    ordered = cmds.getAttr("lidFactor.%sLidVerts"%upLowLR[2:] )###replaced   
  
    # create parent group for eyelid joints
    if not cmds.objExists('eyeLidJnt_grp'):
        cmds.group ( n = 'eyeLidJnt_grp', em =True, p ="jnt_grp" ) 
                 
    null = cmds.group ( n = upLowLR+'EyeLidJnt_grp', em =True, p ="eyeLidJnt_grp" ) 
    cmds.xform (null, t = eyeCenterPos, ws =1 )
    cmds.select(cl = True) 
  
    #create eyeLids parent joint
    LidJntP = cmds.joint(n = upLowLR + 'LidP_jnt', p = eyeCenterPos) 
    #cmds.setAttr ( LidJntP + ".jointOrientY", 0)
    cmds.parent ( LidJntP, null )
    cmds.setAttr ( null + '.ry', eyeRotY ) 
    cmds.select(cl =1)
    #UI for 'null.rx/ry/rz'?? cmds.setAttr ( null + '.rz', eyeRotZ )    
    index = 1
    for v in ordered:
        vertPos = cmds.xform ( v, t = True, q = True, ws = True)             
        lidJnt = cmds.joint(n = upLowLR + 'Lid' + str(index).zfill(2) + '_jnt', p = vertPos ) 
        lidJntTX = cmds.joint(n = upLowLR + 'LidTX' + str(index).zfill(2) + '_jnt', p = vertPos )
        cmds.joint ( lidJnt, e =True, zso =True, oj = 'zyx', sao= 'yup')
        blinkJnt = cmds.duplicate ( lidJnt, po=True, n = upLowLR + 'LidBlink' + str(index).zfill(2)+'_jnt' )
        cmds.parent ( blinkJnt[0], LidJntP )
        cmds.setAttr ( blinkJnt[0] + '.tx' , 0 )
        cmds.setAttr ( blinkJnt[0] + '.ty' , 0 )  
        cmds.setAttr ( blinkJnt[0] + '.tz' , 0 ) 
        cmds.parent ( lidJnt, blinkJnt[0] )     
            
        wideJnt = cmds.duplicate ( blinkJnt, po=True, n = upLowLR + 'LidWide' + str(index).zfill(2) + '_jnt' )  
        scaleJnt = cmds.duplicate ( blinkJnt, po=True, n = upLowLR + 'LidScale' + str(index).zfill(2) + '_jnt' )
        cmds.parent ( blinkJnt, scaleJnt[0] )
        #cmds.joint ( scaleJnt[0], e =True, zso =True, oj = 'xyz', sao= 'yup')
        cmds.parent ( wideJnt[0], scaleJnt[0] )
  
        index = index + 1
      
    mirrorLowLR = ''
    if 'l_up' in upLowLR:
        mirrorLowLR = 'r_up'
    elif 'l_lo' in upLowLR:
        mirrorLowLR = 'r_lo'
     
    print eyeCenterPos    
    RNull = cmds.group ( n = mirrorLowLR +'EyeLidJnt_grp', em =True, p = "eyeLidJntP" ) 
    cmds.xform (RNull, t = (-eyeCenterPos[0], 0, 0) ) 
    cmds.setAttr ( RNull + '.ry', -eyeRotY ) 
    cmds.setAttr ( RNull + '.rz', -eyeRotZ )
    RLidJntP = cmds.mirrorJoint ( LidJntP, mirrorBehavior=True, myz = True, searchReplace = ('l_', 'r_'))
    cmds.parent ( RLidJntP[0], RNull ) 
    zeroAtts = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
    for i in zeroAtts:
        cmds.setAttr ( RLidJntP[0] + '.' + i, 0)





def eyeCornerJoints(): 
      
    if not ('lEyePos'):
        print "create the face locators"
          
    else:    
        eyeRotY = cmds.getAttr ('lEyePos.ry' )
        eyeRotZ = cmds.getAttr ('lEyePos.rz' ) 
        eyeCenterPos = cmds.xform( 'lEyePos', t = True, q = True, ws = True) 
      
    #reorder the vertices in selection list  
    vtxs =cmds.ls(sl=1 , fl=1)
    myList = {}
    for i in vtxs:        
        val = re.findall('\d+', i )
        xyz = cmds.getAttr ("head_REN.vrts[" +val[0]+"]")[0]
        myList[ i ] = xyz[0]
    ordered = sorted(myList, key = myList.__getitem__)    
    
    # create parent group for eyelid jointsw
    if not cmds.objExists('eyeLidJntP'):
        cmds.group ( n = 'eyeLidJntP', em =True, p ="eyeRig" ) 

    null = cmds.group ( n = 'l_eyeCorner_grp', em =True, p ="eyeLidJntP" ) 
    cmds.xform (null, t = eyeCenterPos, ws =1 )
    cmds.select(cl = True) 
      
    #create eyeLids parent joint
    LidJntP = cmds.joint(n = 'l_eyeCornerP_jnt', p = eyeCenterPos) 
    cmds.parent ( LidJntP, null )
    cmds.setAttr ( null + '.ry', eyeRotY ) 
    cmds.select(cl =1)    
    name = ['inner','outer']
    for v in range(0, len(ordered)): 
        vertPos = cmds.xform ( ordered[v], t = True, q = True, ws = True)             
        lidJnt = cmds.joint(n = 'l_' +name[v]+ '_jnt', p = vertPos ) 
        lidJntTX = cmds.joint(n = 'l_' +name[v]+ 'TX_jnt', p = vertPos )
        cmds.joint ( lidJnt, e =True, zso =True, oj = 'zyx', sao= 'yup')
        blinkJnt = cmds.duplicate ( lidJnt, po=True, n = 'l_'+name[v]+'Blink_jnt' )
        cmds.parent ( blinkJnt[0], LidJntP )
        cmds.setAttr ( blinkJnt[0] + '.tx' , 0 )
        cmds.setAttr ( blinkJnt[0] + '.ty' , 0 )  
        cmds.setAttr ( blinkJnt[0] + '.tz' , 0 ) 
        cmds.parent ( lidJnt, blinkJnt[0] )     
                
        wideJnt = cmds.duplicate ( blinkJnt, po=True, n = 'l_'+name[v]+'Wide_jnt' )  
        scaleJnt = cmds.duplicate ( blinkJnt, po=True, n = 'l_'+name[v]+'Scale_jnt' )
        cmds.parent ( blinkJnt, scaleJnt[0] )
        #cmds.joint ( scaleJnt[0], e =True, zso =True, oj = 'xyz', sao= 'yup')
        cmds.parent ( wideJnt[0], scaleJnt[0] )
  
    print eyeCenterPos    
    RNull = cmds.group ( n = 'r_eyeCorner_grp', em =True, p = "eyeLidJntP" ) 
    cmds.xform (RNull, t = (-eyeCenterPos[0], 0, 0) ) 
    cmds.setAttr ( RNull + '.ry', -eyeRotY ) 
    RLidJntP = cmds.mirrorJoint ( LidJntP, mirrorBehavior=True, myz = True, searchReplace = ('l_', 'r_'))
    cmds.parent ( RLidJntP[0], RNull ) 
    zeroAtts = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
    for i in zeroAtts:
        cmds.setAttr ( RLidJntP[0] + '.' + i, 0)







#eyelids expression 
def jumperPanel():
    if not cmds.objExists('jumperPanel'):
        #set the start with plusMinusAverage  
        cmds.group( n = "jumperPanel", em = 1, p = "faceMain" )   

    if not cmds.objExists('lids_EXP'):
        #set the start with plusMinusAverage  
        cmds.group( n = "lids_EXP", em = 1, p = "jumperPanel" )    
    upJnts = cmds.ls( "l_upLidBlink*_jnt", fl =1, type= "joint" )
    loJnts = cmds.ls( "l_loLidBlink*_jnt", fl =1, type= "joint" )
    upLen = len(upJnts)    
    loLen = len(loJnts)
    cmds.select ('lids_EXP') #lids_EXP: lid start/ end /open 
    #nodes for ValAB
    
    pushY_mult = cmds.shadingNode( 'multiplyDivide', asUtility =1, n ='lidPushY_mult')

    prefix = [ 'l_', 'r_' ]
    for LR in prefix:

        if 'l_' in LR:
            XYZ = 'X'

        if 'r_' in LR:
            XYZ = 'Y' 
         
        for i in range(0, max(upLen, loLen)): 
            #create each push_lid point in jumperPanel
            cmds.addAttr('jumperPanel', longName= LR + "upPush_Lid%s"%str(i), attributeType='float', dv = 0)
            cmds.addAttr('jumperPanel', longName= LR + "loPush_Lid%s"%str(i), attributeType='float', dv = 0)
            
            #Start = - .cv(LUpCrv.cv) -   +  push_Lid5 + ctrl.ty* *  .squint
            cmds.addAttr('lids_EXP', longName= LR + "upEyeStart%s"%str(i), attributeType='float', dv = 0)
            ##eyeOpenCrv shape ( start + blinkCtrl ) : upEyeStart0 -lids_EXP.l_upGap*l_eyeBlink.ty*(1-blinkLevel)
            cmds.addAttr('lids_EXP', longName= LR +"upEyeOpen%s"%str(i), attributeType='float', dv = 0)
            #blink target POC.positionY on the loEyeCrv
            cmds.addAttr('lids_EXP', longName= LR +"EyeEnd%s"%str(i), attributeType='float', dv = 0)
        
            cmds.addAttr('lids_EXP', longName= LR +"loEyeStart%s"%str(i), attributeType='float', dv = 0)
            cmds.addAttr('lids_EXP', longName= LR +"loEyeOpen%s"%str(i), attributeType='float', dv = 0)
             
        #Y = lookUp/Down  X = lookLeft/Right           
        cmds.addAttr('jumperPanel', longName= LR + "lidPushY", attributeType='float', dv = 0)                      
        cmds.addAttr('jumperPanel', longName= LR + "lidPushX", attributeType='float', dv = 0) 
        
        cmds.addAttr('jumperPanel', longName= LR + "valA", attributeType='float', dv = 0)
        cmds.addAttr('jumperPanel', longName= LR + "valB", attributeType='float', dv = 0)
        
        
        #make -JumperPanel.l_lidPushY into +
        cmds.connectAttr ( 'jumperPanel.' + LR + 'lidPushY', pushY_mult + '.input1'+XYZ)
        cmds.setAttr ( pushY_mult + '.input2'+XYZ, -1 )
        
        #ValA and ValB define by LidPushY clamp
        pushY_clamp = cmds.shadingNode( 'clamp', asUtility =1, n = LR + 'lidPushY_clamp')
        cmds.setAttr ( pushY_clamp + '.maxR', 1 )
        cmds.setAttr ( pushY_clamp + '.maxG', 1 )
        #ValAB / LidPushY defined by l_eyeballRotX 
        cmds.connectAttr ( 'jumperPanel.' + LR + 'lidPushY', pushY_clamp + '.inputR')
        cmds.connectAttr ( pushY_mult + '.output'+XYZ, pushY_clamp + '.inputG' )
        cmds.connectAttr (  pushY_clamp + '.outputR', 'jumperPanel.' + LR + 'valA') # l_valA = + lidPushY
        cmds.connectAttr (  pushY_clamp + '.outputG', 'jumperPanel.' + LR + 'valB')# l_valB = -(-lidPushY)        
        
        #l_eyeballRotX --> 'jumperPanel.l_lidPushY'
        
        eyeRotX_mult = cmds.shadingNode( 'multiplyDivide', asUtility =1, n = LR + 'eyeRotX_mult')
        rotX_invert = cmds.shadingNode( 'multiplyDivide', asUtility =1, n = LR + 'rotX_invert')
        cmds.connectAttr ( 'lidFactor.eyeBallRotX_scale', rotX_invert + '.input1X' )
        cmds.setAttr ( rotX_invert + '.input2X', -1)

        cmds.setAttr ( eyeRotX_mult + '.operation', 2)
        cmds.connectAttr ( LR + 'eyeballRot.rotateX', eyeRotX_mult + '.input1X')
        cmds.connectAttr ( rotX_invert + '.outputX', eyeRotX_mult + '.input2X' )
        
        eyeUD_mult = cmds.shadingNode( 'multiplyDivide', asUtility =1, n = LR + 'eyeUD_mult')
        cmds.connectAttr ( eyeRotX_mult + '.outputX', eyeUD_mult + '.input1X' )
        cmds.connectAttr ( eyeRotX_mult + '.outputX', eyeUD_mult + '.input1Y' )
        cmds.connectAttr ( 'lidFactor.range_'+LR+'eyeU', eyeUD_mult + '.input2X')
        cmds.connectAttr ( 'lidFactor.range_'+LR+'eyeD', eyeUD_mult + '.input2Y')
        
        pushY_con = cmds.shadingNode( 'condition', asUtility =1, n = LR + 'lidPushY_con')
        cmds.connectAttr ( LR + 'eyeballRot.rotateX', pushY_con+'.firstTerm' )
        cmds.setAttr ( pushY_con+".secondTerm", 0 )
        cmds.setAttr ( pushY_con+".operation", 4 )
        cmds.connectAttr ( eyeUD_mult + '.outputX', pushY_con+ '.colorIfTrueR' )
        cmds.connectAttr ( eyeUD_mult + '.outputY', pushY_con+ '.colorIfFalseR' )
        cmds.connectAttr ( pushY_con+ '.outColorR', 'jumperPanel.' +LR+ 'lidPushY' )
        
        #l_eyeballRotY --> 'jumperPanel.l_lidPushX'
        eyeRotY_mult = cmds.shadingNode( 'multiplyDivide', asUtility =1, n = LR + 'eyeRotY_mult')
        cmds.setAttr ( eyeRotY_mult + '.operation', 2)
        cmds.connectAttr ( 'lidFactor.eyeBallRotY_scale', eyeRotY_mult + '.input2X' )
        cmds.connectAttr ( 'lidFactor.eyeBallRotY_scale', eyeRotY_mult + '.input2Y' )
        cmds.connectAttr ( LR + 'eyeballRot.rotateY', eyeRotY_mult + '.input1X')
        cmds.connectAttr ( LR + 'eyeballRot.rotateY', eyeRotY_mult + '.input1Y')
        
        eyeLR_mult = cmds.shadingNode( 'multiplyDivide', asUtility =1, n = LR + 'eyeLR_mult')
        cmds.connectAttr ( eyeRotY_mult + '.outputX', eyeLR_mult + '.input1X' )
        cmds.connectAttr ( eyeRotY_mult + '.outputX', eyeLR_mult + '.input1Y' )
        cmds.connectAttr ( 'lidFactor.range_'+LR+'eyeR', eyeLR_mult + '.input2X')
        cmds.connectAttr ( 'lidFactor.range_'+LR+'eyeL', eyeLR_mult + '.input2Y')
        
        pushX_con = cmds.shadingNode( 'condition', asUtility =1, n = LR + 'lidPushX_con')
        cmds.connectAttr ( LR + 'eyeballRot.rotateY', pushX_con +'.firstTerm' )
        cmds.setAttr ( pushY_con+".secondTerm", 0 )
        cmds.setAttr ( pushY_con+".operation", 4 )
        cmds.connectAttr ( eyeLR_mult + '.outputX', pushX_con+ '.colorIfTrueG' )
        cmds.connectAttr ( eyeLR_mult + '.outputY', pushX_con+ '.colorIfFalseG' )
        cmds.connectAttr ( pushX_con+ '.outColorG', 'jumperPanel.' +LR+ 'lidPushX')  
        
        
'''
LUpCrvMP7.parameter = (LUpCtrlA.scaleX - 0.3) * 0.5714285714 + (1 - (LUpCtrlA.scaleX - 0.3)) / 2.0 - (LUpCtrlA.translateX / 4.0);
LUpCrvMP6.parameter = (LUpCtrlA.scaleX - 0.3) * 0.5 + (1 - (LUpCtrlA.scaleX - 0.3)) / 2.0 - (LUpCtrlA.translateX / 4.0);
'''        
def lidDetailCtl():
    if not cmds.objExists ('eyeLidCrv_grp'):
        eyeLidCrvGrp = cmds.group (em =1, n = 'eyeLidCrv_grp', p = 'faceMain|crv_grp' ) 
       
    LRUpLow = ['l_up','r_up', 'l_lo', 'r_lo' ]
    for updn in LRUpLow:
             
        ctlP = updn + "Ctrl0"
        kids = cmds.listRelatives (ctlP, ad=True, type ='transform')   
        if kids:
            cmds.delete (kids)
        lidJnts = cmds.ls( updn + "LidBlink*_jnt", type = 'joint')
        lidJntsLen = len(lidJnts)
             
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
        detailPs = []
        increment = 2.0 /(lidJntsLen+1)
        for i in range(1, lidJntsLen+1):
            #print increment*i
            detailCtl = controller( updn + 'Detail'+ str(i).zfill(2), [0,0,0], 0.06, "sq" )            
            detailCtlP = detailCtl[1]
            detailPs.append(detailCtlP)
            cmds.parent (detailCtlP, ctlP )
            cmds.setAttr (detailCtlP + ".tx", increment*i - 1.0 )
            cmds.setAttr (detailCtlP + ".ty", 0 )
            cmds.setAttr (detailCtlP + ".tz", 0 )
            cmds.xform ( detailCtl, r =True, s = (1, 1, 1))
            for y in attTemp:
                cmds.setAttr (detailCtl[0] +"."+ y, lock = True, keyable = False, channelBox =False)    
        
        #eyelids controller curve shape ( different number of points )
        if cmds.objExists( updn +'Ctl_crv'):
            cmds.delete (updn +'Ctl_crv')
  
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
            cmds.percent (inCls[0], cornerCrvCv[1],  v = 0.8 )    
            outCls = cmds.cluster (cornerCrvCv[3:5], n = updn[:2] +'outTwistCls')
            cmds.percent (outCls[0], cornerCrvCv[3], v = 0.8 ) 
    
        elif '_lo' in updn:
            cmds.sets( cornerCrvCv[0:2], add= updn[:2] +'inTwistClsSet' )
            cmds.percent ( updn[:2] +'inTwistCls', cornerCrvCv[1],  v = 0.8 ) 
            cmds.sets( cornerCrvCv[3:5], add= updn[:2] +'outTwistClsSet' )
            cmds.percent ( updn[:2] +'outTwistCls', cornerCrvCv[3],  v = 0.8 )
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
            if "l_" in updn:
                cmds.connectAttr ( updn + "InCorner.ty" , ctlCrvCv[0] + ".yValue" )
                cmds.connectAttr ( updn + "InCorner.ty" , ctlCrvCv[1] + ".yValue" )
                cmds.connectAttr ( updn + "OutCorner.ty" , ctlCrvCv[3] + ".yValue" )
                cmds.connectAttr ( updn + "OutCorner.ty" , ctlCrvCv[4] + ".yValue" )
            elif "r_" in updn:
                cmds.connectAttr ( updn + "InCorner.ty" , ctlCrvCv[3] + ".yValue" )
                cmds.connectAttr ( updn + "InCorner.ty" , ctlCrvCv[4] + ".yValue" )
                cmds.connectAttr ( updn + "OutCorner.ty" , ctlCrvCv[0] + ".yValue" )
                cmds.connectAttr ( updn + "OutCorner.ty" , ctlCrvCv[1] + ".yValue" )            
            cmds.setAttr ( ctlCrvCv[0] + ".xValue" , lock = True )     
            cmds.setAttr ( ctlCrvCv[1] + ".xValue" , lock = True ) 
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
        
        incrementPoc = 1.0/(lidJntsLen-1)
        for i in range (0, lidJntsLen ):

            #POC for positionX on the eyelids ctl curve 
            '''ctlXPOC = cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = updn + 'CtlXPoc' + str(i).zfill(2)) 
            cmds.connectAttr ( updn + "Ctl_crvShape.worldSpace", ctlXPOC + '.inputCurve')   
            cmds.setAttr ( ctlXPOC + '.turnOnPercentage', 1 )'''       
            #cmds.setAttr ( ctlXPOC + '.parameter', incrementPoc *i )
            
            #POC for positionY on the eyelids ctl curve 
            ctlYPOC = cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = updn + 'CtlYPoc' + str(i+1).zfill(2)) 
            cmds.connectAttr ( updn + "Ctl_crvShape.worldSpace", ctlYPOC + '.inputCurve')   
            cmds.setAttr ( ctlYPOC + '.turnOnPercentage', 1 )
                       
            #cmds.connectAttr ( ctlXPOC + ".positionX", ctlYPOC + '.parameter' )
            cmds.expression( s= "%s.parameter = (%s.scaleX - 0.3) *%s + (1 - (%s.scaleX - 0.3)) / 2.0 - (%s.translateX / 4.0)"%
            (ctlYPOC, updn + "Center", incrementPoc*i, updn + "Center", updn + "Center") )
            #POC on ctlCrv drive detail control parent
            if "l_" in ctlYPOC:
                cmds.connectAttr ( ctlYPOC +".positionY", detailPs[i] + ".ty" )
            elif "r_" in ctlYPOC:
                cmds.connectAttr ( ctlYPOC +".positionY", detailPs[lidJntsLen-i-1] + ".ty" )
            
            #curves for corner Adjust 06/23/2016
            cornerPOC = cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = updn + 'CornerPoc' + str(i+1).zfill(2)) 
            cmds.connectAttr ( updn +"CornerCrv.worldSpace", cornerPOC + '.inputCurve' )   
            cmds.setAttr ( cornerPOC + '.turnOnPercentage', 1 )        
            cmds.setAttr ( cornerPOC + '.parameter', incrementPoc*i )    
            

          
#lidDetailCtl()





def eyeLidsCrvs( ctlSize ): 
 
    if not ('lEyePos'):
        print "create the face locators"         
    else: 
        eyeRotY = cmds.getAttr ('lEyePos.ry' ) 
        eyeCenterPos = cmds.xform( 'lEyePos', t = True, q = True, ws = True)
 
    if not cmds.objExists ('eyeLidCrv_grp'):
        eyeLidCrvGrp = cmds.group (em =1, n = 'eyeLidCrv_grp', p = 'faceMain|crv_grp' )
    
    if not cmds.objExists ('eyeLidCtl_grp'):
        eyeLidCtlGrp = cmds.group (em =1, n = 'eyeLidCtl_grp', p = 'attachCtl_grp' )        
  
    prefix = ["l_up","l_lo" ]
    for pre in prefix:
        
        jnts = cmds.ls( pre + "LidBlink*_jnt", fl =1, type="joint" )
        leng = len(jnts)
        print leng    
        preR = pre.replace("l_", "r_")
        #create ctrl group 
        lLidCtlGrp = cmds.group (em=True, n = pre + "LidCtl_grp", p= 'eyeLidCtl_grp' ) 
        cmds.xform (lLidCtlGrp, ws = True, t = eyeCenterPos ) 
        cmds.setAttr ( lLidCtlGrp + ".ry", eyeRotY ) 
        rLidCtlGrp = cmds.duplicate ( lLidCtlGrp, n = preR +"LidCtl_grp" )
        cmds.setAttr ( rLidCtlGrp[0] + ".tx", -eyeCenterPos[0] )
        cmds.setAttr ( rLidCtlGrp[0] + ".ry", -eyeRotY )
        cmds.setAttr ( rLidCtlGrp[0] + ".sx", -1 )
        
        #minYCrv /maxYCrv  
        tempMinCrv = cmds.curve( d = 3, p = [(0,0,0),(.25,0,0),(.5,0,0),(.75,0,0),(1,0,0)])
        cmds.rebuildCurve( tempMinCrv, d = 1, rt=0, kr =0, s = leng -1  )
        lMinCrv = cmds.rename (tempMinCrv,  pre[2:] +"Min_crv" )
            
        tempMaxCrv = cmds.curve( d = 3, p = [(0,0,0),(.25,0,0),(.5,0,0),(.75,0,0),(1,0,0)])
        cmds.rebuildCurve( tempMaxCrv, d = 1, rt=0, kr = 0, s = leng -1  ) 
        lMaxCrv = cmds.rename (tempMaxCrv, pre[2:] +"Max_crv" ) 
 
        squintCrv = cmds.duplicate (lMaxCrv, n= pre[2:] +"Squint_crv" )
        annoyCrv = cmds.duplicate ( squintCrv, n= pre[2:] +'Annoy_crv')
        #put curves in the eyeLidCrv_grp  
        cmds.parent (lMinCrv,  lMaxCrv, squintCrv, annoyCrv, 'eyeLidCrv_grp') 
        
        #shape crvs for eyeDirections
        pushA_crv = cmds.duplicate ( lMinCrv,  n = pre +'LidPushA_crv' )
        pushB_crv = cmds.duplicate ( pushA_crv, n= pre +'LidPushB_crv')
        pushC_crv = cmds.duplicate ( pushA_crv, n= pre +'LidPushC_crv')
        pushC_crv = cmds.duplicate ( pushA_crv, n= pre +'LidPushD_crv')
        
    UDLR = ["l_up", "l_lo", "r_up", "r_lo"]    
    for UD in UDLR:        
        if "up" in UD:      
            ty = 1               

        elif "lo" in UD: 
            ty = 0
            
        jnts = cmds.ls( UD + "LidBlink*_jnt", fl =1, type="joint" )
        length = len(jnts)
        
        #eyeOpenCrv with math expression
        if not cmds.objExists( UD +"EyeOpen_crv" ): 
            tempCrv = cmds.curve( d = 3, p = [(0,ty,0),(.25,ty,0),(.5,ty,0),(.75,ty,0),(1,ty,0) ])
            cmds.rebuildCurve( tempCrv, d = 1, rt=0, kr = 0, s = length -1  )
            openCrv = cmds.rename (tempCrv,  UD +"EyeOpen_crv" )
            startCrv = cmds.duplicate (openCrv, n = UD +"EyeStart_crv")
            cmds.parent (openCrv,startCrv, 'eyeLidCrv_grp') 
                   
        #UD / i /  ctlSize /  ctlPOC? /   
        for i in range( 0, length ):            
                        
            #바디 따라다니는 눈꺼플 컨트롤 eyeLid ctrls attach to body 
            childPos = cmds.xform ( cmds.listRelatives (jnts[i], c=1, type ='joint')[0], t = True, q = True, ws = True)   
            lidCtl = controller( UD + "Lid" + str(i+1).zfill(2), childPos, ctlSize*0.1, "cc")
            cmds.parent ( lidCtl[1], UD + "LidCtl_grp" )
            cmds.setAttr ( lidCtl[1] + ".tz", cmds.getAttr(lidCtl[1] + '.tz') + ctlSize*0.2 )
            cmds.setAttr ( lidCtl[1] + ".ry", 0)     
         
            #jumperPanel.l_upPush_Lid# define 
            '''
            LUpPush_Lid0 =  PushLid_EXP.ValA * ((-jumperPanel.LLidPushX + 1) / 2 * LUpDetail0.pushA + (jumperPanel.LLidPushX + 1) / 2 * LUpDetail0.pushB) + 
                            PushLid_EXP.ValB * ((-jumperPanel.LLidPushX + 1) / 2 * LUpDetail0.pushC + (jumperPanel.LLidPushX + 1) / 2 * LUpDetail0.pushD);
            '''
            if "l_" in UD:
                AB = ['A','B']
                CD = ['C','D']
            elif "r_" in UD:
                AB = ['B','A']
                CD = ['D','C'] 
            lid0 = 'jumperPanel.' + UD + 'Push_Lid%s'%str(i) 
            valA = 'jumperPanel.' + UD[:2] + 'valA'
            valB = 'jumperPanel.' + UD[:2] + 'valB'
            pushX = 'jumperPanel.'+ UD[:2] + "lidPushX"
            pushA0 = 'l_'+UD[2:] +'LidPush'+ AB[0] +'_crvShape.cv[%s].yValue'%str(i)  
            pushB0 = 'l_'+UD[2:] +'LidPush'+ AB[1] + '_crvShape.cv[%s].yValue'%str(i)  
            pushC0 = 'l_'+UD[2:] +'LidPush'+ CD[0] + '_crvShape.cv[%s].yValue'%str(i)  
            pushD0 = 'l_'+UD[2:] +'LidPush'+ CD[1] + '_crvShape.cv[%s].yValue'%str(i)  
            
            pushMath = cmds.expression (n=UD+"pushCrv_math%s"%str(i+1), s=" %s=%s*((-%s+1)/2*%s + (%s+1)/2*%s) + %s*((-%s+1)/2*%s + (%s+1)/2*%s)"%(lid0, valA, pushX, pushA0, pushX, pushB0, valB, pushX, pushC0, pushX, pushD0), 
            o = 'jumperPanel.' + UD + 'Push_Lid%s'%str(i), ae =1) 
    
    cornerLidGrp = cmds.group (em =1, n = 'cornerLid_grp', p = 'eyeLidCtl_grp' )          
    corners = [ 'l_inner','l_outer', 'r_inner','r_outer' ]
    for cn in corners:
               
        #바디 따라다니는 corner 눈꺼플 컨트롤 eyeLid ctrls attach to body 
        childPos = cmds.xform ( cn+'Lid_jnt', t = True, q = True, ws = True )   
        lidCtl = controller( cn + "Lid", childPos, ctlSize*0.1, "cc" )
        cmds.parent ( lidCtl[1], cornerLidGrp )
        cmds.setAttr ( lidCtl[1] + ".tz", cmds.getAttr(lidCtl[1] + '.tz') + ctlSize*0.2 )
        cmds.setAttr ( lidCtl[1] + ".ry", 0 )
        
#eyeLidsCrvs(1) : eyeLid_ctls on face are created





#l_eyeBlink / l_eye_ctl connection with eyeBall
#corner LidBlink_jnts setup
def eyeCtl_EXP():
    
    eyeBulge = cmds.shadingNode ( 'multiplyDivide', asUtility=True, n = 'eyeBulge')
    prefix = {"l_": "x", "r_": "y"} #setup on upLids / only a few thing for lolids
    maxCvs = cmds.ls("upMax_crv.cv[*]", fl=1 )    
    maxlen = len(maxCvs)
    for LR in prefix:
        
        #blink setup                
        blinkClamp = cmds.shadingNode("clamp", asUtility =1, n = LR+'blink_clamp')
        blinkMinus = cmds.shadingNode ( 'multiplyDivide', asUtility=True, n = LR + 'blinkMinus_mult')
        cmds.setAttr( blinkMinus + '.input2', -1,-1,-1  )     
        #up lid clamp seperate condition node (blinkCon +'.outColorR' : open(+)/blink (-) )
        # eyeBlinkCtl open
        cmds.connectAttr ( LR + "eyeBlink.ty", blinkClamp + '.inputR' )  
        cmds.setAttr ( blinkClamp + '.maxR', 1 ) 
        cmds.connectAttr ( LR + "eyeBlink.ty", blinkMinus + '.input1Y' )  
        #eyeBlinkCtl blink
        cmds.connectAttr (  blinkMinus + '.outputY', blinkClamp + '.inputG' ) 
        cmds.setAttr ( blinkClamp + '.maxG', 1 )

        #eyeLid thickness : "eyeBlink.tx" setup or "eyeBlink.ty(below -1.0 )" 
        cmds.connectAttr ( LR + "eyeBlink.tx", eyeBulge + ".input1"+ prefix[LR].title() )
        if LR == "l_":
            cmds.setAttr ( eyeBulge + ".input2X", 0.3 )
        else:
            cmds.setAttr ( eyeBulge + ".input2Y", -0.3 )
        #eyeDirections
        eyeBallMult = cmds.shadingNode ( 'multiplyDivide', asUtility=True, n = LR + 'eyeBall_mult')
        #eyeBall rotX (up/down)
        cmds.connectAttr ( LR + "eye_ctl.ty", eyeBallMult + '.input1Y' )
        print cmds.listConnections(eyeBallMult + '.input1Y', s=1, d=0 )
        cmds.connectAttr ( 'lidFactor.eyeBallRotX_scale', blinkMinus + '.input1X' )

        cmds.connectAttr ( blinkMinus + '.outputX', eyeBallMult + '.input2Y' )
        cmds.connectAttr ( eyeBallMult + '.outputY', LR + 'eyeballRot.rx' )
        #eyeBall rotY (left/rigt)
        cmds.connectAttr ( LR + "eye_ctl.tx", eyeBallMult + '.input1X' )
        cmds.connectAttr ( 'lidFactor.eyeBallRotY_scale', eyeBallMult + '.input2X' )
        cmds.connectAttr ( eyeBallMult + '.outputX', LR + 'eyeballRot.ry' )  
                    
        #squint setup
        squintInvert = cmds.shadingNode ('multiplyDivide', asUtility =1, n = LR+'squintInvert_mult' )              
        cmds.connectAttr( LR+'eyeSquint.translateX', squintInvert + '.input1X')
        cmds.connectAttr( LR+'eyeSquint.translateY', squintInvert + '.input1Y')
        cmds.setAttr ( squintInvert + '.input2X', -1 )
        cmds.setAttr ( squintInvert + '.input2Y', -1 )
        #annoy : -squint ctrl 
        annoyRemap = cmds.shadingNode ('remapValue', asUtility =1, n = LR +'annoy_remap' )
        cmds.connectAttr( squintInvert + '.outputY', annoyRemap + '.inputValue')
        cmds.connectAttr( squintInvert + '.outputX', annoyRemap + '.inputMin')
        #squint : +squint ctrl 
        squintRemap = cmds.shadingNode ('remapValue', asUtility =1, n = LR+'squint_remap' )
        cmds.connectAttr( LR+'eyeSquint.translateY', squintRemap + '.inputValue')
        cmds.connectAttr( squintInvert + '.outputX', squintRemap + '.inputMin') 

        #eyeTwist setup     
        #connect lidTwist ctrl to corner jnt
        cornerMult = cmds.shadingNode ('multiplyDivide', asUtility =1, n = LR + 'corner_mult')
        scaleDownMult = cmds.shadingNode ('multiplyDivide', asUtility =1, n = LR + 'scaleDown_mult')
        inCornerSum = cmds.shadingNode ( 'plusMinusAverage', asUtility=True, n = LR + 'inCornerSum')
        outCornerSum = cmds.shadingNode ( 'plusMinusAverage', asUtility=True, n = LR + 'outCornerSum')
        rotX_invert = LR + 'rotX_invert'
        cornerPocs = cmds.ls(LR + "upCornerPoc*", fl=1, type="pointOnCurveInfo" )
        
        #outer corner ctl. ty
        #POC node for far end of curves
        outMaxCv_mult = cmds.shadingNode ('multiplyDivide', asUtility=True, n = LR + 'maxCorner_mult' )
        inMaxCv_mult = cmds.shadingNode ('multiplyDivide', asUtility=True, n = LR + 'maxCorner_mult' )
        print maxCvs[-1], maxCvs[0]
        cmds.connectAttr(maxCvs[-1]+ ".yValue", outMaxCv_mult+".input1Y" )
        cmds.connectAttr(blinkClamp+ ".outputR", outMaxCv_mult+".input2Y" )
        cmds.connectAttr( "jumperPanel.%supPush_Lid%s"%(LR, maxlen-1), scaleDownMult + ".input1Y")
        cmds.setAttr( scaleDownMult + ".input2Y", 0.5 )
        #adding ( outerLid_ctl + detail_ctl + pushLid + eyeWide(no blink) + squint + annoy ) 
        yInputs = [ LR + "outerLid.ty", LR + "outerDetail.ty", scaleDownMult + ".outputY", outMaxCv_mult+".outputY" ]
        plusMinusConnect( outCornerSum, "2D", "y", yInputs )
        
        #cornerSum * eyeBallRotX_scale
        cmds.expression( n= LR+"outCnrSum_exp" , s= " %scnrLidBlink02_jnt.rx = (%s.output2Dy*%s.yValue+ %s.positionY*1.1)*%s;"%(LR, outCornerSum, maxCvs[-1], cornerPocs[-1], cmds.getAttr(rotX_invert + '.outputX')) )       
        cmds.expression( n= LR+"outCnrSum_exp" , s= " %scnrWide02_jnt.rx = (%s.output2Dy*%s.yValue+ %s.positionY*1.1)*%s;"%(LR, outCornerSum, maxCvs[-1],cornerPocs[-1], cmds.getAttr(rotX_invert + '.outputX')) )    
        #cmds.connectAttr ( outCornerMult + '.outputY', LR + 'cnrLidBlink02_jnt.rx' )
        #cmds.connectAttr ( outCornerMult + '.outputY', LR + 'cnrWide02_jnt.rx' )
        
        #outer corner ctl.tx       
        maxCV_add = cmds.shadingNode('addDoubleLinear', asUtility=1, n = LR + "maxCorner_add" )        
        cmds.connectAttr ( maxCvs[-1] + '.xValue', maxCV_add+ '.input1' )
        cmds.setAttr ( maxCV_add+ '.input2', -1 )
        cmds.connectAttr ( maxCV_add+ '.output', outMaxCv_mult + '.input1X' )
        cmds.connectAttr ( blinkClamp + '.outputR', outMaxCv_mult + '.input2X' )

        #adding (cornerCrv Poc + outerLid_ctl + detail_ctl + eyeWide(no blink) )
        xInputs = [ cornerPocs[-1]+'.positionX', -1.0, LR + 'outerLid.tx', LR + 'outerDetail.tx', outMaxCv_mult + '.outputX' ]
        plusMinusConnect( outCornerSum, "2D", "x", xInputs )
        
        cmds.connectAttr ( outCornerSum + '.output2Dx', cornerMult + '.input1X')
        cmds.setAttr ( cornerMult + '.input2X', cmds.getAttr('lidFactor.eyeBallRotY_scale') )
        cmds.connectAttr ( cornerMult + '.outputX', LR + 'cnrLidBlink02_jnt.ry' )
        cmds.connectAttr ( cornerMult + '.outputX', LR + 'cnrWide02_jnt.ry' )        
        
        #inner corner ctl.ty
        #create POC node for far end of curves 
        cmds.connectAttr(maxCvs[0]+ ".yValue", inMaxCv_mult+".input1Y" )
        cmds.connectAttr(blinkClamp+ ".outputR", inMaxCv_mult+".input2Y" )
        cmds.connectAttr( "jumperPanel.%supPush_Lid0"%LR, scaleDownMult + ".input1Z")
        cmds.setAttr( scaleDownMult + ".input2Z", 0.5 )        
        #adding ( outerLid_ctl + detail_ctl + pushLid + eyeWide(no blink) + squint + annoy ) 
        innerYInputs = [ LR + "innerLid.ty", LR + "innerDetail.ty", scaleDownMult + ".outputZ", inMaxCv_mult+".outputY" ]
        plusMinusConnect( inCornerSum, "2D", "y", innerYInputs )        
        
        cmds.expression( n= LR+"inCnrSum_exp" , s= " %scnrLidBlink01_jnt.rx = (%s.output2Dy*%s.yValue+ %s.positionY*1.1)*%s;"%(LR, inCornerSum, maxCvs[0],cornerPocs[0], cmds.getAttr(rotX_invert + '.outputX') ) )       
        cmds.expression( n= LR+"inCnrSum_exp" , s= " %scnrWide01_jnt.rx = (%s.output2Dy*%s.yValue+ %s.positionY*1.1)*%s;"%(LR, inCornerSum, maxCvs[0], cornerPocs[0], cmds.getAttr(rotX_invert + '.outputX') ) ) 
        
        #inner corner ctl.tx
        cmds.connectAttr ( maxCvs[0] + '.xValue', inMaxCv_mult + '.input1X' )
        cmds.connectAttr ( blinkClamp + '.outputR', inMaxCv_mult + '.input2X' )

        #adding (cornerCrv Poc + outerLid_ctl + detail_ctl + eyeWide(no blink) )
        innerXInputs = [ cornerPocs[0]+'.positionX', LR + 'innerLid.tx', LR + 'innerDetail.tx', inMaxCv_mult + '.outputX' ]
        plusMinusConnect( inCornerSum, "2D", "x", innerXInputs )
        
        cmds.connectAttr ( inCornerSum + '.output2Dx', cornerMult + '.input1Z')
        cmds.setAttr ( cornerMult + '.input2Z', cmds.getAttr('lidFactor.eyeBallRotY_scale') )
        cmds.connectAttr ( cornerMult + '.outputZ', LR + 'cnrLidBlink01_jnt.ry')
        cmds.connectAttr ( cornerMult + '.outputZ', LR + 'cnrWide01_jnt.ry' )          

        '''#offset setup ( using squash deformer )
        offsetMult = cmds.shadingNode ('multiplyDivide', asUtility =1, n = LR + 'offset_mult')
        cmds.connectAttr ( LR + 'lidOffset', offsetMult + '.input1X')  
        cmds.setAttr ( offsetMult + '.input2X', 2 )
        cmds.connectAttr ( offsetMult + '.outputX', LR + 'upLidP_jnt' )
        '''




def eyeCrvIncrement(UD):
	
	orderedVerts=cmds.getAttr("lidFactor.%sLidVerts"%UD)
	cornerVerts =cmds.getAttr("lidFactor.cornerVerts" )
	orderedVerts.insert(0,cornerVerts[0])
	orderedVerts.append(cornerVerts[-1])
	vNum = len(orderedVerts)

	vPos = []
	for v in range(vNum): 
	    voc = cmds.xform (orderedVerts[v], t =1, q=1, ws = 1)
	    vocXZ = [ voc[0], 0, voc[2] ]
	    vPos.append(vocXZ)
	vrtsDist = []
	for p in range (0, vNum-1 ):
	    vDist = distance( vPos[p], vPos[p+1])
	    vrtsDist.append(vDist)

	vLength = sum( vrtsDist )

	incremList=[]
	distSum = 0.0
	for i in range (0, vNum-1 ):
	    distSum += vrtsDist[i]
	    increment = distSum / vLength
	    incremList.append(increment)  
	return incremList[:-1]
    

import math
def distance(inputA=[1,1,1], inputB=[2,2,2]):
    return math.sqrt(pow(inputB[0]-inputA[0], 2) + pow(inputB[1]-inputA[1], 2) + pow(inputB[2]-inputA[2], 2))





# mainly setup loLid_jnts 
def eyeCrvToJnt():
    UDLR = ["l_up", "l_lo", "r_up", "r_lo"]
    for UD in UDLR:
                
        jnts = cmds.ls( UD + "LidBlink*_jnt", fl =1, type="joint" )
        length = len(jnts) 
        wideJnts = cmds.ls( UD + "Wide*_jnt", fl =1, type="joint" )       
        maxCrv = UD[2:] +"Max_crv"
        minCrv = UD[2:] +"Min_crv"
        squintCrv = UD[2:] +"Squint_crv" 
        annoyCrv = UD[2:] +"Annoy_crv" 
        squintRemap = UD[:2] +'squint_remap'  
        annoyRemap = UD[:2] +'annoy_remap' 
        blinkClamp = UD[:2]+'blink_clamp'
        loLevel = 'lidFactor.'+ UD[:2] + 'loBlinkLevel'        
        rotX_invert = UD[:2] + 'rotX_invert'

        openCrvParam = eyeCrvIncrement(UD[2:])
        print UD, openCrvParam
        for i in range( 0, length ):        

            #1.ty        
            #ty sum for lids_EXP.EyeStart drives eyeLid_jnt rotateX /
            startSum = cmds.shadingNode ( 'plusMinusAverage', asUtility=True, n = UD + 'StartSum' + str(i+1).zfill(2))            
            #POC on the eyelids ctls curve
            ctlYPOC = UD + 'CtlYPoc' + str(i+1).zfill(2)                           
            lidCtl = UD + "Lid" + str(i+1).zfill(2)
            lidCtlBase = UD + "LidBase" + str(i+1).zfill(2)              
                      
            #squintCrv * squint Ctrl for start_sum  /annoyRemap + '.outValue'/squintRemap + '.outValue'
            squint_mult = cmds.shadingNode ('multiplyDivide', asUtility=True, n = UD + 'Squint_mult' + str(i+1).zfill(2)) 
            #upOpenCrv ( squintCrv -1) . / loOpenCrv squintCrv
            if '_up' in UD:
                #create match_poc for loEyeOpen_crvShape     
                upMatchPOC = cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = UD + 'MatchPoc'+str(i+1).zfill(2) ) 
                cmds.connectAttr ( UD[:2] + 'loEyeStart_crv.worldSpace', upMatchPOC + '.inputCurve' )   
                cmds.setAttr ( upMatchPOC + '.turnOnPercentage', 1 )        
                cmds.setAttr ( upMatchPOC + '.parameter', openCrvParam[i] )
 
                squint_addD = cmds.shadingNode ('addDoubleLinear', asUtility=True, n = UD + 'Squint_addD' + str(i+1).zfill(2))                         
                cmds.connectAttr ( UD[2:] + 'Squint_crvShape.cv[%s].yValue'%str(i), squint_addD + '.input1')
                cmds.setAttr ( squint_addD + '.input2', -1 )
                cmds.connectAttr ( squint_addD + '.output', squint_mult + '.input1Y')
                
                annoy_addD = cmds.shadingNode ('addDoubleLinear', asUtility=True, n = UD + 'Annoy_addD' + str(i+1).zfill(2))                        
                cmds.connectAttr ( UD[2:] + 'Annoy_crvShape.cv[%s].yValue'%str(i), annoy_addD + '.input1')
                cmds.setAttr ( annoy_addD + '.input2', -1 )
                cmds.connectAttr ( annoy_addD + '.output', squint_mult + '.input1X')
                #upLid wide(+)
                cmds.connectAttr( blinkClamp + '.outputR', startSum + '.input2D[0].input2Dy')

                
            elif '_lo' in UD:

                invertMult = cmds.shadingNode ('multiplyDivide', asUtility =1, n = UD +  'InvertMult'+ str(i+1).zfill(2) )
                cmds.connectAttr ( UD[2:] + 'Squint_crvShape.cv[%s].yValue'%str(i), squint_mult + '.input1Y')
                cmds.connectAttr ( UD[2:] + 'Annoy_crvShape.cv[%s].yValue'%str(i), squint_mult + '.input1X')
                #loLid wide(+) by blink ctrl up
                cmds.connectAttr( blinkClamp + '.outputR', invertMult + '.input1X' )
                cmds.setAttr ( invertMult + '.input2X', -1 )
                cmds.connectAttr( invertMult + '.outputX', startSum + '.input2D[0].input2Dy')
            
                                     
            cmds.connectAttr ( squintRemap + '.outValue', squint_mult + '.input2Y' )
            cmds.connectAttr ( squint_mult + '.outputY', startSum +'.input2D[1].input2Dy' )
          
            #annoyCrv * squint ctrl for start_sum / #upOpenCrv ( annoyCrv -1) . / loOpenCrv annoyCrv 
            cmds.connectAttr ( annoyRemap + '.outValue', squint_mult + '.input2X') 
            cmds.connectAttr ( squint_mult + '.outputX', startSum + '.input2D[2].input2Dy' )
          
            #ty sum for eyeStart            
            #cmds.connectAttr (ctlYPOC + '.positionY', startSum + '.input2D[3].input2Dy' ) 
            cmds.connectAttr ( UD + 'Detail%s.ty'%str(i+1).zfill(2), startSum + '.input2D[4].input2Dy')                       
            cmds.connectAttr ( 'jumperPanel.'+UD+'Push_Lid%s'%str(i), startSum + '.input2D[5].input2Dy')     
            #add the lid ctls(on the body) to startSum
            cmds.connectAttr ( lidCtl + '.ty', startSum + '.input2D[6].input2Dy')            
            
            
            if '_lo' in UD:
                #create start_poc for loEyeOpen_crvShape     
                loStartPOC = cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = UD + 'StartPoc'+str(i+1).zfill(2) ) 
                cmds.connectAttr ( UD + 'EyeStart_crv.worldSpace', loStartPOC + '.inputCurve' )  
                cmds.setAttr ( loStartPOC + '.turnOnPercentage', 1 )        
                cmds.setAttr ( loStartPOC + '.parameter', openCrvParam[i] )
                
                #define lids_EXP start
                minMaxMult = cmds.shadingNode ('multiplyDivide', asUtility =1, n = UD + 'MinMax_mult'+ str(i+1).zfill(2))
                #minMaxWideScale = cmds.shadingNode ('multiplyDivide', asUtility =1, n = UD + 'MinMax_wideScale'+ str(i+1).zfill(2))
                loStartCon = cmds.shadingNode ('condition', asUtility =1, n = UD +  'StartCon'+ str(i+1).zfill(2) )
                cmds.connectAttr ( startSum + '.output2Dy', loStartCon + '.firstTerm' )
                cmds.setAttr ( loStartCon +'.operation', 2 )
                cmds.connectAttr ( startSum + '.output2Dy', minMaxMult  + '.input1X' )
                cmds.connectAttr ( 'loMin_crvShape.cv[%s].yValue'%str(i), minMaxMult  + '.input2X' )
                cmds.connectAttr ( minMaxMult  + '.outputX', loStartCon + '.colorIfTrueR')
                cmds.connectAttr ( startSum + '.output2Dy', minMaxMult  + '.input1Y' )
                cmds.connectAttr ( 'loMax_crvShape.cv[%s].yValue'%str(i), minMaxMult  + '.input2Y' )
                cmds.connectAttr ( minMaxMult  + '.outputY', loStartCon + '.colorIfFalseR')                             
                cmds.connectAttr (loStartCon +'.outColorR', 'lids_EXP.' + UD + 'EyeStart%s'%str(i))                
                cmds.connectAttr ('lids_EXP.' + UD + 'EyeStart%s'%str(i), UD + 'EyeStart_crvShape.controlPoints[%s].yValue'%str(i) )
                #wideSum * min / max scale control( wide jnt을 위한 ctrl 필요하다)                
                cmds.connectAttr ( minMaxMult  + '.outputY', loStartCon + '.colorIfFalseG')                      
                
                #define lids_EXP Open
                minLen = 'loMin_crvShape.cv[%s].yValue'%str(i)                                 
                blinkSum = cmds.shadingNode ('plusMinusAverage', asUtility=True, n = UD + 'BlinkSum' + str(i+1).zfill(2))
                cmds.connectAttr ( loStartPOC +'.positionY', blinkSum + '.input1D[0]')
                cmds.expression (n="damp_math"+ str(i), s = "%s= %s*%s*%s;"%(blinkSum + '.input1D[1]', blinkClamp+'.outputG', minLen, loLevel ), o = 'input2', ae =1)
                
                #add extra ( cornerPoc ) 
                cornerPOC = UD + 'CornerPoc' + str(i+1).zfill(2)
                cmds.connectAttr(cornerPOC + '.positionY', blinkSum + '.input1D[2]')
                
                #define lids_EXP open = start + blinkRemap
                cmds.connectAttr (blinkSum + '.output1D', 'lids_EXP.' + UD + 'EyeOpen%s'%str(i))
                cmds.connectAttr ('lids_EXP.' + UD + 'EyeOpen%s'%str(i), UD + 'EyeOpen_crvShape.controlPoints[%s].yValue'%str(i) ) 
                jntMult = cmds.shadingNode ('multiplyDivide', asUtility =1, n = UD + 'JntMult'+ str(i+1).zfill(2))              
                                    
                cmds.connectAttr (blinkSum + '.output1D', jntMult + '.input1Y')
                # -'lidFactor.lidRotateX_scale' (= rotX_invert + '.outputX')
                cmds.connectAttr( rotX_invert + '.outputX', jntMult + '.input2Y')
                cmds.connectAttr( jntMult +'.outputY', jnts[i] + '.rx' )               
                
                cmds.connectAttr( loStartCon +'.outColorG',  jntMult + '.input1X' )
                # -'lidFactor.lidRotateX_scale' (= rotX_invert + '.outputX')
                cmds.connectAttr( rotX_invert + '.outputX', jntMult + '.input2X' )
                cmds.connectAttr( jntMult +'.outputX', wideJnts[i] + '.rx' )        
                
                #add squint + annoy for 'in/outCornerSum'                
                if i == 0:
                    innerSquint_add = cmds.shadingNode ('addDoubleLinear', asUtility=True, n = UD + 'InnerSquint_Add')  
                    cmds.connectAttr( squint_mult + '.outputX', innerSquint_add + ".input1" )
                    cmds.connectAttr( squint_mult + '.outputY', innerSquint_add + ".input2" )
                    cmds.connectAttr( innerSquint_add + ".output", minMaxMult+ ".input1Z" )
                    cmds.setAttr( minMaxMult+ ".input2Z", 0.2 )
                    cmds.connectAttr ( minMaxMult+ ".outputZ", UD[:2] + 'inCornerSum.input2D[5].input2Dy' )
                elif i == length-1:
                    outerSquint_add = cmds.shadingNode ('addDoubleLinear', asUtility=True, n = UD + 'OuterSquint_Add')  
                    cmds.connectAttr( squint_mult + '.outputX', outerSquint_add + ".input1" )
                    cmds.connectAttr( squint_mult + '.outputY', outerSquint_add + ".input2" )
                    cmds.connectAttr( outerSquint_add + ".output", minMaxMult+ ".input1Z" )
                    cmds.setAttr( minMaxMult+ ".input2Z", 0.2 )
                    cmds.connectAttr ( minMaxMult+ ".outputZ", UD[:2] + 'outCornerSum.input2D[5].input2Dy' )                        
        
             #2.tx

            #get maxCrv.cv[i].xValue movement
            cvMove_addD = cmds.shadingNode ('addDoubleLinear', asUtility=True, n = UD + 'MaxCV' + str(i+1).zfill(2))            
            maxTX = cmds.getAttr (UD[2:] +'Max_crv' + '.cv[%s].xValue'%str(i) )           
            cmds.connectAttr (UD[2:] +'Max_crv' + '.cv[%s].xValue'%str(i), cvMove_addD + '.input1' )
            cmds.setAttr (cvMove_addD + '.input2', -maxTX )                     
            
            maxCv_mult = cmds.shadingNode ('multiplyDivide', asUtility=True, n = UD + 'MaxCv_mult' + str(i+1).zfill(2))
            cmds.connectAttr (cvMove_addD + '.output', maxCv_mult + '.input1X' )
            cmds.connectAttr ( blinkClamp + '.outputR', maxCv_mult + '.input2X' )
            cmds.connectAttr (maxCv_mult + '.outputX', startSum + '.input2D[2].input2Dx')
            cmds.connectAttr( lidCtl + '.tx', startSum + '.input2D[3].input2Dx' ) 

            if "r_" in UD:

                cmds.connectAttr ( UD + 'CtlYPoc' + str(length-i).zfill(2) +".positionY", startSum + '.input2D[3].input2Dy' )
                invert = cmds.shadingNode ('multiplyDivide', asUtility =1, n = UD + 'InvertMult'+ str(i+1).zfill(2) )
                cmds.setAttr( invert+ ".input2", -1,-1,-1)

                cmds.connectAttr (UD + 'Detail%s.tx'%str(i+1).zfill(2), invert+ ".input1Y" )
                cmds.connectAttr ( invert+ ".outputY", startSum + '.input2D[1].input2Dx')              
                #right eyeBulge
                cmds.connectAttr ( 'eyeBulge.outputY', jnts[i].replace("Blink", "Tx") + '.tz' )
    
            elif "l_" in UD:
                cmds.connectAttr ( ctlYPOC +".positionY", startSum + '.input2D[3].input2Dy' )
                cmds.connectAttr (UD + 'Detail%s.tx'%str(i+1).zfill(2), startSum + '.input2D[1].input2Dx')
                #right eyeBulge               
                cmds.connectAttr ( 'eyeBulge.outputX', jnts[i].replace("Blink", "Tx") + '.tz' )
            
            #add lidCorner crv positionX
            cornerPOC = UD + 'CornerPoc' + str(i+1).zfill(2)
            cmds.connectAttr ( cornerPOC + '.positionX', startSum + '.input2D[4].input2Dx')
            cornerTX = cmds.getAttr( cornerPOC + '.positionX' )
            #cmds.setAttr ( startSum + '.input2D[5].input2Dx', -cornerTX )
                         
            '''true = (ctlPoc[i]+ Detail[i].tx + lidCtl + '.tx' ) *180 * (maxCrv[i]-initialX)
            false = (ctlPOC+ Detail[i].tx + lidCtl + '.tx' ) *180 * (squintCrv[i]-initialX)'''    
            #openCrvTX = cmds.getAttr(UD + 'EyeOpen_crvShape.controlPoints[%s].xValue'%str(i) )
            rotY_mult = cmds.shadingNode ('multiplyDivide', asUtility=True, n = UD + 'BlinkRY_mult' + str(i+1).zfill(2))
            txForJnt = cmds.shadingNode ('addDoubleLinear', asUtility=True, n = UD + 'TxForJnt_add' + str(i+1).zfill(2)) 
            cmds.connectAttr(startSum + '.output2Dx', txForJnt + '.input1')            
            cmds.setAttr( txForJnt + '.input2', -cornerTX )
            cmds.connectAttr( txForJnt + '.output', rotY_mult + '.input1X')
            cmds.connectAttr( 'lidFactor.lidRotateY_scale', rotY_mult + '.input2X' )
            cmds.connectAttr( rotY_mult + '.outputX', jnts[i] + '.ry')
            
            #Wide tx  
            cmds.connectAttr( rotY_mult + '.outputX', wideJnts[i] + '.ry' )
            
            '''cmds.connectAttr (maxCv_mult + '.outputX', rotY_mult + '.input1Y')
            cmds.connectAttr( 'lidFactor.lidRotateY_scale', rotY_mult + '.input2Y')'''         
            
            #eyeOpenCrv  tx  
            cmds.connectAttr( startSum + '.output2Dx', UD + 'EyeOpen_crvShape.controlPoints[%s].xValue'%str(i))

    cmds.connectAttr ( 'eyeBulge.outputY', 'r_innerLidTxTX_jnt.tz'  )
    cmds.connectAttr ( 'eyeBulge.outputY', 'r_outerLidTxTX_jnt.tz'  )
    cmds.connectAttr ( 'eyeBulge.outputX', 'l_innerLidTxTX_jnt.tz' )
    cmds.connectAttr ( 'eyeBulge.outputX', 'l_outerLidTxTX_jnt.tz' )



#upperLid jnts connections
def blinkRemap():
    
    UDLR = ["l_up", "r_up" ]
    for UD in UDLR:
        
        blinkClamp = UD[:2]+'blink_clamp'
        upLevel = 'lidFactor.'+ UD + 'BlinkLevel'
        jnts = cmds.ls( UD + "LidBlink*_jnt", fl =1, type="joint" )        
        length = len(jnts)
        wideJnts = cmds.ls( UD + "Wide*_jnt", fl =1, type="joint" )
        loPOC = cmds.ls( UD + 'MatchPoc*', fl=1, type="pointOnCurveInfo" )

        for i in range( 0, length ):
                                   
            startSum = UD + 'StartSum' + str(i+1).zfill(2)
            DU = UD.replace('up','lo')
            
            jntMult = cmds.shadingNode ('multiplyDivide', asUtility =1, n = UD + 'JntMult'+ str(i+1).zfill(2))
            #create PointOnCurve node ( on the loLidCrv) to match uplid joints for blink
            '''loPOC = cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = DU + 'MatchPoc' + str(i+1).zfill(2))
            cmds.connectAttr ( DU + "EyeStart_crvShape.worldSpace",  loPOC + '.inputCurve')   
            cmds.setAttr ( loPOC + '.turnOnPercentage', 1 )               
            cmds.connectAttr ( UD + "EyeOpen_crvShape.controlPoints[%s].xValue"%str(i), loPOC + '.parameter')'''

            #blink remap setup
            blinkRemap = cmds.shadingNode ('remapValue', asUtility =1, n =  UD + 'RemapBlink' + str(i+1).zfill(2))
            loStart = loPOC[i] + '.positionY'
            minLen = 'upMin_crvShape.controlPoints[%s].yValue'%str(i)
            #blinkRemap+'.outputMax'= min(loStart(loPOC[i] + '.positionY') - 'upMin_crvShape.controlPoints[%s].yValue'%str(i)*upLevel), 0)
            cmds.expression (n="remapMax_math"+ str(i), s = "%s=min((%s - %s*%s),0);"%( blinkRemap+'.outputMax', loStart, minLen, upLevel ), o = 'outputMax', ae =1)           

            #condition for upStart to include Min/Max curves 
            minMaxMult = cmds.shadingNode ('multiplyDivide', asUtility =1, n = UD + 'MinMax_mult'+ str(i+1).zfill(2))
            #minMaxWideMult = cmds.shadingNode ('multiplyDivide', asUtility =1, n = UD + 'MinMaxWide_mult'+ str(i+1).zfill(2))
            upStartCon = cmds.shadingNode ('condition', asUtility =1, n = UD +  'StartCon'+ str(i+1).zfill(2) )
            cmds.connectAttr ( startSum + '.output2Dy', upStartCon + '.firstTerm' )
            cmds.setAttr ( upStartCon +'.operation', 4 )
            cmds.connectAttr ( startSum + '.output2Dy', minMaxMult  + '.input1X' )
            cmds.connectAttr ( 'upMin_crvShape.cv[%s].yValue'%str(i), minMaxMult  + '.input2X' )
            cmds.connectAttr ( minMaxMult  + '.outputX', upStartCon + '.colorIfTrueR')
            cmds.connectAttr ( startSum + '.output2Dy', minMaxMult  + '.input1Y' )
            cmds.connectAttr ( 'upMax_crvShape.cv[%s].yValue'%str(i), minMaxMult  + '.input2Y' )
            cmds.connectAttr ( minMaxMult  + '.outputY', upStartCon + '.colorIfFalseR')                             
            cmds.connectAttr (upStartCon +'.outColorR', 'lids_EXP.' + UD + 'EyeStart%s'%str(i))
                                               
            #remap outputMin / inputValue
            cmds.connectAttr ( upStartCon +'.outColorR', blinkRemap + '.outputMin' )
            cmds.connectAttr( blinkClamp + '.outputG', blinkRemap + '.inputValue' )
            
            #define lids_EXP open
            cmds.connectAttr ( blinkRemap + '.outValue', 'lids_EXP.' + UD + 'EyeOpen%s'%str(i))
            cmds.connectAttr ('lids_EXP.' + UD + 'EyeOpen%s'%str(i), UD + 'EyeOpen_crvShape.controlPoints[%s].yValue'%str(i))
            
            #add extra ( cornerPoc ) 
            twist_addD = cmds.shadingNode ('addDoubleLinear', asUtility=True, n = UD + 'TwistAdd' + str(i+1).zfill(2))
            cornerPOC = UD + 'CornerPoc' + str(i+1).zfill(2)
            cmds.connectAttr(cornerPOC + '.positionY', twist_addD + '.input1')
            cmds.connectAttr( blinkRemap + '.outValue', twist_addD + '.input2')
            #connect blink_jnt
            rotX_invert = UD[:2] + 'rotX_invert'
            cmds.connectAttr( twist_addD + '.output', jntMult + '.input1Y' )
            cmds.connectAttr( rotX_invert + '.outputX', jntMult + '.input2Y' )
            cmds.connectAttr( jntMult +'.outputY', jnts[i] + '.rx' )            
            
            #condition for upWideSum to include Min/Max curves 
            '''cmds.connectAttr ( wideSum + '.output1D', minMaxWideMult  + '.input1X' )
            cmds.connectAttr ( 'upMin_crvShape.cv[%s].yValue'%str(i), minMaxWideMult  + '.input2X' )
            cmds.connectAttr ( minMaxWideMult  + '.outputX', upStartCon + '.colorIfTrueG')
            cmds.connectAttr ( wideSum + '.output1D', minMaxWideMult  + '.input1Y' )
            cmds.connectAttr ( 'upMax_crvShape.cv[%s].yValue'%str(i), minMaxWideMult  + '.input2Y' )
            cmds.connectAttr ( minMaxWideMult  + '.outputY', upStartCon + '.colorIfFalseG')'''                             
            #wideJnt for upStartCon + side
            #twist_addWide = cmds.shadingNode ('plusMinusAverage', asUtility=True, n = UD + 'TwistWideAdd' + str(i+1).zfill(2))
            cmds.connectAttr ( minMaxMult  + '.outputY', upStartCon + '.colorIfFalseG')
            # wideSum to wide jnt     
            cmds.connectAttr( upStartCon +'.outColorG',  jntMult + '.input1X' )
            cmds.connectAttr( rotX_invert + '.outputX', jntMult + '.input2X' )
            cmds.connectAttr( jntMult +'.outputX', wideJnts[i] + '.rx' )
            

        
            
            
def plusMinusConnect( node, div, xyz, inputs ):
    
    for n, ip in enumerate(inputs):
        print n, ip
        if div =="1D":
            if isinstance(ip, float ):
                cmds.connectAttr ( ip, node + '.input1D[%s]'%str(n))                
            else:
                cmds.setAttr ( node + '.input1D[%s]'%str(n), ip )
                
        else:
            if isinstance(ip, float ):
                print ip
                cmds.setAttr ( node + '.input%s[%s].input%s%s'%(div, str(n), div, xyz), ip )
            else:
                print ip
                cmds.connectAttr ( ip, node + '.input%s[%s].input%s%s'%(div, str(n), div, xyz) )

                
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
