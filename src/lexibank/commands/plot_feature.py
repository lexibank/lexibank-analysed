"""
Plot Continuous Phonological Features to a Map.
"""
import json

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np

from cltoolkit.features.collection import FeatureCollection, feature_data

from lexibank.cartopy import LAND, OCEAN, COASTLINE, BORDERS, LAKES, RIVERS, CMAP


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
    parser.add_argument(
        "--dpi",
        help="DPI for the plot",
        action="store",
        type=int,
        default=900
    )


def run(args):
    data = json.load(open(args.datafile))

    # get feature collection and feature data
    fc = FeatureCollection.from_data(feature_data())
    
    # check if feature exists
    features = list(data.values())[0]["features"]
    if not args.feature in features:
        raise ValueError("feature not available in data")
    elif not args.feature in [f.id for f in fc.features]:
        raise ValueError("feature not described in cltoolkit")

    # retrieve feature data
    feature = fc.features[args.feature]

    fig = plt.figure(figsize=[20, 10])
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

    ax.coastlines(resolution='50m')
    ax.add_feature(LAND)
    ax.add_feature(OCEAN)
    ax.add_feature(COASTLINE)
    ax.add_feature(BORDERS, linestyle=':')
    ax.add_feature(LAKES, alpha=0.5)
    ax.add_feature(RIVERS)

    # check for continuous features
    if feature.type in ["float", "integer"]:
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
                args.log.warning("Skipping {0} / {1}".format(language.dataset, language.name))
        
        cbar = plt.colorbar(
            cm.ScalarMappable(norm=None, cmap=colormap),
            ax=ax,
            orientation="horizontal",
            shrink=0.4,
            ticks=[0, 0.5, 1]
        )
        cbar.ax.set_xticklabels([
            str(round(targets[0], 2)),
            str(round((targets[5]+targets[6])/2, 2)),
            str(round(targets[-1], 2))])

    elif feature.type == "categorical":
        # get dictionary of feature categories for the legend
        categories = {int(k): v for k, v in feature.categories.items()}
        colormap = CMAP.get(args.colormap, CMAP["base"])
        values = set()
        for language in sorted(data.values(), key=lambda x: x["features"]["concepts"]):
            value = language["features"][args.feature]
            color = colormap[value]
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
            plt.plot(-100, -100, "o", markersize=10, color=colormap[v], label=categories[v])
        plt.legend(loc=4)
    elif feature.type == "bool":
        colormap = CMAP.get("bool", {True: "crimson", False: "CornFlowerBlue", None: "0.5"})
        categories = {{"true": True, "false": False, "null": None}[k]: v for k, v in feature.categories.items()}
        for language in sorted(data.values(), key=lambda x: x["features"]["concepts"]):
            value = language["features"][args.feature]
            color = colormap[value]
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
        for v in [True, False, None]:
            plt.plot(-100, -100, "o", markersize=10, color=colormap[v], label=categories[v])
        plt.legend(loc=4)

    plt.savefig(args.filename, dpi=args.dpi)
    args.log.info('output saved to {}'.format(args.filename))
