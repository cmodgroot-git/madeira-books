import json, sys
# usage: mkphoto.py regions.json  -> prints PHOTOS entries
# regions.json: {"sabado:5": {"img":"img/b2p6.jpg","W":1600,"H":898,"regions":[["key", [[x,y],...]], ...]}}
spec = json.load(open(sys.argv[1]))
W0, H0 = 465.8, 260
out = []
for pid, d in spec.items():
    sid, n = pid.split(':')
    p = f"{sid}{n}"
    sx, sy = W0 / d["W"], H0 / d["H"]
    defs, body = [], []
    for i, (key, pts) in enumerate(d["regions"]):
        s = " ".join(f"{x*sx:.1f},{y*sy:.1f}" for x, y in pts)
        defs.append(f'<clipPath id="{p}c{i}"><polygon points="{s}"/></clipPath>')
        body.append("${o('" + key + "',`<use href=\"#" + p + "ph\" clip-path=\"url(#" + p + f"c{i})\"/><polygon points=\"{s}\" fill=\"none\" stroke=\"#FFE2B8\" stroke-width=\"1.2\" stroke-linejoin=\"round\"/>`)}}")
    svg = "<defs>" + "".join(defs) + "</defs>" + f'<image id="{p}ph" href="{d["img"]}" x="0" y="0" width="465.8" height="260" preserveAspectRatio="none"/><rect class="dimmer" x="0" y="0" width="465.8" height="260" fill="#1B1512"/>' + "".join(body)
    out.append(f"'{pid}':{{w:465.8,svg:()=>`{svg}`}},")
print("\n".join(out))
