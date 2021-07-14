# Using the Lexibank Data Repository

Lexibank is a collection of lexical datasets provided in [CLDF](https://cldf.clld.org) formats. These CLDF datasets were compiled with the help of the `pylexibank` package, which is an extension for the [CLDFBench](https://github.com/cldf/cldfbench) package for handling CLDF datasets. Since data in the lexibank collection is maximally integrated with cross-linguistic resources that have been compiled during the past years, it is possible to make active use of the data to compute many features (lexical and phonological) automatically. In the following, we will describe the major workflow.

## 1 Lexibank Collection

The lexibank collection consists of mainly two types of datasets:

1. CLDF datasets linked to Concepticon and Glottolog with consistent lexeme forms which have a sufficient size in terms of concepts covered. This collection is called `clicscore` collection, since it fulfills the criteria to be included into the [CLICS](https://clics.clld.org) database. The collection can be used to compute various lexical features for individual language varieties.
2. CLDF datasets linked to Concepticon and Glottolog with lexeme forms which are transcribed in the BIPA transcription system proposed by the [CLTS](https://clts.clld.org) project. This collection, which may overlap with the `clicscore` collection, is called `lexicore` and can be used to compute various phonological features for language varieties.

The decision about which datasets are assigned to which collection is currently carried out by the board of lexibank editors, who estimate how well each of the datasets qualifies for the inclusion in either or both collections. The decisions are available in the form of a spreadsheet, shared along with this repository (see [src/lexibank/data/lexibank.tsv](https://github.com/lexibank/lexibank-study/blob/main/src/lexibank/data/lexibank.tsv)).

The original datafile itself will be curated on the [nextcloud server of the MPI-EVA](https://share.eva.mpg.de/index.php/s/dqmqQn567P4PKie). For now, however, we experience problems with the nextcloud server and therefore edit the spreadsheet on [GoogleSheets](https://docs.google.com/spreadsheets/d/1x8c_fuWkUYpDKedn2mNkKFxpwtHCFAOBUeRT8Mihy3M/edit?usp=sharing). 


## 2 Lexibank Workflow

We provide code with this repository, which you can use to:

1. download the data in the most recent lexibank collection (lexicore and clicscore)
2. compute various phonological and lexical features from the data
3. plot the features to a map in order to inspect them

The workflow uses a commandline interface written in Python which requires several dependencies to be installed. The basic workflow consists of the following steps:

**1 Install the Code and Dependencies**

```
$ git clone https://github.com/lexibank/lexibank-study
$ cd lexibank-study
$ pip install -e ./
```
**2 Download the data collections**

The data collections will be downloaded by reading the most recent selection of lexibank datasets from the file `src/lexibank/data/lexibank.tsv` and then downloading the relevant datasets to a folder which you specify with the kewyord `destination`. We will call the folder `datasets` in the following.

```
$ lexibank download --destination=datasets
```

**3 Compute phonological features**

The computation of phonological features (inspired by those features typically listed in datasets like the [World Atlast of Language Structures](https://wals.info) is carried out with the help of the phonological feature inference methods provided by the [cltoolkits](https://github.com/cldf/cltoolkit) package, which offers facilitated (high-level) access to CLDF datasets (specifically lexical datasets). Having downloaded the data packages, you can run the following code to compute the current 18 phonological features from the `lexicore` data. Since the target of phonological features is `lexicore` data (data defined in the `lexicore` collection of lexibank), the command will create a file called `lexicore.json`, in which the major information on phonological features is stored.

```
$ lexibank inventory --datadir=datasets
```


**4 Compute lexical features**

Lexical features (dedicated colexifications and partial colexifications) can be computed with the help of the command:

```
$ lexibank lexicon --datadir=datasets
```

This command will create a file `clics.json`, in which the lexical feature data is stored. As an example for the structure of the data in the `clics.json` file (which is analogous to the data in the `lexicore.json` file), consider the following excerpt:

```
{
  "chenhmongmien-EasternLuobuohe": {
    "name": "Luobuohe, Eastern",
    "glottocode": "luop1235",
    "dataset": "chenhmongmien",
    "latitude": 26.63966,
    "longitude": 107.913354,
    "subgroup": "Hmongic",
    "family": "Hmong-Mien",
    "features": {
      "concepts": 792,
      "forms": 891,
      "senses": 880,
      "LegAndFoot": false,
      "ArmAndHand": null,
      "FingerAndHand": false,
      "GreenAndBlue": false,
      "RedAndYellow": false,
      "FootAndToe": null,
      "EyeInTear": false,
      "WaterInTear": false,
      "TreeInBark": null,
      "SkinInBark": null
    }
  }
}
```

The information in both data files is later used to compute correlations and to plot data onto geographic maps.

**5 Check for available features**

To check for features that are available for a given data file, just type:

```
$ lexibank features --datafile=clics.json
```

This will produce the following table:

| Number | Feature | Description | Type | Note |
|---------:|:--------------|:----------------------------------------|:-------|:----------|
| 1 | ArmAndHand | arm and hand distinguished or not | bool | WALS 129A |
| 2 | EyeInTear | eye partially colexified in tear | bool | |
| 3 | FingerAndHand | finger andhand distinguished or not | bool | WALS 130A |
| 4 | FootAndToe | foot and toe colexified or not | bool | |
| 5 | GreenAndBlue | green and blue colexified or not | bool | |
| 6 | LegAndFoot | has the same word form for foot and leg | bool | |
| 7 | RedAndYellow | red and yellow colexified or not | bool | |
| 8 | SkinInBark | skin partially colexified in bark | bool | |
| 9 | TreeInBark | tree partially colexified in bark | bool | |
| 10 | WaterInTear | water partially colexified in tear | bool | |

And another table will be produced if you specify the data file to `lexicore.json`:

```
$ lexibank features --datafile=lexicore.json
```

| Number | Feature | Description | Type | Note |
|---------:|:------------------------|:--------------------------------------------------------------|:------------|:---------|
| 1 | CVQualityRatio | consonant and vowel ratio (by quality) | float | |
| 2 | CVRatio | consonant and vowel ratio | float | |
| 3 | CVSoundRatio | consonant and vowel ratio (including diphthongs and clusters) | float | |
| 4 | ConsonantQualitySize | consonant quality size | integer | |
| 5 | ConsonantSize | consonant size | integer | |
| 6 | GlottalizedConsonants | presence of glottalized consonants | integer | |
| 7 | HasLaterals | presence of glottalized consonants | integer | |
| 8 | HasNasalVowels | has nasal vowels or not | categorical | WALS 10A |
| 9 | HasRoundedVowels | has rounded vowels or not | categorical | WALS 11A |
| 10 | HasUncommonConsonants | has uncommon consonants | categorical | WALS 19A |
| 11 | LacksCommonConsonants | gaps in plosives | categorical | WALS 18A |
| 12 | PlosiveFricativeVoicing | voicing in plosives and fricatives | integer | |
| 13 | PlosiveVoicingGaps | voicing and gaps in plosives | categorical | WALS 5A |
| 14 | SyllableStructure | complexity of the syllable structure | categorical | WALS 12A |
| 15 | UvularConsonants | presence of uvular consonants | integer | |
| 16 | VelarNasal | has the velar nasal (engma) | integer | WALS 9A |
| 17 | VowelQualitySize | vowel quality size | integer | |
| 18 | VowelSize | vowel size | integer | |


You can also use the feature code to search for outliers:

```
$ lexibank features --datafile=lexicore.json --outliers
```

| Feature | Description | Minimum | Maximum |
|:------------------------|:--------------------------------------------------------------|:----------------------------------------------------|:--------------------------------------------------|
| ConsonantQualitySize | consonant quality size | johanssonsoundsymbolic-Rotokas: 7 | chenhmongmien-Chuanqiandian, Northeast Yunnan: 98 |
| VowelQualitySize | vowel quality size | johanssonsoundsymbolic-Adyghe: 2 | yangyi-CE-Yong'an: 44 |
| VowelSize | vowel size | blustaustronesian-Hanunoo: 3 | yangyi-CE-Yong'an: 44 |
| ConsonantSize | consonant size | johanssonsoundsymbolic-Rotokas: 7 | chenhmongmien-Chuanqiandian, Northeast Yunnan: 99 |
| CVRatio | consonant and vowel ratio | johanssonsoundsymbolic-Waorani: 0.47058823529411764 | northeuralex-Adyghe: 17.0 |
| CVQualityRatio | consonant and vowel ratio (by quality) | johanssonsoundsymbolic-Waorani: 0.8 | johanssonsoundsymbolic-Adyghe: 23.5 |
| CVSoundRatio | consonant and vowel ratio (including diphthongs and clusters) | johanssonsoundsymbolic-Waorani: 0.47058823529411764 | northeuralex-Adyghe: 17.0 |
| HasNasalVowels | has nasal vowels or not | allenbai-Heqing: 1 | yangyi-Toloza: 2 |
| HasRoundedVowels | has rounded vowels or not | allenbai-Jianchuan: 1 | yangyi-Hlepho: 4 |
| VelarNasal | has the velar nasal (engma) | allenbai-Eryuan: 2 | wold-Wichí: 3 |
| PlosiveVoicingGaps | voicing and gaps in plosives | blustaustronesian-Tetum: 1 | yangyi-Toloza: 5 |
| LacksCommonConsonants | gaps in plosives | allenbai-Eryuan: 1 | johanssonsoundsymbolic-Waorani: 6 |
| HasUncommonConsonants | has uncommon consonants | allenbai-Eryuan: 1 | wold-Tarifiyt Berber: 7 |
| PlosiveFricativeVoicing | voicing in plosives and fricatives | beidasinitic-Guangzhou: 1 | yangyi-Toloza: 4 |
| UvularConsonants | presence of uvular consonants | allenbai-Eryuan: 1 | yangyi-S. Muji: 4 |
| GlottalizedConsonants | presence of glottalized consonants | allenbai-Eryuan: 1 | wold-Hausa: 8 |
| HasLaterals | presence of glottalized consonants | birchallchapacuran-Cojubim: 1 | yangyi-Toloza: 3 |
| SyllableStructure | complexity of the syllable structure | carvalhopurus-Apurinã: 1 | yangyi-Toloza: 3 |



**6 Plot one feature onto a map**

When plotting a feature on to a map, 
you need to pass two major types of information: which data file to use (`clics.json` or `lexicore.json`), and which feature to plot.

Features are computed with `cltoolkits`, and major information can accordingly be found in the `cltoolkit` package, in the file [src/cltoolkit/features/features.json](https://github.com/cldf/cltoolkit/blob/main/src/cltoolkit/features/features.json). A feature is describe by a couple of characteristics as shown below:

```json
  {
    "id": "ConsonantQualitySize",
    "name": "consonant quality size",
    "type": "integer",
    "target": "inventory",
    "module": "cltoolkit.features.phonology",
    "function": "consonant_quality_size",
    "note": ""
  }
```

Important aspects are the `id`, since we use the same identifier in our lexibank package, and the `type`, which is defined as an `integer` in this example. The type has an influence on the way in which the feature will be plotted to a map. If it is set to `integer` or `float`, this means that we deal with "continuous" feature variables which we plot with the help of typical colormaps, as they are provided by [matplotlib.cm](https://matplotlib.org/stable/tutorials/colors/colormaps.html). 

To plot a continuous feature, you can therefore simply type:

```
$ lexibank plot_feature --feature=ConsonantQualitySize --colormap=plasma --filename=plots/ConsonantQualitySize.jpg --dpi=300 --datafile=lexicore.json
```

As a result, you can find the following plot in the folder `plots`:

![image](https://raw.githubusercontent.com/lexibank/lexibank-study/main/plots/ConsonantQualitySize.jpg)

In addition, we also find features like the following in `cltoolkit`:

```json
  {
    "id": "HasRoundedVowels",
    "name": "has rounded vowels or not",
    "type": "categorical",
    "target": "inventory",
    "module": "cltoolkit.features.phonology",
    "function": "has_rounded_vowels",
    "note": "WALS 11A",
    "categories": {
      "1": "no high and no mid vowels",
      "2": "high and mid vowels",
      "3": "high and no mid vowels",
      "4": "mid and no high vowels"
    }
  }
```

This feature, which is equivalent with the feature 11A from [WALS](https://wals.info), is given the type `categorical`, which means that we provide a list of `categories` which give concrete explanations for each aspect. If the feature value is `1`, for example, this means that we do not find high and mid vowels in the language (according to our automatic analysis), `2` says there are "high and mid vowels", etc. 

Plotting this feature can be done in the same way, but you can no longer use the continuous colormaps provided by matplotlib. Instead, we offer some predefined colormap schemas in [src/lexibank/caropy.py#L52-L101](https://github.com/lexibank/lexibank-study/blob/f997ce806c03a388d509e0d9ad31c515db3504a5/src/lexibank/cartopy.py#L52-L101). 

Since we need exactly four values to plot our data, we therefore select the colormap `SequentialOrRd4`:


```
$ lexibank plot_feature --feature=HasRoundedVowels --colormap=SequentialOrRd4 --filename=plots/HasRoundedVowels.jpg --dpi=300 --datafile=lexicore.json
```

![image](https://github.com/lexibank/lexibank-study/blob/main/plots/HasRoundedVowels.jpg?raw=true)


As a final type of feature, consider the following one:

```json
  {
    "id": "SkinInBark",
    "name": "skin partially colexified in bark",
    "type": "bool",
    "target": "inventory",
    "module": "cltoolkit.features.lexicon",
    "function": "has_skin_in_bark",
    "note": "",
    "categories": {
      "true": "skin partially colexified in bark",
      "false": "skin not partially colexified in bark",
      "null": "missing data"
    }
  }
```

The feature `SkinInBark` is a so-called partial colexification, which means that the word expressing "skin" recurs in part in the word expressing "bark" in the language variety in question, while not being identical with it.

This feature is given the type `bool`, since it has two major outcomes, true and false, and -- as a third case -- `None`, when data are missing (there is no word for "skin" or for "bark" in our data). 
We can plot the feature in the same way in which we plotted the data before, but we pass the `clics.json` data as our datafile this time, and we use the standard colormap (+++integration of boolean colormaps is pending+++). 

```
$ lexibank plot_feature --feature=SkinInBark --filename=plots/SkinInBark.jpg --dpi=300 --datafile=clics.json
```

![image](https://github.com/lexibank/lexibank-study/blob/main/plots/SkinInBark.jpg?raw=true)



**7 Plot two features onto a map**

You can also plot two features at the same time onto a map +++ but for now only logical features +++. In order to do so, just select those features which you think are useful to be inspected synchronously, and type:

```
$ lexibank plot_features --featureA=ArmAndHand --featureB=LegAndFoot --markersize=2 --dpi=300 --filename=plots/ArmAndHand-LegAndFoot.jpg --datafile=clics.json
```

The resulting plot offers a new account on the data by combining feature information for two features. 


![image](https://github.com/lexibank/lexibank-study/blob/main/plots/ArmAndHand-LegAndFoot.jpg?raw=true)
