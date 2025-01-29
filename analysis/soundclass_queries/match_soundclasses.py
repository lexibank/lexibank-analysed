"""
Query with the Lexibank Database.
"""
import logging
import pathlib
import sqlite3
import argparse
import itertools

from csvw.dsv import UnicodeWriter
from clldutils.clilib import add_format, Table, PathType
from lingpy import tokens2class, ipa2tokens
from pysem import to_concepticon

logging.basicConfig(level=logging.INFO)


def cc(dolgo_sound_classes):
    """
    Compute consonant classes from Dolgopolsky sound classes.
    """
    condensed = dolgo_sound_classes.replace('V', '').replace('+', '').replace('1', '')
    if dolgo_sound_classes.startswith('V'):
        return ('H' + condensed + 'H')[:2]
    return (condensed + 'H')[:2]


def run_query(args):
    """Runs the query against the selected glottocode."""

    # load lexibank database
    db = sqlite3.connect("../lexibank.sqlite3")
    cursor = db.cursor()
    db.create_function('cc', 1, cc)

    if args.query.stem == 'q_proto':
        cursor.execute(pathlib.Path('q_proto_view.sql').read_text(encoding='utf8'))
        hits = []
        for row in pathlib.Path('data.txt').read_text(encoding='utf8').split('\n'):
            word, _, concepts = row.partition("=")
            for concept in concepts.strip().split(", ") if concepts else []:
                mappings = to_concepticon([{"gloss": concept}])[concept]
                if mappings:
                    cursor.execute(
                        args.query.read_text(encoding='utf8'),
                        (
                            cc("".join(tokens2class(ipa2tokens(word.strip()), "dolgo"))),
                            mappings[0][1],
                        ))
                    hits.extend(cursor.fetchall())

        table = []
        for lid, rows in itertools.groupby(sorted(hits, key=lambda r: r[0]), lambda row: row[0]):
            rows = list(rows)
            table.append(list(rows[0]) + [len(rows)])
        table = sorted(table, key=lambda r: -r[-1])
    else:
        cursor.execute(args.query.read_text(encoding='utf8'), (args.glottocode, args.glottocode) if args.query.stem != 'q_proto' else ())
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

    logging.getLogger(__name__).info(f"Saved file with maximal number of hits at {max_hits}.")

    header = []
    if args.query.stem in ('q_base', 'q_proto'):
        header = ["Name", "ID", "Glottocode", "Family", "Latitude", "Longitude", "Hits"]
    elif args.query.stem == 'q_extended':
        header = [
            "Name", "ID", "Glottocode", "Family", "Latitude", "Longitude", "Concepticon",
            "Core Concept", "Dolgopolsky", "Segments A", "Segments B", "Hits"
        ]

    with Table(args, *header) as t:
        t.extend(table[:10])

    with UnicodeWriter('matches.tsv', delimiter='\t') as writer:
        writer.writerows([header] + table)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--query', type=PathType(type='file'),
                        help='Choose which query to run: base or extended')
    parser.add_argument('--glottocode', type=str, default='kusu1250',
                        help='Choose which glottocode to use for the query')
    add_format(parser, default='simple')
    args = parser.parse_args()

    run_query(args)
