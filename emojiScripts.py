# -*- coding: utf-8 -*-
import maya.cmds as cmds
import maya.mel as mel
import re



def charCtrlUI():
    #check to see if window exists
    if cmds.window ('charCtlUI', exists = True):
        cmds.deleteUI( 'charCtlUI')

    #create window
    window = cmds.window( 'charCtlUI', title = 'char ctrls', w =400, h =500, mnb = True, mxb = True, sizeable=True, resizeToFitChildren = True )

    #main layout
    mainLayout = cmds.scrollLayout(	horizontalScrollBarThickness=16, verticalScrollBarThickness=16 )
    #cmds.columnLayout( w =420, h=800)

    #rowColumnLayout
    cmds.rowColumnLayout( numberOfColumns = 3, columnWidth = [(1, 140),(2, 120),(3, 120)], columnOffset = [(1, 'right', 10)] )
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    
    cmds.text( label = 'faceCtrls')
    cmds.optionMenu('face_area', changeCommand=printNewMenuItem )
    cmds.menuItem( label= "faceBasic" )
    cmds.menuItem( label= "mouth" )
    cmds.menuItem( label= "eye" )
    cmds.text( label = '')

    cmds.separator( h = 15)
    cmds.button( label = 'selectCtrls', command = faceSelect )  
    cmds.button( label = 'setKey', command = faceSetKeys )
    cmds.separator( h = 15)    
    cmds.button( label = 'reset', command = faceResetCtrl )
    cmds.text( label = '')    
    cmds.separator( h = 15)    
    cmds.separator( h = 15)
    cmds.separator( h = 15)
    
    cmds.text( label = 'bodyCtrls')
    cmds.optionMenu('body_area', changeCommand=printNewMenuItem )
    cmds.menuItem( label= "bodyBasic" )
    cmds.menuItem( label= "lHandFingers" )
    cmds.menuItem( label= "rHandFingers" )
    cmds.text( label = '')

    cmds.separator( h = 15)
    cmds.button( label = 'selectCtrls', command = bodySelect )  
    cmds.button( label = 'setKey', command = bodySetKeys )
    cmds.separator( h = 15)    
    cmds.button( label = 'reset', command = bodyResetCtrl )    
    cmds.text( label = '') 
    cmds.separator( h = 15)    
    cmds.separator( h = 15)
    cmds.separator( h = 15)    
    
    cmds.text( label = 'allCtrls')
    cmds.button( label = 'allSelect', command = allSelect )  
    cmds.button( label = 'allSetKey', command = allSetKeys )
    cmds.separator( h = 15)    
    cmds.button( label = 'allReset', command = allResetCtrl )    
    cmds.text( label = '') 
    cmds.separator( h = 15)    
    cmds.separator( h = 15)
    cmds.separator( h = 15) 


    cmds.showWindow( window )
    
    
def printNewMenuItem( item ):
    print item
    
def faceResetCtrl(*pArgs):
    faceSet = cmds.optionMenu('face_area', query=True, value=True)
    resetCtrl( faceSet )
    
    
def faceSetKeys(*pArgs):
    faceSet = cmds.optionMenu('face_area', query=True, value=True)
    setCtrlKeys(faceSet)


def faceSelect(*pArgs):
    faceSet = cmds.optionMenu('face_area', query=True, value=True)
    selectCtrl(faceSet)
    
def bodyResetCtrl(*pArgs):
    bodySet = cmds.optionMenu('body_area', query=True, value=True)
    resetCtrl( bodySet )
    
    
def bodySetKeys(*pArgs):
    bodySet = cmds.optionMenu('body_area', query=True, value=True)
    setCtrlKeys(bodySet)


def bodySelect(*pArgs):
    bodySet = cmds.optionMenu('body_area', query=True, value=True)
    selectCtrl(bodySet)

def allResetCtrl(*pArgs):
    resetCtrl( "allBasic" )
    
    
def allSetKeys(*pArgs):
    setCtrlKeys("allBasic")


def allSelect(*pArgs):
    selectCtrl( "allBasic" )
    

def resetCtrl( ctrlSet ):
    cmds.select( ctrlSet )
    ctrls = cmds.ls( sl=1 )
    for ct in ctrls:

        attrs = cmds.listAttr( ct, k=1, unlocked = 1 )
        for at in attrs:
            if 'scale' in at:
                cmds.setAttr( ct+"."+at, 1 )
            elif at=='visibility':
                continue
                #cmds.setAttr( ct+"."+at, 1 )
            else:
                cmds.setAttr( ct+"."+at, 0 )
                
