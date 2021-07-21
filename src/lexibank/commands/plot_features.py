"""
Plot Two Features to a Map.
"""
import json

import cartopy.crs as ccrs
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge
from cltoolkit.features.collection import FeatureCollection, feature_data

from lexibank.cartopy import LAND, OCEAN, COASTLINE, BORDERS, LAKES, RIVERS


def register(parser):
    parser.add_argument(
        '--datafile',
        help='location of dataset file in JSON',
        action='store',
        default="lexicore.json"
    )
    parser.add_argument(
        "--featureA",
        help="select the first feature you want to plot",
        action="store",
        default="ArmAndHand"
    )
    parser.add_argument(
        "--featureB",
        help="select the second feature you want to plot",
        action="store",
        default="LegAndFoot"
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
        "--colormapA",
        help="select the first colormap to be used",
        action="store",
        default="base"
    )
    parser.add_argument(
        "--colormapB",
        help="select the second colormap to be used",
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
    if not args.featureA in features or not args.featureB in features:
        raise ValueError("features not available in data")
    elif not args.featureA in [f.id for f in fc.features] or not \
            args.featureB in [f.id for f in fc.features]:
        raise ValueError("features not described in cltoolkit")

    # retrieve feature data
    featureA = fc.features[args.featureA]
    featureB = fc.features[args.featureB]

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

    if featureA.type == "bool" and featureB.type == "bool":
        colormapA = {True: "crimson", False: "white", None: "0.5"}
        colormapB = {True: "cornflowerblue", False: "white", None: "0.5"}

        categoriesA = {{"true": True, "false": False, "null": None}[k]: v for
                k, v in featureA.categories.items()}
        categoriesB = {{"true": True, "false": False, "null": None}[k]: v for
                k, v in featureB.categories.items()}

        for language in sorted(data.values(), key=lambda x: x["features"]["concepts"]):
            valueA = language["features"][args.featureA]
            colorA = colormapA[valueA]
            valueB = language["features"][args.featureB]
            colorB = colormapB[valueB]

            if valueA and valueB:
                zorder = 60
            elif valueA or valueB:
                zorder = 50
            elif valueA is not None and valueB is not None:
                zorder = 40
            elif valueA is not None or valueB is not None:
                zorder = 30
            else:
                zorder = 20

            try:
                wedgeAB = Wedge(
                    [language["longitude"], language["latitude"]],
                    args.markersize,
                    0,
                    360,
                        facecolor="white",
                        transform=data_crs,
                        zorder=zorder-5,
                        edgecolor="black",
                        alpha=0.75
                )
                wedgeA = Wedge(
                    [language["longitude"], language["latitude"]],
                    args.markersize,
                    90,
                    270,
                    facecolor=colorA,
                    transform=data_crs,
                    zorder=zorder,
                    edgecolor="black",
                )
                wedgeB = Wedge(
                    [language["longitude"], language["latitude"]],
                    args.markersize,
                    270,
                    90,
                    facecolor=colorB,
                    transform=data_crs,
                    zorder=zorder,
                    edgecolor="black",
                )
                ax.add_patch(wedgeAB)
                ax.add_patch(wedgeA)
                ax.add_patch(wedgeB)
            except TypeError:
                args.log.warning(language.dataset, language.name)
        for v in [True, None]:
            plt.plot(-100, -100, "o", markersize=10, color=colormapA[v], label=categoriesA[v])
        plt.plot(-100, -100, "o", markersize=10, color=colormapB[True], label=categoriesB[True])
        plt.legend(loc=4)
    else:
        raise ValueError("only available for boolean features so far")

    plt.savefig(args.filename, dpi=args.dpi)
    args.log.info('output saved to {}'.format(args.filename))
