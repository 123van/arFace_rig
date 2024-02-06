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
            print "ON!!"
        elif bool == 0:
            cmds.setAttr( df + '.nodeState', 1-bool)
            print "OFF!!"
            


""" create circle controller(l_/r_/c_) and parent group at the position
    shape : circle = cc / square = sq 
    colorNum : 13 = red, 15 = blue, 17 = yellow, 18 = lightBlue, 20 = lightRed, 23 = green
    return [ ctrl, ctrlP ]
24 똥색 / 23:숙색 / 22:밝은 노랑 / 21:밝은 주황 / 20: 밝은 핑크 / 19: 밝은연두 / 18: 하늘색 / 17 yellow / 16 white
15: dark blue / 14: bright green / 13: red / 12: red dark 자두색 / 11: 고동색 / 10: 똥색 / 9: 보라 / 8: 남보라
7: 녹색 / 6: 파랑 / 5 : 남색 / 4 : 주황 / 3 : 회색 / 2: 진회색 / 1: 검정"""
def genericController( ctlName, position, radius, shape, colorId ):
    if shape == "cc":
        degree = 3 # cubic
        section = 8 # smooth circle
        
    elif shape =="sq" :
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
    clusterDict = { 'jawRigPos': ['jawOpen_cls', 'jawClose_cls' ], 'lipYPos':'lip_cls', 'lipRollPos':'lipRoll_cls', 'lipNPos': 'upLipRoll_cls',
'lipSPos': 'bttmLipRoll_cls', 'cheekPos':['l_cheek_cls','r_cheek_cls'], 
    'lEyePos':['eyeBlink_cls', 'eyeWide_cls'], 'lowCheekPos': ['l_lowCheek_cls', 'r_lowCheek_cls'], 'squintPuffPos':['l_squintPuff_cls', 'r_squintPuff_cls'], 
    'lEarPos':['l_ear_cls','r_ear_cls'], 'rotXPivot':['browUp_cls','browDn_cls'], 'rotYPivot':'browTZ_cls', 'nosePos': 'nose_cls' }
    
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
            if loc in [ 'lowCheekPos', 'cheekPos', 'squintPuffPos' ]:
                mirrPos = [ -ctlPos[0], ctlPos[1], ctlPos[2]]
                mirrLoc = cmds.spaceLocator(  n= loc.replace("Pos","Mirr") )
                cmds.parent(mirrLoc, 'allPos')
                cmds.xform ( mirrLoc, ws=1, t= mirrPos )
                offsetOnFace = [ 0,0,tranZ ]
             
                lCtlJnt = clusterOnJoint( loc, clsName[0], "midCtl_grp", offsetOnFace, rad, 8 )
                rCtlJnt = clusterOnJoint( mirrLoc, clsName[1], "midCtl_grp", offsetOnFace, rad, 8 )               

                for at in [ "t","r","s"]:
                    cmds.connectAttr( lCtlJnt[0] + "." + at, lCtlJnt[1] + "."+ at ) 
                    cmds.connectAttr( rCtlJnt[0] + "." + at, rCtlJnt[1] + "."+ at )                            
                
            elif loc == "lEarPos":
                mirrPos = [ -ctlPos[0], ctlPos[1], ctlPos[2]]
                mirrLoc = cmds.spaceLocator(  n= loc.replace("Pos","Mirr") )
                cmds.parent(mirrLoc, 'allPos')
                cmds.xform ( mirrLoc, ws=1, t= mirrPos )
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
                
            elif loc == 'lEyePos':
				colorList = [18, 14, 4, 12, 11, 10, 2, 6 ]
				# 'eyeBlink_cls', 'eyeWide_cls'
				for cls in clsName:
					index-=1
					ctlJnt =  clusterForSkinWeight( loc, zDepth, cls, "faceClsFrame", rad*index, 4, colorList[index+1] )			
					tranToRot_mult( ctlJnt, 30 )
            	
            
            else:
                #print clsName
				colorList = [18, 14, 4, 12, 11, 10, 2, 6 ]
				#'jawOpen_cls', 'jawClose_cls' 'eyeBlink_cls', 'eyeWide_cls'
				for cls in clsName:
					index-=1
					ctlJnt =  clusterForSkinWeight( loc, zDepth, cls, "faceClsFrame", rad*index, 4, colorList[index+1] )
					tranToRot_mult( ctlJnt, 30 )
					if cls == "jawClose_cls":
						cmds.hide(ctlJnt[0])
                                 
      
        else:

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
				print "the single cls: "+ clsName
				ctlJnt = clusterForSkinWeight( loc, zDepth, clsName, "faceClsFrame", rad, 8, 9 )                
				for att in [ "t","r","s"]:
					cmds.connectAttr( ctlJnt[0] + "." + att, ctlJnt[1] + "."+ att ) 
    
	cmds.setAttr( "faceClsFrame.tx", xMax*2 )
                





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





