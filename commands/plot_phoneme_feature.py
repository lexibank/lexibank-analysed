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
ax.add_feature(LAND)
ax.add_feature(OCEAN)
ax.add_feature(COASTLINE)
ax.add_feature(BORDERS, linestyle=':')
ax.add_feature(LAKES, alpha=0.5)
ax.add_feature(RIVERS)

markersize = 3

values = set()
for language in sorted(data.values(), key=lambda x: x["features"]["concepts"]):
    value = language["features"][argv[2]]
    color = CMAP[value]
    values.add(value)
    try:
        ax.plot(
                language["longitude"],
                language["latitude"],
                marker="o",
                color=color,
                zorder=10,
                markersize=8
                )
    except TypeError:
        print(language.dataset, language.name)

for v in values:
    plt.plot(-100, -100, "o", markersize=10, color=CMAP[v], label=str(v))
plt.legend(loc=4)
plt.savefig(pkg_path.parent.joinpath("plots", argv[2]+".pdf").as_posix(), dpi=900)

