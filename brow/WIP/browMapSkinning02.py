"""
use:
1. run createMapSurf() : create polyPlane as "browMapSurf" based on the number of brow joints
2. modeling the browSurfMap for the forhead : completely cover brow and eyelid area
WIP!! Jon to create function for browSurfMap polyPlane mirroring 
3. run browMapSkinning() : bevel the mapSurf geo / skinning / weight 100% for each brow joint
4. ngSkinTools "Initialize Skinning layers" on browSurfMap
5. select browSurfMap and head geo / run "copySkinLayers" (download from creativeCrash) to copy skinWeight
6. smooth the brow layer / paint layer mask 
7. export browJnts weight as jason file for the blendShape
8. layer mask fine tuning
"""




import maya.cmds as cmds
"""create browMapMesh"""
def createMapSurf():
    facebbox = cmds.xform ("head_REN", q =1, boundingBox =1 )
    tranX = cmds.xform ("lEarPos", q =1, ws =1, t=1 )
    sizeX = tranX[0]*2
    bboxSizeY = facebbox[4] - facebbox[1]
    JntLen = len (cmds.ls("*_browBaseJnt*", type = "joint"))
    browMapSurf = cmds.polyPlane(n= "browMapSurf", w = sizeX, h =bboxSizeY/2, subdivisionsX = browJntLen, subdivisionsY = 3 )
    cmds.xform( browMapSurf, p = 1, rp =(0, 0, bboxSizeY/4))
    
    #place the mapSurf at the upper part of the face
    cmds.setAttr ( browMapSurf[0] + ".rotateX", 90 )
    cmds.xform (browMapSurf[0], ws =1, t = (0, facebbox[1] + bboxSizeY/2, 0))
    
    #move down the 2nd low of edges
    browCtls = cmds.ls("*_brow*_ctl", type = "transform")
    tranY = cmds.xform (browCtls[-1], q =1, ws =1, t=1 )
    cmds.select( browMapSurf[0] + ".vtx[%s:%s]"%(browJntLen+1, browJntLen*2 +1))
    verts = cmds.ls(sl=1, fl =1)
    for v in verts:
        vPos = cmds.xform(v, q =1, ws =1, t=1 )
        cmds.xform (v, ws =1, t = ( vPos[0], tranY[1], vPos[2] ))
        cmds.select ( cl =1 ) 
#createMapSurf()



'''if not working, check below
1. "browMapSurf" exist or name check
2. brow joint name "*browBaseJnt*"
3. "headSkel_jnt" exist
 '''
def browMapSkinning( ):
    if not "browMapSurf":
        print "create browMapSurf first!!"
    else : browMapSurf = "browMapSurf"
    browJnts = cmds.ls ("*browBaseJnt*", type ="joint")
    JntLen = len(browJnts)
    browJnts.sort()
    z = [ browJnts[0] ]
    y = browJnts[1:JntLen/2+1]
    browJnts.reverse()
    x = browJnts[:JntLen/2]
    orderJnts = x + z + y
    orderChildren = cmds.listRelatives (cmds.listRelatives(orderJnts, c =1, type = "joint"), c=1, type="joint")
    
    edges= cmds.polyEvaluate(browMapSurf, e =1 )
    cmds.polyBevel( browMapSurf +'.e[0:%s]'%(edges-1), offset=0.01 )
    cmds.delete( browMapSurf, constructionHistory =1)
    #edges= cmds.polyEvaluate("browMapSurf", e =1 )
    #cmds.polyBevel( "browMapSurf.e[0:%s]"%(edges-1), com =1, fraction= 0.1, offsetAsFraction= 1, autoFit= 1, segments= 1 )
    faces = []
    for i in range(0, JntLen-1):
        face = browMapSurf+ ".f[%s]"%(4+2*i)
        faces.append(face)
    faces.append(browMapSurf+ ".f[%s]"%(3+2*(JntLen-1)))    
    faceLen = len(faces)
    
    #get the joints to be bound, check if "headSkel_jnt" exists
    joints = cmds.ls("*_browJnt*", fl =1, type = "joint")
    if "headSkel_jnt":
        joints.append("headSkel_jnt")
    
    #skin the map geo    
    skin = cmds.ls( cmds.listHistory(browMapSurf ), type ="skinCluster" )
    if not skin:
        skinCls = cmds.skinCluster(joints , browMapSurf, toSelectedBones=1 )
    # 100% skinWeight to headSkel_jnt
    cmds.skinPercent(skinCls[0], browMapSurf, transformValue = ["headSkel_jnt", 1])
    # skinWeight
    for i in range (0, faceLen):
        vtxs = cmds.polyListComponentConversion(faces[i], ff=True, tv=True )
        #cmds.select(vtxs, r=1)
        cmds.skinPercent( skinCls[0], vtxs, transformValue = [ orderChildren[i], 1])