# -*- coding: utf-8 -*-

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
    
        cmds.delete( splitSurfGeo[0] )   
    
    
    
    

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
    

    
    

       
    
#twitchBS 에 포함되어 있는 타겟만 연결된다. 나중에 타겟이 추가되면 다시 실행해서 연결한다.
def ctrlConnectBlendShape():    

    #curve blendShape connection
    if cmds.objExists("*LipCrvBS") & cmds.objExists("*browBS"):
        typeCList ={ "mouth_happysad":[["up_Happy", "lo_Happy"],["up_Sad", "lo_Sad"]] }

        for LR in ["l_","r_"]:
            # "B"type ctl setup
            if not cmds.listConnections( LR+ "brow_Furrow", s=0, d=1 ):
                BCDtypeCtrlSetup.BCtrlSetup( LR + "brow_Furrow", "y", LR+ "Furrow_crv" , LR+ "Relax_crv" )
            else:
                print "%s already have connections"%(LR+ "brow_Furrow")
            
            '''if not cmds.listConnections( LR+ "brow_madsad", s=0, d=1 ):
                BCDtypeCtrlSetup.CCtrlSetup( LR + "brow_madsad", LR, ["y","x"], [ LR+ "browSad" ], [  LR+ "browMad" ] )     
            else:
                print "%s already have connections"%(LR+ "brow_madsad" )       
            
            # "C"type ctl setup
            for C, cList in typeCList.iteritems():
            	if not cmds.listConnections( LR+ C, s=0, d=1 ):#if there is no connections to the ctl
            	    cListA = [ LR+ x for x in cList[0] ]
            	    cListB = [ LR+ x for x in cList[1] ]
            	    BCDtypeCtrlSetup.CCtrlSetup( LR+C, LR, ["y","x"], cListA, cListB )
                else:
                    print "%s already have connections"%( LR+C )'''
                    
            # phoneme "D" type ctrl setup
            if not cmds.listConnections( LR+ "phonemes_ctl", s=0, d=1 ):
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
            else:
                print "%s already have connections"%( LR + "phonemes_ctl" )
                                
    #mesh blendShape connection          
    if cmds.objExists("twitchBS"):

        typeAList ={ "sneer":"nose_sneer.ty", "flare":"nose_flare.ty" }
        typeBList ={ "brow_Furrow":["furrow", "relax"], "bridge_puffsuck":["puff", "suck"], "ShM":["Sh", "M"] }
        typeCList ={ "mouth_happysad":["happy", "sad", "up_Happy", "lo_Happy", "up_Sad", "lo_Sad"], "brow_madsad": ["browSad", "browMad", "browSad_crv", "browMad_crv"] }
        
        for LR in ["l_","r_"]:
            for A, attr in typeAList.iteritems():
                if not cmds.listConnections( "twitchBS." + LR+ A, s=1, d=0 ):
                    cmds.connectAttr( LR + attr, "twitchBS." + LR + A )
                else:
                    print "twitchBS.%s already has connections"%( LR+ A)    
         
            for B in typeBList:
                BCDtypeCtrlSetup.BCtrlSetup( LR + B, "y", LR+ typeBList[B][0], LR+ typeBList[B][1] )  
                    
            for C in typeCList:
                BCDtypeCtrlSetup.CCtrlSetup( LR+ C, LR, ["y","x"], [ LR+typeCList[C][0] ], [ LR+typeCList[C][1] ] )
    
            # phoneme "D" type ctrl setup 
            if cmds.listConnections( LR+ "phonemes_ctl", s=0, d=1 ):
                if not cmds.listConnections( "twitchBS." + LR+ "U", s=1, d=0 ):
                    cmds.connectAttr( "lipFactor."+LR+"phonemeXPos_YPos", "twitchBS." + LR+ "U" ) 
                
                if not cmds.listConnections( "twitchBS." + LR+ "E", s=1, d=0 ):
                    cmds.connectAttr( "lipFactor."+LR+"phonemeXNeg_YPos", "twitchBS." + LR+ "E" )                         

                if not cmds.listConnections( "twitchBS." + LR+ "O", s=1, d=0 ):
                    cmds.connectAttr( "lipFactor."+LR+"phonemeXPos_YNeg", "twitchBS." + LR+ "O" )                     

                if not cmds.listConnections( "twitchBS." + LR+ "wide", s=1, d=0 ):
                    cmds.connectAttr( "lipFactor."+LR+"phonemeXNeg_YNeg", "twitchBS." + LR+ "wide" ) 
            else:
                BCDtypeCtrlSetup.DCtrlSetup( LR + "phonemes_ctl", LR+"phoneme", "lip")
                cmds.connectAttr( "lipFactor."+LR+"phonemeXPos_YPos", "twitchBS." + LR+ "U" )                

                cmds.connectAttr( "lipFactor."+LR+"phonemeXNeg_YPos", "twitchBS." + LR+ "E" )                

                cmds.connectAttr( "lipFactor."+LR+"phonemeXPos_YNeg", "twitchBS." + LR+ "O" )                

                cmds.connectAttr( "lipFactor."+LR+"phonemeXNeg_YNeg", "twitchBS." + LR+ "wide" )  
           
                
                
                
