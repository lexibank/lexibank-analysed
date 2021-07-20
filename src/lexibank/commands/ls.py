"""
List data and make major statistics.
"""
import pathlib
import collections

import lexibank
from cltoolkit import Wordlist
from pycldf import Dataset
from clldutils.clilib import Table, add_format


def register(parser):
    add_format(parser, default='pipe')
    lexibank.add_datadir(parser)


def run(args):

    datasets = lexibank.lexibank_data()
    
    stats = collections.OrderedDict({
            "LexiCore": {
                "datasets": 0,
                "glottocodes": collections.defaultdict(list),
                "doculects": 0,
                "words": 0,
                "concepts": collections.defaultdict(list),
                },
            "ClicsCore": {
                "datasets": 0,
                "glottocodes": collections.defaultdict(list),
                "doculects": 0,
                "words": 0,
                "concepts": collections.defaultdict(list),
                },
            "CogCore": {
                "datasets": 0,
                "glottocodes": collections.defaultdict(list),
                "doculects": 0,
                "words": 0,
                "concepts": collections.defaultdict(list),
                },
            "ProtoCore": {
                "datasets": 0,
                "glottocodes": collections.defaultdict(list),
                "doculects": 0,
                "words": 0,
                "concepts": collections.defaultdict(list),
                },
            "Total": {
                "datasets": 0,
                "glottocodes": collections.defaultdict(list),
                "doculects": 0,
                "words": 0,
                "concepts": collections.defaultdict(list),
                }
            })
    
    for row in datasets:
        args.log.info("analyzing {0}".format(row["Dataset"]))
        wl = None
        for key in ["LexiCore", "CogCore", "ClicsCore", "ProtoCore"]:
            if row[key].strip() == "x":
                wl = wl or Wordlist(datasets=[Dataset.from_metadata(
                    pathlib.Path(args.datadir, row["Dataset"], "cldf", "cldf-metadata.json"))])
                stats[key]["datasets"] += 1
                stats[key]["doculects"] += len(wl.languages)
                stats[key]["words"] += len(wl.forms)
                for language in wl.languages:
                    if language.glottocode:
                        stats[key]["glottocodes"][language.glottocode] += [language]
                        for concept in language.concepts:
                            stats[key]["concepts"][concept.id] += [concept]
        if row["LexiCore"].strip() == "x" or row["ClicsCore"].strip("") == "x":
            stats["Total"]["datasets"] += 1
            stats[key]["doculects"] += len(wl.languages)
            stats[key]["words"] += len(wl.forms)
            for language in wl.languages:
                if language.glottocode:
                    stats["Total"]["glottocodes"][language.glottocode] += [language]
                    for concept in language.concepts:
                        stats["Total"]["concepts"][concept.id] += [concept]

    with Table(args, "Collection", "Glottocodes", "Doculects", "Concepts", "Word Forms") as table:
        for stat, vals in stats.items():
            table.append([
                stat, vals["datasets"],
                len(vals["glottocodes"]),
                vals["doculects"],
                len(vals["concepts"]),
                vals["words"]
            ])