#select the updated locator in new position : run script to update cluster handle's rotatePivot
#check if headSkel_jnt in the right place and fix it manually if it is wrong place
def updateFaceCluster():
    #temporaly hide face joints for
    clusterDict = { 'jawRigPos': 'jawOpen_cls', 'lipYPos':'lip_cls', 'lipRollPos':'lipRoll_cls', 'cheekPos':['l_cheek_cls','r_cheek_cls'], 
    'lEyePos':['eyeBlink_cls', 'eyeWide_cls'], 'lowCheekPos': ['l_lowCheek_cls', 'r_lowCheek_cls'], 'squintPuffPos':['l_squintPuff_cls', 'r_squintPuff_cls'], 
    'lEarPos':['l_ear_cls','r_ear_cls'], 'rotXPivot':['browUp_cls','browDn_cls'], 'nosePos': 'nose_cls' }
    
    loc = cmds.ls(sl=1, type="transform" )
    locPos =cmds.xform( loc[0], q=1, ws=1, t =1 )
    cls = clusterDict[loc[0]]
    print cls

    if len(cls)==2:
        if "l_" in cls[0]:
            handle=cmds.listConnections(cls[0]+".matrix", s=1, d=0, type="transform")
            cmds.xform( handle[0], ws=1, rotatePivot = locPos )
            cmds.xform( cls[0].replace("cls","grp"), ws=1, t = locPos )
                        
            mirrorPos = [-locPos[0], locPos[1], locPos[2] ]
            rHandle=cmds.listConnections(cls[1]+".matrix", s=1, d=0, type="transform")
            cmds.xform( rHandle[0], ws=1, rotatePivot = mirrorPos )                
            cmds.xform( cls[1].replace("cls","grp"), ws=1, t = mirrorPos )
        else:
            
            for c in cls:
                handle=cmds.listConnections(c+".matrix", s=1, d=0, type="transform")
                cmds.xform( handle[0], ws=1, p=1, rotatePivot = locPos )
            if "eyeBlink_cls" in cls:
                cmds.xform( "eyeRig", ws=1, t = locPos )
                
    else:        
        handle=cmds.listConnections(cls+".matrix", s=1, d=0, type="transform")
        cmds.xform( handle[0], ws=1, rotatePivot = locPos ) 
        ''''if cls == "jawOpen_cls":
            cmds.xform("jawRig", ws=1, t = locPos )
        elif cls == "node_cls":
            cmds.xform("noseRig", ws=1, t = locPos )'''
            
            
#when locators (headSkel, cheek, nose, ears) position changed or hierachy created before creating skinning.          
def updateHierachy():
        
    locPos = { '1headSkelPos': ["headSkel"], '2jawRigPos':['jawRig'], '3cheekPos':['l_cheek_grp','r_cheek_grp'], '4squintPuffPos':['l_squintPuff_grp','r_squintPuff_grp'], 
    '5lowCheekPos':['l_lowCheek_grp','r_lowCheek_grp'], '6lEyePos':['eyeRig'], '7nosePos':['noseRig'], '8lEarPos':['l_ear_grp','r_ear_grp'] } 

    headGeo = cmds.getAttr( "helpPanel_grp.headGeo")
    skins= mel.eval("findRelatedSkinCluster %s"%headGeo ) 
    if skins:
        cmds.warning("use reposition Rig")
        
    else:        
        for loc in sorted(locPos.items()):
            locName =  loc[0][1:]
            grpName = loc[1][0]
            if cmds.objExists(locName):
                
                if len(loc[1])== 1:
                    
                    if locName == 'headSkelPos':
                        headPos = cmds.xform( 'headSkelPos', t = True, q = True, ws = True )
                        oldHeadPos = cmds.xform( grpName, t = True, q = True, ws = True )
                                            
                        if not headPos == oldHeadPos:
                            # update position of headSkel_jnt/ bodyHeadTRSP 
                            cmds.xform( grpName,  ws = True, piv = headPos )
                            kids = ( k for k in cmds.listRelatives("headSkel", c=1 ) if k not in ["jawRig","eyeRig","browRig"] )
                            for kd in kids:
                                cmds.xform( kd,  ws = True, t = headPos)
                            
                    elif locName == 'jawRigPos':
                        
                        jawPos = cmds.xform( 'jawRigPos', t = True, q = True, ws = True )
                        oldJawPos = cmds.xform( grpName, t = True, q = True, ws = True )
                                            
                        if not jawPos == oldJawPos:                    
                            cmds.xform( grpName,  ws = True, t = jawPos )

                        jotYPos = cmds.xform( 'lipYPos', t = True, q = True, ws = True ) 
                        jotY = cmds.ls("*JotY*", type = "transform" )
                        for y in jotY:
                            cmds.xform( y,  ws = True, t = jotYPos )
                            
                        rollPos = cmds.xform( 'lipYPos', t = True, q = True, ws = True ) 
                        rollP = cmds.ls("*LipRollP*", type = "transform" )                    
                                                                
                        for rp in rollP:
                            guide = rp.replace("RollP", "Guide")+"_poc"
                            poc = guide.replace("Lip","_lip")
                            rpPos = cmds.getAttr( poc + ".position")
                            cmds.xform( rp,  ws = True, t = rpPos[0] ) 
                        
                    
                    elif loc == 'lEyePos':
                        pos = cmds.xform( 'lEyePos', t = True, q = True, ws = True )
                        oldPos = cmds.xform( grpName, t = True, q = True, ws = True )
                        
                        if not oldPos[1] == pos[1] and not oldPos[2] == pos[2]:
                            cmds.xform( grpName, ws = True, t = ( 0, pos[1], pos[2] ) )                        
                            
                    else:

                        pos = cmds.xform( locName, t = True, q = True, ws = True ) 
                        oldPos = cmds.xform( grpName, t = True, q = True, ws = True)
                        if not oldPos == pos:
                            cmds.xform( grpName, ws = True, t = pos )         
                
                elif len(loc[1])==2:            
        
                    pos = cmds.xform( locName, t = True, q = True, ws = True )
                    oldPos = cmds.xform( grpName, t = True, q = True, ws = True)
                    
                    # ex) if jawRig position is not same as 'jawRigPos'
                    if not oldPos == pos:
                        cmds.xform( loc[1][0], ws = True, t = pos )
                        cmds.xform( loc[1][1], ws = True, t = ( -pos[0], pos[1], pos[2] ) )   
        
        
        
        
