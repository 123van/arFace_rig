import maya.cmds as mc
'''
from ..Misc import Core
reload(Core)

cPrefix        = 'c_',
                 prefix         = ['l_', 'r_'],
                 uploPrefix     = ['up', 'lo'],
                 cnrPrefix      = 'cnr',
                 ctlSuffix      = '_ctl',
                 jntSuffix      = '_jnt',
                 grpSuffix      = '_grp',
                 crvSuffix      = '_crv',
                 jntGrp         = 'jnt_grp',
                 crvGrp         = 'crv_grp',
                 clsGrp         = 'cls_grp',
                 ctlGrp         = 'ctl_grp',
                 jsonFileName   = 'info.json',
                 jsonBasePath   = '/corp/projects/eng/jhwang/svn/test/facialTest',
                 baseMaPath     = '/corp/projects/eng/jhwang/svn/maya/arFace/maFiles',
                 configFile     = '',
                 panelFilename  = 'panel.ma',
                 panelTopNode   = 'Panel',
                 faceMainNode   = 'faceMain',
                 faceLocTopNode = 'faceLoc_grp',
                 locFileName    = 'locators.ma',
                 faceFactors    = {},


class CreateGuides(Core.Core, Util.Util):
    def __init__(self, **kw):
        """
        initializing variables
        """
        Core.Core.__init__(self, **kw)
        Util.Util.__init__(self)'''

#object constants
GROUP = "grp"
JOINT = "jnt"
GUIDE = "guide"
JAW = "jaw"
#side constants
LEFT = "L"
RIGHT = "R"
CENTER = "C"

def addOffset( obj, suffix = 'Off' ):

    grp_offset = mc.createNode('transform', n = '{}_{}'.format(obj, suffix))
    obj_mat = mc.xform( obj, q=1, m = 1, ws=1)
    mc.xform( grp_offset, m= obj_mat, ws=1 )

    obj_parent = mc.listRelatives( obj, p =1 )
    if obj_parent:
        mc.parent( grp_offset, obj_parent)

    mc.parent( obj, grp_offset)

    return grp_offset

def createGuideChain( name, parent, loc_pos ):

    loc = mc.spaceLocator(n= name )[0]
    loc_off = addOffset(loc, suffix='Off')
    loc_grp = mc.createNode("transform", name= '{}_{}'.format(name, GROUP), p= parent )
    mc.setAttr('{}.t'.format(loc_off), *loc_pos)
    return loc_off, loc_grp

