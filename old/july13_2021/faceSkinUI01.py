# -*- coding: utf-8 -*-
'''__init__? ??? ??? ? ????? ?????.
from folder import file
reload(file)
file.zeroOutCluster()
'''

import maya.cmds as cmds
import os
from twitchScript import faceSkinFunction
reload(faceSkinFunction)
from twitchScript import squachSetup
reload(squachSetup)
from twitchScript import twitchPanelConnect
reload(twitchPanelConnect)
from twitchScript import blendShapeMethods
reload(blendShapeMethods)
from twitchScript import faceCompFunction
reload(faceCompFunction)

def faceSkinUI():

    #check to see if window exists
    if cmds.window ('faceSkinUI', exists = True):
        cmds.deleteUI( 'faceSkinUI')

    #create window
    window = cmds.window( 'faceSkinUI', title = 'faceSkin UI', w =420, h =900, mnb = True, mxb = True, sizeable=True, nestedDockingEnabled = True, resizeToFitChildren = True )

    tabs = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)

    #rowColumnLayout
    child1= cmds.rowColumnLayout( numberOfColumns = 3, bgc=[.22,.3,.40], columnWidth = [(1, 140),(2, 120),(3, 120)], columnOffset = [(1, 'right', 10)] )
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = 'Store Head Info', bgc = [.12,.2,.30], fn = "boldLabelFont",height= 20 )
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    
    cmds.text( label = '')
    cmds.text( label = 'select head geo')
    cmds.text( label = 'select allPos/ store pos')
    cmds.text( label = '')
    cmds.button( label = 'head geo', bgc=[.42,.5,.60], command = headGeo )
    cmds.button( label = 'store faceLocator', bgc=[.42,.5,.60], command = setupLocator )
    cmds.text( label = 'move hierachy to locPos' )
    cmds.button( label = 'update Hierachy/Cls', bgc=[.42,.5,.60], command = updateHierachy, ann = "when locators (headSkel, cheek, nose, ears) position changed" )
    cmds.text( label = '*before skinCls          ' )
    
    cmds.text( label = '')
    cmds.text( label = "store faceLocator first!!" )
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.button( label = 'plug NewHeadShape', bgc=[.42,.5,.60], command = plugNewHeadShape )
    cmds.button( label = '?', command = plugNewHead_helpImage )
    cmds.button( label = '?', command = updateFaceMain_helpImage )
    cmds.button( label = 'update FaceMain', bgc=[.42,.5,.60], command = updateHierachy_FaceMain )
    cmds.button( label = 'update clsFaceMain', bgc=[.42,.5,.60], command = updateHierachy_clsFaceMain )
    cmds.text( label = '')
    cmds.button( label = 'update ctl_Placement', bgc=[.42,.5,.60], command = update_CtlsPlacement, ann = "shape CTLCrv to hiCrv and run" ) 
    cmds.button( label = '?', command = updateCtlPlace_helpImage )
    cmds.text( label = 'from twitch to arFace')
    cmds.button( label = 'arFacePanel transfer', bgc=[.42,.5,.60], command = arFacePanel_transfer )
    cmds.text( label = '')
    
    
    cmds.separator( h = 15)    
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    
    cmds.text( label = '')
    cmds.text( label = 'Vertice Store', bgc = [.12,.2,.30], fn = "boldLabelFont",height= 20 )
    cmds.text( label = '')
    
    cmds.text( label = '')
    cmds.text( label = 'select browVtx in order')
    cmds.text( label = '/store in browFactor')
    cmds.text( label = '')
    cmds.button( label = 'browVerts',bgc=[.42,.5,.60], command = browVerts, ann = "store in order of vert tx value" )
    cmds.button( label = 'select browVerts',bgc=[.42,.5,.60], command = selectBrowVerts )
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')        
    cmds.text( label = '')
    cmds.text( label = 'select corner verts') 
    cmds.text( label = '/ direction vert on loop')
    cmds.text( label = 'Pick Eye or Lip! :', fn = "boldLabelFont" )
    cmds.optionMenu('eye_lip', bgc=[0,0,0], changeCommand=printNewMenuItem )
    cmds.menuItem( label='eye' )
    cmds.menuItem( label='lip' )
    cmds.button( label = 'orderedVerts', bgc=[.42,.5,.60], command = orderedUpLoVert ) 
    cmds.text( label = '         arFace verts')
    cmds.text( label = 'stored in order             ')
    cmds.button( label = 'arfOrderedVerts', bgc=[.42,.5,.60], command = arFaceOrderedVert_upLo )
    cmds.text( label = 'Select:    ', fn = "boldLabelFont" )
    cmds.button( label = 'up Verts', bgc=[.42,.5,.60], command = upVertSel )
    cmds.button( label = 'low Verts', bgc=[.42,.5,.60], command = lowVertSel )
    cmds.separator( h = 15)    
    cmds.separator( h = 15)
    cmds.separator( h = 15)

    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')    
    cmds.text( label = '')
    cmds.text( label = 'Controller', bgc = [.12,.2,.30], fn = "boldLabelFont",height= 20 )
    cmds.text( label = '')

    cmds.text( label = 'ctrl size / offset:')
    sizeField = cmds.floatField( "ctl_size", value = .2 )
    offsetField = cmds.floatField( "ctl_offset", value = .2 )
    cmds.text( label = 'ctrl name / color:')    
    cmds.optionMenu("ctlShape", bgc=[.42,.5,.60], changeCommand=printNewMenuItem )
    cmds.menuItem( label='circle' )
    cmds.menuItem( label='square' )
    colorID = cmds.floatField( "ctl_color", value = 10 )
    cmds.text( label = 'select rotate pivot')    
    cmds.button( label = 'create controller', bgc=[.42,.5,.60], command = controller )
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    
    cmds.text( label = '')
    cmds.text( label = 'Brow Setup', bgc = [.12,.2,.30], fn = "boldLabelFont",height= 20 )
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    
    cmds.text( label = 'brow joint:' )
    cmds.button( label = 'browJoints', bgc=[.42,.5,.60], command = browJoints )
    cmds.text( label = '')
    
    cmds.text( label = '')
    cmds.text( label = 'select "polyEdgeCrv"&"ctl"')
    cmds.text( label = '(or not)"                             '  )
    
    cmds.text( label = 'brow ctls:')
    cmds.optionMenu('numOfBrowCtl', bgc=[.42,.5,.60], changeCommand= printNewMenuItem )
    cmds.menuItem( label='7' )
    cmds.menuItem( label='9' )
    cmds.menuItem( label='11' )

    cmds.button( label = 'connect Brow ctrl', bgc=[.42,.5,.60], command = connectBrowCtrls )
    #cmds.button( label = 'twitch Brow ctrl', bgc=[.42,.5,.60], command = connectBrowCtrls )
        
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = 'Absolete', fn = "boldLabelFont", height= 20 )
    cmds.button( label = 'browWideJnt', bgc=[.42,.5,.60], command = browWideJnt )     
    cmds.button( label = 'browFix(up/down)', bgc=[.42,.5,.60], command = browUpDownReverse ) 
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')    
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')


    cmds.text( label = '')
    cmds.text( label = 'Eye Setup', bgc = [.12,.2,.30], fn = "boldLabelFont",height= 20 )
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.button( label = 'eyelid Joints', bgc=[.42,.5,.60], command = eyelidJoints )
    cmds.text( label = '')
    
    cmds.text( label = 'num of ctls/ offset:')
    cmds.optionMenu( "numOfEyeCtls", bgc=[.42,.5,.60], changeCommand= printNewMenuItem )   
    cmds.menuItem( label=3 )
    cmds.menuItem( label=5 )
    cmds.menuItem( label=7 )
    offsetField = cmds.floatField( "eyeCtlOffset", value = .5 )
    cmds.text( label = '')
    cmds.text( label = 'shape CTLCrv to HiCrv', fn = "boldLabelFont",height= 20 )
    cmds.text( label = 'wire/ skin CTLCrv    ')
    
    cmds.text( label = '' )
    cmds.button( label = 'eyeCtlCurves', bgc=[.42,.5,.60], command = eyeCtlCrv )
    cmds.button( label = 'eyeCrvConnect', bgc=[.42,.5,.60], command = eyeCrvConnect ) 
    cmds.text( label = '' )
    cmds.text( label = '    fix "double transform"')
    cmds.text( label = 'after merge with body    ' )
 
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')

    cmds.text( label = '')
    cmds.text( label = 'Jaw Setup', bgc = [.12,.2,.30], fn = "boldLabelFont",height= 20 )
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = 'num of lipCtl for up/lo' )
    cmds.text( label = '')

    cmds.text( label = 'lip ctls:')
    cmds.optionMenu('numOfLipCtl', bgc=[.42,.5,.60], changeCommand= printNewMenuItem )
    cmds.menuItem( label='5' )
    cmds.menuItem( label='7' )
    cmds.menuItem( label='9' )
    cmds.menuItem( label='11' )

    cmds.button( label = 'mouthJoint', bgc=[.42,.5,.60], command = mouthJoint )
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = 'poc to jnt /create ctlJnt')
    cmds.text( label = 'import ShapePanel first', fn = "boldLabelFont", height= 20)
    cmds.text( label = 'crv to jnt')
    cmds.button( label = 'jawCrvConnect', bgc=[.42,.5,.60], command = jawCrvConnect )     
    cmds.button( label = 'jawCtl_setup', bgc=[.42,.5,.60], command = jawCtl_setup )
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = ' ctl offset ')
    cmds.text( label = 'select custom ctrl!!', fn = "boldLabelFont", height= 20 )
    cmds.text( label = '')
    offsetField = cmds.floatField( "lipCtlOffset", value = .2 )

    cmds.button( label = 'lipFreeCtl', bgc=[.42,.5,.60], command = lipFreeCtl )
        
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')

         
    cmds.setParent( '..' )
    
    #2nd tab "face lift"
    child2= cmds.rowColumnLayout( numberOfColumns = 4, bgc=[.3,.22,.2], columnWidth = [(1, 120),(2, 120),(3, 120),(4, 40)], columnOffset = [(1, 'right', 5)] )
    
    spaceBetween(2,4)    
    
    cmds.text( label = '')
    cmds.text( label = 'Face Clusters', bgc = [.5,.6,.4], fn = "boldLabelFont",height= 20 )
    cmds.text( label = '')
    cmds.text( label = '')
    
    spaceBetween(2,4) 
    
    cmds.button( label = '?', command = createFaceCls_helpImage )
    cmds.button( label = 'Face Clusters', command = faceClusters )
    cmds.button( label = 'delete cluster layer', command = deleteClusterLayer )
    cmds.button( label = '?', command = deleteClusterLayer_helpImage )
    
    spaceBetween(1,4) 
    
    cmds.button( label = '?', height =15, width=15, command = updateFaceCls_helpImage )
    cmds.button( label = 'update FaceCluster', command = updateFaceCluster )
    cmds.text( label = '')
    cmds.text( label = '')    
        
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = 'select geometry!!')
    cmds.text( label = '')
    
    cmds.separator( h = 15 )
    cmds.optionMenu('clusterName', bgc=[0,0,0], changeCommand=printNewMenuItem )
    cmds.menuItem( label='browUp_cls' )
    cmds.menuItem( label='browDn_cls' )
    cmds.menuItem( label='browTZ_cls' )
    cmds.menuItem( label='jawOpen_cls' )
    cmds.menuItem( label='lip_cls' )
    cmds.menuItem( label='upLipRoll_cls' )
    cmds.menuItem( label='bttmLipRoll_cls' )
    cmds.menuItem( label='lipRoll_cls' )
    cmds.menuItem( label='eyeWide_cls' )
    cmds.menuItem( label='eyeBlink_cls' )
    cmds.menuItem( label='l_squintPuff_cls' )
    cmds.menuItem( label='l_cheek_cls' )
    cmds.menuItem( label='l_lowCheek_cls' )
    cmds.menuItem( label='l_ear_cls' )
    cmds.menuItem( label='nose_cls' ) 
    cmds.menuItem( label='upLipRoll_cls' )
    cmds.menuItem( label='bttmLipRoll_cls' )
    cmds.button( label = 'weightedVerts', command = weightedVerts )
    cmds.text( label = '')
    
    spaceBetween(1,4)
    
    cmds.text( label = '')    
    cmds.optionMenu('ddClusterName', bgc=[0,0,0], changeCommand=printNewMenuItem )
    cmds.menuItem( label='browUp_cls' )
    cmds.menuItem( label='browDn_cls' )
    cmds.menuItem( label='browTZ_cls' )
    cmds.menuItem( label='jawOpen_cls' )
    cmds.menuItem( label='lip_cls' )
    cmds.menuItem( label='lipRoll_cls' )
    cmds.menuItem( label='upLipRoll_cls' )
    cmds.menuItem( label='bttmLipRoll_cls' )
    cmds.menuItem( label='eyeWide_cls' )
    cmds.menuItem( label='eyeBlink_cls' )
    cmds.menuItem( label='l_squintPuff_cls' )
    cmds.menuItem( label='l_cheek_cls' )
    cmds.menuItem( label='l_lowCheek_cls' ) 
    cmds.menuItem( label='l_ear_cls' )
    cmds.menuItem( label='nose_cls' )
    cmds.menuItem( label='upLipRoll_cls' )
    cmds.menuItem( label='bttmLipRoll_cls' )
    cmds.button( label = 'copy ClsWgt', command = copyClusterWgt ) 
    cmds.text( label = '')
    
    spaceBetween(1,4)
    
    cmds.text( label = '')
    cmds.button( label = 'exportClsWgt', command = exportClsWgt )
    cmds.button( label = 'importClsWgt', command = importClsWgt )
    cmds.text( label = '')

    spaceBetween(1,4)
    
    cmds.text( label = 'lipCorner Clusters')
    cmds.button( label = 'lipCorner clusters', bgc=[.5,.6,.4], command = lipCornerCls  )
    cmds.button( label = 'mirrorWgt Cluster', bgc=[.5,.6,.4], command = faceClsMirrorWgt )
    cmds.text( label = '')
    
    cmds.text( label = '')
    cmds.optionMenu('select_cluster', bgc=[0,0,0], changeCommand= printNewMenuItem )
    cmds.menuItem( label= "eyeWide" )
    cmds.menuItem( label= "eyeBlink" )
    cmds.menuItem( label= "lowCheek" )
    cmds.menuItem( label= "squintPuff" )
    cmds.menuItem( label= "ear" )
    cmds.menuItem( label= "cheek" )
    cmds.menuItem( label= "cornerUp" ) 
    cmds.menuItem( label= "cornerDwn" )
    cmds.button( label = 'indieCls mirrorWgt', bgc=[.5,.6,.4], command = indieClsWeightMirror )
    cmds.text( label = '')
    
    cmds.text( label = 'faceCls connect')
    cmds.button( label = 'faceCls connect', bgc=[.5,.6,.4], command = connectFaceCluster )
    cmds.text( label = '')
    cmds.text( label = '')
    
    cmds.text( label = '')    
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.text( label = '')
    
    cmds.text( label = 'Toggle Deform:')
    cmds.button( label = 'toggleDeform', command = deformerToggle  )
    cmds.button( label = 'zero Cls', command = zeroOutCluster  )
    cmds.text( label = '')
    
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.text( label = '')
    
    spaceBetween(2,4)
    
    cmds.text( label = '')
    cmds.text( label = 'Curve on Mesh', bgc = [.5,.6,.4], fn = "boldLabelFont",height= 20 )
    cmds.text( label = '')
    cmds.text( label = '')
    
    spaceBetween(1,4)
    
    cmds.text( label = 'vtx type            ')    
    cmds.text( label = 'curve open/close')
    cmds.text( label = 'degree')
    cmds.text( label = '')
    
    cmds.optionMenu('mapName', bgc=[0,0,0], changeCommand=printNewMenuItem )
    cmds.menuItem( label="brow" )
    cmds.menuItem( label="eye" )
    cmds.menuItem( label="lip" )
    cmds.optionMenu('openClose', bgc=[0,0,0], changeCommand=printNewMenuItem )
    cmds.menuItem( label="open" )
    cmds.menuItem( label="close" )
    cmds.optionMenu('degree', bgc=[0,0,0], changeCommand=printNewMenuItem )
    cmds.menuItem( label=1 )
    cmds.menuItem( label=3 )
    cmds.text( label = '')
    
    cmds.text( label = '')
    cmds.text( label = '      select left half vertices')
    cmds.text( label = 'in order                            ')
    cmds.text( label = '')

    cmds.optionMenu('crvCharacterName', bgc=[0,0,0], changeCommand=printNewMenuItem )
    cmds.menuItem( label="" )
    cmds.menuItem( label="_guide" )
    cmds.menuItem( label="_map" )
    cmds.menuItem( label="_BS" )
    cmds.menuItem( label="_wire" )
    cmds.menuItem( label="_temp" )
    cmds.menuItem( label="_test" )    
    cmds.button( label = 'curve_halfVerts', command = curve_halfVerts )
    cmds.text( label = '')
    cmds.button( label = '?', command = faceLift_helpImage3 )
    
    spaceBetween(1,4)
    cmds.text( label = '')
    cmds.button( label = 'store_uParam', command = store_uParam )
    cmds.text( label = '')
    cmds.button( label = '?', command = faceLift_helpImage4 )
    
    cmds.separator( h = 15)    
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.text( label = '')
    
    cmds.text( label = '')
    cmds.text( label = 'loop curves Eye/Lip', bgc = [.5,.6,.4], fn = "boldLabelFont", height= 20 )
    cmds.text( label = '')
    cmds.text( label = '')
    
    spaceBetween(1,4)
    
    cmds.text( label = 'select facePart')
    cmds.text( label = '2vtx (corner/vector)')
    cmds.text( label = '')
    cmds.text( label = '')
    
    cmds.optionMenu('facePart', bgc=[0,0,0], changeCommand=printNewMenuItem )
    cmds.menuItem( label='eye' )
    cmds.menuItem( label='lip' )
    cmds.button( label = 'curveOnLoop', command = curveOnLoop )
    cmds.text( label = '')
    cmds.button( label = '?', command = faceLift_helpImage5 )
    
    cmds.text( label = '')
    cmds.text( label = '       corner vertices /vector ')
    cmds.text( label = 'vertex                              ')
    cmds.text( label = '')

    cmds.text( label = '')
    cmds.button( label = 'all curves loop', command = seriesOfEdgeLoopCrv )
    cmds.text( label = '')
    cmds.button( label = '?', command = faceLift_helpImage6 )
    
    spaceBetween(1,4)
    
    cmds.text( label = '') 
    cmds.text( label = 'symmetrize', bgc = [.4,.5,.4], height= 20 )
    cmds.text( label = '') 
    cmds.text( label = '')
    
    cmds.text( label = 'mirror direction')
    cmds.text( label = 'select open curve')
    cmds.text( label = 'select loop curve')    
    cmds.text( label = '')
    
    cmds.checkBox( 'direction', label='+To-' ) 
    cmds.button( label = 'symmetry Open', command = symmetrizeOpenCrv )  
    cmds.button( label = 'symmetry Loop', command = symmetrizeLipCrv )
    cmds.text( label = '')
    
    cmds.separator( h = 15)    
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.text( label = '')
    
    spaceBetween(1,4)
    '''cmds.text( label = 'browFactor:')    
    if cmds.objExists("browFactor"):
        if cmds.attributeQuery("browUp_scale", node = "browFactor", exists=1)==True:
            browRxField = cmds.intField( value = cmds.getAttr('browFactor.browUp_scale'))
            browRyField = cmds.intField( value = cmds.getAttr('browFactor.browRotateY_scale'))
    else: 
        browRxField = cmds.intField( value = 20 )
        browRyField = cmds.intField( value = 10 )'''    
    cmds.text( label = '')
    cmds.text( label = 'Map Skinning', bgc = [.5,.6,.4], fn = "boldLabelFont",height= 20 )
    cmds.text( label = '')
    cmds.text( label = '')
    
    spaceBetween(1,4)
    
    cmds.text( label = '')
    cmds.text( label = 'select crvs in order')
    cmds.text( label = 'do not delete crv yet')
    cmds.text( label = '')
    
    cmds.text( label = '')
    cmds.button( label = 'loft MapSurface', command = loftMapSurf )
    cmds.button( label = 'browSurfMapSkin', command = browMapSkin )
    cmds.text( label = '')
    
    spaceBetween(1,4)
    
    cmds.text( label = '')
    cmds.button( label = 'lipSurfMapSkin', command = lipMapSkinning  )
    cmds.button( label = 'eyeSurfMapSkin', command = eyeMapSkin  )
    cmds.text( label = '')
    
    cmds.separator( h = 15)    
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.text( label = '')
    
    spaceBetween(3,4)
    
    cmds.text( label = '')
    cmds.text( label = 'Extra', bgc = [.5,.6,.4], fn = "boldLabelFont",height= 20 )
    cmds.text( label = '')
    cmds.text( label = '')
    
    spaceBetween(1,4)
    
    cmds.separator( h = 15)    
    cmds.text( label = 'manually select edges')
    cmds.text( label = 'corner/vector 2 verts')
    cmds.text( label = '')
    
    cmds.text( label = 'manual curve')     
    cmds.button( label = 'edgeSelection', command = edgeSelection ) 
    cmds.button( label = 'curveOnEdgeSel', command = curveOnEdgeSelection )
    cmds.text( label = '')
    
    cmds.separator( h = 15)    
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.text( label = '')
    
    cmds.separator( h = 15)
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    
    spaceBetween(3,4)
        
    cmds.setParent( '..' )
    
    child3= cmds.rowColumnLayout( numberOfColumns = 3, bgc=[.5,.2,.1], columnWidth = [(1, 140),(2, 120),(3, 120)], columnOffset = [(1, 'right', 5)] )

    '''import sys
    sys.path.append('c:/Users/sshin/Documents/maya/2016/scripts/twitchScript')'''
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = 'need "shape panel"/"face' )
    cmds.text( label = ' clusters"                            ')
    cmds.button( label = '?', command = eyeRig_helpImage )
    cmds.button( label = 'create Eye Rig', bgc=[.5,.6,.4], command = createEyeRig ) 
    #def eyeBallDirection/ def eyeLidOffset_scale / lidBlendShape_setup(Push_squint_blink)
    cmds.text( label = ' select eyeBall with BS    ')
    cmds.button( label = '?', command = skinEyeBall_helpImage )
    cmds.button( label = 'jointSkinEyeBall', bgc=[.5,.6,.4], command = jointSkinEyeBall )
    cmds.button( label = 'irisPupilSetup', bgc=[.5,.6,.4], command = irisPupilSetup )

    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    
    cmds.text( label = '')
    cmds.text( label = 'arFace Skinning', bgc = [.1,.2,.2], fn = "boldLabelFont",height= 20 )
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = 'head geo:')
    objName = cmds.textField( 'headGeoName', text = "head_REN" )
    cmds.text( label = '')
    cmds.separator( h = 15)
    cmds.button( label = 'headSkin', bgc=[.5,.6,.4], command = headSkin )
    cmds.button( label = 'arFaceHeadSkin', bgc=[.5,.6,.4], command = arFaceHeadSkin )
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    
    cmds.text( label = 'head geo:')
    cmds.button( label = 'copyTrioSkinWgt', bgc=[.5,.6,.4], command = copyTrioSkinWeights  )
    cmds.button( label = 'exportTrioSkinWgt', bgc=[.5,.6,.4], command = exportTrioSkinWgt  )
    cmds.text( label = 'check if lock weight')
    cmds.button( label = 'calculateSkinWgt', bgc=[.5,.6,.4], command = faceWeightCalculate  )
    cmds.button( label = 'mouth_pivot change', bgc=[.5,.6,.4], command = mouth_pivotChange  )
    
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
       
    cmds.text( label = 'seperate eyeLid:')
    cmds.button( label = 'copyExportEyeSkin', bgc=[.5,.6,.4], command = copyExportEyeSkinWeights  )
    cmds.button( label = 'eyeWeightCalculate', bgc=[.5,.6,.4], command = eyeWeightCalculate  )
    cmds.text( label = '')
    cmds.button( label = 'switchEyeJnt toCls', bgc=[.5,.6,.4], command = switchJntToCls  )   
    cmds.text( label = '')    
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.text( label = '')
    cmds.text( label = 'arFace Curves', bgc = [.1,.2,.2], fn = "boldLabelFont",height= 20 )
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = 'eyeLid curve')
    cmds.optionMenu('eyeLid_crv', bgc=[0,0,0], changeCommand= printNewMenuItem )

    cmds.menuItem( label= "squint_crv" )
    cmds.menuItem( label= "annoy_crv" )
    cmds.menuItem( label= "PushA_crv" )
    cmds.menuItem( label= "PushB_crv" )
    cmds.menuItem( label= "PushC_crv" )
    cmds.menuItem( label= "PushD_crv" )
    cmds.button( label = 'eyeLid curve', bgc=[.5,.6,.4], command = eyeLidCrvIsolate )

    cmds.text( label = 'lip curve')
    cmds.optionMenu('lip_crv', bgc=[0,0,0], changeCommand= printNewMenuItem )
    cmds.menuItem( label= "happy_crv" )
    cmds.menuItem( label= "sad_crv" )
    cmds.menuItem( label= "E_crv" )
    cmds.menuItem( label= "wide_crv" )
    cmds.menuItem( label= "U_crv" )
    cmds.menuItem( label= "O_crv" )
    cmds.menuItem( label= "jawOpen" )
    cmds.menuItem( label= "jawDrop" )
    cmds.button( label = 'lip curve', bgc=[.5,.6,.4], command = lipCrvIsolate )

    cmds.text( label = 'brow curve')
    cmds.optionMenu('brow_crv', bgc=[0,0,0], changeCommand= printNewMenuItem )
    cmds.menuItem( label= "browSad" )
    cmds.menuItem( label= "browMad" )
    cmds.menuItem( label= "furrow" )
    cmds.menuItem( label= "relax" )
    cmds.button( label = 'brow curve', bgc=[.5,.6,.4], command = browCrvIsolate )

    spaceBetween(1,3)
    cmds.text( label = '')
    cmds.text( label = 'select 2 curves')
    cmds.text( label = '*no curve direction change')
    cmds.text( label = 'copy/Mirror curves')
    cmds.button( label = 'copy curve shape', bgc=[.5,.6,.4], command = copyCurveShape )
    cmds.button( label = 'mirror curve Shape', bgc=[.5,.6,.4], command = mirrorCurveShape ) 
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = 'eyeLidA to B, C to D')
    cmds.text( label = '')
    cmds.optionMenu('ABCD', bgc=[0,0,0], changeCommand= printNewMenuItem )
    cmds.menuItem( label= "lookUp" )
    cmds.menuItem( label= "lookDown" )
    cmds.button( label = 'mirror eyeLid shape', bgc=[.5,.6,.4], command = mirror_eyeLidShape )

    cmds.text( label = '') 
    cmds.text( label = ' set 2 blenadShape.crv') 
    cmds.text( label = 'to max                     ')     
    cmds.text( label = '')
    cmds.optionMenu('browLip', bgc=[0,0,0], changeCommand= printNewMenuItem )
    cmds.menuItem( label= "brow" )
    cmds.menuItem( label= "lip" )    
    cmds.button( label = 'corrective curve', bgc=[.5,.6,.4], command = correctiveCrv )
    
    spaceBetween(1,3)    
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.separator( h = 15)

    cmds.text( label = '')
    cmds.text( label = 'arFace BlendShape', bgc = [.1,.2,.2], fn = "boldLabelFont",height= 20 )
    cmds.text( label = '')
    
    spaceBetween(1,3)
    cmds.text( label = '   select base   ', bgc = [.1,.2,.2], fn = "boldLabelFont",height= 20 )
    cmds.button( label = 'split BS Weight', bgc=[.5,.6,.4], command = splitBSWeightMap )
    cmds.button( label = 'create twitchBS', bgc=[.5,.6,.4], command = createTwitchBS )
    spaceBetween(1,3)
    cmds.text( label = 'Connect curveBS first,', fn = "boldLabelFont" )
    cmds.text( label = 'then twitchBS if exists  ', fn = "boldLabelFont")
    cmds.button( label = 'ctrls connect BS', bgc=[.5,.6,.4], command = ctrlConnectBS, annotation = "BCDtype connection" )
    spaceBetween(1,3)
    cmds.text( label = '   corrective shape   ', bgc = [.1,.2,.2], fn = "boldLabelFont",height= 20 )
    cmds.text( label = 'set ctls(l,r) to 1!  &  sele', fn = "boldLabelFont" )
    cmds.text( label = 'ct Aim Shape( no base)', fn = "boldLabelFont")
    cmds.button( label = '?', command = BScorrective_reset_helpImage )
    cmds.button( label = 'fix BS_corrective', bgc=[.5,.6,.4], command = fixTwitchTarget )
    cmds.button( label = 'reset corrective', bgc=[.5,.6,.4], command = resetForCorrectiveFix )
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = 'select baseGeo :  ', fn = "boldLabelFont")
    cmds.text( label = 'twitch update weight ', fn = "boldLabelFont")
    cmds.text( label = 'Set ctls 1 !!', fn = "boldLabelFont" )
    cmds.optionMenu('split_range', bgc=[0,0,0], changeCommand= printNewMenuItem )
    cmds.menuItem( label= "ear" )
    cmds.menuItem( label= "mouth" )
    cmds.menuItem( label= "nose" ) 
    cmds.button( label = ' update weight ', bgc=[.5,.6,.4], command = updateWeight )
    cmds.text( label = '')
    cmds.text( label = 'select new mesh  :', fn = "boldLabelFont" )
    cmds.text( label = 'add twitchBS ', fn = "boldLabelFont" )
    cmds.button( label = '?', command = addTarget_helpImage )
    cmds.optionMenu( 'target_type', bgc=[0,0,0], changeCommand = printNewMenuItem )
    cmds.menuItem( label= "target" )
    cmds.menuItem( label= "corrective" )
    cmds.button( label = ' add target ', bgc=[.5,.6,.4], command = addTarget )
    
    spaceBetween(1,3)
    cmds.text( label = '  1. xyz   ', bgc = [.10,.4,.40], height= 20 )
    cmds.text( label = '  2. plusTarget name   ', bgc = [.10,.4,.40], height= 20 )
    cmds.text( label = '  3. minusTarget name   ', bgc = [.10,.4,.40], height= 20 )
    cmds.text( label = '')
    cmds.text( label = 'assume "l/r_" in names ' )
    cmds.text( label = '(l/r_)Happy, (l/r_)Sad' )    
    cmds.optionMenu('xyzAxis', bgc=[0,0,0], changeCommand= printNewMenuItem )
    cmds.menuItem( label= "x" )
    cmds.menuItem( label= "y" )
    cmds.menuItem( label= "z" )    

    cmds.textField( 'plusTarget_name', text = "Happy" )
    cmds.textField( 'minusTarget_name', text = "Sad" )

    cmds.text( label = '')
    cmds.text( label = '  select 2 ctls & objects', fn = "boldLabelFont" )
    cmds.text( label = 'with BS/ check weight', fn = "boldLabelFont")
    
    cmds.button( label = '?', command = extraCrvCorrective_helpImage )
    cmds.button( label = ' simpleCtl_bsConnect', bgc=[.5,.6,.4], command = simpleCtl_bsConnect )    
    cmds.button( label = ' extraCrv_corrective ', bgc=[.5,.6,.4], command = extraCrvShape_corrective ) 
    
    spaceBetween(1,3)    
    cmds.text( label = '')
    cmds.text( label = 'set ctrls 1')
    cmds.text( label = 'select tgt(name!)')
    cmds.text( label = '')
    cmds.button( label = 'brow corrective', bgc=[.5,.6,.4], command = createBrowCorrective )
    cmds.button( label = 'update remapMax', bgc=[.5,.6,.4], command = updateRemapMax )
    cmds.text( label = 'fix mixedBS')
    cmds.button( label = 'fix mix', bgc=[.5,.6,.4], command = fixMix )
    cmds.button( label = 'split XYZ', bgc=[.5,.6,.4], command = splitXYZ, annotation = "select target and base mesh( create new blendshape with target_x, target_y, target_z )" )
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.separator( h = 15) 
    
    cmds.text( label = '')
    cmds.text( label = '  select all the objects')
    cmds.text( label = 'for upTeeth / loTeeth grp')
    cmds.text( label = 'teeth setup')
    cmds.button( label = 'upTeeth', bgc=[.5,.6,.4], command = upTeethSetup )
    cmds.button( label = 'loTeeth', bgc=[.5,.6,.4], command = loTeethSetup )

    cmds.text( label = 'tongue setup')
    cmds.text( label = 'position tongue_ctl')
    cmds.button( label = 'tongueSetup', bgc=[.5,.6,.4], command = tongueSetup )     
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    '''cmds.text( label = '') 
    cmds.text( label = 'jawOpen fix') 
    cmds.text( label = 'lipCorner level/TZ') 
    cmds.text( label = 'jaw Extra')
    cmds.button( label = 'jawDetail_crv', bgc=[.5,.6,.4], command = jawRigDetailCrv  )
    cmds.button( label = 'corner Level/Lip Tz', bgc=[.5,.6,.4], command = lipTzSetup  )
    cmds.text( label = '')
    cmds.button( label = 'lipThinning', bgc=[.5,.6,.4], command = lipThinningSetup  )
    cmds.button( label = 'dial lipFactor', bgc=[.5,.6,.4], command = dial_lipFactor  )
    
    cmds.separator( h = 15)    
    cmds.separator( h = 15)
    cmds.separator( h = 15)'''    
   
    cmds.setParent( '..' )    


    #4nd tab "face lift"
    child4= cmds.rowColumnLayout( numberOfColumns = 4, bgc=[.22,.3,.40], columnWidth = [(1, 120),(2, 120),(3, 120),(4, 40)], columnOffset = [(1, 'right', 5)] )
    spaceBetween(2,4)

    cmds.text( label = '')
    cmds.text( label = 'faceControls', bgc = [.12,.2,.30], fn = "boldLabelFont",height= 20 )
    cmds.text( label = '')
    cmds.text( label = '')
    
    spaceBetween(1,4)

    cmds.text( label = '')
    cmds.button( label = 'faceControls', bgc=[.42,.5,.60], command = faceControls ) 
    cmds.button( label = 'arFaceSelection', bgc=[.42,.5,.60], command = arFaceSelection )
    cmds.text( label = '')   

    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.text( label = '')
    
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    
    cmds.text( label = '    BlendShape    ', bgc = [.12,.2,.30], height= 20 )
    cmds.text( label = '   select targets (name!!)')
    cmds.text( label = 'and base with BS             ')
    cmds.text( label = '') 
        
    cmds.text( label = '  1. Edit Targets   ', bgc = [.10,.4,.40], height= 20 )
    cmds.button( label = 'target Add/Reconnect', bgc=[.42,.5,.60], command = targetAdd_Reconnect )
    cmds.button( label = 'crv Add/Reconnect', bgc=[.42,.5,.60], command = crvAdd_reconnect )
    cmds.button( label = '?', command = crvAddReconnect_helpImage )
    
    cmds.text( label = '')
    cmds.text( label = ' set L/R ctls to 1 /  select')
    cmds.text( label = 'corrective and base crv')   
    cmds.text( label = '')
    
    cmds.button( label = '?', command = addCrvCorrective_helpImage )
    cmds.button( label = 'addCrv_corrective', bgc=[.42,.5,.60], command = addCrv_corrective )
    cmds.text( label = '')
    cmds.text( label = '')
    
    spaceBetween(1,4)
    cmds.text( label = '   2. Propagate     ', bgc = [.10,.4,.40], height= 20 )
    cmds.text( label = 'select tgt and base')
    cmds.text( label = 'sel newTgt, oldTgt')
    cmds.text( label = '')
    
    cmds.text( label = '' )
    cmds.button( label = 'propagate fix setup', bgc=[.42,.5,.60], command = propagateFix_setup )
    cmds.button( label = 'propagate gap', bgc=[.42,.5,.60], command = propagateGap )
    cmds.text( label = '')
    
    spaceBetween(1,4)

    cmds.text( label = '')    
    cmds.text( label = 'name for new curve')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '   Transfer BS   ', bgc = [.12,.2,.30], height= 20 )    
    wireName = cmds.textField( 'crvWire_name', text = "brow" )
    cmds.button( label = 'dnCrv_srcUParam', bgc=[.42,.5,.60], command = dnCrv_srcUParam )
    cmds.text( label = '')

    cmds.text( label = '')
    cmds.text( label = 'select head_base')
    cmds.text( label = 'select "CV" at corner', fn = "boldLabelFont",height= 20 )
    cmds.text( label = '')
    
    cmds.button( label = '?', command = wtCircle_helpImage )
    cmds.button( label = 'create_wtCircle', bgc=[.42,.5,.60], command = create_wtCircle )
    cmds.button( label = 'Wide Tight crvBS', bgc=[.42,.5,.60], command = WideTight_crvBS )    
    cmds.button( label = '?', command = WideTightCrvBS_helpImage )
    
    cmds.text( label = '')
    cmds.text( label = 'select src/tgt crv')
    cmds.text( label = 'bake BS with angle gap')
    cmds.text( label = '')
    
    cmds.button( label = '?', command = bakeDelta_helpImage )
    cmds.button( label = 'bakeCrvDeltaBS', bgc=[.42,.5,.60], command = bakeCrvDeltaBS )
    cmds.button( label = 'transferCurveBS', bgc=[.42,.5,.60], command = transferCurveBS )
    cmds.button( label = '?', command = transferCurve_helpImage )
    
    cmds.text( label = 'select curve with BS')
    cmds.button( label = 'bakeTarget_reconnect', bgc=[.42,.5,.60], command = bakeTarget_reconnect )
    cmds.text( label = '')
    cmds.text( label = '')
    
    spaceBetween(1,4)
    
    cmds.text( label = '      Wire Setup      ', bgc = [.12,.2,.30], height= 20 )
    cmds.text( label = 'shp/wtWire, head_base')
    cmds.text( label = 'nurbsSphere, head_base')
    cmds.text( label = '')
    
    cmds.button( label = '?', command = lipWireSetup_helpImage )
    cmds.button( label = 'lipWire_setup', bgc=[.42,.5,.60], command = lipWire_setup )
    cmds.button( label = 'cheekSculpt head', bgc=[.42,.5,.60], command = cheekSculpt_head )
    cmds.button( label = '?', command = cheekSculptHead_helpImage )
    
    cmds.text( label = '')
    cmds.text( label = 'wire, head_base')
    cmds.text( label = '')
    cmds.text( label = '')
    
    cmds.text( label = '')
    cmds.button( label = 'browWire_setup', bgc=[.42,.5,.60], command = browWire_setup )
    cmds.text( label = '')
    cmds.text( label = '')
    spaceBetween(1,4)
    
    cmds.text( label = '      shape tool      ', bgc = [.12,.2,.30], height= 20 )
    cmds.button( label = 'shapeToCurve', bgc=[.42,.5,.60], command = shapeToCurve )
    cmds.text( label = '')
    cmds.text( label = '')
    
    spaceBetween(1,4)

    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.text( label = '')
    cmds.text( label = 'joints length:')
    jntLen = cmds.intField( 'joint_length', value = 12 )
    cmds.text( label = '')
    cmds.text( label = '')
    
    cmds.button( label = '?', command = squachBox_helpImage )
    cmds.button( label = 'squachBox', bgc=[.42,.5,.60], command = squachBoxForLattice )    
    cmds.button( label = 'squachSetup', bgc=[.42,.5,.60], command = squachFunction )
    cmds.button( label = '?', command = squachSetup_helpImage )
    
    cmds.text( label = '')
    cmds.button( label = 'boxSkin wgt to Lattice', bgc=[.42,.5,.60], command = copyBoxSkinToLattice )
    cmds.text( label = '')
    cmds.text( label = '')
    
    cmds.text( label = 'select objects to add')
    cmds.optionMenu('lattice_jnt', changeCommand= printNewMenuItem )
    cmds.menuItem( label= "lattice" )
    cmds.menuItem( label= "joint" )
    cmds.button( label = 'addSquachGeo', bgc=[.42,.5,.60], command = addSquachGeo )    
    cmds.text( label = '')
    
    cmds.text( label = 'squach name')
    cmds.text( label = 'bendDirection')
    cmds.text( label = 'select bttm/top ctl')
    cmds.text( label = '')
    
    objName = cmds.textField( 'objName', text = "body" )
    #x+, xdown, yup, ydown, zup, zdown, none.
    cmds.optionMenu('bendDirection', changeCommand= printNewMenuItem )
    cmds.menuItem( label= "xup" )
    cmds.menuItem( label= "xdown" )
    cmds.menuItem( label= "yup" )
    cmds.menuItem( label= "ydown" )
    cmds.menuItem( label= "zup" )
    cmds.menuItem( label= "zdown" )
    cmds.button( label = 'nonTwitch squach', bgc=[.42,.5,.60], command = nonTwitchSquachRig )
    cmds.button( label = '?', command = nonTwitchSquach_helpImage )
    
    cmds.separator( h = 15) 
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.text( label = '')
    spaceBetween(1,4)
    cmds.text( label = '')
    cmds.text( label = 'Michelleneous', bgc = [.12,.2,.30], fn = "boldLabelFont",height= 20 )
    cmds.text( label = '')
    cmds.text( label = '')
    
    spaceBetween(1,4)

    cmds.text( label = '')
    cmds.button( label = 'create Parent Null', bgc=[.42,.5,.60], command = createPntNull )     
    cmds.button( label = 'transfer cluster WN', bgc=[.42,.5,.60], command = changeClsWeightNode ) 
    cmds.text( label = '')
    
    spaceBetween(1,4)
       
    cmds.text( label = '  replace node   ', bgc = [.12,.2,.30], height= 20 )
    cmds.text( label = 'select item to Replace', bgc = [.12,.2,.20] )
    cmds.text( label = 'in:source / out:destine', bgc = [.12,.2,.20] )
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
    cmds.text( label = '')
    cmds.text( label = '')
    
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
    cmds.button( label = 'delete plugins', bgc=[.42,.5,.60], command = deleteUnknown_plugins )
    cmds.text( label = '')
    
    cmds.text( label = '')
    cmds.text( label = 'select geo/crv + ctl prnts')
    cmds.text( label = '/select top group for ctls ')
    cmds.text( label = '')
    
    cmds.text( label = '')
    cmds.button( label = 'stick ctl to skin', bgc=[.42,.5,.60], command = stickCtlToFace )
    cmds.button( label = 'compensate stickyCtl', bgc=[.42,.5,.60], command = compensateStickyCtl )  
    cmds.text( label = '')
    
    spaceBetween(1,4)
        
    cmds.text( label = 'multi input:')
    cmds.text( label = 'select source ctrls')
    cmds.text( label = "then select target")
    cmds.text( label = '')
    
    cmds.text( label = 'attribute')
    cmds.optionMenu('tform', changeCommand=printNewMenuItem )
    cmds.menuItem( label='translate' )
    cmds.menuItem( label='rotate' )
    cmds.menuItem( label='scale' )
    cmds.button( label = 'multi ctrls connect', bgc=[.42,.5,.60], command = multiInputConnect )
    cmds.text( label = '')
    
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.text( label = '')
    
    spaceBetween(1,4)
    
    cmds.text( label = '')
    cmds.button( label = 'copy weight', bgc=[.42,.5,.60], command = copyWeight )
    cmds.button( label = 'paste weight', bgc=[.42,.5,.60], command = pasteWeight )
    cmds.text( label = '')
    
    spaceBetween(1,4)
 

    '''   
    cmds.text( label = '')
    cmds.text( label = 'RNK tool', bgc = [.12,.2,.30], fn = "boldLabelFont",height= 20 )
    cmds.text( label = '')

    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = 'jawOpen,lipRoll,browUp' )    
    cmds.text( label = 'Blink,Wide,l_ear,nose' ) 
    cmds.text( label = 'up/bttmLipRoll,l_cheek' )
    cmds.text( label = 'RNK calculate Face:')
    cmds.button( label = 'rnkFaceWeight', bgc=[.42,.5,.60], command = rnkFaceWeightCalculate  )
    cmds.button( label = 'rnkCopyJaw', bgc=[.42,.5,.60], command = rnkCopyJawOpenWeight  )
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = 'Split BS weight')
    cmds.text( label = 'create splitMapBS first!!')
    cmds.text( label = '')
    cmds.text( label = 'select : ')
    cmds.text( label = 'geo with blendShape' )
    cmds.text( label = 'geo(with BS)/target geo')

    cmds.optionMenu('weight_scale', bgc=[.42,.5,.60], changeCommand= printNewMenuItem )
    cmds.menuItem( label='1' )
    cmds.menuItem( label='2' )
    cmds.menuItem( label='3' )
    cmds.button( label = 'rnk Split BSWeight', bgc=[.42,.5,.60], command = rnkSplitBSWeight )      
    cmds.button( label = 'copyBSWeight', bgc=[.42,.5,.60], command = copyBSWeight )''' 

    cmds.setParent( '..' )
            
    cmds.tabLayout( tabs, edit=True, tabLabel=((child1, 'Run It All'), (child2, 'Face Lift'), (child3, 'Face Skinninng'), (child4, 'Michelleneous')) )
    #show window
    cmds.showWindow(window)

