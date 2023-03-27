# -*- coding: utf-8 -*-
#컨트롤 패널 리셋,키,선택
#컨트롤 패널과 얼굴 clusters / blendShape curves 연결


import maya.cmds as cmds
import BCDtypeCtrlSetup
reload(BCDtypeCtrlSetup)

def selectCtls(char):
    jackBody = [u'head_anim_ctl', u'shoulder_anim', u'torso_2_anim', u'torso_1_anim', u'hip_anim', u'body_anim', u'GeoViz', u'l_ik_hand_anim', 
u'l_ik_elbow_anim', u'l_shoulder_anim', u'l_upperarm_bend', u'l_lowerarm_bend', u'r_shoulder_anim', u'r_ik_elbow_anim', u'r_ik_hand_anim', 
u'r_lowerarm_bend', u'r_upperarm_bend', u'l_foot_anim', u'r_foot_anim', u'l_knee_anim', u'r_knee_anim', u'settings_anim', u'settings_visibility', 
u'l_thumb_2_ctrl', u'l_thumb_1_ctrl', u'l_thumb_base_ctrl', u'l_ring_3_ctrl', u'l_ring_2_ctrl', u'l_ring_1_ctrl', u'l_pinky_3_ctrl', 
u'l_pinky_2_ctrl', u'l_pinky_1_ctrl', u'l_index_3_ctrl', u'l_index_2_ctrl', u'l_index_1_ctrl', u'l_middle_3_ctrl', u'l_middle_2_ctrl', 
u'l_middle_1_ctrl', u'l_index_base_ctrl', u'l_middle_base_ctrl', u'l_ring_base_ctrl', u'l_pinky_base_ctrl', u'l_fingers_anim', u'l_thumb_anim', 
u'l_middle_anim', u'l_ring_anim', u'l_pinky_anim', u'l_pointer_anim', u'r_index_3_ctrl', u'r_index_2_ctrl', u'r_index_1_ctrl', u'r_index_base_ctrl', 
u'r_middle_3_ctrl', u'r_middle_2_ctrl', u'r_middle_1_ctrl', u'r_middle_base_ctrl', u'r_ring_3_ctrl', u'r_ring_2_ctrl', u'r_ring_1_ctrl', 
u'r_ring_base_ctrl', u'r_pinky_3_ctrl', u'r_pinky_2_ctrl', u'r_pinky_1_ctrl', u'r_pinky_base_ctrl', u'r_thumb_2_ctrl', u'r_thumb_1_ctrl', 
u'r_thumb_base_ctrl', u'r_fingers_anim', u'r_thumb_anim', u'r_pointer_anim', u'r_middle_anim', u'r_ring_anim', u'r_pinky_anim', u'neck_anim']

    if char == "jackBody":
        return jackBody
    elif char == "hodongBody":
        return hodongBody

    elif char == "jackFace":
        return jackFace
        
    elif char == "hodongFace":
        return hodongFace
        
        
