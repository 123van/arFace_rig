# -*- coding: utf-8 -*-
#create “jawClose_cls” / “mouth_cls” calculated by existing clusters
def calExtraClsWgt():

    clusters = ["lip_cls", "lipRoll_cls", "jawOpen_cls"]
    for cls in clusters:
    
    	if not cmds.objExists (cls):
    	
    		print cls+' Is Not Available'
    
    shapes = cmds.cluster ( "lip_cls", q=1, g=1 )
    objs = cmds.listRelatives( shapes, p=1 )
    obj = objs[0]
    clsIndices =grinFaceIndices(obj)
    
    size = cmds.polyEvaluate(obj, v=1)
    mouthWgt = []
    lipWgt = cmds.getAttr ("lip_cls.wl[0].w[0:"+str(size-1)+"]")
    rollWgt = cmds.getAttr ("lipRoll_cls.wl[0].w[0:"+str(size-1)+"]")
    jawOpenWgt = cmds.getAttr ("jawOpen_cls.wl[0].w[0:"+str(size-1)+"]")
    
    for i in clsIndices:
    
    	#first calculate the mouth with lip and lipRoll
        mouthWgt.append( min(1, max(lipWgt[i], rollWgt[i])) )
        '''if mouthWgt[i]<0:
    	    mouthWgt[i] = 0
    	mouthWgt[i] += rollWgt[i]
    	if mouthWgt[i]>1: mouthWgt[i] = 1'''		
    
    	# filter out lip area by multiple (1 - mouth)
        jawOpenWgt[i] *= pow((1 - mouthWgt[i]),1)
    
    	#then add the mouth back
        jawOpenWgt[i] += mouthWgt[i]
    
    valStr = ''
    mouthValStr = ''
    for i in range(size):
        tempVal = mouthWgt[i]
        mouthValStr += str(tempVal) + " "
    
        tmpVal = jawOpenWgt[i]
        valStr += str(tmpVal)+" "
                   
    commandStr = ("setAttr -s "+str(size)+" mouth_cls.wl[0].w[0:"+str(size-1)+"] "+mouthValStr);
    mel.eval (commandStr)
    
    commandStr = ("setAttr -s "+str(size)+" jawClose_cls.wl[0].w[0:"+str(size-1)+"] "+valStr);
    mel.eval (commandStr)






# cluster dictionary : 0보다 큰 웨이트값을 가진 버텍스 딕셔너리
def clsVertsDict( obj, cls):

    verts = {}
    for x in range(cmds.polyEvaluate( obj, v = 1)):
        val = cmds.percent( cls, obj+'.vtx[%s]'%x, q =1, v=1 )
        if val[0] > 0.001:
            verts[ x ] = val[0]
    return verts



import maya.mel as mel
def grinFaceIndices(headGeo):

    indices=[]
    if mel.eval('attributeExists "grinFace" %s'%headGeo): 
        indices = getAttr (headGeo+".grinFace")
    else:
        indices = range(cmds.polyEvaluate(headGeo, v=1))

	return indices



'''# 카피 스킨한 후, 웨이트값을 익스포트 한다.
1.copy weight from lipMapSurf to head_REN
2. export headSkin weight
3. cluster ctrl to 0
4. 100% skin weight to headSkel_jnt  
'''
#set up the project first!!
import maya.cmds as cmds
def exportLipMap(geoName):

    cls =[nd for nd in cmds.listHistory(geoName) if cmds.nodeType(nd) in ['cluster', 'blendShape', 'ffd' ] ]
    for c in cls:
        cmds.setAttr( c+ '.nodeState', 1)
    cmds.setAttr('jawOpen_cls.nodeState', 0)
    
    lipDict = clsVertsDict( 'head_REN', 'lip_cls')
    lipVert = [ 'head_REN.vtx[%s]'%t for t in lipDict ]
    
    mapVert = []
    for v in range(cmds.polyEvaluate( 'lipTip_map', v = 1)):
        mapVert.append('lipTip_map.vtx[%s]'%v)     
    cmds.select( mapVert, r=1)
    # select target vtx
    cmds.select( lipVert, add=1 )    
    cmds.copySkinWeights( sa= 'closestPoint', ia = 'closestJoint', sm=0, noMirror =1 )
    cmds.copySkinWeights( ss = 'headSkin', ds = 'headSkin', mirrorMode= 'YZ', sa= 'closestPoint', ia = 'closestJoint') 
    
    path = cmds.workspace(  q=True, dir= True )
    pathProject = path.split('scenes', 1)
    dataPath = pathProject[0]+'data'
    
    #overwrite the skin data    
    cmds.deformerWeights ('headSkin.xml', export =1, deformer="headSkin", path= dataPath ) 
    
    #jawOpenCls back to 0
    cmds.setAttr( 'jawOpen_ctl.t', 0,0,0)
    #set weight back to 1 on the headSkel_jnt
    vertNum = cmds.polyEvaluate( 'head_REN', v = 1)
    cmds.skinPercent( 'headSkin', 'head_REN.vtx[0:%s]'%(vertNum-1), tv = ['headSkel_jnt',1] )
    
    calExtraClsWgt()

    for c in cls:
        cmds.setAttr( c+ '.nodeState', 0)