def createGuides():
    """

    Args:
        number:

    Returns:

    """
    if mc.objExists('jawRigPos'):
        jaw_pos = mc.xform('jawRigPos', q=1, ws=1, t=1)

        jaw_guide_grp = mc.createNode("transform", name='{}_{}_{}'.format(CENTER, GUIDE, GROUP))
        locs_grp = mc.createNode("transform", name='{}_lip_{}_{}'.format(CENTER, GUIDE, GROUP), p=jaw_guide_grp)
        lip_locs_grp = mc.createNode("transform", name='{}_lipLoc_{}_{}'.format(CENTER, GUIDE, GROUP), p=locs_grp)
        mc.setAttr('{}.t'.format(jaw_guide_grp), *jaw_pos)
    else:
        mc.confirmDialog( title='Confirm', message='import face_locators first!! ' )

    for upLow in ['up','lo']:
        if mc.objExists( upLow + '_guide_crv'):

            poc_list = sorted(mc.listConnections( upLow + 'Lip_guide_crvShape', d=1, t = 'pointOnCurveInfo' ))

            poc_len = len(poc_list)
            c_poc_index = (poc_len - 1) / 2
            left_poc = poc_list[c_poc_index + 1:-1]
            right_poc = list(reversed(poc_list[1:c_poc_index]))

            mid_name = '{}_{}_lip_{}'.format(CENTER, upLow, GUIDE)
            mid_nulls = createGuideChain( mid_name, lip_locs_grp)
            mid_pos = mc.getAttr( poc_list[c_poc_index] + '.position' )[0]
            mc.setAttr('{}.t'.format(mid_nulls[0]), *mid_pos)
            mc.parent(mid_nulls[0], mid_nulls[1])

            for side in [LEFT , RIGHT]:
                side_poc_list = left_poc if side == LEFT else right_poc
                for x in range(c_poc_index-1):

                    loc_name = '{}_{}_lip_{:02d}_{}'.format(side, upLow, x + 1, GUIDE)
                    poc_pos = mc.getAttr( side_poc_list[x] + '.position')[0]
                    loc_nulls = createGuideChain( loc_name, lip_locs_grp)
                    mc.setAttr('{}.t'.format(loc_nulls[0]), *poc_pos)
                    mc.parent(loc_nulls[0], loc_nulls[0])

        for locShp in mc.listRelatives(jaw_guide_grp, ad=1, typ='locator'):
            locTran = mc.listRelatives(locShp, p=1)[0]
            mc.setAttr(locTran + '.localScale', *(0.2, 0.2, 0.2))

        mc.select(cl=1)

    #create corners
    left_corner_name = '{}_Corner_lip_{}'.format( LEFT, GUIDE )
    left_nulls = createGuideChain( left_corner_name, lip_locs_grp)

    right_corner_name = '{}_Corner_lip_{}'.format(RIGHT, GUIDE)
    right_nulls = createGuideChain(right_corner_name, lip_locs_grp)

    left_pos = mc.getAttr(poc_list[-1] + '.position')[0]
    right_pos = mc.getAttr(poc_list[0] + '.position')[0]

    mc.setAttr('{}.t'.format(left_nulls[0]), *left_pos)
    mc.parent(left_nulls[0], left_nulls[1])
    mc.setAttr('{}.t'.format(right_nulls[0]), *right_pos)
    mc.parent(right_nulls[0], right_nulls[1])
    mc.select(cl=1)

def lip_guides():

    """

    Returns:

    """
    grp = '{}_lipMinor_{}_{}'.format(CENTER, GUIDE, GROUP)
    guides = [ loc for loc in mc.listRelatives(grp, c=1) if mc.objExists(grp)]

    return guides

def jaw_guides():
    """

    Returns:

    """
    grp = '{}_{}_base_{}_{}'.format(CENTER, JAW, GUIDE, GROUP)
    guides = [loc for loc in mc.listRelatives(grp, c=1) if mc.objExists(grp)]

    return guides

def createHierarchy():

    main_grp = mc.createNode( 'transform', n = '{}_{}_rig_{}'.format(CENTER, JAW, GROUP) )
    lip_grp = mc.createNode('transform', n='{}_{}Lip_{}'.format(CENTER, JAW, GROUP), p = main_grp)
    base_grp = mc.createNode( 'transform', n = '{}_{}Base_{}'.format(CENTER, JAW, GROUP) , p = lip_grp )

    minor_grp = mc.createNode('transform', n='{}_{}_LipMinor_{}'.format(CENTER, JAW, GROUP), p = lip_grp )
    broad_grp = mc.createNode('transform', n='{}_{}_LipBroad_{}'.format(CENTER, JAW, GROUP), p=lip_grp)

    mc.select(cl=1)


def createMinorJoints():

    minor_joints = []
    for guide in lip_guides():
        mat= mc.xform( guide, q=1, m=1, ws=1 )
        jnt = mc.joint( name = guide.replace( GUIDE, JOINT))
        mc.setAttr( '{}.radius'.format(jnt), 0.5 )
        mc.xform( jnt, m=mat, ws = True )

        #parent joint
        mc.parent( jnt, '{}_{}_LipMinor_{}'.format(CENTER, JAW, GROUP) )

        minor_joints.append(jnt)

    return minor_joints