#update 5/9/2019 : browDown_jnt, browTz weight will get cut by browUp weight
#update 10/25/2017 : browUp/Dn , browWide_jnt setup
#set the headSkin weight to 1 on headSkel_jnt before calculate
#import the xml weight file and calculate the jaw joint weight 
def faceWeightCalculate():   

    headGeo = cmds.getAttr("helpPanel_grp.headGeo")
    eyeLidGeo = cmds.getAttr("lidFactor.eyelidGeo")
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
    eyeBlinkWgt =cmds.getAttr ( "eyeBlink_cls.wl[0].w[0:%s]"%str(size-1))
    eyeWideWgt = cmds.getAttr ( "eyeWide_cls.wl[0].w[0:%s]"%str(size-1))							
   
    valStr = ''
    jcValStr = ''
    upCheekStr = ''
    midCheekStr = ''
    headSkelID = getJointIndex( 'headSkin','headSkel_jnt' )
    jawCloseID = getJointIndex( 'headSkin','jawClose_jnt' )
    #upCheekID = getJointIndex ( 'headSkin', 'l_upCheek_jnt' )
    #midCheekID = getJointIndex ( 'headSkin', 'l_midCheek_jnt' )
    
    #set weight back to 1 on the headSkel_jnt
    cmds.skinPercent( 'headSkin', headGeo+'.vtx[0:%s]'%(size-1), nrm=1, tv = ['headSkel_jnt',1] )
    #cmds.skinPercent( 'eyeLidMapSkin', 'eyeLidMapHead.vtx[0:%s]'%(size-1), nrm=1, tv = ['headSkel_jnt',1] )
    #cmds.skinPercent( 'browMapSkin', 'browMapHead.vtx[0:%s]'%(size-1), nrm=1, tv = ['headSkel_jnt',1] )
    cmds.setAttr( 'headSkin.normalizeWeights', 0 )
    
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
     
    commandStr = ("setAttr -s "+str(size)+" headSkin.wl[0:"+str(size-1)+"].w["+headSkelID+"] "+ valStr);
    mel.eval (commandStr)
                 
    cmmdStr = ("setAttr -s "+str(size)+" headSkin.wl[0:"+str(size-1)+"].w["+jawCloseID+"] "+ jcValStr);
    mel.eval (cmmdStr)
    '''
    upCheekCmmdStr = ("setAttr -s "+str(size)+" headSkin.wl[0:"+str(size-1)+"].w["+upCheekID+"] "+ upCheekStr);
    mel.eval (upCheekCmmdStr)

    upCheekCmmdStr = ("setAttr -s "+str(size)+" headSkin.wl[0:"+str(size-1)+"].w["+midCheekID+"] "+ midCheekStr);
    mel.eval (upCheekCmmdStr)'''
    
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
                
                lipYJntID = getJointIndex('headSkin',lipYJnt)
                print lipYJnt, lipYJntID
                rollJntID = getJointIndex('headSkin',jntName)
                
                for dict in rootHeadSkin[i]:
                    vertNum = int(dict.attrib['index'])
                    wgtVal= float(dict.attrib['value'])
                    #if vertNum in rollVertNum:
                    cmds.setAttr ( 'headSkin.wl['+ str(vertNum) + "].w[" + str(rollJntID)+ "]", min(1, rollWgt[vertNum])* wgtVal  )
                                     
                    #if vertNum in lipVertNum:                        
                    cmds.setAttr ( 'headSkin.wl['+ str(vertNum) + "].w[" + str(lipYJntID) + "]", max( lipWgt[vertNum] - rollWgt[vertNum], 0 )* wgtVal )
    else:
        print "headSkin.xml(lipWeight file) does not exists"     
    
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
				
				blinkJntID = getJointIndex( "headSkin",eyeTipJnt )
				wideJntID = getJointIndex( "headSkin",eyeWideJnt )
				for dict in rootEyeLidSkin[c]:				
					vertID = int(dict.attrib['index'])
					weight= float(dict.attrib['value'])
					cmds.setAttr ( 'headSkin.wl['+ str(vertID) + "].w[" + str(blinkJntID)+ "]", ( min(1, eyeBlinkWgt[vertID]) * weight) )
					 
					cmds.setAttr ( 'headSkin.wl['+ str(vertID) + "].w[" + str(wideJntID) + "]", ( max( eyeWideWgt[vertID] -eyeBlinkWgt[vertID], 0 )* weight) )

    
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
                rotYJntID = getJointIndex('headSkin',rotYJnt[0] ) 
                childJntID = getJointIndex('headSkin',browJnt )
                baseJnt = browPJnt[0].replace("P","Base")
                baseJntID = getJointIndex('headSkin',baseJnt )
                browWide = browPJnt[0].replace("P","Wide")
                if cmds.objExists(browWide):
                    wideJntID = getJointIndex('headSkin',browWide )
                    
                for dict in rootBrowSkin[f]:
                    vertIndex = int(dict.attrib['index'])
                    wgtValue= float(dict.attrib['value'])
                    #if vertIndex in browTZNum:
                     
                    cmds.setAttr ( 'headSkin.wl['+ str(vertIndex) + "].w[" + str(childJntID)+ "]", ( min(1, browTZWgt[vertIndex]) * wgtValue))                
             
                    baseVal = max( ( browUpWgt[vertIndex] - browDnWgt[vertIndex] ),0 )
                    cmds.setAttr ( 'headSkin.wl['+ str(vertIndex) + "].w[" + str(baseJntID) + "]", baseVal*wgtValue )
                    
                    roYVal = max( ( browUpWgt[vertIndex] - baseVal - browTZWgt[vertIndex] ), 0 )
                    cmds.setAttr ( 'headSkin.wl['+ str(vertIndex) + "].w[" + str(rotYJntID) + "]", roYVal*wgtValue )                    
                  
                    if cmds.objExists(browWide):
                        wideVal = max( (browDnWgt[vertIndex] - browUpWgt[vertIndex]),0 )
                        cmds.setAttr ( 'headSkin.wl['+ str(vertIndex) + "].w[" + str(wideJntID) + "]", wideVal*wgtValue )           
        
    #cmds.skinPercent('headSkin', headGeo, nrm=False, prw=100)
    cmds.setAttr( 'headSkin.normalizeWeights', 1 )#normalization mode. 0 - none, 1 - interactive, 2 - post         
    cmds.skinPercent('headSkin', headGeo, nrm= 1 )
    # mirror weight 
    #cmds.copySkinWeights( ss = 'headSkin', ds = 'headSkin', mirrorMode= 'YZ', sa= 'closestPoint', influenceAssociation = 'label', ia = 'oneToOne', normalize=1) 


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




