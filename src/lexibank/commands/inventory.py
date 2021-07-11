"""
Compute Inventory Statistics from LexiCore.
"""
from cltoolkit import Wordlist
import json
from cltoolkit.features.collection import feature_data, FeatureCollection
import lexibank


def run(args):
    lexicore = Wordlist(datasets=lexibank.lexicore_data())
    fc = FeatureCollection.from_data(feature_data())
    data = {}
    warnings = {}
    for language in lexicore.languages:
        if language.name == None or language.name == "None":
            warnings[language.id] = language
        else:
            print(language.name, fc.features["SyllableStructure"](language))
            if language.latitude and len(language.bipa_forms) >= 80:
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
                            "bipa_forms": len(language.bipa_forms),
                            "senses": len(language.senses)
                            }
                        }
                for feature in fc.features:
                    if feature.module.endswith("phonology"):
                        value = feature(language)
                        data[language.id]["features"][feature.id] = value
    
    with open("lexicore.json", "w") as f:
        json.dump(data, f)
    print(len(data))