def createJawBase():

    jaw_jnt = mc.joint( n = '{}_{}_{}'.format(CENTER, JAW, JOINT))
    jaw_inverse_jnt = mc.joint( n = '{}_inverse_{}_{}'.format(CENTER, JAW, JOINT))

    jaw_mat = mc.xform( jaw_guides()[0], q=1, ws=1, m=1)
    jaw_inverse_mat = mc.xform( jaw_guides()[1], q=1, ws=1, m=1)

    mc.xform( jaw_jnt, m = jaw_mat, ws=1)
    mc.xform( jaw_inverse_jnt, m = jaw_inverse_mat, ws=1)

    mc.parent( jaw_jnt,'{}_{}Base_{}'.format(CENTER, JAW, GROUP) )
    mc.parent(jaw_inverse_jnt, '{}_{}Base_{}'.format(CENTER, JAW, GROUP))

    mc.select(cl=1)

    #add offset
    addOffset( jaw_jnt, suffix = 'OFF')
    addOffset( jaw_inverse_jnt, suffix = 'OFF')


def matrixParentConstraint(prnt, child_list):

    if not type(child_list) == list:
        child_list = [child_list]

    for child in child_list:

        name_split=child.split('_')
        name = name_split[0] +'_'+ name_split[1]
        offset_matrix = mc.createNode('multMatrix', n=name + "_off_matrix")
        mult_matrix = mc.createNode('multMatrix', n=name + "_mult_matrix")
        decompose_matrix = mc.createNode('decomposeMatrix', n=name + "_decompose")

        mc.connectAttr(child + '.worldMatrix', offset_matrix + '.matrixIn[0]')
        mc.connectAttr(prnt + '.worldInverseMatrix', offset_matrix + '.matrixIn[1]')

        '''helpNode = "jaw_local_help"
        helpNode if mc.objExists(helpNode) else mc.createNode('transform', n=helpNode)
        mc.addAttr(helpNode, ln='localMatrix', numberOfChildren=100, at='compound')
        mc.addAttr(helpNode, ln="offsetMat_attr", at="fltMatrix")'''

        loca_mat = mc.getAttr(offset_matrix + '.matrixSum')
        mc.setAttr(mult_matrix + '.matrixIn[0]', loca_mat, type="matrix")
        #mc.connectAttr(offset_matrix + '.matrixSum', helpNode + '.offsetMat_attr')
        #mc.connectAttr(helpNode + '.offsetMat_attr', mult_matrix + '.matrixIn[0]')
        mc.connectAttr(prnt + '.worldMatrix', mult_matrix + '.matrixIn[1]')

        child_prnt = mc.listRelatives(child, p=1)
        if child_prnt:
            mc.connectAttr(child_prnt[0] + '.worldInverseMatrix', mult_matrix + '.matrixIn[2]')

        #disconnect to prevent any cycle
        #mc.disconnectAttr(offset_matrix + '.matrixSum', helpNode + '.offsetMat_attr')
        # mult_matrix to decompose_matrix
        mc.connectAttr(mult_matrix + '.matrixSum', decompose_matrix + '.inputMatrix')

        # connect child transform. t.r.s
        mc.connectAttr(decompose_matrix + '.outputTranslate', child + '.translate')
        mc.connectAttr(decompose_matrix + '.outputRotate', child + '.rotate')
        mc.connectAttr(decompose_matrix + '.outputScale', child + '.scale')

        # clean up
        mc.delete(offset_matrix)

