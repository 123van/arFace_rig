import maya.cmds as cmds
import maya.mel as mel
from imp import reload
from twitchScript.face import blendShapeFunc

reload(blendShapeFunc)
from twitchScript.face import face_utils

reload(face_utils)
import re

'''
from twitchScript.face import weight_transferUI
reload(weight_transferUI)


wgtTran = weight_transferUI.WeightTransferUI()
wgtTran.show()
'''
print('shin')
class WeightTransferUI(face_utils.Util):

    def __init__(self, configFile=None):

        super(WeightTransferUI, self).__init__()
        # blendShapeFunc.BlendShapeFunc.__init__(self)

        self.UtilClass = face_utils.Util()
        self.BSClass = blendShapeFunc.BlendShapeFunc()
        self.configFile = configFile
        self.windowName = 'WeightTransferUI'
        self.textColor = [0.64, 0.42, 0.33]
        self.buttonColor = [0.8, 0.7, 0.6]
        self.existingTargets = {}
        self.sourceDeformer = None
        self.sourceItem = None
        self.sourceGeo = None

        # self.targetDformer = None

    def show(self):

        if cmds.window(self.windowName, query=True, exists=True):
            cmds.deleteUI(self.windowName)

        cmds.window(self.windowName, menuBar=True, widthHeight=(400, 600), bgc=[0.25, 0.3, 0.3])

        form = cmds.formLayout()

        self.buildUI(form)

        cmds.select(cl=1)

        cmds.showWindow()

    def buildUI(self, form):

        # cmds.columnLayout()
        # rowColumnLayout
        cmds.rowColumnLayout(numberOfColumns=4, bgc=[0.25, 0.3, 0.3],
                             columnWidth=[(1, 20), (2, 120), (3, 120), (4, 20)],
                             columnOffset=[(1, 'right', 5)])
        self.spaceBetween(1, 4, "text")

        cmds.text(label='')
        cmds.text(label='Source Weight', bgc=[.12, .2, .30], fn="boldLabelFont", height=20)
        self.spaceBetween(1, 7, "text")

        cmds.text(label='Select Source Geo with')
        cmds.text(label='Deformers               ')
        cmds.text(label=' ')
        self.spaceBetween(1, 1, "text")

        cmds.button(label='Source deformers', bgc=self.buttonColor, c=self.setWeightedDeformer)
        self.srcDeformOption = cmds.optionMenu('source_dformerList', bgc=[0, 0, 0], changeCommand=self.printNewMenuItem)

        self.spaceBetween(1, 2, "text")

        cmds.button(label='Weight Source Items', bgc=self.buttonColor, c=self.weightSourceItems)
        self.srcItemOption = cmds.optionMenu('source_itemList', bgc=[0, 0, 0], changeCommand=self.printNewMenuItem)
        self.spaceBetween(1, 10, "text")

        cmds.text(label='Target Weight', bgc=[.12, .2, .30], fn="boldLabelFont", height=20)
        self.spaceBetween(1, 7, "text")

        cmds.text(label='Select Tareget Geo with')
        cmds.text(label='Deformers                ')
        self.spaceBetween(1, 2, "text")

        cmds.button(label='Target deformers', bgc=self.buttonColor, c=self.setTargetDeformer)
        self.tgtDeformOption = cmds.optionMenu('target_dformerList', bgc=[0, 0, 0], changeCommand=self.printNewMenuItem)
        self.spaceBetween(1, 2, "text")

        cmds.button(label='Weight Target Items', bgc=self.buttonColor, c=self.weightTargetItems)
        self.trgtItemOption = cmds.optionMenu('target_itemList', bgc=[0, 0, 0], changeCommand=self.printNewMenuItem)
        self.spaceBetween(1, 10, "text")

        cmds.text(label='Transfer Weight', bgc=[.12, .2, .30], fn="boldLabelFont", height=20)
        cmds.text(label=' : From Source To Target')
        self.spaceBetween(1, 6, "text")

        cmds.button(label='deformerWeight to BS', bgc=self.buttonColor, c=self.deformerWeight_toBlendShape)
        # cmds.checkBox('invert', label='invert', w=10, align='center')
        cmds.checkBoxGrp('InvertBox', columnWidth2=[50, 100], numberOfCheckBoxes=1, label='Invert', v1=False)
        self.spaceBetween(1, 10, "text")

        cmds.text(label=' Create Corrective', bgc=[.12, .2, .30], fn="boldLabelFont", height=20)
        cmds.text(label=' : set a pose first!!')
        self.spaceBetween(1, 6, "text")

        cmds.text(label=' Target Name ')
        cmds.text(label=' Target & MainGeo')
        self.spaceBetween(1, 2, "text")

        cmds.textField("targetName", placeholderText="Type Target Name")
        cmds.button(label='Add Corrective or Reset', bgc=self.buttonColor, c=self.addCorrective_reset)
        self.spaceBetween(1, 2, "text")

        cmds.text(label=' Target & MainGeo')
        cmds.text(label=' Update Weights')
        cmds.text(label=' ')
        self.spaceBetween(1, 1, "text")

        cmds.button(label='joint To Corrective', bgc=self.buttonColor, c=self.jointWeight_toCorrective)
        cmds.button(label='bakeWeight_toCorrective', bgc=self.buttonColor, c=self.bakeWeight_toCorrective)

    def spaceBetween(self, numOfRow, numOfColm, space=""):

        for x in range(numOfRow):

            for i in range(numOfColm):

                if space == "text":
                    cmds.text(l='')

                elif space == "seperator":
                    cmds.separator(h=15)

    def printNewMenuItem(self, item):

        print(item)

    def setWeightedDeformer(self, *args):

        # Update the weightedDeformer list
        self.sourceGeo = cmds.ls(sl=1)
        if not self.sourceGeo:
            raise RuntimeError('select source mesh')

        sourceGeo = self.sourceGeo[0]
        optionMenuLabel = self.srcDeformOption
        self.setDeformer(optionMenuLabel, sourceGeo)

    def setTargetDeformer(self, *args):

        # Update the weightedDeformer list
        self.targetGeo = cmds.ls(sl=1)
        if not self.targetGeo:
            raise RuntimeError('select target mesh')

        targetGeo = self.targetGeo[0]
        optionMenuLabel = self.tgtDeformOption
        self.setDeformer(optionMenuLabel, targetGeo)

    def setDeformer(self, optionMenuLabel, geo):

        geoHistory = cmds.listHistory(geo, pruneDagObjects=1, interestLevel=1)
        self.weightedDeformer = [x for x in geoHistory if "geometryFilter" in cmds.nodeType(x, inherited=1)]

        # Clear existing items in the option menu
        if cmds.optionMenu(optionMenuLabel, exists=True):

            cmds.optionMenu(optionMenuLabel, edit=True, dai=True)

        else:
            cmds.warning("Option menu {} not found".format(optionMenuLabel))

        # Add the new items to the option menu
        for deformer in self.weightedDeformer:

            cmds.menuItem(label=deformer, p=optionMenuLabel)

    def addCorrective_reset(self, *args):

        """
        select target first and headGeo (add target in blendShape)
        """
        mySel = cmds.ls(os=1, type='transform')
        target = mySel[0]
        baseGeo = mySel[1]
        targetName = cmds.textField("targetName", q=True, text=True)

        self.addCorrectiveReset(target, baseGeo, targetName)

    def weightSourceItems(self, *args):

        self.sourceDeformer = cmds.optionMenu('source_dformerList', q=True, v=True)

        if not self.sourceDeformer:
            raise RuntimeError('select the deformer first!!')

        deformer = self.sourceDeformer
        option_menu = self.srcItemOption
        self.setWeightItems(deformer, option_menu)

    def weightTargetItems(self, *args):

        self.targetDeformer = cmds.optionMenu('target_dformerList', q=True, v=True)

        if not self.targetDeformer:
            raise RuntimeError('select the deformer first!!')

        deformer = self.targetDeformer
        option_menu = self.trgtItemOption

        self.setWeightItems(deformer, option_menu)

    def setWeightItems(self, deformer, optionMenuLabel):

        if cmds.nodeType(deformer) == "blendShape":

            targets = self.get_blendshape_targets(deformer)

            if targets:

                self.weightedItems = targets

            else:
                cmds.warning("No blendShape targets found for {}.".format(deformer))

        elif cmds.nodeType(deformer) == "skinCluster":

            wgtInfluences = cmds.skinCluster(deformer, q=1, wi=1)

            if wgtInfluences:
                self.weightedItems = wgtInfluences
            else:
                cmds.warning("No influences found for {}.".format(deformer))

        elif cmds.nodeType(deformer) == "cluster":

            self.weightedItems = [deformer]

        else:
            print('add {} to the source deformer'.format(cmds.nodeType(deformer)))

        # Clear existing items in the option menu
        if cmds.optionMenu(optionMenuLabel, exists=True):
            cmds.optionMenu(optionMenuLabel, edit=True, dai=True)
        else:
            cmds.warning("Option menu 'source_itemList' not found.")

        # Add the new items to the option menu
        for item in self.weightedItems:
            cmds.menuItem(label=item, p=optionMenuLabel)

    def deformerWeight_toBlendShape(self, *args):

        self.sourceDeformer = cmds.optionMenu('source_dformerList', q=True, v=True)
        self.sourceItem = cmds.optionMenu('source_itemList', q=True, v=True)

        if not self.sourceDeformer or not self.sourceItem:
            raise RuntimeError('select the source deformer and item first!!')

        self.targetDeformer = cmds.optionMenu('target_dformerList', q=True, v=True)
        self.targetItem = cmds.optionMenu('target_itemList', q=True, v=True)

        if not self.targetDeformer or not self.targetItem:
            raise RuntimeError('select the target deformer and item first!!')

        srcWgtTarget = self.sourceItem
        destWgtTarget = self.targetItem
        invertWgt = cmds.checkBoxGrp('InvertBox', q=True, v1=True)

        self.weightTransfer(srcWgtTarget, destWgtTarget, invertWgt)

    def jointWeight_toCorrective(self, *args):

        '''
        select target and baseGeo in order!
        The names of joint(" _jnt") would be part of the corrective name(" _crrct")
        '''

        self.sourceDeformer = cmds.optionMenu('source_dformerList', q=True, v=True)
        if not self.sourceDeformer:
            raise RuntimeError('Select the deformer first!!')

        source_deformer = self.sourceDeformer

        if not cmds.nodeType(source_deformer) == 'skinCluster':
            raise RuntimeError('Select SkinCluster')

        selection = cmds.ls(os=1)
        if not selection:
            raise RuntimeError('Select target and baseGeo in order')

        srcGeo = self.sourceGeo
        target = selection[0]
        mainGeo = self.targetGeo
        vtxNum = cmds.polyEvaluate(srcGeo, v=1)
        tgt_vtxNum = cmds.polyEvaluate(mainGeo, v=1)
        if not vtxNum == tgt_vtxNum:
            raise RuntimeError('Source Geo should be same as Target Geo')

        self.jntWeight_toCorrective(target)

    def get_targetIndex(self, bsNode, target):

        '''
        Returns the new target index if the target is not in bsNode,
        or the existing target index if the target is found.
        '''

        # Get the list of aliases and their weights
        aliasList = cmds.aliasAttr(bsNode, q=True)
        if not aliasList:

            raise RuntimeError('{} has no target'.format(bsNode))

        # Iterate over the alias list
        for tgt, wgt in zip(*[iter(aliasList)] * 2):

            targetIndex = int(re.findall(r'\d+', wgt)[0])
            self.existingTargets[tgt] = targetIndex

        # Check if the target is already in the blend shape node
        if target in self.existingTargets.keys():
            return self.existingTargets[target]

        # Return a new index
        else:
            return max(self.existingTargets.values()) + 1

    def jntWeight_toCorrective(self, sculptedGeo):

        """
        set source/ target optionMenu
        """
        if not self.targetGeo or not self.targetDeformer:
            raise RuntimeError('set target deformer')

        if not cmds.nodeType(self.sourceDeformer) == 'skinCluster':
            raise RuntimeError('set source deformer to skinCluster')

        if not cmds.nodeType(self.targetDeformer) == 'blendShape':
            raise RuntimeError('set target deformer to blendShape')

        mainGeo = self.targetGeo[0]
        BS_nodes = self.targetDeformer
        mapSkin = self.sourceDeformer

        aliasBS = cmds.aliasAttr(BS_nodes, q=1)
        if sculptedGeo in aliasBS:
            sculptedShape = cmds.listRelatives(sculptedGeo, c=1, s=1)[0]
            cnnct = cmds.listConnections(sculptedShape, s=0, d=1, p=1, type='blendShape')
            if cnnct:
                cmds.disconnectAttr('{}.worldMesh'.format(sculptedShape), cnnct[0])

        sourceIndex = self.get_targetIndex(BS_nodes, sculptedGeo)
        targetAlias = cmds.textField("targetName", q=True, text=True)  # or f"{sculptedGeo}_crrct"

        if targetAlias not in aliasBS:
            # add the target to get the delta value
            corrective_target = cmds.duplicate(sculptedGeo, rc=1, n=targetAlias)[0]
            cmds.blendShape(BS_nodes, e=1, tc=1, t=(mainGeo, sourceIndex, corrective_target, 1))
            cmds.blendShape(BS_nodes, e=True, resetTargetDelta=(0, sourceIndex))
            cmds.blendShape(BS_nodes, e=1, weight=(sourceIndex, 1.0))
            cmds.sculptTarget(BS_nodes, e=1, target=sourceIndex)
            cmds.delete(corrective_target)
            print('{} index number is {}'.format(sculptedGeo, sourceIndex))
            cmds.select(sculptedGeo, mainGeo, r=1)
            mel.eval("copyShape")

        jntList = [jnt for jnt in cmds.skinCluster(mapSkin, q=1, wi=1) if not "WJNT_PIN_01_C" in jnt]

        for jnt in jntList:

            # duplicate delta
            new_alias = '{}_{}'.format(jnt, targetAlias)
            targetIndex = cmds.blendShape(BS_nodes, q=1, wc=1)
            corrective_target = cmds.duplicate(mainGeo, rc=1, n=new_alias)[0]
            print(targetIndex, new_alias)
            cmds.blendShape(BS_nodes, e=1, tc=1, t=(mainGeo, targetIndex, corrective_target, 1))
            cmds.delete(corrective_target)
            cmds.blendShape(BS_nodes, e=True, resetTargetDelta=(0, targetIndex))

            comp = cmds.getAttr('{}.it[0].itg[{}].iti[6000].inputComponentsTarget'.format(BS_nodes, str(sourceIndex)))
            delta = cmds.getAttr('{}.it[0].itg[{}].iti[6000].inputPointsTarget'.format(BS_nodes, str(sourceIndex)))

            cmds.setAttr('{}.it[0].itg[{}].iti[6000].inputComponentsTarget'.format(BS_nodes, str(targetIndex)),
                         len(comp), *comp, type="componentList")

            cmds.setAttr('{}.it[0].itg[{}].iti[6000].inputPointsTarget'.format(BS_nodes, str(targetIndex)),
                         len(delta), *delta, type="pointArray")

            cmds.blendShape(BS_nodes, e=1, weight=(int(targetIndex), 0.0))

            self.weightTransfer(jnt, new_alias, 0)

        cmds.blendShape(BS_nodes, e=1, weight=(int(sourceIndex), 0.0))

    def weightTransfer(self, srcWgtTarget, destWgtTarget, invertWgt):

        print(srcWgtTarget, destWgtTarget)
        srcGeo = self.sourceGeo[0]
        srcDeformer = self.sourceDeformer
        destGeo = self.targetGeo
        destDform = self.targetDeformer

        srcType = cmds.nodeType(srcDeformer)
        destType = cmds.nodeType(destDform)

        vtxNum = cmds.polyEvaluate(srcGeo, v=1)
        weightVal = []
        if srcType == "skinCluster":
            jntID = face_utils.getJointIndex(srcDeformer, srcWgtTarget)
            weightVal = cmds.getAttr('{}.wl[0:{}].w[{}]'.format(srcDeformer, str(vtxNum - 1), jntID))

        elif srcType == "cluster":

            geometryIndex = face_utils.geoID_cluster(srcGeo, srcDeformer)
            weightVal = cmds.getAttr('{}.wl[{}].w[0:{}]'.format(srcDeformer, str(geometryIndex), str(vtxNum - 1)))

        elif srcType == "blendShape":

            tgtIndex = self.get_targetIndex(srcDeformer, srcWgtTarget)

            # {}.inputTarget[0].inputTargetGroup[{}].targetWeights[0:{}]
            weightVal = cmds.getAttr(
                '{}.it[0].itg[{}].tw[0:{}]'.format(srcDeformer, str(tgtIndex), str(vtxNum - 1)))

        else:
            print("working on it!!")

        print(invertWgt)
        if invertWgt:
            weightVal = [(1 - wgt) for wgt in weightVal]

        # transfer weightVals to the destination deformer
        if destType == 'cluster':

            geoIndex = face_utils.geoID_cluster(destGeo, destDform)
            cmds.setAttr('{}.wl[{}].w[0:{}]'.format(destDform, geoIndex, str(vtxNum - 1)), s=len(weightVal) - 1,
                         *weightVal)

        elif destType == "blendShape":

            tgtIndex = self.get_targetIndex(destDform, destWgtTarget)
            cmds.setAttr('{}.it[0].itg[{}].tw[0:{}]'.format(destDform, str(tgtIndex), str(vtxNum - 1)), *weightVal)

    def addCorrectiveReset(self, target, baseGeo, targetName):

        BSnodes = [x for x in cmds.listHistory(baseGeo, pdo=1) if cmds.nodeType(x) == 'blendShape']

        if not BSnodes or len(BSnodes) >= 2:
            raise RuntimeError('{} has no blendShape or more than 1'.format(mainGeo))

        aliasBS = cmds.aliasAttr(BSnodes[0], q=1)
        target_index = get_targetIndex(BSnodes[0], target)

        if target in aliasBS:

            cmds.blendShape(BSnodes[0], e=True, resetTargetDelta=(0, target_index))

        else:
            temp_target = cmds.duplicate(target, rc=1, n=targetName)[0]
            cmds.blendShape(BSnodes[0], e=1, tc=1, t=(baseGeo, target_index, temp_target, 1))
            cmds.delete(temp_target)
            cmds.blendShape(BSnodes[0], e=True, resetTargetDelta=(0, target_index))

            cmds.blendShape(BSnodes[0], e=True, weight=(target_index, 1.0))
            cmds.sculptTarget(BSnodes[0], e=True, target=target_index)

    def get_blendshape_targets(self, blendshape_node):

        # Get the targets of the blendShape node
        targets = cmds.listAttr(blendshape_node + '.w', multi=True) or []

        return targets

    # -----------------------------------------------------------------------------------------------------------

    def bakeWeight_toCorrective(self, wgtDeformer, wgtSourceItem, sculptedGeo, *args):

        """
        1. sculptedGeo add to BlendShape (delta only)
        2. if twitch has a sculptedGeo as target, then it rebuild the target
        wgtDeformer = mapSkinCluster / splitMap / cluster...on Geo that has same vtx order as headGeo
        wgtSourceItem = weighted obj list ( joints, shapes....)
        select sculpted geo and headGeo
        """
        self.headGeo = cmds.getAttr('helpPanel_grp.headGeo')

        # add blendShape target
        BS_nodes = [x for x in cmds.listHistory(self.headGeo, pdo=1) if cmds.nodeType(x) == 'blendShape']

        self.bsNode = [y for y in BS_nodes if not y == 'splitMapBS']
        aliasBS = cmds.aliasAttr(self.bsNode, q=1)
        baseTargetID = self.get_targetIndex(self.bsNode, sculptedGeo)

        if sculptedGeo in aliasBS:
            baseTargetID = wgtID + 1

        else:
            baseTargetID = wgtIDList[-1] + 1
            temp_target = cmds.duplicate(self.headGeo, rc=1, n="temp_{}".format(sculptedGeo))[0]
            cmds.blendShape(self.bsNode, e=1, tc=1, t=(self.headGeo, baseTargetID, temp_target, 1))
            cmds.blendShape(self.bsNode, e=True, resetTargetDelta=(0, baseTargetID))
            cmds.blendShape(self.bsNode, e=1, weight=(baseTargetID, 1.0))
            cmds.sculptTarget(self.bsNode, e=1, target=baseTargetID)
            cmds.delete(temp_target)
            cmds.select(sculptedGeo, self.headGeo, r=1)
            mel.eval("copyShape")

        baseIndex = self.get_targetIndex(self.bsNode, sculptedGeo)
        comp = cmds.getAttr('twitchBS.it[0].itg[{}].iti[6000].inputComponentsTarget'.format(str(baseIndex)))
        delta = cmds.getAttr('twitchBS.it[0].itg[{}].iti[6000].inputPointsTarget'.format(str(baseIndex)))
        print(comp, baseIndex, wgtSourceItem)
        self.deformerType = cmds.nodeType(wgtDeformer)

        for index, weightSrcName in enumerate(wgtSourceItem):

            # duplicate delta
            nameSplit = weightSrcName.split('_')
            if self.deformerType == "skinCluster":
                new_alias = '{}_{}_{}'.format(nameSplit[0], sculptedGeo, nameSplit[2])

            if self.deformerType == "blendShape":
                new_alias = '{}_{}'.format(nameSplit[0][0], sculptedGeo)

            tgtIndex = self.get_targetIndex(self.bsNode, new_alias)
            if not tgtIndex:

                tgtIndex = baseTargetID + index + 1
                temp_target = cmds.duplicate(self.headGeo, rc=1, n=new_alias)[0]
                print(tgtIndex, new_alias)
                cmds.blendShape(self.bsNode, e=1, tc=1, t=(self.headGeo, tgtIndex, temp_target, 1))
                cmds.delete(temp_target)
                cmds.blendShape(self.bsNode, e=True, resetTargetDelta=(0, tgtIndex))

            self.bakeWgt_toDelta(comp, delta, tgtIndex, weightSrcName, wgtDeformer)

            cmds.blendShape(self.bsNode, e=1, weight=(int(tgtIndex), 0.0))

    # check original one in blendShapeFunc module
    def bakeWgt_toDelta(self, comp, delta, bsTargetID, weightSrcName, dformer):

        # get weightValue(BS target, jnt) for vtx[index] in comp
        wgtValList = []

        # get "weightSrc values" within delta Component list
        if self.deformerType == "blendShape":

            weightSrcIndex = self.get_targetIndex(dformer, weightSrcName)
            print('{} target name is {} and weightIndex {}'.format(dformer, weightSrcName, weightSrcIndex))
            for vtxID in comp:

                vtxIndex = vtxID.split('vtx')[1]

                weightVal = cmds.getAttr(
                    '{}.inputTarget[0].inputTargetGroup[{}].targetWeights{}'.format(dformer, weightSrcIndex, vtxIndex))

                if isinstance(weightVal, list):
                    for val in weightVal:
                        wgtValList.append(val)
                else:
                    wgtValList.append(weightVal)

        elif self.deformerType == "skinCluster":

            jntID = face_utils.getJointIndex(dformer, weightSrcName)
            for vtxID in comp:

                vtxIndex = vtxID.split('vtx')[1]

                weightVal = cmds.getAttr('{}.wl{}.w[{}]'.format(dformer, vtxIndex, jntID))

                if isinstance(weightVal, list):

                    for val in weightVal:
                        wgtValList.append(val)
                else:
                    wgtValList.append(weightVal)

            newDelta = []
            for i, vector in enumerate(delta):

                pos = vector[:-1]
                wgtVal = wgtValList[i]
                if wgtVal < 0.001:
                    wgtVal = 0
                newPos = [wgtVal * p for p in pos]
                newPos.append(1.0)
                tuplePos = tuple(newPos)
                newDelta.append(tuplePos)

            cmds.setAttr('{}.it[0].itg[{}].iti[6000].inputComponentsTarget'.format(self.bsNode, str(bsTargetID)), len(comp),
                         *comp, type="componentList")
            cmds.setAttr('{}.it[0].itg[{}].iti[6000].inputPointsTarget'.format(self.bsNode, str(bsTargetID)), len(newDelta),
                         *newDelta, type="pointArray")


