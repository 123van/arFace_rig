# -*- coding: utf-8 -*-
# new default name will be obj+"_default"( )
import maya.cmds as cmds
def copyOrigMesh( obj ):
    
    shapes = cmds.listRelatives( obj, ad=1, type='shape' )
    origShape = [ t for t in shapes if 'Orig' in t ]
    #get the orig shapes with history and delete the ones with with same name.
    myOrig = ''
    for orig in origShape:
        if cmds.listHistory( orig, f=1 ):
            myOrig = orig
        else: cmds.delete(orig)
    
    #unique origShape duplicated
    headTemp = cmds.duplicate ( myOrig, n = myOrig.replace('ShapeOrig', '_default'), renameChildren =1 )
    tempShape = cmds.listRelatives( headTemp[0], ad=1, type ='shape' )
    num = 0
    for ts in tempShape:
        if 'ShapeOrig' in ts:
            tempOrig = cmds.rename( ts, ts.replace('ShapeOrig', '_defaultShape') )
        else: cmds.delete(ts)
        
    cmds.setAttr( tempOrig+".intermediateObject", 0)
    cmds.sets ( tempOrig, e=1, forceElement = 'initialShadingGroup' )
    return headTemp[0]