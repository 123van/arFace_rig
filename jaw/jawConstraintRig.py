import maya.cmds as cmds
from twitchScript.face import face_utils
reload(face_utils)

#object constants
GROUP = "grp"
JOINT = "jnt"
GUIDE = "guide"
JAW = "jaw"
#side constants
LEFT = "l_"
RIGHT = "r_"
CENTER = "c_"


def setLipJntLabel(jnt):
    """
    #l_upJawY_04_jnt / l_JawY_corner_jnt
    Args:
        jnt: "up", "lo", "corner"

    Returns:

    """
    jName = jnt.split("_")
    if jnt.startswith("l_"):
        index = 1

    elif jnt.startswith("r_"):
        index = 2

    elif jnt.startswith("c_"):
        index = 0

    cmds.setAttr(jnt + '.side', index)
    cmds.setAttr(jnt + '.type', 18)
    cmds.setAttr(jnt + '.otherType', jName[1] + jName[2], type="string")


class JawConstraintRig(face_utils.Util):

    def __init__(self, orderedVtx):

        super(JawConstraintRig, self).__init__()
        #face_utils.Util.__init__(self)

        self.orderedVtx = orderedVtx
        self.jawMain_grp = "faceMain|spn|headSkel|jawRig"
        self.base_grp = None
        self.broad_grp= None
        self.jawCloseClamp = None
        self.lipPartOrder ={}
        self.guideCurves = []
        self.guide_pocs = []
        self.midJntDict = {}
        self.polyCrv = {}
        # self.boundingBoxData = self.getBoundBox()

    def createMinorJoints(self):
        """

        Returns:

        """
        if not cmds.objExists('lipJotStable'):
            raise RuntimeError("import rigStructure first!!")

        if not cmds.objExists('lipJotP'):
            cmds.group(n='lipJotP', em=True, p='lipJotStable')

        lipJntGrp = 'lipJotP'

        if not self.guideData:
            self.createGuidesDict()

        cmds.xform(lipJntGrp, ws=1, t= self.guideData["jawRigPos"])
        
        for upLow in ["up","lo"]:

            if upLow == "up":
                lipCntPos = self.guideData["lipNPos"]
            elif upLow == "lo":
                lipCntPos = self.guideData["lipSPos"]

            length = len(self.orderedVtx[upLow])

            lipEPos = self.guideData["lipEPos"]
            lipWPos = [-lipEPos[0], lipEPos[1], lipEPos[2]]
            tempCrv = cmds.curve(d=3, ep=[lipWPos, lipCntPos, lipEPos])

            guideCrv = cmds.rename(tempCrv, "{}_lip_guide_crv".format(upLow))
            guideCrvShape = cmds.listRelatives(guideCrv, c=True)[0]
            cmds.rebuildCurve(guideCrv, d=3, rebuildType=0, keepRange=0)
            
            if not cmds.objExists('guideCrv_grp'):
                cmds.group(n='guideCrv_grp', em=True, p='faceMain|crv_grp')

            cmds.parent(guideCrv, "guideCrv_grp")
            self.guideCurves.append(guideCrv)
            
            param = 1.0 / (length - 1)
            lipNameOrder = self.mirrorOrder_name(length)
            self.lipPartOrder[upLow] ={}
            for index, preList in lipNameOrder.items():
                if not index ==0 and not index ==(length - 1):

                    name = self.namingMethod(preList[0], upLow, "Jaw", preList[1], "poc")
                    guidePoc = self.createPocNode( name, guideCrvShape, param * index)
                    pocPos = cmds.getAttr(guidePoc + ".position")[0]
                    lipJot = self.createLipJoint( preList, upLow, "Jaw", pocPos, lipJntGrp)
                    self.guide_pocs.append(guidePoc)
                    self.lipPartOrder[upLow][index]=lipJot

            lipPartOrder = [self.lipPartOrder[upLow][x] for x in self.lipPartOrder[upLow].keys()]
            face_utils.addAttrStoreData("lipFactor", "{}LipJnt".format(upLow), "stringArray", lipPartOrder, "stringArray")

        corners =[lipNameOrder[0], lipNameOrder[length - 1]]
        self.lipPartOrder["corner"] =[]
        for idx, preList in enumerate(corners):
            name = self.namingMethod(preList[0], "", "Jaw", preList[1], "poc")
            guidePoc = self.createPocNode(name, guideCrvShape, idx)
            pocPos = cmds.getAttr(guidePoc + ".position")[0]
            lipCorner = self.createLipJoint( preList, "", "Jaw", pocPos, lipJntGrp)
            self.guide_pocs.append(guidePoc)
            self.lipPartOrder["corner"].append(lipCorner)

        lipCornerOrder = self.lipPartOrder["corner"]
        face_utils.addAttrStoreData("lipFactor", "cornerLipJnt", "stringArray", lipCornerOrder, "stringArray")

    def createLipJoint(self, preList, position, title, pocPos, parentGrp):
        prefix = preList[0]
        order = preList[1]

        lipJntP = cmds.group(n=self.namingMethod(prefix, position, title+"P", order), em=True, parent= parentGrp)
        lipJotX = cmds.group(n=self.namingMethod(prefix, position, title+"RX", order), em=True, parent=lipJntP)
        lipJotY = cmds.group(n=self.namingMethod(prefix, position, title+"RY", order), em=True, parent=lipJotX)
        cmds.xform(lipJotY, ws=1, t=self.guideData["lipYPos"])
        lipYJnt = cmds.joint(n=self.namingMethod(prefix, position, title+"Y", order, "jnt"), relative=True, p=[0, 0, 0])
        setLipJntLabel(lipYJnt)
        lipRollT = cmds.group(n=self.namingMethod(prefix, position, title+"RollT", order), em=True, parent=lipYJnt)
        cmds.xform(lipRollT, ws=True, t=pocPos)
        cmds.group(n=self.namingMethod(prefix, position, title+"RollP", order), em=True, p=lipRollT)
        cmds.joint(n=self.namingMethod(prefix, position, title+"Roll",  order, "jnt"), relative=True, p=[0, 0, 0])

        return lipJntP

    def jawRigHierarchy(self):

        self.base_grp = cmds.createNode('transform', n='JawBase{}'.format( self.grpSuffix), p= self.jawMain_grp)

        self.broad_grp = cmds.createNode('transform', n='Jaw_Broad{}'.format( self.grpSuffix), p= self.jawMain_grp)

        cmds.select(cl=1)


    def createGuides( self, number = 5 ):
        """

        Args:
            number:

        Returns:

        """
        jaw_guide_grp = cmds.createNode("transform", name ='{}_{}_{}'.format(CENTER, GUIDE, GROUP))
        locs_grp = cmds.createNode("transform", name ='{}_lip_{}_{}'.format(CENTER, GUIDE, GROUP), p = jaw_guide_grp)
        lip_locs_grp = cmds.createNode("transform", name ='{}_lipMinor_{}_{}'.format(CENTER, GUIDE, GROUP), p= locs_grp)

        #create locators
        for part in ["Upper","Lower"]:

            part_mult = 1 if part == 'Upper' else -1
            mid_data = ( 0, part_mult, 0 )

            mid_loc = cmds.spaceLocator(n='{}_{}{}_lip_{}'.format(CENTER, JAW, part, GUIDE))[0]
            cmds.parent(mid_loc, lip_locs_grp)

            for side in [LEFT, RIGHT]:
                for x in range(number):
                    multiplier = x+1 if side == LEFT else -(x+1)
                    loc_data = ( multiplier, part_mult, 0)
                    loc = cmds.spaceLocator(n ='{}_{}{}_lip_{:02d}_{}'.format(side, JAW, part, x + 1, GUIDE))[0]
                    cmds.parent(loc, lip_locs_grp)
                    cmds.setAttr('{}.t'.format(loc), *loc_data)

            cmds.setAttr('{}.t'.format(mid_loc), *mid_data)

        #create corners
        left_corner_loc = cmds.spaceLocator(n ='{}_{}Corner_lip_{}'.format(LEFT, JAW, GUIDE))[0]
        right_corner_loc = cmds.spaceLocator(n ='{}_{}Corner_lip_{}'.format(RIGHT, JAW, GUIDE))[0]

        cmds.parent(left_corner_loc, lip_locs_grp)
        cmds.parent(right_corner_loc, lip_locs_grp)

        cmds.setAttr('{}.t'.format(left_corner_loc), *(1 + number, 0, 0))
        cmds.setAttr('{}.t'.format(right_corner_loc), *(-(1 + number), 0, 0))

        cmds.select(cl=1)

        #create jaw base
        jaw_base_quide_grp = cmds.createNode('transform', name ='{}_{}_base_{}_{}'.format(CENTER, JAW, GUIDE, GROUP),
                                             parent= jaw_guide_grp)
        jaw_guide = cmds.spaceLocator(n='{}_{}_{}'.format(CENTER, JAW, GUIDE))[0]
        jaw_inverse_guide = cmds.spaceLocator(n='{}_{}_inverse_{}'.format(CENTER, JAW, GUIDE))[0]

        cmds.setAttr(jaw_guide + ".t", *(0, -1, -number))
        cmds.setAttr(jaw_inverse_guide + ".t", *(0, 1, -number))
        cmds.parent(jaw_guide, jaw_inverse_guide, jaw_base_quide_grp)
        '''
        for locShp in cmds.listRelatives(jaw_guide_grp, ad=1, typ = 'locator'):
            locTran = cmds.listRelatives( locShp, p=1)[0]
            cmds.setAttr(locTran + '.localScale', *(0.1, 0.1, 0.1))'''

        cmds.select(cl=1)

        def lip_joints(self):

            """

            Returns:

            """
            grp = 'minorJaw_{}'.format(self.grpSuffix)
            minorJnts = [jnt for jnt in cmds.listRelatives(grp, c=1) if cmds.objExists(jnt)]

            return minorJnts

        def jaw_bases(self):
            """

            Returns:

            """
            grp = '{}_{}_base_{}_{}'.format(CENTER, JAW, GUIDE, GROUP)
            guides = [loc for loc in cmds.listRelatives(grp, c=1) if cmds.objExists(grp)]

            return guides

    def createJawBase(self):

        jaw_jnt = cmds.joint(n ='{}Jaw{}'.format(self.cPrefix, self.jntSuffix))
        jaw_inverse_jnt = cmds.joint(n ='{}inverseJaw{}'.format(self.cPrefix, self.jntSuffix))

        #jaw_mat = cmds.xform(jaw_guides()[0], q=1, ws=1, m=1)
        #jaw_inverse_mat = cmds.xform(jaw_guides()[1], q=1, ws=1, m=1)

        cmds.xform(jaw_jnt, ws=1, t = self.guideData['jawRigPos'])
        cmds.xform(jaw_inverse_jnt, t= self.guideData['jawRigPos'], ws=1)

        cmds.parent(jaw_jnt, self.base_grp)
        cmds.parent(jaw_inverse_jnt, self.base_grp)
        cmds.setAttr( "{}.radius".format(jaw_jnt), 5)
        cmds.setAttr("{}.radius".format(jaw_inverse_jnt), 5)

        cmds.select(cl=1)

        #add offset
        face_utils.addOffset( jaw_jnt, suffix = '_OFF')
        face_utils.addOffset( jaw_inverse_jnt, suffix = '_OFF')

        face_utils.addOffset( jaw_jnt, suffix = '_AUTO')
        face_utils.addOffset( jaw_inverse_jnt, suffix = '_AUTO')


    def createBroadJoints(self):

        centerPoc = [x for x in self.guide_pocs if "c_" in x]
        cornerPoc = [x for x in self.guide_pocs if "corner" in x]

        if not cmds.objExists("lipBroadCtl_grp"):
            cmds.group(em=1, n = "lipBroadCtl_grp")

        dist = cmds.getAttr("helpPanel_grp.headBBox")
        self.midJntDict = {}
        midCtlDict = {}
        for poc in centerPoc:

            uplo = poc[2:4]
            pocPos = cmds.getAttr(poc + ".position")[0]

            self.createLipJoint(["c_","00"], uplo, "LipBroad", pocPos, self.broad_grp)
            self.midJntDict["c_{}".format(uplo)] = "c_{}LipBroadRX_00".format(uplo)
            #create mid ctrls
            orderedVerts = cmds.getAttr("lipFactor." + uplo + "LipVerts")
            self.polyCrv[uplo] = self.createPolyToCurve(orderedVerts, name="{}_lipCtlGuide".format(uplo))
            cmds.rebuildCurve(self.polyCrv[uplo], ch=1, rebuildType=0, spans=len(orderedVerts) - 1, keepRange=0, keepControlPoints=1, degree=1)
            cmds.parent(self.polyCrv[uplo], "guideCrv_grp")

            myCtl = self.genericController(self.midJntDict["c_{}".format(uplo)].replace("RX_00","_controller"), (0, 0, 0),
                                         dist[1] / 80.0, "circle", self.colorIndex["green"][0])

            name = self.midJntDict["c_{}".format(uplo)].replace("RX_00","_ctl")
            print(name)
            ctlChain = self.createMidController(name, dist[1] / 50.0, myCtl, param=0.5,
                                                guideCrv=self.polyCrv[uplo], colorID=self.colorIndex["green"][0])
            ctl, offset, null, poc = [ctlChain[0], ctlChain[1], ctlChain[2], ctlChain[3]]
            cmds.parent(null, "lipBroadCtl_grp")

            face_utils.polyCrvCtlSetup( name, ctl, offset, dist[1] / 60.0)

            #uplo ctl connections
            midJntAdd = cmds.shadingNode("addDoubleLinear", asUtility=True, n="{}MidJntAdd".format(uplo))
            uploJawBroad = self.midJntDict["c_{}".format(uplo)]
            uploCtlMult = cmds.shadingNode("multiplyDivide", asUtility=True, n="{}Ctl_mult".format(uplo))
            cmds.connectAttr( "{}.tx".format(ctl), "{}.input1X".format(uploCtlMult))
            cmds.connectAttr( "lipFactor.lipJotX_ry", "{}.input2X".format(uploCtlMult))
            cmds.connectAttr("{}.outputX".format(uploCtlMult), "{}.ry".format(uploJawBroad))
            cmds.connectAttr( "{}.ty".format(ctl), "{}.input1Y".format(uploCtlMult))
            cmds.connectAttr( "lipFactor.lipJotX_rx", "{}.input2Y".format(uploCtlMult))
            cmds.connectAttr("{}.outputY".format(uploCtlMult), "{}.input1".format(midJntAdd))
            cmds.connectAttr("{}.output".format(midJntAdd), "{}.rx".format(uploJawBroad))
            cmds.connectAttr("{}.rz".format(ctl),  "{}.rz".format(uploJawBroad))
            cmds.connectAttr("{}.tz".format(ctl), "{}.tz".format(uploJawBroad))
            cmds.delete(myCtl)

            midCtlDict["c_{}".format(uplo)] = ctl
            if not cmds.attributeQuery( "{}_lipCtlGuide".format(uplo), node = "lipFactor", exists=1):
                cmds.addAttr("lipFactor", ln="{}_lipCtlGuide".format(uplo), dt="string")

            cmds.setAttr("lipFactor.{}_lipCtlGuide".format(uplo), self.polyCrv[uplo], typ="string" )

        jawJnt = "c_Jaw_jnt"
        jawOpenFollowMult = cmds.shadingNode("multiplyDivide", asUtility=True, n="jawOpenFollow_mult")

        cmds.connectAttr("{}.rx".format(jawJnt), "{}.input1X".format(jawOpenFollowMult))
        cmds.connectAttr("{}.rx".format(jawJnt), "{}.input1Y".format(jawOpenFollowMult))
        cmds.connectAttr("{}.rx".format(jawJnt), "{}.input1Z".format(jawOpenFollowMult))
        cmds.setAttr("{}.input2".format(jawOpenFollowMult), 0.03, -0.06, 0.06)

        cmds.connectAttr("{}.outputX".format(jawOpenFollowMult), "{}.input2".format(midJntAdd))

        param = [0,1]
        for index, poc in enumerate(cornerPoc):
            prefix = poc[:2]
            pcPos = cmds.getAttr(poc + ".position")[0]

            self.createLipJoint([prefix,"corner"], "", "LipBroad", pcPos, self.broad_grp)

            self.midJntDict["{}corner".format(prefix)] = "{}LipBroadRX_corner".format(prefix)
            cornerCtl = self.genericController("{}LipBroadRX_corner".format(prefix).replace("_corner","_ctl"), (0, 0, 0),
                                         dist[1] / 80.0, "circle", self.colorIndex["blue"][0])

            name = "{}LipBroadRX_corner".format(prefix).replace("RX_corner","Corner_ctl")
            ctlChain = self.createMidController(name, dist[1] / 50.0, cornerCtl, param=param[index],
                                                guideCrv=self.polyCrv["up"], colorID=self.colorIndex["green"][0])
            ctl, offset, null, poc = [ctlChain[0], ctlChain[1], ctlChain[2], ctlChain[3]]
            cmds.parent(null, "lipBroadCtl_grp")

            if prefix == "r_":
                cmds.setAttr("{}.sx".format(null), -1)

            face_utils.polyCrvCtlSetup(name, ctl, offset, dist[1] / 60.0)

            midCtlDict["{}corner".format(prefix)] = ctl
            cmds.delete(cornerCtl)

        cornerJawBroad = [self.midJntDict["l_corner"], self.midJntDict["r_corner"]]

        addDoubleList = []
        for index, LR in enumerate(["l_", "r_"]):

            cornerBroad = cornerJawBroad[index]
            cornerRollBroad, cornerRYJnt = cmds.listRelatives(cornerBroad, ad=1, type='joint')
            cornerYBroad = cmds.listRelatives(cornerRYJnt, p=1)[0]
            cornerCtl = midCtlDict["{}corner".format(LR)]
            lipCornerMult = cmds.shadingNode("multiplyDivide", asUtility=True, n="{}lipCorner_mult".format(LR))
            addDouble = cmds.shadingNode("addDoubleLinear", asUtility=True, n="{}lipTX_add".format(LR))

            if LR == "r_":
                conversion = cmds.shadingNode("unitConversion", asUtility=True, n="{}lipCorner_conversion".format(LR))
                cmds.connectAttr("{}.tx".format(cornerCtl), "{}.input".format(conversion))
                cmds.setAttr("{}.conversionFactor".format(conversion), - 1)
                cmds.connectAttr("{}.output".format(conversion), "{}.input1X".format(lipCornerMult))
                RZconversion = cmds.shadingNode("unitConversion", asUtility=True, n="{}lipCorner_RzConv".format(LR))
                cmds.connectAttr("{}.rz".format(cornerCtl), "{}.input".format(RZconversion))
                cmds.setAttr("{}.conversionFactor".format(RZconversion), - 1)
                cmds.connectAttr("{}.output".format(RZconversion), "{}.rotateZ".format(cornerBroad))
            else:
                cmds.connectAttr("{}.tx".format(cornerCtl), "{}.input1X".format(lipCornerMult))
                cmds.connectAttr("{}.rz".format(cornerCtl), "{}.rotateZ".format(cornerBroad))

            cmds.connectAttr("{}.ty".format(cornerCtl), "{}.input1Y".format(lipCornerMult))
            cmds.connectAttr("{}.tz".format(cornerCtl), "{}.input1Z".format(lipCornerMult))
            cmds.connectAttr("lipFactor.lipJotX_ry", "{}.input2X".format(lipCornerMult))
            cmds.connectAttr("lipFactor.lipJotX_rx", "{}.input2Y".format(lipCornerMult))
            #cmds.setAttr("{}.input2Z".format(lipCornerMult), inverseVal[index])

            cmds.connectAttr("{}.outputX".format(lipCornerMult), "{}.input1".format(addDouble))
            cmds.connectAttr("{}.output".format(addDouble), "{}.ry".format(cornerYBroad))
            cmds.connectAttr("{}.outputY".format(lipCornerMult), "{}.rx".format(cornerBroad))
            cmds.connectAttr("{}.outputZ".format(lipCornerMult), "{}.tz".format(cornerBroad))
            addDoubleList.append(addDouble)

        #add corner inner movement
        cmds.connectAttr("{}.outputY".format(jawOpenFollowMult), "{}.input2".format(addDoubleList[0]))
        cmds.connectAttr("{}.outputZ".format(jawOpenFollowMult), "{}.input2".format(addDoubleList[1]))

        cmds.parent("lipBroadCtl_grp", "attachCtl_grp")
        cmds.select(self.guide_pocs)
        cmds.delete


    def constraintBroadJoints(self):

        #scale up midJoints to make them visible
        for key, jntTop in self.midJntDict.items():
            jntList = [x for x in cmds.listRelatives(jntTop, ad=1, type="joint")]
            for jnt in jntList:
                cmds.setAttr("{}.radius".format(jnt), 3)

        jaw_jnt = '{}Jaw{}'.format(self.cPrefix, self.jntSuffix)
        jaw_inv_jnt = '{}inverseJaw{}'.format(self.cPrefix, self.jntSuffix)

        broad_upper = cmds.listRelatives(self.midJntDict["c_up"], p=1, type ="transform")[0]
        broad_lower = cmds.listRelatives(self.midJntDict["c_lo"], p=1, type ="transform")[0]
        broad_left = cmds.listRelatives(self.midJntDict["l_corner"], p=1, type ="transform")[0]
        broad_right = cmds.listRelatives(self.midJntDict["r_corner"], p=1, type ="transform")[0]

        self.matrixParentConstraint( jaw_jnt, broad_lower)
        self.matrixParentConstraint( jaw_inv_jnt, broad_upper)

        #create constraints to corners
        self.matrixMultParentConstraint( [broad_upper, broad_lower], broad_left)
        self.matrixMultParentConstraint( [broad_upper, broad_lower], broad_right)

        cmds.select(cl=1)

    def getLipParts(self):
        """
        Create Dictionary: Each minor joint pairs with corresponding Broad joints
        Returns:

        """
        c_upper = self.midJntDict["c_up"]
        c_lower = self.midJntDict["c_lo"]
        l_corner = self.midJntDict["l_corner"]
        r_corner= self.midJntDict["r_corner"]

        lip_joints = cmds.listRelatives('lipJotP', c = 1)

        lookup = { 'c_up' : {},
                   'c_lo' : {},
                   'l_up': {},
                   'l_lo': {},
                   'r_up': {},
                   'r_lo': {},
                   'l_corner': {},
                   'r_corner': {}
        }

        for jnt in lip_joints:
            if not cmds.objectType(jnt) == "transform":
                continue

            if jnt.startswith('c') and "_up" in jnt:
                lookup['c_up'][jnt] = [ c_upper ]

            elif jnt.startswith('c') and "_lo" in jnt:
                lookup['c_lo'][jnt] = [ c_lower ]

            elif jnt.startswith( 'l') and "_up" in jnt:
                lookup['l_up'][jnt] = [ c_upper, l_corner]

            elif jnt.startswith( 'l') and "_lo" in jnt:
                lookup['l_lo'][jnt] = [c_lower, l_corner]

            elif jnt.startswith('r') and "_up" in jnt:
                lookup['r_up'][jnt] = [c_upper, r_corner]

            elif jnt.startswith('r') and "_lo" in jnt:
                lookup['r_lo'][jnt] = [c_lower, r_corner]

            elif jnt.startswith('l') and "corner" in jnt:
                lookup['l_corner'][jnt] = [ l_corner]

            elif jnt.startswith('r') and "corner" in jnt:
                lookup['r_corner'][jnt] = [ r_corner ]

        return lookup



    def createSeal(self, part):

        seal_name = 'jaw_seal_grp'
        seal_parent = seal_name if cmds.objExists(seal_name) else \
            cmds.createNode('transform', name = seal_name, p = self.jawMain_grp)

        part_grp = cmds.createNode('transform', name = seal_name.replace('seal', 'seal_{}'.format(part)), p = seal_parent)
        c_upper = self.midJntDict["c_up"]
        c_lower = self.midJntDict["c_lo"]
        l_corner = self.midJntDict["l_corner"]
        r_corner = self.midJntDict["r_corner"] #'{}_{}_broadCorner_{}'.format( RIGHT, JAW, JOINT)

        length = len(self.lipPartOrder[part])
        partList = self.lipPartOrder[part]

        # check if there is any flip!!
        corner_value = 1.0 / (float(length + 1) / 2)
        valueList = [z * corner_value for z in range((length + 1) / 2)]
        valueList = valueList[::-1] + valueList[1:]

        for index, jnt in partList.items():

            node = cmds.group( em=True, name=jnt.replace('JawP', 'Seal'), p = part_grp )

            rollJnt = [x for x in cmds.listRelatives( jnt, ad=1, type= "joint") if "Roll" in x][0]
            rollPos = cmds.xform(rollJnt, q=1, ws=1, t=1)
            rollLoc = cmds.spaceLocator( name = rollJnt.replace('JawRoll', 'Seal'), a=1)
            cmds.xform(rollLoc, ws=1, t=rollPos)
            cmds.parent( rollLoc, node)

            if jnt.startswith('r_'):

                prnt = [ c_upper, c_lower, r_corner ]

                #matrix_driver = self.matrixMultParentConstraint(prnt, node)
                const = cmds.parentConstraint(prnt, node, mo=1)[0]

                centerVal = float(corner_value*index)
                center_value = centerVal/2
                r_corner_value = 1.0 - centerVal

                cmds.setAttr('{}.{}W2'.format(const, r_corner), r_corner_value)
                cmds.setAttr('{}.{}W0'.format(const, c_upper), center_value)
                cmds.setAttr('{}.{}W1'.format(const, c_lower), center_value)
                print('{} r_corner const-strength is {}'.format(node, r_corner_value))

            elif jnt.startswith('c_'):
                prnt = [c_upper, c_lower]
                #matrix_driver = self.matrixMultParentConstraint(prnt, node)
                const = cmds.parentConstraint(prnt, node, mo=1)[0]

                cmds.setAttr('{}.{}W0'.format(const, c_upper), 0.5)
                cmds.setAttr('{}.{}W1'.format(const, c_lower), 0.5)

            elif jnt.startswith('l_'):

                prnt = [ c_upper, c_lower, l_corner ]
                #matrix_driver = self.matrixMultParentConstraint(prnt, node)
                const = cmds.parentConstraint(prnt, node, mo=1)[0]

                centerVal = float(corner_value*(length - index +1))
                center_value = centerVal / 2
                l_corner_value = 1.0 - centerVal

                cmds.setAttr('{}.{}W2'.format(const, l_corner), l_corner_value)
                cmds.setAttr('{}.{}W0'.format(const, c_upper), center_value)
                cmds.setAttr('{}.{}W1'.format(const, c_lower), center_value)
                print('index{}, {} l_corner const-strength is {}'.format(length - index, node, l_corner_value))
            #cmds.setAttr(wtAddMatrix + '.wtMatrix[%s].weightIn' % str(0), l_corner_value)
            #cmds.setAttr(wtAddMatrix + '.wtMatrix[%s].weightIn' % str(1), r_corner_value)

        cmds.setAttr('{}.visibility'.format(seal_parent), 0)

    def swivelSetup(self):

        if not cmds.objExists("arFacePanel"):
            raise RuntimeError("import arFacePanel")

        #swivel_ctl controls (LipJotX.tx/ ty/ tz. & LipJotX.ry / rz)
        swivelMult = cmds.shadingNode('multiplyDivide', asUtility=True, n='swivel_mult')
        self.jawCloseClamp = cmds.shadingNode("clamp", asUtility=True, n="jawClose_clamp")
        cmds.connectAttr('swivel_ctl.tx', swivelMult + '.input1X' )
        cmds.connectAttr('swivel_ctl.ty', swivelMult + '.input1Y' )
        cmds.connectAttr('swivel_ctl.tz', swivelMult + '.input1Z' )
        cmds.connectAttr("lipFactor.swivelMult_tx", swivelMult + '.input2X')
        cmds.connectAttr("lipFactor.swivelMult_ty", swivelMult + '.input2Y')
        cmds.connectAttr("lipFactor.swivelMult_tz", swivelMult + '.input2Z')

        cmds.connectAttr(swivelMult + '.outputX', 'jawClose_jnt.tx')
        cmds.connectAttr(swivelMult + '.outputZ', 'jawClose_jnt.tz')
        # limit jawClose's "up movement"
        cmds.connectAttr('{}.outputY'.format(swivelMult), "{}.inputR".format(self.jawCloseClamp))
        cmds.setAttr("{}.minR".format(self.jawCloseClamp), -5)
        cmds.connectAttr("{}.outputR".format(self.jawCloseClamp), 'jawClose_jnt.ty')

        jawCloseMult = cmds.shadingNode('multiplyDivide', asUtility=True, n='jawClose_mult')
        jawClose_add = cmds.shadingNode('addDoubleLinear', asUtility=True, n="jawClose_add")
        cmds.connectAttr('swivel_ctl.tx', jawCloseMult + '.input1Y')
        cmds.connectAttr("lipFactor.lipJotX_ry", jawCloseMult + '.input2Y')
        cmds.connectAttr(jawCloseMult + '.outputY', 'jawClose_jnt.ry')

        # complementary rz movement for ry !!! lower the rz value!!!
        cmds.connectAttr('swivel_ctl.tx', jawCloseMult + '.input1Z')
        cmds.connectAttr("lipFactor.lipJotX_rz", jawCloseMult + '.input2Z')
        cmds.connectAttr(jawCloseMult + '.outputZ', jawClose_add + ".input1")
        cmds.connectAttr('swivel_ctl.rz', jawClose_add + ".input2")
        cmds.connectAttr(jawClose_add + ".output", 'jawClose_jnt.rz')

    def jawOpenSetup(self):

        tranY_plus = cmds.shadingNode('plusMinusAverage', asUtility=True, n='ctlY_plus')
        pivot = cmds.xform("c_Jaw_jnt", q=1, ws=1, rp=1)
        cmds.xform("jawOpen_ctl", ws=1, piv=pivot)

        jawSemi = "jawSemi"
        jawJnt = "c_Jaw_jnt"
        cmds.connectAttr("jawOpen_ctl.t", "{}.t".format(jawJnt), f=1)
        cmds.connectAttr("jawOpen_ctl.r", "{}.r".format(jawJnt), f=1)
        cmds.parentConstraint(jawJnt, "jawSemiAdd")

        #limit the up movement
        cmds.connectAttr("jawSemiAdd.ty", "{}.inputG".format(self.jawCloseClamp))
        cmds.connectAttr("jawSemiAdd.rx", "{}.inputB".format(self.jawCloseClamp))
        cmds.setAttr("{}.minG".format(self.jawCloseClamp), -5)
        cmds.setAttr("{}.maxB".format(self.jawCloseClamp), 50)

        cmds.connectAttr("jawSemiAdd.tx", "{}.tx".format(jawSemi))
        cmds.connectAttr("{}.outputG".format(self.jawCloseClamp), "{}.ty".format(jawSemi))
        cmds.connectAttr("jawSemiAdd.tz", "{}.tz".format(jawSemi))

        cmds.connectAttr("{}.outputB".format(self.jawCloseClamp), "{}.rx".format(jawSemi))
        cmds.connectAttr("jawSemiAdd.ry", "{}.ry".format(jawSemi))
        cmds.connectAttr("jawSemiAdd.rz", "{}.rz".format(jawSemi))

        cmds.connectAttr("jawClose_jnt.ty", tranY_plus + ".input1D[0]")  # jaw_drop.ty *1
        cmds.connectAttr("jawSemi.ty", tranY_plus + ".input1D[1]")  # swivel_ctrl.ty * 1
        cmds.setAttr(tranY_plus + ".input1D[2]", -1)

        inputAttr = "{}.output1D".format(tranY_plus)
        outputAttr = ["lipJotP.scaleX", "lipJotP.scaleY", "jawSemi.scaleX", "jawSemi.scaleY"]
        exponent = ["lipFactor.jawSX_exponent", "lipFactor.jawSY_exponent"]
        face_utils.Util.indieScaleSquach(inputAttr, outputAttr, exponent)

        cmds.addAttr("jawOpen_ctl", ln="l_seal", at="double", min=0, max=10, dv=0, k=1)
        cmds.connectAttr("jawOpen_ctl.l_seal", "jaw_attributes.L_seal")
        cmds.addAttr("jawOpen_ctl", ln="r_seal", at="double", min=0, max=10, dv=0, k=1)
        cmds.connectAttr("jawOpen_ctl.r_seal", "jaw_attributes.R_seal")

        jawFatJnt = cmds.duplicate("jawClose_jnt", n="jawFat_jnt")[0]
        chinJnt = cmds.duplicate("jawClose_jnt", n="chin_jnt")[0]

        lipYPos = cmds.getAttr("helpPanel_grp.lipYPos")
        chinPos = cmds.getAttr("helpPanel_grp.chinPos")
        cmds.xform(jawFatJnt, ws=1, t=lipYPos)
        jawFatOff = face_utils.addOffset(jawFatJnt)[1]
        cmds.parent(jawFatOff, "jawClose_jnt")

        cmds.xform(chinJnt, ws=1, t=(0, chinPos[1], chinPos[2]))
        chinOffset = face_utils.addOffset(chinJnt)[1]
        cmds.parent(chinOffset, "jawClose_jnt")

    def build(self):

        self.createMinorJoints()
        #setLipJntLabel(self, upLoCorner)
        self.jawRigHierarchy()
        self.createJawBase()
        self.createBroadJoints()
        self.constraintBroadJoints()
        self.createSeal("up")
        self.createSeal("lo")
        self.createJawAttrs()
        self.createConstraints()
        self.seal_connect("up")
        self.seal_connect("lo")
        self.createInitialValues("up")
        self.createInitialValues("lo")
        self.swivelSetup()
        self.jawOpenSetup()

    def createJawAttrs(self):

        lipPartDict = self.getLipParts()
        print(lipPartDict)
        node = cmds.createNode('transform', n='jaw_attributes', p ='faceFactors')
        cmds.addAttr(node, ln = lipPartDict['c_up'].keys()[0], min = 0, max = 1, dv = 0)
        cmds.setAttr('{}.{}'.format(node, lipPartDict['c_up'].keys()[0]), lock =1)

        for upper in sorted(lipPartDict['l_up'].keys()):
            cmds.addAttr(node, ln = upper, min = 0, max = 1, dv=0)

        cmds.addAttr(node, ln = lipPartDict['l_corner'].keys()[0], min =0, max=1, dv=1)
        cmds.setAttr('{}.{}'.format(node, lipPartDict['l_corner'].keys()[0]), lock=1)

        for lower in sorted(lipPartDict['l_lo'].keys())[::-1]:
            cmds.addAttr(node, ln = lower, min = 0, max = 1, dv=0)

        cmds.addAttr(node, ln = lipPartDict['c_lo'].keys()[0], min =0, max=1, dv=0)
        cmds.setAttr('{}.{}'.format(node, lipPartDict['c_lo'].keys()[0]), lock=1)

        self.createOffsetFollow()
        self.addSealAttrs()


    def createOffsetFollow(self):

        jaw_attr = 'jaw_attributes'

        jaw_joint = '{}Jaw{}'.format(self.cPrefix, self.jntSuffix)
        jaw_auto = '{}Jaw{}_AUTO'.format(self.cPrefix, self.jntSuffix)

        # add following attributes
        cmds.addAttr(jaw_attr, ln='follow_ty', min=-10, max=10, dv=1)
        cmds.addAttr(jaw_attr, ln='follow_tz', min=-10, max=10, dv=1)

        unit = cmds.createNode('unitConversion', name='{}_Jaw_follow_UNIT'.format(self.cPrefix))

        remap_y = cmds.createNode('remapValue', name='{}_Jaw_followY_remap'.format(self.cPrefix))
        cmds.setAttr('{}.inputMax'.format(remap_y), 1)

        remap_z = cmds.createNode('remapValue', name='{}_Jaw_followZ_remap'.format(self.cPrefix))
        cmds.setAttr('{}.inputMax'.format(remap_z), 1)

        jaw_mult = cmds.createNode('multDoubleLinear', name='{}_Jaw_follow_mult'.format(self.cPrefix))
        cmds.setAttr('{}.input2'.format(jaw_mult), -1)

        cmds.connectAttr('{}.rx'.format(jaw_joint), '{}.input'.format(unit))
        cmds.connectAttr('{}.output'.format(unit), '{}.inputValue'.format(remap_y))
        cmds.connectAttr('{}.output'.format(unit), '{}.inputValue'.format(remap_z))

        cmds.connectAttr('{}.follow_ty'.format(jaw_attr), '{}.input1'.format(jaw_mult))
        cmds.connectAttr('{}.follow_tz'.format(jaw_attr), '{}.outputMax'.format(remap_z))
        cmds.connectAttr('{}.output'.format(jaw_mult), '{}.outputMax'.format(remap_y))

        cmds.connectAttr('{}.outValue'.format(remap_y), '{}.ty'.format(jaw_auto))
        cmds.connectAttr('{}.outValue'.format(remap_z), '{}.tz'.format(jaw_auto))

    def addSealAttrs(self):
        """

        Returns:

        """
        jaw_attr = 'jaw_attributes'
        cmds.addAttr(jaw_attr, at='double', ln='L_seal', min=0, max=10, dv=0)
        cmds.addAttr(jaw_attr, at='double', ln='R_seal', min=0, max=10, dv=0)

        cmds.addAttr(jaw_attr, at='double', ln='L_seal_delay', min=0.1, max=10, dv=4)
        cmds.addAttr(jaw_attr, at='double', ln='R_seal_delay', min=0.1, max=10, dv=4)


    def createConstraints(self):

        valueList = self.getLipParts().values()
        # minor joint connection or constraint
        for value in valueList:
            #r_loJawP_01': ['c_loLipBroadRX_00', 'r_LipBroadRX_corner']....., 'c_upJawP_00': ['c_upLipBroadRX_00']
            for lip_jnt, broad_jnt in value.items():

                #seal_token = 'upper_seal' if 'Upper' in lip_jnt else 'lower_seal'
                lip_seal = lip_jnt.replace( "JawP", "Seal")

                # minor JawRY_jnt connection 01/08/2024
                minorRY_jnt = lip_jnt.replace('JawP','JawRY')
                #l_LipBroadRX_corner -- > l_LipBroadRY_corner
                #broad_ryJnt = [ bj.replace('BroadRX', 'BroadRY') for bj in broad_jnt if not bj.startswith('c_')]

                #lipCorners have no seal node
                if not cmds.objExists(lip_seal):

                    const = cmds.parentConstraint(broad_jnt, lip_jnt, mo=1)[0]
                    cmds.setAttr('{}.interpType'.format(const), 1)
                    broad_ryJnt = broad_jnt[0].replace('BroadRX', 'BroadRY')
                    cmds.connectAttr('{}.ry'.format(broad_ryJnt), '{}.ry'.format(minorRY_jnt))
                    continue

                const = cmds.parentConstraint(broad_jnt, lip_seal, lip_jnt, mo =1)[0]
                cmds.setAttr('{}.interpType'.format(const), 1)

                if len(broad_jnt) == 1:
                    seal_attr = '{}_parentConstraint1.{}W1'.format(lip_jnt, lip_seal)
                    rev = cmds.createNode('reverse', n = lip_jnt.replace("JawP", 'rev'))
                    cmds.connectAttr(seal_attr, '{}.inputX'.format(rev))
                    cmds.connectAttr('{}.outputX'.format(rev), '{}_parentConstraint1.{}W0'.format(lip_jnt, broad_jnt[0]))
                    cmds.setAttr(seal_attr, 0)

                elif len(broad_jnt) == 2:

                    seal_attr = '{}_parentConstraint1.{}W2'.format(lip_jnt, lip_seal)
                    cmds.setAttr(seal_attr, 0)
                    seal_rev = cmds.createNode('reverse', n=lip_jnt.replace("JawP", 'Seal_rev'))
                    jaw_attr_rev = cmds.createNode('reverse', n=lip_jnt.replace("JawP", 'jaw_attr_rev'))
                    seal_mult = cmds.createNode('multiplyDivide', n=lip_jnt.replace("JawP", 'Seal_mult'))
                    minorRY_mult = cmds.createNode('multDoubleLinear', n=minorRY_jnt.replace("JawRY", 'JawRY_mult'))

                    cmds.connectAttr(seal_attr, '{}.inputX'.format(seal_rev))
                    cmds.connectAttr('{}.outputX'.format(seal_rev), '{}.input2X'.format(seal_mult))
                    cmds.connectAttr('{}.outputX'.format(seal_rev), '{}.input2Y'.format(seal_mult))

                    cmds.connectAttr('jaw_attributes.{}'.format(lip_jnt.replace(lip_jnt[0], 'l')), '{}.input1Y'.format(seal_mult))
                    cmds.connectAttr('jaw_attributes.{}'.format(lip_jnt.replace(lip_jnt[0], 'l')), '{}.inputX'.format(jaw_attr_rev))
                    cmds.connectAttr('{}.outputX'.format(jaw_attr_rev), '{}.input1X'.format(seal_mult))

                    cmds.connectAttr('{}.outputX'.format(seal_mult), '{}_parentConstraint1.{}W0'.format(lip_jnt, broad_jnt[0]))
                    cmds.connectAttr('{}.outputY'.format(seal_mult), '{}_parentConstraint1.{}W1'.format(lip_jnt, broad_jnt[1]))

                    #minor RY connection
                    broad_ryJnt = broad_jnt[1].replace('BroadRX', 'BroadRY')
                    cmds.connectAttr('{}.ry'.format(broad_ryJnt), '{}.input1'.format(minorRY_mult))
                    cmds.connectAttr('jaw_attributes.{}'.format(lip_jnt.replace(lip_jnt[0], 'l')),
                                     '{}.input2'.format(minorRY_mult))
                    cmds.connectAttr('{}.output'.format(minorRY_mult), '{}.ry'.format(minorRY_jnt))

                    print('jaw_attributes.{} connected to {}'.format(lip_jnt, minorRY_jnt))

    def createRotYConstraint(self):

        c_upperRY = cmds.listRelatives(self.midJntDict["c_up"], c=1)
        c_lowerRY = cmds.listRelatives(self.midJntDict["c_lo"], c=1)
        l_cornerRY = cmds.listRelatives(self.midJntDict["l_corner"], c=1)
        r_cornerRY = cmds.listRelatives(self.midJntDict["r_corner"], c=1)


    def createInitialValues(self, upLow, degree=1.3):
        # the bigger the degree the steeper the curve gets
        jaw_attr = [part for part in self.lipPartOrder[upLow].values() if not part.startswith('c') and not part.startswith('r')]
        length = len(jaw_attr)

        # for index, attr_name in enumerate( jaw_attr ):
        #     attr = 'jaw_attributes.{}'.format(attr_name)
        #
        #     linear_value = float(index)/float(browLength-1)
        #
        #     div_value = linear_value / degree
        #     final_value = div_value * linear_value
        #     cmds.setAttr(attr, final_value)

        crv = self.normalizedCurve("jawOpen_{}Crv".format(upLow))
        CVs = cmds.ls("{}.cv[*]".format(crv))
        pocList = self.create_pointOnCurve("jawOpen_{}".format(upLow), crv, length + 2)
        for i, poc in enumerate(pocList[1:-1]):
            attr = 'jaw_attributes.{}'.format(jaw_attr[i])
            cmds.connectAttr("{}.position.positionY".format(poc), attr)

    @classmethod
    def createAnimCurve(cls, name, period, height):
        animCrv = cmds.createNode('animCurveTU', name='{}_sineWave'.format(name))

        cmds.setKeyframe(animCrv, t=0, v=0, itt='flat', ott='flat')
        cmds.setKeyframe(animCrv, t=period, v=0, itt='flat', ott='flat')
        cmds.setKeyframe(animCrv, t=(period / 2.0), v=height, itt='flat', ott='flat')

        return animCrv

    @staticmethod
    def createFrameCache( name, period, height, length):
        """
        create bell type animCurve and attach frameCaches to get the yValues
        Args:
            name: frameCache name (name_frameCache00, 01...)
            period: max frame (time)
            height: max value
            length: number of cache required

        Returns: list of frameCache

        """
        crv = self.createAnimCurve( name, period, height)
        frmCaches = []
        for x in range(length):
            frameCache = cmds.createNode("frameCache", n ="{}_frameCache{:02d}".format(name, x))
            cmds.connectAttr("{}.output".format(crv), "{}.stream".format(frameCache))
            cmds.setAttr("{}.varyTime".format(frameCache), float(x * period / float(length)))
            frmCaches.append(frameCache)
        return frmCaches

    def seal_connect(self, part):

        jaw_attributes = "jaw_attributes"
        jnts = self.lipPartOrder[part].values()
        length = len(jnts)
        param = 1 / float(length - 1)
        seal_driver = cmds.createNode("lightInfo", name ="seal_{}_driver".format(part))

        triggers = {"L": list(), "R": list()}

        #seal from left to right and from right to left
        for side in "LR":

            seal_token = "{}_{}_seal".format(part, side)

            # substract = 10 - seal_delay
            sub = cmds.shadingNode("plusMinusAverage", asUtility=True, n='{}_sub'.format(seal_token))
            cmds.setAttr("{}.operation".format(sub), 2)
            cmds.setAttr("{}.input1D[0]".format(sub), 10)
            cmds.connectAttr("{}.{}_seal_delay".format(jaw_attributes, side), "{}.input1D[1]".format(sub))

            #division = substract / (browLength-1)
            divMult = cmds.shadingNode("multDoubleLinear", asUtility=True, n ='{}_div'.format(seal_token))
            cmds.connectAttr("{}.output1D".format(sub), "{}.input1".format(divMult))
            cmds.setAttr("{}.input2".format(divMult), param)

            trigger =[]
            triggers[side] = trigger

            for index, jnt in enumerate(jnts):

                if side=='L':
                    index = (length-index-1)

                delayRemap = cmds.shadingNode("remapValue", asUtility=True, n ='{}_{:02d}_delay_Remap'.format(seal_token, index))
                cmds.setAttr("{}.value[0].value_Interp".format(delayRemap), 2)
                cmds.connectAttr("{}.{}_seal".format(jaw_attributes, side), "{}.inputValue".format(delayRemap))

                # min value = division( (10-5:delay)/browLength * index ( if 6 jnts: 0, 1, 2, 3, 4, 5)
                # when delay close to 0.1, gap between min/max value close to 0.1 which means
                indexMult = cmds.shadingNode("multDoubleLinear", asUtility=True, n ='{}_{:02d}_index_mult'.format(seal_token, index))
                cmds.connectAttr("{}.output".format(divMult), "{}.input1".format(indexMult))
                cmds.setAttr("{}.input2".format(indexMult), index)

                # max value = min value + 5:delay ( if 6 jnts: 5, 6, 7, 8, 9, 10 )
                addition = cmds.shadingNode("plusMinusAverage", asUtility=True, n ='{}_{:02d}_delayAdd'.format(seal_token, index))
                cmds.connectAttr("{}.output".format(indexMult), "{}.input1D[0]".format(addition))
                cmds.connectAttr("{}.{}_seal_delay".format(jaw_attributes, side), "{}.input1D[1]".format(addition))

                #connect remap inputMin/inputMax
                cmds.connectAttr("{}.output".format(indexMult), "{}.inputMin".format(delayRemap))
                cmds.connectAttr("{}.output1D".format(addition), "{}.inputMax".format(delayRemap))

                trigger.append(delayRemap)

        idx = 0
        for lRemap, rRemap in zip(triggers["L"], triggers["R"]):

            totalSum = cmds.shadingNode("plusMinusAverage", asUtility=True, n ='{}_lip{:02d}_total_sum'.format(part, idx))
            cmds.connectAttr("{}.outValue".format(lRemap), "{}.input1D[0]".format(totalSum))
            cmds.connectAttr("{}.outValue".format(rRemap), "{}.input1D[1]".format(totalSum))

            #clamp to normalize the weight
            clamp = cmds.shadingNode("clamp", asUtility=True, n='{}_lip{:02d}_clamp'.format(part, idx))
            cmds.setAttr("{}.maxR".format(clamp), 1)
            cmds.connectAttr("{}.output1D".format(totalSum), "{}.input.inputR".format(clamp))

            constraint = '{}_parentConstraint1'.format(jnts[idx])
            sealAttr = [x for x in cmds.listAttr(constraint, c=True, inUse=True) if "Seal" in x]

            #add seal_driver attributes to debug
            attr_name = "seal_{}_{:02d}".format(part, idx)
            cmds.addAttr(seal_driver, ln = attr_name, at ="double", min=0, max=1, dv=0)
            cmds.connectAttr("{}.outputR".format(clamp), "{}.{}".format(seal_driver, attr_name))
            cmds.connectAttr("{}.{}".format(seal_driver, attr_name), "{}.{}".format(constraint, sealAttr[0]))
            idx +=1


    def sealCrvSetup(self):
        '''
        replace seal matrix constraints
        Returns:

        '''

        guideCrvs = []
        for upLow in ['up', 'lo']:

            guideCrv = '{}_lip_guide_crv'.format(upLow)
            if upLow == 'up':
                sealGuideCrv = cmds.duplicate(guideCrv, rc=1, n=guideCrv.replace('up', 'seal'))

            sealCrvShp = cmds.listRelatives(sealGuideCrv, c=1, s=1)[0]

            guideCrvs.append(guideCrv)

        bsNode = cmds.blendShape(guideCrvs, sealCrvShp, n='seal_crvBS')[0]
        for crv in guideCrvs:
            cmds.setAttr('{}.{}'.format(bsNode, crv), 0.5)

        for upLow in ['up', 'lo']:
            guideCrv = '{}_lip_guide_crv'.format(upLow)
            crvShp = cmds.listRelatives(guideCrv, c=1, s=1)[0]
            pocs = cmds.listConnections(crvShp, s=0, d=1, t='pointOnCurveInfo')

            nulls = cmds.listRelatives('jaw_seal_{}_grp'.format(upLow), c=1)

            for null in nulls:

                splits = null.split('_')
                prefix = '{}_'.format(splits[0])
                number = splits[-1]
                loc = cmds.listRelatives(null, c=1)[0]
                poc = '{}{}Jaw_{}_poc'.format(prefix, upLow, number)  # r_upJaw_09_poc
                if poc in pocs:
                    dummy = cmds.group(em=1, n='{}_{}Seal_{}_grp'.format(prefix, upLow, number),
                                       p='jaw_seal_{}_grp'.format(upLow))
                    cmds.connectAttr('{}.worldSpace[0]'.format(midCrvShp), '{}.inputCurve'.format(poc), f=1)
                    cmds.connectAttr('{}.position'.format(poc), '{}.translate'.format(dummy), f=1)
                    cmds.parent(null, dummy)