def normalize_name(name):
    prefix_map = {'R_': 'R_', 'r_': 'R_', 'Right': 'R_', 'right': 'R_', 'L_': 'L_', 'l_': 'L_', 'Left': 'L_',
                  'left': 'L_'}
    for prefix, standard in prefix_map.items():
        if name.startwith(prefix):
            normalized_name = name.replace(prefix, standard, 1)

        else:
            cmds.warning('{} has no prefix (R_, L_...)'.format(name))

    return normalized_name

def ctrl_connections():

    bsNode = 'appendHead_blendShape'
    positions = ["R_out", "R_mid", "R_in", "L_in", "L_mid", "L_out"]
    shapeDict = {"plus": ['browUp', 'relax'], "minus": ['browDown', 'furrow']}
    alias = cmds.aliasAttr(bsNode, q=1)
    for pos in positions:
        ctl = "{}_brow_ctl".format(pos)

        plusClamp = cmds.shadingNode('clamp', asUtility=1, n=ctl.replace('_ctl', '_plusClamp'))
        minusClamp = cmds.shadingNode('clamp', asUtility=1, n=ctl.replace('_ctl', '_minusClamp'))
        plusMult = cmds.shadingNode('multiplyDivide', asUtility=1, n=ctl.replace('_ctl', '_plusMult'))
        minusMult = cmds.shadingNode('multiplyDivide', asUtility=1, n=ctl.replace('_ctl', '_reverseMult'))
        cmds.connectAttr('{}.t'.format(ctl), '{}.input1'.format(plusMult), f=1)
        cmds.connectAttr('{}.t'.format(ctl), '{}.input1'.format(minusMult), f=1)
        cmds.setAttr('{}.input2'.format(plusMult), 2, 1, 1)
        cmds.setAttr('{}.input2'.format(minusMult), -2, -2, -1)

        cmds.connectAttr('{}.output'.format(plusMult), '{}.input'.format(plusClamp))
        cmds.connectAttr('{}.output'.format(minusMult), '{}.input'.format(minusClamp))
        cmds.setAttr("{}.max".format(plusClamp), 1, 2, 2)

        cmds.setAttr("{}.max".format(minusClamp), 1, 1, 1)

        for axis, shpPair in shapeDict.items():

            if axis == 'plus':
                tyTarget = [tgt for tgt in alias if "{}_{}".format(pos, shpPair[0]) in tgt][0]
                txTarget = [tgt for tgt in alias if "{}_{}".format(pos, shpPair[1]) in tgt][0]
                cmds.connectAttr('{}.outputR'.format(plusClamp), '{}.{}'.format(bsNode, txTarget))
                cmds.connectAttr('{}.outputG'.format(plusClamp), '{}.{}'.format(bsNode, tyTarget))

            elif axis == 'minus':
                tyTarget = [tgt for tgt in alias if "{}_{}".format(pos, shpPair[0]) in tgt][0]
                txTarget = [tgt for tgt in alias if "{}_{}".format(pos, shpPair[1]) in tgt][0]
                cmds.connectAttr('{}.outputR'.format(minusClamp), '{}.{}'.format(bsNode, txTarget))
                cmds.connectAttr('{}.outputG'.format(minusClamp), '{}.{}'.format(bsNode, tyTarget))


