# -*- coding: utf-8 -*-
''' 
update/ add script
*11/12/2017
    1. faceClusters() update
    2. updateFaceCluster()
    3. browWideJnt()
*10/23/2017
    1.symmetrizeCurve()
    2.copyClusterWgt()
    3.update browUp/Dn_cls in calExtraClsWgt() 

-"nose_ctl" position fix
headSkin : 텍스트 필드의 오브젝트를 받아, 모든 디포머를 no effect 상태로 만들고 헤드 스키닝한다.

1. surfMap Skin ( 각가의 부의별 메쉬를 V방향으로 100% 스키닝 )
2. arFaceHeadSkin : 텍스트 필드 'head_REN'인 경우, 모든 디포머를 no effect 상태로 만들고 두개의 헤드 originalShape을 카피한다. 하나씩 헤드 스키닝(interactive normalize)한다.
3. exportFaceSkinWeights():    
    A.각각의 'head'의 스킨웨이트를 'headSkel'에 몰빵 (카피하기 전 웨이트값을 깨끗한게 노말라이즈된 백지상태로 )
    B.각각의 메쉬 웨이트맵surf map(lipTip_map/ eyeTip_map/ browMapSurf) weight을 머리에 카피하고 노말라이즈시킨다. 
    C."head"들의 카피된 skinWeight값을 각각 xml export  
    checking point!!! : 만약 맵에 문제가 있다면 나중에 문제를 찾아내기가 매우 어렵다. 

4. faceWeightCalculate :
    A. we must set the normalizeWeights attribute to 0(none), otherwise Maya would normalize the skinweights with each iteration we add weights. 
    B. faceWeightCalculate() = set weight back to 1 on the headSkel_jnt, 얼굴 맵 xml 파일들을 임포트하고 데이터들을 계산해서 얼굴 웨이트를 만든다. (calculateFaceWgt = jawClose + cheek weight > 1 경우, 마이너스값을 cheek weight에서 빼준다.) 

    *update map: 
1. when change map weight --> export the updated map(lipMap, eyeLidMap, browMap )
2. when change cluster --> export faceWgt
'''

import maya.cmds as cmds
import maya.mel as mel
import re
import xml.etree.ElementTree as ET
import os
from twitchScript import squachSetup
reload(squachSetup)
import math
from twitchScript import BCDtypeCtrlSetup
reload(BCDtypeCtrlSetup)


def removeVertMark():
    myGeo = cmds.ls( sl=1, type = 'transform' )
    history = cmds.listHistory( myGeo[0] )    
    
    for nd in history:
        if cmds.nodeType(nd) == 'polyColorPerVertex':
            print nd
            cmds.delete( nd )            
        else:
            cmds.polyColorPerVertex( myGeo[0], rem=True )


def deformerToggle():
    myGeo = cmds.ls( sl=1, type = 'transform' )
    deforms =[nd for nd in cmds.listHistory(myGeo[0]) if cmds.nodeType(nd) in ['cluster', 'blendShape', 'ffd'] ]
    for df in deforms:
        bool = cmds.getAttr( df + '.nodeState')
        print bool
        if bool == 1:
            cmds.setAttr( df + '.nodeState', 1-bool)
            print df + "   ON!!"
        elif bool == 0:
            cmds.setAttr( df + '.nodeState', 1-bool)
            print df + "  OFF!!"
            


""" create circle controller(l_/r_/c_) and parent group at the position
    shape : circle = cc / square = sq 
    colorNum : 13 = red, 15 = blue, 17 = yellow, 18 = lightBlue, 20 = lightRed, 23 = green
    return [ ctrl, ctrlP ]
24 똥색 / 23:숙색 / 22:밝은 노랑 / 21:밝은 주황 / 20: 밝은 핑크 / 19: 밝은연두 / 18: 하늘색 / 17 yellow / 16 white
15: dark blue / 14: bright green / 13: red / 12: red dark 자두색 / 11: 고동색 / 10: 똥색 / 9: 보라 / 8: 남보라
7: 녹색 / 6: 파랑 / 5 : 남색 / 4 : 주황 / 3 : 회색 / 2: 진회색 / 1: 검정"""
def genericController( ctlName, position, radius, shape, colorId ):

    if shape in ["cc", "circle"]:
        degree = 3 # cubic
        section = 8 # smooth circle
        
    elif shape in [ "sq", "square" ]:
        degree = 1 # linear
        section = 4 # straight line

    else:
        print 'shape = either "cc"(circle) or "sq"(square)'
    
    #if none of c_, l_, r_
    circleCtrl = cmds.circle (n = ctlName, ch=False, nr=(0, 0, 1), c=(0, 0, 0), sw=360, r= radius, d=degree, s=section )
    cmds.setAttr (circleCtrl[0] +".overrideEnabled", 1 )
    cmds.setAttr (circleCtrl[0] +".overrideShading", 0 )
    cmds.setAttr (circleCtrl[0] + ".overrideColor", colorId )
    null = cmds.group (circleCtrl[0], w =True, n = circleCtrl[0]+"P")
    cmds.xform (null, ws = True, t = position )
    ctrl = [circleCtrl[0], null]
    return ctrl
	


            
def faceClusters():
    headGeo = cmds.getAttr("helpPanel_grp.headGeo")  
    #xmin ymin zmin xmax ymax zmax (face bounding box)
    facebbox = cmds.xform( headGeo, q=1, boundingBox =1 )
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
    clusterDict = { 'jawRigPos': ['jawOpen_cls', 'jawClose_cls' ], 'lipYPos':'lip_cls', 'lipRollPos':'lipRoll_cls', 'lipNPos': 'upLipRoll_cls', 'lipSPos': 'bttmLipRoll_cls', 
    'cheekPos':['l_cheek_cls','r_cheek_cls'], 'lEyePos':[ 'eyeWide_cls', 'eyeBlink_cls'], 'lowCheekPos': ['l_lowCheek_cls', 'r_lowCheek_cls'], 
    'squintPuffPos':['l_squintPuff_cls', 'r_squintPuff_cls'], 'lEarPos':['l_ear_cls','r_ear_cls'], 'rotXPivot':['browUp_cls','browDn_cls'], 'rotYPivot':'browTZ_cls', 'nosePos': 'nose_cls' }
    
    locators = cmds.listRelatives('allPos', ad =1, type = 'transform' )
    for k in clusterDict.keys():
        if not k in locators:
            print "there is a faceLocators naming problem"   
    
    cls = cmds.cluster( headGeo, n= 'mouth_cls', bindState =1 )
    cmds.select(headGeo, r=1)
    cmds.percent( cls[0], v=0.0 )
    cmds.group( cls[1], p= "cls_grp", n= cls[0]+"P" )
    
    null = cmds.group( em =1, name = "midCtl_grp", parent='attachCtl_grp' )

    for loc, clsName in clusterDict.items():
        ctlPos = cmds.xform ( loc, q= 1, ws =1 , t=1 )
        distance = facebbox[5]- ctlPos[2]
        tranZ = (facebbox[5]-facebbox[2])/20
        index =4
        if len(clsName) == 2:
            #clusters to be included for face rig
            if loc == 'lEyePos':           

                mirrLoc = cmds.spaceLocator(  n= loc.replace("lEye","rEye") )[0]
                cmds.parent(mirrLoc, 'allPos')
                unitMult = cmds.shadingNode( "multiplyDivide", asUtility=1, n = mirrLoc + "_mult" )
                cmds.setAttr( unitMult + ".input2X", -1 )
                cmds.connectAttr( loc + ".tx", unitMult + ".input1X" )
                cmds.connectAttr( loc + ".ty", unitMult + ".input1Y" )
                cmds.connectAttr( loc + ".tz", unitMult + ".input1Z" )
                cmds.connectAttr( unitMult + ".outputX", mirrLoc + ".tx" )
                cmds.connectAttr( unitMult + ".outputY", mirrLoc + ".ty" )
                cmds.connectAttr( unitMult + ".outputZ", mirrLoc + ".tz" )                
            
                colorList = [18, 14, 4, 12, 11, 10, 2, 6 ]
                # 'eyeBlink_cls', 'eyeWide_cls' 
                for cls in clsName:                    
                    index-=1
                    lCtlCls =  clusterForSkinWeight( loc, zDepth, "l_"+ cls, "faceClsFrame", rad*index, 4, colorList[index+1] )
                    rCtlCls =  clusterForSkinWeight( mirrLoc, zDepth, "r_"+ cls, "faceClsFrame", rad*index, 4, colorList[index+1] )
                    tranToRot_mult( lCtlCls, 30 )
                    tranToRot_mult( rCtlCls, 30 )
                    
            elif loc in ['lowCheekPos', 'cheekPos', 'squintPuffPos' ]:
                
                mirrLoc = cmds.spaceLocator(  n= loc.replace("Pos","Mirr") )[0]
                cmds.parent(mirrLoc, 'allPos')
                unitMult = cmds.shadingNode( "multiplyDivide", asUtility=1, n = mirrLoc + "_mult" )
                cmds.setAttr( unitMult + ".input2X", -1 )
                cmds.connectAttr( loc + ".tx", unitMult + ".input1X" )
                cmds.connectAttr( loc + ".ty", unitMult + ".input1Y" )
                cmds.connectAttr( loc + ".tz", unitMult + ".input1Z" )
                cmds.connectAttr( unitMult + ".outputX", mirrLoc + ".tx" )
                cmds.connectAttr( unitMult + ".outputY", mirrLoc + ".ty" )
                cmds.connectAttr( unitMult + ".outputZ", mirrLoc + ".tz" )
                offsetOnFace = [ 0,0,tranZ ]
                print clsName
                lCtlJnt = clusterOnJoint( loc, clsName[0], "midCtl_grp", offsetOnFace, rad, 8 )
                rCtlJnt = clusterOnJoint( mirrLoc, clsName[1], "midCtl_grp", offsetOnFace, rad, 8 )               

                for at in [ "t","r","s"]:
                    cmds.connectAttr( lCtlJnt[0] + "." + at, lCtlJnt[1] + "."+ at ) 
                    cmds.connectAttr( rCtlJnt[0] + "." + at, rCtlJnt[1] + "."+ at )                            
                
            elif loc == "lEarPos":
            
                mirrLoc = cmds.spaceLocator(  n= loc.replace("Pos","Mirr") )[0]
                cmds.parent(mirrLoc, 'allPos')
                unitMult = cmds.shadingNode( "multiplyDivide", asUtility=1, n = mirrLoc + "_mult" )
                cmds.setAttr( unitMult + ".input2X", -1 )
                cmds.connectAttr( loc + ".tx", unitMult + ".input1X" )
                cmds.connectAttr( loc + ".ty", unitMult + ".input1Y" )
                cmds.connectAttr( loc + ".tz", unitMult + ".input1Z" )
                cmds.connectAttr( unitMult + ".outputX", mirrLoc + ".tx" )
                cmds.connectAttr( unitMult + ".outputY", mirrLoc + ".ty" )
                cmds.connectAttr( unitMult + ".outputZ", mirrLoc + ".tz" )
                lOffset = [ tranZ, 0,0 ]
                rOffset = [ -tranZ, 0,0 ]
                
                lCtlJnt = clusterOnJoint( loc, clsName[0], "midCtl_grp", lOffset, rad, 8 )
                rCtlJnt = clusterOnJoint( mirrLoc, clsName[1], "midCtl_grp", rOffset, rad, 8 )               

                for at in [ "t","r","s"]:
                    cmds.connectAttr( lCtlJnt[0] + "." + at, lCtlJnt[1] + "."+ at ) 
                    cmds.connectAttr( rCtlJnt[0] + "." + at, rCtlJnt[1] + "."+ at )
                    
            elif loc == "rotXPivot": #browUD_cls 
            
            	ctlUpJnt = clusterForSkinWeight( loc, zDepth, clsName[0], "faceClsFrame", rad*2, 4, 21 )#square/orange
            	tranToRot_mult( ctlUpJnt, 10 )
            	ctlDnJnt = clusterForSkinWeight( loc, zDepth, clsName[1], "faceClsFrame", rad*3, 6, 12 )#hexagon/plum
            	tranToRot_mult( ctlDnJnt, 10 )
            
            elif loc == "jawRigPos":#'jawOpen_cls', 'jawClose_cls'
            
                colorList = [18, 14, 4, 12, 11, 10, 2, 6 ]
                for cls in clsName:
                    index-=1
                    ctlJnt =  clusterForSkinWeight( loc, zDepth, cls, "faceClsFrame", rad*index, 4, colorList[index+1] )
                    tranToRot_mult( ctlJnt, 30 )
                    if cls == "jawClose_cls":
                        cmds.hide(ctlJnt[0])
      
        else:
            print loc, clsName    
            if loc == 'lipYPos': #'lip_cls'

				ctlJnt = clusterForSkinWeight( loc, zDepth, clsName, "faceClsFrame", rad*2, 4, 10 )#square/lightBrown
				tranToRot_mult( ctlJnt, 10 )
            
            elif loc =='lipNPos': #'uplipRoll_cls'
				ctlJnt = clusterForSkinWeight( loc, zDepth, clsName, "faceClsFrame", rad/2, 16, 20 )#square /pink
				tranToRot_mult( ctlJnt, 10 )

            elif loc =='lipSPos': #'bttmlipRoll_cls'
				ctlJnt = clusterForSkinWeight( loc, zDepth, clsName, "faceClsFrame", rad/2, 16, 21 )#square /pink
				tranToRot_mult( ctlJnt, 10 )

            elif loc =='rotYPivot': #'browTZ_cls'

				ctlJnt = clusterForSkinWeight( loc, zDepth, clsName, "faceClsFrame", rad, 8, 19  )                
				for at in [ "t","r","s"]:
					cmds.connectAttr( ctlJnt[0] + "." + at, ctlJnt[1] + "."+ at )
				cmds.setAttr( cmds.listRelatives(ctlJnt[0], p=1, type='transform')[0] + '.tx', 0 )
            
            elif loc =='nosePos' : # 'nose_cls'
				offset = [ 0,0, distance*1.2 ]
				ctlJnt = clusterOnJoint( loc, clsName, "midCtl_grp", offset, rad, 12 )                
				for at in [ "t","r","s"]:
					cmds.connectAttr( ctlJnt[0] + "." + at, ctlJnt[1] + "."+ at )
                    
            else:				
				ctlJnt = clusterForSkinWeight( loc, zDepth, clsName, "faceClsFrame", rad, 8, 9 )                
				for att in [ "t","r","s"]:
					cmds.connectAttr( ctlJnt[0] + "." + att, ctlJnt[1] + "."+ att ) 
    
	cmds.setAttr( "faceClsFrame.tx", xMax*2 )
                



# delete all the cluster related items
def deleteClusterLayer():

    # recreate clusters on face
    clsGrps = cmds.listRelatives( "cls_grp", c=1 )
    if clsGrps:
        cmds.delete( clsGrps )
            
        if cmds.objExists("allPos"):
            locs = ["lipRollPos", "rEyePos", "lowCheekMirr", "cheekMirr", "lEarMirr", "squintPuffMirr"]
            for loc in locs:
                if cmds.objExists( loc ):
                    cmds.delete(loc)
                    
        # recreate ctls on face
        if cmds.objExists("midCtl_grp"): 
            ctls = cmds.listRelatives( "midCtl_grp", c=1 )
            if ctls:
                cmds.delete( ctls )         
    
                
        if cmds.objExists("faceClsFrame"):
            cmds.delete("faceClsFrame")
        
    else:
        cmds.confirmDialog( title='Confirm', message='create faceClusters first!!' )
        
        


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
def clusterOnJoint( loc, clsName, ctlP, offset, rad, sect ):         
    headGeo = cmds.getAttr("helpPanel_grp.headGeo") 
    clsPos = cmds.xform ( loc, q= 1, ws =1 , t=1 )
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
    handle = cmds.group( em=1, p = clsP, name= clsName + 'Handle' )     
    clsNode = cmds.cluster( headGeo, n= clsName, bindState =1, wn = ( handle, handle))
    cmds.select(headGeo, r=1)
    cmds.percent( clsNode[0], v=0.0 )
    return [ctl[0], handle]


    

    
#update rotateY ( from locator to clsParent )    
#create joint for cluster and ctrl
#place ctlP for easy grab ( "faceLoc_grp| "faceClsFrame" or "attachCtl_grp"|"midCtl_grp" )
def clusterForSkinWeight( loc, zDepth, clsName, ctlP, rad, sect, colorID ):       
    
    headGeo = cmds.getAttr("helpPanel_grp.headGeo") 
    clsPos = cmds.xform ( loc, q= 1, ws =1 , t=1 )
    clsRot = cmds.xform ( loc, q= 1, ws =1 , ro=1 )
    position = (clsPos[0], clsPos[1], zDepth )
    ctlName = clsName.replace( 'cls', 'ctl')
    ctl = genericController( ctlName , position, rad, "sq", colorID )
    cmds.parent( ctl[1], ctlP, r=1 )
    cmds.select(cl=1)
    
    clsP = cmds.group( n= clsName.replace("cls","clsP"), em=1, p = "faceMain|cls_grp" )
    cmds.xform(clsP,  ws=1, t = clsPos )
    cmds.xform(clsP,  ws=1, ro = (0, clsRot[1] ,0) )
    handle =cmds.group( em=1, p = clsP, name= clsName + 'Handle' )     
    clsNode = cmds.cluster( headGeo, n= clsName, bindState =1, wn = ( handle, handle))
    cmds.select( headGeo, r=1)
    cmds.percent( clsNode[0], v=0.0 )
    return [ctl[0], handle]





#update cluster layer( then use updateHierachy_FaceMain() for updating Hierachy ) :run script to update cluster handle's rotatePivot     
def updateFaceCluster():    

    clusterDict = { 'jawRigPos': ['jawOpen_cls', 'jawClose_cls'], 'headSkelPos':['mouth_cls'], 'lipYPos':['lip_cls'], 'lipRollPos':['lipRoll_cls'], 'cheekPos':['l_cheek_cls','r_cheek_cls'], 
    'lEyePos':['l_eyeBlink_cls', 'l_eyeWide_cls'], 'rEyePos':['r_eyeBlink_cls', 'r_eyeWide_cls'], 'lowCheekPos': ['l_lowCheek_cls', 'r_lowCheek_cls'], 'squintPuffPos':['l_squintPuff_cls', 'r_squintPuff_cls'], 
    'lEarPos':['l_ear_cls','r_ear_cls'], 'rotXPivot':['browUp_cls','browDn_cls'], 'rotYPivot':['browTZ_cls'], 'nosePos': ['nose_cls'], 'lipNPos': ['upLipRoll_cls'], 'lipSPos': ['bttmLipRoll_cls'] }

    for loc, cls in clusterDict.iteritems():       

        if len(cls)==2:
            
            handles = [] 
            for cl in cls:
                hand = cmds.listConnections(cl +".matrix", s=1, d=0, type="transform")[0]
                handles.append(hand)
            newPos = cmds.xform( loc, t = True, q = True, ws = True )
            oldPos = cmds.xform( handles[0], t = True, q = True, ws = True )
            if oldPos == newPos:
                pass
                
            else:
                                 
                if "l_" in cls[0] and "r_" in cls[1]:

                    cmds.xform( handles[0], ws=1, rotatePivot = newPos )
                    clsParent = cmds.listRelatives( handles[0], p =1 )[0]
                    cmds.xform( clsParent, ws=1, piv = newPos )
                                
                    mirrorPos = [-newPos[0], newPos[1], newPos[2] ]
                    cmds.xform( handles[1], ws=1, rotatePivot = mirrorPos )
                    clsParent = cmds.listRelatives( handles[1], p =1 )[0]                    
                    cmds.xform( clsParent, ws=1, piv = mirrorPos )        

                else:
                    
                    for i, C in enumerate(cls):
                        print cls, handles[i]
                        cmds.xform( handles[i], ws=1, rotatePivot = newPos )
                        clsParent = cmds.listRelatives( handles[i], p =1 )[0]
                        cmds.xform( clsParent, ws=1, piv = newPos )
                        print handles, clsParent
                                           
        else:
            
            if cmds.objExists(cls[0]):

                handle = cmds.listConnections( cls[0] +".matrix", s=1, d=0, type="transform" )                
                currentPos = cmds.xform( loc, t = True, q = True, ws = True )
                oldPos = cmds.xform( handle, t = True, q = True, ws = True )
                if oldPos == newPos:
                    pass
                    
                else:           
                    cmds.xform( handle, ws=1, rotatePivot = currentPos )
                    clsParent = cmds.listRelatives( handles, p =1 )[0]                    
                    cmds.xform( clsParent, ws=1, piv = currentPos )       
     

        





        
