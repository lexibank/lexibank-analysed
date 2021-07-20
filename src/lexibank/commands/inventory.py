"""
Compute Inventory Statistics from LexiCore.
"""
from cltoolkit import Wordlist
import json
from cltoolkit.features.collection import feature_data, FeatureCollection
import lexibank
from pyclts import CLTS
from collections import defaultdict
from matplotlib import pyplot as plt


def register(parser):
    parser.add_argument(
        "--datadir",
        help="destination of your datasets",
        action="store",
        default="datasets"
        )
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
        lexicore = Wordlist(
                datasets=lexibank.lexicore_data(args.datadir),
                ts=args.clts.bipa
                )
    else:
        lexicore = Wordlist(
                datasets=lexibank.lexicore_data(args.datadir)[:args.sample],
                ts=args.clts.bipa
                )

    fc = FeatureCollection.from_data(feature_data())
    data = {}
    warnings = {}
    sounds = defaultdict(int)
    sounds_in_words = defaultdict(int)
    for language in lexicore.languages:
        if language.name == None or language.name == "None":
            warnings[language.id] = language
        else:
            args.log.info("{0}-{1}".format(language.name,
                fc.features["SyllableStructure"](language)))
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
    
    with open("lexicore.json", "w") as f:
        json.dump(data, f, indent=2)
    with open("sounds.json", "w") as f:
        json.dump([sounds, sounds_in_words], f, indent=2)
    if args.plot:
        fig = plt.Figure()
        with open("sounds.tsv", "w") as f:
            f.write("Sound\tCLTS Name\tFrequencyInVarieties\tFrequencyInWords\n")
            for sound in sounds:
                f.write("{0}\t{1}\t{2}\t{3}\n".format(
                    sound, args.clts.bipa[sound].name, sounds[sound],
                    sounds_in_words[sound]))
                plt.plot(sounds[sound], sounds_in_words[sound], "o",
                        color="0.75", markersize=0.5)
                plt.text(sounds[sound], sounds_in_words[sound], sound,
                        color="black", size=2)
        plt.xlabel("occurrences per language variety")
        plt.ylabel("individual occurrences in words")
        plt.savefig(args.filename)
    args.log.info("Calculated features for {0} languages and found {1} sounds".format(len(data), len(sounds)))
