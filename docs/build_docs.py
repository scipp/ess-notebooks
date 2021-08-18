# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2021 Scipp contributors (https://github.com/scipp)
# @author Neil Vaytet

import os
import argparse
import urllib
import requests
import re
from pathlib import Path
import subprocess
import sys

parser = argparse.ArgumentParser(description='Build doc pages with sphinx')
parser.add_argument('--prefix', default='build')
parser.add_argument('--work_dir', default='.doctrees')
parser.add_argument('--data_dir', default='data')
parser.add_argument('--builder', default='html')


def download_file(source, target):
    os.write(1, "Downloading: {}\n".format(source).encode())
    urllib.request.urlretrieve(source, target)


def make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


# def download_multiple(remote_url, target_dir, extensions):
#     """
#     Generate file list by parsing the html source of the web server and search
#     for links that include the relevant file extensions.
#     Then download all the files in the list.
#     """
#     make_dir(target_dir)
#     page_source = requests.get(remote_url).text
#     data_files = []
#     for ext in extensions:
#         for f in re.findall(r'href=.*{}">'.format(ext), page_source):
#             data_files.append(f.lstrip('href="').rstrip('">'))
#     for f in data_files:
#         target = os.path.join(target_dir, f)
#         # Note that only checking if file exists won't download new versions of
#         # files that are already on disk
#         if not os.path.isfile(target):
#             download_file(os.path.join(remote_url, f), target)


def download_multiple(remote_url, target_dir, extensions):
    """
    Generate file list by parsing the html source of the web server and search
    for links that include the relevant file extensions.
    Then download all the files in the list.
    """
    make_dir(target_dir)
    page_source = requests.get(remote_url).text
    data_files = []
    for f in re.findall(r'\[DIR\].*/"', page_source):
        dir_name = f.lstrip('[DIR]"></td><td><a href').lstrip('="').rstrip(
            '/"')
        download_multiple(os.path.join(remote_url, dir_name),
                          os.path.join(target_dir, dir_name), extensions)
    for ext in extensions:
        for f in re.findall(r'href=.*{}">'.format(ext), page_source):
            data_files.append(f.lstrip('href="').rstrip('">'))
    for f in data_files:
        target = os.path.join(target_dir, f)
        # Note that only checking if file exists won't download new versions of
        # files that are already on disk
        if not os.path.isfile(target):
            download_file(os.path.join(remote_url, f), target)


def get_abs_path(path, root):
    if os.path.isabs(path):
        return path
    else:
        return os.path.join(root, path)


if __name__ == '__main__':

    args = parser.parse_args()

    docs_dir = Path(__file__).parent.absolute()
    work_dir = get_abs_path(path=args.work_dir, root=docs_dir)
    prefix = get_abs_path(path=args.prefix, root=docs_dir)
    data_dir = get_abs_path(path=args.data_dir, root=docs_dir)

    # Download data files
    remote_url = "https://public.esss.dk/groups/scipp/ess-notebooks"
    extensions = [
        ".nxs", ".h5", ".hdf5", ".raw", ".dat", ".xml", ".txt", ".tiff"
    ]
    download_multiple(remote_url, data_dir, extensions)

    # Run the make_config to configure data directories
    sys.path.append(os.path.join(docs_dir, '..', 'tools'))
    from make_config import make_config
    make_config(root=data_dir)

    # Build the docs with sphinx-build
    status = subprocess.check_call(
        ['sphinx-build', '-b', args.builder, '-d', work_dir, docs_dir, prefix],
        stderr=subprocess.STDOUT,
        shell=sys.platform == "win32")
