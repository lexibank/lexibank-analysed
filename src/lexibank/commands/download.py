"""
Download the lexibank data.
"""
from lexibank import pkg_path
from pathlib import Path
from git import Repo, GitCommandError
from csvw.dsv import UnicodeDictReader

def register(parser):
    parser.add_argument(
        '--destination',
        help='destination of the data',
        action='store',
        default="datasets"
    )

def run(args):
    with UnicodeDictReader(pkg_path.joinpath("data", "lexibank.tsv"), delimiter="\t") as reader:
        data = []
        for row in reader:
            data += [row]

    for row in data:
        args.log.info("Checking {0}".format(row["Dataset"]))
        dest = Path(args.destination, row["Dataset"])
        if not row["LexiCore"].strip() and not row["ClicsCore"].strip():
            args.log.info("... skipping dataset.")
        elif dest.exists():
            args.log.info("... dataset already exists.")
        else:
            args.log.info("... cloning {0}".format(row["Dataset"]))
            try:
                Repo.clone_from(
                        "https://github.com/{0}/{1}.git".format(
                            row["Organization"],
                            row["Dataset"]
                            ),
                        dest.as_posix()
                        )
            except GitCommandError as e:
                args.log.error("... download failed\n{}".format(str(e)))
