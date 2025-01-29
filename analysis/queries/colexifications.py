"""
Query New Dataset against the Lexibank Database.
"""
import argparse
import csv
import logging
import sqlite3
from clldutils.clilib import add_format, Table

logging.basicConfig(level=logging.INFO)


def run_query(args):
    # get the data on the language
    query = 'q_colexifications.sql'

    # load lexibank database
    db = sqlite3.connect("../lexibank.sqlite3")
    cursor = db.cursor()

    with open(query, encoding='utf8') as f:
        query = f.read()

    cursor.execute(query, (args.concept_1, args.concept_2))
    header = [row[0] for row in cursor.description]
    table = cursor.fetchall()

    with open("coordinates.js", "w", encoding='utf8') as f:
        for row in table[::-1]:
            f.write(
                f"L.circle([{row[4]}, {row[5]}], {{color: 'black', fillOpacity: 1, weight: 1, fillColor: 'darkgray', radius: 3e5}}).addTo(map)\n"
            )
            f.write(f'.bindPopup("<b>{row[1]}: {row[-1]}</b>");\n')

    with Table(args, *header) as t:
        t.extend(table[:10])

    with open('matches.tsv', 'w', encoding='utf8', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(header)
        writer.writerows(table)

    logging.info("Saved file with %s colexifications.", len(table))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--concept_1', type=str,
                        help='Choose the first concept to compare')
    parser.add_argument('--concept_2', type=str,
                        help='Choose the second concept to compare')
    add_format(parser, default='simple')
    args = parser.parse_args()

    run_query(args)
