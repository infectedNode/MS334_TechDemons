def hsv(clr):
    r = clr[0]
    g = clr[1]
    b = clr[2]
    r, g, b = r/255.0, g/255.0, b/255.0
    mx = max(r, g, b)
    mn = min(r, g, b)
    df = mx-mn
    if mx == mn:
        h = 0
    elif mx == r:
        h = (60 * ((g-b)/df) + 360) % 360
    elif mx == g:
        h = (60 * ((b-r)/df) + 120) % 360
    elif mx == b:
        h = (60 * ((r-g)/df) + 240) % 360
    if mx == 0:
        s = 0
    else:
        s = (df/mx)*100
    v = mx*100

    return [int(h), int(s), int(v)]

def testColorH(val):
    if(val < 0):
        return 0
    elif(val > 360):
        return 360
    else:
        return val

def testColor(val):
    if(val < 0):
        return 0
    elif(val > 100):
        return 100
    else:
        return val               

def setColors(clrs=None):

    for clr in clrs:
        hsv_value = hsv(clr['rgb'])
        l1 = testColorH(hsv_value[0]-10)
        l2 = testColor(hsv_value[1]-20)
        l3 = testColor(hsv_value[2]-15)

        u1 = testColorH(hsv_value[0]+10)
        u2 = testColor(hsv_value[1]+20)
        u3 = testColor(hsv_value[2]+15)

        clr['lw'] = [l1, l2, l3]
        clr['up'] = [u1, u2, u3]

    return clrs    