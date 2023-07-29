# -*- coding: utf-8 -*-
import maya.cmds as cmds
import re
import math
import sys
import maya.mel as mel
from maya import OpenMaya
import os.path
import json
from functools import partial
import pymel.core as pm

def shapeBakeWire_tool():

    #check to see if window exists
    if cmds.window ('faceShapeBake_setup', exists = True):
        cmds.deleteUI( 'faceShapeBake_setup')

    #create window
    swWindow = cmds.window( 'faceShapeBake_setup', title = 'faceShapeBake setup', w =420, h =940, mnb = True, mxb = True, sizeable=True, resizeToFitChildren = True )
    
    #main layout
    mainLayout = cmds.scrollLayout(	horizontalScrollBarThickness=16, verticalScrollBarThickness=16)
    cmds.columnLayout( w =400, h =920)
    
    #rowColumnLayout
    cmds.rowColumnLayout( numberOfColumns = 3, columnWidth = [(1, 80),(2, 120),(3, 120) ], columnOffset = [(1, 'right', 10)] )
    spaceBetween(2,3)#2: row 3: column
    cmds.text( label = '')
    cmds.text( label = 'Wire BS transfer', bgc = [.12,.2,.30], height= 20 )
    cmds.text( label = '')    
    spaceBetween(1,3) 
    cmds.text( label = 'wire name : ')
    wireName = cmds.textField( 'wireDfom_name', text = "lip" )  
    cmds.text( label = '')
    
    cmds.text( label = '')
    cmds.text( label = 'select src & tgt crv' )    
    cmds.text( label = '')
    
    cmds.text( label = '')
    cmds.button( label = 'copy CrvBS delta', bgc=[.42,.5,.60], command = copyCrvBS_delta )
    cmds.button( label = 'lipCrv setup', bgc=[.42,.5,.60], command = transferWireBS )

    cmds.text( label = 'number of CVs')
    cmds.text( label = 'select "CV" at corner', fn = "boldLabelFont", height= 20 )    
    cmds.text( label = 'select curve with BS')
    
    cmds.optionMenu('number_CVs', bgc=[0,0,0], changeCommand=printNewMenuItem )
    cmds.menuItem( label=4 )
    cmds.menuItem( label=5 )
    cmds.menuItem( label=6 )
    cmds.menuItem( label=7 )
    cmds.menuItem( label=8 )
    cmds.menuItem( label=9 )

    cmds.button( label = 'wide/Tight crvBS', bgc=[.42,.5,.60], command = WideTight_crvBS )    
    cmds.button( label = 'bakeTarget_reconnect', bgc=[.42,.5,.60], command = bakeTarget_reconnect )

    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.separator( h = 15)   
    spaceBetween(1,3)
    cmds.text( label = '')
    cmds.text( label = '      Wire Setup      ', bgc = [.12,.2,.30], height= 20 )
    cmds.text( label = '')

    cmds.text( label = '        select:', fn = "boldLabelFont", height= 20 )
    cmds.text( label = 'shp/wtWire, head_base   |')
    cmds.text( label = '|   nurbSphere, head_base ')
    
    #cmds.button( label = '?', command = lipWireSetup_helpImage )
    cmds.text( label = '')
    cmds.button( label = 'lipWire_setup', bgc=[.42,.5,.60], command = lipWire_setup )
    cmds.button( label = 'cheekSculpt head', bgc=[.42,.5,.60], command = cheekSculptHead_window )
    
    spaceBetween(1,3)
    cmds.text( label = '        select:', fn = "boldLabelFont", height= 20 )
    cmds.text( label = 'wire, head_base')
    cmds.text( label = 'browWire, head_base' )
    
    cmds.text( label = '')
    cmds.button( label = 'browWire_head', bgc=[.42,.5,.60], command = browWireHead_window )
    cmds.button( label = 'shrinkHead_zAxis', bgc=[.42,.5,.60], command = shrinkHead_window )
    
    spaceBetween(1,3)
    cmds.text( label = '')
    cmds.text( label = '      Weight Tool      ', bgc = [.12,.2,.30], height= 20 )
    cmds.text( label = '')
    spaceBetween(1,3)
    
    cmds.optionMenu('lip_brow', bgc=[0,0,0], changeCommand=printNewMenuItem )
    cmds.menuItem( label="lip" )
    cmds.menuItem( label="cheek" )
    cmds.menuItem( label="brow" )
    cmds.button( label = 'create set', bgc=[.42,.5,.60], command = create_sets )
    cmds.button( label = 'select border Vtx', bgc=[.42,.5,.60], command = selectBorderVtx )
    cmds.text( label = '')
    cmds.button( label = 'create zero set', bgc=[.42,.5,.60], command = createZeroWgtSet )
    cmds.button( label = 'create mid set', bgc=[.42,.5,.60], command = createMidWgtSet )
    
    spaceBetween(1,3)
    cmds.text( label = '')
    cmds.optionMenu('weight_sets', bgc=[0,0,0], changeCommand=printNewMenuItem )
    cmds.menuItem( label= 'lipWgt_set' )
    cmds.menuItem( label= 'lipZero_set')
    cmds.menuItem( label= 'lipMid_set')
    cmds.menuItem( label= 'cheekWgt_set')
    cmds.menuItem( label= 'browWgt_set')
    cmds.menuItem( label= 'browZero_set')
          
    cmds.button( label = 'select weight_set', bgc=[.82,.75,.10], command = selectWgtSet )

    cmds.text( label = '')
    cmds.button( label = 'replace vtx for the set', bgc=[.42,.5,.60], command = replaceVtxSet )
    cmds.text( label = '')
    
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    spaceBetween(1,3)    
    cmds.text( label = '')
    cmds.text( label = '      Shape Tool      ', bgc = [.12,.2,.30], height= 20 )
    cmds.text( label = '')

    cmds.text( label = '        select:', fn = "boldLabelFont", height= 20 )
    cmds.text( label = ' target curve & vertices ' )
    cmds.text( label = ' select target & base ')
    
    cmds.text( label = '')
    cmds.button( label = 'shapeToCurve', bgc=[.42,.5,.60], command = shapeToCurveFunc )
    cmds.button( label = 'splitXYZ ', bgc=[.42,.5,.60], command = splitXYZ )

    cmds.text( label = '')
    cmds.button( label = 'fixMix', bgc=[.42,.5,.60], command = fixMix ) 
    cmds.button( label = 'add target', bgc=[.42,.5,.60], command = targetAdd )
    
    spaceBetween(1,3)
    
    cmds.text( label = '')
    cmds.text( label = 'Curve on Mesh', bgc=[.12,.2,.30], fn = "boldLabelFont",height= 20 )
    cmds.text( label = '')
    spaceBetween(1,3)
    cmds.optionMenu('faceRegion', bgc=[0,0,0], changeCommand=printNewMenuItem )
    cmds.menuItem( label="brow" )
    cmds.menuItem( label="eye" )
    cmds.menuItem( label="lip" )
    cmds.optionMenu('open_close', bgc=[0,0,0], changeCommand=printNewMenuItem )
    cmds.menuItem( label="open" )
    cmds.menuItem( label="close" )
    cmds.optionMenu('degree_level', bgc=[0,0,0], changeCommand=printNewMenuItem )
    cmds.menuItem( label=1 )
    cmds.menuItem( label=3 )
    
    cmds.text( label = '            select:', fn = "boldLabelFont", height= 20)
    cmds.text( label = 'left vertices ( 6 for brows')
    cmds.text( label = '/ 9 for lips) in order     ')

    cmds.optionMenu('crv_title', bgc=[0,0,0], changeCommand=printNewMenuItem )
    cmds.menuItem( label="" )
    cmds.menuItem( label="_guide" )
    cmds.menuItem( label="_map" )
    cmds.menuItem( label="_BS" )
    cmds.menuItem( label="_wire" )
    cmds.menuItem( label="_temp" )
    cmds.menuItem( label="_test" )    
    cmds.button( label = 'curve_halfVerts', command = curve_halfVerts )
    cmds.text( label = '')
    spaceBetween(1,3)
    
    cmds.checkBox( 'directionTo', label='+To-' ) 
    cmds.button( label = 'symmetry Open', command = symmetrizeOpen )  
    cmds.button( label = 'symmetry Loop', command = symmetrizeClose )
    
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    
    spaceBetween(1,3)

    cmds.text( label = '')
    cmds.text( label = ' select lipCrv & head' )
    cmds.text( label = 'select nurbs & head' )
    
    cmds.text( label = '')    
    cmds.button( label = 'lipShpBS smoothWeight', command = lipBS_smoothWeight )  
    cmds.button( label = 'skinWeight to BS', command = copySkinWeightToBS )    
    
    spaceBetween(1,3)
    
    cmds.text( label = 'jsonFile')
    jsonFilePath = cmds.textField( 'jsonFilePath', text = "D:/work_place/GoogleDrive/Rainmaker/presentation/faceWire_reference/lipCrv_data.json" )  
    cmds.text( label = '')   
    
    cmds.text( label = '   reference and')
    cmds.text( label = 'select prototype_crvs       ')
    cmds.text( label = '    select newCrv') 
    
    cmds.text( label = '')
    cmds.button( label = 'write CrvData', command = writeCrvData_json )  
    cmds.button( label = 'findClosestCrv', command = findClosestCrv )
    
    print (swWindow)
    dock = "swDock"
    if cmds.dockControl(dock, exists=True):
        cmds.deleteUI(dock)
    allowedArea = ['right', 'left']
    cmds.dockControl( dock, area="right", content= swWindow, allowedArea="all" )
    
    #cmds.showWindow(swWindow)



    

def spaceBetween( numOfRow, numOfColm ):
    for x in range( numOfRow ):
        for i in range(numOfColm):
            cmds.text( l = '')
            
def printNewMenuItem( item ):
    print (item)

def arHelpImage( imageTitle ):   

    if cmds.window( "arFace_helpImage", q =1, ex =1 ):
        cmds.deleteUI("arFace_helpImage" )

    arWindow = cmds.window( title="arFace_helpImage", iconName='helpImage', widthHeight=(400, 550) )
    cmds.paneLayout()
    cmds.image( image='C:/Users/SW/OneDrive/Documents/maya/2020/scripts/twitchScript/arFaceImage/%s.png'%imageTitle )
    #cmds.setParent( '..' )
    cmds.showWindow( arWindow )
    

def lipWideNarrow_helpImage( *pArgs ):
    arHelpImage( "lipWideNarrow_crv" )

    
def copyCrvBS_delta( *pArgs):
    wireDfmTitle = cmds.textField( 'wireDfom_name', query=True, text=True )
    print (wireDfmTitle)
    curvs = cmds.ls( os=1 )
    # curve with blendShape
    sourceCrv = curvs[0]
    # newly created wire curve based on srcCrv uParam 
    targetCrv = curvs[1]
    cmds.makeIdentity( targetCrv, apply=1, t= 1, r = 0, s = 0, n = 0, pn = 1 )
    
    bakeCrvBS_delta( sourceCrv, targetCrv, wireDfmTitle)
    
    prntGrp = wireDfmTitle + "Wire_grp"
    if cmds.objExists( prntGrp ):
        cmds.parent( targetCrv, prntGrp )
    else:
        prntGrp = cmds.group( w=1, n= wireDfmTitle + "Wire_grp" )
        
    

   
def transferWireBS( *pArgs ):
    wireDfmName = cmds.textField( 'wireDfom_name', query=True, text=True )
    print (wireDfmName)
    curvs = cmds.ls( os=1 )
    # curve with blendShape
    srcCrv = curvs[0]
    # newly created wire curve based on srcCrv uParam 
    tgtCrv = curvs[1]  
    transfer_lipCrvBS( srcCrv, tgtCrv, wireDfmName )

    
def bakeTarget_reconnect(*pArgs):
    crvSel = cmds.ls(sl=1, typ ='transform')
    baseCrv = crvSel[0]
    bakeTarget_reconnect_func(baseCrv)


    
# select lipCorner vertex!!
def WideTight_crvBS_old(*pArgs):

    wtBaseCv = cmds.ls(sl=1)[0]
    wtBaseCrv = wtBaseCv.split(".")[0]
    cmds.makeIdentity( wtBaseCrv, apply=1, t= 1, r = 1, s = 1, n = 0, pn = 1 )
    
    cvID = wtBaseCv.split("[")[1][:-1]
    numOfCv = int(cvID)-1
    totalCvs = numOfCv*2+2
    prm = 1.0/44
    if cmds.objExists( wtBaseCrv.split("_")[0] + "_target_grp" ):
        cornerTgtGrp = wtBaseCrv.split("_")[0] + "_target_grp"
    else:
        cornerTgtGrp = cmds.group( em=1, n = wtBaseCrv.split("_")[0] + "_target_grp" )
        
    if wtBaseCrv:
        wCrv = cmds.duplicate( wtBaseCrv )[0]
        wideCrv = cmds.rename(wCrv, "cornerW_crv")
        tCrv = cmds.duplicate( wtBaseCrv )[0]
        tightCrv =cmds.rename(wCrv, "cornerT_crv")
        uCrv = cmds.duplicate( wtBaseCrv )[0]
        upCrv =cmds.rename( wCrv, "cornerU_crv")
        dCrv = cmds.duplicate( wtBaseCrv )[0]
        downCrv =cmds.rename( wCrv, "cornerD_crv")         
        #creat curve for tightRatio
        tempCrv = cmds.curve ( d = 1, p =([0,0.04,0],[0.25,0.24,0],[0.5,0.25,0],[0.75, 0.12, 0],[1, 0.02, 0]) ) 
        cmds.rebuildCurve ( tempCrv, rebuildType = 0, spans = 4, keepRange = 0, degree = 3 )
        wtRatioCrv = cmds.rename( tempCrv, 'wtRatioCrv' )
        temCrv = cmds.curve ( d = 1, p =([0,0,0],[0.25,0.06,0],[0.5,0.25,0],[0.75, 0.12, 0],[1, 0, 0]) ) 
        cmds.rebuildCurve ( temCrv, rebuildType = 0, spans = 4, keepRange = 0, degree = 3 )
        udRatioCrv = cmds.rename( temCrv, 'udRatioCrv' )
        
        meter = 1.0/totalCvs
        print (meter)
        ratios =[]
        udPocs =[]
        for x in range(totalCvs+1):
         
            #loc = cmds.spaceLocator( n = 'wtLoc'+ str(x+1) )  
            wtRatioCrvShp = cmds.listRelatives( wtRatioCrv, c=1, typ = "nurbsCurve")[0] or []
            ratioPoc = cmds.shadingNode( 'pointOnCurveInfo', asUtility =1, n = 'ratioPoc'+ str(x+1))            
            cmds.connectAttr( wtRatioCrvShp + ".worldSpace", ratioPoc + ".inputCurve")
            cmds.setAttr( ratioPoc + ".parameter", meter*x )
            wtPos = cmds.getAttr( ratioPoc + ".position" )[0]
            #cmds.connectAttr( ratioPoc + ".position", loc[0] + ".t" )        
            ratios.append(wtPos[1])
            udRatioCrvShp = cmds.listRelatives( udRatioCrv, c=1, typ = "nurbsCurve")[0]
            udPoc = cmds.shadingNode( 'pointOnCurveInfo', asUtility =1, n = 'udPoc'+ str(x+1))        
            cmds.connectAttr( udRatioCrvShp + ".worldSpace", udPoc + ".inputCurve")
            cmds.setAttr( udPoc + ".parameter", meter*x )
            udPos = cmds.getAttr( udPoc + ".position" )[0]
            udPocs.append(udPos[1])
            
        ratios.remove(ratios[0])
        udPocs.remove(udPocs[0])

        pocList = []
        for i, rt in enumerate(ratios):
            cvIndex = i+2  
            
            wtBaseCrvShp = cmds.listRelatives( wtBaseCrv, c=1, typ = "nurbsCurve")[0]
            poc = cmds.shadingNode( 'pointOnCurveInfo', asUtility =1, n = 'wtPoc'+ str(cvIndex))
            cmds.connectAttr( wtBaseCrvShp + ".worldSpace", poc + ".inputCurve")
            cmds.setAttr( poc + ".parameter", prm*(i+1) - rt/10.0 )

            tightPos = cmds.getAttr( poc + ".position" )[0]

            cmds.xform( tightCrv + ".cv[%s]"%cvIndex, ws=1, t = tightPos )
            
            cmds.setAttr( poc + ".parameter", prm*(i+1) + rt/10.0 )
            widePos = cmds.getAttr( poc + ".position" )[0]

            cmds.xform( wideCrv + ".cv[%s]"%cvIndex, ws=1, t = widePos )
            
            cmds.setAttr( poc + ".parameter", prm*(i+1))
            pocPos = cmds.getAttr( poc + ".position" )[0]
            upPos = [pocPos[0], pocPos[1]+ (udPocs[i]*2) , pocPos[2]]
            cmds.xform( upCrv + ".cv[%s]"%cvIndex, ws=1, t = upPos )

            downPos = [pocPos[0], pocPos[1]-(udPocs[i]*2) , pocPos[2]]
            cmds.xform( downCrv + ".cv[%s]"%cvIndex, ws=1, t = downPos )            
            pocList.append(poc)
            
        for crv in [ wideCrv, tightCrv, upCrv, downCrv ]:
            cmds.select( crv, r=1)
            symmetrizeLipCrv(1)

        cmds.blendShape( tightCrv, wideCrv , upCrv, downCrv, wtBaseCrv, n = "wtCrv_BS" )
        cmds.parent( tightCrv, wideCrv, upCrv, downCrv, cornerTgtGrp )
        cmds.hide(cornerTgtGrp)
        #cmds.delete( wtRatioCrv, udRatioCrv )

def WideTight_crvBS(*pArgs):
    numOfCvs = cmds.optionMenu('number_CVs', query=True, value=True )
    cntOrder = int(numOfCvs)
    WideTight_crvBS_func( cntOrder )
    
    
# select lipCorner vertex!!
        
