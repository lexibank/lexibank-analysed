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
python commands/download.py
```

Assemble phoneme features in file lexicore.json:

```
python commands/inventory.py
```

Create plot of data in lexicore:

```
python commands/plot_lexicore.py lexicore.json
```

Create plot of a feature:

```
python commands/plot_phoneme_feature.py lexicore.json SyllableComplexity
```
