import numpy as np
from cartopy.feature import NaturalEarthFeature

# Cartopy configuration
COLORS = {'land': np.array((240, 240, 220)) / 256.,
          'land_alt1': np.array((220, 220, 220)) / 256.,
          'water': np.array((152, 183, 226)) / 256.}

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

"""
Colormaps from ColorBrewer2.org
"""
CMAP = {
        "base": {
            1: "#a6cee3",
            2: "#1f78b4",
            3: "#b2df8a",
            4: "#33a02c",
            5: "#fb9a99",
            6: "#e31a1c",
            7: "#fdbf6f",
            8: "#ff7f00",
            9: "#cab2d6",
            10: "#6a3d9a",
            11: "#ffff99",
            12: "#b15928"
        },
        "SequentialOrRd3": {
            1: "#fee8c8",
            2: "#fdbb84",
            3: "#e34a33"
            },
        "SequentialOrRd4": {
            1: "#fef0d9",
            2: "#fdcc8a",
            3: "#fc8d59",
            4: "#d7301f"
            },
        "SequentialOrRd5": {
            1: "#fef0d9",
            2: "#fdcc8a",
            3: "#fc8d59",
            4: "#e34a33",
            5: "#b30000",
            },
        "SequentialOrRd6": {
            1: "#fef0d9",
            2: "#fdd49e",
            3: "#fdbb84",
            4: "#fc8d59",
            5: "#e34a33",
            6: "#b30000"
            },
        "Qualitative6": {
            1: "#e41a1c",
            2: "#377eb8",
            3: "#4daf4a",
            4: "#984ea3",
            5: "#ff7f00",
            6: "#ffff33"
            }
}
