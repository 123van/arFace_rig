# -*- coding: utf-8 -*-
import pymel.core as pm
import maya.cmds as cmds
import maya.mel as mel
import BCDtypeCtrlSetup
reload(BCDtypeCtrlSetup)

#CorrectiveShape_____________________________________________________________________________________________________________
#_____________________________________________________________________________________________________________
"""
check if browMapHead has right skinWeight map

1. select geo and run splitBSWeightMap() : 
    A. make all deformers zero except headSkin. It will create temp geo("tempSplitGeo") from current selected geo("head_REN")
    B. improve : find the way to adjust "splitMapSurf"
    C. 
    
2. createTwitchBS(): blendShape 타겟 자리 깔기
    A. blendShape 이 쓰이는 부위에 default shape으로 자리를 깐다. 

3. ctrlConnectBlendShape()
    A. ctrls(happy / sad, brow sad/mad, U,E,O,Wide) to blendShape curves and twitch correctives
    
4. fixTwitchTarget(): 포즈를 잡아 놓고 aim shape(in correctiveList or targetList)을 선택한다.
    각각의 타겟을 sculpting하고 twitchBS에 코렉티브나 쉐입으로 연결한다. 원하는 타겟 웨이트가 1인 상태에서 수정된 타겟을 선택하고 실행.
    가. 개별적인 쉐입 업데이트하기
    나. 코렉티브 다시 수정할 경우 리셋 요망

5. updateLRSplitTargetWeight( splitRange, target ): target LR weight update or add LR target with splitRange
    #splitRange = "face", "nose" ( 타겟 웨이트나 새 타겟을 추가한다. 컨트롤과 manually 연결시켜준다)

 
6. add/update target: "ear"/"mouth"/"nose" 선택하고 타겟을 선택 
    가. 추가할 타겟을 선택 : 좌우 블렌쉐입을 추가한다.
    나. 포즈를 잡고 컨트롤 선택: 웨이트 수정 

4. createBrowCorrective( posMax, negMax, inMax, outMax ): 눈썹 코렉티브 쉐입 셋업/조인트 하나하나에 코렉티브를 넣는다
    # posMax(10) : browJnt.rx -10일때 twitch.browUp reaches to max(1)    
    # negMax(6) : browJnt.rx 6일때 twitch.browDown reaches to max(1)
    # inMax(10) : l_browYJnt.ry -10/l_browYJnt.ry 10일때 twitch.browIn reaches to max(1)
    # posMax(10) : l_browYJnt.ry 10/r_browYJnt.ry -10일때 twitch.browOut reaches to max(1)    

5.

## curve shape 중 "squint","annoy"는 위아래 눈꺼플이 오버랩되지 않도록한다. blink를 망칠수 있다.(스크립트를 수정하자) 
"""



#select "head_REN" with all deforms zero
def splitBSWeightMap():
    geoSel = cmds.ls(sl=1, type = "transform")
    lPos = cmds.xform( "lEarPos", q=1, ws=1, t=1)
    rPos = [-lPos[0], lPos[1], lPos[2] ]
    cmds.select(cl=1)
    if not cmds.objExists("lWgtJnt") or not cmds.objExists("rWgtJnt"):
        lWgtJnt = cmds.joint( n="lWgtJnt", p = lPos)
        cmds.select(cl=1)
        rWgtJnt = cmds.joint( n="rWgtJnt", p = rPos)
    else:
        lWgtJnt="lWgtJnt"
        rWgtJnt="rWgtJnt"
        
    if not cmds.objExists("tempSplitGeo"):
        splitGeo =cmds.duplicate( geoSel[0], renameChildren=1, n = "tempSplitGeo")
        splitGeoName = cmds.rename (splitGeo[0], "tempSplitGeo" )
        splitSkin =cmds.skinCluster( lWgtJnt, rWgtJnt, splitGeoName, toSelectedBones=True, n = "splitSkin" )
    else:
        splitGeo =["tempSplitGeo"]
        splitSkin = ["splitSkin"]
    
    facebbox =  cmds.exactWorldBoundingBox(geoSel[0])
    lEyePos = cmds.xform( "lEyePos", q=1, ws=1, t=1 )
    #facebbox[0]*2 얼굴폭 /5 코폭
    sizeX =[ facebbox[3], lEyePos[0]*2, facebbox[3]*1/3 ]
    bboxSizeY = facebbox[4] - facebbox[1]
    prefix = ["ear", "mouth", "nose"]
    if not cmds.objExists( "dumpAtMerge" ):
        cmds.group( em=1, p = " faceMain ", n = "dumpAtMerge" )
    #create faceSplitSurf / noseSplitSurf 
    for w in range(3): 
        splitSurfGeo = cmds.polyPlane(n= "%sSplitMapSurf"%prefix[w], w = sizeX[w], h =bboxSizeY, subdivisionsX = 4, subdivisionsY = 1 )
        cmds.xform( splitSurfGeo[0], ws =1, t=[ 0, facebbox[1]+bboxSizeY/2 , facebbox[5]] )
        cmds.setAttr( splitSurfGeo[0] + ".rx", 90 )
        '''if w==0:
            edgePos = {  -lipEPos[0]:[1,6],  lipEPos[0]:[3,8] }
            for xPos, vtx in edgePos.iteritems():
                for v in vtx:
                    origPos = cmds.pointPosition( splitSurfGeo[0] + ".vtx[%s]"%v, w=1)
                    cmds.xform ( splitSurfGeo[0] + ".vtx[%s]"%v, ws=1, t=[ xPos, origPos[1], origPos[2]] )'''
                    
        #create split weight 
        splitSurfSkin =cmds.skinCluster( lWgtJnt, rWgtJnt, splitSurfGeo[0], normalizeWeights=1, toSelectedBones=True )
        wgtVal = [1, 1, 0.5, 0, 0 ]
        for i in range( 5 ):
            cmds.select( splitSurfGeo[0] +".vtx[%s]"%str(i), splitSurfGeo[0] +".vtx[%s]"%str(i+5)) 
            cmds.skinPercent(splitSurfSkin[0], transformValue = [ rWgtJnt, wgtVal[i] ] )   
        
        cmds.select( splitSurfGeo[0], splitGeo[0], r=1 )
        cmds.copySkinWeights( noMirror=1, surfaceAssociation ="closestPoint",  influenceAssociation ="closestJoint")
        
        lTarget = cmds.duplicate( splitGeo[0], n = "l%s_weightMap"%prefix[w].title() )
        rTarget = cmds.duplicate( splitGeo[0], n = "r%s_weightMap"%prefix[w].title() )
        history = cmds.listHistory( geoSel[0] )
        if "splitMapBS" in history:
            alias = cmds.aliasAttr( "splitMapBS", q=1)
            cmds.blendShape( "splitMapBS", e=1, t = [ geoSel[0], len(alias)/2, lTarget[0], 1 ] )
            cmds.blendShape( "splitMapBS", e=1, t = [ geoSel[0], len(alias)/2+1, rTarget[0], 1 ] )
    
        else:
            splitBS = cmds.blendShape( lTarget[0], rTarget[0], geoSel[0], n = "splitMapBS" )        
        #get each joint weight
        size = cmds.polyEvaluate( splitGeo[0], v=1)
        jntID =jointIndices( splitGeo[0], [lWgtJnt, rWgtJnt] ) 
        lBsVal = cmds.getAttr( splitSkin[0] + '.wl[0:%s].w[%s]'%(size-1, jntID[lWgtJnt] ) )
        rBsVal = cmds.getAttr( splitSkin[0] + '.wl[0:%s].w[%s]'%(size-1, jntID[rWgtJnt] ) )    
    
        cmds.setAttr( "splitMapBS.inputTarget[0].inputTargetGroup[%s].targetWeights[0:%s]"%(w*2, size-1), *lBsVal )    
        cmds.setAttr( "splitMapBS.inputTarget[0].inputTargetGroup[%s].targetWeights[0:%s]"%(w*2+1, size-1), *rBsVal )
        cmds.delete( lTarget, rTarget )
        if w==0:
            cmds.parent( splitGeo[0], lWgtJnt, rWgtJnt, "dumpAtMerge" )
    
        #cmds.delete( splitSurfGeo[0] )   
    
    
    
    

#트위치 블렌쉐입 미니멈을 생성하고 추가하면서 완성
# createSplitMap first
# run this before create corrective shapes
def createTwitchBS( ):
    #L / R targets 
    targetList =["happy", "sad", "E","U","O","wide", "Sh", "M", "sneer", "flare", "puff", "suck", "squint", "annoy", "furrow",
 "relax", "browSad", "browMad" ]
    wgtList = [ 0, 0, 0, 0, 0, 0, 0, 0, 2, 2, 0, 0, 4, 4, 2, 2, 2, 2 ]
    baseGeo =cmds.getAttr("helpPanel_grp.headGeo")
    vtxLen= cmds.polyEvaluate( baseGeo, v=1 )
    baseBS = cmds.ls( cmds.listHistory(baseGeo), type = "blendShape" )
    if baseBS:
        if 'twitchBS' in baseBS:
            print "twitchBS already exists!!"
        else:
            twitchBS = cmds.blendShape( baseGeo, foc=1, o="local", n = "twitchBS")
            # get left / right splitWeight map 
            lEarWgt = cmds.getAttr( "splitMapBS.inputTarget[0].inputTargetGroup[0].targetWeights[0:%s]"%( vtxLen-1) )
            rEarWgt = cmds.getAttr( "splitMapBS.inputTarget[0].inputTargetGroup[1].targetWeights[0:%s]"%( vtxLen-1) ) 
            lMouthWgt = cmds.getAttr( "splitMapBS.inputTarget[0].inputTargetGroup[2].targetWeights[0:%s]"%( vtxLen-1) )
            rMouthWgt = cmds.getAttr( "splitMapBS.inputTarget[0].inputTargetGroup[3].targetWeights[0:%s]"%( vtxLen-1) )
            lNoseWgt = cmds.getAttr( "splitMapBS.inputTarget[0].inputTargetGroup[4].targetWeights[0:%s]"%( vtxLen-1) )
            rNoseWgt = cmds.getAttr( "splitMapBS.inputTarget[0].inputTargetGroup[5].targetWeights[0:%s]"%( vtxLen-1) )  
            instGrp = cmds.group( em=True, n = "correctiveGrp", p = "dumpAtMerge" )
            if not cmds.objExists("origShape"):
                origTarget = copyOrigMesh( baseGeo, "origShape" )
                cmds.parent( origTarget, instGrp )
                cmds.hide( "dumpAtMerge" )
            
            for i, tgt in enumerate(zip(*[targetList, wgtList] )):
            	i=i*3
            	if cmds.objExists( tgt[0] ):
            	    cmds.rename(tgt[0], tgt[0]+"_tg" )
            	if tgt[1]==0:
            	    createLRTargets( baseGeo, vtxLen, origTarget, tgt[0], twitchBS[0], i, lEarWgt, rEarWgt )                
            	elif tgt[1]==2:
            	    createLRTargets( baseGeo, vtxLen, origTarget, tgt[0], twitchBS[0], i, lMouthWgt, rMouthWgt ) 
            	elif tgt[1]==4:
            	    createLRTargets( baseGeo, vtxLen, origTarget, tgt[0], twitchBS[0], i, lNoseWgt, rNoseWgt ) 	
    else:
        print "create splitMapBS first!!!" 
     
 


def createLRTargets( baseGeo, vtxLen, origTarget, tgt, twitchBS, targetID, lWgt, rWgt):
    #add target on the blendShape
    mainTarget = cmds.duplicate( origTarget, n = tgt )
    cmds.rename( cmds.listRelatives(mainTarget[0], c=1, s=1 )[0], tgt +'Shape' )
    lTarget = cmds.duplicate( mainTarget[0], instanceLeaf =1, n ="l_"+ tgt )
    rTarget = cmds.duplicate( mainTarget[0], instanceLeaf =1, n ="r_"+ tgt )
    cmds.blendShape( twitchBS, e=1, topologyCheck=0,  t = [baseGeo, targetID, mainTarget[0], 1 ] )
    cmds.blendShape( twitchBS, e=1, topologyCheck=0, t = [baseGeo, targetID+1, lTarget[0], 1 ] )
    cmds.blendShape( twitchBS, e=1, topologyCheck=0,  t = [baseGeo, targetID+2, rTarget[0], 1 ] )    
    
    cmds.setAttr( twitchBS+ ".inputTarget[0].inputTargetGroup[%s].targetWeights[0:%s]"%( targetID+1, vtxLen-1), *lWgt )
    cmds.setAttr( twitchBS+ ".inputTarget[0].inputTargetGroup[%s].targetWeights[0:%s]"%( targetID+2, vtxLen-1), *rWgt )  
    
    cmds.delete( mainTarget[0], lTarget[0], rTarget[0] )
    return [lTarget[0], rTarget[0]]
    

    
def returnAttr_connectedBS( ctl ):

    cnnt = cmds.listConnections( ctl, d=1)
    utilList = [ x for x in cnnt if cmds.nodeType(x) in ["remapValue", "multiplyDivide", "clamp","plusMinusAverage"]]
    myNode = []
    util2List = []
    plugCnnts = []
    if utilList:        
        for ut in set(utilList):
            cnntND = cmds.listConnections( ut, s=0, d=1 )
            if cnntND:
                bs = [ y for y in cnntND if cmds.nodeType(y) == "blendShape" ]
                if bs:
                    myNode.append(ut)        
                    
                else:
                    util2List+= cnntND
                
        for nd in set(util2List):
            
            destinND = cmds.listConnections( nd, s=0, d=1 )
            if destinND:
                BS = [ z for z in destinND if cmds.nodeType(z) == "blendShape" ]
                if BS:
                    myNode.append(nd)
                    
        for it in set(myNode):
            plugAttr = cmds.listConnections( it, s=0, d=1, c=1, p=1, type = "blendShape" )
            plugCnnts.append(plugAttr)
    
    return plugCnnts
   
