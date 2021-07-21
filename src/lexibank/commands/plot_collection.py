"""
Plot the LexiCore data to a Map.
"""
import json

import cartopy.crs as ccrs
import matplotlib.pyplot as plt

from lexibank.cartopy import *


def register(parser):
    parser.add_argument(
        '--datafile',
        help='location of lexicore dataset file',
        action='store',
        default="lexicore.json"
    )
    parser.add_argument(
        '--filename',
        help="name for the file to store",
        action="store",
        default="plot.pdf"
    )


def run(args):
    data = json.load(open(args.datafile))
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
    plt.savefig(args.filename, dpi=900)