# not working because the joint movements are different for macro up and child ctrls up
'''
def ctrl_connectionsXX():
    bsNode = 'appendHead_blendShape'
    positions = ["R_out", "R_mid", "R_in", "L_in", "L_mid", "L_out"]
    shapeDict = {"plus": ['brow_jnt_browUp', 'brow_jnt_browWide'], "minus": ['brow_jnt_browDown', 'brow_jnt_furrow']}
    alias = cmds.aliasAttr(bsNode, q=1)

    mainCtlDict = {}
    for main in ["R_brow_ctl", "L_brow_ctl"]:
        main_plusMult = cmds.shadingNode('multiplyDivide', asUtility=1, n=ctl.replace('_ctl', '_plusMult'))
    main_minusMult = cmds.shadingNode('multiplyDivide', asUtility=1, n=ctl.replace('_ctl', '_reverseMult'))

    cmds.connectAttr(f'{main}.t', f'{main_plusMult}.input1', f=1)
    cmds.connectAttr(f'{main}.t', f'{main_minusMult}.input1', f=1)
    cmds.setAttr(f'{main_plusMult}.input2', 2, 1, 1)
    cmds.setAttr(f'{main_minusMult}.input2', -2, -1.0 / 0.8, -1)

    mainCtlDict[main] = {'plus': main_plusMult, 'minus': main_minusMult}

    for pos in positions:
        ctl = f"{pos}_brow_ctl"
        mainCtl = f"{pos[0]}_brow_ctl"

        mainPlusMult = mainCtlDict[mainCtl]['plus']
        mainMinusMult = mainCtlDict[mainCtl]['minus']

        plusClamp = cmds.shadingNode('clamp', asUtility=1, n=ctl.replace('_ctl', '_plusClamp'))
        minusClamp = cmds.shadingNode('clamp', asUtility=1, n=ctl.replace('_ctl', '_minusClamp'))
        plusMult = cmds.shadingNode('multiplyDivide', asUtility=1, n=ctl.replace('_ctl', '_plusMult'))
        minusMult = cmds.shadingNode('multiplyDivide', asUtility=1, n=ctl.replace('_ctl', '_reverseMult'))
        plusAverage = cmds.shadingNode('plusMinusAverage', asUtility=1, n=ctl.replace('_ctl', '_plusAverage'))
        minsuAverage = cmds.shadingNode('plusMinusAverage', asUtility=1, n=ctl.replace('_ctl', 'minsuAverage'))

        cmds.connectAttr(f'{ctl}.t', f'{plusMult}.input1', f=1)
        cmds.connectAttr(f'{ctl}.t', f'{minusMult}.input1', f=1)
        cmds.setAttr(f'{plusMult}.input2', 2, 1, 1)
        cmds.setAttr(f'{minusMult}.input2', -2, -1.0 / 0.8, -1)

        cmds.connectAttr(f'{plusMult}.output', f"{plusAverage}.input3D[0]")
        cmds.connectAttr(f'{mainPlusMult}.output', f"{plusAverage}.input3D[1]")

        cmds.connectAttr(f'{minusMult}.output', f"{minsuAverage}.input3D[0]")
        cmds.connectAttr(f'{mainMinusMult}.output', f"{minsuAverage}.input3D[1]")

        cmds.connectAttr(f'{plusAverage}.output3D', f'{plusClamp}.input')
        cmds.connectAttr(f'{minsuAverage}.output3D', f'{minusClamp}.input')
        cmds.setAttr(f"{plusClamp}.max", 2, 2, 2)

        cmds.setAttr(f"{minusClamp}.max", 2, 2, 1)

        for axis, shpPair in shapeDict.items():
            if axis == 'plus':
                tyTarget = [tgt for tgt in alias if f"{pos}_{shpPair[0]}" in tgt][0]
                txTarget = [tgt for tgt in alias if f"{pos}_{shpPair[1]}" in tgt][0]
                cmds.connectAttr(f'{plusClamp}.outputR', f'{bsNode}.{txTarget}')
                cmds.connectAttr(f'{plusClamp}.outputG', f'{bsNode}.{tyTarget}')

            elif axis == 'minus':
                tyTarget = [tgt for tgt in alias if f"{pos}_{shpPair[0]}" in tgt][0]
                txTarget = [tgt for tgt in alias if f"{pos}_{shpPair[1]}" in tgt][0]
                cmds.connectAttr(f'{minusClamp}.outputR', f'{bsNode}.{txTarget}')
                cmds.connectAttr(f'{minusClamp}.outputG', f'{bsNode}.{tyTarget}')'''