#update 12/26/2019 : getJointIndex(skinCluster:update , jointName )      
#update 5/9/2019 : browDown_jnt, browTz weight will get cut by browUp weight
#update 10/25/2017 : browUp/Dn , browWide_jnt setup
#set the headSkin weight to 1 on headSkel_jnt before calculate
#import the xml weight file and calculate the jaw joint weight 
def faceWeightCalculate():   

    headGeo = cmds.getAttr("helpPanel_grp.headGeo")
    skinCls = mel.eval("findRelatedSkinCluster %s"%headGeo )
    print skinCls
    size = cmds.polyEvaluate( headGeo, v = 1)
    lipWgt = cmds.getAttr ("lip_cls.wl[0].w[0:"+str(size-1)+"]")
    rollWgt = cmds.getAttr ("lipRoll_cls.wl[0].w[0:"+str(size-1)+"]")
    jawOpenWgt = cmds.getAttr ("jawOpen_cls.wl[0].w[0:"+str(size-1)+"]")
    jawCloseWgt = cmds.getAttr ("jawClose_cls.wl[0].w[0:%s]"%str(size-1))
    mouthWgt = cmds.getAttr ("mouth_cls.wl[0].w[0:%s]"%str(size-1))
    cheekWgt = cmds.getAttr ( "l_cheek_cls.wl[0].w[0:%s]"%str(size-1))
    browUpWgt = cmds.getAttr ( "browUp_cls.wl[0].w[0:%s]"%str(size-1))
    browDnWgt = cmds.getAttr ( "browDn_cls.wl[0].w[0:%s]"%str(size-1))
    browTZWgt = cmds.getAttr ( "browTZ_cls.wl[0].w[0:%s]"%str(size-1))
    eyeBlinkWgt =cmds.getAttr ( "l_eyeBlink_cls.wl[0].w[0:%s]"%str(size-1))
    eyeWideWgt = cmds.getAttr ( "l_eyeWide_cls.wl[0].w[0:%s]"%str(size-1))							
   
    valStr = ''
    jcValStr = ''
    upCheekStr = ''
    midCheekStr = ''
    headSkelID = getJointIndex( skinCls,'headSkel_jnt' )
    jawCloseID = getJointIndex( skinCls,'jawClose_jnt' )
    
    #set weight back to 1 on the headSkel_jnt
    cmds.skinPercent( skinCls, headGeo+'.vtx[0:%s]'%(size-1), nrm=1, tv = ['headSkel_jnt',1] )
    #cmds.skinPercent( 'eyeLidMapSkin', 'eyeLidMapHead.vtx[0:%s]'%(size-1), nrm=1, tv = ['headSkel_jnt',1] )
    #cmds.skinPercent( 'browMapSkin', 'browMapHead.vtx[0:%s]'%(size-1), nrm=1, tv = ['headSkel_jnt',1] )
    cmds.setAttr( skinCls + '.normalizeWeights', 0 )
    
    for x in range(size): 

        if browUpWgt[x]>1:
            browUpWgt[x] = 1
            
        vtxVal= browUpWgt[x]-browTZWgt[x]
        if vtxVal<0:
            print vtxVal
            browTZWgt[x] = browUpWgt[x]
      
        if browDnWgt[x]>1:
            browDnWgt[x] = 1 
                   
        #browTZWgt[x] can't not bigger than browDnWgt[x]
        if browTZWgt[x] - browUpWgt[x]>0:
            browTZWgt[x] = browUpWgt[x]
               
        #jawClose_jnt weight
        tempVal = jawCloseWgt[x]-mouthWgt[x]
        '''#take cheek weight inside jawCloseWgt out of cheek weight
        upCheekVal = max( cheekWgt[x]- tempVal, 0)
        upCheekStr +=str(upCheekVal) + " "  
        
        midCheekVal = cheekWgt[x] - upCheekVal
        midCheekStr +=str(midCheekVal) + " "'''
        
        jcValStr += str(tempVal)+" "       
        
        # take out negative value from browWgt, if 1 - (eyeLid + brow weight) < 0
        browVal = max( browDnWgt[x], browUpWgt[x] )
       	eyeBrowVal = eyeWideWgt[x] + browVal
       	        	
        #headSkel_jnt weight =  1-( max(jawOpen,lipCls,lipRoll) + max(browDn,browUp) + max(eyeWide,blink))         
        tmpVal = 1 -jawCloseWgt[x] -eyeBrowVal
        valStr += str(tmpVal)+" "
     
    commandStr = ("setAttr -s "+str(size)+ " %s.wl[0:"%skinCls +str(size-1)+"].w["+headSkelID+"] "+ valStr);
    mel.eval (commandStr)
                 
    cmmdStr = ("setAttr -s "+str(size)+" %s.wl[0:"%skinCls +str(size-1)+"].w["+jawCloseID+"] "+ jcValStr);
    mel.eval (cmmdStr)

    
    #get the xml file for skinWeight ( brow/ eyeLid / lip )
    dataPath = cmds.fileDialog2(fileMode=3, caption="set directory")
    
    if os.path.exists(dataPath[0] + '/headSkin.xml'):

        headSkinWeight = ET.parse( dataPath[0] + '/headSkin.xml')
        rootHeadSkin = headSkinWeight.getroot()
         
        for i in range(2, len(rootHeadSkin) ):
            jntName = rootHeadSkin[i].attrib['source']
            print jntName
            if 'LipRoll' in jntName:
                lipYJnt = jntName.replace('Roll','Y')
                
                lipYJntID = getJointIndex( skinCls,lipYJnt)
                print lipYJnt, lipYJntID
                rollJntID = getJointIndex( skinCls,jntName)
                
                for dict in rootHeadSkin[i]:
                    vertNum = int(dict.attrib['index'])
                    wgtVal= float(dict.attrib['value'])
                    #if vertNum in rollVertNum:
                    cmds.setAttr ( skinCls+'.wl['+ str(vertNum) + "].w[" + str(rollJntID)+ "]", min(1, rollWgt[vertNum])* wgtVal  )
                                     
                    #if vertNum in lipVertNum:                        
                    cmds.setAttr ( skinCls + '.wl['+ str(vertNum) + "].w[" + str(lipYJntID) + "]", max( lipWgt[vertNum] - rollWgt[vertNum], 0 )* wgtVal )
    else:
        print "%s.xml(lipWeight file) does not exists"%skinCls     
    
    if os.path.exists(dataPath[0] + '/eyeLidMapSkin.xml'):      
        eyeLidSkinWeight = ET.parse( dataPath[0] + '/eyeLidMapSkin.xml')
        rootEyeLidSkin = eyeLidSkinWeight.getroot()
        blinkJnts = cmds.ls("l_*LidBlink*_jnt", type = "joint" )
        eyeTipList = lastJntOfChain( blinkJnts ) 
    	
        for c in range(2, len(rootEyeLidSkin)-2 ):
            infJnt = rootEyeLidSkin[c].attrib['source']
            
            if infJnt in eyeTipList:
				eyeTipJnt = infJnt
				blinkJnt = cmds.listRelatives(cmds.listRelatives(eyeTipJnt, p=1)[0], p=1)[0]
				eyeWideJnt = blinkJnt.replace("Blink", "Wide")
				
				blinkJntID = getJointIndex( skinCls, eyeTipJnt )
				wideJntID = getJointIndex( skinCls, eyeWideJnt )
				for dict in rootEyeLidSkin[c]:				
					vertID = int(dict.attrib['index'])
					weight= float(dict.attrib['value'])
					cmds.setAttr ( skinCls + '.wl['+ str(vertID) + "].w[" + str(blinkJntID)+ "]", ( min(1, eyeBlinkWgt[vertID]) * weight) )
					 
					cmds.setAttr ( skinCls + '.wl['+ str(vertID) + "].w[" + str(wideJntID) + "]", ( max( eyeWideWgt[vertID] -eyeBlinkWgt[vertID], 0 )* weight) )

    
    if os.path.exists(dataPath[0] + '/browMapSkin.xml'):  
        browSkinWeight = ET.parse( dataPath[0] + '/browMapSkin.xml')
        rootBrowSkin = browSkinWeight.getroot()
         
        browPJnts = cmds.ls ("*_browP*_jnt", type ="joint")
        childJnts = cmds.listRelatives(browPJnts, c =1, type = "joint")     
        for f in range(2, len(rootBrowSkin)-2 ):
            browJnt = rootBrowSkin[f].attrib['source']
            if browJnt in childJnts:
                browPJnt = cmds.listRelatives( browJnt, p=1, type = "joint" )
                rotYJnt = cmds.listRelatives( browPJnt, p=1, type = "joint" )
                rotYJntID = getJointIndex( skinCls, rotYJnt[0] ) 
                childJntID = getJointIndex( skinCls, browJnt )
                baseJnt = browPJnt[0].replace("P","Base")
                baseJntID = getJointIndex( skinCls,baseJnt )
                browWide = browPJnt[0].replace("P","Wide")
                if cmds.objExists(browWide):
                    wideJntID = getJointIndex( skinCls, browWide )
                    
                for dict in rootBrowSkin[f]:
                    vertIndex = int(dict.attrib['index'])
                    wgtValue= float(dict.attrib['value'])
                    #if vertIndex in browTZNum:
                     
                    cmds.setAttr ( skinCls+'.wl['+ str(vertIndex) + "].w[" + str(childJntID)+ "]", ( min(1, browTZWgt[vertIndex]) * wgtValue))                
             
                    baseVal = max( ( browUpWgt[vertIndex] - browDnWgt[vertIndex] ),0 )
                    cmds.setAttr ( skinCls+ '.wl['+ str(vertIndex) + "].w[" + str(baseJntID) + "]", baseVal*wgtValue )
                    
                    roYVal = max( ( browUpWgt[vertIndex] - baseVal - browTZWgt[vertIndex] ), 0 )
                    cmds.setAttr ( skinCls + '.wl['+ str(vertIndex) + "].w[" + str(rotYJntID) + "]", roYVal*wgtValue )                    
                  
                    if cmds.objExists(browWide):
                        wideVal = max( (browDnWgt[vertIndex] - browUpWgt[vertIndex]),0 )
                        cmds.setAttr ( skinCls + '.wl['+ str(vertIndex) + "].w[" + str(wideJntID) + "]", wideVal*wgtValue )           
        
    #cmds.skinPercent('headSkin', headGeo, nrm=False, prw=100)
    cmds.setAttr( skinCls + '.normalizeWeights', 1 )#normalization mode. 0 - none, 1 - interactive, 2 - post         
    cmds.skinPercent( skinCls, headGeo, nrm= 1 )
    # mirror weight 
    #cmds.copySkinWeights( ss = 'headSkin', ds = 'headSkin', mirrorMode= 'YZ', sa= 'closestPoint', influenceAssociation = 'label', ia = 'oneToOne', normalize=1) 




#mouth_move ctl pivot on 
def mouth_pivotChange():
    # mouth_move to "jointX.rx" or "jointY.rx" 
    rotX_plus = cmds.ls( "*JotXRot*_plus", typ = "plusMinusAverage" )
    rotY_plus = cmds.ls('*JotYRot*_plus', type = "plusMinusAverage" )
    
    for i, plus in enumerate(rotX_plus):
        
        RX_source = cmds.listConnections( plus + ".input3D[3].input3Dy", s=1, d=0 )  
        if RX_source: 
            if RX_source[0] == "mouth_move":
                
                rotY_mult = cmds.listConnections( rotY_plus[i] + ".output3Dx", s=0, d=1 )[0]
                rotX_mult = cmds.listConnections( plus + ".output3Dx", s=0, d=1 )[0]
                cmds.setAttr( "mouth_move.ty", 0 )
                cmds.disconnectAttr( "mouth_move.ty", plus + ".input3D[3].input3Dy" )
                cmds.connectAttr( "mouth_move.ty", rotY_plus[i] + ".input3D[0].input3Dy" )
                if not cmds.listConnections( rotY_mult + ".input1X", s=1, d=0 ):
                    cmds.connectAttr( rotY_plus[i] + ".output3Dy", rotY_mult + ".input1X", f=1 )#mouth_move.ty to RY_plus to RY_mult        
                if not cmds.listConnections( rotY_mult + ".input2X", s=1, d=0 ):
                    cmds.connectAttr( "lipFactor.lipJotX_rx", rotY_mult + ".input2X", f=1 )#connect lipFactor.lipJotX_rx
                # get ry_jnt from rx_mult
                RX_jnt = cmds.listConnections( rotX_mult + ".outputX", s=0, d=1, scn =1 )[0]
                RY_jnt = cmds.listRelatives( cmds.listRelatives( RX_jnt, c = 1 )[0] , c = 1 )[0] 
                # connect ry_mult to ry_jnt
                if not cmds.listConnections( RY_jnt + ".rx", s=1, d=0 ):
                    cmds.connectAttr( rotY_mult + ".outputX", RY_jnt + ".rx", f=1 )
                if i ==0:
                    cmds.confirmDialog( title='Confirm', message="mouth move around lipYPos!" )
                                
            
        else:
            RY_source = cmds.listConnections( RotY_plus[i] + ".input3D[0].input3Dy", s=1, d=0 )
            if RY_source:
                if RY_source[0] == "mouth_move":
                    print "connect LipX_jnt.rx"
                    cmds.setAttr( "mouth_move.ty", 0 )
                    cmds.disconnectAttr( "mouth_move.ty", RotY_plus[i] + ".input3D[0].input3Dy" )
                    cmds.connectAttr( "mouth_move.ty", plus + ".input3D[3].input3Dy" )

                    if i ==0:
                        cmds.confirmDialog( title='Confirm', message="mouth move around jawRigPos!" )




#transfer blendShape weight from splitMapBS to other blendShape.
#select geo with target blendShape and target geo (weightSize(1=large, 2=mideum, 3 = toll ))    
def copyBSWeight( weightSize ):
    myList = cmds.ls(os=1, type = "transform")
    size = cmds.polyEvaluate( myList[0], v=1)
    tgtBS = [ t for t in cmds.listHistory( myList[0] ) if cmds.nodeType(t) == "blendShape" ][0]
    tgt = myList[1]
         
    lBsVal = cmds.getAttr( "splitMapBS.inputTarget[0].inputTargetGroup[%s].targetWeights[0:%s]"%(weightSize*2-2, size-1) )    
    rBsVal = cmds.getAttr( "splitMapBS.inputTarget[0].inputTargetGroup[%s].targetWeights[0:%s]"%(weightSize*2-1, size-1) )
    
    
    if "L_" in tgt:
        
        alias = cmds.aliasAttr(tgtBS, q=1 )
        for t , w in zip(*[iter(alias)]*2):
            if t == tgt:
                tgtID = w.split("[")[1][:-1]
                cmds.setAttr( tgtBS + ".inputTarget[0].inputTargetGroup[%s].targetWeights[0:%s]"%(tgtID, size-1), *lBsVal )
            elif t == tgt.replace("L_","R_"):
                tgtID = w.split("[")[1][:-1]
                cmds.setAttr( tgtBS + ".inputTarget[0].inputTargetGroup[%s].targetWeights[0:%s]"%(tgtID, size-1), *rBsVal )   



#transfer blendShape weight splitMapBS to other blendShape
#select geo with target blendShape (weightSize(1=large, 2=mideum, 3 = toll ))
def rnkSplitBSWeight( weightSize ):
    
    myList = cmds.ls(os=1, type = "transform")
    size = cmds.polyEvaluate( myList[0], v=1)
    tgtBS = [ t for t in cmds.listHistory( myList[0] ) if cmds.nodeType(t) == "blendShape" ][0]
    alias = cmds.aliasAttr(tgtBS, q=1 )
         
    lBsVal = cmds.getAttr( "splitMapBS.inputTarget[0].inputTargetGroup[%s].targetWeights[0:%s]"%(weightSize*2-2, size-1) )    
    rBsVal = cmds.getAttr( "splitMapBS.inputTarget[0].inputTargetGroup[%s].targetWeights[0:%s]"%(weightSize*2-1, size-1) )
    
    for t , w in zip(*[iter(alias)]*2):
        if "L_" in t:
            tgtID = w.split("[")[1][:-1]
            cmds.setAttr( tgtBS + ".inputTarget[0].inputTargetGroup[%s].targetWeights[0:%s]"%(tgtID, size-1), *lBsVal )
            rt = t.replace("L_","R_")
            for x, i in zip(*[iter(alias)]*2):
                if x == rt:
                    tgID = i.split("[")[1][:-1]
                    cmds.setAttr( tgtBS + ".inputTarget[0].inputTargetGroup[%s].targetWeights[0:%s]"%(tgID, size-1), *rBsVal )  
            


    

# cluster list : 0보다 큰 웨이트 값을 가진 클러스터 vertex index 리스트
def selectedClsVerts( obj, cls):

    verts = []
    for x in range(cmds.polyEvaluate( obj, v = 1)):
        val = cmds.getAttr( cls + '.wl[0].w[%s]'%str(x))
        if val > 0.0:
            verts.append( x )
    return verts





#조인트 리스트의 인덱스 넘버 dictionary: {u'upLipRollJot12_jnt': u'121', u'loLipRollJot13_jnt': u'106',....}
import re
def jointIndices( jntList ):

    jntIndex = {}
    for jnt in jntList:
             
        connections = cmds.listConnections( jnt + '.worldMatrix[0]', p=1)
        for cnnt in connections:
            if 'headSkin' in cnnt:
                skinJntID = cnnt
        jntID = re.findall ( '\d+', skinJntID )
        jntIndex[jnt] = jntID[0]
    return jntIndex






#browUp/Dn_cls update 10/23/2017 
#create “jawClose_cls” / “mouth_cls” calculated by existing clusters
def calExtraClsWgt(): #normalize clusters weight( calculate with the stored weight value : not care of cls position )

    clusters = ["lip_cls", "lipRoll_cls", "jawOpen_cls"]
    for cls in clusters:
    
        if not cmds.objExists (cls):
        
            print cls+' Is missing'
    
    shapes = cmds.cluster ( "lip_cls", q=1, g=1 )
    objs = cmds.listRelatives( shapes, p=1 )
    obj = objs[0]
    faceIndices =grinFaceIndices(obj)
    
    size = cmds.polyEvaluate(obj, v=1)
    mouthWgt = []
    lipWgt = cmds.getAttr ("lip_cls.wl[0].w[0:"+str(size-1)+"]")
    rollWgt = cmds.getAttr ("lipRoll_cls.wl[0].w[0:"+str(size-1)+"]")
    jawOpenWgt = cmds.getAttr ("jawOpen_cls.wl[0].w[0:"+str(size-1)+"]")
    browUpWgt = cmds.getAttr ("browUp_cls.wl[0].w[0:"+str(size-1)+"]") 
    browDnWgt = cmds.getAttr ("browDn_cls.wl[0].w[0:"+str(size-1)+"]")  
    browTZWgt = cmds.getAttr ("browTZ_cls.wl[0].w[0:"+str(size-1)+"]")
    eyeWideWgt = cmds.getAttr ("l_eyeWide_cls.wl[0].w[0:"+str(size-1)+"]")
    eyeBlinkWgt = cmds.getAttr ("l_eyeBlink_cls.wl[0].w[0:"+str(size-1)+"]") 

    for i in faceIndices:

        vtxVal= browUpWgt[i]-browTZWgt[i]
        if vtxVal<0:
            cmds.setAttr("browTZ_cls.wl[0].w[%s]"%str(i), browUpWgt[i])  
        
        browVal= browDnWgt[i]-browUpWgt[i]
        if vtxVal<0:
            cmds.setAttr("browUp_cls.wl[0].w[%s]"%str(i), browDnWgt[i])  
            
        eyeVtxVal= eyeWideWgt[i]-eyeBlinkWgt[i]
        if eyeVtxVal<0:
            cmds.setAttr("l_eyeBlink_cls.wl[0].w[%s]"%str(i), eyeWideWgt[i])
            
        #first calculate the mouth with lip and lipRoll
        mouthWgt.append( min(1, max(lipWgt[i], rollWgt[i])) )      
    
        # filter out lip area by multiple (1 - mouth)
        jawOpenWgt[i]*=(1 - mouthWgt[i])
    
        #then add the mouth back
        jawOpenWgt[i] += mouthWgt[i]
         
    
    valStr = ''
    mouthValStr = ''
    eyeLidVal = ''
    browVal=''
    for j in range(size):
        tempVal = mouthWgt[j]
        mouthValStr += str(tempVal) + " "
    
        tmpVal = jawOpenWgt[j]
        valStr += str(tmpVal)+" "        
                   
    commandStr = ("setAttr -s "+str(size)+" mouth_cls.wl[0].w[0:"+str(size-1)+"] "+mouthValStr);
    mel.eval (commandStr)
    
    jcCmmdStr = ("setAttr -s "+str(size)+" jawClose_cls.wl[0].w[0:"+str(size-1)+"] "+valStr);
    mel.eval (jcCmmdStr)
    

    



def grinFaceIndices(headGeo):

    indices=[]
    if mel.eval('attributeExists "grinFace" %s'%headGeo): 
        indices = getAttr (headGeo+".grinFace")
    else:
        indices = range(cmds.polyEvaluate(headGeo, v=1))

    return indices






#surf map 웨이트가 카피된 각각의 부위별(눈, 눈썹, 입)의 skinWeight값을 export 
#set up the project first!!
#jawClose/mouth cluster weight update할때: calExtraClsWgt()
#improve: copy all the map surf and export them all
def copyTrioSkinWeights():
    #set only the jawOpen_cls.ty, 1
    headGeo = cmds.getAttr("helpPanel_grp.headGeo")
    cls =[nd for nd in cmds.listHistory(headGeo) if cmds.nodeType(nd) in ['cluster', 'blendShape', 'ffd' ] ]
    for c in cls:
        #has no effect
        cmds.setAttr( c+ '.nodeState', 1)
    cmds.setAttr('jawOpen_cls.nodeState', 0)

    tempHeadMap = { 'lip_cls':['lipTip_map', headGeo,'headSkin'], 'eyeWide_cls':['eyeTip_map','eyeLidMapHead','eyeLidMapSkin'], 
    'browDn_cls':['browMapSurf','browMapHead', 'browMapSkin'] }         
        
    #copy skinWeight from map_surf to map_head and export skinWeight    

    for x, y in tempHeadMap.iteritems():
        if cmds.objExists(y[0]) and cmds.objExists(y[1]):
            copySkinWeightInClsVerts( x, y[1], y[0], y[2] )          
            #cmds.deformerWeights ( y[2]+'.xml', export =1, deformer=y[2], path= trioWgtPath )
            #cmds.skinPercent( y[2], y[1]+'.vtx[0:%s]'%(vertNum-1), tv = ['headSkel_jnt',1] )             
        else :
            print 'create %s map_surf and map_head!!!'%x   
    
    #jawOpenCls back to 0
    cmds.setAttr( 'jawOpen_ctl.t', 0,0,0)

    for c in cls:
        cmds.setAttr( c+ '.nodeState', 0)



def exportTrioSkinWgt():
    headGeo = cmds.getAttr("helpPanel_grp.headGeo")

    tempHeadMap = { 'lip_cls':['lipTip_map', headGeo,'headSkin'], 'eyeWide_cls':['eyeTip_map','eyeLidMapHead','eyeLidMapSkin'], 
    'browDn_cls':['browMapSurf','browMapHead', 'browMapSkin'] }  
    #copy skinWeight from map_surf to map_head and export skinWeight
    
    #create folder "trioSkinWeight"
    trioWgtPath = dataPath()
 
    for x, y in tempHeadMap.iteritems():
        if cmds.objExists(y[0]) and cmds.objExists(y[1]):
                     
            cmds.deformerWeights ( y[2]+'.xml', export =1, deformer=y[2], path= trioWgtPath )        


#'headSkel_jnt'에 스킨 몰빵하고 cls surf 웨이트를 cls head에 카피            
#select MapSurf vertices and clsHead vertices that has cls weight/ then copySkinWeight
def copySkinWeightInClsVerts( cls, clsHead, clsMapSurf, skinCls ):
    #skinCls = mel.eval("findRelatedSkinCluster %s"%clsHead )
    #headGeo = cmds.getAttr("helpPanel_grp.headGeo")
    #clsDict = clsVertsDict( clsHead, cls )    
    #clsVert = [ clsHead + '.vtx[%s]'%t for t in clsDict ]

    vertNum = cmds.polyEvaluate( clsHead, v = 1)    
    vertLen = cmds.polyEvaluate( clsMapSurf, v = 1)
    cmds.setAttr( skinCls+'.normalizeWeights', 1 )
    cmds.skinPercent( skinCls, clsHead + '.vtx[0:%s]'%(vertNum-1), tv = ['headSkel_jnt',1], normalize=1 )

    cmds.select( clsMapSurf+'.vtx[0:%s]'%(vertLen-1))
    # select target vtx
    cmds.select( clsHead, add=1 )    
    cmds.copySkinWeights( sa= 'closestPoint', ia = 'closestJoint', sm=0, normalize=1, noMirror =1 )
    #cmds.copySkinWeights( ss = 'headSkin', ds = 'headSkin', mirrorMode= 'YZ', sa= 'closestPoint', ia = 'closestJoint')




    
