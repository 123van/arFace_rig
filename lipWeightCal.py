# -*- coding: utf-8 -*-
#path를 찾는 좀 더 정확한 방법?? workspace
# jawClose/mouth cluster weight update할때: calExtraClsWgt()

# headSkel weight 1 / clsVertDict update (2/1/2017)
import maya.mel as mel
import maya.cmds as cmds
def lipWeightCalculate():
    #import the xml weight file and calculate the jaw joint weight
    import xml.etree.ElementTree as ET
    
    path = cmds.workspace(  q=True, dir= True )
    pathProject = path.split('scenes', 1)
    dataPath = pathProject[0]+'data'
    
    headSkinWeight = ET.parse( dataPath + '/headSkin.xml')
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
    #cmds.setAttr( 'headSkin.normalizeWeights', 2 )
    valStr = ''
    jcValStr = ''
    headSkelID = getJointIndex( 'headSkel_jnt' )
    jawCloseID = getJointIndex( 'jawClose_jnt' )
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
            lipYtmp = jntName.replace('RollJot','JotY') 
            lipYJnt = lipYtmp.split('_')[0]
            lipYJntID = getJointIndex(lipYJnt)
            rollJntID = getJointIndex(jntName)
            
            for dict in rootHeadSkin[i]:
                vertNum = int(dict.attrib['index'])
                wgtVal= float(dict.attrib['value'])
                if vertNum in rollVertNum:
                    
                    cmds.setAttr ( 'headSkin.wl['+ str(vertNum) + "].w[" + str(rollJntID)+ "]", ( min(1, rollWgt[vertNum]) * wgtVal) )
            
                if vertNum in lipVertNum:
                    
                    cmds.setAttr ( 'headSkin.wl['+ str(vertNum) + "].w[" + str(lipYJntID) + "]", ( max( lipWgt[vertNum] - rollWgt[vertNum], 0 )* wgtVal) )

    cmds.skinPercent('headSkin', 'head_REN', nrm= 1)
    #cmds.setAttr( 'headSkin.normalizeWeights', 2 )

    
    
    
 # cluster dictionary : 0보다 큰 웨이트값을 가진 버텍스 딕셔너리
def clsVertsDict( obj, cls):

    verts = {}
    for x in range(cmds.polyEvaluate( obj, v = 1)):
        val = cmds.percent( cls, obj+'.vtx[%s]'%x, q =1, v=1 )
        if val[0] > 0.001:
            verts[ x ] = val[0]
    return verts


# cluster list : 0보다 큰 웨이트 값을 가진 클러스터 vertex리스트
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




#조인트의 인덱스 넘버 구하기 integer
def getJointIndex( jntName ):
    connections = cmds.listConnections( jntName + '.worldMatrix[0]', p=1)
    for cnnt in connections:
        if 'headSkin' in cnnt:
            skinJntID = cnnt
    jntID = re.findall ( '\d+', skinJntID )

    return jntID[0]






# dictionary : 조인트의 영향을 받는 vertex 와 weight value 
def selectedInfVerts( obj, jntNum ):
    
    skinCls = mel.eval('findRelatedSkinCluster %s' %obj)
    verts ={}
    for x in range(cmds.polyEvaluate( obj, v = 1)):
        #cmds.getAttr ('headSkin.wl[1362].w[128]') 
        val = cmds.getAttr ('headSkin.wl[x].w[%s]'%jntNum ) 
        if val > 0.0:
            verts[ x ] = val
    
        return verts   
    
    