# -*- coding: utf-8 -*-
#두상 안에 포함되어 있는 눈 이빨 혀 포함
#상위 3,4개의 조인트 웨이트를 합쳐준다(cut & add). skull부분은 20~30% 웨이트만 갖는다. 
#헤어, 모자등은 stretch joint chain에 스킨한다.(웨이트 수정)
#lattice 는 제자리에 있는다. 얼굴은 플렌쉐입 혹은 랩으로 바디를 따라간다.
#눈과 이빨도 블렌쉐입, 눈썹은 랩으로 바디를 따라간다.

import maya.cmds as cmds
import maya.mel as mel
import blendShapeMethods
import faceCompFunction 
 
def powCurve( jntName, jntLen ):
    tmpCrv = cmds.curve ( d = 3, p =([0,1,0],[0.33,1,0],[0.66,1,0],[1,1,0])) 
    cmds.rebuildCurve( tmpCrv, rt = 0, d = 3, kr = 0, s = 2 )   
    powCrv = cmds.rename( tmpCrv,  jntName+"Pow_crv" )
    incrementPoc = 1.0/(jntLen-1)
    pocList =[]
    for i in range ( jntLen ):
        #POC for positionX on the eyelids ctl curve 
        powPOC = cmds.shadingNode ( 'pointOnCurveInfo', asUtility=True, n = jntName+'_poc' + str(i).zfill(2)) 
        powCrvShape = cmds.listRelatives( powCrv, c=1, type = "nurbsCurve" )
        cmds.connectAttr ( powCrv + ".worldSpace", powPOC + '.inputCurve')   
        cmds.setAttr ( powPOC + '.turnOnPercentage', 1 )        
        cmds.setAttr ( powPOC + '.parameter', incrementPoc*(i) )
        pocList.append(powPOC)
    return pocList
 
 

#individual axis
def indieScaleSquach( squachNode, axis, name ):
    
    tranYPowerMult = cmds.shadingNode ( 'multiplyDivide', asUtility= True, n = name+'pow_mult' )
    cmds.setAttr(tranYPowerMult  + '.operation', 3 )        
    divideMult = cmds.shadingNode ( 'multiplyDivide', asUtility= True, n = name+'pow_divide' )
    cmds.setAttr(divideMult + '.operation', 2 )
    ratioMult = cmds.shadingNode ( 'multiplyDivide', asUtility= True, n = name+'divisionRatio' )
    cmds.setAttr( ratioMult + '.operation', 2 )
    
    # stretch ratio
    xyz = ['x','y','z']
    xyz.remove(axis)
        
    oriValue = cmds.getAttr( squachNode +'.s' + axis )
    cmds.connectAttr( squachNode + '.s'+ axis, ratioMult + '.input1'+ axis.title() )
    cmds.setAttr( ratioMult + '.input2'+ axis.title(), oriValue )
    
    #pow operation
    cmds.addAttr( squachNode, longName= "squach", attributeType='float', dv = 0.5) 
    cmds.connectAttr( ratioMult + '.output'+ axis.title(), tranYPowerMult+ '.input1'+ axis.title() )
    cmds.connectAttr( squachNode + ".squach", tranYPowerMult+ '.input2'+ axis.title())
    
    #divide operation 
    cmds.setAttr( divideMult + '.input1'+ axis.title(), 1 )
    cmds.connectAttr( tranYPowerMult + '.output'+ axis.title(), divideMult+ '.input2'+ axis.title() )
    
    cmds.connectAttr( divideMult+ '.output'+ axis.title(), squachNode+ ".s"+xyz[0] )
    cmds.connectAttr( divideMult+ '.output'+ axis.title(), squachNode+ ".s"+xyz[1] )
    
    