#select trioSkinWeight folder or create the folder 
def dataPath():    
    xmlPath = cmds.fileDialog2(fileMode=3, caption="set directory")
    if "trioSkinWeight" not in xmlPath[0]:
        i = 0
        while os.path.isdir(xmlPath[0] + "/trioSkinWeight%s" % i):   
            i += 1
        os.makedirs( xmlPath[0] + "/trioSkinWeight" + str(i))
        xmlPath = [xmlPath[0] + "/trioSkinWeight" + str(i)]

    return xmlPath[0]
    

    
def exportLipMap():
    headGeo = cmds.getAttr("helpPanel_grp.headGeo")
    lipWgtPath = dataPath()
    if cmds.objExists( headGeo) and cmds.objExists( 'lipTip_map' ):
        copySkinWeightInClsVerts( 'lip_cls', headGeo, 'lipTip_map' )            
        cmds.deformerWeights ( 'headSkin'+'.xml', export =1, deformer='headSkin', path=  lipWgtPath )
    else :
        print 'create lip map_surf and head_REN!!!'      

def exportEyeLidMap():
    eyeWgtPath = dataPath()
    if cmds.objExists('eyeLidMapHead') and cmds.objExists('eyeTip_map'):
        copySkinWeightInClsVerts( 'eyeWide_cls', 'eyeLidMapHead', 'eyeTip_map' )            
        cmds.deformerWeights ( 'eyeLidMapSkin'+'.xml', export =1, deformer='eyeLidMapSkin', path= eyeWgtPath )
    else :
        print 'create eyeLid map_surf and eyeLidMapHead!!!'    


#update brow cluster weight and export browMapSkin weight
def exportBrowMap():
    browWgtPath = dataPath()
            
    if cmds.objExists('browMapHead') and cmds.objExists('browMapSurf'):
        copySkinWeightInClsVerts( 'browUD_cls', 'browMapHead', 'browMapSurf' )            
        cmds.deformerWeights ( 'browMapSkin'+'.xml', export =1, deformer='browMapSkin', path=  browWgtPath )
    else :
        print 'create brow browMapSurf and browMapHead!!!'




def zeroOutCluster():
    ctls = ['jawOpen_ctl', 'jawClose_ctl', 'lip_ctl', 'lipRoll_ctl', 'l_cheek_onCtl', 'r_cheek_onCtl', 'l_eyeBlink_ctl', 'r_eyeBlink_ctl', 
    'l_eyeWide_ctl', 'r_eyeWide_ctl', 'l_lowCheek_onCtl', 'r_lowCheek_onCtl', 'l_squintPuff_onCtl','r_squintPuff_onCtl', 'browUp_ctl', 
    'browDn_ctl', 'browTZ_ctl', 'nose_onCtl', 'l_ear_onCtl', 'r_ear_onCtl' ]
   
    for ct in ctls:

        attrs = cmds.listAttr( ct, k=1, unlocked = 1 )
        for at in attrs:
            if 'scale' in at or "visibility" in at:
                cmds.setAttr( ct+"."+at, 1 )
            else:
                cmds.setAttr( ct+"."+at, 0 )




# geo(머리 or 눈꺼플 or 눈썹)을 headSkin한다. 눈꺼플 조인트(pre+LidBlink*_jnt)를 클러스터로 변환한다. Wide_jnt는 여전히 스킨을 컨트롤 한다.
def switchJntToCls(pre, geo ):

    geoSkin = mel.eval("findRelatedSkinCluster %s"%geo ) 
    jnts =cmds.ls( pre + "LidBlink*_jnt", type = "joint" )
    vtxLeng = cmds.polyEvaluate( geo, v=1 )
          
    for j in jnts:
        #get the last joint( LidTX_jnt ) for blink weight 
        child = lastJntOfChain( j )
        #when blink_cls already exists
        wgtInf=cmds.skinCluster( geoSkin, q=1, wi =1)
        
        if cmds.objExists( j.replace("_jnt","_cls")):
            if child[0] in wgtInf:
                print j
                cls = [ j.replace("_jnt","_cls") ]
                cmds.cluster( cls[0], e=1, g= geo, wn=(j, j) )
                clusterSet = cmds.listConnections( cls[0], type = "objectSet" )[0]
                geoGrp = cmds.listConnections( clusterSet + ".dagSetMembers", s=1, d=0, p=1 )
                for i, g in enumerate(geoGrp):
                    if geo in g:
                        geoID = i
                print geoID
                jID = getJointIndex( geoSkin, child[0] )
                wgt = cmds.getAttr( geoSkin + ".weightList[0:%s].weights[%s]"%( str(vtxLeng-1), jID))
                #cmds.setAttr( cls[0] + ".wl[%s].w[0:%s]"%( geoID, str(vtxLeng-1) ),  *wgt , s=vtxLeng )
                
                for x in range(vtxLeng):
                    cmds.percent( cls[0], geo+".vtx[%s]"%str(x), v = wgt[x] )
                
        else:        
            cls = cmds.cluster( geo, n = j.replace("_jnt","_cls") )
            cmds.cluster( cls[0], e=1, bindState=1, wn = ( j , j ) )
            #cmds.setAttr( cls[0] + ".wl[0].w[0:%s]"%(vtxLeng -1 ), *val )
            cmds.delete(cls[1])
        
            #weight transfer from skin to cluster
            clusterSet = cmds.listConnections( cls[0], type = "objectSet" )[0]
            geoGrp = cmds.listConnections( clusterSet + ".dagSetMembers", s=1, d=0, p=1 )
            for i, g in enumerate(geoGrp):
                if geo in g:
                    geoID = i
                            
            jID = getJointIndex( geoSkin, child[0] )
            wgt = cmds.getAttr( geoSkin + ".weightList[0:%s].weights[%s]"%( str(vtxLeng-1), jID))
            cmds.setAttr( cls[0] + ".wl[%s].w[0:%s]"%( geoID, str(vtxLeng-1) ),  *wgt , s=vtxLeng )
        
        
        
        
        
#with blink clusters when eyeLid same piece with head
#remove blink joint weight and add it to headSkel_joint       
def remove_blinkWgtWIP():

    geoShape =cmds.cluster( "eyeBlink_cls", q=1, g=1 )    
    jnts =cmds.ls( "*LidBlink*_jnt", type = "joint" )
    
    for i, g in enumerate(geoShape):
        geo = cmds.listRelatives( g, p=1, typ = "transform")[0]
        vtxLen = cmds.polyEvaluate( geo, v=1 )
        skinCls = mel.eval( "findRelatedSkinCluster %s"%geo)
        cmds.setAttr( skinCls + '.normalizeWeights', 0 )
        #get headSkel weight
        headSkelID = getJointIndex( skinCls, "headSkel_jnt" )
        headWgt = cmds.getAttr( skinCls + ".weightList[0:%s].weights[%s]"%( str(vtxLen-1), headSkelID))    
        blinkClsWgt = cmds.getAttr( "eyeBlink_cls.wl[%s].w[0:%s]"%(str(i), str(vtxLen-1)) )
        calVal =[]
        # calculate headSkel weight:  headSkinWgt + blinkClsWgt
        for v in range( vtxLen ):
            val = headWgt[v] + blinkClsWgt[v]
            calVal.append(val)
        cmds.setAttr( skinCls + ".wl[0:%s].w[%s]"%(vtxLen-1,headSkelID ), *calVal, s = vtxLen )
        
        for j in jnts:
            child = lastJntOfChain( j )
            print child
            cmds.skinPercent( skinCls, geo + ".vtx[0:%s]"%(vtxLen), tv = ( child[0], 0 ) )
            
        cmds.skinPercent( skinCls, geo, nrm= 1 )
        
        
        
        
'''
1.eyeLidGeo should be seperate from Head geo
1.make sure headSkinObj includes the wide/lidTx joints
'''
def copyExportEyeSkinWeights():
    
    #set only the jawOpen_cls.ty, 1
    headGeo = cmds.getAttr("helpPanel_grp.headGeo")
    eyeLidGeo = cmds.getAttr("lidFactor.eyelidGeo")
    if cmds.objExists(eyeLidGeo):
        if not eyeLidGeo==headGeo:
            
            deformers =[nd for nd in cmds.listHistory(eyeLidGeo) if cmds.nodeType(nd) in ['cluster', 'blendShape', 'ffd' ] ]
            for df in deformers:
                #has no effect
                cmds.setAttr( df + '.nodeState', 1)
            
            if cmds.objExists(eyeLidGeo):
        		if not eyeLidGeo==headGeo:
        		    size = cmds.polyEvaluate( eyeLidGeo, v = 1)
        		    tmpSkin =mel.eval("findRelatedSkinCluster %s"%eyeLidGeo )
        		    eyeLidSkin = cmds.rename( tmpSkin, "eyeLidGeoSkin") 
        		    eyeMap = {  'eyeWide_cls':['eyeTip_map', eyeLidGeo, eyeLidSkin ] }
        		    cls = eyeMap.keys()[0]
        		    if cmds.objExists(eyeMap[cls][0]):
        		        copySkinWeightInClsVerts( cls, eyeMap[cls][1], eyeMap[cls][0], eyeMap[cls][2] )
        		        
        		    else:
        		        cmds.warning (" eyeSurfMap geo doesn't exists")
        		else:
        		    cmds.warning (" eyeLid geo is not seperate")
    
            for df in deformers:
                #has no effect
                cmds.setAttr( df + '.nodeState', 0)            
            #create folder "trioSkinWeight"
            weightPath = cmds.fileDialog2(fileMode=3, caption="set directory")[0]
         
            cmds.deformerWeights ( eyeLidSkin+'.xml', export =1, deformer= eyeLidSkin, path= weightPath ) 

    else:
        cmds.warning (" eyeLid geo doesn't exists")
        
'''
1.eyeLidGeo should be seperate from Head geo
1.make sure headSkinObj includes the wide/lidTx joints
'''
def eyeWeightCalculate():   
    
	eyeLidGeo = cmds.getAttr( "lidFactor.eyelidGeo" )
	eyeLen = cmds.polyEvaluate( eyeLidGeo, v = 1)
	eyeLidSkin =mel.eval("findRelatedSkinCluster %s"%eyeLidGeo )
	eyeBlinkWgt =cmds.getAttr ( "eyeBlink_cls.wl[1].w[0:%s]"%str(eyeLen-1))
	eyeWideWgt = cmds.getAttr ( "eyeWide_cls.wl[1].w[0:%s]"%str(eyeLen-1))
	headSkelID = getJointIndex( eyeLidSkin,'headSkel_jnt' )	
	valStr = ''
	cmds.skinPercent( eyeLidSkin, eyeLidGeo+'.vtx[0:%s]'%(eyeLen-1), nrm=1, tv = ['headSkel_jnt',1] )
	for i in range( eyeLen ):
		if eyeBlinkWgt[i]>1:
			print eyeBlinkWgt[i]
			eyeBlinkWgt[i] = 1            
		if eyeWideWgt[i]>1:
			eyeWideWgt[i] = 1                        
		vtxVal= eyeWideWgt[i]-eyeBlinkWgt[i]
		if vtxVal<0:
			print vtxVal
			eyeBlinkWgt[i] = eyeWideWgt[i]

		tmpVal = 1 - eyeWideWgt[i]
		print tmpVal
		valStr += str(tmpVal)+" "	
			    
	commandStr = ("setAttr -s "+str(eyeLen)+ " " + eyeLidSkin + ".wl[0:"+str(eyeLen-1)+"].w["+headSkelID+"] "+ valStr);
	mel.eval (commandStr)
	
	#get the xml file for skinWeight ( brow/ eyeLid / lip )
	dataPath = cmds.fileDialog2(fileMode=3, caption="set directory")
    	
	if os.path.exists(dataPath[0] + '/eyeLidGeoSkin.xml'):      
		eyeLidSkinWeight = ET.parse( dataPath[0] + '/eyeLidGeoSkin.xml')
		rootEyeLidSkin = eyeLidSkinWeight.getroot()
		blinkJnts = cmds.ls("l_*LidBlink*_jnt", type = "joint" )
		eyeTipList = lastJntOfChain( blinkJnts ) 
		for c in range(2, len(rootEyeLidSkin)-2 ):
		    eyeLidJnt = rootEyeLidSkin[c].attrib['source']
		    if eyeLidJnt in eyeTipList:
				eyeTipJnt = eyeLidJnt
				blinkJnt = cmds.listRelatives(cmds.listRelatives(eyeTipJnt, p=1)[0], p=1)[0]
				eyeWideJnt = blinkJnt.replace("Blink", "Wide")
				wideJntID = getJointIndex( eyeLidSkin, eyeWideJnt )
				blinkJntID = getJointIndex( eyeLidSkin, eyeTipJnt )
				for dict in rootEyeLidSkin[c]:
					vertID = int(dict.attrib['index'])
					weight= float(dict.attrib['value'])
					cmds.setAttr ( eyeLidSkin + '.wl['+ str(vertID) + "].w[" + str(blinkJntID)+ "]", ( min(1, eyeBlinkWgt[vertID]) * weight) )
					cmds.setAttr ( eyeLidSkin + '.wl['+ str(vertID) + "].w[" + str(wideJntID) + "]", ( max( eyeWideWgt[vertID] - eyeBlinkWgt[vertID], 0 )* weight) )
	






# new name should be given
def copyOrigMesh( obj, name ):
    
    shapes = cmds.listRelatives( obj, ad=1, type='shape' )
    origShape = [ t for t in shapes if 'Orig' in t ]
    #get the orig shapes with history and delete the ones with with same name.
    myOrig = ''
    for orig in origShape:
        if cmds.listConnections( orig, s=0, d=1 ):
            myOrig = orig
        else: cmds.delete(orig)
    
    #unique origShape duplicated
    headTemp = cmds.duplicate ( myOrig, n = name, renameChildren =1 )
    tempShape = cmds.listRelatives( headTemp[0], ad=1, type ='shape' )
    num = 0
    for ts in tempShape:
        if 'ShapeOrig' in ts:
            tempOrig = cmds.rename( ts, ts.replace('ShapeOrig', 'Shape') )
        else: cmds.delete(ts)
     
    cmds.setAttr( tempOrig+".intermediateObject", 0)
    cmds.sets ( tempOrig, e=1, forceElement = 'initialShadingGroup' )
    
    for c in ['x','y','z']:
        if cmds.getAttr( headTemp[0] + '.t%s'%c, lock =1 ):
            cmds.setAttr(headTemp[0] + '.t%s'%c, lock =0 )
    return headTemp[0]
    
    
    
    
# get OrigShape and delete useless one
def getOrigMesh( obj ):
    
    shapes = cmds.listRelatives( obj, ad=1, type = 'shape')
    origList = [ s for s in shapes if "Orig" in s ]
    #check if it treverse forward the shape of the selection 
    origShape = []
    for org in origList:
        connections = cmds.listConnections( org, s=0, d=1 )
        if connections:
            origShape = org            
        
        else: cmds.delete( org )
    return origShape




def headInfluences():
    #brow joints
    browBase = cmds.listRelatives("eyebrowJnt_grp", c=1 )
    browAllJnt = []
    for bb in browBase:
        cList = cmds.listRelatives( bb, ad=1 )
        if cList:
            num = len(cList)        
            for i in range(0, num, 2 ):               
                browAllJnt.append( cList[i] )
    #eyeLid joints            
    eyeWideJnts = cmds.ls('*LidWide*_jnt', fl =1, type = 'joint')
    blinkJnts = cmds.ls("*LidBlink*_jnt", type = "joint" )
    eyeJnts = lastJntOfChain( blinkJnts )     
    
    #lip joints
    lipJnt = lastJntOfChain("lipJotP")
    #faceJnts = cmds.listRelatives('supportRig', ad =1, type = 'joint' )
    skinJnts = ['jawClose_jnt', 'headSkel_jnt']
    for jList in [ browBase, browAllJnt, eyeWideJnts, eyeJnts, lipJnt ]:
   		skinJnts+=jList

    return skinJnts   



#get the last child joint of the chain.
def lastJntOfChain( jntList ):
    chlidJnt = cmds.listRelatives( jntList, ad=1, type = "joint" )
    childJntGrp = []
    for jt in chlidJnt:
        child = cmds.listRelatives( jt, c=1, type = "joint" )
        if not child:
            childJntGrp.append(jt)
    
    return (childJntGrp)
    





'''full skinning module for lipMapSkinning (geometrys for skinning need to have "_" in their name)'''
def headSkinObj(geoName):

    # normalize clusters and calculate extra(jawClose_cls, mouth_cls)
    calExtraClsWgt()
    deforms =[nd for nd in cmds.listHistory(geoName) if cmds.nodeType(nd) in ['cluster', 'blendShape', 'ffd'] ]
    for df in deforms:
        if cmds.getAttr( df + '.nodeState')==0:
            #hasNoEffect
            cmds.setAttr( df + '.nodeState', 1)       

    skinJnts = headInfluences()
    for geo in geoName:
        skin = cmds.skinCluster ( geo, skinJnts, tsb =1, n = geo + 'Skin' )
    return skin

    
    
''' 각각의 서피스 웨이트 맵의 값을 카피할 디폴트 skin face하나씩 만든다 '''
# skin head with normal interactive / skinPercent to headSkel_jnt with normalization
def arFaceHeadSkin(geoName):
    if geoName == cmds.getAttr("helpPanel_grp.headGeo"):
    
        # normalize clusters and calculate extra(jawClose_cls, mouth_cls)
        calExtraClsWgt()
        
        # duplicate heads for brow/eyeLid map
        deforms =[nd for nd in cmds.listHistory(geoName) if cmds.nodeType(nd) in ['cluster', 'blendShape', 'ffd'] ]
        if len(deforms) > 0:
		    for df in deforms:
		        cmds.setAttr( df + '.nodeState', 1)
        
        browHead = copyOrigMesh( geoName, 'browMapHead' )
        eyeLidGeo = cmds.duplicate( browHead, name = 'eyeLidMapHead')[0]
        #get headSkin influence joints
        skinJnts = headInfluences()
        headSkinDict = {geoName: 'headSkin', browHead:'browMapSkin', eyeLidGeo:'eyeLidMapSkin'}
        for head, skin in headSkinDict.iteritems():
            cmds.skinCluster ( head, skinJnts, tsb =1, normalizeWeights=1, n = skin )

        for df in deforms:

            cmds.setAttr( df + '.nodeState', 0 )
   
    else:
        cmds.confirmDialog( title='Confirm', message='check head geo name' )



"""create browMapMesh"""
def createMapSurf():
    faceGeo = cmds.ls(sl =1, type ='transform')
    #xmin ymin zmin xmax ymax zmax (face bounding box)
    facebbox = cmds.xform( faceGeo, q=1, boundingBox =1 )
    sizeX = facebbox[3]*2
    bboxSizeY = facebbox[4] - facebbox[1]
    browJntLen = len (cmds.ls("*_browBase*", type = "joint"))
    browMapSurf = cmds.polyPlane(n= "browMapSurf", w = sizeX, h =bboxSizeY/2, subdivisionsX = browJntLen, subdivisionsY = 1 )
    cmds.xform( browMapSurf, p = 1, rp =(0, 0, bboxSizeY/4))
    
    #place the mapSurf at the upper part of the face
    cmds.setAttr ( browMapSurf[0] + ".rotateX", 90 )
    cmds.xform (browMapSurf[0], ws =1, t = (0, facebbox[1] + bboxSizeY/2, 0))
    
    '''#move down the 2nd low of edges
    browCtls = cmds.ls("*_brow*_ctl", type = "transform")
    tranY = cmds.xform (browCtls[-1], q =1, ws =1, t=1 )
    cmds.select( browMapSurf[0] + ".vtx[%s:%s]"%(browJntLen+1, browJntLen*2 +1))
    verts = cmds.ls(sl=1, fl =1)
    for v in verts:
        vPos = cmds.xform(v, q =1, ws =1, t=1 )
        cmds.xform (v, ws =1, t = ( vPos[0], tranY[1], vPos[2] ))
        cmds.select ( cl =1 )''' 


        
        
     
# cluster dictionary : 0보다 큰 웨이트값을 가진 버텍스 딕셔너리
def clsVertsDict( obj, cls):
    
    geometryIndex = geoIDforCls( obj, cls)
    if not geometryIndex == None:
        vtxNum = cmds.polyEvaluate( obj, v = 1)
        clsVal= cmds.getAttr( cls + '.wl['+ str(geometryIndex) + '].w[0:%s]'%(vtxNum-1) )
        verts = {}
        for x in range(vtxNum):
            val = clsVal[x]
            if val > 0.001:
                verts[ x ] = val
        return verts



#모든 influenced shape들은 clusterSet + ".dagSetMembers[0],[1],[2]..." 순서대로 연결되어 있고, 그 순서대로 리턴된다.
def geoIDforCls( geo, cls):
         
    clsObj = cmds.cluster( cls, q=1, g=1 )
    
    # get the source geoID for the cluster
    geoID = None
    for i, x in enumerate(clsObj):
        infGeo = cmds.listRelatives( x, p =1 )[0]
        if infGeo == geo:
            geoID = i           
            
    if geoID == None:
        cmds.confirmDialog( title='Confirm', message="selected geometry is not in the cluster's objList " )
    else:
        return geoID
    

  
def weightedVerts(obj, cls):

    if clsVertsDict( obj, cls):
        vtx =[ obj + '.vtx[%s]'%v for v in clsVertsDict( obj, cls).keys() ]
        cmds.select(vtx)
    else :
        print "paint weight on the cluster"
        



#select geometry or it will grab the head
#select 2 cluster handle from option( to copy weight / to paste weight )
def copyClusterWgt(sdCls, ddCls):

    myGeo = cmds.ls( sl=1, typ = "transform")
    if myGeo:
        geo = myGeo[0]
    else:
        geo = cmds.getAttr("helpPanel_grp.headGeo")
        
    size = cmds.polyEvaluate( geo, v=1)       
    
    if "eye" in sdCls :
        for pre in ["l_","r_"]:
            sdID = geoIDforCls( geo, pre+sdCls)
            ddID = geoIDforCls( geo, pre+ddCls)
            valString = ""
            for i in range(size):
                copyWgt = cmds.getAttr( pre + sdCls + ".wl[%s].w[%s]"%( str(sdID), str(i) ) )
                valString += str(copyWgt)+" "
                
            print ddID, sdID
            commandStr = ("setAttr -s " +str(size) + " %s.wl[%s].w[0:%s] "%( pre+ddCls, str(ddID), str(size-1)) + valString);
            mel.eval(commandStr)
            
    
    else:
        sdID = geoIDforCls( geo, sdCls)
        ddID = geoIDforCls( geo, ddCls)
        valStr = ""
        for i in range(size):
            copyWgt = cmds.getAttr( sdCls + ".wl[%s].w[%s]"%( str(sdID), str(i) ) )
            valStr += str(copyWgt)+" "
            
        print ddID, sdID
        commandStr = ("setAttr -s " +str(size) + " %s.wl[%s].w[0:%s] "%(ddCls, str(ddID), str(size-1)) + valStr);
        mel.eval(commandStr)
    
    
    


