<p align="center">
  <img src="https://raw.githubusercontent.com/TMFNK/pygridmappr/main/examples/demo2_compactness.png" alt="pygridmappr compactness comparison" width="700">
</p>

<h1 align="center">pygridmappr</h1>

<p align="center">
  <strong>Optimal grid layouts from geographic points, in three lines of Python.</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/pygridmappr/"><img src="https://img.shields.io/pypi/v/pygridmappr.svg" alt="PyPI version"></a>
  <a href="https://pypi.org/project/pygridmappr/"><img src="https://img.shields.io/pypi/pyversions/pygridmappr.svg" alt="Python versions"></a>
  <a href="https://www.gnu.org/licenses/agpl-3.0"><img src="https://img.shields.io/badge/License-AGPLv3-blue.svg" alt="License: AGPL v3"></a>
  <a href="https://github.com/TMFNK/pygridmappr/actions"><img src="https://img.shields.io/github/actions/workflow/status/TMFNK/pygridmappr/ci.yml?branch=main&label=tests" alt="Tests"></a>
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> &bull;
  <a href="#installation">Installation</a> &bull;
  <a href="#examples">Examples</a> &bull;
  <a href="#api-reference">API Reference</a> &bull;
  <a href="#contributing">Contributing</a>
</p>

---

