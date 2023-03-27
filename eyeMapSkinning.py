# -*- coding: utf-8 -*-
'''
skin the map surface start where the 
'''
import maya.cmds as cmds
def eyeMapSkinning():
    
    surf = 'eyeWeight_map'
    if not cmds.objExists(surf):
        print "create eye surface map first!!"
        
    else:
        cvs = cmds.ls( 'eyeloftCurve01.cv[*]', fl =1)
        cvLen = len(cvs)
        jnts = cmds.ls('l_*LidTx*_jnt', fl =1, type = 'joint')  
        jntLen = len(jnts)
        if not cvLen == jntLen:
            print 'the number of mouth joints is different to the cvs'
        else: 
            loftCrvs = cmds.ls( 'eyeloftCurve*', fl =1, type = 'transform')
            crvLen = len(loftCrvs)
            # ordered Joints for skin
            uplipJntP = cmds.ls('l_upLidTx*_jnt', fl =1, type = 'joint' )
            lolipJntP = cmds.ls('l_loLidTx*_jnt', fl =1, type = 'joint' )
            lolipJntP.reverse()
            
            uplipJntP.insert(0, 'l_innerLidTxTX_jnt')
            lolipJntP.insert(0, 'l_outerLidTxTX_jnt')
            orderJnt = uplipJntP + lolipJntP
            jntNum = len(orderJnt)
            vrtPerJnt = cvLen*crvLen/jntNum
            
            headSkinObj(surf)
            index = 0       
            for x in range(0, cvLen*crvLen, vrtPerJnt):        
                for y in range( x, x + vrtPerJnt ):
                    cmds.skinPercent( surf.split('_')[0] + 'Skin', surf +'.vtx[%s]'%str(y), tv = ( orderJnt[index], 1))
                index +=1 