def WideTight_crvBS_func( movingCvs ):
        
    wtBaseCv = cmds.ls(sl=1)[0]
    wtBaseCrv = wtBaseCv.split(".")[0]
    cmds.makeIdentity( wtBaseCrv, apply=1, t= 1, r = 1, s = 1, n = 0, pn = 1 )
    #total cvs 
    totalCvs = len( cmds.ls( wtBaseCrv + '.cv[*]', fl=1) )
    leftCVs = (totalCvs-2)/2 # cvs in leftSide
    cvID = int(wtBaseCv.split("[")[1][:-1])
    innerCvs = cvID-1 # 갯수(includes selected CV)
    outerCvs = 21 - innerCvs #left outer cvs
       
    # center CV from moving CVs
    moveCVsInner = min( innerCvs, movingCvs ) #갯수
    moveCVsOuter = min( outerCvs, movingCvs )
    moveNumCVs = moveCVsInner + moveCVsOuter
    #centerParam = float(moveCVsInner)/moveNumCVs

    prm = 1.0/44
    if cmds.objExists( wtBaseCrv.split("_")[0] + "_target_grp" ):
        cornerTgtGrp = wtBaseCrv.split("_")[0] + "_target_grp"
    else:
        cornerTgtGrp = cmds.group( em=1, n = wtBaseCrv.split("_")[0] + "_target_grp" )
        
    if wtBaseCrv:
        wCrv = cmds.duplicate( wtBaseCrv )[0]
        wideCrv = cmds.rename(wCrv, "cornerW_crv")
        tCrv = cmds.duplicate( wtBaseCrv )[0]
        tightCrv =cmds.rename(wCrv, "cornerT_crv")
        uCrv = cmds.duplicate( wtBaseCrv )[0]
        upCrv =cmds.rename( wCrv, "cornerU_crv")
        dCrv = cmds.duplicate( wtBaseCrv )[0]
        downCrv =cmds.rename( wCrv, "cornerD_crv")         

        attTitle = cmds.objExists( wtBaseCrv + '.' + "ratioCrv"  )
        if attTitle == False:
            cmds.addAttr( wtBaseCrv, ln = "ratioCrv", at= "double", min=0, max =5, dv=0  )
            
        #create anim curve
        height = moveNumCVs/10.0
        cmds.setKeyframe( wtBaseCrv + '.ratioCrv', value=0, time=0)
        cmds.setKeyframe( wtBaseCrv + '.ratioCrv', value= height*2, time= moveCVsInner )
        cmds.setKeyframe( wtBaseCrv + '.ratioCrv', value=0, time= moveNumCVs +1 )
        
               
        if moveCVsInner == movingCvs: # the num of innerCvs is more than the num of movingCvs 
            firstCvID = cvID-(movingCvs-1)    
            
        else:
            
            firstCvID = 2
             
        #get y value from the anim curve
        ratios =[]
        caches =[]
        for x in range(1, moveNumCVs+1):
            
            frmeCache = cmds.createNode('frameCache', n = "ratio_cache%s"%str(x).zfill(2) )
            cmds.connectAttr( wtBaseCrv + '.ratioCrv', frmeCache + '.stream')
            cmds.setAttr( frmeCache + ".varyTime", x  )
            ratio = cmds.getAttr( frmeCache + ".varying" )
            ratios.append(ratio)
            caches.append(frmeCache)        
          
        for i, rt in enumerate(ratios):
            
            cvIndex = firstCvID + i
            
            wtBaseCrvShp = cmds.listRelatives( wtBaseCrv, c=1, typ = "nurbsCurve")[0]
            poc = cmds.shadingNode( 'pointOnCurveInfo', asUtility =1, n = 'wtPoc'+ str(cvIndex))
            cmds.connectAttr( wtBaseCrvShp + ".worldSpace", poc + ".inputCurve")
            
            cmds.setAttr( poc + ".parameter", prm*(cvIndex-1) - rt/50.0 )
            tightPos = cmds.getAttr( poc + ".position" )[0]
            cmds.xform( tightCrv + ".cv[%s]"%cvIndex, ws=1, t = tightPos )
        
            cmds.setAttr( poc + ".parameter", prm*(cvIndex-1) + rt/50.0 )
            widePos = cmds.getAttr( poc + ".position" )[0]
            cmds.xform( wideCrv + ".cv[%s]"%cvIndex, ws=1, t = widePos )
            
            cmds.setAttr( poc + ".parameter", prm*(cvIndex-1))
            pocPos = cmds.getAttr( poc + ".position" )[0]
            upPos = [pocPos[0], pocPos[1]+ rt , pocPos[2]]
            cmds.xform( upCrv + ".cv[%s]"%cvIndex, ws=1, t = upPos )
        
            downPos = [pocPos[0], pocPos[1]- rt, pocPos[2]]
            cmds.xform( downCrv + ".cv[%s]"%cvIndex, ws=1, t = downPos ) 
            
        for crv in [ wideCrv, tightCrv, upCrv, downCrv ]:
            cmds.select( crv, r=1)
            symmetrizeLipCrv(1)

        cmds.blendShape( tightCrv, wideCrv , upCrv, downCrv, wtBaseCrv, n = "wtCrv_BS" )
        cmds.parent( tightCrv, wideCrv, upCrv, downCrv, cornerTgtGrp )
        #cmds.delete(caches)
        cmds.hide(cornerTgtGrp)

        
def lipWire_setup(*pArgs):
    
    lipWire_setupFunc()


def cheekSculptHead_window(*pArgs):    
    
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
    cheekSculpt_setup(bsNode)


def browWireHead_window(*pArgs):    
    
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
    history = cmds.listHistory( baseGeo, il=1, pdo=1)
    if history:
        dformers = [ x for x in cmds.listHistory( baseGeo, il=1, pdo=1) if "geometryFilter" in cmds.nodeType( x, inherited=1)]
        
        cmds.text( label = '')
        option = cmds.optionMenu('blendShape_list', changeCommand= printNewMenuItem )
        for dform in dformers:
            if cmds.nodeType(dform) == "blendShape":
                cmds.menuItem( label= dform )
    
    else:
        cmds.text( label = '')
        option = cmds.optionMenu('blendShape_list', changeCommand= printNewMenuItem )
        cmds.menuItem( label= "" )      
    
    cmds.text( label = '')
    cmds.text( label = '')    
    cmds.text( label = '')        
    cmds.button( label = 'browWire head', bgc=[.42,.5,.60], command = browWire_setup )
    
    cmds.showWindow(window)
    
    
def browWire_setup(*pArgs):
    bsNode = cmds.optionMenu( 'blendShape_list', query=True, value=True)
    
    if not bsNode == "":
   
        aliasAtt = cmds.aliasAttr( bsNode, q=1 ) 
        for x, y in zip(*[iter(aliasAtt)]*2):
        
            cmds.setAttr( bsNode + "." + x, 0  )                       
            
    browWire_func(bsNode)    
    

def shrinkHead_window(*pArgs):    
    
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
    cmds.button( label = 'zAxis shrinkHead', bgc=[.42,.5,.60], command = zAxis_shrinkHead )
    
    cmds.showWindow(window)

    
def zAxis_shrinkHead(*pArgs):
    bsNode = cmds.optionMenu( 'blendShape_list', query=True, value=True) 
    # select browCrv / headGeo in order
    browSculpt = cmds.ls( sl=1 )
    browCrv = browSculpt[0]
    headBase = browSculpt[1]
    if len(cmds.ls( headBase, typ = 'transform')) ==1:
        if len(cmds.ls( browCrv, typ = 'transform')) ==1:
            
            shrinkBrow_Func(browCrv, headBase, bsNode)

        else:
            cmds.confirmDialog( title='Confirm', message='select browWire curve and head geo!!' )
    else:
        cmds.confirmDialog( title='Confirm', message='there are more than 1 %s!!'%headBase )


            
def create_sets(*pArgs):
    setTitle = cmds.optionMenu( 'lip_brow', query=True, value=True) 
    # select browCrv / headGeo in order
    vtxSel = cmds.ls( sl=1 )
    onlyVertices = cmds.filterExpand(vtxSel, sm=31)
    wgtSet = setTitle + 'Wgt_set'
    if cmds.objExists( wgtSet ):
        cmds.delete( wgtSet )

    if onlyVertices:
        cmds.sets( onlyVertices, n= wgtSet )
    else:
        cmds.confirmDialog( title='Confirm', message='select vertices!!' )
        
   
def selectBorderVtx (*pArgs):
    
    # select browCrv / headGeo in order
    baseHead = cmds.ls( sl=1 )[0].split('.')[0]

    #Select all edges
    cmds.select('{0}.e[*]'.format(baseHead))

    #Filter selection to only borders. Look up documentation for more info on the parameters
    cmds.polySelectConstraint(bo=1, t=0x8000, w=1, m=2)

    #Disable filter select so it doesn't mess with your selection tool afterwards
    cmds.polySelectConstraint(m=0, w=0, bo=0)

    borderVtx = cmds.polyListComponentConversion( fe=True, tv=True )

    cmds.select(borderVtx, r=1)    
    

def createZeroWgtSet(*pArgs):
    
    setTitle = cmds.optionMenu( 'lip_brow', query=True, value=True) 
    # select browCrv / headGeo in order
    vtxSel = cmds.ls( sl=1 )
    onlyVertices = cmds.filterExpand(vtxSel, sm=31)
    zeroSet = setTitle + 'Zero_set'
    if cmds.objExists( zeroSet ):
        cmds.delete( zeroSet )
    
    if onlyVertices:
        cmds.sets(onlyVertices, n= zeroSet )
    else:
        cmds.confirmDialog( title='Confirm', message='select vertices!!' ) 

       
def createMidWgtSet(*pArgs):
    setTitle = cmds.optionMenu( 'lip_brow', query=True, value=True) 
    # select browCrv / headGeo in order
    midSetName = setTitle + 'Mid_set'
    if cmds.objExists(midSetName):
        cmds.delete( midSetName )
    
    headGeo = cmds.ls( sl=1 )[0].split('.')[0]
    headVtx = cmds.ls( headGeo + ".vtx[*]", fl=1)
    headSetTitle = headGeo.split('_')[0] + '_set'
    if cmds.objExists( headSetTitle ):
        cmds.delete( headSetTitle )    
    headSet = cmds.sets( headVtx, n = headSetTitle )
    cmds.select( setTitle + 'Wgt_set', setTitle +'Zero_set', r=1 )
    sumVtx = cmds.ls(sl=1, fl=1 )
    tempSet = cmds.sets( sumVtx, rm = headSet )
    midSet =cmds.rename( tempSet, setTitle + 'Mid_set' )

def selectWgtSet(*pArgs):
    wgtSet = cmds.optionMenu('weight_sets', query=True, value=True)
    if cmds.objExists( wgtSet ):
        cmds.select (wgtSet, r=1)
    else:
        cmds.confirmDialog( title='Confirm', message='create wgtSet first!!' )     
    

def replaceVtxSet(*pArgs):
    wgtSet = cmds.optionMenu('weight_sets', query=True, value=True)
    mySel = cmds.ls(sl=1)
    vtxSel = cmds.filterExpand(mySel, sm=31)
    if cmds.objExists(wgtSet):
        if vtxSel:
            cmds.delete( wgtSet )
            cmds.sets( vtxSel, n= wgtSet )
        else:
            cmds.confirmDialog( title='Confirm', message='select vertices!!' )
    else:
        cmds.confirmDialog( title='Confirm', message='create %s set!!'%wgtSet )
        
    

    
    
def shapeToCurveFunc(*pArgs):

    shapeToCurve()



def curve_halfVerts( *pArgs ):
    openClose = cmds.optionMenu('open_close', query=True, value=True )
    degree = cmds.optionMenu('degree_level', query=True, value=True )    
    item = cmds.optionMenu('faceRegion', query=True, value=True ) #lip, brow, eye
    character = cmds.optionMenu('crv_title', query=True, value=True )
    name = item + character
    trackSelectionOrder = cmds.selectPref( q=1, tso=1 )
    print (item, name)
    if trackSelectionOrder == False:
        cmds.confirmDialog( title='Confirm', message='the trackSelectionOrder should be on in preference' )
    
    myVert = cmds.ls( os=1, fl=1 )  
    curve_halfVertsFunc( myVert, name, openClose, degree )


    
def writeCrvData_json(*pArgs): 

    filePath = cmds.textField( 'jsonFilePath', query=True, text=True )
    protCrvs = cmds.ls(sl=1, long=1, typ = 'transform' )
    writeCrvData(protCrvs, filePath)
    
def findClosestCrv( *pArgs ):

    filePath = cmds.textField( 'jsonFilePath', query=True, text=True )
    myCrv = cmds.ls(sl=1, typ = 'transform' )
    findClosesetCrvData( myCrv, filePath )

'''    
def browCrv_measure( *pArgs ):
    protypeTitle = cmds.textField( 'prototypeCrv_name', query=True, text=True  ) 
    print protypeTitle
    browCrv = cmds.ls(sl=1)[0]
    browProtoCrv_raio(browCrv, protypeTitle )'''

def lipBS_smoothWeight(*Arg ):

    mySel = cmds.ls(sl=1, typ = 'transform')
    
    crvShp = cmds.listRelatives( mySel[0], c=1, s=1 )
    geoShp = cmds.listRelatives( mySel[1], c=1, s=1 )
    if crvShp and geoShp:
        if cmds.nodeType(crvShp[0]) == "nurbsCurve":
        
            lipShpCrv = mySel[0]
            
            if cmds.nodeType(geoShp[0]) == "mesh":
                headBase = mySel[1]
                lipSmoothWeight( lipShpCrv , headBase )
                
            else:
                cmds.confirmDialog( title='Confirm', message='select headGeo last' )
                
        else:
            cmds.confirmDialog( title='Confirm', message='select lipCrv first' )
            
    else:
        cmds.confirmDialog( title='Confirm', message='select lipCrv and headGeo in order' )

        
    

def copySkinWeightToBS(*pArgs):
    
    weightSel = cmds.ls(sl=1) 
    weightSurf = weightSel[0] 
    headGeo = weightSel[1] 
    dfrmList = [ x for x in cmds.listHistory( headGeo, il=1, pdo=1) if "geometryFilter" in cmds.nodeType( x, inherited=1)]
    
    if cmds.window ('bsTargetItem_select', exists = True):
        cmds.deleteUI( 'bsTargetItem_select')
        
    cmds.window('bsTargetItem_select', title = 'bsTargetSelect UI', w = 300, h = 200, mnb = True, mxb = True, sizeable=True, resizeToFitChildren = True )
    mainLayout = cmds.columnLayout( w =400, h= 100)

    #rowColumnLayout
    cmds.rowColumnLayout( numberOfColumns = 3, columnWidth = [(1, 100),(2, 120),(3, 120)], columnOffset = [(1, 'right', 10)] )
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')    
    
    tgtList =[]
    for dform in dfrmList:
             
        nodeTyp = cmds.nodeType(dform)
        if nodeTyp == 'blendShape':
            
            bsNode = dform
            aliasAtt = cmds.aliasAttr(bsNode, q=1)
            
            for tgt, wgt in zip(*[iter(aliasAtt)]*2):
                tgtList.append(tgt)
                
    if bsNode:
    
        cmds.optionMenu('target_items', changeCommand= printNewMenuItem )
        if tgtList:
            for tg in tgtList:
                cmds.menuItem( label= tg )

        cmds.button( label = 'copyWgtToBS', bgc=[.42,.5,.60], command = partial (copyWgtToBS, weightSurf, headGeo, bsNode ) )
    
    else:
        cmds.confirmDialog( title='Confirm', message='%s has no blendShape!!'%headGeo )
    
    cmds.showWindow()




#select surface and headGeo
def copyWgtToBS(weightSurf, headGeo, bsNode, *args):    
    
    target = cmds.optionMenu('target_items',  query=True, value=True )  
    
    if cmds.objExists('lipWgt_head'):
        
        wgtHead = 'lipWgt_head'
        cmds.select( weightSurf, wgtHead, r=1 )
        cmds.copySkinWeights( noMirror=1, surfaceAssociation ="closestPoint",  influenceAssociation ="closestJoint")        
               
        size = cmds.polyEvaluate( headGeo, v=1)
        
        #get the lipJntWeight from wgtHead
        jntID =jointIndices( wgtHead, ["lipWgtJnt", "baseWgtJnt"] ) 
        wgtHeadSkin = mel.eval("findRelatedSkinCluster %s"%wgtHead )
        wgtVal = cmds.getAttr( wgtHeadSkin + '.wl[0:%s].w[%s]'%(size-1, jntID["lipWgtJnt"] ) )   
        aliasAtt = cmds.aliasAttr(bsNode, q=1)
        for tgt, wgt in zip(*[iter(aliasAtt)]*2):
            if tgt == target:
                tgtID = wgt.split("[")[1][:-1]
            
        cmds.setAttr( bsNode + ".inputTarget[0].inputTargetGroup[%s].targetWeights[0:%s]"%(tgtID,( size-1)), *wgtVal )

    else:
        cmds.confirmDialog( title='Confirm', message='"lipWgt_head" not exists ' ) 
        

def transfer_lipCrvBS( srcCrv, tgtCrv, wireName ):
    # curve cvs    
      
    cmds.makeIdentity( tgtCrv, apply=1, t= 1, r = 1, s = 0, n = 0, pn = 1 )
    wireCrv = cmds.rename( tgtCrv, wireName + 'Shape_wire' )
    srcCvs = cmds.ls( srcCrv + ".cv[*]", fl=1 )
    tgtCvs = cmds.ls( wireCrv + ".cv[*]", fl=1 )

    srcLeng = len(srcCvs)
    tgtLeng = len(tgtCvs)

    '''vectorAngle = angleGap_2crvs(srcCrv, wireCrv )
    # source vector bigger than target vector angle 
    if vectorAngle[0]>vectorAngle[1]:
        angle = vectorAngle[2]
    # target vector bigger than source vector angle 
    else:
        angle = -vectorAngle[2]
        
    startNum = 1
    endNum = srcLeng/2 + 1

    targetRotCls = cmds.cluster( tgtCvs[startNum], n = wireCrv + "_cls" )
    clsSet = cmds.listConnections( targetRotCls[0], type="objectSet" )[0]
    tgtCvs.remove(tgtCvs[startNum])
    cmds.sets( tgtCvs, add= clsSet )
    # source curve 와 똑같은 기울기로 만들어준다
    cmds.setAttr( targetRotCls[1] + ".rx", angle )

    # delete history 
    cmds.delete( wireCrv, ch=1 )'''
    
    # srcCrv BS delta baking  
    bakeCrvBS_delta( srcCrv, wireCrv, wireName )
    targetGrp = bakeTarget_reconnect_func(wireCrv)
    cmds.hide( targetGrp )
    
    '''# target curve 기울기로 다시 전환
    cvs = cmds.ls( wireCrv + ".cv[*]", fl=1 )
    rotateCls = cmds.cluster( cvs[startNum], n = wireCrv + "_nCls" )
    clusterSet = cmds.listConnections( rotateCls[0], type="objectSet" )[0]
    cvs.remove(cvs[startNum])
    cmds.sets( cvs, add= clusterSet )

    cmds.setAttr( rotateCls[1] + ".rx", -angle )'''
    
    bendDfm = cmds.nonLinear( tgtCvs, type = "bend", curvature=0 ) 
    bendHandle = bendDfm[1]            
    cmds.setAttr( bendHandle + ".rz", -90 )
    cmds.setAttr( bendHandle + ".ry", 90 )

    #add attr on the wire curve
    attrN = wireCrv.split("_")[0]
    attTitle = cmds.objExists( wireCrv + '.' + attrN + "_curvature"  )
    if attTitle == False:
        cmds.addAttr( wireCrv, ln = attrN + "_curvature", at= "double", min=-10, max =20, dv=0  )
    
    cmds.setAttr( wireCrv + ".%s_curvature"%attrN, e=1, keyable= 1 )
    cmds.connectAttr( wireCrv + ".%s_curvature"%attrN, bendDfm[0] + ".curvature" )
                
    lipCrv_pos = cmds.xform( wireCrv + ".cv[1]", q=1, ws=1, t=1 )
    if lipCrv_pos[0] < 0.001:
        
        wtCrv = create_wtCircle(lipCrv_pos)        
        
    else:
        cmds.confirmDialog( title='Confirm', message=' %s positionX is not zero'%wireCrv )    
    
    wireGrp = cmds.group( w=1, n= "wireTarget_grp" ) 
    cmds.parent( wireCrv, bendDfm[1], targetGrp, wireGrp )