def matrixMultParentConstraint(prnt_list, child):

    if not type(prnt_list) == list : prnt_list = [prnt_list]

    nameItems = child.split('_')
    length = len(nameItems)
    if length > 1:
        formatlist = []
        for i in range(length - 1):
            braket = '{}'
            braket += "_" + braket
            temp = nameItems[i]
            formatlist.append(temp)
        name = braket.format(*formatlist)
    else:
        name = child

    wtAddMatrix = None

    for i, prnt in enumerate(prnt_list):

        offset_matrix = mc.createNode('multMatrix', n=name + "_off_matrix")
        mult_matrix = mc.createNode('multMatrix', n=name + "_mult_matrix")
        decompose_matrix = mc.createNode('decomposeMatrix', n=name + "_decompose")

        mc.connectAttr(child + '.worldMatrix', offset_matrix + '.matrixIn[0]')
        mc.connectAttr(prnt + '.worldInverseMatrix', offset_matrix + '.matrixIn[1]')

        #mc.connectAttr(offset_matrix + '.matrixSum', helpNode + '.offsetMat_attr')
        loca_mat = mc.getAttr(offset_matrix + '.matrixSum')
        mc.setAttr(mult_matrix + '.matrixIn[0]', loca_mat, type="matrix")
        #mc.connectAttr(helpNode + '.offsetMat_attr', mult_matrix + '.matrixIn[0]')
        mc.connectAttr(prnt + '.worldMatrix', mult_matrix + '.matrixIn[1]')

        child_prnt = mc.listRelatives(child, p=1)
        if child_prnt:
            mc.connectAttr(child_prnt[0] + '.worldInverseMatrix', mult_matrix + '.matrixIn[2]')

        #disconnect to prevent any cycle
        #mc.disconnectAttr(offset_matrix + '.matrixSum', helpNode + '.offsetMat_attr')
        # clean up
        mc.delete(offset_matrix)

        if not wtAddMatrix:
            wtAddMatrix = mc.createNode('wtAddMatrix', n=name + "_wtAddMatrix")
        ratio = 1.0/len(prnt_list)

        mc.connectAttr(mult_matrix +'.matrixSum', wtAddMatrix + '.wtMatrix[%s].matrixIn' % str(i))
        mc.setAttr(wtAddMatrix +'.wtMatrix[%s].weightIn'%str(i), ratio)

    # wtAddMatrix to decompose_matrix
    mc.connectAttr(wtAddMatrix + '.matrixSum', decompose_matrix + '.inputMatrix' )

    # connect child transform. t.r.s
    mc.connectAttr(decompose_matrix + '.outputTranslate', child + '.translate')
    mc.connectAttr(decompose_matrix + '.outputRotate', child + '.rotate')
    mc.connectAttr(decompose_matrix + '.outputScale', child + '.scale')

    return wtAddMatrix


def constraintBroadJoints():

    jaw_jnt = 'jawClose_jnt'
    jaw_inv_jnt = 'headSkel_jnt'

    upper_grp = '{}_broadUpper_{}_grp'.format(CENTER, JAW, JOINT)
    lower_grp = '{}_{}_broadLower_{}_grp'.format(CENTER, JAW, JOINT)
    left_grp = '{}_{}_broadCorner_{}_grp'.format(LEFT, JAW, JOINT)
    right_grp= '{}_{}_broadCorner_{}_grp'.format(RIGHT, JAW, JOINT)

    print ( jaw_jnt, lower_grp )
    matrixParentConstraint( jaw_jnt, lower_grp)
    print(jaw_inv_jnt, upper_grp)
    matrixParentConstraint( jaw_inv_jnt, upper_grp)

    #create constraints to corners
    matrixMultParentConstraint( [upper_grp, lower_grp], left_grp)
    matrixMultParentConstraint( [upper_grp, lower_grp], right_grp)

    mc.select(cl=1)

