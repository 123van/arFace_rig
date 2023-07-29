
import jaw_utils
reload(jaw_utils) 
jaw_utils.createGuides( 10, 9 )

jaw_utils.lip_guides()
jaw_utils.jaw_guides()
jaw_utils.createHierarchy()
jaw_utils.createMinorJoints()
jaw_utils.createBroadJoints()
jaw_utils.createJawBase()
jaw_utils.constraintBroadJoints()
jaw_utils.getLipParts()['L_upper']
jaw_utils.lipPart('upper')
jaw_utils.createSeal('upper')
jaw_utils.createSeal('lower')
jaw_utils.createJawAttrs()
jaw_utils.createConstraints()
jaw_utils.createInitialValues( degree=1.3)

jaw_utils.createInitialValues( 'upper',degree=1.3)
jaw_utils.createInitialValues( 'lower',degree=1.3)

import jaw_utils
reload(jaw_utils) 
jaw_utils.createGuides(5)
jaw_utils.lip_guides()
jaw_utils.base_guides()
jaw_utils.createHierarchy()
jaw_utils.createMinorJoints()
jaw_utils.createBroadJoints()
jaw_utils.createJawBase()
jaw_utils.constraintBroadJoints()

from maya import cmds
import sys
sys.modules.keys()

path = 'C:\Users\SW\OneDrive\Documents\maya\2020\scripts\arFace'

for module_name in sys.modules.keys():
    top_module = module_name.split('.')[0]
    if top_module == 'arFace':
        print module_name
    
    

from arFace.Misc import Core
reload(Core)
xx =Core.Core()
xx.prefix
xx.jasonPath

from functools import partial
def func(u,v,w,x):
    return u , v , w,  x
#Enter your code here to create and print with your partial function

dbl = partial(func, 4 , 2)
print (dbl(3,8))

class Character(object):
    
    def __init__(self, name):
        self.health= 100
        self.name = name

    def characterName(self,name):
        print (f"she is {name}")

class Blacksmith(Character):

    def __init__(self, name):
        super(Blacksmith, self).__init__(name)
        self.forgeName = self.forge( name )

    def forge(self, name):
        print (f"he is {name}")
        #print (health)

bs = Blacksmith("mochi")
bs.forgeName
bs.forge("cat")
print (bs.health) #100


class Hero(Blacksmith):
    def __init__(self, name, catName):
        super(Hero, self).__init__(name)
        self.cat = catName

    def heroName(self, name, cat, health):
        print ( f"your name is {name} + {cat} : {health}")

xx = Hero("mom", "son")
xx.characterName( "Annette")
xx.forgeName
xx.heroName( "Sukwon", "dog", 40 )


class BaseClass(object):
    def __init__(self):
        self.x = 5

    def printHam(self):

        print Base.printName()

        def writeLocInfoData(self, data, jsonPath = ''):
        
            #writing info data json file
            if not jsonPath:
                jsonPath = self.jsonPath
            
            with open(jsonPath, 'w+') as outfile:
                json.dump(data, outfile)
            outfile.close()
        
class inheritedClass(BaseClass):
    def __init__(self, y ):
        super(inheritedClass, self).__init__()
        self.y = y

    def mult( self, y ):
        print ( self.x*y )

kk = inheritedClass(8)
print (kk.y)
kk.mult(10)