'''
def angleGap_2crvs( srcCrv, tgtCrv ):
     
    srcCvs = pm.ls( srcCrv + ".cv[*]", fl=1 )
    tgtCvs = pm.ls( tgtCrv + ".cv[*]", fl=1 )
    
    srcLeng = len(srcCvs)
    tgtLeng = len(tgtCvs)
    if srcLeng == tgtLeng:
        
        startNum = 1
        endNum = srcLeng/2 + 1
        
        #source curve angle vector
        sourceStartPos = pm.xform( srcCvs[startNum], q=True,ws=True,t=True)
        sourceStartPos = [ 0, sourceStartPos[1],sourceStartPos[2]]
        srcStartPos  = pm.datatypes.Point(sourceStartPos)
        
        sourceEndPos= pm.xform( srcCvs[endNum], q=True,ws=True,t=True)
        sourceEndPos = [ 0, sourceEndPos[1],sourceEndPos[2]]
        srcEndPos = pm.datatypes.Point(sourceEndPos)
        
        sourceStartEndVector = pm.datatypes.Vector(srcStartPos-srcEndPos ) 
        print sourceStartEndVector[2]
        #target curve angle vector
        targetStartPos = pm.xform( tgtCvs[startNum], q=True,ws=True,t=True)
        targetStartPos = [ 0, targetStartPos[1],targetStartPos[2]]
        tgtStartPos  = pm.datatypes.Point(targetStartPos)
        
        targetEndPos= pm.xform( tgtCvs[endNum], q=True,ws=True,t=True)
        targetEndPos = [ 0, targetEndPos[1],targetEndPos[2]]
        tgtEndPos = pm.datatypes.Point(targetEndPos)
        
        targetStartEndVector = pm.datatypes.Vector(tgtStartPos-tgtEndPos )    
        print targetStartEndVector[2]
        #get angle between target/source curve
        angleGap = pm.angleBetween( v1= targetStartEndVector, v2= sourceStartEndVector )
        return [sourceStartEndVector[2], targetStartEndVector[2], angleGap[3]]

    else:
        pm.confirmDialog( title='Confirm', message='source/target CV numbers are different' )'''
        
        
# select curve with BS and new curve in origin world
# copy BS delta when number of cvs are same.     
def bakeCrvBS_delta( sourceCrv, targetCrv, name):    

    for crv in [ sourceCrv, targetCrv ]:
        cmds.xform( crv, centerPivots =1 )
    
    #multList = boundingRatio_2Object( sourceCrv, targetCrv )
    crvBS = [ n for n in cmds.listHistory( sourceCrv , historyAttr=1 ) if cmds.nodeType(n) == "blendShape" ]    
    if crvBS:
        aliasAtt = cmds.aliasAttr(crvBS[0], q=1 )
        dnTarget = []
        for i in range(len(aliasAtt)/2):
            
            for tgt, wgt in zip(*[iter(aliasAtt)]*2):
                index = wgt.split("[")[1][:-1]
            
                if int(index)==i:
           
                    if cmds.objExists(tgt):
                        cmds.delete(tgt)
                        copyCrv = cmds.duplicate ( targetCrv, n= tgt )[0]
                        dnTarget.append(copyCrv)
                    else:            
                        copyCrv = cmds.duplicate ( targetCrv, n= tgt )[0]
                        dnTarget.append(copyCrv)
        
        numTgt = len(dnTarget)
        cmds.select(dnTarget, r=1)
        cmds.select(targetCrv, add=1)
        newBS = cmds.blendShape ( n = name + '_bakeBS')
        cmds.delete(dnTarget)

        comp = [0]
        for i in range( numTgt ):
            # browLength of comp is different for each target because the vertexs that has none movement don't counts
            comp = cmds.getAttr(crvBS[0]+ '.inputTarget[0].inputTargetGroup[%s].inputTargetItem[6000].inputComponentsTarget'%str(i) )
            delta = cmds.getAttr(crvBS[0]+ '.inputTarget[0].inputTargetGroup[%s].inputTargetItem[6000].inputPointsTarget'%str(i) )
            newDelta = []

            if delta:
                for dt in delta:
                    xyz = ( dt[0], dt[1] , dt[2], dt[3])
                    newDelta.append(xyz)
         
                cmds.setAttr(newBS[0]+'.inputTarget[0].inputTargetGroup[%s].inputTargetItem[6000].inputComponentsTarget'%str(i), len(comp), *comp, type="componentList" )
                cmds.setAttr(newBS[0]+'.inputTarget[0].inputTargetGroup[%s].inputTargetItem[6000].inputPointsTarget'%str(i), len(newDelta), *newDelta, type="pointArray" )
            else:
                cmds.confirmDialog( title='Confirm', message='dnTarget[index] + " has no delta ' )

    else:
        cmds.confirmDialog( title='Confirm', message='create blendShape first' )




# select two object 
# get the ratio( 2nd obj/1st obj) for size comparison 
def boundingRatio_2Object( source, target ):

    #source curve bounding box
    scOrig = [ x for x in cmds.listRelatives( source, s=1, fullPath=1 ) if 'Orig' in x ]
    print (scOrig)
    scBbox = cmds.exactWorldBoundingBox( scOrig )
    xScLen = scBbox[3]-scBbox[0]
    yScLen = scBbox[4]-scBbox[1]
    zScLen = scBbox[5]-scBbox[2]
    #destination curve bounding box
    dnBbox = cmds.exactWorldBoundingBox( target )
    xDnLen = dnBbox[3]-dnBbox[0]
    yDnLen = dnBbox[4]-dnBbox[1]
    zDnLen = dnBbox[5]-dnBbox[2]
    
    if xScLen > 0: 
        xMult = xDnLen/xScLen
    else:
        xMult = 1
        
    if yScLen > 0:
        yMult = yDnLen/yScLen
    else:
        yMult = 1

    if zScLen > 0:
        zMult = zDnLen/zScLen
    else:
        zMult = 1

    return [ xMult, yMult, zMult ]
    
#make all the target name unique( _crv )!!
#create targets after copy blendShape delta        
#select curve with blendShape(clean, no connections)
#copy target and reconnect for blendShape

def bakeTarget_reconnect_func(baseCrv):

    #deactivate skinCls, wire...( all deformers but blendShape )
    targetHistory = cmds.listHistory( baseCrv, pruneDagObjects =1, interestLevel= 1 )
    dformers = [ x for x in targetHistory if "geometryFilter" in cmds.nodeType( x, inherited =1 )]
    crvBS = [ n for n in dformers if cmds.nodeType(n) == "blendShape" ]    
    if crvBS:
        aliasAtt = cmds.aliasAttr(crvBS[0], q=1)
        dformers.remove(crvBS[0])
        for df in dformers:
            cmds.setAttr( df + ".envelope", 0 )
            
        for tgt, wgt in zip(*[iter(aliasAtt)]*2):
            cmds.setAttr( crvBS[0] + "."+ tgt, 0 )
            
        targetGrp = cmds.group( em=1, n = baseCrv.split('_')[0] + "_target_grp")
        crvTgt = []
        for tgt, wgt in zip(*[iter(aliasAtt)]*2):
            
            # check if target curve exists
            if cmds.objExists(tgt):
                cmds.confirmDialog( title='Confirm', message='%s target exists already'%tgt )
                break
                
            else:
                cnnt = cmds.listConnections(  crvBS[0] +"."+tgt, s=1, d=0, p=1 )
                if cnnt:
                    cmds.disconnectAttr( cnnt[0], crvBS[0] +"."+tgt )
                
                cmds.setAttr( crvBS[0] + "."+ tgt, 1 )
                copyCrv = cmds.duplicate ( baseCrv, rc=1, n= tgt )[0]
                crvTgt.append(copyCrv)
                tgtID= wgt.split("[")[1][:-1]
                cmds.connectAttr( copyCrv+".worldSpace", crvBS[0]+ ".inputTarget[0].inputTargetGroup[%s].inputTargetItem[6000].inputGeomTarget"%str(tgtID) )
                cmds.setAttr( crvBS[0] + "."+ tgt, 0 )
                cmds.parent( tgt, targetGrp )
                if cnnt:
                    cmds.connectAttr( cnnt, crvBS+"."+tgt )
                    
        #re-activate skinCls, wire...( all deformers but blendShape )        
        for df in dformers:
            cmds.setAttr( df + ".envelope", 1 )
            
    else: 
        cmds.confirmDialog( title='Confirm', message='no blendShape for the object!!' )  

    return targetGrp

def create_wtCircle(pos):
    
    baseGeo = cmds.ls(sl=1)[0]
    bbox = cmds.exactWorldBoundingBox( baseGeo )
    wtCircle = cmds.circle( c=( 0, 0, 0),  nr = (0, 1, 0), sw= 360, d= 3, ut= 0, tol= 0.01, s= 8, ch= 1)[0]
    makeCircle = cmds.listHistory( wtCircle, il = 1, pdo =1 )
    cmds.setAttr( makeCircle[0] + ".radius", 10 )
    cmds.setAttr( wtCircle + ".ry", 180 )
    yDist =  ( bbox[4] - bbox[1] )/2
    zDist =  ( bbox[-1] -bbox[2] )/2
    cmds.xform( wtCircle, ws=1, t = (0, pos[1], zDist ) )
    wtCrvNum = len(cmds.ls("lipWT_wireShape*"))
    wtCrv = cmds.rename( wtCircle, "lipWT_wire0"+ str(wtCrvNum+1) )  
    #cmds.makeIdentity( wtCrv, apply=1, t= 1, r = 1, s = 1, n = 0, pn = 1 )
    cmds.rebuildCurve( wtCrv, ch=1, rpo= 1, rt= 0, end= 1, kr= 0, kcp= 0, kep= 1, kt= 0, s= 44, d= 3, tol= 0.01 )
    cmds.delete( wtCrv, ch=1 )
    
    return wtCrv
    



# curve should have center cv[ 0, y, z]
def symmetrizeLipCrv(direction):
    
    crvSel = cmds.ls(sl=1, long=1, type= "transform")
    crvShp = cmds.listRelatives(crvSel[0], c=1, ni=1, s=1)
    
    if len(cmds.ls(crvShp)) == 1:
        periodic = cmds.getAttr( crvShp[0] + '.form' )
        crvCvs= cmds.ls(crvSel[0]+".cv[*]", l=1, fl=1 )
        numCv = len(crvCvs)
        
        numList = [ x for x in range(numCv) ]
        if periodic in [1, 2]:         
            if numCv%2 == 0:
                halfLen = (numCv-2)/2 
                centerCV =[]
                for cv in crvCvs:
                    pos = cmds.xform( cv, q=1, ws=1, t=1 )
                    if pos[0]**2 < 0.00001 :

                        num = cv.split('[')[1][:-1]
                        centerCV.append(int(num))
                
                if len(centerCV) == 2:
                    startNum = centerCV[0]+1
                    endNum = startNum+halfLen
                    halfNum = numList[startNum:endNum]
                    opphalf = numList[endNum+1:] + numList[:centerCV[0]]
                    # curve direction( --> )    
                    if cmds.xform( crvCvs[startNum], q=1, ws=1, t=1)[0]>0:
                        leftNum = halfNum
                        rightNum = opphalf[::-1]
                    # curve direction( <-- )    
                    elif cmds.xform( crvCvs[startNum], q=1, ws=1, t=1)[0]<0:
                        leftNum = opphalf
                        rightNum = halfNum[::-1]
                                
                    print (leftNum, rightNum)
                    if direction == 1:
                        print ("left cv to right cv")
                        for i in range(halfLen):
                            pos = cmds.xform( crvCvs[leftNum[i]], q=1, ws=1, t=1 )
                            cmds.xform( crvCvs[rightNum[i]], ws=1, t=( -pos[0], pos[1], pos[2] ) )
                        
                    else:
                        print ("right cv to left cv")
                        for i in range(halfLen):
                            pos = cmds.xform( crvCvs[rightNum[i]], q=1, ws=1, t=1 )
                            cmds.xform( crvCvs[leftNum[i]], ws=1, t=( -pos[0], pos[1], pos[2] ) )                
                else:
                    cmds.confirmDialog( title='Confirm', message='number of CVs( tx=0 :at center ) of curve should be 2!!!' )      
            
        if periodic == 0:
            if numCv%2 == 1:
                halfLen = (numCv-2)/2 
                centerNum = ''
                for cv in crvCvs:
                    pos = cmds.xform( cv, q=1, ws=1, t=1 )
                    if pos[0]**2 < 0.0001 :
                        num = cv.split('[')[1][:-1]
                        centerNum = int(num)
                    
                if centerNum:
                    halfNum = numList[centerNum+1:]
                    opphalf = numList[:centerNum]            
                    # curve direction( --> )    
                    if cmds.xform( crvCvs[centerNum+1], q=1, ws=1, t=1)[0]>0:
                        leftNum = halfNum
                        rightNum = opphalf[::-1]
                    # curve direction( <-- )    
                    elif cmds.xform( crvCvs[centerNum+1], q=1, ws=1, t=1)[0]<0:
                        leftNum = opphalf
                        rightNum = halfNum[::-1]        
                        
                    if direction == 1:
                        print ("left cv to right cv")
                        for i in range( halfLen ):
                            pos = cmds.xform( crvCvs[leftNum[i]], q=1, ws=1, t=1 )
                            cmds.xform( crvCvs[rightNum[i]], ws=1, t=( -pos[0], pos[1], pos[2] ) )
                        
                    else:
                        print ("right cv to left cv")
                        for i in range(halfLen ):
                            pos = cmds.xform( crvCvs[rightNum[i]], q=1, ws=1, t=1 )
                            cmds.xform( crvCvs[leftNum[i]], ws=1, t=( -pos[0], pos[1], pos[2] ) )

                else:
                    cmds.confirmDialog( title='Confirm', message='position the %s.cv[%s] tx should be at center!!!'%(crvSel[0],centerNum) ) 

    else:
        cmds.confirmDialog( title='Confirm', message= 'More than one %s matches name'%crvShp )
        
# select wire/sphere and head_base in order
# set the jaw_drop pose ( for "jaw_drop" duplicate )
# select wire, and head_REN( base )
def lipWire_setupFunc():
    # select lipDrop_wireCrv and headBase 
    # create or add blendShape with targets that are deformed by each wire

    mySel = cmds.ls( os=1, typ = "transform" )
    if not len(mySel) >= 3:
        cmds.confirmDialog( title='Confirm', message='select lipShp_wire, lipWT_wire and head_base in order!!' )
        
    else:
        wtCrv = ""
        shapeCrv = ""
        bend =[]
        for item in mySel:
            shpNode = cmds.listRelatives(item, c=1, typ= 'shape')[0]
            nodeTp = cmds.nodeType(shpNode)
            history = cmds.listHistory(item, pruneDagObjects =1, interestLevel= 1 )    
            if history:
            
                deform = [ x for x in history if cmds.nodeType( x ) == "blendShape"]
                if deform:
                    if nodeTp == 'nurbsCurve':          
                                  
                        if 'wtCrv_BS' in deform[0]:                
                            wtCrv = item           
                        else:                
                            bend = [ x for x in history if cmds.nodeType(x) == 'nonLinear' ]   
                            shapeCrv = item
                            shapeCrvBS = deform[0]
                
                    elif nodeTp == 'mesh':
                        headBase = item
                        headBaseShape = shpNode  
                        headBS = deform[0]
            
                else:
                    cmds.confirmDialog( title='Confirm', message='%s has no blendShape!!'%item )
                    sys.exit()
            else:
                cmds.confirmDialog( title='Confirm', message='%s has no deformer!!'%item )
                sys.exit()
                
        aliasAtt = cmds.aliasAttr(headBS, q=1)

        '''jawDrops = []
        jawDropNames = [ "jawdrop", "jaw_drop"]
        for x, y in zip(*[iter(aliasAtt)]*2):
            for jawD in jawDropNames:
                if jawD in x.lower():
                    jawDrops.append(x)
        
        print jawDrops
        if len(jawDrops) == 1:

            for x, y in zip(*[iter(aliasAtt)]*2):
            
                if x == jawDrops[0]:
                    cmds.setAttr( headBS + "." + x, 1 )                
                else:
                    cmds.setAttr( headBS + "." + x, 0 )

        else:
            cmds.confirmDialog( title='Confirm', message='%s must have only 1 jawDrop shape!!'%headBS )''' 
     
        
        headBBox = cmds.exactWorldBoundingBox( headBase )

        if  len(cmds.ls(headBase)) == 1:           
            
            if cmds.objExists("mainHead_temp"):
                defaultHead = "mainHead_temp"
            else:
                defaultHead = copyOrigMesh( headBase, "mainHead_temp" )
            
            wireHeads = { wtCrv : "corner_head", shapeCrv: "shape_head" }
            if cmds.objExists(wtCrv):

                wtWireGrp = cmds.group( em=1, n= "mainHead_Grp" )
                cornerTgtGrp = wtCrv.split('_')[0] + "_target_grp"                
                shapeTgtGrp = shapeCrv.split('_')[0] + "_target_grp"
                
                if cmds.objExists(cornerTgtGrp):
                    cmds.parent( wtCrv, defaultHead, shapeTgtGrp, cornerTgtGrp, wtWireGrp )
                else:
                    cmds.parent( wtCrv, defaultHead, wtWireGrp )
                
                #create "corner_head" for mainHead  
                cornerHead = wireHeads[wtCrv]
                
                dup = cmds.duplicate( defaultHead, rc =1, n = cornerHead )[0]
                name = cornerHead.split("_")[0] + "_wire"
                wireDeform = cmds.wire( dup, w = wtCrv, n = name )
                cmds.setAttr( wireDeform[0] + ".rotation", 0 )
                cmds.setAttr( wireDeform[0] + '.dropoffDistance[0]', 10 )                    
                cmds.hide(dup)                    
                                 
                wtBS = cmds.blendShape( cornerHead, defaultHead, n = "main_headBS" )   
                
            if cmds.objExists(shapeCrv):
                
                shpWireGrp = cmds.group( em=1, n= "paintWeight_Grp" )
                # zero out jawDrop blendShape target weights
                aliasAtt = cmds.aliasAttr( shapeCrvBS, q=1)
                for tgt, wgt in zip( *[iter( aliasAtt )]*2 ):
                    cmds.setAttr( shapeCrvBS + "." + tgt, 0 )                     
                 
                jawDrop = cmds.duplicate( headBase, rc=1, n = "jawDrop_geo" )[0]
                
                shapeCrvPrnt = cmds.listRelatives( shapeCrv, p=1)[0]
                print (bend)
                bendHand = cmds.listConnections( bend[0] + '.matrix', s=1, d=0 )[0] 
                cmds.parent( shapeCrv, bendHand, jawDrop, shpWireGrp )                        
                cmds.delete(shapeCrvPrnt)
                jawDropMinus = cmds.duplicate( jawDrop, rc =1, n = "jawDrop_minus" )[0]                
                
                #create "shape_head" for jawDrop_geo 
                shapeHead = wireHeads[shapeCrv] 

                dup = cmds.duplicate( jawDrop, rc =1, n = shapeHead )[0]
                name = shapeHead.split("_")[0] + "_wire"
                wireDform = cmds.wire( dup, w = shapeCrv, n = name )
                cmds.setAttr( wireDform[0] + ".rotation", 0 )
                cmds.setAttr( wireDform[0] + '.dropoffDistance[0]', 10 )
                cmds.hide( dup )
                
                #add attr on the wire curve
                attrN = shapeHead.split("_")[0]
                attTitle = cmds.objExists( shapeCrv + '.' + attrN + "Wire_rot"  )

                if attTitle == False:
                    cmds.addAttr( shapeCrv, ln =  attrN + "Wire_rot", at= "double", min=0, max =1, dv=0  )
                    cmds.addAttr( shapeCrv, ln =  attrN + "DropOff", at= "double", min=1, max =100, dv=10  )
                
                cmds.setAttr( shapeCrv + ".%sWire_rot"%attrN, e=1, keyable= 1 )
                cmds.connectAttr( shapeCrv + ".%sWire_rot"%attrN, wireDform[0] + ".rotation" )
                
                cmds.setAttr( shapeCrv + ".%sDropOff"%attrN, e=1, keyable= 1 )
                cmds.connectAttr( shapeCrv + ".%sDropOff"%attrN, wireDform[0] + ".dropoffDistance[0]" )              
                
                #create blendShape for jawDrop            
                shpBS = cmds.blendShape( shapeHead, jawDrop, n = "jawDrop_headBS" )
                cmds.setAttr( "jawDrop_headBS." + shapeHead, 1 )
                
                #move the grp down
                cmds.setAttr( shpWireGrp + ".ty", -( headBBox[4] - headBBox[1]) )     
                
            cmds.hide(headBase)
            
            if cmds.objExists("jawDrop_headBS") and cmds.objExists("main_headBS"):
                
                alias = cmds.aliasAttr("main_headBS", q=1 )
                jawDropList = [ jawDrop, jawDropMinus ]
                for i, target in enumerate(jawDropList):                
                    cmds.blendShape( "main_headBS", e=1, t = [defaultHead, len(alias)/2 + i, target, 1 ] )                    
                
                cmds.setAttr( "main_headBS." + jawDrop, 1 )
                cmds.setAttr( "main_headBS." + jawDropMinus, -1 )
                cmds.delete( jawDropMinus )
                cmds.hide( cornerHead )

        else:
            cmds.confirmDialog( title='Confirm', message='more than one %s exist'%(headBase) )

