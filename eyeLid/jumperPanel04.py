import maya.cmds as cmds
def jumperPanel():
    if not cmds.objExists('jumperPanel'):
        #set the start with plusMinusAverage  
        cmds.group( n = "jumperPanel", em = 1, p = "faceMainRig" )   

    if not cmds.objExists('lids_EXP'):
        #set the start with plusMinusAverage  
        cmds.group( n = "lids_EXP", em = 1, p = "jumperPanel" )    
    upJnts = cmds.ls( "l_upLidBlink*_jnt", fl =1, type= "joint" )
    loJnts = cmds.ls( "l_loLidBlink*_jnt", fl =1, type= "joint" )
    upLen = len(upJnts)    
    loLen = len(loJnts)
    cmds.select ('lids_EXP') #lids_EXP: lid start/ end /open 
    #nodes for ValAB
    
    pushY_mult = cmds.shadingNode( 'multiplyDivide', asUtility =1, n ='lidPushY_mult')

    prefix = [ 'l_', 'r_' ]
    for LR in prefix:

        if 'l_' in LR:
            XYZ = 'X'

        if 'r_' in LR:
            XYZ = 'Y' 
         
        for i in range(0, max(upLen, loLen)): 
            #create each push_lid point in jumperPanel
            cmds.addAttr('jumperPanel', longName= LR + "upPush_Lid%s"%str(i), attributeType='float', dv = 0)
            cmds.addAttr('jumperPanel', longName= LR + "loPush_Lid%s"%str(i), attributeType='float', dv = 0)
            
            #Start = - .cv(LUpCrv.cv) -   +  push_Lid5 + ctrl.ty* *  .squint
            cmds.addAttr('lids_EXP', longName= LR + "upEyeStart%s"%str(i), attributeType='float', dv = 0)
            ##eyeOpenCrv shape ( start + blinkCtrl ) : upEyeStart0 -lids_EXP.l_upGap*l_eyeBlink.ty*(1-blinkLevel)
            cmds.addAttr('lids_EXP', longName= LR +"upEyeOpen%s"%str(i), attributeType='float', dv = 0)
			#blink target POC.positionY on the loEyeCrv
            cmds.addAttr('lids_EXP', longName= LR +"EyeEnd%s"%str(i), attributeType='float', dv = 0)
        
            cmds.addAttr('lids_EXP', longName= LR +"loEyeStart%s"%str(i), attributeType='float', dv = 0)
            cmds.addAttr('lids_EXP', longName= LR +"loEyeOpen%s"%str(i), attributeType='float', dv = 0)
             
        #Y = lookUp/Down  X = lookLeft/Right           
        cmds.addAttr('jumperPanel', longName= LR + "lidPushY", attributeType='float', dv = 0)                      
        cmds.addAttr('jumperPanel', longName= LR + "lidPushX", attributeType='float', dv = 0) 
        
        cmds.addAttr('jumperPanel', longName= LR + "valA", attributeType='float', dv = 0)
        cmds.addAttr('jumperPanel', longName= LR + "valB", attributeType='float', dv = 0)
        
        
        #make -JumperPanel.l_lidPushY into +
        cmds.connectAttr ( 'jumperPanel.' + LR + 'lidPushY', pushY_mult + '.input1'+XYZ)
        cmds.setAttr ( pushY_mult + '.input2'+XYZ, -1 )
        
        #ValA and ValB define by LidPushY clamp
        pushY_clamp = cmds.shadingNode( 'clamp', asUtility =1, n = LR + 'lidPushY_clamp')
        cmds.setAttr ( pushY_clamp + '.maxR', 1 )
        cmds.setAttr ( pushY_clamp + '.maxG', 1 )
        #ValAB / LidPushY defined by l_eyeballRotX 
        cmds.connectAttr ( 'jumperPanel.' + LR + 'lidPushY', pushY_clamp + '.inputR')
        cmds.connectAttr ( pushY_mult + '.output'+XYZ, pushY_clamp + '.inputG' )
        cmds.connectAttr (  pushY_clamp + '.outputR', 'jumperPanel.' + LR + 'valA') # l_valA = + lidPushY
        cmds.connectAttr (  pushY_clamp + '.outputG', 'jumperPanel.' + LR + 'valB')# l_valB = -(-lidPushY)        
        
        #l_eyeballRotX --> 'jumperPanel.l_lidPushY'
        
        eyeRotX_mult = cmds.shadingNode( 'multiplyDivide', asUtility =1, n = LR + 'eyeRotX_mult')
        rotX_invert = cmds.shadingNode( 'multiplyDivide', asUtility =1, n = LR + 'rotX_invert')
        cmds.connectAttr ( 'faceFactors.eyeBallRotX_scale', rotX_invert + '.input1X' )
        cmds.setAttr ( rotX_invert + '.input2X', -1)

        cmds.setAttr ( eyeRotX_mult + '.operation', 2)
        cmds.connectAttr ( LR + 'eyeballRot.rotateX', eyeRotX_mult + '.input1X')
        cmds.connectAttr ( rotX_invert + '.outputX', eyeRotX_mult + '.input2X' )
        
        eyeUD_mult = cmds.shadingNode( 'multiplyDivide', asUtility =1, n = LR + 'eyeUD_mult')
        cmds.connectAttr ( eyeRotX_mult + '.outputX', eyeUD_mult + '.input1X' )
        cmds.connectAttr ( eyeRotX_mult + '.outputX', eyeUD_mult + '.input1Y' )
        cmds.connectAttr ( 'faceFactors.range_'+LR+'eyeU', eyeUD_mult + '.input2X')
        cmds.connectAttr ( 'faceFactors.range_'+LR+'eyeD', eyeUD_mult + '.input2Y')
        
        pushY_con = cmds.shadingNode( 'condition', asUtility =1, n = LR + 'lidPushY_con')
        cmds.connectAttr ( LR + 'eyeballRot.rotateX', pushY_con+'.firstTerm' )
        cmds.setAttr ( pushY_con+".secondTerm", 0 )
        cmds.setAttr ( pushY_con+".operation", 4 )
        cmds.connectAttr ( eyeUD_mult + '.outputX', pushY_con+ '.colorIfTrueR' )
        cmds.connectAttr ( eyeUD_mult + '.outputY', pushY_con+ '.colorIfFalseR' )
        cmds.connectAttr ( pushY_con+ '.outColorR', 'jumperPanel.' +LR+ 'lidPushY' )
        
        #l_eyeballRotY --> 'jumperPanel.l_lidPushX'
        eyeRotY_mult = cmds.shadingNode( 'multiplyDivide', asUtility =1, n = LR + 'eyeRotY_mult')
        cmds.setAttr ( eyeRotY_mult + '.operation', 2)
        cmds.connectAttr ( 'faceFactors.eyeBallRotY_scale', eyeRotY_mult + '.input2X' )
        cmds.connectAttr ( 'faceFactors.eyeBallRotY_scale', eyeRotY_mult + '.input2Y' )
        cmds.connectAttr ( LR + 'eyeballRot.rotateY', eyeRotY_mult + '.input1X')
        cmds.connectAttr ( LR + 'eyeballRot.rotateY', eyeRotY_mult + '.input1Y')
        
        eyeLR_mult = cmds.shadingNode( 'multiplyDivide', asUtility =1, n = LR + 'eyeLR_mult')
        cmds.connectAttr ( eyeRotY_mult + '.outputX', eyeLR_mult + '.input1X' )
        cmds.connectAttr ( eyeRotY_mult + '.outputX', eyeLR_mult + '.input1Y' )
        cmds.connectAttr ( 'faceFactors.range_'+LR+'eyeR', eyeLR_mult + '.input2X')
        cmds.connectAttr ( 'faceFactors.range_'+LR+'eyeL', eyeLR_mult + '.input2Y')
        
        pushX_con = cmds.shadingNode( 'condition', asUtility =1, n = LR + 'lidPushX_con')
        cmds.connectAttr ( LR + 'eyeballRot.rotateY', pushX_con +'.firstTerm' )
        cmds.setAttr ( pushY_con+".secondTerm", 0 )
        cmds.setAttr ( pushY_con+".operation", 4 )
        cmds.connectAttr ( eyeLR_mult + '.outputX', pushX_con+ '.colorIfTrueG' )
        cmds.connectAttr ( eyeLR_mult + '.outputY', pushX_con+ '.colorIfFalseG' )
        cmds.connectAttr ( pushX_con+ '.outColorG', 'jumperPanel.' +LR+ 'lidPushX')   