def exportClsWgt():
    #pathProject = cmds.workspace(  q=True, rd = True )
    dataPath = cmds.fileDialog2(fileMode=3, caption="set directory")
    #cmds.file( filename[0], i=True );
    if "clusterWeight" not in dataPath[0]:
        i = 0
        while os.path.isdir(dataPath[0] + "/clusterWeight%s" % i):   
            i += 1
        os.makedirs( dataPath[0] + "/clusterWeight" + str(i))
        dataPath = [dataPath[0] + "/clusterWeight" + str(i)]
    mesh = cmds.ls( sl=1 )
    if not mesh:
        cmds.confirmDialog( title='Confirm', message='select geo for export weights from!' )
    
    else:    
        clsList = [ c for c in cmds.listHistory( mesh[0] ) if cmds.nodeType(c) == "cluster" ]
        for cls in clsList:
            cmds.deformerWeights( cls.replace("cls","wgt") + ".xml", deformer = cls, ex =1, path = dataPath[0] )
        


def importClsWgt():    
    #pathProject = cmds.workspace(  q=True, rd = True )
    dataPath = cmds.fileDialog2(fileMode=3, caption="set directory")

    mesh = cmds.ls( sl=1 )
    if not mesh:
        cmds.confirmDialog( title='Confirm', message='select geo for importing weights on!' )
    
    else:    
        clsList = [ c for c in cmds.listHistory( mesh[0] ) if cmds.nodeType(c) == "cluster" ]
        for cls in clsList:
            wgt = cls.replace("cls","wgt")
            if os.path.exists( dataPath[0] + "/" + wgt + ".xml"):
                cmds.deformerWeights( wgt + ".xml", im=1, method= "index", deformer = cls, path = dataPath[0] )
            else:
                print "%s.xml file doesn't exist"%wgt
        
        
        
# dictionary ={ vertexNum:  weight value } 
def selectedInfVerts( obj, jntNum ):
    
    skinCls = mel.eval('findRelatedSkinCluster %s' %obj)
    verts ={}
    for x in range(cmds.polyEvaluate( obj, v = 1)):
        #cmds.getAttr ('headSkin.wl[1362].w[128]') 
        val = cmds.getAttr ( skinCls + '.wl[%s].w[%s]'%(x, jntNum) ) 
        if val > 0.0:
            verts[ x ] = val
    
    return verts



def getJointIndex( skinCls, jntName ):
    connections = cmds.listConnections( jntName + '.worldMatrix[0]', p=1)
    skinJntID = ''
    for cnnt in connections:
        if skinCls == cnnt.split('.')[0]:
            skinJntID = cnnt
    jntID = re.findall ( '\d+', skinJntID )

    return jntID[-1]


    
#select source shape-curves and run( “커브 이름” +X / curve.cvs 갯수가 달라도 된다 ) 
def copyCurveSel():

    crvSel = cmds.ls( sl=1, l=1, type="transform" )
    for crv in crvSel:        
        cmds.select( crv, r=1 )
        name = crv.split("|")
        sourceCrv = cmds.rename(  name[-1]+"X" )
        cmds.xform(sourceCrv, ws=1, t=(0,0,0))
        
        if ":" in sourceCrv:
            srcName = sourceCrv.split(":")
            targetCrv = srcName[-1][:-1]
            print targetCrv
        else:
            targetCrv = sourceCrv[:-1]
            
        if cmds.objExists( targetCrv ):            
            cmds.select( sourceCrv, targetCrv )
            copyCurveShapes()

'''# select source curve first and target curve
def copyCurveShapes():
    crvSel = cmds.ls(os=1, fl=1, long=1, type= "transform")
    scCv = cmds.ls(crvSel[0]+".cv[*]", l=1, fl=1 )
    dnCv = cmds.ls(crvSel[1]+".cv[*]", l=1, fl=1 )
    if len(scCv) == len( dnCv ):
        for i in range(len(dnCv)):
            scPos = cmds.xform(scCv[i], q=1, ws=1, t=1 )
            cmds.setAttr( dnCv[i]+".xValue", scPos[0])
            cmds.setAttr( dnCv[i]+".yValue", scPos[1])
            cmds.setAttr( dnCv[i]+".zValue", scPos[2])   
    
    else:
        increm=1.0/(len(dnCv)-1)
        for i, dnVtx in enumerate( dnCv ):
            dnPOC = cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = 'dnPOC'+ str(i+1).zfill(2))
            cmds.connectAttr ( crvSel[0] + ".worldSpace",  dnPOC + '.inputCurve')
    	    cmds.setAttr ( dnPOC + '.turnOnPercentage', 1 )
    	    cmds.setAttr ( dnPOC + '.parameter', increm *i )	    
    	
            xyz = cmds.getAttr(dnPOC+".position" )
            cmds.setAttr( dnVtx+".xValue", xyz[0][0] )
            cmds.setAttr( dnVtx+".yValue", xyz[0][1] )
            cmds.setAttr( dnVtx+".zValue", xyz[0][2] )'''	
#mirror A crv for B crv 
def copyCurveShape( ):
    
    crvSel = cmds.ls(os=1, fl=1, long=1, type= "transform")
    scCrv = crvSel[0]
    tgtCrv = crvSel[1]
    scCvs = cmds.ls( scCrv+".cv[*]", l=1, fl=1 )
    dnCvs = cmds.ls( tgtCrv+".cv[*]", l=1, fl=1 )
    
    scStart = cmds.xform( scCvs[0], q=1, os=1, t=1)
    scEnd = cmds.xform( scCvs[-1], q=1, os=1, t=1)
    #get sc curve u direction
    scDirection = scEnd[0] - scStart[0]
    
    dnStart = cmds.xform( dnCvs[0], q=1, os=1, t=1)
    dnEnd = cmds.xform( dnCvs[-1], q=1, os=1, t=1)
    #get curve u direction
    dnDirection = dnEnd[0] - dnStart[0]
    
    scLeng = len(scCvs )
    dnLeng = len(dnCvs )
    
    scBBox = cmds.xform(scCrv, q=1, bb=1 )
    dnBBox = cmds.xform(tgtCrv, q=1, bb=1 )
    if scLeng == dnLeng:    

        for i in range( scLeng ):
            scPos = cmds.xform(scCvs[i], q=1, os=1, t=1 )
            print dnCvs[i], scPos[0]
            cmds.setAttr( dnCvs[i]+".xValue", scPos[0] )
            cmds.setAttr( dnCvs[i]+".yValue", scPos[1] )
            cmds.setAttr( dnCvs[i]+".zValue", scPos[2] )
                    
    else:
        cmds.confirmDialog( title='Confirm', message='select curves with same number of cvs' )
                
                
            
'''# select left curve and right curve
def mirrorCurveShape():
    print "mirror"

    crvSel = cmds.ls(os=1, fl=1, type= "transform")
    scCrv = crvSel[0]
    dnCvs = cmds.ls(crvSel[1]+".cv[*]", l=1, fl=1 )
    
    mrrCrv = cmds.duplicate( scCrv, rc= 1, n= "mrr_" + scCrv)[0]
    cmds.makeIdentity( mrrCrv, t=1, r=1, s=1 )
    axis = ['x', 'y', 'z']
    attrs = ['t', 'r', 's']
    for ax in axis:
        for attr in attrs:
            cmds.setAttr( mrrCrv + '.'+attr+ax, lock=0 )
            
    cmds.setAttr( mrrCrv + ".sx", -1 )
    cmds.makeIdentity( mrrCrv, apply=1, t= 1, r= 1, s= 1, n= 0, pn= 1 )
    mrrCv = cmds.ls(mrrCrv +".cv[*]", l=1, fl=1 )
            
    leng = len(mrrCv)
    if leng == len(dnCvs):
        for i in range(leng ):
            scPos = cmds.xform(mrrCv[i], q=1, ws=1, t=1 )
            cmds.setAttr( dnCvs[i]+".xValue", scPos[0] )
            cmds.setAttr( dnCvs[i]+".yValue", scPos[1] )
            cmds.setAttr( dnCvs[i]+".zValue", scPos[2] )
    
    else:
        increm=1.0/(len(dnCvs)-1)
        for i, dnVtx in enumerate( dnCvs ):
            dnPOC = cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = 'dnPOC'+ str(i+1).zfill(2))
            cmds.connectAttr ( mrrCv + ".worldSpace",  dnPOC + '.inputCurve')
    	    cmds.setAttr ( dnPOC + '.turnOnPercentage', 1 )
    	    cmds.setAttr ( dnPOC + '.parameter', increm *i )	    
    	
            xyz = cmds.getAttr(dnPOC+".position" )
            cmds.setAttr( dnVtx+".xValue", xyz[0][0] )
            cmds.setAttr( dnVtx+".yValue", xyz[0][1] )
            cmds.setAttr( dnVtx+".zValue", xyz[0][2] )	
    print mrrCrv
    cmds.delete(mrrCrv)'''           

def mirrorCurveShape( ):
    
    crvSel = cmds.ls(os=1, fl=1, long=1, type= "transform")
    scCrv = crvSel[0]
    tgtCrv = crvSel[1]
    scCvs = cmds.ls( scCrv+".cv[*]", l=1, fl=1 )
    dnCvs = cmds.ls( tgtCrv+".cv[*]", l=1, fl=1 )
    
    scStart = cmds.xform( scCvs[0], q=1, os=1, t=1)
    scEnd = cmds.xform( scCvs[-1], q=1, os=1, t=1)
    #get sc curve u direction
    scDirection = scEnd[0] - scStart[0]
    
    dnStart = cmds.xform( dnCvs[0], q=1, os=1, t=1)
    dnEnd = cmds.xform( dnCvs[-1], q=1, os=1, t=1)
    #get curve u direction
    dnDirection = dnEnd[0] - dnStart[0]
    
    scLeng = len(scCvs )
    dnLeng = len(dnCvs )

    scBBox = cmds.xform(scCrv, q=1, bb=1 )
    dnBBox = cmds.xform(tgtCrv, q=1, bb=1 )

    print "sitting on X -X or -X X"
    if scDirection*dnDirection > 0: 
        if scLeng == dnLeng:
            for i in range( scLeng ):
                scPos = cmds.xform(scCvs[i], q=1, os=1, t=1 )
                
                cmds.setAttr( dnCvs[dnLeng-i-1]+".xValue", -scPos[0] )
                cmds.setAttr( dnCvs[dnLeng-i-1]+".yValue", scPos[1] )
                cmds.setAttr( dnCvs[dnLeng-i-1]+".zValue", scPos[2] )
        
        else:
            cmds.confirmDialog( title='Confirm', message='select curves with same number of cvs' )
            '''increm=1.0/(dnLeng-1)
            for j in range( dnLeng ):                
                dnPOC = cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = 'dnPOC'+ str(j+1).zfill(2))
                crvShape = cmds.listRelatives( scCrv, c=1, s=1, ni =1 )[0] 
                cmds.connectAttr ( crvShape + ".worldSpace",  dnPOC + '.inputCurve')
                cmds.setAttr ( dnPOC + '.turnOnPercentage', 1 )
                cmds.setAttr ( dnPOC + '.parameter', increm *i )        	
                xyz = cmds.getAttr(dnPOC+".position" )
                cmds.setAttr( dnCvs[dnLeng-i-1]+".xValue", -xyz[0][0] )
                cmds.setAttr( dnCvs[dnLeng-i-1]+".yValue", xyz[0][1] )
                cmds.setAttr( dnCvs[dnLeng-i-1]+".zValue", xyz[0][2] )'''	
                
    elif scDirection*dnDirection < 0:            
  
        if scLeng == dnLeng:
            for i in range( scLeng ):
                scPos = cmds.xform(scCvs[i], q=1, os=1, t=1 )
                
                cmds.setAttr( dnCvs[i]+".xValue", -scPos[0] )
                cmds.setAttr( dnCvs[i]+".yValue", scPos[1] )
                cmds.setAttr( dnCvs[i]+".zValue", scPos[2] )
        
        else:
            cmds.confirmDialog( title='Confirm', message='select curves with same number of cvs' )
'''                
    else: 
        print "sitting on X X or -X -X"
        if scDirection*dnDirection > 0: 
            if scLeng == dnLeng:
                for i in range( scLeng ):
                    scPos = cmds.xform(scCvs[i], q=1, os=1, t=1 )
                    scEndPos = cmds.xform(scCvs[dnLeng-i-1], q=1, os=1, t=1 )
                    #scXPos = cmds.xform(scCvs[dnLeng-i-1], q=1, os=1, t=1 )
                    cmds.setAttr( dnCvs[dnLeng-i-1]+".xValue", scEndPos[0] )
                    cmds.setAttr( dnCvs[dnLeng-i-1]+".yValue", scPos[1] )
                    cmds.setAttr( dnCvs[dnLeng-i-1]+".zValue", scPos[2] )
            
            else:
                cmds.confirmDialog( title='Confirm', message='select curves with same number of cvs' )
                    
        elif scDirection*dnDirection < 0:            
                    
            if scLeng == dnLeng:
                for i in range( scLeng ):
                    scPos = cmds.xform(scCvs[i], q=1, os=1, t=1 )
                    scEndPos = cmds.xform(scCvs[dnLeng-i-1], q=1, os=1, t=1 )
                    cmds.setAttr( dnCvs[i]+".xValue", scEndPos[0] )
                    cmds.setAttr( dnCvs[i]+".yValue", scPos[1] )
                    cmds.setAttr( dnCvs[i]+".zValue", scPos[2] )
            
            else:
                cmds.confirmDialog( title='Confirm', message='select curves with same number of cvs' )'''
                
                
def mirror_eyeLidShape( ABCD ):

    print "l_up%sLid_crv"%ABCD[0]
    for ud in ["up","lo"]:
        if cmds.objExists("l_%s%sLid_crv"%(ud, ABCD[0] )):
            cmds.select( cl=1 )
            cmds.select( "l_%s%sLid_crv"%(ud,ABCD[0] ) )
            cmds.select( "r_%s%sLid_crv"%(ud,ABCD[1] ), add=1 )
            mirrorCurveShape( )
            
            cmds.select( cl=1 )
            cmds.select( "l_%s%sLid_crv"%(ud,ABCD[1] ) )
            cmds.select( "r_%s%sLid_crv"%(ud,ABCD[0] ), add=1 )
            mirrorCurveShape( )    
        
        else:
            cmds.confirmDialog( title='Confirm', message='EyeLid curves not exists' )

            

# run after faceWeightCalculate done( 입술 코너 cluster는 headSkin 보조적인 역할 )
#create lipCorner clusters to help skinCluster refining lipCorners
def lipCornerCls():
    headGeo = cmds.getAttr("helpPanel_grp.headGeo")
    # create lipCornerClusters
    lipEPos = cmds.xform("lipEPos", q=1, ws=1, t=1 )
    #lipWLoc = cmds.spaceLocator(  n= "lipWPos" )
    #cmds.parent(lipWLoc, 'allPos')
    lipWPos = [ -lipEPos[0], lipEPos[1], lipEPos[2] ]
    
    #lipCorner cluster and lip curves connecttion
    upLipCrvPoc=cmds.ls("upLipCrv*_poc", fl=1, type ="pointOnCurveInfo")
    upCtlCrvPoc=cmds.ls("upLipCtl*_poc", fl=1, type ="pointOnCurveInfo")

    #list "*Lip_Crv" , "*LipCtl_crv" corner poc node 
    lCornerPoc = [ upLipCrvPoc[-1], upCtlCrvPoc[-1] ]
    rCornerPoc = [ upLipCrvPoc[0], upCtlCrvPoc[0] ]

    for jnt in ['l_cornerUp_jnt','r_cornerUp_jnt','l_cornerDwn_jnt','r_cornerDwn_jnt']:     
        
        handle = cmds.duplicate( "lipEPos", po =1, n= jnt.replace("jnt","handle") )
        handleP = cmds.duplicate( handle[0], n= jnt.replace("jnt","clsP") )
        cmds.parent( handle[0], handleP[0] )
        cmds.parent ( handleP[0], "cls_grp")
        
        if "l_" in jnt:
            cmds.xform( handleP[0] , ws=1, t = lipEPos )
            endPoc = lCornerPoc
            minusX = -2
        
        elif "r_" in jnt:
            cmds.xform( handleP[0] , ws=1, t = lipWPos )
            endPoc = rCornerPoc
            minusX = 0
        
        clsNode = cmds.cluster( headGeo, n= jnt.replace("jnt","cls"), bindState =1, wn = ( handle[0], handle[0] ))
        print clsNode
        cmds.select(headGeo, r=1 )
        cmds.percent( clsNode[0], v=0.0 )    

        #plus poc.positionXY 
        plus = cmds.shadingNode("plusMinusAverage", asUtility=1, n = jnt.replace("jnt","pocPlus") )
        
        if "up" in jnt.lower():
            #positionY sum for lipCorner cls.ty
            upClamp = cmds.shadingNode("clamp", asUtility=1, n = jnt.replace("jnt", "clamp"))
            cmds.setAttr( upClamp + ".max", 1,1,1)
            cmds.connectAttr( endPoc[0]+".result.position.positionY ", upClamp + ".inputR" )
            cmds.connectAttr( endPoc[1]+".result.position.positionY ", upClamp + ".inputG" )
            cmds.connectAttr ( upClamp + ".outputR", plus + ".input3D[0].input3Dy" )
            cmds.connectAttr ( upClamp + ".outputG", plus + ".input3D[1].input3Dy" )            
            
            #positionXZ sum for lipCorner cls.tx / tz
            cmds.connectAttr( endPoc[0]+".result.position.positionX ", plus + ".input3D[0].input3Dx" )
            cmds.connectAttr( endPoc[1]+".result.position.positionX ", plus + ".input3D[1].input3Dx" )
            cmds.setAttr( plus + ".input3D[2].input3Dx", minusX )
            
            cmds.connectAttr( endPoc[0]+".result.position.positionZ ", plus + ".input3D[0].input3Dz" )
            cmds.connectAttr( endPoc[1]+".result.position.positionZ ", plus + ".input3D[1].input3Dz" )
            
            
            division = cmds.shadingNode("multiplyDivide", asUtility =1, n = jnt[:2] + "upTXMult" ) 
            
            cmds.setAttr( division + ".input2X", 2 )
            cmds.setAttr( division + ".input2Y", 4 )
            cmds.setAttr( division + ".input2Z", -0.5 )
            
            cmds.connectAttr( plus + ".output3Dx", division+".input1X" )
            cmds.connectAttr( plus + ".output3Dy", division+".input1Y" )
            cmds.connectAttr( plus + ".output3Dz", division+".input1Z" )            
            
            cmds.connectAttr( division+ ".outputX", clsNode[1]+".tx" )
            cmds.connectAttr ( division+ ".outputY", clsNode[1]+".ty" )
            cmds.connectAttr( division+ ".outputZ", clsNode[1]+".tz" ) 


        elif "dwn" in jnt.lower():
            
            loCond = cmds.shadingNode("condition", asUtility=1, n = jnt.replace("jnt", "cond"))
            
            #positionXYZ sum for lipCorner cls.tx/ ty / tz
            cmds.connectAttr( endPoc[0]+".result.position.positionX ", plus + ".input3D[0].input3Dx" )
            cmds.connectAttr( endPoc[1]+".result.position.positionX ", plus + ".input3D[1].input3Dx" )
            cmds.setAttr( plus + ".input3D[2].input3Dx", minusX )
            
            cmds.connectAttr( endPoc[0]+".result.position.positionY ", plus + ".input3D[0].input3Dy" )
            cmds.connectAttr( endPoc[1]+".result.position.positionY ", plus + ".input3D[1].input3Dy" )
              
            cmds.connectAttr( endPoc[0]+".result.position.positionZ ", plus + ".input3D[0].input3Dz" )
            cmds.connectAttr( endPoc[1]+".result.position.positionZ ", plus + ".input3D[1].input3Dz" )
            
            #if "ty" is less than 0, clusters start moving  
            cmds.connectAttr( plus + ".output3Dy" , loCond + ".firstTerm" )
            cmds.setAttr( loCond + ".operation", 4 )
            cmds.setAttr( loCond + ".colorIfFalse", 0,0,0 )
            cmds.connectAttr( plus + ".output3Dx" , loCond + ".colorIfTrueR" )
            cmds.connectAttr( plus + ".output3Dy" , loCond + ".colorIfTrueG" )
            cmds.connectAttr( plus + ".output3Dz" , loCond + ".colorIfTrueB" )
            
            multi = cmds.shadingNode("multiplyDivide", asUtility =1, n = jnt[:2] + "dwnMult" )
            txRemap = cmds.shadingNode("remapValue", asUtility =1, n = jnt[:2] + "dwnTXremap" )
            tzRemap = cmds.shadingNode("remapValue", asUtility =1, n = jnt[:2] + "dwnTZremap" )
            
            # cls.ty(0 ~ -1) * "multi node" input2 define 
            cmds.connectAttr( plus + ".output3Dx" , txRemap + ".inputValue" )
            cmds.setAttr( txRemap +".inputMin", 0 )
            cmds.setAttr( txRemap +".inputMax", -1 )
            cmds.setAttr( txRemap +".outputMin", 0 )
            cmds.setAttr( txRemap +".outputMax", 2 )
            cmds.connectAttr( txRemap + ".outValue", multi + ".input2X" )
            
            cmds.setAttr( multi + ".input2Y", 2 )

            cmds.connectAttr( plus + ".output3Dz" , tzRemap + ".inputValue" )
            cmds.setAttr( tzRemap +".inputMin", 0 )
            cmds.setAttr( tzRemap +".inputMax", -1 )
            cmds.setAttr( tzRemap +".outputMin", 0 )
            cmds.setAttr( tzRemap +".outputMax", -.5 )
            cmds.connectAttr( tzRemap + ".outValue", multi + ".input2Z" )
            
            # "multi node" input1 define             
            cmds.connectAttr( loCond + ".outColorR", multi + ".input1X" )
            cmds.connectAttr( loCond + ".outColorG", multi + ".input1Y" )
            cmds.connectAttr( loCond + ".outColorB", multi + ".input1Z" )
            
            cmds.connectAttr( multi+ ".outputX", clsNode[1]+".tx" )
            cmds.connectAttr( multi+ ".outputY", clsNode[1]+".ty" )
            cmds.connectAttr( multi+ ".outputZ", clsNode[1]+".tz" )   
    
    
    
    