def cheekSculpt_setup( bsNode ):
    mySel = cmds.ls( os=1, typ = "transform" )
    if not len(mySel) == 2:
        cmds.confirmDialog( title='Confirm', message='select nurbSphere and head_base in order!!' )
        
    sculptSphere = mySel[0]  
    headBase = mySel[-1]        
    cmds.select( sculptSphere, r=1 )
    cmds.makeIdentity(apply=True, t=1, r=1, s=0, n=0 )
    
    cheekHead = copyOrigMesh( headBase, "cheek_head" )
    headBaseShape = cmds.listRelatives( headBase, c=1, ni=1, s=1 )[0]
    
    if  cmds.nodeType(headBaseShape) == "mesh" :
        name = headBase.split("_")[0] + "_sculpt"
        sculptDform = cmds.sculpt( sculptSphere, mode='flip', insideMode='even', objectCentered=1, n= name )
        prnt = createPntNull( [ sculptDform[1] ] )# create parent for "sculptor1"
        cmds.parent( sculptDform[2], prnt[0] )# parent StretchOrigin to prnt        
        cmds.sculpt( sculptDform[0], e=1, g= cheekHead )
        cmds.delete(sculptSphere)
        
        aliasAtt = cmds.aliasAttr( bsNode, q=1 ) 
        maxNum = []
        for x, y in zip(*[iter(aliasAtt)]*2):
            num = y.split("[")[1][:-1]
            maxNum.append(int(num))
            
        #add corrective crvs in BlendShape    
        index = max(maxNum)+1
        cmds.blendShape( bsNode, e=1, t=( headBase, index, cheekHead, 1.0)  )
        cmds.hide(cheekHead)

    else:
        cmds.confirmDialog( title='Confirm', message='select nurbSphere and head_base in order!!' )



# select "brow_wire" and head_REN( base ) in order
def browWire_func( BS_node ):

    mySel = cmds.ls( os=1, l=1, typ = "transform")
    headBase = mySel[-1] #name head_orig
    browWireCrv = mySel[0]
    #check if headBase is mesh  
    if len(cmds.ls(headBase))==1:

        if not cmds.nodeType( cmds.listRelatives(headBase, pa=1, c=1)[0]) == "mesh":
            print ("select browWireCrv and head_base geo in order!!")
            
        else:         
                
            browWireHeads = ["browUpWire_head", "browDnWire_head", "browShrink_head" ]
            for head in browWireHeads:
                
                if head == "browShrink_head":
                    brow1Dup = cmds.duplicate( headBase )[0]
                    brow2Dup = cmds.duplicate( headBase )[0]
                    target = cmds.rename( brow1Dup, head )
                    mesh = cmds.rename( brow2Dup, "shrink_base" )
                    sculptDform = create_shrink_wrap( target, mesh, projection = 4 )
                    cmds.setAttr( sculptDform + ".targetSmoothLevel", 2 )
                    cmds.setAttr( sculptDform + ".shapePreservationEnable", 1 )
                    cmds.setAttr( sculptDform + ".shapePreservationSteps", 3 )
                    cmds.setAttr( sculptDform + ".shapePreservationReprojection", 2 )  
                    cmds.hide( mesh )
                
                else:

                    browDup = cmds.duplicate( headBase, rc =1, n = head )[0]
                    wireDform = cmds.wire( browDup, w = browWireCrv, n = head.split("_")[0] )
                    cmds.setAttr( wireDform[0] + ".dropoffDistance[0]", 5 )
                    cmds.setAttr( wireDform[0] + ".rotation", 0 )
                    headTitle = head.split("_")[0]
                    attTitle = cmds.objExists( browWireCrv + '.' + headTitle + "_rot"  )
                    if attTitle == False:                    
                        cmds.addAttr( browWireCrv, ln = headTitle + "_rot", at= "double", min=0, max =1, dv=0  )
                        cmds.setAttr( browWireCrv + ".%s_rot"%headTitle, e=1, keyable= 1 )
                        
                    cmds.connectAttr( browWireCrv + ".%s_rot"%headTitle, wireDform[0] + ".rotation" )                
                
            if BS_node == "":
            
                cmds.blendShape( browWireHeads[:-1], headBase, n = "browWire_headBS" )
                prnt = cmds.group( em=True, name= browWireCrv + "_grp" )
                cmds.parent( browWireCrv, prnt )
                cmds.parent( browWireHeads, prnt )
                cmds.hide( browWireHeads )
                cmds.setAttr( "browWire_headBS." + browWireHeads[0], 1 )
            
            else:
            
                aliasAtt = cmds.aliasAttr( BS_node, q=1 ) 
                maxNum = []
                for x, y in zip(*[iter(aliasAtt)]*2):
                    num = y.split("[")[1][:-1]
                    maxNum.append(int(num))
                    
                index = max(maxNum)+1
                for i, browHead in enumerate( browWireHeads ):
                    cmds.blendShape( BS_node, e=1, t=( headBase, index + i, browHead, 1.0)  )

                cmds.setAttr( BS_node + "." + browWireHeads[0], 1 )
                #cmds.setAttr( BS_node + "." + browWireHeads[2], 1 )
                cmds.hide(browWireHeads)               
        
    else:
        print ("There are more than 1 %s!!"%headBase)
'''
# select browCrv / headGeo in order
browSculpt = cmds.ls( sl=1 )
browCrv = browSculpt[0]
headBase = browSculpt[1]'''

def shrinkBrow_Func( browCrv, headBase, bsNode ):
    
    browCrvShape = cmds.listRelatives( browCrv, c=1, typ = 'nurbsCurve' )
    
    dnPOC = cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = 'brow_centerPOC' )
    loc = cmds.spaceLocator ( n = "browPoc_loc" )[0]
    cmds.connectAttr (browCrvShape[0] + ".worldSpace",  dnPOC + '.inputCurve')
    cmds.setAttr ( dnPOC + '.turnOnPercentage', 1 )
    cmds.setAttr ( dnPOC + '.parameter', .8 )
    cmds.connectAttr( dnPOC + '.result.position', loc + '.translate' )

    browBS = [ n for n in cmds.listHistory( browCrv , historyAttr=1 ) if cmds.nodeType(n) == "blendShape" ]
    if browBS:
        aliasAtt = cmds.aliasAttr(browBS[0], q=1 )
        startPos = []
        endPos = []
        actTgt = []
        #get the target whose weight value == 1
        for tgt, wgt in zip( *[iter(aliasAtt)]*2 ):
            wgtVal = cmds.getAttr( browBS[0] + '.' + tgt )
            if wgtVal >= 0.5:
                actTgt.append( tgt )
                
        if actTgt:
            if len(actTgt)==1:
                endPos = cmds.getAttr( loc + '.ty')      
        else:
            cmds.confirmDialog( title='Confirm', message='set a target weight 1' )
            
        cmds.setAttr( browBS[0] + '.' + actTgt[0], 0  )        
        startPos = cmds.getAttr( loc + '.ty')
        
        tranY = endPos - startPos
        print (tranY)

    else:
        cmds.confirmDialog( title='Confirm', message='selected obj has no blendShape!!' )
    
    # translate "browShrink_head" yAxis
    sculptTarget = "browShrink_head"
    sculptBase = "shrink_base"                
    xyzVal = cmds.xform( sculptTarget, q=1, ws=1, t=1 ) 
    cmds.xform( sculptTarget, ws=1, t =( xyzVal[0], xyzVal[1] + tranY, xyzVal[2]) )
    
    #extract the Sculpt_head in zAxis     
    tget = isolatAxisBlend( sculptBase, sculptTarget, 'z' )
    browZ = cmds.rename( tget, actTgt[0].split('_')[0] + '_TZ' ) 

    aliasAtt = cmds.aliasAttr( bsNode, q=1 ) 
    maxNum = []
    for x, y in zip(*[iter(aliasAtt)]*2):
        num = y.split("[")[1][:-1]
        maxNum.append(int(num))
        
    #add corrective crvs in BlendShape    
    index = max(maxNum)+1
    cmds.blendShape( bsNode, e=1, t=( headBase, index, browZ, 1.0)  )
    cmds.setAttr( browBS[0] + '.' + actTgt[0], 1  )
    #cmds.delete( dnPOC, loc )
    cmds.xform( sculptTarget, ws=1, t =( xyzVal[0], xyzVal[1], xyzVal[2]) )
    cmds.hide(browZ)
    
  



def isolatAxisBlend( base, target, axis ):

    object = cmds.duplicate( target, n = target + "_dup_" + axis )
    obj = object[0]
    
    size = cmds.polyEvaluate( base, v = 1)
    for i in range( size ):
        xformBase = cmds.xform( base +".vtx[%s]"%str(i), q=1, t =1 )
        xformObj = cmds.xform( obj + ".vtx[%s]"%str(i), q=1, t =1)
        
        if axis == "z":
            cmds.xform( obj + ".vtx[%s]"%str(i), os=1, t= ( xformBase[0], xformBase[1], xformObj[2] ) ) 
        elif axis == "y":
            cmds.xform( obj + ".vtx[%s]"%str(i), os=1, t= ( xformBase[0], xformObj[1], xformBase[2] ) )     
        elif axis == "x":
            cmds.xform( obj + ".vtx[%s]"%str(i), os=1, t= ( xformObj[0], xformBase[1], xformBase[2] ) ) 
    return obj
    
    
    
def create_shrink_wrap(mesh, target, **kwargs):
    """
    Check available kwargs with parameters below.
    """
    parameters = [
        ("projection", 4),
        ("closestIfNoIntersection", 1),
        ("reverse", 0),
        ("bidirectional", 1),
        ("boundingBoxCenter", 1),
        ("axisReference", 1),
        ("alongX", 0),
        ("alongY", 0),
        ("alongZ", 1),
        ("offset", 0),
        ("targetInflation", 0),
        ("targetSmoothLevel", 0),
        ("falloff", 0),
        ("falloffIterations", 1),
        ("shapePreservationEnable", 0),
        ("shapePreservationSteps", 1)
    ]

    target_shapes = cmds.listRelatives(target, f=True, shapes=True, type="mesh", ni=True)
    if not target_shapes:
        raise ValueError("The target supplied is not a mesh")
    target_shape = target_shapes[0]

    shrink_wrap = cmds.deformer(mesh, type="shrinkWrap")[0]

    for parameter, default in parameters:
        cmds.setAttr(
            shrink_wrap + "." + parameter,
            kwargs.get(parameter, default))

    connections = [
        ("worldMesh", "targetGeom"),
        ("continuity", "continuity"),
        ("smoothUVs", "smoothUVs"),
        ("keepBorder", "keepBorder"),
        ("boundaryRule", "boundaryRule"),
        ("keepHardEdge", "keepHardEdge"),
        ("propagateEdgeHardness", "propagateEdgeHardness"),
        ("keepMapBorders", "keepMapBorders")
    ]

    for out_plug, in_plug in connections:
        cmds.connectAttr(
            target_shape + "." + out_plug,
            shrink_wrap + "." + in_plug)

    return shrink_wrap

    



#create null between the selected nodes and it's parent
#the selected nodes' transform becomes zero out
def createPntNull( mySelList ):    
     
    grpList =[]
    for nd in mySelList:
        
        pos = cmds.xform(nd, q=1, ws=1, rotatePivot=1 ) 
        
        if cmds.nodeType(nd) =="transform":
            topGrp = cmds.duplicate( nd, po=1, n=nd+"P" )[0]
            cmds.parent(nd, topGrp)
            grpList.append(topGrp)
            
        else: #joint, cluster....
            prnt = cmds.listRelatives( nd, p=1, type ="transform")
            emGrp = cmds.group( em=1, n= nd+"P" )
            cmds.xform( emGrp, ws=1, t=pos )
            cmds.parent( nd, emGrp )    
            grpList.append(emGrp)            
                        
            if prnt:
                cmds.parent( emGrp, prnt[0] )
    
    return grpList  #list of parent group nodes      


# new name should be given
def copyOrigMesh( obj, name ):
    
    #get the orig shapes with history and delete the ones with with same name.
    origShape = getOrigMesh( obj )

    if origShape:
        myOrig = origShape

        #unique origShape duplicated
        headTemp = cmds.duplicate( myOrig, n = name, renameChildren =1 )
        tempShape = cmds.listRelatives( headTemp[0], ad=1, type ='shape' )
     
        for ts in tempShape:
            if 'Orig' in ts:
                tempOrig = cmds.rename( ts, name+ 'Shape' )
            else:
                print ("delete %s"%ts)
                cmds.delete(ts)
        
        cmds.setAttr( tempOrig+".intermediateObject", 0)
        cmds.sets ( tempOrig, e=1, forceElement = 'initialShadingGroup' )

        for trs in ['t','r','s']:
            for c in ['x','y','z']:
                if cmds.getAttr( headTemp[0] + '.' + trs + c, lock =1 ):
                    cmds.setAttr(headTemp[0] + '.' + trs + c, lock =0 )
        return headTemp[0]
        
    else:
        cmds.confirmDialog( title='Confirm', message='selected object has no origShape(intermediateObject)' )
        

# get OrigShape and delete useless one
def getOrigMesh( obj ):
    
    shapes = cmds.listRelatives( obj, ad=1, type = 'shape')
    origList = [ s for s in shapes if "Orig" in s ]
    #check if it treverse forward the shape of the selection 
    origShape = []
    for org in origList:
        connections = cmds.listConnections( org, s=0, d=1 )
        if connections:
            origShape = org            
        
        else: cmds.delete( org )
    
    return origShape    




def shapeToCurve():
    mySel = cmds.ls(os=1, fl=1 )
    #freeze curve
    targetCrv = mySel[-1]
    cmds.makeIdentity(targetCrv, apply=True, t=1, r=1, s=1, n=0, pn=1)
    targetCrvShape = cmds.listRelatives( targetCrv, c=1, typ = "nurbsCurve" )
    sourceVtx = mySel[:-1]
    numVtx = len(sourceVtx)    
    if numVtx == 2:
    
        cmds.select( sourceVtx[0], sourceVtx[1])
        orderVtx = orderedVerts_edgeLoop()

    elif numVtx > 2:
        orderVtx = sourceVtx       
            
    for i, vtx in enumerate( orderVtx ):
        pos = cmds.xform( vtx, q=1, ws=1, t=1 ) 
        uParam = getUParam ( pos, targetCrv )
        print (uParam )       
        dnPOC = cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = 'dnPOC'+ str(i+1).zfill(2))
        #loc = cmds.spaceLocator ( n = "targetPoc"+ str(index+1).zfill(2))
        cmds.connectAttr (targetCrvShape[0] + ".worldSpace",  dnPOC + '.inputCurve')
        #cmds.setAttr ( dnPOC + '.turnOnPercentage', 1 )
        cmds.setAttr ( dnPOC + '.parameter', uParam )        
    
        posOnCrv = cmds.getAttr(dnPOC + ".position" )[0]        
        cmds.xform( vtx, ws=1, t= posOnCrv )


# place curve at the origin(0,0,0)        
def getUParam( pnt = [], crv = None):

    point = OpenMaya.MPoint(pnt[0],pnt[1],pnt[2])
    curveFn = OpenMaya.MFnNurbsCurve(getDagPath(crv))
    paramUtill=OpenMaya.MScriptUtil()
    paramPtr=paramUtill.asDoublePtr()
    isOnCurve = curveFn.isPointOnCurve(point)
    if isOnCurve == True:
        
        curveFn.getParamAtPoint(point , paramPtr,0.001,OpenMaya.MSpace.kObject )
    else :
        point = curveFn.closestPoint(point, paramPtr,0.001, OpenMaya.MSpace.kObject)
        curveFn.getParamAtPoint(point , paramPtr,0.001, OpenMaya.MSpace.kObject )
    
    param = paramUtill.getDouble(paramPtr)  
    return param
    

            


