# -*- coding: utf-8 -*-

import maya.cmds as cmds
import os
import faceCompFunction
reload(faceCompFunction)
import twitchPanelConnect
reload(twitchPanelConnect)

def faceControlsUI():

    #check to see if window exists
    if cmds.window ('faceControlsUI', exists = True):
        cmds.deleteUI( 'faceControlsUI')

    #create window
    window = cmds.window( 'faceControlsUI', title = 'faceControls UI', w =400, h =900, mnb = True, mxb = True, sizeable=True, resizeToFitChildren = True )

    #main layout
    mainLayout = cmds.columnLayout( w =420, h=600)
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    #rowColumnLayout
    cmds.rowColumnLayout( numberOfColumns = 3, columnWidth = [(1, 140),(2, 120),(3, 120)], columnOffset = [(1, 'right', 10)] )
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.separator( h = 15)

    cmds.text( label = '')
    cmds.text( label = 'faceControls', bgc = [.12,.2,.30], fn = "boldLabelFont",height= 20 )
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = 'select Ctl Groups ')
    cmds.text( label = '')
    cmds.text( label = 'store ctl groups ', fn = "boldLabelFont" )
    cmds.button( label = 'browCtl list', bgc=[.42,.5,.60], command = browCtlGrp )
    cmds.button( label = 'eyeCtl list', bgc=[.42,.5,.60], command = eyeCtlGrp )
    cmds.text( label = 'and ctl list', fn = "boldLabelFont")
    cmds.button( label = 'mouthCtl list', bgc=[.42,.5,.60], command = mouthCtlGrp )
    cmds.button( label = 'bridgeCtl list', bgc=[.42,.5,.60], command = bridgeCtlGrp )
    cmds.text( label = '')
    cmds.button( label = 'detailCtl list', bgc=[.42,.5,.60], command = detailCtlGrp )
    cmds.text( label = '')
    
    spaceBetween(1,3)
    
    cmds.text( label = 'arFace shortcut :', fn = "boldLabelFont" )
    cmds.button( label = 'arFace ctl list', bgc=[.42,.5,.60], command = arFace_ctlList )
    cmds.text( label = ' hard code for arFace ctls')
    cmds.text( label = '')
    cmds.text( label = '')    
    cmds.text( label = '')    
    cmds.text( label = '')
    cmds.button( label = 'all/main ctlList', bgc=[.42,.5,.60], command = all_main_detailCtls )
    cmds.text( label = '')
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.text( label = '')
    cmds.text( label = 'level ctl', fn = "boldLabelFont")
    cmds.text( label = 'region ctl', fn = "boldLabelFont")
    cmds.text( label = '')
    cmds.optionMenu('face_level', changeCommand= printNewMenuItem )
    cmds.menuItem( label= 'mainCtl' )
    cmds.menuItem( label= 'detailCtl')
    cmds.menuItem( label= 'allCtl')

    cmds.optionMenu('face_region', changeCommand= printNewMenuItem )
    cmds.menuItem( label= 'browCtl' )
    cmds.menuItem( label= 'eyeCtl')
    cmds.menuItem( label= 'mouthCtl')
    cmds.menuItem( label= 'bridgeCtl')
    cmds.text( label = '')
    cmds.button( label = 'select ctl', bgc=[.42,.5,.60], command = select_mCtl )
    cmds.button( label = 'select ctl', bgc=[.42,.5,.60], command = select_ctl )
    cmds.text( label = '')
    cmds.button( label = 'reset ctl', bgc=[.42,.5,.60], command = reset_mCtl )
    cmds.button( label = 'reset ctl', bgc=[.42,.5,.60], command = reset_ctl )
    cmds.text( label = '')
    cmds.button( label = 'set keys', bgc=[.42,.5,.60], command = setKeysOnMCtl )
    cmds.button( label = 'set keys', bgc=[.42,.5,.60], command = setKeysOnCtl )
    cmds.text( label = '')
    cmds.button( label = 'delete CtrlKeys', bgc=[.42,.5,.60], command = deleteMCtlKeys )
    cmds.button( label = 'delete CtrlKeys', bgc=[.42,.5,.60], command = deleteCtrlKeys )
    spaceBetween(1,3)
    cmds.text( label = '')
    cmds.button( label = 'add items To LevelArray', bgc=[.42,.5,.60], command = addItemToLevelArray )
    cmds.button( label = 'add new item To Region', bgc=[.42,.5,.60], command = addItemToRegionArray )
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.separator( h = 15)  
    cmds.text( label = '  !! set both "LEVEL', fn = "boldLabelFont")   
    cmds.text( label = '  select ctls to add ', fn = "boldLabelFont" )
    cmds.text( label = '    ' )   
    
    cmds.text( label = '/REGION ctl"!!       ',fn = "boldLabelFont")
    cmds.button( label = 'add items to exist-sets', bgc=[.42,.5,.60], command = addItems_set   )
    cmds.button( label = 'remove items from sets', bgc=[.42,.5,.60], command = removeItems_set   )
    spaceBetween(1,3)
    cmds.text( label = '')
    cmds.text( label = 'Ctl_list to Ctl_set   ( ', fn = "boldLabelFont")    
    cmds.text( label = 'browCtl_set, eyeCtl_set...)')
    cmds.text( label = '')
    cmds.button( label = 'create ctlSets', bgc=[.42,.5,.60], command = create_ctlSets )
    cmds.text( label = '')
    cmds.showWindow(window)

