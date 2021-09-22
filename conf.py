###############################################################
# Copyright 2020 Lawrence Livermore National Security, LLC
# (c.f. AUTHORS, NOTICE.LLNS, COPYING)
#
# This file is part of the Flux resource manager framework.
# For details, see https://github.com/flux-framework.
#
# SPDX-License-Identifier: LGPL-3.0
###############################################################

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
import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'Flux'
copyright = '''Copyright 2014 Lawrence Livermore National Security, LLC and Flux developers.

SPDX-License-Identifier: LGPL-3.0'''
author = 'This page is maintained by the Flux community.'

# -- RTD configuration -------------------------------------------------------

# on_rtd is whether we are on readthedocs.org, this line of code grabbed from docs.readthedocs.org
on_rtd = os.environ.get("READTHEDOCS", None) == "True"

# This is used for linking and such so we link to the thing we're building
rtd_version = os.environ.get("READTHEDOCS_VERSION", "latest")
if rtd_version not in ["stable", "latest"]:
    rtd_version = "stable"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.intersphinx",
    'sphinxcontrib.spelling',
    'sphinx_copybutton',
]

# sphinxcontrib.spelling settings
spelling_word_list_filename = [
    'spell.en.pws'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

master_doc = 'index'
source_suffix = '.rst'

# -- Options for Intersphinx -------------------------------------------------

intersphinx_mapping = {
    # note: rfc only has 'latest' version, no 'stable' available, yet?
    "rfc": (
        "https://flux-framework.readthedocs.io/projects/flux-rfc/en/latest/",
        None,
    ),
    "core": (
        "https://flux-framework.readthedocs.io/projects/flux-core/en/latest/",
        None,
    ),
    "workflow-examples": (
        "https://flux-framework.readthedocs.io/projects/flux-workflow-examples/en/latest/",
        None,
    ),
}

# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_static_path = ['_static']

# -- Options for man output -------------------------------------------------

man_pages = [
]
