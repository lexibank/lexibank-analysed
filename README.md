# Study on lexibank data (presenting the lexibank dataset).

## Links

* [Lexibank Paper](https://share.eva.mpg.de/index.php/s/drLi7WZwtFGJosH)
* [Lexibank List of Datasets](https://docs.google.com/spreadsheets/d/1x8c_fuWkUYpDKedn2mNkKFxpwtHCFAOBUeRT8Mihy3M/edit?usp=sharing)

## Running the scripts

Install the lexibank package:

```
pip install -e ./
```

Download the data (git):

```
lexibank download --destination=datasets
```

Assemble phoneme features in file lexicore.json:

```
lexibank inventory
```

Create plot of data in lexicore:

```
lexibank plot_lexicore --lexicore=lexicore.json
```

Create plot of a feature:

```
lexibank plot_discrete_pfeature --filename=plots/HasLaterals.pdf --feature=HasLaterals --colormap=SequentialOrRd3 --lexicore=lexicore.json
```

## Detailed Discussion of Commands

### Plotting Discrete Phonological Features

Phonological features are calculated from selected lexical datasets, using dedicated functions defined in the `cltoolkit` package. Many features were modeled after the features described in existing databases dedicated to providing cross-linguistic information on various language varieties, such as the World Atlas of Language Structures online (Dryer and Haspelmath 2013).

Features are computed beforehand using dedicated commands and then stored in a JSON file. 

In order to get an overview on the features which are available, just type:

```
$ lexibank feature --datafile=lexicore.json --format=simple
```

The output will plot all features which have currently been computed:

```
Feature                  Description
-----------------------  -------------------------------------------------------------
ConsonantQualitySize     consonant quality size
VowelQualitySize         vowel quality size
VowelSize                vowel size
ConsonantSize            consonant size
CVRatio                  consonant and vowel ratio
CVQualityRatio           consonant and vowel ratio (by quality)
CVSoundRatio             consonant and vowel ratio (including diphthongs and clusters)
HasNasalVowels           has nasal vowels or not
HasRoundedVowels         has rounded vowels or not
VelarNasal               has the velar nasal (engma)
PlosiveVoicingGaps       voicing and gaps in plosives
LacksCommonConsonants    gaps in plosives
HasUncommonConsonants    has uncommon consonants
PlosiveFricativeVoicing  voicing in plosives and fricatives
UvularConsonants         presence of uvular consonants
GlottalizedConsonants    presence of glottalized consonants
HasLaterals              presence of glottalized consonants
SyllableStructure        complexity of the syllable structure
```