#faceArea = all, mouth, bridge, eye
def returnCtls( faceArea ):
    lipDetailP = cmds.ls("loLipDetailP*", fl=1, type = "transform") + cmds.ls("upLipDetailP*", fl=1, type = "transform")
    lipDetails = cmds.listRelatives( lipDetailP , c=1)
    mouthCtls = ['lipLoCtrlRB', 'lipLoCtrlRA', 'lipLoCtrlLB', 'lipLoCtrlLA', 'lipLoCtrlMid', 'lipUpCtrlRB', 'lipUpCtrlRA', 'lipUpCtrlLB', 'lipUpCtrlLA', 'lipUpCtrlMid',
     'r_lipLoRoll_ctl', 'l_lipLoRoll_ctl', 'midLipLoRoll_ctl', 'r_lipUpRoll_ctl', 'l_lipUpRoll_ctl', 'midLipUpRoll_ctl', "rCornerTZ", "lCornerTZ", 'lipCtrlLTip', 'lipCtrlRTip', 'lowJaw_dir', 'swivel_ctrl', 'jaw_UDLR', 'r_phonemes_ctl', 'l_phonemes_ctl', 'mouth_move', "cornerLip_levelCtl",
     'r_mouth_happysad', 'l_mouth_happysad', 'upteeth_motion', 'loteeth_motion',"l_ShM","r_ShM" ]
    
    squachOnFc = [ x for x in [ "topSquach_ctl", "bttmSquach_ctl" ] if cmds.objExists(x) ]
    bridgeCtls = [ "headSquach_top","headSquach_bttm",'r_nose_flare', 'l_nose_flare', 'r_nose_sneer', 'l_nose_sneer', 'nose_move', 'r_bridge_puffsuck', 'l_bridge_puffsuck',
     "l_ear_ctl","r_ear_ctl", "l_earRot_ctl","r_earRot_ctl", 'r_cheek_ctl', 'l_cheek_ctl', 'r_lidPuff_ctl', 'l_lidPuff_ctl', 'r_loCheek_ctl', 'l_loCheek_ctl']     
    
    #eyelid Ctrl list
    lidDetailP = cmds.ls("*_upDetail*_grp", type = "transform" )+ cmds.ls("*_loDetail*P", type = "transform" )
    lidDetail = cmds.listRelatives(lidDetailP, c=1, type ="transform" )
    lidCtls = [ 'r_upOutCorner', 'r_upInCorner', 'r_upCenter', 'l_upOutCorner', 'l_upInCorner', 'l_upCenter', 'r_loOutCorner', 'r_loInCorner', 'r_loCenter', 'l_loOutCorner', 
    'l_loInCorner', 'l_loCenter']   
    lidCorners = ["l_innerLidTwistP", "l_outerLidTwistP", "r_innerLidTwistP","r_outerLidTwistP"]
    cornerShapes = cmds.listRelatives( lidCorners, ad=1, type="nurbsCurve" )
    cornerCtls = cmds.listRelatives( cornerShapes, p=1, type = "transform")
    
    #ctrl list on the face 
    ctlOnFace = cmds.listRelatives(cmds.listRelatives( "attachCtl_grp", ad=1, type = "nurbsCurve"), p=1, type="transform")
    browDetailCtls = cmds.listRelatives( cmds.ls( "browDetail*Shape", type = "nurbsCurve" ), p =1 ) 
    
    eyeCtls = ['brow_arcE', 'brow_arcC', 'brow_arcD', 'brow_arcB', 'brow_arcA', 'l_brow_Furrow', 'r_brow_Furrow', 'r_brow_madsad', 'l_brow_madsad', 'rEyeShapeCtrl', 'lEyeShapeCtrl', 
    'r_outerDetail', 'r_outerLidTwist', 'r_innerDetail', 'r_innerLidTwist', 'l_outerDetail', 'l_outerLidTwist', 'l_innerDetail', 'l_innerLidTwist', 'r_eyeBlink', 'l_eyeBlink', 
    'l_eyeSquint', 'r_eyeSquint', 'r_eye_ctl', 'l_eye_ctl', 'riris_dial', 'liris_dial', 'rpupil_dial', 'lpupil_dial', 'eyeblend_dir', 'l_eyeOffset_ctl', 'r_eyeOffset_ctl', 
    'l_eyeSmooth', 'r_eyeSmooth', 'r_eyeSquach', 'l_eyeSquach', 'l_lidHeight', 'r_lidHeight']+ browDetailCtls + lidCtls + cornerCtls     
           
    baseCtl = mouthCtls + bridgeCtls + eyeCtls + [ z for z in ctlOnFace if not "Lid" in z ]
    allCtls = mouthCtls + bridgeCtls + eyeCtls + lipDetails + lidDetail + ctlOnFace + squachOnFc
    if faceArea == "basic":
        return baseCtl

    elif faceArea == "all":
        return allCtls
        
    elif faceArea == "mouth":
        return mouthCtls
        
    elif faceArea == "eye":
        return eyeCtls
        
    elif faceArea == "bridge":
        return bridgeCtls
        


def resetCtrl(facePart):
    ctrls = returnCtls( facePart ) 
    for ct in ctrls:

        attrs = cmds.listAttr( ct, k=1, unlocked = 1 )
        for at in attrs:
            if 'scale' in at:
                cmds.setAttr( ct+"."+at, 1 )
            elif at=='visibility':
                continue
                #cmds.setAttr( ct+"."+at, 1 )
            else:
                cmds.setAttr( ct+"."+at, 0 )
                
        
def deleteCtrlKeys(facePart):
    ctrls = returnCtls( facePart ) 
    for ct in ctrls:
    
        attrs = cmds.listAttr( ct, k=1, unlocked = 1 )
        for at in attrs:
            keyCount = cmds.keyframe( ct+"."+ at, query=True, keyframeCount=True )
            if keyCount:            
                cmds.cutKey( ct+"."+at )


def selectCtrl(facePart):
    ctrls = returnCtls( facePart ) 
    cmds.select( ctrls, r=1 )


    