**pygridmappr** allocates geographic points to grid cells while preserving spatial relationships. It uses the [Hungarian algorithm](https://en.wikipedia.org/wiki/Hungarian_algorithm) to find the assignment that minimizes total squared distance between geographic positions and grid cell centers.

A faithful Python port of Roger Beecham's R package [`gridmappr`](https://github.com/rogerbeecham/gridmappr).

**Use cases:** small-multiple cartograms, glyph maps, tile grid maps, any visualization where you need to show data for geographic areas in a regular grid layout.

## Quick Start

```python
import pandas as pd
from pygridmappr import points_to_grid, visualize_allocation

pts = pd.DataFrame({
    'area_name': ['A', 'B', 'C', 'D'],
    'x': [0, 100, 100, 0],
    'y': [0, 0, 100, 100]
})

result = points_to_grid(pts, n_row=2, n_col=2, compactness=0.5)
fig, axes = visualize_allocation(result, n_row=2, n_col=2)
```

That's it. Each point gets a unique grid cell, and the layout respects the original geography.

## Installation

```bash
pip install pygridmappr
```

Or install from source for the latest version:

```bash
git clone https://github.com/TMFNK/pygridmappr
cd pygridmappr
pip install -e .
```

**Requirements:** Python 3.8+ &bull; NumPy &bull; Pandas &bull; SciPy &bull; Matplotlib

## Examples

### Compactness Parameter

The `compactness` parameter (0 to 1) controls the trade-off between geographic fidelity and grid density:

| Value | Effect |
|-------|--------|
| `0.0` | Points spread toward grid edges |
| `0.5` | Preserves scaled geographic layout |
| `1.0` | Points cluster toward grid center |

```python
from pygridmappr import compare_compactness, generate_sample_points

pts = generate_sample_points(n_points=20, pattern='random', seed=42)
fig, axes = compare_compactness(pts, n_row=5, n_col=5, compactness_values=[0.0, 0.5, 1.0])
```

![Compactness comparison](https://raw.githubusercontent.com/TMFNK/pygridmappr/main/examples/demo2_compactness.png)

### Spacer Cells

Block specific grid cells to create visual separation (e.g., separating an island from a mainland):

```python
spacers = [(1, 11), (2, 11), (3, 11), (1, 10), (2, 10)]

result = points_to_grid(pts, n_row=13, n_col=12, compactness=0.6, spacers=spacers)
```

![Spacer constraints](https://raw.githubusercontent.com/TMFNK/pygridmappr/main/examples/demo3_spacers.png)

### Geographic Patterns

The algorithm handles any spatial distribution:

![Geographic patterns](https://raw.githubusercontent.com/TMFNK/pygridmappr/main/examples/demo4_patterns.png)

### Grid Size Exploration

Find the right balance between available space and geographic fidelity:

![Grid sizes](https://raw.githubusercontent.com/TMFNK/pygridmappr/main/examples/demo5_grid_sizes.png)

### Quality Metrics

Measure how well the grid preserves geography:

```python
from pygridmappr import compute_allocation_quality

quality = compute_allocation_quality(result, n_row=13, n_col=12)
print(f"RMSE: {quality['rmse']:.3f}")
print(f"Mean distance: {quality['mean_distance']:.3f}")
print(f"Max distance: {quality['max_distance']:.3f}")
```

## API Reference

### `points_to_grid(pts, n_row, n_col, compactness=1.0, spacers=None)`

Allocate geographic points to grid cells using optimal assignment.

**Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `pts` | `pd.DataFrame` | DataFrame with `'x'` and `'y'` columns |
| `n_row` | `int` | Number of grid rows |
| `n_col` | `int` | Number of grid columns |
| `compactness` | `float` | Layout control, 0 to 1 (default: `1.0`) |
| `spacers` | `list[tuple]` | `(row, col)` cells to exclude, 1-based indexing, bottom-left origin |

**Returns:** Copy of input DataFrame with added columns: `row`, `col`, `grid_x`, `grid_y`

### `compute_allocation_quality(result, n_row=None, n_col=None)`

Compute quality metrics for a grid allocation.

**Returns:** `dict` with keys: `mean_distance`, `total_distance`, `max_distance`, `rmse`

### `visualize_allocation(result, n_row, n_col, ...)`

Side-by-side visualization of geographic and grid layouts.

### `compare_compactness(pts, n_row, n_col, compactness_values=None, ...)`

Compare allocations across different compactness values.

### `generate_sample_points(n_points=50, pattern='random', seed=None)`

Generate test data. Patterns: `'random'`, `'cluster'`, `'ring'`, `'grid'`.

## How It Works

For each point *i* and grid cell *j*, the algorithm computes a cost matrix:

```
C[i,j] = (x_scaled[i] - x_grid[j])^2 + (y_scaled[i] - y_grid[j])^2
```

When `compactness != 0.5`, costs are adjusted by distance from grid center:

```
C[i,j] += -2(compactness - 0.5) * dist_from_center[j] * mean(C[i,:])
```

The optimal one-to-one assignment is solved with [`scipy.optimize.linear_sum_assignment`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linear_sum_assignment.html) (Hungarian algorithm).

## Differences from R Implementation

| Aspect | R (`gridmappr`) | Python (`pygridmappr`) |
|--------|-----------------|----------------------|
| Solver | R linear programming | `scipy.optimize.linear_sum_assignment` |
| Visualization | ggplot2 | matplotlib |
| Data structures | tibble | pandas DataFrame |

Core algorithm behavior is identical.

## References

- Beecham, R. (2021). *gridmappr: Gridmap Allocations with Approximate Spatial Arrangements*. [GitHub](https://github.com/rogerbeecham/gridmappr)
- Beecham, R., Dykes, J., Hama, L. and Lomax, N. (2021). On the Use of 'Glyphmaps' for Analysing the Scale and Temporal Spread of COVID-19 Reported Cases. *ISPRS International Journal of Geo-Information*, 10(4), 213. [DOI](https://doi.org/10.3390/ijgi10040213)
- Wood, J. Observable notebooks on [Linear Programming](https://observablehq.com/@jwolondon/hello-linear-programming) and [Gridmap Allocation](https://observablehq.com/@jwolondon/gridmap-allocation)

## Citation

```bibtex
@software{beecham2021gridmappr,
  author = {Beecham, Roger},
  title = {gridmappr: Gridmap Allocations with Approximate Spatial Arrangements},
  year = {2021},
  url = {https://github.com/rogerbeecham/gridmappr}
}
```

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) before getting started.

Whether you're fixing a bug, adding a feature, or improving documentation, we appreciate your help.

## License

[AGPL-3.0](LICENSE) (matching original R package)

## Acknowledgments

All credit for the algorithm design goes to [Roger Beecham](https://github.com/rogerbeecham) and [Jo Wood](https://github.com/jwoLondon). This package is a Python port of their work.