def squachBoxForLattice( jntLen ):

    #xmin ymin zmin xmax ymax zmax (face bounding box)
    geo = cmds.ls(sl=1, type="transform")
    if not geo:
        print "select headGeo!!!"
    else:
        facebbox = cmds.exactWorldBoundingBox(geo[0])
        
        latticeBox = cmds.polyCube( w = (facebbox[3]-facebbox[0])*1.1, h =(facebbox[4] -facebbox[1])*1.1, d=(facebbox[5]-facebbox[2])*1.1, sx=1, sy=int(jntLen), sz=4, n = "latticeCube" )
        tranX = (facebbox[3]+facebbox[0])/2 
        tranY = (facebbox[4] +facebbox[1])/2 
        tranZ = (facebbox[5]+facebbox[2])/2 

        cmds.xform( latticeBox[0], ws=1, t =[tranX, tranY, tranZ ] )
        

    
    
#머리 디폼을 최소화하기 위해 눈썹까지만 스키닝한다. 
def squachSetup( jntLen ):
    #scale not working
    #xmin ymin zmin xmax ymax zmax (face bounding box)
    geo = cmds.ls(sl=1, type="transform")
    if not geo:
        print "select headGeo!!!"
    else:
        facebbox = cmds.exactWorldBoundingBox(geo[0])
        tranX = (facebbox[3]+facebbox[0])/2
        tranY = (facebbox[4] +facebbox[1])/2
        tranZ = (facebbox[5]+facebbox[2])/2
        '''
        latticeBox = cmds.polyCube( w = (facebbox[3]-facebbox[0])*1.1, h =(facebbox[4] -facebbox[1])*1.2, d=(facebbox[5]-facebbox[2])*1.1, sx=1, sy=int(jntLen), sz=4, n = "latticeCube" )

        cmds.xform( latticeBox[0], ws=1, t =[tranX, tranY, tranZ ] )
        cmds.select( cl=1 )'''
        space =  (facebbox[4] - facebbox[1])/float(jntLen)
        if not cmds.objExists("jnt_grp"):
            cmds.group(em=1, n="jnt_grp")
        squachJntGrp = cmds.group( em=1, p = "jnt_grp", n ="squachJnt_grp" ) 
        stretchJntList=[]
        for i in range( int(jntLen)+1 ):
            stretchJnt = cmds.joint( p =( tranX, facebbox[1]+i*space, tranZ ), n = 'squach%s_Jnt'%str(i).zfill(2) )
            stretchJntList.append(stretchJnt)
        #cmds.parent ( stretchJntList[0], squachJntGrp ) 
         
        #edit stretchJnt chain x forward
        for jnt in stretchJntList :
            cmds.joint( jnt, e =True, zso =True, oj = 'zyx', sao= 'ydown')
            cmds.setAttr( jnt+".rotateOrder", 0 )
        
        headSkel = cmds.duplicate(stretchJntList[0], po=1, n = "squachHead_jnt" )
        #cmds.xform( headSkel, ws=1, t =[ tranX, facebbox[1], facebbox[2]/2 ] )        
        topJnt = cmds.duplicate(stretchJntList[-1], po=1, n = "topCtrl_jnt" )
        bttmJnt = cmds.duplicate(topJnt[0], n = "bttmCtrl_jnt" )
        cmds.xform( bttmJnt, ws=1, t = ( tranX, facebbox[1], tranZ ) )
        print "bttm jnt is %s and topJnt is %s"%(stretchJntList[0], stretchJntList[-1])
        cmds.parent( topJnt, w=1 )
        ctlJnts = [ bttmJnt[0], topJnt[0] ]
        cmds.select(ctlJnts, r=1) 
        jntPList = createPntNull()
        print jntPList
        cmds.parent ( jntPList, squachJntGrp )
         
        #create ctrl on face
        if not cmds.objExists("supportRig"):
            cmds.group(em=1, n="supportRig")
        squachCtlGrp = cmds.group( em=1, p = "supportRig", n ="squachCtl_grp"  ) 
        topCtl= cmds.circle( c =( 0,0,0), nr=(0,0,0), sw = 360, r=facebbox[3]/4.0, s=1, d=1, ch=1, n="topSquach_ctl" )
        bttmCtl= cmds.circle( c =( 0,0,0), nr=(0,0,0), sw = 360, r=facebbox[3]/4.0, s=1, d=1, ch=1, n="bttmSquach_ctl" )
        bttmPos = cmds.xform(bttmJnt[0], q=1, ws=1, t=1 )
        topPos = cmds.xform(topJnt[0], q=1, ws=1, t=1 )
        cmds.xform( topCtl[0], ws=1, t =( topPos[0], topPos[1]+space, facebbox[5]/2) )
        cmds.xform( bttmCtl[0], ws=1, t =( bttmPos[0], bttmPos[1]-space, facebbox[5]/2) )
        ctlList = [ topCtl[0], bttmCtl[0] ]
        cmds.select(ctlList, r=1)         
        ctlGrpList = createPntNull()
        print ctlGrpList
        #cmds.parent ( ctlGrpList, squachCtlGrp )
         
        #topStretch_ctl, + twitch panel -->upCtrl_jnt
        for tb in [ "top", "bttm"]:
            stretchPlus = cmds.shadingNode( "plusMinusAverage", asUtility=1, n = tb+"Stretch_plus" )
            stretchRot = cmds.shadingNode( "plusMinusAverage", asUtility=1, n = tb+"Stretch_rot" )
            #translate sum
            cmds.connectAttr( tb + "Squach_ctl.t", stretchPlus + ".input3D[0]") 
            if cmds.objExists("headSquach_%s.t"%tb):
                cmds.connectAttr( "headSquach_%s.t"%tb, stretchPlus + ".input3D[1]")
            cmds.connectAttr( stretchPlus + ".output3D", tb+"Ctrl_jnt.t")
            #rotate sum
            cmds.connectAttr( tb + "Squach_ctl.r", stretchRot + ".input3D[0]")
            if cmds.objExists("headSquach_%s.t"%tb):
                cmds.connectAttr( "headSquach_%s.r"%tb, stretchRot + ".input3D[1]")
            cmds.connectAttr( stretchRot + ".output3D", tb+"Ctrl_jnt.r")
         
        #create ik spline Handle
        ikSpline = cmds.ikHandle( sj=stretchJntList[0], ee=stretchJntList[-1], sol = "ikSplineSolver", createCurve=1, n ="squach_ik", rootOnCurve=True, parentCurve=False, numSpans = 2 )
        cmds.skinCluster( topJnt[0], bttmJnt[0],  ikSpline[-1], n="squach_skin" )
        #connect curveInfo node to get curve browLength
        crvLen = cmds.shadingNode( "curveInfo", asUtility=1, n = "stretch_crvInfo" )
        cmds.connectAttr( ikSpline[-1]+".worldSpace[0]", crvLen+".inputCurve" )
         
        #stretch setup
        stretchScale = cmds.shadingNode( "multiplyDivide", asUtility=1, n = "stretchScale_mult" ) 
        cmds.setAttr( stretchScale+ ".operation", 2 )
        cmds.connectAttr( crvLen + ".arcLength", stretchScale+".input1X" )
        cmds.setAttr( stretchScale+".input2X", cmds.getAttr( crvLen+".arcLength" ))
         
        #volume preservation( 1/sqrt( stretchScale )== 1/pow( stretchScale, 0.5))
        powerMult = cmds.shadingNode( "multiplyDivide", asUtility=1, n = "power_mult" ) 
        cmds.setAttr( powerMult+ ".operation", 3 )
        cmds.connectAttr( stretchScale+".outputX", powerMult+".input1X" )
        cmds.setAttr( powerMult+ ".input2X", 0.5 )
        divideMult = cmds.shadingNode( "multiplyDivide", asUtility=1, n = "stretchScale_mult" )
        cmds.setAttr( divideMult + ".operation", 2 )
        cmds.setAttr( divideMult +".input1X", 1  ) 
        cmds.connectAttr( powerMult+".outputX", divideMult+".input2X" )
        
        #get the joint around eyebrow
        #browPos = cmds.xform("rotXPivot", q=1, ws=1, t=1)
        skinJnts =stretchJntList[:-1]    
                
        #create powCurve and poc for volumn shape
        volumPowPoc = powCurve( "volume", len(skinJnts) )
        stretchPowPoc = powCurve( "stretch", len(skinJnts) )
        for vp, sp, jot in zip(volumPowPoc, stretchPowPoc, skinJnts ) :
            #volume curve connect
            volumePowMult = cmds.shadingNode( "multiplyDivide", asUtility=1, n = "volumePow_mult" )
            cmds.setAttr(volumePowMult+".operation", 3)
            cmds.connectAttr( divideMult+".outputX", volumePowMult+".input1Y" )
            cmds.connectAttr( vp+".positionY", volumePowMult+".input2Y")
            #stretch curve connect
            cmds.connectAttr( stretchScale+".outputX", volumePowMult+".input1X" )
            cmds.connectAttr( sp+".positionY", volumePowMult+".input2X" )
            cmds.connectAttr( volumePowMult+".outputX", jot+".sz" )
            cmds.connectAttr( volumePowMult+".outputY", jot+".sx" )
            cmds.connectAttr( volumePowMult+".outputY", jot+".sy" )    
         
        cmds.setAttr (ikSpline[0]+".dTwistControlEnable", 1)
        #world up type : object rotation up( start/ end )
        cmds.setAttr (ikSpline[0]+".dWorldUpType", 4)
        #joint orientation axis Forward( "Z"yx ) 
        cmds.setAttr (ikSpline[0]+".dForwardAxis", 4) 
        #joint orientation axis Up( z"Y"x)
        cmds.setAttr (ikSpline[0]+".dWorldUpAxis", 0) 
        #world up vector : -z
        cmds.setAttr ( ikSpline[0]+".dWorldUpVectorX", 0 ) 
        cmds.setAttr ( ikSpline[0]+".dWorldUpVectorY", 0 ) 
        cmds.setAttr ( ikSpline[0]+".dWorldUpVectorZ", -1 )
        cmds.setAttr ( ikSpline[0]+".dWorldUpVectorEndX", -1 ) 
        cmds.setAttr ( ikSpline[0]+".dWorldUpVectorEndY", 0 )
        cmds.setAttr ( ikSpline[0]+".dWorldUpVectorEndZ", -1 )
         
        cmds.connectAttr( bttmCtl[0]+".worldMatrix[0]",  ikSpline[0]+".dWorldUpMatrix" )
        cmds.connectAttr( topCtl[0]+".worldMatrix[0]", ikSpline[0]+ ".dWorldUpMatrixEnd" )
        
        #skin latticeBox
        skinJnts.append( "squachHead_jnt" )

        squachLattice = cmds.lattice( geo[0], divisions= [ 2, int(jntLen)+1, 5 ], objectCentered=1, ldivisions=[2,2,2], n = "squach_ffd1" )
        squachFFd = [ ffd for ffd in squachLattice if cmds.nodeType(ffd)=="ffd" ]
        latticeSkin = cmds.skinCluster( skinJnts, squachLattice[1], normalizeWeights= 1, n = "squachLattice_skin" )
        cmds.lattice( squachFFd[0], e=1, rm =1, geometry = geo[0] )
        boxSkin = cmds.skinCluster( skinJnts, geo[0], normalizeWeights= 1, n = "squachBox_skin" )
                
        
        '''#create head_main for the head squach  
        if cmds.objExists("origShape"):
            origShape="origShape"
        else:
            orig = [x for x in cmds.listRelatives(geo[0], ad=1 ) if "Orig" in x]
            if orig:
                origShape= blendShapeMethods.copyOrigMesh( geo[0], "origShape" )
            else:
                print "select skinned object!!"

        headMain = cmds.duplicate(origShape, n = "head_main" )
        if not cmds.listRelatives(headMain[0], p=1)[0]=="faceGeo_grp":
            cmds.parent( headMain[0], "faceGeo_grp" )
            
        if mel.eval("findRelatedSkinCluster %s"%geo[0]):
            cmds.blendShape( geo[0], headMain[0], n = "squachBS" )
            cmds.setAttr( "squachBS."+ geo[0], 1 )
            cmds.hide( geo[0], origShape )
            headMainSkin = cmds.skinCluster( skinJnts, headMain[0], normalizeWeights=1, n = "squachHead_skin" )

        print squachFFd[0],latticeBox[0]
        cmds.lattice( squachFFd[0], e=1, g=latticeBox[0], remove=1 )'''
        
        cmds.addAttr( "topSquach_ctl", ln ="squachBox_skin", dt = "string"  )
        cmds.setAttr( "topSquach_ctl.squachBox_skin", boxSkin[0], type="string" )
        cmds.addAttr( "topSquach_ctl", ln ="latticeSkin", dt = "string"  )
        cmds.setAttr( "topSquach_ctl.latticeSkin", latticeSkin[0], type="string" )
        return latticeSkin
 
 

    