def getDagPath(objectName):
    '''
    This function let you get an MObject from a string representing the object name
    @param[in] objectName : string , the name of the object you want to work on 
    '''
    if isinstance(objectName, list)==True:
        oNodeList=[]
        for o in objectName:
            selectionList = OpenMaya.MSelectionList()
            selectionList.add(o)
            oNode = OpenMaya.MObject()
            selectionList.getDagPath(0, oNode)
            oNodeList.append(oNode)
        return oNodeList
    else:
        selectionList = OpenMaya.MSelectionList()
        print (selectionList, objectName)
        selectionList.add(objectName)
        oNode = OpenMaya.MDagPath()
        selectionList.getDagPath(0, oNode)
        return oNode


def splitXYZ(*pArgs):
    sel= cmds.ls(sl=1, type = "transform")
    if len(sel)<=1:
        cmds.warning( "Select the target you need to split, then select the base " )
        
    else:
        shape = cmds.listRelatives( sel[0], c=1 )[0]
        xyzTarget =[]
        if cmds.nodeType(shape) == "nurbsCurve":
            for i in ["x","y","z"]:        
                tgtCrv = isolatAxisCrv( sel[1], sel[0], i )            
                xyzTarget.append(tgtCrv)
                
        elif cmds.nodeType(shape) == "mesh":
            for i in ["x","y","z"]:        
                tgtMesh = isolatAxisMesh( sel[1], sel[0], i )            
                xyzTarget.append(tgtMesh)       
            
        cmds.blendShape( xyzTarget, sel[1], n = sel[0]+"_xyzBS" )
        print (xyzTarget)
        cmds.delete( xyzTarget )

        
def isolatAxisCrv( baseCrv, tgtCrv, axis ):
    
    newCrv = cmds.duplicate( tgtCrv, n = tgtCrv + "_dup_" + axis )[0]
    cvs = cmds.ls( newCrv + '.cv[*]', fl=1)
    size = len( cvs )

    for i in range( size ):
        
        xformBase = cmds.xform( baseCrv +".cv[%s]"%str(i), q=1, t =1 )
        xformTgt = cmds.xform( newCrv + ".cv[%s]"%str(i), q=1, t =1)
        
        if axis == "z":
            cmds.xform( newCrv + ".cv[%s]"%str(i), os=1, t= ( xformBase[0], xformBase[1], xformTgt[2] ) ) 
        if axis == "y":
            cmds.xform( newCrv + ".cv[%s]"%str(i), os=1, t= ( xformBase[0], xformTgt[1], xformBase[2] ) ) 
        if axis == "x":
            cmds.xform( newCrv + ".cv[%s]"%str(i), os=1, t= ( xformTgt[0], xformBase[1], xformBase[2] ) ) 
    
    return newCrv
    

def isolatAxisMesh( base, target, axis ):

    object = cmds.duplicate( target, n = target + "_dup_" + axis )
    obj = object[0]
    
    size = cmds.polyEvaluate( base, v = 1)
    for i in range( size ):
        xformBase = cmds.xform( base +".vtx[%s]"%str(i), q=1, t =1 )
        xformObj = cmds.xform( obj + ".vtx[%s]"%str(i), q=1, t =1)
        
        if axis == "z":
            cmds.xform( obj + ".vtx[%s]"%str(i), os=1, t= ( xformBase[0], xformBase[1], xformObj[2] ) ) 
        elif axis == "y":
            cmds.xform( obj + ".vtx[%s]"%str(i), os=1, t= ( xformBase[0], xformObj[1], xformBase[2] ) )     
        elif axis == "x":
            cmds.xform( obj + ".vtx[%s]"%str(i), os=1, t= ( xformObj[0], xformBase[1], xformBase[2] ) ) 
    return obj
    



def fixMix(*pArgs):
    mySel = cmds.ls(os=1, typ = "transform")
    headBase = mySel[0]
    target = mySel[1]

    shapes = cmds.listRelatives(headBase, s=1)
    #get intermediate shapes
    if len(cmds.ls(shapes[0]))==1:
    
        if cmds.objExists('mix'): cmds.delete('mix')
        elif cmds.objExists ('originGeo'): cmds.delete('originGeo')
        
        newTarget = cmds.duplicate( headBase, n = 'mix')
        tempChild = cmds.listRelatives(newTarget[0], c =1 )
        if tempChild:
            child = [ c for c in cmds.listRelatives(newTarget[0], c =1 ) if 'Orig' in c ]
            cmds.delete( child )   
        
        defaultMesh = copyOrigMesh( headBase, target + "_fix" )
        
        existBS = cmds.ls( "tempBS*", type = "blendShape" )
        tmpBS = cmds.blendShape( 'mix', target, defaultMesh, tc=0, n= 'tempBS'+ str(len(existBS)).zfill(2) )
        cmds.blendShape( tmpBS[0], e=1, w=[(0, 1.0), (1, -1.0)] )
        cmds.duplicate ( defaultMesh, n = 'minus')
        cmds.blendShape( tmpBS[0], edit=1, t=( defaultMesh, 2, 'minus', 1.0) )
        cmds.delete('minus')
        cmds.blendShape ( tmpBS[0], edit=1,  w = [ (0, 1.0),(1, 0.0),(2, -1.0)] )
        objBbox = cmds.xform ( defaultMesh, q =1, boundingBox =1 )
        
        if cmds.getAttr( defaultMesh + '.tx', lock=1) == True:
            cmds.setAttr( defaultMesh + '.tx', lock=0)
        cmds.setAttr( defaultMesh + '.tx', objBbox[3]-objBbox[0])
        cmds.select ( defaultMesh, 'mix', r=1)  
        
        activePanel = cmds.getPanel( withFocus=True )#return the name of the panel that currently has focus
        panelType = cmds.getPanel( typeOf =activePanel)#return the type of the specified panel
        if panelType == 'modelPanel':
            state = cmds.isolateSelect( activePanel, q=1, s=1)
            if state == 0:
                mel.eval('enableIsolateSelect %s 1' % activePanel)
            else:
                mel.eval('enableIsolateSelect %s 0' % activePanel)
                mel.eval('enableIsolateSelect %s 1' % activePanel)
    else:    
        cmds.confirmDialog( title='Confirm', message='there is more than 1 %s'%headBase )     
        

def targetAdd(*pArgs):    
    
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
    cmds.button( label = 'target Add/Reconnect', bgc=[.42,.5,.60], command = targetAddReconnect )
    
    cmds.showWindow(window)
    

def targetAddReconnect(*pArgs):
    bsNode = cmds.optionMenu( 'blendShape_list', query=True, value=True)
    print (bsNode)
    targetAdd_Reconnect_func( bsNode )

    
# select target(name!!) and base with blendShape( reconnect the target to blendShape )
def targetAdd_Reconnect_func( BSnode ):
    
    meshSel = cmds.ls(sl=1, typ ='transform')
    base = meshSel[-1]  
    tgtList = meshSel[:-1] 

    for i, target in enumerate(tgtList):

        shp = cmds.listRelatives( target, c=1, ni=1 )
        history = cmds.listHistory( target )
        deformList = [ x for x in history if "geometryFilter" in cmds.nodeType( x, inherited =1 )]
        if not deformList:
            xx = [ x for x in shp if "Orig" in x ]
            if xx:
                print ("delete %s"%xx)
                cmds.delete(xx)
            
        aliasAtt = cmds.aliasAttr(BSnode, q=1)
        if target in aliasAtt:
            for tgt, wgt in zip(*[iter(aliasAtt)]*2):
                tgtID = wgt.split("[")[1][:-1]        
                print (tgtID)
                # check if target curve exists
                if target == tgt :
                    tgtID = wgt.split("[")[1][:-1]
                    if cmds.nodeType(shp[0]) == "mesh":
                        connection = cmds.listConnections( BSnode+ ".inputTarget[0].inputTargetGroup[%s].inputTargetItem[6000].inputGeomTarget"%str(tgtID), sh=1 )
                        if connection:
                            continue
                        else:
                            print (shp[0], tgtID)
                            cmds.connectAttr( shp[0]+".worldMesh", BSnode+ ".inputTarget[0].inputTargetGroup[%s].inputTargetItem[6000].inputGeomTarget"%str(tgtID) )
                            
                    elif cmds.nodeType(shp[0]) == "nurbsCurve":
                        cmds.connectAttr( shp[0]+".worldSpace", BSnode+ ".inputTarget[0].inputTargetGroup[%s].inputTargetItem[6000].inputGeomTarget"%str(tgtID) )
                                    
        else:
            print (target)
            maxNum = []
            for x, y in zip(*[iter(aliasAtt)]*2):
                num = y.split("[")[1][:-1]
                maxNum.append(int(num))
                
            #add corrective crvs in BlendShape    
            maxNum = max(maxNum)            
        
            targetID = maxNum + 1
            cmds.blendShape( BSnode, e=1, t = [base, targetID, target, 1 ] )
            
            
            
            
# distance로 계산하므로 vtx 간 거리가 불규칙할 경우() 순서대로 선택해야 한다.
def vertices_distanceOrder( myVert ):    
    
    firstVert = myVert[0]
    orderedVerts = [firstVert]   
    
    while len(myVert)>1:
    
        myVert.remove(firstVert)
        firstPos = cmds.xform( firstVert, q=1, ws=1, t=1 )   
        
        vertDist = {}
        for vt in myVert:            
            
            vtPos = cmds.xform( vt, q=1, ws=1, t=1 )
            dist = distance( firstPos, vtPos)
            
            vertDist[ vt ] = dist    
        
        print (vertDist)
        secondVert = min(vertDist, key= vertDist. get) 
        print (secondVert)    
    
        orderedVerts.append(secondVert)
        firstVert = secondVert
                                
    return orderedVerts



def distance(inputA=[1,1,1], inputB=[2,2,2]):
    return math.sqrt(pow(inputB[0]-inputA[0], 2) + pow(inputB[1]-inputA[1], 2) + pow(inputB[2]-inputA[2], 2)) 

    
'''create brow curve for browMapSurf'''
#select verices in order to create reference curve/  
#turn off symmetry select / turn on tracking selection 
#select vertices in order(left half) or select start vert first / end vert last
#automatrically select right half in order using browCurve() with "closestPointOnMesh" to complete curve.
def curve_halfVertsFunc( myVert, name, openClose, degree ):
   
    vertNum = len(myVert)
    orderedBrow = []
    if "brow" in name:
        
        orderedBrow = vertices_distanceOrder( myVert )
        
        if orderedBrow:
            
            mapCrv = mapCurve( orderedBrow, name, openClose, degree )
            #mapEPCurve( ordered, name, openClose, degree ) #3degree epCurve create extra 2 CVs

    else:
        mapCrv = mapCurve( myVert, name, openClose, degree )
        #mapEPCurve( myVert, name, openClose, degree )

    # keepRange 0 - reparameterize the resulting curve from 0 to 1
    crvRebuild = cmds.rebuildCurve( mapCrv, ch =0, rpo =1, kr=0, kcp=1, kep=1, d= int(degree), n = name )
    
    if cmds.listHistory(crvRebuild[0]):
        cmds.delete( crvRebuild[0], ch=1 )
    
    cmds.xform( crvRebuild[0], centerPivots =1 )

'''
def EPCurve_chordLength():
    vtx = cmds.ls( os=1, fl=1 )
    vt = cmds.xform( vtx[0], q=1, t=1, ws=1)
    orderPos =[]
    # verts selection is only left part
    if vt[0]**2 <0.001:
	    for t in vtx[1:][::-1]:
		    vtxPos = cmds.xform( t, q=1, t=1, ws=1)
		    mrrPos = [-vtxPos[0],vtxPos[1],vtxPos[2]]
		    if vtxPos[0]-mrrPos[0]>0.001:
			    orderPos.append(mrrPos)        
	    print len(orderPos), 
	    for v in vtx:		    
		    vtxPos = cmds.xform( v, q=1, t=1, ws=1)
		    orderPos.append(vtxPos)

    coords = orderPos
    curveFn = OpenMaya.MFnNurbsCurve() 
    arr = OpenMaya.MPointArray() 
    
    for pos in coords: 
        arr.append(*pos) 
    print arr
    curveFn.createWithEditPoints( 
                                  arr, 
                                  3, 
                                  OpenMaya.MFnNurbsCurve.kPeriodic, 
                                  False, 
                                  False, 
                                  True 
                         	    )''' 
                         	    
                         	    
#select left vtx
def mapEPCurve( vtx, name, openClose, degree ):
      
    orderPos =[]
    if name in ["brow","lip"]:
        vt = cmds.xform( vtx[0], q=1, t=1, ws=1)
        # verts selection is only left part
        if vt[0]**2 <0.001:
            for t in vtx[1:][::-1]:

                vtxPos = cmds.xform( t, q=1, t=1, ws=1 )
                mrrPos = [-vtxPos[0],vtxPos[1],vtxPos[2]]
                orderPos.append(mrrPos)
                
            for v in vtx:

                vtxPos = cmds.xform( v, q=1, t=1, ws=1 )
                orderPos.append(vtxPos)
                
        # if verts selection in order entire region
        else:
            cmds.confirmDialog( title='Confirm', message='object or first vertex is off from center in X axis' )
            for v in vtx:
                vtxPos = cmds.xform( v, q=1, t=1, ws=1)
                orderPos.append(vtxPos)
    
    elif name == "eye":
    
        for v in vtx:
            vtxPos = cmds.xform( v, q=1, t=1, ws=1)
            orderPos.append(vtxPos)
                   
    if openClose == "open":
        browMapCrv = cmds.curve( d=float(degree), p=orderPos )
        cmds.rename( browMapCrv,  name + "MapCrv01" )
    
    elif openClose == "close":

        coords = orderPos
        curveFn = OpenMaya.MFnNurbsCurve() 
        arr = OpenMaya.MPointArray()
        for pos in coords: 
            arr.append(*pos)            
        
        curveFn.createWithEditPoints( 
                                      arr, 
                                      int(degree), 
                                      OpenMaya.MFnNurbsCurve.kPeriodic, 
                                      False, 
                                      False, 
                                      True 
                                    )
                

#버텍스 반만 순서대로 선택하면 미러한 포지션으로 커프를 만든다./ vtx = 이미 순서대로 정열된 버텍스 리스트
#geo should be symmetrical/ for open curve or curve is part of edge loop  
def mapCurve( vtx, name, openClose, degree ):
      
    orderPos =[]
    mirrOrderPos =[] 
    if name.split("_")[0] in ["brow","lip"]:
        vt = cmds.xform( vtx[0], q=1, t=1, ws=1)
        # verts selection is only left part
        if vt[0]**2 < 0.001:
            for t in vtx[1:][::-1]:
                vtxPos = cmds.xform( t, q=1, t=1, ws=1)
                mrrPos = [-vtxPos[0],vtxPos[1],vtxPos[2]]
                mirrOrderPos.append(mrrPos)
                
            for v in vtx:
                vtxPos = cmds.xform( v, q=1, t=1, ws=1 )
                orderPos.append(vtxPos)
        # if verts selection in order entire region
        else:
            cmds.confirmDialog( title='Confirm', message='object or first vertex is off from center in X axis' )
            for t in vtx[::-1]:
                vtxPos = cmds.xform( t, q=1, t=1, ws=1)
                mrrPos = [-vtxPos[0],vtxPos[1],vtxPos[2]]
                mirrOrderPos.append(mrrPos)
                
            for v in vtx:
                vtxPos = cmds.xform( v, q=1, t=1, ws=1 )
                orderPos.append(vtxPos)
                    
    elif name.split("_")[0] == "eye":
    
        for v in vtx:
            vtxPos = cmds.xform( v, q=1, t=1, ws=1)
            orderPos.append(vtxPos)
    
    # "open" / "close"
    if openClose == "open":
        orderPosAll = mirrOrderPos + orderPos
        browMapCrv = cmds.curve( d=float(degree), p= orderPosAll )
        #create unique name
        mapCrv = cmds.ls( name + "_crv*", typ = "transform" )
        if not mapCrv:
            newNum = 01
        else:
            lastNum = re.findall('\d+', mapCrv[-1])[0]
            newNum = int(lastNum)+1
        mapCrv = cmds.rename( browMapCrv,  name + "_crv"+ str(newNum).zfill(2) )
        return mapCrv
        
    elif openClose == "close":
        
        orderPosAll = mirrOrderPos[-2:] + orderPos[:-1] + mirrOrderPos[:-1] #if mirrOrderPos = []: orderPosAll = orderPos
        #create unique name
        mapCrv = cmds.ls( name + "_crv*", typ = "transform" )
        if not mapCrv:
            newNum = 01
        else:
            number = re.findall('\d+', mapCrv[-1])[0]
            newNum = int(number)+1
            
        '''circleCrv = cmds.circle( c = (0,0,0), nr = (0,0,1), sw = 360, r=1, d=3, tol = 0.01, s=len(orderPosAll) )
        cmds.reverseCurve( circleCrv[0], ch =1, rpo =1 )'''
        epCrv = cmds.curve( ep=orderPosAll, d=3 )
        cmds.closeCurve( epCrv, ch=0, ps=2, rpo=1, bb= 0.5, bki= 0, p= 0.1 )        
        guideCircle = cmds.rename( epCrv,  name + "_crv"+ str(newNum).zfill(2) )
        #zero out the center vertices
        circleCvs = cmds.ls( guideCircle + '.cv[*]', fl=1 )
        cvsNum = len(circleCvs)
        startCV = circleCvs[1]
        endCV = circleCvs[cvsNum/2+1]
        
        cmds.setAttr(  startCV + '.xValue', 0 )
        cmds.setAttr(  endCV + '.xValue', 0 )

        '''
        for index, pos in enumerate(orderPosAll) :
            
            cmds.xform( guideCircle + '.cv[%s]'%str(index+1), ws=1, t = pos )
        cmds.xform( guideCircle + '.cv[0]', ws=1, t = orderPosAll[-1] )'''
        
        cmds.select( guideCircle, r=1 )
        symmetrizeLipCrv(1)        
        cmds.delete( guideCircle, ch=1)        
        
        return guideCircle
        
        
# mapCurve(3, "open", "lip" )'''



def symmetrizeOpen( *pArgs ):
    check = cmds.checkBox( 'directionTo', query=True, value = True)
    print (check)
    symmetrizeOpenCrv(check)
    
def symmetrizeClose( *pArgs ):
    check = cmds.checkBox( 'directionTo', query=True, value = True)
    print (check)
    symmetrizeLipCrv(check)

    
