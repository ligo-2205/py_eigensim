import yaml

try: 
    with open("params.yaml", "r") as f:
        p = yaml.safe_load(f)
    
    l_inner = p["l_inner"]
    l_outer = p["l_outer"]
    thick = p["thick"]
    pitch = p["pitch"]
    n = p["n"]
    theta = p["theta"]
    res = p["res"]
    outer_r = p["outer_r"]

except Exception as e: 
    print("Error opening yaml file. using defaults")
    l_inner = 40
    l_outer = 10
    thick = 5
    pitch = thick + 5
    n = 9
    theta = 80
    res = 4
    outer_r = 200