#['browCtl', 'eyeCtl', 'mouthCtl', 'bridgeCtl', 'detailCtl' ]    
def browCtlGrp(*pArgs):
    twitchPanelConnect.storeCtlGrp_list('browCtl')
    
def eyeCtlGrp(*pArgs):
    twitchPanelConnect.storeCtlGrp_list('eyeCtl')
    
def mouthCtlGrp(*pArgs):
    twitchPanelConnect.storeCtlGrp_list('mouthCtl')
    
def bridgeCtlGrp(*pArgs):
    twitchPanelConnect.storeCtlGrp_list('bridgeCtl')
    
def detailCtlGrp(*pArgs):
    twitchPanelConnect.storeCtlGrp_list('detailCtl')
    
def all_main_detailCtls(*pArgs):
    twitchPanelConnect.all_main_detailCtls()

def arFace_ctlList(*pArgs):
    twitchPanelConnect.arFace_ctlList()

def reset_mCtl(*pArgs):
    facePart = cmds.optionMenu('face_level', query=True, value=True)
    twitchPanelConnect.resetCtrl(facePart)
    
def reset_ctl(*pArgs):
    facePart = cmds.optionMenu('face_region', query=True, value=True)
    twitchPanelConnect.resetCtrl(facePart)

def setKeysOnMCtl(*pArgs):
    facePart = cmds.optionMenu('face_level', query=True, value=True)
    twitchPanelConnect.setKeysOnCtl(facePart)    
def setKeysOnCtl(*pArgs):
    facePart = cmds.optionMenu('face_region', query=True, value=True)
    twitchPanelConnect.setKeysOnCtl(facePart)

def deleteMCtlKeys(*pArgs):
    facePart = cmds.optionMenu('face_level', query=True, value=True)
    twitchPanelConnect.deleteCtrlKeys(facePart)
def deleteCtrlKeys(*pArgs):
    facePart = cmds.optionMenu('face_region', query=True, value=True)
    twitchPanelConnect.deleteCtrlKeys(facePart)

def select_mCtl(*pArgs):
    facePart = cmds.optionMenu('face_level', query=True, value=True)
    cmds.select("%s_set"%facePart, r=1)
    
def select_ctl(*pArgs):
    facePart = cmds.optionMenu('face_region', query=True, value=True)
    cmds.select("%s_set"%facePart, r=1)

def addItemToLevelArray(*pArgs):
    ctlist = cmds.optionMenu('face_level', query=True, value=True)
    items = cmds.ls(sl=1, type = 'transform')
    twitchPanelConnect.addItemToArray( ctlist, items )
    
    
def addItemToRegionArray(*pArgs):
    ctlist = cmds.optionMenu('face_region', query=True, value=True)
    items = cmds.ls(sl=1, type = 'transform')
    twitchPanelConnect.addItemToArray( ctlist, items )

def removeItems_set( *pArgs ):
    ctlevel = cmds.optionMenu('face_level', query=True, value=True)
    ctlRegion = cmds.optionMenu('face_region', query=True, value=True)
    if ctlevel in ["mainCtl", "detailCtl"]:
        twitchPanelConnect.removeItems_deformerSet( ctlevel +"_set" )
        twitchPanelConnect.removeItems_deformerSet( ctlRegion +"_set" )
        twitchPanelConnect.removeItems_deformerSet( "allCtl_set" )
    else:
        cmds.confirmDialog( title='Confirm', message='set right ctl level/ region' )
        
def addItems_set( *pArgs ):
    ctllevel = cmds.optionMenu('face_level', query=True, value=True)
    ctlRegion = cmds.optionMenu('face_region', query=True, value=True)
    if ctllevel in ["mainCtl", "detailCtl"]:
        twitchPanelConnect.addItems_deformerSet( ctllevel+"_set" )
        twitchPanelConnect.addItems_deformerSet( ctlRegion +"_set" )
        twitchPanelConnect.addItems_deformerSet( "allCtl_set" )
    else:
        cmds.confirmDialog( title='Confirm', message='position the curve tx on center!!!' )

#eyeBrowLipGrp = browCtl/eyeCtl/lipCtl/bridgeCtl/all
def create_ctlSets(*pArgs):
    myLists = cmds.listAttr("helpPanel_grp", ud =1 )
    ctlLists = [ cx for cx in myLists if cx.split("_")[-1] == 'list' ]
    for clist in ctlLists:
        print clist
        twitchPanelConnect.create_ctlSets( clist)

def spaceBetween( numOfRow, numOfColm ):
    for x in range( numOfRow ):
        for i in range(numOfColm):
            cmds.text( l = '')
            
def printNewMenuItem( item ):
    print item
