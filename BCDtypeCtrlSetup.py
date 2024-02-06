# -*- coding: utf-8 -*-
#2/18/2018 bs = [twitchBS]
import maya.cmds as cmds

#[LR + "upSquint_crv", LR + "loSquint_crv"], [LR + "upAnnoyed_crv", LR + "loAnnoyed_crv"]
def CCtrlSetup( ctrl, LR, xyz, targetAList, targetBList):

    BSList = cmds.ls("*LipCrvBS", "*browBS", "*Shape_BS", "*Wide_BS", "*HiCrv_BS", "*twitchBS")
    bsListA = {}
    for tg in targetAList:
        if cmds.objExists(tg):
            bs = cmds.listConnections(cmds.listRelatives(tg, c=1, s=1)[0], d=1, s=0, type="blendShape")
            if bs:
                print(bs)
                tgBS = [x for x in bs if x in BSList]
                bsListA[tg] = tgBS[0]

            else:
                cmds.confirmDialog(title='Confirm', message='no blendShape is found for %s'%tg )
        else:
            bsListA[tg] = "twitchBS"           
        
    bsListB = {}
    for tgt in targetBList:
        if cmds.objExists(tgt):
            BS = cmds.listConnections(cmds.listRelatives(tgt, c=1, s=1)[0], d=1, s=0, type="blendShape")
            if BS:
                print(BS)
                tgtBS = [y for y in BS if y in BSList]
                bsListB[tgt] = tgtBS[0]

            else:
                cmds.confirmDialog(title='Confirm', message='no blendShape is found for %s'%tgt)
        else:
            bsListB[tgt] = "twitchBS"
            
    invertMult = cmds.shadingNode("multiplyDivide", asUtility=1, n=LR+"invert_mult")
    cmds.setAttr(invertMult + ".input2", -1, -1, -1)
    posRemap = cmds.shadingNode("remapValue", asUtility=1, n=LR+"posRemap")
    negRemap = cmds.shadingNode("remapValue", asUtility=1, n=LR+"negRemap")
    
    cmds.connectAttr(ctrl + ".t"+xyz[1], invertMult + ".input1"+xyz[1].title())
    cmds.connectAttr(invertMult + ".output"+xyz[1].title(), posRemap + ".inputMin")
    cmds.connectAttr(invertMult + ".output"+xyz[1].title(), negRemap + ".inputMin")
    
    cmds.connectAttr(ctrl + ".t" + xyz[0], invertMult + ".input1" + xyz[0].title() )
    cmds.connectAttr(invertMult + ".output" + xyz[0].title(), negRemap + ".inputValue" )
    cmds.connectAttr(ctrl + ".t" + xyz[0], posRemap + ".inputValue")

    for target, aBS in bsListA.iteritems():
        print(aBS + "." + target)
        cmds.connectAttr(posRemap + ".outValue", aBS + "." + target)

    for tgt, bBS in bsListB.iteritems():
        print(bBS + "." + tgt)
        cmds.connectAttr(negRemap + ".outValue", bBS + "." + tgt)


#BCtrlSetup("l_brow_Furrow_ctl","l_","y", "lFurrow_crv", "lRelax_crv") 
#            컨트롤 네임 ,   좌/우,  "x"or"y"or"z"          
#BCtrlSetup("l_brow_madsad","l_","y", "l_browSad","l_browMad") 
def BCtrlSetup(ctrl, xyz, plusList, minusList):
    """
    arFace setup targets must be in crvBS or twitchBS
    """

    plusPair = {}
    minusPair = {}
    for tg in plusList:
        if cmds.objExists(tg):
            shape = cmds.listRelatives(tg, c=1, s=1)
            bs = cmds.listConnections(shape[0], d=1, s=0, type="blendShape")
            if bs:
                print(bs)
                plusPair[tg] = bs[0]
            else:
                cmds.confirmDialog(title='Confirm', message='no blendShape is found for {}'.format(tg))
                    
        else:
            plusPair[tg] = "twitchBS"

    for tgt in minusList:
        if cmds.objExists(tgt):
            tgtShp = cmds.listRelatives(tgt, c=1, s=1)[0]
            BS = cmds.listConnections(tgtShp, d=1, s=0, type="blendShape")
            print(BS)
            if BS:
                minusPair[tgt] = BS[0]
            else:
                cmds.confirmDialog(title='Confirm', message='no blendShape is found for {}'.format(tgt))

        else:
            minusPair[tgt] = "twitchBS"
            
    ctlNegMult = cmds.shadingNode('multiplyDivide', asUtility=1, n=ctrl+'Neg_mult')
    cmds.setAttr(ctlNegMult + '.input2', -1, -1, -1)
    cmds.connectAttr(ctrl+".t" + xyz, ctlNegMult+".input1"+xyz.title())
    
    ctlClamp = cmds.shadingNode('clamp', asUtility=1, n=ctrl+'Neg_clamp')
    # plus --> inputR
    cmds.connectAttr(ctrl+".t" + xyz, ctlClamp + '.inputR')
    cmds.setAttr(ctlClamp + ".maxR", 1)
    # minus --> inputG
    cmds.connectAttr(ctlNegMult+".output"+xyz.title(), ctlClamp + '.inputG' )
    cmds.setAttr(ctlClamp + ".maxG", 1)
    
    for target, BS in plusPair.items():
        cmds.connectAttr(ctlClamp + '.outputR', '{}.{}'.format(BS, target))

    for target, BS in minusPair.items():
        cmds.connectAttr(ctlClamp + '.outputG', '{}.{}'.format(BS, target))