def rnkCopyJawOpenWeight():
    
    headGeo = cmds.ls(sl=1, type = "transform")[0]
    size = cmds.polyEvaluate( headGeo, v = 1)
    skinCls = mel.eval("findRelatedSkinCluster %s"%headGeo )
    print skinCls
    #set weight back to 1 on the headSkel_jnt
    cmds.skinPercent( skinCls, headGeo+'.vtx[0:%s]'%(size-1), nrm=1, tv = ['C_jnt_jaw_Head_JNT', 1] )
    cmds.setAttr( skinCls +'.normalizeWeights', 0 )
    
    jawOpenWgt = cmds.getAttr ("jawOpen_cls.wl[0].w[0:"+str(size-1)+"]" )             
    upLipWgt = cmds.getAttr ("upLipRoll_cls.wl[0].w[0:"+str(size-1)+"]")
    bttmLipWgt = cmds.getAttr ( "bttmLipRoll_cls.wl[0].w[0:%s]"%str(size-1))    

    headSkelID = getJointIndex( skinCls,'C_jnt_jaw_Head_JNT' )
    upjawID = getJointIndex( skinCls, 'C_jnt_jaw_uJaw_JNT' ) 
    jawID = getJointIndex( skinCls, 'C_jnt_jaw_Jaw_JNT' )
    topLipID = getJointIndex ( skinCls, 'C_jnt_jaw_lips_Top_pivot_JNT' )
    botLipID = getJointIndex ( skinCls, 'C_jnt_jaw_lips_Bot_pivot_JNT' )

    botLipStr = ''
    upLipStr = ''
    jcValStr = ''
    valStr =''
    headVal = ''
    for x in range(size):
        
        if jawOpenWgt[x]>1:
            jawOpenWgt[x] = 1 

        upLipStr +=str(upLipWgt[x])+" "
        
        tempVal = jawOpenWgt[x] - bttmLipWgt[x] 
        if tempVal < 0 :
            bttmLipWgt[x] = jawOpenWgt[x]
        #jaw weight - bttmLip weight            
        jcVal = jawOpenWgt[x] - bttmLipWgt[x]
        jcValStr += str(jcVal)+" "
              
        botLipStr +=str(bttmLipWgt[x]) + " "
        
        #headSkel_jnt weight =           
        tmpVal = 1 -jawOpenWgt[x] - upLipWgt[x]
        valStr +=str(tmpVal)+" "
        
        headVal +=str(0)+" " 

    
    commandStr = ("setAttr -s "+str(size)+" " + skinCls+".wl[0:"+str(size-1)+"].w["+upjawID+"] "+ valStr );
    mel.eval (commandStr)                 

    headCmmdStr = ("setAttr -s "+str(size)+" " + skinCls+".wl[0:"+str(size-1)+"].w["+headSkelID+"] "+ headVal );
    mel.eval (headCmmdStr) 
    
    cmmdStr = ("setAttr -s "+str(size)+" " +skinCls + ".wl[0:"+str(size-1)+"].w["+jawID+"] "+ jcValStr);
    mel.eval (cmmdStr)
    
    topLipCmmdStr = ("setAttr -s "+str(size)+" " + skinCls+".wl[0:"+str(size-1)+"].w["+topLipID+"] "+ upLipStr);
    mel.eval (topLipCmmdStr) 
      
    botLipCmmdStr = ("setAttr -s "+str(size)+" " + skinCls+".wl[0:"+str(size-1)+"].w["+botLipID+"] "+ botLipStr);
    mel.eval (botLipCmmdStr)

    #cmds.skinPercent('headSkin', headGeo, nrm=False, prw=100)
    cmds.setAttr( skinCls + '.normalizeWeights', 1 )#normalization mode. 0 - none, 1 - interactive, 2 - post         
    cmds.skinPercent( skinCls , headGeo, nrm= 1 )


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
def calExtraClsWgt():

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
    eyeWideWgt = cmds.getAttr ("eyeWide_cls.wl[0].w[0:"+str(size-1)+"]")
    eyeBlinkWgt = cmds.getAttr ("eyeBlink_cls.wl[0].w[0:"+str(size-1)+"]") 

    for i in faceIndices:

        vtxVal= browUpWgt[i]-browTZWgt[i]
        if vtxVal<0:
            cmds.setAttr("browTZ_cls.wl[0].w[%s]"%str(i), browUpWgt[i])  
        
        browVal= browDnWgt[i]-browUpWgt[i]
        if vtxVal<0:
            cmds.setAttr("browUp_cls.wl[0].w[%s]"%str(i), browDnWgt[i])  
            
        eyeVtxVal= eyeWideWgt[i]-eyeBlinkWgt[i]
        if eyeVtxVal<0:
            cmds.setAttr("eyeBlink_cls.wl[0].w[%s]"%str(i), eyeWideWgt[i])
            
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
    calExtraClsWgt()

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
    ctls = ['jawOpen_ctl', 'jawClose_ctl', 'lip_ctl', 'lipRoll_ctl', 'l_cheek_onCtl', 'r_cheek_onCtl', 'eyeBlink_ctl', 'eyeWide_ctl', 
    'l_lowCheek_onCtl', 'r_lowCheek_onCtl', 'l_squintPuff_onCtl','r_squintPuff_onCtl', 'browUp_ctl', 'browDn_ctl', 'browTZ_ctl', 'nose_onCtl',
    'l_ear_onCtl', 'r_ear_onCtl' ]
   
    for ct in ctls:

        attrs = cmds.listAttr( ct, k=1, unlocked = 1 )
        for at in attrs:
            if 'scale' in at or "visibility" in at:
                cmds.setAttr( ct+"."+at, 1 )
            else:
                cmds.setAttr( ct+"."+at, 0 )




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
    
    
    
    