def getLipParts():

    up_lip_jnts = mc.listRelatives('upLip_grp', c=1)
    lo_lip_jnts = mc.listRelatives('loLip_grp', c=1)

    l_corner = up_lip_jnts[-1]
    r_corner = up_lip_jnts[0]

    up_lip_jnts = up_lip_jnts[1:-1]

    upJnt_len = len(up_lip_jnts)
    loJnt_len = len(lo_lip_jnts)
    c_up_index = (upJnt_len - 1) / 2
    c_lo_index = (loJnt_len - 1) / 2

    c_up_jnt = up_lip_jnts[c_up_index]
    c_lo_jnt = lo_lip_jnts[c_lo_index]

    # from center to corner
    l_up_jnts = up_lip_jnts[c_up_index + 1:]
    l_lo_jnts = lo_lip_jnts[c_lo_index + 1:]
    # from center to corner
    r_up_jnts = list(reversed(up_lip_jnts[:c_up_index]))
    r_lo_jnts = list(reversed(lo_lip_jnts[:c_lo_index]))

    C_upper = '{}_{}_broadUpper_{}'.format( CENTER, JAW, GROUP)
    C_lower = '{}_{}_broadLower_{}'.format( CENTER, JAW, GROUP)
    L_corner = '{}_{}_broadCorner_{}'.format(LEFT, JAW, GROUP)
    R_corner= '{}_{}_broadCorner_{}'.format(RIGHT, JAW, GROUP)

    lookup = { 'C_upper' : {},
               'C_lower' : {},
               'L_upper': {},
               'L_lower': {},
               'R_upper': {},
               'R_lower': {},
               'L_corner': {},
               'R_corner': {}
    }

    lookup['C_upper'][c_up_jnt] = [ C_upper ]

    lookup['C_lower'][c_lo_jnt] = [ C_lower ]

    for jnt in l_up_jnts:
        lookup['L_upper'][jnt] = [ C_upper, L_corner]

    for jnt in l_lo_jnts:
        lookup['L_lower'][jnt] = [C_lower, L_corner]

    for jnt in r_up_jnts:
        lookup['R_upper'][jnt] = [C_upper, R_corner]

    for jnt in r_lo_jnts:
        lookup['R_lower'][jnt] = [C_lower, R_corner]

    lookup['L_corner'][l_corner] = [ L_corner]

    lookup['R_corner'][r_corner] = [ R_corner ]

    return lookup




def lipPart(part):

    lipDict = getLipParts()

    # 'C_lower : { minor joint: broad joint }, L_corner : { minor joint: broad joint}....'
    lip_parts = [ sorted(lipDict['R_{}'.format(part)].keys()), lipDict['C_{}'.format(part) ].keys(),
    sorted(lipDict['L_{}'.format(part)].keys())]
    #
    return [jnt for jnt in lip_parts for jnt in jnt]


def createBroadJoints():

    if mc.objExists( 'jawRig'):

        broad_grp = mc.createNode('transform', n='{}_{}_LipBroad_{}'.format(CENTER, JAW, GROUP), p='jawRig')

        upper_jnt_name = '{}_{}_broadUpper_{}'.format(CENTER, JAW, GROUP)
        upper_lipJnt = getLipParts()['C_upper'].keys()

        upper_broad_jnt = mc.duplicate( upper_lipJnt, rc=1, n = upper_jnt_name )
        upper_rotY_child = mc.listRelatives(upper_broad_jnt[0], ad =1, type ='joint')[1]

        #completely redo the naming start over
        upper_new_jnt = mc.rename( upper_rotY_child, upper_jnt_name.replace(GROUP, 'jotY'))
        mc.parent( upper_broad_jnt[0], broad_grp)

        mc.select(cl=1)

        lower_jnt_name = '{}_{}_broadLower_{}'.format(CENTER, JAW, GROUP)
        lower_lipJnt = getLipParts()['C_lower'].keys()
        lower_broad_jnt = mc.duplicate( lower_lipJnt, rc=1, n = lower_jnt_name )
        print lower_broad_jnt
        lower_rotY_child = mc.listRelatives(lower_broad_jnt[0], ad =1, type ='joint')[1]
        lower_new_jnt = mc.rename( lower_rotY_child, lower_jnt_name.replace(GROUP, 'jotY'))
        mc.parent( lower_broad_jnt[0], broad_grp)

        mc.select(cl=1)

        left_jnt_name = '{}_{}_broadCorner_{}'.format(LEFT, JAW, GROUP)
        left_lipJnt = getLipParts()['L_corner'].keys()
        left_broad_jnt = mc.duplicate( left_lipJnt, rc=1, n = left_jnt_name )
        print left_broad_jnt
        left_rotY_child = mc.listRelatives(left_broad_jnt[0], ad =1, type ='joint')[1]
        left_new_jnt = mc.rename( left_rotY_child, left_jnt_name.replace(GROUP, 'jotY'))
        mc.parent( left_broad_jnt[0], broad_grp)

        mc.select(cl=1)

        right_jnt_name = '{}_{}_broadCorner_{}'.format(RIGHT, JAW, GROUP)
        right_lipJnt = getLipParts()['R_corner'].keys()
        right_broad_jnt = mc.duplicate( right_lipJnt, rc=1, n = right_jnt_name )
        print right_broad_jnt
        right_rotY_child = mc.listRelatives(right_broad_jnt[0], ad =1, type ='joint')[1]
        right_new_jnt = mc.rename( right_rotY_child, right_jnt_name.replace(GROUP, 'jotY'))
        mc.parent( right_broad_jnt[0], broad_grp)

        mc.select(cl=1)