#return [ u'l_posRemap1.outValue', u'browBS.l_BrowSad_crv' ], [ u'l_negRemap1.outValue', u'browBS.l_BrowMad_crv' ]


       
#you can first connect curves, and twitchBS later   
#twitchBS에 포함되어 있는 타겟만 연결된다. 나중에 타겟이 추가되면 다시 실행해서 연결한다.
def ctrlConnectBS():
    
    if cmds.objExists("*LipCrvBS") & cmds.objExists("*browBS"):

        for LR in ["l_","r_"]:
            
            for ctl in [ LR+ "brow_madsad", LR + "mouth_happysad", LR+ "brow_Furrow", LR+ "brow_UD"  ]:
                ctlCnnt = returnAttr_connectedBS( ctl )
                if ctlCnnt:#ctl has connection with blendShape
                    break   
            
            if ctlCnnt:
                if len(ctlCnnt) ==2:
                    # get node name without attribute
                    AList = [ x.split(".")[0] for x in ctlCnnt[0] ]
                    BList = [ y.split(".")[0] for y in ctlCnnt[1] ]
                    cnntList = AList + BList
                    
                else:
                    cnntList = [ x.split(".")[0] for x in ctlCnnt[0] ]
                    
                if "twitchBS" in cnntList:
                
                    cmds.confirmDialog( title='Confirm', message="ctls already connected to crvBS and twitchBS" )
                        
                else: #connection only with twitchBS
                    
                    if cmds.objExists("twitchBS"): 
                        #only twitchBS connections!!
                        crvCtls = { LR+ "brow_Furrow":["furrow","relax"], LR+ "brow_madsad":["browMad","browSad"], LR + "mouth_happysad":["sad","happy"], LR + "eyeSquint":["annoy","squint"] }
                        typeBList = { "bridge_puffsuck":["puff", "suck"], "ShM":["Sh", "M"] }
                        typeAList ={ "sneer":"nose_sneer.ty", "flare":"nose_flare.ty" }
                        for A, attr in typeAList.iteritems():   
                                cmds.connectAttr( LR + attr, "twitchBS." + LR + A )
                                
                        for B in typeBList:
                            BCDtypeCtrlSetup.BCtrlSetup( LR + B, "y", LR+ typeBList[B][0], LR+ typeBList[B][1] ) 
                        
                        for ctl in crvCtls:
                            ctlCnnt = returnAttr_connectedBS( ctl )
                            if len(ctlCnnt) == 2: #[['l_negRemap1.outValue', 'browBS.l_BrowMad_crv'], ['l_posRemap1.outValue', 'browBS.l_BrowSad_crv']]
                                for cnnt in ctlCnnt:
                                    attName = cnnt[1].split(".")[1]#l_up_Happy / l_lo_Happy / ....
                                    for it in crvCtls[ctl]:
                                        if it.lower() in attName.lower():
                                            target = it                   

                                    cmds.connectAttr( cnnt[0], "twitchBS." + LR + target ) 
                                    
                            else:
                                for node, bsAttr in zip(*[iter(ctlCnnt[0])]*2):#[['l_Furrow_crvNeg_clamp.outputR', 'browBS.l_Furrow_crv', 'l_Furrow_crvNeg_clamp.outputG', 'browBS.l_Relax_crv']]
                                    attName = bsAttr.split(".")[1]#l_up_Happy / l_lo_Happy / ....
                                    for it in crvCtls[ctl]:
                                        if it in attName.lower():
                                            target = it                                 
                                    cmds.connectAttr( node, "twitchBS." + LR + target )                       
                                                        
                        if not cmds.listConnections( "twitchBS." + LR+ "U", s=1, d=0 ):
                            cmds.connectAttr( "lipFactor."+LR+"phonemeXPos_YPos", "twitchBS." + LR+ "U" ) 
                        
                        if not cmds.listConnections( "twitchBS." + LR+ "E", s=1, d=0 ):
                            cmds.connectAttr( "lipFactor."+LR+"phonemeXNeg_YPos", "twitchBS." + LR+ "E" )                         

                        if not cmds.listConnections( "twitchBS." + LR+ "O", s=1, d=0 ):
                            cmds.connectAttr( "lipFactor."+LR+"phonemeXPos_YNeg", "twitchBS." + LR+ "O" )                     

                        if not cmds.listConnections( "twitchBS." + LR+ "wide", s=1, d=0 ):
                            cmds.connectAttr( "lipFactor."+LR+"phonemeXNeg_YNeg", "twitchBS." + LR+ "wide" )
                            
                    else:
                        cmds.confirmDialog( title='Confirm', message="create twitchBS first!" )
                        
            else: #no connection
                # 1. curve blendShape connection!!
                # "B"type ctl setup______________________________________________________________________
                BCDtypeCtrlSetup.BCtrlSetup( LR + "brow_Furrow", "y", LR+ "Furrow_crv" , LR+ "Relax_crv" )             
                BCDtypeCtrlSetup.BCtrlSetup( LR + "brow_UD", "y", LR+ "BrowUp_crv" , LR+ "BrowDown_crv" )

                BCDtypeCtrlSetup.CCtrlSetup( LR+ "brow_madsad", LR, ["y","x"], [ LR + "BrowSad_crv"], [ LR + "BrowMad_crv"] )
                BCDtypeCtrlSetup.CCtrlSetup( LR+ "mouth_happysad", LR, ["y","x"], [ LR + "up_Happy", LR + "lo_Happy"], [ LR + "up_Sad", LR + "lo_Sad"] )    
                
                # "D"type ctl setup_____________________________________________________________________
                BCDtypeCtrlSetup.DCtrlSetup( LR + "phonemes_ctl", LR+"phoneme", "lip")   
         
                cmds.connectAttr( "lipFactor."+LR+"phonemeXPos_YPos", "upLipCrvBS." + LR+ "up_U" )
                cmds.connectAttr( "lipFactor."+LR+"phonemeXPos_YPos", "loLipCrvBS." + LR+ "lo_U" )
                #cmds.connectAttr( "lipFactor."+LR+"phonemeXPos_YPos", LR[0] + "CheekBS." + LR+ "uCheek_crv" )
                       
                cmds.connectAttr( "lipFactor."+LR+"phonemeXNeg_YPos", "upLipCrvBS." + LR+ "up_E" )
                cmds.connectAttr( "lipFactor."+LR+"phonemeXNeg_YPos", "loLipCrvBS." + LR+ "lo_E" )
                #mds.connectAttr( "lipFactor."+LR+"phonemeXNeg_YPos", LR[0] + "CheekBS." + LR+ "eCheek_crv" )
                
                cmds.connectAttr( "lipFactor."+LR+"phonemeXPos_YNeg", "upLipCrvBS." + LR+ "up_O" )
                cmds.connectAttr( "lipFactor."+LR+"phonemeXPos_YNeg", "loLipCrvBS." + LR+ "lo_O" )
                #cmds.connectAttr( "lipFactor."+LR+"phonemeXPos_YNeg", LR[0] + "CheekBS." + LR+ "oCheek_crv" )
                
                cmds.connectAttr( "lipFactor."+LR+"phonemeXNeg_YNeg", "upLipCrvBS." + LR+ "up_lipWide" )
                cmds.connectAttr( "lipFactor."+LR+"phonemeXNeg_YNeg", "loLipCrvBS." + LR+ "lo_lipWide" )
                #cmds.connectAttr( "lipFactor."+LR+"phonemeXNeg_YNeg", LR[0] + "CheekBS." + LR+ "wideCheek_crv" )
                
                if cmds.objExists("twitchBS"): 
                    #only twitchBS connections!!
                    crvCtls = { LR+ "brow_Furrow":["furrow","relax"], LR+ "brow_madsad":["browMad","browSad"], LR + "mouth_happysad":["sad","happy"], LR + "eyeSquint":["annoy","squint"] }
                    typeBList = { "bridge_puffsuck":["puff", "suck"], "ShM":["Sh", "M"] }
                    typeAList ={ "sneer":"nose_sneer.ty", "flare":"nose_flare.ty" }
                    for A, attr in typeAList.iteritems():   
                            cmds.connectAttr( LR + attr, "twitchBS." + LR + A )
                            
                    for B in typeBList:
                        BCDtypeCtrlSetup.BCtrlSetup( LR + B, "y", LR+ typeBList[B][0], LR+ typeBList[B][1] ) 
                    
                    for ctl in crvCtls:
                        ctlCnnt = returnAttr_connectedBS( ctl )
                        if len(ctlCnnt) == 2: #[['l_negRemap1.outValue', 'browBS.l_BrowMad_crv'], ['l_posRemap1.outValue', 'browBS.l_BrowSad_crv']]
                            for cnnt in ctlCnnt:
                                attName = cnnt[1].split(".")[1]#l_up_Happy / l_lo_Happy / ....
                                for it in crvCtls[ctl]:
                                    if it.lower() in attName.lower():
                                        target = it                   

                                cmds.connectAttr( cnnt[0], "twitchBS." + LR + target ) 
                                
                        else:
                            for node, bsAttr in zip(*[iter(ctlCnnt[0])]*2):#[['l_Furrow_crvNeg_clamp.outputR', 'browBS.l_Furrow_crv', 'l_Furrow_crvNeg_clamp.outputG', 'browBS.l_Relax_crv']]
                                attName = bsAttr.split(".")[1]#l_up_Happy / l_lo_Happy / ....
                                for it in crvCtls[ctl]:
                                    if it in attName.lower():
                                        target = it                                 
                                cmds.connectAttr( node, "twitchBS." + LR + target )                       
                                                    
                    if not cmds.listConnections( "twitchBS." + LR+ "U", s=1, d=0 ):
                        cmds.connectAttr( "lipFactor."+LR+"phonemeXPos_YPos", "twitchBS." + LR+ "U" ) 
                    
                    if not cmds.listConnections( "twitchBS." + LR+ "E", s=1, d=0 ):
                        cmds.connectAttr( "lipFactor."+LR+"phonemeXNeg_YPos", "twitchBS." + LR+ "E" )                         

                    if not cmds.listConnections( "twitchBS." + LR+ "O", s=1, d=0 ):
                        cmds.connectAttr( "lipFactor."+LR+"phonemeXPos_YNeg", "twitchBS." + LR+ "O" )                     

                    if not cmds.listConnections( "twitchBS." + LR+ "wide", s=1, d=0 ):
                        cmds.connectAttr( "lipFactor."+LR+"phonemeXNeg_YNeg", "twitchBS." + LR+ "wide" )

       
                
                
                
           
                
                
'''                
#after createTwitchBS                
#ctrls(happy / sad, brow sad/mad, U,E,O,Wide) to blendShape curves                

def ctrlConnectBlendShape():
 
    for LR in ["l_","r_"]:    
        
        if not cmds.listConnections( "twitchBS." + LR+ "squint", s=1, d=0 ):
            cmds.connectAttr( LR + "squint_remap.outValue", "twitchBS." + LR + "squint" )
        if not cmds.listConnections( "twitchBS." + LR+ "annoy", s=1, d=0 ):
            cmds.connectAttr( LR + "annoy_remap.outValue", "twitchBS." + LR + "annoy" )

        if not cmds.listConnections( "twitchBS." + LR+ "sneer", s=1, d=0 ):
            cmds.connectAttr( LR + "nose_sneer.ty", "twitchBS." + LR+ "sneer" )

        if not cmds.listConnections( "twitchBS." + LR+ "flare", s=1, d=0 ):
            cmds.connectAttr( LR + "nose_flare.ty", "twitchBS." + LR+ "flare" )                                     

        # happy / sad "C" type ctrl setup 
        if not cmds.listConnections( LR+ "mouth_happysad", s=0, d=1 ):#if there is no connections to the ctl
            BCDtypeCtrlSetup.CCtrlSetup( LR+"mouth_happysad", LR, ["y","x"], [ LR+"upHappy_crv", LR+"loHappy_crv", LR+"happyCheek_crv", LR + "happy" ], 
            [ LR+"upSad_crv", LR+"loSad_crv", LR+"sadCheek_crv", LR + "sad"] )    

        #brow sad/mad "C" type ctrl setup
        if not cmds.listConnections( LR+ "brow_madsad", s=0, d=1 ):
            BCDtypeCtrlSetup.CCtrlSetup( LR+"brow_madsad", LR, ["y","x"], [ LR[0]+"BrowSad_crv", LR+"browSad"], [ LR[0]+"BrowMad_crv", LR+"browMad" ] )
        
        if not cmds.listConnections( LR+ "brow_Furrow", s=0, d=1 ):
            BCDtypeCtrlSetup.BCtrlSetup( LR + "brow_Furrow", LR, "y", [ LR[0]+"Furrow_crv", LR+"furrow" ], [ LR[0]+"Relax_crv", LR+"relax" ] )   
        
        if not cmds.listConnections( LR+"bridge_puffsuck", s=0, d=1 ):
            BCDtypeCtrlSetup.BCtrlSetup( LR + "bridge_puffsuck", LR, "y", [ LR+"puff"], [LR+"suck"] )
    
        # phoneme "D" type ctrl setup 
        if not cmds.listConnections( LR+ "phonemes_ctl", s=0, d=1 ):
            BCDtypeCtrlSetup.DCtrlSetup( LR + "phonemes_ctl", LR+"phoneme", "lip")   
     
            cmds.connectAttr( "lipFactor."+LR+"phonemeXPos_YPos", "upLipCrvBS." + LR+ "upU_crv" )
            cmds.connectAttr( "lipFactor."+LR+"phonemeXPos_YPos", "loLipCrvBS." + LR+ "loU_crv" )
            cmds.connectAttr( "lipFactor."+LR+"phonemeXPos_YPos", LR[0] + "CheekBS." + LR+ "uCheek_crv" )
            cmds.connectAttr( "lipFactor."+LR+"phonemeXPos_YPos", "twitchBS." + LR+ "U" )
            
            cmds.connectAttr( "lipFactor."+LR+"phonemeXNeg_YPos", "upLipCrvBS." + LR+ "uplipE_crv" )
            cmds.connectAttr( "lipFactor."+LR+"phonemeXNeg_YPos", "loLipCrvBS." + LR+ "lolipE_crv" )
            cmds.connectAttr( "lipFactor."+LR+"phonemeXNeg_YPos", LR[0] + "CheekBS." + LR+ "eCheek_crv" )
            cmds.connectAttr( "lipFactor."+LR+"phonemeXPos_YPos", "twitchBS." + LR+ "E" )
            
            cmds.connectAttr( "lipFactor."+LR+"phonemeXPos_YNeg", "upLipCrvBS." + LR+ "upO_crv" )
            cmds.connectAttr( "lipFactor."+LR+"phonemeXPos_YNeg", "loLipCrvBS." + LR+ "loO_crv" )
            cmds.connectAttr( "lipFactor."+LR+"phonemeXPos_YNeg", LR[0] + "CheekBS." + LR+ "oCheek_crv" )
            cmds.connectAttr( "lipFactor."+LR+"phonemeXPos_YPos", "twitchBS." + LR+ "O" )
            
            cmds.connectAttr( "lipFactor."+LR+"phonemeXNeg_YNeg", "upLipCrvBS." + LR+ "uplipWide_crv" )
            cmds.connectAttr( "lipFactor."+LR+"phonemeXNeg_YNeg", "loLipCrvBS." + LR+ "lolipWide_crv" )
            cmds.connectAttr( "lipFactor."+LR+"phonemeXNeg_YNeg", LR[0] + "CheekBS." + LR+ "wideCheek_crv" )
            cmds.connectAttr( "lipFactor."+LR+"phonemeXPos_YPos", "twitchBS." + LR+ "wide" )'''
    
    