#face lift tab
def spaceBetween( numOfRow, numOfColm ):
    for x in range( numOfRow ):
        for i in range(numOfColm):
            cmds.text( l = '')
        
def arHelpImage( imageTitle ):   

    if cmds.window( "arFace_helpImage", q =1, ex =1 ):
        cmds.deleteUI("arFace_helpImage" )

    arWindow = cmds.window( title="arFace_helpImage", iconName='helpImage', widthHeight=(400, 550) )
    cmds.paneLayout()
    cmds.image( image='C:/Users/SW/OneDrive/Documents/maya/2018/scripts/twitchScript/arFaceImage/%s.png'%imageTitle )
    #cmds.setParent( '..' )
    cmds.showWindow( arWindow )


def plugNewHead_helpImage( *pArgs ):
    arHelpImage( "plugNewHead03" )
    
def updateFaceMain_helpImage( *pArgs ):
    arHelpImage( "update_FaceMain06" )

def updateCtlPlace_helpImage( *pArgs ):
    arHelpImage( "update_ctlConnect04" )
    
def createFaceCls_helpImage( *pArgs ):
    arHelpImage( "createFaceCls02" )

def deleteClusterLayer_helpImage( *pArgs ):
    arHelpImage( "deleteClusterLayer02" )    

def updateFaceCls_helpImage( *pArgs ):
    arHelpImage( "update_faceCls06" )

