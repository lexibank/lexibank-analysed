"""
Query New Dataset against the Lexibank Database.
"""
from pysem import to_concepticon
import sqlite3
from lingpy import tokens2class, ipa2tokens
from tabulate import tabulate
from clldutils.misc import slug
import csv

# kusu1250 Kusunda
# basq1248 Basque
# mapu1245 Mapudungun
# bang1363 Bangime
GCODE = 'taus1253'
OUT = 'base.sql'

# load lexibank database
db = sqlite3.connect("../data/lexibank2.sqlite3")
cursor = db.cursor()

# get the data on the language
data = []
with open("data.txt", encoding='utf8') as f:
    for row in f:
        word, concepts = row.strip().split("=")
        for concept in concepts.strip().split(", "):
            mappings = to_concepticon([{"gloss": concept}])[concept]
            if mappings:
                data += [[
                    word.strip(),
                    "".join(tokens2class(ipa2tokens(word.strip()), "dolgo")),
                    concept,
                    mappings[0][0],
                    mappings[0][1]
                    ]]

# cursor.execute("insert into LanguageTable(cldf_id) values ('proto');")
# for i, row in enumerate(data):
#     cursor.execute(
#         "insert into FormTable(cldf_id, cldf_form, cldf_value, cldf_languageReference, " +
#         " cldf_Segments, cldf_parameterReference, " +
#         "Dolgo_Sound_Classes) values ('proto-" + str(i + 1) +
#         "', '" + row[0] + "', '" + row[0] + "', "
#         "'proto', '" +
#         " ".join(ipa2tokens(row[0])) + "', '" +
#         slug(row[4]) + "', '" +
#         row[1] + "');"
#         )
try:
    cursor.execute("ALTER TABLE LanguageTable DROP COLUMN filter")
except:
    pass

cursor.execute(f"ALTER TABLE LanguageTable ADD COLUMN filter VARCHAR DEFAULT {GCODE}")


with open(OUT, encoding='utf8') as f:
    query = f.read()

cursor.execute(query)
table = cursor.fetchall()

if OUT == 'base.sql':
    # """Currently only ready for the base-query."""
    max_hits = table[0][-1]
    colors = {
        max_hits: "black",
        max_hits - 1: "darkgray",
        max_hits - 2: "lightgray"
    }
    SCALE = 0.25

    with open("coordinates.js", "w", encoding='utf8') as f:
        for row in table[::-1]:
            if row[-1] >= max_hits - 2:
                f.write(
                    "L.circle([{0:.4f}, {1:.2f}], {{color: 'black', size: 10, fillOpacity: 1, weight: 1, fillColor: '{2}', radius: {3}}}).addTo(map)\n".format(
                        row[4], row[5],
                        colors[row[6]],
                        row[6] * SCALE * 50000
                    )
                )
                f.write('.bindPopup("<b>{0}: {1} Hits</b>");\n'.format(row[0], row[6]))

    print(f"[i] Saved file with maximal number of hits at {max_hits}.")

if OUT == 'base.sql':
    header = ["Name", "ID", "Glottocode", "Family", "Latitude", "Longitude", "Hits"]
elif OUT == 'extended.sql':
    header = ["Name", "Glottocode", "Family", "Latitude", "Longitude", "Concepticon", "Core Concept", "Dolgopolsky", "Segments A", "Segments B"]

print(tabulate(
    table[:10],
    tablefmt="pipe",
    headers=header)
    )

with open('matches.tsv', 'w', encoding='utf8', newline='') as f:
    writer = csv.writer(f, delimiter='\t')
    writer.writerows(table)