def constraintBroadJointsNew():

    jaw_jnt = 'jawClose_jnt'
    jaw_inv_jnt = 'headSkel_jnt'

    upper_grp = f'{CENTER}_{JAW}_broadUpper_{GROUP}'
    lower_grp = f'{CENTER}_{JAW}_broadLower_{GROUP}'
    left_grp = f'{LEFT}_{JAW}_broadCorner_{GROUP}'
    right_grp= f'{RIGHT}_{JAW}_broadCorner_{GROUP}'

    print ( jaw_jnt, lower_grp )
    matrixParentConstraint(jaw_jnt, lower_grp)
    print(jaw_inv_jnt, upper_grp)
    matrixParentConstraint(jaw_inv_jnt, upper_grp)

    #create constraints to corners : connect to offset parent matrix of broadCorner_jotY
    matrixMultParentConstraint([upper_grp, lower_grp], left_grp)
    matrixMultParentConstraint([upper_grp, lower_grp], right_grp)

    mc.select(cl=1)


def createSeal(part):

    jaw_jnt_pos = mc.xform( 'jawClose_jnt', q=1, ws=1, m=1)
    jaw_inv_jnt_pos = mc.xform( 'headSkel_jnt', q=1, ws=1, m=1)
    jaw_pos = jaw_inv_jnt_pos if part == 'upper' else jaw_jnt_pos

    seal_name = '{}_seal_{}'.format( CENTER, GROUP)
    seal_parent = seal_name if mc.objExists( seal_name) else \
        mc.createNode( 'transform', name = seal_name, p = '{}_{}_rig_{}'.format(CENTER, JAW, GROUP) )
    mc.xform( seal_parent, ws=1, m= jaw_pos )

    part_grp = mc.createNode( 'transform', name = seal_name.replace('seal', 'seal_{}'.format(part)), p = seal_parent)

    l_corner = '{}_{}_broadCorner_{}'.format( LEFT, JAW, GROUP)
    r_corner = '{}_{}_broadCorner_{}'.format( RIGHT, JAW, GROUP)

    length = len(lipPart(part))
    part_dict = lipPart(part)

    for idex, jnt in enumerate( part_dict):

        child_jnt = mc.listRelatives( jnt, ad=1, type ='joint' )

        jnt_pos = mc.xform( child_jnt[0], q=1, ws=1, t=1 )
        jntY_pos = mc.xform( child_jnt[1], q=1, ws=1, m=1 )
        name = jnt.replace( 'JotX','_seal_')
        loc_off, loc_grp = createGuideChain(name, part_grp, jnt_pos)
        locY_grp = mc.createNode( 'transform', n = jnt.replace( 'JotX','_jotY_'))
        mc.xform( locY_grp, ws=1, m= jntY_pos)
        mc.parent( locY_grp, loc_grp )
        mc.parent(loc_off, locY_grp )

        # check if there is any flip!!
        addMatrix = matrixMultParentConstraint( [l_corner, r_corner], loc_grp )

        l_corner_value = float(idex)/float(length-1)
        r_corner_value = 1 - l_corner_value

        mc.setAttr(addMatrix + '.wtMatrix[%s].weightIn' % str(0), l_corner_value)
        mc.setAttr(addMatrix + '.wtMatrix[%s].weightIn' % str(1), r_corner_value)