def faceLift_helpImage3( *pArgs ):
    arHelpImage( "curve_halfVerts03" )

def faceLift_helpImage4( *pArgs ):
    arHelpImage( "store_uParam01" )
 
def faceLift_helpImage5( *pArgs ):
    arHelpImage( "lip_curveOnLoop02" )

def faceLift_helpImage6( *pArgs ):
    arHelpImage( "all_curveOnLoop02" )
    
def eyeRig_helpImage(*pArgs):
    arHelpImage( "createEyeRig" )

def skinEyeBall_helpImage(*pArgs):
    arHelpImage( "eyeBall_skinWeight01" )

def extraCrvCorrective_helpImage(*pArgs):
    arHelpImage( "extraCrv_corrective03" )
    
def BScorrective_reset_helpImage(*pArgs):
    arHelpImage( "fix_twitch_target02" )
    
def addTarget_helpImage(*pArgs):
    arHelpImage( "addTarget01" )
    
def wtCircle_helpImage(*pArgs):
    arHelpImage( "create_wtCircle02" )

def WideTightCrvBS_helpImage(*pArgs):
    arHelpImage( "wide_tightCrvBS01" )  

def bakeDelta_helpImage(*pArgs):
    arHelpImage( "copyRemodel_crv01" )

def crvAddReconnect_helpImage(*pArgs):
    arHelpImage( "crvAdd_reconnect02" )

