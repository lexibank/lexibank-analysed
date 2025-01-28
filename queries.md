# Accessing the Lexibank data via SQLite queries

## Install dependencies

In a first step, we install all the necessary requirements for running the code presented here.

```shell
cd analysis/
pip install -r requirements.txt
```

Then, we convert the Lexibank data to a SQLite database that we can query:

```shell
cldf createdb ../cldf/wordlist-metadata.json lexibank.sqlite3
```

## Query one Wordlist Against Lexibank

The queries discussed in this chapter are stored in the folder `soundclass_queries`.

```shell
cd soundclass_queries
```

The first set of queries that we will present are based on Dolgopolsky sound classes. They are run via the script `match_soundclasses.py`, and look for matches in sound classes for data from a specific language, compared to all other languages in Lexibank. Two queries are offered: `base.sql`, and `extended.sql`. Both are called via the command line, where you can also specify the glottocode from the language that you want to compare with all other cases. The `base.sql` query only gives you the number of matches, while `extended.sql` also provides you with the list of matches themselves. In both cases, the results are stored in `matches.tsv` and a map is created as `index.html` that you can open in a browser. Here, the languages with most matches are colored accordingly.

```shell
python match_soundclasses.py --setting=q_base.sql --glottocode=kusu1250
python match_soundclasses.py --setting=q_extended.sql --glottocode=cand1248
```

The third setting uses the `q_proto.sql` query. Here, we check for matches based on a list of lexical forms provided in `data.txt`. This replaces the glottocode, since we provide the data manually.

```shell
python match_soundclasses.py --setting=q_proto.sql
```

## Queries: Colexifications

tbc
