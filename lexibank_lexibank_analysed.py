import pathlib
import zipfile
import itertools
import collections

import pycldf
from cldfbench import CLDFSpec
from pylexibank.cldf import LexibankWriter
from pylexibank import Dataset as BaseDataset
import pylexibank.dataset
from cltoolkit import Wordlist
from cltoolkit.features import FEATURES
from cldfzenodo import oai_lexibank
from pyclts import CLTS
from git import Repo, GitCommandError
from tqdm import tqdm
from csvw.dsv import reader
import attr

from pylexibank import Lexeme, Concept

import lingpy
from clldutils.misc import slug

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
    'Lexibank': (
        'Metacollection of wordlists belonging to either of the datasets',
        'all wordlists in the Lexibank collection'
        ),
}
CONDITIONS = {
        "LexiCore": lambda x: len(x.forms_with_sounds) >= 100 and len(x.concepts) >= 100,
        "ClicsCore": lambda x: len(x.forms_with_sounds) >= 250 and len(x.concepts) >= 250,
        "ProtoCore": lambda x: len(x.forms_with_sounds) >= 100 and len(x.concepts) >= 100,
        "CogCore": lambda x: len(x.forms_with_sounds) >= 100 and len(x.concepts) >= 100,
        "Lexibank": lambda x: len(x.forms_with_sounds) >= 100 and len(x.concepts) >= 100
        }
CLTS_2_1 = (
    "https://zenodo.org/record/4705149/files/cldf-clts/clts-v2.1.0.zip?download=1",
    'cldf-clts-clts-04f04e3')
_loaded = {}

LB_VERSION = "lexibank-bliss.tsv"

@attr.s
class CustomLexeme(Lexeme):
    CV_Template = attr.ib(default=None)
    Sound_Classes = attr.ib(default=None)


