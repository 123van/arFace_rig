# -*- coding: utf-8 -*-
'''
1. from twitchScript import jawSetup
reload(jawSetup)
jawSetup.mouthJoint() 

2.setLipJntLabel() : LipY*_jnt set label for mirror weight 

3.bridgeJoints(): 

4.mouthCtlToCrv()

5.lipCrvToJoint() 
'''


import re
import fnmatch
import maya.cmds as cmds

def lipCrvToJoint( upLow ):
        
    #main lipCtrls connect with LipCtl_crv   
    UD = upLow.title()
    lipCtrls=['lip' + UD + 'CtrlRB', 'lip' + UD + 'CtrlRA', 'lip' + UD + 'CtrlMid', 'lip' + UD + 'CtrlLA', 'lip' + UD + 'CtrlLB']
    lipCtrls.insert(0, 'lipCtrlRTip' )
    lipCtrls.append('lipCtrlLTip')
    lipCtrlLen = len(lipCtrls)
    
    for x in range( 0, lipCtrlLen ):
        # curve cv xValue zero out
        zeroX = cmds.shadingNode ( 'addDoubleLinear', asUtility=True, n = upLow + lipCtrls[x].split('Ctrl', 1)[1] + '_xAdd' ) 
        cvTx = cmds.getAttr(upLow + 'LipCtl_crv.controlPoints['+str(x)+'].xValue' ) 
        cmds.connectAttr ( lipCtrls[x] +'.tx', zeroX + '.input1' )
        cmds.setAttr (zeroX + '.input2' , cvTx ) 
        cmds.connectAttr ( zeroX + '.output', upLow + 'LipCtl_crv.controlPoints['+str(x)+'].xValue' )
        # main ctrl's TY drive the ctrl curve point yValue
        cmds.connectAttr ( lipCtrls[x] +'.ty' , upLow + 'LipCtl_crv.controlPoints['+str(x)+'].yValue' ) 
    
    #main lipRoll Ctrls connect with 'LipRollCtl_crv' /'RollYZCtl_crv' 
    mainRollCtrlP = cmds.listRelatives ( 'Lip'+ upLow.title() + 'RollCtrl', ad =1, type = 'transform' )
    lipRollCtls = fnmatch.filter( mainRollCtrlP, '*Roll_ctl')
    rollCtlDict = { 0:2, 1:3, 2:1 }
    for q, p in rollCtlDict.items(): 
        # lipRollCtrl  to 'RollCtl_crv' 
        cmds.connectAttr ( lipRollCtls[q]+ '.rz', upLow + 'LipRoll_crv.controlPoints[%s].yValue'%p ) 
        # lipRollCtrl  to 'RollYZCtl_crv' 
        cmds.connectAttr ( lipRollCtls[q]+ '.ty', upLow + 'RollYZ_crv.controlPoints[%s].yValue'%p )
        cmds.connectAttr ( lipRollCtls[q]+ '.tx', upLow + 'RollYZ_crv.controlPoints[%s].zValue'%p )
    
    # curve's Poc drive the joint
    lipJots= cmds.ls ( upLow + 'LipJotX*', fl=True, type ='transform' )
    jotNum = len (lipJots)
      
    if upLow == 'up':
        min = 0
        max = jotNum
    elif upLow == 'lo':  
        min = 1
        max = jotNum+1
        
    for i in range ( min, max ):  
    
        jotXMult = cmds.shadingNode ( 'multiplyDivide', asUtility=True, n = upLow + 'JotXRot' + str(i)+'_mult' )
        jotX_AddD = cmds.shadingNode ( 'addDoubleLinear', asUtility=True, n = upLow + 'JotXRY' + str(i) + '_add' )
        jntYMult = cmds.shadingNode ( 'multiplyDivide', asUtility=True, n = upLow + 'JotYRot' + str(i)+'_mult' )
        jntY_AddD = cmds.shadingNode ( 'addDoubleLinear', asUtility=True, n = upLow + 'JotYRZ' + str(i) + '_add' )
        mouthTX_AddD = cmds.shadingNode ( 'addDoubleLinear', asUtility=True, n = upLow + 'MouthTX' + str(i) + '_add' )
        mouthTY_AddD = cmds.shadingNode ( 'addDoubleLinear', asUtility=True, n = upLow + 'MouthTY' + str(i) + '_add' )
        jotXPosMult = cmds.shadingNode ( 'multiplyDivide', asUtility=True, n = upLow + 'LipJotXPos' + str(i)+'_mult' )
        plusTXAvg = cmds.shadingNode ( 'plusMinusAverage', asUtility=True, n = upLow + 'TX' + str(i) +'_plus' )   
        plusTYAvg = cmds.shadingNode ( 'plusMinusAverage', asUtility=True, n = upLow + 'TY' + str(i) +'_plus' )  
        jotXPosAvg = cmds.shadingNode ( 'plusMinusAverage', asUtility=True, n = upLow + 'LipJotXPos' + str(i)+'_plus' )        
        jotX_rzAddD = cmds.shadingNode ( 'addDoubleLinear', asUtility=True, n = upLow + 'RZ' + str(i) + '_add' )
        rollYZMult = cmds.shadingNode ( 'multiplyDivide', asUtility=True, n = upLow + 'RollYZ' + str(i)+'_mult' )
        poc = upLow +'LipCrv' + str(i) + '_poc'
        initialX = cmds.getAttr ( poc + '.positionX' )
        
        TYpoc = upLow +'LipTy' + str(i) + '_poc'
        initialTYX = cmds.getAttr ( TYpoc + '.positionX' )
        
        ctlPoc = upLow +'LipCtl' + str(i) + '_poc'
        initialCtlX = cmds.getAttr ( ctlPoc + '.positionX' )
        
        lipRollPoc = upLow +'LipRoll' + str(i) + '_poc'
        rollYZPoc = upLow +'LipRollYZ' + str(i) + '_poc'     
        
        if i==0 or i==jotNum-1:
            zeroTip = cmds.shadingNode ( 'addDoubleLinear', asUtility=True, n = 'zeroTip' + str(i) + '_plus' )
            momTY = cmds.getAttr ( upLow + 'LipDetailP' + str(i) +'.ty' )
            cmds.connectAttr ( ctlPoc + '.positionY', zeroTip + '.input1'  )
            cmds.setAttr ( zeroTip + '.input2', momTY )
            cmds.connectAttr ( zeroTip + '.output', upLow + 'LipDetailP' +str(i) + '.ty')
            
        else:
            # LipCtl_crv connect with lipDetailP (lipDetailCtrl parents)
            cmds.connectAttr ( ctlPoc + '.positionY', upLow + 'LipDetailP' +str(i) + '.ty')        
        
        #TranslateX add up for        
        #1. curve translateX add up for LipJotX       swivelTranX_mult.outputY - ry
        swivelTranXMult = 'swivelTranX_mult'
        swivelTranYMult = 'swivelTranY_mult'
        mouthTxMult = 'mouthTranX_mult'
        mouthTyMult = 'mouthTranY_mult'
        
        cmds.connectAttr ( poc + '.positionX', plusTXAvg + '.input3D[0].input3Dx') 
        cmds.setAttr (plusTXAvg + '.input3D[1].input3Dx', -initialX ) 
        #swivel.tx --> not lipJotX.tx but lipJotP.tx   
        cmds.connectAttr ( plusTXAvg + '.output3Dx', jotXMult + '.input1X' ) 
        cmds.connectAttr ( 'lipFactor.txSum_lipJntX_ry', jotXMult + '.input2X' )       
        cmds.connectAttr ( jotXMult + '.outputX', jotX_AddD + '.input1')
        cmds.connectAttr ( swivelTranXMult + '.outputY', jotX_AddD + '.input2' )
        cmds.connectAttr ( jotX_AddD + '.output', upLow + 'LipJotX'+str(i)+'.ry' ) 
        
        #swivel.tx / rz --> lipJotX.rz        
        cmds.connectAttr ( 'swivel_ctrl.rz',  jotX_rzAddD+ '.input1' ) 
        cmds.connectAttr ( swivelTranXMult + '.outputZ', jotX_rzAddD + '.input2' ) 
        cmds.connectAttr ( jotX_rzAddD + '.output', upLow + 'LipJotX'+str(i)+'.rz' )
        
        # curve translateY add up ( joint(LipJotX)"rx" driven by both curves(lipCrv, lipCtlCrv))
        # ty(input3Dy) / extra ty(input3Dx) seperate out for jawSemi
       
        cmds.setAttr ( plusTYAvg + '.operation', 1 )
        cmds.connectAttr ( poc + '.positionY', plusTYAvg + '.input1D[0]' )
        cmds.connectAttr ( ctlPoc + '.positionY', plusTYAvg + '.input1D[1]') 
        cmds.connectAttr ( upLow + 'LipDetail'+ str(i) + '.ty', plusTYAvg + '.input1D[2]' )    
        #connect translateY plusAvg to joint rotateX Mult        
        cmds.connectAttr ( plusTYAvg + '.output1D', jotXMult + '.input1Y' )  
        cmds.connectAttr ( 'lipFactor.tySum_lipJntX_rx', jotXMult + '.input2Y' ) 
        cmds.connectAttr ( jotXMult + '.outputY', mouthTY_AddD + '.input1' )
        cmds.connectAttr ( mouthTyMult + '.outputX', mouthTY_AddD + '.input2' )  
        cmds.connectAttr ( mouthTY_AddD + '.output', upLow + 'LipJotX'+ str(i) + '.rx' )   
        
        #joint(LipJotX) translateX driven by poc positionX sum
        cmds.connectAttr ( TYpoc + '.positionX', jotXPosAvg + '.input3D[0].input3Dx' ) 
        cmds.setAttr ( jotXPosAvg + '.input3D[1].input3Dx', -initialTYX )        
        cmds.connectAttr ( jotXPosAvg + '.output3Dx', jotXPosMult + '.input1X' )  
        cmds.connectAttr ( 'lipFactor.txSum_lipJntX_tx', jotXPosMult + '.input2X' ) 
        cmds.connectAttr ( jotXPosMult + '.outputX', upLow + 'LipJotX'+ str(i) + '.tx' )
         
        #2. poc positionY,Z sum drive joint("lipJotX") translateY,Z
        cmds.connectAttr ( TYpoc + '.positionY',  jotXPosAvg + '.input3D[0].input3Dy' )
        
        cmds.connectAttr ( jotXPosAvg + '.output3Dy', jotXPosMult + '.input1Y' )
        cmds.connectAttr ( 'lipFactor.tySum_lipJntX_ty', jotXPosMult + '.input2Y' )  
        cmds.connectAttr ( jotXPosMult + '.outputY', upLow + 'LipJotX'+str(i)+'.ty' )     
        
        # joint(LipJotX) translateZ driven by poc positionZ sum
        cmds.connectAttr ( TYpoc + '.positionZ', jotXPosAvg + '.input3D[0].input3Dz' )
        cmds.connectAttr ( poc + '.positionZ', jotXPosAvg + '.input3D[1].input3Dz' ) 
        cmds.connectAttr ( rollYZPoc + '.positionZ', jotXPosAvg + '.input3D[2].input3Dz' ) 
        cmds.connectAttr ( jotXPosAvg + '.output3Dz', jotXPosMult + '.input1Z' )
        cmds.connectAttr ( 'lipFactor.tzSum_lipJntX_tz', jotXPosMult + '.input2Z' ) 
        cmds.connectAttr ( jotXPosMult + '.outputZ', upLow + 'LipJotX'+ str(i) + '.tz' )          
        
        #3. LipCtlCrv Poc.positionX + LipDetail.tx for LipJotY 
        # mouth_move.tx --> lipJotY0.ry .rz /mouth_move.rz --> lipJotY0.rz
        cmds.connectAttr ( ctlPoc + '.positionX', plusTXAvg + '.input3D[0].input3Dy' )  
        cmds.setAttr ( plusTXAvg + '.input3D[1].input3Dy', -initialCtlX )  
        cmds.connectAttr ( upLow + 'LipDetail'+ str(i)+'.tx', plusTXAvg + '.input3D[2].input3Dy' )
        cmds.connectAttr (  plusTXAvg + '.output3Dy', jntYMult + '.input1Y' )          
        cmds.connectAttr ( 'lipFactor.txSum_lipJntY_ry', jntYMult + '.input2Y' )   
        cmds.connectAttr ( jntYMult + '.outputY', mouthTX_AddD+ '.input1')
        cmds.connectAttr ( mouthTxMult + '.outputX', mouthTX_AddD+ '.input2')  
        cmds.connectAttr ( mouthTX_AddD+ '.output', upLow+'LipY'+str(i)+'_jnt.ry' ) 
       
        cmds.connectAttr ( 'mouth_move.rz', jntY_AddD + '.input1' )          
        cmds.connectAttr ( mouthTxMult + '.outputZ', jntY_AddD + '.input2' )   
        cmds.connectAttr ( jntY_AddD + '.output', upLow+'LipY'+str(i)+'_jnt.rz' ) 
        
        #lipRollYZCrv --> lipRollJotT* .ty / tz
        cmds.connectAttr ( rollYZPoc + '.positionY', rollYZMult + '.input1Y' )
        cmds.connectAttr ( 'lipFactor.YZPoc_rollJntT_ty', rollYZMult + '.input2Y' ) 
        cmds.connectAttr ( rollYZMult + '.outputY', upLow+'LipRollJotT'+str(i)+'.ty' )
        
        cmds.connectAttr ( rollYZPoc + '.positionZ', rollYZMult + '.input1Z' )
        cmds.connectAttr ( 'lipFactor.YZPoc_rollJntT_tz', rollYZMult + '.input2Z' ) 
        cmds.connectAttr ( rollYZMult + '.outputZ', upLow+'LipRollJotT'+str(i)+'.tz' )
        
        #lipRollCrv --> lipRollJot*_jnt 
        cmds.connectAttr ( lipRollPoc + '.positionY', upLow+'LipRoll'+str(i)+'_jnt.rx' )

    setLipJntLabel()



