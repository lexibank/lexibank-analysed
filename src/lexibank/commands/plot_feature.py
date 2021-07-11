"""
Plot Continuous Phonological Features to a Map.
"""
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

from lexibank.cartopy import (
        LAND, OCEAN, COASTLINE, BORDERS, LAKES, RIVERS, CMAP)
from lexibank import pkg_path
import numpy as np



def register(parser):
    parser.add_argument(
        '--datafile',
        help='location of dataset file in JSON',
        action='store',
        default="lexicore.json"
    )
    parser.add_argument(
        "--feature",
        help="select the feature you want to plot",
        action="store",
        default="UvularConsonants"
    )
    parser.add_argument(
        "--continuous",
        help="indicate if feature is continuous",
        action="store_true",
        default=False
    )
    parser.add_argument(
        "--filename",
        help="define name of output file for plot",
        action="store",
        default="file.pdf"
    )
    parser.add_argument(
        "--markersize",
        help="select size of marker file",
        type=float,
        action="store",
        default=8.0
        )
    parser.add_argument(
        "--colormap",
        help="select a colormap to be used",
        action="store",
        default="base"
        )


def run(args):
    data = json.load(open(args.datafile))
    fig = plt.figure(figsize=[20, 10])
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    
    ax.coastlines(resolution='50m')
    ax.add_feature(LAND)
    ax.add_feature(OCEAN)
    ax.add_feature(COASTLINE)
    ax.add_feature(BORDERS, linestyle=':')
    ax.add_feature(LAKES, alpha=0.5)
    ax.add_feature(RIVERS)
    
    if args.continuous:
        colormap = getattr(cm, args.colormap, cm.jet)

        # assemble values to get them arranged
        value_set = []
        for language in data.values():
            value_set += [language["features"][args.feature]]
        value_set = sorted(set(value_set))

        minv, maxv = min(value_set), max(value_set)
        targets = np.linspace(minv, maxv, 10)
        conv = {}
        for value in value_set:
            for i, v in enumerate(targets):
                if v <= value:
                    conv[value] = 0.1 * i
        
        for language in sorted(data.values(), key=lambda x: x["features"]["concepts"]):
            value = language["features"][args.feature]
            color = colormap(conv[value])
            try:
                ax.plot(
                        language["longitude"],
                        language["latitude"],
                        marker="o",
                        color=color,
                        zorder=10,
                        markersize=args.markersize
                        )
            except TypeError:
                args.log.warning("Skipping {0} / {1}".format(language.dataset,
                    language.name))
        
        cbar = plt.colorbar(cm.ScalarMappable(norm=None, cmap=colormap), ax=ax,
                orientation="horizontal", shrink=0.4,
                ticks=[0, 0.5, 1]
                )
        cbar.ax.set_xticklabels(
                [str(round(targets[0], 2)), str(round((targets[5]+targets[6])/2, 2)),
                    str(round(targets[-1], 2))]
                )
    else:
        colormap = CMAP.get(args.colormap, CMAP["base"])
        values = set()
        for language in sorted(data.values(), key=lambda x: x["features"]["concepts"]):
            value = language["features"][args.feature]
            color = CMAP[args.colormap][value]
            values.add(value)
            try:
                ax.plot(
                        language["longitude"],
                        language["latitude"],
                        marker="o",
                        color=color,
                        zorder=10,
                        markersize=args.markersize
                        )
            except TypeError:
                args.log.warning(language.dataset, language.name)
        
        for v in values:
            plt.plot(-100, -100, "o", markersize=10, color=CMAP[args.colormap][v], label=str(v))
        plt.legend(loc=4)

    plt.savefig(args.filename, dpi=900)