# make symmetry for none periodic curve( with no deformer ) 
#select the curve and run
def symmetrizeOpenCrv(direction):

    #direction = cmds.checkBox( 'directionTo', query=True, value = True)
    crvSel = cmds.ls(sl=1, fl=1, long=1, type= "transform")
    crvNum = cmds.ls(crvSel[0]+".cv[*]", l=1, fl=1 )
    leng = len(crvNum )
        
    if direction == True:
        print ("left cv to right cv")
        for i in range(leng/2 ):
            xPos = cmds.getAttr(crvNum[leng-i-1]+".xValue" )
            cmds.setAttr( crvNum[i]+".xValue", -xPos)
            yPos = cmds.getAttr(crvNum[leng-i-1]+".yValue" )
            cmds.setAttr( crvNum[i]+".yValue", yPos)
            zPos = cmds.getAttr(crvNum[leng-i-1]+".zValue" )
            cmds.setAttr( crvNum[i]+".zValue", zPos)

    else:
        print ("right cv to left cv")
        for i in range(leng/2 ):
            xPos = cmds.getAttr(crvNum[i]+".xValue" )
            cmds.setAttr( crvNum[leng-i-1]+".xValue", -xPos)
            yPos = cmds.getAttr(crvNum[i]+".yValue" )
            cmds.setAttr( crvNum[leng-i-1]+".yValue", yPos)
            zPos = cmds.getAttr(crvNum[i]+".zValue" )
            cmds.setAttr( crvNum[leng-i-1]+".zValue", zPos)
            


# curve should have center cv[ 0, y, z]
def symmetrizeLipCrv(direction):

    crvSel = cmds.ls(sl=1, long=1, type= "transform")
    crvShp = cmds.listRelatives(crvSel[0], c=1, ni=1, s=1)
    
    if len(cmds.ls(crvShp))==1:
    
        periodic = cmds.getAttr( crvShp[0] + '.form' )
        crvCvs= cmds.ls(crvSel[0]+".cv[*]", l=1, fl=1 )
        numCv = len(crvCvs)
        
        numList = [ x for x in range(numCv) ]
        if periodic in [1, 2]:         
            if numCv%2 == 0:
                halfLen = (numCv-2)/2 
                centerCV =[]
                for cv in crvCvs:
                    pos = cmds.xform( cv, q=1, ws=1, t=1 )
                    if pos[0]**2 < 0.0001 :
                        print (cv)
                        num = cv.split('[')[1][:-1]
                        centerCV.append(int(num))
                
                if len(centerCV) == 2:
                    startNum = centerCV[0]+1
                    endNum = startNum+halfLen
                    halfNum = numList[startNum:endNum]
                    opphalf = numList[endNum+1:] + numList[:centerCV[0]]
                    # curve direction( --> )    
                    if cmds.xform( crvCvs[startNum], q=1, ws=1, t=1)[0]>0:
                        leftNum = halfNum
                        rightNum = opphalf[::-1]
                    # curve direction( <-- )    
                    elif cmds.xform( crvCvs[startNum], q=1, ws=1, t=1)[0]<0:
                        leftNum = opphalf
                        rightNum = halfNum[::-1]
                                
                    print (leftNum, rightNum)    
                    if direction == True:
                        print "left cv to right cv"
                        for i in range(halfLen):
                            pos = cmds.xform( crvCvs[leftNum[i]], q=1, ws=1, t=1 )
                            cmds.xform( crvCvs[rightNum[i]], ws=1, t=( -pos[0], pos[1], pos[2] ) )
                        
                    else:
                        print "right cv to left cv"
                        for i in range(halfLen):
                            pos = cmds.xform( crvCvs[rightNum[i]], q=1, ws=1, t=1 )
                            cmds.xform( crvCvs[leftNum[i]], ws=1, t=( -pos[0], pos[1], pos[2] ) )                
                else:
                    cmds.confirmDialog( title='Confirm', message='number of CVs( tx=0 :on center ) of curve should be 2!!!' )      
            
        if periodic == 0:
            if numCv%2 == 1:
                halfLen = (numCv-2)/2 
                centerNum = ''
                for cv in crvCvs:
                    pos = cmds.xform( cv, q=1, ws=1, t=1 )
                    if pos[0]**2 < 0.0001 :
                        num = cv.split('[')[1][:-1]
                        centerNum = int(num)
                    
                if centerNum:
                    halfNum = numList[centerNum+1:]
                    opphalf = numList[:centerNum]            
                    # curve direction( --> )    
                    if cmds.xform( crvCvs[centerNum+1], q=1, ws=1, t=1)[0]>0:
                        leftNum = halfNum
                        rightNum = opphalf[::-1]
                    # curve direction( <-- )    
                    elif cmds.xform( crvCvs[centerNum+1], q=1, ws=1, t=1)[0]<0:
                        leftNum = opphalf
                        rightNum = halfNum[::-1]        
                        
                    if direction == 1:
                        print "left cv to right cv"
                        for i in range( halfLen ):
                            pos = cmds.xform( crvCvs[leftNum[i]], q=1, ws=1, t=1 )
                            cmds.xform( crvCvs[rightNum[i]], ws=1, t=( -pos[0], pos[1], pos[2] ) )
                        
                    else:
                        print "right cv to left cv"
                        for i in range(halfLen ):
                            pos = cmds.xform( crvCvs[rightNum[i]], q=1, ws=1, t=1 )
                            cmds.xform( crvCvs[leftNum[i]], ws=1, t=( -pos[0], pos[1], pos[2] ) )

                else:
                    cmds.confirmDialog( title='Confirm', message='position the curve tx on center!!!' ) 

    else:
        cmds.confirmDialog( title='Confirm', message='more than 1 "%s" matches name!!'%crvShp[0] )



    
#miscellenious-----------------------------------------------------------------------chellenious-----------------------------------------------------------------------

#record_prototypeCrv measurement    
def prototypeCrv_data( protCrvs ):

    crvData = {}
    for crv in protCrvs:
        
        myCrv = cmds.duplicate( crv, rc=1 )[0]
        dupCrv = cmds.rename( myCrv, "tempCrv")
        dupCrvShp = cmds.listRelatives( dupCrv, c=1, fullPath=1, ni = 1 )
        
        if dupCrvShp:
            if cmds.nodeType(dupCrvShp[0]) == "nurbsCurve":
                          
                rPiv = cmds.xform(dupCrv, q=True, rp=True)  # query rotation pivot
                crvBbox = cmds.exactWorldBoundingBox( dupCrv )
                # scale X/Y to be uniform scale of 2 
                cmds.setAttr( dupCrv + ".sx", 1.0/crvBbox[3] )
                cmds.setAttr( dupCrv + ".sy", 2.0/(crvBbox[4]-crvBbox[1]) )
                cmds.setAttr( dupCrv + ".sz", 1.0/crvBbox[3] )               
                
                cvs = [ dupCrv + '.cv[1]', dupCrv + '.cv[2]', dupCrv + '.cv[3]', dupCrv + '.cv[5]', dupCrv + '.cv[7]', dupCrv + '.cv[8]', dupCrv + '.cv[9]' ]
                topPos = cmds.xform( cvs[0], q=1, ws=1, t=1 )
                upFirstPos = cmds.xform( cvs[1], q=1, ws=1, t=1)
                upMidPos = cmds.xform( cvs[2], q=1, ws=1, t=1)
                cornerPos = cmds.xform(cvs[3], q=1, ws=1, t=1)
                loMidPos = cmds.xform( cvs[4], q=1, ws=1, t=1)
                loFirstPos = cmds.xform( cvs[5], q=1, ws=1, t=1)
                bttmPos = cmds.xform(cvs[6], q=1, ws=1, t=1)
                
                #Ydistnace (top to corner)/(bttom to corner) : 1 (the closer to 1, the more central the cornerCv ) 
                centralCorner = (topPos[1]-cornerPos[1])/ (cornerPos[1] - bttmPos[1])
                #Zdistance/Xdistance 
                depthCorner =  abs(topPos[2]-cornerPos[2])
                #xyRatio = [ topYLength / cornerXLength, upFirstPosY/upFirstPosX, upMidPosZ/cornerZ!!! ]
                upXyRatio = [  abs(upFirstPos[1]-cornerPos[1])/upFirstPos[0], abs( upMidPos[2]-cornerPos[2])/(upMidPos[0]) ]                
                loXyRatio = [  abs(cornerPos[1]-loFirstPos[1])/loFirstPos[0], abs(loMidPos[2]-cornerPos[2])/(upMidPos[0]) ]
                
                #yValue (topCv - bttmCV)/ xValue cornerCV 
                #xyRatio = (topPos[1] - bttmPos[1]) /cornerPos[0]
                dupCrvBbox = cmds.exactWorldBoundingBox( dupCrv )                               
                NPOC = cmds.createNode("nearestPointOnCurve")
                cmds.connectAttr( dupCrvShp[0] + ".worldSpace", NPOC + ".inputCurve")
                cmds.setAttr(NPOC + ".inPosition", dupCrvBbox[3], dupCrvBbox[4], dupCrvBbox[2], type="double3")
                upShpPoint = cmds.getAttr( NPOC + ".position")[0]
                
                upMidDist = math.sqrt( pow(upShpPoint[0]-rPiv[0],2) + pow(upShpPoint[1]-rPiv[1],2) + pow(upShpPoint[2]-rPiv[2],2) )    

                  
                cmds.setAttr(NPOC + ".inPosition", dupCrvBbox[3], dupCrvBbox[1], dupCrvBbox[2], type="double3")
                loShpPoint = cmds.getAttr( NPOC + ".position")[0]
                
                loMidDist = math.sqrt( pow(loShpPoint[0]-rPiv[0],2) + pow(loShpPoint[1]-rPiv[1],2)+ pow(loShpPoint[2]-rPiv[2],2) )
                                
                #get parameter for upMidPos
                cmds.setAttr(NPOC + ".inPosition", upMidPos[0], upMidPos[1], upMidPos[2], type="double3") 
                
                upUParam = cmds.getAttr(NPOC + ".parameter") 
                #upLoc = cmds.spaceLocator( a=1, p= upMidPos, n= "upMidPoint_loc" )
                          
                #get distance loMidPoint
                cmds.setAttr(NPOC + ".inPosition", loMidPos[0], loMidPos[1], loMidPos[2], type="double3") 
                loUParam = cmds.getAttr(NPOC + ".parameter") 
                #loLoc = cmds.spaceLocator( a=1, p= loMidPos, n= "loMidPoint_loc" )        
             
                cmds.delete(dupCrv)
                
                if cmds.referenceQuery( crv, isNodeReferenced=True ) == True:
                    
                    fName = cmds.referenceQuery(crv, filename=True)
                    nameList = fName.split("/")[-1].split("_")
                    title = nameList[0] + nameList[1]                
                    
                else:
                    
                    fName = ""
                    title = crv               
        
                currentDict = { 
                                "centralCorner" : centralCorner,
                                "depthCorner" : depthCorner,
                                "upXY_ratio" : upXyRatio,
                                "loXY_ratio" : loXyRatio,
                                "upMidDist" : upMidDist,
                                "loMidDist" : loMidDist,
                                "upMidPointParam" : upUParam,
                                "loMidPointParam" : loUParam,
                                "sceneName":fName,
                                 }
                                 
                crvData[ title ] = currentDict
            
        else:
            cmds.confirmDialog( title='Confirm', message='%s is not nurbsCurve!! '%crv ) 
            
    return crvData  
    
def prototypeCrv_data_old( protCrvs ):

    crvData = {}
    for crv in protCrvs:
        
        crvShp = cmds.listRelatives( crv, c=1, fullPath=1, ni = 1 )
        if crvShp:
            if cmds.nodeType(crvShp[0]) == "nurbsCurve":
                          
                rPiv = cmds.xform(crv, q=True, rp=True)  # query rotation pivot
                crvBbox = cmds.exactWorldBoundingBox( crv )
                cvs = [ crv + '.cv[1]', crv + '.cv[3]', crv + '.cv[5]', crv + '.cv[7]', crv + '.cv[9]' ]
                topPos = cmds.xform( cvs[0], q=1, ws=1, t=1 )
                upMidPos = cmds.xform( cvs[1], q=1, ws=1, t=1)
                cornerPos = cmds.xform(cvs[2], q=1, ws=1, t=1)
                loMidPos = cmds.xform( cvs[3], q=1, ws=1, t=1)
                bttmPos = cmds.xform(cvs[4], q=1, ws=1, t=1)
                
                #Ydistnace (top to corner)/(bttom to corner) : 1 (the closer to 1, the more central the cornerCv ) 
                centralCorner = (topPos[1]-cornerPos[1])/ (cornerPos[1] - bttmPos[1])
                #Zdistance/Xdistance 
                depthCorner =  abs(topPos[2]-cornerPos[2])/cornerPos[0] 
                
                #yValue (topCv - bttmCV)/ xValue cornerCV 
                xyRatio = (topPos[1] - bttmPos[1]) /cornerPos[0]               
                
                
                NPOC = cmds.createNode("nearestPointOnCurve")
                cmds.connectAttr( crvShp[0] + ".worldSpace", NPOC + ".inputCurve")
                cmds.setAttr(NPOC + ".inPosition", upMidPos[0], upMidPos[1], upMidPos[2], type="double3") 
                
                upUParam = cmds.getAttr(NPOC + ".parameter") 
                #upLoc = cmds.spaceLocator( a=1, p= upMidPos, n= "upMidPoint_loc" )
                
                upMidDist = math.sqrt( pow(upMidPos[0]-rPiv[0],2) + pow(upMidPos[1]-rPiv[1],2) + pow(upMidPos[2]-rPiv[2],2) )
                
                cornerDistX = cornerPos[0]
                
                #get distance loMidPoint
                cmds.setAttr(NPOC + ".inPosition", loMidPos[0], loMidPos[1], loMidPos[2], type="double3") 
                loUParam = cmds.getAttr(NPOC + ".parameter") 
                #loLoc = cmds.spaceLocator( a=1, p= loMidPos, n= "loMidPoint_loc" )
                
                loMidDist = math.sqrt( pow(loMidPos[0]-rPiv[0],2) + pow(loMidPos[1]-rPiv[1],2) + pow(loMidPos[2]-rPiv[2],2) )    
                
                upMidRatio = upMidDist / cornerDistX     
                loMidRatio = loMidDist / cornerDistX                
             
                if cmds.referenceQuery( crv, isNodeReferenced=True ) == True:
                    
                    fName = cmds.referenceQuery(crv, filename=True)
                    nameList = fName.split("/")[-1].split("_")
                    title = nameList[0] + nameList[1]                
                    
                else:
                    
                    fName = ""
                    title = crv               
        
                currentDict = { 
                                "centralCorner" : centralCorner,
                                "xyRatio" : xyRatio, 
                                "depthCorner" : depthCorner,
                                "upMidRatio_toRadius" : upMidRatio,
                                "loMidRatio_toRadius" : loMidRatio,
                                "upMidPointParam" : upUParam,
                                "loMidPointParam" : loUParam,
                                "sceneName":fName,
                                 }
                                 
                crvData[ title ] = currentDict
            
        else:
            cmds.confirmDialog( title='Confirm', message='%s is not nurbsCurve!! '%crv ) 
            
    return crvData


def browProtoCrv_data_old(browCrvList):
                
    browCrvData = {}
    for browCrv in browCrvList:
        
        crvShp = cmds.listRelatives( browCrv, c=1, fullPath=1, ni = 1 )
        if crvShp:
            if cmds.nodeType(crvShp[0]) == "nurbsCurve":
        
                browBbox = cmds.exactWorldBoundingBox( browCrv )   
                xLength = browBbox[3]
                yLength = abs(browBbox[4]-browBbox[1])
                zLength = abs(browBbox[5]-browBbox[2])
                
                cvs = [ browCrv + '.cv[5]', browCrv + '.cv[7]', browCrv + '.cv[8]', browCrv + '.cv[10]' ]
                centerPos = cmds.xform( cvs[0], q=1, ws=1, t=1 )
                browInPos = cmds.xform( cvs[1], q=1, ws=1, t=1 )
                browMidPos = cmds.xform( cvs[2], q=1, ws=1, t=1)
                cornerPos = cmds.xform(cvs[3], q=1, ws=1, t=1)

                zDepthRatio = zLength/xLength
                yHeightRatio = yLength/xLength
                
                midToCenter = browMidPos[1] - centerPos[1]  
                midToCorner = browMidPos[1] - cornerPos[1]
                
                midYCurvature = midToCenter/midToCorner #the closer to 1 : steep curvature / closer to 0 : smooth curvature
                
                # xValue of "center to inPoint" / xValue of "inPoint to corner"
                inXdistRatio = ( inPos[0] )/ (cornerPos[0] - inPos[0])
                
                sceneName = cmds.file(q=True, sn=True)
                
                if cmds.referenceQuery( browCrv, isNodeReferenced=True ) == True:
                    
                    fName = cmds.referenceQuery(browCrv, filename=True)
                    nameList = fName.split("/")[-1].split("_")
                    title = nameList[0] + nameList[1]                
                    
                else:
                    
                    fName = ""
                    title = browCrv               
        
                currentDict = { 
                                "yHeightRatio" : yHeightRatio,
                                "zDepthRatio" : zDepthRatio, 
                                "midYCurvature" : midYCurvature,
                                "midXdistRatio":midXdistRatio,
                                "sceneName":fName,
                                
                                 }
                                 
                browCrvData[ title ] = currentDict
                    
            else:
                cmds.confirmDialog( title='Confirm', message='select "brow_prototypeCrvs"!! ' ) 
            
    return browCrvData
    
  
