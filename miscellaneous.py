# -*- coding: utf-8 -*-

import maya.cmds as cmds
import os
from twitchScript import faceCompFunction
from twitchScript import faceSkinFunction
from twitchScript import twitchPanelConnect
from twitchScript import blendShapeMethods
def miscellaneousUI():

    #check to see if window exists
    if cmds.window ('miscellaneousUI', exists = True):
        cmds.deleteUI( 'miscellaneousUI')

    #create window
    window = cmds.window( 'miscellaneousUI', title = 'miscellaneous UI', w =400, h =800, mnb = True, mxb = True, sizeable=True, resizeToFitChildren = True )

    #main layout
    mainLayout = cmds.columnLayout( w =420, h=800)
    
    #rowColumnLayout
    cmds.rowColumnLayout( numberOfColumns = 4, columnWidth = [(1, 100),(2, 120),(3, 120), (4, 60) ], columnOffset = [(1, 'right', 10)] )
    spaceBetween(2,4)#2: row 4: column
    cmds.text( label = '')
    cmds.text( label = 'Michelleneous', bgc = [.12,.2,.30], fn = "boldLabelFont",height= 20 )
    cmds.text( label = '')
    cmds.text( label = '')
    
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.text( label = '')
    spaceBetween(1,4)

    cmds.text( label = '')
    cmds.text( label = 'merge arFace to body')
    cmds.text( label = 'selec a pairs( geo or grp )')
    cmds.text( label = '')
    
    cmds.text( label = '')
    cmds.button( label = 'blendHead_toBody', bgc=[.42,.5,.60], command = blendShapeHead_toBody )     
    cmds.text( label = '')
    cmds.button( label = '?', command = blendHead_toBody_helpImage )
    spaceBetween(1,4)
    
    cmds.text( label = '')
    cmds.button( label = 'create Parent Null', bgc=[.42,.5,.60], command = createPntNull )     
    cmds.button( label = 'transfer cluster WN', bgc=[.42,.5,.60], command = changeClsWeightNode ) 
    cmds.text( label = '')
    
    spaceBetween(1,4)
       
    cmds.text( label = '  replace node   ', bgc = [.10,.4,.40], height= 20 )
    cmds.text( label = 'select item to Replace', bgc = [.10,.4,.40] )
    cmds.text( label = 'in:source / out:destine', bgc = [.10,.4,.40] )
    cmds.text( label = '')
    
    cmds.text( label = '')
    cmds.optionMenu('node_shape', changeCommand=printNewMenuItem )
    cmds.menuItem( label='node' )
    cmds.menuItem( label='shape' )
    cmds.optionMenu('in_out', changeCommand=printNewMenuItem )
    cmds.menuItem( label='in' )
    cmds.menuItem( label='out' )
    cmds.text( label = '')
    
    cmds.text( label = '')
    cmds.text( label = '    select node with connect' )
    cmds.text( label = 'tions and new node         ' )
    cmds.text( label = '')

    cmds.text( label = '')    
    cmds.button( label = 'transfer connections', bgc=[.42,.5,.60], command = transferConnections )
    cmds.button( label = 'faceCtlRotate_toBody', bgc=[.42,.5,.60], command = faceCtlRotate_toBody )
    cmds.button( label = '?', command = faceCtlRotate_toBody_helpImage )
 
   
    cmds.separator( h = 15) 
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.text( label = '')
    
    cmds.text( label = '')   
    cmds.text( label = 'select newCtl / oldCtl' )
    cmds.text( label = '' )
    cmds.text( label = '' )
    
    cmds.text( label = '')
    cmds.button( label = 'controller shape swap', bgc=[.42,.5,.60], command = ctlShapeTransfer )    
    cmds.button( label = 'dgTimer', bgc=[.42,.5,.60], command = dgTimer  )
    cmds.text( label = '')

    cmds.text( label = '')
    cmds.button( label = 'renameDuplicates', bgc=[.42,.5,.60], command = renameDuplicates )
    cmds.button( label = 'renameCrvShape', bgc=[.42,.5,.60], command = renameCrvShape )
    spaceBetween(1,2)
    cmds.button( label = 'delete plugins', bgc=[.42,.5,.60], command = deleteUnknown_plugins )
    spaceBetween(1,2)
    spaceBetween(1,4)
    
    cmds.text( label = '         select   ', bgc = [.10,.4,.40], height= 20)
    cmds.text( label = 'geo(crv) and ctl parents', bgc = [.10,.4,.40], height= 20)
    cmds.text( label = ' select top group for ctls')
    cmds.text( label = '')
    
    cmds.text( label = '')
    cmds.button( label = 'stick ctl to skin', bgc=[.42,.5,.60], command = stickCtlToFace )
    cmds.button( label = 'compensate stickyCtl', bgc=[.42,.5,.60], command = compensateStickyCtl )  
    cmds.text( label = '')
    
    spaceBetween(1,4)
        
    cmds.text( label = 'multi input:', bgc = [.10,.4,.40], height= 20)
    cmds.text( label = 'select source ctrls', bgc = [.10,.4,.40], height= 20 )
    cmds.text( label = "then select target", bgc = [.10,.4,.40], height= 20)
    cmds.text( label = '')
    
    cmds.text( label = 'attribute')
    cmds.optionMenu('tform', changeCommand=printNewMenuItem )
    cmds.menuItem( label='translate' )
    cmds.menuItem( label='rotate' )
    cmds.menuItem( label='scale' )
    cmds.button( label = 'multi ctrls connect', bgc=[.42,.5,.60], command = multiInputConnect )
    cmds.text( label = '')
    
    spaceBetween(1,4)
    cmds.text( label = ' ' )
    cmds.text( label = 'copy cluster/BS wgt' )
    cmds.text( label = "to other cluster/BS")
    cmds.text( label = '')
    
    cmds.text( label = '')
    cmds.button( label = 'copy weight', bgc=[.42,.5,.60], command = copyWeight )
    cmds.button( label = 'paste weight', bgc=[.42,.5,.60], command = pasteWeight )
    cmds.text( label = '')
    spaceBetween(1,4)

    cmds.text( label = ' ' )
    cmds.text( label = 'when final rig is done', bgc = [.10,.4,.40], height= 20 )
    cmds.text( label = ' ')
    cmds.text( label = ' ')
    
    cmds.text( label = ' deform layer ')
    cmds.optionMenu('dFormLayer', changeCommand=printNewMenuItem )
    cmds.menuItem( label='cluster' )
    cmds.menuItem( label='blendShape' )
    cmds.menuItem( label='squach' )
    cmds.menuItem( label='all' )    
    cmds.button( label = 'cleanUp faceMain', bgc=[.42,.5,.60], command = cleanUp_faceMain )
    cmds.text( label = ' ')
    
    cmds.text( label = ' ')
    cmds.text( label = 'fix the clusters weight' )
    cmds.text( label = '/create headSkin.xml first' )
    cmds.text( label = ' ')
    
    cmds.text( label = 'fix skin weight')
    cmds.button( label = 'copy browSkinWeight', bgc=[.42,.5,.60], command = copyBrowSkinWeight )
    cmds.button( label = 'copy eyelidSkinWeight', bgc=[.42,.5,.60], command = copyEyelidSkinWeight )
    cmds.text( label = '')
    spaceBetween(1,4)
    
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.text( label = '')
    
    cmds.text( label = '')
    cmds.text( label = 're-assign shaders', bgc = [.12,.2,.30], fn = "boldLabelFont",height= 20 )
    cmds.text( label = '')
    cmds.text( label = '')
    spaceBetween(1,4)

    cmds.text( label = ' ' )
    cmds.text( label = 'shadingHelp_grp created' )
    cmds.text( label = 'select "shadingHelp_grp"', bgc = [.10,.4,.40], height= 20)
    cmds.text( label = '')
    
    cmds.text( label = '')
    cmds.button( label = 'store shadingSets', bgc=[.42,.5,.60], command = storeShadingSets )
    cmds.button( label = 'assign objs to shaders', bgc=[.42,.5,.60], command = assignShadingSets )
    cmds.text( label = '')
    spaceBetween(1,4)
    
    cmds.text( label = ' ' )
    cmds.text( label = '      select ctls in order')
    cmds.text( label = '(selection order on)       ' )
    cmds.text( label = ' ' )
    cmds.text( label = ' ' )
    cmds.optionMenu('direction', changeCommand=printNewMenuItem )
    cmds.menuItem( label='UD' )
    cmds.menuItem( label='LR' )
    cmds.button( label = 'pickWalk_setup', bgc=[.42,.5,.60], command = pickWalk_setup )
    cmds.text( label = '')    

    
    cmds.showWindow(window)


