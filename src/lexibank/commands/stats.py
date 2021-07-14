"""
Compute summary statistics for data.
"""

from cltoolkit import Wordlist
import lexibank
from collections import defaultdict


def register(parser):
    parser.add_argument(
        "--datadir", help="destination of your datasets", action="store", default="datasets"
    )


def run(args):
    # TODO: Distinguish by Wordlist type (transcribed, large, with proto-forms, etc)
    # TODO: output (Markdown) table

    lexicore = Wordlist(datasets=lexibank.lexicore_data(args.datadir))
    languages = defaultdict(list)
    senses = set()
    concepts = defaultdict(list)
    forms = []

    for language in lexicore.languages:
        languages[language.name].append(language.id)

    for sense in lexicore.senses:
        senses.add(sense.id)

    for concept in lexicore.concepts:
        concepts[concept.concepticon_gloss].append(concept.senses)

    for form in lexicore.forms:
        forms.append(form)

    print("Number of languages:", len(languages))
    print("Number of senses:", len(senses))
    print("Number of concepts:", len(concepts))
    print("Number of forms:", len(forms))
