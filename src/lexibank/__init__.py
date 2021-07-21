import pathlib
import functools

from pycldf import Dataset
from clldutils.apilib import API
from clldutils.path import readlines
from clldutils.misc import nfilter
from clldutils.clilib import PathType
from csvw.dsv import reader

__version__ = "0.1.0.dev0"

pkg_path = pathlib.Path(__file__).parent


def add_datadir(parser):
    parser.add_argument(
        '--datadir',
        help='directory where the datasets are located',
        type=PathType(type='dir'),
        default=pathlib.Path("datasets"),
    )


def _data(set_, datadir):
    """
    Load all datasets from a defined group of datasets.
    """
    return [
        Dataset.from_metadata(pathlib.Path(datadir, ds, "cldf", "cldf-metadata.json"))
        for ds in nfilter(readlines(pkg_path / 'data' / '{}.txt'.format(set_), strip=True))]


lexicore_data = functools.partial(_data, 'lexicore')
clics_data = functools.partial(_data, 'clics')


def lexibank_data():
    return list(reader(pkg_path.joinpath("data", "lexibank.tsv"), delimiter="\t", dicts=True))


class LexiBank(API):
    def __init__(self, repos=None, datasets=None):
        API.__init__(self, repos)
        self.datadir = datasets
