# Contributing to JamSplitter

Thank you for your interest in contributing to JamSplitter! We welcome all contributions, including bug reports, feature requests, documentation improvements, and code contributions.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How to Contribute](#how-to-contribute)
  - [Reporting Bugs](#reporting-bugs)
  - [Suggesting Enhancements](#suggesting-enhancements)
  - [Your First Code Contribution](#your-first-code-contribution)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Code Style and Standards](#code-style-and-standards)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How to Contribute

### Reporting Bugs

Before creating a bug report, please check if the issue has already been reported in the [issue tracker](https://github.com/yourusername/jam-splitter/issues). If you find an existing issue, feel free to add a comment with additional information.

When creating a bug report, please include:

1. A clear and descriptive title
2. Steps to reproduce the issue
3. Expected behavior
4. Actual behavior
5. Environment details (OS, Python version, etc.)
6. Any relevant error messages or logs

### Suggesting Enhancements

We welcome enhancement suggestions that would improve the project. Please use the issue tracker to submit your ideas. When suggesting an enhancement, please include:

1. A clear and descriptive title
2. A detailed description of the enhancement
3. Why this enhancement would be useful
4. Any examples or mockups if applicable

### Your First Code Contribution

Unsure where to begin contributing? You can start by looking through the "good first issue" and "help wanted" issues in the issue tracker.

## Development Setup

1. Fork the repository and clone it locally
2. Set up a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install the package in development mode with all dependencies:
   ```bash
   pip install -e ".[dev]"
   ```
4. Install pre-commit hooks:
   ```bash
   pre-commit install
   ```

## Pull Request Process

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```
2. Make your changes and commit them with a descriptive message
3. Push your changes to your fork
4. Open a pull request against the `main` branch

Please ensure your pull request adheres to the following guidelines:

- Include tests for new features or bug fixes
- Update the documentation as needed
- Ensure all tests pass
- Keep the code style consistent with the project
- Write clear commit messages

## Code Style and Standards

We use several tools to maintain code quality and style:

- **Black** for code formatting
- **isort** for import sorting
- **Flake8** for linting
- **Mypy** for static type checking

Run the following command to format and check your code:

```bash
pre-commit run --all-files
```

## Testing

We use `pytest` for testing. To run the test suite:

```bash
pytest
```

To run tests with coverage:

```bash
pytest --cov=src --cov-report=term-missing
```

## Documentation

Good documentation is crucial for any open-source project. When contributing, please ensure that:

1. New features include appropriate docstrings
2. The README is updated if necessary
3. Any new command-line arguments or configuration options are documented

Thank you for contributing to JamSplitter!
