#Function for connecting brow Curve and controller to the brow Joints
import maya.cmds as cmds
def browCrvCtlToJnt (browCtrl, browDetail, jnt, ctrlP, madPOC, POC, initialMadX, initialX, RotateScale, index ):        
    #connect browCtrlCurve and controller to the brow joints
    ctrlMult = cmds.shadingNode ( 'multiplyDivide', asUtility=True, n = jnt.split('Base', 1)[0] +'CtrlMult'+ str(index) )
    crvMult = cmds.shadingNode ( 'multiplyDivide', asUtility=True, n = jnt.split('Base', 1)[0] +'CrvMult'+ str(index) )
    browCtlSum = cmds.shadingNode ( 'plusMinusAverage', asUtility=True, n = jnt.split('Base', 1)[0] +'CtlSum'+ str(index))
    browCtlRotSum = cmds.shadingNode ( 'plusMinusAverage', asUtility=True, n = jnt.split('Base', 1)[0] +'CtlRotSum'+ str(index))
    PocXYSum = cmds.shadingNode ( 'plusMinusAverage', asUtility=True, n = jnt.split('Base', 1)[0] +'PocXYSum'+ str(index))
    xyTotal = cmds.shadingNode ( 'plusMinusAverage', asUtility=True, n = jnt.split('Base', 1)[0] +'XYtotal'+ str(index))
     
    cmds.connectAttr ( browCtrl + '.tx', browCtlSum + '.input3D[0].input3Dx')
    cmds.connectAttr ( browDetail + '.tx', browCtlSum + '.input3D[1].input3Dx')
    cmds.connectAttr ( browCtrl + '.ty', browCtlSum + '.input3D[0].input3Dy')
    cmds.connectAttr ( browDetail + '.ty', browCtlSum + '.input3D[1].input3Dy')
    cmds.connectAttr ( browCtrl + '.tz', browCtlSum + '.input3D[0].input3Dz')
    cmds.connectAttr ( browDetail + '.tz', browCtlSum + '.input3D[1].input3Dz')   
    cmds.connectAttr ( madPOC + '.positionZ', browCtlSum + '.input3D[2].input3Dz') 
       
    cmds.connectAttr ( browCtrl + '.rx', browCtlRotSum + '.input3D[0].input3Dx') 
    cmds.connectAttr ( browDetail + '.rx', browCtlRotSum + '.input3D[1].input3Dx') 
    cmds.connectAttr ( browCtrl + '.ry', browCtlRotSum + '.input3D[0].input3Dy') 
    cmds.connectAttr ( browDetail + '.ry', browCtlRotSum + '.input3D[1].input3Dy')  
    cmds.connectAttr ( browCtrl + '.rz', browCtlRotSum + '.input3D[0].input3Dz') 
    cmds.connectAttr ( browDetail + '.rz', browCtlRotSum + '.input3D[1].input3Dz')     

    #browCrv's POC.tx zero out 
    cmds.connectAttr ( POC + '.positionX', PocXYSum + '.input3D[0].input3Dx')
    cmds.setAttr ( PocXYSum + '.input3D[1].input3Dx', -initialX )
    cmds.connectAttr ( madPOC + '.positionX', PocXYSum + '.input3D[2].input3Dx')
    cmds.setAttr ( PocXYSum + '.input3D[3].input3Dx', -initialMadX )
    #POC.ty sum
    cmds.connectAttr ( POC + '.positionY', PocXYSum +'.input3D[0].input3Dy')
    cmds.connectAttr ( madPOC + '.positionY', PocXYSum + '.input3D[1].input3Dy')
    
    #connect crvMult to ctrlP
    cmds.connectAttr ( PocXYSum + '.output3Dx', crvMult + '.input1X')
    cmds.connectAttr ( PocXYSum + '.output3Dy', crvMult + '.input1Y')    
    cmds.setAttr ( crvMult + '.input2X', RotateScale )
    cmds.setAttr ( crvMult + '.input2Y', -RotateScale )
    cmds.connectAttr ( crvMult + ".outputX", ctrlP + '.ry')
    cmds.connectAttr ( crvMult + ".outputY", ctrlP + '.rx')
    #X total
    cmds.connectAttr ( browCtlSum + '.output3Dx', xyTotal + '.input3D[0].input3Dx')
    cmds.connectAttr ( PocXYSum + '.output3Dx', xyTotal + '.input3D[1].input3Dx')
    #Y total
    cmds.connectAttr ( browCtlSum + '.output3Dy', xyTotal + '.input3D[0].input3Dy')   
    cmds.connectAttr ( POC + '.positionY', xyTotal + '.input3D[1].input3Dy')  
    cmds.connectAttr ( madPOC + '.positionY', xyTotal + '.input3D[2].input3Dy') 
   
    cmds.connectAttr ( xyTotal + '.output3Dx', ctrlMult + '.input1X')
    cmds.connectAttr ( xyTotal + '.output3Dy', ctrlMult + '.input1Y')
    
    cmds.setAttr ( ctrlMult + '.input2X', RotateScale )
    cmds.setAttr ( ctrlMult + '.input2Y', -RotateScale )
    
    browPJnt = cmds.listRelatives ( jnt, c =1, type = 'joint')
    browJnt = cmds.listRelatives ( browPJnt, c =1, type = 'joint')
    #Z total
    #cmds.connectAttr ( browCtlSum + '.output3Dz', xyTotal + '.input3D[0].input3Dz' )
    #cmds.connectAttr ( ctrlMult + '.input2Z', xyTotal + '.input3D[1].input3Dz' )
        
    cmds.connectAttr ( ctrlMult + '.outputX', jnt + '.ry')
    cmds.connectAttr ( ctrlMult + '.outputY', jnt + '.rx')
    cmds.connectAttr ( browCtlSum + '.output3Dz', browJnt[0] + ".tz" )
    
    cmds.connectAttr ( browCtlRotSum + '.output3Dx', browPJnt[0] + '.rx')
    cmds.connectAttr ( browCtlRotSum + '.output3Dy', browPJnt[0] + '.ry')
    cmds.connectAttr ( browCtlRotSum + '.output3Dz', browPJnt[0] + '.rz')
