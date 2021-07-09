# Temporarily taken from cldf-buildbot:

import re
import json
import base64
import pathlib

from github import Github, GithubException

ORGS = [
    'lexibank',
    'numeralbank',
    'cldf-datasets',
    'dictionaria',
    'intercontinental-dictionary-series',
]


def cldfbench_curated(repo):
    curator_pattern = re.compile(
        r"""["'](?P<curator>lexibank|cldfbench|international-dictionary-series)\.dataset["']""")
    for f in repo.get_contents('.'):
        if f.name == 'setup.py':
            match = curator_pattern.search(base64.b64decode(f.content).decode('utf8'))
            if match:
                return match.group('curator')


def iter_repos(gh):
    for org in ORGS:
        for repo in gh.get_organization(org).get_repos():
#            if repo.private:
#                continue
            try:
                yield (
                    org,
                    repo.clone_url,
                    [f.path for f in repo.get_contents('cldf') if f.name.endswith('metadata.json')],
                    cldfbench_curated(repo)
                )
            except GithubException:
                continue


def main(gh):
    with pathlib.Path('reposlist.json').open('w', encoding='utf8') as fp:
        json.dump(
            [repo for repo in sorted(iter_repos(gh), key=lambda t: (t[0], t[1])) if repo[2]],
            fp,
            indent=4)


if __name__ == '__main__':
    import sys

    main(Github(sys.argv[1]))
