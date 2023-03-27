import re
import maya.cmds as cmds
def skinWeightToBlendShape( base, myBS, target, targetsLen, jnt):
    #select joint and target geo    
    history= cmds.listHistory( base )
    skinCls = [ x for x in history if cmds.nodeType(x)=="skinCluster"]
    numVert = cmds.polyEvaluate(base, v=1)
    infObj= cmds.skinCluster( skinCls[0],  q= 1, wi = 1 )
    childJnts = cmds.listRelatives( jnt, ad =1, type = "joint")
    for j in childJnts:
        if j in infObj:
            infJnt = j
    vertWeight = 0.0
    weighted = []
    for i in range(0, numVert):
        vert = base + ".vtx[%s]"%str(i)
        vertNum = int(re.search(r'\d+', vert).group())
        vertWeight = cmds.skinPercent(skinCls[0], vert, t = infJnt, q =1 ) 
        
      	cmds.setAttr ( myBS + '.inputTarget[0].inputTargetGroup[%s].targetWeights[%s]'%( str(targetsLen), str(vertNum)), vertWeight ) 