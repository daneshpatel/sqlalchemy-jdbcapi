# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from pathlib import Path

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'SQLAlchemy JDBC/ODBC API'
copyright = '2024, Danesh Patel, Pavel Henrykhsen'
author = 'Danesh Patel, Pavel Henrykhsen'

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parents[1] / 'src'))

# Get version from package
try:
    from sqlalchemy_jdbcapi._version import version as release
except ImportError:
    release = '2.0.0'

version = '.'.join(release.split('.')[:2])  # Short version (X.Y)

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx.ext.autosummary',
    'sphinx.ext.coverage',
    'sphinx.ext.githubpages',
    'sphinx_copybutton',
    'myst_parser',
]

# MyST Parser configuration
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "substitution",
    "tasklist",
]

# Source file types
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'furo'
html_static_path = ['_static']

html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#2563eb",
        "color-brand-content": "#2563eb",
    },
    "dark_css_variables": {
        "color-brand-primary": "#3b82f6",
        "color-brand-content": "#3b82f6",
    },
    "sidebar_hide_name": False,
    "navigation_with_keys": True,
    "top_of_page_button": "edit",
}

html_title = "SQLAlchemy JDBC/ODBC API"
html_short_title = "JDBC/ODBC API"

# Custom CSS
html_css_files = [
    'custom.css',
]

# Furo-specific options
html_context = {
    "display_github": True,
    "github_user": "daneshpatel",
    "github_repo": "sqlalchemy-jdbcapi",
    "github_version": "master",
    "conf_py_path": "/docs/",
}

# Announcement banner (optional - remove if not needed)
# html_theme_options["announcement"] = "🎉 Version 2.0 is here! Check out the new features."

# Logo (optional - add if you have one)
# html_logo = "_static/logo.png"
# html_favicon = "_static/favicon.ico"

# -- Extension configuration -------------------------------------------------

# Autodoc configuration
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__',
    'show-inheritance': True,
}

autodoc_typehints = 'description'
autodoc_typehints_description_target = 'documented'

# Napoleon settings (for Google/NumPy style docstrings)
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True

# Intersphinx configuration
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'sqlalchemy': ('https://docs.sqlalchemy.org/en/20/', None),
}

# Autosummary configuration
autosummary_generate = True
autosummary_imported_members = False
