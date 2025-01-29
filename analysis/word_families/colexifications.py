"""
Query New Dataset against the Lexibank Database.
"""
import argparse
import csv
import logging
import sqlite3
from tabulate import tabulate
from clldutils.clilib import add_format, Table, PathType

logging.basicConfig(level=logging.INFO)


def run_query(args):
    # get the data on the language
    query = 'colexifications.sql'

    # load lexibank database
    db = sqlite3.connect("../lexibank.sqlite3")
    cursor = db.cursor()

    with open(query, encoding='utf8') as f:
        query = f.read()

    cursor.execute(query, (args.concept_1, args.concept_2))

    table = cursor.fetchall()

    header = ["Count", "Language", "Glottocode", "Family", "Form"]

    print(tabulate(
        table[:10],
        tablefmt="pipe",
        headers=header,
    ))

    with open('colex.tsv', 'w', encoding='utf8', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(header)
        writer.writerows(table)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--concept_1', type=str,
                        help='Choose the first concept to compare')
    parser.add_argument('--concept_2', type=str,
                        help='Choose the second concept to compare')
    add_format(parser, default='simple')
    args = parser.parse_args()

    run_query(args)
