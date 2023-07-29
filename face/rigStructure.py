import maya.cmds as cmds

from arFace.Misc import Core

class RigStructure(Core.Core):
    def __init__(self, **kw):
        """
        initializing variables
        """
        super(RigStructure, self).__init__()
        #Core.Core.__init__(self, **kw)

    def placeFaceRig(self):
        """
        run to create default structure containers
        """
        if not cmds.objExists("faceLoc_grp"):
            raise RuntimeError("Import the Locator first!!")

        headSkelPos     = cmds.xform('headSkelPos', t = True, q = True, ws = True)
        jawRigPos       = cmds.xform('jawRigPos', t = True, q = True, ws = True)
        lEyePos         = cmds.xform('lEyePos', t = True, q = True, ws = True)

        faceMain        = cmds.group(em =1, n = self.faceMainNode)
        clsGroup        = cmds.group(em =1, n = 'cls' + self.grpSuffix, p = faceMain)
        crvGroup        = cmds.group(em =1, n = 'crv' + self.grpSuffix, p = faceMain)
        jntGroup        = cmds.group(em =1, n = 'jnt' + self.grpSuffix, p = faceMain)
        ctlGroup        = cmds.group(em =1, n = 'ctl' + self.grpSuffix, p = faceMain)
        helpPanelGroup  = cmds.group(em =1, n = 'helpPanel' + self.grpSuffix, p = faceMain )
        faceGeoGroup    = cmds.group(em =1, n = 'faceGeo' + self.grpSuffix, p = faceMain )
        dumpBinGrp = cmds.group(em=1, n='dumpBin' + self.grpSuffix, p=faceMain)
        spn             = cmds.group(em=1, n='spn', p = faceMain)
        headSkel        = cmds.group(em=1, n='headSkel', p = spn)
        headSkelJnt = cmds.joint(n='headSkel' + self.jntSuffix)
        cmds.xform(headSkel, ws=1, t=headSkelPos)
        
        if cmds.objExists("allPos"):

            currentGuides = cmds.listRelatives("allPos", ad=1, type="transform")

            for loc in currentGuides:
                pos = cmds.xform(loc, t=True, q=True, ws=True)
                if not cmds.attributeQuery(loc, node=helpPanelGroup, exists=1):
                    cmds.addAttr(helpPanelGroup, sn=loc, dt='doubleArray')
                #store locator world space 
                cmds.setAttr("{}.{}".format(helpPanelGroup, loc), pos, type="doubleArray")
        else: 
            cmds.confirmDialog( title='Confirm', message='create faceLoc_grp first!!')
    
        #-jawRig hierarchy
        jawRig     = cmds.group(em=1, n='jawRig', p=headSkel)
        cmds.xform(jawRig, ws=1, t=jawRigPos)
        jaw        = cmds.group(em=1, n='jaw', p=jawRig)
        jawSemiAdd = cmds.group(n='jawSemiAdd', em=True, parent=jaw)
        jawSemi    = cmds.group(n='jawSemi', em=True, parent=jaw)
        cmds.setAttr(jawSemi + ".translate", 0, 0, 0)
        jawClose   = cmds.joint(n='jawClose' + self.jntSuffix, relative = True, p=[0, 0, 0])
        jotStable  = cmds.group(n='lipJotStable', em=True, parent=jaw)
        lipJotP    = cmds.group(n='lipJotP', em=True, parent=jotStable)
    
        #-eyeRig hierarchy
        eyeRig           = cmds.group(em=1, n='eyeRig', p=headSkel)
        cmds.xform(eyeRig, ws=1, t=(0, lEyePos[1], lEyePos[2]))
        eyeRigP          = cmds.group(em=1, n='eyeRigP', p=eyeRig)
        eyeTR            = cmds.group(em=1, n='eyeTR', p=eyeRigP)
        ffdSquachLattice = cmds.group(em=1, n='ffdSquachLattice', p=eyeRigP)
        browRig          = cmds.group(em=1, n='browRig', p=headSkel)
        bodyHeadP        = cmds.group(em=1, n='bodyHeadTRSP', p=headSkel)
        cmds.xform(bodyHeadP, ws=1, t=headSkelPos)
        bodyHead         = cmds.group(em=1, n='bodyHeadTRS', p=bodyHeadP)
        cmds.xform(bodyHead, ws=1, t=headSkelPos)
        attachCtlGrp     = cmds.group(em=1, n='attachCtl' + self.grpSuffix, p=bodyHead)
        cmds.xform(attachCtlGrp, ws=1, t=headSkelPos)
        
        #- support rig
        supportRig = cmds.group(em=1, n='supportRig', p=headSkel)

        '''lEarP = cmds.group(em =1, n = self.prefix[0] + 'ear' + self.grpSuffix, p = supportRig)
        cmds.xform(lEarP, ws = 1, t = lEarPos)
        rEarP = cmds.group(em =1, n = self.prefix[1] + 'ear' + self.grpSuffix, p = supportRig)
        cmds.xform(rEarP, ws = 1, t = (-lEarPos[0], lEarPos[1], lEarPos[2]))
        noseRig = cmds.group(em =1, n = 'nose' + self.grpSuffix, p = supportRig)
        cmds.xform(noseRig, ws = 1, t = nosePos)
        lCheekGrp = cmds.group(em =1, n = self.prefix[0] + 'cheek' + self.grpSuffix, p = supportRig)
        cmds.xform(lCheekGrp, ws = 1, t = cheekPos, ro = cheekRot)
        rCheekGrp = cmds.group(em =1, n = self.prefix[1] + 'cheek' + self.grpSuffix, p = supportRig)
        cmds.xform(rCheekGrp, ws = 1, t =(-cheekPos[0], cheekPos[1], cheekPos[2]), ro =(cheekRot[0],cheekRot[1],-cheekRot[2]))
        lSquintPuffGrp = cmds.group(em =1, n = self.prefix[0] + 'squintPuff' + self.grpSuffix, p = supportRig)
        cmds.xform(lSquintPuffGrp, ws = 1, t = squintPuffPos, ro = squintPuffRot)
        rSquintPuffGrp = cmds.group(em =1, n = self.prefix[1] + 'squintPuff' + self.grpSuffix, p = supportRig)
        cmds.xform(rSquintPuffGrp, ws = 1, t =(-squintPuffPos[0], squintPuffPos[1], squintPuffPos[2]), ro =(squintPuffRot[0],squintPuffRot[1],-squintPuffRot[2]))
        lLowCheek = cmds.group(em =1, n = self.prefix[0] + 'lowCheek' + self.grpSuffix, p = supportRig)
        cmds.xform(lLowCheek, ws = 1, t = lowCheekPos)
        rLowCheek = cmds.group(em =1, n = self.prefix[1] + 'lowCheek' + self.grpSuffix, p = supportRig)
        cmds.xform(rLowCheek, ws = 1, t =(-lowCheekPos[0], lowCheekPos[1], lowCheekPos[2]))'''


