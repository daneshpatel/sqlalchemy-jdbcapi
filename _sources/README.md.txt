# Documentation

This directory contains the Sphinx documentation for SQLAlchemy JDBC/ODBC API.

## Building the Documentation

### Prerequisites

Install the documentation dependencies:

```bash
pip install -e ".[docs]"
```

Or install dependencies manually:

```bash
pip install sphinx sphinx_rtd_theme myst-parser
```

### Build HTML Documentation

```bash
# From the docs directory
make html

# Or from the project root
cd docs && make html
```

The generated HTML documentation will be in `docs/_build/html/`.

### View Documentation

```bash
# macOS
open _build/html/index.html

# Linux
xdg-open _build/html/index.html

# Windows
start _build/html/index.html
```

### Clean Build Files

```bash
make clean
```

## Documentation Structure

```
docs/
├── conf.py                      # Sphinx configuration
├── index.rst                    # Main documentation index
├── quickstart.md                # Quick start guide
├── usage.md                     # Usage documentation (from root)
├── drivers.md                   # Driver documentation (from root)
├── sqlalchemy_integration.md    # SQLAlchemy integration guide
├── examples.md                  # Examples and patterns
├── troubleshooting.md           # Troubleshooting guide (JPype, drivers, connections)
├── contributing.md              # Contributing guide (from root)
├── changelog.md                 # Changelog (from root)
├── api/                         # API reference documentation
│   ├── index.rst                # API reference index
│   ├── jdbc.rst                 # JDBC module API
│   ├── odbc.rst                 # ODBC module API
│   └── dialects.rst             # Dialects module API
├── _build/                      # Generated documentation (gitignored)
├── _static/                     # Static files for documentation
└── _templates/                  # Custom Sphinx templates
```

## Updating Documentation

### Markdown Files

Most documentation is written in Markdown using MyST parser:

- `quickstart.md` - Getting started guide
- `usage.md` - Comprehensive usage examples
- `drivers.md` - Driver installation and configuration
- `sqlalchemy_integration.md` - SQLAlchemy features
- `examples.md` - Code examples and patterns

### API Documentation

API documentation is auto-generated from docstrings using Sphinx autodoc:

- Edit docstrings in source code (`src/sqlalchemy_jdbcapi/`)
- Rebuild docs to see changes

### Adding New Pages

1. Create a new `.md` or `.rst` file in `docs/`
2. Add it to the `toctree` in `index.rst`
3. Rebuild the documentation

## Documentation Style Guide

### Docstrings

Use Google-style docstrings:

```python
def function(arg1: str, arg2: int) -> bool:
    """Brief description.

    Longer description with more details.

    Args:
        arg1: Description of arg1
        arg2: Description of arg2

    Returns:
        Description of return value

    Raises:
        ValueError: When something is wrong

    Example:
        >>> result = function("test", 42)
        >>> print(result)
        True
    """
    ...
```

### Markdown

- Use descriptive headers
- Include code examples with proper syntax highlighting
- Add links to related sections
- Keep paragraphs concise

## Troubleshooting

### Import Errors

If you see import errors when building:

```bash
# Make sure the package is installed in development mode
pip install -e .
```

### Missing Dependencies

```bash
# Install all development dependencies
pip install -e ".[dev,docs]"
```

### Build Warnings

Some warnings are normal (missing cross-references, etc.). The build should still succeed.

## Publishing Documentation

The documentation can be published to:

- **GitHub Pages**: Use `sphinx.ext.githubpages` extension (already configured)
- **Read the Docs**: Connect your GitHub repository
- **Custom hosting**: Deploy the `_build/html/` directory

## Resources

- [Sphinx Documentation](https://www.sphinx-doc.org/)
- [MyST Parser](https://myst-parser.readthedocs.io/)
- [Read the Docs Theme](https://sphinx-rtd-theme.readthedocs.io/)
