"""
pygridmappr - Python implementation of R package gridmappr

A Python port of Roger Beecham's R package for automated gridmap layout generation.

This package allocates geographic point locations to grid cells while minimizing
the total squared distance between geographic and grid positions. It uses the
Hungarian algorithm (linear sum assignment) to find optimal allocations.

Original R package: https://github.com/rogerbeecham/gridmappr
Author: Roger Beecham
Python port maintains full functional parity with the R implementation.

Main Functions
--------------
points_to_grid : Allocate points to grid cells
visualize_allocation : Visualize the allocation results
compute_allocation_quality : Calculate quality metrics

Example
-------
>>> import pandas as pd
>>> from pygridmappr import points_to_grid, visualize_allocation
>>> 
>>> # Create sample data
>>> pts = pd.DataFrame({
...     'area_name': ['A', 'B', 'C'],
...     'x': [0, 100, 50],
...     'y': [0, 0, 100]
... })
>>> 
>>> # Allocate to grid
>>> result = points_to_grid(pts, n_row=2, n_col=2, compactness=0.5)
>>> 
>>> # Visualize
>>> fig, axes = visualize_allocation(result, n_row=2, n_col=2)
"""

__version__ = '0.1.0'
__author__ = 'Python port of gridmappr by Roger Beecham'

from .core import points_to_grid, compute_allocation_quality
from .utils import (
    visualize_allocation,
    create_grid_layout,
    compare_compactness,
    generate_sample_points,
    export_to_csv,
    load_from_csv
)

__all__ = [
    'points_to_grid',
    'compute_allocation_quality',
    'visualize_allocation',
    'create_grid_layout',
    'compare_compactness',
    'generate_sample_points',
    'export_to_csv',
    'load_from_csv'
]