#cheek_crv(happy, E, O...)는 *Cheek_grp을 드라이브하고 *Cheek_ctl과 볼에 영향을 주는 모든 ctrls(lipCtrlLTip,  )은 *cheek_jnt를 드라이브한다.  
def faceClsMirrorWgt():
    headGeo =cmds.getAttr("helpPanel_grp.headGeo")
    
    # pair clusters( blink, cheek...) weight mirror
    pairCls = ['l_lowCheek_cls','r_lowCheek_cls','l_cornerUp_cls','r_cornerUp_cls','l_squintPuff_cls', 'r_squintPuff_cls',
    'l_ear_cls','r_ear_cls', 'l_cheek_cls','r_cheek_cls', 'l_eyeBlink_cls', 'r_eyeBlink_cls', 'l_eyeWide_cls', 'r_eyeWide_cls' ]
     
    for j,k in zip(*[iter(pairCls)]*2):
        if cmds.objExists(j) and cmds.objExists(k):            
            cmds.copyDeformerWeights( sd = j, ss= headGeo, ds = headGeo, dd = k, mirrorMode = "YZ", surfaceAssociation = "closestPoint" )
            print "%s weight mirrored"%j
    
    # single cluster( nose, brow...) weight mirror
    singleCls = [ 'jawOpen_cls', 'jawClose_cls', 'mouth_cls', 'lip_cls', 'lipRoll_cls', 'browUp_cls', 'browDn_cls', 
    'browTZ_cls', 'nose_cls', 'upLipRoll_cls', 'bttmLipRoll_cls' ]
    for sCls in singleCls:
        if cmds.objExists(sCls):
            
            cmds.copyDeformerWeights( sd = sCls, ss= headGeo, ds = headGeo, mirrorMode = "YZ", surfaceAssociation = "closestPoint" )


#mirror cls weight left to right 
def indieClsWeightMirror( clsName ):
    headGeo = cmds.getAttr("helpPanel_grp.headGeo")
    cmds.copyDeformerWeights( sd = "l_"+clsName+"_cls", ss=headGeo, ds = headGeo, dd =  "r_"+clsName+"_cls", mirrorMode = "YZ", surfaceAssociation = "closestPoint" )
    print "%s weight mirrored"%("l_"+clsName+"_cls")


            
            

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
    
    
    
    
#first seperate the mesh for presto ctrl     
def prestoCtrl( cls, deform ):

    ctls = [  'l_lowCheek_ctl', 'r_lowCheek_ctl', 'l_squintPuff_ctl', 'r_squintPuff_ctl', 'l_ear_ctl', 'r_ear_ctl', 'nose_ctl' ]
    for c in ctls:
        if c and cmds.nodeType(c)=="nurbsCurve":
            cmds.xform( c,  cpc = 1 )
            wrapCtrl = cmds.duplicate( c, n = c.replace("ctl","wrap"))
            #select driver(source) and driven(target)
            cmds.select("head_REN", wrapCtrl[0])
            args = cmds.ls(os=1)
            kwargs = { "weightThreshold": 1.0, 'maxDistance':1.0, 'exclusiveBind':0 , 'autoWeightThreshold':1, 'falloffMode':0}
            createWrap(*args,**kwargs)
            ctlBS = cmds.blendShape( wrapCtrl[0], c, origin = "world", n = c.replace("_ctl","BS") )
            cmds.setAttr( ctlBS[0]+"."+wrapCtrl[0], 1 )
            cmds.hide(wrapCtrl[0])




#바디에 붙은 머리 먼저 선택 그리고 twitch머리 선택
#select bodyHead and twitchHead : move squachJnt_grp to the bodyHead position 
#don't use freeze transform geo 
def attachTwitchHead():
    headSel = cmds.ls(sl=1, type = "transform" )
    change=cmds.xform(headSel[1], q=1, ws=1, t=1 )
    origin=cmds.xform(headSel[0], q=1, ws=1, t=1 )
    cmds.xform("squachJnt_grp", ws=1, t=(origin[0], origin[1]-xyz[1], origin[2]-xyz[2]) )



def deleteUnknown_plugins():
    unknown_plugins = cmds.unknownPlugin(q=True, list=True) or []
    for up in unknown_plugins:
        print up
        cmds.unknownPlugin(up, remove=True)


    
# miscellaneous_____________________________________________________________________________________________________________
  



    
def storeSrcWgt( geo, dformer ):
    
    vtxLeng = cmds.polyEvaluate( geo, v=1 ) 
    wgt = []
    if cmds.nodeType(dformer) == "cluster":
        
        geoID = geoIDforCls( geo, cls)
        wgt = cmds.getAttr(  cls[0] + ".wl[%s].w[0:%s]"%( str(geoID), str(vtxLeng-1) ))

    elif cmds.nodeType(dformer)== "blendShape":
            
        alias = cmds.aliasAttr(dformer, q=1)
        tgID = ""
        for tgt, wgt in zip(*[iter(alias)]*2):
            if cmds.getAttr( dformer + "." + tgt )== 1.0:
                number = wgt.split("[")[1]
                tgID = number[:-1]  
        
        if not tgID:
            cmds.confirmDialog( title='Confirm', message='set the blendShape.target to 1 for store its weight' )
            
        else:
            wgt = cmds.getAttr( dformer + ".inputTarget[0].inputTargetGroup[%s].targetWeights[0:%s]"%( tgID, str(vtxLeng-1)) )
        
    #elif cmds.nodeType(dformer) == "skinCluster":
    #elif cmds.nodeType(dformer) == "wire":
    if wgt:
        return wgt


        
        

#select driven first and driver
#driven을 잡고 transform을 조정하면 surface를 따라 움직인다
#mel.eval("source createMembrane")
def surfSlideDeform():
    geoSel = cmds.ls(sl=1, type = "transform")
    driver = geoSel[-1]
    driverShape = cmds.listRelatives(driver, c=1, ni=1, s=1 )
    cmds.select(geoSel[0])
    membrane = mel.eval("createMembrane")
    for att in ["gravity", "windSpeed", "drag","tangentialDrag"]:
        cmds.setAttr(membrane[0]+"."+att, 0 )    
    cmds.connectAttr( driverShape[0]+".worldMesh", membrane[0]+".collideMesh" )
    cmds.setAttr(membrane[0]+".thickness", -0.010 )
    cmds.setAttr(membrane[0]+".pushOut", -1 )
    cmds.setAttr(membrane[0]+".pushOutRadius", 5 )#radius by pushout
    cmds.setAttr(membrane[0]+".bendResistance", 10 )
    cmds.setAttr(membrane[0]+".rigidity", .5 )
    
    

    
               

def wideJntBlink():
    for LR in ["l_up","l_lo","r_up", "r_lo" ]:
        
        blinkCtl =LR[:2]+"blinkMinus_mult"
        blinkWideRemap = cmds.shadingNode ('remapValue', asUtility =1, n = LR +'wideBlink_remap' )
        cmds.connectAttr( blinkCtl+".outputY", blinkWideRemap+".inputValue" )      
        cmds.setAttr(blinkWideRemap+".inputMin", 1.0)
        cmds.setAttr(blinkWideRemap+".inputMax", 2.0)
        if "up" in LR:
            cmds.setAttr(blinkWideRemap+".outputMax", -0.5 )
        elif "lo" in LR:
            cmds.setAttr(blinkWideRemap+".outputMax", 0.5 )
        
        minMaxMult = cmds.ls(LR + "MinMax_mult*", fl=1, type = 'multiplyDivide')
        startCons = cmds.ls(LR+"StartCon*", fl=1, type = 'condition')
    
        if "lo" in LR:
            for i, sc in enumerate(startCons):
                blink_add = cmds.shadingNode ( 'addDoubleLinear', asUtility=True, n = LR + 'wideBlink_add'+str(i+1).zfill(2) )
                cmds.connectAttr( sc +".outColorG", blink_add + ".input1"  )
                cmds.connectAttr( blinkWideRemap+".outValue",  blink_add + ".input2" )
                cmds.connectAttr( blink_add + ".output", LR+"JntMult"+str(i+1).zfill(2)+".input1X", f=1 )        
        else:
            wide_add = cmds.shadingNode ( 'addDoubleLinear', asUtility=True, n = LR + 'wide_add' ) 
            cmds.connectAttr( blinkWideRemap+".outValue", wide_add+".input1" )
            cmds.connectAttr( LR[0]+"EyeShapeCtrl.tx", wide_add+".input2" )            
            for i, sc in enumerate(startCons):
        
            	blink_add = cmds.shadingNode ( 'addDoubleLinear', asUtility=True, n = LR + 'wideBlink_add'+str(i+1).zfill(2) )
            	cmds.connectAttr( wide_add+".output", minMaxMult[i]+".input1Z" )
            	cmds.connectAttr("upMin_crvShape.controlPoints[%s].yValue"%str(i), minMaxMult[i]+".input2Z" )
            	cmds.connectAttr( sc +".outColorG", blink_add + ".input1"  )
            	cmds.connectAttr( minMaxMult[i]+".outputZ",  blink_add + ".input2" )
            	cmds.connectAttr( blink_add + ".output", LR+"JntMult"+str(i+1).zfill(2)+".input1X", f=1 )  

                

    
        
        
        
#arFaceHeadSkin first, export browWgt then calculate!! 
def browWeightCalculate():

    size = cmds.polyEvaluate( "head_REN", v = 1)
    browUDWgt = cmds.getAttr ( "browUD_cls.wl[0].w[0:%s]"%str(size-1))
    browTZWgt = cmds.getAttr ( "browTZ_cls.wl[0].w[0:%s]"%str(size-1))
    eyeBlinkWgt =cmds.getAttr ( "eyeBlink_cls.wl[0].w[0:%s]"%str(size-1))
    eyeWideWgt = cmds.getAttr ( "eyeWide_cls.wl[0].w[0:%s]"%str(size-1))
    jawCloseWgt = cmds.getAttr ("jawClose_cls.wl[0].w[0:%s]"%str(size-1))
    cheekWgt = cmds.getAttr ( "l_cheek_cls.wl[0].w[0:%s]"%str(size-1))
    browDict = clsVertsDict( 'head_REN', 'browUD_cls')
    browNum = [i for i in browDict] 
    browVert = [ 'head_REN.vtx[%s]'%t for t in browNum ]
    headSkelID = getJointIndex( 'headSkin', 'headSkel_jnt' )
    cmds.setAttr( "headSkin.envelope", 0 )
    #browUDWgt >= browTZWgt  
    for x in range(size):
        if browUDWgt[x]>1:
            print browUDWgt[x]
            browUDWgt[x] = 1
            
        vtxVal= browUDWgt[x]-browTZWgt[x]
        if vtxVal<0:
            print vtxVal
            browTZWgt[x] = browUDWgt[x]
      
        # take out negative value from browWgt, if 1 - (eyeLid + brow weight) < 0 
        #eyeBrowVal =  eyeWideWgt + browUDWgt
        eyeBrowVal = max(eyeWideWgt[x], eyeBlinkWgt[x]) + browUDWgt[x]
        negBrowVal = 0
        if eyeBrowVal>1: # normalize weight
            negBrowVal = 1-eyeBrowVal
        browUDWgt[x] +=negBrowVal
      
                  
    # set headSkel_jnt weight first
    for bn in browNum:
        minusBrowVal = 1-( browUDWgt[bn]+ max(eyeWideWgt[bn], eyeBlinkWgt[bn])+jawCloseWgt[bn] +cheekWgt[bn])
        #make a space for the eyelid weight
        cmds.setAttr('headSkin.wl[%s].w[%s]'%(bn, headSkelID), minusBrowVal )  
             
    dataPath = cmds.fileDialog2(fileMode=3, caption="set directory")
    if os.path.exists(dataPath[0] + '/browMapSkin.xml'):  
        browSkinWeight = ET.parse( dataPath[0] + '/browMapSkin.xml')
        rootBrowSkin = browSkinWeight.getroot()
    
        browPJnts = cmds.ls ("*_browP*_jnt", type ="joint")
        childJnts = cmds.listRelatives(browPJnts, c =1, type = "joint")     
        for f in range(2, len(rootBrowSkin)-2 ):
            browJnt = rootBrowSkin[f].attrib['source']
            if browJnt in childJnts:
                browPJnt = cmds.listRelatives( browJnt, p=1, type = "joint" )
                parentJntID = getJointIndex('headSkin',browPJnt[0] ) 
                childJntID = getJointIndex('headSkin',browJnt )
                for dict in rootBrowSkin[f]:
                    vertIndex = int(dict.attrib['index'])
                    wgtValue= float(dict.attrib['value'])
                    #if vertIndex in browTZNum:                 
                    cmds.setAttr ( 'headSkin.wl['+ str(vertIndex) + "].w[" + str(childJntID)+ "]", ( browTZWgt[vertIndex]* wgtValue) )
             
                    #elif vertIndex in restVert:
                    restVal = ( browUDWgt[vertIndex] - browTZWgt[vertIndex])* wgtValue
                    cmds.setAttr ( 'headSkin.wl['+ str(vertIndex) + "].w[" + str(parentJntID) + "]", restVal )
                    
    cmds.copySkinWeights( ss='headSkin', ds='headSkin', mirrorMode='YZ', sa="closestPoint", influenceAssociation="oneToOne", normalize =1 )
    #cmds.setAttr( "headSkin.envelope", 1 )

    
    

'''
1. headSkel의 월드 transform값을 상쇄시켜준다. inverseMatrix값을 eyeParent("InverseHeadSkel")에 연결
2. EyeballRot의 월드 matrix를 L_EyeDecompose에 연걸
3. l_lo/up/cnrLidP_jnt driven by LeyeOffsetCtrl
5. parent eyeball under "EyeballRot" for all the defroming
6.   create instance eyeball / parent under "eyeOffSet" to follow bodyRig 
7. "lEyePos.rotate" line up with "l_eyeRP.rot"/
'''
#create "L_EyeDecompose" to attach to body
def createEyeRig():
    
    if cmds.objExists("eyeRigP")==False:
        eyeRigP = cmds.group( em=True, n = "eyeRigP", p= "eyeRig" )      

    if cmds.objExists('eyeTR')==False:
        eyeRigTR = cmds.group( em=True, n = 'eyeTR', p= 'eyeRigP' )
    else:
        eyeRigTR = "eyeTR"
        if not "eyeRigP" in cmds.listRelatives( eyeRigTR, p = 1 ):
            cmds.parent( eyeRigTR, "eyeRigP")
    
    headSkel = cmds.listRelatives("eyeRig", p=1 )[0]
       
    for LR in ["l_","r_"]:
        if cmds.objExists( LR + 'eyeP' ):
            cmds.confirmDialog( title='Confirm', message='the EyeRig already created' )
        else:
            EyePos = cmds.xform( 'lEyePos', t = True, q = True, ws = True)
            EyeRot = cmds.xform( 'lEyePos', ro = True, q = True, ws = True)
            if LR == "r_":
                EyePos = [ -EyePos[0], EyePos[1], EyePos[2] ]
                EyeRot = [ EyeRot[0], -EyeRot[1], EyeRot[2] ]       
                       
            DMat = cmds.shadingNode( 'decomposeMatrix', asUtility =1, n = LR +'EyeDMat')
            inverseDMat = cmds.shadingNode( 'decomposeMatrix', asUtility =1, n = LR+'inverseDMat')  
            #ffdSquachLattice = cmds.group(em =1, n = 'ffdSquachLattice', p = 'eyeRigP')
            EyeP = cmds.group(em=True, n = LR + 'eyeP', p= eyeRigTR) 
            cmds.xform( EyeP, ws =1, t =(EyePos[0], EyePos[1], EyePos[2])) 
            EyeRP = cmds.group(em=True, n = LR + 'eyeRP', p= EyeP )
            cmds.setAttr( EyeRP + ".ry", EyeRot[1] )
            cmds.setAttr( EyeRP + ".rx", EyeRot[0] )
            EyeScl = cmds.group(em=True, n = LR + 'eyeScl', p= EyeRP )
            #squachSetup.indieScaleSquach( EyeScl, "y" ) 
            EyeRot = cmds.group(em=True, n = LR + 'eyeRot', p= EyeScl )
            EyeballRot = cmds.group(em=True, n = LR + 'eyeballRot', p= EyeRot )
            # EyeBallRot worldMatrix - HeadSkel.worldMatrix --> eyeDecompose
            cmds.connectAttr( headSkel + ".worldInverseMatrix", inverseDMat +".inputMatrix")        
            cmds.connectAttr( EyeballRot + ".worldMatrix", DMat + ".inputMatrix" )
                
            #under headTRS    
            decomNullP = cmds.group( em=1, n =LR + "eyeDecomposeP", p = "supportRig" )
            decomNull = cmds.group( em=1, n = LR+ "eyeDecompose" , p = decomNullP )
            eyeBallTran = cmds.group( em=1, n =LR+ "eyeTransform", p = decomNull )
            cmds.xform( decomNullP, ws =1, t =(EyePos[0], EyePos[1], EyePos[2] ))
            #connect inverseDMat
            cmds.connectAttr( inverseDMat + ".outputTranslate", decomNullP + ".t" )
            cmds.connectAttr( inverseDMat + ".outputRotate", decomNullP + ".r" )
            cmds.connectAttr( inverseDMat + ".outputScale", decomNullP + ".s" )   
            cmds.connectAttr( inverseDMat + ".outputShear", decomNullP + ".shear" ) 
            
            cmds.connectAttr( DMat + ".outputTranslate", decomNull + ".t" )
            cmds.connectAttr( DMat + ".outputRotate", decomNull + ".r" )
            cmds.connectAttr( DMat + ".outputScale", decomNull + ".s" )   
            cmds.connectAttr( DMat + ".outputShear", decomNull + ".shear" ) 
            
            ctl = LR+"eye_ctl"
            if cmds.objExists( ctl ):
                mult = cmds.shadingNode("multiplyDivide", asUtility=1, n = LR + "eyeBall_mult")
                cmds.connectAttr( ctl + ".tx", mult + ".input1X")
                cmds.connectAttr( ctl + ".ty", mult + ".input1Y") 
                cmds.connectAttr( "lidFactor.eyeBallRotY_scale", mult + ".input2X")
                cmds.connectAttr( "lidFactor.eyeBallRotX_scale", mult + ".input2Y")
                cmds.connectAttr( mult + ".outputX", EyeballRot + ".ry")
                cmds.connectAttr( mult + ".outputY", EyeballRot + ".rx")
            else:
                cmds.confirmDialog( title='Confirm', message='import "shape panel" first' )


'''#eyeLid push "lidFactor.lValA : 
def lidPushFactor():
    if not cmds.objExists('lidFactor'):
        #set the start with plusMinusAverage  
        cmds.group( n = "lidFactor", em = 1, p = "faceMain" )   
    
    pushY_mult = cmds.shadingNode( 'multiplyDivide', asUtility =1, n ='lidPushY_mult')

    prefix = [ 'l_', 'r_' ]
    for LR in prefix:

        if 'l_' in LR:
            XYZ = 'X'

        if 'r_' in LR:
            XYZ = 'Y' 
         
        #Y = lookUp/Down  X = lookLeft/Right           
        cmds.addAttr('lidFactor', longName= LR + "lidPushY", attributeType='float', dv = 0)                      
        cmds.addAttr('lidFactor', longName= LR + "lidPushX", attributeType='float', dv = 0) 
        
        cmds.addAttr('lidFactor', longName= LR + "valA", attributeType='float', dv = 0)
        cmds.addAttr('lidFactor', longName= LR + "valB", attributeType='float', dv = 0)
        
        
        #make -JumperPanel.l_lidPushY into +
        cmds.connectAttr ( 'lidFactor.' + LR + 'lidPushY', pushY_mult + '.input1'+XYZ)
        cmds.setAttr ( pushY_mult + '.input2'+XYZ, -1 )
        
        #ValA and ValB define by LidPushY clamp
        pushY_clamp = cmds.shadingNode( 'clamp', asUtility =1, n = LR + 'lidPushY_clamp')
        cmds.setAttr ( pushY_clamp + '.maxR', 1 )
        cmds.setAttr ( pushY_clamp + '.maxG', 1 )
        #ValAB / LidPushY defined by l_eyeballRotX 
        cmds.connectAttr ( 'lidFactor.' + LR + 'lidPushY', pushY_clamp + '.inputR')
        cmds.connectAttr ( pushY_mult + '.output'+XYZ, pushY_clamp + '.inputG' )
        cmds.connectAttr (  pushY_clamp + '.outputR', 'lidFactor.' + LR + 'valA') # l_valA = + lidPushY
        cmds.connectAttr (  pushY_clamp + '.outputG', 'lidFactor.' + LR + 'valB')# l_valB = -(-lidPushY)        
        
        #l_eyeballRotX --> 'lidFactor.l_lidPushY'
        
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
        cmds.connectAttr ( pushY_con+ '.outColorR', 'lidFactor.' +LR+ 'lidPushY' )
        
        #l_eyeballRotY --> 'lidFactor.l_lidPushX'
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
        cmds.connectAttr ( pushX_con+ '.outColorG', 'lidFactor.' +LR+ 'lidPushX' )'''
        
        
        


def lidPush_blink_squint():
    
    for LR in ['l_','r_']:
        #squint ctl connection to blendshape
        BCDtypeCtrlSetup.CCtrlSetup( LR + "eyeSquint", LR, ["y","x"], [LR + "upSquint_crv", LR + "loSquint_crv"], [LR + "upAnnoyed_crv", LR + "loAnnoyed_crv"] )
        
        #blink ctl connection to blendshape
        BCDtypeCtrlSetup.BCtrlSetup(  LR[0].title() + "eye_open", "y", LR +"upWide_crv", LR + "upBlinkCrv01" )  
        BCDtypeCtrlSetup.BCtrlSetup(  LR[0].title() + "eye_open", "y", LR +"loWide_crv", LR + "loBlinkCrv01" )       
        
        #eyePush ctl connection to blendshape
        #DCtrlSetup( "l_eye_ctl", "l_lidPush", "lid")
        eyeDCtrlSetup( LR + "eyeballRot", LR+"lidPush", "lid")
        cmds.connectAttr( "lidFactor."+LR+"lidPushXPos_YPos", LR + "upLid_bs." + LR+ "upBLid_crv" )
        cmds.connectAttr( "lidFactor."+LR+"lidPushXPos_YPos", LR + "loLid_bs." + LR+ "loBLid_crv" )
        
        cmds.connectAttr( "lidFactor."+LR+"lidPushXNeg_YPos", LR + "upLid_bs." + LR+ "upALid_crv" )
        cmds.connectAttr( "lidFactor."+LR+"lidPushXNeg_YPos", LR + "loLid_bs." + LR+ "loALid_crv" )    
            
        cmds.connectAttr( "lidFactor."+LR+"lidPushXPos_YNeg", LR + "upLid_bs." + LR+ "upCLid_crv" )
        cmds.connectAttr( "lidFactor."+LR+"lidPushXPos_YNeg", LR + "loLid_bs." + LR+ "loCLid_crv" ) 
        
        cmds.connectAttr( "lidFactor."+LR+"lidPushXNeg_YNeg", LR + "upLid_bs." + LR+ "upDLid_crv" )
        cmds.connectAttr( "lidFactor."+LR+"lidPushXNeg_YNeg", LR + "loLid_bs." + LR+ "loDLid_crv" ) 


