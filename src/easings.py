
import math

# https://easings.net/

def mix(src,dst,pct,easing="LINEAR"):
    if easing == "LINEAR":
        return mixLinear(src,dst,pct)
    if easing == "EASEINOUT":
        return mixInOutSine(src,dst,pct)
    if easing == "INOUTSINE":
        return mixInOutSine(src,dst,pct)
    if easing == "INOUTQUAD":
        return mixInOutQuad(src,dst,pct)
    if easing == "INOUTCUBIC":
        return mixInOutCubic(src,dst,pct)
    if easing == "INOUTQUART":
        return mixInOutQuart(src,dst,pct)
    if easing == "INOUTQUINT":
        return mixInOutQuint(src,dst,pct)
    if easing == "INOUTEXPO":
        return mixInOutExpo(src,dst,pct)
    if easing == "INOUTCIRC":
        return mixInOutCirc(src,dst,pct)

    raise Exception("Easing "+easing+" not supported")

def mixLinear(src,dst,pct):
    return float(src)+(float(dst)-float(src))*pct/100

def mixInOutSine(src,dst,pct):
    return float(src)+(float(dst)-float(src))*easeInOutSine(pct/100)

def mixInOutQuad(src,dst,pct):
    return float(src)+(float(dst)-float(src))*easeInOutQuad(pct/100)

def mixInOutCubic(src,dst,pct):
    return float(src)+(float(dst)-float(src))*easeInOutCubic(pct/100)

def mixInOutQuart(src,dst,pct):
    return float(src)+(float(dst)-float(src))*easeInOutQuart(pct/100)

def mixInOutQuint(src,dst,pct):
    return float(src)+(float(dst)-float(src))*easeInOutQuint(pct/100)

def mixInOutExpo(src,dst,pct):
    return float(src)+(float(dst)-float(src))*easeInOutExpo(pct/100)

def mixInOutCirc(src,dst,pct):
    return float(src)+(float(dst)-float(src))*easeInOutCirc(pct/100)



# -- helpers

def linear(t):
    return t

def easeInSine(t):
    return -math.cos(t * math.pi / 2) + 1

def easeOutSine(t):
    return math.sin(t * math.pi / 2)

def easeInOutSine(t):
    return -(math.cos(math.pi * t) - 1) / 2

def easeInQuad(t):
    return t * t

def easeOutQuad(t):
    return -t * (t - 2)

def easeInOutQuad(t):
    t *= 2
    if t < 1:
        return t * t / 2
    else:
        t -= 1
        return -(t * (t - 2) - 1) / 2

def easeInCubic(t):
    return t * t * t

def easeOutCubic(t):
    t -= 1
    return t * t * t + 1

def easeInOutCubic(t):
    t *= 2
    if t < 1:
        return t * t * t / 2
    else:
        t -= 2
        return (t * t * t + 2) / 2

def easeInQuart(t):
    return t * t * t * t

def easeOutQuart(t):
    t -= 1
    return -(t * t * t * t - 1)

def easeInOutQuart(t):
    t *= 2
    if t < 1:
        return t * t * t * t / 2
    else:
        t -= 2
        return -(t * t * t * t - 2) / 2

def easeInQuint(t):
    return t * t * t * t * t

def easeOutQuint(t):
    t -= 1
    return t * t * t * t * t + 1

def easeInOutQuint(t):
    t *= 2
    if t < 1:
        return t * t * t * t * t / 2
    else:
        t -= 2
        return (t * t * t * t * t + 2) / 2

def easeInExpo(t):
    return math.pow(2, 10 * (t - 1))

def easeOutExpo(t):
    return -math.pow(2, -10 * t) + 1

def easeInOutExpo(t):
    t *= 2
    if t < 1:
        return math.pow(2, 10 * (t - 1)) / 2
    else:
        t -= 1
        return -math.pow(2, -10 * t) - 1

def easeInCirc(t):
    return 1 - math.sqrt(1 - t * t)

def easeOutCirc(t):
    t -= 1
    return math.sqrt(1 - t * t)

def easeInOutCirc(t):
    t *= 2
    if t < 1:
        return -(math.sqrt(1 - t * t) - 1) / 2
    else:
        t -= 2
        return (math.sqrt(1 - t * t) + 1) / 2