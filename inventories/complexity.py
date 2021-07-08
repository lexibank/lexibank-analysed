from cltoolkit import Wordlist
from cltoolkit.util import datasets_by_id
from pyclts import CLTS
from cldfcatalog import Config
from pycldf import Dataset
from pyconcepticon import Concepticon

from cartopy import *
import cartopy.io.img_tiles as cimgt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
from cltoolkit.features.collection import feature_data, FeatureCollection

from matplotlib import cm
import cartopy.feature as cfeature
from cartopy.feature import NaturalEarthFeature
import numpy as np

from sys import argv

# load the feature collection
fc = FeatureCollection.from_data(feature_data())

clts = CLTS(Config.from_file().get_clone("clts"))
concepticon = Concepticon(Config.from_file().get_clone("concepticon"))

# Cartopy configuration
COLORS = {'land': np.array((240, 240, 220)) / 256.,
          'land_alt1': np.array((220, 220, 220)) / 256.,
          'water': np.array((152, 183, 226)) / 256.}


LAND = NaturalEarthFeature('physical', 'land', '50m',
                           edgecolor='face',
                           facecolor=COLORS['land'], zorder=-1)

BORDERS = NaturalEarthFeature('cultural', 'admin_0_boundary_lines_land',
                              '50m', edgecolor='black', facecolor='none')
"""Small scale (1:110m) country boundaries."""

STATES = NaturalEarthFeature('cultural', 'admin_1_states_provinces_lakes',
                             '50m', edgecolor='black', facecolor='none')
"""Small scale (1:110m) state and province boundaries."""

COASTLINE = NaturalEarthFeature('physical', 'coastline', '50m',
                                edgecolor='black', facecolor='none')
"""Small scale (1:110m) coastline, including major islands."""


LAKES = NaturalEarthFeature('physical', 'lakes', '50m',
                            edgecolor='face',
                            facecolor=COLORS['water'])
"""Small scale (1:110m) natural and artificial lakes."""


LAND = NaturalEarthFeature('physical', 'land', '50m',
                           edgecolor='face',
                           facecolor=COLORS['land'], zorder=-1)
"""Small scale (1:110m) land polygons, including major islands."""


OCEAN = NaturalEarthFeature('physical', 'ocean', '50m',
                            edgecolor='face',
                            facecolor=COLORS['water'], zorder=-1)
"""Small scale (1:110m) ocean polygons."""


RIVERS = NaturalEarthFeature('physical', 'rivers_lake_centerlines', '50m',
                             edgecolor=COLORS['water'],
                             facecolor='none')


## get the datasets
lexicore = Wordlist(datasets=datasets_by_id(
    *[x.strip() for x in open("datasets.txt").readlines()],
    path="data/*/cldf/cldf-metadata.json"))

if "fig1" in argv:
    fig = plt.figure(figsize=[20, 10])
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
    #ax.set_extent(
    
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
    
    for language in sorted(lexicore.languages, key=lambda x: len(x.concepts), reverse=True):
        if len(language.concepts) > 1000:
            color = "green"
            scaler = 5,
        elif len(language.concepts) > 500:
            color = "darkgreen"
            scaler = 3
        elif len(language.concepts) >= 200:
            color = "orange"
            scaler = 2
        elif len(language.concepts) >= 100:
            color = "yellow"
            scaler = 1
        else:
            color = "red"
            scaler = 0.5
        
        try:
            ax.plot(
                    float(language.longitude),
                    float(language.latitude),
                    marker="o",
                    color=color,
                    markersize=markersize*scaler
                    )
        except TypeError:
            print(language.dataset, language.name)
    plt.savefig("lexibank-clics-data.pdf", dpi=900)

if "complexity" in argv:
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
    
    for language in sorted(lexicore.languages, key=lambda x: len(x.concepts), reverse=True):
        comp = 10 * fc.features["SyllableStructure"](language) / 100
        color = cm.jet(comp)
        print(language.name, comp)
        
        try:
            ax.plot(
                    float(language.longitude),
                    float(language.latitude),
                    marker="o",
                    color=color,
                    zorder=10,
                    markersize=8
                    )
        except TypeError:
            print(language.dataset, language.name)
    plt.savefig("syllable-complexity.pdf", dpi=900)


