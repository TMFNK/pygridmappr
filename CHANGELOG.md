# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

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
