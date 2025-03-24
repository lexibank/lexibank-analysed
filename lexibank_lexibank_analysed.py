import pathlib
import zipfile
import itertools
import collections
import shutil
import json
import codecs
import nameparser
import attr

import pycldf
from tqdm import tqdm
import pylexibank.dataset
from pyclts import CLTS
from pylexibank import Lexeme, Concept, Language
from pylexibank.cldf import LexibankWriter
from pylexibank import Dataset as BaseDataset
from cldfbench import CLDFSpec
from cldfzenodo import API as cldfzenodoapi
from cltoolkit import Wordlist
from cltoolkit.features import FEATURES
from clldutils.misc import slug
from lingpy.sequence.sound_classes import prosodic_string

COLLECTIONS = {
    'LexiCore': (
        'Wordlists with phonetic transcriptions in which sound segments can be readily described '
        'by the CLTS system and in which at least 80 concepts can be linked to Concepticon.',
        'wordlists with phonetic transcriptions and at least 80 concepts)'),
    'ClicsCore': (
        'Wordlists with large form inventories in which at least 180 concepts can be linked to '
        'the Concepticon',
        'large wordlists with at least 180 concepts'),
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
        'all wordlists in the Lexibank collection'),
    "Selexion": (
        "Selection of one language per Glottocode, ranked by number of "
        "unique concepts mapped to Concepticon",
        "selected wordlists in Lexibank"),
}

CONDITIONS = {
    "LexiCore": lambda x: len(x.forms_with_sounds) >= 80 and len(x.concepts) >= 80,
    "ClicsCore": lambda x: len(x.forms_with_sounds) >= 180 and len(x.concepts) >= 180,
    "ProtoCore": lambda x: len(x.forms_with_sounds) >= 80 and len(x.concepts) >= 80,
    "CogCore": lambda x: len(x.forms_with_sounds) >= 80 and len(x.concepts) >= 80,
    "Lexibank": lambda x: len(x.forms_with_sounds) >= 80 and len(x.concepts) >= 80,
}

CLTS_2_3 = (
    "https://zenodo.org/records/10997741/files/cldf-clts/clts-v2.3.0.zip?download=1",
    'cldf-clts-clts-1c0b886')

_loaded = {}

LB_VERSION = "lexibank.tsv"


@attr.s
class CustomLexeme(Lexeme):
    CV_Template = attr.ib(default=None)
    Prosodic_String = attr.ib(default=None)
    Dolgo_Sound_Classes = attr.ib(default=None)
    SCA_Sound_Classes = attr.ib(default=None)


@attr.s
class CustomConcept(Concept):
    Central_Concept = attr.ib(default=None)
    Core_Concept = attr.ib(default=None)


@attr.s
class CustomLanguage(Language):
    Family_in_Data = attr.ib(default=None)
    Subgroup = attr.ib(default=None)
    Forms = attr.ib(default=None)
    FormsWithSounds = attr.ib(default=None)
    Concepts = attr.ib(default=None)
    Dataset = attr.ib(default=None)
    LexiCore = attr.ib(default=None)
    ClicsCore = attr.ib(default=None)
    CogCore = attr.ib(default=None)
    ProtoCore = attr.ib(default=None)
    Selexion = attr.ib(default=None)


