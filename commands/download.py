from lexibank import pkg_path
from git import Repo, GitCommandError
from csvw.dsv import UnicodeDictReader

def download():
    with UnicodeDictReader(pkg_path.joinpath("lexibank.tsv"), delimiter="\t") as reader:
        data = []
        for row in reader:
            data += [row]

    for row in data:
        print("Downloading {0}".format(row["Dataset"]))
        try:
            Repo.clone_from(
                    "https://github.com/{0}/{1}.git".format(
                        row["Organization"],
                        row["Dataset"]
                        ),
                    pkg_path.joinpath("datasets", row["Dataset"]).as_posix()
                    )
        except GitCommandError:
            print("... dataset already exists.")
