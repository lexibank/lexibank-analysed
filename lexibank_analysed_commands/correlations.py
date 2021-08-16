"""
Run Correlation Tests on the Results
"""
from statistics import median

from pycldf import Dataset
from collections import defaultdict as dd
from tqdm import tqdm as progressbar
from scipy.stats import spearmanr
from pyclts import CLTS
from cldfcatalog import Config
from cltoolkit.features import FEATURES
from cldfzenodo import Record
from clldutils.clilib import Table, add_format

from cldfbench_lexibank_analysed import Dataset as LB
from cltoolkit.models import Language, Inventory


def register(parser):
    add_format(parser)


def run(args):
    lba = LB()
    
    clts = CLTS(Config.from_file().get_clone("clts"))
    clts2phoible = clts.transcriptiondata_dict["phoible"]

    # WALS Online v2020.1
    wmd = Record.from_doi('10.5281/zenodo.4683137').download_dataset(lba.raw_dir / 'wals')
    # PHOIBLE 2.0.1
    pmd = Record.from_doi('10.5281/zenodo.2677911').download_dataset(lba.raw_dir / 'phoible')

    phoible = Dataset.from_metadata(pmd)
    wals = Dataset.from_metadata(wmd)
    lexicore = Dataset.from_metadata(lba.cldf_dir / "phonology-metadata.json")

    by_gcode = dd(lambda: dd(lambda: dd(lambda: dd(dict))))
    
    # transform wals data
    lexicorekeys = {lg.id: lg for lg in lexicore.objects("LanguageTable")}

    for value in progressbar(lexicore.objects("ValueTable"), desc="loading lexicore data2"):
        if lexicorekeys[value.cldf.languageReference].cldf.glottocode:
            lg = lexicorekeys[value.cldf.languageReference]
            by_gcode[lg.cldf.glottocode]["lexicore"][lg.id][value.cldf.parameterReference] = \
                value.cldf.value

    # transform phoible data
    phoiblekeys = {lg.id: lg for lg in phoible.objects("LanguageTable")}
    phoibledata = dd(lambda: dd(list))

    for value in progressbar(phoible.objects("ValueTable"), desc="phoible data2"):
        language = value.cldf.languageReference
        contribution = value.data["Contribution_ID"]
        phoibledata[language][contribution].extend([
            clts2phoible.grapheme_map.get(value.cldf.value, "?")])

    for gcode in progressbar(phoibledata):
        for lid, sounds in phoibledata[gcode].items():
            if not "?" in sounds:        
                language = Language(
                    id=lid,
                    data=phoiblekeys[gcode].data,
                    obj=phoiblekeys[gcode].cldf,
                    dataset="phoible")
                language.sound_inventory = Inventory.from_list(clts.bipa, *sounds)
                by_gcode[gcode]["phoible"][lid] = language

    # transform wals data
    walskeys = {lg.id: lg for lg in wals.objects("LanguageTable")}
    for value in progressbar(wals.objects("ValueTable"), desc="loading wals data2"):
        if walskeys[value.cldf.languageReference].cldf.glottocode:
            lg = walskeys[value.cldf.languageReference]
            by_gcode[lg.cldf.glottocode]["wals"][lg.id][value.cldf.parameterReference] = \
                value.cldf.value

    features = [
        ("1A", "ConsonantSize", FEATURES["ConsonantSize"], int),
        ("2A", "VowelQualitySize", FEATURES["VowelQualitySize"], int),
        ("3A", "CVQualityRatio", FEATURES["CVQualityRatio"], float),
        ("4A", "PlosiveFricativeVoicing", FEATURES["PlosiveFricativeVoicing"], int),
        ("5A", "PlosiveVoicingGaps", FEATURES["PlosiveVoicingGaps"], int),
    ]

    comparisons = {row[0]: [] for row in features}
    with Table(args, "Feature", "WALS/LexiCore", "WALS/PHOIBLE", "LexiCore/PHOIBLE", "N") as table:
        for gcode, dsets in by_gcode.items():
            if len(dsets) == 3:
                for d1, d2, d3, convert in features:
                    # start with wals
                    wals_values = []
                    for dc, values in dsets["wals"].items():
                        if values.get(d1):
                            wals_values += [convert(values[d1])]
                    lexicore_values = []
                    for dc, values in dsets["lexicore"].items():
                        if values.get(d2):
                            lexicore_values += [convert(values[d2])]
                    phoible_values = []
                    for dc, values in dsets["phoible"].items():
                        phoible_values += [d3(values)]
                    if wals_values and lexicore_values and phoible_values:
                        comparisons[d1] += [[
                            median(wals_values),
                            median(lexicore_values),
                            median(phoible_values)]]
        for d1, d2, d3, _ in features:
            p1, r1 = spearmanr([x[0] for x in comparisons[d1]], [x[1] for x in comparisons[d1]])
            p2, r2 = spearmanr([x[0] for x in comparisons[d1]], [x[2] for x in comparisons[d1]])
            p3, r3 = spearmanr([x[1] for x in comparisons[d1]], [x[2] for x in comparisons[d1]])
            table.append([
                d1,
                "{0:.2f} / {1:.2f}".format(p1, r1),
                "{0:.2f} / {1:.2f}".format(p2, r2),
                "{0:.2f} / {1:.2f}".format(p3, r3),
                len(comparisons[d1])
            ])
