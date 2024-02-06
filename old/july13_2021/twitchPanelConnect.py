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
        

#after all ctls have connections 
def getCtlList( grp ):
    
    if cmds.objExists( grp ):
        tmpChild = cmds.listRelatives( grp, ad=1, ni=1, type = ["nurbsCurve", "mesh", "nurbsSurface"]  )
        child = [ t for t in tmpChild if not "Orig" in t ]
        ctls = cmds.listRelatives( child, p=1 )
        ctlSet = set(ctls)
        ctlist = []
        for c in ctlSet:
            # check if ctl + .translateX/Y/Z connection exists
            for att in ["translate","rotate","scale","translateX","translateX","translateY","rotateZ","rotateY","rotateZ","scaleX","scaleY","scaleZ"]:
            
                cnnt = cmds.listConnections( "%s.%s"%(c, att ), s=1, d=1, c=1 )
                if cnnt:
                    ctlist.append(c)
                    break
        return ctlist
        

# = browCtl / eyeCtl / mouthCtl / bridgeCtl / detailCtl   
def storeCtlGrp_list(eyeBrowLipGrp):

    myGrp = cmds.ls(sl=1, typ ="transform" )
    if cmds.attributeQuery("%s_grp"%eyeBrowLipGrp, node = "helpPanel_grp", exists=1)==False:
        cmds.addAttr( "helpPanel_grp", ln ="%s_grp"%eyeBrowLipGrp, dt = "stringArray"  )
    cmds.setAttr("helpPanel_grp.%s_grp"%eyeBrowLipGrp, type= "stringArray", *([len(myGrp)] + myGrp))

    partGrp = cmds.getAttr( "helpPanel_grp.%s_grp"%(eyeBrowLipGrp))
    ctlList = []
    for grp in partGrp:
        ctls = getCtlList(grp)
        for c in ctls:
            ctlList.append(c)
        
    if cmds.attributeQuery("%s_list"%eyeBrowLipGrp, node = "helpPanel_grp", exists=1)==False:
        cmds.addAttr( "helpPanel_grp", ln ="%s_list"%eyeBrowLipGrp, dt = "stringArray"  )
    cmds.setAttr("helpPanel_grp.%s_list"%eyeBrowLipGrp, type= "stringArray", *([len(ctlList)] + ctlList))
        
        
 
    
def arFace_ctlList():

    browCtl =[ 'r_brow_UD','l_brow_UD','r_brow_Furrow','l_brow_Furrow','r_brow_madsad','l_brow_madsad' ]
    eyeCtl = [ 'r_eye_ctl','l_eye_ctl', 'riris_dial','liris_dial', 'l_eyeOffset_ctl','r_eyeOffset_ctl','eyeblend_dir','Reye_open','Leye_open',
    'r_eyeSquint','l_eyeSquint','l_lidHeight','r_lidHeight']
    mouthCtl = [ 'swivel_ctrl','mouth_move','jaw_drop','jaw_open','r_phonemes_ctl','r_mouth_happysad','l_mouth_happysad','l_phonemes_ctl','r_ShM','l_ShM' ]
    bridgeCtl = [ 'r_bridge_puffsuck', 'l_bridge_puffsuck', 'r_nose_flare', 'l_nose_flare', 'r_nose_sneer','l_nose_sneer']
    
    ctlDict = { "browCtl":[browCtl, "browCtl_grp","browDtailCtl_grp"], "eyeCtl": [eyeCtl, "eyeOnCtl_grp"], "mouthCtl": [mouthCtl,"lip_ctl_grp"], 
    "bridgeCtl":[bridgeCtl,"midCtl_grp" ], "detailCtl" : ["lip_dtailCtl_grp","browDtailCtl_grp"] }
    
    for regionCtl, ctlGrp in ctlDict.items():
        
        if cmds.attributeQuery("%s_list"%regionCtl, node = "helpPanel_grp", exists=1)==False:
            cmds.addAttr( "helpPanel_grp", ln ="%s_list"%regionCtl, dt = "stringArray"  )
        
        ctlList = []
        for cg in ctlGrp:
            if type(cg) == str:
                ctlList+= getCtlList( cg )
            else:
                ctlList+= cg  
        
        cmds.setAttr("helpPanel_grp.%s_list"%regionCtl, type= "stringArray", *([len(ctlList)] + ctlList) )


        

    