def addCrvCorrective_helpImage(*pArgs):
    arHelpImage( "addCorrecitve_crv01" )
    
def transferCurve_helpImage(*pArgs):
    arHelpImage( "transferCurveBS02" )

def lipWireSetup_helpImage(*pArgs):
    arHelpImage( "lipWire_setup01" )
    
def cheekSculptHead_helpImage(*pArgs):
    arHelpImage( "cheekSculpt_head01" ) 

def squachBox_helpImage(*pArgs):
    arHelpImage( "squachBoxN01" ) 

def squachSetup_helpImage(*pArgs):
    arHelpImage( "squachSetup01" )

def nonTwitchSquach_helpImage(*pArgs):
    arHelpImage( "nonTwitchSquach03" )
    
def headGeo( *pArgs ):
    faceCompFunction.headGeo()

def setupLocator(*pArgs):
    faceCompFunction.setupLocator()


def plugNewHeadShape(*pArgs):
    mySel = cmds.ls( os =1, typ = "transform")
    plugHead = mySel[0]
    rigHead = mySel[1]
    faceCompFunction.plugNewHeadShape(plugHead, rigHead)

def updateHierachy( *pArgs ):
    faceCompFunction.updateHierachy()
    
def updateHierachy_FaceMain( *pArgs ):
    faceCompFunction.updateHierachy_FaceMain()

