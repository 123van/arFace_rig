# -*- coding: utf-8 -*-
'''__init__? ??? ??? ? ????? ?????.
from folder import file
reload(file)
file.zeroOutCluster()
'''

import maya.cmds as cmds
import os
import faceCompFunction
reload(faceCompFunction)

def faceCompositionUI():

    #check to see if window exists
    if cmds.window ('faceCompositionUI', exists = True):
        cmds.deleteUI( 'faceCompositionUI')

    #create window
    window = cmds.window( 'faceCompositionUI', title = 'faceComposition UI', w =400, h =900, mnb = True, mxb = True, sizeable=True, resizeToFitChildren = True )

    #main layout
    mainLayout = cmds.columnLayout( w =420, h=600)

    #rowColumnLayout
    cmds.rowColumnLayout( numberOfColumns = 3, columnWidth = [(1, 140),(2, 120),(3, 120)], columnOffset = [(1, 'right', 10)] )
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.separator( h = 15)

    '''import sys
    sys.path.append('c:/Users/sshin/Documents/maya/2016/scripts/twitchScript')'''
    
    cmds.text( label = 'mark vertex')
    cmds.button( label = 'mark verts', command = markVertex )
    cmds.button( label = 'remove vertMark', command = removeVertMark )
    cmds.separator( h = 15)    
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    
    cmds.text( label = '')
    cmds.text( label = 'select corner verts') 
    cmds.text( label = '/ direction vert on loop')
    cmds.text( label = 'Up/Low Verts')
    cmds.optionMenu('eye_lip', changeCommand=printNewMenuItem )
    cmds.menuItem( label='eye' )
    cmds.menuItem( label='lip' )
    cmds.button( label = 'orderedVerts', command = orderedUpLoVert )
    cmds.text( label = 'Select:')
    cmds.button( label = 'up Verts', command = upVertSel )
    cmds.button( label = 'low Verts', command = lowVertSel )
    cmds.separator( h = 15)    
    cmds.separator( h = 15)
    cmds.separator( h = 15)

    cmds.separator( h = 15)  
    cmds.text( label = 'select vertices')
    cmds.text( label = 'in order')
    cmds.text( label = 'brow Curve:')
    cmds.button( label = 'browMapCurve', command = browMapCurve )
    cmds.text( label = '')    
    cmds.separator( h = 15)    
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    
    cmds.separator( h = 15)  
    cmds.text( label = 'select 2verts!!!')
    cmds.text( label = 'corner/vector 2 verts')
    cmds.text( label = 'Eye/Lip Curve:')
    cmds.optionMenu('facePart', changeCommand=printNewMenuItem )
    cmds.menuItem( label='eye' )
    cmds.menuItem( label='lip' )
    cmds.button( label = 'curve Loop', command = curveOnLoop )

    cmds.separator( h = 15) 
    cmds.text( label = 'cornerVerts/vector') 
    cmds.text( label = 'select a lip curve')
    cmds.text( label = '')    
    cmds.button( label = 'curves loop', command = curvesOnLoop ) 
    cmds.button( label = 'symmetyLipCrv', command = symmetrizeLipCrv )
    
    cmds.text( label = 'manual curve') 
    cmds.text( label = 'manually select edges')
    cmds.text( label = 'corner/vector 2 verts')   
    cmds.button( label = 'edgeSelection', command = edgeSelection ) 
    cmds.button( label = 'curveOnEdgeSel', command = curveOnEdgeSelection )
    cmds.separator( h = 15)    
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.separator( h = 15)    
    cmds.text( label = 'select curves')
    cmds.text( label = 'in order')  
    cmds.text( label = 'MapSurface:' )
    cmds.button( label = 'loftFacePart', command = loftFacePart )
    cmds.text( label = '')
    cmds.separator( h = 15)    
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    
    cmds.text( label = 'browWide:' )
    cmds.button( label = 'browWideJnt', command = browWideJnt )
    cmds.text( label = '')    

    cmds.text( label = 'browFactor:')
    if cmds.objExists("browFactor"):
        jawCoseSxField = cmds.intField( value = cmds.getAttr('browFactor.browUp_scale'))
        jawCoseSzField = cmds.intField( value = cmds.getAttr('browFactor.browRotateY_scale'))
    else: 
        cmds.text( label = '')
        cmds.text( label = '')         

    cmds.button( label = 'browSurfMapSkin', command = browMapSkin )
    cmds.text( label = '')    
    cmds.text( label = 'LipMapSurface:')
    cmds.button( label = 'lipSurfMapSkin', command = lipMapSkinning  )
    cmds.text( label = '')
    cmds.text( label = 'eyeMapSurface:')
    cmds.button( label = 'eyeSurfMapSkin', command = eyeMapSkin  )
    cmds.text( label = '')
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    
    cmds.text( label = 'zero out')
    cmds.button( label = 'createPntNull', command = createPntNull  )
    cmds.text( label = '')
    
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    
    cmds.text( label = 'radius:')
    cmds.text( label = 'controller Shape')
    cmds.text( label = 'select "rotate pivot"!')
    radiusField = cmds.floatField( "radius", minValue=0.01, maxValue=10, value=1.0 )
    cmds.optionMenu("ctlShape", changeCommand=printNewMenuItem )
    cmds.menuItem( label='circle' )
    cmds.menuItem( label='square' )
    cmds.button( label = 'controller', command = controller )
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    
    cmds.text( label = 'multi input:')
    cmds.text( label = 'select source ctrls')
    cmds.text( label = "then select target")
    cmds.text( label = 'attribute')
    cmds.optionMenu('tform', changeCommand=printNewMenuItem )
    cmds.menuItem( label='translate' )
    cmds.menuItem( label='rotate' )
    cmds.menuItem( label='scale' )
    cmds.button( label = 'multi ctrls connect', command = multiInputConnect )
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.text( label = 'sel nd with connections')
    cmds.text( label = 'and new node')  
    cmds.button( label = 'transfer connections', command = replaceConnection )    
    
    cmds.showWindow(window)

  
