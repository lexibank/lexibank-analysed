from pycldf import Dataset
from cltoolkit import Wordlist
from pathlib import Path
from cltoolkit.util import datasets_by_id
from collections import defaultdict
from tqdm import tqdm as progressbar
import random
from scipy.stats import spearmanr
random.seed(1234)
from itertools import combinations
from tabulate import tabulate
from cltoolkit.features.collection import feature_data, FeatureCollection
from cltoolkit.models import Language, Inventory
from pyclts import CLTS
from cldfcatalog import Config

clts = CLTS(Config.from_file().get_clone("clts"))
clts2phoible = clts.transcriptiondata_dict["phoible"]

# Concept thresholds
C = 200

# load the feature collection
fc = FeatureCollection.from_data(feature_data())

phoible = Dataset.from_metadata("data/phoible/cldf/StructureDataset-metadata.json")
wals = Dataset.from_metadata("data/wals/cldf/StructureDataset-metadata.json")

by_gcode = defaultdict(dict)

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
            language.sound_inventory = Inventory.from_list(*sounds,
                    ts=clts.bipa)
            try:
                by_gcode[gcode]["phoible"][lid] = language
            except KeyError:
                by_gcode[gcode]["phoible"] = {lid: language}

## get the datasets
lexicore = Wordlist(datasets=datasets_by_id(
    *[x.strip() for x in open("datasets.txt").readlines()],
    path="data/*/cldf/cldf-metadata.json"))
for language in lexicore.languages:
    if len(language.concepts) > C:
        try:
            by_gcode[language.glottocode]["lexicore"][language.id] = language
        except KeyError:
            by_gcode[language.glottocode]["lexicore"] = {language.id:
                    language}

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

# create the tables for the correlation
features = {
        "1A": "ConsonantSize",
        "2A": "VowelQualitySize",
        "3A": "CVRatio",
        "4A": "PlosiveFricativeVoicing",
        "5A": "PlosiveVoicingGaps",
        "6A": "UvularConsonants",
        "7A": "GlottalizedConsonants",
        "8A": "HasLaterals",
        #"9A": "HasEngma",
        "10A": "HasNasalVowels",
        "11A": "HasRoundedVowels",
        #"12A": "SyllableComplexity",
        "18A": "LacksCommonConsonants",
        "19A": "HasUncommonConsonants",
        }

for f, fid in features.items():
    scores = {"wals/phoible": [], "wals/lexicore": [], "phoible/lexicore": []}
    for i in range(100):
        tabW, tabP, tabL = [], [], []
        selected = [k for k, v in by_gcode.items() if len(v) == 3]
        table = []
        for row in selected:
            wals_v, phoible_v, lexicore_v = None, None, None
    
            # make sure that WALS has the feature
            wals_subset = [key for key in by_gcode[row]["wals"] if f in
                    by_gcode[row]["wals"][key]]
    
            if wals_subset:
                wals_choice = random.choice(wals_subset)
                wals_v = int(by_gcode[row]["wals"][wals_choice][f])
            phoible_choice = random.choice([key for key in
                by_gcode[row]["phoible"]])
            lexicore_choice = random.choice([key for key in
                by_gcode[row]["lexicore"]])
            phoible_v = fc.features[fid](by_gcode[row]["phoible"][phoible_choice])
            lexicore_v = fc.features[fid](by_gcode[row]["lexicore"][lexicore_choice])
            if wals_v:
                tabW += [wals_v]
                tabP += [phoible_v]
                tabL += [lexicore_v]
    
        for (ds1, tb1), (ds2, tb2) in combinations([
            ("wals", tabW), ("phoible", tabP), ("lexicore", tabL)], r=2):
            p, r = spearmanr(tb1, tb2)
            table += [[ds1, ds2, p, r, len(selected)]]
            scores[ds1+'/'+ds2] += [p]
    print('# Feature {0} / {1}'.format(f, fid))
    table = []
    for k, v in list(scores.items()):
        table += [[k, sum(v)/len(v)]]
    print(tabulate(table))
        

        

        
        


 