def arHelpImage( imageTitle ):   

    if cmds.window( "arFace_helpImage", q =1, ex =1 ):
        cmds.deleteUI("arFace_helpImage" )

    arWindow = cmds.window( title="arFace_helpImage", iconName='helpImage', widthHeight=(400, 550) )
    cmds.paneLayout()
    cmds.image( image='C:/Users/SW/OneDrive/Documents/maya/2018/scripts/twitchScript/arFaceImage/%s.png'%imageTitle )
    #cmds.setParent( '..' )
    cmds.showWindow( arWindow )

def blendHead_toBody_helpImage( *pArgs ):
    arHelpImage( "blendHeadToBody02" )

def faceCtlRotate_toBody_helpImage( *pArgs ):
    arHelpImage( "faceCtlRotate_toBody" )

def spaceBetween( numOfRow, numOfColm ):
    for x in range( numOfRow ):
        for i in range(numOfColm):
            cmds.text( l = '')

def blendShapeHead_toBody(*pArgs):
    blendShapeMethods.blendShapeHead_toBody()

def changeClsWeightNode(*pArgs):
    faceCompFunction.changeClsWeightNode() 


def createPntNull(*pArgs):
    mySelList = cmds.ls( sl=1, typ = "transform" )
    faceCompFunction.createPntNull( mySelList )  
    