def getOrigMesh( obj ):
    
    shapes = cmds.listRelatives( obj, ad=1, type = 'shape')
    origList = [ s for s in shapes if "Orig" in s ]
    #check if it treverse forward the shape of the selection 
    for org in origList:
        future = cmds.listHistory( obj+'Shape', f=1 )
        if future:
            if obj+'Shape' in future:
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

    
    
''' 각각의 서피스 웨이트 맵의 값을 카피할 디폴트 skin face하나씩 만든다 '''
# skin head with normal interactive / skinPercent to headSkel_jnt with normalization
def arFaceHeadSkin(geoName):
    if geoName == cmds.getAttr("helpPanel_grp.headGeo"):
        
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
        print "do headSkin, if it's not for arFace setup"



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
    
    geo = cmds.cluster( cls, q=1, g=1)
    #get geometryIndex if the cluster deforms multiple geo
    if len(geo)>1:
        for i, g in enumerate(geo):
            if obj in g:
                geometryIndex = i
        vtxNum = cmds.polyEvaluate( obj, v = 1)
        clsVal= cmds.getAttr( cls + '.wl['+ str(geometryIndex) + '].w[0:%s]'%(vtxNum-1) )
        verts = {}
        for x in range(vtxNum):
            val = clsVal[x]
            if val > 0.001:
                verts[ x ] = val
        return verts
    else:
        vtxNum = cmds.polyEvaluate( obj, v = 1)
        clsVal= cmds.getAttr( cls + '.wl[0].w[0:%s]'%(vtxNum-1) )
        verts = {}
        for x in range(vtxNum):
            val = clsVal[x]
            if val > 0.001:
                verts[ x ] = val
        return verts


    
def weightedVerts(obj, cls):
    if clsVertsDict( obj, cls):
        vtx =[ obj + '.vtx[%s]'%v for v in clsVertsDict( obj, cls).keys() ]
        cmds.select(vtx)
    else :
        print "paint weight on the cluster"
        

#select 2 cluster handle ( to copy weight / to paste weight )
def copyClusterWgt(sdCls, ddCls):
    headGeo = cmds.getAttr("helpPanel_grp.headGeo")
    size = cmds.polyEvaluate( headGeo, v=1)
    valStr = ""
    for i in range(size):
        copyWgt = cmds.getAttr( sdCls + ".wl[0].w[%s]"%str(i) )
        valStr += str(copyWgt)+" "
    commandStr = ("setAttr -s " +str(size) + " %s.wl[0].w[0:%s] "%(ddCls, str(size-1)) + valStr);
    mel.eval(commandStr)
    

def exportClsWgt():
    #pathProject = cmds.workspace(  q=True, rd = True )
    dataPath = cmds.fileDialog2(fileMode=3, caption="set directory")
    #cmds.file( filename[0], index=True );
    if "clusterWeight" not in dataPath[0]:
        i = 0
        while os.path.isdir(dataPath[0] + "/clusterWeight%s" % i):   
            i += 1
        os.makedirs( dataPath[0] + "/clusterWeight" + str(i))
        dataPath = [dataPath[0] + "/clusterWeight" + str(i)]
    mesh = cmds.ls( sl=1 )
    clsList = [ c for c in cmds.listHistory( mesh ) if cmds.nodeType(c) == "cluster" ]
    for cls in clsList:
        cmds.deformerWeights( cls.replace("cls","wgt") + ".xml", deformer = cls, ex =1, path = dataPath[0] )
        


def importClsWgt():    
    #pathProject = cmds.workspace(  q=True, rd = True )
    dataPath = cmds.fileDialog2(fileMode=3, caption="set directory")

    mesh = cmds.ls( sl=1 )
    clsList = [ c for c in cmds.listHistory( mesh ) if cmds.nodeType(c) == "cluster" ]
    for cls in clsList:
        if os.path.exists( dataPath[0] + "/" + cls.replace("cls","wgt") + ".xml"):
            cmds.deformerWeights( cls.replace("cls","wgt") + ".xml", im=1, method= "index", deformer = cls, path = dataPath[0] )
        else:
            print "%s wgt.xml file doesn't exist"%cls
        
        
        
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

# select source curve first and target curve
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
            cmds.setAttr( dnVtx+".zValue", xyz[0][2] )	

            
