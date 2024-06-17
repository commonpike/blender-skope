import random

def mix(src,dst,pct,easing):
    if easing == "LINEAR":
        return mixLinear(src,dst,pct)
    raise Exception("Easing "+easing+" not supported")

def mixLinear(src,dst,pct):
    return float(src)+(float(dst)-float(src))*pct/100

def rnd(min,max,dist):
    if dist == "LINEAR":
        return rndLinear(min,max)
    raise Exception("Distribution "+dist+" not supported")

def rndLinear(min,max):
    return min + random.random() * (max - min)