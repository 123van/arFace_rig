# -*- coding: utf-8 -*-
'''
1.make sure head_REN go back to default shape
1.make sure headSkinObj includes the wide/lidTx joints
'''
import maya.cmds as cmds
import maya.mel as mel
from copyOrigMesh import copyOrigMesh 
from headSkinObj import headSkinObj
def eyeWeightCalculate():
    
    headTemp = copyOrigMesh( 'head_REN' )
    if cmds.listRelatives( headTemp, p=1):
        cmds.parent( headTemp, w=1)
    skin = headSkinObj(headTemp)
    cmds.copySkinWeights( ss = 'headSkin', ds = skin[0], sa= 'closestPoint', ia = 'oneToOne', sm=0, noMirror =1 )
    
    eyeDict = clsVertsDict( 'head_REN', 'eyeWide_cls')
    eyeNum = [i for i in eyeDict]
    eyeVert = [ headTemp + '.vtx[%s]'%t for t in eyeNum ]
    headSkelID = getJointIndex( skin[0], 'headSkel_jnt' )    
    #select eyeSurfMap vertices
    mapVert = []
    for v in range(cmds.polyEvaluate( 'eyeTip_map', v = 1)):
        mapVert.append('eyeTip_map.vtx[%s]'%v)    
    cmds.select( mapVert, r=1)
    #select target(obj+'_default') vertices
    cmds.select( eyeVert, add=1 )    
    cmds.copySkinWeights( sa= 'closestPoint', ia = 'closestJoint', sm=0, noMirror =1 )
    
    vtxNum = cmds.polyEvaluate( 'head_REN', v=1)
    eyeWideVal= cmds.getAttr( 'eyeWide_cls.wl[0].w[0:%s]'%(vtxNum-1) )
    blinkVal = cmds.getAttr( 'eyeBlink_cls.wl[0].w[0:%s]'%(vtxNum-1) )
    headSkinVal = cmds.getAttr( 'headSkin.wl[0:%s].w[%s]'%(vtxNum-1, headSkelID))
    cmds.setAttr( "headSkin.envelope", 0 )
    # set headSkel_jnt weight first
    for num in eyeNum:
        eyeMaxVal = max( eyeWideVal[num], blinkVal[num] )
        #make a space for the eyelid weight
        cmds.setAttr('headSkin.wl[%s].w[%s]'%(num, headSkelID), max( headSkinVal[num]-eyeMaxVal, 0))
    
    eyeScljnt = cmds.ls('l_*Scale*_jnt', type = 'joint')
    for p in eyeScljnt:
        cmds.select(p, r=1)
        childJnt = cmds.ls(dag=1, ap=1, sl=1, type="joint")
        wideJnt = childJnt[-1]
        blinkJnt = childJnt[-2]
        # joint index for headSkin, skin[0] is same
        blinkJntID = getJointIndex( skin[0],blinkJnt )
        wideJntID = getJointIndex( skin[0], wideJnt )
    
        eyeLidVtx = selectedInfVerts( headTemp, blinkJntID ) 
        for v,w in eyeLidVtx.items():
            wideVal = max(eyeWideVal[v] - blinkVal[v], 0)
            cmds.setAttr('headSkin.wl[%s].w[%s]'%(v,wideJntID), wideVal*w )
            cmds.setAttr('headSkin.wl[%s].w[%s]'%(v,blinkJntID), blinkVal[v]*w )            
    
    cmds.setAttr( "headSkin.envelope", 1 )    
    cmds.copySkinWeights( ss = 'headSkin', ds = 'headSkin', mirrorMode= 'YZ', sa= 'closestPoint', ia = 'closestJoint')
    cmds.delete(headTemp)
          


import re
def getJointIndex( skinCls, jntName ):
    connections = cmds.listConnections( jntName + '.worldMatrix[0]', p=1)
    skinJntID = ''
    for cnnt in connections:
        if skinCls == cnnt.split('.')[0]:
            skinJntID = cnnt
    jntID = re.findall ( '\d+', skinJntID )

    return jntID[-1]

    
    
# cluster dictionary : 0보다 큰 웨이트값을 가진 버텍스 딕셔너리
def clsVertsDict( obj, cls):

    verts = {}
    for x in range(cmds.polyEvaluate( obj, v = 1)):
        val = cmds.percent( cls, obj+'.vtx[%s]'%x, q =1, v=1 )
        if val[0] > 0.001:
            verts[ x ] = val[0]
    return verts



# dictionary ={ vertNum:  weight value } 
def selectedInfVerts( obj, jntNum ):
    
    skinCls = mel.eval('findRelatedSkinCluster %s' %obj)
    verts ={}
    for x in range(cmds.polyEvaluate( obj, v = 1)):
        #cmds.getAttr ('headSkin.wl[1362].w[128]') 
        val = cmds.getAttr ( skinCls + '.wl[%s].w[%s]'%(x, jntNum) ) 
        if val > 0.0:
            verts[ x ] = val
    
    return verts
    
    
    

