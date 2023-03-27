#RNK skinWeighting
def rnkBrowMapSkinning():
    if not "browMapSurf":
        print "create browMapSurf first!!"
    else : browMapSurf = "browMapSurf"
    lBrowJnts = cmds.ls ("L_*Eyebrow*", type ="joint")
    rBrowJnts = cmds.ls ("R_*Eyebrow*", type ="joint")
    
    x = rBrowJnts[::-1]
    y = lBrowJnts
    orderJnts = x + y
    jntNum = len(orderJnts)    
    if not cmds.objExists('C_jnt_fineTune_Head_JNT'):
        headSkelPos = cmds.xform('headSkelPos', q =1, ws =1, t =1 )
        cmds.joint(n = 'C_jnt_fineTune_Head_JNT', p = headSkelPos )
    orderJnts.insert( jntNum/2, "C_jnt_fineTune_Head_JNT" )
    jntNum = len(orderJnts)
    vrts= cmds.polyEvaluate(browMapSurf, v =1 )
    numVtx = vrts/jntNum
    if vrts%jntNum==0:
        skinCls = cmds.skinCluster(orderJnts , browMapSurf, toSelectedBones=1 )
        # 100% skinWeight to C_jnt_fineTune_Head_JNT
        cmds.skinPercent(skinCls[0], browMapSurf, transformValue = ["C_jnt_fineTune_Head_JNT", 1])
        # skinWeight
        for i in range (0, jntNum):
            vtxs = "browMapSurf.vtx[%s:%s]"%( numVtx*i, numVtx*i+numVtx-1 )
            cmds.skinPercent( skinCls[0], vtxs, transformValue = [ orderJnts[i], 1])
    else:
        print "Number of faces and browJnts are not matching"  
        
        
        




def rnkEyeMapSkinning():

    if not "eyeTip_map":
        print "create eyeTip_map first!!"
    else : eyeMapSurf = "eyeTip_map"
    orderJnts=['L_jnt_fineTune_Eyelid_InCorner_JNT' ,'L_jnt_fineTune_Eyelid_Top_in_JNT', 'L_jnt_fineTune_Eyelid_Top_mid_JNT','L_jnt_fineTune_Eyelid_Top_out_JNT',
    'L_jnt_fineTune_Eyelid_OutCorner_JNT', 'L_jnt_fineTune_Eyelid_Bot_out_JNT', 'L_jnt_fineTune_Eyelid_Bot_mid_JNT', 'L_jnt_fineTune_Eyelid_Bot_in_JNT' ]
    
    if cmds.objExists('L_jnt_fineTune_Eyelid_scale_JNT'):

        orderJnts.append( 'L_jnt_fineTune_Eyelid_scale_JNT' )
        
    else:
        print "L_Eyelid_scale_JNT is missing"
    
    jntNum = len(orderJnts[:-1])    
    vrts= cmds.polyEvaluate(eyeMapSurf, v =1 )
    numVtx = vrts/jntNum
    print vrts, jntNum
    if vrts%jntNum==0:
        skinCls = cmds.skinCluster(orderJnts , eyeMapSurf, toSelectedBones=1 )
        # skinWeight
        for i in range (0, jntNum):
            vtxs = "eyeTip_map.vtx[%s:%s]"%( numVtx*i, numVtx*i+numVtx-1 )
            cmds.skinPercent( skinCls[0], vtxs, transformValue = [ orderJnts[i], 1])
    else:
        print "Number of faces and eyeJnts are not matching"  

        


def rnkLipMapSkinning():

    if not "lipTip_map":
        print "create lipTip_map first!!"
    else : lipMapSurf = "lipTip_map"

    orderJnts = [ 'R_jnt_fineTune_Lips_Bot_JNT', 'R_jnt_fineTune_Lips_Corner_JNT','R_jnt_fineTune_Lips_Top_JNT', 'C_jnt_fineTune_Lips_Top_JNT',
     'L_jnt_fineTune_Lips_Top_JNT', 'L_jnt_fineTune_Lips_Corner_JNT', 'L_jnt_fineTune_Lips_Bot_JNT', 'C_jnt_fineTune_Lips_Bot_JNT' ]

    jntNum = len(orderJnts)    
    vrts= cmds.polyEvaluate(lipMapSurf, v =1 )
    numVtx = vrts/jntNum
    print vrts, jntNum
    if vrts%jntNum==0:
        skinCls = cmds.skinCluster(orderJnts , lipMapSurf, toSelectedBones=1 )

        # skinWeight
        for i in range (0, jntNum):
            vtxs = "lipTip_map.vtx[%s:%s]"%( numVtx*i, numVtx*i+numVtx-1 )
            cmds.skinPercent( skinCls[0], vtxs, transformValue = [ orderJnts[i], 1])
    else:
        print "Number of faces and lipJnts are not matching"  









