# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import sys
# sys.path.insert(0, os.path.abspath('.'))
import doctest
import sphinx_rtd_theme
# -- Project information -----------------------------------------------------

project = u'ess-notebooks'
copyright = u'2021 Scipp contributors'
copyright = u'Scipp contributors'

# The full version, including alpha/beta/rc tags
version = u''
release = u''

html_show_sourcelink = True
nbsphinx_prolog = (
    "`Download this Jupyter notebook "
    "<https://raw.githubusercontent.com/scipp/ess-notebooks/main/docs/"
    "{{ env.doc2path(env.docname, base=None) }}>`_")

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc', 'sphinx.ext.autosummary', 'sphinx.ext.intersphinx',
    'sphinx.ext.mathjax', 'sphinx.ext.doctest',
    'IPython.sphinxext.ipython_directive',
    'IPython.sphinxext.ipython_console_highlighting', 'nbsphinx'
]

templates_path = ['_templates']

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '**.ipynb_checkpoints']

# -- Options for HTML output -------------------------------------------------

html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

html_context = {'css_files': ['_static/theme_overrides.css']}

html_theme_options = {'logo_only': True}

html_logo = "_static/logo.png"
html_favicon = "_static/favicon.ico"

html_static_path = ['_static']

# -- Options for Matplotlib in notebooks ----------------------------------

nbsphinx_execute_arguments = [
    "--Session.metadata=scipp_docs_build=True",
]

# -- Options for doctest --------------------------------------------------

doctest_global_setup = '''
import numpy as np
import scipp as sc
'''

# Using normalize whitespace because many __str__ functions in scipp produce
# extraneous empty lines and it would look strange to include them in the docs.
doctest_default_flags = doctest.ELLIPSIS | doctest.IGNORE_EXCEPTION_DETAIL | \
                        doctest.DONT_ACCEPT_TRUE_FOR_1 | \
                        doctest.NORMALIZE_WHITESPACE

# -- Options for linkcheck ------------------------------------------------

linkcheck_ignore = [
    # Specific lines in Github blobs cannot be found by linkcheck.
    r'https?://github\.com/.*?/blob/[a-f0-9]+/.+?#'
]