def eyeDCtrlSetup( ctl, name, factor ):    

    if "l_" in name:
        prefix = "l_"
    elif "r_" in name:
        prefix = "r_"
    else:
        prefix = name
 
    posClamp = cmds.shadingNode( 'clamp', asUtility = 1, n =prefix +'xyPos_clamp' )
    negClamp = cmds.shadingNode( 'clamp', asUtility = 1, n =prefix +'xyNeg_clamp' )        

    # tx inputValue / ty inputMin
    xPosYPos = cmds.shadingNode( 'remapValue', asUtility =1, n = prefix + 'xPosYPos_remap' )
    xNegYPos = cmds.shadingNode( 'remapValue', asUtility =1, n = prefix + 'xNegYPos_remap' )
    xPosYNeg = cmds.shadingNode( 'remapValue', asUtility =1, n = prefix + 'xPosYNeg_remap' )
    xNegYNeg = cmds.shadingNode( 'remapValue', asUtility =1, n = prefix + 'xNegYNeg_remap' )
    
    yPosXPos = cmds.shadingNode( 'remapValue', asUtility =1, n = prefix + 'yPosXPos_remap' )
    yNegXPos = cmds.shadingNode( 'remapValue', asUtility =1, n = prefix + 'yNegXPos_remap' )
    yPosXNeg = cmds.shadingNode( 'remapValue', asUtility =1, n = prefix + 'yPosXNeg_remap' )
    yNegXNeg = cmds.shadingNode( 'remapValue', asUtility =1, n = prefix + 'yNegXNeg_remap' )
    
    AMult = cmds.shadingNode( 'multiplyDivide', asUtility =1, n = prefix + 'A_Mult' )
    BMult = cmds.shadingNode( 'multiplyDivide', asUtility =1, n = prefix + 'B_Mult' )
    CMult = cmds.shadingNode( 'multiplyDivide', asUtility =1, n = prefix + 'C_Mult' )
    DMult = cmds.shadingNode( 'multiplyDivide', asUtility =1, n = prefix + 'D_Mult' )
    
    attrs = ['X_pos','Y_pos', 'X_neg', 'Y_neg','XPos_YPos', 'XPos_YNeg', 'XNeg_YNeg', 'XNeg_YPos']
    cmds.select( factor+"Factor")
    for att in attrs:
        if cmds.attributeQuery( name+att, node= factor+"Factor", exists=True)==False:
            cmds.addAttr( longName= name+att, attributeType='double' )
    
    posClamp = cmds.shadingNode( 'clamp', asUtility = 1, n =name + 'xyPos_clamp' )
    cmds.connectAttr( factor +'Factor.' + name+ 'X_pos', posClamp + ".inputR" )
    cmds.connectAttr( factor +'Factor.' + name+ 'Y_pos', posClamp + ".inputG" )
    cmds.setAttr( posClamp + ".minR", -1 )
    cmds.setAttr( posClamp + ".minG", -1 )
    cmds.setAttr( posClamp + ".maxR", 1 )
    cmds.setAttr( posClamp + ".maxG", 1 )
    
    negClamp = cmds.shadingNode( 'clamp', asUtility = 1, n =name + 'xyNeg_clamp' )
    cmds.connectAttr( factor +'Factor.' + name+ 'X_neg', negClamp + ".inputR" )
    cmds.connectAttr( factor +'Factor.' + name+ 'Y_neg', negClamp + ".inputG" )
    cmds.setAttr( negClamp + ".minR", -1 )
    cmds.setAttr( negClamp + ".minG", -1 )
    cmds.setAttr( negClamp + ".maxR", 1 )
    cmds.setAttr( negClamp + ".maxG", 1 )

    # eyeballRot RX ( = eye_ctl.ty ) reverse
    if cmds.objExists(prefix + "ctlPosMult"):
        posMult = prefix + "ctlPosMult"                
    else:
        posMult = cmds.shadingNode( "multiplyDivide", asUtility =1, n = prefix + "ctlPosMult")        
         
    cmds.setAttr( posMult + ".operation", 2 )
    cmds.setAttr( posMult + ".input2", 20, 20, 20  )   
    cmds.connectAttr( ctl + ".rx", posMult + ".input1X", f=1 )    
    cmds.connectAttr( ctl + ".ry", posMult + ".input1Y", f=1 )   
    # eyeballRot RX: 20 -방향 ( pushY neg ) 
    cmds.connectAttr( posMult + ".outputX", "lidFactor.%slidPushY_neg"%prefix, f=1 )    
    # eyeballRot RY: 20 +방향 ( pushX pos )
    cmds.connectAttr( posMult + ".outputY", "lidFactor.%slidPushX_pos"%prefix, f=1 )    
    
    if cmds.objExists(prefix + "ctlNegMult"):
        negMult = prefix + "ctlNegMult"        
    else:
        negMult = cmds.shadingNode( "multiplyDivide", asUtility =1, n = prefix + "ctlNegMult")
        
    cmds.setAttr( negMult + ".operation", 2 )
    cmds.setAttr( negMult + ".input2", -20, -20, -20  )   
    cmds.connectAttr( ctl + ".rx", negMult + ".input1X", f=1 )    
    cmds.connectAttr( ctl + ".ry", negMult + ".input1Y", f=1 )    
    # eyeballRot RX: -20 +방향 ( pushY pos ) 
    cmds.connectAttr( negMult + ".outputX", "lidFactor.%slidPushY_pos"%prefix, f=1 )    
    # eyeballRot RY: -20 -방향 ( pushX neg )
    cmds.connectAttr( negMult + ".outputY", "lidFactor.%slidPushX_neg"%prefix, f=1 )
    
    #1...xPosYPos * yPosXPos == U (BMult) # inputMin
    cmds.connectAttr( factor +'Factor.' + name+'X_pos', xPosYPos + ".inputValue" )
    #negClamp.outputG =factor +'Factor.' + name+'Y_neg'
    cmds.connectAttr( negClamp + ".outputG", xPosYPos + ".inputMin" )# set Y_neg to open plus Y
    
    cmds.connectAttr( factor +'Factor.' + name+'Y_pos', yPosXPos + ".inputValue" )
    #negClamp.outputR =factor +'Factor.' + name+'X_neg'
    cmds.connectAttr( negClamp + ".outputR", yPosXPos + ".inputMin" )# set X_neg to open plus X
    
    #multiply 2 remap
    cmds.connectAttr( xPosYPos + ".outValue", BMult + ".input1X")
    cmds.connectAttr( yPosXPos + ".outValue", BMult + ".input2X")
    cmds.connectAttr( BMult + ".outputX", factor +'Factor.' + name+'XPos_YPos')
    
    #2...xPosYNeg * yNegXPos == O (CMult)
    cmds.connectAttr( factor +'Factor.' + name+'X_pos', xPosYNeg + ".inputValue" )
    #posClamp.outputG =factor +'Factor.' + name+'Y_pos'
    cmds.connectAttr( posClamp + ".outputG", xPosYNeg + ".inputMin" )# set Y_pos to open minus Y
    
    cmds.connectAttr( factor +'Factor.' + name+'Y_neg', yNegXPos + ".inputValue" )
    #negClamp.outputR =factor +'Factor.' + name+'X_neg'
    cmds.connectAttr( negClamp + ".outputR", yNegXPos + ".inputMin" )# set X_neg to get plus X
    
    cmds.connectAttr( xPosYNeg + ".outValue", CMult + ".input1X" )
    cmds.connectAttr( yNegXPos + ".outValue", CMult + ".input2X" )
    cmds.connectAttr( CMult + ".outputX", factor +'Factor.' + name+'XPos_YNeg' )
    
    #3...xNegYNeg * yNegXNeg == Wide (DMult)
    cmds.connectAttr( factor +'Factor.' + name+'X_neg', xNegYNeg + ".inputValue" )
    #posClamp.outputG =factor +'Factor.' + name+'Y_pos'
    cmds.connectAttr( posClamp + ".outputG", xNegYNeg + ".inputMin" )# set X_pos to get minus X
    
    cmds.connectAttr( factor +'Factor.' + name+'Y_neg', yNegXNeg + ".inputValue" )
    #posClamp.outputR =factor +'Factor.' + name+'X_pos'
    cmds.connectAttr( posClamp + ".outputR", yNegXNeg + ".inputMin" )
    
    cmds.connectAttr( xNegYNeg + ".outValue", DMult + ".input1X")
    cmds.connectAttr( yNegXNeg + ".outValue", DMult + ".input2X")
    cmds.connectAttr( DMult + ".outputX", factor +'Factor.' + name+'XNeg_YNeg' )
    
    #4...xNegYNeg * yNegXNeg == E (AMult)
    cmds.connectAttr( factor +'Factor.' + name+'X_neg', xNegYPos + ".inputValue" )
    #negClamp.outputG =factor +'Factor.' + name+'Y_neg'    
    cmds.connectAttr( negClamp + ".outputG", xNegYPos + ".inputMin" )# factor +'Factor.' + name+'Y_neg'
    
    cmds.connectAttr( factor +'Factor.' + name+'Y_pos', yPosXNeg + ".inputValue" )
    #posClamp.outputR =factor +'Factor.' + name+'X_pos'
    cmds.connectAttr( posClamp + ".outputR", yPosXNeg + ".inputMin" )# factor +'Factor.' + name+'X_pos'
    
    cmds.connectAttr( xNegYPos + ".outValue", AMult + ".input1X")
    cmds.connectAttr( yPosXNeg + ".outValue", AMult + ".input2X")
    cmds.connectAttr( AMult + ".outputX", factor +'Factor.' + name+'XNeg_YPos' )


            
def eyeBallDirection():
    
    lEyePos = cmds.xform("lEyePos", q=1, ws=1, t=1)
    rEyePos = [ -lEyePos[0], lEyePos[1], lEyePos[2] ]
    aimCtlP = "eyeAim_ctl"
    aimCtlTop = cmds.duplicate( aimCtlP, po =1, n = "eyeAim_ctlTop")
    cmds.parent( aimCtlP, aimCtlTop )
    cmds.parent( aimCtlTop[0], "attachCtl_grp" )
    cmds.xform( aimCtlTop[0], ws=1, t = [0, lEyePos[1], lEyePos[2] ] )
    aimCtlKids =cmds.listRelatives( aimCtlP, c=1, type ="transform")
   
    for LR, pos in { "l_":lEyePos, "r_":rEyePos }.iteritems():        
         
        headSkelInverse = LR+"eyeDecomposeP"
        eyeDecomp = cmds.listRelatives(headSkelInverse, c=1, typ = "transform" )[0]
        eyeAimNull = cmds.group( em=1, p = headSkelInverse, n = LR + "eyeAimNull" )#l_eyeAimNull
        eyeOffSet = LR+"eyeTransform"        
            
        cmds.xform( eyeAimNull, ws=1, t =pos )
           
        aimCtlGrp = [ grp for grp in aimCtlKids if LR in grp ]        
        aimCtl = cmds.listRelatives( aimCtlGrp[0], c=1, type ="transform") 
        cmds.xform( aimCtlGrp[0], ws=1, t= pos )
        const = cmds.aimConstraint( aimCtl[0], eyeAimNull, mo=1, aimVector =[0, 0, 1], upVector=[0, 1, 0] )
            
        rotXBlend = cmds.shadingNode( "blendTwoAttr", asUtility =1, n = LR + "decompRX_blend")
        cmds.connectAttr( LR+"eyeBall_mult.outputY", rotXBlend+".input[0]")
        cmds.connectAttr( eyeAimNull + ".rx", rotXBlend+".input[1]")
        rotYBlend = cmds.shadingNode( "blendTwoAttr", asUtility =1, n = LR + "decompRY_blend")
        cmds.connectAttr( LR+"eyeBall_mult.outputX", rotYBlend+".input[0]")
        cmds.connectAttr( eyeAimNull + ".ry", rotYBlend+".input[1]")
            
        conversionX = cmds.listConnections( LR+"eyeballRot.rx", s=1, d=0, p=1, scn=1 )
        cmds.disconnectAttr( conversionX[0], LR+"eyeballRot.rx" )
        conversionY = cmds.listConnections( LR+"eyeballRot.ry", s=1, d=0, p=1, scn=1 )
        cmds.disconnectAttr( conversionY[0], LR+"eyeballRot.ry" )
        cmds.connectAttr( rotXBlend+".output", LR + "eyeballRot.rotateX" )
        cmds.connectAttr( rotYBlend+".output", LR + "eyeballRot.rotateY" )
        cmds.connectAttr( "eyeblend_dir.tx", rotXBlend+".attributesBlender" )
        cmds.connectAttr( "eyeblend_dir.tx", rotYBlend+".attributesBlender" )
        
        #eyeBall offset setup
        eyeOffCtl = LR + "eyeOffset_ctl"
        eyeOffMult = cmds.shadingNode( "multiplyDivide", asUtility=1, n =LR+"eyeOffset_mult" )
        cmds.connectAttr( eyeOffCtl+".ty", eyeOffMult + ".input1X" )
        cmds.connectAttr( eyeOffCtl+".tx", eyeOffMult + ".input1Y" )
        cmds.connectAttr( "lidFactor.eyeBallRotX_scale", eyeOffMult+".input2X" )
        cmds.connectAttr( "lidFactor.eyeBallRotY_scale", eyeOffMult+".input2Y" )
        cmds.connectAttr( eyeOffMult + ".outputX", eyeOffSet+".rx" )
        cmds.connectAttr( eyeOffMult + ".outputY", eyeOffSet+".ry" )        
        
        #eyelid offset setup       
        '''offSetCtl = LR + "lidHeight"
        offsetMult = cmds.shadingNode( "multiplyDivide", asUtility=1, n =LR+"lidOffset_mult" )
        cmds.connectAttr( offSetCtl+".ty", offsetMult + ".input1X" )
        cmds.connectAttr( offSetCtl+".tx", offsetMult + ".input1Y" )
        cmds.setAttr( offsetMult+".input2X", rxVal/2 )
        cmds.setAttr( offsetMult+".input2Y", ryVal/2 )
        
        lidPGrp = [ LR +"upLidP_jnt", LR +"loLidP_jnt", LR +"cnrLidP_jnt" ]
        for p in lidPGrp:
            cmds.connectAttr( offsetMult + ".outputX", p+".rx" )
            cmds.connectAttr( offsetMult + ".outputY", p+".ry" )                            
        cmds.hide(eyeHi)'''   
    cmds.setAttr( aimCtlTop[0] + ".tz", lEyePos[0]*10 )
    cmds.connectAttr( "eyeblend_dir.tx", aimCtlP +".visibility" )
    
    

def eyeLidOffset_scale():
    
    geo = cmds.getAttr("helpPanel_grp.headGeo")
    numVtx = cmds.polyEvaluate( geo, v=1 )
    val=[]
    for i in range(numVtx):
        v = 0
        val.append(v)
        
    lEyePos = cmds.xform("lEyePos", q=1, ws=1, t=1)
    rEyePos = [ -lEyePos[0], lEyePos[1], lEyePos[2] ]
    
    rWideNull= "r_eyeWide_clsHandle"
    
    clsList =[ nd for nd in cmds.listHistory(geo) if cmds.nodeType(nd)=='cluster' ]
    
    '''if "l_eyeWide_cls" in clsList:
        
        #cmds.reorderDeformers( "eyeWide_cls", clsList[0], geo )            
        cls = cmds.cluster( geo, n= "r_eyeWide_cls", bs=1, wn = ( rWideNull, rWideNull ) )
        cmds.setAttr( cls[0]+".wl[0].w[0:%s]"%str(numVtx-1), s=numVtx, *val )
        #cmds.cluster( cls[0], e=1, bs=1, wn = ( rWideNull, rWideNull ) )
        cmds.copyDeformerWeights( sd = "eyeWide_cls", ss= geo, ds = geo, dd = cls[0], mirrorMode = "YZ", surfaceAssociation = "closestPoint" )
    else:
        cmds.warning( "create eyeWide_cls first!!" )'''  
        
    for LR in ["l_","r_"]:
        eyeWideMult = cmds.shadingNode( "multiplyDivide", asUtility=1, n =LR +"eyeWide_mult")
        cmds.connectAttr( LR + "lidHeight.tx", eyeWideMult + ".input1Y" )
        cmds.connectAttr( LR + "lidHeight.ty", eyeWideMult + ".input1X" )
        cmds.connectAttr( "lidFactor.eyeBallRotY_scale", eyeWideMult + ".input2Y" )
        cmds.connectAttr( "lidFactor.eyeBallRotX_scale", eyeWideMult + ".input2X" )
        if LR == "l_":
            clsHandle = "l_eyeWide_clsHandle"
            
        else:
            clsHandle = "r_eyeWide_clsHandle"
        
        eyeScl = LR + "eyeScl"    
        cmds.connectAttr(  eyeWideMult + ".outputY", clsHandle + ".ry", f=1 )
        cmds.connectAttr(  eyeWideMult + ".outputX", clsHandle + ".rx", f=1 )
        cmds.connectAttr( LR + "lidHeight.rz", clsHandle + ".rz", f=1 )
        cmds.connectAttr( LR + "lidHeight.sx", clsHandle + ".sx", f=1 )
        cmds.connectAttr( LR + "lidHeight.sy", clsHandle + ".sy", f=1 )
        cmds.connectAttr( LR + "lidHeight.sx", eyeScl + ".sx", f=1 )
        cmds.connectAttr( LR + "lidHeight.sy", eyeScl + ".sy", f=1 )        
        
            
def jointSkinEyeBall():#for compensating squach stretch
    
    cmds.select( cl=1 )
    eyePos = cmds.xform("lEyePos", q=1, ws=1, t=1 )
    
    for LR in ["l_","r_"]:
        
        crvCvs = cmds.ls(LR + "upCTLCrv01.cv[*]", fl=1)    
        midPoint = (len(crvCvs)+1)/2.0
        midPos = cmds.xform( crvCvs[int(midPoint)-1], q=1, ws=1, t=1 )    
        
        if LR == "r_":
            eyePos = [ -eyePos[0], eyePos[1], eyePos[2] ]

        dist = distance( eyePos, midPos )
        cmds.select( LR + "eyeTransform", r=1 )
        eyeDMat = cmds.shadingNode( "decomposeMatrix", asUtility=1, n = LR + "eyeDMatrix" )
        eyeBallJnt = cmds.joint(n = LR + "eyeBall_jnt", p= eyePos )
        pupilJnt = cmds.joint( n = LR + "pupil_jnt", p= [eyePos[0], eyePos[1], eyePos[2]+dist*0.9 ] )
        eyeBallScl= LR + "eyeScl"
        cmds.connectAttr( eyeBallScl + ".worldInverseMatrix ", eyeDMat + ".inputMatrix" )
        cmds.connectAttr( eyeDMat + ".outputScale", pupilJnt + ".s")
        
        #parent to eyeDecompose null
        eyeOffsetNull = LR+"eyeTransform"
        if cmds.objExists( eyeOffsetNull):
            cmds.parent(eyeBallJnt, eyeOffsetNull )
        cmds.setAttr( eyeBallJnt+".jointOrient", 0,0,0 ) 
        cmds.select(cl=1)



def distance(inputA=[1,1,1], inputB=[2,2,2]):
    #sqrt( ( inputB[0]-inputA[0])*(inputB[0]-inputA[0]) +.....  )
    return math.sqrt(pow(inputB[0]-inputA[0], 2) + pow(inputB[1]-inputA[1], 2) + pow(inputB[2]-inputA[2], 2))


