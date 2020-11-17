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
import os
# -- Project information -----------------------------------------------------

project = u'ess-notebooks'
copyright = u'2020 scipp ess-notebooks contributors'
copyright = u'scipp ess-notebook contributors'

# The full version, including alpha/beta/rc tags
version = u''
release = u''

html_show_sourcelink = True
nbsphinx_prolog = """`Download this Jupyter notebook <https://raw.githubusercontent.com/scipp/ess-notebooks/master/{{ env.doc2path(env.docname, base=None) }}>`_"""


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ['sphinx.ext.autodoc', 'sphinx.ext.autosummary', 'sphinx.ext.intersphinx',
              'sphinx.ext.mathjax', 'IPython.sphinxext.ipython_directive',
              'IPython.sphinxext.ipython_console_highlighting', 'nbsphinx']

templates_path = ['_templates']

exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '**.ipynb_checkpoints']

# -- Options for HTML output -------------------------------------------------
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

if not on_rtd:  # only import and set the theme if we're building docs locally
    import sphinx_rtd_theme
    html_theme = 'sphinx_rtd_theme'
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

    html_context = {
        'css_files': [
            '_static/theme_overrides.css'
        ]
    }
else:
    html_context = {
        'css_files': [
            '//media.readthedocs.org/css/sphinx_rtd_theme.css',
            '//media.readthedocs.org/css/readthedocs-doc-embed.css',
            '_static/theme_overrides.css'
        ]
    }

html_theme_options = {
    'logo_only': True
}

html_logo = "_static/logo-large-v4.png"

html_static_path = ['_static']

# -- Options for Matplotlib in notebooks ----------------------------------

nbsphinx_execute_arguments = [
    "--InlineBackend.figure_formats={'png'}",
    "--InlineBackend.rc={'figure.dpi': 96}",
    "--Session.metadata={'scipp_docs_build': True}",
]
