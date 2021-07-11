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