@attr.s
class CustomConcept(Concept):
    Central_Concept = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "lexibank-analysed"
    lexeme_class = CustomLexeme
    concept_class = CustomConcept

    def cldf_specs(self):
        return {
            None: pylexibank.dataset.CLDFSpec(
                dir=self.cldf_dir,
                metadata_fname='wordlist-metadata.json',
                writer_cls=LexibankWriter,
                module="Wordlist",
                zipped=["FormTable"],
                data_fnames=dict(
                    ParameterTable="concepts.csv",
                    LanguageTable="languages.csv",
                    CognateTable="cognates.csv",
                    FormTable="forms.csv"
                    )),
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

    @property
    def dataset_meta(self):
        res = collections.OrderedDict()
        for row in self.etc_dir.read_csv(LB_VERSION, delimiter='\t', dicts=True):
            # uncomment below when having added all data to zenodo
            #if not row['Zenodo'].strip():
            #    continue
            row['collections'] = set(key for key in COLLECTIONS if row.get(key, '').strip() == 'x')
            if any(coll in row['collections'] for coll in ['LexiCore', 'ClicsCore']):
                res[row['Dataset']] = row
        return res

    def cmd_download(self, args):
        github_info = {rec.doi: rec.github_repos for rec in oai_lexibank()}

        for dataset, row in self.dataset_meta.items():
            ghinfo = github_info[row['Zenodo']]
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
                    Repo.clone_from(ghinfo.clone_url, str(dest))
                except GitCommandError as e:
                    args.log.error("... download failed\n{}".format(str(e)))
                    continue

            # check out release (fall back to master branch)
            repo = Repo(str(dest))
            if ghinfo.tag:
                args.log.info('... checking out tag {}'.format(ghinfo.tag))
                repo.git.checkout(ghinfo.tag)
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
            try:
                if ds not in _loaded:                    
                    _loaded[ds] = (
                        pycldf.Dataset.from_metadata(self.raw_dir / ds / "cldf" / "cldf-metadata.json"),
                        self.dataset_meta[ds])
                res.append(_loaded[ds]) if with_metadata else res.append(_loaded[ds][0])
            except FileNotFoundError:
                print("Missing Dataset: {0}".format(ds))

        return res

    def _schema(self, writer, with_stats=False, collstats=None):
        writer.cldf.add_component(
            'LanguageTable',
            {
                'name': 'Dataset',
                'propertyUrl': 'http://cldf.clld.org/v1.0/terms.rdf#contributionReference',
            },
            {'name': 'Forms', 'datatype': 'integer', 'dc:description': 'Number of forms'},
            {'name': "FormsWithSounds", "datatype": "integer",
                "dc:description": "Number of forms with sounds"},
            {'name': 'Concepts', 'datatype': 'integer', 'dc:description': 'Number of concepts'},
            {'name': 'Incollections'},
            'Subgroup',
            'Family')
        t = writer.cldf.add_table(
            'collections.csv',
            'ID',
            'Name',
            'Description',
            'Varieties',
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

        if not with_stats:
            return
        for ds, md in tqdm(self._datasets(with_metadata=True), desc='Computing summary stats'):
            langs = list(ds.iter_rows('LanguageTable', 'glottocode'))
            gcs = set(lg['glottocode'] for lg in langs if lg['glottocode'])
            senses = list(ds.iter_rows('ParameterTable', 'concepticonReference'))
            csids = set(sense['concepticonReference'] for sense in senses if sense['concepticonReference'])
            contrib = dict(
                ID=md['ID'],
                Name=ds.properties['dc:title'],
                Citation=ds.properties['dc:bibliographicCitation'],
                Collection_IDs=[key for key in COLLECTIONS if md.get(key, '').strip() == 'x'],
                Glottocodes=len(gcs),
                Doculects=len(langs),
                Concepts=len(csids),
                Senses=len(senses),
                Forms=len(list(ds['FormTable'])),
            )
            writer.objects['ContributionTable'].append(contrib)
        if collstats:
            for d in collstats.values():
                d['Glottocodes'] = len(d['Glottocodes'])
                d['Concepts'] = len(d['Concepts'])
                writer.objects['collections.csv'].append(d)

    def cmd_makecldf(self, args):
        cid2gls = {c.id: c.gloss for c in
                   self.concepticon.conceptsets.values()}
        visited = set()
        collstats = collections.OrderedDict()
        for cid, (desc, name) in COLLECTIONS.items():
            collstats[cid] = dict(
                ID=cid,
                Name=name,
                Description=desc,
                Varieties=0,
                Glottocodes=set(),
                Concepts=set(),
                Forms=0,
            )
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

        def _add_language(
                writer, language, features, attr_features,
                collection='', visited=set()):
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
                    "Forms": len(language.forms or []),
                    "FormsWithSounds": len(language.forms_with_sounds or []),
                    "Concepts": len(language.concepts),
                    "Incollections": collection,
                }
            else:
                l['Incollections'] = l['Incollections'] + collection
            if language.id not in visited:
                for cid in ["ClicsCore", "LexiCore", "CogCore", "ProtoCore"]:
                    try:
                        if self.dataset_meta[language.dataset][cid] == 'x' and CONDITIONS[cid](language):
                            collstats[cid]["Glottocodes"].add(language.glottocode)
                            collstats[cid]["Varieties"] += 1
                            collstats[cid]["Forms"] += len(language.forms)
                            collstats[cid]["Concepts"].update(
                                    [concept.id for concept in language.concepts])
                    except:
                        print("problems with {0}".format(language.dataset))
                if CONDITIONS["Lexibank"](language):
                    collstats["Lexibank"]["Glottocodes"].add(language.glottocode)
                    collstats["Lexibank"]["Varieties"] += 1
                    collstats["Lexibank"]["Forms"] += len(language.forms)
                    collstats["Lexibank"]["Concepts"].update(
                                    [concept.id for concept in language.concepts])
                visited.add(language.id)
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

        def _add_languages(writer, languages, condition, features,
                attr_features, collection='', visited=set([]), ):
            for language in tqdm(languages, desc='computing features'):
                if language.name == None or language.name == "None":
                    args.log.warning('{0.dataset}: {0.id}: {0.name}'.format(language))
                    continue
                if language.latitude and condition(language):
                    _add_language(writer, language, features, attr_features,
                            collection=collection, visited=visited)
                    yield language

        # we add both the concepts and the forms, we add the languages later
        # via the LexiCore phonology module
        clts = CLTS(self.raw_dir / CLTS_2_1[1])
        with self.cldf_writer(args) as writer:
            # add sources
            writer.add_sources()
            # add concepts and the like
            wl = Wordlist(self._datasets("LexiCore"), ts=clts.bipa)
            best_varieties = collections.defaultdict(dict)
            var_count = 0
            for lng in wl.languages:
                if CONDITIONS["LexiCore"](lng) and lng.latitude and lng.glottocode:
                    fws = len(lng.forms_with_sounds)
                    var_count += 1
                    best_varieties[lng.glottocode][lng.id] = (lng, fws)
            args.log.info("found {0} different glottocodes with {1} varieties".format(len(best_varieties), var_count))

            visited_concepts = set()
            for i, glc in tqdm(enumerate(best_varieties), desc="add_forms"):
                # select best variety
                language = sorted(best_varieties[glc].items(), key=lambda x: x[1][0], reverse=True)[0][1][0]
                print(language.id, language.dataset)
                for form in language.forms_with_sounds:
                    if form.concept and form.concept.concepticon_id and form.concept.concepticon_id in cid2gls:
                        cgls = cid2gls[form.concept.concepticon_id]
                        writer.add_form_with_segments(
                                Local_ID=form.id,
                                Parameter_ID=slug(cgls, lowercase=True),
                                Language_ID=language.id,
                                Value=form.value,
                                Form=form.form,
                                Segments=form.sounds,
                                CV_Template="".join(clts.soundclass("cv")(form.sounds)),
                                Sound_Classes="".join(clts.soundclass("dolgo")(form.sounds)),
                                Source=self.dataset_meta[language.dataset]["Source"].split(" ")
                                )
                        visited_concepts.add(cgls)
            args.log.info('added lexibank forms')
            # retrieve central concept from Rzymski concept list
            central_concepts = {
                    cid2gls[c.concepticon_id]: c.attributes["central_concept"] for c in
                    self.concepticon.conceptlists["Rzymski-2020-1624"].concepts.values()
                    if c.concepticon_id
                    }
            for concept in wl.concepts:
                if concept.concepticon_id in cid2gls:
                    cgls = cid2gls[concept.concepticon_id]
                    if cgls in visited_concepts:
                        writer.add_concept(
                                ID=slug(cgls, lowercase=True),
                                Name=concept.concepticon_gloss,
                                Concepticon_ID=concept.concepticon_id,
                                Concepticon_Gloss=cgls,
                                Central_Concept=central_concepts.get(concept.concepticon_gloss, "")
                                )
            args.log.info("added concepts for wordlist")

        with self.cldf_writer(args, cldf_spec='phonology', clean=False) as writer:
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
                [lng for lng in wl.languages], 
                CONDITIONS["LexiCore"], # len(l.forms_with_sounds) >= 80,
                features,
                ['concepts', 'forms', 'forms_with_sounds', 'senses'],
                collection='LexiCore',
                visited=visited
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
                [lng for lng in wl.languages if self.dataset_meta[lng.dataset]["ClicsCore"] == "x"],
                CONDITIONS["ClicsCore"], #lambda l: len(l.concepts) >= 250,
                features,
                ['concepts', 'forms', 'senses'],
                collection='ClicsCore',
                visited=visited,
            ))

        with self.cldf_writer(args, cldf_spec='phonemes', clean=False) as writer:
            writer.cldf.add_columns('ParameterTable', 'cltsReference')
            self._schema(writer, with_stats=True, collstats=collstats)
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
                for lid, freq in sorted(occurrences.items()):
                    writer.objects['ValueTable'].append(dict(
                        ID='{}-{}'.format(lid, clts_id),
                        Language_ID=lid,
                        Parameter_ID=clts_id,
                        Value=freq,
                    ))
