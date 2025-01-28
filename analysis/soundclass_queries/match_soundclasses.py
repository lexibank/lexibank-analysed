"""
Query with the Lexibank Database.
"""
import argparse
import csv
import sqlite3
from clldutils.misc import slug
from lingpy import tokens2class, ipa2tokens
from pysem import to_concepticon
from tabulate import tabulate


# load lexibank database
db = sqlite3.connect("../lexibank.sqlite3")
cursor = db.cursor()


def run_query(setting, gcode):
    """Runs the query against the selected glottocode."""
    # get the data on the language
    data = []

    if setting == 'q_proto.sql':
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
        cursor.execute("insert into LanguageTable(cldf_id) values ('proto');")
        for i, row in enumerate(data):
            cursor.execute(
                "insert into FormTable(cldf_id, cldf_form, cldf_value, cldf_languageReference, " +
                " cldf_Segments, cldf_parameterReference, " +
                "Dolgo_Sound_Classes) values ('proto-" + str(i + 1) + 
                "', '" + row[0] + "', '" + row[0] + "', " 
                "'proto', '" +
                " ".join(ipa2tokens(row[0])) + "', '" +
                slug(row[4]) + "', '" +
                row[1] + "');"
                )
    try:
        cursor.execute("ALTER TABLE LanguageTable DROP COLUMN filter")
    except sqlite3.OperationalError:
        pass

    if setting != 'q_proto.sql':
        cursor.execute(f"ALTER TABLE LanguageTable ADD COLUMN filter VARCHAR DEFAULT {gcode}")

    with open(setting, encoding='utf8') as f:
        query = f.read()

    cursor.execute(query)
    table = cursor.fetchall()

    max_hits = table[0][-1]
    colors = {
        max_hits: "black",
        max_hits - (0.25*max_hits): "darkgray",
        max_hits - (0.50*max_hits): "lightgray"
    }
    scale = 0.50

    with open("coordinates.js", "w", encoding='utf8') as f:
        for row in table[::-1]:
            if row[-1] >= max_hits - (0.5*max_hits):
                for key, color in colors.items():
                    if key <= row[-1]:
                        fill = color
                        break

                f.write(
                    f"L.circle([{row[4]}, {row[5]}], {{color: 'black', fillOpacity: 1, weight: 1, fillColor: '{fill}', radius: {row[-1] * scale * 50000}}}).addTo(map)\n"
                )
                f.write(f'.bindPopup("<b>{row[0]}: {row[-1]} Hits</b>");\n')

    print(f"[i] Saved file with maximal number of hits at {max_hits}.")

    header = []
    if setting in ('q_base.sql', 'q_proto.sql'):
        header = ["Name", "ID", "Glottocode", "Family", "Latitude", "Longitude", "Hits"]
    elif setting == 'q_extended.sql':
        header = [
            "Name", "ID", "Glottocode", "Family", "Latitude", "Longitude", "Concepticon",
            "Core Concept", "Dolgopolsky", "Segments A", "Segments B", "Hits"
        ]

    print(tabulate(
        table[:10],
        tablefmt="pipe",
        headers=header
        ))

    with open('matches.tsv', 'w', encoding='utf8', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerows(table)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--setting', type=str,
                        help='Choose which query to run: base or extended')
    parser.add_argument('--glottocode', type=str, default='kusu1250',
                        help='Choose which glottocode to use for the query')
    args = parser.parse_args()

    run_query(
        setting=args.setting,
        gcode=args.glottocode
        )
