
def mix(src,dst,pct,easing):
    if easing == "LINEAR":
        return mixLinear(src,dst,pct)
    raise Exception("Easing "+easing+" not supported")

def mixLinear(src,dst,pct):
    return float(src)+(float(dst)-float(src))*pct/100