def setLipJntLabel():
    upJntY = cmds.ls('upLipY*_jnt', fl=1, type = 'joint')
    loJntY = cmds.ls('loLipY*_jnt', fl=1, type = 'joint')
    upJntNum = len(upJntY)
    loJntNum = len(loJntY)
    rightUp = upJntY[0:upJntNum/2]
    leftUp = upJntY[upJntNum/2+1: ]
    rightLo =loJntY[0: loJntNum/2] 
    leftLo = loJntY[loJntNum/2+1: ]
    leftLo.reverse()
    rightUp.reverse()
    leftJnt = leftUp + leftLo
    rightJnt = rightUp + rightLo
    cntJnt =[ upJntY[upJntNum/2], loJntY[loJntNum/2] ]
    for i, j in enumerate(leftJnt):
        cmds.setAttr(j + '.side', 1)
        cmds.setAttr(j + '.type', 18)
        cmds.setAttr(j + '.otherType', str(i).zfill(2), type = "string")
    for id, k in enumerate(rightJnt):
        cmds.setAttr(k + '.side', 2)
        cmds.setAttr(k + '.type', 18)
        cmds.setAttr(k + '.otherType', str(id).zfill(2), type = "string")    
        

#individual mouth ctrls to curves and jawSemi/ midCheek jnt/ loCheek_cls  
def mouthCtlToCrv():    
    
    '''1. swivel setup'''
    if not cmds.listConnections('lipJotP', s=1 ):
        
        swivelTranXMult = cmds.shadingNode ('multiplyDivide', asUtility = 1, n = 'swivelTranX_mult')
        cmds.connectAttr ( 'swivel_ctrl.tx', swivelTranXMult + '.input1X' )
        cmds.connectAttr ( 'swivel_ctrl.tx', swivelTranXMult + '.input1Y' )
        cmds.connectAttr ( 'swivel_ctrl.tx', swivelTranXMult + '.input1Z' )
        # tx*0.5 = lipJotP.tx / tx*6 = LipJotX*.ry / tx*20 = 'jawSemi.rz'
        cmds.connectAttr ('lipFactor.swivel_lipJntP_tx', swivelTranXMult + '.input2X' )
        cmds.connectAttr ('lipFactor.swivel_lipJntX_ry', swivelTranXMult + '.input2Y' )
        cmds.connectAttr ('lipFactor.swivel_lipJntX_rz', swivelTranXMult + '.input2Z' )
        cmds.connectAttr ( swivelTranXMult + '.outputX', 'lipJotP.tx' )
        
        swivelTranYMult = cmds.shadingNode ('multiplyDivide', asUtility = 1, n = 'swivelTranY_mult')
        cmds.connectAttr ( 'swivel_ctrl.ty', swivelTranYMult + '.input1X' ) # for scale
        cmds.connectAttr ( 'swivel_ctrl.ty', swivelTranYMult + '.input1Y' )
        cmds.connectAttr ( 'swivel_ctrl.ty', swivelTranYMult + '.input1Z' ) # for scale
        cmds.connectAttr ( 'lipFactor.swivel_lipJntP_ty', swivelTranYMult + '.input2Y' )
        cmds.connectAttr ( swivelTranYMult + '.outputY', 'lipJotP.ty' )

        # mouth_move setup
        mouthTxMult = cmds.shadingNode ('multiplyDivide', asUtility = 1, n = 'mouthTranX_mult')
        loCheekY_mult = cmds.shadingNode ('multiplyDivide', asUtility = 1, n = 'loCheekY_mult')
        midCheekY_Mult = cmds.shadingNode ('multiplyDivide', asUtility = 1, n = 'midCheekY_mult')
        cmds.connectAttr ( 'mouth_move.tx', mouthTxMult + '.input1X' )
        cmds.connectAttr ( 'mouth_move.tx', mouthTxMult + '.input1Z' )
        cmds.connectAttr ('lipFactor.mouth_lipJntY_ry', mouthTxMult + '.input2X' )  
        cmds.connectAttr ('lipFactor.mouth_lipJntY_rz', mouthTxMult + '.input2Z' )  
        cmds.connectAttr ( 'mouth_move.tx', loCheekY_mult + '.input1X' )
        cmds.connectAttr ( 'mouth_move.tx', loCheekY_mult + '.input1Y' )    
        cmds.connectAttr ( 'mouth_move.tx', midCheekY_Mult + '.input1X' )
        cmds.connectAttr ( 'mouth_move.tx', midCheekY_Mult + '.input1Y' ) 
        cmds.connectAttr ('lipFactor.mouth_loCheekRY', loCheekY_mult + '.input2X' )
        cmds.connectAttr ('lipFactor.mouth_loCheekRZ', loCheekY_mult + '.input2Y' )
        cmds.connectAttr ('lipFactor.mouth_midCheekRY', midCheekY_Mult + '.input2X' )# for cheekRotY
        cmds.connectAttr ('lipFactor.mouth_midCheekRZ', midCheekY_Mult + '.input2Y' )# for cheekRotY
        midCheekRY = [ 'l_midCheekRotY', 'r_midCheekRotY' ]
        loCheekRY = [ 'l_loCheekRotY', 'r_loCheekRotY' ]
        for lo in loCheekRY:            
            cmds.connectAttr ( loCheekY_mult + '.outputX', lo + '.ry' )
            cmds.connectAttr ( loCheekY_mult + '.outputY', lo + '.rz' )
        for mid in midCheekRY:
            cmds.connectAttr ( midCheekY_Mult + '.outputX', mid + '.ry' )
            cmds.connectAttr ( midCheekY_Mult + '.outputY', mid + '.rz' )
        
        mouthTyMult = cmds.shadingNode ('multiplyDivide', asUtility = 1, n = 'mouthTranY_mult')
        cmds.connectAttr ( 'mouth_move.ty', mouthTyMult + '.input1X' )
        cmds.connectAttr ( 'mouth_move.ty', mouthTyMult+ '.input1Y' )
        cmds.connectAttr ( 'mouth_move.ty', mouthTyMult + '.input1Z' )
        cmds.connectAttr ('lipFactor.mouth_lipJntX_rx', mouthTyMult + '.input2X' )
        cmds.connectAttr ('lipFactor.mouth_midCheekRX', mouthTyMult + '.input2Y' )# for cheekRotX
        cmds.connectAttr ('lipFactor.mouth_loCheekRX', mouthTyMult + '.input2Z' )
        
        #jawSemi setup
        cmds.connectAttr ( swivelTranXMult + '.outputX', 'jawSemi.tx' )
        cmds.connectAttr ( swivelTranXMult + '.outputY', 'jawSemi.ry' )
        cmds.connectAttr ( swivelTranXMult + '.outputZ', 'jawSemi.rz' )
        # swivel.ty mainly control lipJotP.ty
        lipPScale_sum = cmds.shadingNode ( 'plusMinusAverage', asUtility= True, n = 'lipPScale_sum' )        
        cmds.connectAttr ( swivelTranYMult + '.outputY', 'jawSemi.ty' )        
        #lipP scale down as lipP/jawSemi goes down
        cmds.setAttr (lipPScale_sum+'.input2D[0].input2Dx', 1 )
        cmds.setAttr (lipPScale_sum+'.input2D[0].input2Dy', 1 )             
        cmds.connectAttr ("lipFactor.swivel_lipJntP_sx", swivelTranYMult + '.input2X')        
        cmds.connectAttr ("lipFactor.swivel_lipJntP_sz", swivelTranYMult + '.input2Z')
        cmds.connectAttr ( swivelTranYMult + '.outputX', lipPScale_sum+'.input2D[1].input2Dx' )
        cmds.connectAttr ( swivelTranYMult + '.outputZ', lipPScale_sum+'.input2D[1].input2Dy' )
        cmds.connectAttr ( lipPScale_sum + '.output2Dx', 'lipJotP.sx' )
        cmds.connectAttr ( lipPScale_sum + '.output2Dy', 'lipJotP.sz' )
        cmds.connectAttr ( lipPScale_sum + '.output2Dx', 'jawSemi.sx' )
        cmds.connectAttr ( lipPScale_sum + '.output2Dy', 'jawSemi.sz' )        
    
    #lowJaw_dir.ty --> 1.lipJotX0.tx / 2. lipJotP.sx. sz    
    #jaw_UDLRIO.ty --> 1.lipJotX0.ty / 2. lipJotP.sx. sz / jaw_UDLRIO.tx --> lipJotX0.tz
    if not cmds.listConnections('lowJaw_dir', d =1 ):    
        jawOpenMult = cmds.shadingNode ('multiplyDivide', asUtility = 1, n = 'jawOpen_mult' )         
        jawOpen_jnt = indiCrvSetup('JawOpen')
        cmds.connectAttr( 'lowJaw_dir.tx',  jawOpenMult + '.input1X' )
        cmds.connectAttr( "lipFactor.jawOpenTX_scale",  jawOpenMult + '.input2X' )
        cmds.connectAttr( jawOpenMult + '.outputX', jawOpen_jnt + '.tx' )
    
        cmds.connectAttr( 'lowJaw_dir.ty',  jawOpenMult + '.input1Y' )
        cmds.connectAttr( "lipFactor.jawOpenTY_scale",  jawOpenMult + '.input2Y' )
        cmds.connectAttr( jawOpenMult + '.outputY', jawOpen_jnt + '.ty' )

        jawCloseRotMult = cmds.shadingNode ('multiplyDivide', asUtility = 1, n = 'jawCloseRot_mult' )        
        # jawClose_jnt.rx = lowJaw_dir.ty * 36  
        cmds.connectAttr ( 'lowJaw_dir.ty', jawCloseRotMult + '.input1X' )
        cmds.connectAttr ( 'lipFactor.jawOpen_jawCloseRX', jawCloseRotMult + '.input2X' )       
        cmds.connectAttr ( jawCloseRotMult + '.outputX', 'jawClose_jnt.rx' )
        
        cmds.connectAttr ( 'lowJaw_dir.tx', jawCloseRotMult + '.input1Y' )
        cmds.connectAttr ( 'lipFactor.jawOpen_jawCloseRY', jawCloseRotMult + '.input2Y' )       
        cmds.connectAttr ( jawCloseRotMult + '.outputY', 'jawClose_jnt.ry' )        
    
    if not cmds.listConnections('jaw_UDLR', d =1 ):
        UDLRT_mult = cmds.shadingNode ('multiplyDivide', asUtility = 1, n = 'UDLR_mult')
        UDLRTscale_mult = cmds.shadingNode ('multiplyDivide', asUtility = 1, n = 'UDLRscale_mult')
        jawCloseTranMult = cmds.shadingNode ('multiplyDivide', asUtility = 1, n = 'jawCloseTran_mult' )
        jawUDLR_jnt = indiCrvSetup('TyLip')
        cmds.connectAttr( 'jaw_UDLR.tx',  UDLRT_mult + '.input1X' )
        cmds.connectAttr( "lipFactor.UDLR_TX_scale",  UDLRT_mult + '.input2X' )
        cmds.connectAttr( UDLRT_mult + '.outputX', jawUDLR_jnt + '.tz' )

        cmds.connectAttr( 'jaw_UDLR.ty',  UDLRT_mult + '.input1Y' )
        cmds.connectAttr( "lipFactor.UDLR_TY_scale",  UDLRT_mult + '.input2Y' )
        cmds.connectAttr( UDLRT_mult + '.outputY', jawUDLR_jnt + '.ty' )
           
        # jaw_UDLRIO.ty --> 1.lipJotX0.ty / 2. lipJotP.sx. sz / jaw_UDLRIO.tx --> lipJotX0.tz                
        cmds.connectAttr ( 'jaw_UDLR.ty', UDLRTscale_mult + '.input1X' )
        cmds.connectAttr ( 'jaw_UDLR.ty', UDLRTscale_mult + '.input1Z' )
        cmds.connectAttr ( "lipFactor.swivel_lipJntP_sx", UDLRTscale_mult + '.input2X')        
        cmds.connectAttr ( "lipFactor.swivel_lipJntP_sz", UDLRTscale_mult + '.input2Z')
        cmds.connectAttr ( UDLRTscale_mult + '.outputX', lipPScale_sum+'.input2D[2].input2Dx' )
        cmds.connectAttr ( UDLRTscale_mult + '.outputZ', lipPScale_sum+'.input2D[2].input2Dy' )        
        
        # jawClose_jnt.ty = UDLR.ty * 2   / jawClose_jnt.tz = UDLR.tx * 1.1     
        cmds.connectAttr ( 'jaw_UDLR.tx', jawCloseTranMult + '.input1X' )
        cmds.connectAttr ( 'lipFactor.UDLR_jawCloseTZ', jawCloseTranMult + '.input2X' )       
        cmds.connectAttr ( jawCloseTranMult + '.outputX', 'jawClose_jnt.tz' )     
        
        cmds.connectAttr ( 'jaw_UDLR.ty', jawCloseTranMult + '.input1Y' )
        cmds.connectAttr ( 'lipFactor.UDLR_jawCloseTY', jawCloseTranMult + '.input2Y' )       
        cmds.connectAttr ( jawCloseTranMult + '.outputY', 'jawClose_jnt.ty' )
        
    tySum_cheekIn = cmds.shadingNode ('plusMinusAverage', asUtility = 1, n = 'cheekXIn_sum')
    midCheekMult = cmds.shadingNode ( 'multiplyDivide', asUtility=True, n = "midCheekIn" )
    loCheekMult = cmds.shadingNode ( 'multiplyDivide', asUtility=True, n = "loCheekIn" )
    #midCheek in plus 
    cmds.connectAttr( "lowJaw_dir.ty", midCheekMult +".input1X" )
    cmds.connectAttr( "cheekFactor.midCheek_in", midCheekMult +".input2X" )
    cmds.connectAttr( midCheekMult +".outputX",  tySum_cheekIn+".input3D[0].input3Dx" )
    cmds.connectAttr( "jaw_UDLR.ty", midCheekMult +".input1Y" )
    cmds.connectAttr( "cheekFactor.midCheek_in", midCheekMult +".input2Y" )
    cmds.connectAttr( midCheekMult +".outputY", tySum_cheekIn+".input3D[1].input3Dx" )
    cmds.connectAttr( "swivel_ctrl.ty", midCheekMult +".input1Z" )
    cmds.connectAttr( "cheekFactor.midCheek_in", midCheekMult +".input2Z" )
    cmds.connectAttr(  midCheekMult +".outputZ", tySum_cheekIn+".input3D[2].input3Dx" )

    #loCheek in plus 
    cmds.connectAttr( "lowJaw_dir.ty", loCheekMult +".input1X" )
    cmds.connectAttr( "cheekFactor.loCheek_in", loCheekMult +".input2X" )
    cmds.connectAttr( loCheekMult +".outputX",  tySum_cheekIn+".input3D[0].input3Dy" )
    cmds.connectAttr( "jaw_UDLR.ty", loCheekMult +".input1Y" )
    cmds.connectAttr( "cheekFactor.loCheek_in", loCheekMult +".input2Y" )
    cmds.connectAttr( loCheekMult +".outputY", tySum_cheekIn+".input3D[1].input3Dy" )
    cmds.connectAttr( "swivel_ctrl.ty", loCheekMult +".input1Z" )
    cmds.connectAttr( "cheekFactor.loCheek_in", loCheekMult +".input2Z" )
    cmds.connectAttr(  loCheekMult +".outputZ", tySum_cheekIn+".input3D[2].input3Dy" )

    #reverse to right side
    cheekIn_reverse = cmds.shadingNode ('multiplyDivide', asUtility = 1, n = 'cheekTX_reverse')
    cmds.connectAttr( tySum_cheekIn + '.output3Dx', cheekIn_reverse + '.input1X' )
    cmds.connectAttr( tySum_cheekIn + '.output3Dy', cheekIn_reverse + '.input1Y' )
    cmds.setAttr ( cheekIn_reverse + '.input2', -1,-1,-1 )
    
    midCheekRX = [ 'l_midCheekRotX', 'r_midCheekRotX' ]
    loCheekRX = [ 'l_loCheekRotX', 'r_loCheekRotX' ]    
    for cheek in midCheekRX + loCheekRX:
        cheek_sum = cmds.shadingNode ( 'plusMinusAverage', asUtility= True, n = cheek[ :-4] + '_sum' )
        lowCheek_sum = cheek[:2] +"lowCheekMinus"
        cheekRx_addD = cmds.shadingNode ( 'addDoubleLinear', asUtility= True, n = cheek[ :-4] + '_add' )
        cmds.connectAttr ( swivelTranXMult + '.outputX', cheek_sum + '.input3D[0].input3Dx' )
        cmds.connectAttr ( cheek_sum + '.output3Dx', cheek + '.tx' ) # swivel.tx        
        cmds.connectAttr ( swivelTranYMult + '.outputY', cheek_sum + '.input3D[0].input3Dy' )
        cmds.connectAttr ( jawCloseTranMult + '.outputY', cheek_sum + '.input3D[1].input3Dy' ) #jaw_UDLRIO.ty --> jawClose_jnt.ty 
        cmds.connectAttr ( cheek_sum + '.output3Dy', cheek + '.ty' ) # swivel.ty   
        cmds.connectAttr ( swivelTranXMult + '.outputY', cheek_sum + '.input3D[0].input3Dz' )
        cmds.connectAttr ( jawCloseRotMult + '.outputY', cheek_sum + '.input3D[1].input3Dz' ) # jawClose_jnt.ry <--jawOpen.tx *(jawOpen_jawCloseRY) 
        cmds.connectAttr ( cheek_sum + '.output3Dz', cheek + '.ry' ) # swivel.tx
        cmds.connectAttr ( swivelTranXMult + '.outputZ', cheek + '.rz' ) # swivel.tx
        cmds.connectAttr ( jawCloseRotMult + '.outputX', cheekRx_addD + '.input1') #'jawClose_jnt.rx' <--'lowJaw_dir.ty'          
        cmds.connectAttr ( jawCloseTranMult + '.outputX', cheek + '.tz' )  #jaw_UDLRIO.tx --> jawClose_jnt.tz
        
        if 'l_mid' in cheek:
            cmds.connectAttr( tySum_cheekIn + '.output3Dx',  cheek_sum + '.input3D[1].input3Dx')
            cmds.connectAttr ( mouthTyMult + '.outputY', cheekRx_addD + '.input2')
            cmds.connectAttr ( cheekRx_addD + '.output', cheek + '.rx' )            
        elif 'r_mid' in cheek:
            cmds.connectAttr(  cheekIn_reverse + '.outputX',  cheek_sum + '.input3D[1].input3Dx')
            cmds.connectAttr ( mouthTyMult + '.outputY', cheekRx_addD + '.input2')
            cmds.connectAttr ( cheekRx_addD + '.output', cheek + '.rx' )# jawClose_jnt.rx <-- jawOpen.ty *(jawOpen_jawCloseRX)  
            
        elif 'l_lo' in cheek:
            cmds.connectAttr( tySum_cheekIn + '.output3Dy',  lowCheek_sum + '.input3D[4].input3Dx')
        else:
            cmds.connectAttr(  cheekIn_reverse + '.outputY',  lowCheek_sum + '.input3D[4].input3Dx')
            









