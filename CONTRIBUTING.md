# Contributing to Kubecost Integration

Thank you for your interest in contributing to the Kubecost Integration library!

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/lecton-apptio/kubecost-integration.git
   cd kubecost-integration
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=kubecost_integration --cov-report=html

# Run specific test file
pytest tests/test_client.py

# Run with verbose output
pytest -v
```

### Code Quality

```bash
# Format code
black kubecost_integration tests examples

# Lint code
ruff check kubecost_integration tests

# Type checking
mypy kubecost_integration
```

### Before Submitting

1. Ensure all tests pass
2. Add tests for new features
3. Update documentation
4. Format code with Black
5. Check for linting issues

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and code quality checks
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Code Style

- Follow PEP 8 guidelines
- Use type hints for all functions
- Write docstrings for all public APIs
- Keep functions focused and small
- Add comments for complex logic

## Testing Guidelines

- Write unit tests for all new features
- Aim for >80% code coverage
- Use pytest fixtures for common setup
- Mock external dependencies
- Test both success and error cases

## Documentation

- Update README.md for user-facing changes
- Add docstrings to all public functions
- Include usage examples
- Document breaking changes

## Questions?

Feel free to open an issue for:
- Bug reports
- Feature requests
- Questions about usage
- Documentation improvements

Thank you for contributing!