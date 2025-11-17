# Contributing to SQLAlchemy JDBC/ODBC API

Thank you for considering contributing to SQLAlchemy JDBC/ODBC API! We welcome contributions from the community.

## Code of Conduct

We are committed to providing a welcoming and inclusive experience for everyone. Please be respectful and professional in all interactions.

## How to Contribute

### Reporting Issues

- **Bugs**: Use the GitHub issue tracker to report bugs. Include:
  - Python version
  - SQLAlchemy version
  - Database type and version
  - Minimal reproducible example
  - Error messages and stack traces

- **Feature Requests**: Submit detailed proposals via GitHub issues explaining:
  - The problem you're trying to solve
  - Your proposed solution
  - Example use cases

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/YOUR_USERNAME/sqlalchemy-jdbcapi.git
   cd sqlalchemy-jdbcapi
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install in Development Mode**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Install Pre-commit Hooks**
   ```bash
   pre-commit install
   ```

### Development Workflow

1. **Create a Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Your Changes**
   - Write clean, well-documented code
   - Follow existing code style and patterns
   - Add type hints for all functions and methods
   - Update documentation as needed

3. **Write Tests**
   - Add unit tests for new functionality
   - Ensure existing tests pass
   - Aim for >80% code coverage
   ```bash
   pytest tests/
   ```

4. **Run Code Quality Checks**
   ```bash
   # Format code
   ruff format src tests

   # Lint code
   ruff check src tests

   # Type check
   mypy src

   # Run all pre-commit hooks
   pre-commit run --all-files
   ```

5. **Test with Multiple Databases** (Optional but Recommended)
   ```bash
   # Test with Docker databases
   ./run_docker_tests.sh

   # Test specific database
   ./run_docker_tests.sh -d postgresql
   ```

6. **Update Documentation**
   - Update relevant markdown files in root or `docs/`
   - Add docstrings to new functions/classes
   - Update API documentation if needed
   ```bash
   cd docs
   make html
   ```

7. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "Add feature: brief description"
   ```

   Commit message format:
   - Use present tense ("Add feature" not "Added feature")
   - Be concise but descriptive
   - Reference issue numbers if applicable (#123)

8. **Push to Your Fork**
   ```bash
   git push origin feature/your-feature-name
   ```

9. **Submit a Pull Request**
   - Go to GitHub and create a pull request
   - Fill out the PR template
   - Link related issues
   - Wait for review

### Pull Request Guidelines

- **One Feature Per PR**: Keep pull requests focused on a single feature or fix
- **Tests Required**: All new features must include tests
- **Documentation**: Update documentation for user-facing changes
- **Backwards Compatibility**: Avoid breaking changes when possible
- **Code Quality**: All checks must pass (ruff, mypy, pytest)

### Code Style

- **Python Version**: Minimum Python 3.10
- **Formatting**: We use Ruff for formatting (88 character line length)
- **Linting**: Ruff with comprehensive rule sets
- **Type Hints**: Mandatory for all functions and methods
- **Docstrings**: Use Google-style docstrings
- **Imports**: Organized with isort (via Ruff)

### Testing Guidelines

1. **Unit Tests**
   - Test individual functions and classes
   - Use mocks for external dependencies
   - Place in `tests/unit/`

2. **Functional Tests**
   - Test with real JDBC/ODBC connections
   - May require database setup
   - Place in `tests/functional/`
   - Mark with `@pytest.mark.functional`

3. **Integration Tests**
   - Test end-to-end workflows
   - Use Docker for database isolation
   - Place in `tests/integration/` or `tests/docker/`
   - Mark with `@pytest.mark.integration` or `@pytest.mark.docker`

### Documentation Guidelines

- **Markdown**: Use GitHub-flavored markdown
- **Code Examples**: Include working, tested examples
- **API Docs**: Use Sphinx autodoc for API reference
- **Docstrings**: Follow Google style:
  ```python
  def example_function(param1: str, param2: int) -> bool:
      """Brief description of function.

      Longer description with more details about what the function does,
      its behavior, and any important notes.

      Args:
          param1: Description of param1
          param2: Description of param2

      Returns:
          Description of return value

      Raises:
          ValueError: When param2 is negative
          TypeError: When param1 is not a string

      Example:
          >>> result = example_function("test", 42)
          >>> print(result)
          True
      """
      ...
  ```

### Adding New Database Dialects

1. **Create Dialect Class**
   - Inherit from `BaseJDBCDialect` or `BaseODBCDialect`
   - Implement required methods
   - Place in `src/sqlalchemy_jdbcapi/dialects/`

2. **Register Entry Point**
   - Add to `pyproject.toml` under `[project.entry-points."sqlalchemy.dialects"]`

3. **Add Tests**
   - Unit tests in `tests/unit/test_dialects.py`
   - Integration tests in `tests/docker/`

4. **Update Documentation**
   - Add to README.md supported databases table
   - Add section in USAGE.md with examples
   - Update docs/api/dialects.rst

### Release Process

Releases are managed by project maintainers:

1. Update CHANGELOG.md with release notes
2. Bump version using `bump-version.sh`
3. Create GitHub release with tag
4. CI/CD automatically builds and publishes to PyPI

## Questions?

- **Documentation**: Check the [docs/](docs/) directory
- **Issues**: Search existing issues or create a new one
- **Discussions**: Use GitHub Discussions for questions

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

## Thank You!

Your contributions help make this project better for everyone. We appreciate your time and effort!
