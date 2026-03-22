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

__version__ = "0.1.2"
__author__ = "Python port of gridmappr by Roger Beecham"

from .core import compute_allocation_quality, points_to_grid

__all__ = [
    "points_to_grid",
    "compute_allocation_quality",
    "visualize_allocation",
    "create_grid_layout",
    "compare_compactness",
    "generate_sample_points",
    "export_to_csv",
    "load_from_csv",
]


def __getattr__(name: str):
    if name in ("visualize_allocation", "create_grid_layout", "compare_compactness"):
        from .utils import (
            compare_compactness,  # noqa: F401
            create_grid_layout,  # noqa: F401
            visualize_allocation,  # noqa: F401
        )

        return locals()[name]
    elif name in ("generate_sample_points", "export_to_csv", "load_from_csv"):
        from .utils import (
            export_to_csv,  # noqa: F401
            generate_sample_points,  # noqa: F401
            load_from_csv,  # noqa: F401
        )

        return locals()[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
