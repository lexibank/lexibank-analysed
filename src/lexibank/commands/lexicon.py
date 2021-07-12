"""
Compute lexical features from the data.
"""

from cltoolkit import Wordlist
import json
from cltoolkit.features.collection import feature_data, FeatureCollection
import lexibank


def register(parser):
    parser.add_argument(
        "--datadir",
        help="destination of your datasets",
        action="store",
        default="datasets"
        )


def run(args):
    lexicore = Wordlist(datasets=lexibank.clics_data(args.datadir))
    fc = FeatureCollection.from_data(feature_data())
    data = {}
    warnings = {}
    for language in lexicore.languages:
        if language.name == None or language.name == "None":
            warnings[language.id] = language
        else:
            args.log.info(language.name, fc.features["HandAndArm"](language))
            if language.latitude and len(language.concepts) >= 250:
                data[language.id] = {
                        "name": language.name,
                        "glottocode": language.glottocode,
                        "dataset": language.dataset,
                        "latitude": float(language.latitude),
                        "longitude": float(language.longitude),
                        "subgroup": language.subgroup,
                        "family": language.family, 
                        "features": {
                            "concepts": len(language.concepts),
                            "forms": len(language.forms),
                            "senses": len(language.senses)
                            }
                        }
                for feature in fc.features:
                    if feature.module.endswith("lexicon"):
                        value = feature(language)
                        data[language.id]["features"][feature.id] = value
    
    with open("clics.json", "w") as f:
        json.dump(data, f)
    args.log.info("Calculated features for {0} languages.".format(len(data)))