#after sculpting, set the twitchBS target 1 : 리깅으로 최대한 가까운 쉐입을 만들고 "head_REN"을 카피해서 쉐입을 모델링한다.
#select target and run ( connect twitchBS ) : 타겟을 선택하고 실행( 트위치블렌쉐입에 코렉티브나 타겟쉐입으로 연결된다 )
# check if curve BlendShape activated
def fixTwitchTarget():   

    aliasAtt = cmds.aliasAttr("twitchBS", q=1)
    targetAim = cmds.ls(sl=1, type = "transform" )    
    targets = []
    IDs = []
    for tgt, wgt in zip(*[iter(aliasAtt)]*2):
        if tgt[:2] not in ["l_", "r_", "c_"]:
            cmds.setAttr( "twitchBS.%s"%tgt, 0 )
        
        tgWgt = cmds.getAttr("twitchBS."+tgt )            
        if tgWgt > 0.98:# if ctrl value == 1
            targets.append(tgt)
            id = wgt.split("[")[1][:-1]
            IDs.append(id)
    
    tgtName = targets[0][2:]
    if tgtName in aliasAtt:
        tgtLength = 3
    else:
        tgtLength = 2
            
    # check if there are activated curves to decide between corrective or target shape.
    crvTgt = []
    crvBS = cmds.ls("*LipCrvBS*", "browBS", "*Lid_bs", "*Blink_bs", typ = "blendShape" )
    for bs in crvBS:
        crvAttr = cmds.aliasAttr(bs, q=1)   
        for tgt, wgt in zip(*[iter(crvAttr)]*2):

            crvWgt = cmds.getAttr( bs + "." + tgt )
            if crvWgt > 0.995:
                crvTgt.append( tgt )
    
    correctiveGrp = "correctiveGrp"
    if not cmds.objExists( correctiveGrp ):
        cmds.group( em=1, n = "correctiveGrp", p = "dumpAtMerge" )
        
    if len(crvTgt) >= 2 and len(targets) == 2:# if curve and mesh blendShape are activated        
            
        if tgtLength ==3: # fix 3 corrective shapes
            targetID = int(min(IDs))-1 
            cmds.setAttr( "twitchBS.%s"%tgtName, 1 )
            cmds.sculptTarget("twitchBS", e=1, target = targetID )
            headGeo = cmds.getAttr("helpPanel_grp.headGeo")
            cmds.select( targetAim[0], headGeo )
            mel.eval("copyShape" )
            cmds.parent(targetAim[0], correctiveGrp )
            cmds.setAttr( "twitchBS.%s"%tgtName, 0 )
            comp = cmds.getAttr('twitchBS.it[0].itg[%s].iti[6000].inputComponentsTarget'%targetID )             
            delta = cmds.getAttr('twitchBS.it[0].itg[%s].iti[6000].inputPointsTarget'%targetID )
            cmds.setAttr('twitchBS.it[0].itg[%s].iti[6000].inputComponentsTarget'%(targetID+1), len(comp), *comp, type="componentList" )
            cmds.setAttr('twitchBS.it[0].itg[%s].iti[6000].inputPointsTarget'%(targetID+1), len(delta), *delta, type="pointArray" )
            cmds.setAttr('twitchBS.it[0].itg[%s].iti[6000].inputComponentsTarget'%(targetID+2), len(comp), *comp, type="componentList" )
            cmds.setAttr('twitchBS.it[0].itg[%s].iti[6000].inputPointsTarget'%(targetID+2), len(delta), *delta, type="pointArray" )
            cmds.sculptTarget("twitchBS", e=1, target = targetID )
            
        elif tgtLength == 2:# fix 2 corrective shapes

            cmds.sculptTarget("twitchBS", e=1, target = int(IDs[0]) )#create corrective shape for left target
            headGeo = cmds.getAttr("helpPanel_grp.headGeo")
            cmds.select( targetAim[0], headGeo )
            mel.eval("copyShape" )
            cmds.parent(targetAim[0], correctiveGrp )
            comp = cmds.getAttr('twitchBS.it[0].itg[%s].iti[6000].inputComponentsTarget'%IDs[0] )             
            delta = cmds.getAttr('twitchBS.it[0].itg[%s].iti[6000].inputPointsTarget'%IDs[0] )
            cmds.setAttr('twitchBS.it[0].itg[%s].iti[6000].inputComponentsTarget'%(IDs[1]), len(comp), *comp, type="componentList" )
            cmds.setAttr('twitchBS.it[0].itg[%s].iti[6000].inputPointsTarget'%(IDs[1]), len(delta), *delta, type="pointArray" )
            cmds.sculptTarget("twitchBS", e=1, target = int(IDs[0]) )
        
        cmds.confirmDialog( title='Confirm', message="%s %s corrective shapes are fixed"%(str(tgtLength), tgtName) )
        
    elif len(crvTgt) == 0 and len(targets) == 2:# it's not corrective target

        if tgtLength ==3: # connect 3 targets
            tgShape= cmds.listRelatives( targetAim[0], c=1, ni=1, s=1)
            targetID = int(min(IDs))-1
            cmds.connectAttr(tgShape[0]+".worldMesh", 'twitchBS.it[0].itg[%s].iti[6000].inputGeomTarget'%targetID )
            cmds.connectAttr(tgShape[0]+".worldMesh", 'twitchBS.it[0].itg[%s].iti[6000].inputGeomTarget'%(targetID+1) )
            cmds.connectAttr(tgShape[0]+".worldMesh", 'twitchBS.it[0].itg[%s].iti[6000].inputGeomTarget'%(targetID+2) )
            if not cmds.listRelatives( targetAim[0], p=1)=="correctiveGrp":
                cmds.parent( targetAim[0], correctiveGrp )  

        elif tgtLength == 2: # connect 2 targets
            tgShape= cmds.listRelatives( targetAim[0], c=1, ni=1, s=1)
            cmds.connectAttr(tgShape[0]+".worldMesh", 'twitchBS.it[0].itg[%s].iti[6000].inputGeomTarget'%IDs[0] )
            cmds.connectAttr(tgShape[0]+".worldMesh", 'twitchBS.it[0].itg[%s].iti[6000].inputGeomTarget'%IDs[1] )
            if not cmds.listRelatives( targetAim[0], p=1)=="correctiveGrp":
                cmds.parent( targetAim[0], correctiveGrp )
        
        cmds.confirmDialog( title='Confirm', message="%s %s shapes are connected"%(str(tgtLength), tgtName) )
        
    else:
        cmds.confirmDialog( title='Confirm', message="no target(or too many targets) is activated. set the ctrls 1 for the pose!" )

    

#select the target with twitchTarget's name and run
def twitchTarget_reconnect():
    
    aliasAtt = cmds.aliasAttr("twitchBS", q=1)
    targetAim = cmds.ls(sl=1, l=1, type = "transform" )
    
    for tgt, wgt in zip(*[iter(aliasAtt)]*2):
        
        if tgt == targetAim[0]:
            id = wgt.split("[")[1][:-1]
            tgShape= cmds.listRelatives( targetAim[0], c=1, ni=1, s=1 )
            cmds.connectAttr(tgShape[0]+".worldMesh", 'twitchBS.it[0].itg[%s].iti[6000].inputGeomTarget'%id )
            cmds.connectAttr(tgShape[0]+".worldMesh", 'twitchBS.it[0].itg[%s].iti[6000].inputGeomTarget'%(id+1) )
            cmds.connectAttr(tgShape[0]+".worldMesh", 'twitchBS.it[0].itg[%s].iti[6000].inputGeomTarget'%(id+2) )
            




 
#update twitchBS LR target's weight or add LR target
'''twitchBS target들 이외의 shape(쌍꺼플 등등)을 추가하고 싶을때는 
1. select updated targets and run
2. run updateAddTarget( splitRange ) : 좌우 타겟으로 블렌쉐입 추가
3. copy the posed head_REN and sculpt
4. copyShape the sculpt to head_REN     
좌우 웨이트를 업데이트 하고 싶을때는 twitchPanel의 컨트롤을 선택, 1로 놓고 실행한다. 
'''
#웨이트를 업데이트(set blendShape target weight 1 )한다

def twitchUpdateWeight( splitRange ):

    baseGeo =cmds.getAttr("helpPanel_grp.headGeo")
    targetHistory = cmds.listHistory( baseGeo, pruneDagObjects =1, interestLevel= 1 )
    dformers = [ x for x in targetHistory if "geometryFilter" in cmds.nodeType( x, inherited =1 )]
    twitchBS = "twitchBS"
    if twitchBS in dformers:        
        
        vtxLen= cmds.polyEvaluate( baseGeo, v=1 )        
        alias = cmds.aliasAttr( twitchBS, q=1 )

        if alias:    
            targetList =set()
            for tgt, wgt in zip(*[iter(alias)]*2):
                if tgt[:2] in ["l_", "r_"]:
                    tgt = tgt[2:]                            
                targetList.add(tgt)
                
        else:
            cmds.confirmDialog( title='Confirm', message="check the name of the twitchBS!" )
            
        if 'splitMapBS' in dformers:
        
            if splitRange == "ear":
                lWgt = cmds.getAttr( "splitMapBS.inputTarget[0].inputTargetGroup[0].targetWeights[0:%s]"%( vtxLen-1))
                rWgt = cmds.getAttr( "splitMapBS.inputTarget[0].inputTargetGroup[1].targetWeights[0:%s]"%( vtxLen-1))
            elif splitRange == "mouth":
                lWgt = cmds.getAttr( "splitMapBS.inputTarget[0].inputTargetGroup[2].targetWeights[0:%s]"%( vtxLen-1))
                rWgt = cmds.getAttr( "splitMapBS.inputTarget[0].inputTargetGroup[3].targetWeights[0:%s]"%( vtxLen-1))        
            elif splitRange == "nose":
                lWgt = cmds.getAttr( "splitMapBS.inputTarget[0].inputTargetGroup[4].targetWeights[0:%s]"%( vtxLen-1))
                rWgt = cmds.getAttr( "splitMapBS.inputTarget[0].inputTargetGroup[5].targetWeights[0:%s]"%( vtxLen-1))     
        
        else:
            cmds.confirmDialog( title='Confirm', message="create splitMapBS first" )            
        
        #update blendShape weight on activated target 

        targets = []
        IDs = []
        #find out the targets with weight 1
        for tgt, wgt in zip(*[iter(alias)]*2):
            tgWgt = cmds.getAttr("twitchBS."+tgt )            
            if tgWgt == 1:
                targets.append(tgt)
                id = wgt.split("[")[1][:-1]
                IDs.append(id)

        if len(targets) == 2: 
        
            cmds.setAttr( twitchBS+ ".inputTarget[0].inputTargetGroup[%s].targetWeights[0:%s]"%( int(IDs[0]), vtxLen-1), *lWgt )
            cmds.setAttr( twitchBS+ ".inputTarget[0].inputTargetGroup[%s].targetWeights[0:%s]"%( int(IDs[1]), vtxLen-1), *rWgt ) 
            print "%s and %s's weight is updated"%(targets[0], targets[1])
        
          
    else:
        cmds.confirmDialog( title='Confirm', message= "no %s in headGeo's history"%twichBS )        




def addTarget( splitRange, targetType ):

    baseGeo =cmds.getAttr("helpPanel_grp.headGeo")
    targetSel = cmds.ls(sl=1, type = "transform")
    shapes = cmds.listRelatives( targetSel, c=1, ni=1, s=1 )
    vtxLen= cmds.polyEvaluate( baseGeo, v=1 )
    twitchBS = "twitchBS"
    alias = cmds.aliasAttr( twitchBS, q=1 )

    if alias:    
        targetList =set()
        for tgt, wgt in zip(*[iter(alias)]*2):
            if tgt[:2] in ["l_", "r_"]:
                tgt = tgt[2:]
                        
            targetList.add(tgt)
    else:
        cmds.confirmDialog( title='Confirm', message="check the name of the twitchBS!" )
        
    if splitRange == "ear":
        lWgt = cmds.getAttr( "splitMapBS.inputTarget[0].inputTargetGroup[0].targetWeights[0:%s]"%( vtxLen-1))
        rWgt = cmds.getAttr( "splitMapBS.inputTarget[0].inputTargetGroup[1].targetWeights[0:%s]"%( vtxLen-1))
    elif splitRange == "mouth":
        lWgt = cmds.getAttr( "splitMapBS.inputTarget[0].inputTargetGroup[2].targetWeights[0:%s]"%( vtxLen-1))
        rWgt = cmds.getAttr( "splitMapBS.inputTarget[0].inputTargetGroup[3].targetWeights[0:%s]"%( vtxLen-1))        
    elif splitRange == "nose":
        lWgt = cmds.getAttr( "splitMapBS.inputTarget[0].inputTargetGroup[4].targetWeights[0:%s]"%( vtxLen-1))
        rWgt = cmds.getAttr( "splitMapBS.inputTarget[0].inputTargetGroup[5].targetWeights[0:%s]"%( vtxLen-1))

        
    if targetSel[0] in targetList:
        cmds.confirmDialog( title='Confirm', message="it is one of the twitch targets, do fixTwitchTarget( corrective ) instead!" )            
    
    else:
        target = targetSel[0]
        targetID = len(alias)/2 + 1
        if targetType =="target":
            lTarget = cmds.duplicate( target, instanceLeaf =1, n ="l_"+ target )
            rTarget = cmds.duplicate( target, instanceLeaf =1, n ="r_"+ target )
            cmds.blendShape( twitchBS, e=1, t = ( baseGeo, targetID, target, 1 ) )
            cmds.blendShape( twitchBS, e=1, t = ( baseGeo, targetID+1, lTarget[0], 1 ) )
            cmds.blendShape( twitchBS, e=1, t = ( baseGeo, targetID+2, rTarget[0], 1 ) )    
            
            cmds.setAttr( twitchBS+ ".inputTarget[0].inputTargetGroup[%s].targetWeights[0:%s]"%( targetID+1, vtxLen-1), *lWgt )
            #cmds.aliasAttr( "l_"+ targetSel[0], twitchBS+".w[%s]"%( targetID+1 ) ) 
            cmds.setAttr( twitchBS+ ".inputTarget[0].inputTargetGroup[%s].targetWeights[0:%s]"%( targetID+2, vtxLen-1), *rWgt ) 
            #cmds.aliasAttr( "r_"+ targetSel[0], twitchBS+".w[%s]"%( targetID+2 ) )
            
            if not cmds.listRelatives( target, p=1)=="correctiveGrp":
                cmds.parent( target,  "correctiveGrp" )

            cmds.confirmDialog( title='Confirm', message= target + " L/R target is added" )  

        elif targetType == "corrective":

            cmds.rename( target, target + "_aim" )
            print target
            origTarget = copyOrigMesh( baseGeo, "default" ) 
            LRtargets = createLRTargets( baseGeo, vtxLen, origTarget, target, twitchBS, targetID, lWgt, rWgt )
            # it delete mainTarget[0], lTarget[0], rTarget[0] for fixCorrective 
            cmds.delete( origTarget )
            return LRtargets
            
    

    
