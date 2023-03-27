def circleCtrl( ctlName, basePos, radius ):
    if ctlName[:2]=="C_":
        #if center, color override is yellow
        circleCtrl = cmds.circle (n = ctlName, ch=False, nr=(0, 0, 1), c=(0, 0, 0), sw=360, r= radius )
        cmds.setAttr (circleCtrl[0] +".overrideEnabled", 1)
        cmds.setAttr (circleCtrl[0] +".overrideShading", 0)
        cmds.setAttr (circleCtrl[0] + ".overrideColor", 17 )
        null = cmds.group (circleCtrl[0], w =True, n = circleCtrl[0].replace("_ctl", "_grp"))
        cmds.xform (null, ws = True, t = basePos )
    
    elif ctlName[:2]=="L_":
        #if left, color override is blue
        circleCtrl = cmds.circle (n = ctlName, ch=False, nr=(0, 0, 1), c=(0, 0, 0), sw=360, r= radius )
        cmds.setAttr (circleCtrl[0] +".overrideEnabled", 1)
        cmds.setAttr (circleCtrl[0] +".overrideShading", 0)
        cmds.setAttr (circleCtrl[0] + ".overrideColor", 6 )
        null = cmds.group (circleCtrl[0], w =True, n = circleCtrl[0].replace("_ctl", "_grp"))
        cmds.xform (null, ws = True, t = basePos )
    
    elif ctlName[:2]=="R_":
        #if right, color override is red
        circleCtrl = cmds.circle (n = ctlName, ch=False, nr=(0, 0, 1), c=(0, 0, 0), sw=360, r= radius )
        cmds.setAttr (circleCtrl[0] +".overrideEnabled", 1)
        cmds.setAttr (circleCtrl[0] +".overrideShading", 0)
        cmds.setAttr (circleCtrl[0] + ".overrideColor", 13 )
        null = cmds.group (circleCtrl[0], w =True, n = circleCtrl[0].replace("_ctl", "_grp"))
        cmds.xform (null, ws = True, t = basePos )

    return circleCtrl[0]