'''individual lip curves setup ('upJawOpen_crv', 'upTyLip_crv’(UDLR) )
select upLip curves that need joints control ('upJawOpen_crv', 'upUDLR_crv'...)
??? ???? ?? ??? ???? ? ?? ??: ?? ?? ?? ???? ???  ???? ?????? ??'''

import maya.cmds as cmds  
def indiCrvSetup(name):

    upCrv = 'up'+ name + '_crv'
    loCrv = 'lo'+ name + '_crv'
    crvShape = cmds.listRelatives ( upCrv, c=1, type = 'nurbsCurve')
    upCVs = cmds.ls ( upCrv + '.cv[*]', fl = 1 )
    loCVs = cmds.ls ( loCrv + '.cv[*]', fl = 1 )
    cvNum = len ( upCVs ) 
       
    lipCrvStartPos = cmds.xform (upCVs[0], q=1, ws =1, t = 1 )
    lipCrvEndPos = cmds.xform (upCVs[cvNum-1], q=1, ws =1, t = 1 )
    nCrvPoc = cmds.shadingNode ( 'pointOnCurveInfo', asUtility =True, n = 'cnt' + name + '_poc' )
    cmds.connectAttr ( crvShape[0]+'.worldSpace',  nCrvPoc + '.inputCurve')   
    cmds.setAttr ( nCrvPoc + '.turnOnPercentage', 1 )    
    cmds.setAttr ( nCrvPoc + '.parameter', .5)
    lipCrvMidPos = cmds.getAttr( nCrvPoc + '.position')
    
    lipCrvStart = cmds.group (em = 1, n = name + 'Start_grp' )
    cmds.xform ( lipCrvStart, ws = 1, t = lipCrvStartPos )
    rCorner = cmds.joint ( n= 'rCorner'+ name+'_jnt', p= lipCrvStartPos )
    
    uplipCrvMid = cmds.group (em = 1, n = 'up' + name + 'Mid_grp' ) 
    cmds.xform ( uplipCrvMid, ws = 1, t = list(lipCrvMidPos[0]) ) 
    midUpJnt = cmds.joint ( n = 'cntUp' + name + '_jnt', relative = True, p = [ 0, 0, 0] )  

    lolipCrvMid = cmds.group (em = 1, n = 'lo' + name + 'Mid_grp' ) 
    cmds.xform ( lolipCrvMid, ws = 1, t = list(lipCrvMidPos[0]) ) 
    midLoJnt = cmds.joint ( n = 'cntLo' + name + '_jnt', relative = True, p = [ 0, 0, 0] )

    lipCrvEnd = cmds.group (em = 1, n = name + 'End_grp' ) 
    cmds.xform ( lipCrvEnd, ws = 1, t = lipCrvEndPos ) 
    lCorner = cmds.joint ( n= 'lCorner' + name + '_jnt', relative = True, p = [ 0, 0, 0] )  

    indiGrp = cmds.group ( lipCrvStart, uplipCrvMid, lolipCrvMid, lipCrvEnd, upCrv, loCrv, n = name + '_indiGrp' ) 
    cmds.parent (indiGrp, 'upLipCrv_grp' )

    #skinning
    upSkin = cmds.skinCluster ( rCorner, midUpJnt, lCorner, upCrv, toSelectedBones = 1 )    
    loSkin = cmds.skinCluster ( rCorner, midLoJnt, lCorner, loCrv, toSelectedBones = 1 )
    

    numVal = { 0: 0.15, 1:0.85, 2:0.98, 4: 0.98, 5:0.85, 6:0.15 }
    for key, val in numVal.items():    
        cmds.skinPercent ( upSkin[0], upCVs[key], tv = ( midUpJnt, val) )
        cmds.skinPercent ( loSkin[0], loCVs[key], tv = ( midLoJnt, val) )         
    
    ctlCrvs = { "JawOpen":"lowJaw_dir", "TyLip":"jaw_UDLR" }
    if name in ctlCrvs.keys():
        cornerMult = cmds.shadingNode ( 'multiplyDivide', asUtility=True, n = name +'Corner_mult' )
        dampMult = cmds.shadingNode ( 'multiplyDivide', asUtility=True, n = name + 'damp_mult' )
        txAvg = cmds.shadingNode ( 'plusMinusAverage', asUtility=True, n = name + 'TX_plus')
        #endAvg = cmds.shadingNode ( 'plusMinusAverage', asUtility=True, n = name + 'TY' + str(index) +'_plus')
        # corner tx value
        cmds.connectAttr ( midLoJnt+ '.tx', cornerMult+ '.input1X' )  
        cmds.connectAttr ( midLoJnt+ '.ty', cornerMult+ '.input1Y' )  
        cmds.connectAttr ( midLoJnt+ '.ty', cornerMult+ '.input1Z' )  
        
        cmds.setAttr ( cornerMult + '.input2X', .5)#lipCorners.tx follow midLoJnt.tx
        cmds.setAttr ( cornerMult + '.input2Y', .06)#lipLCorner.tx inner when jaw open 
        cmds.setAttr ( cornerMult + '.input2Z', -.06)#lipRCorner.tx inner when jaw open
        
        cmds.connectAttr ( cornerMult + '.outputY', txAvg + '.input3D[0].input3Dy' )
        cmds.connectAttr ( cornerMult + '.outputZ', txAvg + '.input3D[0].input3Dz' )
        cmds.connectAttr ( cornerMult + '.outputX', txAvg + '.input3D[1].input3Dy' )
        cmds.connectAttr ( cornerMult + '.outputX', txAvg + '.input3D[1].input3Dz' )
        cmds.connectAttr ( txAvg + '.output3Dy', lCorner + '.tx' )
        cmds.connectAttr ( txAvg + '.output3Dz', rCorner + '.tx' )
        
        # corner ty value
        cmds.connectAttr ( midLoJnt+ '.tx', dampMult + '.input1X' )  
        cmds.connectAttr ( midLoJnt+ '.ty', dampMult + '.input1Y' )  
        cmds.connectAttr ( midLoJnt+ '.ty', dampMult + '.input1Z' ) 
        
        cmds.setAttr ( dampMult+ '.input2X', .1) # lipCenter.tx follow jaw
        cmds.setAttr ( dampMult+ '.input2Y', .5) # lipCorners.ty follow jaw
        cmds.setAttr ( dampMult+ '.input2Z', .01) # lipCenter.ty follow jaw
        
        cmds.connectAttr ( dampMult + '.outputX',  midUpJnt+'.tx')
        cmds.connectAttr ( dampMult + '.outputZ',  midUpJnt+'.ty')
        cmds.connectAttr ( dampMult + '.outputY',  lCorner+'.ty')
        cmds.connectAttr ( dampMult + '.outputY',  rCorner+'.ty')        
        # connect curve joint with controller 
        '''cmds.connectAttr ( ctlCrvs[name] + '.tx', midLoJnt + '.tx')
        cmds.connectAttr ( ctlCrvs[name] + '.ty', midLoJnt + '.ty')
        cmds.connectAttr ( ctlCrvs[name] + '.tz', midLoJnt + '.tz')'''
    return midLoJnt







    
    
    

