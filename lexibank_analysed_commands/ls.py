"""
List data and make major statistics.
"""
import collections

from cltoolkit import Wordlist
from pycldf import Dataset
from clldutils.clilib import Table, add_format

from cldfbench_lexibank_analysed import Dataset as DS


def register(parser):
    add_format(parser, default='pipe')


def run(args):
    ds = DS()
    datasets = ds.etc_dir.read_csv('lexibank.tsv', delimiter='\t', dicts=True)

    stats = collections.OrderedDict({
        "LexiCore": {
            "datasets": 0,
            "glottocodes": set(),
            "doculects": 0,
            "words": 0,
            "concepts": set(),
        },
        "ClicsCore": {
            "datasets": 0,
            "glottocodes": set(),
            "doculects": 0,
            "words": 0,
            "concepts": set(),
        },
        "CogCore": {
            "datasets": 0,
            "glottocodes": set(),
            "doculects": 0,
            "words": 0,
            "concepts": set(),
        },
        "ProtoCore": {
            "datasets": 0,
            "glottocodes": set(),
            "doculects": 0,
            "words": 0,
            "concepts": set(),
        },
        "Total": {
            "datasets": 0,
            "glottocodes": set(),
            "doculects": 0,
            "words": 0,
            "concepts": set(),
        }
    })

    for row in datasets:
        args.log.info("analyzing {0}".format(row["Dataset"]))
        wl = None
        incoll = False
        for key in ["LexiCore", "CogCore", "ClicsCore", "ProtoCore"]:
            if row[key].strip() == "x":
                incoll = True
                wl = wl or Wordlist(datasets=[Dataset.from_metadata(
                    ds.raw_dir / row["Dataset"] / "cldf" / "cldf-metadata.json")])
                stats[key]["datasets"] += 1
                stats[key]["doculects"] += len(wl.languages)
                stats[key]["words"] += len(wl.forms)
                for language in wl.languages:
                    if language.glottocode:
                        stats[key]["glottocodes"].add(language.glottocode)
                        for concept in language.concepts:
                            stats[key]["concepts"].add(concept.id)
        if incoll:
            stats["Total"]["datasets"] += 1
            stats[key]["doculects"] += len(wl.languages)
            stats[key]["words"] += len(wl.forms)
            for language in wl.languages:
                if language.glottocode:
                    stats["Total"]["glottocodes"].add(language.glottocode)
                    for concept in language.concepts:
                        stats["Total"]["concepts"].add(concept.id)

    with Table(args, "Collection", "Datasets", "Glottocodes", "Doculects", "Concepts", "Word Forms") as table:
        for stat, vals in stats.items():
            table.append([
                stat,
                vals["datasets"],
                len(vals["glottocodes"]),
                vals["doculects"],
                len(vals["concepts"]),
                vals["words"]
            ])