def rnkCopyJawOpenWeight():
    
    headGeo = cmds.ls(sl=1, type = "transform")[0]
    size = cmds.polyEvaluate( headGeo, v = 1)
    skinCls = mel.eval("findRelatedSkinCluster %s"%headGeo )
    print skinCls
    #set weight back to 1 on the headSkel_jnt
    cmds.skinPercent( skinCls, headGeo+'.vtx[0:%s]'%(size-1), nrm=1, tv = ['C_jnt_jaw_Head_JNT', 1] )
    cmds.setAttr( skinCls +'.normalizeWeights', 0 )
    
    jawOpenWgt = cmds.getAttr ("jawOpen_cls.wl[0].w[0:"+str(size-1)+"]" )             
    upLipWgt = cmds.getAttr ("upLipRoll_cls.wl[0].w[0:"+str(size-1)+"]")
    bttmLipWgt = cmds.getAttr ( "bttmLipRoll_cls.wl[0].w[0:%s]"%str(size-1))    

    headSkelID = getJointIndex( skinCls,'C_jnt_jaw_Head_JNT' )
    upjawID = getJointIndex( skinCls, 'C_jnt_jaw_uJaw_JNT' ) 
    jawID = getJointIndex( skinCls, 'C_jnt_jaw_Jaw_JNT' )
    topLipID = getJointIndex ( skinCls, 'C_jnt_jaw_lips_Top_pivot_JNT' )
    botLipID = getJointIndex ( skinCls, 'C_jnt_jaw_lips_Bot_pivot_JNT' )

    botLipStr = ''
    upLipStr = ''
    jcValStr = ''
    valStr =''
    headVal = ''
    for x in range(size):
        
        if jawOpenWgt[x]>1:
            jawOpenWgt[x] = 1 

        upLipStr +=str(upLipWgt[x])+" "
        
        tempVal = jawOpenWgt[x] - bttmLipWgt[x] 
        if tempVal < 0 :
            bttmLipWgt[x] = jawOpenWgt[x]
        #jaw weight - bttmLip weight            
        jcVal = jawOpenWgt[x] - bttmLipWgt[x]
        jcValStr += str(jcVal)+" "
              
        botLipStr +=str(bttmLipWgt[x]) + " "
        
        #headSkel_jnt weight =           
        tmpVal = 1 -jawOpenWgt[x] - upLipWgt[x]
        valStr +=str(tmpVal)+" "
        
        headVal +=str(0)+" " 

    
    commandStr = ("setAttr -s "+str(size)+" " + skinCls+".wl[0:"+str(size-1)+"].w["+upjawID+"] "+ valStr );
    mel.eval (commandStr)                 

    headCmmdStr = ("setAttr -s "+str(size)+" " + skinCls+".wl[0:"+str(size-1)+"].w["+headSkelID+"] "+ headVal );
    mel.eval (headCmmdStr) 
    
    cmmdStr = ("setAttr -s "+str(size)+" " +skinCls + ".wl[0:"+str(size-1)+"].w["+jawID+"] "+ jcValStr);
    mel.eval (cmmdStr)
    
    topLipCmmdStr = ("setAttr -s "+str(size)+" " + skinCls+".wl[0:"+str(size-1)+"].w["+topLipID+"] "+ upLipStr);
    mel.eval (topLipCmmdStr) 
      
    botLipCmmdStr = ("setAttr -s "+str(size)+" " + skinCls+".wl[0:"+str(size-1)+"].w["+botLipID+"] "+ botLipStr);
    mel.eval (botLipCmmdStr)

    #cmds.skinPercent('headSkin', headGeo, nrm=False, prw=100)
    cmds.setAttr( skinCls + '.normalizeWeights', 1 )#normalization mode. 0 - none, 1 - interactive, 2 - post         
    cmds.skinPercent( skinCls , headGeo, nrm= 1 )