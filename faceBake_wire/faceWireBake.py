# -*- coding: utf-8 -*-
import maya.cmds as mc
import re
import math
import sys
import maya.mel as mel
from maya import OpenMaya
import os.path
import json
from functools import partial

def shapeWireBakeUI():

    windowName = 'shapeWireBakeUI'
    if mc.window( windowName, exists =True ):
        mc.deleteUI("shapeWireBakeUI")

    #create window
    mc.window('shapeWireBakeUI', title='shapeWireBakeUI', w=420, h=940, sizeable =True, resizeToFixChildren =True)