#after createTwitchBS                
#ctrls(happy / sad, brow sad/mad, U,E,O,Wide) to blendShape curves                
'''
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
    
    aliasAtt = cmds.aliasAttr("twitchBS", q=1)
    targetAim = cmds.ls(sl=1, type = "transform" )
    targets = []
    IDs = []
    for tgt, wgt in zip(*[iter(aliasAtt)]*2):
        if tgt[:2] not in ["l_", "r_", "c_"]:
            cmds.setAttr( "twitchBS.%s"%tgt, 0 )
        
        tgWgt = cmds.getAttr("twitchBS."+tgt )            
        if tgWgt == 1:
            if tgt[2:] in correctives+tgList:
                targets.append(tgt)
                id = wgt.split("[")[1][:-1]
                IDs.append(id)
        
    if len(targets) == 2:
        target = targets[0][2:]
        targetID = int(min(IDs))-1
   
        if target in correctives:

            cmds.sculptTarget("twitchBS", e=1, target = targetID )
            headGeo = cmds.getAttr("helpPanel_grp.headGeo")
            cmds.select( targetAim[0], headGeo )
            mel.eval("copyShape" )
            cmds.delete(targetAim[0])
            #cmds.setAttr( "twitchBS.%s"%tg[0], 0 )
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
                cmds.parent( targetAim[0], "correctiveGrp" )
                
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
def updateAddTarget( splitRange ):
    targetList =["happy", "sad", "E","U","O","wide", "sneer", "flare", "puff", "suck", "squint", "annoy", "browSad", "browMad", "Sh", "M" ]
    baseGeo =cmds.getAttr("helpPanel_grp.headGeo")
    targetSel = cmds.ls(sl=1, type = "transform")
    shapes = cmds.listRelatives( targetSel, c=1, ni=1, s=1 )
    vtxLen= cmds.polyEvaluate( baseGeo, v=1 )
    twitchBS = "twitchBS"
    alias = cmds.aliasAttr( twitchBS, q=1 )
    
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
        ctl = cmds.listRelatives( targetSel[0], c =1 )[0]        
        if cmds.nodeType(ctl)=="nurbsCurve":
            targets = []
            IDs = []
            #find out the targets with weight 1
            for tgt, wgt in zip(*[iter(alias)]*2):
                tgWgt = cmds.getAttr("twitchBS."+tgt )            
                if tgWgt == 1:
                    targets.append(tgt)
                    id = wgt.split("[")[1][:-1]
                    IDs.append(id)
            twitchTG =[ t for t in targets if not "0" in t ]
            if len(twitchTG) == 2:
                target = twitchTG[0][2:]
                print target
                targetID = int(min(IDs))-1    
            
            cmds.setAttr( twitchBS+ ".inputTarget[0].inputTargetGroup[%s].targetWeights[0:%s]"%( int(targetID)+1, vtxLen-1), *lWgt )
            cmds.setAttr( twitchBS+ ".inputTarget[0].inputTargetGroup[%s].targetWeights[0:%s]"%( int(targetID)+2, vtxLen-1), *rWgt ) 
            print target + "'s weight is updated"
      

    

    
#before fix the target shape, set the target back to origShape
'''블렌쉐입에서 1로 activate 된 타겟을 읽고 그 타겟의 웨이트를 업데이트 한다.( brows up/down/in/out 은 직접 수정 with BSpiritCorrectiveShape;)
1. 수정할 타겟 블렌쉐입을 1로 놓기 위해 포즈를 잡고 실행하면 델타 데이터가 오리지널 쉐입으로 대체된다.
2. 오리지널 쉐입을 카피해서 타겟이름으로 바꾼다
3. 타겟 이름(happy)이 블렌쉐입 타겟과 같으면 카피한 쉐입을 블렌쉐입에 연결시켜준다.
4. 타겟 이름(happy)이 블렌쉐입 타겟(l_browUp01)에 포함되어 있으면 인스탄트로 카피해서 연결시켜준다.
'''
def resetForCorrectiveFix():
    targetList =["happy", "sad", "E","U","O","wide", "squint", "annoy", "furrow", "relax", "browSad", "browMad" ]
    baseGeo = 'head_REN'
    #target = cmds.ls(sl=1, type ="transform")
    #cmds.rename(target[0], target[0]+"_aim")
    
    if not cmds.objExists("origShape"):
        origTarget = copyOrigMesh( baseGeo, "origShape" )
    else:
        origTarget = "origShape"
    
    if not cmds.objExists("dumpAtMerge"):
        dumpGrp = cmds.group(em=1, p = "faceMain", n = "dumpAtMerge")        
    else:
        dumpGrp = "dumpAtMerge"
    cmds.select(cl=1) 
    
    alias = cmds.aliasAttr( "twitchBS", q=1 )
    targets = []
    IDs = []
    #find out the targets with weight 1
    for tgt, wgt in zip(*[iter(alias)]*2):        

        tgWgt = cmds.getAttr("twitchBS."+tgt )            
        if tgWgt == 1:
            if tgt[2:] in targetList:
                targets.append(tgt)
                id = wgt.split("[")[1][:-1]
                IDs.append(id)
    
    if len(targets) == 2:
        target = targets[0][2:]
        targetReset = cmds.duplicate( origTarget, n = target )
        targetID = int(min(IDs))-1        
                                     
        cmds.connectAttr( targetReset[0]+".worldMesh[0]", "twitchBS.inputTarget[0].inputTargetGroup[%s].inputTargetItem[6000].inputGeomTarget"%targetID )
        cmds.connectAttr( targetReset[0]+".worldMesh[0]", "twitchBS.inputTarget[0].inputTargetGroup[%s].inputTargetItem[6000].inputGeomTarget"%(targetID+1) )
        cmds.connectAttr( targetReset[0]+".worldMesh[0]", "twitchBS.inputTarget[0].inputTargetGroup[%s].inputTargetItem[6000].inputGeomTarget"%(targetID+2) )
        cmds.delete( targetReset[0] )
            


                
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
    num = 0
    for ts in tempShape:
        if 'Orig' in ts:
            tempOrig = cmds.rename( ts, name+ 'Shape' )
        else: cmds.delete(ts)
    print tempOrig 
    cmds.setAttr( tempOrig+".intermediateObject", 0)
    cmds.sets ( tempOrig, e=1, forceElement = 'initialShadingGroup' )
    
    for c in ['x','y','z']:
        if cmds.getAttr( headTemp[0] + '.t%s'%c, lock =1 ):
            cmds.setAttr(headTemp[0] + '.t%s'%c, lock =0 )
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

    eyeLidCrv = { "min_crv":[ "upMin_crv","loMin_crv" ], "max_crv":[ "upMax_crv","loMax_crv" ], "squint_crv":[ "upSquint_crv", "loSquint_crv" ], 
    "annoy_crv":[ "upAnnoy_crv", "loAnnoy_crv" ], "PushA_crv":[ "l_upLidPushA_crv", "l_loLidPushA_crv" ], "PushB_crv":[ "l_upLidPushB_crv", "l_loLidPushB_crv" ],
    "PushC_crv":[ "l_upLidPushC_crv", "l_loLidPushC_crv" ], "PushD_crv":[ "l_upLidPushD_crv", "l_loLidPushD_crv" ] }    
        
    for eV in eyeLidCrv:
        if crvTitle == eV:
            crvSel = eyeLidCrv[crvTitle]
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
    

    

def lipCrvIsolate( lipTitle ):

    lipCrv = { "jawOpen":["upJawOpen_crv","loJawOpen_crv"], "tyOpen":["upTyLip_crv","loTyLip_crv"], "happy_crv":["l_upHappy_crv","l_loHappy_crv","l_happyCheek_crv"],
    "sad_crv":["l_upSad_crv","l_loSad_crv","l_sadCheek_crv" ], "E_crv":["l_uplipE_crv","l_lolipE_crv","l_eCheek_crv" ], "wide_crv":["l_uplipWide_crv","l_lolipWide_crv","l_wideCheek_crv" ],
    "U_crv":["l_upU_crv","l_loU_crv","l_uCheek_crv" ], "O_crv":["l_upO_crv","l_loO_crv","l_oCheek_crv" ] }   

    for eV in lipCrv :
        if lipTitle == eV:
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

    browCrv = { "browSad":["lBrowSad_crv", "rBrowSad_crv"], "browMad":["lBrowMad_crv", "rBrowMad_crv"], "furrow":["lFurrow_crv", "rFurrow_crv"], "relax":["lRelax_crv", "rRelax_crv"] } 

    for eV in browCrv :
        if browTitle == eV:
            crvSel = browCrv[browTitle]

    cmds.select( crvSel )
    activePanel = cmds.getPanel( withFocus=True )#return the name of the panel that currently has focus
    panelType = cmds.getPanel( typeOf =activePanel)#return the type of the specified panel
    if panelType == 'modelPanel':
        state = cmds.isolateSelect( activePanel, q=1, s=1)
        if state == 0:
            mel.eval('enableIsolateSelect %s 1' % activePanel)
        else:
            mel.eval('enableIsolateSelect %s 0' % activePanel)    
    



#pose to set two curve blenadShape to max
#browLip = "brow" or "lip"
def correctiveCrv( browLip ):
    if browLip =="brow":
    
        jnts = cmds.ls ( '*browBase*_jnt', fl = True, type ='joint')
        jntNum = len(jnts)
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
                
                fixName = '%s_%s_fix'%( ts[0].split("_")[0], ts[1].split("_")[0] )
                print fixName
                tempBrowCrv = cmds.curve ( d = 1, p =([-1,0,0],[-0.5,0,0],[0,0,0],[0.5,0,0],[1,0,0]) ) 
                cmds.rebuildCurve ( tempBrowCrv, rebuildType = 0, spans = jntNum-1, keepRange = 0, degree = 1 )    
                browCrv = cmds.rename (tempBrowCrv, fixName )  
                cmds.blendShape( "browBS",  edit=True, t=( "brow_crv", len(aliasBS)/2+i, browCrv, 1.0) )
                
                addD =cmds.shadingNode ( 'addDoubleLinear', asUtility=True, n = fixName.replace("fix","addD") )
                cmds.connectAttr( "browBS." + ts[0], addD + ".input1")
                cmds.connectAttr( "browBS." + ts[1], addD + ".input2")
                
                remap =cmds.shadingNode ( 'remapValue', asUtility=True, n = fixName.replace("fix","remap") )
                cmds.connectAttr( addD+".output", remap + ".inputValue" )
                cmds.setAttr( remap + ".inputMin", 1 ) 
                cmds.setAttr( remap + ".inputMax", 2 )      
                cmds.connectAttr(remap + ".outValue", "browBS."+ browCrv )
            
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
        print lTgts, rTgts
        for i, ts in enumerate([lTgts,rTgts]):
            if len(ts) ==2:
        
                fixName = '%s_%s_fix'%( ts[0].split("_")[1], ts[1].split("_")[1] )
                templipCrv = cmds.curve ( d = 3, p =([0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0])) 
                cmds.rebuildCurve ( rt = 0, d = 3, kr = 0, s = 4 )   
                upLipFix = cmds.rename (templipCrv, ts[0][:2]+fixName )          
                cmds.blendShape( "upLipCrvBS",  edit=True, t=( "upLip_crv", len(aliasUpBS)/2+i, upLipFix, 1.0) )
        
                loFist = ts[0].replace("up","lo")
                loSecnd = ts[1].replace("up","lo")
                loFixName = fixName.replace("up", "lo")
                loCrvTemp = cmds.duplicate( upLipFix )
                loLipFix = cmds.rename (loCrvTemp, ts[0][:2]+loFixName )
                cmds.blendShape( "loLipCrvBS",  edit=True, t=("loLip_crv", len(aliasUpBS)/2+i, loLipFix, 1.0) )                 
                
                plus =cmds.shadingNode ( 'plusMinusAverage', asUtility=True, n = ts[0][:2]+fixName.replace("fix","Plus") )
                cmds.connectAttr( "upLipCrvBS." + ts[0], plus + ".input2D[0].input2Dx" )
                cmds.connectAttr( "upLipCrvBS." + ts[1], plus + ".input2D[1].input2Dx" )
                cmds.connectAttr( "loLipCrvBS." + loFist, plus + ".input2D[0].input2Dy" )
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
        
        
#correctiveCrv( "lip" )
    
    
    
#miscellaneous--------------------------------------------------------------------------------------------------------------------------------------------------------------#
#get Orig mesh using tweak node and avoid name dependency

def fixMix():
    headTemp = cmds.ls(sl=1)
    if cmds.objExists('mix'): cmds.delete('mix')
    newTarget = cmds.duplicate( headTemp[0], n = 'mix')
    child = [ c for c in cmds.listRelatives(newTarget[0], c =1 ) if 'Orig' in c ]
    cmds.delete( child[0])
    if cmds.objExists ('originGeo'): cmds.delete('originGeo')
    origMesh = getOrigMesh( headTemp[0])
    if 'Orig' in origMesh:
        cmds.setAttr( origMesh +".intermediateObject", 0 )
        cmds.duplicate ( origMesh, n= 'originGeo' )
        origChild =cmds.listRelatives('originGeo', c=1)   
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
           	 
    else :
        print 'check the original shape(ShapeOrig)!!'
 
 
 
 
 
 
 
def getOrigMesh( obj ):
    
    shapes = cmds.listRelatives( obj, s=1, type = 'shape')
    origList = [ s for s in shapes if "Orig" in s ]
    #check if it treverse forward the shape of the selection
    for org in origList:
        future = cmds.listHistory( obj+'Shape', f=1 )
        if future:
            if obj+'Shape' in future:
                origShape = org       	 
     
        else: cmds.delete( org )
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
def targetAdd_Reconnect():

    meshSel = cmds.ls(sl=1, typ ='transform')
    base = meshSel[1]
    target = meshSel[0] 
    BSnode = [ n for n in cmds.listHistory(base, historyAttr=1 ) if cmds.nodeType(n) == "blendShape" ]    
    if BSnode:
        aliasAtt = cmds.aliasAttr(BSnode[0], q=1)        
    else:
        print "select the object with blendShape"    
    
    if target in aliasAtt:
        for tgt, wgt in zip(*[iter(aliasAtt)]*2):        
            # check if target curve exists
            if target == tgt :
                tgtID = wgt.split("[")[1][:-1]
                print tgtID
                cmds.connectAttr( target+".worldMesh", BSnode[0]+ ".inputTarget[0].inputTargetGroup[%s].inputTargetItem[6000].inputGeomTarget"%str(tgtID) )
            
    else:
        targetID = len(aliasAtt)/2 + 1
        cmds.blendShape( BSnode, e=1, t = [base, targetID, target, 1 ] )
        
        
        
        
#create targets after copy blendShape delta        
#select curve with blendShape(clean, no connections)
#copy target and reconnect for blendShape
def bakeTarget_reconnect():

    crvSel = cmds.ls(sl=1, typ ='transform')
    baseCrv = crvSel[0]
    BSnode = [ n for n in cmds.listHistory(baseCrv, historyAttr=1 ) if cmds.nodeType(n) == "blendShape" ]    
    if crvBS:
        aliasAtt = cmds.aliasAttr(crvBS[0], q=1)
        
    else:
        print "select the curve with blendShape"    

    for tgt, wgt in zip(*[iter(aliasAtt)]*2):
        cmds.setAttr( crvBS[0] + "."+ tgt, 0 )
    
    crvTgt = []
    for tgt, wgt in zip(*[iter(aliasAtt)]*2):
        
        # check if target curve exists
        if cmds.objExists(tgt):
            cmds.confirmDialog( title='Confirm', message='%s target exists already' )
            
        else:
            cmds.setAttr( crvBS[0] + "."+ tgt, 1 )
            copyCrv = cmds.duplicate ( baseCrv, rc=1, n= tgt )[0]
            crvTgt.append(copyCrv)
            tgtID= wgt.split("[")[1][:-1]
            cmds.connectAttr( copyCrv+".worldSpace", crvBS[0]+ ".inputTarget[0].inputTargetGroup[%s].inputTargetItem[6000].inputGeomTarget"%str(tgtID) )
            cmds.setAttr( crvBS[0] + "."+ tgt, 0 )
            
            
            
            
            
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
