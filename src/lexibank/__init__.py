from pathlib import Path
from cltoolkit.util import datasets_by_id
from pycldf import Dataset
from clldutils.apilib import API
from csvw.dsv import UnicodeDictReader

__version__ = "0.1.0.dev0"

pkg_path = Path(__file__).parent

def lexicore_data(datadir):
    """
    Load all datasets currently defined as lexicore datasets.
    """
    with open(pkg_path.joinpath("data", "lexicore.txt")) as f:
        datasets = [row for row in (row.strip() for row in f) if row]
    return [Dataset.from_metadata(Path(datadir, ds, "cldf",
        "cldf-metadata.json")) for ds in datasets]


def clics_data(datadir):
    """
    Load all datasets currently defined as CLICS datasets.
    """
    with open(pkg_path.joinpath("data", "clics.txt")) as f:
        datasets = [row.strip() for row in f.readlines()]
    return [Dataset.from_metadata(Path(datadir, ds, "cldf",
        "cldf-metadata.json")) for ds in datasets]

def lexibank_data():
    with UnicodeDictReader(pkg_path.joinpath("data", "lexibank.tsv"), delimiter="\t") as reader:
        data = []
        for row in reader:
            data += [row]
    return data


class LexiBank(API):

    def __init__(self, repos=None, datasets=None):
        API.__init__(self, repos)
        self.datadir = datasets
