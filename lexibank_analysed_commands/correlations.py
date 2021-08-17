"""
Run Correlation Tests on the Results
"""
from statistics import median
from collections import defaultdict as dd

from tqdm import tqdm as progressbar
from scipy.stats import spearmanr
from pycldf import Dataset, iter_datasets
from pyclts import CLTS
from cltoolkit.models import Language, Inventory
from cltoolkit.features import FEATURES
from cldfzenodo import Record
from clldutils.clilib import Table, add_format

from cldfbench_lexibank_analysed import Dataset as LB, CLTS_2_1


def register(parser):
    add_format(parser)


def get_cldf_dataset(doi, directory):
    if directory.exists():
        return next(iter_datasets(directory))
    return Dataset.from_metadata(Record.from_doi(doi).download_dataset(directory))


def run(args):
    lba = LB()

    args.log.info('Loading data ...')
    clts = CLTS(lba.raw_dir / CLTS_2_1[1])
    clts2phoible = clts.transcriptiondata_dict["phoible"]

    # WALS Online v2020.1
    wals = get_cldf_dataset('10.5281/zenodo.4683137', lba.raw_dir / 'wals')
    # PHOIBLE 2.0.1
    phoible = get_cldf_dataset('10.5281/zenodo.2677911', lba.raw_dir / 'phoible')

    lexicore = Dataset.from_metadata(lba.cldf_dir / "phonology-metadata.json")

    by_gcode = dd(lambda: dd(lambda: dd(lambda: dd(dict))))

    args.log.info('... LexiCore ...')
    lexicorekeys = {lg.id: lg for lg in lexicore.objects("LanguageTable")}

    for value in lexicore.objects("ValueTable"):
        if lexicorekeys[value.cldf.languageReference].cldf.glottocode:
            lg = lexicorekeys[value.cldf.languageReference]
            by_gcode[lg.cldf.glottocode]["lexicore"][lg.id][value.cldf.parameterReference] = \
                value.cldf.value

    args.log.info('... PHOIBLE ...')
    phoiblekeys = {lg.id: lg for lg in phoible.objects("LanguageTable")}
    phoibledata = dd(lambda: dd(list))

    for value in phoible.objects("ValueTable"):
        language = value.cldf.languageReference
        contribution = value.data["Contribution_ID"]
        phoibledata[language][contribution].extend([
            clts2phoible.grapheme_map.get(value.cldf.value, "?")])

    for gcode in progressbar(phoibledata, desc='extracting PHOIBLE inventories'):
        for lid, sounds in phoibledata[gcode].items():
            if not "?" in sounds:        
                language = Language(
                    id=lid,
                    data=phoiblekeys[gcode].data,
                    obj=phoiblekeys[gcode].cldf,
                    dataset="phoible")
                language.sound_inventory = Inventory.from_list(clts.bipa, *sounds)
                by_gcode[gcode]["phoible"][lid] = language

    args.log.info('... WALS ...')
    walskeys = {lg.id: lg for lg in wals.objects("LanguageTable")}
    for value in wals.objects("ValueTable"):
        if walskeys[value.cldf.languageReference].cldf.glottocode:
            lg = walskeys[value.cldf.languageReference]
            by_gcode[lg.cldf.glottocode]["wals"][lg.id][value.cldf.parameterReference] = \
                value.cldf.value
    args.log.info('... done')

    features = [
        ("1A", "ConsonantSize", FEATURES["ConsonantSize"], int),
        ("2A", "VowelQualitySize", FEATURES["VowelQualitySize"], int),
        ("3A", "CVQualityRatio", FEATURES["CVQualityRatio"], float),
        ("4A", "PlosiveFricativeVoicing", FEATURES["PlosiveFricativeVoicing"], int),
        ("5A", "PlosiveVoicingGaps", FEATURES["PlosiveVoicingGaps"], int),
    ]

    args.log.info('Computing correlations ...')
    comparisons = {row[0]: [] for row in features}
    with Table(args, "Feature", "WALS/LexiCore", "WALS/PHOIBLE", "LexiCore/PHOIBLE", "N") as table:
        for gcode, dsets in by_gcode.items():
            if len(dsets) == 3:
                for d1, d2, d3, convert in features:
                    wals_values = [
                        convert(vals[d1]) for vals in dsets["wals"].values() if vals.get(d1)]
                    lexicore_values = [
                        convert(vals[d2]) for vals in dsets["lexicore"].values() if vals.get(d2)]
                    phoible_values = [d3(vals) for vals in dsets["phoible"].values()]

                    if wals_values and lexicore_values and phoible_values:
                        comparisons[d1].append([
                            median(wals_values), median(lexicore_values), median(phoible_values)])
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
