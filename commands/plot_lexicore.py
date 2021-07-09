from cartopy import *
import cartopy.io.img_tiles as cimgt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt

import cartopy.feature as cfeature
from cartopy.feature import NaturalEarthFeature
import numpy as np
import json

from lexibank.cartopy import *
from lexibank import pkg_path

from sys import argv

if len(argv) > 1:
    data = json.load(open(argv[1]))
else:
    data = json.load(open("lexicore.json"))

fig = plt.figure(figsize=[20, 10])
ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

ax.coastlines(resolution='50m')
#ax.stock_img(resolution='50m')
ax.add_feature(LAND)
#ax.add_feature(cfeature.NaturalEarthFeature('physical','admin_0_boundary_lines_land',
#    '50m'))
ax.add_feature(OCEAN)
ax.add_feature(COASTLINE)
ax.add_feature(BORDERS, linestyle=':')
ax.add_feature(LAKES, alpha=0.5)
ax.add_feature(RIVERS)

markersize = 3
for language in sorted(data.values(), key=lambda x: x["features"]["concepts"]):
    if language["features"]["concepts"] > 1000:
        color = "Blue"
        scaler = 3
    elif language["features"]["concepts"] > 500:
        color = "CornFlowerBlue"
        scaler = 2.5
    elif language["features"]["concepts"] >= 200:
        color = "Purple"
        scaler = 2
    elif language["features"]["concepts"] >= 100:
        color = "Red"
        scaler = 1.5
    else:
        color = "red"
        scaler = 1
    
    ax.plot(
            language["longitude"],
            language["latitude"],
            marker="o",
            color=color,
            markersize=markersize*scaler
            )

plt.plot(-100, -100, "o", markersize=10, color="Blue", label="> 1000 concepts")
plt.plot(-100, -100, "o", markersize=10, color="CornFlowerBlue", label="> 500 concepts")
plt.plot(-100, -100, "o", markersize=10, color="Purple", label="> 200 concepts")
plt.plot(-100, -100, "o", markersize=10, color="Red", label="> 100 concepts")


plt.legend(loc=4)
plt.savefig(pkg_path.parent.joinpath("plots", "lexicore.pdf").as_posix(), dpi=900)


