# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2021 Scipp contributors (https://github.com/scipp)
# @author Neil Vaytet

import os
import argparse
import requests
from pathlib import Path
import subprocess
import sys
import tarfile

parser = argparse.ArgumentParser(description='Build doc pages with sphinx')
parser.add_argument('--prefix', default='build')
parser.add_argument('--work_dir', default='.doctrees')
parser.add_argument('--data_dir', default='data')
parser.add_argument('--builder', default='html')


def download_file(source, target):
    os.write(1, "Downloading: {}\n".format(source).encode())

    r = requests.get(source, stream=True)

    with open(target, "wb") as f:
        for chunk in r.iter_content(chunk_size=1_048_576):
            if chunk:
                f.write(chunk)


def make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)


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

    # Download and extract tarball containing data files
    tar_name = "ess-notebooks.tar.gz"
    remote_url = "https://public.esss.dk/groups/scipp"
    target = os.path.join(data_dir, tar_name)
    make_dir(data_dir)
    download_file(os.path.join(remote_url, tar_name), target)
    tar = tarfile.open(target, "r:gz")
    tar.extractall(path=data_dir)
    tar.close()

    # Run the make_config to configure data directories
    sys.path.append(os.path.join(docs_dir, '..', 'tools'))
    from make_config import make_config
    make_config(root=data_dir)

    # Create Mantid properties file so that it can find the data files.
    # Also turn off the logging so that it doesn't appear in the docs.
    home = str(Path.home())
    config_dir = os.path.join(home, ".mantid")
    make_dir(config_dir)
    properties_file = os.path.join(config_dir, "Mantid.user.properties")
    with open(properties_file, "a") as f:
        f.write("\nusagereports.enabled=0\ndatasearch.directories={}\n".format(
            data_dir))
        f.write("\nlogging.loggers.root.level=error\n")

    # Build the docs with sphinx-build
    status = subprocess.check_call(
        ['sphinx-build', '-b', args.builder, '-d', work_dir, docs_dir, prefix],
        stderr=subprocess.STDOUT,
        shell=sys.platform == "win32")