def build():
    # after create arFace Jaw
    createBroadJoints()
    constraintBroadJointsNew()
    createSeal('upper')
    createSeal('lower')
    createJawAttrs()
    createConstraints()

    createInitialValues('upper', degree=1.3)
    createInitialValues('lower', degree=1.3)


def createJawAttrs():
    # {'C_lower': {u'c_jawLower_lip_jnt': ['c_jaw_broadLower_jnt']},'C_upper': {u'c_jawUpperBS_lip_jnt': ['c_jaw_broadUpper_jnt']}....
    lipPartDict = getLipParts()
    node = mc.createNode( 'transform', n= 'jaw_attributes', p = 'faceFactors')

    mc.addAttr( node, ln = lipPartDict['R_corner'].keys()[0], min =0, max=1, dv=1 )
    mc.setAttr( '{}.{}'.format( node, lipPartDict['R_corner'].keys()[0] ), lock=1 )

    for upper in sorted(lipPartDict['R_upper'].keys()):
        mc.addAttr( node, ln = upper, min = 0, max = 1, dv=0)

    mc.addAttr( node, ln = lipPartDict['C_upper'].keys()[0], min = 0, max = 1, dv = 0 )
    mc.setAttr( '{}.{}'.format(node, lipPartDict['C_upper'].keys()[0] ), lock =1 )

    for upper in sorted(lipPartDict['L_upper'].keys()):
        mc.addAttr( node, ln = upper, min = 0, max = 1, dv=0)

    mc.addAttr( node, ln = lipPartDict['L_corner'].keys()[0], min =0, max=1, dv=1 )
    mc.setAttr( '{}.{}'.format( node, lipPartDict['L_corner'].keys()[0] ), lock=1 )

    for lower in sorted(lipPartDict['R_lower'].keys()):
        mc.addAttr( node, ln = lower, min = 0, max = 1, dv=0)

    mc.addAttr( node, ln = lipPartDict['C_lower'].keys()[0], min =0, max=1, dv=0 )
    mc.setAttr( '{}.{}'.format( node, lipPartDict['C_lower'].keys()[0] ), lock=1 )

    for lower in sorted(lipPartDict['L_lower'].keys()):
        mc.addAttr( node, ln = lower, min = 0, max = 1, dv=0)