def bridgeJoints():    
    
    jawRigPos = cmds.xform('jawRigPos', q =1, ws =1, t=1 )
    lipYPos = cmds.xform('lipYPos', q =1, ws =1, t=1 ) 
    # ear / nose joint
    lEarP = cmds.group ( n = 'l_earP', em =True, p = "l_ear_grp" )
    cmds.xform (lEarP, relative = True, t = [ 0, 0, 0] )
    lEarJnt = cmds.joint(n = 'l_ear_jnt', relative = True, p = [ 0, 0, 0] ) 
    rEarP = cmds.group ( n = 'r_earP', em =True, p = "r_ear_grp" )
    cmds.xform (rEarP, relative = True, t = [ 0, 0, 0]  )
    rEarJnt = cmds.joint(n = 'r_ear_jnt', relative = True, p = [ 0, 0, 0] ) 
    
    noseP = cmds.group ( n = 'noseP', em =True, p = "noseRig" )
    cmds.xform (noseP, relative = True, t = [ 0, 0, 0] )
    noseJnt = cmds.joint(n = 'nose_jnt', relative = True, p = [ 0, 0, 0] ) 
    
    # cheek joint - check the cheek/squintPush group and angle
    lCheekP = cmds.group ( n = 'l_cheekP', em =True, p = "l_cheek_grp" )
    cmds.xform (lCheekP, relative = True, t = [ 0, 0, 0] )
    lUpCheekP = cmds.duplicate ( lCheekP, n = 'l_upCheekP' )
    cmds.parent( lUpCheekP[0], lCheekP )
    lUpCheekJnt = cmds.joint(n = 'l_upCheek_jnt', relative = True, p = [ 0, 0, 0] )
    
    lMidCheekP = cmds.duplicate ( lUpCheekP, po =1, n = 'l_midCheekP' )
    lMidCheekRotY = cmds.group( lMidCheekP, n= 'l_midCheekRotY', p = lCheekP )
    cmds.xform( lMidCheekRotY, piv =lipYPos, ws =1 )
    lMidCheekRotX = cmds.group( lMidCheekRotY, n= 'l_midCheekRotX', p = lCheekP )
    cmds.xform( lMidCheekRotX, piv =jawRigPos, ws =1 )
    cmds.select( lMidCheekP[0] )
    lMidCheekJnt = cmds.joint(n = 'l_midCheek_jnt', relative = True, p = [ 0, 0, 0] ) 
       
    rCheekP = cmds.group ( n = 'r_cheekP', em =True, p = "r_cheek_grp" )    
    cmds.xform (rCheekP, relative = True, t = [ 0, 0, 0] )
    rUpCheekP = cmds.duplicate ( rCheekP, n = 'r_upCheekP' )
    cmds.parent( rUpCheekP[0], rCheekP )   
    rUpCheekJnt = cmds.joint(n = 'r_upCheek_jnt', relative = True, p = [ 0, 0, 0] )
    
    rMidCheekP = cmds.duplicate ( rUpCheekP, po =1, n = 'r_midCheekP' )
    rMidCheekRotY = cmds.group( rMidCheekP, n= 'r_midCheekRotY', p = rCheekP )
    cmds.xform( rMidCheekRotY, piv =lipYPos, ws =1 )
    rMidCheekRotX = cmds.group( rMidCheekRotY, n= 'r_midCheekRotX', p = rCheekP )
    cmds.xform( rMidCheekRotX, piv =jawRigPos, ws =1 )
    cmds.select( rMidCheekP[0])
    rMidCheekJnt = cmds.joint(n = 'r_midCheek_jnt', relative = True, p = [ 0, 0, 0] ) 
    
    # squintPuff joint
    lSqiuntPuff = cmds.group ( n = 'l_squintPuffP', em =True, p = "l_squintPuff_grp" )
    cmds.xform (lSqiuntPuff, relative = True, t = [ 0, 0, 0] )
    lSqiuntPuffJnt = cmds.joint(n = 'l_squintPuff_jnt', relative = True, p = [ 0, 0, 0] ) 
    rSquintPuff = cmds.group ( n = 'r_squintPuffP', em =True, p = "r_squintPuff_grp" )
    cmds.xform (rSquintPuff, relative = True, t = [ 0, 0, 0])
    rSqiuntPuffJnt = cmds.joint(n = 'r_squintPuff_jnt', relative = True, p = [ 0, 0, 0] ) 
    
    #lowCheek joint
    lLowCheek = cmds.group ( n = 'l_lowCheekP', em =True, p = "l_lowCheek_grp" )
    cmds.xform (lLowCheek, relative = True, t = [ 0, 0, 0] )
    lLoCheekRotY = cmds.group( lLowCheek, n= 'l_loCheekRotY', p = "l_lowCheek_grp" )
    cmds.xform( lLoCheekRotY, piv =lipYPos, ws =1 )
    lLoCheekRotX = cmds.group( lLoCheekRotY, n= 'l_loCheekRotX', p = "l_lowCheek_grp" )
    cmds.xform( lLoCheekRotX, piv =jawRigPos, ws =1 )
    cmds.select( lLowCheek )    
    lLowCheekJnt = cmds.joint(n = 'l_lowCheek_jnt', relative = True, p = [ 0, 0, 0] ) 
    
    rLowCheek = cmds.group ( n = 'r_lowCheekP', em =True, p = "r_lowCheek_grp" )
    cmds.xform (rLowCheek,  relative = True, t = [ 0, 0, 0]  )
    rLoCheekRotY = cmds.group( rLowCheek, n= 'r_loCheekRotY', p = "r_lowCheek_grp" )
    cmds.xform( rLoCheekRotY, piv =lipYPos, ws =1 )
    rLoCheekRotX = cmds.group( rLoCheekRotY, n= 'r_loCheekRotX', p = "r_lowCheek_grp" )
    cmds.xform( rLoCheekRotX, piv =jawRigPos, ws =1 )
    cmds.select( rLowCheek )
    rLowCheekJnt = cmds.joint(n = 'r_lowCheek_jnt', relative = True, p = [ 0, 0, 0] ) 
    
    
    

    


