import maya.cmds as cmds
import os

def copyWeightUI(geo):
    print geo
    #check to see if window exists
    if cmds.window ('copyWeightUI', exists = True):
        cmds.deleteUI( 'copyWeightUI')

    #create window
    window = cmds.window( 'copyWeightUI', title = 'copyWeight UI', w = 400, h =400, mnb = True, mxb = True, sizeable=True, resizeToFitChildren = True )

    #main layout
    mainLayout = cmds.columnLayout( w =400, h= 200)
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    #rowColumnLayout
    cmds.rowColumnLayout( numberOfColumns = 3, columnWidth = [(1, 100),(2, 120),(3, 120)], columnOffset = [(1, 'right', 10)] )
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.text( label = '')
    cmds.text( label = 'source deformer')
    cmds.text( label = 'source subItems')
    cmds.text( label = '')
    dformers = [ x for x in cmds.listHistory(geo, il=1, pdo=1) if "geometryFilter" in cmds.nodeType( x, inherited=1)]
    option = cmds.optionMenu('source_deformer', changeCommand= printNewMenuItem )
    for dformer in dformers:
        cmds.menuItem( label= dformer )

    cmds.button( label = 'select sub_item', bgc=[.42,.5,.60], command = selectSourceItem )
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    
    '''
    dform = cmds.optionMenu(option, q=1, v = 1 )
    tgtList =[]
    if cmds.nodeType(dform) == "blendShape":
        aliasAtt = cmds.aliasAttr(BSnode, q=1)        
        for tgt, wgt in zip(*[iter(aliasAtt)]*2):
            tgtList.append(tgt)

    cmds.optionMenu('source bs target', changeCommand= printNewMenuItem )    
    if tgtList:
        for tg in tgtList:
            cmds.menuItem( label= tg )'''
        
    cmds.showWindow(window)


def pasteWeightUI(geo):
    if cmds.window ('pasteWeightUI', exists = True):
        cmds.deleteUI( 'pasteWeightUI')

    #create window
    window = cmds.window( 'pasteWeightUI', title = 'pasteWeight UI', w = 400, h =400, mnb = True, mxb = True, sizeable=True, resizeToFitChildren = True )

    #main layout
    mainLayout = cmds.columnLayout( w =400, h= 200 )

    #rowColumnLayout
    cmds.rowColumnLayout( numberOfColumns = 3, columnWidth = [(1, 100),(2, 120),(3, 120)], columnOffset = [(1, 'right', 10)] )
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    
    cmds.text( label = '')
    cmds.text( label = 'target deformer')
    cmds.text( label = 'target_subItems')    
    cmds.text( label = '')
    dformers = [ x for x in cmds.listHistory(geo, il=1, pdo=1) if "geometryFilter" in cmds.nodeType( x, inherited=1)]
    option = cmds.optionMenu('target_deformer', changeCommand= printNewMenuItem )
    for dformer in dformers:
        cmds.menuItem( label= dformer )

    cmds.button( label = 'select sub_item', bgc=[.42,.5,.60], command = selectTargetItem )
    
    cmds.text( label = '')

    cmds.text( label = '')
    cmds.text( label = '')
    cmds.text( label = '')
    
    cmds.showWindow(window)
    
    
    
    
    

def printNewMenuItem( item ):
    print item

def selectSourceItem(*pArgs):
    dform = cmds.optionMenu('source_deformer', query=True, value=True)
    print "deformer is " + dform
    if cmds.window ('sourceItem_select', exists = True):
        cmds.deleteUI( 'sourceItem_select')
        
    cmds.window('sourceItem_select', title = 'sourceSelect UI', w = 300, h = 200, mnb = True, mxb = True, sizeable=True, resizeToFitChildren = True )
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
    if cmds.nodeType(dform) == "blendShape":
        aliasAtt = cmds.aliasAttr(dform, q=1)
        for tgt, wgt in zip(*[iter(aliasAtt)]*2):
            tgtList.append(tgt)
    elif cmds.nodeType(dform) == "skinCluster":
        tgtList = cmds.skinCluster( dform, q=1, inf=1 )
        
    cmds.optionMenu('source_subItem', changeCommand= printNewMenuItem )
    if tgtList:
        for tg in tgtList:
            cmds.menuItem( label= tg )

    cmds.button( label = 'store src weight', bgc=[.42,.5,.60], command = store_srcWeight )
    
    cmds.showWindow()