def updateHierachy_clsFaceMain( *pArgs ):
    faceCompFunction.updateHierachy_clsFaceMain()
    
    
def update_CtlsPlacement( *pArgs ):
    '''
    1. new faceGeo drives eyeGuide_crv
    2. eyeGuide_crv drives eyeCtl_poc 
    3. eyeCtl_poc drives eye ctl grp(corner A,B,C,D, corner)
    '''  
    prefix = ["l_up", "l_lo", "r_up", "r_lo" ]
    for pre in prefix:
        faceCompFunction.update_ctlConnection(pre)
        
    #reposition eyeCrv joints
    eyeCtls = cmds.listRelatives( "eyeOnCtl_grp", c=1 )
    crvJnts = cmds.listRelatives( "eyeCrvJnt_grp", c=1 )
    for i, ct in enumerate(eyeCtls):
        ctPos = cmds.xform( ct, q=1, ws=1, t=1 )
        cmds.setAttr( crvJnts[i] + ".t", ctPos[0], ctPos[1], ctPos[2] )

    #update browCtl placement?? if polyEdgeToCurve is on, no need to select 
    selCrv = cmds.ls(sl=1)
    if selCrv:
        print selCrv[0]
        selCrvShape = cmds.listRelatives( selCrv[0], c=1)[0]
        if cmds.nodeType(selCrvShape) == "nurbsCurve":
            faceCompFunction.update_browCtl(selCrv[0])
        
    #activate deformers back     
    for pre in ["l_","r_"]:
        
        blinkLevelCrv = pre + "BlinkLevelCrv"
        faceCompFunction.activateDeformers( blinkLevelCrv )
        for ud in [ "up","lo" ]:
            blinkCrv = pre + ud + "BlinkCrv01"
            targetCtlCrv = pre+ ud + "CTLCrv01"
            HiCrv = pre+ ud + "HiCrv01"
            faceCompFunction.activateDeformers( blinkCrv )
            faceCompFunction.activateDeformers( targetCtlCrv )
            print targetCtlCrv
            faceCompFunction.activateDeformers( HiCrv )
            
            crvBS = pre+ud + "Lid_bs"         
            if cmds.objExists(crvBS): 
                aliasAtt = cmds.aliasAttr(crvBS, q=1)            
                for tgt, wgt in zip(*[iter(aliasAtt)]*2):
                        cnnt = cmds.listConnections(  crvBS+"."+tgt, s=1, d=0, p=1 )[0]
                        if cnnt:
                            cmds.disconnectAttr( cnnt, crvBS+"."+tgt )
                        
                        cmds.setAttr( crvBS + "." + tgt, 1 )
                        copyCrv = cmds.duplicate ( targetCtlCrv, n= tgt )[0]
                        print copyCrv
                        cmds.parent(copyCrv, "eyeShapeCrv_grp")
                        copyCrvShape = cmds.listRelatives( copyCrv, c=1 )[0]
                        tgtID = wgt.split("[")[1][:-1]
                        cmds.connectAttr( copyCrvShape + ".worldSpace[0]", crvBS + ".inputTarget[0].inputTargetGroup[%s].inputTargetItem[6000].inputGeomTarget"%tgtID )
                        if cnnt:
                            cmds.connectAttr( cnnt, crvBS+"."+tgt )

        

