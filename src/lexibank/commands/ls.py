"""
List data and make major statistics.
"""
import lexibank
from cltoolkit import Wordlist
from cltoolkit.util import datasets_by_id
from collections import defaultdict
from pathlib import Path
from pycldf import Dataset
from clldutils.clilib import Table, add_format

def register(parser):
    add_format(parser, default='pipe')
    parser.add_argument(
        "--datadir",
        help="point to lexibank datafiles",
        action="store",
        default="datasets"
    )


def run(args):

    datasets = lexibank.lexibank_data()
    
    stats = {
            "LexiCore": {
                "datasets": 0,
                "glottocodes": defaultdict(list),
                "doculects": 0,
                "words": 0,
                "concepts": defaultdict(list),
                },
            "ClicsCore": {
                "datasets": 0,
                "glottocodes": defaultdict(list),
                "doculects": 0,
                "words": 0,
                "concepts": defaultdict(list),
                },
            "CogCore": {
                "datasets": 0,
                "glottocodes": defaultdict(list),
                "doculects": 0,
                "words": 0,
                "concepts": defaultdict(list),
                },
            "ProtoCore": {
                "datasets": 0,
                "glottocodes": defaultdict(list),
                "doculects": 0,
                "words": 0,
                "concepts": defaultdict(list),
                }
            }
    
    for row in datasets:
        args.log.info("analyzing {0}".format(row["Dataset"]))
        wl = None
        for key in stats:
            if row[key].strip() == "x":
                wl = wl or Wordlist(datasets=[Dataset.from_metadata(
                    Path(args.datadir, row["Dataset"], "cldf",
                    "cldf-metadata.json"))])
                stats[key]["datasets"] += 1
                stats[key]["doculects"] += len(wl.languages)
                stats[key]["words"] += len(wl.forms)
                for language in wl.languages:
                    if language.glottocode:
                        stats[key]["glottocodes"][language.glottocode] += [language]
                        for concept in language.concepts:
                            stats[key]["concepts"][concept.id] += [concept]
    table = []
    with Table(args, "Collection", "Glottocodes", "Doculects", "Concepts",
            "Word Forms") as table:
        for stat, vals in stats.items():
            table.append([
                        stat, vals["datasets"], 
                        len(vals["glottocodes"]),
                        vals["doculects"], 
                        len(vals["concepts"]),
                        vals["words"]
                        ])
        
