"""
Run Correlation Tests on the Results
"""
from pycldf import Dataset
from cltoolkit import Wordlist
from pathlib import Path
from cltoolkit.util import datasets_by_id
from collections import defaultdict
from tqdm import tqdm as progressbar
import random
from scipy.stats import spearmanr
from statistics import median
from itertools import combinations
from tabulate import tabulate
from pyclts import CLTS
from cldfcatalog import Config
from cltoolkit.features import FEATURES

from cldfbench_lexibank_analysed import Dataset as LB
from cltoolkit.models import Language, Inventory


def run(args):
    lba = LB()
    
    clts = CLTS(Config.from_file().get_clone("clts"))
    clts2phoible = clts.transcriptiondata_dict["phoible"]
    
    phoible = Dataset.from_metadata(lba.raw_dir / "phoible/cldf/StructureDataset-metadata.json")
    wals = Dataset.from_metadata(lba.raw_dir / "wals/cldf/StructureDataset-metadata.json")
    lexicore = Dataset.from_metadata(lba.cldf_dir / "phonology-metadata.json")
    
    
    by_gcode = defaultdict(dict)
    
    # transform wals data
    lexicorekeys = {}
    for language in progressbar(lexicore.objects("LanguageTable"), desc="loading lexcicore data"):
        if language.cldf.glottocode:
            try:
                by_gcode[language.cldf.glottocode]["lexicore"][language.id] = {}
            except KeyError:
                by_gcode[language.cldf.glottocode]["lexicore"] = {language.id: {}}
                
        lexicorekeys[language.id] = language
    for value in progressbar(lexicore.objects("ValueTable"), desc="loading lexicore data2"):
        if lexicorekeys[value.cldf.languageReference].cldf.glottocode:
            language = lexicorekeys[value.cldf.languageReference]
            by_gcode[language.cldf.glottocode]["lexicore"][
                    language.id][value.cldf.parameterReference] = value.cldf.value
    
    # transform phoible data
    phoiblekeys = {}
    phoibledata = defaultdict(dict)
    phoible_language_map = {}
    for language in progressbar(phoible.objects("LanguageTable"), desc="phoible data"):
        phoible_language_map[language.id] = language
        phoibledata[language.id] = {}
        phoiblekeys[language.id] = language
    for value in progressbar(phoible.objects("ValueTable"), desc="phoible data2"):
        language = value.cldf.languageReference
        contribution = value.data["Contribution_ID"]
        try:
            phoibledata[language][contribution] += [
                    clts2phoible.grapheme_map.get(value.cldf.value, "?")]
        except:
            phoibledata[language][contribution] = [clts2phoible.grapheme_map.get(value.cldf.value, "?")]
                                         
    for gcode in progressbar(phoibledata):
        for lid, sounds in phoibledata[gcode].items():
            if not "?" in sounds:        
                language = Language(id=lid, data=phoiblekeys[gcode].data,
                        obj=phoiblekeys[gcode].cldf, dataset="phoible")
                language.sound_inventory = Inventory.from_list(clts.bipa, *sounds)
                try:
                    by_gcode[gcode]["phoible"][lid] = language
                except KeyError:
                    by_gcode[gcode]["phoible"] = {lid: language}
    
    # transform wals data
    walskeys = {}
    for language in progressbar(wals.objects("LanguageTable"), desc="loading wals data"):
        if language.cldf.glottocode:
            try:
                by_gcode[language.cldf.glottocode]["wals"][language.id] = {}
            except KeyError:
                by_gcode[language.cldf.glottocode]["wals"] = {language.id: {}}
                
        walskeys[language.id] = language
    for value in progressbar(wals.objects("ValueTable"), desc="loading wals data2"):
        if walskeys[value.cldf.languageReference].cldf.glottocode:
            language = walskeys[value.cldf.languageReference]
            by_gcode[language.cldf.glottocode]["wals"][
                    language.id][value.cldf.parameterReference] = value.cldf.value
    
    features = [
            ("1A", "ConsonantSize", FEATURES["ConsonantSize"], int),
            ("2A", "VowelQualitySize", FEATURES["VowelQualitySize"], int),
            ("3A", "CVQualityRatio", FEATURES["CVQualityRatio"], float),
            ("4A", "PlosiveFricativeVoicing", FEATURES["PlosiveFricativeVoicing"],
                int),
            ("5A", "PlosiveVoicingGaps", FEATURES["PlosiveVoicingGaps"], int),
            ]

    #features = {
    #        "1A": "ConsonantSize",
    #        "2A": "VowelQualitySize",
    #        "3A": "CVRatio",
    #        "4A": "PlosiveFricativeVoicing",
    #        "5A": "PlosiveVoicingGaps",
    #        "6A": "UvularConsonants",
    #        "7A": "GlottalizedConsonants",
    #        "8A": "HasLaterals",
    #        #"9A": "HasEngma",
    #        "10A": "HasNasalVowels",
    #        "11A": "HasRoundedVowels",
    #        #"12A": "SyllableComplexity",
    #        "18A": "LacksCommonConsonants",
    #        "19A": "HasUncommonConsonants",
    #        }
    
    
    
    comparisons = {row[0]: [] for row in features}
    table = []
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
        p1, r1 = spearmanr(
                [x[0] for x in comparisons[d1]],
                [x[1] for x in comparisons[d1]]
                )
        p2, r2 = spearmanr(
                [x[0] for x in comparisons[d1]],
                [x[2] for x in comparisons[d1]]
                )
        p3, r3 = spearmanr(
                [x[1] for x in comparisons[d1]],
                [x[2] for x in comparisons[d1]]
                )
        table += [[
            d1,
            "{0:.2f} / {1:.2f}".format(p1, r1), 
            "{0:.2f} / {1:.2f}".format(p2, r2), 
            "{0:.2f} / {1:.2f}".format(p3, r3)
            ]]
    
    print(tabulate(table, headers=["Feature", "WALS/LexiCore", "WALS/PHOIBLE",
        "LexiCore/PHOIBLE"]))