# select all the objects in up/lo teeth geo group 
def teethSetup(UpLo):
    
    teethSel = cmds.ls( sl=1, type="transform" )
    cmds.parent(teethSel, 'faceGeo_grp' ) 
    
    if cmds.objExists("teethCtl_grp"):
        if "teethCtl_grp" not in cmds.listRelatives('bodyHeadTRS', c=1 ):
            cmds.parent("teethCtl_grp", 'bodyHeadTRS' )
    else:
        teethGrp = cmds.group( em=1, p='bodyHeadTRS', n="teethCtl_grp")

    pos = cmds.xform("jawRigPos", q=1, ws=1, t=1 )
    cmds.xform( "teethCtl_grp", ws =1, t = (0,pos[1],pos[2]) )  
     
    upTranPlus = cmds.shadingNode( "plusMinusAverage", asUtility=1, n = "upTeeth_tranSum")
    loTranPlus = cmds.shadingNode( "plusMinusAverage", asUtility=1, n = "loTeeth_tranSum")
    loRotPlus = cmds.shadingNode( "plusMinusAverage", asUtility=1, n = "loTeeth_rotSum")
    loTeethNull = cmds.group( em=1, p = "jawSemiAdd", n = "constLoTeeth")
    cmds.parentConstraint("jawClose_jnt", loTeethNull, maintainOffset = 1 )
    cmds.connectAttr( loTeethNull+".tx" , loTranPlus+".input3D[0].input3Dx" )
    cmds.connectAttr( loTeethNull+".ty" , loTranPlus+".input3D[0].input3Dy" )
    cmds.connectAttr( loTeethNull+".tz" , loTranPlus+".input3D[0].input3Dz" )
    cmds.connectAttr( loTeethNull+".rx" , loRotPlus+".input3D[0].input3Dx" )
    cmds.connectAttr( loTeethNull+".ry" , loRotPlus+".input3D[0].input3Dy" )
    cmds.connectAttr( loTeethNull+".rz" , loRotPlus+".input3D[0].input3Dz" )
    
    if not cmds.objExists( "teeth%sTRSP"%UpLo.title()):
        upLoGrp =cmds.group( em =1, p="teethCtl_grp", n="teeth%sTRSP"%UpLo.title())
        teethJnt=cmds.joint(  p=(0,0,0), r=True, n=UpLo+"Teeth_jnt" )
    else:
        upLoGrp = "teeth%sTRSP"%UpLo.title()
        teethJnt = UpLo+"Teeth_jnt"
        
    for teeth in teethSel:
        cmds.skinCluster( teethJnt, teeth, bm=0, nw=1, weightDistribution=0, mi=1, omi=True,  tsb=True )
    
    teethCtl = [ UpLo + "teeth_motion", UpLo + "teeth_motion_ctl" ]
    if cmds.objExists( teethCtl[0] ):
        teethTranMult = cmds.shadingNode("multiplyDivide", asUtility =1, n = UpLo + "teethTran_mult")
        addD = cmds.shadingNode("addDoubleLinear", asUtility=1, n = UpLo+ "teethTZ_addD")
        cmds.connectAttr( teethCtl+".tx", teethTranMult + ".input1X")
        cmds.setAttr(teethTranMult + ".input2X", 2)
        cmds.connectAttr( teethCtl+".ty", teethTranMult + ".input1Y")
        cmds.setAttr(teethTranMult + ".input2Y", 2)
        cmds.connectAttr( teethCtl+".sx", teethTranMult + ".input1Z")
        cmds.setAttr(teethTranMult + ".input2Z", 1 )
        #connect ctl to teeth TRSP
        if UpLo == "up":
            cmds.connectAttr( teethTranMult + ".outputX", upTranPlus+".input3D[0].input3Dz" )
            cmds.connectAttr( teethTranMult + ".outputY", upTranPlus+".input3D[0].input3Dy" )
            cmds.connectAttr(upTranPlus+".output3Dy", upLoGrp+".ty" )           
            cmds.connectAttr( teethTranMult + ".outputZ", upLoGrp+".sx" )
            cmds.connectAttr( teethCtl + ".sy", upLoGrp+".sy" )

            cmds.connectAttr(upTranPlus+".output3Dz", upLoGrp+".tz" )
            cmds.connectAttr( teethCtl + ".rz", upLoGrp+".rz"  )
            
        elif UpLo == "lo":
            cmds.connectAttr( loTranPlus+".output3Dx", upLoGrp+".tx" )
            cmds.connectAttr( teethTranMult + ".outputX", loTranPlus+".input3D[1].input3Dz" )
            cmds.connectAttr( teethTranMult + ".outputY", loTranPlus+".input3D[1].input3Dy" )
            #"loteeth_motion.scaleX" --> loTeeth scale
            cmds.connectAttr( teethTranMult + ".outputZ", upLoGrp+".sx" )
            cmds.connectAttr( teethCtl + ".sy", upLoGrp+".sy" )
            
            cmds.connectAttr( loTranPlus+".output3Dy", upLoGrp+".ty" )
            #"loteeth_motion.tranX" --> loTeeth tz
            cmds.connectAttr( loTranPlus+".output3Dz", upLoGrp+".tz" )
            #rotateZ
            cmds.connectAttr( teethCtl + ".rz", loRotPlus+".input3D[1].input3Dz" )
            cmds.connectAttr( loRotPlus+".output3D", upLoGrp+".r" )
    
    else:
           
        # connect with arFace panel
        if cmds.objExists( teethCtl[1] ):
            
            teethTranMult = cmds.shadingNode("multiplyDivide", asUtility =1, n = UpLo + "teethTran_mult")

            cmds.connectAttr( teethCtl+".tx", teethTranMult + ".input1X")
            cmds.setAttr(teethTranMult + ".input2X", 1 )
            cmds.connectAttr( teethCtl+".ty", teethTranMult + ".input1Y")
            cmds.setAttr(teethTranMult + ".input2Y", 1 )
            cmds.connectAttr( teethCtl+".tz", teethTranMult + ".input1Z")
            cmds.setAttr(teethTranMult + ".input2Z", 1 )
            #connect ctl to teeth TRSP
            if UpLo == "up":
                cmds.connectAttr( teethTranMult + ".outputX", upTranPlus+".input3D[0].input3Dx" )
                cmds.connectAttr( teethTranMult + ".outputY", upTranPlus+".input3D[0].input3Dy" )
                cmds.connectAttr(upTranPlus+".output3Dx", upLoGrp+".tx" )
                cmds.connectAttr(upTranPlus+".output3Dy", upLoGrp+".ty" )           
                cmds.connectAttr( teethTranMult + ".outputZ", upLoGrp+".tz" )
                cmds.connectAttr( teethCtl + ".rz", upLoGrp+".rz" )
                cmds.connectAttr( teethCtl + ".sx", upLoGrp+".sx" )  
                cmds.connectAttr( teethCtl + ".sy", upLoGrp+".sy" )        
                    
            elif UpLo == "lo":
                #loTeethNull( following ) connected loTranPlus[0]        
                cmds.connectAttr( teethTranMult + ".outputX", loTranPlus+".input3D[1].input3Dx" )
                cmds.connectAttr( teethTranMult + ".outputY", loTranPlus+".input3D[1].input3Dy" )
                cmds.connectAttr( teethTranMult + ".outputZ", loTranPlus+".input3D[1].input3Dz" )
                #"loteeth_motion.scaleX" --> loTeeth scale
                cmds.connectAttr( teethCtl + ".sx", upLoGrp+".sx" )
                cmds.connectAttr( teethCtl + ".sy", upLoGrp+".sy" )
                
                cmds.connectAttr( loTranPlus+".output3Dx", upLoGrp+".tx" )
                cmds.connectAttr( loTranPlus+".output3Dy", upLoGrp+".ty" )
                cmds.connectAttr( loTranPlus+".output3Dz", upLoGrp+".tz" )
                #rotateZ
                cmds.connectAttr( teethCtl + ".rz", loRotPlus+".input3D[1].input3Dz" )
                cmds.connectAttr( loRotPlus+".output3D", upLoGrp+".r" )
        
        else:
            cmds.confirmDialog( title='Confirm', message=' teeth ctls are missing' )     



#squach setup on tongue later        
def tongueSetupOld():
    
    tongueCtl = "tongue_ctl"
    pos = cmds.xform("jawRigPos", q=1, ws=1, t=1 )
    
    #create ctlP node with pivot on jawRigPos
    tngCtlP = cmds.group( em=1, p = 'attachCtl_grp', n = "tongueCtlP" )
    cmds.xform( tngCtlP, ws=1, t= pos )

    tngCtlGrp= cmds.duplicate( tongueCtl, po=1, n="tongueCtlGrp" )
    cmds.parent( tongueCtl, tngCtlGrp[0])
    cmds.parent( tngCtlGrp[0], tngCtlP )
    
    tongueCnst = cmds.group( em=1, p = "jawSemiAdd", n = "tongueConst" )    
    cmds.parentConstraint("jawClose_jnt", tongueCnst, maintainOffset = 1 )

    #tongueCnst + tongueWhole_move
    tngTranPlus = cmds.shadingNode( "plusMinusAverage", asUtility=1, n = "loTeeth_tranSum")
    tngRotPlus = cmds.shadingNode( "plusMinusAverage", asUtility=1, n = "loTeeth_rotSum")
    
    cmds.connectAttr( tongueCnst+".tx" , tngTranPlus+".input3D[0].input3Dx" )
    cmds.connectAttr( tongueCnst+".ty" , tngTranPlus+".input3D[0].input3Dy" )
    cmds.connectAttr( tongueCnst+".tz" , tngTranPlus+".input3D[0].input3Dz" )
    cmds.connectAttr( tongueCnst+".rx" , tngRotPlus+".input3D[0].input3Dx" )
    cmds.connectAttr( tongueCnst+".ry" , tngRotPlus+".input3D[0].input3Dy" )
    cmds.connectAttr( tongueCnst+".rz" , tngRotPlus+".input3D[0].input3Dz" )
    
    cmds.connectAttr( "tongueWhole_move.tx" , tngTranPlus+".input3D[1].input3Dz" )
    cmds.connectAttr( "tongueWhole_move.ty" , tngTranPlus+".input3D[1].input3Dy" )    
    #set offset values
    tran = cmds.getAttr( tngCtlP+".t")[0]
    rot = cmds.getAttr( tngCtlP+".r")[0]
    cmds.setAttr( tngTranPlus+".input3D[2].input3Dy", tran[1])
    cmds.setAttr( tngTranPlus+".input3D[2].input3Dz", tran[2])
    cmds.setAttr( tngRotPlus+".input3D[1].input3Dx", rot[0] )
    
    cmds.connectAttr( tngTranPlus+".output3D", tngCtlP+".t" )
    cmds.connectAttr( tngRotPlus+".output3D", tngCtlP+".r" )
    
    if cmds.objExists("tongueRig"):
        tongueGeo = cmds.listRelatives("tongueRig", ad=1, ni=1, type="mesh" )
        cmds.parent( cmds.listRelatives(tongueGeo[0], p=1 )[0], 'faceGeo_grp' )
        
        if "tongueRig" not in cmds.listRelatives('jaw', c=1 ):
            cmds.parent("tongueRig", 'jaw')



#1. create joint chain for tongue
#2. run script
#3. skin using delta mush 
def tongueSetup():
    
    mySel = cmds.ls(sl=1, typ = "joint")[0]
    baseJnt =  cmds.rename( mySel , "tongueBase_jnt" )
    baseJPos = cmds.xform( baseJnt, q=1, ws=1, t=1  )
    jnts = cmds.listRelatives(baseJnt, ad=1, typ = "joint" )
    
    tongueJPos = cmds.xform( jnts[-1], q=1, ws=1, t=1  ) 
    radius = distance( baseJPos, tongueJPos )
    baseCtl= genericController( "tongueBase_ctl", baseJPos, radius, "circle", 11 )
    baseGrp = cmds.group( em =1, n = "tongueBase_grp", p = baseCtl[0] )
    cmds.parent( baseJnt,  baseGrp )
    
    for i, j in enumerate(jnts[1:][::-1]):
        
        jntName = cmds.rename( j , "tongue_jnt"+str(i+1).zfill(2))
        jPos = cmds.xform( jntName, q=1, ws=1, t=1  )
        #create ctl on the jnt
        jCtl = genericController( jntName.replace("jnt", "ctl"), jPos, radius, "circle", 11 )    
        #create grp under ctl
        jGrp = cmds.group( em =1, n = jntName.replace("jnt","grp"), p = jCtl[0] )
        cmds.parent( jCtl[1],  baseJnt )
        cmds.parent( jntName,  jGrp )
        baseJnt = jntName

        
    
#턱 조인트 셋업에 추가할 디테일 커브 셋업( jawOpen, jawUDRL ctl).   
#additional detail curves for "JawOpen_crv"( jawOpen ctl ), "TyLip_crv"( jaw_UDLR ctl )
def jawRigDetailCrv():

    inverseMult = cmds.shadingNode('multiplyDivide', asUtility =1, n = 'ctlInverse_mult')
    #cmds.setAttr(inverseMult+".input2", -1, -1, -1 )
    cmds.connectAttr(  "lowJaw_dir.ty",  inverseMult+".input1X" ) 
    cmds.connectAttr( "jaw_UDLR.ty", inverseMult+".input1Y" ) 
    
    #addAttr to control detail crv
    lipDetailMult = cmds.shadingNode('multiplyDivide', asUtility =1, n = 'lipDetail_mult')
    cmds.setAttr( lipDetailMult+".input2", -1, -1, -1 )
    
    ctlDict = {"lowJaw_dir":"X", "jaw_UDLR":"Y" }
    for ctl, XY in  ctlDict.iteritems():
        attrName = ctl.split("_")[1]+ '_detail'
        cmds.addAttr( ctl, shortName='detail', longName= attrName, defaultValue=0.0, minValue=0.0, maxValue=1.0, keyable= 1 )
        
        cmds.connectAttr( ctl + "." + attrName, lipDetailMult+ ".input1"+XY )
        cmds.connectAttr( lipDetailMult+ ".output"+XY, inverseMult+ ".input2"+XY )

    ctlClamp = cmds.shadingNode("clamp", asUtility =1, n = 'jawCtl_clamp' ) 
    cmds.connectAttr( inverseMult+".outputX", ctlClamp+".inputR" )
    cmds.setAttr( ctlClamp + ".maxR", 1)
     
    cmds.connectAttr( inverseMult+".outputY", ctlClamp+".inputG" )
    cmds.setAttr( ctlClamp + ".maxG", 1)
    for upLo in ["up","lo"]:
        #jawOpen plusAverage nodes
        jawOpenPlus = cmds.ls( upLo+"TY*_plus", fl=1, type="plusMinusAverage")
        openTXPlus = cmds.ls( upLo+ "TX*_plus", fl=1, type="plusMinusAverage")
        plusLen =len(jawOpenPlus)
        #jawOpen plusAverage nodes
        jawTYPlus = cmds.ls( upLo+"LipJotXPos*_plus", fl=1, type="plusMinusAverage")
        
        openCrv = cmds.curve ( d = 1, p =([-0.5,0,0],[-0.25,0,0],[0,0,0],[0.25,0,0],[0.5,0,0]) ) 
        cmds.rebuildCurve ( rt = 0, d = 1, kr = 0, s = plusLen-1 )
        jawOpenCrv= cmds.rename( openCrv, upLo + "JawDetail_crv" )
        
        TYCrv = cmds.curve ( d = 1, p =([-0.5,0,0],[-0.25,0,0],[0,0,0],[0.25,0,0],[0.5,0,0]) ) 
        cmds.rebuildCurve ( rt = 0, d = 1, kr = 0, s = plusLen-1 )
        jawTYCrv = cmds.rename( TYCrv, upLo + "TYDetail_crv" )
        
        cmds.parent( jawOpenCrv, "JawOpen_indiGrp")
        cmds.parent( jawTYCrv, "TyLip_indiGrp" )
        
        for i in range( plusLen ):
    
            connectDetailCrv( jawOpenCrv, jawOpenPlus[i], jawTYCrv, openTXPlus[i], jawTYPlus[i], ctlClamp, i )
            
            
def connectDetailCrv( jawOpenCrv, jawOpenPlus, jawTYCrv, openTXPlus, jawTYPlus, ctlClamp, index ):
    
    crvCV = jawOpenCrv+".cv[%s]"%str(index)
    jawTYCrvCV = jawTYCrv +".cv[%s]"%str(index)
    
    jawOpenDetailMult = cmds.shadingNode('multiplyDivide', asUtility =1, n = jawOpenCrv.split("_")[0]+'%s_mult'%str(index+1).zfill(2) )
    jawTYDetailMult = cmds.shadingNode('multiplyDivide', asUtility =1, n = jawTYCrv.split("_")[0]+'%s_mult'%str(index+1).zfill(2) )
    
    cvPlusMinus = cmds.shadingNode("plusMinusAverage", asUtility =1, n = 'detail%sTx_minus'%str(index+1).zfill(2) )
 
    #CVs positionX 
    txVal = cmds.getAttr( crvCV + ".xValue" )
    cmds.setAttr( cvPlusMinus+".input3D[1].input3Dx", -1*txVal )
    cmds.connectAttr( crvCV + ".xValue", cvPlusMinus+".input3D[0].input3Dx" )
 
    txV = cmds.getAttr( jawTYCrvCV + ".xValue")
    cmds.setAttr( cvPlusMinus+".input3D[1].input3Dy", -1*txV )    
    cmds.connectAttr( jawTYCrvCV + ".xValue", cvPlusMinus +".input3D[0].input3Dy" )
    '''
    txValue = cmds.getAttr( happyCrvCV + ".xValue")
    cmds.setAttr( cvPlusMinus+"input3D[1].input3Dz", -1*txValue )     
    cmds.connectAttr( happyCrvCV + ".xValue", cvPlusMinus+".input3D[2].input3Dz" )'''
    
    #jawOpenCrv CVs x/yValue connect
    cmds.connectAttr( cvPlusMinus+".output3Dx", jawOpenDetailMult+".input1X" )
    cmds.connectAttr( crvCV + ".yValue", jawOpenDetailMult+".input1Y" )   
 
    cmds.connectAttr( ctlClamp+".outputR", jawOpenDetailMult+".input2X" )
    cmds.connectAttr( ctlClamp+".outputR", jawOpenDetailMult+".input2Y" )
    
    #jawTyCrv    
    cmds.connectAttr( cvPlusMinus+".output3Dy", jawTYDetailMult+".input1X" )
    cmds.connectAttr( jawTYCrvCV + ".yValue", jawTYDetailMult+".input1Y" )   
    cmds.connectAttr( jawTYCrvCV + ".zValue", jawTYDetailMult+".input1Z" )
    
    cmds.connectAttr( ctlClamp+".outputG", jawTYDetailMult+".input2X" )
    cmds.connectAttr( ctlClamp+".outputG", jawTYDetailMult+".input2Y" )   
    cmds.connectAttr( ctlClamp+".outputG", jawTYDetailMult+".input2Z" )
    '''
    for lr in ["l_","r_"]:
        happyDetailMult = cmds.shadingNode('multiplyDivide', asUtility =1, n = happyCrv.split("_")[0]+'%s_mult'%str(index).zfill(2))
    #happyCrv    
    cmds.connectAttr( cvPlusMinus+".output3Dz", happyDetailMult+".input1X" )
    cmds.connectAttr( crvCV + ".yValue", happyDetailMult+".input1Y" )   
    cmds.connectAttr( crvCV + ".zValue", happyDetailMult+".input1Z" )    
 
    cmds.connectAttr( LR+ "posRemap.outValue", jawTYDetailMult+".input2X" ) 
    cmds.connectAttr( LR + "posRemap.outValue", jawTYDetailMult+".input2Y" )   
    cmds.connectAttr( LR + "posRemap.outValue", jawTYDetailMult+".input2Z" )'''
    
    #connect mult to plus
    cmds.connectAttr( jawOpenDetailMult+".outputY", jawOpenPlus +".input1D[3]" )
    cmds.connectAttr( jawOpenDetailMult+".outputX", openTXPlus+ ".input3D[2].input3Dx" ) 
    cmds.connectAttr( jawTYDetailMult+".outputX", jawTYPlus +".input3D[2]input3Dx " ) 
    cmds.connectAttr( jawTYDetailMult+".outputY", jawTYPlus +".input3D[2]input3Dy " )
    cmds.connectAttr( jawTYDetailMult+".outputZ", jawTYPlus +".input3D[3]input3Dz ") 
    
    
    
    
def detailOnOff(): 
    upLidDetail = cmds.ls("*_upDetail*P", type = "transform" ) 
    loLidDetail = cmds.ls("*_loDetail*P", type = "transform" ) 
    inDetail = cmds.ls("*_innerDetailP", type = "transform" ) 
    outDetail = cmds.ls("*_outerDetailP", type = "transform" )
    mouthDetail = cmds.ls( "*LipDetailP*", type = "transform" )
    upFaceDetail = cmds.ls("*_upLid*P", type = "transform" )
    loFaceDetail = cmds.ls("*_loLid*P", type = "transform" )
    
    cnrDetail = cmds.listRelatives("cornerLid_grp", ad=1, type = "nurbsCurve" )
    cnrFaceDetail = [ cmds.listRelatives(z, p=1)[0] for z in cnrDetail ]
    details=upLidDetail+loLidDetail+inDetail+outDetail+mouthDetail+upFaceDetail+loFaceDetail+cnrFaceDetail
    
    for d in details:
        cmds.connectAttr("detail_ctl.tx", d+".visibility", f=1 )
        
        

#control lipCorner in/out and Open        
def cornerLipLevel():

    #jaw corner Open In
    cornerMult = [["JawOpendamp_mult", "JawOpenCorner_mult"], ["TyLipdamp_mult", "TyLipCorner_mult"]]
    ctl ="cornerLip_levelCtl"
    for mlt in cornerMult:
        
        cornerYSum = cmds.shadingNode ( 'plusMinusAverage', asUtility= 1, n = 'lipCorner_sum' )        
        invertXMult = cmds.shadingNode ('multiplyDivide', asUtility = 1, n = 'invertX_mult')
        cmds.connectAttr( ctl+".ty", invertXMult + ".input1X" )
        cmds.setAttr( invertXMult + ".input2X", -1 )
        cmds.connectAttr( invertXMult + ".outputX", cornerYSum+".input3D[0].input3Dx" )
        cmds.setAttr( cornerYSum+".input3D[1].input3Dx", 0.5 )
        cmds.connectAttr( cornerYSum+".output3Dx", mlt[0] +".input2Y")
        if "JawOpendamp_mult" in mlt:
            xVal = 0.3
        else:
            xVal = 0.1
        
        LRList = [["l_", "y", -1 ],["r_", "z", 1 ]]
        for LR in LRList:
            cmds.connectAttr( ctl+".tx", invertXMult + ".input1"+LR[1].title() )
            cmds.setAttr( invertXMult + ".input2"+LR[1].title(), LR[2] )
            cmds.connectAttr( invertXMult + ".output"+LR[1].title(), cornerYSum+".input3D[0].input3D"+LR[1] )
                 
            cmds.setAttr( cornerYSum+".input3D[1].input3D"+LR[1], -LR[2]*xVal )
            cmds.connectAttr( cornerYSum+".output3D"+LR[1], mlt[1]+".input2"+LR[1].title() )



def lipCornerTZSetup():
    LR = { "l":[4,3] , "r":[0,1] }
    for p, q in LR.items():
        lipTzMult = cmds.shadingNode ('multiplyDivide', asUtility = 1, n = p +'CornerTZ_mult')
        cmds.setAttr( lipTzMult+ ".operation", 2 )  
        cmds.connectAttr( p + "CornerTZ.tx", lipTzMult+".input1Y", f=1)
        cmds.setAttr( lipTzMult+".input2Y", 3)
        UD ={ "up":"X", "lo":"Z" }
        for ud, xy in UD.items():
            
            lipTzAddD = cmds.shadingNode ( 'addDoubleLinear', asUtility = 1, n = p+ud.title()+'CornerTZ_add' )
            cmds.connectAttr( lipTzMult+".outputY", ud+"RollYZ_crv.cv[%s].zValue"%q[0], f=1)
            cmds.connectAttr( p + "CornerTZ.tx", lipTzAddD + ".input1" ) 
            cmds.connectAttr( p+ "_lip%sRoll_ctl.tx"%ud.title(), lipTzAddD + ".input2" )            
            cmds.connectAttr( lipTzAddD + ".output", lipTzMult+ ".input1"+ xy )
            cmds.setAttr( lipTzMult+ ".input2"+ xy, 4 )
            
            cmds.connectAttr( lipTzMult+ ".output"+ xy, ud+"RollYZ_crv.cv[%s].zValue"%q[1], f=1 )
            
            
            
      
        
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
        
        
        