#before fix the target shape, set the target back to origShape
'''블렌쉐입에서 1로 activate 된 타겟을 읽고 그 타겟의 웨이트를 업데이트 한다.( brows up/down/in/out 은 직접 수정 with BSpiritCorrectiveShape;)
1. 수정할 타겟 블렌쉐입을 1로 놓기 위해 포즈를 잡고 실행하면 델타 데이터가 (0,0,0,1) 된다.
2. 오리지널 쉐입을 카피해서 타겟이름으로 바꾼다
3. 타겟 이름(happy)이 블렌쉐입 타겟과 같으면 카피한 쉐입을 블렌쉐입에 연결시켜준다.
'''
def resetForCorrectiveFix():

    cmds.select(cl=1) 
    baseGeo = cmds.getAttr("helpPanel_grp.headGeo")
    alias = cmds.aliasAttr( "twitchBS", q=1 )
    targets = []
    IDs = []
    #find out the targets with weight 1
    for tgt, wgt in zip(*[iter(alias)]*2):        

        tgWgt = cmds.getAttr("twitchBS."+tgt )            
        if tgWgt > 0.999:

            targets.append(tgt)
            id = wgt.split("[")[1][:-1]
            IDs.append(id)
    
    if len(targets) == 2:
            
        target = targets[0][2:]
        targetID = int(min(IDs))-1
        
        worldMesh = cmds.listConnections( 'twitchBS.it[0].itg[%s].iti[6000].inputGeomTarget'%targetID, s=1, d=0 )
        if worldMesh:
            cmds.confirmDialog( title='Confirm', message= " twitchBS.%s already has connection from %s.worldMesh"%(target, worldMesh[0]) )      
            
        else:            
            comp = cmds.getAttr('twitchBS.it[0].itg[%s].iti[6000].inputComponentsTarget'%(targetID) )
            delta = cmds.getAttr('twitchBS.it[0].itg[%s].iti[6000].inputPointsTarget'%(targetID)) 
            newDelta =[]
            for i in range(len(delta)):
                newDelta.append((0.0, 0.0, 0, 1.0))
                
            #reset happy
            cmds.setAttr('twitchBS.it[0].itg[%s].iti[6000].inputComponentsTarget'%(targetID), len(comp), *comp, type="componentList" )
            cmds.setAttr('twitchBS.it[0].itg[%s].iti[6000].inputPointsTarget'%(targetID), len(delta), *newDelta, type="pointArray" )
            #reset l_happy
            cmds.setAttr('twitchBS.it[0].itg[%s].iti[6000].inputComponentsTarget'%(targetID+1), len(comp), *comp, type="componentList" )
            cmds.setAttr('twitchBS.it[0].itg[%s].iti[6000].inputPointsTarget'%(targetID+1), len(delta), *newDelta, type="pointArray" )
            #reset r_happy
            cmds.setAttr('twitchBS.it[0].itg[%s].iti[6000].inputComponentsTarget'%(targetID+2), len(comp), *comp, type="componentList" )
            cmds.setAttr('twitchBS.it[0].itg[%s].iti[6000].inputPointsTarget'%(targetID+2), len(delta), *newDelta, type="pointArray" )
            '''
            targetReset = copyOrigMesh( baseGeo, "default" )
            cmds.connectAttr( targetReset +".worldMesh[0]", "twitchBS.inputTarget[0].inputTargetGroup[%s].inputTargetItem[6000].inputGeomTarget"%targetID )
            cmds.connectAttr( targetReset +".worldMesh[0]", "twitchBS.inputTarget[0].inputTargetGroup[%s].inputTargetItem[6000].inputGeomTarget"%(targetID+1) )
            cmds.connectAttr( targetReset +".worldMesh[0]", "twitchBS.inputTarget[0].inputTargetGroup[%s].inputTargetItem[6000].inputGeomTarget"%(targetID+2) )
            cmds.delete( targetReset )'''
    
    else:
        cmds.confirmDialog( title='Confirm', message= "activate the targets to reset" )  
        

#_________________________________________________________________________________________________________
# only for lip and brow for now 
# important!! name it without prefix "Happy" "BrowMad"!!!
# select LR ctrls and BS_crv(s)
def extraCrvShape_corrective( mySel, xyz, plusName, minusName, splitRange ):
    ctl = mySel[:2]
    bsCrvs = mySel[2:]
    lengCrv = len(bsCrvs)

    plusList = []
    minusList = []

    hist = cmds.listHistory( bsCrvs[0], pruneDagObjects =1, interestLevel= 1 )
    dformers = [ x for x in hist if "geometryFilter" in cmds.nodeType( x, inherited =1 )]
    for dform in dformers:
        cmds.setAttr( dform + ".nodeState", 1 )

    crvPlus = cmds.duplicate(bsCrvs[0], rc =1, n =  plusName + "_crv" )[0]
    crvMinus = cmds.duplicate( bsCrvs[0], rc =1, n = minusName + "_crv" )[0]
        
    deleteOrigShapes( [crvPlus, crvMinus] )# remove intermediateObj
    
    for dform in dformers:
        cmds.setAttr( dform + ".nodeState", 0 )
    
    for bCrv in bsCrvs:
        
        cmds.select( crvPlus, bCrv )
        myPlusCrvs = cmds.ls( os = 1 )
        plusTargets = crvAdd_reconnect( myPlusCrvs ) # add newTarget curves( l_/r_) , return target list
        plusList += plusTargets

        cmds.select( crvMinus, bCrv )
        myMinusCrvs = cmds.ls( os = 1 )
        minusTargets = crvAdd_reconnect( myMinusCrvs ) # add newTarget curves( l_/r_) , return target list
        minusList += minusTargets
    
    # II. addTarget to twitchBS for corrective
    baseGeo =cmds.getAttr("helpPanel_grp.headGeo") 
    plusTarget = cmds.duplicate( baseGeo, rc =1, n = plusName )[0] #just for the script, not be used
    cmds.select( plusTarget , r =1 )
    plusLRtarget = addTarget( splitRange, "corrective" ) #create empty twitchBS.3targets for correctives        
    plusList += plusLRtarget
    
    minusTarget = cmds.duplicate( baseGeo, rc =1, n = minusName )[0] #just for the script, not be used
    cmds.select( minusTarget , r =1 )
    minusLRtarget =addTarget( splitRange, "corrective" )        
    minusList += minusLRtarget
    
    for LR in ["l_", "r_"]:            
        if LR in ctl:
            targetPlus = [ x for x in plusList if LR in x ]
            targetMinus = [ y for y in minusList if LR in y ]
            ctrlPlusMinus_connect(  ctl, xyz, targetPlus, targetMinus )    




# check if the names is in BS ( L/R_ctrls 뒤는 모두 objects with BS node )
def simpleCtl_bsConnect( mySel, xyz, plusName, minusName, splitRange):

    myCtls = mySel[:2]    
    
    plusNames = [ "_"+plusName[0].lower()+plusName[1:], "_"+plusName[0].upper()+plusName[1:] ]
    minusNames = [ "_"+minusName[0].lower()+minusName[1:], "_"+minusName[0].upper()+minusName[1:] ]
    
    if len(mySel)> 2:
        bsObjects = mySel[2:]
        bsList = []
        for obj in bsObjects:
            hist = cmds.listHistory( obj, pruneDagObjects =1, interestLevel= 1 )
            bs = [ x for x in hist if cmds.nodeType( x ) == "blendShape"]
            if bs:
                bsList += bs
    
    else:        
        bsList = cmds.ls( "*LipCrvBS", "*browBS","*Lid_bs", "*twitchBS" )
        
    plusList = []
    minusList = []

    for name in plusNames:
        for bs in bsList:
            bsAttr = cmds.aliasAttr(bs, q=1)
            for tgt, wgt in zip(*[iter(bsAttr)]*2):
                if name in tgt:
                    plusList.append(tgt) 
    for name in minusNames:
        for bs in bsList:
            bsAttr = cmds.aliasAttr(bs, q=1)
            for tgt, wgt in zip(*[iter(bsAttr)]*2):
                if name in tgt:
                    minusList.append(tgt)
    print plusList[0] 
    
    for LR in ["l_", "r_"]:

        ctl = [ c for c in myCtls if LR in c ]
        if ctl:
            targetPlus = [ x for x in plusList if LR in x ]
            print ctl, targetPlus
            targetMinus = [ y for y in minusList if LR in y ]
            ctrlPlusMinus_connect(  ctl[0], xyz, targetPlus, targetMinus )  
        
        
        
#_________________________________________________________________________________________________________

#블렌쉐입 타겟 이름으로 컨트롤
def ctrlPlusMinus_connect(  ctrl, xyz, targetPlus, targetMinus ):
    
    twitchBS = "twitchBS"     
    plusAtts = [] 
    minusAtts = []
    for tg in targetPlus:
        
        twitchAlias = cmds.aliasAttr( twitchBS, q=1 )
        if tg in twitchAlias:
            
            plusAtts.append( twitchBS + "." + tg )   
    
        else:
            shape=cmds.listRelatives( tg, pa=1, c=1, s=1 )
            bs = cmds.listConnections( shape[0], d=1, s=0, type="blendShape" )
            if bs:
                plusAtts.append( bs[0] + "." + tg )
            
            else:
                cmds.confirmDialog( title='Confirm', message='no blendShape is found for %s'%tg )
                    
    
    for tg in targetMinus:
        
        twitchAlias = cmds.aliasAttr( twitchBS, q=1 )
        if tg in twitchAlias:
            
            minusAtts.append( twitchBS + "." + tg )   
    
        else:
            shape=cmds.listRelatives( tg, pa=1, c=1, s=1 )
            bs = cmds.listConnections( shape[0], d=1, s=0, type="blendShape" )
            if bs:
                minusAtts.append( bs[0] + "." + tg )
            
            else:
                cmds.confirmDialog( title='Confirm', message='no blendShape is found for %s'%tg )
    
    
    ctlNegMult = cmds.shadingNode( 'multiplyDivide', asUtility =1, n = ctrl+'Neg_mult')
    cmds.setAttr( ctlNegMult + '.input2', -1, -1, -1 )
    cmds.connectAttr( ctrl+".t" +xyz, ctlNegMult+".input1"+xyz.title() )
    
    ctlClamp = cmds.shadingNode( 'clamp', asUtility =1, n =  ctrl +'Neg_clamp')
    # + side inputR 
    cmds.connectAttr(  ctrl+".t" +xyz, ctlClamp + '.inputR' )
    cmds.setAttr( ctlClamp +".maxR", 1)
    # - side inputG 
    cmds.connectAttr( ctlNegMult+".output"+xyz.title(), ctlClamp + '.inputG' )
    cmds.setAttr( ctlClamp +".maxG", 1)
    
    for plus in plusAtts:       
    
        cmds.connectAttr( ctlClamp + '.outputR', plus )
        
    for minus in minusAtts:       
        cmds.connectAttr( ctlClamp + '.outputG', minus )





                
#brow 타겟(코렉티브 쉐입이 아니다)을 하나씩 선택한 후 twitchPanel의 ctl들로 타겟과 근접한 포즈를 잡고 실행한다.[이름 중요 "browUp","browDown", "browIn","browOut"] 
#꼭 필요한 경우에만 만든다. 대부분 browIn/Out만 해도 충분.     
# posMax(10) : browJnt.rx -10일때 twitchBS.browUp reaches to max(1)    
# negMax(6) : browJnt.rx 6일때 twitchBS.browDown reaches to max(1)
# inMax(10) : furrow 와 다르다. l_browYJnt.ry -10/l_browYJnt.ry 10일때 twitchBS.browIn reaches to max(1)
# posMax(10): relax 와 다르다. l_browYJnt.ry 10/r_browYJnt.ry -10일때 twitchBS.browOut reaches to max(1)
def createBrowCorrective( posMax, negMax, inMax, outMax ):
    
    baseGeo = cmds.getAttr("helpPanel_grp.headGeo")
    browSel = cmds.ls(sl=1, type="transform")
    vtxLen= cmds.polyEvaluate( baseGeo, v=1 )
    baseBS = cmds.ls( cmds.listHistory(baseGeo), type = "blendShape" )
    if baseBS:
        if 'twitchBS' in baseBS:
            twitchBS = ['twitchBS']
        else:
            twitchBS = cmds.blendShape( baseGeo, n = "twitchBS")
    else:
        twitchBS = cmds.blendShape( baseGeo, n = "twitchBS")
    
    #brow corrective setup
    browJnts = cmds.ls ("*_browP*_jnt", type ="joint")
    jntNum = len(browJnts)
    browJnts.sort()
    z = [ browJnts[0] ]
    y = browJnts[1:jntNum/2+1]
    browJnts.reverse()
    x = browJnts[:jntNum/2]
    orderJnts = x + z + y
    skinJnts = cmds.listRelatives( orderJnts, c =1, type = 'joint')
    if cmds.objExists("browMapHead"): 
        browSkin = mel.eval("findRelatedSkinCluster browMapHead" )
    else:
        dataPath = cmds.fileDialog2(fileMode=1, caption="single existing file")
        browSkinWeight = ET.parse( dataPath[0])
        browSkin = browSkinWeight.getroot()
            
    for brow in browSel:
        if brow in ["browUp","browDown", "browIn","browOut"]:
                    
            alias = cmds.aliasAttr( twitchBS, q=1 )
            if not alias:
                targetID = 0
            else:
                targetID = len(alias)/2
            print targetID    
            cmds.blendShape(twitchBS[0], e = 1, target = [ baseGeo, targetID, brow, 1.0] )
            cmds.setAttr( twitchBS[0]+"."+brow, 1 )
            cmds.sculptTarget(twitchBS[0], e=1, target = targetID )
            cmds.select( brow, baseGeo )
            mel.eval("copyShape" )
            #cmds.setAttr( "twitchBS.%s"%tg[0], 0 )
            comp = cmds.getAttr('twitchBS.it[0].itg[%s].iti[6000].inputComponentsTarget'%targetID )             
            delta = cmds.getAttr('twitchBS.it[0].itg[%s].iti[6000].inputPointsTarget'%targetID )            

            for i in range( jntNum ):
                skinJntP = cmds.listRelatives( skinJnts[i], allParents =1, f=1 )
                browBase = [ bb for bb in skinJntP[0].split("|") if "Base" in bb ]
                browRY = cmds.listRelatives( browBase, c=1, type ="joint" )            
                name = skinJnts[i].split("_j")[0]

                if "r_" in browBase[0]:
                    upMax = posMax*-1
                    dnMax = negMax
                    innerMax = inMax
                    outerMax = outMax*-1
                else:
                    upMax = posMax*-1
                    dnMax = negMax
                    innerMax = inMax*-1
                    outerMax = outMax
                
                if "Up" in brow:                
                    rxPosRemap = cmds.shadingNode ('remapValue', asUtility =True, n= name + "_upRemap" )
                    cmds.setAttr (rxPosRemap + '.inputMax', upMax )
                    cmds.connectAttr ( browBase[0] + '.rx', rxPosRemap+'.inputValue' )
                    remap = rxPosRemap
                elif "Down" in brow:

                    rxNegRemap = cmds.shadingNode ('remapValue', asUtility =True, n= name + "_downRemap" )
                    cmds.setAttr (rxNegRemap + '.inputMax', dnMax )
                    cmds.connectAttr ( browBase[0] + '.rx', rxNegRemap+'.inputValue' )
                    remap = rxNegRemap

                elif "In" in brow:

                    ryInRemap = cmds.shadingNode ('remapValue', asUtility =True, n= name + "_inRemap" )
                    cmds.setAttr (ryInRemap + '.inputMax', innerMax )
                    cmds.connectAttr ( browRY[0] + '.ry', ryInRemap+'.inputValue' )
                    remap = ryInRemap

                elif "Out" in brow:

                    ryOutRemap = cmds.shadingNode ('remapValue', asUtility =True, n= name + "_outRemap" )
                    cmds.setAttr (ryOutRemap + '.inputMax', outerMax )
                    cmds.connectAttr ( browRY[0] + '.ry', ryOutRemap+'.inputValue' )
                    remap = ryOutRemap
                
                tgID = targetID+i+1
                targetName = name.replace("brow", brow )   
                cmds.blendShape( twitchBS, e=1, t = [baseGeo, tgID, brow, 1 ] )
                cmds.aliasAttr( targetName, "twitchBS.w[%s]"%(tgID) )
                correctiveBrowTgt( baseGeo, browSkin, skinJnts[i], vtxLen, targetName, twitchBS[0], tgID, remap )
            
            cmds.setAttr( twitchBS[0]+"."+brow, 0 )
            
        for map in [ "inRemap", "outRemap"]:
            if cmds.objExists( "c_brow01_"+ map ):
                cmds.setAttr( "c_brow01_%s.inputMax"%map, 2 )
                addD = cmds.shadingNode( "addDoubleLinear", asUtility=1, n = map+"_addD" )
                cmds.connectAttr( "l_brow01_%s.outValue"%map, addD+".input1")
                cmds.connectAttr( "r_brow01_%s.outValue"%map, addD + ".input2")
                cmds.connectAttr( addD + ".output", "c_brow01_%s.inputValue"%map, f=1 )            
            
#createBrowCorrective( 20, 18, 10, 10 )            
            





