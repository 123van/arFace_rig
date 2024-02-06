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
        splitSkin =cmds.skinCluster( lWgtJnt, rWgtJnt, splitGeo[0], toSelectedBones=True, n = "splitSkin" )
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
#either create correctiveShape("happy", "sad", "E”...) or reconnect target shape("Sh", "M", "sneer"...)
def fixTwitchTarget():
    correctives =["happy", "sad", "E","U","O","wide", "squint", "annoy", "furrow", "relax", "browSad", "browMad" ]
    tgList = [ "Sh", "M", "sneer", "flare", "puff", "suck" ]
    
    correctiveGrp = "correctiveGrp"
    aliasAtt = cmds.aliasAttr("twitchBS", q=1)
    targetAim = cmds.ls(sl=1, type = "transform" )
    targets = []
    IDs = []
    for tgt, wgt in zip(*[iter(aliasAtt)]*2):
        if tgt[:2] not in ["l_", "r_", "c_"]:
            cmds.setAttr( "twitchBS.%s"%tgt, 0 )
        
        tgWgt = cmds.getAttr("twitchBS."+tgt )            
        if tgWgt == 1:# if ctrl value == 1
            if tgt[2:] in correctives+tgList:
                targets.append(tgt)
                id = wgt.split("[")[1][:-1]
                IDs.append(id)
        
    if len(targets) == 2:
        target = targets[0][2:]
        targetID = int(min(IDs))-1
   
        if target in correctives:
            worldMesh = cmds.listConnections( 'twitchBS.it[0].itg[%s].iti[6000].inputGeomTarget'%targetID, s=1, d=0 )
            if worldMesh:
                cmds.confirmDialog( title='Confirm', message= " twitchBS.%s already has connection from %s .worldMesh"%(target, worldMesh[0]) )                
                
            else:
                cmds.setAttr( "twitchBS.%s"%target, 1 )
                cmds.sculptTarget("twitchBS", e=1, target = targetID )
                headGeo = cmds.getAttr("helpPanel_grp.headGeo")
                cmds.select( targetAim[0], headGeo )
                mel.eval("copyShape" )
                cmds.parent(targetAim[0], correctiveGrp )
                cmds.setAttr( "twitchBS.%s"%target, 0 )
                comp = cmds.getAttr('twitchBS.it[0].itg[%s].iti[6000].inputComponentsTarget'%targetID )             
                delta = cmds.getAttr('twitchBS.it[0].itg[%s].iti[6000].inputPointsTarget'%targetID )
                cmds.setAttr('twitchBS.it[0].itg[%s].iti[6000].inputComponentsTarget'%(targetID+1), len(comp), *comp, type="componentList" )
                cmds.setAttr('twitchBS.it[0].itg[%s].iti[6000].inputPointsTarget'%(targetID+1), len(delta), *delta, type="pointArray" )
                cmds.setAttr('twitchBS.it[0].itg[%s].iti[6000].inputComponentsTarget'%(targetID+2), len(comp), *comp, type="componentList" )
                cmds.setAttr('twitchBS.it[0].itg[%s].iti[6000].inputPointsTarget'%(targetID+2), len(delta), *delta, type="pointArray" )            

        elif target in tgList:

            tgShape= cmds.listRelatives( targetAim[0], c=1, ni=1, s=1)
            print targetID
            cmds.connectAttr(tgShape[0]+".worldMesh", 'twitchBS.it[0].itg[%s].iti[6000].inputGeomTarget'%targetID )
            cmds.connectAttr(tgShape[0]+".worldMesh", 'twitchBS.it[0].itg[%s].iti[6000].inputGeomTarget'%(targetID+1) )
            cmds.connectAttr(tgShape[0]+".worldMesh", 'twitchBS.it[0].itg[%s].iti[6000].inputGeomTarget'%(targetID+2) )
            if not cmds.listRelatives( targetAim[0], p=1)=="correctiveGrp":
                cmds.parent( targetAim[0], correctiveGrp )
                
    else:
        print "no target(or too many targets) is activated. set the ctrls 1 for the pose!"
    

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
#웨이트를 업데이트(set blendShape target weight 1 )하거나, 추가적인 타겟쉐입(select mesh)을 애드한다
'''
A.타겟이 메쉬일때:
 이름이 기존 타겟에 없으면 Add

B.타겟이 컨트롤러(nurbsCurve)일때
 update target weight
'''
def updateWeight_AddTarget( splitRange ):

    baseGeo =cmds.getAttr("helpPanel_grp.headGeo")
    targetSel = cmds.ls(sl=1, type = "transform")
    shapes = cmds.listRelatives( targetSel, c=1, ni=1, s=1 )
    vtxLen= cmds.polyEvaluate( baseGeo, v=1 )
    twitchBS = "twitchBS"
    alias = cmds.aliasAttr( twitchBS, q=1 )
    
    targetList =set()
    for tgt, wgt in zip(*[iter(alias)]*2):
        if tgt[:2] in ["l_", "r_"]:
            tgt = tgt[2:]
                    
        targetList.add(tgt)
    
    if splitRange == "ear":
        lWgt = cmds.getAttr( "splitMapBS.inputTarget[0].inputTargetGroup[0].targetWeights[0:%s]"%( vtxLen-1))
        rWgt = cmds.getAttr( "splitMapBS.inputTarget[0].inputTargetGroup[1].targetWeights[0:%s]"%( vtxLen-1))
    elif splitRange == "mouth":
        lWgt = cmds.getAttr( "splitMapBS.inputTarget[0].inputTargetGroup[2].targetWeights[0:%s]"%( vtxLen-1))
        rWgt = cmds.getAttr( "splitMapBS.inputTarget[0].inputTargetGroup[3].targetWeights[0:%s]"%( vtxLen-1))        
    elif splitRange == "nose":
        lWgt = cmds.getAttr( "splitMapBS.inputTarget[0].inputTargetGroup[4].targetWeights[0:%s]"%( vtxLen-1))
        rWgt = cmds.getAttr( "splitMapBS.inputTarget[0].inputTargetGroup[5].targetWeights[0:%s]"%( vtxLen-1))     
    
    #add selected target to blendShape  
    if cmds.nodeType(shapes[0])=="mesh":
        if targetSel[0] in targetList:
            print "it is one of the twitch targets, do fixTwitchTarget!!"
            
        else:
            target = targetSel[0]
            targetID = len(alias)/2
            
            cmds.blendShape( twitchBS, e=1, t = [baseGeo, targetID, target, 1 ] )
            cmds.blendShape( twitchBS, e=1, t = [baseGeo, targetID+1, target, 1 ] )
            cmds.blendShape( twitchBS, e=1, t = [baseGeo, targetID+2, target, 1 ] )    
            
            cmds.setAttr( twitchBS+ ".inputTarget[0].inputTargetGroup[%s].targetWeights[0:%s]"%( targetID+1, vtxLen-1), *lWgt )
            cmds.aliasAttr( "l_"+ targetSel[0], twitchBS+".w[%s]"%( targetID+1 ) ) 
            cmds.setAttr( twitchBS+ ".inputTarget[0].inputTargetGroup[%s].targetWeights[0:%s]"%( targetID+2, vtxLen-1), *rWgt ) 
            cmds.aliasAttr( "r_"+ targetSel[0], twitchBS+".w[%s]"%( targetID+2 ) )
            
            if not cmds.listRelatives( target, p=1)=="correctiveGrp":
                cmds.parent( target,  "correctiveGrp" )
            print target + " L/R target is added"
        

    
    #if twitch ctrls selected, update the weight on the activated "l_"/"r_" targets
    else:
        targets = []
        IDs = []
        #find out the targets with weight 1
        for tgt, wgt in zip(*[iter(alias)]*2):
            tgWgt = cmds.getAttr("twitchBS."+tgt )            
            if tgWgt == 1:
                targets.append(tgt)
                id = wgt.split("[")[1][:-1]
                IDs.append(id)

        if len(twitchTG) == 2: 
        
            cmds.setAttr( twitchBS+ ".inputTarget[0].inputTargetGroup[%s].targetWeights[0:%s]"%( int(IDs[0]), vtxLen-1), *lWgt )
            cmds.setAttr( twitchBS+ ".inputTarget[0].inputTargetGroup[%s].targetWeights[0:%s]"%( int(IDs[1]), vtxLen-1), *rWgt ) 
            print target + "'s weight is updated"

      

    

    
