# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [0.1.3] - 2026-05-31

### Fixed
- Geographic coordinates now scaled to `[0, n_col] x [0, n_row]` to match grid cell centers, fixing degraded assignment quality on larger grids
- `points_to_grid` now handles DataFrames with non-default indices via positional indexing
- `compare_compactness` uses relative import instead of `sys.path` manipulation

### Changed
- `compute_allocation_quality` accepts optional `n_row` and `n_col` parameters to avoid underestimating grid dimensions from sparse allocations

### Added
- `CONTRIBUTING.md` with development setup, code style, and contribution guidelines
- Improved README with hero image, quick-nav, API reference table, and concise examples
- GitHub issue templates (bug report, feature request) and PR template
- Jupyter notebook quick-start example (`examples/quickstart.ipynb`)
- PEP 561 `py.typed` marker for type checker support

### Fixed
- `examples/demo.py` uses package imports instead of `sys.path` hack

## [Unreleased]

### Added
- `pyproject.toml` replacing legacy `setup.py` + `MANIFEST.in`
- GitHub Actions CI workflow
- Full type annotations on all public functions
- Input validation with descriptive error messages
- Vectorized cost matrix construction
- `figsize` and `dpi` parameters on all visualization functions
- Determinism and no-mutation tests

### Fixed
- Division-by-zero in coordinate scaling for degenerate point sets
- `plt.show()` removed from library visualization functions
- Input DataFrame no longer mutated by `points_to_grid`

### Removed
- `requirements.txt` (superseded by `pyproject.toml`)
- Committed build artifacts (`__pycache__/`, `dist/`, `build/`, `.egg-info/`)
- `.DS_Store` macOS metadata file
