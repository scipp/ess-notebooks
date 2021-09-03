# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2021 Scipp contributors (https://github.com/scipp)

import os
from pathlib import Path
import scippbuildtools as sbt

if __name__ == '__main__':
    args, _ = sbt.docs_argument_parser().parse_known_args()
    docs_dir = str(Path(__file__).parent.absolute())
    # Convert Namespace object `args` to a dict with `vars(args)`
    builder = sbt.DocsBuilder(docs_dir=docs_dir, **vars(args))

    if not args.no_setup:
        builder.download_test_data(tar_name="ess-notebooks.tar.gz")
        builder.make_mantid_config(
            content="\nusagereports.enabled=0\ndatasearch.directories={}\n"
            "logging.loggers.root.level=error\n".format(
                os.path.join(builder._data_dir, "ess-notebooks")))
        # Run the make_config to configure data directories
        sys.path.append(os.path.join(docs_dir, '..', 'tools'))
        from make_config import make_config
        make_config(root=data_dir)

    if 'PYTHONPATH' in os.environ:
        os.environ['PYTHONPATH'] += ':' + str(docs_dir)
    else:
        os.environ['PYTHONPATH'] = str(docs_dir)

    builder.run_sphinx(builder=args.builder, docs_dir=docs_dir)