'''
create lip joints and lip curves (create up/loLip_grp, up/loLipCrv_grp)
'''
def mouthJoint( upLow ): 

    vtxs =cmds.ls(sl=1 , fl=1)
    myList = {}
    index = 0
    for i in vtxs:        
        xyz = cmds.xform ( i, q =1, ws =1, t =1 )
        myList[ i ] = xyz[0]
    
    orderedVerts = sorted(myList, key = myList.__getitem__)    
    vNum = len(vtxs) 
    lipEPos = cmds.xform( 'lipEPos', t = True, q = True, ws = True )
    lipWPos = [-lipEPos[0], lipEPos[1], lipEPos[2]] 
    lipNPos = cmds.xform( 'lipNPos', t = True, q = True, ws = True ) 
    lipSPos = cmds.xform( 'lipSPos', t = True, q = True, ws = True ) 
    lipYPos = cmds.xform( 'lipYPos', t = True, q = True, ws = True ) 
    JawRigPos = cmds.xform( 'jawRigPos', t = True, q = True, ws = True )
    cheekPos = cmds.xform( 'cheekPos', t = True, q = True, ws = True)
    squintPuffPos = cmds.xform( 'squintPuffPos', t = True, q = True, ws = True)
    lowCheekPos = cmds.xform( 'lowCheekPos', t = True, q = True, ws = True) 
 
    if upLow == "up":
        lipCntPos = lipNPos
        min = 0
        max = vNum 
            
    elif upLow == "lo":
        lipCntPos = lipSPos
        min = 1
        max = vNum -1   
    # create lip joint guide curve
    tempCrv = cmds.curve ( d= 3, ep= [(-lipEPos[0], lipEPos[1], lipEPos[2]), ( lipCntPos ), (lipEPos)] ) 
    guideCrv = cmds.rename ( tempCrv, upLow + "Guide_crv" )
    guideCrvShape = cmds.listRelatives ( guideCrv, c = True ) 
    cmds.rebuildCurve ( guideCrv, d = 3, rebuildType = 0, keepRange = 0) 
    
    # final lip shape ctrl curve
    lipCrvGrp = cmds.group ( n = upLow +'LipCrv_grp', em =True, p = 'faceMain|crv_grp' ) 
    templipCrv = cmds.curve ( d = 3, p =([0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0])) 
    cmds.rebuildCurve ( rt = 0, d = 3, kr = 0, s = 4 )    
    lipCrv = cmds.rename (templipCrv, upLow +'Lip_crv')
    lipCrvShape = cmds.listRelatives ( lipCrv, c = True )
    cmds.parent ( lipCrv, lipCrvGrp )
    
    # lip curve for LipJotX tx,ty for UDLR ctrl
    tempTyCrv = cmds.curve ( d = 3, p =([0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0])) 
    cmds.rebuildCurve ( rt = 0, d = 3, kr = 0, s = 4 )    
    tyLipCrv = cmds.rename ( tempTyCrv, upLow +'TyLip_crv') 
    tylipCrvShape = cmds.listRelatives ( tyLipCrv, c = True ) 
    cmds.parent ( tyLipCrv, lipCrvGrp )

    # lipTarget curve shape
    jawOpenCrv = cmds.duplicate ( lipCrv, n= upLow +'JawOpen_crv') 
    lLipWideCrv = cmds.duplicate ( lipCrv, n= 'l_'+ upLow +'lipWide_crv')
    rLipWideCrv = cmds.duplicate ( lipCrv, n= 'r_'+ upLow +'lipWide_crv') 
    LRCurve_mirror( lLipWideCrv[0], rLipWideCrv[0])
    cmds.hide(rLipWideCrv[0])
    lLipECrv = cmds.duplicate ( lipCrv, n= 'l_'+ upLow +'lipE_crv')
    rLipECrv = cmds.duplicate ( lipCrv, n= 'r_'+ upLow +'lipE_crv') 
    LRCurve_mirror( lLipECrv[0], rLipECrv[0])
    cmds.hide(rLipECrv[0])
    lUCrv = cmds.duplicate ( lipCrv, n= 'l_'+upLow +'U_crv') 
    rUCrv = cmds.duplicate ( lipCrv, n= 'r_'+upLow +'U_crv')
    LRCurve_mirror( lUCrv[0], rUCrv[0])
    cmds.hide(rUCrv[0])
    lOCrv = cmds.duplicate ( lipCrv, n= 'l_'+upLow +'O_crv') 
    rOCrv = cmds.duplicate ( lipCrv, n= 'r_'+upLow +'O_crv')
    LRCurve_mirror( lOCrv[0], rOCrv[0])
    cmds.hide(rOCrv[0])
    lHappyCrv = cmds.duplicate ( lipCrv, n= 'l_'+upLow +'Happy_crv')
    rHappyCrv = cmds.duplicate ( lipCrv, n= 'r_'+upLow +'Happy_crv')
    LRCurve_mirror( lHappyCrv[0], rHappyCrv[0]) 
    cmds.hide(rHappyCrv[0]) 
    lSadCrv = cmds.duplicate ( lipCrv, n= 'l_'+upLow +'Sad_crv')
    rSadCrv = cmds.duplicate ( lipCrv, n= 'r_'+upLow +'Sad_crv')
    LRCurve_mirror( lSadCrv[0], rSadCrv[0]) 
    cmds.hide(rSadCrv[0]) 
    lipCrvBS = cmds.blendShape ( jawOpenCrv[0], lLipECrv[0],rLipECrv[0], lLipWideCrv[0],rLipWideCrv[0], lUCrv[0],rUCrv[0], lOCrv[0],rOCrv[0], lHappyCrv[0],rHappyCrv[0], lSadCrv[0],rSadCrv[0], lipCrv, n =upLow + 'LipCrvBS')
    cmds.blendShape( lipCrvBS[0], edit=True, w=[(0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1),(9, 1), (10, 1), (11, 1), (12, 1)])   
    
    # lip freeform Ctrls curve( different number of points (4), so can not be target of the blendShape)      
    templipCtlCrv = cmds.curve ( d = 3, p =([0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0])) 
    cmds.rebuildCurve ( rt = 0, d = 3, kr = 0, s = 4)   
    lipCtlCrv = cmds.rename ( templipCtlCrv, upLow +'LipCtl_crv')
    lipCtlCrvShape = cmds.listRelatives ( lipCtlCrv, c = True ) 
    cmds.parent (lipCtlCrv, lipCrvGrp) 
    
    # lip Roll control curve shape ( different number of points (4), so can not be target of the blendShape)      
    tempRollCrv = cmds.curve ( d = 3, p =([0,0,0],[0.25,0,0],[0.5,0,0],[0.75,0,0],[1,0,0])) 
    cmds.rebuildCurve ( rt = 0, d = 3, kr = 0, s = 2 )   
    lipRollCrv = cmds.rename ( templipCtlCrv, upLow +'LipRoll_crv')  
    lipRollCrvShape = cmds.listRelatives ( lipRollCrv, c = True ) 
    cmds.parent ( lipRollCrv, lipCrvGrp) 
    
    #lip RollYZ control curve shape
    lipRollYZCrv = cmds.duplicate ( lipRollCrv, n= upLow +'RollYZ_crv')
    lipRollYZCrvShape = cmds.listRelatives ( lipRollYZCrv, c = True )
    
    if not cmds.objExists('cheekCrv_grp'):
        cheekCrvGrp = cmds.group ( n = 'cheekCrv_grp', em =True, p = 'faceMain|crv_grp' ) 
       
        cheekTempCrv = cmds.curve ( d=1, p = [(lowCheekPos), (lipEPos), (cheekPos), (squintPuffPos)] ) 
        lCheekCrv = cmds.rename ( cheekTempCrv, "l_cheek_crv" )
        rCheekCrv = cmds.duplicate ( lCheekCrv, n= 'r_cheek_crv')
        cmds.setAttr ( rCheekCrv[0] + '.scaleX', -1)
        cmds.parent(lCheekCrv,rCheekCrv, 'faceMain|crv_grp|cheekCrv_grp')
        cmds.xform (lCheekCrv,rCheekCrv, centerPivots = 1)    
        
        lHappyCheekCrv = cmds.duplicate ( lCheekCrv, n= 'l_happyCheek_crv')
        rHappyCheekCrv = cmds.instance ( lHappyCheekCrv, n= 'r_happyCheek_crv')
        #cmds.parent ( lHappyCheekCrv, rHappyCheekCrv, 'HappyCrv_grp')
        lWideCheekCrv = cmds.duplicate ( lCheekCrv, n= 'l_wideCheek_crv')
        rWideCheekCrv = cmds.instance ( lWideCheekCrv, n= 'r_wideCheek_crv')
        #cmds.parent ( lWideCheekCrv, rWideCheekCrv, 'WideCrv_grp')
        lECheekCrv = cmds.duplicate ( lCheekCrv, n= 'l_eCheek_crv')
        rECheekCrv = cmds.instance ( lECheekCrv, n= 'r_eCheek_crv')
        
        lSadCheekCrv = cmds.duplicate ( lCheekCrv, n= 'l_sadCheek_crv')
        rSadCheekCrv = cmds.instance ( lSadCheekCrv, n= 'r_sadCheek_crv')
        #cmds.parent ( lSadCheekCrv, rSadCheekCrv, 'SadCrv_grp')
        lUCheekCrv = cmds.duplicate ( lCheekCrv, n= 'l_uCheek_crv')
        rUCheekCrv = cmds.instance ( lUCheekCrv, n= 'r_uCheek_crv')
        #cmds.parent ( lUCheekCrv, rUCheekCrv, 'UCrv_grp')
        lOCheekCrv = cmds.duplicate ( lCheekCrv, n= 'l_oCheek_crv')
        rOCheekCrv = cmds.instance ( lOCheekCrv, n= 'r_oCheek_crv')
        #cmds.parent ( lOCheekCrv, rOCheekCrv, 'OCrv_grp')
        
        lCheekBS = cmds.blendShape ( lHappyCheekCrv[0],lWideCheekCrv[0],lECheekCrv[0],lSadCheekCrv[0],lUCheekCrv[0],lOCheekCrv[0], lCheekCrv, n ='lCheekBS')
        cmds.blendShape( lCheekBS[0], edit=True, w=[(0, 1), (1, 1), (2, 1), (3,1), (4,1), (5,1)])  
        rCheekBS = cmds.blendShape ( rHappyCheekCrv[0],rWideCheekCrv[0],rECheekCrv[0],rSadCheekCrv[0],rUCheekCrv[0],rOCheekCrv[0], rCheekCrv, n ='rCheekBS')
        cmds.blendShape( rCheekBS[0], edit=True, w=[(0, 1), (1, 1), (2, 1), (3,1), (4,1), (5,1)])   
        cmds.move ( 2,0,0, lHappyCheekCrv, lWideCheekCrv, lSadCheekCrv, lECheekCrv, lUCheekCrv[0], lOCheekCrv, rotatePivotRelative = 1  )
        cmds.move (-2,0,0, rHappyCheekCrv, rWideCheekCrv, rSadCheekCrv, rECheekCrv, rUCheekCrv[0], rOCheekCrv, rotatePivotRelative = 1  )
        #attach ctrls to main cheek curves
    
    if not cmds.objExists('cheekWorld'):
        cheekSetup()
        
    # create lip joints parent group
    lipJotGrp = cmds.group ( n = upLow + 'Lip_grp', em =True ) 
    cmds.parent ( lipJotGrp, 'lipJotP' )
    cmds.xform (lipJotGrp, ws = 1, t = JawRigPos ) 
    # delete detail lip ctrls 
    lipDetailP = upLow + 'LipDetailGrp' 
    kids = cmds.listRelatives (lipDetailP, ad=True, type ='transform')   
    if kids:
        cmds.delete (kids)

    vPos = []
    for v in range(vNum): 
        voc = cmds.xform (orderedVerts[v], t =1, q=1, ws = 1)
        vPos.append(voc)
    vrtsDist = []
    for p in range (0, vNum-1 ):
        vDist = distance( vPos[p], vPos[p+1])
        vrtsDist.append(vDist)
    vrtsDist.insert(0,0)
    vLength = sum( vrtsDist )
    
    linearDist = 1.0/(vNum-1)
    distSum = 0.0
    for i in range (min, max ):
        distSum += vrtsDist[i]
        increment = distSum / vLength               
        poc = cmds.shadingNode ( 'pointOnCurveInfo', asUtility =True, n = upLow + 'Lip' + str(i) + '_poc' )
        cmds.connectAttr ( guideCrvShape[0]+'.worldSpace',  poc + '.inputCurve')   
        cmds.setAttr ( poc + '.turnOnPercentage', 1 )    
        cmds.setAttr ( poc + '.parameter', increment )        
        #create detail lip ctrl        
        if i==0 or i== vNum-1:
            corners = createLipJoint( upLow, JawRigPos, lipYPos, poc, lipJotGrp, i )
            print corners
            createDetailCtl( upLow, i )
            cmds.parent ( upLow +'LipDetailP'+ str(i), lipDetailP )
            cmds.setAttr (upLow +'LipDetailP'+ str(i)+'.tx', linearDist*i )
            cmds.setAttr (upLow +'LipDetailP'+ str(i)+'.ty', -1.5 )
            cmds.setAttr (upLow +'LipDetailP'+ str(i)+'.tz', 0 )
            cmds.setAttr (upLow +'LipDetailP'+ str(i)+'.sx', 0.25 )
        else:
            createLipJoint( upLow, JawRigPos, lipYPos, poc, lipJotGrp, i ) 
            createDetailCtl( upLow, i )           
            cmds.parent ( upLow +'LipDetailP'+ str(i), lipDetailP )
            cmds.setAttr (upLow +'LipDetailP'+ str(i) + '.tx', linearDist*i ) 
            cmds.setAttr (upLow +'LipDetailP'+ str(i) + '.ty', 0 )
            cmds.setAttr (upLow +'LipDetailP'+ str(i) + '.tz', 0 )
            
        # create lipCtrl curve POC
        lipCrvPoc = cmds.shadingNode ( 'pointOnCurveInfo', asUtility =True, n = upLow +'LipCrv' + str(i) + '_poc' )
        cmds.connectAttr ( lipCrvShape[0] + ".worldSpace",  lipCrvPoc + '.inputCurve')   
        cmds.setAttr ( lipCrvPoc  + '.turnOnPercentage', 1 )    
        cmds.setAttr ( lipCrvPoc  + '.parameter', increment )
        
        lipTYPoc = cmds.shadingNode ( 'pointOnCurveInfo', asUtility =True, n = upLow +'LipTy' + str(i) + '_poc' )
        cmds.connectAttr ( tylipCrvShape[0] + ".worldSpace",  lipTYPoc + '.inputCurve')
        cmds.setAttr ( lipTYPoc  + '.turnOnPercentage', 1 )    
        cmds.setAttr ( lipTYPoc  + '.parameter', increment ) 
                
        # create lipCtrl curve POC
        ctlPoc = cmds.shadingNode ( 'pointOnCurveInfo', asUtility =True, n = upLow +'LipCtl' + str(i) + '_poc' )
        cmds.connectAttr ( lipCtlCrvShape[0] + ".worldSpace",  ctlPoc + '.inputCurve')   
        cmds.setAttr ( ctlPoc  + '.turnOnPercentage', 1 )    
        cmds.setAttr ( ctlPoc  + '.parameter', increment ) 
        
        # create lipRoll curve POC  lipRollCrv, lipRollYZCrv
        lipRollPoc = cmds.shadingNode ( 'pointOnCurveInfo', asUtility =True, n = upLow +'LipRoll' + str(i) + '_poc'  )
        cmds.connectAttr ( lipRollCrvShape[0] + ".worldSpace",  lipRollPoc + '.inputCurve')  
        cmds.setAttr ( lipRollPoc + '.turnOnPercentage', 1 )   
        cmds.setAttr ( lipRollPoc + '.parameter', increment ) 
        
        lipRollYZPoc = cmds.shadingNode ( 'pointOnCurveInfo', asUtility =True, n = upLow +'LipRollYZ' + str(i) + '_poc'  )
        cmds.connectAttr ( lipRollYZCrvShape[0] + ".worldSpace",  lipRollYZPoc + '.inputCurve')  
        cmds.setAttr ( lipRollYZPoc  + '.turnOnPercentage', 1 )   
        cmds.setAttr ( lipRollYZPoc  + '.parameter', increment )


        


        
        
        
