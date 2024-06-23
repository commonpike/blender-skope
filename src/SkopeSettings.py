# SkopeSettings extends a dict
# with some extra features: 
#
# Each item can be accessed as a property
#
# Each item can represent a more complex value
# using nested dicts with properties
# like `default`, `minimum`, `maximum`
#
# The more complex values can be accessed 
# with methods like `get()`, `rnd()`, etc.
#

import random
  
class SkopeSettings(dict):
    def __init__(self, mapping=None):
        self.config = mapping
        super().__init__(mapping)

    def __getattr__(self,key):
        if key in self:
            return self[key]
        raise Exception("Key "+key+" not found")
    
    def get(self,key):
        return self.default(key)
     
    def default(self,key):
        if key in self:
            if not isinstance(self[key], dict):
                return self[key]
            if 'set' in self[key]:
                return self[key]['set']
            if 'fixed' in self[key]:
                return self[key]['fixed']
            if 'default' in self[key]:
                return self[key]['default']
            raise Exception("Key "+key+" has no default")
        raise Exception("Key "+key+" not found")

    def isRandom(self,key):
        if key in self:
            if 'random' in self[key]:
                return self[key]['random']
            return False
        raise Exception("Key "+key+" not found")
          
    def rnd(self,key,min=None,max=None,dist=None):
        if key in self:
            if not 'random' in self[key] or not self[key]['random']:
                return self.get(key)
            if dist is None:
                if 'distribution' in self[key]:
                    dist = self[key]['distribution']
                else:
                    dist = 'LINEAR'
            if min is None:
                if 'minimum' in self[key]:
                    min = self[key]['minimum']
                else:
                    min = self.get(key)
            if max is None:
                if 'maximum' in self[key]:
                    max = self[key]['maximum']
                else:
                    max = self.get(key)
            if dist == "LINEAR":
                return self.rndLinearFloat(min,max)
            raise Exception("Distribution "+dist+" not supported")
        raise Exception("Key "+key+" not found")

    def rndint(self,key, min=None, max=None, dist=None):
        if key in self:
            if not 'random' in self[key] or not self[key]['random']:
                return self.get(key)
            if dist is None:
                if 'distribution' in self[key]:
                    dist = self[key]['distribution']
                else:
                    dist = 'LINEAR'
            if min is None:
                if 'minimum' in self[key]:
                    min = self[key]['minimum']
                else:
                    min = self.get(key)
            if max is None:
                if 'maximum' in self[key]:
                    max = self[key]['maximum']
                else:
                    max = self.get(key)
            if dist == "LINEAR":
                return self.rndLinearInt(min,max)
            raise Exception("Distribution "+dist+" not supported")
        raise Exception("Key "+key+" not found")

    def rndbool(self,key):
        if key in self:
            if not 'random' in self[key] or not self[key]['random']:
                return self.get(key)
            if 'chance' in self[key]:
                chance = self[key]['chance']
            else:
                chance = .5
            return random.random() < chance
        raise Exception("Key "+key+" not found")
  
    # helpers 

    def rndLinearFloat(self,min,max):
        return min + random.random() * (max - min)

    def rndLinearInt(self,min,max):
        return random.randint(min,max)
        
        
