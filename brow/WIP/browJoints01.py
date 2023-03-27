import maya.cmds as cmds
# brow joints create
'''
UI  : controller size, mult.input 2 values
select left brow vertex points and pivot point. run the script
name = centerBrowBase0l, EyeBrowBase01... '''
def browJoints():    
    sel = cmds.ls( os = True, fl = True)
    verts = sel[:-1]
    GeoName = verts[0].split("vtx", 1)[0]
    browBall = sel[-1]
    browBallPos = cmds.xform( browBall, t = True, q = True, ws = True )
    cmds.select(cl = True)
    index = 0
    posXs = []
    
    #reorder verts list by getting the vertex ?tx value? (from small to big)
    for i in verts:
        vertPos = cmds.xform (i, t = True, q = True, ws = True)
        posX = str(vertPos[0]) + i
        posXs.append(posX)
    
    posXs.sort()
    orderedVerts = []
    name = ''
    for x in posXs:
        y = x.split("vtx", 1)[1]
        name = GeoName + 'vtx' + y
        orderedVerts.append(name)    
    
    cmds.select(cl = True)
    index = 1
    for x in orderedVerts:
        vertPos = cmds.xform(x, t = True, q = True, ws = True)
        
        if ( vertPos[0] <= 0.05):
            
            baseCntJnt = cmds.joint(n = 'c_browBaseJnt' + str(index).zfill(2), p = [ 0, browBallPos[1], browBallPos[2]])
            parentCntJnt = cmds.joint(n = 'c_browPJnt' + str(index).zfill(2), p = vertPos)
            cmds.setAttr ( baseCntJnt+'.rotateOrder', 2)
            cmds.joint(n = 'c_browJnt' + str(index).zfill(2), p = vertPos)
            cmds.select(cl = True)
        else:
    
            baseJnt = cmds.joint(n = 'l_browBaseJnt' + str(index).zfill(2), p = [browBallPos[0], browBallPos[1], browBallPos[2]])
            parentJnt = cmds.joint(n = 'l_browPJnt' + str(index).zfill(2), p = vertPos)
            cmds.setAttr ( baseJnt+'.rotateOrder', 2)
            cmds.joint(n = 'l_browJnt' + str(index).zfill(2), p = vertPos)
            cmds.select(cl = True)
           
            cmds.mirrorJoint ( baseJnt, mirrorYZ= True, mirrorBehavior=1, searchReplace=('l', 'r'))
            cmds.select(cl = True)
            index = index + 1
            
#browJoints()