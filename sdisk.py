import pya
import re
import numpy as np
from pathlib import Path

def generate_gds(p: dict):
    """Takes a dictionary and generates a gds file at the location: layouts\sdisk\layouts

    One example of p might be: 
    p = {'arm_inner_frac': 0.05,
        'arm_n': 4,
        'arm_outer_frac': 0.05,
        'arm_pitch_ratio': 1.2,
        'arm_thetas': [0, 90, 180, 270],
        'arm_thick_frac': 0.05,
        'arm_w_frac': 0.5,
        'actual_disk_r': 500,
        'disk_r': 500,
        'inner_arc_frac': 0.25,
        'ped_arc_frac': 0.1
        }

    Args:
        p (dict): _description_
    """
    def Serpentine(arm_inner_frac: float,
                   arm_outer_frac: float,
                   arm_w_frac: float,
                   arm_thick_frac: float,
                   arm_pitch_ratio: float,
                   arm_n: int,
                   rot=0) -> pya.DPath:

        w_meander = arm_w_frac*disk_r
        thick = arm_thick_frac*disk_r
        pitch = arm_pitch_ratio*thick
        # extend arm_inner for simplicity
        arm_inner = inner_arc_frac*disk_r + arm_inner_frac*disk_r
        arm_outer = arm_outer_frac*disk_r
        # print(f"{arm_inner + arm_outer + (arm_n+1)*pitch} um")

        pts = list()
        pts += [pya.DPoint(0, 0), pya.DPoint(0, arm_inner),
                pya.DPoint(-w_meander/2, arm_inner)]

        for i in range(1, arm_n+1):
            ring_r = (arm_inner + i*pitch)

            if i % 2 == 0:
                x1 = w_meander/2
                x2 = -w_meander/2
            else:
                x1 = -w_meander/2
                x2 = w_meander/2

            y = arm_inner + i*pitch
            pts += [pya.DPoint(x1, y), pya.DPoint(x2, y)]

        if i % 2 == 0:
            x1 = -w_meander/2
            x2 = 0
        else:
            x1 = w_meander/2
            x2 = 0

        y1 = arm_inner + (arm_n)*pitch
        y2 = arm_inner + (arm_n+1)*pitch
        pts += [pya.DPoint(x1, y1), pya.DPoint(x2, y2)]

        pts.append(pya.DPoint(0, arm_outer +
                              arm_inner + pitch*(arm_n + 1)))

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

    arm_inner_frac = p["arm_inner_frac"]
    arm_outer_frac = p["arm_outer_frac"]
    arm_w_frac = p["arm_w_frac"]
    arm_thick_frac = p["arm_thick_frac"]
    arm_pitch_ratio = p["arm_pitch_ratio"]
    arm_n = p["arm_n"]
    disk_r = p["disk_r"]
    arm_thetas = p["arm_thetas"]
    inner_arc_frac = p["inner_arc_frac"]
    ped_arc_frac = p["ped_arc_frac"]
    actual_disk_r = p['actual_disk_r']

    layout = pya.Layout()
    scaling_factor = int(1/layout.dbu)

    si = layout.create_cell("si")
    l1 = layout.layer(1, 0)
    l2 = layout.layer(2, 0)

    for t in arm_thetas:
        s = Serpentine(arm_inner_frac=arm_inner_frac,
                       arm_outer_frac=arm_outer_frac,
                       arm_w_frac=arm_w_frac,
                       arm_thick_frac=arm_thick_frac,
                       arm_pitch_ratio=arm_pitch_ratio,
                       arm_n=arm_n,
                       rot=t)
        si.shapes(l1).insert(s)

    inner_disk = Circle(inner_arc_frac*disk_r)
    si.shapes(l1).insert(inner_disk)

    thick = arm_thick_frac*disk_r
    pitch = arm_pitch_ratio*thick
    arm_inner = inner_arc_frac*disk_r + arm_inner_frac*disk_r
    arm_outer = arm_outer_frac*disk_r
    disk_r_inner = arm_inner + arm_outer + (arm_n+1)*pitch
    assert disk_r_inner < actual_disk_r
    ring = Donut(disk_r_inner,
                 actual_disk_r,
                 scaling_factor)
    si.shapes(l1).insert(ring)

    gen_new = True
    gds_dir = Path(r"layouts\sdisk\layouts")

    i = 0
    for gds in gds_dir.glob("*.gds"):
        existing_i = int(re.findall(r'[0-9]+', gds.name)[0])
        if existing_i >= i:
            if gen_new:
                i = existing_i + 1
            else:
                i = existing_i

    # sdisk means serpentine disk
    gds_path = gds_dir/Path("sdisk{}.gds".format(i))

    layout.write(str(gds_path))