def setLipJntLabel():
    upJntY = cmds.ls('upLipY*_jnt', fl=1, type = 'joint')
    loJntY = cmds.ls('loLipY*_jnt', fl=1, type = 'joint')
    upJntNum = len(upJntY)
    loJntNum = len(loJntY)
    rightUp = upJntY[0:upJntNum/2]
    leftUp = upJntY[upJntNum/2+1: ]
    rightLo =loJntY[0: loJntNum/2] 
    leftLo = loJntY[loJntNum/2+1: ]
    leftLo.reverse()
    rightUp.reverse()
    leftJnt = leftUp + leftLo
    rightJnt = rightUp + rightLo
    cntJnt =[ upJntY[upJntNum/2], loJntY[loJntNum/2] ]
    for i, j in enumerate(leftJnt):
        cmds.setAttr(j + '.side', 1)
        cmds.setAttr(j + '.type', 18)
        cmds.setAttr(j + '.otherType', str(i).zfill(2), type = "string")
    for id, k in enumerate(rightJnt):
        cmds.setAttr(k + '.side', 2)
        cmds.setAttr(k + '.type', 18)
        cmds.setAttr(k + '.otherType', str(id).zfill(2), type = "string")    


        

        
        
def cheekSetup():        
    cheekWorld = cmds.group (em =1, n= 'cheekWorld', p ='supportRig')
    inverseMatrix = cmds.shadingNode('decomposeMatrix', asUtility=1, n = 'inverseMat' )
    cmds.connectAttr( 'headSkel.worldInverseMatrix', inverseMatrix + '.inputMatrix' )
    cmds.connectAttr( inverseMatrix + '.outputTranslate', cheekWorld + '.translate' )
    cmds.connectAttr( inverseMatrix + '.outputRotate', cheekWorld + '.rotate' )
    cmds.connectAttr( inverseMatrix + '.outputScale', cheekWorld + '.scale' )
    cmds.connectAttr( inverseMatrix + '.outputShear', cheekWorld + '.shear' )
    for LR in ['l','r']:
        cvLs = cmds.ls( LR + '_cheek_crv.cv[*]', fl = 1 )
        cvLen = len(cvLs)
        lipCorner = cmds.group (em =1, n= LR+'_lipCorner', p ='supportRig')    
        cheekList = [LR + '_lowCheek_grp', lipCorner, LR + '_cheek_grp', LR + '_squintPuff_grp']        
        cmds.parent (cheekList, cheekWorld)
        
        for v in range(0, cvLen):
            cheekPoc = cmds.shadingNode ( 'pointOnCurveInfo', asUtility =True, n = 'cheek' + str(v) + '_poc' )
            cmds.connectAttr ( LR+'_cheek_crvShape.worldSpace', cheekPoc + '.inputCurve')  
            cmds.setAttr (cheekPoc + '.parameter', v )      	 
            cmds.connectAttr (cheekPoc + '.positionX', cheekList[v] + '.tx')
            cmds.connectAttr (cheekPoc + '.positionY', cheekList[v] + '.ty')
            cmds.connectAttr (cheekPoc + '.positionZ', cheekList[v] + '.tz')        
        
        



