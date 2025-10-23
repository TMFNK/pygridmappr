# pygridmappr Quick Reference

## Installation

```bash
pip install -e .
# or
pip install -r requirements.txt
```

## Basic Usage

```python
import pandas as pd
from pygridmappr import points_to_grid

# Your data with x, y coordinates
pts = pd.DataFrame({
    'area_name': ['A', 'B', 'C'],
    'x': [0, 50, 100],
    'y': [0, 50, 100]
})

# Allocate to grid
result = points_to_grid(pts, n_row=2, n_col=2, compactness=0.5)
```

## Main Function

### `points_to_grid(pts, n_row, n_col, compactness=1.0, spacers=None)`

**Parameters:**

- `pts`: DataFrame with 'x', 'y' columns (required)
- `n_row`: Number of grid rows (int ≥ 1)
- `n_col`: Number of grid columns (int ≥ 1)
- `compactness`: Float in [0, 1]
  - `0.0` → push to edges
  - `0.5` → preserve geography (recommended)
  - `1.0` → pull to center
- `spacers`: List of (row, col) tuples to exclude (1-based)

**Returns:** DataFrame with added columns: `row`, `col`, `grid_x`, `grid_y`

## Visualization

```python
from pygridmappr import visualize_allocation

fig, axes = visualize_allocation(
    result,
    n_row=2,
    n_col=2,
    title="My Gridmap",
    label_column='area_name',  # Optional: column for labels
    show_labels=True
)
```

## Quality Metrics

```python
from pygridmappr import compute_allocation_quality

metrics = compute_allocation_quality(result)
print(f"RMSE: {metrics['rmse']:.3f}")
print(f"Mean distance: {metrics['mean_distance']:.3f}")
print(f"Max distance: {metrics['max_distance']:.3f}")
```

## Compare Compactness Values

```python
from pygridmappr import compare_compactness

fig, axes = compare_compactness(
    pts,
    n_row=5,
    n_col=5,
    compactness_values=[0.0, 0.5, 1.0]
)
```

## Using Spacers

```python
# Exclude specific grid cells (row, col with 1-based indexing)
spacers = [
    (1, 5),  # Bottom-right corner
    (2, 5),
    (3, 5)
]

result = points_to_grid(
    pts,
    n_row=5,
    n_col=5,
    compactness=0.6,
    spacers=spacers
)
```

## Generate Sample Data

```python
from pygridmappr import generate_sample_points

# Pattern types: 'random', 'cluster', 'ring', 'grid'
pts = generate_sample_points(
    n_points=25,
    pattern='cluster',
    seed=42  # For reproducibility
)
```

## Common Workflows

### Find Best Grid Size

```python
for n in [6, 8, 10, 12]:
    result = points_to_grid(pts, n_row=n, n_col=n, compactness=0.5)
    quality = compute_allocation_quality(result)
    print(f"{n}×{n}: RMSE = {quality['rmse']:.3f}")
```

### Optimize Compactness

```python
best_rmse = float('inf')
best_c = None

for c in [0.0, 0.2, 0.4, 0.5, 0.6, 0.8, 1.0]:
    result = points_to_grid(pts, 8, 8, compactness=c)
    quality = compute_allocation_quality(result)
    if quality['rmse'] < best_rmse:
        best_rmse = quality['rmse']
        best_c = c

print(f"Best compactness: {best_c} (RMSE: {best_rmse:.3f})")
```

### Separate Non-Contiguous Regions

```python
# 1. Visualize without spacers to identify problem areas
result1 = points_to_grid(pts, 10, 10, compactness=0.6)
visualize_allocation(result1, 10, 10)

# 2. Add spacers to create separation
spacers = [(1,8), (2,8), (3,8), (1,9), (2,9)]

# 3. Re-allocate with spacers
result2 = points_to_grid(pts, 10, 10, compactness=0.6, spacers=spacers)
visualize_allocation(result2, 10, 10, spacers=spacers)
```

## Tips & Best Practices

### Choosing Compactness

- **0.5**: Start here - preserves geographic relationships
- **> 0.5**: If you want a more compact, centered layout
- **< 0.5**: If you want to emphasize periphery or create space in center

### Choosing Grid Size

1. Must have at least as many cells as points: `n_row × n_col ≥ n_points`
2. Too small: Less geographic accuracy, more space per cell
3. Too large: Better geography, less space for visualizations
4. Rule of thumb: Try `ceil(sqrt(n_points * 1.2))` as starting point

### When to Use Spacers

- Separating islands from mainland
- Non-contiguous territories (Alaska, Hawaii)
- Creating visual gaps or regions
- Handling geographic "holes" (e.g., inner cities)

### Quality Metrics Interpretation

- **RMSE < 1.0**: Excellent geographic preservation
- **RMSE 1.0-2.0**: Good preservation
- **RMSE > 3.0**: Consider larger grid or adjusting compactness

## Coordinate System Notes

- **Input**: Use any coordinate system (lat/lon, projected, pixels, etc.)
- **Output**: 1-based grid coordinates with origin at **bottom-left**
  - Row 1 = bottom, Row N = top
  - Col 1 = left, Col N = right
- **Spacers**: Also use 1-based indexing: `(row, col)` with `(1,1)` at bottom-left

## Common Issues

### "Grid has only X available cells but Y points"

**Problem**: Grid too small or too many spacers

**Solution**:

```python
# Increase grid size
n_row, n_col = 8, 8  # Instead of 5, 5

# OR reduce spacers
spacers = spacers[:3]  # Use fewer
```

### "compactness must be between 0 and 1"

**Problem**: Invalid compactness value

**Solution**:

```python
compactness = 0.5  # Must be in [0, 1]
```

### Points not where expected

**Problem**: Forgetting 1-based indexing or bottom-left origin

**Solution**: Remember (1,1) is bottom-left corner, not top-left

## File Export/Import

```python
from pygridmappr import export_to_csv, load_from_csv

# Export results
export_to_csv(result, 'gridmap_allocation.csv')

# Load points from file
pts = load_from_csv('geographic_points.csv')
```

## Running Examples

```bash
# Run all demonstrations
cd examples
python demo.py

# Open Jupyter notebook
jupyter notebook getting_started.ipynb
```

## Testing

```bash
# Run unit tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=pygridmappr --cov-report=html
```

## Getting Help

1. Check `README.md` for overview
2. Read `TECHNICAL_SPECIFICATION.md` for algorithm details
3. Browse `examples/demo.py` for working examples
4. Open `examples/getting_started.ipynb` in Jupyter
5. Run tests to see expected behavior: `pytest tests/ -v`

## Original R Package

This Python implementation replicates:

- **R Package**: https://github.com/rogerbeecham/gridmappr
- **Author**: Roger Beecham
- **Documentation**: https://www.roger-beecham.com/gridmappr/

## Minimal Working Example

```python
import pandas as pd
from pygridmappr import points_to_grid, visualize_allocation

# Create data
pts = pd.DataFrame({'x': [0, 10, 10, 0], 'y': [0, 0, 10, 10]})

# Allocate
result = points_to_grid(pts, n_row=2, n_col=2, compactness=0.5)

# View
print(result[['x', 'y', 'row', 'col']])

# Visualize
visualize_allocation(result, 2, 2)
```

## License

GPL-3.0 License (matching original R package)