def browProtoCrv_data(browCrvList):
                
    browCrvData = {}
    for browCrv in browCrvList:
        
        crvShp = cmds.listRelatives( browCrv, c=1, fullPath=1, ni = 1 )
        if crvShp:
            if cmds.nodeType(crvShp[0]) == "nurbsCurve":
    
                browBbox = cmds.exactWorldBoundingBox( browCrv )   
                xLength = browBbox[3]
                yLength = abs(browBbox[4]-browBbox[1])
                zLength = abs(browBbox[5]-browBbox[2])
                
                cvs = [ browCrv + '.cv[5]', browCrv + '.cv[7]', browCrv + '.cv[8]', browCrv + '.cv[10]' ]
                centerPos = cmds.xform( cvs[0], q=1, ws=1, t=1 )
                browMidPos = cmds.xform( cvs[2], q=1, ws=1, t=1)
                cornerPos = cmds.xform(cvs[3], q=1, ws=1, t=1)

                zDepthRatio = zLength/xLength
                yHeightRatio = yLength/xLength
                
                topToCenter = browBbox[4] - centerPos[1]  
                topToCorner = browBbox[4] - cornerPos[1]
                
                # curvature in Y Axis
                yCurvature = topToCenter/topToCorner # the closer to 1 : steep curvature / closer to 0 : smooth curvature
                
                zCenterToMid = centerPos[2] - browMidPos[2]  
                zMidToCorner = browMidPos[2] - cornerPos[2]                
                
                # midCv 'cv[8]' location in Z Axis
                midZCurvature = zCenterToMid/zMidToCorner 
                
                # inPoint brow xRatio : xValue of "center to inPoint" / xValue of "inPoint to corner"
                midXdistRatio = browMidPos[0]/(cornerPos[0] - browMidPos[0])                          
                
                sceneName = cmds.file(q=True, sn=True)                
                
                if cmds.referenceQuery( browCrv, isNodeReferenced=True ) == True:
                    
                    fName = cmds.referenceQuery(browCrv, filename=True)
                    nameList = fName.split("/")[-1].split("_")
                    title = nameList[0] + nameList[1]                
                    
                else:
                    
                    fName = ""
                    title = browCrv               
        
                currentDict = { 
                                "yHeightRatio" : yHeightRatio,
                                "zDepthRatio" : zDepthRatio, 
                                "yCurvature" : yCurvature,
                                "midZCurvature" : midZCurvature,
                                "midXdistRatio": midXdistRatio,
                                "sceneName": fName,
                                
                                 }
                                 
                browCrvData[ title ] = currentDict
                
        else:
            cmds.confirmDialog( title='Confirm', message='%s is not nurbsCurve!! '%browCrv ) 
            
    return browCrvData





def writeCrvData_old(protCrvs, filePath): 
    
    fileName = filePath.split("/")[-1]
    print fileName
    
    if "lipCrv" in fileName:
        
        crvDict = prototypeCrv_data( protCrvs )                 
    
    elif "browCrv" in fileName:
        
        crvDict = browProtoCrv_data( protCrvs ) 
        
    else:
        cmds.confirmDialog( title='Confirm', message='The file name should include either "lipCrv" or "browCrv"!! ' )
    

    #check if the json file exists
    if os.path.isfile(filePath):
        
        #open json file
        with open(filePath) as json_file:
            crvData = json.load(json_file)
    
        crvsJson = crvData.keys()
        
        #add new crv       
        for newCrv, v in crvDict.items():
          
            if newCrv in crvsJson:
                pass
                
            else:
                dforms = [ x for x in cmds.listHistory( newCrv, il=1, pdo=1) if "geometryFilter" in cmds.nodeType( x, inherited=1)]
                if "blendShape" in dforms:
                    crvData[newCrv]= v

        toBeSaved = json.dumps(crvData, indent = 4 )
        dataFile = open(filePath, 'w')
        dataFile.write(toBeSaved)
        dataFile.close()
                        
    else:   

        toBeSaved = json.dumps(crvDict, indent = 4 )
        dataFile = open(filePath, 'w')
             
        dataFile.write(toBeSaved)
        dataFile.close()
    
def writeCrvData(protCrvs, filePath): 
    
    fileName = filePath.split("/")[-1]
    print fileName
    
    if "lipCrv" in fileName:        
  
        newCrvs = []
        for lipCrv in protCrvs:
            dforms = [ x for x in cmds.listHistory( lipCrv, il=1, pdo=1) if "geometryFilter" in cmds.nodeType( x, inherited=1)]
            bsNode = [y for y in dforms if cmds.nodeType(y) == "blendShape" ]
            if bsNode:
                newCrvs.append( lipCrv )
            else:
                cmds.confirmDialog( title='Confirm', message='%s has no blendShape!! '%lipCrv )   
        
        crvDict = prototypeCrv_data( newCrvs )
        toBeSaved = json.dumps(crvDict, indent = 4 )
        dataFile = open(filePath, 'w')
             
        dataFile.write(toBeSaved)
        dataFile.close()              
    
    elif "browCrv" in fileName:       

        newCrvs = []
        for browCrv in protCrvs:
            dforms = [ x for x in cmds.listHistory( browCrv, il=1, pdo=1) if "geometryFilter" in cmds.nodeType( x, inherited=1)]
            bsNode = [y for y in dforms if cmds.nodeType(y) == "blendShape" ]
            if bsNode:
                newCrvs.append( browCrv )
            else:
                cmds.confirmDialog( title='Confirm', message='%s has no blendShape!! '%browCrv ) 
                
        crvDict = browProtoCrv_data( protCrvs )
        toBeSaved = json.dumps(crvDict, indent = 4 )
        dataFile = open(filePath, 'w')
             
        dataFile.write(toBeSaved)
        dataFile.close()          
    
    else:
        cmds.confirmDialog( title='Confirm', message='The file name should include either "lipCrv" or "browCrv"!! ' )
    