def setCtrlKeys(ctrlSet):
    cmds.select( ctrlSet )    
    ctrls = cmds.ls( sl=1 )
    for ct in ctrls:
    
        attrs = cmds.listAttr( ct, k=1, unlocked = 1 )
        for at in attrs:
            if at=='visibility':
                continue
            else:cmds.setKeyframe( ct,  attribute = at )

def selectCtrl(ctrlSet):
    cmds.select( ctrlSet )            


    
def rapperCacheGeoToExport():

    cacheGeo=['l_heelCap','l_outSole','r_toeTip0','r_heelCap0','gum_upper_main','gum_bttm_main','ffd_tongue_main','upr_teeth_main','head_main','r_toeCap0','l_toeTip','r_tearMain',
    'ribbonMesh2','ribbonMesh1','l_tearMain','jacket','l_toeCap','l_elastic','eyeBrow_geo','Stitches','Snapback','r_outSole0','r_elastic0','sweatHead_mustach','hodong_hair2',
     'goatTee','l_eyeBall_main','l_cornea_main','lwr_teeth_main','r_cornea_main','r_eyeBall_main','pants','HDBody','roadPoly']
     
    expCache =[]
    for cc in cacheGeo:
        if cmds.objExists(cc):
            expCache.append(cc)
    cmds.select(expCache) 

#assign shading to Alembic cache (hodong, annette ) 

def getSGfromShader(shader=None):
    if shader:
        if cmds.objExists(shader):
            sgq = cmds.listConnections(shader, d=True, et=True, t='shadingEngine')
            if sgq: 
                return sgq[0]

    return None


def assignObjectListToShader(objList=None, shader=None):
    """ 
    Assign the shader to the object list
    arguments:
        objList: list of objects or faces
    """
    # assign selection to the shader
    shaderSG = getSGfromShader(shader)
    if objList:
        if shaderSG:
            cmds.sets(objList, e=True, forceElement=shaderSG)
        else:
            print 'The provided shader didn\'t returned a shaderSG'
    else:
        print 'Please select one or more objects'

def assignSelectionToShader(shader=None):
    sel = cmds.ls(sl=True, l=True)
    if sel:
        assignObjectListToShader(sel, shader)

def assignShader():
    #assign shader to hodong objects
    shadingDict={ "ai_airShdr":["invisibleBody"], "ai_hdSkin_shdr":["visibleBody","head_main" ], "ai_hd_iris":["l_eyeBall_main", "r_eyeBall_main"], "aiStandardHair":["hodong_hair2", "sweatHead_mustach","eyeBrow_geo","goatTee"], 
    "ai_hiphopCap":["Snapback"],"cornea_mtlf":["l_cornea_main","r_cornea_main"],"gum_Mtl":["gum_upper_main","gum_bttm_main", "ffd_tongue_main"], "hd_Jacket":["jacket"], "hd_pants":["pants"],"teeth_mtl":["upr_teeth_main","lwr_teeth_main"] }
    
    #select shaders
    for k, v in shadingDict.items():
        if cmds.objExists(k):
            if len(v)>1:
                for i in v:
                    if cmds.objExists(i):
                        cmds.select(i)
                        assignSelectionToShader( k )
                    
                    else:
                        cmds.warning("there is no %s geo!!"%i )                                        
                    
               
            else:
                if cmds.objExists(v[0]):
                    cmds.select( v[0] )
                    assignSelectionToShader( k )                
    
    
        else:
            cmds.warning("import %s shaders!!"%k )  



            

            
#import cache / select arnoldLights and run
def finalizeRenderSetting():
    #turn off opaque option
    opaque= cmds.ls("*Body*", "ribbonMesh*", "*tearMain", l=1, ni=1, type="mesh")
    if opaque:
        for bd in opaque:
            cmds.setAttr( bd +".aiOpaque", 0 )
    else:
        cmds.warning("Turn off opaque option manually")
    
    #head geo smooth render
    head = cmds.ls("head*", l=1, ni=1, type="mesh")
    if head:
        for hd in head:
            cmds.setAttr( hd+".aiSubdivType", 1 )
            cmds.setAttr( hd+".aiSubdivIterations", 1 )
    else:
        cmds.warning("smooth head display manually!")
            
    myLight= cmds.ls("*LightShape*" )
    for light in myLight:        
        if cmds.nodeType(light)=="aiAreaLight":
            cmds.setAttr(light+".aiSamples", 4 )
            cmds.setAttr(light+".aiResolution", 1024 )
            cmds.setAttr(light+ ".aiNormalize", 0 )
            cmds.setAttr(light+".aiCastVolumetricShadows", 0 )
            cmds.setAttr(light+".aiVolumeSamples", 0 )        
        
        elif cmds.nodeType(light)=="aiSkyDomeLight":

            cmds.setAttr(light+ ".aiNormalize", 1 )
            cmds.setAttr(light+".aiSamples", 4 )
            cmds.setAttr(light+".aiCastVolumetricShadows", 0 )
            cmds.setAttr(light+".aiVolumeSamples", 0 )    
            cmds.setAttr(light+ ".camera", 0)
            
        elif cmds.nodeType(light) in ["spotLight", "pointLight" ]:

            cmds.setAttr(light+ ".aiRadius", 1 )
            cmds.setAttr(light+".aiSamples", 4 )

                    
    cmds.setAttr( "defaultArnoldRenderOptions.GIDiffuseSamples", 5)
    cmds.setAttr( "defaultArnoldRenderOptions.GISpecularSamples", 5)
    cmds.setAttr( "defaultArnoldRenderOptions.GITransmissionSamples", 5)
    cmds.setAttr( "defaultArnoldRenderOptions.GISssSamples", 3)

    from twitchScript import faceSkinFunction
    reload(faceSkinFunction)
    faceSkinFunction.deleteUnknown_plugins()
    

    
