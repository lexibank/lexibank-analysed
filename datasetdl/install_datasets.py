import json
import subprocess

from sys import argv

class Dataset:
    def __init__(self, org, clone_url, cldf_metadata, cldfbench_curator):
        self.url = clone_url
        self.org = org
        self.name = self.url.split("/")[-1].replace(".git", "")
        self.cldf_metadata = cldf_metadata
        self.cldfbench_curator = cldfbench_curator

with open('reposlist.json') as f:
    datasets = [Dataset(*args) for args in json.load(f)]

lexibank_datasets = [(lexibank.url, lexibank.name) for lexibank in datasets if lexibank.org == "lexibank"]
eggs = [f"git+{url}#egg=lexibank_{name}" for url, name in lexibank_datasets]

if "pipinstall" in argv:
    for egg in eggs:
        subprocess.run(["pip", "install", "-e", egg])

if "clone" in argv:
    for lexibank_dataset in lexibank_datasets:
        subprocess.run(["git", "clone", lexibank_dataset[0]])

