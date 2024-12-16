"""
Query New Dataset against the Lexibank Database.
"""
import sqlite3
from tabulate import tabulate
import csv

OUT = 'lb_release.sql'
concept_one = ''
concept_two = ''

# load lexibank database
db = sqlite3.connect("data/lexibank1.sqlite3")
cursor = db.cursor()

# get the data on the language
with open(OUT, encoding='utf8') as f:
    query = f.read()

cursor.execute(query)
table = cursor.fetchall()

header = ["Count", "Language", "Glottocode", "Longitude", "Latitude", "Family"]

print(tabulate(
    table[:10],
    tablefmt="pipe",
    headers=header)
    )

with open('lb_1.tsv', 'w', encoding='utf8', newline='') as f:
    writer = csv.writer(f, delimiter='\t')
    writer.writerow(header)
    writer.writerows(table)