'''
xPosYPos * yPosXPos == U
xPosYNeg * yNegXPos == O
xNegYNeg * yNegXNeg == Wide
xNegYPos * yPosXNeg == E '''
#DCtrlSetup( "l_phonemes_ctl", "l_phoneme", "lip")
def DCtrlSetup(ctrl, name, factor):

    if "l_" in name:
        prefix = "l_"
    elif "r_" in name:
        prefix = "r_"
    else:
        prefix = name

    inverse = cmds.shadingNode('multiplyDivide', asUtility=1, n=prefix + 'ctlNeg_mult')

    # tx inputValue / ty inputMin
    xPosYPos = cmds.shadingNode('remapValue', asUtility =1, n = prefix + 'xPosYPos_remap')
    xNegYPos = cmds.shadingNode('remapValue', asUtility =1, n = prefix + 'xNegYPos_remap')
    xPosYNeg = cmds.shadingNode('remapValue', asUtility =1, n = prefix + 'xPosYNeg_remap')
    xNegYNeg = cmds.shadingNode('remapValue', asUtility =1, n = prefix + 'xNegYNeg_remap')
    
    yPosXPos = cmds.shadingNode('remapValue', asUtility =1, n = prefix + 'yPosXPos_remap')
    yNegXPos = cmds.shadingNode('remapValue', asUtility =1, n = prefix + 'yNegXPos_remap')
    yPosXNeg = cmds.shadingNode('remapValue', asUtility =1, n = prefix + 'yPosXNeg_remap')
    yNegXNeg = cmds.shadingNode('remapValue', asUtility =1, n = prefix + 'yNegXNeg_remap')
    
    AMult = cmds.shadingNode('multiplyDivide', asUtility =1, n = prefix + 'A_Mult')
    BMult = cmds.shadingNode('multiplyDivide', asUtility =1, n = prefix + 'B_Mult')
    CMult = cmds.shadingNode('multiplyDivide', asUtility =1, n = prefix + 'C_Mult')
    DMult = cmds.shadingNode('multiplyDivide', asUtility =1, n = prefix + 'D_Mult')
    
    attrs = ['X_pos','Y_pos', 'X_neg', 'Y_neg', 'XPos_YPos', 'XPos_YNeg', 'XNeg_YNeg', 'XNeg_YPos']
    cmds.select(factor+"Factor")
    for att in attrs:
        if not cmds.attributeQuery(name+att, node=factor+"Factor", exists=True):
            cmds.addAttr(longName=name+att, attributeType='double')
    
    #inverse "ctrl.tx/ty" to minus  
    cmds.connectAttr(ctrl + '.tx', inverse + '.input1X')
    cmds.connectAttr(ctrl + '.ty', inverse + '.input1Y')
    cmds.setAttr(inverse + '.input2', -1, -1, -1)

    #"ctrl.tx/ty" 
    cmds.connectAttr(ctrl + '.tx', factor + 'Factor.' + name+'X_pos')
    cmds.connectAttr(ctrl + '.ty', factor + 'Factor.' + name+'Y_pos')
    
    #inverse "ctrl.tx/ty" 
    cmds.connectAttr(inverse + '.outputX', factor + 'Factor.' + name+'X_neg')
    cmds.connectAttr(inverse + '.outputY', factor + 'Factor.' + name+'Y_neg')

    posClamp = cmds.shadingNode('clamp', asUtility=1, n=name + 'xyPos_clamp')
    cmds.connectAttr(factor + 'Factor.' + name + 'X_pos', posClamp + ".inputR")
    cmds.connectAttr(factor + 'Factor.' + name + 'Y_pos', posClamp + ".inputG")
    cmds.setAttr(posClamp + ".minR", -1)
    cmds.setAttr(posClamp + ".minG", -1)
    cmds.setAttr(posClamp + ".maxR", 1)
    cmds.setAttr(posClamp + ".maxG", 1)
    
    negClamp = cmds.shadingNode('clamp', asUtility=1, n=name + 'xyNeg_clamp' )
    cmds.connectAttr(factor + 'Factor.' + name + 'X_neg', negClamp + ".inputR")
    cmds.connectAttr(factor + 'Factor.' + name + 'Y_neg', negClamp + ".inputG")
    cmds.setAttr(negClamp + ".minR", -1)
    cmds.setAttr(negClamp + ".minG", -1)
    cmds.setAttr(negClamp + ".maxR", 1)
    cmds.setAttr(negClamp + ".maxG", 1)
        
    #1...xPosYPos * yPosXPos == U (BMult) # inputMin
    cmds.connectAttr(factor + 'Factor.' + name+'X_pos', xPosYPos + ".inputValue")
    #negClamp.outputG =factor +'Factor.' + name+'Y_neg'
    cmds.connectAttr(negClamp + ".outputG", xPosYPos + ".inputMin")# set Y_neg to open plus Y
    
    cmds.connectAttr(factor + 'Factor.' + name+'Y_pos', yPosXPos + ".inputValue")
    #negClamp.outputR =factor +'Factor.' + name+'X_neg'
    cmds.connectAttr(negClamp + ".outputR", yPosXPos + ".inputMin")# set X_neg to open plus X
    
    #multiply 2 remap
    cmds.connectAttr(xPosYPos + ".outValue", BMult + ".input1X")
    cmds.connectAttr(yPosXPos + ".outValue", BMult + ".input2X")
    cmds.connectAttr(BMult + ".outputX", factor + 'Factor.' + name+'XPos_YPos')
    
    #2...xPosYNeg * yNegXPos == O (CMult)
    cmds.connectAttr(factor + 'Factor.' + name+'X_pos', xPosYNeg + ".inputValue")
    #posClamp.outputG =factor +'Factor.' + name+'Y_pos'
    cmds.connectAttr(posClamp + ".outputG", xPosYNeg + ".inputMin")# set Y_pos to open minus Y
    
    cmds.connectAttr(factor + 'Factor.' + name+'Y_neg', yNegXPos + ".inputValue")
    #negClamp.outputR =factor +'Factor.' + name+'X_neg'
    cmds.connectAttr(negClamp + ".outputR", yNegXPos + ".inputMin")# set X_neg to get plus X
    
    cmds.connectAttr(xPosYNeg + ".outValue", CMult + ".input1X" )
    cmds.connectAttr(yNegXPos + ".outValue", CMult + ".input2X" )
    cmds.connectAttr(CMult + ".outputX", factor + 'Factor.' + name+'XPos_YNeg' )
    
    #3...xNegYNeg * yNegXNeg == Wide (DMult)
    cmds.connectAttr( factor + 'Factor.' + name+'X_neg', xNegYNeg + ".inputValue" )
    #posClamp.outputG =factor +'Factor.' + name+'Y_pos'
    cmds.connectAttr( posClamp + ".outputG", xNegYNeg + ".inputMin" )# set X_pos to get minus X
    
    cmds.connectAttr( factor + 'Factor.' + name+'Y_neg', yNegXNeg + ".inputValue" )
    #posClamp.outputR =factor +'Factor.' + name+'X_pos'
    cmds.connectAttr( posClamp + ".outputR", yNegXNeg + ".inputMin" )
    
    cmds.connectAttr( xNegYNeg + ".outValue", DMult + ".input1X")
    cmds.connectAttr( yNegXNeg + ".outValue", DMult + ".input2X")
    cmds.connectAttr( DMult + ".outputX", factor + 'Factor.' + name+'XNeg_YNeg' )
    
    #4...xNegYNeg * yNegXNeg == E (AMult)
    cmds.connectAttr( factor + 'Factor.' + name+'X_neg', xNegYPos + ".inputValue" )
    #negClamp.outputG =factor +'Factor.' + name+'Y_neg'    
    cmds.connectAttr( negClamp + ".outputG", xNegYPos + ".inputMin" )# factor +'Factor.' + name+'Y_neg'
    
    cmds.connectAttr( factor + 'Factor.' + name+'Y_pos', yPosXNeg + ".inputValue" )
    #posClamp.outputR =factor +'Factor.' + name+'X_pos'
    cmds.connectAttr( posClamp + ".outputR", yPosXNeg + ".inputMin" )# factor +'Factor.' + name+'X_pos'
    
    cmds.connectAttr( xNegYPos + ".outValue", AMult + ".input1X")
    cmds.connectAttr( yPosXNeg + ".outValue", AMult + ".input2X")
    cmds.connectAttr( AMult + ".outputX", factor + 'Factor.' + name+'XNeg_YPos')
    
    