def arFacePanel_transfer( *pArgs ):
    twitchPanelConnect.arFacePanel_transfer()

    
def browVerts( *pArgs ):
    faceCompFunction.browVerts()
    
def selectBrowVerts(*pArgs):
    faceCompFunction.selectBrowVerts()
    
    
def orderedUpLoVert( *pArgs ):
    currentName = cmds.optionMenu('eye_lip', query=True, value=True) 
    faceCompFunction.orderedVert_upLo(currentName)

def arFaceOrderedVert_upLo( *pArgs ):
    currentName = cmds.optionMenu('eye_lip', query=True, value=True) 
    faceCompFunction.rnkOrderedVert_upLo(currentName)
    
def upVertSel( *pArgs ):
    eyeLip = cmds.optionMenu('eye_lip', query=True, value=True)
    faceCompFunction.upVertSel( eyeLip )

def lowVertSel( *pArgs ):
    eyeLip = cmds.optionMenu('eye_lip', query=True, value=True)
    faceCompFunction.loVertSel( eyeLip )

def browJoints(*pArgs):
    faceCompFunction.browJoints()
    
def browWideJnt(*pArgs):
    faceCompFunction.browWideJnt()
    
#select "ctl guide curve", "controller"(both or either or none) 
def connectBrowCtrls(*pArgs):
    size = cmds.floatField( 'ctl_size', q=1, value = 1 ) 
    offset = cmds.floatField( 'ctl_offset', q=1, value = 1 )
    numOfCtl = cmds.optionMenu( 'numOfBrowCtl', query=True, value=True )
    mySel = cmds.ls(sl=1, typ ="transform")
    myCtl = ""
    polyEdgeCrv = ""
    if mySel:
        if len(mySel) == 2:
            polyEdgeCrv = mySel[0]
            myCtl = mySel[1]
            
        elif len( mySel ) == 1:
            cnnt = cmds.listHistory( mySel[0], pdo=1, lv=2  )
            if cnnt:
                polyEdgeCrv = mySel[0]
            else:
                myCtl = mySel[0]
                  
    crv = faceCompFunction.browCtl_onHead( int(numOfCtl), offset, size, polyEdgeCrv, myCtl )        
    faceCompFunction.connectBrowCtrls( int(numOfCtl), size, offset, crv )    

        
def browUpDownReverse(*pArgs):
    faceCompFunction.browUpDownReverse()


def eyelidJoints(*pArgs):
	prefix = ["l_up", "l_lo"] 
	for pre in prefix:
		faceCompFunction.eyelidJoints( pre )
        
       
def eyeCtlCrv(*pArgs):

    numEyeCtl = cmds.optionMenu( 'numOfEyeCtls', query=True, value=True )
    offset = cmds.floatField( 'eyeCtlOffset', q=1, value = 1 )  
    print offset
    prefix = ["l_up", "l_lo", "r_up", "r_lo"] 
    for pre in prefix:
    
        faceCompFunction.eyeHiCrv( pre )       
        faceCompFunction.eyeCtrls( pre, int(numEyeCtl),offset )
    faceCompFunction.eyeCtlCrv()
    
    
def eyeCrvConnect(*pArgs):
    prefix = ["l_", "r_"]
    for pre in prefix:
        faceCompFunction.eyeCrvConnect( pre )

    preName = ["l_up", "l_lo", "r_up", "r_lo" ]
    for prx in preName:
        faceCompFunction.wideLid_setup(prx )
    faceCompFunction.eyeWideJntLabel()


def compensateStickyCtl(*pArgs):    
    grp = cmds.ls( sl=1, typ = "transform" )[0]
    faceCompFunction.compensateStickyCtl( grp )    
    
def mouthJoint(*pArgs ):
    numCtls = cmds.optionMenu( "numOfLipCtl", q =1, value = 1 )
    for ud in ["up","lo"]:
        faceCompFunction.mouthJoint( ud, int(numCtls) )
    faceCompFunction.setLipJntLabel()


#numCtls = number of freeform ctls
def jawCrvConnect(*pArgs ):
    faceCompFunction.faceFactorFix()
    numCtls = cmds.optionMenu( "numOfLipCtl", q =1, value = 1 )
    for ud in ["up","lo"]:        
        faceCompFunction.mouthCrvToJoint( ud ) #connect crv's poc to jaw_jnts  
        faceCompFunction.lipCtlSetup( ud, int(numCtls) ) #create "lipBS_grp" /"_lipBS_crv" blendShape /crv joints


def jawCtl_setup(*pArgs ):
    faceCompFunction.indieCrvSetup()#lipBS /jawDrop/Open Crv with "joints" setup (check if expression on upMid_jawOpen )
    faceCompFunction.jawOpenDrop_setup()
    faceCompFunction.swivel_ctrl_setup()
    faceCompFunction.mouth_move_setup()



def lipFreeCtl(*pArgs ):
  
    numCtls = cmds.optionMenu( 'numOfLipCtl', q =1, value = 1 )
    offset = cmds.floatField( 'lipCtlOffset', q=1, value = 1 ) 
    mySel = cmds.ls(sl=1)
    if len(mySel)==1:
        shp = cmds.listRelatives( mySel, ad=1 )
        if shp:
            if cmds.nodeType(shp[0]) == "nurbsCurve":
                
                customCtl= cmds.listRelatives( shp, p=1 )[0]
                cmds.parent( customCtl, w=1 )
            else:
                cmds.confirmDialog( title='Confirm', message="select custom controller" )
        else:
            cmds.confirmDialog( title='Confirm', message="select custom controller" )
    else:
        customCtl = ""
    
    for i, ud in enumerate(["up","lo"]):
     
        faceCompFunction.lipFreeCtl( ud, int(numCtls), offset, customCtl )
                
    #faceCompFunction.lipPuff_crvSetup( int(numDetail) )
    

def changeClsWeightNode(*pArgs):
    faceCompFunction.changeClsWeightNode() 


def createPntNull(*pArgs):
    mySelList = cmds.ls( sl=1, typ = "transform" )
    faceCompFunction.createPntNull( mySelList )    


def transferCurveBS( *pArgs ):
    name = cmds.textField( 'crvWire_name', query=True, text=True )
    curvs = cmds.ls( os=1 )
    # curve with blendShape
    srcCrv = curvs[0]
    # newly created wire curve based on srcCrv uParam 
    tgtCrv = curvs[1]  
    
    blendShapeMethods.transferCurveBS( srcCrv, tgtCrv, name )


def bakeCrvDeltaBS(*pArgs):
    name = cmds.textField( 'crvWire_name', query=True, text=True )
    curvs = cmds.ls( os=1 )
    # curve with blendShape
    srcCrv = curvs[0]
    # newly created wire curve based on srcCrv uParam 
    tgtCrv = curvs[1]    
    blendShapeMethods.bakeCrvDeltaBS( srcCrv, tgtCrv, name ) 


def dnCrv_srcUParam(*pArgs):
    crvSel = cmds.ls(sl=1)
    if crvSel:
        scCrv = crvSel[0]
        dnCrv = crvSel[1]
    else:
        print "select source curve and target curve"        
    name = cmds.textField( 'crvWire_name', query=True, text=True )
    faceCompFunction.dnCrv_srcUParam( scCrv, dnCrv, name )


def create_wtCircle(*pArgs):

    blendShapeMethods.create_wtCircle()
    
def WideTight_crvBS(*pArgs):

    blendShapeMethods.WideTight_crvBS()
    
    
def lipWire_setup(*pArgs):

    blendShapeMethods.lipWire_setup()

def cheekSculpt_head(*pArgs):    
    
    #check to see if window exists
    if cmds.window ('blendShapeListUI', exists = True):
        cmds.deleteUI( 'blendShapeListUI')

    #create window
    window = cmds.window( 'blendShapeListUI', title = 'blendShapeList', w = 300, h =200, mnb = True, mxb = True, sizeable=True, resizeToFitChildren = True )

    #main layout
    mainLayout = cmds.columnLayout( w =400, h= 200)
    cmds.text( label = '')
    cmds.text( label = '')
    #rowColumnLayout
    cmds.rowColumnLayout( numberOfColumns = 2, columnWidth = [(1, 100),(2, 120) ], columnOffset = [(1, 'right', 10)] )
    
    cmds.text( label = '')
    cmds.text( label = 'blendShape list')

    cmds.separator( h = 15)
    cmds.separator( h = 15)
    
    baseGeo = cmds.ls(sl=1)[-1]
    dformers = [ x for x in cmds.listHistory( baseGeo, il=1, pdo=1) if "geometryFilter" in cmds.nodeType( x, inherited=1)]
    
    cmds.text( label = '')
    option = cmds.optionMenu('blendShape_list', changeCommand= printNewMenuItem )
    for dform in dformers:
        if cmds.nodeType(dform) == "blendShape":
            cmds.menuItem( label= dform )
    cmds.text( label = '')
    cmds.text( label = '')    
    cmds.text( label = '')        
    cmds.button( label = 'cheek sculpt head', bgc=[.42,.5,.60], command = cheekSculpt_func )
    
    cmds.showWindow(window)
    
