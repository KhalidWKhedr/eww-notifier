# Contributing to eww-notifier

Thank you for your interest in contributing to eww-notifier! This document provides guidelines and instructions for
contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in the Issues section
2. If not, create a new issue with:
    - A clear, descriptive title
    - Steps to reproduce the bug
    - Expected behavior
    - Actual behavior
    - Screenshots if applicable
    - System information (OS, Python version, etc.)

### Suggesting Features

1. Check if the feature has already been suggested
2. If not, create a new issue with:
    - A clear, descriptive title
    - Detailed description of the feature
    - Use cases
    - Potential implementation approach (if any)

### Pull Requests

1. Fork the repository
2. Create a new branch for your feature/fix
3. Make your changes
4. Add tests for your changes
5. Ensure all tests pass
6. Update documentation if needed
7. Submit a pull request

## Development Setup

1. Clone the repository:
   ```sh
   git clone https://github.com/KhalidWKhedr/eww-notifier.git
   cd eww-notifier
   ```

2. Create a virtual environment:
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   pip install -e .
   ```

4. Install development dependencies:
   ```sh
   pip install pytest pytest-cov black flake8 mypy
   ```

## Code Style

- Follow PEP 8 guidelines
- Use type hints
- Write docstrings for all functions and classes
- Keep functions small and focused
- Use meaningful variable names
- Add comments for complex logic

## Testing

1. Run tests:
   ```sh
   pytest
   ```

2. Check coverage:
   ```sh
   pytest --cov=eww_notifier
   ```

3. Type checking:
   ```sh
   mypy eww_notifier
   ```

4. Linting:
   ```sh
   flake8 eww_notifier
   ```

5. Formatting:
   ```sh
   black eww_notifier
   ```

## Documentation

- Update README.md if needed
- Add docstrings to new functions/classes
- Update type hints
- Add comments for complex logic

## Commit Messages

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Reference issues and pull requests liberally
- Consider starting the commit message with an applicable emoji:
    - 🎨 `:art:` when improving the format/structure of the code
    - 🐎 `:racehorse:` when improving performance
    - 🚱 `:non-potable_water:` when plugging memory leaks
    - 📝 `:memo:` when writing docs
    - 🐛 `:bug:` when fixing a bug
    - 🔥 `:fire:` when removing code or files
    - 💚 `:green_heart:` when fixing the CI build
    - ✅ `:white_check_mark:` when adding tests
    - 🔒 `:lock:` when dealing with security
    - ⬆️ `:arrow_up:` when upgrading dependencies
    - ⬇️ `:arrow_down:` when downgrading dependencies

## License

By contributing to eww-notifier, you agree that your contributions will be licensed under the project's MIT License. 