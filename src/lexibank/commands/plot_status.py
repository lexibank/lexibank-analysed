"""
Plot the endangerment information status data to a Map.
"""
import json

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
from matplotlib import cm

from pyglottolog import Glottolog

from lexibank.cartopy import *



def register(parser):
    parser.add_argument(
        '--lexicore',
        help='location of lexicore dataset file',
        action='store',
        default="lexicore.json"
    )
    parser.add_argument(
        '--clics',
        help='location of lexicore dataset file',
        action='store',
        default="clics.json"
    )

    parser.add_argument(
        '--filename',
        help="name for the file to store",
        action="store",
        default="plot.pdf"
        )
    parser.add_argument(
        "--markersize",
        help="select size of marker file",
        type=float,
        action="store",
        default=3.0
        )
    parser.add_argument(
        "--colormap",
        help="select size of marker file",
        action="store",
        default="jet"
        )
    parser.add_argument(
        "--glottolog",
        help="select size of marker file",
        action="store",
        default="./"
        )


def run(args):
    dataA = json.load(open(args.lexicore))
    dataB = json.load(open(args.clics))
    data = {}
    for language, vals in dataA.items():
        data[language] = vals
        if language in dataB:
            data[language]["type"] = "3"
        else:
            data[language]["type"] = "1"
    for language, vals in dataB.items():
        if language in dataA:
            pass
        else:
            data[language] = vals
            data[language]["type"] = "2"

    colormap = getattr(cm, args.colormap)

    fig = plt.figure(figsize=[20, 10])
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    
    ax.coastlines(resolution='50m')
    ax.add_feature(LAND)
    ax.add_feature(OCEAN)
    ax.add_feature(COASTLINE)
    ax.add_feature(BORDERS, linestyle=':')
    ax.add_feature(LAKES, alpha=0.5)
    ax.add_feature(RIVERS)
    data_crs = ccrs.PlateCarree()
    vals = []
    for language in data.values():
        vals += [language["features"]["concepts"]]
    minv, maxv = min(vals), max(vals)
    targets = np.linspace(minv, maxv, 100)
    conv = {}
    for val in vals:
        for i, v in enumerate(targets):
            if v <= val:
                conv[val] = colormap(0.01*i)
    
    # load glottolog data
    glottolog = {g.id: g for g in Glottolog(args.glottolog).languoids()}

    # endangerment status
    endangerment = {
            "safe": "green",
            "threatened": "crimson",
            "shifting": "orange",
            "critical": "red",
            "vulnerable": "yellow",
            "extinct": "black",
            "definite": "gray",
            "severe": "goldenrod"
            }

    for language in sorted(data.values(), key=lambda x: x["features"]["concepts"]):
        zorder = language["features"]["concepts"]
        try:
            languoid = glottolog[language["glottocode"]]
            if languoid.endangerment:
                color = endangerment[languoid.endangerment.status.id]
            else:
                color = "white"
        except:
            color = "white"

        wedgeA = Wedge( 
            [language["longitude"], language["latitude"]], args.markersize,
            0, 360, facecolor=color, transform=data_crs, zorder=zorder,
            edgecolor="black", alpha=0.75
            )
        ax.add_patch(wedgeA)

    
    plt.plot(-100, -100, "o", markersize=10, color="Blue", label="> 1000 concepts")
    
    cbar = plt.colorbar(cm.ScalarMappable(norm=None, cmap=colormap), ax=ax,
                orientation="horizontal", shrink=0.4,
                ticks=[0, 0.25, 0.5, 0.75, 1]
                )
    cbar.ax.set_xticklabels(
                [   str(int(round(targets[0], 0))), 
                    str(int(round(targets[25], 0))),
                    str(int(round(targets[50], 0))),
                    str(int(round(targets[75], 0))),
                    str(int(round(targets[-1], 0)))]
                )
    
    plt.savefig(args.filename, dpi=900)
