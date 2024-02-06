#눈꺼플 조인트 생성하기 - lidJntP joint orient zero out 
#z forward joint (x rotation)
# lidBlink joint starts at eye center 
# fix joint rx orient  -06/ 21 /2016
# fix head name to "head_REN"  -08/ 12 /2016
'''
UI  : controller size, mult.input 2 values
The locator "lEyePos" for eye center should exist.  
select left eyeLid vertices(up/low) and run the script 
upLowLR = "l_up", "l_lo" '''
 
import re
import maya.cmds as cmds
def eyelidJoints ( upLowLR ): 
      
    if not ('lEyePos'):
        print "create the face locators"
          
    else:    
        eyeRotY = cmds.getAttr ('lEyePos.ry' )
        eyeRotZ = cmds.getAttr ('lEyePos.rz' ) 
        eyeCenterPos = cmds.xform( 'lEyePos', t = True, q = True, ws = True) 
      
    #reorder the vertices in selection list  
    vtxs =cmds.ls(sl=1 , fl=1)
    myList = {}
    for i in vtxs:        
        val = re.findall('\d+', i )
        print val
        xyz = cmds.getAttr ("head_REN.vrts[" +val[0]+"]")[0]
        myList[ i ] = xyz[0]
    ordered = sorted(myList, key = myList.__getitem__)    
  
    # create parent group for eyelid joints
    if not cmds.objExists('eyeLidJntP'):
        cmds.group ( n = 'eyeLidJntP', em =True, p ="eyeRig" ) 
                 
    null = cmds.group ( n = upLowLR+'EyeLidJnt_grp', em =True, p ="eyeLidJntP" ) 
    cmds.xform (null, t = eyeCenterPos, ws =1 )
    cmds.select(cl = True) 
  
    #create eyeLids parent joint
    LidJntP = cmds.joint(n = upLowLR + 'LidP_jnt', p = eyeCenterPos) 
    #cmds.setAttr ( LidJntP + ".jointOrientY", 0)
    cmds.parent ( LidJntP, null )
    cmds.setAttr ( null + '.ry', eyeRotY ) 
    cmds.setAttr ( null + '.rz', eyeRotZ ) 
    cmds.select(cl =1)
    #UI for 'null.rx/ry/rz'?? cmds.setAttr ( null + '.rz', eyeRotZ )    
    index = 1
    for v in ordered:
        vertPos = cmds.xform ( v, t = True, q = True, ws = True)             
        lidJnt = cmds.joint(n = upLowLR + 'Lid' + str(index).zfill(2) + '_jnt', p = vertPos ) 
        lidJntTX = cmds.joint(n = upLowLR + 'LidTX' + str(index).zfill(2) + '_jnt', p = vertPos )
        cmds.joint ( lidJnt, e =True, zso =True, oj = 'zyx', sao= 'yup')
        blinkJnt = cmds.duplicate ( lidJnt, po=True, n = upLowLR + 'LidBlink' + str(index).zfill(2)+'_jnt' )
        cmds.parent ( blinkJnt[0], LidJntP )
        cmds.setAttr ( blinkJnt[0] + '.tx' , 0 )
        cmds.setAttr ( blinkJnt[0] + '.ty' , 0 )  
        cmds.setAttr ( blinkJnt[0] + '.tz' , 0 ) 
        cmds.parent ( lidJnt, blinkJnt[0] )     
            
        wideJnt = cmds.duplicate ( blinkJnt, po=True, n = upLowLR + 'LidWide' + str(index).zfill(2) + '_jnt' )  
        scaleJnt = cmds.duplicate ( blinkJnt, po=True, n = upLowLR + 'LidScale' + str(index).zfill(2) + '_jnt' )
        cmds.parent ( blinkJnt, scaleJnt[0] )
        #cmds.joint ( scaleJnt[0], e =True, zso =True, oj = 'xyz', sao= 'yup')
        cmds.parent ( wideJnt[0], scaleJnt[0] )
  
        index = index + 1
      
    mirrorLowLR = ''
    if 'l_up' in upLowLR:
        mirrorLowLR = 'r_up'
    elif 'l_lo' in upLowLR:
        mirrorLowLR = 'r_lo'
     
    print eyeCenterPos    
    RNull = cmds.group ( n = mirrorLowLR +'EyeLidJnt_grp', em =True, p = "eyeLidJntP" ) 
    cmds.xform (RNull, t = (-eyeCenterPos[0], 0, 0) ) 
    cmds.setAttr ( RNull + '.ry', -eyeRotY ) 
    cmds.setAttr ( RNull + '.rz', -eyeRotZ )
    RLidJntP = cmds.mirrorJoint ( LidJntP, mirrorBehavior=True, myz = True, searchReplace = ('l_', 'r_'))
    cmds.parent ( RLidJntP[0], RNull ) 
    zeroAtts = ['tx', 'ty', 'tz', 'rx', 'ry', 'rz']
    for i in zeroAtts:
        cmds.setAttr ( RLidJntP[0] + '.' + i, 0)