# select left curve and right curve
def mirrorCurveSel():
    print "mirror"
    crvSel = cmds.ls(os=1, fl=1, long=1, type= "transform")
    scCv = cmds.ls(crvSel[0]+".cv[*]", l=1, fl=1 )
    dnNum = cmds.ls(crvSel[1]+".cv[*]", l=1, fl=1 )
    leng = len(scCv )
    if leng == len(dnNum):
        for i in range(leng ):
            scPos = cmds.xform(scCv[i], q=1, ws=1, t=1 )
            cmds.setAttr( dnNum[leng-i-1]+".xValue", -scPos[0] )
            cmds.setAttr( dnNum[leng-i-1]+".yValue", scPos[1] )
            cmds.setAttr( dnNum[leng-i-1]+".zValue", scPos[2] )
    
    else:
        increm=1.0/(len(dnNum)-1)
        for i, dnVtx in enumerate( dnNum ):
            dnPOC = cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = 'dnPOC'+ str(i+1).zfill(2))
            cmds.connectAttr ( crvSel[0] + ".worldSpace",  dnPOC + '.inputCurve')
    	    cmds.setAttr ( dnPOC + '.turnOnPercentage', 1 )
    	    cmds.setAttr ( dnPOC + '.parameter', increm *i )	    
    	
            xyz = cmds.getAttr(dnPOC+".position" )
            cmds.setAttr( dnVtx+".xValue", -xyz[0][0] )
            cmds.setAttr( dnVtx+".yValue", xyz[0][1] )
            cmds.setAttr( dnVtx+".zValue", xyz[0][2] )	
                

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
    
    jnts = ['l_lowCheek_jnt','r_lowCheek_jnt','l_cornerUp_jnt','r_cornerUp_jnt','l_cornerDwn_jnt','r_cornerDwn_jnt','l_squintPuff_jnt', 'r_squintPuff_jnt','l_ear_jnt','r_ear_jnt','nose_jnt']
     
    for j,k in zip(*[iter(jnts)]*2):
        if j.replace("jnt","cls") and k.replace("jnt","cls"):            
            cmds.copyDeformerWeights( sd = j.replace("jnt","cls"), ss= headGeo, ds = headGeo, dd = k.replace("jnt","cls"), mirrorMode = "YZ", surfaceAssociation = "closestPoint" )
            print "%s weight mirrored"%j.replace("jnt","cls")



#mirror cls weight left to right 
def indieClsWeightMirror( clsName ):
    headGeo = cmds.getAttr("helpPanel_grp.headGeo")
    cmds.copyDeformerWeights( sd = "l_"+clsName+"_cls", ss=headGeo, ds = headGeo, dd =  "r_"+clsName+"_cls", mirrorMode = "YZ", surfaceAssociation = "closestPoint" )
    print "%s weight mirrored"%("l_"+clsName+"_cls")


            
            

#set keys on all ctrls
def dgTimer():
    dataPath = cmds.fileDialog2(fileMode=3, caption="set directory")
    #cmds.file( filename[0], index=True );
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
def attatchTwitchHead():
    headSel = cmds.ls(sl=1, type = "transform")
    change=cmds.xform(headSel[1], q=1, ws=1, t=1 )
    origin=cmds.xform(headSel[0], q=1, ws=1, t=1 )
    cmds.xform("squachJnt_grp", ws=1, t=(origin[0], origin[1]-xyz[1], origin[2]-xyz[2]) )



def deleteUnknown_plugins():
    unknown_plugins = cmds.unknownPlugin(q=True, list=True) or []
    for up in unknown_plugins:
        print up
        cmds.unknownPlugin(up, remove=True)


    
#miscellaneous__________________________________________________________________________________________________________________________________________________________________________________________________________________________
#_____________________________________________________________________________________________________________
# select curve with BS and new curve in origin world    
def copyCrvDeltaBS():    
    crvSel = cmds.ls(sl=1)
    crvBS = [ n for n in cmds.listHistory(crvSel[0], historyAttr=1 ) if cmds.nodeType(n) == "blendShape" ]    
    if crvBS:
        aliasAtt = cmds.aliasAttr(crvBS[0], q=1)
        
    else:
        print "select the curve with blendShape" 
    browCrv = crvSel[1]
    browTgt = []
    for tgt, wgt in zip(*[iter(aliasAtt)]*2):
        browCopyCrv = cmds.duplicate ( browCrv, n= tgt )[0]
        browTgt.append(browCopyCrv)
    numTgt = len(browTgt)
    cmds.select(browTgt, r=1)
    cmds.select(browCrv, add=1)   
    newBS = cmds.blendShape ( n ='browBS')
    cmds.delete(browTgt)
    print newBS
    for i in range( numTgt ):
        
        comp = cmds.getAttr(crvBS[0]+ '.inputTarget[0].inputTargetGroup[%s].inputTargetItem[6000].inputComponentsTarget'%str(i) )
        delta = cmds.getAttr(crvBS[0]+ '.inputTarget[0].inputTargetGroup[%s].inputTargetItem[6000].inputPointsTarget'%str(i) )
        cmds.setAttr(newBS[0]+'.inputTarget[0].inputTargetGroup[%s].inputTargetItem[6000].inputComponentsTarget'%str(i), len(comp), *comp, type="componentList" )
        cmds.setAttr(newBS[0]+'.inputTarget[0].inputTargetGroup[%s].inputTargetItem[6000].inputPointsTarget'%str(i), len(delta), *delta, type="pointArray" ) 