def all_main_detailCtls():
    ctlBranch = ['browCtl', 'eyeCtl', 'mouthCtl', 'bridgeCtl', 'detailCtl' ]
    allCtl = []
    for branch in ctlBranch[:-1]:

        ctls = cmds.getAttr( "helpPanel_grp.%s_list"%branch )
        allCtl += ctls
        
    detailCtl = cmds.getAttr( "helpPanel_grp.%s_list"%ctlBranch[-1] )
    mainCtl = [ x for x in allCtl if x not in detailCtl ]
    
    if cmds.attributeQuery("allCtl_list", node = "helpPanel_grp", exists=1)==False:
        cmds.addAttr( "helpPanel_grp", ln ="allCtl_list", dt = "stringArray" )
    cmds.setAttr("helpPanel_grp.allCtl_list", type= "stringArray", *([len(allCtl)] + allCtl))
    
    if cmds.attributeQuery("mainCtl_list", node = "helpPanel_grp", exists=1)==False:
        cmds.addAttr( "helpPanel_grp", ln ="mainCtl_list", dt = "stringArray" )
    cmds.setAttr("helpPanel_grp.mainCtl_list", type= "stringArray", *([len(mainCtl)] + mainCtl))    


    
def addItemToArray( ctlList, items ):
    print items
    strList = cmds.getAttr("helpPanel_grp." + ctlList + "_list" )
    for i in items:
        strList.append( i )
        
    #remove duplicate in the list
    newList = []
    for str in strList:
        if str not in newList:
            newList.append(str)
            
    cmds.setAttr("helpPanel_grp." + ctlList + "_list" , type= "stringArray", *([len(newList)] + newList))
    
    

#eyeBrowLipGrp = browCtl_list/eyeCtl_list/mouthCtl_list/bridgeCtl_list/allCtl_list...
def create_ctlSets(clist):
    ctlList = cmds.getAttr( "helpPanel_grp.%s"%(clist))
    setName = clist.replace("_list","_set") 
    if cmds.objExists( setName ):
        cmds.sets( e=1, cl =setName )
        cmds.sets( ctlList, e=1, add= setName )
    else:
        ctlSet = cmds.sets( ctlList, n= setName )
    
    
    
    
def resetCtrl(facePart):

    cmds.select("%s_set"%facePart, r=1)
    ctrls = cmds.ls( sl=1, typ="transform")
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
    cmds.select(cl=1)
    
    
                
def setKeysOnCtl(facePart):
    cmds.select("%s_set"%facePart, r=1)
    ctrls = cmds.ls( sl=1, typ="transform")
    for ct in ctrls:    
        attrs = cmds.listAttr( ct, k=1, unlocked = 1 )
        for at in attrs:
            cmds.setKeyframe( ct, attribute=at )

                
        
