from cartopy import *
import cartopy.io.img_tiles as cimgt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt

import cartopy.feature as cfeature
from cartopy.feature import NaturalEarthFeature
import numpy as np
import json
from matplotlib import cm

from lexibank.cartopy import *
from lexibank import pkg_path
import numpy as np

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

# assemble values to get them arranged
value_set = []
for language in data.values():
    value_set += [language["features"][argv[2]]]
value_set = sorted(set(value_set))

minv, maxv = min(value_set), max(value_set)
targets = np.linspace(minv, maxv, 10)
conv = {}
for value in value_set:
    for i, v in enumerate(targets):
        if v <= value:
            conv[value] = 0.1 * i

values = set()
for language in sorted(data.values(), key=lambda x: x["features"]["concepts"]):
    value = language["features"][argv[2]]
    color = cm.jet(conv[value])
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

cbar = plt.colorbar(cm.ScalarMappable(norm=None, cmap=cm.jet), ax=ax,
        orientation="horizontal", shrink=0.4,
        ticks=[0, 0.5, 1]
        )
cbar.ax.set_xticklabels(
        [str(round(targets[0], 2)), str(round((targets[5]+targets[6])/2, 2)),
            str(round(targets[-1], 2))]
        )
plt.savefig(pkg_path.parent.joinpath("plots", argv[2]+".pdf").as_posix(), dpi=900)

