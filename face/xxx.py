from maya import cmds
from imp import reload
import maya.mel as mel

# from conLibrary import app
# reload(app)
from conLibrary import controllerLibTest

reload(controllerLibTest)
from twitchScript.face import faceFactor

reload(faceFactor)
from functools import partial
from twitchScript.face import face_utils, faceSkin, curve_utils, blendShapeFunc

reload(face_utils)
reload(faceSkin)
reload(curve_utils)
reload(blendShapeFunc)
import os

USERAPPDIR = cmds.internalVar(userAppDir=1)
DIRECTORY = os.path.join(USERAPPDIR, "arcMaFile")


def createDirectoryTest(directory=DIRECTORY):
    if not os.path.exists(DIRECTORY):
        os.mkdir(DIRECTORY)
    return DIRECTORY


def printNewMenuItem(item, *args):
    print(item)


def spaceBetween(numOfRow, numOfColm, space=""):
    for x in range(numOfRow):
        for i in range(numOfColm):
            if space == "text":
                cmds.text(l='')

            elif space == "seperator":
                cmds.separator(h=15)

class faceAssistUI(face_utils.Util):

    def __init__(self, configFile=None):

        super(faceAssistUI, self).__init__()
        # face_utils.Util.__init__(self)

        # self.util = face_utils.Util()
        self.skin = None
        self.ctlLib = None
        self.ctl = None
        self.configFile = configFile
        self.windowName = 'bardelFaceUI'
        self.headInfo = {}
        self.vertexData = {}
        self.lipOrderVtx = {}
        self.textColor = [0.64, 0.42, 0.33]
        self.buttonColor = [0.8, 0.7, 0.6]
        self.directory = createDirectoryTest()
        self.targetsForCtls = {}
        self.BSClass = None
        self.locList = []

    def show(self):

        if cmds.window(self.windowName, query=True, exists=True):
            cmds.deleteUI(self.windowName)

        cmds.window(self.windowName, menuBar=False, widthHeight=(400, 1000), bgc=[0.25, 0.3, 0.3])

        form = cmds.formLayout()

        self.buildUI(form)

        cmds.select(cl=1)

        cmds.showWindow()

    def buildUI(self, form):

        tabs = cmds.tabLayout(innerMarginWidth=5, innerMarginHeight=5)
        cmds.formLayout(form, edit=True,
                        attachForm=((tabs, 'top', 0), (tabs, 'left', 0), (tabs, 'bottom', 0), (tabs, 'right', 0)))

        runAllTab = cmds.columnLayout()
        # rowColumnLayout
        runAllRowCol = cmds.rowColumnLayout(numberOfColumns=5, bgc=[0.25, 0.3, 0.3],
                                            columnWidth=[(1, 20), (2, 120), (3, 120), (4, 120), (5, 20)],
                                            columnOffset=[(1, 'right', 5)])
        spaceBetween(1, 5, "text")

        cmds.text(label='')
        cmds.text(label='Foundation', bgc=[.12, .2, .30], fn="boldLabelFont", height=20)
        spaceBetween(1, 8, "text")

        cmds.text(label='')
        cmds.button(label='Build', bgc=self.buttonColor, command=self.buildFoundation)
        spaceBetween(1, 8, "text")

        cmds.setParent(runAllTab)

        cmds.rowColumnLayout(numberOfColumns=5, bgc=[0.25, 0.3, 0.3],
                             columnWidth=[(1, 20), (2, 120), (3, 120), (4, 120), (5, 20)],
                             columnOffset=[(1, 'right', 5)])

        cmds.text(label='')
        cmds.text(label="Select 'face part'")
        cmds.text(label="corner(s)/ direction vtx")
        cmds.text(label="")
        cmds.text(label='')

        cmds.text(label='')
        cmds.optionMenu('eye_lip_brow', bgc=[0, 0, 0], changeCommand=printNewMenuItem)
        cmds.menuItem(label='brow')
        cmds.menuItem(label='eye')
        cmds.menuItem(label='lip')
        cmds.button(label='Ordered Vertices', bgc=self.buttonColor, command=self.setOrderedVert_upLo)
        cmds.text(label='')

        cmds.setParent(runAllTab)

        cmds.rowColumnLayout(numberOfColumns=4, bgc=[0.25, 0.3, 0.3],
                             columnWidth=[(1, 20), (2, 120), (3, 240), (4, 20)],
                             columnOffset=[(1, 'right', 5)])

        spaceBetween(1, 4, "text")
        self.vertexData = self.createVtxData()
        cmds.text(label='')
        cmds.button(label='Brow Select', bgc=self.buttonColor, c=partial(self.selectVertices, 'eyebrowVertsTextField'))
        if 'browVerts' in self.vertexData:
            insertText = self.vertexData['browVerts']
        else:
            insertText = ''
        self.eyebrowVertsTextField = cmds.textField('eyebrowVertsTextField', ed=False, tx=str(insertText), w=240)
        spaceBetween(1, 2, "text")

        cmds.button(label='Up EyeLid Select', bgc=self.buttonColor,
                    c=partial(self.selectVertices, 'upEyelidVertsTextField'))
        if 'upLidVerts' in self.vertexData:
            insertText = self.vertexData['upLidVerts']
        else:
            insertText = ''
        self.upEyelidVertsTextField = cmds.textField('upEyelidVertsTextField', ed=False, tx=str(insertText), w=240)

        spaceBetween(1, 2, "text")

        cmds.button(label='Low EyeLid Select', bgc=self.buttonColor,
                    c=partial(self.selectVertices, 'loEyelidVertsTextField'))
        if 'loLidVerts' in self.vertexData:
            insertText = self.vertexData['loLidVerts']
        else:
            insertText = ''
        self.loEyelidVertsTextField = cmds.textField('loEyelidVertsTextField', ed=False, tx=str(insertText), w=240)

        spaceBetween(1, 2, "text")

        cmds.button(label='Up Lip Select', bgc=self.buttonColor, c=partial(self.selectVertices, 'upLipVertsTextField'))
        if 'upLipVerts' in self.vertexData:
            insertText = self.vertexData['upLipVerts']
        else:
            insertText = ''
        self.upLipVertsTextField = cmds.textField('upLipVertsTextField', ed=False, tx=str(insertText), w=240)

        spaceBetween(1, 2, "text")

        cmds.button(label='Low Lip Select', bgc=self.buttonColor, c=partial(self.selectVertices, 'loLipVertsTextField'))
        if 'loLipVerts' in self.vertexData:
            insertText = self.vertexData['loLipVerts']
        else:
            insertText = ''
        self.loLipVertsTextField = cmds.textField('loLipVertsTextField', ed=False, tx=str(insertText), w=240)
        spaceBetween(1, 2, "text")

        cmds.setParent('..')

        # rowColumnLayout
        cmds.rowColumnLayout(numberOfColumns=5, bgc=[0.25, 0.3, 0.3],
                             columnWidth=[(1, 20), (2, 120), (3, 120), (4, 120), (5, 20)],
                             columnOffset=[(1, 'right', 5)])

        spaceBetween(1, 6, "text")
        cmds.text(label='Curve On Mesh', bgc=[.12, .2, .30], fn="boldLabelFont", height=20)
        spaceBetween(1, 8, "text")

        cmds.text(label='')
        cmds.text(label='face part            ')
        cmds.text(label='upper / lower')
        cmds.text(label='guideLength')
        spaceBetween(1, 2, "text")

        cmds.optionMenu('facePartName', bgc=[0, 0, 0], highlightColor=[0.9, 0.5, 0.4], changeCommand=printNewMenuItem)
        cmds.menuItem(label="")
        cmds.menuItem(label="brow")
        cmds.menuItem(label="eye")
        cmds.menuItem(label="lip")
        cmds.menuItem(label="Nose")
        cmds.menuItem(label="Cheek")
        cmds.menuItem(label="Teeth")

        cmds.optionMenu('upperLower', bgc=[0, 0, 0], changeCommand=printNewMenuItem)
        cmds.menuItem(label='')
        cmds.menuItem(label='up')
        cmds.menuItem(label='lo')
        cmds.menuItem(label='center')

        # cmds.optionMenu('guideLength', bgc=[0, 0, 0], changeCommand= printNewMenuItem)
        cmds.intField('guideLength', bgc=[0, 0, 0], minValue=0, maxValue=20, value=7, changeCommand=printNewMenuItem)

        spaceBetween(1, 7, "text")

        cmds.button(label='createFaceCrv', bgc=self.buttonColor, command=self.faceCrv_onVtxList)
        cmds.button(label='Match Guides', bgc=self.buttonColor, command=self.matchGuides)
        cmds.button(label='Custom Curve', bgc=self.buttonColor, command=self.evenLocCustomCrv)
        spaceBetween(1, 1, "text")

        cmds.setParent('..')
        cmds.setParent('..')

        skinTab = cmds.columnLayout()
        cmds.rowColumnLayout(numberOfColumns=5, bgc=[0.25, 0.3, 0.3],
                             columnWidth=[(1, 20), (2, 120), (3, 120), (4, 120), (5, 20)],
                             columnOffset=[(1, 'right', 5)])
        spaceBetween(1, 5, "text")

        cmds.text(label='')
        cmds.text(label='Face Cluster', bgc=[.12, .2, .30], fn="boldLabelFont", height=20)
        spaceBetween(1, 8, "text")

        cmds.setParent('..')
        cmds.setParent('..')

        shapeTab = cmds.columnLayout()
        cmds.rowColumnLayout(numberOfColumns=5, bgc=[0.25, 0.3, 0.3],
                             columnWidth=[(1, 20), (2, 120), (3, 120), (4, 120), (5, 20)],
                             columnOffset=[(1, 'right', 5)])

        spaceBetween(1, 6, "text")

        cmds.text(label='   select base   ', fn="boldLabelFont", height=20)
        spaceBetween(1, 4, "text")

        cmds.button(label='weight transfer', bgc=self.buttonColor, command=self.weightTransfer)
        spaceBetween(1, 9, "text")

        cmds.text(label='Deformer on the Geo with')
        cmds.text(label='same vertex order as the')
        cmds.text(label='headGeo                          ')
        spaceBetween(1, 2, "text")

        cmds.button(label='Source Deformer', bgc=self.buttonColor, c=self.setWeightedDeformer)
        self.weightedDeformer = cmds.textField('weightedDeformer', ed=True, tx='', w=240)
        spaceBetween(1, 3, "text")

        cmds.button(label='Weight Source Items', bgc=self.buttonColor, c=self.weightSourceItems)
        self.weightedItems = cmds.textField('weightedItems', ed=True, tx='', w=240)
        spaceBetween(1, 8, "text")

        # cmds.button(label='Add Corrective & Reset', bgc=self.buttonColor, c=self.addCorrective_reset)
        # cmds.button(label='bakeWgt To Corrective', bgc=self.buttonColor, c=self.bakeWeight_toCorrective)

        cmds.tabLayout(tabs,
                       edit=True,
                       tabLabel=((runAllTab, 'Run It All'), (skinTab, 'Skinning'), (shapeTab, 'shape'))
                       )

    def buildFoundation(self, *args):
        """
        build all foundation together
        """
        fFactor = faceFactor.FaceFactor(configFile=self.configFile)
        fFactor.create()

    def createVtxData(self, *args):
        if cmds.objExists("faceFactors"):

            if cmds.attributeQuery("l_upLidVerts", node="lidFactor", exists=1):
                self.vertexData["upLidVerts"] = cmds.getAttr("lidFactor.l_upLidVerts")

            if cmds.attributeQuery("l_loLidVerts", node="lidFactor", exists=1):
                self.vertexData["loLidVerts"] = cmds.getAttr("lidFactor.l_loLidVerts")

            if cmds.attributeQuery("upLipVerts", node="lipFactor", exists=1):
                self.vertexData["upLipVerts"] = cmds.getAttr("lipFactor.upLipVerts")

            if cmds.attributeQuery("loLipVerts", node="lipFactor", exists=1):
                self.vertexData["loLipVerts"] = cmds.getAttr("lipFactor.loLipVerts")

            if cmds.attributeQuery("browVerts", node="browFactor", exists=1):
                self.vertexData["browVerts"] = cmds.getAttr("browFactor.browVerts")

        return self.vertexData

    def selectVertices(self, txtField, *args):
        """
        select vertexes in text field
        """
        parts = cmds.textField(txtField, q=True, tx=True)
        print(parts)
        if parts:
            cmds.select(eval(parts), r=True)
        else:
            cmds.select(cl=True)

    def updateVtxSelection(self, *args):
        """

        Returns:

        """
        currentName = self.optionMenu_refresh("eye_lip_brow")

        vrtSelection = cmds.ls(os=1, fl=1)

        self.vertexData = self.createVtxData()

        if currentName == "brow":

            orderedVerts = vrtSelection

            if not cmds.attributeQuery("browVerts", node="browFactor", exists=1):
                cmds.addAttr("browFactor", ln="browVerts", dt="stringArray")

            cmds.setAttr("browFactor.browVerts", type="stringArray", *([len(orderedVerts)] + orderedVerts))

            self.vertexData["browVerts"] = orderedVerts
            cmds.textField(self.eyebrowVertsTextField, e=True, tx=str(self.vertexData["browVerts"]))

        elif currentName == "eye":

            upLidVerts = vrtSelection
            loLidVerts = vrtSelection

            if not cmds.attributeQuery("l_upLidVerts", node="lidFactor", exists=1):
                cmds.addAttr("lidFactor", ln="l_upLidVerts", dt="stringArray")

            cmds.setAttr("lidFactor.l_upLidVerts", type="stringArray", *([len(upLidVerts)] + upLidVerts))

            self.vertexData["l_upLidVerts"] = upLidVerts
            cmds.textField(self.eyebrowVertsTextField, e=True, tx=str(self.vertexData["l_upLidVerts"]))

            if not cmds.attributeQuery("l_loLidVerts", node="lidFactor", exists=1):
                cmds.addAttr("lidFactor", ln="l_loLidVerts", dt="stringArray")

            cmds.setAttr("lidFactor.l_loLidVerts", type="stringArray", *([len(loLidVerts)] + loLidVerts))

            self.vertexData["l_loLidVerts"] = loLidVerts
            cmds.textField(self.eyebrowVertsTextField, e=True, tx=str(self.vertexData["l_loLidVerts"]))

        elif currentName == "lip":

            if self.vertexData["upLipVerts"]:
                pass

            if self.vertexData["loLipVerts"]:
                pass

    def setOrderedVert_upLo(self, *pArgs):
        # cmds.optionMenu('eye_lip_brow', query=True, value=True)
        currentName = self.optionMenu_refresh("eye_lip_brow")
        trioSel = cmds.ls(os=1, fl=1)
        trioVtx = curve_utils.orderedTrioVert(trioSel)

        if currentName == "brow":

            orderedVtx = curve_utils.browOrderedVertices(trioVtx)[0]

            self.vertexData = self.createVtxData()
            # check if selected vertices are on the edgeLoop
            edgeLoop = self.checkEdgeLoopWithSelectedVtx(orderedVtx)

            if edgeLoop:
                cmds.optionMenu("browJointMultiple", e=1, value="Every")
            else:
                raise RuntimeError("can not create an edgeLoop")

            cmds.textField(self.eyebrowVertsTextField, e=True, tx=str(orderedVtx))

        else:
            upLoVtxList = curve_utils.orderedVert_upLo(currentName, trioVtx)
            upVtx, loVtx = upLoVtxList

            if currentName == "eye":

                cmds.textField(self.upEyelidVertsTextField, e=True, tx=str(upVtx))
                cmds.textField(self.loEyelidVertsTextField, e=True, tx=str(loVtx))

            elif currentName == "lip":

                cmds.textField(self.upLipVertsTextField, e=True, tx=str(upVtx))
                cmds.textField(self.loLipVertsTextField, e=True, tx=str(loVtx))

    def storeManualSelection(self, *args):
        face_utils.trackSelOrder()
        # cmds.optionMenu('eye_lip_brow', query=True, value=True)
        currentName = self.optionMenu_refresh("eye_lip_brow")

        selectedVtx = cmds.ls(os=1, fl=1)
        vtxList = self.setManualSelection(selectedVtx, currentName)

        if currentName == "brow":
            cmds.textField(self.eyebrowVertsTextField, e=True, tx=str(vtxList))

            self.vertexData = self.createVtxData()

            self.vertexData['browVerts'] = vtxList
            # if cmds.attributeQuery("browJntList", node="browFactor", exists=1):
            #     jntLength = len(cmds.getAttr("browFactor.browJntList"))
            #     jntMult = (jntLength+1) / vtxLength
            #     multiple = ["Single", "Double", "Triple"]
            #     cmds.optionMenu('browJointMultiple', e=1, value=multiple[jntMult-1])

        else:
            pass

    def weightTransfer(self, *args):
        print('create UI')

    def setWeightedDeformer(self, *args):
        dformer = cmds.ls(sl=1)[0]
        cmds.textField('weightedDeformer', e=1, tx=str(dformer))
        '''
        weightedObjList = []
        if cmds.nodeType(dformer) == 'skinCluster':
            if ":" in dformer:
                deformer = dformer.split(':')[1]

            facePart = deformer.split('Map')[0]
            if facePart == 'brow':
                jntList = cmds.getAttr('browFactor.browJntList')

            elif facePart == 'lip':
                upJntList = cmds.getAttr('lipFactor.upLipJnt')
                loJntList = cmds.getAttr('lipFactor.loLipJnt')
                cornerJntList = cmds.getAttr('lipFactor.cornerLipJnt')
                jntList = [cornerJntList[0]] + upJntList + [cornerJntList[1]] + loJntList

            wgtJnts = cmds.skinCluster(dformer, q=1, wi=1)
            for jnt in jntList:
                childJnt = cmds.listRelatives(jnt, ad=1, type='joint')[0]
                weightedJnt = [jot for jot in wgtJnts if childJnt in jot][0]
                weightedObjList.append(weightedJnt)

        elif cmds.nodeType(dformer) == 'blendShape':

            weightedObjList = cmds.listAttr(dformer + '.w', multi=True)

        else:
            print("let's add other deformer")
            pass

        length = len(weightedObjList)
        targetText = str()
        for index in range(length):
            if index == length-1:
                targetText += weightedObjList[index]
            else:
                targetText += weightedObjList[index] + ','

        cmds.textField('weightedItems', e=1, tx=str(targetText))'''

    def get_blendshape_targets(self, blendshape_node):
        # Get the targets of the blendShape node
        targets = cmds.listAttr(blendshape_node + '.w', multi=True) or []

        return targets

    def weightSourceItems(self, *args):
        dform = cmds.textField('weightedDeformer', q=1, tx=1)
        self.show_weighted_items_window(dform)

    def show_weighted_items_window(self, dform):
        """
        1. It is ok to use a deformer from the other geometry (same topology)
        """

        # Create a window
        window_name = "weightSourceWindow"
        if cmds.window(window_name, exists=True):
            cmds.deleteUI(window_name, window=True)

        cmds.window(window_name, title="weight source", widthHeight=(300, 200))

        # Create a layout
        cmds.columnLayout(adjustableColumn=True)

        if cmds.nodeType(dform) == "blendShape":
            targets = self.get_blendshape_targets(dform)

            if targets:
                cmds.text(label=dform, font="boldLabelFont")

                target_list = cmds.textScrollList(
                    numberOfRows=len(targets),
                    allowMultiSelection=True,
                    append=targets
                )
            else:
                cmds.warning("No blendShape targets found for {}.".format(dform))

        if cmds.nodeType(dform) == "skinCluster":
            weightedObjList = []
            if ":" in dform:
                deformer = dform.split(':')[1]

            facePart = deformer.split('Map')[0]
            if facePart == 'brow':
                jntList = cmds.getAttr('browFactor.browJntList')

            elif facePart == 'lip':
                upJntList = cmds.getAttr('lipFactor.upLipJnt')
                loJntList = cmds.getAttr('lipFactor.loLipJnt')
                cornerJntList = cmds.getAttr('lipFactor.cornerLipJnt')
                jntList = [cornerJntList[0]] + upJntList + [cornerJntList[1]] + loJntList

            wgtJnts = cmds.skinCluster(dform, q=1, wi=1)
            for jnt in jntList:
                childJnt = cmds.listRelatives(jnt, ad=1, type='joint')[0]
                weightedJnt = [jot for jot in wgtJnts if childJnt in jot][0]
                weightedObjList.append(weightedJnt)

            if weightedObjList:
                cmds.text(label=dform, font="boldLabelFont")

                target_list = cmds.textScrollList(
                    numberOfRows=len(weightedObjList),
                    allowMultiSelection=True,
                    append=weightedObjList
                )

        # Create a button to get the selected targets
        cmds.button(label="Store Selected Targets", command=lambda x: self.store_selected_weightedItems(target_list))

        # Create a button to close the window
        cmds.button(label="Close", command=lambda x: cmds.deleteUI(window_name, window=True))

        # Show the window
        cmds.showWindow(window_name)

    def store_selected_weightedItems(self, target_list):
        # Get the selected targets from the textScrollList / return list[]
        selected_targets = cmds.textScrollList(target_list, query=True, selectItem=True) or []

        print("Selected Targets:", selected_targets)
        cmds.textField('weightedItems', e=1, tx=str(selected_targets))

    def faceCrv_onVtxList(self, *args):
        pass

    def matchGuides(self, *args):
        pass

    def evenLocCustomCrv(self, *args):
        pass