import math
def distance(inputA=[1,1,1], inputB=[2,2,2]):
    return math.sqrt(pow(inputB[0]-inputA[0], 2) + pow(inputB[1]-inputA[1], 2) + pow(inputB[2]-inputA[2], 2))


'''
mirror left curve(cvs) to right curve(cvs), all curves are from 0 to +x
'''
def LRCurve_mirror( lCrv, rCrv):

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
        


import re
import maya.cmds as cmds
def LRBlendShapeWeight( lipCrv, lipCrvBS ):
   cvs = cmds.ls ( lipCrv+'.cv[*]', fl =1)
   length = len (cvs)
 
   increment = 1.0/(length-1)
   targets = cmds.aliasAttr( lipCrvBS, q=1)
   tNum = len(targets)
  
   for i in range(0, length):
              
       for t in range(0, tNum, 2):           
           if lipCrv[:2]+'L' in targets[t]:
               indexL=re.findall('\d+', targets[t+1])
               cmds.setAttr ( lipCrvBS + '.inputTarget[0].inputTargetGroup[%s].targetWeights[%s]'%(str(indexL[0]), str(i)), increment*i )      
 
           elif lipCrv[:2]+'R' in targets[t]:
               indexR =re.findall('\d+', targets[t+1])
               cmds.setAttr ( lipCrvBS + '.inputTarget[0].inputTargetGroup[%s].targetWeights[%s]'%(str(indexR[0]), str(i)), 1-increment*i )






