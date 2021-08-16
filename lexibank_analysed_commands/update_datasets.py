"""
Re-download `etc/lexibank.csv`.
"""
from cldfbench.cli_util import with_dataset, add_dataset_spec
from collabutils.googlesheets import Spreadsheet


def register(parser):
    add_dataset_spec(parser)
    parser.add_argument(
        '--doc-key',
        help='Google Docs ID of the spreadsheet',
        action='store',
        default='1x8c_fuWkUYpDKedn2mNkKFxpwtHCFAOBUeRT8Mihy3M')


def _run(dataset, args):
    Spreadsheet(args.doc_key).fetch_sheets(
        {'datasets': 'lexibank.csv'},
        dataset.etc_dir)


def run(args):
    with_dataset(args, _run)
