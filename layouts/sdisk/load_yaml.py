import yaml

try:
    with open(r"layouts\sdisk\params.yaml", "r") as f:
        p = yaml.safe_load(f)

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

except Exception as e:
    print("Error opening yaml file. using defaults")
    arm_inner_frac = 0.1
    arm_outer_frac = 0.1
    arm_w_frac = 0.1
    arm_thick_frac = 0.1
    arm_pitch_ratio = 1.0
    arm_n = 4
    disk_r = 300
    arm_thetas = [0, 90, 270]
    inner_arc_frac = 0.25
    ped_arc_frac = 0.1
    actual_disk_r = 300