def createLipJoint( upLow, JawRigPos, lipYPos, poc, lipJotGrp, i):   

    lipJotX  = cmds.group( n = upLow + 'LipJotX' + str(i), em =True, parent = lipJotGrp ) 
    lipJotZ  = cmds.group( n = upLow +' LipJotZ' + str(i), em =True, parent = lipJotX ) 
   
    lipJotY  = cmds.group( n = upLow +'LipJotY' + str(i), em =True, parent = lipJotZ )    
    lipYJnt  = cmds.joint( n = upLow +'LipY' + str(i) + '_jnt', relative = True, p = [ 0, 0, 0] )     
    lipJot = cmds.group( n = upLow +'LipJot' + str(i), em =True, parent = lipYJnt )
    lipRollJotT = cmds.group( n = upLow +'LipRollJotT' + str(i), em =True, parent = lipJot )
    cmds.xform ( lipJotY, ws = True, t = lipYPos )
     
    #lip joint placement on the curve with verts tx        
    lipRollJotP = cmds.group( n =upLow + 'LipRollJotP' + str(i), em =True, p = lipRollJotT ) 
    pocPosX = cmds.getAttr ( poc + '.positionX')
    pocPosY = cmds.getAttr ( poc + '.positionY')
    pocPosZ = cmds.getAttr ( poc + '.positionZ')
    
    cmds.xform ( lipRollJotP, ws = True, t = [ pocPosX, pocPosY, pocPosZ] )
    lipRollJot = cmds.joint(n = upLow + 'LipRoll' + str(i) + '_jnt', relative = True, p = [ 0, 0, 0] ) 
    
    
    
    
def createDetailCtl( updn, i ):

    detailCtlP = cmds.group ( em =True, n = updn  + 'LipDetailP'+ str(i) )
    detailCtl = cmds.circle ( n = updn  + 'LipDetail' + str(i), ch=False, o =True, nr = ( 0, 0, 1), r = 0.05  )
    cmds.parent(detailCtl[0], detailCtlP)
    cmds.setAttr (detailCtl[0]+"Shape.overrideEnabled", 1 )
    cmds.setAttr( detailCtl[0]+"Shape.overrideColor", 20 )
    cmds.setAttr (detailCtl[0]+'.translate', 0,0,0 )
    cmds.transformLimits ( detailCtl[0], tx = ( -.5, .5), etx=( True, True) )
    cmds.transformLimits ( detailCtl[0], ty = ( -.5, .5), ety=( True, True) )
    attTemp = ['scaleX','scaleY','scaleZ', 'rotateX','rotateY','rotateZ', 'tz', 'visibility' ]  
    for y in attTemp:
        cmds.setAttr (detailCtl[0] +"."+ y, lock = True, keyable = False, channelBox =False) 