def multiInputConnect(*pArgs):
    currentValue = cmds.optionMenu('tform', query=True, value=True)
    faceCompFunction.multiInputConnect(currentValue)


def transferConnections(*pArgs):
    node_shape = cmds.optionMenu('node_shape', query=True, value=True)
    in_out = cmds.optionMenu('in_out', query=True, value=True)
    twitchPanelConnect.transferConnections( node_shape, in_out )

def faceCtlRotate_toBody(*pArgs):
    faceCompFunction.faceCtlRotate_toBody()
    
#no translate freeze. swap in world space
def ctlShapeTransfer( *pArgs ):
    faceCompFunction.ctlShapeTransfer()
    
    
def dgTimer(*pArgs):
    faceCompFunction.dgTimer()    

def renameDuplicates(*pArgs):
    faceCompFunction.renameDuplicates()

def renameCrvShape(*pArgs):
    crvs = cmds.ls(sl=1, typ = "transform" )
    faceCompFunction.renameCrvShape(crvs)
    
def deleteUnknown_plugins(*pArgs):
    faceCompFunction.deleteUnknown_plugins()
    
#select geo and ctls
def stickCtlToFace( *pArgs ):
    sel = cmds.ls( sl=1 )
    obj = sel[0]
    ctls = sel[1:]
    faceCompFunction.stickCtlToFace( obj, ctls )

#select ctl group node
def compensateStickyCtl(*pArgs):    
    grp = cmds.ls( sl=1, typ = "transform" )[0]
    faceCompFunction.compensateStickyCtl( grp )  

def multiInputConnect(*pArgs):
    currentValue = cmds.optionMenu('tform', query=True, value=True)
    faceCompFunction.multiInputConnect(currentValue)

def copyWeight(*pArgs):
    from twitchScript import transferWeight
    reload(transferWeight)
    mySel = cmds.ls(sl=1, typ= 'transform')
    if mySel:
        geo = mySel[0]
        transferWeight.copyWeightUI(geo)
    else:
        cmds.confirmDialog( title='Confirm', message=' select geo with deformer' )

def pasteWeight(*pArgs):
    from twitchScript import transferWeight
    reload(transferWeight)
    mySel = cmds.ls(sl=1, typ= 'transform')
    if mySel:
        geo = mySel[0]
        transferWeight.pasteWeightUI(geo)
    else:
        cmds.confirmDialog( title='Confirm', message=' select geo with deformer' )


def cleanUp_faceMain(*pArgs):
    currentLayer = cmds.optionMenu('dFormLayer', query=True, value=True)
    faceCompFunction.cleanUp_faceMain(currentLayer)


def storeShadingSets(*pArgs):
    faceCompFunction.storeShadingSets()

def assignShadingSets(*pArgs):
    shadingHelpGrp = cmds.ls(sl=1, typ = 'transform')
    if shadingHelpGrp:
        faceCompFunction.assignShadingSets(shadingHelpGrp[0])
    else:
        cmds.confirmDialog( title='Confirm', message=' select shadingHelp_grp ' )

#select ctls in order(selection order on)
def pickWalk_setup(ctls):
    
    direction = cmds.optionMenu('direction', query=True, value=True)
    ctls = cmds.ls(os=1)
    if direction == "UD":
        for c in ctls:
            tag = cmds.listConnections(c, t = 'controller')
            if not tag:
                cmds.controller( c )
                
        for i in range(len(ctls)-1):
            frstTag = cmds.listConnections(ctls[i], t = 'controller')[0] 
            sndTag = cmds.listConnections(ctls[i+1], t = 'controller')[0]
            #connect frstTag.parent to sndTag.children[0] 
            cmds.connectAttr( frstTag + '.parent', sndTag + '.children[0]')
            
        fristTag = cmds.listConnections(ctls[0], t = 'controller')[0]
        cmds.connectAttr( sndTag + '.parent', fristTag + '.children[0]' )
    
    elif direction == "LR":
        cmds.controller( ctls, group = 1 )

def copyBrowSkinWeight(*pArgs):
    faceSkinFunction.ArFace_copyBrowSkinWeight()
    
def copyEyelidSkinWeight(*pArgs):
    faceSkinFunction.ArFace_copyEyeLidSkinWeight()
    
def printNewMenuItem( item ):
    print item

