#  twitch 컨트롤로 만든 눈썹 쉐입을 커브로 만들기.
# 각각의 커프(sad, mad, furrow) 버튼 만들자.
def copyCurrnetCrv(name):
    #블렌쉐입 해당 커브 웨이트 0 ( 1일땐 각각의 cv가 더블 트랜스폼 된다 )
    cmds.setAttr ("browBS.l" + name + "_crv", 0)
    cmds.setAttr ("browBS.r" + name + "_crv", 0)    
	indiGrp = cmds.group (em = 1, n = name + "Crv_grp", p = "browCrv_grp")
    cmds.parent("l" + name + "_crv", "r" + name + "_crv", indiGrp) 
    
    # 눈썹 베이스 조인트들 리스트
    browJnt = cmds.ls("*BrowBaseJnt*", fl =1, type = "joint")  
    browLen = len(browJnt) 
    browJnt.sort()
    z = [ browJnt[0] ]
    y = browJnt[1:browLen/2+1]
    browJnt.reverse()
    x = browJnt[:browLen/2]
    orderJnts = x + z + y 
   
    browShapeCv= cmds.ls("l" + name + "_crv.cv[*]", fl = 1)
    cvJntList = []
    for i in range(0, browLen): 
        # 각각의 cv에 스킨할 조인트 생성         
        cvPos = cmds.xform (browShapeCv[i], q=1, ws =1, t = 1 )
        ctlName = orderJnts[i].split("BrowBaseJnt",1)[0]+ name + orderJnts[i].split("BrowBaseJnt",1)[1] + '_ctl' 
        cvCtl = circleCtrl( ctlName, cvPos, 0.05 )
        ctlColor = cmds.getAttr(cvCtl + ".overrideColor")
        cvCtlP = cmds.listRelatives( cvCtl, ap = 1, type = "transform")
        #create Joint for each CV
        cvJnt = cmds.joint ( n = ctlName.replace("_ctl","_jnt"), p = cvPos)
        cvJntList.append(cvJnt)
        cmds.parent( cvCtl + "Shape", cvJnt, r =1, shape =1)
        cmds.setAttr (cvJnt +".overrideEnabled", 1)
        cmds.setAttr (cvJnt + ".overrideColor", ctlColor )
        cmds.delete (cvCtl)
		cmds.parent(cvCtlP, indiGrp)
    #디포머를 이용해야 하기 때문에 rCrv를 instance 로 쓸 수 없다. 
    cmds.skinCluster( cvJntList, "l" + name + "_crv", toSelectedBones=1)
    cmds.skinCluster( cvJntList, "r" + name + "_crv", toSelectedBones=1)
    ctlPList = cmds.listRelatives( cvJntList, ap =1, type = "transform") 

    for x in range(0, browLen):
        #커브에 디포머가 붙으면 cv 위치값은 0,0,0 이 된다.(위치값은 tweak 노드에 저장된다) 
        cvPos = cmds.xform (browShapeCv[x], q=1, ws =1, t = 1 )
        childJnt = cmds.listRelatives (cmds.listRelatives( orderJnts[x], c = 1, type = "joint"), c =1) 
        rotX = cmds.getAttr( orderJnts[x]+".rx")
        rotY = cmds.getAttr( orderJnts[x]+".ry")
        tranZ = cmds.getAttr( childJnt[0]+".tz")
        initialX = list(cvPos)[0]
        posX = rotY/10 + initialX
        posY = rotX/-10   

        cmds.setAttr( ctlPList[x] + ".tx", posX )
        cmds.setAttr( ctlPList[x] + ".ty", posY )
        cmds.setAttr( ctlPList[x] + ".tz", tranZ )
	#모든 눈썹 컨트롤러 zero out
    dtlCtl = cmds.listRelatives(cmds.ls("browDetail*P", fl = 1, type = "transform" ), c=1, type = "transform" )
    arcCtls = cmds.listConnections( "browCtrlCrvShape", s =1, type = "transform" )
    jntCtl = cmds.listRelatives ( cmds.ls("*_BrowCtrlJnt*P", fl = 1, type = "transform" ), c=1, type = "transform" ) 
    ctlLen = len(arcCtls)
    browCtls = dtlCtl + arcCtls[1:ctlLen-1] + jntCtl
    for BC in browCtls:
        zeroAtt = ["translateX", "translateY", "translateZ", "rotateX", "rotateY", "rotateZ"]
        att = cmds.listAttr ( BC, s =1, v=1, k =1, u =1 )
        keyAtt = [y for y in att if y in zeroAtt]

        for a in keyAtt:
            cmds.setAttr (BC + ".%s"%a, 0)        

    cmds.setAttr ("browBS.l" + name + "_crv", 1)
    cmds.setAttr ("browBS.r" + name + "_crv", 1)