def cheekSculpt_func(*pArgs):
    bsNode = cmds.optionMenu( 'blendShape_list', query=True, value=True) 
    blendShapeMethods.cheekSculpt_func(bsNode)


def browWire_setup(*pArgs):
    
    blendShapeMethods.browWire_setup()    
    
def shapeToCurve(*pArgs):
    faceCompFunction.shapeToCurve()
    
def curve_halfVerts( *pArgs ):
    openClose = cmds.optionMenu('openClose', query=True, value=True )
    degree = cmds.optionMenu('degree', query=True, value=True )    
    item = cmds.optionMenu('mapName', query=True, value=True )
    character = cmds.optionMenu('crvCharacterName', query=True, value=True )
    name = item + character
    trackSelectionOrder = cmds.selectPref( q=1, tso=1 )
    if trackSelectionOrder == False:
        cmds.confirmDialog( title='Confirm', message='the trackSelectionOrder should be on in preference' )
    
    myVert = cmds.ls( os=1, fl=1 )  
    faceCompFunction.curve_halfVerts( myVert, name, openClose, degree )
   
def store_uParam(*pArgs):
    wireCrv = cmds.ls(sl=1, typ = 'transform')[0]
    title = cmds.optionMenu('mapName', query=True, value=True )
    faceCompFunction.store_uParam( wireCrv, title )

def browMapSurf(*pArgs):
    faceCompFunction.browMapSurf()
    
def loftMapSurf(*pArgs):
    faceCompFunction.loftMapSurf()

def curveOnLoop( facePart, *pArgs ):
    currentValue = cmds.optionMenu('facePart', query=True, value=True)
    faceCompFunction.curveOnEdgeLoop(currentValue)

def edgeSelection( facePart, *pArgs ):
    currentValue = cmds.optionMenu('facePart', query=True, value=True)
    faceCompFunction.edgeSelection(currentValue)
    
def curveOnEdgeSelection( facePart, *pArgs ):
    currentValue = cmds.optionMenu('facePart', query=True, value=True)
    faceCompFunction.curveOnEdgeSelection(currentValue)
    
def seriesOfEdgeLoopCrv( *pArgs ):
    currentValue = cmds.optionMenu('facePart', query=True, value=True)
    faceCompFunction.seriesOfEdgeLoopCrv(currentValue)

def symmetrizeOpenCrv( *pArgs ):
    check = cmds.checkBox( 'direction', query=True, value = True)
    print check
    faceCompFunction.symmetrizeOpenCrv(check) 
    
def symmetrizeLipCrv( *pArgs ):
    check = cmds.checkBox( 'direction', query=True, value = True)
    print check
    faceCompFunction.symmetrizeLipCrv(check)
    
def loftFacePart( *pArgs ):
    currentValue = cmds.optionMenu('facePart', query=True, value=True)
    faceCompFunction.loftFacePart( currentValue )   

def browMapSkin( *pArgs ):
    faceCompFunction.browMapSkinning()

def rnkBrowMapSkinning( *pArgs ):
    faceCompFunction.rnkBrowMapSkinning() 

def lipMapSkinning( *pArgs ):
    faceCompFunction.lipMapSkinning()

    
def eyeMapSkin(*pArgs):
    faceCompFunction.eyeMapSkinning()
    
   
#face skinning tab
def eyeBallDirection( *pArgs ):
    faceSkinFunction.eyeBallDirection() 

def createEyeRig( *pArgs ):
    #create eyeDecomposeNull 
    #place them under supportRig if lattice will apply 
    faceSkinFunction.createEyeRig()

    #aimConstraint to the eyeAim_ctl
    faceSkinFunction.eyeBallDirection()
    
    #eyeWide cluster for offset and scale
    faceSkinFunction.eyeLidOffset_scale()
    
    #eyeShape control( blendShape to lidPush, blink, squint)  
    faceSkinFunction.lidPush_blink_squint()
    
def eyeLidOffset_scale( *pArgs ):
    faceSkinFunction.eyeLidOffset_scale()


def jointSkinEyeBall( *pArgs ):
    faceSkinFunction.jointSkinEyeBall()

#select eyeBall with blendShape
def irisPupilSetup( *pArgs ):
    faceCompFunction.irisPupilSetup()     
    
def detailOnOff( *pArgs ):
    faceSkinFunction.detailOnOff()    


def deleteCtrlKeys(*pArgs):
    facePart = cmds.optionMenu('face_area', query=True, value=True)
    twitchPanelConnect.deleteCtrlKeys(facePart)


def selectCtrl(*pArgs):
    facePart = cmds.optionMenu('face_area', query=True, value=True)
    twitchPanelConnect.selectCtrl(facePart)
    
    
def faceClusters( *pArgs ):
    faceSkinFunction.faceClusters()    

def deleteClusterLayer( *pArgs ):
    faceSkinFunction.deleteClusterLayer()

def updateFaceCluster( *pArgs ):
    faceSkinFunction.updateFaceCluster()

    
#set project first
#select mesh with clusters and run
def exportClsWgt( *pArgs ):
    faceSkinFunction.exportClsWgt( )


###create pop up window for import directory
def importClsWgt(*pArgs ):
    #pathProject = cmds.workspace(  q=True, rd = True )
    faceSkinFunction.importClsWgt()


def weightedVerts(*pArgs):

    clsName = cmds.optionMenu('clusterName', query=True, value=True)
    obj = cmds.ls(sl=1, type = 'transform')[0]
    if cmds.objExists(obj):
        faceSkinFunction.weightedVerts(obj, clsName)
    else:
        cmds.warning("select object!!")
        
def copyClusterWgt(*pArgs):
    sdCls = cmds.optionMenu('clusterName', query=True, value=True)
    ddCls = cmds.optionMenu('ddClusterName', query=True, value=True)
    print sdCls, ddCls
    faceSkinFunction.copyClusterWgt(sdCls, ddCls)

def printNewMenuItem( item ):
    print item


def faceControls(*pArgs):
    from twitchScript import faceControls
    reload(faceControls)
    faceControls.faceControlsUI()

def arFaceSelection(*pArgs):
    from twitchScript import arFaceSelection
    reload(arFaceSelection)
    arFaceSelection.faceControlsUI()
    
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
        

def deformerToggle(*pArgs):
    faceSkinFunction.deformerToggle()

def zeroOutCluster(*pArgs):
    faceSkinFunction.zeroOutCluster()

def rnkFaceWeightCalculate(*pArgs):
	faceSkinFunction.rnkFaceWeightCalculate()
	
def rnkCopyJawOpenWeight(*pArgs):
	faceSkinFunction.rnkCopyJawOpenWeight()

def rnkSplitBSWeight(*pArgs):
	weightSize = cmds.optionMenu('weight_scale', query=True, value=True)
	faceSkinFunction.rnkSplitBSWeight( int(weightSize) )
	
def copyBSWeight(*pArgs):
	weightSize = cmds.optionMenu('weight_scale', query=True, value=True) 
	faceSkinFunction.copyBSWeight( int(weightSize) )
	    
   
def headSkin(*pArgs):
    geoName = cmds.ls(sl=1, typ = "transform")
    if geoName:
        faceSkinFunction.headSkinObj(geoName)
    else:
        cmds.confirmDialog( title='Confirm', message='select geo for headSkinning' )
        
def arFaceHeadSkin(*pArgs):
    geoName = cmds.textField( 'headGeoName', query=True, text=True )
    faceSkinFunction.arFaceHeadSkin(geoName)

def copyTrioSkinWeights(*pArgs):
    faceSkinFunction.copyTrioSkinWeights()

def exportTrioSkinWgt(*pArgs):
    faceSkinFunction.exportTrioSkinWgt()
    
def exportLipMap(*pArgs):
    faceSkinFunction.exportLipMap()    
    
def exportEyeLidMap(*pArgs):
    faceSkinFunction.exportEyeLidMap()    
    
def exportBrowMap(*pArgs):
    faceSkinFunction.exportBrowMap()    

def faceWeightCalculate(*pArgs): 
    faceSkinFunction.faceWeightCalculate()

def mouth_pivotChange(*pArgs):
    faceSkinFunction.mouth_pivotChange()

def switchJntToCls(*pArgs):
    prefix = [ "l_up","l_lo", "r_up","r_lo"]
    geo = cmds.ls(sl=1, typ = "transform" )[0]
    for pre in prefix:
        faceSkinFunction.switchJntToCls(pre, geo)
        
def copyExportEyeSkinWeights(*pArgs):
    faceSkinFunction.copyExportEyeSkinWeights()    
    

def eyeWeightCalculate(*pArgs):
    faceSkinFunction.eyeWeightCalculate()      


def eyeLidCrvIsolate(*pArgs):
    crvTitle = cmds.optionMenu( 'eyeLid_crv', query=True, value=True)
    blendShapeMethods.eyeLidCrvIsolate( crvTitle )

def lipCrvIsolate(*pArgs):
    lipTitle = cmds.optionMenu( 'lip_crv', query=True, value=True)
    blendShapeMethods.lipCrvIsolate( lipTitle )    
    
def browCrvIsolate(*pArgs):
    browTitle = cmds.optionMenu( 'brow_crv', query=True, value=True)
    blendShapeMethods.browCrvIsolate( browTitle )

def copyCurveShape(*pArgs):
    faceSkinFunction.copyCurveShape()

def mirrorCurveShape(*pArgs):
    faceSkinFunction.mirrorCurveShape()
    
def mirror_eyeLidShape(*pArgs):
    currentName = cmds.optionMenu('ABCD', query=True, value=True)
    if currentName == "lookUp":
        ABCD = ["A","B"]
    elif currentName == "lookDown":
        ABCD = ["C","D"]    
    faceSkinFunction.mirror_eyeLidShape(ABCD)

def correctiveCrv( *pArgs ):
    browLip = cmds.optionMenu('browLip', query=True, value=True) 
    blendShapeMethods.correctiveCrv( browLip )
    
def lipCornerCls(*pArgs):
    faceSkinFunction.lipCornerCls() 

def faceClsMirrorWgt(*pArgs):
    faceSkinFunction.faceClsMirrorWgt() 

def indieClsWeightMirror(*pArgs):
    clsName = cmds.optionMenu('select_cluster', query=True, value=True)
    faceSkinFunction.indieClsWeightMirror( clsName )