def createConstraints():

    values = getLipParts().values()
    ratio = 2.0 / float(len(values)-2)
    for value in values:
        for lip_jnt, broad_jnt in value.items():

            lip_seal = lip_jnt.replace( 'JotX', '_seal_')+'_grp'

            if mc.objExists( lip_seal):
                broad_jnt.append(lip_seal)
                const = mc.parentConstraint( broad_jnt, lip_jnt, mo =1 )[0]
                mc.setAttr( '{}.interpType'.format(const), 2)

                if len(broad_jnt) == 2:
                    seal_attr = '{}_parentConstraint1.{}W1'.format(lip_jnt, lip_seal)
                    rev = mc.createNode( 'reverse', n = lip_jnt.replace(JOINT, 'rev'))
                    mc.connectAttr( seal_attr, '{}.inputX'.format(rev))
                    mc.connectAttr( '{}.outputX'.format(rev), '{}_parentConstraint1.{}W0'.format(lip_jnt, broad_jnt[0]))
                    mc.setAttr( seal_attr, 0 )

                elif len(broad_jnt) == 3:

                    seal_attr = '{}_parentConstraint1.{}W2'.format(lip_jnt, lip_seal)
                    mc.setAttr(seal_attr, 0)
                    seal_rev = mc.createNode('reverse', n=lip_jnt.replace(JOINT, 'seal_rev'))
                    jaw_attr_rev = mc.createNode('reverse', n=lip_jnt.replace(JOINT, 'jaw_attr_rev'))
                    seal_mult = mc.createNode('multiplyDivide', n=lip_jnt.replace(JOINT, 'seal_mult'))

                    mc.connectAttr(seal_attr, '{}.inputX'.format(seal_rev))
                    mc.connectAttr('{}.outputX'.format(seal_rev), '{}.input2X'.format(seal_mult) )
                    mc.connectAttr('{}.outputX'.format(seal_rev), '{}.input2Y'.format(seal_mult) )

                    mc.connectAttr('jaw_attributes.{}'.format(lip_jnt), '{}.input1Y'.format(seal_mult))
                    mc.connectAttr('jaw_attributes.{}'.format(lip_jnt), '{}.inputX'.format(jaw_attr_rev))
                    mc.connectAttr('{}.outputX'.format(jaw_attr_rev), '{}.input1X'.format(seal_mult))

                    mc.connectAttr('{}.outputX'.format(seal_mult), '{}_parentConstraint1.{}W0'.format(lip_jnt, broad_jnt[0]))
                    mc.connectAttr('{}.outputY'.format(seal_mult), '{}_parentConstraint1.{}W1'.format(lip_jnt, broad_jnt[1]))

            else:
                const = mc.parentConstraint( broad_jnt, lip_jnt, mo =1 )[0]
                mc.setAttr( '{}.interpType'.format(const), 2)



def createInitialValues( UpLo, degree=1.3):
    # the bigger the degree the steeper the curve gets
    jnts = lipPart(UpLo)
    length = len(jnts)
    center = (length+1)/2
    print center
    l_jaw_attr = jnts[center:]
    r_jaw_attr = jnts[:center-1]
    print (l_jaw_attr)
    print (r_jaw_attr)
    #jaw_attr = [ part for part in lipPart(UpLo) if not part == '{}LipJotX{}'.format( UpLo[:-3],str(center)) ]

    value = len(l_jaw_attr)

    for index, attr_name in enumerate( r_jaw_attr ):
        attr = 'jaw_attributes.{}'.format(attr_name)
        print (attr_name)
        linear_value = 1-float(index)/float(value-1)

        div_value = linear_value / degree
        final_value = div_value * linear_value
        mc.setAttr(attr, final_value)

    for index, attr_name in enumerate( l_jaw_attr ):
        print (attr_name)
        attr = 'jaw_attributes.{}'.format(attr_name)

        linear_value = float(index)/float(value-1)

        div_value = linear_value / degree
        final_value = div_value * linear_value
        mc.setAttr(attr, final_value)

    '''
    for part in ['upper', 'lower']:

        jaw_jnts = sorted(getLipParts()['L_{}'.format(part)].keys() )
        print jaw_jnts
        length = len(jaw_jnts)

        for idex, jnt in enumerate(jaw_jnts):
            linear_val = float(idex + 1) / float(length)
            div_value = linear_val / degree
            final_val = linear_val * div_value

            mc.setAttr('jaw_attributes.%s' % jnt, final_val)'''




class FrontNameGenernator(object):
        def __init__(self):

            self.name_split = None
            self.front_name = None

        def split_name(self, node_name, splitter):

            self.name_split = node_name.split(splitter)
            length = len(self.name_split)

            if self.length > 1:
                format_list = []
                for i in range(self.length - 1):
                    braket = '{}'
                    braket += "_%s" % braket
                    fmat = self.name_split[i]
                    print fmat

                    format_list.append(fmat)

                self.front_name = braket.format(*format_list)

            else:
                self.front_name = node_name

            return self.front_name


#frontName = FrontNameGenernator()
#frontName.split_name('l_jawUpper_lip_01_guide', '_')


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

frontNm = FrontName()
print frontNm.frontName('l_jawUpper_lip_01_guide', '_')