#lip_crv lipCtl_crv to lipCornerCls/ cheek_crv to lowCheek, cheek, squintPff
def ctrlConnectFaceCluster():
    
    #nose cls connect
    inCnnt = cmds.listConnections ("nose_clsHandle", d=0, s=1, p=1, type ="transform" )
    if len(inCnnt) == 3:                
        cmds.disconnectAttr ( inCnnt[0], "nose_clsHandle.t" )
        cmds.disconnectAttr ( inCnnt[1], "nose_clsHandle.r" )
        cmds.disconnectAttr ( inCnnt[2], "nose_clsHandle.s" )  
    noseTranPlus = cmds.shadingNode( "plusMinusAverage", asUtility=1, n = "noseTranPlus" )
    noseRotPlus = cmds.shadingNode( "plusMinusAverage", asUtility=1, n = "noseRotPlus" )
    noseScalPlus = cmds.shadingNode( "plusMinusAverage", asUtility=1, n = "noseScalPlus" )
    #nose translate plus
    cmds.connectAttr ( "nose_onCtl.t", noseTranPlus+".input3D[0]" )
    cmds.connectAttr ( "nose_move.t", noseTranPlus+".input3D[1]" )
    #nose rotate plus
    cmds.connectAttr ( "nose_onCtl.r", noseRotPlus+".input3D[0]" )
    cmds.connectAttr ( "nose_move.r", noseRotPlus+".input3D[1]" )
    #nose scale plus
    cmds.connectAttr ( "nose_onCtl.s", noseScalPlus+".input3D[0]" )
    #cmds.connectAttr ( "nose_move.s", noseScalPlus+".input3D[1]" )
          
    #nose_cls connect                         
    cmds.connectAttr ( noseTranPlus+".output3D", "nose_clsHandle.t" )
    cmds.connectAttr ( noseRotPlus+".output3D", "nose_clsHandle.r" )
    cmds.connectAttr ( noseScalPlus+".output3D", "nose_clsHandle.s" )
    
    #cheek cluster connected to cheek curve
    for LR in ["l_","r_"]:
        earClsCnnt = cmds.listConnections ( LR+"ear_clsHandle", d=0, s=1, type="transform")        
        if len(earClsCnnt) ==3:
            cmds.disconnectAttr ( earClsCnnt[0]+".t", LR+"ear_clsHandle.t" )
            cmds.disconnectAttr ( earClsCnnt[0]+".r", LR+"ear_clsHandle.r" )
            cmds.disconnectAttr ( earClsCnnt[0]+".s", LR+"ear_clsHandle.s" )
        else:
            print "break connection manually"
        earTranPlus = cmds.shadingNode( "plusMinusAverage", asUtility=1, n = LR + "earTranPlus" )
        earRotPlus = cmds.shadingNode( "plusMinusAverage", asUtility=1, n = LR + "earRotPlus" )
        earScalPlus = cmds.shadingNode( "plusMinusAverage", asUtility=1, n = LR + "earScalPlus" )
        #poc node1 connect
        cmds.connectAttr ( LR+"ear_ctl.t", earTranPlus+".input3D[0]" )
        cmds.connectAttr ( LR+"ear_onCtl.t", earTranPlus+".input3D[1]" )
        
        cmds.connectAttr ( LR+"earRot_ctl.r", earRotPlus +".input3D[0]" )
        cmds.connectAttr ( LR+"ear_onCtl.r", earRotPlus +".input3D[1]" )
        
        #cmds.connectAttr ( LR+"ears_ctl.s", earScalPlus +".input3D[0]" )
        cmds.connectAttr ( LR+"ear_onCtl.s", earScalPlus +".input3D[1]" )
        
        #loCheek_ctl connect
        cmds.connectAttr ( earTranPlus+".output3D", LR+"ear_clsHandle.t" ) 
        cmds.connectAttr ( earRotPlus+".output3D", LR+"ear_clsHandle.r" ) 
        cmds.connectAttr ( earScalPlus+".output3D", LR+"ear_clsHandle.s" )  
        
        #[u'cheek2_poc', u'cheek3_poc', u'cheek0_poc', u'cheek1_poc']
        pocList = cmds.listConnections( LR + "cheek_crvShape", d=1, s=0, type = "pointOnCurveInfo")
        for i in range(len(pocList)):
            param = cmds.getAttr( pocList[i]+".parameter")
            if param == 0:
                inCnnt = cmds.listConnections ( LR + "lowCheek_grp", d=0, s=1, p=1)
                if len(inCnnt) ==3:               
                    cmds.disconnectAttr ( pocList[i]+".positionX", LR + "lowCheek_grp.tx" )
                    cmds.disconnectAttr ( pocList[i]+".positionY", LR + "lowCheek_grp.ty" )
                    cmds.disconnectAttr ( pocList[i]+".positionZ", LR + "lowCheek_grp.tz" )
                minusAverage = cmds.shadingNode( "plusMinusAverage", asUtility=1, n = LR + "lowCheekMinus" )
                #poc node1 connect
                cmds.connectAttr ( pocList[i]+".position", minusAverage+".input3D[0]" )
                cmds.setAttr( minusAverage+".input3D[1].input3Dx", -1*(cmds.getAttr( pocList[i]+".positionX" )) )
                cmds.setAttr( minusAverage+".input3D[1].input3Dy", -1*(cmds.getAttr( pocList[i]+".positionY" )) )
                cmds.setAttr( minusAverage+".input3D[1].input3Dz", -1*(cmds.getAttr( pocList[i]+".positionZ" )) )
                #loCheek_ctl connect
                cmds.connectAttr ( LR+"loCheek_ctl.t", minusAverage+".input3D[2]" )
                #lowCheek_ctl( on face ) connect
                cmds.connectAttr ( LR+"lowCheek_onCtl.t", minusAverage+".input3D[3]" )
                
                #lowCheek_cls connect                         
                cmds.connectAttr ( minusAverage+".output3D", LR+"lowCheek_clsHandle.t", f=1 )
            
            if param == 2:
                outCnnt = cmds.listConnections (pocList[i], d=1, s=0, p=1, type ="transform" )
                if len(outCnnt) == 3:                
                    cmds.disconnectAttr ( pocList[i]+".positionX", outCnnt[0] )
                    cmds.disconnectAttr ( pocList[i]+".positionY", outCnnt[1] )
                    cmds.disconnectAttr ( pocList[i]+".positionZ", outCnnt[2] )  
                cheekPlus = cmds.shadingNode( "plusMinusAverage", asUtility=1, n = LR + "cheekPlus" )
                #poc node1 connect
                cmds.connectAttr ( pocList[i]+".position", cheekPlus+".input3D[0]" )
                #loCheek_ctl connect
                cmds.connectAttr ( LR+"cheek_ctl.t", cheekPlus+".input3D[1]" )           
                #lowCheek_ctl( on face ) connect
                cmds.connectAttr ( LR+"cheek_onCtl.t", cheekPlus+".input3D[2]" )
                
                #lowCheek_cls connect                         
                cmds.connectAttr ( cheekPlus+".output3D", LR+"cheek_grp.t" )                
                        
            if param == 3:
                outCnnt = cmds.listConnections ( pocList[i], d=1, s=0, p=1, type="transform")
                if len(inCnnt) ==3:               
                    cmds.disconnectAttr ( pocList[i]+".positionX", outCnnt[0] )
                    cmds.disconnectAttr ( pocList[i]+".positionY", outCnnt[1] )
                    cmds.disconnectAttr ( pocList[i]+".positionZ", outCnnt[2] )
                squintPlus = cmds.shadingNode( "plusMinusAverage", asUtility=1, n = LR + "squintPuffPlus" )
                #poc node1 connect
                cmds.connectAttr ( pocList[i]+".position", squintPlus+".input3D[0]" )
                cmds.setAttr( squintPlus+".input3D[1].input3Dx", -1*(cmds.getAttr( pocList[i]+".positionX" )) )
                cmds.setAttr( squintPlus+".input3D[1].input3Dy", -1*(cmds.getAttr( pocList[i]+".positionY" )) )
                cmds.setAttr( squintPlus+".input3D[1].input3Dz", -1*(cmds.getAttr( pocList[i]+".positionZ" )) )
                #loCheek_ctl connect
                cmds.connectAttr ( LR+"lidPuff_ctl.t", squintPlus+".input3D[2]" )           
                #lowCheek_ctl( on face ) connect
                cmds.connectAttr ( LR+"squintPuff_onCtl.t", squintPlus+".input3D[3]" )            
                #lowCheek_cls connect                         
                cmds.connectAttr ( squintPlus+".output3D", LR+"squintPuff_clsHandle.t", f=1 )
                
                

                