def sealOrignal(part):

    seal_token = 'seal_{}'.format(part)

    jaw_attrs = 'jaw_attributes'

    lip_jnts = lipPart(part)
    length = len(lip_jnts)
    seal_driver = cmds.createNode("lightInfo", name="C_{}_DRV".format(seal_token))

    triggers = {"L": list(), 'R':list()}

    for side in "LR":
        # get fall off
        delay_sub_name = "{}_{}_delay_SUB".format(side, seal_token)
        delay_sub = cmds.createNode("plusMinusAverage", name=delay_sub_name)

        cmds.setAttr('{}.operation'.format(delay_sub), 2)
        cmds.setAttr('{}.input1D[0]'.format(delay_sub), 10)
        cmds.connectAttr('{}.{}_seal_delay'.format(jaw_attrs, side), '{}.input1D[1]'.format(delay_sub))

        linearData = 1/float(length-1)
        print (linearData)
        delay_div_name = '{}_{}_delay_DIV'.format(side, seal_token)
        delay_div = cmds.createNode('multDoubleLinear', name = delay_div_name)
        cmds.setAttr('{}.input2'.format(delay_div), linearData)
        cmds.connectAttr('{}.output1D'.format(delay_sub), '{}.input1'.format(delay_div))
        # sealRatio = 1/(browLength-1) * (delay max(10) - delay current(4))

        mult_triggers = list()
        sub_triggers = list()
        triggers[side].append(mult_triggers)
        triggers[side].append(sub_triggers)

        for index in range(length):
            index_name = 'jaw_{:02d}'.format(index)

            #create mult node = sealRatio * index
            delay_mult_name = '{}_{}_{}_delay_MULT'.format(index_name, side, index)
            delay_mult = cmds.createNode("multDoubleLinear", name = delay_mult_name)
            cmds.setAttr('{}.input1'.format(delay_mult), index)
            cmds.connectAttr('{}.output'.format(delay_div), '{}.input2'.format(delay_mult))

            # inputMin for remap
            mult_triggers.append(delay_mult)

            #create sub node = sealRatio * index + seal_delay(4) == joint16 max 10 / joint15 max 9.625 /....joint01 max 4.375/ joint00 max 4.00
            delay_sum_name = '{}_{}_{}_delay_SUM'.format(index_name, side, index)
            delay_sum = cmds.createNode("plusMinusAverage", name = delay_sub_name)
            cmds.connectAttr('{}.output'.format(delay_mult), '{}.input1D[0]'.format(delay_sum))
            cmds.connectAttr('{}.{}_seal_delay'.format(jaw_attrs, side), '{}.input1D[1]'.format(delay_sum))
            # inputMax for remap
            sub_triggers.append(delay_sum)

    #connect seal triggers to driver node
    for left_index in range(length):

        right_index = length - left_index - 1
        index_name = '{}_{}'.format(seal_token, left_index)

        l_mult_trigger, l_sub_trigger = triggers["L"][0][left_index], triggers["L"][1][left_index]
        r_mult_trigger, r_sub_trigger = triggers["L"][0][right_index], triggers["L"][1][right_index]

        #Left
        l_remap_name = "L_{}_REMAP".format(index_name)
        l_remap = cmds.shadingNode("remapValue", asUtility =True, n = l_remap_name)
        cmds.setAttr("{}.outputMax".format(l_remap), 1)
        cmds.setAttr("{}.value[0].value_Interp".format(l_remap), 2)

        cmds.connectAttr("{}.output".format(l_mult_trigger), "{}.inputMin".format(l_remap))
        cmds.connectAttr("{}.output1D".format(l_sub_trigger), "{}.inputMax".format(l_remap))

        # connect left seal attribute to input of remap
        cmds.connectAttr("{}.L_seal".format(jaw_attrs), "{}.inputValue".format(l_remap))

        #Right
        # substract 1 minus result from left_remap
        r_sub_name = "R_{}_SUB".format(index_name)
        r_sub = cmds.shadingNode("plusMinusAverage", asUtility =True, n = r_sub_name)
        cmds.setAttr("{}.operation".format(r_sub), 2)
        cmds.setAttr("{}.input1D[0]".format(r_sub), 1)

        cmds.connectAttr("{}.outValue".format(l_remap), "{}.input1D[1]".format(r_sub))

        r_remap_name = "R_{}_REMAP".format(index_name)
        r_remap = cmds.shadingNode("remapValue", asUtility =True, n = r_remap_name)
        cmds.setAttr("{}.outputMax".format(r_remap), 1)
        cmds.setAttr("{}.value[0].value_Interp".format(r_remap), 2)

        cmds.connectAttr("{}.output".format(r_mult_trigger), "{}.inputMin".format(r_remap))
        cmds.connectAttr("{}.output1D".format(r_sub_trigger), "{}.inputMax".format(r_remap))

        # connect left seal attribute to input of remap
        cmds.connectAttr("{}.R_seal".format(jaw_attrs), "{}.inputValue".format(r_remap))
        cmds.connectAttr("{}.output1D".format(r_sub), "{}.outputMax".format(r_remap))

        #final addition of both sides
        plus_name = "{}_final_SUM".format(index_name)
        plus = cmds.shadingNode("plusMinusAverage", asUtility =True, n = plus_name)

        cmds.connectAttr('{}.outValue'.format(l_remap), '{}.input1D[0]'.format(plus))
        cmds.connectAttr('{}.outValue'.format(r_remap), '{}.input1D[1]'.format(plus))

        #Clamp
        clamp_name = "{}_CLAMP".format(index_name)
        clamp = cmds.shadingNode("remapValue", asUtility =True, n = clamp_name)
        cmds.connectAttr('{}.output1D'.format(plus), '{}.inputValue'.format(clamp))
        #cmds.setAttr('{}.inputR'.format(clamp))

        cmds.addAttr(seal_driver, at='double', ln = index_name, min=0, max=1, dv=0)
        cmds.connectAttr("{}.outValue".format(clamp), "{}.{}".format(seal_driver, index_name))

        const = "{}_parentConstraint1".format(lip_jnts[left_index])
        const_attr = [attr for attr in cmds.listAttr(const, ud = True) if "seal" in attr]
        print ("{}.{}".format(const, const_attr[0]))
        cmds.connectAttr("{}.{}".format(seal_driver, index_name), "{}.{}".format(const, const_attr[0]))