#select the obj with skin to be copied 
def copyBoxSkinToLattice():
    HeadSkin = cmds.getAttr("topSquach_ctl.squachBox_skin")    
    latticeSkin = cmds.getAttr("topSquach_ctl.latticeSkin")
    cmds.copySkinWeights( ss = HeadSkin, ds=latticeSkin, sa= 'closestPoint', ia = 'closestJoint', sm=0, noMirror=True )
 

 
 
#select geometry to add squach deformer ( dropdown menus "hair" : direct skin/ "teeth" :lattice/ "eyeLash": lattice )
def addSquachGeo( dformer ): 
    mySel = cmds.ls( sl=1, type = "transform")
    if dformer =="lattice":        
        lattice = cmds.lattice("squach_ffd1", e=1, geometry = mySel )         
        
    if dformer =="joint":
        squachSkin = mel.eval('findRelatedSkinCluster head_main');
        squachJnt = cmds.skinCluster(squachSkin, q=1, inf=1 )
        for obj in mySel:
            skinCls = cmds.skinCluster( squachJnt, obj, normalizeWeights=1, n = "squach%s_skin"%obj.title() )    
            cmds.copySkinWeights( ss = squachSkin, ds=skinCls[0], sa= 'closestPoint', ia = 'closestJoint', sm=0, noMirror=True )
            
            

