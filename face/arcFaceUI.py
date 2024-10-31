from maya import cmds
import maya.mel as mel
# from conLibrary import app
# reload(app)
from imp import reload
#from conLibrary import controllerLibTest
#reload(controllerLibTest)

from functools import partial
from twitchScript.face import face_utils, rigStructure, faceFactor, faceSkin, curve_utils, blendShapeFunc, weight_transferUI
reload(face_utils)
reload(faceFactor)
reload(faceSkin)
reload(curve_utils)
reload(blendShapeFunc)
reload(weight_transferUI)

import os
from twitchScript.brow import browRig
reload(browRig)
from twitchScript.eyeLid import eyeMirrorRig
reload(eyeMirrorRig)
from twitchScript.jaw import jawConstraintRig, lipShapeRig
reload(jawConstraintRig)
reload(lipShapeRig)

#- load necessary plugin
# if not cmds.pluginInfo('matrixNodes.mll', loaded = True, q = True):
#     print "Loading Plug in, 'matrixNodes.mll'"
#     cmds.loadPlugin('matrixNodes.mll')
#
USERAPPDIR = cmds.internalVar(userAppDir=1)
DIRECTORY = os.path.join(USERAPPDIR, "arcMaFile")

def createDirectoryTest(directory=DIRECTORY):

    if not os.path.exists(DIRECTORY):
        os.mkdir(DIRECTORY)
    return DIRECTORY