def replaceCrv_jnt( uplo ):

    if cmds.objExists(uplo + '_jawOpenHiCrv'):

        crvShp = cmds.listRelatives(uplo + '_jawOpenHiCrv', c=1, type='nurbsCurve')[0]
        pocs = sorted(cmds.listConnections(crvShp, type ='pointOnCurveInfo'))
        l_poc = pocs[-1]
        r_poc = pocs[0]

        part = 'upper' if uplo == 'up' else 'lower'
        lipJnts = lipPart( part )
        print (len(lipJnts))
        lCorner_jnt = getLipParts()['L_corner'].keys()
        rCorner_jnt = getLipParts()['R_corner'].keys()

        print (lCorner_jnt)
        print (rCorner_jnt)

        if uplo == 'up':

            pocs = pocs[1:-1]

            l_connections = cmds.listConnections(l_poc, c=1, p=1, type='plusMinusAverage')
            for outAttr, inAttr in zip(*[iter(l_connections)] * 2):
                if 'positionX' in outAttr:
                    cmds.connectAttr(lCorner_jnt[0] + '.tx', inAttr, f=1)
                elif 'positionY' in outAttr:
                    cmds.connectAttr(lCorner_jnt[0] + '.ty', inAttr, f=1)
                elif 'positionZ' in outAttr:
                    cmds.connectAttr(lCorner_jnt[0] + '.tz', inAttr, f=1)

            r_connections = cmds.listConnections(r_poc, c=1, p=1, type='plusMinusAverage')
            for outAttr, inAttr in zip(*[iter(r_connections)] * 2):
                if 'positionX' in outAttr:
                    cmds.connectAttr(rCorner_jnt[0] + '.tx', inAttr, f=1)
                elif 'positionY' in outAttr:
                    cmds.connectAttr(rCorner_jnt[0] + '.ty', inAttr, f=1)
                elif 'positionZ' in outAttr:
                    cmds.connectAttr(rCorner_jnt[0] + '.tz', inAttr, f=1)

        print (len(pocs))
        for x, pc in enumerate(pocs):

            connections = cmds.listConnections(pc, c=1, p=1, type='plusMinusAverage')
            for outAttr, inAttr in zip(*[iter(connections)] * 2):
                if 'positionX' in outAttr:
                    cmds.connectAttr(lipJnts[x] + '.tx', inAttr, f=1)
                elif 'positionY' in outAttr:
                    cmds.connectAttr(lipJnts[x] + '.ty', inAttr, f=1)
                elif 'positionZ' in outAttr:
                    cmds.connectAttr(lipJnts[x] + '.tz', inAttr, f=1)



class FrontName(object):

    def __init__(self):

        self.front_name = None

    def frontName(self, node_name, splitter):

        name_split = node_name.split(splitter)

        length = len(name_split)

        if length > 1:
            format_list = []
            brakets = '{}'
            for i in range(length - 1):
                brakets +="_{}" if i < (length-2) else ""
                temp = name_split[i]
                format_list.append(temp)
            print format_list, length,  brakets
            self.front_name = brakets.format(*format_list)

        else:
            self.front_name = node_name

        return self.front_name



