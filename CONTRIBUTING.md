# Contributing to PhD Timeline Intelligence Platform

Thank you for your interest in contributing to the PhD Timeline Intelligence Platform!

## Getting Started

1. Fork the repository
2. Clone your fork: `git clone <your-fork-url>`
3. Create a new branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes
6. Commit your changes: `git commit -m "Add your commit message"`
7. Push to your fork: `git push origin feature/your-feature-name`
8. Create a Pull Request

## Development Setup

See the [Development Setup Guide](resources/docs/development-setup.md) for detailed instructions.

Quick start:
```bash
# Install dependencies
make install

# Setup environment
make setup-dev

# Start development servers
docker-compose up -d
```

## Code Standards

### Backend (Python)
- Follow PEP 8 style guide
- Use type hints
- Write docstrings for functions and classes
- Run `black` for formatting
- Run `flake8` for linting
- Run `mypy` for type checking

```bash
make lint-backend
make format-backend
```

### Frontend (TypeScript/React)
- Follow ESLint configuration
- Use TypeScript for all new code
- Write meaningful component names
- Use functional components with hooks

```bash
make lint-frontend
```

## Testing

- Write tests for new features
- Maintain test coverage above 80%
- Run tests before submitting PR

```bash
make test
```

## Commit Messages

Follow conventional commits format:
- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `style:` Code style changes (formatting)
- `refactor:` Code refactoring
- `test:` Test changes
- `chore:` Build process or auxiliary tool changes

Example: `feat: add timeline visualization component`

## Pull Request Process

1. Update documentation if needed
2. Add tests for new features
3. Ensure all tests pass
4. Update CHANGELOG.md
5. Request review from maintainers
6. Address review comments
7. Squash commits if requested

## Code Review Guidelines

Reviewers should check for:
- Code quality and readability
- Test coverage
- Documentation updates
- Performance implications
- Security considerations

## Questions?

Feel free to open an issue for discussion or reach out to the maintainers.

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.
