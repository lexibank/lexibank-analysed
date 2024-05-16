from pycldf import iter_datasets


def test_valid(cldf_dataset, cldf_logger):
    for ds in iter_datasets(cldf_dataset.directory):
        assert ds.validate(log=cldf_logger)
