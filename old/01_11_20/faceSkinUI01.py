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
    window = cmds.window( 'faceSkinUI', title = 'faceSkin UI', w =420, h =900, mnb = True, mxb = True, sizeable=True, resizeToFitChildren = True )

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
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.button( label = 'head geo', bgc=[.42,.5,.60], command = headGeo )
    cmds.text( label = '')
    
    cmds.text( label = '')
    cmds.text( label = "when loc pos change" )
    cmds.text( label = "/ hierachy not match")
    cmds.text( label = '')
    cmds.button( label = 'update hierachy', bgc=[.42,.5,.60], command = updateHierachy, ann = "when locators (headSkel, cheek, nose, ears) position update, do it before creating skinning" )
    cmds.text( label = '')
    
    cmds.separator( h = 15)    
    cmds.separator( h = 15)
    cmds.separator( h = 15)

    cmds.text( label = '')
    cmds.text( label = '')
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
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.button( label = 'rnkOrderedVerts', bgc=[.42,.5,.60], command = rnkOrderedVert_upLo )
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
    cmds.text( label = '')
    cmds.text( label = '')
    

    cmds.text( label = '')
    cmds.text( label = 'Brow Setup', bgc = [.12,.2,.30], fn = "boldLabelFont",height= 20 )
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = 'ctrl size/offset:')
    sizeField = cmds.floatField( "browCtlSize", value = .2 )
    offsetField = cmds.floatField( "browCtlOffset", value = .2 )
    cmds.text( label = 'brow joint:' )
    cmds.button( label = 'browJoints', bgc=[.42,.5,.60], command = browJoints )
    cmds.text( label = '')
    cmds.text( label = 'brow ctls:')
    cmds.optionMenu('numOfBrowCtl', bgc=[.42,.5,.60], changeCommand= printNewMenuItem )
    cmds.menuItem( label='5' )
    cmds.menuItem( label='7' )
    cmds.menuItem( label='9' )
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.button( label = 'connect Brow ctrl', bgc=[.42,.5,.60], command = connectBrowCtrls )
    cmds.button( label = 'twitch Brow ctrl', bgc=[.42,.5,.60], command = connectBrowCtrls )
    
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
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
    cmds.text( label = 'Eye joint:' )
    cmds.button( label = 'eyelid Joints', bgc=[.42,.5,.60], command = eyelidJoints )
    cmds.button( label = 'eyeHiCurves', bgc=[.42,.5,.60], command = eyeHiCrv )
    cmds.text( label = 'num of ctls/ offset:')
    cmds.optionMenu( "numOfEyeCtls", bgc=[.42,.5,.60], changeCommand= printNewMenuItem )   
    cmds.menuItem( label=3 )
    cmds.menuItem( label=5 )
    cmds.menuItem( label=7 )
    offsetField = cmds.floatField( "eyeCtlOffset", value = .5 )
    cmds.text( label = '')
    cmds.text( label = '          shape CTLCrv to')
    cmds.text( label = 'the HiCrv first!!          ')
    cmds.text( label = '')
    cmds.button( label = 'eyeCtlCurves', bgc=[.42,.5,.60], command = eyeCtlCrv )
    cmds.button( label = 'eyeCrvConnect', bgc=[.42,.5,.60], command = eyeCrvConnect )
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
    cmds.text( label = 'num of lipCtl' )
    cmds.text( label = 'num of Dtail')

    cmds.text( label = 'lip ctls:')
    cmds.optionMenu('numOfLipCtl', bgc=[.42,.5,.60], changeCommand= printNewMenuItem )
    cmds.menuItem( label='5' )
    cmds.menuItem( label='7' )
    cmds.menuItem( label='9' )
    cmds.menuItem( label='11' )

    cmds.button( label = 'jawJoints', bgc=[.42,.5,.60], command = jawJoints )
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = 'poc to jnt /create ctlJnt')
    cmds.text( label = 'import lipCtrls first!')
    cmds.text( label = 'crv to jnt')
    cmds.button( label = 'jawCrvConnect', bgc=[.42,.5,.60], command = jawCrvConnect )     
    cmds.button( label = 'jawCtl_setup', bgc=[.42,.5,.60], command = jawCtl_setup )
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = 'ctl offset')
    cmds.text( label = '   create polyToCurves!')
    cmds.text( label = '   select up_crv first! ')
    offsetField = cmds.floatField( "lipCtlOffset", value = .5 )
    cmds.optionMenu('numOfDtailCtl', bgc=[.42,.5,.60], changeCommand= printNewMenuItem )
    cmds.menuItem( label='11' )
    cmds.menuItem( label='13' )
    cmds.menuItem( label='15' )
    cmds.menuItem( label='17' )
    cmds.menuItem( label='19' )
    cmds.button( label = 'freeform_setup', bgc=[.42,.5,.60], command = freeform_setup )
    cmds.separator( h = 15)    
    cmds.separator( h = 15)
    cmds.separator( h = 15)
        
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')

         
    cmds.setParent( '..' )
    
    #2nd tab "face lift"
    child2= cmds.rowColumnLayout( numberOfColumns = 3, bgc=[.3,.22,.2], columnWidth = [(1, 140),(2, 120),(3, 120)], columnOffset = [(1, 'right', 5)] )
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = 'Face Clusters', bgc = [.2,.15,.15], fn = "boldLabelFont",height= 20 )
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    
    cmds.separator( h = 15)  
    cmds.text( label = '')
    cmds.text( label = 'select face locator')   
    cmds.text( label = 'SkinWeight Help:')
    cmds.button( label = 'Face Clusters', command = faceClusters )
    cmds.button( label = 'update clsPivot', command = updateFaceCluster )
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = 'select geometry!!')
    
    cmds.separator( h = 15)
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
    cmds.text( label = '')
    cmds.text( label = '')
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
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.button( label = 'exportClsWgt', command = exportClsWgt )
    cmds.button( label = 'importClsWgt', command = importClsWgt )
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    
    cmds.text( label = 'Toggle Deform:')
    cmds.button( label = 'toggleDeform', command = deformerToggle  )
    cmds.button( label = 'zero Cls', command = zeroOutCluster  )
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.separator( h = 15)

    
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')    

    #brow map Surf
    cmds.text( label = '')
    cmds.text( label = 'Brow Map', bgc = [.2,.15,.15], fn = "boldLabelFont",height= 20 )
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = 'vtx type            ')    
    cmds.text( label = 'curve open/close')
    cmds.text( label = 'degree')

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
    cmds.text( label = 'select left halfVerts')
    cmds.text( label = 'select crvs in order')

    cmds.text( label = '')
    cmds.button( label = 'curve_halfVerts', command = curve_halfVerts )
    cmds.button( label = 'browMapSurf', command = browMapSurf ) 
    cmds.separator( h = 15)    
    cmds.separator( h = 15)
    cmds.separator( h = 15)

    cmds.text( label = 'browFactor:')    
    if cmds.objExists("browFactor"):
        if cmds.attributeQuery("browUp_scale", node = "browFactor", exists=1)==True:
            browRxField = cmds.intField( value = cmds.getAttr('browFactor.browUp_scale'))
            browRyField = cmds.intField( value = cmds.getAttr('browFactor.browRotateY_scale'))
    else: 
        browRxField = cmds.intField( value = 20 )
        browRyField = cmds.intField( value = 10 )    
    
    cmds.text( label = '')
    cmds.button( label = 'loft MapSurf', command = loftMapSurf )
    cmds.text( label = '')
    cmds.text( label = '')

    cmds.button( label = 'browSurfMapSkin', command = browMapSkin )
    cmds.button( label = 'rnk_browSurfMapSkin', command = rnkBrowMapSkinning )

    cmds.separator( h = 15)    
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')    
    #eye/ lip map Surf
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = 'Eye/Lip map', bgc = [.2,.15,.15], fn = "boldLabelFont",height= 20 )
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.separator( h = 15)  
    cmds.text( label = 'select facePart first!!')
    cmds.text( label = '')
    
    cmds.text( label = 'Eye/Lip Curve')
    cmds.optionMenu('facePart', bgc=[0,0,0], changeCommand=printNewMenuItem )
    cmds.menuItem( label='eye' )
    cmds.menuItem( label='lip' )
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '2vtx (corner/vector)')
    cmds.text( label = 'cornerVtxs/vector vtx')
    cmds.text( label = 'select vertices')
    cmds.button( label = 'curveOnLoop', command = curveOnLoop )
    cmds.button( label = 'all curves loop', command = curvesOnLoop )

    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')   

    cmds.text( label = 'mirror direction')
    cmds.text( label = 'select open curve')
    cmds.text( label = 'select loop curve')
    
    
    cmds.checkBox( 'direction', label='+To-' ) 
    cmds.button( label = 'symmetryOpenCrv', command = symmetrizeOpenCrv )  
    cmds.button( label = 'symmetryLipCrv', command = symmetrizeLipCrv )

    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')    
    cmds.separator( h = 15)    
    cmds.text( label = 'manually select edges')
    cmds.text( label = 'corner/vector 2 verts')
    cmds.text( label = 'manual curve')     
    cmds.button( label = 'edgeSelection', command = edgeSelection ) 
    cmds.button( label = 'curveOnEdgeSel', command = curveOnEdgeSelection )
    cmds.separator( h = 15)    
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.separator( h = 15)    
    cmds.text( label = 'select crvs in order')
    cmds.text( label = 'select 2vtx /shape crv')  
    cmds.text( label = 'MapSurface:' )
    cmds.button( label = 'loftFacePart', command = loftFacePart )
    cmds.text( label = '')
    cmds.separator( h = 15)    
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = 'Map Skinning', bgc = [.2,.15,.15], fn = "boldLabelFont",height= 20 )
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    
    cmds.text( label = 'LipMapSurface:')
    cmds.button( label = 'lipSurfMapSkin', command = lipMapSkinning  )
    cmds.button( label = 'rnk_lipSurfMapSkin', command = rnkLipMapSkinning  )
    cmds.text( label = 'eyeMapSurface:')
    cmds.button( label = 'eyeSurfMapSkin', command = eyeMapSkin  )
    cmds.button( label = 'rnk_eyeSurfMapSkin', command = rnkEyeMapSkinning  )
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    
    cmds.text( label= 'face Lift' ) 
    cmds.button( label = 'faceLift', command = faceLift ) 
    cmds.text( label = '')    
    cmds.setParent( '..' )
    
    child3= cmds.rowColumnLayout( numberOfColumns = 3, columnWidth = [(1, 140),(2, 120),(3, 120)], columnOffset = [(1, 'right', 5)] )
    '''import sys
    sys.path.append('c:/Users/sshin/Documents/maya/2016/scripts/twitchScript')'''
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')    
    cmds.text( label = '')
    cmds.text( label = 'creat eye rig' )
    cmds.text( label = 'eye direction Offset')
    cmds.text( label = 'Eye Rig')
    cmds.button( label = 'create Eye Rig', command = createEyeRig )
    cmds.button( label = 'eyeBall Direction', command = eyeBallDirection ) 
    cmds.text( label = '')
    cmds.button( label = 'eyeLid offset/scale', command = eyeLidOffset_scale )
    cmds.button( label = 'jointSkinEyeBall', command = jointSkinEyeBall )
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.separator( h = 15)
            
    cmds.text( label = 'ctrls')
    cmds.optionMenu('face_area', changeCommand=printNewMenuItem )
    cmds.menuItem( label= "basic" )
    cmds.menuItem( label= "all" )
    cmds.menuItem( label= "mouth" )
    cmds.menuItem( label= "eye" )
    cmds.menuItem( label= "bridge" )
    cmds.button( label = 'reset', command = resetCtrl ) 
    cmds.separator( h = 15)
    cmds.button( label = 'selectCtrls', command = selectCtrl )    
    cmds.button( label = 'deleteKeys', command = deleteCtrlKeys )
    cmds.separator( h = 15)    
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    
    cmds.text( label = 'Head Skin:')
    objName = cmds.textField( 'headGeoName', text = "head_REN" )
    cmds.button( label = 'JointLabel', command = setLipJntLabel )
    cmds.separator( h = 15)
    cmds.button( label = 'headSkin', command = headSkin )
    cmds.button( label = 'arFaceHeadSkin', command = arFaceHeadSkin )
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    
    cmds.text( label = 'head geo:')
    cmds.button( label = 'copyTrioSkinWgt', command = copyTrioSkinWeights  )
    cmds.button( label = 'exportTrioSkinWgt', command = exportTrioSkinWgt  )
    cmds.text( label = '')
    cmds.button( label = 'calculateSkinWgt', command = faceWeightCalculate  )
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
       
    cmds.text( label = 'seperate eyeLid:')
    cmds.button( label = 'copyExportEyeSkin', command = copyExportEyeSkinWeights  )
    cmds.button( label = 'eyeWeightCalculate', command = eyeWeightCalculate  )
    cmds.text( label = '')
    cmds.button( label = 'switchEyeJnt toCls', command = switchJntToCls  )   
    cmds.text( label = '')    
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.separator( h = 15)

    cmds.text( label = 'eyeLid curve')
    cmds.optionMenu('eyeLid_crv', changeCommand= printNewMenuItem )
    cmds.menuItem( label= "min_crv" )
    cmds.menuItem( label= "max_crv" )
    cmds.menuItem( label= "squint_crv" )
    cmds.menuItem( label= "annoy_crv" )
    cmds.menuItem( label= "PushA_crv" )
    cmds.menuItem( label= "PushB_crv" )
    cmds.menuItem( label= "PushC_crv" )
    cmds.menuItem( label= "PushD_crv" )
    cmds.button( label = 'eyeLid curve', command = eyeLidCrvIsolate )

    cmds.text( label = 'lip curve')
    cmds.optionMenu('lip_crv', changeCommand= printNewMenuItem )
    cmds.menuItem( label= "happy_crv" )
    cmds.menuItem( label= "sad_crv" )
    cmds.menuItem( label= "E_crv" )
    cmds.menuItem( label= "wide_crv" )
    cmds.menuItem( label= "U_crv" )
    cmds.menuItem( label= "O_crv" )
    cmds.menuItem( label= "jawOpen" )
    cmds.menuItem( label= "tyOpen" )
    cmds.button( label = 'lip curve', command = lipCrvIsolate )

    cmds.text( label = 'brow curve')
    cmds.optionMenu('brow_crv', changeCommand= printNewMenuItem )
    cmds.menuItem( label= "browSad" )
    cmds.menuItem( label= "browMad" )
    cmds.menuItem( label= "furrow" )
    cmds.menuItem( label= "relax" )
    cmds.button( label = 'brow curve', command = browCrvIsolate )
    cmds.text( label = '')
    cmds.text( label = 'select 2 curves')
    cmds.text( label = '')
    cmds.text( label = 'copy/Mirror curves')
    cmds.button( label = 'copy curve', command = copyCurveSel )
    cmds.button( label = 'mirror curve', command = mirrorCurveSel )    
    
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.text( label = 'lipCorner Clusters')
    cmds.button( label = 'lipCorner clusters', command = lipCornerCls  )
    cmds.button( label = 'mirrorWgt Cluster', command = faceClsMirrorWgt )
    cmds.text( label = '')
    cmds.optionMenu('select_cluster', changeCommand= printNewMenuItem )
    cmds.menuItem( label= "cheek" )
    cmds.menuItem( label= "lowCheek" )
    cmds.menuItem( label= "squintPuff" )
    cmds.menuItem( label= "ear" )
    cmds.menuItem( label= "EyeWide" )
    cmds.menuItem( label= "cornerUp" ) 
    cmds.menuItem( label= "cornerDwn" )
    cmds.button( label = 'indieCls mirrorWgt', command = indieClsWeightMirror )
    cmds.text( label = 'faceCls connect')
    cmds.button( label = 'faceCls connect', command = connectFaceCluster )
    cmds.text( label = '')
    cmds.separator( h = 15)
    cmds.separator( h = 15) 
    cmds.separator( h = 15)     
    cmds.text( label = 'blendShape') 
    cmds.button( label = 'split BS Weight', command = splitBSWeightMap )
    cmds.button( label = 'create twitchBS', command = createTwitchBS )
    cmds.text( label = '')
    cmds.button( label = 'ctrl connectBS', command = connectBlendShape, annotation = "BCDtype connection" )
    cmds.button( label = 'split XYZ', command = splitXYZ, annotation = "select target and base mesh( create new blendshape with target_x, target_y, target_z )" )
    cmds.text( label = '')
    cmds.text( label = 'set ctls for pose!')
    cmds.text( label = 'select Aim Shape!')
    cmds.text( label = 'fix each target' )
    cmds.button( label = 'fix Twitch_target', command = fixTwitchTarget )
    cmds.button( label = 'reset corrective', command = resetForCorrectiveFix )
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = 'if mesh: add twitchBS')
    cmds.text( label = 'if ctl:update weight')
    cmds.text( label = 'set ctls for pose!!')
    cmds.optionMenu('split_range', changeCommand= printNewMenuItem )
    cmds.menuItem( label= "ear" )
    cmds.menuItem( label= "mouth" )
    cmds.menuItem( label= "nose" ) 
    cmds.button( label = 'add tgt/update wgt', command = updateAddTargetWeight )
    cmds.text( label = '')
    cmds.separator( h = 15)
    cmds.separator( h = 15)

    cmds.text( label = 'browUp/DownMax:')
    browUpField = cmds.intField( "upMax", value = 20 )
    browDownField = cmds.intField( "downMax", value = 10 )
    cmds.text( label = 'browIn/OutMax:')
    browInField = cmds.intField( "inMax", value = 10 )
    browOutField = cmds.intField( "outMax", value = 10 )

    cmds.text( label = '')
    cmds.text( label = 'set ctrls 1')
    cmds.text( label = 'select tgt(name!)')
    cmds.text( label = '')
    cmds.button( label = 'brow corrective', command = createBrowCorrective )
    cmds.button( label = 'update remapMax', command = updateRemapMax )
    cmds.text( label = 'fix mixedBS')
    cmds.button( label = 'fix mix', command = fixMix )
    cmds.text( label = '')    
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.separator( h = 15) 
    
    cmds.text( label = '')
    cmds.text( label = '  select all the objects')
    cmds.text( label = 'for upTeeth / loTeeth grp')
    cmds.text( label = 'teeth setup')
    cmds.button( label = 'upTeeth', command = upTeethSetup )
    cmds.button( label = 'loTeeth', command = loTeethSetup )

    cmds.text( label = 'tongue setup')
    cmds.text( label = 'position tongue_ctl')
    cmds.button( label = 'tongueSetup', command = tongueSetup )     
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.text( label = '') 
    cmds.text( label = 'jawOpen fix') 
    cmds.text( label = 'lipCorner level/TZ') 
    cmds.text( label = 'jaw Extra')
    cmds.button( label = 'jawDetail_crv', command = jawRigDetailCrv  )
    cmds.button( label = 'corner Level/Lip Tz', command = lipTzSetup  )
    cmds.text( label = '')
    cmds.button( label = 'lipThinning', command = lipThinningSetup  )
    cmds.button( label = 'dial lipFactor', command = dial_lipFactor  )
    
    cmds.separator( h = 15)    
    cmds.separator( h = 15)
    cmds.separator( h = 15)    
    cmds.text( label = 'joints browLength:')
    jntLen = cmds.intField( 'joint_length', value = 12 )
    cmds.button( label = 'squachSetup', command = squachFunction )
    cmds.text( label = 'select objects!')
    cmds.optionMenu('lattice_jnt', changeCommand= printNewMenuItem )
    cmds.menuItem( label= "lattice" )
    cmds.menuItem( label= "joint" )

    cmds.button( label = 'addSquachGeo', command = addSquachGeo )
    
    cmds.text( label = 'squach name:')
    objName = cmds.textField( 'objName', text = "body" )
    cmds.button( label = 'nonTwitch squach', command = nonTwitchSquachRig )
    cmds.separator( h = 15) 
    cmds.separator( h = 15)
    cmds.separator( h = 15)    
    cmds.setParent( '..' )    


    #4nd tab "face lift"
    child4= cmds.rowColumnLayout( numberOfColumns = 3, bgc=[.22,.3,.40], columnWidth = [(1, 140),(2, 120),(3, 120)], columnOffset = [(1, 'right', 5)] )
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = 'Michelleneous', bgc = [.12,.2,.30], fn = "boldLabelFont",height= 20 )
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')

    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')

    cmds.text( label = 'Mark:   ', fn = "boldLabelFont" )
    cmds.button( label = 'mark verts', bgc=[.42,.5,.60], command = markVertex )
    cmds.button( label = 'remove vertMark', bgc=[.42,.5,.60], command = removeVertMark )
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.button( label = 'create Parent Null', bgc=[.42,.5,.60], command = createPntNull )     
    cmds.button( label = 'transfer cluster WN', bgc=[.42,.5,.60], command = changeClsWeightNode ) 

    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.text( label = '')
    cmds.text( label = 'select target(name!!)')
    cmds.text( label = 'and base with BS')
    cmds.text( label = 'blendShape')
    cmds.button( label = 'target Add/Reconnect', bgc=[.42,.5,.60], command = targetAdd_Reconnect )
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')    
    cmds.text( label = 'name for curve')
    cmds.textField( 'crv_name', text = "brow" )
    cmds.text( label = '')        
    cmds.text( label = '')
    cmds.text( label = 'src crv(BS/no targets)')
    cmds.text( label = 'copy tgt crv           ')
    cmds.text( label = 'copy blendShape delta')
    cmds.button( label = 'copyCrvBS delta', bgc=[.42,.5,.60], command = copyCrvDeltaBS )
    cmds.button( label = 'bakeCrvBS_target', bgc=[.42,.5,.60], command = bakeCrvBS_target )
    cmds.text( label = '')
    cmds.text( label = 'select curve with BS')
    cmds.text( label = '')
    cmds.text( label = 'create target curves')
    cmds.button( label = 'bakeTarget_reconnect', bgc=[.42,.5,.60], command = bakeTarget_reconnect )
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = ' select vtx on loop')
    cmds.text( label = 'and curve          ')
    cmds.text( label = '')
    cmds.button( label = 'shapeToCurve', bgc=[.42,.5,.60], command = shapeToCurve )
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = 'select bodyHead and ')
    cmds.text( label = 'twitchHead')
    
    cmds.text( label = 'attach twitchHead')
    cmds.button( label = 'attachTwitchHead', bgc=[.42,.5,.60], command = attachTwitchHead  )
    cmds.button( label = 'dgTimer', bgc=[.42,.5,.60], command = dgTimer  )
    cmds.separator( h = 15)    
    cmds.button( label = 'renameDuplicates', bgc=[.42,.5,.60], command = renameDuplicates )
    cmds.button( label = 'delete plugins', bgc=[.42,.5,.60], command = deleteUnknown_plugins )
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')    
        
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
    '''cmds.text( label = 'Split BS weight')
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

def headGeo( *pArgs ):
    faceCompFunction.headGeo()
    
def updateHierachy( *pArgs ):
    faceSkinFunction.updateHierachy()
        
def browVerts( *pArgs ):
    faceCompFunction.browVerts()
    
def selectBrowVerts(*pArgs):
    faceCompFunction.selectBrowVerts()

    
def removeVertMark( *pArgs ):
    faceCompFunction.removeVertMark()
    
def orderedUpLoVert( *pArgs ):
    currentName = cmds.optionMenu('eye_lip', query=True, value=True) 
    faceCompFunction.orderedVert_upLo(currentName)

def rnkOrderedVert_upLo( *pArgs ):
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
    
#select "ctl guide curve", "controller"
def connectBrowCtrls(*pArgs):
    size = cmds.floatField( 'browCtlSize', q=1, value = 1 ) 
    offset = cmds.floatField( 'browCtlOffset', q=1, value = 1 )
    numOfCtl = cmds.optionMenu( 'numOfBrowCtl', query=True, value=True )
    mySel = cmds.ls(sl=1, typ ="transform")
    if len(mySel) == 1:
        faceCompFunction.browCtl_onHead( int(numOfCtl), offset )        
        faceCompFunction.connectBrowCtrls( int(numOfCtl), size, offset, "" )
        
    elif len(mySel) == 2:
        faceCompFunction.browCtl_onHead( int(numOfCtl), offset )        
        faceCompFunction.connectBrowCtrls( int(numOfCtl), size, offset, mySel[1] )
    
def browUpDownReverse(*pArgs):
    faceCompFunction.browUpDownReverse()


def eyelidJoints(*pArgs):
	prefix = ["l_up", "l_lo"] 
	for pre in prefix:
		faceCompFunction.eyelidJoints( pre )
		
        
def eyeHiCrv(*pArgs):
	prefix = ["l_up", "l_lo", "r_up", "r_lo"] 
	for pre in prefix:
		faceCompFunction.eyeHiCrv( pre )
		
def eyeCtlCrv(*pArgs):

    numEyeCtl = cmds.optionMenu( 'numOfEyeCtls', query=True, value=True )
    offset = cmds.floatField( 'eyeCtlOffset', q=1, value = 1 )  
    prefix = ["l_up", "l_lo", "r_up", "r_lo"] 
    for pre in prefix:
       
	    faceCompFunction.eyeCtrlCrv( pre, int(numEyeCtl),offset )
    faceCompFunction.eyeCtlCrv() 
    
def eyeCrvConnect(*pArgs):
    prefix = ["l_", "r_"] 
    for pre in prefix:
        faceCompFunction.eyeCrvConnect( pre ) 

    preName = ["l_up", "l_lo", "r_up", "r_lo" ]
    for prx in preName:
        faceCompFunction.wideLid_setup(prx )
    faceCompFunction.eyeWideJntLabel()
    
def jawJoints(*pArgs ):
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


def freeform_setup(*pArgs ):
    sel = cmds.ls(os=1 )    
    numCtls = cmds.optionMenu( 'numOfLipCtl', q =1, value = 1 )
    numDetail = cmds.optionMenu( 'numOfDtailCtl', q =1, value = 1 )
    offset = cmds.floatField( 'lipCtlOffset', q=1, value = 1 ) 
    for i, ud in enumerate(["up","lo"]):
        lipVerts = cmds.getAttr( "lipFactor." + ud + "LipVerts" )
        if int(numDetail)>len( lipVerts ):
            numDetail = len( lipVerts )
        if sel:
            crvSel = sel[i]
        else:
            crvSel =[]        
        faceCompFunction.lipFreeCtl( ud, crvSel, int(numCtls), int(numDetail) , offset )
                
    #faceCompFunction.lipPuff_crvSetup( int(numDetail) )
    
		
def createPntNull(*pArgs):
    faceCompFunction.createPntNull()


def changeClsWeightNode(*pArgs):
	faceCompFunction.changeClsWeightNode() 


def copyCrvDeltaBS(*pArgs):
	faceCompFunction.bakeCrvDeltaBS()

def bakeCrvBS_target(*pArgs):
    crvName = cmds.textField( 'crv_name', query=True, text=True )
    faceCompFunction.copyCrvBS_target(crvName )
		
def shapeToCurve(*pArgs):
	faceCompFunction.shapeToCurve()
    
def curve_halfVerts( *pArgs ):
    openClose = cmds.optionMenu('openClose', query=True, value=True )
    degree = cmds.optionMenu('degree', query=True, value=True )    
    name = cmds.optionMenu('mapName', query=True, value=True )
    faceCompFunction.curve_halfVerts( name, openClose, degree )
   
def browMapSurf(*pArgs):
    faceCompFunction.browMapSurf()
    
def loftMapSurf(*pArgs):
    title = cmds.optionMenu('mapName', query=True, value=True )
    faceCompFunction.loftMapSurf(title)

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

def rnkLipMapSkinning( *pArgs ):
    faceCompFunction.rnkLipMapSkinning()
    
def eyeMapSkin(*pArgs):
    faceCompFunction.eyeMapSkinning()
    
def rnkEyeMapSkinning( *pArgs ):
    faceCompFunction.rnkEyeMapSkinning()    
    
#face skinning tab
def eyeBallDirection( *pArgs ):
    faceSkinFunction.eyeBallDirection() 

def createEyeRig( *pArgs ):
    faceSkinFunction.createEyeRig()

def eyeLidOffset_scale( *pArgs ):
    faceSkinFunction.eyeLidOffset_scale()

def eyeDirectionOffset( *pArgs ):
    faceSkinFunction.eyeDirection_offset()        


def jointSkinEyeBall( *pArgs ):
    faceSkinFunction.jointSkinEyeBall()    
    
def detailOnOff( *pArgs ):
    faceSkinFunction.detailOnOff()    

def resetCtrl(*pArgs):
    facePart = cmds.optionMenu('face_area', query=True, value=True)
    twitchPanelConnect.resetCtrl(facePart)


def deleteCtrlKeys(*pArgs):
    facePart = cmds.optionMenu('face_area', query=True, value=True)
    twitchPanelConnect.deleteCtrlKeys(facePart)


def selectCtrl(*pArgs):
    facePart = cmds.optionMenu('face_area', query=True, value=True)
    twitchPanelConnect.selectCtrl(facePart)
    
    
def faceClusters( *pArgs ):
    faceSkinFunction.faceClusters()
    

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

def markVertex( *pArgs ):
    vtxSel = cmds.ls(sl=1, fl=1)
    cmds.polyColorPerVertex(vtxSel, r=1, g=0.3, b=0.3, a=1, cdo=1 )

def removeVertMark( *pArgs ):
    faceSkinFunction.removeVertMark()

def faceLift(*pArgs):
    from twitchScript import faceComp
    reload(faceComp)
    faceComp.faceCompositionUI()


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
	    
def setLipJntLabel(*pArgs):
    faceSkinFunction.setLipJntLabel()
   
def headSkin(*pArgs):
    geoName = cmds.textField( 'headGeoName', query=True, text=True )
    faceSkinFunction.headSkinObj(geoName)

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

def copyCurveSel(*pArgs):
    faceSkinFunction.copyCurveShapes()

def mirrorCurveSel(*pArgs):
    faceSkinFunction.mirrorCurveSel()
    
def lipCornerCls(*pArgs):
    faceSkinFunction.lipCornerCls() 

def faceClsMirrorWgt(*pArgs):
    faceSkinFunction.faceClsMirrorWgt() 

def indieClsWeightMirror(*pArgs):
    clsName = cmds.optionMenu('select_cluster', query=True, value=True)
    faceSkinFunction.indieClsWeightMirror( clsName )
    
def squachFunction(*pArgs):
    jntLenNum = cmds.intField( 'joint_length', q=1, value = 1 )    
    squachSetup.squachSetup(jntLenNum)
   
def addSquachGeo(*pArgs):
    dformer = cmds.optionMenu( 'lattice_jnt', q=1, value = 1 )  
    squachSetup.addSquachGeo(dformer)

def nonTwitchSquachRig(*pArgs):
    jntLenNum = cmds.intField( 'joint_length', q=1, value = 1 )
    name = cmds.textField( 'objName', query=True, text=True )    
    squachSetup.nonTwitchSquachRig(jntLenNum, name )
    
def connectFaceCluster(*pArgs):
    twitchPanelConnect.ctrlConnectFaceCluster()

def splitBSWeightMap( *pArgs ):
    blendShapeMethods.splitBSWeightMap() 

def createTwitchBS( *pArgs ):
    blendShapeMethods.createTwitchBS()

def updateAddTargetWeight( *pArgs ):
    splitRange = cmds.optionMenu('split_range', query=True, value=True)
    blendShapeMethods.updateAddTarget( splitRange )

def connectBlendShape(*pArgs):
    blendShapeMethods.ctrlConnectBlendShape() 

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

def targetAdd_Reconnect(*pArgs):
    blendShapeMethods.targetAdd_Reconnect()

def bakeTarget_reconnect(*pArgs):
    blendShapeMethods.bakeTarget_reconnect()
    
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
