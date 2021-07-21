"""
Download the lexibank data.
"""
from git import Repo, GitCommandError

from lexibank import lexibank_data, add_datadir


def register(parser):
    add_datadir(parser)


def run(args):
    for row in lexibank_data():
        args.log.info("Checking {0}".format(row["Dataset"]))
        dest = args.datadir / row["Dataset"]
        if not row["LexiCore"].strip() and not row["ClicsCore"].strip():
            args.log.info("... skipping dataset.")
        elif dest.exists():
            args.log.info("... dataset already exists.")
        else:
            args.log.info("... cloning {0}".format(row["Dataset"]))
            try:
                Repo.clone_from(
                    "https://github.com/{0}/{1}.git".format(row["Organization"], row["Dataset"]),
                    str(dest),
                )
            except GitCommandError as e:
                args.log.error("... download failed\n{}".format(str(e)))
