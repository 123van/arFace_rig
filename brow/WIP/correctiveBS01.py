#joint connect remap for corrective shape 
'''
타겟 and 베이스를 선택하고 실행
blendshapes = cmds.ls(*cmds.listHistory(targetMesh)or [], type= 'blendShape') 

source_shapes =  cmds.ls(*cmds.listHistory('blendShape22') or [], type= 'tweak', ni=True)

코렉티브 쉐입을 일단 add blendShape 한다. 
조인트 갯수만큼 인스탄트로 카피된 똑같은 쉐입들이 블렌쉐입에 추가된다.
각각의 조인트 weight map을 각각의 코렉티브 블렌쉐입에 적용한다
리멥으로 조인트 움직임에 따라 블렌쉐입이 움직인다. 
add the corrective shape to the blendShape
select brow joints and the target(corrective shape)
run script
name = 'up': rx - , 'down': rx +, 'furrow': ry 
inputMax = -30
'''
import maya.cmds as cmds
def correctiveBS( rotateAxis, inputMax ):
    # inputUp = -20 / inputDown = 20  / inputFurrow = -15

    browJnts = cmds.ls ("*BrowBaseJnt*", type ="joint")
    jntNum = len(browJnts)
    browJnts.sort()
    z = [ browJnts[0] ]
    y = browJnts[1:jntNum/2+1]
    browJnts.reverse()
    x = browJnts[:jntNum/2]
    orderJnts = x + z + y
    
    # add corrective shapes to the blendShape 
    mySel = cmds.ls( sl = 1, type = "transform" )    
    base = mySel[-1]
    trgt = mySel[0]
    myBS = cmds.ls( cmds.listHistory(base), type = "blendShape" )    
    cmds.select(cl = 1)
    
    if not cmds.objExists("faceMain|target_grp"):
        trgtGrp = cmds.group( em=True, n = "targetShape_grp", p = "faceMain")   
        instGrp = cmds.group( em=True, n = "correctiveGrp", p = "faceMain|targetShape_grp" )   
    #why not working if myBS[0] used?
    if  myBS:

        existTarget = cmds.aliasAttr (myBS[0], q =1 )
        targetLen = len(existTarget)/2        
        cmds.blendShape(myBS[0], e = 1, target = [ base, targetLen, trgt, 1.0])
        
    elif not myBS:

        myBS = cmds.blendShape ( trgt, base, n = "twitchBS", frontOfChain =1 )
    
    #조인트 갯수만큼 인스탄트로 카피된 똑같은 쉐입들이 블렌쉐입에 추가된다.         
    
    for i in range(jntNum):
        # remap for each joint
        remap = cmds.shadingNode ('remapValue', asUtility =True, n= trgt + str(i).zfill(2) + "_remap" )
        cmds.setAttr (remap + '.inputMax', inputMax )
        cmds.connectAttr ( orderJnts[i] + '.' + rotateAxis, remap+'.inputValue' )
        
        inst = cmds.instance( trgt, n = trgt + str(i+1) )
        cmds.parent( inst, instGrp )
        
        existTargets = cmds.aliasAttr (myBS[0], q =1 )
        targetsLen = len(existTargets)/2        
        cmds.blendShape(myBS[0], e = 1, target = [ str(base), targetsLen, inst[0], 1.0])
        cmds.blendShape(myBS[0], e = 1, w=[(targetsLen, 0)] )
        #transfer joint skinWeight to BlendShape weight
        skinWeightToBlendShape( base, myBS[0], inst[0], targetsLen, orderJnts[i])
        
        cmds.connectAttr ( remap + ".outValue", myBS[0] + "." + inst[0])
        
        cmds.delete( inst )
	#correctiveBS( 'rx', -35 ) 