import math
def distance(inputA=[1,1,1], inputB=[2,2,2]):
    #sqrt( ( inputB[0]-inputA[0])*(inputB[0]-inputA[0]) +.....  )
    return math.sqrt(pow(inputB[0]-inputA[0], 2) + pow(inputB[1]-inputA[1], 2) + pow(inputB[2]-inputA[2], 2))
    
#_______________________________________________________________________________________________________________________________________________
# return list of the parent group of the each selected obj
def createPntNull():
    
    mySel =cmds.ls(sl=1)       
    grpList = []
    for nd in mySel:
        
        pos = cmds.xform(nd, q=1, ws=1, rotatePivot=1 ) 
        
        if cmds.nodeType(nd) =="transform":
            topGrp = cmds.duplicate( nd, po=1, n=nd+"P" )
            cmds.parent(nd, topGrp)
            
        else:
            prnt = cmds.listRelatives( nd, p=1, type ="transform")
            topGrp = cmds.group( em=1, n= nd+"P" )
            cmds.xform( topGrp, ws=1, t=pos )
            cmds.parent( nd, topGrp )        
            if prnt:
                cmds.parent( topGrp, prnt[0] )
        grpList.append(topGrp)
        
    return grpList


def createParentNull( mySelList ):    
     
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
            grpList.append( emGrp )            
                        
            if prnt:
                cmds.parent( emGrp, prnt[0] )
    
    return grpList  #list of parent group nodes


    

