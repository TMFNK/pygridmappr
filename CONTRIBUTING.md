# Contributing to pygridmappr

Thanks for your interest in contributing! This guide will help you get started.

## What to Work On

Check the [issue tracker](https://github.com/TMFNK/pygridmappr/issues) for open issues. Good starting points:

- Issues labeled **`good first issue`** are beginner-friendly
- Issues labeled **`help wanted`** are where we most need contributions
- Bug reports with reproduction steps

If you have an idea that isn't in the issues, [open one first](https://github.com/TMFNK/pygridmappr/issues/new) to discuss before writing code. This avoids wasted effort on changes that don't fit the project direction.

### Areas We'd Love Help With

- **More test coverage** for edge cases (single-row grids, very large grids, degenerate inputs)
- **Performance benchmarks** comparing against the R implementation
- **Real-world examples** using actual geographic datasets
- **Documentation improvements** and typo fixes
- **Bug fixes** (always welcome)

### What to Avoid

- Changes that break mathematical fidelity with the [original R implementation](https://github.com/rogerbeecham/gridmappr)
- Adding dependencies beyond the core stack (NumPy, Pandas, SciPy, Matplotlib)
- Large refactors without prior discussion

## Development Setup

```bash
git clone https://github.com/TMFNK/pygridmappr
cd pygridmappr
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

This installs the package in editable mode with development dependencies (pytest, ruff, mypy).

## Making Changes

1. **Fork the repo** and create a branch from `main`:
   ```bash
   git checkout -b fix/description-of-change
   ```
   Use prefixes: `fix/`, `feat/`, `docs/`, `test/`, `chore/`

2. **Make your changes.** Keep diffs small and focused. One logical change per PR.

3. **Run the tests:**
   ```bash
   pytest tests/ -v
   ```
   All tests must pass. Add tests for new functionality or bug fixes.

4. **Run the linter:**
   ```bash
   ruff check pygridmappr/
   ruff format pygridmappr/
   ```
   Code must pass `ruff check` with no errors. We use the project's [ruff config](pyproject.toml) (line length 88, target Python 3.8).

5. **Commit** with a descriptive message following [Conventional Commits](https://www.conventionalcommits.org/):
   ```
   fix: correct off-by-one in spacer boundary check
   feat: add CSV export for grid layouts
   docs: clarify compactness parameter range
   test: add coverage for non-default DataFrame index
   ```

6. **Open a Pull Request** against `main`. In the PR description:
   - Describe what changed and why
   - Link to any related issue (`Fixes #123`)
   - Include before/after if the change affects output

## Code Style

- **Line length:** 88 characters (ruff enforced)
- **Target version:** Python 3.8
- **Linter rules:** E, F, W, I, UP, B, C4, SIM (see `pyproject.toml`)
- **Formatting:** `ruff format` handles this automatically
- **Comments:** Only when the *why* is non-obvious. Well-named code speaks for itself.
- **Type hints:** Use them on public function signatures (match the style in `core.py`)

## Testing

Tests live in `tests/` and use pytest. Run them with:

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_core.py -v

# With coverage
pytest tests/ --cov=pygridmappr --cov-report=term-missing
```

When writing tests:
- Test both the happy path and edge cases
- Use descriptive test names: `test_spacer_cells_are_excluded_from_assignment`
- Keep tests independent (no shared mutable state between tests)

## Reporting Bugs

[Open an issue](https://github.com/TMFNK/pygridmappr/issues/new) with:

1. **What you expected** to happen
2. **What actually happened** (include the error message / traceback)
3. **Minimal code to reproduce** the problem
4. **Your environment:** Python version, OS, package version (`pygridmappr.__version__`)

## Reporting Security Vulnerabilities

If you find a security issue, please **do not** open a public issue. Email the maintainers directly via the contact information on the [GitHub profile](https://github.com/TMFNK).

## License

By contributing, you agree that your contributions will be licensed under the [AGPL-3.0 License](LICENSE).
