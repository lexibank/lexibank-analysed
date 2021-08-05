import collections
import io
import itertools
import json
import pathlib
import re
import textwrap
import urllib.request
import zipfile
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup as bs
import requests

import pycldf
from cldfbench import CLDFSpec
from cldfbench import Dataset as BaseDataset
from clldutils.misc import nfilter
from clldutils.path import readlines
from cltoolkit import Wordlist
from cltoolkit.features import FEATURES
from pyclts import CLTS
from git import Repo, GitCommandError
from tqdm import tqdm
from csvw.metadata import Link

CLTS_2_1 = (
    "https://zenodo.org/record/4705149/files/cldf-clts/clts-v2.1.0.zip?download=1",
    'cldf-clts-clts-04f04e3')
_loaded = {}

OAI_PMH_URL = 'https://zenodo.org/oai2d?verb=ListRecords&set=user-lexibank&metadataPrefix=oai_dc'
RESUME_URL = 'https://zenodo.org/oai2d?verb=ListRecords&resumptionToken={}'
RECORD_TAG = '{http://www.openarchives.org/OAI/2.0/oai_dc/}dc'
ID_TAG = '{http://purl.org/dc/elements/1.1/}identifier'
REL_TAG = '{http://purl.org/dc/elements/1.1/}relation'


def parse_oai_record(record):
    for id_ in record.iter(ID_TAG):
        if id_.text.startswith('10.5281/zenodo.'):
            doi = id_.text
            break
    else:
        return None

    for rel in record.iter(REL_TAG):
        match = re.fullmatch(
            r'url:https://github\.com/([^/]+)/([^/]+)/tree/([^/]+)',
            rel.text)
        if match:
            gh_orga, gh_repo, gh_tag = match.groups()
            break
    else:
        return None

    return doi, {'orga': gh_orga, 'repo': gh_repo, 'tag': gh_tag}