#select bttm ctrl and top ctrl(locator)/ run ( createPrntNull the ctrls!! (should be oriented in the direction of joints) ) 
#name = tongue, body, head....
def nonTwitchSquachRig(jntLen, bendDirection, name ):
    ctlSel =cmds.ls( os =1, type="transform")
    bttmCtl = ctlSel[0]
    topCtl =ctlSel[1]

    #xup, xdown, yup, ydown, zup, zdown, none.
    if bendDirection == "xup":        

        worldUpVector = [1, 0 ,0]
    elif bendDirection == "xdown":        

        worldUpVector = [-1, 0 ,0]
    elif bendDirection == "yup":        

        worldUpVector = [0, 1 ,0]
    elif bendDirection == "ydown":        

        worldUpVector = [0, -1 ,0]
    elif bendDirection == "zup":        

        worldUpVector = [0, 0 ,1]
    elif bendDirection == "zdown":        

        worldUpVector = [0, 0 ,-1]
        
    bttmPos = cmds.xform( bttmCtl, q=1, ws=1, rp=1 )
    topPos =cmds.xform( topCtl, q=1, ws=1, rp=1 )  
    squachJntGrp = cmds.group( em=1, n = name+"SquachJnt_grp" ) 
    
    bttmJnt = cmds.joint( p = bttmPos, n = name +'SquachBttm_Jnt' )
    topJnt = cmds.joint( p = topPos, n = name +'SquachTop_Jnt' )
    cmds.joint( bttmJnt, e =True, zso =True, oj = 'zyx', sao= bendDirection )
    cmds.setAttr( bttmJnt+".rotateOrder", 0 )
    cmds.select(bttmJnt)    
    mel.eval('js_splitSelJoint (%s)'%jntLen);
    stretchJntList= cmds.listRelatives( bttmJnt, ad=1, type="joint")
    
    newJntList=[]
    for jnt in stretchJntList[1:]:
        num = jnt.split("_")[3]
        newJnt = cmds.rename(jnt, name + "Squach_Jnt"+ num )
        newJntList.append(newJnt)     
    
    newJntList.append(bttmJnt)      
    #edit stretchJnt chain z forward #joint -e  -oj zyx -secondaryAxisOrient yup -ch -zso;
    for jnt in newJntList:
        cmds.joint( jnt, e =True, zso =True, oj = 'zyx', sao= bendDirection )
        cmds.setAttr( jnt+".rotateOrder", 0 )

    bttmCtlJnt = cmds.duplicate(bttmJnt, po=1, n = name+"BttmCtrl_jnt" )
    cmds.parent( bttmCtlJnt, w=1 )
    topCtlJnt = cmds.duplicate(topJnt, po=1, n = name+"TopCtrl_jnt" )
    cmds.parent( topCtlJnt, w=1 )    
    ctlJnts = [ bttmCtlJnt[0], topCtlJnt[0] ] 
    jntPList = createParentNull( ctlJnts )
    cmds.parent ( jntPList, squachJntGrp )
    print jntPList, squachJntGrp
    #create ik spline Handle ##ikHandle -sol ikSplineSolver -n "mario" -pcv false -ccv false -scv false -sj "joint1" -ee "joint7" -c "curve1" -fj true;
    ikSpline = cmds.ikHandle( sj= bttmJnt, ee= topJnt, sol = "ikSplineSolver", createCurve=1, n = name + "squach_ik", rootOnCurve=True, 
    parentCurve=False, simplifyCurve = False )
    cmds.skinCluster( topCtlJnt[0], bttmCtlJnt[0],  ikSpline[-1], n=name+"Squach_skin" )
    #connect curveInfo node to get curve browLength
    crvLen = cmds.shadingNode( "curveInfo", asUtility=1, n = name+"Stretch_crvInfo" )
    cmds.connectAttr( ikSpline[-1]+".worldSpace[0]", crvLen+".inputCurve" )
     
    #stretch setup
    stretchScale = cmds.shadingNode( "multiplyDivide", asUtility=1, n = name+"StretchScale_mult" ) 
    cmds.setAttr( stretchScale+ ".operation", 2 )
    cmds.connectAttr( crvLen + ".arcLength", stretchScale+".input1X" )
    cmds.setAttr( stretchScale+".input2X", cmds.getAttr( crvLen+".arcLength" ))

    #volume preservation( 1/sqrt( stretchScale )== 1/pow( stretchScale, 0.5))
    powerMult = cmds.shadingNode( "multiplyDivide", asUtility=1, n =  name+ "Power_mult" ) 
    cmds.setAttr( powerMult+ ".operation", 3 )
    cmds.connectAttr( stretchScale+".outputX", powerMult+".input1X" )
    cmds.setAttr( powerMult+ ".input2X", 0.5 )
    divideMult = cmds.shadingNode( "multiplyDivide", asUtility=1, n = name+"StretchScale_mult" )
    cmds.setAttr( divideMult + ".operation", 2 )
    cmds.setAttr( divideMult +".input1X", 1  ) 
    cmds.connectAttr( powerMult+".outputX", divideMult+".input2X" )
            
    skinJnts = newJntList[::-1]
    print skinJnts
    #create powCurve and poc for volumn shape
    volumPowPoc = powCurve( "volume", len(skinJnts) )
    stretchPowPoc = powCurve( "stretch", len(skinJnts) )
    for vp, sp, jot in zip(volumPowPoc, stretchPowPoc, skinJnts ) :
        #volume curve connect
        volumePowMult = cmds.shadingNode( "multiplyDivide", asUtility=1, n = name+"VolumePow_mult" )
        cmds.setAttr(volumePowMult+".operation", 3)
        cmds.connectAttr( divideMult+".outputX", volumePowMult+".input1Y" )
        cmds.connectAttr( vp+".positionY", volumePowMult+".input2Y")
        #stretch curve connect
        cmds.connectAttr( stretchScale+".outputX", volumePowMult+".input1X" )
        cmds.connectAttr( sp+".positionY", volumePowMult+".input2X" )
        cmds.connectAttr( volumePowMult+".outputX", jot+".sz" )
        cmds.connectAttr( volumePowMult+".outputY", jot+".sx" )
        cmds.connectAttr( volumePowMult+".outputY", jot+".sy" )    

    cmds.setAttr (ikSpline[0]+".dTwistControlEnable", 1)
    #world up type : object rotation up( start/ end )
    cmds.setAttr (ikSpline[0]+".dWorldUpType", 4)
    #joint orientation axis Forward( "Z"yx ) 
    cmds.setAttr (ikSpline[0]+".dForwardAxis", 4) 
    #joint orientation axis Up( z"Y"x)
    cmds.setAttr (ikSpline[0]+".dWorldUpAxis", 0 ) 
    #world up vector : -z
    cmds.setAttr ( ikSpline[0]+".dWorldUpVectorX", worldUpVector[0] ) 
    cmds.setAttr ( ikSpline[0]+".dWorldUpVectorY", worldUpVector[1] ) 
    cmds.setAttr ( ikSpline[0]+".dWorldUpVectorZ", worldUpVector[2] )
    cmds.setAttr ( ikSpline[0]+".dWorldUpVectorEndX", worldUpVector[0] ) 
    cmds.setAttr ( ikSpline[0]+".dWorldUpVectorEndY", worldUpVector[1] )
    cmds.setAttr ( ikSpline[0]+".dWorldUpVectorEndZ", worldUpVector[2] )
     
    cmds.connectAttr( bttmCtl+".worldMatrix[0]",  ikSpline[0]+".dWorldUpMatrix" )
    cmds.connectAttr( topCtl+".worldMatrix[0]", ikSpline[0]+ ".dWorldUpMatrixEnd" )


#stretchRig(12)


def createCube(jntLen):
    geo = cmds.ls(sl=1, type="transform")
    facebbox = cmds.exactWorldBoundingBox(geo[0])
    
    latticeBox = cmds.polyCube( w = (facebbox[3]-facebbox[0])*1.1, h =(facebbox[4] -facebbox[1])*1.1, d=(facebbox[5]-facebbox[2])*1.1, sx=1, sy=int(jntLen), sz=4, n = "latticeCube" )
    tranX = (facebbox[3]+facebbox[0])/2
    tranY = (facebbox[4] +facebbox[1])/2
    tranZ = (facebbox[5]+facebbox[2])/2
    
    cmds.xform( latticeBox[0], ws=1, t =[tranX, tranY, tranZ ] )
    
    
