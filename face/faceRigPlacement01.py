''' faceRig Structure/ hierarchy'''
def placefaceRig():
    ''' after place the face locators'''
    headSkelPos = cmds.xform( 'headSkelPos', t = True, q = True, ws = True)
    JawRigPos = cmds.xform( 'jawRigPos', t = True, q = True, ws = True)
    lEyePos = cmds.xform( 'lEyePos', t = True, q = True, ws = True)
    cheekPos = cmds.xform( 'cheekPos', t = True, q = True, ws = True)
    cheekRot = cmds.xform( 'cheekPos', ro = True, q = True, ws = True)
    squintPuffPos = cmds.xform( 'squintPuffPos', t = True, q = True, ws = True)
    squintPuffRot = cmds.xform( 'squintPuffPos', ro = True, q = True, ws = True)
    lowCheekPos = cmds.xform( 'lowCheekPos', t = True, q = True, ws = True)
    LEarPos = cmds.xform( 'lEarPos', t = True, q = True, ws = True)
    nosePos = cmds.xform( 'nosePos', t = True, q = True, ws = True)
    
    faceMain = cmds.group (em =1, n = 'faceMain', )    
    clsGroup = cmds.group (em =1, n = 'cls_grp', p = faceMain )
    crvGroup = cmds.group (em =1, n = 'crv_grp', p = faceMain )
    jntGroup = cmds.group(em =1, n = 'jnt_grp', p = faceMain)
    #??ctlGroup = cmds.group(em =1, n = 'ctl_grp', p = faceMain)
    
    #eyeLidCrv_grp/ browCrv_grp??
    faceGeoGroup = cmds.group (em =1, n = 'faceGeo_grp', p = faceMain )
    helpPanel = cmds.group (em =1, n = 'helpPanel_grp', p = faceMain )
    spn = cmds.group (em =1, n = 'spn', p = faceMain )
    headSkel = cmds.group (em =1, n = 'headSkel', p = spn )
    cmds.xform ( headSkel, ws = 1, t = headSkelPos )
    #jawRig hierarchy
    jawRig = cmds.group (em =1, n = 'jawRig', p = headSkel )
    cmds.xform ( jawRig, ws = 1, t = JawRigPos )
    jaw = cmds.group (em =1, n = 'jaw', p = jawRig )            
    jawSemi = cmds.group ( n = 'jawSemi', em =True, parent = jaw )
    jawSemiAdd = cmds.group(n = 'jawSemiAdd', em =True, parent = jaw)     
    cmds.setAttr ( jawSemi + ".translate", 0,0,0 )
    jawClose = cmds.joint(n = 'jawClose_jnt', relative = True, p = [ 0, 0, 0] )        
    jotStable = cmds.group ( n = 'lipJotStable', em =True, parent = jaw ) 
    lipJotP = cmds.group( n = 'lipJotP', em =True, parent = jotStable )
         
    #eyeRig hierarchy
    eyeRig = cmds.group (em =1, n = 'eyeRig', p = headSkel )
    cmds.xform ( eyeRig, ws = 1, t =( 0, lEyePos[1],lEyePos[2] ) )
    eyeRigP = cmds.group (em =1, n = 'eyeRigP', p = eyeRig )
    eyeTR = cmds.group(em =1, n = 'eyeTR', p = eyeRigP)
    ffdSquachLattice = cmds.group(em =1, n = 'ffdSquachLattice', p = eyeRigP)
    browRig = cmds.group (em =1, n = 'browRig', p = headSkel )
    
    #bodyHead connection node
    bodyHeadP = cmds.group (em =1, n = 'bodyHeadTRSP', p = headSkel )
    cmds.xform ( bodyHeadP, ws = 1, t = headSkelPos )    
    bodyHead = cmds.group (em =1, n = 'bodyHeadTRS', p = bodyHeadP )
    cmds.xform ( bodyHead, ws = 1, t = headSkelPos )    
    attachCtl = cmds.group (em =1, n = 'attachCtl_grp', p = bodyHead )
    cmds.xform(attachCtlGrp, ws = 1, t = headSkelPos)
    supportRig = cmds.group (em =1, n = 'supportRig', p = headSkel )
    
    lEarP = cmds.group (em =1, n = 'l_ear_grp', p = supportRig )
    cmds.xform ( lEarP, ws = 1, t = LEarPos )
    rEarP = cmds.group (em =1, n = 'r_ear_grp', p = supportRig )
    cmds.xform ( rEarP, ws = 1, t = (-LEarPos[0], LEarPos[1], LEarPos[2]) )
    noseRig = cmds.group (em =1, n = 'noseRig', p = supportRig )
    cmds.xform ( noseRig, ws = 1, t = nosePos )
    lCheekGrp = cmds.group (em =1, n = 'l_cheek_grp', p = supportRig )
    cmds.xform ( lCheekGrp, ws = 1, t = cheekPos, ro = cheekRot )
    rCheekGrp = cmds.group (em =1, n = 'r_cheek_grp', p = supportRig )
    cmds.xform ( rCheekGrp, ws = 1, t = (-cheekPos[0], cheekPos[1], cheekPos[2]), ro = (cheekRot[0],cheekRot[1],-cheekRot[2]) )
    lSquintPuffGrp = cmds.group (em =1, n = 'l_squintPuff_grp', p = supportRig )
    cmds.xform ( lSquintPuffGrp, ws = 1, t = squintPuffPos, ro = squintPuffRot )
    rSquintPuffGrp = cmds.group (em =1, n = 'r_squintPuff_grp', p = supportRig )
    cmds.xform ( rSquintPuffGrp, ws = 1, t = (-squintPuffPos[0], squintPuffPos[1], squintPuffPos[2]), ro = (squintPuffRot[0],squintPuffRot[1],-squintPuffRot[2]))
    lLowCheek = cmds.group (em =1, n = 'l_lowCheek_grp', p = supportRig ) 
    cmds.xform ( lLowCheek, ws = 1, t = lowCheekPos )
    rLowCheek = cmds.group (em =1, n = 'r_lowCheek_grp', p = supportRig ) 
    cmds.xform ( rLowCheek, ws = 1, t = (-lowCheekPos[0], lowCheekPos[1], lowCheekPos[2]) ) 