class ArcFaceUI(face_utils.Util):

    def __init__(self, configFile=None):

        super(ArcFaceUI, self).__init__()
        #face_utils.Util.__init__(self)

        #self.util = face_utils.Util()
        self.browClass = None
        self.eyeLidClass = None
        self.jawRigClass = None
        self.skin = None
        self.ctlLib = None
        self.ctl = None
        self.configFile = configFile
        self.windowName = 'arcFaceUI'
        self.headInfo = {}
        self.vertexData = {}
        self.lipOrderVtx = {}
        self.textColor = [0.64, 0.42, 0.33]
        self.buttonColor = [0.8, 0.7, 0.6]
        self.directory = createDirectoryTest()
        self.targetsForCtls = {}
        self.BSClass = None

    def show(self):

        if cmds.window(self.windowName, query=True, exists=True):
            cmds.deleteUI(self.windowName)

        cmds.window(self.windowName, menuBar=True, widthHeight=(400, 1000), bgc = [0.25, 0.3, 0.3])
        # - constructing Menu Items
        cmds.menu(label='File')
        cmds.menuItem(label='Open Info.json', c=partial(self.openInfoFile))
        cmds.menuItem(label='Save Info.json', c=partial(self.saveInfoFile))

        cmds.menu(label='Tools')
        cmds.menuItem(label='NG Skin Tool', c=partial(self.openNgSkinTool))
        cmds.menuItem(label='Copy Layer Tool', c=partial(self.openCopyLayersTool))
        # cmds.menuItem(label='---------------')
        # cmds.menuItem(label='Create Panel Camera', c=partial(self.createPanelCam))
        # cmds.menuItem(label='Create Curve Camera', c=partial(self.createCurveCam))
        # cmds.menuItem(label='---------------')
        # cmds.menuItem(label='Set Range Tool', c=partial(self.importRangeTool))

        cmds.menu(label='Help')
        cmds.menuItem(label='Ask sshin')

        form = cmds.formLayout()

        self.buildUI(form)

        cmds.select(cl=1)

        cmds.showWindow()

    def buildUI(self, form):

        tabs = cmds.tabLayout( innerMarginWidth=5, innerMarginHeight=5)
        cmds.formLayout(form, edit=True,
                        attachForm=((tabs, 'top', 0), (tabs, 'left', 0), (tabs, 'bottom', 0), (tabs, 'right', 0)))

        runAllTab = cmds.columnLayout()
        # rowColumnLayout
        cmds.rowColumnLayout(numberOfColumns=5, bgc=[0.25, 0.3, 0.3],
                             columnWidth=[(1, 20), (2, 120), (3, 120), (4, 120), (5, 20)],
                             columnOffset=[(1, 'right', 5)])
        self.spaceBetween(1, 5, "text")

        cmds.text(label='')
        cmds.text(label='Foundation', bgc=[.12, .2, .30], fn="boldLabelFont", height=20)
        self.spaceBetween(1, 8, "text")

        cmds.text(label='')
        cmds.button(label='Build', bgc=self.buttonColor, command=self.buildFoundation)
        self.spaceBetween(1, 8, "text")

        cmds.text(label='')
        cmds.button(label='Import Locator', bgc=self.buttonColor, command=self.importLocators)
        cmds.button(label='Create Hierarchy', bgc=self.buttonColor, command=self.createHierarchy)
        cmds.button(label='Import ControlPanel', bgc=self.buttonColor, command=self.importControlPanel)
        self.spaceBetween(1, 11, "text")
        cmds.setParent('..')

        cmds.rowColumnLayout(numberOfColumns=4, bgc=[0.25, 0.3, 0.3],
                             columnWidth=[(1, 20), (2, 120), (3, 240), (4, 20)],
                             columnOffset=[(1, 'right', 5)])

        cmds.text(label='')
        cmds.text(label='Store Head Info', bgc=[.12, .2, .30], fn="boldLabelFont", height=20)
        self.spaceBetween(1, 6, "text")

        self.getHeadInfoGuideData()

        cmds.text(label='')
        cmds.button(label='Head Geo', bgc=self.buttonColor, command=self.storeHeadGeo)
        if self.headInfo:
            insertText = str(self.headInfo['headGeo'])
        else:
            insertText = ''
        self.headGeoTextField = cmds.textField('headGeoTextField', ed=False, tx=insertText, w=240)
        #cmds.button(label='        <<        ', bgc=self.buttonColor, c=self.updateHeadGeoTextField)
        cmds.text(label='')

        cmds.text(label='')
        cmds.button(label='Store FaceLocator', bgc=self.buttonColor, command=self.setupLocator)

        if self.guideData:
            insertText = str(self.guideData.keys())
        else:
            insertText = ''
        self.setupLocTextField = cmds.textField('setupLocTextField', ed=False, tx=insertText, w = 240)
        cmds.text(label='')
        cmds.setParent('..')

        cmds.rowColumnLayout(numberOfColumns=5, bgc=[0.25, 0.3, 0.3],
                             columnWidth=[(1, 20), (2, 120), (3, 120), (4, 120), (5, 20)],
                             columnOffset=[(1, 'right', 5)])

        self.spaceBetween(1, 5, "text")
        cmds.text(label='')
        cmds.text(label="Select 'face part'")
        cmds.text(label=" Store In Order ")
        cmds.text(label="Select Left In Order")
        cmds.text(label='')

        cmds.text(label='')
        cmds.optionMenu('eye_lip_brow', bgc=[0, 0, 0], changeCommand=self.printNewMenuItem)
        cmds.menuItem(label='brow')
        cmds.menuItem(label='eye')
        cmds.menuItem(label='lip')
        cmds.button(label='Ordered Vertices', bgc=self.buttonColor, command=self.setOrderedVert_upLo)
        cmds.button(label='Manual Selection', bgc=self.buttonColor, command=self.storeManualSelection)
        cmds.text(label='')

        # cmds.text(label='@ Locators position changed')
        # cmds.button(label='rebuildHierarchy ', bgc=[.42, .5, .60], command=self.rebuildHierarchy)
        # cmds.button(label='?', command=self.plugNewHead_helpImage)
        # cmds.button(label='plug NewHeadShape', bgc=[.42, .5, .60], command=self.plugNewHeadShape)
        # cmds.text(label=': store faceLocator first!!')
        # self.spaceBetween(1, 7, "text")
        cmds.setParent('..')

        cmds.rowColumnLayout(numberOfColumns=4, bgc=[0.25, 0.3, 0.3],
                             columnWidth=[(1, 20), (2, 120), (3, 240), (4, 20)],
                             columnOffset=[(1, 'right', 5)])

        self.spaceBetween(1, 4, "text")
        self.vertexData = self.createVtxData()
        cmds.text(label='')
        cmds.button(label='Brow Select', bgc =self.buttonColor, c=partial(self.selectVertices, 'eyebrowVertsTextField'))
        if self.vertexData.has_key('browVerts'):
            insertText = self.vertexData['browVerts']
        else:
            insertText = ''
        self.eyebrowVertsTextField = cmds.textField('eyebrowVertsTextField', ed=False, tx=str(insertText), w=240)
        self.spaceBetween(1, 2, "text")

        cmds.button(label='Up EyeLid Select', bgc=self.buttonColor, c=partial(self.selectVertices, 'upEyelidVertsTextField'))
        if self.vertexData.has_key('upLidVerts'):
            insertText = self.vertexData['upLidVerts']
        else:
            insertText = ''
        self.upEyelidVertsTextField = cmds.textField('upEyelidVertsTextField', ed = False, tx = str(insertText), w = 240)

        self.spaceBetween(1, 2, "text")

        cmds.button(label='Low EyeLid Select', bgc=self.buttonColor, c=partial(self.selectVertices, 'loEyelidVertsTextField'))
        if self.vertexData.has_key('loLidVerts'):
            insertText = self.vertexData['loLidVerts']
        else:
            insertText = ''
        self.loEyelidVertsTextField = cmds.textField('loEyelidVertsTextField', ed=False, tx=str(insertText), w = 240)

        self.spaceBetween(1, 2, "text")

        cmds.button(label='Up Lip Select', bgc=self.buttonColor, c=partial(self.selectVertices, 'upLipVertsTextField'))
        if self.vertexData.has_key('upLipVerts'):
            insertText = self.vertexData['upLipVerts']
        else:
            insertText = ''
        self.upLipVertsTextField = cmds.textField('upLipVertsTextField', ed=False, tx=str(insertText), w=240)

        self.spaceBetween(1, 2, "text")

        cmds.button(label='Low Lip Select', bgc=self.buttonColor, c=partial(self.selectVertices, 'loLipVertsTextField'))
        if self.vertexData.has_key('loLipVerts'):
            insertText = self.vertexData['loLipVerts']
        else:
            insertText = ''
        self.loLipVertsTextField = cmds.textField('loLipVertsTextField', ed=False, tx=str(insertText), w=240)
        self.spaceBetween(1, 2, "text")

        cmds.button(label='Update Vtx Selection', bgc=self.buttonColor, command= self.updateVtxSelection)
        self.spaceBetween(1, 3, "text")

        cmds.setParent('..')

        # rowColumnLayout
        cmds.rowColumnLayout(numberOfColumns=5, bgc=[0.25, 0.3, 0.3],
                             columnWidth=[(1, 20), (2, 120), (3, 120), (4, 120), (5, 20)],
                             columnOffset=[(1, 'right', 5)])

        self.spaceBetween(1, 5, "text")

        cmds.text(label='')
        cmds.text(label='Controller', bgc=[.12, .2, .30], fn="boldLabelFont", height=20)
        self.spaceBetween(1, 8, "text")

        cmds.text(label='')
        cmds.button(label='Control Library', bgc=self.buttonColor, command= self.controllerLibrary)
        cmds.button(label='Store Controller', bgc=self.buttonColor, command=self.storeController)

        self.ctl = ''
        if cmds.objExists("helpPanel_grp"):
            if cmds.attributeQuery("controller", node="helpPanel_grp", exists=1):
                self.ctl = cmds.getAttr("helpPanel_grp.controller")

        self.controllerTextField = cmds.textField('SelectedController', ed=False, tx=str(self.ctl), w = 120)
        self.spaceBetween(1, 6, "text")

        cmds.text(label='')
        cmds.text(label='Brow Setup', bgc=[.12, .2, .30], fn="boldLabelFont", height=20)
        self.spaceBetween(1, 8, "text")

        cmds.text(label='')
        cmds.text(label='Total Number of Ctl')
        cmds.text(label='Number of Vtx')
        cmds.text(label='Extra Layer')
        self.spaceBetween(1, 2, "text")

        cmds.optionMenu('numOfBrowCtl', bgc=[0, 0, 0], changeCommand=self.printNewMenuItem)
        cmds.menuItem(label=7)
        cmds.menuItem(label=9)
        cmds.menuItem(label=11)
        cmds.menuItem(label=13)
        cmds.optionMenu('browJointMultiple', bgc=[0, 0, 0], changeCommand=self.printNewMenuItem)
        cmds.menuItem(label='Single')
        cmds.menuItem(label='Double')
        cmds.menuItem(label='Every')
        cmds.optionMenu('extraBrowUpLoChain', bgc=[0, 0, 0], changeCommand=self.printNewMenuItem)
        cmds.menuItem(label='Lower')
        cmds.menuItem(label='Upper')

        if self.vertexData:
            #edgeLoop = self.util.checkEdgeLoopWithSelectedVtx(self.vertexData['browVerts'])
            edgeLoop = self.checkEdgeLoopWithSelectedVtx(self.vertexData['browVerts'])
            if edgeLoop:
                cmds.optionMenu("browJointMultiple", e=1, value="Every")
            else:
                vtxLength = len(self.vertexData['browVerts'])
                if cmds.attributeQuery("browJntList", node="browFactor", exists=1):
                    jntLength = len(cmds.getAttr("browFactor.browJntList"))
                    jntMult = (jntLength+1) / vtxLength
                    if jntMult == 0:
                        cmds.optionMenu('browJointMultiple', e=1, value="Single")
                    else:
                        multiple = ["Single", "Double"]
                        cmds.optionMenu('browJointMultiple', e=1, value=multiple[jntMult-1])

            if cmds.attributeQuery("ctlList", node="browFactor", exists=1):
                browCtlLength = len(cmds.getAttr("browFactor.ctlList"))
                cmds.optionMenu('numOfBrowCtl', e=1, value=str(browCtlLength))

        self.spaceBetween(1, 2, "text")

        cmds.text(label='select ctl')
        cmds.text(label=' change number : Ctl/Multi')
        cmds.text(label=' lower layer is must')
        self.spaceBetween(1, 2, "text")

        cmds.button(label='Brow Rig', bgc=self.buttonColor, command=self.browRigBuild)
        cmds.button(label='Rebuild BrowRig', bgc=self.buttonColor, command=self.rebuildBrowRig)
        cmds.button(label='ExtraBrowWideJnt', bgc=self.buttonColor, command=self.browWideJnt)

        self.spaceBetween(3, 4, "text")

        cmds.text(label='Eyelid Setup', bgc=[.12, .2, .30], fn="boldLabelFont", height=20)
        self.spaceBetween(1, 9, "text")

        cmds.text(label='Up/Low number of ctl')
        cmds.text(label=' change number : Ctl/Multi')
        cmds.text(label='')
        self.spaceBetween(1, 2, "text")

        cmds.optionMenu('numOfEyeMidCtl', bgc=[0, 0, 0], changeCommand=self.printNewMenuItem)
        cmds.menuItem(label=5)
        cmds.menuItem(label=6)
        cmds.menuItem(label=7)
        cmds.optionMenu('eyeJointMultiple', bgc=[0, 0, 0], changeCommand=self.printNewMenuItem)
        cmds.menuItem(label='Every')
        cmds.menuItem(label='Half')

        self.spaceBetween(1, 3, "text")
        cmds.button(label='Eye Rig', bgc=self.buttonColor, command=self.eyeRigBuild)
        cmds.button(label='EyeCrvRig', bgc=self.buttonColor, command=self.eyeCrvRig)
        cmds.button(label='ExtraEyeWideLayer', bgc=self.buttonColor, command=self.eyeWideLayer)

        self.spaceBetween(1, 11, "text")

        cmds.text(label='')
        cmds.text(label='Jaw Setup', bgc=[.12, .2, .30], fn="boldLabelFont", height=20)
        self.spaceBetween(1, 4, "text")

        self.spaceBetween(1, 5, "text")

        cmds.text(label='Number of Ctl')
        cmds.text(label='Number of Jnt : vtx Multi')
        self.spaceBetween(1, 3, "text")

        cmds.optionMenu('numOfLipCtl', bgc=[0, 0, 0], changeCommand=self.printNewMenuItem)
        cmds.menuItem(label=5)
        cmds.menuItem(label=7)
        cmds.menuItem(label=9)

        cmds.optionMenu('jawJntNumber', bgc=[0, 0, 0], changeCommand=self.lipJntMultChange)
        cmds.menuItem(label='Every')
        cmds.menuItem(label='Half')
        cmds.text(label='reset the optionMenu')

        jawMultValue = cmds.optionMenu('jawJntNumber', q=True, value=True)
        if cmds.objExists("lipFactor"):
            for upLow in ["up", "lo"]:
                if cmds.attributeQuery(upLow + "LipVerts", node="lipFactor", exists=1):
                    orderedVerts = cmds.getAttr("lipFactor." + upLow + "LipVerts")

                if jawMultValue == "Every":
                    self.lipOrderVtx[upLow] = orderedVerts

                elif jawMultValue == "Half":
                    center = (len(orderedVerts)-1)/2
                    right = orderedVerts[:center][::2]
                    leftTemp = orderedVerts[center+1:][::-1][::2]
                    left = leftTemp[::-1]
                    self.lipOrderVtx[upLow] = right + [orderedVerts[center]] + left

        self.spaceBetween(1, 2, "text")
        cmds.button(label='Jaw Rig', bgc=self.buttonColor, command=self.jawConstRig)
        cmds.button(label='lipShape Rig', bgc=self.buttonColor, command=self.lipShapeRig)
        self.spaceBetween(1, 2, "text")

        cmds.setParent('..')
        cmds.setParent('..')

        skinTab = cmds.columnLayout()
        cmds.rowColumnLayout(numberOfColumns=5, bgc=[0.25, 0.3, 0.3],
                             columnWidth=[(1, 20), (2, 120), (3, 120), (4, 120), (5, 20)],
                             columnOffset=[(1, 'right', 5)])
        self.spaceBetween(1, 5, "text")

        cmds.text(label='')
        cmds.text(label='Face Cluster', bgc=[.12, .2, .30], fn="boldLabelFont", height=20)
        self.spaceBetween(1, 8, "text")

        cmds.text(label='')
        cmds.button(label='Import ClusterPanel', bgc=self.buttonColor, command=self.importClusterPanel)
        cmds.button(label='Face Clusters', bgc=self.buttonColor, command=self.faceClusters)
        cmds.button(label='Update FaceClusters', bgc=self.buttonColor, command=self.updateFaceCluster)
        self.spaceBetween(1, 7, "text")
        cmds.text(label='source cluster')
        cmds.text(label='create "browDn_cls_set"!!')
        cmds.text(label='(for skinWgt calculation)')
        self.spaceBetween(1, 1, "text")

        cmds.separator(h=15)
        cmds.optionMenu('clusterName', bgc=[0, 0, 0], highlightColor=[0.9, 0.5, 0.4], changeCommand=self.printNewMenuItem)
        cmds.menuItem(label='browUp_cls')
        cmds.menuItem(label='browDn_cls')
        cmds.menuItem(label='browTZ_cls')
        cmds.menuItem(label='eyeWide_cls')
        cmds.menuItem(label='eyeBlink_cls')
        cmds.menuItem(label='jawOpen_cls')
        cmds.menuItem(label='lip_cls')
        cmds.menuItem(label='jawFat_cls')
        cmds.menuItem(label='chin_cls')
        cmds.menuItem(label='lipRoll_cls')
        cmds.menuItem(label='bttmLipRoll_cls')
        cmds.menuItem(label='lipRoll_cls')
        cmds.menuItem(label='squintPuff_cls')
        cmds.menuItem(label='cheek_cls')
        cmds.menuItem(label='lowCheek_cls')
        cmds.menuItem(label='ear_cls')
        cmds.menuItem(label='nose_cls')

        self.spaceBetween(1, 4, "text")

        cmds.button(label='Create Vtx Set', bgc=self.buttonColor, command=self.createVtxSet)
        cmds.button(label='Select Set', bgc=self.buttonColor, command=self.selectSetVtx)
        cmds.button(label='Select WeightedVtx', bgc=self.buttonColor, command=self.selectWeightedVerts)
        self.spaceBetween(1, 2, "text")
        cmds.text(label='target cluster')
        self.spaceBetween(1, 3, "text")
        cmds.text(label='+ -')

        cmds.optionMenu('targetClusterName', bgc=[0, 0, 0], highlightColor=[0.9, 0.5, 0.4], changeCommand=self.printNewMenuItem)
        cmds.menuItem(label='browUp_cls')
        cmds.menuItem(label='browDn_cls')
        cmds.menuItem(label='browTZ_cls')
        cmds.menuItem(label='eyeWide_cls')
        cmds.menuItem(label='eyeBlink_cls')
        cmds.menuItem(label='jawOpen_cls')
        cmds.menuItem(label='lip_cls')
        cmds.menuItem(label='jawFat_cls')
        cmds.menuItem(label='chin_cls')
        cmds.menuItem(label='lipRoll_cls')
        cmds.menuItem(label='bttmLipRoll_cls')
        cmds.menuItem(label='lipRoll_cls')
        cmds.menuItem(label='squintPuff_cls')
        cmds.menuItem(label='cheek_cls')
        cmds.menuItem(label='lowCheek_cls')
        cmds.menuItem(label='ear_cls')
        cmds.menuItem(label='nose_cls')

        cmds.text(label='choose target cluster')
        cmds.text(label='select head geo')
        self.spaceBetween(1, 1, "text")

        cmds.checkBox('clsXDirection', label='')
        cmds.button(label='Copy Cls Weight', bgc=self.buttonColor, command=self.copyClusterWeight)
        cmds.button(label='indie Cls Mirror', bgc=self.buttonColor, command=self.indiClsMirrorWeight)
        cmds.button(label='AllCls Mirror', bgc=self.buttonColor, command=self.allClsMirrorWeight)

        self.spaceBetween(1, 2, "text")
        cmds.text(label='only weigheted clusters')
        cmds.text(label='')
        cmds.text(label='')
        self.spaceBetween(1, 2, "text")

        cmds.button(label='Export All Cls Weight', bgc=self.buttonColor, command=self.exportClsWeight)
        cmds.button(label='Import All Cls Weight', bgc=self.buttonColor, command=self.importClsWeight)
        cmds.button(label='Toggle Deformers', bgc=self.buttonColor, command=self.toggleDeformer)
        self.spaceBetween(1, 12, "text")

        cmds.text(label='Curve On Mesh', bgc=[.12, .2, .30], fn="boldLabelFont", height=20)
        self.spaceBetween(1, 8, "text")

        cmds.text(label='')
        cmds.text(label='face part            ')
        cmds.text(label='degree')
        cmds.text(label='nature')
        self.spaceBetween(1, 2, "text")

        cmds.optionMenu('facePartName', bgc=[0, 0, 0], highlightColor=[0.9, 0.5, 0.4], changeCommand=self.printNewMenuItem)
        cmds.menuItem(label="brow")
        cmds.menuItem(label="eye")
        cmds.menuItem(label="lip")

        cmds.optionMenu('degree', bgc=[0, 0, 0], changeCommand=self.printNewMenuItem)
        cmds.menuItem(label=1)
        cmds.menuItem(label=3)

        cmds.optionMenu('crvCharacterName', bgc=[0, 0, 0], changeCommand=self.printNewMenuItem)
        cmds.menuItem(label="_guide")
        cmds.menuItem(label="_map")
        cmds.menuItem(label="_BS")
        cmds.menuItem(label="_wire")
        cmds.menuItem(label="_temp")
        cmds.menuItem(label="_test")

        self.spaceBetween(1, 7, "text")
        cmds.text(label='multiple vtx in right corner')
        cmds.text(label='corner(s)/ direction vtx')
        cmds.text(label='left half verts in order')
        self.spaceBetween(1, 2, "text")

        cmds.button(label='All Loop Crv', bgc=self.buttonColor, command=self.seriesOfEdgeLoopCrv)
        cmds.button(label='Crv On EdgeLoop', bgc=self.buttonColor, command=self.curveOnEdgeLoop)
        cmds.button(label='Symmetry Crv(Manual)', bgc=self.buttonColor, command=self.manualCrv_halfVerts)
        self.spaceBetween(1, 1, "text")

        cmds.text(label='+ -')
        cmds.text(label='mirror tx direction')
        cmds.text(label='')
        cmds.text(label='select the wrap Mesh last')
        self.spaceBetween(1, 1, "text")

        cmds.checkBox('xDirection', label='')
        cmds.button(label='Symmetrize Crv', bgc=self.buttonColor, command=self.symmetrizeCrv)
        cmds.text(label='')
        cmds.button(label='Skin Wrap', bgc=self.buttonColor, command=self.create_shrink_wrap)
        self.spaceBetween(1, 7, "text")

        # cmds.text(label='BS Curve tool', bgc=[.12, .2, .30], fn="boldLabelFont", height=20)
        # self.spaceBetween(1, 9, "text")

        cmds.button(label='Copy CurveShape', bgc=self.buttonColor, command=self.copyCurveShape)

        cmds.button(label='Mirror CurveShape', bgc=self.buttonColor, command=self.mirrorCurveShape)

        cmds.button(label='Reset Curve', bgc=self.buttonColor, command=self.resetBS_targetCrv)
        self.spaceBetween(1, 12, "text")

        cmds.text(label='Map Skinning', bgc=[.12, .2, .30], fn="boldLabelFont", height=20)
        self.spaceBetween(1, 9, "text")

        cmds.optionMenu('facePart', bgc=[0, 0, 0], highlightColor=[0.9, 0.5, 0.4], changeCommand=self.printNewMenuItem)
        cmds.menuItem(label="brow")
        cmds.menuItem(label="eye")
        cmds.menuItem(label="lip")

        cmds.button(label='Loft MapSurface', bgc=self.buttonColor, command=self.loftMapSurface)
        cmds.button(label='SurfaceMap Skin', bgc=self.buttonColor, command=self.surfMapSkinning)
        self.spaceBetween(1, 7, "text")

        cmds.button(label='Calculate Skin', bgc=self.buttonColor, command=self.calculateSkinWgt)
        cmds.button(label='HeadSkin Object', bgc=self.buttonColor, command=self.headSkinObject)
        cmds.button(label='Reset ArFaceCtl', bgc=self.buttonColor, command=self.resetArFaceCtl)
        self.spaceBetween(1, 12, "text")


        cmds.setParent('..')
        cmds.setParent('..')

        ctl_lenShape = cmds.columnLayout()
        cmds.rowColumnLayout(numberOfColumns=5, bgc=[0.25, 0.3, 0.3],
                             columnWidth=[(1, 20), (2, 120), (3, 120), (4, 120), (5, 20)],
                             columnOffset=[(1, 'right', 5)])
        self.spaceBetween(1, 6, "text")

        cmds.text(label='BS Ctl setup', bgc=[.12, .2, .30], fn="boldLabelFont", height=20)
        self.spaceBetween(1, 9, "text")

        cmds.button(label='Plus Targets', bgc=self.buttonColor, c=partial(self.selectPlusTargets, 'plusTargets'))
        self.plusTextField = cmds.textField('plusTargets', ed=True, tx='', w=240)
        self.spaceBetween(1, 3, "text")

        cmds.button(label='Minus Targets', bgc=self.buttonColor, c=partial(self.selectMinusTargets, 'minusTargets'))
        self.minusTextField = cmds.textField('minusTargets', ed=True, tx='', w=240)
        self.spaceBetween(1, 3, "text")

        cmds.text(label='XYZ Axis ')
        cmds.text(label='Select Ctrls ')
        cmds.text(label=' ')
        self.spaceBetween(1, 2, "text")

        cmds.optionMenu('xyzAxis', bgc=[0, 0, 0], changeCommand=self.printNewMenuItem)
        cmds.menuItem(label="x")
        cmds.menuItem(label="y")
        cmds.menuItem(label="z")

        cmds.button(label='Basic Ctl BsConnect', bgc=self.buttonColor, c=self.basicCtl_connect)
        self.spaceBetween(1, 8, "text")

        cmds.text(label='Twitch BlendShape', bgc=[.12, .2, .30], fn="boldLabelFont", height=20)
        self.spaceBetween(1, 9, "text")

        cmds.text(label='   select base   ', fn="boldLabelFont", height=20)
        self.spaceBetween(1, 4, "text")
        cmds.button(label='split BS Weight', bgc=self.buttonColor, command=self.splitBSWeightMap)
        cmds.button(label='create twitchBS', bgc=self.buttonColor, command=self.createTwitchBS)
        cmds.button(label='weight transfer', bgc=self.buttonColor, command=self.weightTransfer)
        self.spaceBetween(1, 7, "text")

        cmds.text(label='Deformer on the Geo with')
        cmds.text(label='same vertex order as the')
        cmds.text(label='headGeo                          ')
        self.spaceBetween(1, 2, "text")

        cmds.button(label='Weight Source Dformer', bgc=self.buttonColor, c=self.setWeightedDeformer)
        self.weightedDeformer = cmds.textField('weightedDeformer', ed=True, tx='', w=240)
        self.spaceBetween(1, 3, "text")

        cmds.button(label='Weight Source Items', bgc=self.buttonColor, c=self.weightSourceItems)
        self.weightedItems = cmds.textField('weightedItems', ed=True, tx='', w=240)
        self.spaceBetween(1, 8, "text")

        cmds.text(label=' select target & baseGeo ')
        cmds.text(label=' mapSkinGeo & sculpted')
        cmds.text(label=' !!joint must have value')
        self.spaceBetween(1, 2, "text")
        cmds.button(label='Add Corrective & Reset', bgc=self.buttonColor, c=self.addCorrective_reset)
        cmds.button(label='bakeWgt To Corrective', bgc=self.buttonColor, c=self.bakeWeight_toCorrective)

        cmds.tabLayout(tabs,
                       edit=True,
                       tabLabel=((runAllTab, 'Run It All'),
                                 (skinTab, 'Skinning'),
                                 (ctl_lenShape, 'Ctl / BlendShape'))

                       )

        # (eyelidTab, 'eyelid'),
        # (eyebrowTab, 'eyebrow'),
        # (lipTab, 'lip'),
        # (skinningTab, 'skinning'),
        # (factorTab, 'Factors')

    def splitBSWeightMap(self, *args):

        blendShapeFunc.splitBSWeightMap()

    def createTwitchBS(self, *args):

        # if not self.BSClass:
        #     self.BSClass = blendShapeFunc.BlendShapeFunc()
        blendShapeFunc.createTwitchBS()

    def weightTransfer(self, *args):

        wgtTranUI = weight_transferUI.WeightTransferUI()
        wgtTranUI.show()

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
            deformer = dform.split(':')[1] if ':' in dform else dform

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

    def bakeWeight_toCorrective(self, *args):

        weightedDformer = cmds.textField('weightedDeformer', q=1, tx=1)
        weightedItems = cmds.textField('weightedItems', q=1, tx=1)
        if not weightedDformer or not weightedItems:

            raise RuntimeError('store targets first!!')

        print(weightedItems)
        sculptedGeo = cmds.ls(sl=1, type='transform')[0]
        if not self.BSClass:
            self.BSClass = blendShapeFunc.BlendShapeFunc()
        self.BSClass.bakeWeight_toCorrective(weightedDformer, weightedItems, sculptedGeo)

    def addCorrective_reset(self, *args):
        """
        select target first and headGeo (add target in blendShape)
        """
        mySel = cmds.ls(os=1, type='transform')
        target = mySel[0]
        baseGeo = mySel[1]
        if not self.BSClass:
            self.BSClass = blendShapeFunc.BlendShapeFunc()
        self.BSClass.addCorrectiveReset(target, baseGeo)

    def jntWeight_toCorrective(self, *args):

        mySel = cmds.ls(os=1, type='transform')
        mapSkinHead = mySel[0]
        sculptedGeo = mySel[1]

        if not self.BSClass:
            self.BSClass = blendShapeFunc.BlendShapeFunc()

        self.BSClass.jntWeight_toCorrective(mapSkinHead, sculptedGeo)

    def selectPlusTargets(self, txField, *args):

        plusTargets = cmds.ls(sl=1)

        # if not cmds.attributeQuery("plusTargets", node="helpPanel_grp", exists=1):
        #     cmds.addAttr('helpPanel_grp', ln='plusTargets', dt='stringArray')
        # cmds.setAttr('helpPanel_grp.plusTargets', type="stringArray", *plusTargets)
        length = len(plusTargets)
        targetText = str()
        for index in range(length):
            if index == length-1:
                targetText += plusTargets[index]
            else:
                targetText += plusTargets[index] + ','

        cmds.textField(txField, e=1, tx=str(targetText))

    def selectMinusTargets(self, txField, *args):

        minusTargets = cmds.ls(sl=1)
        length = len(minusTargets)
        tgtText = str()
        for index in range(length):
            if index == length-1:
                tgtText += minusTargets[index]
            else:
                tgtText += minusTargets[index] + ','

        cmds.textField(txField, e=1, tx=str(tgtText))

    def basicCtl_connect(self, *args):

        plusTarget = cmds.textField(self.plusTextField, q=1, tx=1)
        minusTarget = cmds.textField(self.minusTextField, q=1, tx=1)
        if not plusTarget and not minusTarget:

            raise RuntimeError('store targets first!!')

        if "," in plusTarget:
            plusList = plusTarget.split(',')
            minusList = minusTarget.split(',')

        else:
            plusList = [plusTarget]
            minusList = [minusTarget]

        if not plusList and not minusList:
            raise RuntimeError('store valid targets first!!')

        print(plusList, minusList)
        ctlSel = cmds.ls(sl=1, type='transform')
        xyz = cmds.optionMenu('xyzAxis', q=1, value=True)

        blendShapeFunc.simpleCtl_bsConnect(ctlSel, xyz, plusList, minusList, range='')

    def spaceBetween(self, numOfRow, numOfColm, space=""):

        for x in range(numOfRow ):
            for i in range(numOfColm):
                if space == "text":
                    cmds.text( l = '')

                elif space == "seperator":
                    cmds.separator(h=15)

    def printNewMenuItem(self, item):
        print(item)

    def createVtxData(self):

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

    def getHeadInfoGuideData(self):
        """
        get dictionary from helpPanel_grp for headInfo and guideData
        Returns:

        """
        if cmds.objExists("helpPanel_grp"):

            if cmds.attributeQuery("headGeo", node="helpPanel_grp", exists=1):
                self.headInfo["headGeo"] = cmds.getAttr("helpPanel_grp.headGeo")

            if cmds.attributeQuery("headBBox", node="helpPanel_grp", exists=1):
                self.headInfo["headBBox"] = cmds.getAttr("helpPanel_grp.headBBox")

            if cmds.objExists("allPos"):

                currentGuides = cmds.listRelatives("allPos", ad=1, ni=1, type="transform")

                if cmds.attributeQuery("headSkelPos", node="helpPanel_grp", exists=1):

                    guideList = cmds.listAttr("helpPanel_grp", ud=1)

                    for guide in guideList:
                        if guide in currentGuides:
                            self.guideData[guide] = cmds.getAttr("helpPanel_grp.{}".format(guide))

    def storeHeadGeo(self, *args):
        """
        updating save TextField
        """
        head = self.headGeo()
        cmds.textField(self.headGeoTextField, e=True, tx=head)
        cmds.select(head)
        self.getBoundBox()
        dist = self.boundingBoxData[2]

        self.headInfo["headBBox"] = dist

        if not cmds.attributeQuery("headBBox", node = "helpPanel_grp", exists=1):
            cmds.addAttr("helpPanel_grp", ln ="headBBox", dt='doubleArray')

        cmds.setAttr("helpPanel_grp.headBBox", dist, type="doubleArray")

    def setupLocator(self, *args):
        """
        create guideData(new or updated) by createGuideDict
        Args:
            *args:

        Returns: None

        """
        self.createGuidesDict()

        # store locator and pos in "helpPanel_grp"
        locData = self.storeLocator(self.guideData)
        cmds.textField(self.setupLocTextField, e=True, tx=str(locData))

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
        #cmds.optionMenu('eye_lip_brow', query=True, value=True)
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
        #cmds.optionMenu('eye_lip_brow', query=True, value=True)
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

    def rebuildHierarchy(self):
        pass

    def plugNewHead_helpImage(self):
        pass

    def plugNewHeadShape(self):
        pass

    def openInfoFile(self, *args):
        """
        manually load info.json

        filename = str(cmds.fileDialog2(fileMode=1, caption="Import Info.json")[0])
        self.locData = self.updateLocdata(filename)
        self.updateLocFields(self.locData)

        # - save session
        self.saveSession(self.locData)"""
        pass

    def saveInfoFile(self, *args):
        pass

    def openNgSkinTool(self, *args):
        pass

    def openCopyLayersTool(self, *args):
        pass

    def importLocators(self, *args):
        """
        Core.faceLocTopNode == "faceLoc_grp"
        Core.faceLocPath == os.path.join(baseMaFile, locFileName)
        importing the help panel
        """
        if cmds.objExists(self.faceLocTopNode):
            raise RuntimeError("Guide locator group already exists")

        fileList = os.listdir(self.directory)
        locFile = [x for x in fileList if x.startswith("locators")]
        if not locFile:
            raise RuntimeError("no locators exists in the directory")

        path = os.path.join(self.directory, locFile[-1])
        cmds.file(path,
                  i=True,
                  type='mayaAscii',
                  mergeNamespacesOnClash=False,
                  rpr='faceLoc',
                  options="v=0",
                  pr=True)

        self.placeLocators()
        return self.faceLocPath

    def placeLocators(self):
        """
        call after importLocator and createHierarchy
        place the locators by the value in json file
        """
        helpPanelGroup = "helpPanel_grp"
        if not cmds.objExists(helpPanelGroup):
            return "Create Hierarchy first!!"

        #current positions for locators
        if not self.guideData:
            self.createGuidesDict()
        locList = self.guideData.keys()

        guideList = cmds.listAttr(helpPanelGroup, ud=1)
        if guideList:
            if "allPos" in guideList:

                basePos = cmds.getAttr("{}.allPos".format(helpPanelGroup))
                cmds.xform("allPos", t=basePos, ws=1)
                guideList.remove("allPos")

                for guide in guideList:
                    if guide in locList:
                        if not cmds.listRelatives(guide, p=1)[0] == "allPos":

                            cmds.parent(guide, "allPos")

                        pos = cmds.getAttr("{}.{}".format(helpPanelGroup, guide))
                        cmds.xform(guide, t=pos, ws=1)

            # for loc in self.locData['setupLoc'].keys():
            #     if not loc == 'allPos':
            #         cmds.xform(loc, t=self.locData['setupLoc'][loc], ws=True)

    def createHierarchy(self, *args):
        """
        create basic container structure for face rig
        with FaceFactors
        """
        if cmds.objExists(self.faceMainNode):
            raise RuntimeError("{} already exists".format(self.faceMainNode))

        ch = rigStructure.RigStructure()
        ch.placeFaceRig()

        if cmds.objExists(self.faceFactors["main"]):
            raise RuntimeError("{} already exists".format(self.faceFactors["main"]))

        fFactor = faceFactor.FaceFactor(configFile=self.configFile)
        faceFactorNode = fFactor.create()

    def importControlPanel(self, *args):
        """
        importing the halp panel
        """
        if cmds.objExists("arFacePanel"):
            raise RuntimeError("arFacePanel already exists")

        fileList = os.listdir(self.directory)
        shapeFile = [x for x in fileList if x.startswith("arFacePanel")]
        if not shapeFile:
            raise RuntimeError("no arFacePanel exists in the directory")

        path = os.path.join(self.directory, shapeFile[-1])
        cmds.file(path, i=True, usingNamespaces=False)

    def buildFoundation(self, *args):
        """
        build all foundation together
        """
        #self.importFacialLoc()
        self.importLocators()
        self.createHierarchy()
        self.importControlPanel()

    def controllerLibrary(self, *args):
        pass
        aas = 'yNegXNeg'
        #self.ctlLib = controllerLibTest.ControllerLibraryUITest()
        #self.ctlLib.show()

    def storeController(self, *args):

        controller = cmds.ls(sl=1)
        if not controller:
            raise RuntimeError("select controller first!!")

        self.ctl = controller[0]

        if not cmds.attributeQuery("controller", node="helpPanel_grp", exists=1):
            cmds.addAttr("helpPanel_grp", ln="controller", dt="string")

        cmds.setAttr("helpPanel_grp.controller", self.ctl, type="string")
        cmds.textField(self.controllerTextField, e=True, tx=str(self.ctl))

    # store head info
    def headGeo(self):

        if not cmds.objExists("helpPanel_grp"):
            raise RuntimeError('import rigStructure first!!')

        head = cmds.ls(sl=1, type="transform")[0]
        if not head:
            raise RuntimeError("select head geometry")

        self.headInfo["headGeo"] = head

        if not cmds.attributeQuery("headGeo", node="helpPanel_grp", exists=1):
            cmds.addAttr("helpPanel_grp", ln="headGeo", dt="string")
        cmds.setAttr("helpPanel_grp.headGeo", head, type="string")

        return head

    # after place all the face locators
    def storeLocator(self, guideData):

        if not cmds.objExists("helpPanel_grp"):
            raise RuntimeError('import rigStructure first!!')

        if not cmds.objExists("faceLoc_grp"):
            raise RuntimeError('import faceLoc_grp first!!')

        helpPanelGroup = "helpPanel_grp"
        locData = []
        for loc, pos in guideData.items():

            if "Mirr" not in loc:
                if not cmds.attributeQuery(loc, node=helpPanelGroup, exists=1):
                    cmds.addAttr(helpPanelGroup, sn=loc, dt='doubleArray')
                # store locator world space
                cmds.setAttr(helpPanelGroup + "." + loc, pos, type="doubleArray")
                locData.append(loc)

        return locData

    def browRigBuild(self, *pArgs):

        jntMultiple = self.optionMenu_refresh("browJointMultiple")
        print(jntMultiple)
        self.browClass = browRig.BrowRig()
        numberOfCtl = self.optionMenu_refresh("numOfBrowCtl")

        myCtl = ""
        if cmds.attributeQuery("controller", node="helpPanel_grp", exists=1):
            controller = cmds.getAttr("helpPanel_grp.controller")
            if cmds.objExists(controller):
                myCtl = cmds.duplicate(controller, n="{}_temp", rc=1)

        multiple = {"Single": 1, "Double": 2, "Triple": 3, "Every": 0}
        self.browClass.build(int(numberOfCtl), multiple[jntMultiple], myCtl)

    def browWideJnt(self, *pArgs):
        numOfCtl = self.optionMenu_refresh("numOfBrowCtl")
        UpLoOption = self.optionMenu_refresh("extraBrowUpLoChain")
        if UpLoOption == "Lower":
            uplo = "lo"
        elif UpLoOption == "Upper":
            uplo = "up"

        if not self.browClass:
            self.browClass = browRig.BrowRig()

        print(uplo)
        self.browClass.browWideJnt(uplo, int(numOfCtl))

    def rebuildBrowRig(self, *pArgs):
        numOfCtl = self.optionMenu_refresh("numOfBrowCtl")
        jntMultiple = self.optionMenu_refresh("browJointMultiple")

        myCtl = ""
        if cmds.attributeQuery("controller", node="helpPanel_grp", exists=1):
            controller = cmds.getAttr("helpPanel_grp.controller")
            if cmds.objExists(controller):
                myCtl = controller

        if not self.browClass:
            self.browClass = browRig.BrowRig()

        multiple = {"Single": 1, "Double": 2, "Triple": 3, "Every": 0}
        self.browClass.rebuildBrowRig(int(numOfCtl), multiple[jntMultiple], myCtl)

    def eyeRigBuild(self, *pArgs):
        #cmds.optionMenu('numOfEyeMidCtl', query=True, value=True)
        numOfEyeCtls = self.optionMenu_refresh("numOfEyeMidCtl")
        self.eyeLidClass = eyeMirrorRig.EyeRig()
        self.eyeLidClass.eyeRigBuild(int(numOfEyeCtls))

    def eyeCrvRig(self, *pArgs):
        pass

    def eyeWideLayer(self, *pArgs):

        if not self.eyeLidClass:
            self.eyeLidClass = eyeMirrorRig.EyeRig()
        self.eyeLidClass.eyeWideLayerBuild()

    def lipJntMultChange(self, *pArgs):

        for upLow in ["up", "lo"]:
            if not cmds.attributeQuery(upLow + "LipVerts", node="lipFactor", exists=1):
                raise RuntimeError("store lip Vertices first!!")

            jawMultValue = cmds.optionMenu("jawJntNumber", query=True, value=True)
            orderedVerts = cmds.getAttr("lipFactor." + upLow + "LipVerts")

            if jawMultValue == "Every":
                self.lipOrderVtx[upLow] = orderedVerts

            elif jawMultValue == "Half":
                center = (len(orderedVerts)-1)/2
                right = orderedVerts[:center][::2]
                leftTemp = orderedVerts[center+1:][::-1][::2]
                left = leftTemp[::-1]
                self.lipOrderVtx[upLow] = right + [orderedVerts[center]] + left

    def jawConstRig(self, *pArgs):

        if not cmds.objExists("arFacePanel"):
            raise RuntimeError("import ControlPanel first!!")

        self.lipJntMultChange()
        self.jawRigClass = jawConstraintRig.JawConstraintRig(self.lipOrderVtx)
        self.jawRigClass.build()

    def lipShapeRig(self, *pArgs):
        #cmds.optionMenu('numOfLipCtl', query=True, value=True)
        numOfLipCtl = self.optionMenu_refresh("numOfLipCtl")
        lipShpRig = lipShapeRig.LipShapeRig(int(numOfLipCtl), self.lipOrderVtx)

        lipShpRig.lipShapeBuild()

    def importClusterPanel(self, *pArgs):
        """
        importing the help panel
        """
        if cmds.objExists("faceClusterPanel"):
            raise RuntimeError("faceClusterPanel already exists")

        fileList = os.listdir(self.directory)
        shapeFile = [x for x in fileList if x.startswith("faceClusterPanel")]
        if not shapeFile:
            raise RuntimeError("no faceClusterPanel exists in the directory")

        path = os.path.join(self.directory, shapeFile[-1])
        cmds.file(path, i=True, usingNamespaces=False)

    def faceClusters(self, *pArgs):

        if not self.guideData:
            self.createGuidesDict()

        self.skin = faceSkin.FaceSkin(self.guideData)
        self.skin.faceClusters()

    def updateFaceCluster(self, *pArgs):
        pass

    def createVtxSet(self, *pArgs):
        #cmds.optionMenu('clusterName', query=True, value=True)
        selectedCluster = self.optionMenu_refresh("clusterName")
        # select browCrv / headGeo in order
        faceSkin.createVtxSet(selectedCluster)

        # lipRollDict = {"lipRoll_cls": "lo", "bttmLipRoll_cls": "up"}
        # if selectedCluster in lipRollDict.keys():
        #     lipRollSet = cmds.getAttr("helpPanel_grp.{}_set".format(selectedCluster))
        #     lipVerts = cmds.ls(cmds.getAttr("lipFactor.{}LipVerts".format(lipRollDict[selectedCluster])), fl=1)
        #     length = len(lipVerts)
        #     num = (length - 1) / 2
        #     cmds.select(lipVerts[num])
        #     for n in range(num - 1):
        #         mel.eval("PolySelectTraverse 1")
        #     removeVtx = cmds.ls(sl=1, fl=1)
        #     lipRollVtx = [x for x in vtxSel if x not in removeVtx]
        #     selectVtxSet = face_utils.createVertexSet(selectedCluster, lipRollVtx)
        #     cmds.sets(lipRollVtx, rm=lipRollSet)

    def selectSetVtx(self, *pArgs):
        #cmds.optionMenu('clusterName', query=True, value=True)
        selectedCluster = self.optionMenu_refresh("clusterName")
        clsSet = cmds.getAttr("helpPanel_grp.{}_set".format(selectedCluster))
        cmds.select(clsSet)

    def selectWeightedVerts(self, *pArgs):
        #cmds.optionMenu('clusterName', query=True, value=True)
        selectedCluster = self.optionMenu_refresh("clusterName")

        obj = cmds.getAttr("helpPanel_grp.headGeo")

        cmds.select(cl=1)

        vtxList = face_utils.weightedVerts(obj, selectedCluster)
        cmds.select(vtxList)

    def copyClusterWeight(self, *pArgs):
        #cmds.optionMenu('clusterName', query=True, value=True)
        scCls = self.optionMenu_refresh("clusterName")
        #cmds.optionMenu('targetClusterName', query=True, value=True)
        ddCls = self.optionMenu_refresh("targetClusterName")

        if not self.guideData:
            self.createGuidesDict()

        if not self.skin:
            self.skin = faceSkin.FaceSkin(self.guideData)

        self.skin.copyClusterWgt(scCls, ddCls)

    def indiClsMirrorWeight(self, *pArgs):
        #cmds.optionMenu('targetClusterName', query=True, value=True)
        checkCls = cmds.checkBox('clsXDirection', query=True, value=True)
        targetCls = self.optionMenu_refresh("targetClusterName")
        faceSkin.faceClsMirrorWgt(targetCls, "indi", direction=checkCls)

    def allClsMirrorWeight(self, *pArgs):
        #cmds.optionMenu('targetClusterName', query=True, value=True)
        targetCls = self.optionMenu_refresh("targetClusterName")
        faceSkin.faceClsMirrorWgt(targetCls, "all")

    def exportClsWeight(self, *pArgs):

        mesh = cmds.ls(sl=1, typ="transform")
        if not mesh:
            raise RuntimeError("select mesh with cluster")

        faceSkin.exportClsWgt(mesh[0])

    def importClsWeight(self, *pArgs):

        mesh = cmds.ls(sl=1, typ="transform")
        if not mesh:
            raise RuntimeError("select mesh with cluster")

        faceSkin.importClsWgt(mesh[0])

    def toggleDeformer(self, *pArgs):

        geoName = cmds.ls(sl=1, type="transform")
        if not geoName:
            raise RuntimeError("select Geo with deformer")

        faceSkin.toggleDeformer(geoName)

    def create_shrink_wrap(self, *pArgs):

        mySel = cmds.ls(os=1)
        target = mySel[0]
        meshWraper = mySel[1]
        face_utils.create_shrink_wrap(target, meshWraper)

    def seriesOfEdgeLoopCrv(self, *pArgs):

        #cmds.optionMenu('facePartName', query=True, value=True)
        name = self.optionMenu_refresh("facePartName")
        #cmds.optionMenu('jointMultiple', query=True, value=True)
        numOfVtx = self.optionMenu_refresh("browJointMultiple")
        #cmds.optionMenu('crvCharacterName', query=True, value=True)
        nature = self.optionMenu_refresh("crvCharacterName")
        selection = cmds.ls(os=1, fl=1)

        if name == "brow":
            print(selection)
            curve_utils.browMapCurve(selection, numOfVtx, nature)

        else:

            curve_utils.seriesOfEdgeLoopCrv(name, nature, selection)

    def curveOnEdgeLoop(self, *pArgs):
        #cmds.optionMenu('facePartName', query=True, value=True)
        name = self.optionMenu_refresh("facePartName")
        #cmds.optionMenu('degree', query=True, value=True)
        degree = self.optionMenu_refresh("degree")
        #cmds.optionMenu('crvCharacterName', query=True, value=True)
        nature = self.optionMenu_refresh("crvCharacterName")
        selection = cmds.ls(os=1, fl=1)
        loopCrv = curve_utils.curveOnEdgeLoop(name, nature, selection, degree)

        print(loopCrv)

    def manualCrv_halfVerts(self, *pArgs):
        openClose = "open"
        #cmds.optionMenu('degree', query=True, value=True)
        degree = self.optionMenu_refresh("degree")
        #cmds.optionMenu('facePartName', query=True, value=True)
        name = self.optionMenu_refresh("facePartName")
        #cmds.optionMenu('crvCharacterName', query=True, value=True)
        suffix = self.optionMenu_refresh("crvCharacterName")

        myVert = cmds.ls(os=1, fl=1)
        curve_utils.curve_halfVerts(myVert, name, openClose, degree, suffix)

    def symmetrizeCrv(self, *pArgs):

        check = cmds.checkBox('xDirection', query=True, value=True)
        crvSel = cmds.ls(sl=1, type="transform")
        if not crvSel:
            raise RuntimeError("select a curve!!")

        crvShape = cmds.listRelatives(crvSel[0], c=1)[0]
        form = cmds.getAttr("{}.form".format(crvShape))
        if form == 0:

            curve_utils.symmetrizeOpenCrv(crvSel[0], direction=check)

        else:

            curve_utils.symmetrizeCloseCrv(crvSel[0], direction=check)

    def resetBS_targetCrv(self, *pArgs):

        selCrv = cmds.ls(sl=1, type='transform')
        curve_utils.resetBStargetCrv(selCrv)

    def copyCurveShape(self, *pArgs):

        selCrv = cmds.ls(os=1, long=1, type="transform")
        curve_utils.copyCurveShape(selCrv)

    def mirrorCurveShape(self, *pArgs):

        selCrv = cmds.ls(os=1, long=1, type="transform")
        curve_utils.mirrorCurveShape(selCrv)

    def loftMapSurface(self, *pArgs):

        # cmds.optionMenu('facePart', query=True, value=True)
        facePart = self.optionMenu_refresh("facePart")

        if facePart == "eye":
            factor = "lid"

        else:
            factor = facePart

        print(facePart)
        crvList = cmds.ls(os=1, type="transform")
        faceSkin.loftFacePart(factor, facePart, crvList)

    def optionMenu_refresh(self, menuTitle, *args):
        currentVal = cmds.optionMenu(menuTitle, query=True, value=True)
        return currentVal

    def surfMapSkinning(self, *pArgs):

        if not self.guideData:
            self.createGuidesDict()

        if not self.skin:
            self.skin = faceSkin.FaceSkin(self.guideData)

        if not self.skin.skinJnts:
            self.skin.headInfluences()

        geo = cmds.getAttr("helpPanel_grp.headGeo")
        if not cmds.objExists(geo):
            raise RuntimeError("check the headGeo name")

        #cmds.optionMenu('facePart', query=True, value=True)
        facePart = self.optionMenu_refresh("facePart")
        print("current facePart is {}".format(facePart))

        if facePart == "brow":
            factor = "brow"
            orderJnt = self.skin.browJnt

        elif facePart == "eye":
            factor = "lid"
            orderJnt = self.skin.eyeLidJnt

        elif facePart == "lip":
            factor = "lip"
            orderJnt = self.skin.lipJnt

        #surfMap, surfSkin = self.skin.surfMapSkinning(factor, facePart, orderJnt)

        #arFaceHeadSkin(geo) / copySkinWeight(geo, mapHead, surfMap)
        self.skin.skinBuild(geo, factor, facePart, orderJnt)

    def calculateSkinWgt(self, *pArgs):

        if not self.guideData:
            self.createGuidesDict()

        self.skin = faceSkin.FaceSkin(self.guideData)

        self.skin.calculateBuild()

    def updateSurfMap(self):
        pass

    def headSkinObject(self, *pArgs):

        if not self.skin:

            self.skin = faceSkin.FaceSkin(self.guideData)

        selObject = cmds.ls(sl=1, type="transform")[0]
        self.skin.headSkinObj(selObject)

    def resetArFaceCtl(self, *pArgs):

        face_utils.resetArFaceCtl()
