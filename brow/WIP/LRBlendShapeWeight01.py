#BrowCrv BlendShape mirror Weight
import re
import maya.cmds as cmds
def LRBlendShapeWeight( lipCrv, lipCrvBS ):
    cvs = cmds.ls ( lipCrv+'.cv[*]', fl =1)
    length = len (cvs)
    
    increment = 1.0/(length-1)
    targets = cmds.aliasAttr( lipCrvBS, q=1)
    tNum = len(targets)   
    
    for t in range(0, tNum, 2):
        if targets[t][0] == 'l' :
            indexL=re.findall('\d+', targets[t+1])
            cmds.setAttr ( lipCrvBS + '.inputTarget[0].inputTargetGroup[%s].targetWeights[%s]'%(str(indexL[0]), str(length/2)), .5 ) 
            for i in range(0, length/2):                
                cmds.setAttr ( lipCrvBS + '.inputTarget[0].inputTargetGroup[%s].targetWeights[%s]'%(str(indexL[0]), str(i)), 0 ) 
                cmds.setAttr ( lipCrvBS + '.inputTarget[0].inputTargetGroup[%s].targetWeights[%s]'%(str(indexL[0]), str(length-i-1)), 1 )   
                
        if targets[t][0] == 'r' :
            indexR=re.findall('\d+', targets[t+1])
            cmds.setAttr ( lipCrvBS + '.inputTarget[0].inputTargetGroup[%s].targetWeights[%s]'%(str(indexR[0]), str(length/2)), .5 ) 
            for i in range(0, length/2):                
                cmds.setAttr ( lipCrvBS + '.inputTarget[0].inputTargetGroup[%s].targetWeights[%s]'%(str(indexR[0]), str(i)), 1 ) 
                cmds.setAttr ( lipCrvBS + '.inputTarget[0].inputTargetGroup[%s].targetWeights[%s]'%(str(indexR[0]), str(length-i-1)), 0 )     