def squachBoxForLattice( *pArgs ):
    jntLenNum = cmds.intField( 'joint_length', q=1, value = 1 )    
    squachSetup.squachBoxForLattice(jntLenNum)
    
def squachFunction(*pArgs):
    jntLenNum = cmds.intField( 'joint_length', q=1, value = 1 )    
    squachSetup.squachSetup(jntLenNum)

def copyBoxSkinToLattice(*pArgs): 
    squachSetup.copyBoxSkinToLattice()
   
def addSquachGeo(*pArgs):
    dformer = cmds.optionMenu( 'lattice_jnt', q=1, value = 1 )  
    squachSetup.addSquachGeo(dformer)

def nonTwitchSquachRig(*pArgs):
    jntLenNum = cmds.intField( 'joint_length', q=1, value = 1 )
    name = cmds.textField( 'objName', query=True, text=True )
    bendDirect = cmds.optionMenu( 'bendDirection', q=1, value = 1 )     
    squachSetup.nonTwitchSquachRig(jntLenNum, bendDirect, name )
    
def connectFaceCluster(*pArgs):
    twitchPanelConnect.ctrlConnectFaceCluster()

def splitBSWeightMap( *pArgs ):
    blendShapeMethods.splitBSWeightMap() 

def createTwitchBS( *pArgs ):
    blendShapeMethods.createTwitchBS()

def updateWeight( *pArgs ):
    splitRange = cmds.optionMenu('split_range', query=True, value=True)
    blendShapeMethods.updateWeight( splitRange )

def addTarget( *pArgs ):
    splitRange = cmds.optionMenu('split_range', query=True, value=True)
    targetType = cmds.optionMenu('target_type', query=True, value=True)
    blendShapeMethods.addTarget( splitRange, targetType )

def extraCrvShape_corrective(*pArgs):
    xyz = cmds.optionMenu('xyzAxis', query=True, value=True)
    plusName = cmds.textField('plusTarget_name', query=True, text=True )
    minusName = cmds.textField('minusTarget_name', query=True, text=True )
    splitRange = cmds.optionMenu('split_range', query=True, value=True)
    mySel = cmds.ls( sl=1, typ = "transform" )
    blendShapeMethods.extraCrvShape_corrective( mySel, xyz, plusName, minusName, splitRange )

# if not for twitchBS, select the objects with BS
def simpleCtl_bsConnect(*pArgs):
    xyz = cmds.optionMenu('xyzAxis', query=True, value=True)
    plusName = cmds.textField('plusTarget_name', query=True, text=True )
    minusName = cmds.textField('minusTarget_name', query=True, text=True )
    splitRange = cmds.optionMenu('split_range', query=True, value=True)
    mySel = cmds.ls( sl=1, typ = "transform" )
    blendShapeMethods.simpleCtl_bsConnect( mySel, xyz, plusName, minusName, splitRange)
    
def ctrlConnectBS(*pArgs):
    blendShapeMethods.ctrlConnectBS() 

def splitXYZ(*pArgs):
    blendShapeMethods.splitXYZ()
    
def fixTwitchTarget(*pArgs):
    blendShapeMethods.fixTwitchTarget()
    
def resetForCorrectiveFix(*pArgs):
    blendShapeMethods.resetForCorrectiveFix()
    
def createBrowCorrective(*pArgs):
    posMax = cmds.intField("upMax", q=1, v=1 )
    negMax = cmds.intField("downMax", q=1, v=1 )
    inMax = cmds.intField("inMax", q=1, v=1 )
    outMax = cmds.intField("outMax", q=1, v=1 )    
    blendShapeMethods.createBrowCorrective(posMax, negMax, inMax, outMax )

def updateRemapMax(*pArgs):
    posMax = cmds.intField("upMax", q=1, v=1 )
    negMax = cmds.intField("downMax", q=1, v=1 )
    inMax = cmds.intField("inMax", q=1, v=1 )
    outMax = cmds.intField("outMax", q=1, v=1 )    
    blendShapeMethods.updateRemapMax(posMax, negMax, inMax, outMax )
    
def fixMix(*pArgs):
    blendShapeMethods.fixMix()     

'''
def getListOfBlendShape(*pArgs):
    
    window = cmds.window()
    cmds.columnLayout()
    cmds.optionMenu( label='BS_list', changeCommand=printNewMenuItem )
    bsList = blendShapeMethods.getListOfBlendShape()
    for bs in bsList:
        cmds.menuItem( label= bs )
    cmds.showWindow( window )'''
    
def targetAdd_Reconnect(*pArgs):    
    
    #check to see if window exists
    if cmds.window ('blendShapeListUI', exists = True):
        cmds.deleteUI( 'blendShapeListUI')

    #create window
    window = cmds.window( 'blendShapeListUI', title = 'blendShapeList', w = 300, h =200, mnb = True, mxb = True, sizeable=True, resizeToFitChildren = True )

    #main layout
    mainLayout = cmds.columnLayout( w =400, h= 200)
    cmds.text( label = '')
    cmds.text( label = '')
    #rowColumnLayout
    cmds.rowColumnLayout( numberOfColumns = 2, columnWidth = [(1, 100),(2, 120) ], columnOffset = [(1, 'right', 10)] )
    
    cmds.text( label = '')
    cmds.text( label = 'blendShape list')

    cmds.separator( h = 15)
    cmds.separator( h = 15)
    
    baseGeo = cmds.ls(sl=1)[-1]
    dformers = [ x for x in cmds.listHistory( baseGeo, il=1, pdo=1) if "geometryFilter" in cmds.nodeType( x, inherited=1)]
    
    cmds.text( label = '')
    option = cmds.optionMenu('blendShape_list', changeCommand= printNewMenuItem )
    for dform in dformers:
        if cmds.nodeType(dform) == "blendShape":
            cmds.menuItem( label= dform )
    cmds.text( label = '')
    cmds.text( label = '')    
    cmds.text( label = '')        
    cmds.button( label = 'target Add/Reconnect', bgc=[.42,.5,.60], command = targetAddReconnect_func )
    
    cmds.showWindow(window)


    
def targetAddReconnect_func(*pArgs):
    bsNode = cmds.optionMenu( 'blendShape_list', query=True, value=True)
    print bsNode
    blendShapeMethods.targetAdd_Reconnect( bsNode )

def crvAdd_reconnect(*pArgs):
    myCrvs = cmds.ls(sl=1)
    blendShapeMethods.crvAdd_reconnect( myCrvs )

def addCrv_corrective(*pArgs):
    crvs = cmds.ls(sl=1, typ = "transform")
    blendShapeMethods.addCrv_corrective(crvs )
 
def bakeTarget_reconnect(*pArgs):
    crvSel = cmds.ls(sl=1, typ ='transform')
    baseCrv = crvSel[0]
    blendShapeMethods.bakeTarget_reconnect(baseCrv)

def propagateFix_setup(*pArgs):
    mySel = cmds.ls( os=1, typ = "transform")
    target = mySel[0]
    base = mySel[1]
    blendShapeMethods.propagateFix_setup( target, base )
    
def propagateGap(*pArgs):
    mySel = cmds.ls(os=1, typ = "transform")
    newTarget = mySel[0]
    oldTarget = mySel[1]
    blendShapeMethods.propagateGap( newTarget, oldTarget )
    
def upTeethSetup(*pArgs):
    faceSkinFunction.teethSetup("up")

def loTeethSetup(*pArgs):
    faceSkinFunction.teethSetup("lo")      

def tongueSetup(*pArgs):
    faceSkinFunction.tongueSetup()    

def jawRigDetailCrv(*pArgs):
    faceSkinFunction.jawRigDetailCrv()  

def lipTzSetup(*pArgs):
    faceSkinFunction.cornerLipLevel()
    faceSkinFunction.lipCornerTZSetup()

def dial_lipFactor(*pArgs):
    faceSkinFunction.dial_lipFactor()
    
def lipThinningSetup(*pArgs):
    faceSkinFunction.lipThinningSetup()

def attachTwitchHead():
    faceSkinFunction.attachTwitchHead()
    
def dgTimer(*pArgs):
    faceSkinFunction.dgTimer()    

def renameDuplicates(*pArgs):
    faceSkinFunction.renameDuplicates() 

def deleteUnknown_plugins(*pArgs):
    faceSkinFunction.deleteUnknown_plugins()


#no translate freeze. swap in world space
def ctlShapeTransfer( *pArgs ):
    faceCompFunction.ctlShapeTransfer()


#select geo and ctls
def stickCtlToFace( *pArgs ):
    sel = cmds.ls( sl=1 )
    obj = sel[0]
    ctls = sel[1:]
    faceCompFunction.stickCtlToFace( obj, ctls )

def controller(*pArgs):
    ctlName = 'ctl'
    obj = cmds.ls(sl=1)[0]
    position = cmds.xform( obj, q=1, ws=1, t=1 )
    shapeValue = cmds.optionMenu('ctlShape', query=True, value=True)
    radius = cmds.floatField( 'ctl_size', q=1, value = 1 )
    colorID = cmds.floatField( 'ctl_color', q=1, value = 10 )
    print ctlName, position, shapeValue, radius, colorID
    faceSkinFunction.genericController( ctlName, position, radius, shapeValue, colorID ) 

def multiInputConnect(*pArgs):
    currentValue = cmds.optionMenu('tform', query=True, value=True)
    faceCompFunction.multiInputConnect(currentValue)


def transferConnections(*pArgs):
    node_shape = cmds.optionMenu('node_shape', query=True, value=True)
    in_out = cmds.optionMenu('in_out', query=True, value=True)
    twitchPanelConnect.transferConnections( node_shape, in_out )
    
'''
from twitchScript import SWbrowSetup01 
reload( SWbrowSetup01 )
SWbrowSetup01.connectBrowCtrls ( .2, .3 )
SWbrowSetup01.browDetailCtls()
SWbrowSetup01.browWideJnt()


from twitchScript import SWeyeLidSetup01 
reload( SWeyeLidSetup01 )
SWeyeLidSetup01.createEyeRig()
SWeyeLidSetup01.jumperPanel()
SWeyeLidSetup01.lidDetailCtl()
SWeyeLidSetup01.eyeLidsCrvs( 1 )#eyeLid Ctl on Face 
SWeyeLidSetup01.eyeCtl_EXP()
SWeyeLidSetup01.eyeCrvToJnt() 
SWeyeLidSetup01.blinkRemap()'''
