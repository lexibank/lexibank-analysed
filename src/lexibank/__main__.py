"""
Main command line interface to the lexibank package.
"""
import sys
import pathlib
import contextlib

from cldfcatalog import Config, Catalog
from clldutils.clilib import register_subcommands, get_parser_and_subparsers, ParserError, PathType
from clldutils.loglib import Logging
from pyclts import CLTS

import lexibank.commands
from lexibank import LexiBank


def main(args=None, catch_all=False, parsed_args=None):
    try:  # pragma: no cover
        repos = Config.from_file().get_clone('clts')
    except KeyError:  # pragma: no cover
        repos = pathlib.Path('.')

    parser, subparsers = get_parser_and_subparsers('lexibank')
    parser.add_argument(
        '--clts',
        help="clone of clts",
        default=repos,
        type=PathType(type='dir'))
    parser.add_argument(
        '--clts-version',
        help="version of clts data. Requires a git clone!",
        default=None)
    parser.add_argument(
        '--datasets',
        default=pathlib.Path('datasets'),
        type=PathType(type='dir'),
        help="folder containing the datasets")
    parser.add_argument(
        "--repos",
        default=pathlib.Path("./"),
        type=PathType(type="dir"),
        help="path to lexibank repository"
        )

    register_subcommands(subparsers, lexibank.commands)

    args = parsed_args or parser.parse_args(args=args)
    if not hasattr(args, "main"):  # pragma: no cover
        parser.print_help()
        return 1

    args.api = LexiBank(repos=args.repos, datasets=args.datasets)
    with contextlib.ExitStack() as stack:
        stack.enter_context(Logging(args.log, level=args.log_level))
        if args.clts_version:  # pragma: no cover
            # If a specific version of the data is to be used, we make
            # use of a Catalog as context manager:
            stack.enter_context(Catalog(args.clts, tag=args.clts_version))
        args.clts = CLTS(args.clts)
        args.log.info('clts at {0}'.format(args.clts))
        try:
            return args.main(args) or 0
        except KeyboardInterrupt:  # pragma: no cover
            return 0
        except ParserError as e:  # pragma: no cover
            print(e)
            return main([args._command, '-h'])
        except Exception as e:  # pragma: no cover
            if catch_all:  # pragma: no cover
                print(e)
                return 1
            raise


if __name__ == '__main__':  # pragma: no cover
    sys.exit(main() or 0)