#instance objects falling    
def selectedObjectFalling( ):
    selObj = cmds.ls( sl=1, type = "transform" )
    ptcl=cmds.ls( type="nParticle")
    cnnPtcl = cmds.listConnections( ptcl, s=1, d=1 )
    cnnt=list(set(cnnPtcl))
    if cnnt:
        inst = [ i for i in cnnt if cmds.nodeType( i ) == "instancer" ]
        print inst
        for ct in cnnt:
            #set 20 falling from Surface
            if "Emitter" in cmds.nodeType( ct ):
                cmds.setAttr( ct+".emitterType", 2)
                cmds.setAttr( ct+".rate", 20 )
                cmds.setAttr( ct+ ".speed", 40 )
                cmds.setAttr( ct + ".speedRandom", 0.1 )
                
            elif cmds.nodeType( ct ) == "nucleus":
                #falling earlier
                cmds.setAttr( ct+".gravity", 2 )
                cmds.setAttr( ct+".maxCollisionIterations", 6 )
                
            elif cmds.nodeType( ct ) == "nParticle":
                #scale random
                cmds.setAttr( ct + ".radiusScaleInput", 1 )
                cmds.setAttr( ct + ".radiusScaleRandomize", 0.1 )
                
                #collision setup
                cmds.setAttr( ct + ".collide", 1 )
                cmds.setAttr( ct + ".selfCollide", 1 )
                cmds.setAttr( ct + ".collideWidthScale", 6 )
                cmds.setAttr( ct + ".selfCollideWidthScale", 2 )
                cmds.setAttr( ct + ".bounce", 0.05 )
                cmds.setAttr( ct + ".friction", 0.1 )
                cmds.setAttr( ct + ".maxSelfCollisionIterations", 8 )
                
                if inst:
                    #rotation setup            
                    cmds.setAttr( ct + ".rotationFriction", 0.9 )
                    cmds.setAttr( ct + ".rotationDamp", 0.2 )
                    cmds.expression( ct, c=1, s='%s.rotationPP=rand(360)'%(ct) )
                    cmds.particleInstancer( ct, e=1, name= inst, rotation= "rotationPP" )   

#get attributes in ChannelBox
ctl = cmds.ls(sl=1, type ="transform" )
for c in ctl:
    cShape = cmds.listRelatives( c, c=1, s=1 )
    if cShape:
        for cs in cShape:
            animAttr= cmds.listAnimatable(cs)
            if animAttr:
                for at in animAttr:
                    cmds.setAttr( at, l=1 )                    
    

# render hair only    
blackGeo = [u'head_main', u'Stitches', u'Snapback', u'hodong_hair2', u'HDBody', u'pants', u'jacket',u'l_elastic0', u'l_heelCap0',
 u'l_outSole0', u'l_toeCap0', u'l_toeTip0', u'l_elastic', u'l_heelCap', u'l_outSole', u'l_toeCap', u'l_toeTip',u'l_eyeBall_main', u'r_eyeBall_main']
shdr = cmds.shadingNode( "surfaceShader", asShader=1, n="noRenderShdr" )
cmds.setAttr( shdr + ".outMatteOpacity", 0, 0, 0, type= 'double3' )
for g in blackGeo:
    if g:
        cmds.select( g )
        cmds.hyperShade( assign= shdr )
matteGeo =[u'ffd_tongue_main', u'eyeBrow_geo', u'goatTee', u'sweatHead_mustach', u'lwr_teeth_main', u'gum_bttm_main', u'gum_upper_main', u'upr_teeth_main']   
cmds.hide(matteGeo)