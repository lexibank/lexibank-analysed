from pathlib import Path
from cltoolkit.util import datasets_by_id
from pycldf import Dataset

__version__ = "0.1.0.dev0"

pkg_path = Path(__file__).parent

def lexicore_data():
    """
    Load all datasets currently defined as lexicore datasets.
    """
    with open(pkg_path.joinpath("lexicore.txt")) as f:
        datasets = [row.strip() for row in f.readlines()]
    return [Dataset.from_metadata(pkg_path.joinpath("datasets", ds, "cldf",
        "cldf-metadata.json")) for ds in datasets]


def clics_data():
    """
    Load all datasets currently defined as CLICS datasets.
    """
    with open(pkg_path.joinpath("clics.txt")) as f:
        datasets = [row.strip() for row in f.readlines()]
    return [Dataset.from_metadata(pkg_path.joinpath("datasets", ds, "cldf",
        "cldf-metadata.json")) for ds in datasets]