def ctlSetLimits( posTx, negTx, posTy, negTy, posTz, negTz ):
    #create popup menu
    ctls = cmds.ls(sl=1, fl =1, type = 'transform')
     
    for c in ctls:
        #set translate limits 
        if cmds.getAttr(c +'.translateX', lock =1 ) == False:
            cmds.transformLimits( c, translationX = ( negTx, posTx ), etx = (1,1) ) 
        if cmds.getAttr(c +'.translateY', lock =1 ) == False:
            cmds.transformLimits( c, translationY = (  negTy, posTy ), ety =(1,1) )
        if cmds.getAttr(c +'.translateZ', lock =1 ) == False:
            cmds.transformLimits( c, translationZ = ( negTz, posTz ), etz =(1,1) )
        '''    
        #set rotate limits
        if cmds.getAttr(c +'.rotateX', lock =1 ) == False:
            cmds.transformLimits( ctls[i], rotateX = ( -rotLimitX, rotLimitX ), erx =(1,1) )
        if cmds.getAttr(c +'.rotateX', lock =1 ) == False:
            cmds.transformLimits( ctls[i], rotateY = ( -rotLimitY, rotLimitY), ery =(1,1) )        
        if cmds.getAttr(c +'.rotateX', lock =1 ) == False:
            cmds.transformLimits( ctls[i], rotateZ = ( -rotLimitZ, rotLimitZ ), erz =(1,1) )''' 


#ctlSetLimits( .5, -.5, .8, -.6, 0, 0 )