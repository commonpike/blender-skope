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

from distributions import rnd,rndint,rndbool

class SkopeSettings(dict):
    def __init__(self, settings=None):
        self.settings = settings
        super().__init__(settings)

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
            if not isinstance(self[key], dict):
                return False
            if 'random' in self[key]:
                return self[key]['random']
            return False
        raise Exception("Key "+key+" not found")
          
    def rnd(self,key):
        if key in self:
            if not isinstance(self[key], dict):
                return self.get(key)
            if not 'random' in self[key] or not self[key]['random']:
                return self.get(key)
            if 'distribution' in self[key]:
                dist = self[key]['distribution']
            else:
                dist = 'UNIFORM'
            if 'minimum' in self[key]:
                min = self[key]['minimum']
            else:
                min = self.get(key)
            if 'maximum' in self[key]:
                max = self[key]['maximum']
            else:
                max = self.get(key)
            print('rnd',key,min,max)
            return rnd(min,max,dist)
        raise Exception("Key "+key+" not found")
    
    def rnd_delta(self,key,val):
        if key in self:
            if not isinstance(self[key], dict):
                return self.get(key)
            if not 'random' in self[key] or not self[key]['random']:
                return self.get(key)
            if 'delta' in self[key]:
                delta = self[key]['delta']
            else:
                delta = .1
            if 'distribution' in self[key]:
                dist = self[key]['distribution']
            else:
                dist = 'UNIFORM'
            if 'minimum' in self[key]:
                min = self[key]['minimum']
            else:
                min = self.get(key)
            if 'maximum' in self[key]:
                max = self[key]['maximum']
            else:
                max = self.get(key)
            deltamin = val - (delta * (val-min))
            deltamax = val + (delta * (max-val))
            print('rnd_delta',key,val,deltamin,deltamax)
            return rnd(deltamin,deltamax,dist)
        
        raise Exception("Key "+key+" not found")

    def rndint(self,key):
        if key in self:
            if not 'random' in self[key] or not self[key]['random']:
                return self.get(key)
            if 'distribution' in self[key]:
                dist = self[key]['distribution']
            else:
                dist = 'UNIFORM'
            if 'minimum' in self[key]:
                min = self[key]['minimum']
            else:
                min = self.get(key)
            if 'maximum' in self[key]:
                max = self[key]['maximum']
            else:
                max = self.get(key)
            return rndint(min,max,dist)
        raise Exception("Key "+key+" not found")

    def rndbool(self,key):
        if key in self:
            if not 'random' in self[key] or not self[key]['random']:
                return self.get(key)
            if 'distribution' in self[key]:
                dist = self[key]['distribution']
            else:
                dist = 'UNIFORM'
            if 'chance' in self[key]:
                chance = self[key]['chance']
            else:
                chance = .5
            return rndbool(chance,dist)
        raise Exception("Key "+key+" not found")
  
        
