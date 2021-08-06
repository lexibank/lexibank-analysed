import re
import pathlib
import zipfile
import itertools
import collections
import xml.etree.ElementTree as ET

import requests

import pycldf
from cldfbench import CLDFSpec
from cldfbench import Dataset as BaseDataset
from clldutils.misc import lazyproperty
from cltoolkit import Wordlist
from cltoolkit.features import FEATURES
from pyclts import CLTS
from git import Repo, GitCommandError
from tqdm import tqdm

COLLECTIONS = {
    'LexiCore': (
        'Wordlists with phonetic transcriptions in which sound segments can be readily described '
        'by the CLTS system',
        'wordlists with phonetic transcriptions)'),
    'ClicsCore': (
        'Wordlists with large form inventories in which at least 250 concepts can be linked to '
        'the Concepticon',
        'large wordlists with at least 250 concepts'),
    'CogCore': (
        'Wordlists with phonetic transcriptions in which cognate sets have been annotated '
        '(a subset of LexiCore)',
        'wordlists with phonetic transcriptions and cognate sets'),
    'ProtoCore': (
        'Wordlists with phonetic transcriptions in which cognate sets have been annotated and '
        'which contain one or more ancestral languages whose forms are proto-forms from which '
        'forms in the descendant languages can be derived (a subset of CogCore)',
        'wordlists with phonetic transcriptions, cognate sets, and proto-languages'),
}
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

    @lazyproperty
    def dataset_meta(self):
        res = collections.OrderedDict()
        for row in self.etc_dir.read_csv('lexibank.tsv', delimiter='\t', dicts=True):
            if not row['Zenodo'].strip():
                continue
            row['collections'] = set(key for key in COLLECTIONS if row[key].strip() == 'x')
            if any(coll in row['collections'] for coll in ['LexiCore', 'ClicsCore']):
                res[row['Dataset']] = row
        return res

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
            (did, get_ghinfo(row)) for did, row in self.dataset_meta.items())

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
                args.log.warning('... could not determine tag to check out')
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

    def _datasets(self, set_=None, with_metadata=False):
        """
        Load all datasets from a defined group of datasets.
        """
        if set_:
            dss = [key for key, md in self.dataset_meta.items() if set_ in md['collections']]
        else:
            dss = list(self.dataset_meta.keys())

        res = []
        for ds in dss:
            if ds not in _loaded:
                _loaded[ds] = (
                    pycldf.Dataset.from_metadata(self.raw_dir / ds / "cldf" / "cldf-metadata.json"),
                    self.dataset_meta[ds])
            res.append(_loaded[ds]) if with_metadata else res.append(_loaded[ds][0])
        return res

    def _schema(self, writer, with_stats=False):
        writer.cldf.add_component(
            'LanguageTable',
            {
                'name': 'Dataset',
                'propertyUrl': 'http://cldf.clld.org//v1.0/terms.rdf#contributionReference',
            },
            {'name': 'Forms', 'datatype': 'integer', 'dc:description': 'Number of forms'},
            {'name': 'Concepts', 'datatype': 'integer', 'dc:description': 'Number of concepts'},
            {'name': 'Incollections'},
            'Subgroup',
            'Family')
        t = writer.cldf.add_table(
            'collections.csv',
            'ID',
            'Name',
            'Description',
            'Glottocodes',
            'Concepts',
            'Forms',
        )
        t.tableSchema.primaryKey = ['ID']
        writer.cldf.add_component(
            'ContributionTable',
            {'name': 'Collection_IDs', 'separator': ' '},
            'Glottocodes',
            'Doculects',
            'Concepts',
            'Senses',
            'Forms',
        )
        writer.cldf.add_foreign_key('ContributionTable', 'Collection_IDs', 'collections.csv', 'ID')

        collstats = collections.OrderedDict()
        for cid, (desc, name) in COLLECTIONS.items():
            collstats[cid] = dict(
                ID=cid,
                Name=name,
                Description=desc,
                Glottocodes=set(),
                Concepts=set(),
                Forms=0,
            )
        if not with_stats:
            return
        for ds, md in tqdm(self._datasets(with_metadata=True), desc='Computing summary stats'):
            langs = list(ds.iter_rows('LanguageTable', 'glottocode'))
            gcs = set(lg['glottocode'] for lg in langs if lg['glottocode'])
            senses = list(ds.iter_rows('ParameterTable', 'concepticonReference'))
            csids = set(sense['concepticonReference'] for sense in senses if sense['concepticonReference'])
            contrib = dict(
                ID=md['Dataset'],
                Name=ds.properties['dc:title'],
                Citation=ds.properties['dc:bibliographicCitation'],
                Collection_IDs=[key for key in COLLECTIONS if md.get(key).strip() == 'x'],
                Glottocodes=len(gcs),
                Doculects=len(langs),
                Concepts=len(csids),
                Senses=len(senses),
                Forms=len(list(ds['FormTable'])),
            )
            writer.objects['ContributionTable'].append(contrib)
            for key, stats in collstats.items():
                if key in md['collections']:
                    stats['Glottocodes'] = stats['Glottocodes'].union(gcs)
                    stats['Concepts'] = stats['Concepts'].union(csids)
                    stats['Forms'] += contrib['Forms']
        for d in collstats.values():
            d['Glottocodes'] = len(d['Glottocodes'])
            d['Concepts'] = len(d['Concepts'])
            writer.objects['collections.csv'].append(d)

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

        def _add_language(writer, language, features, attr_features, collection=''):
            l = languages.get(language.id)
            if not l:
                l = {
                    "ID": language.id,
                    "Name": language.name,
                    "Glottocode": language.glottocode,
                    "Dataset": language.dataset,
                    "Latitude": language.latitude,
                    "Longitude": language.longitude,
                    "Subgroup": language.subgroup,
                    "Family": language.family,
                    "Forms": len(language.forms_with_sounds or []),
                    "Concepts": len(language.concepts),
                    "Incollections": collection,
                }
            else:
                l['Incollections'] = l['Incollections'] + collection
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

        def _add_languages(writer, wordlist, condition, features, attr_features, collection=''):
            for language in tqdm(wordlist.languages, desc='computing features'):
                if language.name == None or language.name == "None":
                    args.log.warning('{0.dataset}: {0.id}: {0.name}'.format(language))
                    continue
                if language.latitude and condition(language):
                    _add_language(writer, language, features, attr_features, collection=collection)
                    yield language

        with self.cldf_writer(args, cldf_spec='phonology') as writer:
            self._schema(writer)
            writer.cldf.add_columns(
                'ParameterTable',
                {"name": "Feature_Spec", "datatype": "json"},
            )

            features = [f for f in FEATURES if f.function.__module__.endswith("phonology")]

            for fid, fname, fdesc in [
                ('concepts', 'Number of concepts', 'Number of senses linked to Concepticon'),
                ('forms', 'Number of forms', ''),
                ('forms_with_sounds', 'Number of BIPA conforming forms', ''),
                ('senses', 'Number of senses', ''),
            ]:
                writer.objects['ParameterTable'].append(
                    dict(ID=fid, Name=fname, Description=fdesc))
            _add_features(writer, features)

            sounds = collections.defaultdict(collections.Counter)
            for language in _add_languages(
                writer,
                Wordlist(datasets=self._datasets('LexiCore'), ts=CLTS(self.raw_dir / CLTS_2_1[1]).bipa),
                lambda l: len(l.forms_with_sounds) >= 80,
                features,
                ['concepts', 'forms', 'forms_with_sounds', 'senses'],
                collection='LexiCore',
            ):
                for sound in language.sound_inventory.segments:
                    sounds[(sound.obj.name.replace(' ', '_'), sound.obj.s)][language.id] = len(sound.occurrences)

        with self.cldf_writer(args, cldf_spec='lexicon', clean=False) as writer:
            self._schema(writer)
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
                Wordlist(datasets=self._datasets('ClicsCore')),
                lambda l: len(l.concepts) >= 250,
                features,
                ['concepts', 'forms', 'senses'],
                collection='ClicsCore',
            ))

        with self.cldf_writer(args, cldf_spec='phonemes', clean=False) as writer:
            writer.cldf.add_columns('ParameterTable', 'cltsReference')
            self._schema(writer, with_stats=True)
            writer.objects['LanguageTable'] = languages.values()
            for clts_id, glyphs in itertools.groupby(sorted(sounds.keys()), lambda k: k[0]):
                glyphs = [g[1] for g in glyphs]
                occurrences = collections.Counter()
                for glyph in glyphs:
                    occurrences.update(**sounds[clts_id, glyph])

                writer.objects['ParameterTable'].append(dict(
                    ID=clts_id,
                    Name=' / '.join(glyphs),
                    CLTS_ID=clts_id,
                ))
                for lid, freq in occurrences.items():
                    writer.objects['ValueTable'].append(dict(
                        ID='{}-{}'.format(lid, clts_id),
                        Language_ID=lid,
                        Parameter_ID=clts_id,
                        Value=freq,
                    ))