def updateRemapMax(posMax, negMax, inMax, outMax):    
    alias = cmds.aliasAttr("twitchBS", q=1 )
    upRemap = []
    downRemap = []
    inRemap = []
    outRemap = []
    for t, w in zip(*[iter(alias)]*2):
        if "_browUp" in t:
            xRemap = cmds.listConnections("twitchBS."+t, s=1, d=0, type="remapValue" )
            upRemap.append(xRemap[0])
            
        elif "_browDown" in t:
            yRemap = cmds.listConnections("twitchBS."+t, s=1, d=0, type="remapValue" )
            downRemap.append(yRemap[0])
        
        elif "_browIn" in t:
            zRemap = cmds.listConnections("twitchBS."+t, s=1, d=0, type="remapValue" )
            inRemap.append(zRemap[0])
    
        elif "_browOut" in t:
            vRemap = cmds.listConnections("twitchBS."+t, s=1, d=0, type="remapValue" )
            outRemap.append(vRemap[0])
    
    if upRemap + downRemap + inRemap + outRemap:       
        for i in range( len(upRemap) ):
        
            if "r_" in upRemap[i]:
                upMax = posMax
                dnMax = negMax*-1
                innerMax = inMax
                outerMax = outMax*-1
            else:
                upMax = posMax*-1
                dnMax = negMax
                innerMax = inMax*-1
                outerMax = outMax
            
            cmds.setAttr( upRemap[i]+".inputMax", upMax )
            cmds.setAttr( downRemap[i]+".inputMax", dnMax )
            cmds.setAttr( inRemap[i]+".inputMax", innerMax )
            cmds.setAttr( outRemap[i]+".inputMax", outerMax )
    
    for map in [ "inRemap", "outRemap"]:
         cmds.setAttr( "c_brow01_%s.inputMax"%map, 2 )
         
         


    


#조인트 아이뒤, 조인트 웨이트, 타겟 카피/블렌쉐입, 웨이트 트랜스퍼, 
#later change the joint in "browMapHead"
#browMapHead 가 없으면 browSkinWeight.xml 파일을 선택한다
def correctiveBrowTgt( baseGeo, browMapSkin, browJnt, vtxLen, targetName, twitchBS, tgID, remap ):
    #get joint weight to transfer
    if cmds.objExists("browMapHead"):

        jntID = jointIndices(  browMapSkin, [browJnt] )
        jntWgt = cmds.getAttr(  browMapSkin + ".wl[0:%s].w[%s]"%( vtxLen-1, jntID[browJnt] ))
        cmds.setAttr( twitchBS + ".inputTarget[0].inputTargetGroup[%s].targetWeights[0:%s]"%( tgID, vtxLen-1), *jntWgt )
        
        cmds.connectAttr ( remap + ".outValue", twitchBS + "." + targetName )
        
    else:
        headSkin = mel.eval("findRelatedSkinCluster head_REN" )
        jntID = jointIndices( headSkin, [browJnt] )
        jntWgt = cmds.getAttr(  headSkin + ".wl[0:%s].w[%s]"%( vtxLen-1, jntID[browJnt] ))
    
        for f in range(2, len(browMapSkin)-2 ):
    
            browJntXml = browMapSkin[f].attrib['source']
            if browJntXml == browJnt:                    
                for dict in browMapSkin[f]:
                    vertIndex = int(dict.attrib['index'])
                    wgtValue= float(dict.attrib['value'])
                    jntWgt[vertIndex]=wgtValue

                cmds.setAttr( twitchBS + ".inputTarget[0].inputTargetGroup[%s].targetWeights[0:%s]"%( tgID,  vtxLen-1), *jntWgt )
                    
                cmds.connectAttr ( remap + ".outValue", twitchBS + "." + targetName )


    
    
    
            

#get joint ID connected with "selected" geo skinCluster 
import re
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





    
def eyeLidCrvIsolate( crvTitle ):

    eyeLidCrv = {  "squint_crv":[ "upSquint_crv", "loSquint_crv" ], "annoy_crv":[ "upAnnoyed_crv", "loAnnoyed_crv" ], "PushA_crv":[ "upALid_crv", "loALid_crv" ], "PushB_crv":[ "l_upLidPushB_crv", "l_loLidPushB_crv" ],
    "PushC_crv":[ "l_upLidPushC_crv", "l_loLidPushC_crv" ], "PushD_crv":[ "l_upLidPushD_crv", "l_loLidPushD_crv" ] }    
    
    eyeCrvClass = []
    for eCrv in eyeLidCrv:
        eyeCrvClass.append(eCrv)
        
    crvSel = []
    if crvTitle in eyeCrvClass:        
        crvList = eyeLidCrv[crvTitle]
        for crv in crvList:
            for LR in [ "l_", "r_"]:
                shpCrv = LR + crv
                if cmds.objExists(shpCrv):
                    crvSel.append(shpCrv)                    
    print crvSel                
    cmds.select( crvSel )
    #isolate
    activePanel = cmds.getPanel( withFocus=True )#return the name of the panel that currently has focus
    panelType = cmds.getPanel( typeOf =activePanel)#return the type of the specified panel
    if panelType == 'modelPanel':
        state = cmds.isolateSelect( activePanel, q=1, s=1)
        if state == 0:
            mel.eval('enableIsolateSelect %s 1' % activePanel)
        else:
            mel.eval('enableIsolateSelect %s 0' % activePanel)
            cmds.select( crvSel )
            mel.eval('enableIsolateSelect %s 1' % activePanel)
    

    

def lipCrvIsolate( lipTitle ):

    lipCrv = { "jawOpen":["up_jawOpen_crv","lo_jawOpen_crv"], "jawDrop":["up_jawDrop_crv","lo_jawDrop_crv"], "happy_crv":["l_up_Happy","l_lo_Happy"],
    "sad_crv":["l_up_Sad","l_lo_Sad" ], "E_crv":["l_up_E","l_lo_E" ], "wide_crv":["l_up_lipWide","l_lo_lipWide" ],
    "U_crv":["l_up_U","l_lo_U" ], "O_crv":["l_up_O","l_lo_O" ] }   

    for crv in lipCrv :
        if lipTitle == crv:
            crvSel = lipCrv[lipTitle]
    cmds.select( crvSel )
    #isolate
    activePanel = cmds.getPanel( withFocus=True )#return the name of the panel that currently has focus
    panelType = cmds.getPanel( typeOf =activePanel)#return the type of the specified panel
    if panelType == 'modelPanel':
        state = cmds.isolateSelect( activePanel, q=1, s=1)
        if state == 0:
            mel.eval('enableIsolateSelect %s 1' % activePanel)
        else:
            mel.eval('enableIsolateSelect %s 0' % activePanel)


def browCrvIsolate( browTitle ):

    browCrv = { "browSad":["l_BrowSad_crv", "r_BrowSad_crv"], "browMad":["l_BrowMad_crv", "r_BrowMad_crv"], "furrow":["l_Furrow_crv", "r_Furrow_crv"], 
    "relax":["l_Relax_crv", "r_Relax_crv"] } 

    for eV in browCrv :
        if browTitle == eV:
            crvSel = browCrv[browTitle]

    cmds.select( crvSel )
    activePanel = cmds.getPanel( withFocus=True )#return the name of the panel that currently has focus
    panelType = cmds.getPanel( typeOf =activePanel)#return the type of the specified panel
    if panelType == 'modelPanel':
        state = cmds.isolateSelect( activePanel, q=1, s=1)
        
        if state == 0:#
            mel.eval('enableIsolateSelect %s 1' % activePanel)
            
        else:
            mel.eval('enableIsolateSelect %s 0' % activePanel)
            mel.eval('enableIsolateSelect %s 1' % activePanel)




# get default curve shape by duplicate Orig Shape
def copyOrigCrv( crv ):

    #copy of crvOrigShape
    crv = "up_lipBS_crv"
    crvTemp = cmds.duplicate( crv )[0]
    intNum = crvTemp[-1]
    newName = cmds.rename( crvTemp, crvTemp[:-1] + "_default" )
    tempShape = cmds.listRelatives( newName, ad=1, type ='shape' )
    for ts in tempShape:
        if 'Orig' in ts:
            tempOrig = cmds.rename( ts, newName + 'Shape' )
        else: cmds.delete(ts)
    cmds.setAttr( tempOrig+".intermediateObject", 0)
    #unlock attributes
    lockAttr = cmds.listAttr( newName, l=1 )
    if lockAttr:
        for at in lockAttr:
            cmds.setAttr( newName + "." + at, l = 0 )

    return newName


#pose to set two curve blendShape to max
#browLip = "brow" or "lip"
def correctiveCrv( browLip ):

    if browLip =="brow":
        # get target curves whose weight == 1
        aliasBS = cmds.aliasAttr( "browBS", q=1 )
        lTgts = []
        rTgts = []
        for tgt, wgt in zip(*[iter(aliasBS)]*2):
            val = cmds.getAttr( "browBS." + tgt )
            if val == 1:
                if tgt[0]=="l":
                    lTgts.append(tgt) 
        
                elif tgt[0]=="r":
                    rTgts.append(tgt) 
                             
        print lTgts, rTgts
        for i, ts in enumerate([lTgts,rTgts]):
            if len(ts) ==2:
                
                nameSplit = ts[0].split("_")
                fixName = '%s_%s_%s_fix'%( nameSplit[0], nameSplit[1], ts[1].split("_")[1] )
                print fixName
                defautBrowCrv = copyOrigCrv( "brow_crv" )    
                browFixCrv = cmds.rename (defautBrowCrv, fixName )  
                cmds.blendShape( "browBS",  edit=True, t=( "brow_crv", len(aliasBS)/2+i, browFixCrv, 1.0) )
                
                addD =cmds.shadingNode ( 'addDoubleLinear', asUtility=True, n = fixName.replace("fix","addD") )
                cmds.connectAttr( "browBS." + ts[0], addD + ".input1")
                cmds.connectAttr( "browBS." + ts[1], addD + ".input2")
                
                remap =cmds.shadingNode ( 'remapValue', asUtility=True, n = fixName.replace("fix","remap") )
                cmds.connectAttr( addD+".output", remap + ".inputValue" )
                cmds.setAttr( remap + ".inputMin", 1 ) 
                cmds.setAttr( remap + ".inputMax", 2 )      
                cmds.connectAttr(remap + ".outValue", "browBS."+ browFixCrv )
            
    if browLip =="lip":
    
        aliasUpBS = cmds.aliasAttr( "upLipCrvBS", q=1 )
        lTgts = []
        rTgts = []
        for tgt, wgt in zip(*[iter(aliasUpBS)]*2):
            val = cmds.getAttr( "upLipCrvBS." + tgt )
            if val == 1:
                if tgt[0]=="l":
                    lTgts.append(tgt) 
        
                elif tgt[0]=="r":
                    rTgts.append(tgt)
        
        lCorrect = []
        rCorrect = []
        for i, ts in enumerate([lTgts,rTgts]):
            if len(ts) ==2:

                fixName = '%s_%s_fix'%( ts[0], ts[1].split("_")[2] )
                
                defautLipCrv = copyOrigCrv( "up_lipBS_crv" )
  
                upLipFix = cmds.rename ( defautLipCrv, fixName )          
                cmds.blendShape( "upLipCrvBS",  edit=True, t=( "up_lipBS_crv", len(aliasUpBS)/2+i, upLipFix, 1.0) )
                
                loFirst = ts[0].replace("up","lo")
                loSecnd = ts[1].replace("up","lo")
                loFixName = fixName.replace("up", "lo")
                loCrvTemp = cmds.duplicate( upLipFix )
                loLipFix = cmds.rename (loCrvTemp[0], loFixName )
                cmds.blendShape( "loLipCrvBS",  edit=True, t=("lo_lipBS_crv", len(aliasUpBS)/2+i, loLipFix, 1.0) )                 
                
                plus =cmds.shadingNode ( 'plusMinusAverage', asUtility=True, n = ts[0][:2]+fixName.replace("fix","Plus") )
                cmds.connectAttr( "upLipCrvBS." + ts[0], plus + ".input2D[0].input2Dx" )
                cmds.connectAttr( "upLipCrvBS." + ts[1], plus + ".input2D[1].input2Dx" )
                cmds.connectAttr( "loLipCrvBS." + loFirst, plus + ".input2D[0].input2Dy" )
                cmds.connectAttr( "loLipCrvBS." + loSecnd, plus + ".input2D[1].input2Dy" )
                        
                upRemap =cmds.shadingNode ( 'remapValue', asUtility=True, n = ts[0][:2]+fixName.replace("fix","remap") )
                loRemap =cmds.shadingNode ( 'remapValue', asUtility=True, n = ts[0][:2]+loFixName.replace("fix","remap") )
                cmds.connectAttr( plus+".output2Dx", upRemap + ".inputValue" )
                cmds.connectAttr( plus+".output2Dy", loRemap + ".inputValue" )
                cmds.setAttr( upRemap + ".inputMin", 1 ) 
                cmds.setAttr( upRemap + ".inputMax", 2 )
                cmds.setAttr( loRemap + ".inputMin", 1 ) 
                cmds.setAttr( loRemap + ".inputMax", 2 )       
                cmds.connectAttr(upRemap + ".outValue", "upLipCrvBS."+ upLipFix )
                cmds.connectAttr(loRemap + ".outValue", "loLipCrvBS."+ loLipFix )
                
                if i == 0:
                    lCorrect.append(upLipFix )
                    lCorrect.append(loLipFix )
                else:
                    rCorrect.append(upLipFix )
                    rCorrect.append(loLipFix )

        for lCrv, rCrv in zip( lCorrect, rCorrect):
            mirrorCurve( lCrv, rCrv)            
        
#correctiveCrv( "lip" )
    
    
#mirror left curve(cvs) to right curve(cvs), all left curves are from 0 to +x
def mirrorCurve( lCrv, rCrv):

    lCrvCv = cmds.ls( lCrv + '.cv[*]', fl =1)
    rCrvCv = cmds.ls( rCrv + '.cv[*]', fl =1)
    cvLeng = len(lCrvCv)
    
    for i in range( cvLeng ):
        mirrorAdd = cmds.shadingNode('addDoubleLinear', asUtility=True, n = 'mirror' + str(i) + '_add' )
        cmds.setAttr( mirrorAdd + '.input1', 1 )
        reversMult = cmds.shadingNode('multiplyDivide', asUtility =1, n = 'reverse%s_mult'%str(i).zfill(2))
        cmds.connectAttr( lCrvCv[i] + '.xValue', reversMult+ '.input1X')
        cmds.setAttr ( reversMult+ '.input2X', -1 )
        cmds.connectAttr ( reversMult+ '.outputX', mirrorAdd + '.input2' )
        cmds.connectAttr( mirrorAdd + '.output', rCrvCv[cvLeng-i-1] + '.xValue' )
        cmds.connectAttr( lCrvCv[i] + '.yValue', rCrvCv[cvLeng-i-1] + '.yValue' )
        cmds.connectAttr( lCrvCv[i] + '.zValue', rCrvCv[cvLeng-i-1] + '.zValue' )

        