def selectTargetItem(*pArgs):
    dform = cmds.optionMenu('target_deformer', query=True, value=True)
    if cmds.window ('sourceItem_select', exists = True):
        cmds.deleteUI( 'sourceItem_select' )
    
    if cmds.window ('targetItem_select', exists = True):
        cmds.deleteUI( 'targetItem_select')
        
    cmds.window('targetItem_select', title = 'targetSelect UI', w = 300, h = 200, mnb = True, mxb = True, sizeable=True, resizeToFitChildren = True )
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
    if cmds.nodeType(dform) == "blendShape":
        aliasAtt = cmds.aliasAttr(dform, q=1)
        for tgt, wgt in zip(*[iter(aliasAtt)]*2):
            tgtList.append(tgt)
    elif cmds.nodeType(dform) == "skinCluster":
        tgtList = cmds.skinCluster( dform, q=1, inf=1 )
        
    cmds.optionMenu('target_subItem', changeCommand= printNewMenuItem )
    if tgtList:
        for tg in tgtList:
            cmds.menuItem( label= tg )

    cmds.text( label = '')
    cmds.text( label = '')
    cmds.button( label = 'paste target weight', bgc=[.42,.5,.60], command = pasteTargetWgt )
    cmds.button( label = 'paste invert weight', bgc=[.42,.5,.60], command = pasteInvert_targetWgt )
    
    cmds.showWindow()

    
def store_srcWeight( *pArgs ):
    mySel = cmds.ls(sl=1, typ= 'transform')
    if mySel:
        geo = mySel[0]
    else:
        cmds.confirmDialog( title='Confirm', message=' select geo with deformer' )
        
    dformer = cmds.optionMenu('source_deformer', query=True, value=True)

    subItem = cmds.optionMenu('source_subItem', query=True, value=True ) 
    print "dformer is " + dformer, subItem
    
    vtxLeng = cmds.polyEvaluate( geo, v=1 )
    if cmds.nodeType(dformer) == "cluster":
            
        geoID = geoIDforCls( geo, dformer)
        wgt = cmds.getAttr(  dformer + ".wl[%s].w[0:%s]"%( str(geoID), str(vtxLeng-1) ) ) 

    elif cmds.nodeType(dformer) == "blendShape":
        
        alias = cmds.aliasAttr(dformer, q=1)
        tgID = ""
        for tgt, wgt in zip(*[iter(alias)]*2):
            if tgt == subItem:
                number = wgt.split("[")[1]
                tgID = number[:-1]
                
        print tgID
        wgt = cmds.getAttr( dformer + ".inputTarget[0].inputTargetGroup[%s].targetWeights[0:%s]"%( tgID, str(vtxLeng-1)) )
            
    #elif cmds.nodeType(dformer) == "wire" 
            
    #elif cmds.nodeType(dformer) == "skinCluster"
    
    if not cmds.objExists( 'helpPanel_grp'):

        cmds.group(em=1, n = 'helpPanel_grp' )

    if cmds.attributeQuery( "weight_storage", node = "helpPanel_grp", exists=1)==False:
        
        cmds.addAttr( "helpPanel_grp", ln = "weight_storage", dt = "doubleArray"  )
    
    cmds.setAttr( "helpPanel_grp.weight_storage", wgt, type= "doubleArray")


def geoIDforCls( geo, cls):
         
    clsObj = cmds.cluster( cls, q=1, g=1 )
    
    # get the source geoID for the cluster
    geoID = None
    for i, x in enumerate(clsObj):
        infGeo = cmds.listRelatives( x, p =1 )[0]
        if infGeo == geo:
            geoID = i           
            
    if geoID == None:
        cmds.warning( "selected geometry is not in the cluster's objList " )       
    else:
        return geoID
        


