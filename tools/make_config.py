#!/usr/bin/env python

import argparse
import os


def make_config(root, force=False):
    existing_config = False
    try:
        import dataconfig  # noqa: F401
        existing_config = True
    except ImportError:
        pass
    if not root:
        raise ValueError('Must provide Root directory. See help')
    if not os.path.exists(root):
        raise ValueError(
            'Path {} does not exist on local machine'.format(root))
    # if not os.path.exists(os.path.join(root, 'ess')):
    #     raise ValueError(
    #         'Bad path {}. Expected directory to contain ess directory'.format(
    #             root))
    if existing_config and not force:
        raise RuntimeError(
            'config.py already exists. cannot overwrite without force option. see help.'
        )
    # make the config.py
    with open('dataconfig.py', 'w') as fh:
        fh.write('data_root="{}"\n'.format(root))
    print('dataconfig.py written')


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="Makes local non-versioned dataconfig.py "
        "for working with ess notebook data. "
        "Test data directory found "
        "https://public.esss.dk/groups/scipp/ess-notebooks "
        "is assumed to be checked out locally. "
        "Generates valid dataconfig.py with the "
        "correct local paths set.",
        prog='make_config')
    positional_args = parser.add_argument_group('Positional arguments')
    optional_args = parser.add_argument_group('Optional arguments')
    positional_args.add_argument(
        'Root',
        nargs='?',
        help="The absolute path to root directory "
        "of the cloned ess-notebooks-data repository.")
    optional_args.add_argument('-f',
                               '--force',
                               action='store_true',
                               default=False,
                               help='Force overwrite of existing config')
    # run the arg parser
    arguments = parser.parse_args()
    make_config(root=arguments.Root, force=arguments.force)