#miscellaneous--------------------------------------------------------------------------------------------------------------------------------------------------------------#
# when merge arFace_head to body
# select geo( in arFace reference file ) that equivalent geo in body file
# selec the pairs one at the time
def blendShapeHead_toBody():
    
    mySel = cmds.ls(sl=1, typ = "transform")
    srcTem = mySel[0]
    trgTem = mySel[1]
    
    srcShp = cmds.listRelatives( srcTem, c = 1, typ = "mesh" )
    trgShp = cmds.listRelatives( trgTem, c = 1, typ = "mesh" )   
                      
    if srcShp and trgShp : # if select geos 
        
        commnTitle = getCommonString_twoItem( srcTem, trgTem ) #return [ common name, first item, second item ] 
        BS = cmds.blendShape( srcTem, trgTem, foc =1, tc=1, n = commnTitle[0] + "bs" )
        cmds.setAttr( BS[0] + "." + commnTitle[1], 1 )
        
    else:
        srcShapes = []
        for x in cmds.listRelatives( srcTem, ad = 1, typ = "mesh" ):
            print x
            if cmds.getAttr( x + ".intermediateObject" )==False:
                srcShapes.append(x)

        trgShapes = []
        for y in cmds.listRelatives( trgTem, ad = 1, typ = "mesh" ):
            print y
            if cmds.getAttr( y + ".intermediateObject" )==False:
                trgShapes.append(y)
                
        common = getCommonString_twoItem( srcShapes[0], trgShapes[0] )  
           
        yesNo = cmds.confirmDialog( title='Confirm', message='common name is %s'%common[0], button=['Yes','No'], defaultButton='Yes', cancelButton='No', dismissString='No' )
        
        if yesNo == "Yes":
            
            for i, src in enumerate(srcShapes):
                
                srcGeo = cmds.listRelatives( src, p = 1, typ = "transform" )
                trgGeo = cmds.listRelatives( trgShapes[i], p = 1, typ = "transform" )
                 
                commonName = getCommonString_twoItem( srcGeo[0], trgGeo[0] )                
                
                bs = cmds.blendShape( srcGeo, trgGeo, foc =1, tc=1, n = commonName[0] + "bs" )
                cmds.setAttr( bs[0] + "." + srcGeo[0], 1 )               
                
        else:
            pass
            



#이름이 "_"로 연결되 있어야 한다
   
def getCommonString_twoItem( first, second ):
    
    common = ""
    difference = ""
    if "|" in first and "|" in second:        
        
        first = first.split("|")[-1]
        second = second.split("|")[-1]
        firstNames = first.split("_")
        secondNames = second.split("_")        
        
    else:
        firstNames = first.split("_")
        secondNames = second.split("_")   
    
    for fn in firstNames:
        if fn in secondNames:
            common = fn
            
        else:
            difference = "_" + fn
            
    return [ common+difference, first, second ] 
            
            




#get Orig mesh using tweak node and avoid name dependency
def parse_active_panel():
    """Parse the active modelPanel.

    Raises
        RuntimeError: When no active modelPanel an error is raised.

    Returns:
        str: Name of modelPanel

    """

    panel = cmds.getPanel(withFocus=True)

    # This happens when last focus was on panel
    # that got deleted (e.g. `capture()` then `parse_active_view()`)
    if not panel or "modelPanel" not in panel:
        raise RuntimeError("No active model panel found")

    return panel


# select list of objects that needs to be appear in the panel
def addIsolatePanel(mySel):    
    activePanel = parse_active_panel()    
    state = cmds.isolateSelect( activePanel, q=1, s=1)
    if state == 1:
        
        objSet = cmds.isolateSelect( activePanel, q=1, viewObjects = 1 )
        for oj in mySel:
            memberStatus = cmds.sets( oj, isMember = objSet  )
            print memberStatus
            if memberStatus == 1:
                cmds.select( oj, r=1 )
                cmds.isolateSelect( activePanel, removeSelected = 1 )
            else:
                cmds.select( oj, r=1 )
                cmds.isolateSelect( activePanel, addSelected = 1 )

            
def fixMix():
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
        
        defaultMesh = copyOrigMesh( headBase, "originGeo" )
        
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

 
 
 
 
#return intermediate shape and delete the one that is not connected
#if multiple intermediate shapes, list order should be bottom to up
def getOrigMesh( obj ):    
    
        #get the shapes of child
        shapes = cmds.listRelatives(obj, s=1)
        #get intermediate shapes

        intermediateObj = [ x for x in shapes if cmds.getAttr(x + ".intermediateObject") == 1 ]
        origShape = []
        for orig in intermediateObj:

            #if nothing is connected to the shape node, delete it
            connections = cmds.listConnections(orig, s=0, d=1)
            if connections:
                connections = cmds.listConnections(orig, s=1, d=0 )
                if connections:
                    print orig + " is first origShape"
                else:
                    origShape.append( orig ) 
                
            else:
                cmds.delete(orig)
        
        return origShape
    


# new name should be given
def copyOrigMesh( obj, name ):
    
    #get the orig shapes with history and delete the ones with with same name.
    origShapes = getOrigMesh( obj )
    
    if origShapes:
        myOrig = origShapes[0]
        
        #unique origShape duplicated
        headTemp = cmds.duplicate( myOrig, n = name, renameChildren =1 )
        tempShape = cmds.listRelatives( headTemp[0], ad=1, type ='shape' )
     
        for ts in tempShape:
            if 'Orig' in ts:
                tempOrig = cmds.rename( ts, name+ 'Shape' )
            else:
                print "delete %s"%ts
                cmds.delete(ts)
        
        cmds.setAttr( tempOrig+".intermediateObject", 0)
        cmds.sets ( tempOrig, e=1, forceElement = 'initialShadingGroup' )

        for trs in ['t','r','s']:
            for c in ['x','y','z']:
                if cmds.getAttr( headTemp[0] + '.' + trs + c, lock =1 ):
                    cmds.setAttr(headTemp[0] + '.' + trs + c, lock =0 )
        return headTemp[0]
        
    else:
        pm.confirmDialog( title='Confirm', message='selected object has no origShape(intermediateObject)' )
        
    

        


#update main shape and propagate to L/R shapes????
def updateDelta_toLRshapes(): 

    if cmds.objExists( "twitchBS "):
    
        alias = cmds.aliasAttr( "twitchBS", q=1 )
    for tgt, wgt in zip(*[iter(alias)]*2):
        wgtVal = cmds.getAttr( "twitchBS."+tgt )
        if wgtVal:
            if "l_" or "r_" in tgt:
                print "activate main target"
            else:
                tgtID = wgt.split("[")[1][:-1]
            
    delta = cmds.getAttr( "twitchBS.inputTarget[0].inputTargetGroup[%s].inputTargetItem[6000].inputPointsTarget"%str(tgtID) )
    cmds.setAttr( "twitchBS.inputTarget[0].inputTargetGroup[%s].inputTargetItem[6000].inputPointsTarget"%str(tgtID+1), *delta )
    cmds.setAttr( "twitchBS.inputTarget[0].inputTargetGroup[%s].inputTargetItem[6000].inputPointsTarget"%str(tgtID+2), *delta )




""" create a new shader """
def createShader(shaderType='lambert', name=''):
    if name == '':
        name = shaderType
    name = cmds.shadingNode(shaderType, asShader=True,  name=name)
    sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name='%sSG' %(name))

    # connect shader to SG
    shaderOutput = 'outValue'
    if shaderType== 'mia_material' or shaderType == 'mia_material_x':
        if shaderType == 'mia_material_x':
            shaderOutput = "result";
        cmds.connectAttr('%s.%s' %(name,shaderOutput), '%s.miMaterialShader' %(sg), force=True)
        cmds.connectAttr('%s.%s' %(name,shaderOutput), '%s.miShadowShader' %(sg), force=True)
        cmds.connectAttr('%s.%s' %(name,shaderOutput), '%s.miPhotonShader' %(sg), force=True)
    else:
        cmds.connectAttr('%s.outColor' %(name), '%s.surfaceShader' %(sg), force=True)
    
    return [name, sg]


def assignToShader(shaderSG=None, objects=None):
    # assign selection to the shader
    if objects is None:
        objects = cmds.ls(sl=True, l=True)
    for i in objects:
        print i
        try:
            cmds.sets(i, e=True, forceElement=shaderSG)
        except:
            pass




#create left right weight map.
def createSplitMap():

    myGeo = cmds.ls( sl=1, type = "transform")
    lTarget = cmds.duplicate( myGeo[0], n = "l_weightMap" )
    rTarget = cmds.duplicate( myGeo[0], n = "r_weightMap" )   
    splitBS = cmds.blendShape( lTarget[0], rTarget[0], myGeo[0], n = "splitMapBS" )
    
    size = cmds.polyEvaluate( myGeo[0], v=1)
     
    # create ramp texture to seperate out L / R weight map for blendShape
    #returen [name, shadingGroup]
    shader = createShader(shaderType='lambert', name='splitMapShader')
    ramp = cmds.shadingNode( "ramp", asTexture =1, n = "splitMapRamp" )
    cmds.setAttr ( ramp + ".type", 1 )
    cmds.setAttr ( ramp + ".colorEntryList[1].color", 1,1,1, type ="double3" )
    cmds.setAttr ( ramp + ".colorEntryList[0].color", 0,0,0, type ="double3" )
    cmds.setAttr( ramp+".colorEntryList[0].position", 0.45)
    cmds.setAttr( ramp+".colorEntryList[1].position", 0.55)
    texture = cmds.shadingNode( "place2dTexture", asUtility =1 )
    cmds.connectAttr( texture + ".outUV", ramp + ".uv", f=1 )
    cmds.connectAttr( texture + ".outUvFilterSize", ramp + ".uvFilterSize")
    cmds.connectAttr ( ramp + ".outColor",  shader[0] + ".color", f=1 )
    #assignToShader
    cmds.sets( lTarget[0], e=True, forceElement= shader[1] )    
    
    for i in range( size ):
        ptPos = cmds.pointPosition ( lTarget[0]+".vtx[%s]"%str(i))
        pos = mel.eval("nearestPointOnMesh -ip " + str(ptPos[0]) + " " + str(ptPos[1]) + " " + str(ptPos[2]) + " -q -parameterU -parameterV " + myGeo[0] )  
        colPnt = cmds.colorAtPoint ( ramp, output = "RGB", u = pos[0], v =pos[1] )
        cmds.setAttr( splitBS[0] + ".it[0].itg[0].tw[%s]"%str(i), colPnt[0] )   
        cmds.setAttr( splitBS[0] + ".it[0].itg[1].tw[%s]"%str(i), 1 - colPnt[0] ) 
         
    cmds.delete( lTarget[0], rTarget[0] )
    
    


#select corrrective shape and 
def correctiveSetup():
    # add corrective shapes to the blendShape
    base = 'head_REN'
    trgt = cmds.ls( sl = 1, type = "transform" )[0]
    myBS = cmds.ls( cmds.listHistory(base), type = "blendShape" )
    if myBS:            
        existTarget = cmds.aliasAttr (myBS[0], q =1 )
        targetLen = len(existTarget)/2        
        cmds.blendShape(myBS[0], e = 1, target = [ base, targetLen, trgt, 1.0])
        
    elif not myBS:
        myBS = cmds.blendShape ( trgt, base, foc =1, n = "twitchBS" )
   
    if not myBS[0] == 'twitchBS':
        cmds.rename(myBS[0], 'twitchBS')
    cmds.select(cl = 1) 
    
    


# select target(name!!) and base with blendShape( reconnect the target to blendShape )
def targetAdd_Reconnect( BSnode ):
    
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
                print "delete %s"%xx
                cmds.delete(xx)
            
        aliasAtt = cmds.aliasAttr(BSnode, q=1)
        if target in aliasAtt:
            for tgt, wgt in zip(*[iter(aliasAtt)]*2):
                tgtID = wgt.split("[")[1][:-1]        
                print tgtID
                # check if target curve exists
                if target == tgt :
                    tgtID = wgt.split("[")[1][:-1]
                    if cmds.nodeType(shp[0]) == "mesh":
                        connection = cmds.listConnections( BSnode+ ".inputTarget[0].inputTargetGroup[%s].inputTargetItem[6000].inputGeomTarget"%str(tgtID), sh=1 )
                        if connection:
                            continue
                        else:
                            print shp[0], tgtID
                            cmds.connectAttr( shp[0]+".worldMesh", BSnode+ ".inputTarget[0].inputTargetGroup[%s].inputTargetItem[6000].inputGeomTarget"%str(tgtID) )
                            
                    elif cmds.nodeType(shp[0]) == "nurbsCurve":
                        cmds.connectAttr( shp[0]+".worldSpace", BSnode+ ".inputTarget[0].inputTargetGroup[%s].inputTargetItem[6000].inputGeomTarget"%str(tgtID) )
                                    
        else:
            print target
            maxNum = []
            for x, y in zip(*[iter(aliasAtt)]*2):
                num = y.split("[")[1][:-1]
                maxNum.append(int(num))
                
            #add corrective crvs in BlendShape    
            maxNum = max(maxNum)            
        
            targetID = maxNum + 1
            cmds.blendShape( BSnode, e=1, t = [base, targetID, target, 1 ] )
        
        
        

#1. 타겟 커브를 소스 커브와 동일한 기울기로 맞춘후에 bakeCrvDeltaBS를 실행한다.
#2. 
def transferCurveBS( srcCrv, tgtCrv, name ):
    # curve cvs
    srcCvs = cmds.ls( srcCrv + ".cv[*]", fl=1 )
    tgtCvs = cmds.ls( tgtCrv + ".cv[*]", fl=1 )

    srcLeng = len(srcCvs)
    tgtLeng = len(tgtCvs)

    vectorAngle = angleGap_2crvs(srcCrv, tgtCrv )
    # source vector bigger than target vector angle 
    if vectorAngle[0]>vectorAngle[1]:
        angle = vectorAngle[2]
    # target vector bigger than source vector angle 
    else:
        angle = -vectorAngle[2]

    print angle
    startNum = 1
    endNum = srcLeng/2 + 1

    targetRotCls = cmds.cluster( tgtCvs[startNum], n = tgtCrv + "_cls" )
    clsSet = cmds.listConnections( targetRotCls[0], type="objectSet" )[0]
    tgtCvs.remove(tgtCvs[startNum])
    cmds.sets( tgtCvs, add= clsSet )

    cmds.setAttr( targetRotCls[1] + ".rx", angle )
    # delete history
    cmds.delete( tgtCrv, ch=1 )
    bakeCrvDeltaBS( srcCrv, tgtCrv, name )
    bakeTarget_reconnect(tgtCrv)
    
    cvs = cmds.ls( tgtCrv + ".cv[*]", fl=1 )
    rotateCls = cmds.cluster( cvs[startNum], n = tgtCrv + "_nCls" )
    clusterSet = cmds.listConnections( rotateCls[0], type="objectSet" )[0]
    cvs.remove(cvs[startNum])
    cmds.sets( cvs, add= clusterSet )

    cmds.setAttr( rotateCls[1] + ".rx", -angle )
    
    bendDfm = cmds.nonLinear( tgtCvs, type = "bend", curvature=0 ) 
    bendHandle = bendDfm[1]            
    cmds.setAttr( bendHandle + ".rz", -90 )
    cmds.setAttr( bendHandle + ".ry", 90 ) 

    

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
        pm.confirmDialog( title='Confirm', message='source/target CV numbers are different' )



# select curve with BS and new curve in origin world
# copy BS delta when number of cvs are same.     
def bakeCrvDeltaBS( sourceCrv, targetCrv, name):    

    for crv in [ sourceCrv, targetCrv ]:
        cmds.xform( crv, centerPivots =1 )
    multList = boundingRatio_2Object( sourceCrv, targetCrv )
    #attribute where history connects on shape nodes
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

        # get ratio delta that fit to the size of new curve
        print multList[0], multList[1], multList[2]
        comp = [0]
        for i in range( numTgt ):
            # length of comp is different for each target because the vertexs that has none movement don't counts
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
                cmds.confirmDialog( title='Confirm', message='dnTarget[i] + " delta has none ' )

    else:
        cmds.confirmDialog( title='Confirm', message='create blendShape first' )




