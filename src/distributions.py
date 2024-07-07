
import sys, random

def rnd(min=0.0,max=1.0,dist='UNIFORM'):
    if dist == "UNIFORM":
        return rndUniformFloat(min,max)
    if dist == "TRIANGULAR":
        return rndTriangularFloat(min,max)
    if dist == "BETA":
        return rndBetaFloat(min,max)
    if dist == "GAUSSIAN":
        return rndGaussianFloat(min,max)
    if dist == "LOGNORM":
        return rndLogNormFloat(min,max)
    raise Exception("Distribution "+dist+" not supported")

def rndint(min=0, max=sys.maxsize, dist='UNIFORM'):
    if dist == "UNIFORM":
        return rndUniformInt(min,max)
    if dist == "TRIANGULAR":
        return rndTriangularInt(min,max)
    if dist == "BETA":
        return rndBetaInt(min,max)
    if dist == "GAUSSIAN":
        return rndGaussianInt(min,max)
    if dist == "LOGNORM":
        return rndLogNormInt(min,max)
    raise Exception("Distribution "+dist+" not supported")

def rndbool(chance=.5,dist='UNIFORM'):
    if dist == "UNIFORM":
        return random.random() < chance
    if dist == "BETA":
        return random.betavariate(2,2) < .5
    raise Exception("Distribution "+dist+" not supported")

#---- helpers 

def rndUniformFloat(min,max):
    return random.uniform(min,max)

def rndTriangularFloat(min,max):
    return random.triangular(min,max)

def rndBetaFloat(min,max):
    return min + (max-min)*random.betavariate(2,2)

def rndGaussianFloat(minv,maxv):
    mu = (minv + maxv) / 2 
    sigma = (maxv - minv) / 3 # covers 99.9%
    return max(minv,min(maxv,random.gauss(mu,sigma)))

def rndLogNormFloat(min,max):
    mu = (min + max) / 2 
    sigma = (max - min) / 3 # covers 99.9%
    return random.uniform(min,max)

# int

def rndUniformInt(min,max):
    return random.randint(min,max)

def rndTriangularInt(min,max):
    return round(rndTriangularFloat(min,max))

def rndBetaInt(min,max):
    return round(rndBetaFloat(min,max))

def rndGaussianInt(min,max):
    return round(rndGaussianFloat(min,max))

def rndLogNormInt(min,max):
    return round(rndLogNormFloat(min,max))
    