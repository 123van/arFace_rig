""" Check the name starting with "l_" , "r_" if it is not working """
def mirrorLRCtl():
    
    lCtl = cmds.ls(sl=1, type = "transform")
    ctlLen = len(lCtl)
    mirrorAttrs = ["translateX", "rotateY", "rotateZ" ]
    for i in range(0, ctlLen):
        attrs = cmds.listAttr( lCtl[i], v =1, k = 1, u = 1 ) 
        print attrs
        for att in attrs :
            if att in mirrorAttrs:
                
                lval= cmds.getAttr ( lCtl[i] + ".%s"%att )
                rCtl = lCtl[i].replace("l_","r_")
                cmds.setAttr ( rCtl + ".%s"%att, -lval )
                
            else: 
                lval= cmds.getAttr ( lCtl[i] + ".%s"%att )
                rCtl = lCtl[i].replace("l_","r_")
                cmds.setAttr ( rCtl + ".%s"%att, lval )