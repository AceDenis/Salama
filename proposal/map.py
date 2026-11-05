import json, math
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPoly, Circle
INK="#17211f"; BR="#0f6b63"; SOFT="#e1f1ee"; LINE="#9fb3ae"; R="#b42318"
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":8.5})
LAT, LON = -1.3124, 36.8043
d = json.load(open("/tmp/pk/geo/kenya_counties.geojson"))
def rings(g):
    return [g["coordinates"][0]] if g["type"] == "Polygon" else [p[0] for p in g["coordinates"]]
fig = plt.figure(figsize=(7.4, 4.1), dpi=200)
ax1 = fig.add_axes([0.01, 0.04, 0.40, 0.90]); ax2 = fig.add_axes([0.45, 0.10, 0.53, 0.80])
# --- Kenya
for f in d["features"]:
    nai = f["properties"]["name"] == "Nairobi"
    for r in rings(f["geometry"]):
        ax1.add_patch(MPoly(r, closed=True, fc=BR if nai else "#eef2f1", ec="#6b7f7a" if not nai else BR, lw=0.7))
ax1.set_xlim(33.6, 42.0); ax1.set_ylim(-4.9, 5.6); ax1.set_aspect(1/ math.cos(math.radians(0))); ax1.axis("off")
ax1.plot([LON], [LAT], marker="o", ms=5, mfc=R, mec="white", mew=0.8, zorder=5)
ax1.annotate("Nairobi", xy=(LON, LAT), xytext=(37.7, -3.3), fontsize=8, color=INK, arrowprops=dict(arrowstyle="-", color=INK, lw=0.7))
ax1.text(37.9, 1.6, "KENYA", fontsize=11, fontweight="bold", color="#6b7f7a", ha="center")
ax1.text(41.4, -4.4, "Indian\nOcean", fontsize=7, color="#8aa", ha="right", style="italic")
ax1.text(34.4, 3.9, "Lake Turkana region\n(north-west)", fontsize=0.1, color="white")
ax1.set_title("a. Location in Kenya", fontsize=9, fontweight="bold", color=BR, loc="left")
# --- Nairobi
nai = [f for f in d["features"] if f["properties"]["name"] == "Nairobi"][0]
for r in rings(nai["geometry"]): ax2.add_patch(MPoly(r, closed=True, fc=SOFT, ec=BR, lw=1.2))
kmlat = 1/110.57; kmlon = 1/(111.32*math.cos(math.radians(abs(LAT))))
for km, ls in ((2, "-"), (5, "--")):
    ax2.add_patch(Circle((LON, LAT), km*kmlat, fill=False, ec=BR, lw=0.9, ls=ls, alpha=0.8))
ax2.plot([LON], [LAT], marker="o", ms=7, mfc=R, mec="white", mew=1, zorder=6)
ax2.set_xlim(36.62, 37.20); ax2.set_ylim(-1.45, -1.12)
ax2.set_aspect(1/ math.cos(math.radians(abs(LAT))))
# cardinal reference: city centre
cbd = (36.8172, -1.2864); ax2.plot(*cbd, marker="s", ms=4, mfc=INK, mec="white", zorder=5)
ax2.annotate("Nairobi city centre (approx.)", xy=cbd, xytext=(36.86, -1.205), fontsize=7, color=INK, arrowprops=dict(arrowstyle="-", color=INK, lw=0.6))
ax2.annotate("Defence College of Health Sciences\nS 1.3124°, E 36.8043°", xy=(LON, LAT), xytext=(36.86, -1.375), fontsize=8, fontweight="bold", color=R,
             arrowprops=dict(arrowstyle="-", color=R, lw=0.8))
ax2.text(LON-2*kmlat*0.72-0.012, LAT-2*kmlat*0.72-0.006, "2 km", fontsize=6.5, color=BR); ax2.text(LON-5*kmlat*0.72-0.012, LAT-5*kmlat*0.72-0.006, "5 km", fontsize=6.5, color=BR)
ax2.text(36.64, -1.135, "Nairobi County boundary (Natural Earth, generalised)", fontsize=6.5, color="#6b7f7a")
# scale bar 5 km and north arrow
x0, y0 = 36.99, -1.425; ax2.plot([x0, x0+5*kmlon*1.0], [y0, y0], color=INK, lw=2); ax2.text(x0+2.5*kmlon, y0+0.008, "5 km", ha="center", fontsize=7)
ax2.annotate("N", xy=(37.17, -1.15), xytext=(37.17, -1.205), ha="center", fontsize=9, fontweight="bold", arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.2))
ax2.set_xticks([36.7, 36.8, 36.9, 37.0, 37.1]); ax2.set_yticks([-1.4, -1.3, -1.2]); ax2.set_xticklabels(["36.7°E", "36.8°E", "36.9°E", "37.0°E", "37.1°E"], fontsize=6.5); ax2.set_yticklabels(["1.4°S", "1.3°S", "1.2°S"], fontsize=6.5)
ax2.grid(True, color=LINE, lw=0.3, alpha=0.6)
ax2.set_title("b. Study site within Nairobi", fontsize=9, fontweight="bold", color=BR, loc="left")
for s in ax2.spines.values(): s.set_color(LINE)
fig.savefig("fig/fig5_map.png", facecolor="white"); print("ok")
