# Using the Lexibank Data Repository

Lexibank is a collection of lexical datasets provided in [CLDF](https://cldf.clld.org) formats. These CLDF datasets were compiled with the help of the `pylexibank` package, which is an extension for the [CLDFBench](https://github.com/cldf/cldfbench) package for handling CLDF datasets. Since data in the lexibank collection is maximally integrated with cross-linguistic resources that have been compiled during the past years, it is possible to make active use of the data to compute many features (lexical and phonological) automatically. In the following, we will describe the major workflow.

## 1 Lexibank Collection

The lexibank collection consists of mainly two types of datasets:

1. CLDF datasets linked to Concepticon and Glottolog with consistent lexeme forms which have a sufficient size in terms of concepts covered. This collection is called `ClicsCore` collection, since it fulfills the criteria to be included in the [CLICS](https://clics.clld.org) database. The collection can be used to compute various lexical features for individual language varieties.
2. CLDF datasets linked to Concepticon and Glottolog with lexeme forms which are transcribed in the BIPA  transcription system proposed by the [CLTS](https://clts.clld.org) project. This collection, which may  overlap with the `ClicsCore` collection, is called `LexiCore` and can be used to compute various phonological   features for language varieties.

The decision about which datasets are assigned to which collection is currently carried out by the board of lexibank editors, who estimate how well each of the datasets qualifies for the inclusion in either or both collections. The decisions are available in the form of a spreadsheet, shared along with this repository (see [etc/lexibank.tsv](etc/lexibank.tsv)).

## 2 Lexibank Workflow

This repository contains a `cldfbench` package, bundling

- code
  - to download the lexibank dataset,
  - to compute phonological and lexical features from this data and
- the computed structural data in three CLDF StructureDatasets.

The workflow consists of a sequence of calls to `cldfbench` subcommands, which in turn call the code described above.

1. Install the package (including Dependencies)

    ```shell
    git clone https://github.com/lexibank/lexibank-analysed
    cd lexibank-analysed
    pip install -e .
    ```

    Clone the repositories from:

   - [Glottolog](https://github.com/glottolog/glottolog)
   - [Concepticon](https://github.com/concepticon/concepticon-data)
   - [CLTS](https://github.com/cldf-clts/clts)

2. Download the data collections

   The data collections will be downloaded by reading the most recent selection of lexibank datasets from the file `etc/lexibank.tsv`:

   ```shell
   cldfbench download lexibank_lexibank_analysed.py
   ```

3. Compute phonological and lexical features and phoneme inventories

   The analysis results of `lexibank-analysed` are stored in three CLDF StructureDatasets.

   - Phonological features (inspired by those features typically listed in datasets like the [World Atlast of Language Structures](https://wals.info)) are computed with the help of the phonological feature inference methods provided by the [cltoolkits](https://github.com/cldf/cltoolkit) package, which offers facilitated (high-level) access to CLDF datasets (specifically lexical datasets). Having downloaded the data packages, you can run the following code to compute the current 18 phonological features from the `LexiCore` data. Since the target of phonological features is `LexiCore` data (data defined in the `LexiCore` collection of lexibank), the command will create a file called `lexicore.json`, in which the major information on phonological features is stored.
   - Lexical features (dedicated colexifications and partial colexifications) are computed as well.
   - Phoneme inventories including frequencies are derived.

   These datasets are created running

   ```shell
   cldfbench lexibank.makecldf lexibank_lexibank_analysed.py --glottolog path_to_glottolog --concepticon path_to_concepticon --clts path_to_clts
   ```

   with the paths to Glottolog (`path_to_glottolog`), Concepticon (`path_to_concepticon`) and CLTS (`path_to_clts`) pointing to the corresponding repositories from Step 1.

4. Make sure valid CLDF data has been created:

   ```shell
   pip install -e ".[test]"
   pytest
   ```

## 3 Data exploration

### Metadata

In addition to feature data, the CLDF data also contains

- provenance information, linking each doculect to the dataset from which it was extracted
- summary statistics about the collections into which we bundle the datasets.

This data is contained in the tables [contributions.csv](cldf/contributions.csv) and [collections.csv](cldf/collections.csv). We can look at the numbers of unique Glottocodes or Concepts and the number of individual forms in each collection:

```shell
pip install csvkit
csvcut -c ID,Glottocodes,Concepts,Forms cldf/collections.csv | csvformat -T -l | tabulate -s "\t" -1 -f "pipe"
```

|   line_number | ID        |   Glottocodes |   Concepts |   Forms |
|--------------:|:----------|--------------:|-----------:|--------:|
|             1 | LexiCore  |          3107 |       3209 | 1847439 |
|             2 | ClicsCore |          2064 |       3177 | 1540641 |
|             3 | CogCore   |          1786 |       1980 |  464690 |
|             4 | ProtoCore |            41 |       1137 |   13150 |
|             5 | Lexibank  |          3107 |       3209 | 1847439 |
|             6 | Selexion  |          3107 |       3193 | 1241274 |

or list how many source datasets are aggregated in each of these collections:

```shell
csvgrep -c Collection_IDs -m Lexi cldf/contributions.csv | csvstat --count
134
```

`contributions.csv` also lists numbers of doculects and senses. Datasets with a low ratio between `Glottocodes` and `Doculects`, i.e. with many doculects mapped to the same glottocode, are typical dialectal collections. We can check this ratio running

```shell
csvsql --query "select id, name, cast(glottocodes as float) / cast(doculects as float) as ratio from contributions order by ratio limit 1" cldf/contributions.csv 
ID,Name,ratio
cals,"CLDF dataset derived from Mennecier et al.'s ""Central Asian Language Survey"" from 2016",0.06818181818181818
```

### Feature data

To check for available features, you can inspect the CLDF ParameterTable of the respective
CLDF datasets:

```shell
csvcut -c ID,Name cldf/phonology-features.csv | column -s"," -t
ID                         Name
concepts                   Number of concepts
forms                      Number of forms
forms_with_sounds          Number of BIPA conforming forms
senses                     Number of senses
ConsonantQualitySize       consonant quality size
VowelQualitySize           vowel quality size
VowelSize                  vowel size
ConsonantSize              consonant size
CVRatio                    consonant and vowel ratio
CVQualityRatio             consonant and vowel ratio (by quality)
CVSoundRatio               consonant and vowel ratio (including diphthongs and clusters)
HasNasalVowels             has nasal vowels or not
HasRoundedVowels           has rounded vowels or not
VelarNasal                 has the velar nasal (engma)
PlosiveVoicingGaps         voicing and gaps in plosives
LacksCommonConsonants      gaps in plosives
HasUncommonConsonants      has uncommon consonants
PlosiveFricativeVoicing    voicing in plosives and fricatives
UvularConsonants           presence of uvular consonants
GlottalizedConsonants      presence of glottalized consonants
HasLaterals                presence of lateral consonants
SyllableStructure          complexity of the syllable structure
FirstPersonWithM           fist person starts with an m-sound
FirstPersonWithN           fist person starts with an n-sound
SecondPersonWithT          second person starts with a t-sound
SecondPersonWithM          second person starts with an m-sound
SecondPersonWithN          second person starts with an n-sound
MotherWithM                mother starts with m-sound
WindWithF                  wind starts with f-sound
HasPrenasalizedConsonants  inventory has pre-nasalized consonants
HasLabiodentalFricatives   inventory has labio-dental fricatives or affricates
FatherWithP                father starts with p-sound
SyllableOnset              complexity of the syllable onset
SyllableOffset             complexity of the syllable offset
```

```shell
csvcut -c ID,Name cldf/lexicon-features.csv | column -s"," -t
ID                                Name
concepts                          Number of concepts
forms                             Number of forms
senses                            Number of senses
LegAndFoot                        has the same word form for foot and leg
ArmAndHand                        arm and hand distinguished or not
BarkAndSkin                       bark and skin distinguished or not
FingerAndHand                     finger andhand distinguished or not
GreenAndBlue                      green and blue colexified or not
RedAndYellow                      red and yellow colexified or not
ToeAndFoot                        toe and foot colexified or not
SeeAndKnow                        see and know colexified or not
SeeAndUnderstand                  see and understand colexified or not
ElbowAndKnee                      elbow and knee colexified or not
FearAndSurprise                   fear and surprise colexified or not
CommonSubstringInElbowAndKnee     elbow and knee are partially colexified or not
CommonSubstringInManAndWoman      man and woman are partially colexified or not
CommonSubstringInFearAndSurprise  fear and surprise are partially colexified or not
CommonSubstringInBoyAndGirl       boy and girl are partially colexified or not
EyeInTear                         eye partially colexified in tear
BowInElbow                        bow partially colexified in elbow
CornerInElbow                     corner partially colexified in elbow
WaterInTear                       water partially colexified in tear
TreeInBark                        tree partially colexified in bark
SkinInBark                        skin partially colexified in bark
MouthInLip                        mouth partially colexified in lip
SkinInLip                         skin partially colexified in lip
HandInFinger                      hand partially colexified in finger
FootInToe                         foot partially colexified in toe
ThreeInEight                      three partially colexified in eight
ThreeInThirteen                   three partially colexified in thirteen
FingerAndToe                      finger and toe colexified or not
HairAndFeather                    hair and feather colexified or not
HearAndSmell                      hear and smell colexified or not
```

You can also easily inspect the data for outliers:

```shell
csvgrep -c Parameter_ID -m ConsonantQualitySize cldf/phonology-values.csv | csvstat -c Value -l | tabulate -s "\t" -1 -f "pipe"
```

|                 |   4. "Value"                     |
|:----------------|:---------------------------------|
|                 | Type of data:          Number    |
|                 | Contains null values:  False     |
|                 | Non-null values:       5477      |
|                 | Unique values:         64        |
|                 | Smallest value:        7         |
|                 | Largest value:         107       |
|                 | Sum:                   130,995   |
|                 | Mean:                  23.917    |
|                 | Median:                23        |
|                 | StDev:                 8.2       |
|                 | Most decimal places:   0         |
|                 | Most common values:    22 (367x) |
|                 | 23 (366x)                        |
|                 | 20 (347x)                        |
|                 | 21 (314x)                        |
|                 | 19 (306x)                        |
| Row count: 5477 |                                  |

```shell
csvgrep -c Parameter_ID -m ConsonantQualitySize cldf/phonology-values.csv | csvgrep -c Value -r"^(7|98)$" | csvcut -c Language_ID,Value | tabulate -s "," -1 -f "pipe"
```

| Language_ID                                |   Value |
|:-------------------------------------------|--------:|
| chenhmongmien-NortheastYunnanChuanqiandian |      98 |
| johanssonsoundsymbolic-Rotokas             |       7 |
| transnewguineaorg-keoru-ahia               |       7 |

And we can correlate our computed features with the corresponding data from other datasets, such as WALS and PHOIBLE (as implemented in [correlations.py](lexibank_analysed_commands/correlations.py)):

```shell
cldfbench lexibank-analysed.correlations
```

| Feature | WALS/LexiCore | WALS/PHOIBLE | LexiCore/PHOIBLE | N |
|:----------|:----------------|:---------------|:-------------------|----:|
| 1A | 0.67 / 0.0 | 0.92 / 0.0 | 0.71 / 0.0 | 281 |
| 2A | 0.54 / 0.0 | 0.68 / 0.0 | 0.7 / 0.0 | 283 |
| 3A | 0.56 / 0.0 | 0.76 / 0.0 | 0.68 / 0.0 | 283 |
| 4A | 0.53 / 0.0 | 0.67 / 0.0 | 0.55 / 0.0 | 283 |
| 5A | 0.36 / 0.0 | 0.55 / 0.0 | 0.59 / 0.0 | 283 |

## 4 Data visualization

Visual exploration of the data can be done with `cldfviz`, a `cldfbench` plugin to visualize CLDF datasets.

First, we can look at all languages in Lexibank with their geographic distribution (to obtain the corresponding PNG file that we show here, add the parameters `-format=png`, `--width 30` and `--height 15` to your command. You must also make sure to install `cldfviz` with `cartopy` support. If you follow the commands as shown here, they will all result in interactive [leaflet maps](https://leafletjs.com/).

```shell
cldfbench cldfviz.map cldf/phonology-metadata.json --language-properties="LexiCore" --language-properties-colormaps='{"1":"#050505"}'  --markersize 10 --pacific-centered --no-legend
```

![basemap](plots/basemap.png)

We can now look at the distribution of languages in LexiCore and ClicsCore on a map:

```shell
cldfbench cldfviz.map cldf/phonology-metadata.json --language-properties="LexiCore,ClicsCore,CogCore" --language-properties-colormaps='{"1":"#fde725"},{"1":"#21918c", "0":"#f8f8ff"},{"1":"#440154", "0":"#f8f8ff"}'  --markersize 15 --pacific-centered
```

![doculects](plots/doculects.png)

We can also plot the number of forms and concepts in the different languages:

```shell
cldfbench cldfviz.map cldf/phonology-metadata.json --language-properties="Forms,Concepts" --language-properties-colormaps="plasma,viridis"  --markersize 15 --pacific-centered
```

![coverage](plots/coverage.png)

We can plot continuous variables on a map, e.g. `CVQualityRatio`:

```shell
cldfbench cldfviz.map cldf/phonology-metadata.json --parameters CVQualityRatio --language-filters '{"Name":"^(?!Adyghe|Yorno So|Togo Kan|Karata$).*$", "Glottocode": "^(?!kajt1238)"}' --colormaps plasma --pacific-centered
```

A screenshot of the resulting [leaflet map](https://leafletjs.com/) is shown below.

![consonant quality size](plots/CVQualityRatio.png)

Map plots for categorical variables like `VelarNasal` are supported as well. This feature is equivalent to [feature 9A from WALS](https://wals.info/feature/9A).

We can inspect the values:

```shell
csvgrep -c Parameter_ID -m "VelarNasal" cldf/phonology-codes.csv | csvcut -c ID,Name | tabulate -s "," -1 -f "pipe"
```

| ID           | Name                                                    |
|:-------------|:--------------------------------------------------------|
| VelarNasal-1 | velar nasal occurs in syllable-initial position         |
| VelarNasal-2 | velar nasal occurs but not in syllable-initial position |
| VelarNasal-3 | velar nasal is missing                                  |

and plot it on a map:

```shell
cldfbench cldfviz.map cldf/phonology-metadata.json --parameters VelarNasal --colormaps tol --pacific-centered
```

![Velar Nasal](plots/VelarNasal.png)

As a final type of feature, consider `SkinInBark`. This feature is a so-called partial colexification, which means that the word expressing "skin" recurs in part in the word expressing "bark" in the language variety in question, while not being identical with it. This feature has two major values, `true` and `false`, and -- as a third case -- `None`, when data are missing (there is no word for "skin" or for "bark" in our data). We can plot the feature in the same way in which we plotted the data before

```shell
cldfbench cldfviz.map cldf/lexicon-metadata.json --parameters SkinInBark --pacific-centered
```

![Skin in Bark](plots/SkinInBark.png)

You can also plot two features at the same time onto a map. In order to do so, just select those features which you think are useful to be inspected synchronously, and type:

```shell
cldfbench cldfviz.map cldf/lexicon-metadata.json --parameters ArmAndHand,LegAndFoot --pacific-centered --markersize 15
```

The resulting plot offers a new account on the data by combining feature information for two features.

![ArmAndHand-LegAndFoot](plots/ArmAndHand-LegAndFoot.png)
