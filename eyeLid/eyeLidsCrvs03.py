#constraint to the inner/outer joint 
import maya.cmds as cmds
import re
def eyeLidsCrvs( ctlSize ): 
 
    if not ('lEyePos'):
        print "create the face locators"         
    else: 
        eyeRotY = cmds.getAttr ('lEyePos.ry' ) 
        eyeCenterPos = cmds.xform( 'lEyePos', t = True, q = True, ws = True)
 
    if not cmds.objExists ('eyeLidCrv_grp'):
        eyeLidCrvGrp = cmds.group (em =1, n = 'eyeLidCrv_grp', p = 'faceMainRig|crv_grp' )
    
    if not cmds.objExists ('eyeLidCtl_grp'):
        eyeLidCtlGrp = cmds.group (em =1, n = 'eyeLidCtl_grp', p = 'attachCtl_grp' )        
  
    prefix = ["l_up","l_lo" ]
    for pre in prefix:
        
        jnts = cmds.ls( pre + "LidBlink*_jnt", fl =1, type="joint" )
        leng = len(jnts)
        print leng    
        preR = pre.replace("l_", "r_")
        #create ctrl group 
        lLidCtlGrp = cmds.group (em=True, n = pre + "LidCtl_grp", p= 'eyeLidCtl_grp' ) 
        cmds.xform (lLidCtlGrp, ws = True, t = eyeCenterPos ) 
        cmds.setAttr ( lLidCtlGrp + ".ry", eyeRotY ) 
        rLidCtlGrp = cmds.duplicate ( lLidCtlGrp, n = preR +"LidCtl_grp" )
        cmds.setAttr ( rLidCtlGrp[0] + ".tx", -eyeCenterPos[0] )
        cmds.setAttr ( rLidCtlGrp[0] + ".ry", -eyeRotY )
        cmds.setAttr ( rLidCtlGrp[0] + ".sx", -1 )
        
        #minYCrv /maxYCrv  
        tempMinCrv = cmds.curve( d = 3, p = [(0,0,0),(.25,0,0),(.5,0,0),(.75,0,0),(1,0,0)])
        cmds.rebuildCurve( tempMinCrv, d = 1, rt=0, kr =0, s = leng -1  )
        lMinCrv = cmds.rename (tempMinCrv,  pre[2:] +"Min_crv" )
            
        tempMaxCrv = cmds.curve( d = 3, p = [(0,0,0),(.25,0,0),(.5,0,0),(.75,0,0),(1,0,0)])
        cmds.rebuildCurve( tempMaxCrv, d = 1, rt=0, kr = 0, s = leng -1  ) 
        lMaxCrv = cmds.rename (tempMaxCrv, pre[2:] +"Max_crv" ) 
 
        squintCrv = cmds.duplicate (lMaxCrv, n= pre[2:] +"Squint_crv" )
        annoyCrv = cmds.duplicate ( squintCrv, n= pre[2:] +'Annoy_crv')
        #put curves in the eyeLidCrv_grp  
        cmds.parent (lMinCrv,  lMaxCrv, squintCrv, annoyCrv, 'eyeLidCrv_grp') 
		
		#shape crvs for eyeDirections
        pushA_crv = cmds.duplicate ( lMinCrv,  n = pre +'LidPushA_crv' )
        pushB_crv = cmds.duplicate ( pushA_crv, n= pre +'LidPushB_crv')
        pushC_crv = cmds.duplicate ( pushA_crv, n= pre +'LidPushC_crv')
        pushC_crv = cmds.duplicate ( pushA_crv, n= pre +'LidPushD_crv')
		
    UDLR = ["l_up", "l_lo", "r_up", "r_lo"]    
    for UD in UDLR:        
        if "up" in UD:      
            ty = 1               

        elif "lo" in UD: 
            ty = 0
            
        jnts = cmds.ls( UD + "LidBlink*_jnt", fl =1, type="joint" )
        length = len(jnts)
        
        #eyeOpenCrv with math expression
        if not cmds.objExists( UD +"EyeOpen_crv" ): 
            tempCrv = cmds.curve( d = 3, p = [(0,ty,0),(.25,ty,0),(.5,ty,0),(.75,ty,0),(1,ty,0) ])
            cmds.rebuildCurve( tempCrv, d = 1, rt=0, kr = 0, s = length -1  )
            openCrv = cmds.rename (tempCrv,  UD +"EyeOpen_crv" )
            startCrv = cmds.duplicate (openCrv, n = UD +"EyeStart_crv")
            cmds.parent (openCrv,startCrv, 'eyeLidCrv_grp') 
                   
        #UD / i /  ctlSize /  ctlPOC? /   
        for i in range( 0, length ):            
                        
            #바디 따라다니는 눈꺼플 컨트롤 eyeLid ctrls attach to body 
            childPos = cmds.xform ( cmds.listRelatives (jnts[i], c=1, type ='joint')[0], t = True, q = True, ws = True)   
            lidCtl = controller( UD + "Lid" + str(i+1).zfill(2), childPos, ctlSize*0.1, "cc")
            cmds.parent ( lidCtl[1], UD + "LidCtl_grp" )
            cmds.setAttr ( lidCtl[1] + ".tz", cmds.getAttr(lidCtl[1] + '.tz') + ctlSize*0.2 )
            cmds.setAttr ( lidCtl[1] + ".ry", 0)     
         
            #jumperPanel.l_upPush_Lid# define 
            '''
            LUpPush_Lid0 =  PushLid_EXP.ValA * ((-jumperPanel.LLidPushX + 1) / 2 * LUpDetail0.pushA + (jumperPanel.LLidPushX + 1) / 2 * LUpDetail0.pushB) + 
                            PushLid_EXP.ValB * ((-jumperPanel.LLidPushX + 1) / 2 * LUpDetail0.pushC + (jumperPanel.LLidPushX + 1) / 2 * LUpDetail0.pushD);
            '''
            AB = ['A','B'] 
            CD = ['C','D'] 
            lid0 = 'jumperPanel.' + UD + 'Push_Lid%s'%str(i) 
            valA = 'jumperPanel.' + UD[:2] + 'valA'
            valB = 'jumperPanel.' + UD[:2] + 'valB'
            pushX = 'jumperPanel.'+ UD[:2] + "lidPushX"
            pushA0 = 'l_'+UD[2:] +'LidPush'+ AB[0] +'_crvShape.cv[%s].yValue'%str(i)  
            pushB0 = 'l_'+UD[2:] +'LidPush'+ AB[1] + '_crvShape.cv[%s].yValue'%str(i)  
            pushC0 = 'l_'+UD[2:] +'LidPush'+ CD[0] + '_crvShape.cv[%s].yValue'%str(i)  
            pushD0 = 'l_'+UD[2:] +'LidPush'+ CD[1] + '_crvShape.cv[%s].yValue'%str(i)  
            
            pushMath = cmds.expression (n=UD+"pushCrv_math%s"%str(i+1), s=" %s=%s*((-%s+1)/2*%s + (%s+1)/2*%s) + %s*((-%s+1)/2*%s + (%s+1)/2*%s)"%(lid0, valA, pushX, pushA0, pushX, pushB0, valB, pushX, pushC0, pushX, pushD0), 
            o = 'jumperPanel.' + UD + 'Push_Lid%s'%str(i), ae =1) 
    
    cornerLidGrp = cmds.group (em =1, n = 'cornerLid_grp', p = 'eyeLidCtl_grp' )          
    corners = [ 'l_inner','l_outer', 'r_inner','r_outer' ]
    for cn in corners:
               
        #바디 따라다니는 눈꺼플 컨트롤 eyeLid ctrls attach to body 
        childPos = cmds.xform ( cn+'_jnt', t = True, q = True, ws = True )   
        lidCtl = controller( cn + "Lid", childPos, ctlSize*0.1, "cc" )
        cmds.parent ( lidCtl[1], cornerLidGrp )
        cmds.setAttr ( lidCtl[1] + ".tz", cmds.getAttr(lidCtl[1] + '.tz') + ctlSize*0.2 )
        cmds.setAttr ( lidCtl[1] + ".ry", 0 )
               
#eyeLidsCrvs(1)
