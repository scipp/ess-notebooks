# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2021 Scipp contributors (https://github.com/scipp)
try:
    from scippbuildtools.sphinxconf import *  # noqa: E402, F401, F403
except ImportError:
    pass

project = u'ess-notebooks'

nbsphinx_prolog = nbsphinx_prolog.replace("XXXX",
                                          "ess-notebooks")  # noqa: F405
