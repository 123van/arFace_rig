# -*- coding: utf-8 -*-
import maya.cmds as cmds
"""create browMapMesh"""
def createMapSurf():
    faceGeo = cmds.ls(sl =1, type ='transform')
    #xmin ymin zmin xmax ymax zmax (face bounding box)
    facebbox =  cmds.exactWorldBoundingBox(faceGeo)
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


"""
modeling the browSurfMap for the forhead
create function for browSurfMap polyPlane mirroring 
"""
def browMapSkinning():
    if not "browMapSurf":
        print "create browMapSurf first!!"
    else : browMapSurf = "browMapSurf"
    browJnts = cmds.ls ("*_browP*", type ="joint")
    jntNum = len(browJnts)
    browJnts.sort()
    z = [ browJnts[0] ]
    y = browJnts[1:jntNum/2+1]
    browJnts.reverse()
    x = browJnts[:jntNum/2]
    orderJnts = x + z + y
    orderChildren = cmds.listRelatives(orderJnts, c =1, type = "joint")
    
    edges= cmds.polyEvaluate(browMapSurf, e =1 )
    cmds.polyBevel( browMapSurf +'.e[0:%s]'%(edges-1), offset=0.01 )
    cmds.delete( browMapSurf, constructionHistory =1)
    #edges= cmds.polyEvaluate("browMapSurf", e =1 )
    #cmds.polyBevel( "browMapSurf.e[0:%s]"%(edges-1), com =1, fraction= 0.1, offsetAsFraction= 1, autoFit= 1, segments= 1 )
    faces = []
    for i in range(0, jntNum):
        faces.append("browMapSurf.f[%s]"%str(i))
 
    faceLen = len(faces)
    cmds.select(cl=1)
    
    #get the joints to be bound, check if "headSkel_jnt" exists
    if not cmds.objExists('headSkel_jnt'):
        headSkelPos = cmds.xform('headSkelPos', q =1, ws =1, t =1 )
        cmds.joint(n = 'headSkel_jnt', p = headSkelPos )
    orderChildren.append("headSkel_jnt")
    
    if faceLen == jntNum:        
        skinCls = cmds.skinCluster(orderChildren , browMapSurf, toSelectedBones=1 )
        # 100% skinWeight to headSkel_jnt
        cmds.skinPercent(skinCls[0], browMapSurf, transformValue = ["headSkel_jnt", 1])
        # skinWeight
        for i in range (0, jntNum):
            vtxs = cmds.polyListComponentConversion(faces[i], ff=True, tv=True )
            cmds.skinPercent( skinCls[0], vtxs, transformValue = [ orderChildren[i], 1])
    else:
        print "Number of faces and browJnts are not matching"
        
        
        
        
        
        
#set up the project first!! calculate brow weight based on the clusters ('browUD_cls','browTZ_cls') 
def browWeightCalculate():

    browDict = clsVertsDict( 'head_REN', 'browUD_cls')
    browNum = [i for i in browDict]
    browVert = [ 'head_REN.vtx[%s]'%t for t in browNum ]
    headSkelID = getJointIndex( 'headSkin', 'headSkel_jnt' )
         
    mapVert = []
    for v in range(cmds.polyEvaluate( 'browMapSurf', v = 1)):
        mapVert.append('browMapSurf.vtx[%s]'%v)    
    cmds.select( mapVert, r=1)
    # select target vtx
    cmds.select( browVert, add=1 )    
    cmds.copySkinWeights( sa= 'closestPoint', ia = 'closestJoint', sm=0, noMirror =1 )
    #cmds.copySkinWeights( ss = 'headSkin', ds = 'headSkin', mirrorMode= 'YZ', sa= 'closestPoint', ia = 'closestJoint')    
    
    vtxNum = cmds.polyEvaluate('head_REN', v=1)
    browUDVal= cmds.getAttr( 'browUD_cls.wl[0].w[0:%s]'%(vtxNum-1) )
    browTZVal = cmds.getAttr( 'browTZ_cls.wl[0].w[0:%s]'%(vtxNum-1) )
    headSkinVal = cmds.getAttr( 'headSkin.wl[0:%s].w[%s]'%(vtxNum-1, headSkelID))
    cmds.setAttr( "headSkin.envelope", 0 )
    # set headSkel_jnt weight first
    for bn in browNum:
        browMaxVal = max(browUDVal[bn], browTZVal[bn] ) 
        #make a space for the eyelid weight
        cmds.setAttr('headSkin.wl[%s].w[%s]'%(bn, headSkelID), max( headSkinVal[bn]-browMaxVal, 0))        
    
    browPjnt = cmds.ls('*browP*_jnt', type = 'joint')    
    for p in browPjnt:
        jntPID = getJointIndex( 'headSkin', p )
        browJnt = cmds.listRelatives( p, c=1 )
        jntID = getJointIndex( 'headSkin', browJnt[0])
        browVtx = selectedInfVerts( 'head_REN', jntID )
        browCloseVal = [] 
        for v,w in browVtx.items():
            #vNum = re.findall ( '\d+', v )
            browCloseVal = max(browUDVal[v] - browTZVal[v], 0)
            cmds.setAttr('headSkin.wl[%s].w[%s]'%(v,jntPID), browCloseVal*w )
            cmds.setAttr('headSkin.wl[%s].w[%s]'%(v,jntID), browTZVal[v]*w )
        
    


    

# cluster dictionary : 0보다 큰 웨이트값을 가진 버텍스 딕셔너리
def clsVertsDict( obj, cls):

    verts = {}
    for x in range(cmds.polyEvaluate( obj, v = 1)):
        val = cmds.percent( cls, obj+'.vtx[%s]'%x, q =1, v=1 )
        if val[0] > 0.001:
            verts[ x ] = val[0]
    return verts




# dictionary ={ vertexNum:  weight value } 
def selectedInfVerts( obj, jntNum ):
    
    skinCls = mel.eval('findRelatedSkinCluster %s' %obj)
    verts ={}
    for x in range(cmds.polyEvaluate( obj, v = 1)):
        #cmds.getAttr ('headSkin.wl[1362].w[128]') 
        val = cmds.getAttr ('headSkin.wl[%s].w[%s]'%(x, jntNum) ) 
        if val > 0.0:
            verts[ x ] = val
    
    return verts



import re
def getJointIndex( skinCls, jntName ):
    connections = cmds.listConnections( jntName + '.worldMatrix[0]', p=1)
    skinJntID = ''
    for cnnt in connections:
        if skinCls == cnnt.split('.')[0]:
            skinJntID = cnnt
    jntID = re.findall ( '\d+', skinJntID )

    return jntID[-1]