'''
xPosYPos * yPosXPos == U
xPosYNeg * yNegXPos == O
xNegYNeg * yNegXNeg == Wide
xNegYPos * yPosXNeg == E 

def DCtrlSetup( ctrl, name, factor ):
    
inverse = cmds.shadingNode( 'multiplyDivide', asUtility =1, n = 'ctlNegMult' )

# tx inputValue / ty inputMin
xPosYPos = cmds.shadingNode( 'remapValue', asUtility =1, n = 'xPosYPos_remap' )
xNegYPos = cmds.shadingNode( 'remapValue', asUtility =1, n = 'xNegYPos_remap' )
xPosYNeg = cmds.shadingNode( 'remapValue', asUtility =1, n = 'xPosYPos_remap' )
xNegYNeg = cmds.shadingNode( 'remapValue', asUtility =1, n = 'xNegYPos_remap' )

yPosXPos = cmds.shadingNode( 'remapValue', asUtility =1, n = 'yPosXPos_remap' )
yNegXPos = cmds.shadingNode( 'remapValue', asUtility =1, n = 'yNegXPos_remap' )
yPosXNeg = cmds.shadingNode( 'remapValue', asUtility =1, n = 'yPosXPos_remap' )
yNegXNeg = cmds.shadingNode( 'remapValue', asUtility =1, n = 'yNegXNeg_remap' )


AMult = cmds.shadingNode( 'multiplyDivide', asUtility =1, n = 'A_Mult' )
BMult = cmds.shadingNode( 'multiplyDivide', asUtility =1, n = 'B_Mult' )
CMult = cmds.shadingNode( 'multiplyDivide', asUtility =1, n = 'C_Mult' )
DMult = cmds.shadingNode( 'multiplyDivide', asUtility =1, n = 'D_Mult' )

attrs = ['X_pos','X_neg','Y_pos','Y_neg','XPos_YNeg','XPos_YPos','XNeg_YNeg', 'XNeg_YPos']
cmds.select( factor+"Factor")
for att in attrs:
    if cmds.attributeQuery( name+att, node= factor+"Factor", exists=True)==False:
        cmds.addAttr( longName= name+att, attributeType='double' )

#inverse "ctrl.tx/ty" to minus  
cmds.connectAttr( ctrl + '.tx', inverse + '.input1X' )
cmds.connectAttr( ctrl + '.ty', inverse + '.input1Y' )
cmds.setAttr( inverse + '.input2', -1,-1,-1 )

#"ctrl.tx/ty" 
cmds.connectAttr( ctrl + '.tx', factor +'Factor.' + name+'X_pos'  )
cmds.connectAttr( ctrl + '.ty', factor +'Factor.' + name+'Y_pos'  )

#inverse "ctrl.tx/ty" 
cmds.connectAttr( inverse + '.outputX', factor +'Factor.' + name+'X_neg'  )
cmds.connectAttr( inverse + '.outputY', factor +'Factor.' + name+'Y_neg'  )

#xPosYPos * yPosXPos == U (BMult)
cmds.connectAttr( factor +'Factor.' + name+'X_pos', xPosYPos + ".inputValue" )
cmds.connectAttr( factor +'Factor.' + name+'Y_neg', xPosYPos + ".inputMin" )# set inputMin -1

cmds.connectAttr( factor +'Factor.' + name+'Y_pos', yPosXPos + ".inputValue" )
cmds.connectAttr( factor +'Factor.' + name+'X_neg', yPosXPos + ".inputMin" )# set inputMin -1'''