# select two object 
# get the ratio( 2nd obj/1st obj) for size comparison 
def boundingRatio_2Object( source, target ):

    #source curve bounding box
    scOrig = [ x for x in cmds.listRelatives( source, s=1, fullPath=1 ) if 'Orig' in x ]
    print scOrig
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






# select targetCurve and sourceCurve : create target curves
# plug targetCrv to sourceCrv and generate all target curves
# 선택1 커브 쉐입을 선택2 커브에 plug in하고 타겟커브를 재생시킨다.
def plugShapeToCrvWithBS( targetCrv, sourceCrv ):    

    shapes = cmds.listRelatives( sourceCrv, ad=1, type='shape' )
    origCrv = [ t for t in shapes if 'Orig' in t ]
    #get the orig shapes with history and delete the ones with with same name.
    myOrig = ''
    for orig in origCrv:
        if cmds.listConnections( orig, s=0, d=1 ):
            myOrig = orig
        else: cmds.delete(orig)
    
    # delete source curve BS target
    crvBS = [ n for n in cmds.listHistory( sourceCrv, historyAttr=1 ) if cmds.nodeType(n) == "blendShape" ]    
    if crvBS:
        aliasAtt = cmds.aliasAttr(crvBS[0], q=1)
        for tgt, wgt in zip(*[iter(aliasAtt)]*2):
            if cmds.objExists(tgt):
                cmds.delete(tgt)       
    else:
        print "select the curve with blendShape" 

    # target shape plug in     
    targetCrvShp = cmds.listRelatives( targetCrv, c=1, ni=1, type='shape' )[0]    
    cmds.connectAttr( targetCrvShp +".worldSpace", myOrig + ".create", f=1 )
        
    for tgt, wgt in zip(*[iter(aliasAtt)]*2):
        cnnt = cmds.listConnections(  crvBS[0]+"."+tgt, s=1, d=0, p=1 )[0]
        if cnnt:
            cmds.disconnectAttr( cnnt, crvBS[0]+"."+tgt )
        
        cmds.setAttr( crvBS[0] + "." + tgt, 1 )
        copyCrv = cmds.duplicate ( sourceCrv, n= tgt )[0]
        copyCrvShape = cmds.listRelatives( copyCrv, c=1 )[0]
        tgtID = wgt.split("[")[1][:-1]
        print tgtID
        cmds.connectAttr( copyCrvShape + ".worldSpace[0]", crvBS[0] + ".inputTarget[0].inputTargetGroup[%s].inputTargetItem[6000].inputGeomTarget"%tgtID )
        cmds.setAttr( crvBS[0] + "." + tgt, 0 )
        
        if cnnt:
            cmds.connectAttr( cnnt, crvBS[0]+"."+tgt )
                        




    
#create targets after copy blendShape delta        
#select curve with blendShape(clean, no connections)
#copy target and reconnect for blendShape
def bakeTarget_reconnect(baseCrv):

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
            
        targetGrp = cmds.group( em=1, n = baseCrv + "_tgtGrp")
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


    
           
           
            
#name the curve except the prefix "l_up/lo_"
#select myCrv(single) and BS_crv for blendShape( ex: happy_crv and "up_lipBS_crv" / happy_crv and "lo_lipBS_crv"  )
def crvAdd_reconnect( myCrvs ):

    myCrv = myCrvs[0]
    bsCrv = myCrvs[-1]
    history = cmds.listHistory( bsCrv, pruneDagObjects =1, interestLevel= 1 )
    bsDeform = [ x for x in history if cmds.nodeType( x ) == "blendShape"]
    
    if bsDeform:
        bsCrvBS = bsDeform[0]     
        aliasAtt = cmds.aliasAttr( bsCrvBS, q=1 )
        maxNum = []
        for x, y in zip(*[iter(aliasAtt)]*2):
            num = y.split("[")[1][:-1]
            maxNum.append(int(num))
            
        #add corrective crvs in BlendShape    
        maxNum = max(maxNum) 
        
        if "lip" in bsCrvBS.lower():
            
            lUpLow = "l_"+ bsCrv[:2]
            rUpLow = "r_"+ bsCrv[:2]
            lCrv   = cmds.duplicate(myCrv,  n = lUpLow + '_' + myCrv, rc=1 )
            rCrv   = cmds.duplicate(myCrv,  n = rUpLow + '_' + myCrv, rc=1 )
            
        elif "brow" in bsCrvBS.lower():

            lUpLow = "l_"
            rUpLow = "r_"
            lCrv   = cmds.duplicate(myCrv,  n = lUpLow + myCrv, rc=1 )
            rCrv   = cmds.duplicate(myCrv,  n = rUpLow + myCrv, rc=1 )
        
        print lCrv, rCrv
        if lCrv[0] in aliasAtt:
            print "Reconnect"
            for x, y in zip(*[iter(aliasAtt)]*2):
                if x == lCrv[0]:
                    index = y.split("[")[1][:-1]
                    cmds.connectAttr( lCrv[0] +".worldSpace", bsCrvBS+ ".inputTarget[0].inputTargetGroup[%s].inputTargetItem[6000].inputGeomTarget"%index )
                    
                elif x == rCrv[0]:
                    indx = y.split("[")[1][:-1]
                    cmds.connectAttr( rCrv[0] +".worldSpace", bsCrvBS+ ".inputTarget[0].inputTargetGroup[%s].inputTargetItem[6000].inputGeomTarget"%indx )                 
                        
        else:
            print "Add"
            cmds.blendShape( bsCrvBS, e=1, t = ( bsCrv, maxNum+1, lCrv[0], 1 ) )
            cmds.blendShape( bsCrvBS, e=1, t = ( bsCrv, maxNum+2, rCrv[0], 1 ) )       

        if "lip" in bsCrvBS.lower():

            mirrorCurve( lCrv[0], rCrv[0] )
            
        elif "brow" in bsCrvBS.lower():

            LRBlendShapeWeight( bsCrv, bsCrvBS )         
        
        return [lCrv[0], rCrv[0]]    

# copy bsCrv and name it (ex: "up_cornerWD", "lo_E_Happy")
# set ctrls 1 / select corrective and base 
def addCrv_corrective(crvs ):

    base = crvs[-1]
    BSnode = [ n for n in cmds.listHistory(base, historyAttr=1 ) if cmds.nodeType(n) == "blendShape" ]  
    if BSnode:
        aliasAtt = cmds.aliasAttr(BSnode[0], q=1)        
    else:
        print "select the object with blendShape"  
    target = crvs[0]
    
    #turn off the deformers     
    hist = cmds.listHistory( base, pruneDagObjects =1, interestLevel= 1 )
    dformers = [ x for x in hist if "geometryFilter" in cmds.nodeType( x, inherited =1 )]
    for dform in dformers:
        cmds.setAttr( dform + ".nodeState", 1 )
        
    fixMult = cmds.shadingNode( "multiplyDivide", asUtility =1, n = target +"_mult" )
    lCrv = cmds.duplicate( base, rc =1, n = "l_"+ target + "_fix" )[0]
    rCrv = cmds.duplicate( base, rc =1, n = "r_"+ target + "_fix" )[0]
    
    if "lip" in BSnode[0].lower():
        print BSnode[0]
        mirrorCurve( lCrv, rCrv )
    elif "brow" in BSnode[0].lower():
        LRBlendShapeWeight( base, BSnode[0] )          
        
    cmds.hide(rCrv)
    #cmds.delete(target)
    
    maxNum = []
    for x, y in zip(*[iter(aliasAtt)]*2):
        num = y.split("[")[1][:-1]
        maxNum.append(int(num))
    
    #turn on the deformers
    for dform in dformers:
        cmds.setAttr( dform + ".nodeState", 0 )
        
    #add corrective crvs in BlendShape    
    maxNum = max(maxNum)            
    cmds.blendShape( BSnode[0], e=1, t = [base, maxNum + 1, lCrv, 1 ] )
    cmds.blendShape( BSnode[0], e=1, t = [base, maxNum + 2, rCrv, 1 ] )
    
    srcList = []
    for tgt, wgt in zip(*[iter(aliasAtt)]*2):                
        if cmds.getAttr( BSnode[0] + "." + tgt )==1:
            srcList.append(tgt)     

    if srcList:
        cmds.connectAttr( BSnode[0] + "."+srcList[0], fixMult + ".input1X")
        cmds.connectAttr( BSnode[0] + "."+srcList[1], fixMult + ".input1Z")
        
        cmds.connectAttr( BSnode[0] + "."+srcList[2], fixMult + ".input2X")
        cmds.connectAttr( BSnode[0] + "."+srcList[3], fixMult + ".input2Z")
                
        print BSnode[0]
        cmds.connectAttr( fixMult + ".outputX", BSnode[0]+".%s"%lCrv ) 
        cmds.connectAttr( fixMult + ".outputZ", BSnode[0]+".%s"%rCrv ) 
        
    else:
        cmds.confirmDialog( title='Confirm', message='set ctrl to 1 to get blendShape target' )   


# select the target curves
def resetTargetCrv( targets ):
    # select target curves with bs
    targets = cmds.ls(sl=1, typ = "transform")
    tgtShape = cmds.listRelatives(targets[0], ni=1, s=1 )
    BSnode = cmds.listConnections( tgtShape, s=0, d=1 )
    if BSnode:
        hist = cmds.listHistory( BSnode[0], il=1 )
        tweakNode = [ x for x in hist if cmds.nodeType( x ) == "tweak" ]
        if tweakNode:
        
            cnnct = cmds.listHistory(tweakNode[0], il =1 ) 
            origShp = []
            for ct in cnnct:
                if cmds.nodeType(ct) in ( "mesh", "nurbsSurface", "nurbsCurve" ):
                    if cmds.getAttr(ct + ".intermediateObject"):
                        origShp.append(ct)
    
            if len(origShp)==1:
                
                plugPoints = cmds.getAttr( origShp[0] + ".controlPoints" , mi=1 )
                for tgt in targets:
                    
                    tgtShp = cmds.listRelatives(tgt, ni=1, s=1 )[0]
                    for i in range(len(plugPoints)):
                        cmds.connectAttr( origShp[0] + ".controlPoints[%s]"%str(i), tgtShp + ".controlPoints[%s]"%str(i) )
                        cmds.disconnectAttr( origShp[0] + ".controlPoints[%s]"%str(i), tgtShp + ".controlPoints[%s]"%str(i) )
                          
            else:
                cmds.confirmDialog(title='Confirm', message='%s has multiple origShapes (%s and %s), do it manuallye'%(obj, origShp[0], origShp[1]) ) 




#mirror left curve(cvs) to right curve(cvs), all curves are from 0 to +x
def mirrorCurve( lCrv, rCrv):

    lCrvCv = cmds.ls( lCrv + '.cv[*]', fl =1)
    rCrvCv = cmds.ls( rCrv + '.cv[*]', fl =1)
    cvLeng = len(lCrvCv)
    
    for i in range( cvLeng ):
        mirrorAdd = cmds.shadingNode('addDoubleLinear', asUtility=True, n = 'mirror' + str(i) + '_add' )
        cmds.setAttr( mirrorAdd + '.input1', 1 )
        reversMult = cmds.shadingNode('multiplyDivide', asUtility =1, n = 'reverse%s_mult'%str(i).zfill(2))
        cmds.connectAttr( lCrvCv[i] + '.xValue', reversMult+ '.input1X')
        cmds.setAttr ( reversMult+ '.input2X', -1 )
        cmds.connectAttr ( reversMult+ '.outputX', mirrorAdd + '.input2' )
        cmds.connectAttr( mirrorAdd + '.output', rCrvCv[cvLeng-i-1] + '.xValue' )
        cmds.connectAttr( lCrvCv[i] + '.yValue', rCrvCv[cvLeng-i-1] + '.yValue' )
        cmds.connectAttr( lCrvCv[i] + '.zValue', rCrvCv[cvLeng-i-1] + '.zValue' )
        



def LRBlendShapeWeight( lipCrv, lipCrvBS):
    cvs = cmds.ls(lipCrv+'.cv[*]', fl =1)
    length = len (cvs)
    
    increment = 1.0/(length-1)
    targets = cmds.aliasAttr( lipCrvBS, q=1)
    tNum = len(targets)   
    
    for t in range(0, tNum, 2):
        if targets[t][0] == 'l' :
            indexL=re.findall('\d+', targets[t+1])
            cmds.setAttr(lipCrvBS + '.inputTarget[0].inputTargetGroup[%s].targetWeights[%s]'%(str(indexL[0]), str(length/2)), .5 ) 
            for i in range(0, length/2):                
                cmds.setAttr(lipCrvBS + '.inputTarget[0].inputTargetGroup[%s].targetWeights[%s]'%(str(indexL[0]), str(i)), 0 ) 
                cmds.setAttr(lipCrvBS + '.inputTarget[0].inputTargetGroup[%s].targetWeights[%s]'%(str(indexL[0]), str(length-i-1)), 1 )   
                
        if targets[t][0] == 'r' :
            indexR=re.findall('\d+', targets[t+1])
            cmds.setAttr(lipCrvBS + '.inputTarget[0].inputTargetGroup[%s].targetWeights[%s]'%(str(indexR[0]), str(length/2)), .5 ) 
            for i in range(0, length/2):                
                cmds.setAttr(lipCrvBS + '.inputTarget[0].inputTargetGroup[%s].targetWeights[%s]'%(str(indexR[0]), str(i)), 1 ) 
                cmds.setAttr(lipCrvBS + '.inputTarget[0].inputTargetGroup[%s].targetWeights[%s]'%(str(indexR[0]), str(length-i-1)), 0 )
                
                
                
                



#select target and base mesh( create new blendshape with target_x, target_y, target_z )     
def splitXYZ():
    sel= cmds.ls(sl=1, type = "transform")
    if len(sel)<=1:
        cmds.warning( "Select the target meshs you need to split, last select the base mesh" )
        
    else:
        xyzTget =[]
        for i in ["x","y","z"]:        
            tget = isolatAxisBlend( sel[1], sel[0], i )
            print tget
            xyzTget.append(tget)
        print xyzTget    
        cmds.blendShape( xyzTget, sel[1], n = sel[0]+"_xyzBS" )


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



def splitXYZ_crv():
    sel= cmds.ls(sl=1, type = "transform")
    if len(sel)<=1:
        cmds.warning( "Select the target meshs you need to split, last select the base mesh" )
        
    else:
        xyzTget =[]
        for i in ["x","y","z"]:        
            tget = isolatAxisCrv( sel[1], sel[0], i )
            print tget
            xyzTget.append(tget)
            
        print xyzTget    
        cmds.blendShape( xyzTget, sel[1], n = sel[0]+"_xyzBS" )
        
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
    
    
#get all the shape nodes and delete one that has no connection
def deleteOrigShapes( mySel):

    for oj in mySel:        
        shps = cmds.listRelatives( oj, fullPath=1, c=1 )
        origShp = [ s for s in shps if cmds.getAttr( s + ".intermediateObject" ) == True ]
        #do not delete if there is only one shape node
        if origShp:
            for orig in origShp :
                connections = cmds.listConnections( orig )
                if not connections:
                    print orig
                    cmds.delete( orig )
                    
                        