class Dataset(BaseDataset):
    dir = pathlib.Path(__file__).parent
    id = "lexibank-analysed"
    lexeme_class = CustomLexeme
    concept_class = CustomConcept
    language_class = CustomLanguage

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
            if not row['Zenodo'].strip():
                continue
            row['collections'] = {key for key in COLLECTIONS if row.get(key, '').strip() == 'x'}
            if any(coll in row['collections'] for coll in ['LexiCore', 'ClicsCore']):
                res[row['Dataset']] = row
        return res

    def cmd_download(self, args):
        sources = pycldf.Sources.from_file(self.raw_dir / "base-sources.bib")
        for dataset, row in self.dataset_meta.items():
            dest = self.raw_dir / dataset
            if dest.exists():
                args.log.info(f'Removing old download in {dest}')
                shutil.rmtree(dest)

            args.log.info(f"Downloading {dataset}")
            record = cldfzenodoapi.get_record(row["Zenodo"])
            # check if record is most recent one
            rec_new = record.from_concept_doi(record.concept_doi)
            if rec_new.doi != record.doi:
                record = rec_new
                args.log.warn(f'DOI for datasets {row["ID"]} is not the latest version!')
            record.download(dest)

            # load zenodo info to make a new bibtex and doi
            with open(self.raw_dir / dataset / ".zenodo.json", encoding='utf8') as f:
                meta = json.load(f)
            editors = [c["name"] for c in meta["contributors"] if c["type"] == "Editor"]
            for i, editor in enumerate(editors):
                name = nameparser.HumanName(editor)
                first = name.first
                if name.middle:
                    first = " " + name.middle
                editors[i] = f"{name.last}, {first}"

            # load normal metadata to get the original citation
            with open(self.raw_dir / dataset / "metadata.json", encoding='utf8') as f:
                meta = json.load(f)
            description = meta["citation"]
            # create bibtex and write to new file
            bib = dict(
                author=" and ".join(record.creators),
                title=record.title,
                publisher="Zenodo",
                year=record.year,
                address="Geneva",
                doi=record.doi)
            if editors:
                bib["editor"] = " and ".join(editors)
            if description:
                bib["citation"] = description

            sources.add(pycldf.Source("book", row["ID"], **bib))

            # check if source is in sources
            for src_key in row["Source"].split(" "):
                if src_key not in sources:
                    args.log.warn(f"source with key '{src_key}' missing in data")

        with codecs.open(self.raw_dir / "sources.bib", "w", "utf-8") as f:
            for source in sources:
                f.write(source.bibtex() + "\n\n")

        with self.raw_dir.temp_download(CLTS_2_3[0], 'ds.zip', log=args.log) as zipp:
            zipfile.ZipFile(str(zipp)).extractall(self.raw_dir)

    def _iter_datasets(self, set_=None, with_metadata=False):
        """
        Load all datasets from a defined group of datasets.
        """
        dataset_meta = self.dataset_meta
        if set_ is None:
            dataset_ids = dataset_meta.keys()
        else:
            dataset_ids = [
                key
                for key, md in dataset_meta.items()
                if set_ in md['collections']]

        for dataset_id in dataset_ids:
            try:
                if dataset_id not in _loaded:
                    _loaded[dataset_id] = (
                        pycldf.Dataset.from_metadata(
                            self.raw_dir / dataset_id / "cldf" / "cldf-metadata.json"), dataset_meta[dataset_id])
                if with_metadata:
                    yield _loaded[dataset_id]
                else:
                    yield _loaded[dataset_id][0]
            except FileNotFoundError:
                print(f"Missing Dataset: {dataset_id}")

    def _schema(self, writer, with_stats=False, collstats=None):
        writer.cldf.add_component(
            'LanguageTable',
            {
                'name': 'Dataset',
                'propertyUrl': 'http://cldf.clld.org/v1.0/terms.rdf#contributionReference',
            },
            {'name': 'Forms', 'datatype': 'integer', 'dc:description': 'Number of forms'},
            {'name': "FormsWithSounds", "datatype": "integer", "dc:description": "Number of forms with sounds"},
            {'name': 'Concepts', 'datatype': 'integer', 'dc:description': 'Number of concepts'},
            {'name': 'Incollections', 'datatype': "string", "separator": " ",
             "dc:description": "Subselections of Lexibank"},
            'LexiCore',
            'ClicsCore',
            'CogCore',
            'ProtoCore',
            'Selexion',
            'Subgroup',
            'Family',
            'Family_in_Data')
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
            {
                "name": 'Source',
                "propertyUrl": "http://cldf.clld.org/v1.0/terms.rdf#source",
                "datatype": "string",
                "separator": ";",
            },
        )
        writer.cldf.add_foreign_key('ContributionTable', 'Collection_IDs', 'collections.csv', 'ID')

        if not with_stats:
            return
        for ds, md in tqdm(self._iter_datasets(with_metadata=True), desc='Computing summary stats'):
            langs = list(ds.iter_rows('LanguageTable', 'glottocode'))
            gcs = {lg['glottocode'] for lg in langs if lg['glottocode']}
            senses = list(ds.iter_rows('ParameterTable', 'concepticonReference'))
            csids = {sense['concepticonReference'] for sense in senses if sense['concepticonReference']}
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
                Source=md["Source"].split(),
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
        languoids = self.glottolog.cached_languoids
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
                            ID=f'{feature.id}-{k}',
                            Name=v,
                        ))

        def _add_language(writer, language, features, attr_features, collection='',
                          visited=None):
            if visited is None:
                visited = set()
            langs = languages.get(language.id)
            if not langs:
                try:
                    family = languoids[language.glottocode].family
                    langs = {
                        "ID": language.id,
                        "Name": language.name,
                        "Glottocode": language.glottocode,
                        "Dataset": language.dataset,
                        "Macroarea": language.macroarea,
                        "Latitude": language.latitude,
                        "Longitude": language.longitude,
                        "Subgroup": language.subgroup,
                        "Family": family.name if family else "",
                        "Family_in_Data": language.family,
                        "Forms": len(language.forms or []),
                        "FormsWithSounds": len(language.forms_with_sounds or []),
                        "Concepts": len(language.concepts),
                        "Incollections": [collection],
                        "LexiCore": 1 if self.dataset_meta[language.dataset]['LexiCore'] == 'x' and CONDITIONS['LexiCore'](language) else 0,
                        "ClicsCore": 1 if self.dataset_meta[language.dataset]['ClicsCore'] == 'x' and CONDITIONS['ClicsCore'](language) else 0,
                        "CogCore": 1 if self.dataset_meta[language.dataset]['CogCore'] == 'x' and CONDITIONS['CogCore'](language) else 0,
                        "ProtoCore": 1 if self.dataset_meta[language.dataset]['ProtoCore'] == 'x' and CONDITIONS['ProtoCore'](language) else 0,
                        "Selexion": 1 if 'Selexion' in [collection] else 0
                    }
                except KeyError:
                    args.log.warn(f"{language.name} / {language.dataset} / {language.glottocode}")
                    return False

            if language.id not in visited:
                for cid in ["ClicsCore", "LexiCore", "CogCore", "ProtoCore"]:
                    try:
                        if self.dataset_meta[language.dataset][cid] == 'x' and CONDITIONS[cid](language):
                            collstats[cid]["Glottocodes"].add(language.glottocode)
                            collstats[cid]["Varieties"] += 1
                            collstats[cid]["Forms"] += len(language.forms)
                            collstats[cid]["Concepts"].update(
                                concept.id for concept in language.concepts)
                    except KeyError:
                        print(f"problems with {language.dataset}")
                if CONDITIONS["Lexibank"](language):
                    collstats["Lexibank"]["Glottocodes"].add(language.glottocode)
                    collstats["Lexibank"]["Varieties"] += 1
                    collstats["Lexibank"]["Forms"] += len(language.forms)
                    collstats["Lexibank"]["Concepts"].update(
                        concept.id for concept in language.concepts)
                visited.add(language.id)
            languages[language.id] = langs
            writer.objects['LanguageTable'].append(langs)
            for attribute in attr_features:
                writer.objects['ValueTable'].append(dict(
                    ID=f'{language.id}-{attribute}',
                    Language_ID=language.id,
                    Parameter_ID=attribute,
                    Value=len(getattr(language, attribute)),
                ))
            for feature in features:
                v = feature(language)
                if feature.categories:
                    assert v in feature.categories, f'{feature.id}: "{v}"'
                writer.objects['ValueTable'].append(dict(
                    ID=f'{language.id}-{feature.id}',
                    Language_ID=language.id,
                    Parameter_ID=feature.id,
                    Value=v,
                    Code_ID=f'{feature.id}-{v}' if feature.categories else None,
                ))
            return True

        def _add_languages(writer, languages, condition, features, attr_features, collection='',
                           visited=None):
            if visited is None:
                visited = set()
            for language in tqdm(languages, desc='computing features'):
                if not language.name or not language.name.strip() or language.name == 'None':
                    args.log.warning(f'{language.dataset}: {language.id}: {language.name}')
                    continue
                if language.latitude and language.glottocode and condition(language):
                    if _add_language(writer, language, features, attr_features,
                                     collection=collection, visited=visited):
                        yield language

        # we add both the concepts and the forms, we add the languages later
        # via the LexiCore phonology module
        clts = CLTS(self.raw_dir / CLTS_2_3[1])
        with self.cldf_writer(args) as writer:
            # add sources, combine the lists
            writer.add_sources()
            # add concepts and the like
            wl = Wordlist(self._iter_datasets("LexiCore"), ts=clts.bipa)
            best_vars = collections.defaultdict(dict)
            var_count = 0
            for lng in wl.languages:
                if CONDITIONS["LexiCore"](lng) and lng.latitude and lng.glottocode in languoids:
                    fws = len(lng.forms_with_sounds)
                    var_count += 1
                    # add form count for sorting
                    best_vars[lng.glottocode][lng.id] = (fws, lng)
            args.log.info(f"found {len(best_vars)} different glottocodes with {var_count} varieties")

            visited_concepts = set()
            best_languages = {}
            excluded = []
            for glc in tqdm(best_vars, desc="add_forms"):
                _, best_language = max(best_vars[glc].values())
                for _, language in best_vars[glc].values():
                    if language.id == best_language.id:
                        best_languages[language.id] = language
                    duplicates = set()
                    for form in language.forms_with_sounds:
                        form_check = f"{form.concept.concepticon_id if form.concept else ''}-{str(form.sounds)}"
                        if form.concept and \
                                form.concept.concepticon_id and \
                                form.concept.concepticon_id in cid2gls and \
                                form_check not in duplicates:
                            duplicates.add(form_check)
                            cgls = cid2gls[form.concept.concepticon_id]
                            writer.add_form_with_segments(
                                Local_ID=form.id,
                                Parameter_ID=slug(cgls, lowercase=True),
                                Language_ID=language.id,
                                Value=form.value,
                                Form=form.form,
                                Segments=form.sounds,
                                CV_Template="".join(clts.soundclass("cv")(form.sounds)),
                                Prosodic_String="".join(
                                    prosodic_string(form.sounds, _output="CcV")),
                                Dolgo_Sound_Classes="".join(
                                    clts.soundclass("dolgo")(form.sounds)),
                                SCA_Sound_Classes="".join(
                                    clts.soundclass("sca")(form.sounds)),
                                Source=self.dataset_meta[language.dataset]["ID"],
                            )
                            visited_concepts.add(cgls)
                        elif form_check in duplicates:
                            excluded.append(form)
            args.log.info(f"excluded {len(excluded)} duplicates")
            with open(self.raw_dir / "duplicates.md", "w", encoding='utf8') as f:
                f.write("# Duplicates\n\n")
                f.write("ID | Language | Concept | Form | Sounds \n")
                f.write("--- | --- | --- | --- | ---\n")
                for form in excluded:
                    f.write(" | ".join([
                        form.id,
                        form.language.name,
                        form.concept.concepticon_gloss,
                        form.form, str(form.sounds)]) + "\n")

            args.log.info('added lexibank forms')
            # retrieve central concept from Rzymski concept list
            central_concepts = {
                cid2gls[c.concepticon_id]: c.attributes["central_concept"]
                for c in self.concepticon.conceptlists["Rzymski-2020-1624"].concepts.values()
                if c.concepticon_id}
            base_concepts = {c: [] for c in cid2gls.values()}
            for clist in [
                    "Swadesh-1952-200",
                    "Swadesh-1955-100",
                    "Starostin-1991-110",
                    "Tadmor-2009-100",
                    "Holman-2008-40"]:
                for c in self.concepticon.conceptlists[clist].concepts.values():
                    if c.concepticon_id and c.concepticon_id in cid2gls:
                        base_concepts[cid2gls[c.concepticon_id]].append(clist)

            for concept in wl.concepts:
                if concept.concepticon_id in cid2gls:
                    cgls = cid2gls[concept.concepticon_id]
                    if cgls in visited_concepts:
                        writer.add_concept(
                            ID=slug(cgls, lowercase=True),
                            Name=concept.concepticon_gloss,
                            Concepticon_ID=concept.concepticon_id,
                            Concepticon_Gloss=cgls,
                            Core_Concept=" ".join(
                                base_concepts.get(concept.concepticon_gloss, "")),
                            Central_Concept=central_concepts.get(concept.concepticon_gloss, ""))
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
                writer.objects['ParameterTable'].append(dict(ID=fid, Name=fname, Description=fdesc))
            _add_features(writer, features)

            sounds = collections.defaultdict(collections.Counter)
            for language in _add_languages(
                writer,
                list(wl.languages),
                CONDITIONS["LexiCore"],  # len(l.forms_with_sounds) >= 80,
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
                CONDITIONS["ClicsCore"],  # lambda l: len(l.concepts) >= 250,
                features,
                ['concepts', 'forms', 'senses'],
                collection='ClicsCore',
                visited=visited,
            ))

        with self.cldf_writer(args, cldf_spec='phonemes', clean=False) as writer:
            writer.cldf.add_columns('ParameterTable', 'cltsReference')

            # add information on included forms here +++
            args.log.info("write information on selected languages")
            for lid, language in languages.items():
                if lid in best_languages:
                    language["Incollections"] += ["Selexion"]
                    language["Selexion"] = 1
                    collstats["Selexion"]["Glottocodes"].add(best_languages[lid].glottocode)
                    collstats["Selexion"]["Varieties"] += 1
                    collstats["Selexion"]["Forms"] += len(best_languages[lid].forms)
                    collstats["Selexion"]["Concepts"].update(
                        concept.id for concept in best_languages[lid].concepts)
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
                        ID=f'{lid}-{clts_id}',
                        Language_ID=lid,
                        Parameter_ID=clts_id,
                        Value=freq,
                    ))