def findClosesetCrvData( myCrv, filePath ):

    fileName = filePath.split("/")[-1]
    
    if "lipCrv" in fileName:
    
        tmpData = prototypeCrv_data( myCrv )
        myCrvData = tmpData[myCrv[0]]
        myCentral = myCrvData["centralCorner"]
        myDepth = myCrvData["depthCorner"]
        myUpXyRatio = myCrvData["upXY_ratio"]
        myLoXyRatio = myCrvData["loXY_ratio"]
        
        myUpMidDist = myCrvData[ "upMidDist" ]
        myLoMidDist = myCrvData[ "loMidDist" ]
        
        myUpMidParam = myCrvData[ "upMidPointParam" ]
        myLoMidParam = myCrvData[ "loMidPointParam" ]
        
        crvFile = open(filePath)
        crvData = json.load(crvFile)
                
        xyDict = {} 
        for k, zDict in crvData.items():           
            
            #xyRatio = [ topYLength / cornerXLength,  upFirstPosY/upFirstPosX, upMidPosY/upMidPosX ]
            upXyRatio = zDict["upXY_ratio"]
            upZipList = zip(myUpXyRatio, upXyRatio)
            upMinusList = [ abs(x -y) for (x, y) in upZipList ]  

            myUpXYGap = upMinusList[0] + upMinusList[1] + upMinusList[2]
            
            loXyRatio = zDict["loXY_ratio"]
            loZipList = zip(myLoXyRatio, loXyRatio)
            loMinusList = [ abs(x -y) for (x, y) in loZipList ]
             
            myLoXYGap = loMinusList[0] + loMinusList[1] + loMinusList[2]
            
            xyDict[k]= myUpXYGap + myLoXYGap
                    
        xyList = sorted( xyDict, key = xyDict.get)[:6]
        
        #renew ranking with xyRatio
        xyRank = {}
        for x, xyCrv in enumerate(xyList):
            xyRank[xyCrv] = x          
        
        print "xyRatioRank"
        print xyRank        
      
        #the closest point to the bounding box
        midDistDict = {} 
        for j, wDict in crvData.items():           
            
            #distance of midPoint (not CV) to curve pivot ( curve shape :how round the curve is ) 
            upMidDist = wDict["upMidDist"]
            myUpMidDistGap = abs(myUpMidDist - upMidDist)
            
            loMidDist = wDict["loMidDist"]
            myLoMidDistGap = abs(myLoMidDist - loMidDist)
            
            midDistDict[j]= myUpMidDistGap + myLoMidDistGap
                
        midDistList = sorted( midDistDict, key = midDistDict.get)[:6]
        
        #renew ranking with midDistance
        midDistRank = {}
        for y, mCrv in enumerate(midDistList):
            midDistRank[mCrv] = y
        
        print "midDistRank"
        print midDistRank                 
        
        commonDict = {} 
        for xyCrv, v in xyRank.items():
            if xyCrv in midDistRank:
                commonDict[xyCrv] = v + midDistRank[xyCrv] # sum of the ranking so far
                 
        print "midDistRank + xyRatioRank" 
        print commonDict
        
        commonLength = len(commonDict) 
        
        if commonLength == 0:
            
            cmds.confirmDialog( title='Confirm', message='adjust jawDrop shape and rerun the script!!' ) 
            
        elif 0< commonLength < 3:
            
            finalList = sorted( commonDict, key = commonDict.get)   
        
        elif commonLength >= 3:
            #Ydistnace (top to corner)/(corner to bttom )
            centralDict = {}
            for crv, dict in crvData.items(): 
                
                if crv in list(commonDict.keys()):
                    
                    central = dict["centralCorner"]
                    centralGap = abs(myCentral - central)
                    centralDict[crv]= centralGap
            
            centralList = sorted(centralDict, key=centralDict.get)
    
            centerRank = {}
            for n, cntCrv in enumerate(centralList):
                
                centerRank[cntCrv] = n + commonDict[cntCrv]
            
            centerRankList = sorted( centerRank, key = centerRank.get)[: commonLength-1 ] 
            
            print "central Corners Rank"
            print centerRankList
            
            centralLength = len(centerRankList)            
            
            if centralLength == 2 :
                finalList = centerRankList
    
            elif centralLength >= 3:                
                
                depthDict = {}
                for crv, dict in crvData.items():           
        
                    if crv in centralList:
                        depthCorner = dict["depthCorner"]
                        depthGap = abs(myDepth - depthCorner)
                        depthDict[crv]= depthGap
        
                depthList = sorted( depthDict, key = depthDict.get)       
                
                depthRank = {}
                for i, dpCrv in enumerate(depthList):
                    
                    depthRank[dpCrv] = i + centerRank[dpCrv]
                    
                finalList = sorted( depthRank, key = depthRank.get)[:2]
                
                print "the last ranking"
                print finalList
                
        if finalList:            
        
            for n, fCrv in enumerate(finalList):
            
                cmds.confirmDialog( title='Confirm', message=" the number %s is %s "%(str(n), fCrv ), button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
                fCrvDict = crvData[fCrv]
                referFile = fCrvDict["sceneName"]                
                cmds.file( referFile, i =1,  mergeNamespacesOnClash = 1 )
                
    elif "browCrv" in fileName:
        
        tmpData = browProtoCrv_data( myCrv ) 
        myCrvData = tmpData[myCrv[0]]
        
        myYHeightRatio = myCrvData["yHeightRatio"]
        myZDepthRatio = myCrvData["zDepthRatio"]
        myYCurvature = myCrvData["yCurvature"]
        myZCurvature = myCrvData["midZCurvature"]
        myMidXdistRatio = myCrvData["midXdistRatio"]
        
        crvFile = open(filePath)
        crvData = json.load(crvFile)    
        
        # curve zDepthRatio
        zDepthDict = {}
        for crv1, dict1 in crvData.items():         

            zDepthRatio = dict1["zDepthRatio"]
            zDepthGap = abs(myZDepthRatio - zDepthRatio)
            zDepthDict[crv1]= zDepthGap
        
        zDepthList = sorted( zDepthDict, key = zDepthDict.get)[:5]        
        print zDepthList
        
        #midCv[8] yValue of "center to midPoint" / yValue of "midPoint to corner"
        yCrvDict = {}
        for crv2, dict2 in crvData.items():
                    
            if crv2 in zDepthList:
                yCurvature = dict2["yCurvature"]
                yCrvGap = abs(myYCurvature - yCurvature)
                yCrvDict[crv2]= yCrvGap
        
        yCrvList = sorted(yCrvDict, key=yCrvDict.get)[:4]        
        print yCrvList
        #xValue of "center to midPoint" / xValue of "midPoint to corner"
        midXdistDict = {}
        for crv3, dict3 in crvData.items():        
            
            if crv3 in yCrvList:
                midXdistRatio = dict3["midXdistRatio"]
                midXdistGap = abs(myMidXdistRatio - midXdistRatio)
                midXdistDict[crv3]= midXdistGap

        midXdistlist = sorted(midXdistDict, key= midXdistDict.get)[:4]   

        
        shapeDict = {}
        for x, yCrv in enumerate(yCrvList):
            for y, xCrv in enumerate(midXdistlist):
                if xCrv == yCrv:
                    shapeDict[xCrv] = x+y
        shapeList = sorted( shapeDict, key = shapeDict.get)[:3]
        
        midZCrvDict = {}
        for crv4, dict4 in crvData.items():
                    
            if crv4 in shapeList:
                midZCurvature = dict4["midZCurvature"]
                midZCrvGap = abs(myZCurvature - midZCurvature )
                midZCrvDict[crv4]= midZCrvGap
        
        midZCrvList = sorted(midZCrvDict, key= midZCrvDict.get)[:3]
        print midZCrvList
        
        finalDict = {}
        for key, val in shapeDict.items():
            for i, dpCrv in enumerate(midZCrvList):
                if dpCrv == key:
                    finalDict[dpCrv] = val + i
            
        finalList = sorted( finalDict, key = finalDict.get)[:2]        
        print finalDict
        
        if finalList:            
        
            for n, fCrv in enumerate(finalList):
            
                cmds.confirmDialog( title='Confirm', message=" the number %s is %s' and the margin of error is %s"%(str(n), fCrv, finalDict[fCrv]), button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
                fCrvDict = crvData[fCrv]
                referFile = fCrvDict["sceneName"]                
                cmds.file( referFile, i =1,  mergeNamespacesOnClash = 1 ) 
    
    else:
        cmds.confirmDialog( title='Confirm', message='The file name should include either "lipCrv" or "browCrv"!! ' )
        
                
def findClosesetCrvData_old( myCrv, filePath ):

    fileName = filePath.split("/")[-1]
    
    if "lipCrv" in fileName:
        
        tmpData = prototypeCrv_data( myCrv )
        myCrvData = tmpData[myCrv[0]]
        myCentral = myCrvData["centralCorner"]
        myDepth = myCrvData["depthCorner"]
        myUpMidRatio = myCrvData["upMidRatio_toRadius"]
        myLoMidRatio = myCrvData["loMidRatio_toRadius"]
        myMidParam = myCrvData["midPointParam"]
        
        crvFile = open(filePath)
        crvData = json.load(crvFile)
        
        #Ydistnace (top to corner)/(corner to bttom )
        tmpDict = {}
        for crv, dic in crvData.items():        
            
            central = dic["centralCorner"]
            centralGap = abs(myCentral - central)
            tmpDict[crv]= centralGap

        gapList = sorted(tmpDict, key=tmpDict.get)[:5]

        # distance of midPoint (not CV) to distance cornerCV ratio ( curve shape :how round the curve is ) 
        midRatioDict = {}
        for ky, xDict in crvData.items():        
            
            if ky in gapList:
                upMidRatio = xDict["upMidRatio_toRadius"]
                loMidRatio = xDict["loMidRatio_toRadius"]
                upMidRatioGap = abs(myUpMidRatio - upMidRatio)
                loMidRatioGap = abs(myLoMidRatio - loMidRatio)
                
                midRatioDict[ky]= upMidRatioGap + loMidRatioGap

        midRatioList = sorted( midRatioDict, key = midRatioDict.get)[:4]
        
        shapeDict = {}
        for x, gapCrv in enumerate(gapList):
            for y, midCrv in enumerate(midRatioList):
                if midCrv == gapCrv:
                    shapeDict[midCrv] = x+y
        shapeList = sorted( shapeDict, key = shapeDict.get)[:3]
        
        # Zdistance/Xdistance = abs(topPos[2]-cornerPos[2])/abs(cornerPos[0])
        depthDict = {}
        for key, xDict in crvData.items():        
            
            if key in shapeList:
                depthCorner = xDict["depthCorner"]
                depthGap = abs(myDepth - depthCorner)
                depthDict[key]= depthGap
        
        depthList = sorted( depthDict, key=depthDict.get)[:3]        

        finalDict = {}
        for key, val in shapeDict.items():
            for i, dpCrv in enumerate(depthList):
                if dpCrv == key:
                    finalDict[dpCrv] = val + i
            
        finalList = sorted( finalDict, key = finalDict.get)[:2]  
        
        '''finalDict = {}
        for n, shpCrv in enumerate(shapeList):
            for m, dpCrv in enumerate(depthList):
                if dpCrv == shpCrv:
                    finalDict[dpCrv] = n + m
            
        finalList = sorted( finalDict, key = finalDict.get)[:2]        
        
        midParamDict = {}
        for kCrv, yDict in crvData.items():        
            
            if kCrv in depthList:
                midParam = yDict["midPointParam"]
                midParamGap = abs(myMidParam - midParam)
                midParamDict[kCrv]= midParamGap
        
        midParamList = sorted( midParamDict, key = midParamDict.get)[:2]
    
        #yValue (topCv - bttmCV)/ xValue cornerCV
        xyRatioDict = {} 
        for k, zDict in crvData.items():        
            
            if k in midParamList:
                xyRatio = zDict["xyRatio"]
                xyRatioGap = abs(myXyRatio - xyRatio)
                xyRatioDict[k]= xyRatioGap   
      
        if finalList:
            cmds.confirmDialog( title='Confirm', message='The best lipCurve is "%s"'%finalList, button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
        
            for fCrv in finalList:
            
                print "the %s's margin of error is %s"%(fCrv, finalDict[fCrv])
                fCrvDict = crvData[fCrv]
                referFile = fCrvDict["sceneName"]                
                cmds.file( referFile, index =1,  mergeNamespacesOnClash = 1 )'''
            
        if finalList:            
        
            for n, fCrv in enumerate(finalList):
            
                cmds.confirmDialog( title='Confirm', message=" the number %s is %s' and the margin of error is %s"%(str(n), fCrv, finalDict[fCrv]), button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
                fCrvDict = crvData[fCrv]
                referFile = fCrvDict["sceneName"]                
                cmds.file( referFile, i =1,  mergeNamespacesOnClash = 1 ) 
                
    elif "browCrv" in fileName:
        
        tmpData = browProtoCrv_data( myCrv ) 
        myCrvData = tmpData[myCrv[0]]
        
        myYHeightRatio = myCrvData["yHeightRatio"]
        myZDepthRatio = myCrvData["zDepthRatio"]
        myYCurvature = myCrvData["yCurvature"]
        myZCurvature = myCrvData["midZCurvature"]
        myMidXdistRatio = myCrvData["midXdistRatio"]
        
        crvFile = open(filePath)
        crvData = json.load(crvFile)    
        
        # curve zDepthRatio
        zDepthDict = {}
        for crv1, dict1 in crvData.items():         

            zDepthRatio = dict1["zDepthRatio"]
            zDepthGap = abs(myZDepthRatio - zDepthRatio)
            zDepthDict[crv1]= zDepthGap
        
        zDepthList = sorted( zDepthDict, key = zDepthDict.get)[:5]        
        print zDepthList
        
        #midCv[8] yValue of "center to midPoint" / yValue of "midPoint to corner"
        yCrvDict = {}
        for crv2, dict2 in crvData.items():
                    
            if crv2 in zDepthList:
                yCurvature = dict2["yCurvature"]
                yCrvGap = abs(myYCurvature - yCurvature)
                yCrvDict[crv2]= yCrvGap
        
        yCrvList = sorted(yCrvDict, key=yCrvDict.get)[:4]        
        print yCrvList
        #xValue of "center to midPoint" / xValue of "midPoint to corner"
        midXdistDict = {}
        for crv3, dict3 in crvData.items():        
            
            if crv3 in yCrvList:
                midXdistRatio = dict3["midXdistRatio"]
                midXdistGap = abs(myMidXdistRatio - midXdistRatio)
                midXdistDict[crv3]= midXdistGap

        midXdistlist = sorted(midXdistDict, key= midXdistDict.get)[:4]   

        
        shapeDict = {}
        for x, yCrv in enumerate(yCrvList):
            for y, xCrv in enumerate(midXdistlist):
                if xCrv == yCrv:
                    shapeDict[xCrv] = x+y
        shapeList = sorted( shapeDict, key = shapeDict.get)[:3]
        
        midZCrvDict = {}
        for crv4, dict4 in crvData.items():
                    
            if crv4 in shapeList:
                midZCurvature = dict4["midZCurvature"]
                midZCrvGap = abs(myZCurvature - midZCurvature )
                midZCrvDict[crv4]= midZCrvGap
        
        midZCrvList = sorted(midZCrvDict, key= midZCrvDict.get)[:3]
        print midZCrvList
        
        finalDict = {}
        for key, val in shapeDict.items():
            for i, dpCrv in enumerate(midZCrvList):
                if dpCrv == key:
                    finalDict[dpCrv] = val + i
            
        finalList = sorted( finalDict, key = finalDict.get)[:2]        
        print finalDict
        
        if finalList:            
        
            for n, fCrv in enumerate(finalList):
            
                cmds.confirmDialog( title='Confirm', message=" the number %s is %s' and the margin of error is %s"%(str(n), fCrv, finalDict[fCrv]), button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
                fCrvDict = crvData[fCrv]
                referFile = fCrvDict["sceneName"]                
                cmds.file( referFile, i =1,  mergeNamespacesOnClash = 1 ) 
    
    else:
        cmds.confirmDialog( title='Confirm', message='The file name should include either "lipCrv" or "browCrv"!! ' )   
  
    

#lip_smoothWeight select lipShpCrv and headGeo
def lipSmoothWeight( crv , headGeo ):

    mySel = cmds.ls(sl=1, typ = 'transform')
    lipShpCrv = mySel[0]
    headBase = mySel[1]
    if len(cmds.ls(headBase)) ==1 and len(cmds.ls(lipShpCrv)) ==1 :
        #create weight group
        if not cmds.objExists( 'lipWgt_grp' ):
            lipWgtGrp = cmds.group(em=1, n = 'lipWgt_grp')
        else:
            lipWgtGrp = 'lipWgt_grp'
            
        dupHead = cmds.duplicate( headBase, rc =1 )
        wgtHead = cmds.rename( dupHead, 'lipWgt_head' )
        
        dupCrv = cmds.duplicate( lipShpCrv, rc =1 )
        shpCrv = cmds.rename( dupCrv, 'lipWgt_crv' )    
        crvScl = cmds.getAttr( shpCrv + '.s' )[0]
        newScl = [ scl*1.2 for scl in crvScl ]
        cmds.setAttr( shpCrv + '.s', newScl[0], newScl[1], newScl[2] )        

        headBbox = cmds.exactWorldBoundingBox( wgtHead )
        
        xScLen = abs(headBbox[3])
        headCenter = cmds.objectCenter( wgtHead, gl=True )
        
        backCrvPivot = ( headCenter[0], headCenter[1], headBbox[2] )
        backCrv = cmds.circle( c=( 0, 0, 0),  nr = (0, 0, 1), sw= 360, d= 3, tol= 0.01, s= 16, ch= 1)[0]             
        makeCircle = cmds.listHistory( backCrv, il = 1, pdo =1 )
        cmds.setAttr( makeCircle[0] + ".radius", xScLen )
        cmds.reverseCurve( backCrv, ch =1, rpo =1 )
        backCircle = cmds.rename( backCrv,  shpCrv.split("_")[0] + "_backCrv" )
        cmds.xform( backCircle, ws=1, t = backCrvPivot )            
        
        softModD = softModForCrv(backCircle)
        for handle, ctl in softModD.items():
            cmds.parent( handle, lipWgtGrp )
            cmds.hide( handle )
            cmds.setAttr( ctl + ".tz" , headBbox[5] )                           
        
        shpCrvPivot = cmds.objectCenter(shpCrv, gl=True)
        cmds.select( lipWgtGrp, r=1)
        lipWgtJnt = cmds.joint( n="lipWgtJnt", p = shpCrvPivot)
        
        baseJnt = cmds.joint( n="baseWgtJnt", p = backCrvPivot )
        #ch 1 -u 1 -c 0 -ar 1 -d 1 -ss 1 -rn 0 -po 1 -rsn true "lipShape_backCrv" "lipShape_wire1";
        wgtSurf = cmds.loft ( backCircle, shpCrv, polygon=1, ch=1, c=0, ar = 1, d=1, u =1, ss =1, rn =1, reverseSurfaceNormals =1 )
        
        cmds.parent( shpCrv, wgtHead, backCircle, lipWgtGrp )
        
        for mesh in [wgtHead,wgtSurf[0]]:
            
            wgtSurfSkin =cmds.skinCluster( baseJnt, lipWgtJnt, mesh, normalizeWeights=1, toSelectedBones=True )
            
        for i in range( 32 ):
            cmds.select( wgtSurf[0] +".vtx[%s]"%str(i) ) 
            if i % 2 == 0:
                cmds.skinPercent(wgtSurfSkin[0], transformValue = [ lipWgtJnt, 0.1 ] )
            else:
                cmds.skinPercent(wgtSurfSkin[0], transformValue = [ lipWgtJnt, 1 ] )
        
        cmds.hide( wgtHead, shpCrv, backCircle, lipWgtJnt )           

        
    else:
        cmds.confirmDialog( title='Confirm', message='more than 1 lipCrv or headGeo!! ' )            

        

   

def softModForCrv(crv):

    upCvPos = cmds.xform( crv + '.cv[1]', q=1, ws=1, t=1)
    loCvPos = cmds.xform( crv + '.cv[9]', q=1, ws=1, t=1)
    posDict = { "up": upCvPos, "lo":loCvPos }

    softDict = {}
    for key, pos in posDict.items():
        
        softModD = cmds.softMod(crv, relative=False, falloffCenter = pos, falloffRadius=5.0, n= key + 'Soft_mod')

        ctlCrv = cmds.curve( d=1, p=[[0.0, 1.0, 0.0], [-0.382683, 0.92388000000000003, 0.0], [-0.70710700000000004, 0.70710700000000004, 0.0], [-0.92388000000000003, 0.382683, 0.0], [-1.0, 0.0, 0.0], [-0.92388000000000003, -0.382683, 0.0], [-0.70710700000000004, -0.70710700000000004, 0.0], [-0.382683, -0.92388000000000003, 0.0], [0.0, -1.0, 0.0], [0.382683, -0.92388000000000003, 0.0], [0.70710700000000004, -0.70710700000000004, 0.0], [0.92388000000000003, -0.382683, 0.0], [1.0, 0.0, 0.0], [0.92388000000000003, 0.382683, 0.0], [0.70710700000000004, 0.70710700000000004, 0.0], [0.382683, 0.92388000000000003, 0.0], [0.0, 1.0, 0.0], [0.0, 0.92388000000000003, 0.382683], [0.0, 0.70710700000000004, 0.70710700000000004], [0.0, 0.382683, 0.92388000000000003], [0.0, 0.0, 1.0], [0.0, -0.382683, 0.92388000000000003], [0.0, -0.70710700000000004, 0.70710700000000004], [0.0, -0.92388000000000003, 0.382683], [0.0, -1.0, 0.0], [0.0, -0.92388000000000003, -0.382683], [0.0, -0.70710700000000004, -0.70710700000000004], [0.0, -0.382683, -0.92388000000000003], [0.0, 0.0, -1.0], [0.0, 0.382683, -0.92388000000000003], [0.0, 0.70710700000000004, -0.70710700000000004], [0.0, 0.92388000000000003, -0.382683], [0.0, 1.0, 0.0], [-0.382683, 0.92388000000000003, 0.0], [-0.70710700000000004, 0.70710700000000004, 0.0], [-0.92388000000000003, 0.382683, 0.0], [-1.0, 0.0, 0.0], [-0.92388000000000003, 0.0, 0.382683], [-0.70710700000000004, 0.0, 0.70710700000000004], [-0.382683, 0.0, 0.92388000000000003], [0.0, 0.0, 1.0], [0.382683, 0.0, 0.92388000000000003], [0.70710700000000004, 0.0, 0.70710700000000004], [0.92388000000000003, 0.0, 0.382683], [1.0, 0.0, 0.0], [0.92388000000000003, 0.0, -0.382683], [0.70710700000000004, 0.0, -0.70710700000000004], [0.382683, 0.0, -0.92388000000000003], [0.0, 0.0, -1.0], [-0.382683, 0.0, -0.92388000000000003], [-0.70710700000000004, 0.0, -0.70710700000000004], [-0.92388000000000003, 0.0, -0.382683], [-1.0, 0.0, 0.0]])
        softCtl = cmds.rename( ctlCrv, softModD[1].split("_")[0] + "_ctl" )
        
        shapes = cmds.listRelatives(softCtl, shapes=True)
        for shape in shapes:
            cmds.setAttr("%s.overrideEnabled"%shape, 1)
            cmds.setAttr("%s.overrideColor"%shape, 14)
            
        controlGrp = createPntNull( [softCtl] )
        print controlGrp
        cmds.xform(controlGrp[0], ws=True, t=pos)

        # connect the pos, rot, scale of the control to the softModHandle
        cmds.connectAttr("%s.translate"%softCtl, "%s.translate"%softModD[1])
        cmds.connectAttr("%s.rotate"%softCtl, "%s.rotate"%softModD[1])
        cmds.connectAttr("%s.scale"%softCtl, "%s.scale"%softModD[1])
        
        cmds.addAttr(softCtl, ln="falloff", at="float", min=0, max=100, k=True, dv=5 )        

        # connect that attr to the softmod falloff radius
        cmds.connectAttr("%s.falloff"%softCtl, "%s.falloffRadius"%softModD[0])
        
        softDict[softModD[1]] = softCtl
        
    return softDict
    
    

def jointIndices( geo, jntList ):
    
    jntIndex = {}
    for jnt in jntList:
             
        connections = cmds.listConnections( jnt + '.worldMatrix[0]', p=1)
        geoSkin = mel.eval("findRelatedSkinCluster %s"%geo )
        for cnnt in connections:
            if geoSkin in cnnt:
                skinJntID = cnnt
        
        jntID = skinJntID.split(".")[1]
        jntIndex[jnt] = re.findall( '\d+', jntID )[0]
        
    return jntIndex



#research the crv shapes and parameter ##{u'|barbieLip_crv_grp|lipParam_wireCrv02': [0.0, 0.05363660170930254, 0.12546778749581972, 0.2520775429903461, 0.2974216966500808, 0.37895697129032, 0.44257646146633456, 0.5], u'|barbie_grandmaLip_grp|targetCrv_grp|lip_wire_crv01': [0.0, 0.04836654372178782, 0.12999410154951657, 0.2478650713167129, 0.3131318368164065, 0.37551059553018656, 0.43678986326725106, 0.5], u'|madMan_lipWire_Protype|baseCrv_grp|lipShpToCrv02': [0.0, 0.05565962947334612, 0.12367107770701294, 0.25183612569990255, 0.2971623071720158, 0.37881887117302876, 0.44208056545744756, 0.5]}
def lipShapeAverage():

    crvs = cmds.ls(sl=1, l =1 )
    cvParam = {}
    crvLsLen = len(crvs)    

    for crv in crvs:
            
        cvs = [ crv + '.cv[1]', crv + '.cv[2]', crv + '.cv[3]', crv + '.cv[4]', crv + '.cv[5]', crv + '.cv[6]', crv + '.cv[7]', crv + '.cv[8]', crv + '.cv[9]' ]
    
        paramList = []
        for i, cv in enumerate(cvs):
            
            pos = cmds.xform( cv, q=1, ws=1, t=1 ) 
            uParam = getUParam ( pos, crv )
            
            paramList.append(uParam )           
        
        cvParam[crv]=paramList
        print cvParam
        
    #sum of each parameter
    CVsLen = len(cvs)
    parmSumList = [ x*0 for x in range(CVsLen)]
    for crv, val in cvParam.items():
        
        for i, v in enumerate(val):
            parmSumList[i] = parmSumList[i] + v

    #print parmSumList
    
    avrg = [ p/crvLsLen for p in parmSumList ]
    return avrg



#select center vertex on the loop of lip / next vertex(direction)
def lip_prototypeCrv():

    selection = cmds.ls(os=1, )
    verts = cmds.filterExpand(selection, sm=31)
    #select only vertices
    if not verts and not len(verts)==2:
        raise Exception("You must select 2 vertices") # exits method or function

    firstVert, secondVert = verts# it becomes curve cv[1],cv[2]

    cmds.select (firstVert,secondVert, r =1)
    # select vertices on the loop
    tempVerts = orderedVerts_edgeLoop()
    vertsOnLoop = [tempVerts[-1]] + tempVerts +tempVerts[:2]
    vertsPos = []
    for v in vertsOnLoop:
        pos = cmds.xform( v, q =1, ws =1, t =1 )
        vertsPos.append(pos)

    #knots = number of CVs + degree - 1
    knotLen = [ x for x in range(len(vertsPos)+2) ]
    tempCrv = cmds.curve( d =3, per=1, p = vertsPos , k = knotLen )
    loopCrv = cmds.rebuildCurve( tempCrv, ch =0, replaceOriginal =1, keepRange=0, keepControlPoints=1, keepEndPoints=1, degree=3 )[0]
    cmds.xform( loopCrv, centerPivots=1 )

    avrg = [0.0, 0.054260471676417114, 0.12498473808447197, 0.19663351979864205, 0.250, 0.3018463892654337, 0.3788140065929279, 0.44033009804322876, 0.5]

    loopCrvShp = cmds.listRelatives( loopCrv, c=1, typ = "nurbsCurve")[0]
    pointPos = []
    for i, param in enumerate(avrg):

        paramPoc = cmds.shadingNode( 'pointOnCurveInfo', asUtility =1, n = 'paramPoc'+ str(i+1))
        cmds.connectAttr( loopCrvShp + ".worldSpace", paramPoc + ".inputCurve")
        cmds.setAttr( paramPoc + ".parameter", param )
        pos = cmds.getAttr(paramPoc + ".result.position")[0]

        pointPos.append(list(pos))
        #loc = cmds.spaceLocator ( n = "lipPoc_loc"+str(index+1) )[0]
        #cmds.connectAttr( paramPoc + '.result.position', loc + '.translate' )

    prototypeCurve( pointPos, "lip", "periodic", 3 )


def prototypeCurve( pointPos, name, openClose, degree ):
    """

    Args:create prototype normalized curve based on the lip edgeLoop vertices
        pointPos: positions of the ordered vertices on edge loop
        name: str "lip" or "brows"
        openClose: curve form ( "open","periodic")
        degree: 3

    Returns:

    """
    orderPos =[]
    mirrOrderPos =[] 

    pos1 = pointPos[0]
    # verts selection is only left part
    if pos1[0]**2 >= 0.001:
        raise RuntimeError('object or center vertex is off from center in X axis')

    for pp in pointPos[::-1]:

        mrrPos = [-pp[0],pp[1],pp[2]]
        mirrOrderPos.append(mrrPos)

    # "open" / "close"
    if openClose == "open":
        orderPosAll = mirrOrderPos[:-1] + orderPos
        browMapCrv = cmds.curve( d=float(degree), p= orderPosAll )
        #create unique name
        mapCrv = cmds.ls( name + "_normalizedCrv*", typ = "transform" )
        if not mapCrv:
            number = 01
        else:
            number = len(mapCrv)
        mapCrv = cmds.rename( browMapCrv,  name + "_normalizedCrv"+ str(number).zfill(2))
        return mapCrv
        
    elif openClose == "periodic":
        
        #create unique name
        mapCrv = cmds.ls( name + "_normalizedCrv*", typ = "transform" )

        if not mapCrv:
            number = 01
        else:
            number = len(mapCrv)
            
        '''#create cv curve
        #앞 3개의 포인트와 마지막 세개의 포인트가 같아야 한다( 앞뒤 3개의 CVs가 하나의 span 을 만들기 때문에 )
        orderPos = mirrOrderPos[-2:] + pointPos[1:] + mirrOrderPos[1:] + pointPos[1:2]
        print orderPos
        knotLen = [ x for x in range(len(orderPos)+2) ]
        closeCrv = cmds.curve( d =3, per=1, p = orderPos , k = knotLen  )'''
        
        #create ep curve
        coords = pointPos + mirrOrderPos[1:]

        curveFn = OpenMaya.MFnNurbsCurve() 
        arr = OpenMaya.MPointArray()
        for position in coords: 
            arr.append(*position)            
        
        periodicCurve = curveFn.createWithEditPoints(
                                      arr, 
                                      int(degree), 
                                      OpenMaya.MFnNurbsCurve.kPeriodic, 
                                      False, 
                                      False, 
                                      True 
                                    )

        lip_crv = curveFn.name()
        print (lip_crv)
        curveDepNode = OpenMaya.MFnDependencyNode(periodicCurve)
        lip_crv = curveDepNode.setName(name + "_normalized_crv" + str(number).zfill(2))
        cmds.xform( (name + "_normalized_crv" + str(number).zfill(2)), centerPivots=1 )
        return lip_crv



#select 2 adjasent vertices ( corner and direction vertex)
#edge loop상에 있는 버텍스 순서대로 나열한다( for curves )
def orderedVerts_edgeLoop():

    myVert = cmds.ls( os=1, fl=1 )
    if len(myVert)==2:
        firstVert = myVert[0]
        secondVert = myVert[1]
        
        cmds.select (firstVert,secondVert, r =1)
        mel.eval('ConvertSelectionToContainedEdges')        
        firstEdge = cmds.ls( sl=1 )[0]
        
        cmds.polySelectSp( firstEdge, loop =1 )
        edges = cmds.ls( sl=1, fl=1 )
        edgeDict = edgeVertDict(edges) #{edge: [vert1, vert2], ...}
        ordered = [firstVert, secondVert]
        for i in range( len(edges)-2 ):            
            del edgeDict[firstEdge]
            #print edgeDict
            for x, y in edgeDict.iteritems():
                if secondVert in y:                    
                    xVerts = y
                    xVerts.remove(secondVert)
                    firstEdge = x
        
            secondVert = xVerts[0]
            ordered.append( secondVert )
        return ordered
    
    else:
        print 'select 2 adjasent vertex!!'
        
def edgeVertDict(edgeList):
    edgeVertDict = { }
    for edge in edgeList:
        cmds.select(edge, r =1)
        cmds.ConvertSelectionToVertices()
        edgeVert = cmds.ls(sl=1, fl=1)
        edgeVertDict[edge] = edgeVert
    return edgeVertDict


