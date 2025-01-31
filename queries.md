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
cd queries
```

The first set of queries that we will present are based on Dolgopolsky sound classes. They are run via the script `etymatch.py`, and look for matches in sound classes for data from a specific language, compared to all other languages in Lexibank. Two queries are offered: `base.sql`, and `extended.sql`. Both are called via the command line, where you can also specify the glottocode from the language that you want to compare with all other cases. The `base.sql` query only gives you the number of matches, while `extended.sql` also provides you with the list of matches themselves. In both cases, the results are stored in `matches.tsv` and a map is created as `index.html` that you can open in a browser. Here, the languages with most matches are colored accordingly.

```shell
$ python etymatch.py --query=q_base.sql --glottocode=kusu1250

cldf_name    cldf_id                               cldf_glottocode    Family                      cldf_latitude    cldf_longitude    Hits
-----------  ------------------------------------  -----------------  ------------------------  ---------------  ----------------  ------
Kamba_kitu   tls-KambaKitu                         kamb1297           Atlantic-Congo                      -1.61             37.95       7
Aleut        northeuralex-ale                      aleu1260           Eskimo-Aleut                        52.12           -174.29       7
Sema         marrisonnaga-Sema                     sumi1235           Sino-Tibetan                        25.85             94.27       7
Akawaio      huntergatherer-70                     akaw1239           Cariban                              6.16            -60.86       7
siroi        zgraggenmadang-siroi                  siro1249           Nuclear Trans New Guinea            -5.53            145.99       6
Japanese     wold-Japanese                         nucl1643           Japonic                             37.00            140.00       6
Yaweyuha     transnewguineaorg-yaweyuha            yawe1241           Nuclear Trans New Guinea            -6.19            145.36       6
Wagi         transnewguineaorg-wagi                wagi1249           Nuclear Trans New Guinea            -5.18            145.73       6
Tauade       transnewguineaorg-tauade              taua1242                                               -8.35            147.09       6
Haida        tolmiebritishcolumbia-Haida-Kumshewa  haid1248                                               53.03           -131.61       6
```

```shell
python etymatch.py --query=q_extended.sql --glottocode=cand1248
```

The third query uses the `q_proto.sql` query. Here, we check for matches based on a list of lexical forms provided in `data.txt`. This replaces the glottocode, since we provide the data manually.

```shell
python etymatch.py --query=q_proto.sql
```

## Queries: Colexifications

The next query shows how you can easily extract specific colexifications between Concepticon concepts. You simply add the two concepts to the function call that you want to compare, and receive a full list of language varieties that feature the colexification in question. The resulting map provides you with information on geographic spread of the languages involved as well as their lexical forms.

```shell
$ python colexifications.py --concept_1 'SUN' --concept_2 'MOON'

  Count  Doculect       Glottocode    Family          cldf_latitude    cldf_longitude  Form
-------  -------------  ------------  ------------  ---------------  ----------------  -------------
      2  Hokkaido Ainu  ainu1240      Ainu                    43.63            142.46  ts u p
      2  Mubami         muba1238      Anim                    -7.55            143.00  b u b e i
      2  Cayapa         chac1249      Barbacoan                0.71            -79.05  p a h t a
      2  Muinane        muin1242      Boran                   -0.87            -72.42  n ɨ ʔ ɨ b a
      2  Kasua          kasu1251      Bosavi                  -6.65            142.99  o p o
      2  Wounaan        woun1238      Chocoan                  8.50            -78.00  e d a u
      2  Bauzi          bauz1241      Geelvink Bay            -2.45            137.63  a l a
      2  Guahibo        guah1255      Guahiboan                5.82            -68.98  h u a m e t o
      2  Playero        play1240      Guahiboan                6.91            -71.00  h u a m e t o
      2  Nukak          nuka1242      Kakua-Nukak              2.66            -71.46  w i d ʔ
INFO:root:Saved file with 29 colexifications.
```

## Queries: Semantic diversity of cognate set

The last query is a bit different, since it makes use of a specific Lexibank dataset, `blumpanotacana`. The same query can be run with all datasets of the *CogCore* subset, since all it requires are annotations for cognacy.

For preparing the data, we only need to clone the repository and create the SQLite database.

```shell
cd cognateset_diversity
git clone https://github.com/pano-takanan-history/blumpanotacana 
cldf createdb blumpanotacana/cldf/cldf-metadata.json blumpanotacana.sqlite3
python cognateset_diversity.py
```

The script provides an output of the different concepts that are annotated for cognacy, as well as the amount of languages in each subgroup that features such semantic value. The result can be visualized by a colexification network.

![Example](analysis/queries/cognateset_diversity/cog_moon.png){width=50%}

In the example we can see that cognateset *4280* features a range of different semantics, where all Tacanan languages have the meaning of MOON, while the Panoan languages feature YEAR, SUN, DAY, and others.