#before fix the target shape, set the target back to origShape
'''블렌쉐입에서 1로 activate 된 타겟을 읽고 그 타겟의 웨이트를 업데이트 한다.( brows up/down/in/out 은 직접 수정 with BSpiritCorrectiveShape;)
1. 수정할 타겟 블렌쉐입을 1로 놓기 위해 포즈를 잡고 실행하면 델타 데이터가 (0,0,0,1) 된다.
2. 오리지널 쉐입을 카피해서 타겟이름으로 바꾼다
3. 타겟 이름(happy)이 블렌쉐입 타겟과 같으면 카피한 쉐입을 블렌쉐입에 연결시켜준다.
'''
def resetForCorrectiveFix():

    cmds.select(cl=1) 
    
    alias = cmds.aliasAttr( "twitchBS", q=1 )
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
            cmds.connectAttr( targetReset[0]+".worldMesh[0]", "twitchBS.inputTarget[0].inputTargetGroup[%s].inputTargetItem[6000].inputGeomTarget"%targetID )
            cmds.connectAttr( targetReset[0]+".worldMesh[0]", "twitchBS.inputTarget[0].inputTargetGroup[%s].inputTargetItem[6000].inputGeomTarget"%(targetID+1) )
            cmds.connectAttr( targetReset[0]+".worldMesh[0]", "twitchBS.inputTarget[0].inputTargetGroup[%s].inputTargetItem[6000].inputGeomTarget"%(targetID+2) )
            cmds.delete( targetReset[0] )'''
            


                
#brow 타겟(코렉티브 쉐입이 아니다)을 하나씩 선택한 후 twitchPanel의 ctl들로 타겟과 근접한 포즈를 잡고 실행한다.[이름 중요 "browUp","browDown", "browIn","browOut"] 
#꼭 필요한 경우에만 만든다. 대부분 browIn/Out만 해도 충분.     
# posMax(10) : browJnt.rx -10일때 twitchBS.browUp reaches to max(1)    
# negMax(6) : browJnt.rx 6일때 twitchBS.browDown reaches to max(1)
# inMax(10) : furrow 와 다르다. l_browYJnt.ry -10/l_browYJnt.ry 10일때 twitchBS.browIn reaches to max(1)
# posMax(10): relax 와 다르다. l_browYJnt.ry 10/r_browYJnt.ry -10일때 twitchBS.browOut reaches to max(1)
def createBrowCorrective( posMax, negMax, inMax, outMax ):
    
    baseGeo ="head_REN"
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


    
    
    
            
# new name should be given
def copyOrigMesh( obj, name ):
    
    shapes = cmds.listRelatives( obj, ad=1, type='shape' )
    origShape = [ t for t in shapes if 'Orig' in t ]
    #get the orig shapes with history and delete the ones with with same name.
    myOrig = ''
    for orig in origShape:
        if cmds.listConnections( orig, s=0, d=1 ):
            myOrig = orig
        else: cmds.delete( orig )
    
    #unique origShape duplicated
    headTemp = cmds.duplicate( myOrig, n = name, renameChildren =1 )
    tempShape = cmds.listRelatives( headTemp[0], ad=1, type ='shape' )
 
    for ts in tempShape:
        if 'Orig' in ts:
            tempOrig = cmds.rename( ts, name+ 'Shape' )
        else:
            print "delete %s"%ts
            cmds.delete(ts)
    print tempOrig 
    cmds.setAttr( tempOrig+".intermediateObject", 0)
    cmds.sets ( tempOrig, e=1, forceElement = 'initialShadingGroup' )

    for trs in ['t','r','s']:
        for c in ['x','y','z']:
            if cmds.getAttr( headTemp[0] + '.' + trs + c, lock =1 ):
                cmds.setAttr(headTemp[0] + '.' + trs + c, lock =0 )
    return headTemp[0]
    
    

    
    
    
 
 
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


#pose to set two curve blenadShape to max
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
    headTemp = cmds.ls(sl=1)
    if cmds.objExists('mix'): cmds.delete('mix')
    newTarget = cmds.duplicate( headTemp[0], n = 'mix')
    child = [ c for c in cmds.listRelatives(newTarget[0], c =1 ) if 'Orig' in c ]
    cmds.delete( child )
    if cmds.objExists ('originGeo'): cmds.delete('originGeo')
    origMesh = getOrigMesh( headTemp[0])[0]
    if 'Orig' in origMesh:
        cmds.setAttr( origMesh +".intermediateObject", 0 )
        cmds.duplicate ( origMesh, n= 'originGeo' )
        origChild = cmds.listRelatives('originGeo', c=1)   
        cmds.sets (origChild[-1], e=1, forceElement = 'initialShadingGroup' )
        shape = origChild[0]
        cmds.delete(shape)
        cmds.rename( origChild[-1], shape )
        cmds.setAttr( origMesh +".intermediateObject", 1 )
   	 
        cmds.blendShape( 'mix', headTemp[1], 'originGeo', tc=0, n= 'tempBS' )
        cmds.blendShape( 'tempBS', e=1, w=[(0, 1.0), (1, -1.0)] )
        cmds.duplicate ( 'originGeo', n = 'minus')
        cmds.blendShape( 'tempBS', edit=1, t=( 'originGeo', 2, 'minus', 1.0) )
        cmds.delete('minus')
        cmds.blendShape ('tempBS', edit=1,  w = [ (0, 1.0),(1, 0.0),(2, -1.0)] )
        objBbox = cmds.xform ('originGeo', q =1, boundingBox =1 )
        if cmds.getAttr('originGeo.tx', lock=1) == True:
            cmds.setAttr('originGeo.tx', lock=0)
        cmds.setAttr('originGeo.tx', objBbox[3]-objBbox[0])
        cmds.select ( 'originGeo', 'mix', r=1)  
        
        activePanel = cmds.getPanel( withFocus=True )#return the name of the panel that currently has focus
        panelType = cmds.getPanel( typeOf =activePanel)#return the type of the specified panel
        if panelType == 'modelPanel':
            state = cmds.isolateSelect( activePanel, q=1, s=1)
            if state == 0:
                mel.eval('enableIsolateSelect %s 1' % activePanel)
            else:
                mel.eval('enableIsolateSelect %s 0' % activePanel)
                mel.eval('enableIsolateSelect %s 1' % activePanel)
           	 
    else :
        print 'check the original shape(ShapeOrig)!!'
 
 
 
 
 
# return intermediate shape and delete the one that is not connected
# if multiple intermediate shapes, list order should be bottom to up
def getOrigMesh( obj ):
    #get the shapes of child
    shapes = cmds.listRelatives(obj, s=1)
    #get intermediate shapes 
    intermediateObj = [ x for x in shapes if cmds.getAttr(x + ".intermediateObject") == 1 ]
    origShape = []
    for orig in intermediateObj:
        #if nothing is connected to the shape node, delete it
        connections = cmds.listConnections(orig)
        if connections:
            origShape.append(orig)            
            
        else:
            cmds.delete(orig)
    
    return origShape





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
def targetAdd_Reconnect( BSorder ):
    
    meshSel = cmds.ls(sl=1, typ ='transform')
    base = meshSel[-1]  
    tgtList = meshSel[:-1] 
    BSnode = [ n for n in cmds.listHistory(base, historyAttr=1 ) if cmds.nodeType(n) == "blendShape" ][BSorder-1]
    print BSnode
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
            maxNum = len(aliasAtt)/2          
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

    else:
        print "create blendShape first" 

    dnTarget = []
    for tgt, wgt in zip(*[iter(aliasAtt)]*2):
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
    print multList, numTgt
    comp = [0]
    for i in range( numTgt ):
        # browLength of comp is different for each target because the vertexs that has none movement don't counts
        comp = cmds.getAttr(crvBS[0]+ '.inputTarget[0].inputTargetGroup[%s].inputTargetItem[6000].inputComponentsTarget'%str(i) )
        delta = cmds.getAttr(crvBS[0]+ '.inputTarget[0].inputTargetGroup[%s].inputTargetItem[6000].inputPointsTarget'%str(i) )
        newDelta = []

        if delta:
            for dt in delta:
                xyz = ( dt[0]*multList[0], dt[1]*multList[1] , dt[2]*multList[2], dt[3])
                newDelta.append(xyz)
     
            cmds.setAttr(newBS[0]+'.inputTarget[0].inputTargetGroup[%s].inputTargetItem[6000].inputComponentsTarget'%str(i), len(comp), *comp, type="componentList" )
            cmds.setAttr(newBS[0]+'.inputTarget[0].inputTargetGroup[%s].inputTargetItem[6000].inputPointsTarget'%str(i), len(newDelta), *newDelta, type="pointArray" )
        else:
            print dnTarget[i] + " delta has none "


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






# select sourceCurve and targetCurve # create target curves
def plugCrvBS():
    
    crvSel = cmds.ls(os=1)
    sourceCrv = crvSel[0]
    targetCrv = crvSel[1]
    shapes = cmds.listRelatives( sourceCrv, ad=1, type='shape' )
    origCrv = [ t for t in shapes if 'Orig' in t ]
    #get the orig shapes with history and delete the ones with with same name.
    myOrig = ''
    for orig in origCrv:
        if cmds.listConnections( orig, s=0, d=1 ):
            myOrig = orig
        else: cmds.delete(orig)
    
    targetCrvShp = cmds.listRelatives( crvSel[1], c=1, ni=1, type='shape' )[0]    
    cmds.connectAttr( targetCrvShp +".worldSpace", myOrig + ".create", f=1 )
    
    crvBS = [ n for n in cmds.listHistory(crvSel[0], historyAttr=1 ) if cmds.nodeType(n) == "blendShape" ]    
    if crvBS:
        aliasAtt = cmds.aliasAttr(crvBS[0], q=1)
        
    else:
        print "select the curve with blendShape" 
    
    browTgt = []
    for tgt, wgt in zip(*[iter(aliasAtt)]*2):
        print tgt, wgt
        cmds.setAttr( crvBS[0] + "." + tgt, 1 )
        browCopyCrv = cmds.duplicate ( sourceCrv, n= tgt )[0]    
        browTgt.append(browCopyCrv)
        cmds.xform(browCopyCrv, ws=1, t = (0,0,0), ro=(0,0,0), s=(1, 1, 1) )
        cmds.setAttr( crvBS[0] + "." + tgt, 0 )
    
    cmds.select(browTgt, r=1)
    cmds.select(targetCrv, add=1 )   
    newBS = cmds.blendShape ( n ='browBS')
    cmds.delete(sourceCrv)



    
#create targets after copy blendShape delta        
#select curve with blendShape(clean, no connections)
#copy target and reconnect for blendShape
def bakeTarget_reconnect(baseCrv):

    dformers = cmds.listHistory(baseCrv, pruneDagObjects =1, interestLevel= 1 )
    crvBS = [ n for n in dformers if cmds.nodeType(n) == "blendShape" ]    
    if crvBS:
        aliasAtt = cmds.aliasAttr(crvBS[0], q=1)
        dformers.remove(crvBS[0])
        for df in dformers:
            cmds.setAttr( df + ".envelope", 0 )            
        
    else:
        print "select the curve with blendShape"

    for tgt, wgt in zip(*[iter(aliasAtt)]*2):
        cmds.setAttr( crvBS[0] + "."+ tgt, 0 )
    
    targetGrp = cmds.group( em=1, n = baseCrv + "_tgtGrp")
    crvTgt = []
    for tgt, wgt in zip(*[iter(aliasAtt)]*2):
        
        # check if target curve exists
        if cmds.objExists(tgt):
            cmds.confirmDialog( title='Confirm', message='%s target exists already'%tgt )
            
        else:
            cmds.setAttr( crvBS[0] + "."+ tgt, 1 )
            copyCrv = cmds.duplicate ( baseCrv, rc=1, n= tgt )[0]
            crvTgt.append(copyCrv)
            tgtID= wgt.split("[")[1][:-1]
            cmds.connectAttr( copyCrv+".worldSpace", crvBS[0]+ ".inputTarget[0].inputTargetGroup[%s].inputTargetItem[6000].inputGeomTarget"%str(tgtID) )
            cmds.setAttr( crvBS[0] + "."+ tgt, 0 )
            cmds.parent( tgt, targetGrp )
            
            
            
            


# set ctrls 1 / select corrective and base 
def addCrv_corrective(crvs ):

    base = crvs[-1]
    BSnode = [ n for n in cmds.listHistory(base, historyAttr=1 ) if cmds.nodeType(n) == "blendShape" ]  
    if BSnode:
        aliasAtt = cmds.aliasAttr(BSnode[0], q=1)        
    else:
        print "select the object with blendShape"  
    target = crvs[0]
    names = target.split("_")

    if "l_" in target:            
        fixMult = cmds.shadingNode( "multiplyDivide", asUtility =1, n = names[1]+names[2]+"_mult" )
        rUpCrv = cmds.duplicate( target, rc =1, n = target.replace("l_","r_") )[0]
        if "lip" in BSnode[0].lower():
            print BSnode[0]
            mirrorCurve( target, rUpCrv )
        elif "brow" in BSnode[0].lower():
            LRBlendShapeWeight( base, BSnode[0] )          
            
        cmds.hide(rUpCrv)
        
        maxNum = []
        for x, y in zip(*[iter(aliasAtt)]*2):
            num = y.split("[")[1][:-1]
            maxNum.append(int(num))
            
        #add corrective crvs in BlendShape    
        maxNum = max(maxNum)            
        cmds.blendShape( BSnode[0], e=1, t = [base, maxNum + 1, target, 1 ] )
        cmds.blendShape( BSnode[0], e=1, t = [base, maxNum + 2, rUpCrv, 1 ] )
        srcList = []
        for tgt, wgt in zip(*[iter(aliasAtt)]*2):                
            if cmds.getAttr( BSnode[0] + "." + tgt )==1:
                srcList.append(tgt)     
        print srcList
        if srcList:
            cmds.connectAttr( BSnode[0] + "."+srcList[0], fixMult + ".input1X")
            cmds.connectAttr( BSnode[0] + "."+srcList[1], fixMult + ".input1Z")
            
            cmds.connectAttr( BSnode[0] + "."+srcList[2], fixMult + ".input2X")
            cmds.connectAttr( BSnode[0] + "."+srcList[3], fixMult + ".input2Z")
                    
            print BSnode[0]
            cmds.connectAttr( fixMult + ".outputX", BSnode[0]+".%s"%target ) 
            cmds.connectAttr( fixMult + ".outputZ", BSnode[0]+".%s"%rUpCrv ) 
            
        else:
            cmds.confirmDialog( title='Confirm', message='set ctrl to 1 to get blendShape target' )   





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
                    
                        

def createPntNull( mySelList ):
    
    mySelList =cmds.ls(sl=1)       
    grpList =[]
    for nd in mySelList:
        
        pos = cmds.xform(nd, q=1, ws=1, rotatePivot=1 ) 
        
        if cmds.nodeType(nd) =="transform":
            topGrp = cmds.duplicate( nd, po=1, n=nd+"P" )
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
    
    return grpList  
    
# select wire/sphere and head_base in order
# set the jaw_drop pose ( for "jaw_drop" duplicate )
# select wire, and head_REN( base )
def lipWire_scult_setup():
    # select lipDrop_wireCrv and headBase 
    # create or add blendShape with targets that are deformed by each wire 
    mySel = cmds.ls( os=1, typ = "transform" )
    if not len(mySel) >= 3:
        cmds.confirmDialog( title='Confirm', message='select wires, sculpt_sphere and head_base in order!!' )
        
    else:
        mySelShapes = cmds.listRelatives( mySel, c=1, ni=1, s=1 )        
        wireShape = [ w for w in mySelShapes if cmds.nodeType( w ) == "nurbsCurve" ]
        wireCrv = cmds.listRelatives( wireShape, p =1 )
        print wireCrv
        sculptSphere = mySel[-2]
        headBase = mySel[-1]
        headBaseShape = cmds.listRelatives(headBase, c=1 )[0]
        
        if  cmds.nodeType(headBaseShape) == "mesh" :
            jawDrop = cmds.duplicate( headBase, rc=1, n = "jaw_drop")[0]
            deleteOrigShapes( [jawDrop] )
            emGrp = cmds.group( em=1, n= "lipWire_shape_Grp" )
            geoGrp = cmds.group( em=1, n= "jawDrop_shape_Grp" )
            cmds.parent( mySel[:-1], emGrp )
            cmds.parent( jawDrop, geoGrp )            

            cmds.select( sculptSphere, r=1 )
            cmds.makeIdentity(apply=True, t=1, r=1, s=0, n=0 )
            
            wireHeads = ["lipWide_head", "lipTight_head", "lipExra_head", "cheek_head", "jawDrop_minus" ]
            for head in wireHeads:
                dup = cmds.duplicate( jawDrop, rc =1, n = head )[0]
                deleteOrigShapes([dup])
                
                if not head == "jawDrop_minus":
                    if head == "cheek_head":
                        name = head.split("_")[0] + "_sculpt"
                        sculptDform = cmds.sculpt( sculptSphere, mode='flip', insideMode='even', objectCentered=1, n= name )
                        prnt = createPntNull( sculptDform[1] )
                        cmds.parent( sculptDform[2], prnt[0] )
                        cmds.sculpt( sculptDform[0], e=1, g= "cheek_head" )
                        cmds.delete(sculptSphere)
                    else:                
                        name = head.split("_")[0] + "_wire"
                        wireDform = cmds.wire( dup, w = wireCrv, n = name )
                        #cmds.setAttr( wireDform[0] + ".dropoffDistance[0]", 1 )
                        cmds.setAttr( wireDform[0] + ".rotation", 0 )
        else:
            cmds.confirmDialog( title='Confirm', message='select wire, sculpt_sphere and head_base in order!!' )
            
        cmds.blendShape( wireHeads[:-1], jawDrop, n = "jawDrop_headBS" )        
        '''
        baseBS = cmds.ls( cmds.listHistory( headBase ), type = "blendShape" )
        if baseBS:
            cmds.select( [ jawDrop, wireHeads[-1] ])
            cmds.select( headBase, add=1 )
            blendShapeMethods.targetAdd_Reconnect( 1 )
            
        else:'''    
        cmds.blendShape( [ jawDrop, wireHeads[-1] ], headBase, n = "weightShaper_headBS" )
        cmds.hide(wireHeads)
                        

                        
                        
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
    cmds.setAttr( newTgt + ".t", 0,0,0)

    aliasAtt = cmds.aliasAttr(BSnode, q=1)
    for tgt, wgt in zip( *[iter( aliasAtt )]*2 ):
        cmds.setAttr( BSnode + "." + tgt, 0 )       
        
    maxNum = len(aliasAtt)/2          
    targetID = maxNum + 1
    cmds.blendShape( BSnode, e=1, t = [base, targetID, newTgt, 1 ] )
    cmds.setAttr( BSnode + "." + newTgt, 1 )
    cmds.setAttr( BSnode + "." + target, 0 )
    cmds.hide( target )
    

# select fixed target and old target when the fix done 
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