class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "lexibank-analysed"

    def cldf_specs(self):
        return {
            'phonology': CLDFSpec(
                metadata_fname='phonology-metadata.json',
                data_fnames=dict(
                    ParameterTable='phonology-features.csv',
                    ValueTable='phonology-values.csv',
                    CodeTable='phonology-codes.csv',
                ),
                dir=self.cldf_dir, module="StructureDataset"),
            'lexicon': CLDFSpec(
                metadata_fname='lexicon-metadata.json',
                data_fnames=dict(
                    ParameterTable='lexicon-features.csv',
                    ValueTable='lexicon-values.csv',
                    CodeTable='lexicon-codes.csv',
                ),
                dir=self.cldf_dir, module="StructureDataset"),
            'phonemes': CLDFSpec(
                metadata_fname='phonemes-metadata.json',
                data_fnames=dict(
                    ParameterTable='phonemes.csv',
                    ValueTable='frequencies.csv',
                ),
                dir=self.cldf_dir, module="StructureDataset"),
        }

    def cmd_download(self, args):
        github_info = collections.OrderedDict()

        next_url = OAI_PMH_URL
        while next_url:
            response = ET.fromstring(requests.get(next_url).text)
            github_info.update(
                filter(
                    None,
                    map(parse_oai_record, response.iter(RECORD_TAG))))

            token_list = response.findall(
                './{http://www.openarchives.org/OAI/2.0/}ListRecords'
                '/{http://www.openarchives.org/OAI/2.0/}resumptionToken')
            if token_list:
                next_url = RESUME_URL.format(token_list[0].text)
            else:
                next_url = ''

        def get_ghinfo(row):
            return (
                github_info.get(row.get('Zenodo'))
                or {'orga': row['Organization'], 'repo': row['Dataset']})
        datasets = collections.OrderedDict(
            (row['Dataset'], get_ghinfo(row))
            for row in self.etc_dir.read_csv('lexibank.tsv', delimiter='\t', dicts=True)
            if row['LexiCore'].strip() or row['ClicsCore'].strip())

        for dataset, ghinfo in datasets.items():
            args.log.info("Checking {}".format(dataset))
            dest = self.raw_dir / dataset

            # download data
            if dest.exists():
                args.log.info("... dataset already exists.  pulling changes.")
                for remote in Repo(str(dest)).remotes:
                    remote.fetch()
            else:
                args.log.info("... cloning {}".format(dataset))
                try:
                    Repo.clone_from(
                        "https://github.com/{}/{}.git".format(ghinfo['orga'], ghinfo['repo']),
                        str(dest))
                except GitCommandError as e:
                    args.log.error("... download failed\n{}".format(str(e)))
                    continue

            # check out release (fall back to master branch)
            repo = Repo(str(dest))
            if 'tag' in ghinfo:
                args.log.info('... checking out tag {}'.format(ghinfo['tag']))
                repo.git.checkout(ghinfo['tag'])
            else:
                args.log.info('... checking out master')
                try:
                    branch = repo.branches.main
                    branch.checkout()
                except AttributeError:
                    try:
                        branch = repo.branches.master
                        branch.checkout()
                    except AttributeError:
                        args.log.error('found neither main nor master branch')
                repo.git.merge()

        with self.raw_dir.temp_download(CLTS_2_1[0], 'ds.zip', log=args.log) as zipp:
            zipfile.ZipFile(str(zipp)).extractall(self.raw_dir)

    def load_data(self, set_=None):
        """
        Load all datasets from a defined group of datasets.
        """
        ds_specs = collections.OrderedDict([
            (r['Dataset'], r)
            for r in self.etc_dir.read_csv('lexibank.tsv', delimiter='\t', dicts=True)])
        if set_:
            dss = nfilter(readlines(self.etc_dir / '{}.txt'.format(set_), strip=True))
        else:
            dss = list(ds_specs.keys())

        res = []
        for ds in dss:
            if ds not in _loaded:
                _loaded[ds] = (
                    pycldf.Dataset.from_metadata(self.raw_dir / ds / "cldf" / "cldf-metadata.json"),
                    ds_specs[ds])
            res.append(_loaded[ds][0])
        return res

    def cmd_makecldf(self, args):
        languages = collections.OrderedDict()

        def _add_features(writer, features):
            for feature in features:
                writer.objects['ParameterTable'].append(dict(
                    ID=feature.id,
                    Name=feature.name,
                    Description=feature.doc,
                    Feature_Spec=feature.to_json(),
                ))
                if feature.categories:
                    for k, v in feature.categories.items():
                        writer.objects['CodeTable'].append(dict(
                            Parameter_ID=feature.id,
                            ID='{}-{}'.format(feature.id, k),
                            Name=v,
                        ))

        def _add_language(writer, language, features, attr_features):
            l = {
                "ID": language.id,
                "Name": language.name,
                "Glottocode": language.glottocode,
                "Dataset": language.dataset,
                "Latitude": language.latitude,
                "Longitude": language.longitude,
                "Subgroup": language.subgroup,
                "Family": language.family,
            }
            languages[language.id] = l
            writer.objects['LanguageTable'].append(l)
            for attr in attr_features:
                writer.objects['ValueTable'].append(dict(
                    ID='{}-{}'.format(language.id, attr),
                    Language_ID=language.id,
                    Parameter_ID=attr,
                    Value=len(getattr(language, attr))
                ))
            for feature in features:
                v = feature(language)
                if feature.categories:
                    assert v in feature.categories, '{}: "{}"'.format(feature.id, v)
                writer.objects['ValueTable'].append(dict(
                    ID='{}-{}'.format(language.id, feature.id),
                    Language_ID=language.id,
                    Parameter_ID=feature.id,
                    Value=v,
                    Code_ID='{}-{}'.format(feature.id, v) if feature.categories else None,
                ))

        def _add_languages(writer, wordlist, condition, features, attr_features):
            for language in tqdm(wordlist.languages, desc='computing features'):
                if language.name == None or language.name == "None":
                    args.log.warning('{0.dataset}: {0.id}: {0.name}'.format(language))
                    continue
                if language.latitude and condition(language):
                    _add_language(writer, language, features, attr_features)
                    yield language

        with self.cldf_writer(args, cldf_spec='phonology') as writer:
            # FIXME: work around cldfbench bug (can't rename core table of a module!):
            writer.cldf['ValueTable'].url = Link('phonology-values.csv')
            writer.cldf.add_component('LanguageTable', 'Dataset', 'Subgroup', 'Family')
            writer.cldf.add_columns(
                'ParameterTable',
                {"name": "Feature_Spec", "datatype": "json"},
            )

            features = [f for f in FEATURES if f.function.__module__.endswith("phonology")]

            for fid, fname, fdesc in [
                ('concepts', 'Number of concepts', 'Number of senses linked to Concepticon'),
                ('forms', 'Number of forms', ''),
                ('bipa_forms', 'Number of BIPA conforming forms', ''),
                ('senses', 'Number of senses', ''),
            ]:
                writer.objects['ParameterTable'].append(
                    dict(ID=fid, Name=fname, Description=fdesc))
            _add_features(writer, features)

            sounds = collections.defaultdict(collections.Counter)
            for language in _add_languages(
                writer,
                Wordlist(datasets=self.load_data('lexicore'), ts=CLTS(self.raw_dir / CLTS_2_1[1]).bipa),
                lambda l: len(l.bipa_forms) >= 80,
                features,
                ['concepts', 'forms', 'bipa_forms', 'senses'],
            ):
                for sound in language.sound_inventory.segments:
                    sounds[(sound.obj.name.replace(' ', '_'), sound.obj.s)][language.id] = len(sound.occs)

        with self.cldf_writer(args, cldf_spec='lexicon', clean=False) as writer:
            # FIXME: work around cldfbench bug (can't rename core table of a module!):
            writer.cldf['ValueTable'].url = Link('lexicon-values.csv')
            writer.cldf.add_component('LanguageTable', 'Dataset', 'Subgroup', 'Family')
            writer.cldf.add_columns(
                'ParameterTable',
                {"name": "Feature_Spec", "datatype": "json"},
            )
            features = [f for f in FEATURES if f.function.__module__.endswith("lexicon")]

            for fid, fname, fdesc in [
                ('concepts', 'Number of concepts', 'Number of senses linked to Concepticon'),
                ('forms', 'Number of forms', ''),
                ('senses', 'Number of senses', ''),
            ]:
                writer.objects['ParameterTable'].append(
                    dict(ID=fid, Name=fname, Description=fdesc))
            _add_features(writer, features)
            _ = list(_add_languages(
                writer,
                Wordlist(datasets=self.load_data('clics')),
                lambda l: len(l.concepts) >= 250,
                features,
                ['concepts', 'forms', 'senses']))

        with self.cldf_writer(args, cldf_spec='phonemes', clean=False) as writer:
            #
            # FIXME: work around cldfbench bug (can't rename core table of a module!):
            writer.cldf['ValueTable'].url = Link('frequencies.csv')
            #
            writer.cldf.add_columns('ParameterTable', 'cltsReference')
            writer.cldf.add_component('LanguageTable', 'Dataset', 'Subgroup', 'Family')
            writer.objects['LanguageTable'] = languages.values()
            for clts_id, glyphs in itertools.groupby(sorted(sounds.keys()), lambda k: k[0]):
                glyphs = [g[1] for g in glyphs]
                occs = collections.Counter()
                for glyph in glyphs:
                    occs.update(**sounds[clts_id, glyph])

                writer.objects['ParameterTable'].append(dict(
                    ID=clts_id,
                    Name=' / '.join(glyphs),
                    CLTS_ID=clts_id,
                ))
                for lid, freq in occs.items():
                    writer.objects['ValueTable'].append(dict(
                        ID='{}-{}'.format(lid, clts_id),
                        Language_ID=lid,
                        Parameter_ID=clts_id,
                        Value=freq,
                    ))