# select sourceCurve and targetCurve
def bakeCrvBSDelta():
    
    crvSel = cmds.ls(os=1)
    sourceCrv = crvSel[0]
    targetCrv = crvSel[1]
    shapes = cmds.listRelatives( sourceCrv, ad=1, type='shape' )
    origCrv = [ t for t in shapes if 'Orig' in t ]
    #get the orig shapes with history and delete the ones with with same name.
    myOrig = ''
    for orig in origCrv:
        if cmds.listConnections( orig, s=0, d=1 ):
            myOrig = orig
        else: cmds.delete(orig)
    
    targetCrvShp = cmds.listRelatives( crvSel[1], c=1, ni=1, type='shape' )[0]
    
    cmds.connectAttr( targetCrvShp +".worldSpace", myOrig + ".create", f=1 )
    
    crvBS = [ n for n in cmds.listHistory(crvSel[0], historyAttr=1 ) if cmds.nodeType(n) == "blendShape" ]    
    if crvBS:
        aliasAtt = cmds.aliasAttr(crvBS[0], q=1)
        
    else:
        print "select the curve with blendShape" 
    
    browTgt = []
    for tgt, wgt in zip(*[iter(aliasAtt)]*2):
        print tgt, wgt
        cmds.setAttr( crvBS[0] + "." + tgt, 1 )
        browCopyCrv = cmds.duplicate ( sourceCrv, n= tgt )[0]    
        browTgt.append(browCopyCrv)
        cmds.xform(browCopyCrv, ws=1, t = (0,0,0), ro=(0,0,0), s=(1, 1, 1) )
        cmds.setAttr( crvBS[0] + "." + tgt, 0 )
    
    cmds.select(browTgt, r=1)
    cmds.select(targetCrv, add=1 )   
    newBS = cmds.blendShape ( n ='browBS')

    



#copy cluster weight to blendShape target weight
def transferWeight(cls, bs, targetID ):
    
    headGeo = cmds.getAttr("helpPanel_grp.headGeo")
    size = cmds.polyEvaluate( headGeo, v=1)
    target = cmds.ls(sl=1, type="transform")[0]
    valStr = []
    for i in range(size):
        copyWgt = cmds.getAttr( cls+ ".wl[0].w[%s]"%str(i) )
        valStr.append(copyWgt)
            
    cmds.setAttr( bs + ".inputTarget[0].inputTargetGroup[%s].targetWeights[0:%s]"%(targetID, size-1), *valStr )
    


    



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

                

    
def surfMapSmoothWgt():    
    clsHead = 'lipTip_map'
    mel.eval('findRelatedSkinCluster '+clsHead)

    size = cmds.polyEvaluate( "browMapSurf", v = 1)
    for i in range(4, size-3, 4):
        print i
        cmds.select("browMapSurf.vtx[%s:%s]"%(i,i+3) )
        mel.eval( 'doSmoothSkinWeightsArgList 3 { ".0", "5", "0", "1"   }' )
        
        
        
        
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
    print "shit"
    
    

'''
1. headSkel의 월드 transform값을 상쇄시켜준다. inverseMatrix값을 eyeParent("InverseHeadSkel")에 연결
2. EyeballRot의 월드 matrix를 L_EyeDecompose에 연걸
3. l_lo/up/cnrLidP_jnt driven by LeyeOffsetCtrl
5. parent eyeball under "EyeballRot" for all the defroming
6.   create instance eyeball / parent under "eyeOffSet" to follow bodyRig 
7. "lEyePos.rotate" line up with "l_eyeRP.rot"/
'''

