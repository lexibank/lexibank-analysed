from pycldf import iter_datasets, Dataset


def test_lexicon(cldf_dataset, cldf_logger):
    md = cldf_dataset.directory / 'lexicon-metadata.json'
    ds = Dataset.from_metadata(md)
    assert ds.validate(log=cldf_logger)


def test_phonemes(cldf_dataset, cldf_logger):
    md = cldf_dataset.directory / 'phonemes-metadata.json'
    ds = Dataset.from_metadata(md)
    assert ds.validate(log=cldf_logger)


def test_phonology(cldf_dataset, cldf_logger):
    md = cldf_dataset.directory / 'phonology-metadata.json'
    ds = Dataset.from_metadata(md)
    assert ds.validate(log=cldf_logger)


def test_wordlist(cldf_dataset, cldf_logger):
    md = cldf_dataset.directory / 'wordlist-metadata.json'
    ds = Dataset.from_metadata(md)
    assert ds.validate(log=cldf_logger)
