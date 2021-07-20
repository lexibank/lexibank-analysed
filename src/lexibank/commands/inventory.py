"""
Compute Inventory Statistics from LexiCore.
"""
from collections import defaultdict

from cltoolkit import Wordlist
from cltoolkit.features.collection import feature_data, FeatureCollection
from matplotlib import pyplot as plt
from cldfbench.cli_util import add_catalog_spec
from clldutils import jsonlib
from csvw.dsv import UnicodeWriter

import lexibank


def register(parser):
    lexibank.add_datadir(parser)
    add_catalog_spec(parser, 'clts')
    parser.add_argument(
        "--sample",
        help="restrict plots to the sample",
        action="store",
        type=int,
        default=0
    )
    parser.add_argument(
        "--plot",
        help="plot the data",
        action="store_true",
        default=False
    )
    parser.add_argument(
        "--filename",
        help="plot the files",
        action="store",
        default="plots/sounds.pdf"
    )


def run(args):
    if not args.sample:
        lexicore = Wordlist(datasets=lexibank.lexicore_data(args.datadir), ts=args.clts.api.bipa)
    else:
        lexicore = Wordlist(
            datasets=lexibank.lexicore_data(args.datadir)[:args.sample], ts=args.clts.api.bipa)

    fc = FeatureCollection.from_data(feature_data())
    data = {}
    warnings = {}
    sounds = defaultdict(int)
    sounds_in_words = defaultdict(int)
    for language in lexicore.languages:
        if language.name == None or language.name == "None":
            warnings[language.id] = language
        else:
            args.log.info(
                "{0}-{1}".format(language.name, fc.features["SyllableStructure"](language)))
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
                for sound in language.sound_inventory.segments:
                    sounds[sound.obj.s] += 1
                    sounds_in_words[sound.obj.s] += len(sound.occs)
    
    jsonlib.dump(data, 'lexicore.json', indent=2)
    jsonlib.dump([sounds, sounds_in_words], 'sounds.json', indent=2)
    if args.plot:
        _ = plt.Figure()
        with UnicodeWriter('sounds.tsv', delimiter='\t') as w:
            w.writerow(["Sound", "CLTS Name", "FrequencyInVarieties", "FrequencyInWords"])
            for sound in sounds:
                w.writerow([
                    sound,
                    args.clts.bipa[sound].name,
                    sounds[sound],
                    sounds_in_words[sound]])
                plt.plot(sounds[sound], sounds_in_words[sound], "o", color="0.75", markersize=0.5)
                plt.text(sounds[sound], sounds_in_words[sound], sound, color="black", size=2)
        plt.xlabel("occurrences per language variety")
        plt.ylabel("individual occurrences in words")
        plt.savefig(args.filename)
    args.log.info("Calculated features for {0} languages and found {1} sounds".format(len(data), len(sounds)))