def eyeDirectionOffset():
    
    lEyePos = cmds.xform("lEyePos", q=1, ws=1, t=1)
    rEyePos = [ -lEyePos[0], lEyePos[1], lEyePos[2] ]
    aimCtlP = "eyeAim_ctl"
    aimCtlTop = cmds.duplicate( aimCtlP, po =1, n = "eyeAim_ctlTop")
    cmds.parent( aimCtlP, aimCtlTop )
    cmds.parent( aimCtlTop[0], "attachCtl_grp" )
    cmds.xform( aimCtlTop[0], ws=1, t = [0, lEyePos[1], lEyePos[2] ] )
    aimCtlKids =cmds.listRelatives( aimCtlP, c=1, type ="transform")

    for LR, pos in { "l_":lEyePos, "r_":rEyePos }.iteritems():
        
        #set eyeBall ry
        eyeHi = LR + "eye_hi"
        if eyeHi:
            eyeballRy = cmds.getAttr( eyeHi+".ry" )
            cmds.setAttr( LR + "eyeRP.ry", eyeballRy )
            cmds.parent( eyeHi, LR + "eyeballRot", a=1 )
            cmds.setAttr( eyeHi + ".ry", 0 )                     
            
        headSkelInverse = cmds.group( em=1, p = "bodyHeadTRS", n = LR + "InverseHeadSkel" )
        eyeDecomp = cmds.group( em=1, p = headSkelInverse, n = LR+"eyeDecompose" )
        eyeAimGrp = cmds.group( em=1, p = headSkelInverse, n = LR + "eyeAimGrp" )
        eyeOffSet = cmds.group( em=1, p = eyeDecomp, n = LR+"eyeOffSet" )
     
        decomp = cmds.shadingNode( "decomposeMatrix", asUtility =1, n = "inverse_headSkel")
        cmds.connectAttr( "headSkel.worldInverseMatrix[0]", decomp+".inputMatrix" )
        cmds.connectAttr( decomp+".outputShear",  headSkelInverse+".shear")
        cmds.connectAttr( decomp+".outputScale",  headSkelInverse+".scale")
        cmds.connectAttr( decomp+".outputRotate",  headSkelInverse+".rotate")
        cmds.connectAttr( decomp+".outputTranslate",  headSkelInverse+".translate")
        
        cmds.xform( eyeAimGrp, ws=1, t =pos )
        eyeBallMatrix = cmds.shadingNode( "decomposeMatrix", asUtility =1, n = LR + "eyeBall_worldMatrix")
        cmds.connectAttr( LR + "eyeballRot.worldMatrix", eyeBallMatrix+".inputMatrix" )
        cmds.connectAttr(  eyeBallMatrix+".outputTranslate", eyeDecomp+".translate" )
        cmds.connectAttr(  eyeBallMatrix+".outputRotate", eyeDecomp+".rotate" )
        cmds.connectAttr(  eyeBallMatrix+".outputScale", eyeDecomp+".scale" )
        cmds.connectAttr(  eyeBallMatrix+".outputShear", eyeDecomp+".shear" )
        
        aimCtlGrp = [ grp for grp in aimCtlKids if LR in grp ]        
        aimCtl = cmds.listRelatives( aimCtlGrp[0], c=1, type ="transform") 
        cmds.xform( aimCtlGrp[0], ws=1, t= pos )
        const = cmds.aimConstraint( aimCtl[0], eyeAimGrp, mo=1, aimVector =[0, 0, 1], upVector=[0, 1, 0] )
        
        #create eyeball attatch to body
        eyeAtBody = cmds.duplicate( LR + "eye_hi", ilf =1, rc=1, n = LR + "eye_REN")
        cmds.parent( eyeAtBody[0], eyeOffSet )
        cmds.setAttr( eyeAtBody[0] + ".ry", 0 )
        
        rotXBlend = cmds.shadingNode( "blendTwoAttr", asUtility =1, n = LR + "decompRX_blend")
        cmds.connectAttr( LR+"eyeBall_mult.outputY", rotXBlend+".input[0]")
        cmds.connectAttr( LR + "eyeAimGrp.rx", rotXBlend+".input[1]")
        rotYBlend = cmds.shadingNode( "blendTwoAttr", asUtility =1, n = LR + "decompRY_blend")
        cmds.connectAttr( LR+"eyeBall_mult.outputX", rotYBlend+".input[0]")
        cmds.connectAttr( LR + "eyeAimGrp.ry", rotYBlend+".input[1]")
        
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
        rxVal = cmds.getAttr("lidFactor.lidRotateX_scale" )
        ryVal = cmds.getAttr("lidFactor.lidRotateY_scale" )
        cmds.setAttr( eyeOffMult+".input2X", -rxVal )
        cmds.setAttr( eyeOffMult+".input2Y", ryVal )
        cmds.connectAttr( eyeOffMult + ".outputX", eyeOffSet+".rx" )
        cmds.connectAttr( eyeOffMult + ".outputY", eyeOffSet+".ry" )        
        
        #eyelid offset setup       
        offSetCtl = LR + "lidHeight"
        offsetMult = cmds.shadingNode( "multiplyDivide", asUtility=1, n =LR+"lidOffset_mult" )
        cmds.connectAttr( offSetCtl+".ty", offsetMult + ".input1X" )
        cmds.connectAttr( offSetCtl+".tx", offsetMult + ".input1Y" )
        cmds.setAttr( offsetMult+".input2X", -rxVal/2 )
        cmds.setAttr( offsetMult+".input2Y", ryVal/2 )
        lidPGrp = [ LR +"upLidP_jnt", LR +"loLidP_jnt", LR +"cnrLidP_jnt" ]
        for p in lidPGrp:
            cmds.connectAttr( offsetMult + ".outputX", p+".rx" )
            cmds.connectAttr( offsetMult + ".outputY", p+".ry" )                            
        cmds.hide(eyeHi)   
    cmds.setAttr( aimCtlTop[0] + ".tz", lEyePos[0]*10 )
    cmds.connectAttr( "eyeblend_dir.tx", aimCtlP +".visibility" ) 
    
    


            

# select up/lo teeth objects and run 
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
    
    teethCtl = UpLo + "teeth_motion"
    upLoGrp =cmds.group( em =1, p="teethCtl_grp", n="teeth%sTRSP"%UpLo.title())
    teethJnt=cmds.joint(  p=(0,0,0), r=True, n=UpLo+"Teeth_jnt" )
    for teeth in teethSel:
        cmds.skinCluster( teethJnt, teeth, bm=0, nw=1, weightDistribution=0, mi=1, omi=True,  tsb=True )

    teethPos = cmds.getAttr( "teeth%sTRSP.t"%UpLo.title())[0]
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
        #cmds.setAttr( upTranPlus+".input3D[1].input3Dy", teethPos[1] )
        cmds.connectAttr(upTranPlus+".output3Dy", upLoGrp+".ty" )           
        cmds.connectAttr( teethTranMult + ".outputZ", upLoGrp+".sx" )
        cmds.connectAttr( teethTranMult + ".outputZ", upLoGrp+".sy" )

        #cmds.setAttr( upTranPlus+".input3D[1].input3Dz", teethPos[2] )
        cmds.connectAttr(upTranPlus+".output3Dz", upLoGrp+".tz" )
        cmds.connectAttr( teethCtl + ".rz", upLoGrp+".rz"  )
        
    elif UpLo == "lo":
        cmds.connectAttr( loTranPlus+".output3Dx", upLoGrp+".tx" )
        cmds.connectAttr( teethTranMult + ".outputX", loTranPlus+".input3D[1].input3Dz" )
        cmds.connectAttr( teethTranMult + ".outputY", loTranPlus+".input3D[1].input3Dy" )
        #"loteeth_motion.scaleX" --> loTeeth scale
        cmds.connectAttr( teethTranMult + ".outputZ", upLoGrp+".sx" )
        cmds.connectAttr( teethTranMult + ".outputZ", upLoGrp+".sy" )
        
        #cmds.setAttr( loTranPlus+".input3D[2].input3Dy", teethPos[1] )
        cmds.connectAttr( loTranPlus+".output3Dy", upLoGrp+".ty" )
        #"loteeth_motion.tranX" --> loTeeth tz
        #cmds.setAttr( loTranPlus+".input3D[2].input3Dz", teethPos[2] )
        cmds.connectAttr( loTranPlus+".output3Dz", upLoGrp+".tz" )
        #rotateZ
        cmds.connectAttr( teethCtl + ".rz", loRotPlus+".input3D[1].input3Dz" )
        cmds.connectAttr( loRotPlus+".output3D", upLoGrp+".r" )      
        
        


#squach setup on tongue later        
def tongueSetup():
    
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
