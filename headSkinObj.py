# -*- coding: utf-8 -*-
'''full skinning module for lipMapSkinning (geometrys for skinning need to have "_" in their name)'''
import maya.cmds as cmds
def headSkinObj(geoName):      
    browJnts = cmds.ls('*_browP*_jnt', fl =1, type = 'joint')
    browAllJnt = cmds.listRelatives( browJnts, c =1, type = 'joint') + browJnts    
    eyeWideJnts = cmds.ls('*Wide*_jnt', fl =1, type = 'joint') 
    blinkJnts = cmds.ls('*LidTx*_jnt', fl =1, type = 'joint')    
    lidAllJnt = eyeWideJnts + blinkJnts
    lipJntP = cmds.ls('*LipRollJotP*', fl =1, type = 'transform')
    lipAllJnt = cmds.listRelatives( lipJntP, c =1, type = 'joint')
    faceJnts = cmds.listRelatives('supportRig', ad =1, type = 'joint' ) + ['jawClose_jnt', 'headSkel_jnt']
    skinJnts = browAllJnt + lidAllJnt + lipAllJnt + faceJnts
    name = geoName.split('_')[0]
    skin = cmds.skinCluster ( geoName, skinJnts, tsb =1, n = name + 'Skin' )
    lipYJnt = cmds.ls('*LipJotY*', fl =1, type = 'transform')
    cmds.skinCluster(skin, edit=True, ai=lipYJnt )
    return skin
    
    
  
#select face skinning joints
def headSkinJointList():      
    browJnts = cmds.ls('*_browP*_jnt', fl =1, type = 'joint')
    browAllJnt = cmds.listRelatives( browJnts, c =1, type = 'joint') + browJnts    
    eyeWideJnts = cmds.ls('*Wide*_jnt', fl =1, type = 'joint') 
    blinkJnts = cmds.ls('*LidTx*_jnt', fl =1, type = 'joint')    
    lidAllJnt = eyeWideJnts + blinkJnts
    lipJntP = cmds.ls('*LipRollJotP*', fl =1, type = 'transform')
    lipAllJnt = cmds.listRelatives( lipJntP, c =1, type = 'joint')
    faceJnts = cmds.listRelatives('supportRig', ad =1, type = 'joint' ) + ['jawClose_jnt', 'headSkel_jnt']
    skinJnts = browAllJnt + lidAllJnt + lipAllJnt + faceJnts




#geometrys for skinning need to have "_" in their name 
def skinningObj(geoName):

    skinJnts = headSkinJointList()
    name = geoName.split('_')[0]
    skin = cmds.skinCluster ( geoName, skinJnts, tsb =1, n = name + 'TempSkin' ) 
    lipYJnt = cmds.ls('*LipJotY*', fl =1, type = 'transform')  
    cmds.skinCluster(skin, edit=True, ai=lipYJnt ) 
    return skin
