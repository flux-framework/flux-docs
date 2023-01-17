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
import sys

import sphinx_immaterial
from recommonmark.transform import AutoStructify  # noqa

sys.path.insert(0, os.path.abspath("."))

# -- Project information -----------------------------------------------------

project = "Flux"
copyright = """Copyright 2014-2023 Lawrence Livermore National Security, LLC and Flux developers.

SPDX-License-Identifier: LGPL-3.0"""
author = "This page is maintained by the Flux Framework community."

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
    "sphinxcontrib.spelling",
    "domainrefs",
    "myst_parser",
    "sphinx.ext.autosummary",
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.extlinks",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.mathjax",
    "sphinx.ext.viewcode",
    "sphinx_markdown_tables",
]

# sphinxcontrib.spelling settings
spelling_word_list_filename = ["spell.en.pws"]


autosummary_generate = True
autoclass_content = "class"

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    "_build",
    "Thumbs.db",
    ".DS_Store",
    "env",
    "venv",
    "README.md",
    ".github",
]


master_doc = "index"
source_suffix = ".rst"

domainrefs = {
    "linux:man1": {
        "text": "%s(1)",
        "url": "http://man7.org/linux/man-pages/man1/%s.1.html",
    },
    "linux:man2": {
        "text": "%s(2)",
        "url": "http://man7.org/linux/man-pages/man2/%s.2.html",
    },
    "linux:man3": {
        "text": "%s(3)",
        "url": "http://man7.org/linux/man-pages/man3/%s.3.html",
    },
    "linux:man7": {
        "text": "%s(7)",
        "url": "http://man7.org/linux/man-pages/man7/%s.7.html",
    },
    "linux:man8": {
        "text": "%s(8)",
        "url": "http://man7.org/linux/man-pages/man8/%s.8.html",
    },
    "core:man1": {
        "text": "%s(1)",
        "url": "https://flux-framework.readthedocs.io/projects/flux-core/en/latest/man1/%s.html",
    },
    "core:man3": {
        "text": "%s(3)",
        "url": "https://flux-framework.readthedocs.io/projects/flux-core/en/latest/man3/%s.html",
    },
    "core:man5": {
        "text": "%s(5)",
        "url": "https://flux-framework.readthedocs.io/projects/flux-core/en/latest/man5/%s.html",
    },
    "core:man7": {
        "text": "%s(7)",
        "url": "https://flux-framework.readthedocs.io/projects/flux-core/en/latest/man7/%s.html",
    },
    "sched:man5": {
        "text": "%s(5)",
        "url": "https://flux-framework.readthedocs.io/projects/flux-sched/en/latest/man5/%s.html",
    },
    "security:man3": {
        "text": "%s(3)",
        "url": "https://flux-framework.readthedocs.io/projects/flux-security/en/latest/man3/%s.html",
    },
    "security:man5": {
        "text": "%s(5)",
        "url": "https://flux-framework.readthedocs.io/projects/flux-security/en/latest/man5/%s.html",
    },
    "security:man8": {
        "text": "%s(8)",
        "url": "https://flux-framework.readthedocs.io/projects/flux-security/en/latest/man8/%s.html",
    },
}

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
    "sched": (
        "https://flux-framework.readthedocs.io/projects/flux-sched/en/latest/",
        None,
    ),
    "security": (
        "https://flux-framework.readthedocs.io/projects/flux-security/en/latest/",
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
extensions.append("sphinx_immaterial")
# html_theme_path = sphinx_immaterial.html_theme_path()
# html_context = sphinx_immaterial.get_html_context()
html_css_files = ["custom.css"]

extensions.append("sphinx_immaterial")
html_theme = "sphinx_immaterial"

# material theme options (see theme.conf for more information)
html_theme_options = {
    "icon": {
        "repo": "fontawesome/brands/github",
        "edit": "material/file-edit-outline",
    },
    "site_url": "http://flux-framework.github.io/flux-docs/",
    "repo_url": "https://github.com/flux-framework/flux-docs/",
    "repo_name": "Flux Framework",
    "repo_type": "github",
    "edit_uri": "blob/main",
    "globaltoc_collapse": True,
    "features": [
        "navigation.expand",
        "navigation.tabs",
        "toc.integrate",
        "navigation.sections",
        "navigation.instant",
        "header.autohide",
        "navigation.top",
        "navigation.tracking",
        "search.highlight",
        "search.share",
        "toc.follow",
        "toc.sticky",
        "content.tabs.link",
        "announce.dismiss",
    ],
    "palette": [
        {
            "media": "(prefers-color-scheme: light)",
            "scheme": "default",
            "primary": "blue",
            "accent": "light-blue",
            "toggle": {
                "icon": "material/lightbulb-outline",
                "name": "Switch to dark mode",
            },
        },
        {
            "media": "(prefers-color-scheme: dark)",
            "scheme": "slate",
            "primary": "blue",
            "accent": "light-blue",
            "toggle": {
                "icon": "material/lightbulb",
                "name": "Switch to light mode",
            },
        },
    ],
    # BEGIN: version_dropdown
    "version_dropdown": False,
    "version_info": [
        {
            "version": "https://flux-framework.readthedocs.io",
            "title": "ReadTheDocs",
            "aliases": [],
        },
        {
            "version": "https://flux-framework.org/flux-docs",
            "title": "Github Pages",
            "aliases": [],
        },
    ],
    # END: version_dropdown
    "toc_title_is_page_title": True,
    # BEGIN: social icons
    "social": [
        {
            "icon": "fontawesome/brands/github",
            "link": "https://github.com/flux-framework/flux-docs",
            "name": "Source on github.com",
        },
        {
            "icon": "material/chart-donut-variant",
            "link": "https://flux-framework.org/",
            "name": "Flux Framework",
        },
    ],
    # END: social icons
}



#    "touch_icon": "images/flux-operator.jpg",
#    "theme_color": "#262626",
#    "nav_links": [
#        {
#            "href": "https://flux-framework.org/",
#            "internal": False,
#            "title": "Flux Framework",
#        },
#        {
#            "href": "https://github.com/flux-framework",
#            "internal": False,
#            "title": "Flux Framework on GitHub",
#        },
#        {
#            "href": "https://github.com/flux-framework/flux-docs",
#            "internal": False,
#            "title": "Flux Documentation on GitHub",
#        },
#    ],

todo_include_todos = True
sphinx_immaterial_bundle_source_maps = True

# Custom sphinx material variables
theme_logo_icon = "images/flux-logo.png"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]
html_show_sourcelink = True
html_sidebars = {
    "**": ["logo-text.html", "globaltoc.html", "localtoc.html", "searchbox.html"]
}
sphinx_immaterial_icon_path = html_static_path

# -- Options for man output -------------------------------------------------

man_pages = []

language = "en"
html_last_updated_fmt = ""

todo_include_todos = True
html_favicon = "images/favicon.ico"

html_use_index = True
html_domain_indices = True

extlinks = {
    "duref": (
        "http://docutils.sourceforge.net/docs/ref/rst/" "restructuredtext.html#%s",
        "",
    ),
    "durole": ("http://docutils.sourceforge.net/docs/ref/rst/" "roles.html#%s", ""),
    "dudir": ("http://docutils.sourceforge.net/docs/ref/rst/" "directives.html#%s", ""),
}

# Enable eval_rst in markdown
def setup(app):
    app.add_config_value(
        "recommonmark_config",
        {"enable_math": True, "enable_inline_math": True, "enable_eval_rst": True},
        True,
    )
    app.add_transform(AutoStructify)
    app.add_object_type(
        "confval",
        "confval",
        objname="configuration value",
        indextemplate="pair: %s; configuration value",
    )
