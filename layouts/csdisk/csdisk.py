import pya

import re
import numpy as np
from load_yaml import *
from pathlib import Path 

def CircularSerpentine(l_inner: float, l_outer: float, thick: float, pitch: float, n: int, theta: float, res=3, rot=0) -> pya.DPath:
    print(f"{l_inner + l_outer + (n+1)*pitch} um")

    pts = list()
    pts += [pya.DPoint(0, 0), pya.DPoint(0, l_inner)]

    # convert to radians
    theta = (theta)*np.pi/180

    dtheta = theta/(2*res)
    for p in range(1, res):
        x = l_inner*np.cos(p*dtheta + np.pi/2)
        y = l_inner*np.sin(p*dtheta + np.pi/2)
        pts.append(pya.DPoint(x, y))

    for i in range(1, n+1):
        dtheta = ((-1)**i)*theta/((i+2)*res)
        if i % 2 == 0:
            shift = np.pi/2 - theta/2
        else:
            shift = theta/2 + np.pi/2

        for p in range(1, (i+2)*res):
            ring_r = (l_inner + i*pitch)
            x = ring_r*np.cos(p*dtheta + shift)
            y = ring_r*np.sin(p*dtheta + shift)
            pts.append(pya.DPoint(x, y))

    if n % 2 == 0:
        dtheta = -1*theta/(2*res*int(n/2))
        shift = theta/2 + np.pi/2
    else:
        dtheta = theta/(2*res*int(n/2))
        shift = np.pi/2 - theta/2

    for p in range(1, res*int(n/2)+1):
        ring_r = (l_inner + (n+1)*pitch)
        x = ring_r*np.cos(p*dtheta + shift)
        y = ring_r*np.sin(p*dtheta + shift)
        pts.append(pya.DPoint(x, y))

    pts.append(pya.DPoint(0, l_outer +
                          l_inner + pitch*(n + 1)))

    tt = pya.DCplxTrans(1,  rot, False, 0, 0)
    return tt*pya.DPath(pts, thick)


def Circle(radius: float,) -> pya.DPolygon:

    pts = list()
    pts += [pya.DPoint(radius*np.sin(theta), radius*np.cos(theta))
            for theta in np.linspace(0, 2*np.pi, 360)]

    return pya.DPolygon(pts)


def Donut(inner_r: float, outer_r: float, scaling_factor: float) -> pya.DPolygon:
    inner_circle = Circle(inner_r*scaling_factor)
    outer_circle = Circle(outer_r*scaling_factor)

    R0 = pya.Region()
    R1 = pya.Region()
    R0.insert(outer_circle)
    R1.insert(inner_circle)

    return R0 - R1


layout = pya.Layout()
scaling_factor = int(1/layout.dbu)

si = layout.create_cell("si")
l = layout.layer(1, 0)


cs1 = CircularSerpentine(l_inner=l_inner,
                         l_outer=l_outer,
                         thick=thick,
                         pitch=pitch,
                         n=n,
                         theta=theta,
                         res=res,
                         rot=0)

cs2 = CircularSerpentine(l_inner=l_inner,
                         l_outer=l_outer,
                         thick=thick,
                         pitch=pitch,
                         n=n,
                         theta=theta,
                         res=res,
                         rot=90)

cs3 = CircularSerpentine(l_inner=l_inner,
                         l_outer=l_outer,
                         thick=thick,
                         pitch=pitch,
                         n=n,
                         theta=theta,
                         res=res,
                         rot=180)

cs4 = CircularSerpentine(l_inner=l_inner,
                         l_outer=l_outer,
                         thick=thick,
                         pitch=pitch,
                         n=n,
                         theta=theta,
                         res=res,
                         rot=270)

ped = Circle(l_inner - 10)
inner_r = l_inner + l_outer + (n+1)*pitch
ring = Donut(inner_r, outer_r, scaling_factor)

si.shapes(l).insert(cs1)
si.shapes(l).insert(cs2)
si.shapes(l).insert(cs3)
si.shapes(l).insert(cs4)
si.shapes(l).insert(ped)
si.shapes(l).insert(ring)

gds_dir = Path("layouts")

i = 0 
for gds in gds_dir.glob("*.gds"):
    existing_i = int(re.findall(r'[0-9]+', gds.name)[0])
    if existing_i >= i:
        i += 1

# csdisk means curved serpentine
gds_path = gds_dir/Path("csdisk{}.gds".format(i))
yml_path = gds_dir/Path("csdisk{}.yml".format(i))

layout.write(str(gds_path))

with open(yml_path, "w") as out: 
    yaml.dump(p, out, default_flow_style=False)