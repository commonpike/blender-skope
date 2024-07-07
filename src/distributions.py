
import sys, random

def rnd(min=0.0,max=1.0,dist='UNIFORM'):
    if dist == "UNIFORM":
        return rndUniformFloat(min,max)
    raise Exception("Distribution "+dist+" not supported")

def rndint(min=0, max=sys.maxsize, dist='UNIFORM'):
    if dist == "UNIFORM":
        return rndUniformInt(min,max)
    raise Exception("Distribution "+dist+" not supported")

def rndbool(chance=.5,dist='UNIFORM'):
    if dist == "UNIFORM":
        return random.random() < chance
    raise Exception("Distribution "+dist+" not supported")

#---- helpers 

def rndUniformFloat(min,max):
    return min + random.random() * (max - min)

def rndUniformInt(min,max):
    return random.randint(min,max)
    