def pasteTargetWgt( *pArgs ):

    mySel = cmds.ls(sl=1, typ= 'transform')
    if mySel:
        geo = mySel[0]
    else:
        cmds.confirmDialog( title='Confirm', message=' select geo with deformer' )
    
    attrList = cmds.listAttr("helpPanel_grp", array=1 )
    wgtAttr = [ x for x in attrList if x == "weight_storage" ]
    
    if wgtAttr:
        vtxLeng = cmds.polyEvaluate( geo, v=1 )
        dformer = cmds.optionMenu('target_deformer', query=True, value=True )
        subItem = cmds.optionMenu( 'target_subItem', query=True, value=True ) 
        #transfer target weight
        weightList = cmds.getAttr( "helpPanel_grp." + wgtAttr[0] )
        
        if len(weightList) == vtxLeng:
        
            if cmds.nodeType(dformer) == "cluster":
                    
                geoID = geoIDforCls( geo, cls )
                cmds.setAttr(  dformer + ".wl[%s].w[0:%s]"%( str(geoID), str(vtxLeng-1) ), *weightList ) 

            elif cmds.nodeType(dformer) == "blendShape":
                alias = cmds.aliasAttr(dformer, q=1)
                tgID = ""
                for tgt, wgt in zip(*[iter(alias)]*2):
                    if tgt == subItem:
                        number = wgt.split("[")[1]
                        tgID = number[:-1]  
                
                cmds.setAttr( dformer + ".inputTarget[0].inputTargetGroup[%s].targetWeights[0:%s]"%( int(tgID), vtxLeng-1), *weightList )
    
        else:
            cmds.confirmDialog( title='Confirm', message='the selected object has different number of vertices to the source obj' )        
    else:
        cmds.confirmDialog( title='Confirm', message=' store weight first!!' )
    

def pasteInvert_targetWgt( *pArgs ):

    mySel = cmds.ls(sl=1, typ= 'transform')
    if mySel:
        geo = mySel[0]
    else:
        cmds.confirmDialog( title='Confirm', message=' select geo with deformer' )

    attrList = cmds.listAttr("helpPanel_grp", array=1 )
    wgtAttr = [ x for x in attrList if x == "weight_storage" ]
    
    if wgtAttr:
        vtxLeng = cmds.polyEvaluate( geo, v=1 )
        dformer = cmds.optionMenu('target_deformer', query=True, value=True )
        subItem = cmds.optionMenu( 'target_subItem', query=True, value=True ) 
        #transfer target weight
        weightList = cmds.getAttr( "helpPanel_grp." + wgtAttr[0] )
        if len(weightList) == vtxLeng:
        
            invertWeight = []
            for wgt in weightList:
                invert = 1 - wgt
                invertWeight.append( invert )
            
            if cmds.nodeType(dformer) == "cluster":
                    
                geoID = geoIDforCls( geo, cls )
                cmds.setAttr(  dformer + ".wl[%s].w[0:%s]"%( str(geoID), str(vtxLeng-1) ), *invertWeight ) 

            elif cmds.nodeType(dformer) == "blendShape":
                alias = cmds.aliasAttr(dformer, q=1)
                tgID = ""
                for tgt, wgt in zip(*[iter(alias)]*2):
                    if tgt == subItem:
                        number = wgt.split("[")[1]
                        tgID = number[:-1]  
                
                cmds.setAttr( dformer + ".inputTarget[0].inputTargetGroup[%s].targetWeights[0:%s]"%( int(tgID), vtxLeng-1), *invertWeight )    

        else:
            cmds.confirmDialog( title='Confirm', message='the selected object has different number of vertices to the source obj' )  
            
    else:
        cmds.confirmDialog( title='Confirm', message=' store weight first!!' )    
    
    
 #copy cluster weight to blendShape target weight
def transferWeight(cls, bs, targetID ):
    
    headGeo = cmds.getAttr("helpPanel_grp.headGeo")
    size = cmds.polyEvaluate( headGeo, v=1)
    target = cmds.ls(sl=1, type="transform")[0]
    valStr = []
    for i in range(size):
        copyWgt = cmds.getAttr( cls+ ".wl[0].w[%s]"%str(i) )
        valStr.append(copyWgt)
            
    cmds.setAttr( bs + ".inputTarget[0].inputTargetGroup[%s].targetWeights[0:%s]"%(targetID, size-1), *valStr )   