def markVertex( *pArgs ):
    vtxSel = cmds.ls(sl=1, fl=1)
    cmds.polyColorPerVertex(vtxSel, r=1, g=0.3, b=0.3, a=1, cdo=1 )

def removeVertMark( *pArgs ):
    faceCompFunction.removeVertMark()
    
def orderedUpLoVert( *pArgs ):
    currentName = cmds.optionMenu('eye_lip', query=True, value=True)
    faceCompFunction.orderedVert_upLo(currentName)

def upVertSel( *pArgs ):
    eyeLip = cmds.optionMenu('eye_lip', query=True, value=True)
    faceCompFunction.upVertSel( eyeLip )

def lowVertSel( *pArgs ):
    eyeLip = cmds.optionMenu('eye_lip', query=True, value=True)
    faceCompFunction.loVertSel( eyeLip )

def browMapCurve(*pArgs ):
    faceCompFunction.browMapCurve():
    
def curveOnLoop( facePart, *pArgs ):
    currentValue = cmds.optionMenu('facePart', query=True, value=True)
    faceCompFunction.curveOnEdgeLoop(currentValue)

def edgeSelection( facePart, *pArgs ):
    currentValue = cmds.optionMenu('facePart', query=True, value=True)
    faceCompFunction.edgeSelection(currentValue)
    
def curveOnEdgeSelection( facePart, *pArgs ):
    currentValue = cmds.optionMenu('facePart', query=True, value=True)
    faceCompFunction.curveOnEdgeSelection(currentValue)
    
def curvesOnLoop( *pArgs ):
    currentValue = cmds.optionMenu('facePart', query=True, value=True)
    faceCompFunction.seriesOfEdgeLoopCrv(currentValue)

def symmetrizeLipCrv( *pArgs ):
    faceCompFunction.symmetrizeLipCrv()
    
def loftFacePart( *pArgs ):
    currentValue = cmds.optionMenu('facePart', query=True, value=True)
    faceCompFunction.loftFacePart( currentValue )   

def browWideJnt(*pArgs):
    faceCompFunction.browWideJnt()        
    
def browMapSurf(*pArgs):
    faceCompFunction.createMapSurf() 

def browMapSkin( *pArgs ):
    faceCompFunction.browMapSkinning()

def lipMapSkinning( *pArgs ):
    currentValue = cmds.optionMenu('facePart', query=True, value=True)
    faceCompFunction.lipMapSkinning() 
    
def eyeMapSkin(*pArgs):
    faceCompFunction.eyeMapSkinning() 

def createPntNull(*pArgs):
    faceCompFunction.createPntNull() 

def controller(*pArgs):
    shapeValue = cmds.optionMenu('ctlShape', query=True, value=True)
    radius = cmds.floatField("radius", q=1, v=1 )
    faceCompFunction.controller( radius, shapeValue ) 

def multiInputConnect(*pArgs):
    currentValue = cmds.optionMenu('tform', query=True, value=True)
    faceCompFunction.multiInputConnect(currentValue)

def replaceConnection(*pArgs):
    faceCompFunction.replaceConnection()
    
    
def printNewMenuItem( item ):
    print item