#lip gets thinner with "happy" "E" "wide" lipShape crv based on the lipFactor lipY/ZVolumn
def lipThinningSetup():

    jntSel = cmds.ls('*LipRollJot*_jnt', fl=1, type = 'joint')
    cmds.addAttr( "lipFactor", shortName="happyY", longName="happy_yVolumn", defaultValue=1.0, minValue=0.0, maxValue=2.0, keyable= 1 )
    cmds.addAttr( "lipFactor", shortName="happyZ", longName="happy_zVolumn", defaultValue=1.0, minValue=0.0, maxValue=2.0, keyable= 1 )
    cmds.addAttr( "lipFactor", shortName="lipWideY", longName="lipWide_yVolumn", defaultValue=1.0, minValue=0.0, maxValue=2.0, keyable= 1 )
    cmds.addAttr( "lipFactor", shortName="lipWideZ", longName="lipWide_zVolumn", defaultValue=1.0, minValue=0.0, maxValue=2.0, keyable= 1 )
    cmds.addAttr( "lipFactor", shortName="EY", longName="E_yVolumn", defaultValue=1.0, minValue=0.0, maxValue=2.0, keyable= 1 )
    cmds.addAttr( "lipFactor", shortName="EZ", longName="E_zVolumn", defaultValue=1.0, minValue=0.0, maxValue=2.0, keyable= 1 )
    volumYMult = cmds.shadingNode("multiplyDivide", asUtility =1, n = "lipYVolum_mult" )
    volumZMult = cmds.shadingNode("multiplyDivide", asUtility =1, n = "lipZVolum_mult" )
    cmds.connectAttr( "lipFactor.happyY",  volumYMult+".input1X")
    cmds.connectAttr( "lipFactor.lipWideY",  volumYMult+".input1Y")
    cmds.connectAttr( "lipFactor.EY",  volumYMult+".input1Z")
    cmds.setAttr( volumYMult+".input2X", -0.2/4 )
    cmds.setAttr( volumYMult+".input2Y", -0.2/4 )
    cmds.setAttr( volumYMult+".input2Z", -0.2/4 )
    
    cmds.connectAttr( "lipFactor.happyZ",  volumZMult+".input1X")
    cmds.connectAttr( "lipFactor.lipWideZ",  volumZMult+".input1Y")
    cmds.connectAttr( "lipFactor.EZ",  volumZMult+".input1Z")
    cmds.setAttr( volumZMult+".input2X", -0.1 )
    cmds.setAttr( volumZMult+".input2Y", -0.1 )
    cmds.setAttr( volumZMult+".input2Z", -0.1 )
    
    for i, jot in enumerate(jntSel):
    
        narrowSum = cmds.shadingNode("plusMinusAverage", asUtility =1, n = "lipThinSum"+str(i).zfill(2) )
        YMult = cmds.shadingNode("multiplyDivide", asUtility =1, n = "lipYThinMult"+str(i).zfill(2) )
        ZMult = cmds.shadingNode("multiplyDivide", asUtility =1, n = "lipZThinMult"+str(i).zfill(2) )
        scaleYMinus = cmds.shadingNode('plusMinusAverage', asUtility=True, n = 'scaleY' + str(i) + '_minus' )
        scaleZMinus = cmds.shadingNode('plusMinusAverage', asUtility=True, n = 'scaleZ' + str(i) + '_minus' )
        
        #scaleY thinning setup
        #1. happy lip thinning ( joint.scaleY = 1 - Ymult )
        cmds.connectAttr( "upLipCrvBS.l_upHappy_crv", narrowSum+".input3D[0].input3Dx" )
        cmds.connectAttr( "upLipCrvBS.r_upHappy_crv", narrowSum+".input3D[1].input3Dx" )
        
        cmds.connectAttr( narrowSum+".output3Dx" , YMult+".input1X" )
        cmds.connectAttr ( volumYMult+".outputX", YMult+".input2X" )
        cmds.connectAttr( narrowSum+".output3Dx" , ZMult+".input1X" )
        cmds.connectAttr ( volumZMult+".outputX", ZMult+".input2X" )
        #2.lipWide lip thinning  
        cmds.connectAttr( "upLipCrvBS.l_uplipWide_crv", narrowSum+".input3D[0].input3Dy" )
        cmds.connectAttr( "upLipCrvBS.r_uplipWide_crv", narrowSum+".input3D[1].input3Dy" )
        cmds.connectAttr( narrowSum+".output3Dy" , YMult+".input1Y" )
        cmds.connectAttr ( volumYMult+".outputY", YMult+".input2Y" )
        cmds.connectAttr( narrowSum+".output3Dy" , ZMult+".input1Y" )
        cmds.connectAttr ( volumZMult+".outputY", ZMult+".input2Y" )
        #3.lipE lip thinning      
        cmds.connectAttr( "upLipCrvBS.l_uplipE_crv", narrowSum+".input3D[0].input3Dz" )
        cmds.connectAttr( "upLipCrvBS.r_uplipE_crv", narrowSum+".input3D[1].input3Dz" )
        cmds.connectAttr( narrowSum+".output3Dz" , YMult+".input1Z" )
        cmds.connectAttr ( volumYMult+".outputZ", YMult+".input2Z" )
        cmds.connectAttr( narrowSum+".output3Dz" , ZMult+".input1Z" )
        cmds.connectAttr ( volumZMult+".outputZ", ZMult+".input2Z" )    
    
        #thinning func: 1-volumn
        cmds.setAttr( scaleYMinus+".input1D[0]", 1 )
        cmds.connectAttr( YMult+".outputX", scaleYMinus+".input1D[1]" )
        cmds.connectAttr( YMult+".outputY", scaleYMinus+".input1D[2]" )
        cmds.connectAttr( YMult+".outputZ", scaleYMinus+".input1D[3]" )
        cmds.connectAttr( scaleYMinus+".output1D", jot+".sy" )
           
        cmds.setAttr( scaleZMinus+".input1D[0]", 1 )
        cmds.connectAttr( ZMult+".outputX", scaleZMinus+".input1D[1]" )
        cmds.connectAttr( ZMult+".outputY", scaleZMinus+".input1D[2]" )
        cmds.connectAttr( ZMult+".outputZ", scaleZMinus+".input1D[3]" )
        cmds.connectAttr( scaleZMinus+".output1D", jot+".sz" )
        
        
        
def dial_lipFactor():
    #lowJaw_dir corner ctrl
    cmds.addAttr( "lowJaw_dir", ln ="cornerInOut", attributeType='float'  )
    cmds.addAttr( "lowJaw_dir", ln ="cornerUpDwn", attributeType='float'  )
    cmds.setAttr( "lowJaw_dir.cornerInOut", .1 )
    cmds.setAttr( "lowJaw_dir.cornerUpDwn", .55 )
    cmds.connectAttr( "lowJaw_dir.cornerInOut", "lipCorner_sum.input3D[1].input3Dy" )
    cmds.expression( s="lipCorner_sum.input3D[1].input3Dz= lowJaw_dir.cornerInOut*-1;" )
    cmds.connectAttr( "lowJaw_dir.cornerUpDwn", "lipCorner_sum.input3D[1].input3Dx" )
    
    #jawSemi Scale control
    
    cmds.addAttr( "lowJaw_dir", ln ="jawSemi_sx", attributeType='float'  )
    cmds.addAttr( "lowJaw_dir", ln ="jawSemi_sz", attributeType='float'  )
    cmds.setAttr( "lowJaw_dir.jawSemi_sx", .08)
    cmds.setAttr( "lowJaw_dir.jawSemi_sz", .03)
    
    #distconnect jawSemi.scale connection
    semiScaleCnnt = cmds.listConnections( "jawSemi", s=1, d=0, p=1, scn=1 )
    if semiScaleCnnt:
        cmds.disconnectAttr( "lipPScaleSum.output2Dx", "jawSemi.sx" )
        cmds.disconnectAttr( "lipPScaleSum.output2Dy", "jawSemi.sz" )
        
    cmds.expression( s="jawSemi.sx = 1+(jaw_UDLR.ty + swivel_ctrl.ty + lowJaw_dir.ty)*lowJaw_dir.jawSemi_sx;" )
    cmds.expression( s="jawSemi.sz = 1+(jaw_UDLR.ty + swivel_ctrl.ty + lowJaw_dir.ty)*lowJaw_dir.jawSemi_sz;" )
    
    #jaw_UDLR corner ctrl
    cmds.addAttr( "jaw_UDLR ", ln ="cornerInOut", attributeType='float'  )
    cmds.addAttr( "jaw_UDLR ", ln ="cornerUpDwn", attributeType='float'  )
    cmds.setAttr( "jaw_UDLR .cornerInOut", .05 )
    cmds.setAttr( "jaw_UDLR .cornerUpDwn", .50 )
    cmds.connectAttr( "jaw_UDLR .cornerInOut", "lipCorner_sum1.input3D[1].input3Dy" )
    cmds.expression( s="lipCorner_sum1.input3D[1].input3Dz= jaw_UDLR.cornerInOut*-1;" )
    cmds.connectAttr( "jaw_UDLR.cornerUpDwn", "lipCorner_sum1.input3D[1].input3Dx" )
    

    
#jawOpen,lipRoll,browUp,eyeBlink,eyeWide,upLipRoll_cls,bttmLipRoll_cls,l_ear_cls,nose_cls 
#unlock eyeScale_JNT 
def rnkFaceWeightCalculate():   
    
    headGeo = cmds.getAttr("helpPanel_grp.headGeo")
    size = cmds.polyEvaluate( headGeo, v = 1)
    skinCls = mel.eval("findRelatedSkinCluster %s"%headGeo )
    
    lipWgt = cmds.getAttr ("lip_cls.wl[0].w[0:"+str(size-1)+"]")
    cheekWgt = cmds.getAttr ( "l_cheek_cls.wl[0].w[0:%s]"%str(size-1))
    browUpWgt = cmds.getAttr ( "browUp_cls.wl[0].w[0:%s]"%str(size-1))
    eyeBlinkWgt =cmds.getAttr ( "eyeBlink_cls.wl[0].w[0:%s]"%str(size-1))
    eyeWideWgt =cmds.getAttr ( "eyeWide_cls.wl[0].w[0:%s]"%str(size-1))
    noseWgt =cmds.getAttr ( "nose_cls.wl[0].w[0:%s]"%str(size-1))   
    valStr = ''
    cheekStr = ''
    eyeSclStr = ''
    noseStr = ''

    headSkelID = getJointIndex( skinCls,'C_jnt_fineTune_Head_JNT' )
    cheekID = getJointIndex ( skinCls, 'L_jnt_fineTune_Cheek_JNT' )
    eyeSclID = getJointIndex ( skinCls, 'L_jnt_fineTune_Eyelid_scale_JNT' )
    noseID = getJointIndex ( skinCls, 'C_jnt_fineTune_Nose_JNT' )

    #set weight back to 1 on the headSkel_jnt
    cmds.skinPercent( skinCls, headGeo+'.vtx[0:%s]'%(size-1), nrm=1, tv = ['C_jnt_fineTune_Head_JNT', 1] )
    cmds.setAttr( skinCls +'.normalizeWeights', 0 )
    
    for x in range(size):
    	if eyeBlinkWgt[x] > eyeWideWgt[x]:
    		eyeBlinkWgt[x] = eyeWideWgt[x]    		 

        if browUpWgt[x]>1:
            browUpWgt[x] = 1
        
        if noseWgt[x]+lipWgt[x]>1:
            noseWgt[x] = 1 -lipWgt[x]
        
        if lipWgt[x]>1:
            lipWgt[x] = 1               
        tempVal = lipWgt[x]+ cheekWgt[x]
        if tempVal >1:
            cheekWgt[x] = 1 - lipWgt[x]        
              
        cheekStr +=str(cheekWgt[x]) + " "
        
        #eyeScale_jnt weight = 
        eyeSclVal = eyeWideWgt[x] - eyeBlinkWgt[x]
        eyeSclStr +=str(eyeSclVal) +" " 
        
        #nose_JNT weight = 
        noseStr +=str(noseWgt[x]) + " " 
        
        #headSkel_jnt weight =           
        tmpVal = 1 -lipWgt[x] -cheekWgt[x] -browUpWgt[x] - eyeWideWgt[x] -noseWgt[x]
        valStr +=str(tmpVal)+" "
     
    commandStr = ("setAttr -s "+str(size)+" " + skinCls+".wl[0:"+str(size-1)+"].w["+headSkelID+"] "+ valStr );
    mel.eval (commandStr)                 
  
    cheekCmmdStr = ("setAttr -s "+str(size)+" " + skinCls+".wl[0:"+str(size-1)+"].w["+cheekID+"] "+ cheekStr );
    mel.eval (cheekCmmdStr)

    eyeSclCmmdStr = ("setAttr -s "+str(size)+" " + skinCls+".wl[0:"+str(size-1)+"].w["+eyeSclID+"] "+ eyeSclStr );
    mel.eval (eyeSclCmmdStr)

    noseCmmdStr = ("setAttr -s "+str(size)+" " + skinCls+".wl[0:"+str(size-1)+"].w["+noseID+"] "+ noseStr );
    mel.eval (noseCmmdStr)
    
    #get the xml file for skinWeight ( brow/ eyeLid / lip )
    dataPath = cmds.fileDialog2(fileMode=3, caption="set directory")
    eyeJnts = [ x for x in cmds.ls('*_jnt_fineTune_Eyelid_*', type = "joint") if not "scale" in x]
    if os.path.exists(dataPath[0] + '/headSkin.xml'):

        headSkinWeight = ET.parse( dataPath[0] + '/headSkin.xml')
        rootHeadSkin = headSkinWeight.getroot()
         
        for i in range(2, len(rootHeadSkin)-2 ):
            jntName = rootHeadSkin[i].attrib['source']
            if '_jnt_fineTune_Lips' in jntName:
                lipJnt = jntName
                lipJntID = getJointIndex( skinCls, lipJnt) 
             
                for dict in rootHeadSkin[i]:

                    vertNum = int(dict.attrib['index'] )
                    wgtVal= float(dict.attrib['value'] )
                    #if vertNum in rollVertNum:
                    cmds.setAttr ( skinCls + '.wl['+ str(vertNum) + "].w[" + str(lipJntID)+ "]", min(1, lipWgt[vertNum])* wgtVal )
                                     
            if jntName in eyeJnts:
                eyeJnt = jntName
                print eyeJnt
                eyeJntID = getJointIndex( skinCls, eyeJnt) 
                
                for dict in rootHeadSkin[i]:
                    vertID = int(dict.attrib['index'])
                    weight= float(dict.attrib['value'])
                    #if vertID in blinkVertNum:
                         
                    cmds.setAttr ( skinCls + '.wl['+ str(vertID) + "].w[" + str(eyeJntID)+ "]", ( min(1, eyeBlinkWgt[vertID]) * weight) )
             

            if "_jnt_fineTune_Eyebrows" in jntName:

                browJnt = jntName
                print browJnt
                browJntID = getJointIndex( skinCls,browJnt )
                    
                for dict in rootHeadSkin[i]:
                    vertIndex = int(dict.attrib['index'])
                    wgtValue= float(dict.attrib['value'])
                    #if vertIndex in browTZNum:
                    cmds.setAttr (  skinCls + '.wl['+ str(vertIndex) + "].w[" + str(browJntID)+ "]", ( min(1, browUpWgt[vertIndex]) * wgtValue) )            
        
    #cmds.skinPercent('headSkin', headGeo, nrm=False, prw=100)
    cmds.setAttr( skinCls + '.normalizeWeights', 1 )#normalization mode. 0 - none, 1 - interactive, 2 - post         
    cmds.skinPercent( skinCls , headGeo, nrm= 1 )



def browSkinWgtCalculate():
    headGeo =cmds.getAttr("helpPanel_grp.headGeo")
    size = cmds.polyEvaluate( headGeo, v = 1)
    browUpWgt = cmds.getAttr ( "browUp_cls.wl[0].w[0:%s]"%str(size-1))
    browDwnWgt = cmds.getAttr ( "browDn_cls.wl[0].w[0:%s]"%str(size-1))
    browTZWgt = cmds.getAttr ( "browTZ_cls.wl[0].w[0:%s]"%str(size-1))
    headSkelID = getJointIndex( 'headSkin', 'headSkel_jnt' )
    cmds.skinPercent( 'headSkin', headGeo+'.vtx[0:%s]'%(size-1), nrm=1, tv = ['headSkel_jnt',1] )
    #browUDWgt >= browTZWgt 
    #x = vertex number 
    for x in range(size):
        if browUpWgt[x]>1:
            print browUpWgt[x]
            browUpWgt[x] = 1
            
        vtxVal= browUpWgt[x]-browTZWgt[x]
        if vtxVal<0:
            print vtxVal
            browTZWgt[x] = browUpWgt[x]
      
        if browDnWgt[x]>1:
            browDnWgt[x] = 1
        
    #get the xml file for skinWeight ( brow/ eyeLid / lip )
    dataPath = cmds.fileDialog2(fileMode=3, caption="set directory")
            
    if os.path.exists(dataPath[0] + '/browMapSkin.xml'):  
        browSkinWeight = ET.parse( dataPath[0] + '/browMapSkin.xml')
        rootBrowSkin = browSkinWeight.getroot()
             
        browPJnts = cmds.ls ("*_browP*_jnt", type ="joint")
        childJnts = cmds.listRelatives(browPJnts, c =1, type = "joint")     
        for f in range(2, len(rootBrowSkin)-2 ):
            browJnt = rootBrowSkin[f].attrib['source']
            if browJnt in childJnts:
                browPJnt = cmds.listRelatives( browJnt, p=True, f=True )
                path= browPJnt[0].split("|")
                baseJnt = [ z for z in path if "Base" in z ][0]
                baseJntID = getJointIndex('headSkin',baseJnt ) 
                childJntID = getJointIndex('headSkin',browJnt )
                browWide = baseJnt.replace("Base","Wide")
                if cmds.objExists(browWide):
                    wideJntID = getJointIndex('headSkin',browWide )
                    
                for dict in rootBrowSkin[f]:
                    vertIndex = int(dict.attrib['index'])
                    wgtValue= float(dict.attrib['value'])
                    #if vertIndex in browTZNum:
                     
                    cmds.setAttr ( 'headSkin.wl['+ str(vertIndex) + "].w[" + str(childJntID)+ "]", ( min(1, browTZWgt[vertIndex]) * wgtValue) )                
             
                    #elif vertIndex in restVert:
                    restVal = ( browUpWgt[vertIndex] - browTZWgt[vertIndex])* wgtValue
                    cmds.setAttr ( 'headSkin.wl['+ str(vertIndex) + "].w[" + str(baseJntID) + "]", restVal )                  
                    
                    if cmds.objExists(browWide):
                        wideVal = (browDwnWgt[vertIndex] - browUpWgt[vertIndex])*wgtValue
                        cmds.setAttr ( 'headSkin.wl['+ str(vertIndex) + "].w[" + str(wideJntID) + "]", wideVal )          
        
        #cmds.skinPercent('headSkin', headGeo, nrm=False, prw=100)
        cmds.setAttr( 'headSkin.normalizeWeights', 1 )#normalization mode. 0 - none, 1 - interactive, 2 - post         
        cmds.skinPercent('headSkin', headGeo, nrm= 1 )    
    
    
    
#path를 찾는 좀 더 정확한 방법?? workspace
# jawClose/mouth cluster weight update할때: calExtraClsWgt()
# headSkel weight 1 / clsVertsDict update (2/1/2017)
def lipWeightCalculate():  
    
    dataPath = cmds.fileDialog2(fileMode=3, caption="set directory")
    
    headSkinWeight = ET.parse( dataPath[0] + '/headSkin.xml')
    rootHeadSkin = headSkinWeight.getroot()
    len(rootHeadSkin)
    
    size = cmds.polyEvaluate( 'head_REN', v = 1)
    mouthWgt = []
    lipWgt = cmds.getAttr ("lip_cls.wl[0].w[0:"+str(size-1)+"]")
    rollWgt = cmds.getAttr ("lipRoll_cls.wl[0].w[0:"+str(size-1)+"]")
    jawOpenWgt = cmds.getAttr ("jawOpen_cls.wl[0].w[0:"+str(size-1)+"]")
    jawCloseWgt = cmds.getAttr ("jawClose_cls.wl[0].w[0:%s]"%str(size-1))
    mouthWgt = cmds.getAttr ("mouth_cls.wl[0].w[0:%s]"%str(size-1))
    #lipRollJnts = cmds.listRelatives(cmds.ls('upLipRollJotP*', type ='transform'), c =1 )
    #rollJntID = getJointIndex( 'upLipRollJot13_jnt' )
    cmds.skinPercent('headSkin', 'head_REN', nrm= 0)
    #cmds.setAttr( 'headSkin.normalizeWeights', 1 )
    valStr = ''
    jcValStr = ''
    headSkelID = getJointIndex( 'headSkin','headSkel_jnt' )
    jawCloseID = getJointIndex( 'headSkin','jawClose_jnt' )
    for x in range(size):
    
        tmpVal =1 - jawCloseWgt[x]
        valStr += str(tmpVal)+" "
        
        tempVal = jawCloseWgt[x]-mouthWgt[x]
        jcValStr += str(tempVal)+" "
        
    commandStr = ("setAttr -s "+str(size)+" headSkin.wl[0:"+str(size-1)+"].w["+headSkelID+"] "+ valStr);
    mel.eval (commandStr)
                  
    cmmdStr = ("setAttr -s "+str(size)+" headSkin.wl[0:"+str(size-1)+"].w["+jawCloseID+"] "+ jcValStr);
    mel.eval (cmmdStr)
       
    rollVertDict = clsVertsDict( 'head_REN', 'lipRoll_cls')
    rollVertNum = [ y for y in rollVertDict ]
    lipVertNum = []
    for z in range(size):
        if lipWgt[z]-rollWgt[z]>0:
            lipVertNum.append( z )   
    
    for i in range(2, len(rootHeadSkin)-2 ): 
        jntName = rootHeadSkin[i].attrib['source']
        if 'LipRollJot' in jntName:
            lipYJnt = jntName.replace('RollJot','Y') 
            
            lipYJntID = getJointIndex('headSkin',lipYJnt)
            rollJntID = getJointIndex('headSkin',jntName)
            
            for dict in rootHeadSkin[i]:
                vertNum = int(dict.attrib['index'])
                wgtVal= float(dict.attrib['value'])
                if vertNum in rollVertNum:
                    
                    cmds.setAttr ( 'headSkin.wl['+ str(vertNum) + "].w[" + str(rollJntID)+ "]", ( min(1, rollWgt[vertNum]) * wgtVal) )
            
                if vertNum in lipVertNum:
                    
                    cmds.setAttr ( 'headSkin.wl['+ str(vertNum) + "].w[" + str(lipYJntID) + "]", ( max( lipWgt[vertNum] - rollWgt[vertNum], 0 )* wgtVal) )

    cmds.skinPercent('headSkin', 'head_REN', nrm= 1)
    #cmds.setAttr( 'headSkin.normalizeWeights', 2 )


