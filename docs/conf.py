# -*- coding: utf-8 -*-


# Project configuration.
project = u'spectator'
copyright = u'2014, Andre Caron'
version = 'v0.1'
release = 'v0.1.1'

# Sphinx configuration.
needs_sphinx = '1.0'
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.todo',
    'sphinx.ext.viewcode',
]

# Source files.
source_suffix = '.rst'
source_encoding = 'utf-8'
master_doc = 'index'
exclude_patterns = []

# Language & locale.
language = 'en'
today_fmt = '%Y-%m-%d'

# Other style issues.
add_function_parentheses = True
pygments_style = 'sphinx'
keep_warnings = True
templates_path = ['.templates']

# HTML output.
html_theme = 'nature'
#html_theme_options = {}
#html_short_title = None
#html_logo = None
#html_favicon = None
html_static_path = []
html_extra_path = []
html_show_sourcelink = True
html_show_sphinx = True
html_show_copyright = True
htmlhelp_basename = 'spectator-docs'