def deleteCtrlKeys(facePart):
    cmds.select("%s_set"%facePart, r=1)
    ctrls = cmds.ls( sl=1, typ="transform")

    for ct in ctrls:    
        attrs = cmds.listAttr( ct, k=1, unlocked = 1 )
        for at in attrs:
            keyCount = cmds.keyframe( ct+"."+ at, query=True, keyframeCount=True )
            if keyCount:            
                cmds.cutKey( ct+"."+at )


    
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
            cmds.transformLimits( ctls[index], rotateX = ( -rotLimitX, rotLimitX ), erx =(1,1) )
        if cmds.getAttr(c +'.rotateX', lock =1 ) == False:
            cmds.transformLimits( ctls[index], rotateY = ( -rotLimitY, rotLimitY), ery =(1,1) )        
        if cmds.getAttr(c +'.rotateX', lock =1 ) == False:
            cmds.transformLimits( ctls[index], rotateZ = ( -rotLimitZ, rotLimitZ ), erz =(1,1) )'''


#ctlSetLimits( .5, -.5, .8, -.6, 0, 0 )



def arFacePanel_transfer():
    
    #Ctls on face setup
    ctlDict = { "eye_ctl":"eyeDir_ctl", "eyeOffset_ctl":"offset_ctl", "liris_dial":"l_irisDial_ctl", "riris_dial":"r_irisDial_ctl",
    "mouth_happysad":"happySad_ctl", "phonemes_ctl": "phoneme_ctl", "up_ShM": "up_ShM_ctl", "lo_ShM": "lo_ShM_ctl", 
     "eyeSquint":"eyeSquint_ctl", "lidHeight":"lidScale_ctl", "Leye_open":"l_eyeOpen_ctl","Reye_open":"r_eyeOpen_ctl", "brow_madsad":"madSad_ctl",
     "jaw_drop":"jawDrop_ctl", "jaw_open":"jawOpen_ctl", "mouth_move":"mouthMove_ctl", "swivel_ctrl":"swivel_ctl", "bridge_puffsuck":"puffsuck",
     "lipCorner":"lipCorner_ctl", "eyeblend_dir":"eyeAim_ctl" }
    
    extra = { "flareSneer_ctl":[ "nose_flare", "nose_sneer" ], "browUD_ctl":[ "brow_Furrow", "brow_UD" ] }
    
    lipEPos = cmds.getAttr( "helpPanel_grp.lipEPos" )
    eyePos = cmds.getAttr( "helpPanel_grp.lEyePos" )
    #position fix
    pocs = cmds.ls("lo_lipGuide*_poc")
    if pocs:
        centerPoc = cmds.getAttr( pocs[ (len(pocs)-1)/2 ] + ".position" )[0]
    
    postion = { "phoneme_grp":lipEPos, "lidShape_grp":eyePos, "jawCtl_grp":centerPoc  }
    for srcGrp, pos in postion.items():
        
        if cmds.objExists("l_"+srcGrp):
            for LR in ["l_","r_"]:    
            
                if LR == "r_":
                    pos = [ -pos[0], pos[1], pos[2] ]
                
                cmds.xform( LR+srcGrp, ws=1, t = pos )            
        else:
            
            cmds.xform( srcGrp, ws=1, t = pos )          
            
    for LR in ["l_","r_"]:
                                 
        for srcCtl, tgtCtl in ctlDict.items():
            
            if cmds.objExists( LR+srcCtl ):                                  

                replaceNodeConnection( LR + srcCtl, LR + tgtCtl )
                
                if LR + srcCtl == "r_lipCorner":                        
                    outAtt = cmds.listConnections( LR + tgtCtl + ".tx", s=0, d=1 )              
                    clamp =[ x for x in outAtt if cmds.nodeType(x) == "clamp" ][0]
                    xPos = cmds.listConnections( clamp + ".inputR", s=1, d=0, p=1 )
                    xNeg = cmds.listConnections( clamp + ".inputG", s=1, d=0, p=1 )
                    cmds.connectAttr( xPos[0],  clamp + ".inputG", f=1 )
                    cmds.connectAttr( xNeg[0],  clamp + ".inputR", f=1 )
                    print clamp + " is for r_lipCorner" 
                    
                elif srcCtl == "phonemes_ctl":
                    xPos = cmds.listConnections("lipFactor.%sphonemeX_pos"%LR, s=1, d=0, p=1 ) #ctl.tx
                    xNeg = cmds.listConnections("lipFactor.%sphonemeX_neg"%LR, s=1, d=0, p=1 ) #mult.outputX
                    cmds.connectAttr( xPos[0],  "lipFactor.%sphonemeX_neg"%LR, f=1 )
                    cmds.connectAttr( xNeg[0],  "lipFactor.%sphonemeX_pos"%LR, f=1 )                  
                
                elif srcCtl == "brow_madsad":
                    mult =[ x for x in cmds.listConnections( LR + tgtCtl + ".tx", s=0, d=1 ) if cmds.nodeType(x) == "multiplyDivide" ][0]
                    cmds.setAttr( mult + ".input2X", 1 )
                    print mult + " is for browMad" 

                elif srcCtl == "lo_ShM":
                    clamp =[ x for x in cmds.listConnections( LR + tgtCtl + ".ty", s=0, d=1 ) if cmds.nodeType(x) == "clamp" ][0]
                    xPos = cmds.listConnections( clamp + ".inputR", s=1, d=0, p=1 )
                    xNeg = cmds.listConnections( clamp + ".inputG", s=1, d=0, p=1 )
                    cmds.connectAttr( xPos[0],  clamp + ".inputG", f=1 )
                    cmds.connectAttr( xNeg[0],  clamp + ".inputR", f=1 )
                    print clamp + " is for SH" 
                    
                elif srcCtl == "bridge_puffsuck":
                    toAttr = cmds.listConnections( LR + tgtCtl + ".ty", s=0, d=1, p=1 )
                    if toAttr:
                        for at in toAttr:
                            cmds.connectAttr( LR + tgtCtl + ".tx", at, f=1 )
                                                 
            else:
                print tgtCtl
    
                replaceNodeConnection( srcCtl, tgtCtl )     
                        

    for lr in ["l_","r_"]:
        for tgt, src in extra.items():
            for child in src:
                if cmds.objExists(lr + child):
        
                    outCnnt = cmds.listConnections( lr + child, s=0, d=1, p=1, c=1)
                    if outCnnt:
                        for s, d in zip(*[iter(outCnnt)]*2):
                            
                            if not cmds.nodeType(d.split(".")[0]) == "shadingEngine":
                                srcAttr = s.split(".")[1]
                                cmds.disconnectAttr( s, d )
                                if "nose_flare" in s or "brow_Furrow" in s:
                                    if "translateY" in srcAttr:
                                        srcAttr = "translateX"
                                cmds.connectAttr( lr + tgt +'.'+ srcAttr, d, f=1 )
                    
                        if child == "brow_Furrow":

                            clamp =[ x for x in cmds.listConnections( lr + tgt +'.tx', s=0, d=1 ) if cmds.nodeType(x) == "clamp" ][0]
                            print clamp + " is for brow"
                            xPos = cmds.listConnections( clamp + ".inputR", s=1, d=0, p=1 )
                            xNeg = cmds.listConnections( clamp + ".inputG", s=1, d=0, p=1 )
                            cmds.connectAttr( xPos[0],  clamp + ".inputG", f=1 )
                            cmds.connectAttr( xNeg[0],  clamp + ".inputR", f=1 )

    UpLoDict = { "up":0,"lo":1 }
    for UpLo, val in UpLoDict.items():
        if cmds.objExists(UpLo + "teeth_motion") and cmds.objExists(UpLo + "teeth_motion_ctl"):
            replaceNodeConnection( UpLo + "teeth_motion", UpLo + "teeth_motion_ctl" )
            teethMult = [ i for i in cmds.listConnections( UpLo + "teeth_motion_ctl", s=0, d=1 ) if cmds.nodeType(i)=="multiplyDivide" ]
            teethTRSP = "teeth%sTRSP"%UpLo.title()
            if teethMult:
                
                cmds.connectAttr( UpLo + "teeth_motion_ctl.tz",  teethMult[0] + ".input1Z", f=1 )
                cmds.setAttr( teethMult[0] + ".input2X", .5 )
                cmds.setAttr( teethMult[0] + ".input2Y", .5 )
                teethSum = [ i for i in cmds.listConnections( teethMult, s=0, d=1 ) if cmds.nodeType(i)=="plusMinusAverage" ][0]
                cmds.connectAttr( teethMult[0] + ".outputZ",  teethSum + ".input3D[%s].input3Dz"%val, f=1 )
                cmds.connectAttr( teethMult[0] + ".outputX", teethSum + ".input3D[%s].input3Dx"%val, f=1 )
                cmds.connectAttr( UpLo + "teeth_motion_ctl.sx",  teethTRSP + ".sx", f=1 )
                cnnt = cmds.listConnections( teethTRSP + ".sy", s=1, d=0, p =1 )
                
                if cnnt:
                    cmds.disconnectAttr( cnnt[0], teethTRSP + ".sy" )
                
                cmds.connectAttr( UpLo + "teeth_motion_ctl.sy",  teethTRSP + ".sy", f=1 )

            

def replaceNodeConnection( source, target ):
                      
    dnCnnt = cmds.listConnections( source, s=0, d=1, p=1, c=1)
    
    if dnCnnt:
        for s, d in zip(*[iter(dnCnnt)]*2):
            if not cmds.nodeType(d.split(".")[0]) == "shadingEngine": 
                scAttr = s.split(".")[1]
                cmds.disconnectAttr( s, d )
                cmds.connectAttr( target +'.'+ scAttr, d, f=1 )
                print s +"  and " + target+'.'+ scAttr
                
                
                
#get ctl list : getArCtlList( "shapeCtl_onFace_grp" )     
def getArCtlList( grp ):

    tmpChild = cmds.listRelatives( grp, ad=1, ni=1, type = ["nurbsCurve", "mesh", "nurbsSurface"] )
    child = [ t for t in tmpChild if "_ctl" in t ]
    ctlSet = set()
    for ct in child:
        ctl = cmds.listRelatives( ct, p=1 )[0]
    
        ctlSet.add(ctl)
    ctlist = []
    for it in ctlSet:
        ctlist.append(it) 
    return (ctlist)
    


# both "twitchPanel" and "arFaceCtl_grp" are required
def updateArFace_ctlSet():
    
    ctlDict = { "eye_ctl":"eyeDir_ctl", "eyeOffset_ctl":"offset_ctl", "liris_dial":"l_iris_dial", "riris_dial":"r_iris_dial",
    "mouth_happysad":"happySad_ctl", "phonemes_ctl": "phoneme_ctl", "up_ShM": "up_ShM_ctl", "lo_ShM": "lo_ShM_ctl", 
     "eyeSquint":"eyeSquint_ctl", "lidHeight":"lidScale_ctl", "eye_open":"eyeOpen_ctl", "brow_madsad":"madSad_ctl",
     "jaw_drop":"jawDrop_ctl", "jaw_open":"jawOpen_ctl", "mouth_move":"mouthMove_ctl", "swivel_ctrl":"swivel_ctl", "bridge_puffsuck":"puffsuck" }
    
    extra = { "flareSneer_ctl":[ "nose_flare", "nose_sneer" ], "browUD_ctl":[ "brow_Furrow", "brow_UD" ] }
    ctlSets = ["allCtl_set", "mainCtl_set", "detailCtl_set", "browCtl_set", "eyeCtl_set", "mouthCtl_set" ]
    
    for ctSet in ctlSets:        
        for srcCtl, tgtCtl in ctlDict.items():    
                
            if cmds.objExists( LR + tgtCtl ):
                
                for LR in ["l_","r_"]:       
                    
                    cmds.sets( LR + srcCtl, rm= ctSet )
                    cmds.sets( LR + tgtCtl, add= ctSet )
        
            elif cmds.objExists( tgtCtl ):
                
                cmds.sets( srcCtl, rm= ctSet )
                cmds.sets( tgtCtl, add= ctSet )
                
        
# miscellaneous_____________________________________________________________________________________________________________


# in : replace input connection 
# out : replace output connection
# select node with connections and select the node For Replacement
def transferConnections( node_shape, in_out ):
    nodeSel = cmds.ls(sl=1 )
    print nodeSel
    if node_shape == 'node':
        source = nodeSel[0]
        target = nodeSel[1]
    
    elif node_shape == 'shape':
        source = cmds.listRelatives(nodeSel[0], c=1)[0]

        target = cmds.listRelatives(nodeSel[1], c=1)[0]        

    replaceNodeInConnection( source, target, in_out )



# get list connection( both source, destination ) and replace the source node
def replaceNodeInConnection( source, target, in_out ):
    if in_out == 'in':
        scCnnt = cmds.listConnections( source, s=1, d=0, p=1, c=1 )
        if scCnnt:
            print scCnnt
            for dn, sc in zip(*[iter(scCnnt)]*2):
                attr = dn.split(".")[1]
                cmds.disconnectAttr( sc, dn )
                cmds.connectAttr( sc, target + '.'+ attr, f=1 )
                
    if in_out == 'out':                        
        dnCnnt = cmds.listConnections( source, s=0, d=1, p=1, c=1)
        print source +"  and " + target
        if dnCnnt:
            for s, d in zip(*[iter(dnCnnt)]*2):
                if not cmds.nodeType(d.split(".")[0]) == "shadingEngine": 
                    scAttr = s.split(".")[1]
                    cmds.disconnectAttr( s, d )
                    cmds.connectAttr( target +'.'+ scAttr, d, f=1 )


# select list to be removed and lastly set
def editDeformerSet(): 
    obj = cmds.ls(sl=1, type = 'transform')
    objShape = cmds.listRelatives(obj[0], c=1, ni=1 )[0]
    setList = cmds.listConnections( objShape, s=1, d=0, t = 'objectSet' )
 
def removeItems_deformerSet( set ):
    cmds.sets(cmds.ls(sl=True, fl=1), e=1, rm= set)

def addItems_deformerSet( mySet ):
    xx = cmds.ls(sl=1, fl=1)
    cmds.sets(xx , add= mySet )