def create_wtCircle():
    
    baseGeo = cmds.ls(sl=1)[0]
    bbox = cmds.exactWorldBoundingBox( baseGeo )
    wtCircle = cmds.circle( c=( 0, 0, 0),  nr = (0, 1, 0), sw= 360, d= 3, ut= 0, tol= 0.01, s= 8, ch= 1)[0]
    makeCircle = cmds.listHistory( wtCircle, il = 1, pdo =1 )
    cmds.setAttr( makeCircle[0] + ".radius", 10 )
    cmds.setAttr( wtCircle + ".ry", 180 )
    yDist =  ( bbox[4] - bbox[1] )/2
    zDist =  ( bbox[-1] -bbox[2] )/2
    cmds.xform( wtCircle, ws=1, t = (0, yDist + bbox[1], zDist + bbox[2] ) )
    wtCrvNum = len(cmds.ls("lipWT_base_crvShape*"))
    wtCrv = cmds.rename( wtCircle, "lipWT_base_crv"+ str(wtCrvNum+1) )  
    cmds.makeIdentity( wtCrv, apply=1, t= 1, r = 1, s = 1, n = 0, pn = 1 )
    cmds.rebuildCurve( wtCrv, ch=1, rpo= 1, rt= 0, end= 1, kr= 0, kcp= 0, kep= 1, kt= 0, s= 44, d= 3, tol= 0.01 )
    cmds.delete( wtCrv, ch=1 )    


    
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
            grpList.append(prnt)            
                        
            if prnt:
                cmds.parent( emGrp, prnt[0] )
    
    return grpList  #list of parent group nodes    
    
    
    
# select lipCorner vertex!!
def WideTight_crvBS():
    
    wtBaseCv = cmds.ls(sl=1)[0]
    wtBaseCrv = wtBaseCv.split(".")[0]
    createPntNull( [ wtBaseCrv ] )
    cvID = wtBaseCv.split("[")[1][:-1]
    numOfCv = int(cvID)-1
    maxDist = numOfCv/2.0 #
    prm = 1.0/44
    
    if wtBaseCrv:
        wCrv = cmds.duplicate( wtBaseCrv )[0]
        wideCrv = cmds.rename(wCrv, "cornerWide_crv")
        tCrv = cmds.duplicate( wtBaseCrv )[0]
        tightCrv =cmds.rename(wCrv, "cornertight_crv")
        first = [x+1 for x in range(numOfCv)]
        order = first + first[::-1]    
        
        for i, time in enumerate(order):
            cvIndex = i+2  
            #loc = cmds.spaceLocator( n = 'wtLoc'+ str(cvIndex) )      
            distance = prm*maxDist*((1.0/numOfCv))#몇개의 section만큼 wide or narrow 움직일지
            wtBaseCrvShp = cmds.listRelatives( wtBaseCrv, c=1, typ = "nurbsCurve")[0]
            poc = cmds.shadingNode( 'pointOnCurveInfo', asUtility =1, n = 'wtPoc'+ str(cvIndex))
            cmds.connectAttr( wtBaseCrvShp + ".worldSpace", poc + ".inputCurve")
            cmds.setAttr( poc + ".parameter", prm*(i+1) - distance*time )        
            pocPos = cmds.getAttr( poc + ".position" )[0]
            print pocPos
            #cmds.connectAttr( poc + ".position", loc[0] + ".t" )
            
            cmds.xform( tightCrv + ".cv[%s]"%cvIndex, ws=1, t = pocPos )
            
            cmds.setAttr( poc + ".parameter", prm*(i+1) + distance*time )
            widePos = cmds.getAttr( poc + ".position" )[0] 
            cmds.xform( wideCrv + ".cv[%s]"%cvIndex, ws=1, t = widePos )
        
        cmds.select( wideCrv, r=1)
        symmetrizeLipCrv(1)
        cmds.select( tightCrv, r=1)
        symmetrizeLipCrv(1)
        cmds.blendShape( tightCrv, wideCrv , wtBaseCrv, n = "wtCrv_BS" )





# curve should have center cv[ 0, y, z]
def symmetrizeLipCrv(direction):
    
    crvSel = cmds.ls(sl=1, long=1, type= "transform")
    crvShp = cmds.listRelatives(crvSel[0], c=1, ni=1, s=1)
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
                            
                print leftNum, rightNum    
                if direction == 1:
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




    
# select wire/sphere and head_base in order
# set the jaw_drop pose ( for "jaw_drop" duplicate )
# select wire, and head_REN( base )
def lipWire_setup():
    # select lipDrop_wireCrv and headBase 
    # create or add blendShape with targets that are deformed by each wire
    myHead = cmds.ls("head_REN")
    if len(myHead) >1:
        cmds.confirmDialog( title='Confirm', message='more than one "head_REN" exist' )
        
    else:
        mySel = cmds.ls( os=1, typ = "transform" )
        if not len(mySel) >= 2:
            cmds.confirmDialog( title='Confirm', message='select wire_crv(s) and head_base in order!!' )
            
        else:
            '''mySelShapes = cmds.listRelatives( mySel, c=1, ni=1, s=1 )        
            wireShape = [ w for w in mySelShapes if cmds.nodeType( w ) == "nurbsCurve" ]
            wireCrv = cmds.listRelatives( wireShape, p =1 )'''
            wtCrv = ""
            shapeCrv = ""
            for crv in mySel:
                history = cmds.listHistory(crv, pruneDagObjects =1, interestLevel= 1 )
                deform = [ x for x in history if cmds.nodeType( x ) == "blendShape"]
                if deform:
                    if "bakeBS" in deform[0]:
                        shapeCrv = crv
                        shapeCrvBS = deform[0]
                    elif "wtCrv_BS" in deform[0]:        
                        wtCrv = crv
            
            headBase = mySel[-1]
            headBBox = cmds.exactWorldBoundingBox( headBase )
            headBaseShape = cmds.listRelatives(headBase, c=1 )[0]    
            if cmds.objExists("baseHead_temp"):
                defaultHead = "baseHead_temp"
            else:
                defaultHead = copyOrigMesh( headBase, "baseHead_temp" )
            
            if  cmds.nodeType(headBaseShape) == "mesh" :           
                
                wireHeads = { wtCrv : ["cornerWide_head", "cornerTight_head"], shapeCrv:[ "shape_head", "shapeExra_head" ] }
                if shapeCrv:
                    shpWireGrp = cmds.group( em=1, n= "jawDropWire_Grp" )
                    # zero out jawDrop blendShape target weights
                    aliasAtt = cmds.aliasAttr( shapeCrvBS, q=1)
                    for tgt, wgt in zip( *[iter( aliasAtt )]*2 ):
                        cmds.setAttr( shapeCrvBS + "." + tgt, 0 )                     
                     
                    jawDrop = cmds.duplicate( headBase, rc=1, n = "jawDrop_geo" )[0]
                    deleteOrigShapes( [jawDrop] )
                    
                    crvTgtGrp = shapeCrv + "_tgtGrp"
                    if cmds.objExists(crvTgtGrp):
                        cmds.parent( shapeCrv, jawDrop, crvTgtGrp, shpWireGrp )
                    else:
                        cmds.parent( shapeCrv, jawDrop, shpWireGrp )                        
                    
                    jawDropMinus = cmds.duplicate( jawDrop, rc =1, n = "jawDrop_minus" )[0] 
                    cmds.hide( jawDropMinus )
                    
                    shapeList = wireHeads[shapeCrv] 
                    for head in shapeList:
                        dup = cmds.duplicate( jawDrop, rc =1, n = head )[0]
                        name = head.split("_")[0] + "_wire"
                        wireDform = cmds.wire( dup, w = shapeCrv, n = name )
                        cmds.setAttr( wireDform[0] + ".rotation", 0 )       
                        cmds.hide( dup )
                    
                    #create blendShape for jawDrop            
                    shpBS = cmds.blendShape( shapeList, jawDrop, n = "jawDrop_headBS" )
                    cmds.setAttr( shpWireGrp + ".ty", -( headBBox[4] - headBBox[1]) )               
                
                if wtCrv:
                    wtWireGrp = cmds.group( em=1, n= "baseHeadWire_Grp" )
                    cornerTgtGrp = wtCrv + "P"
                    if cmds.objExists(cornerTgtGrp):
                        cmds.parent( wtCrv, defaultHead, cornerTgtGrp, wtWireGrp )
                    else:
                        cmds.parent( wtCrv, defaultHead, wtWireGrp )
                        
                    shapeList = wireHeads[wtCrv]
                    
                    for head in shapeList:
                        dup = cmds.duplicate( defaultHead, rc =1, n = head )[0]
                        name = head.split("_")[0] + "_wire"
                        wireDform = cmds.wire( dup, w = wtCrv, n = name )
                        cmds.setAttr( wireDform[0] + ".rotation", 0 )                    
                        cmds.hide(dup)                    
                                     
                    wtBS = cmds.blendShape( shapeList, defaultHead, n = "weightShaper_headBS" )                
                    
                #combine blendShape altogether
                prnt = cmds.listRelatives( headBase, ap =1 )
                cmds.hide(prnt)
                
                if cmds.objExists("jawDrop_headBS") and cmds.objExists("weightShaper_headBS"):
                    
                    alias = cmds.aliasAttr("weightShaper_headBS", q=1 )
                    jawDropList = [ jawDrop, jawDropMinus ]
                    for i, target in enumerate(jawDropList):                
                        cmds.blendShape( "weightShaper_headBS", e=1, t = [defaultHead, len(alias)/2 + i, target, 1 ] )
                    cmds.hide(wireHeads[wtCrv])

                elif cmds.objExists("jawDrop_headBS") and not cmds.objExists("weightShaper_headBS") :
                    
                    cmds.blendShape( jawDrop, jawDropMinus, defaultHead, n = "weightShaper_headBS" )
                        

def cheekSculpt_func( bsNode ):
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
def browWire_setup():

    mySel = cmds.ls( os=1, l=1, typ = "transform")
    headBase = mySel[-1] #name head_orig
    browWireCrv = mySel[0]
    #check if headBase is mesh  
    if not cmds.nodeType( cmds.listRelatives(headBase, pa=1, c=1)[0]) == "mesh":
        print "select browWireCrv and head_base geo in order!!"
        
    else:
        
        browWireHeads = ["browUpWire_head", "browDownWire_head", "browExra_head"]
        for head in browWireHeads:
            browDup = cmds.duplicate( headBase, rc =1, n = head )[0]
            deleteOrigShapes([browDup])
            wireDform = cmds.wire( browDup, w = browWireCrv, n = head.split("_")[0] )
            cmds.setAttr( wireDform[0] + ".dropoffDistance[0]", 5 )
            cmds.setAttr( wireDform[0] + ".rotation", 0 )        
    
        cmds.blendShape( browWireHeads, headBase, n = "browWire_headBS" )
        prnt = cmds.group( em=True, name= browWireCrv + "_grp" )
        cmds.parent( browWireCrv, prnt )
        cmds.parent( browWireHeads, prnt )
        cmds.hide( browWireHeads )

        
#implementation later        
def performWireDeformer(shape, deformCurves, baseCurves):
    count = len(deformCurves)
    wireDef = cmds.wire(shape, wc= count)[0]
    print wireDef
    for i in range(count):
        print deformCurves[i], baseCurves[i]  
        cmds.connectAttr('%s.worldSpace[0]' % deformCurves[i], '%s.deformedWire[%s]' % (wireDef, i)) 
        cmds.connectAttr('%s.worldSpace[0]' % baseCurves[i], '%s.baseWire[%s]' % (wireDef, i)) 
    cmds.setAttr('%s.rotation' % wireDef, 0)
    

#select target and base to propagate the fix
'''
1. duplicate the target and add it to blendShape as "new_"+target
2. fix the shape and set old target -1 ( create gap between old and new target )
'''

def propagateFix_setup( target, base ):
    
    future = cmds.listHistory( target, f =1, lv = 1 )
    BSnode = [ x for x in future if cmds.nodeType( x ) == "blendShape" ][0] # first blendShape node generally    
    newTgt = cmds.duplicate( target, rc =1, n = "new_"+target )[0]
    unlockedAttr = cmds.listAttr( newTgt, k=1, unlocked=1 )
    axis = ['X', 'Y', 'Z'] 
    attrs = ['translate', 'rotate', 'scale'] 
    for ax in axis:
        for attr in attrs:
            if not attr+ax in unlockedAttr:                
                cmds.setAttr(newTgt+'.'+attr+ax, lock=0)
    
    cmds.setAttr( newTgt + ".t", 0,0,0)

    aliasAtt = cmds.aliasAttr(BSnode, q=1)
    maxNum = []
    for tgt, wgt in zip( *[iter( aliasAtt )]*2 ):
        cmds.setAttr( BSnode + "." + tgt, 0 )       
        num = wgt.split("[")[1][:-1]
        maxNum.append(int(num))
        
    #add corrective crvs in BlendShape    
    maxNum = max(maxNum) 
                
    targetID = maxNum + 1
    cmds.blendShape( BSnode, e=1, t = [base, targetID, newTgt, 1 ] )
    cmds.setAttr( BSnode + "." + newTgt, 1 )
    cmds.setAttr( BSnode + "." + target, 0 )
    cmds.hide( target )
    

#select fixed target and old target when the fix done
#zero out all other targets/ set newTarget 1 and oldTarget -1
def propagateGap( newTarget, oldTarget ):
    
    oldFuture = cmds.listHistory( oldTarget, f =1, lv = 1 )
    newFuture = cmds.listHistory( newTarget, f =1, lv = 1 )
    BSnode = [ x for x in oldFuture if cmds.nodeType( x ) == "blendShape" ]
    newBS = [ x for x in newFuture if cmds.nodeType( x ) == "blendShape" ]
    if BSnode:

        future = cmds.listHistory( BSnode[0], f=1 )
        baseShape = [ x for x in future if cmds.nodeType(x) == "mesh"]
        base = cmds.listRelatives( baseShape[0], p =1 )
        aliasBS = cmds.aliasAttr( BSnode[0], q=1 )
        print newBS, BSnode
        if not newBS[0] == BSnode[0]:
            maxNum = len(aliasBS)/2          
            targetID = maxNum + 1
            print base[0], newTarget
            cmds.blendShape( BSnode[0], e=1, t = [base[0], targetID, newTarget, 1 ] )   

        for tgt, wgt in zip( *[iter( aliasBS )]*2 ):
            cmds.setAttr( BSnode[0] + "." + tgt, 0 )


        cmds.setAttr( BSnode[0] + "." + oldTarget, -1 )
        cmds.setAttr( BSnode[0] + "." + newTarget, 1 )   
                     
        baseShape = cmds.blendShape( BSnode[0], q=1, geometry=1 )[0] #return shape
        base = cmds.listRelatives( baseShape, p=1 )[0]
        fixGap = cmds.duplicate( base, rc =1, n = oldTarget + "_fixGap" )[0]
        
        maxNum = len(aliasBS)/2          
        targetID = maxNum + 1
        cmds.blendShape( BSnode[0], e=1, t = [base, targetID, fixGap, 1 ] )
        cmds.setAttr( BSnode[0] + "." + oldTarget, 0 )
        cmds.setAttr( BSnode[0] + "." + newTarget, 0 ) 
        cmds.hide( fixGap )
    
    else:
        cmds.confirmDialog( title='Confirm', message='select oldTarget with blendShape' )