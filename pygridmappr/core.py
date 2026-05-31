"""
pygridmappr - Python implementation of R package gridmappr
Core module containing the main allocation algorithm.

This is a faithful Python recreation of Roger Beecham's R package 'gridmappr',
which allocates geographic point locations to grid cells while minimizing
the total squared distance between geographic and grid positions.

Original R package: https://github.com/rogerbeecham/gridmappr
Based on Jo Wood's Observable notebooks on Linear Programming and Gridmap Allocation

References:
    Beecham, R., Dykes, J., Hama, L. and Lomax, N. (2021)
    'On the Use of 'Glyphmaps' for Analysing the Scale and Temporal Spread
    of COVID-19 Reported Cases', ISPRS International Journal of Geo-Information

Mathematical Approach:
    The algorithm uses the Hungarian algorithm (linear sum assignment) to solve
    the assignment problem. For each point i and grid cell j, we compute a cost
    matrix C[i,j] that represents the squared Euclidean distance between:
    1. The geographic position of point i (scaled to grid bounds)
    2. The position of grid cell j

    The compactness parameter modulates this cost by adding a penalty that
    attracts points toward (compactness > 0.5) or repels them from
    (compactness < 0.5) the grid center.
"""

from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from scipy.optimize import linear_sum_assignment


def points_to_grid(
    pts: pd.DataFrame,
    n_row: int,
    n_col: int,
    compactness: float = 1.0,
    spacers: Optional[List[Tuple[int, int]]] = None,
) -> pd.DataFrame:
    """
    Allocate geographic points to grid cells using optimal assignment.

    This function replicates the R gridmappr::points_to_grid() function.
    It allocates each geographic point to a unique grid cell such that the
    total squared distance between geographic positions (scaled to grid bounds)
    and grid positions is minimized.

    Parameters
    ----------
    pts : pd.DataFrame
        DataFrame with columns 'x' and 'y' containing geographic coordinates.
        May optionally contain an 'area_name' or other identifier column.
    n_row : int
        Number of rows in the grid.
    n_col : int
        Number of columns in the grid.
    compactness : float, optional (default=1.0)
        Parameter between 0 and 1 controlling allocation behavior:
        - 0.5: Preserves scaled geographic positions
        - 1.0: Allocates points toward grid center (compact cluster)
        - 0.0: Allocates points toward grid edges
    spacers : list of tuple, optional
        List of (row, col) tuples defining grid cells that cannot be assigned.
        Coordinates use 1-based indexing with origin (1,1) at bottom-left,
        matching the R implementation convention.

    Returns
    -------
    pd.DataFrame
        Copy of input dataframe with added columns:
        - 'row': Grid row assignment (1-based, bottom-left origin)
        - 'col': Grid column assignment (1-based, bottom-left origin)
        - 'grid_x': X coordinate of assigned grid cell center
        - 'grid_y': Y coordinate of assigned grid cell center

    Notes
    -----
    The algorithm works as follows:
    1. Scale geographic coordinates to [0, n_col] x [0, n_row] range
    2. Generate all valid grid cell positions (excluding spacers)
    3. Compute cost matrix C[i,j] = squared distance between point i and cell j
    4. Modify costs based on compactness parameter
    5. Use Hungarian algorithm to find optimal assignment

    The compactness effect is implemented by computing distance from each
    grid cell to the grid center, then using this to adjust costs:
    - When compactness > 0.5: Cells closer to center have lower costs
    - When compactness < 0.5: Cells farther from center have lower costs
    - When compactness = 0.5: No modification (pure geographic distance)

    Examples
    --------
    >>> import pandas as pd
    >>> pts = pd.DataFrame({
    ...     'area_name': ['A', 'B', 'C', 'D'],
    ...     'x': [0, 100, 100, 0],
    ...     'y': [0, 0, 100, 100]
    ... })
    >>> result = points_to_grid(pts, n_row=2, n_col=2, compactness=0.5)
    >>> print(result[['area_name', 'row', 'col']])
    """
    if not isinstance(pts, pd.DataFrame):
        raise TypeError(f"pts must be a pandas DataFrame, got {type(pts).__name__}")
    if "x" not in pts.columns or "y" not in pts.columns:
        raise ValueError("pts must contain columns 'x' and 'y'")
    if len(pts) == 0:
        raise ValueError("pts must not be empty")
    if n_row < 1 or n_col < 1:
        raise ValueError(
            f"n_row and n_col must be >= 1, got n_row={n_row}, n_col={n_col}"
        )
    if not (0.0 <= compactness <= 1.0):
        raise ValueError(f"compactness must be in [0, 1], got {compactness}")
    if len(pts) > n_row * n_col:
        raise ValueError(
            f"Number of points ({len(pts)}) exceeds grid capacity "
            f"({n_row}×{n_col} = {n_row * n_col} cells)"
        )
    if spacers is None:
        spacers = []
    n_available_cells = n_row * n_col - len(spacers)

    n_points = len(pts)
    if n_available_cells < n_points:
        raise ValueError(
            f"Grid has only {n_available_cells} available cells "
            f"but {n_points} points need to be allocated. "
            f"Increase grid dimensions or reduce spacers."
        )

    # Create a copy to avoid modifying the input
    result = pts.copy()

    # Extract coordinates
    x = pts["x"].values
    y = pts["y"].values

    x_range = x.max() - x.min()
    y_range = y.max() - y.min()
    # Scale geographic coords to [0, n_col] x [0, n_row] to match grid cell centers
    x_scaled = pd.Series(
        (x - x.min()) / x_range * n_col
        if x_range > 0
        else pd.Series(n_col / 2.0, index=pts.index),
        index=pts.index,
    )
    y_scaled = pd.Series(
        (y - y.min()) / y_range * n_row
        if y_range > 0
        else pd.Series(n_row / 2.0, index=pts.index),
        index=pts.index,
    )

    # Step 2: Generate all grid cell positions
    # Grid uses 1-based indexing with origin at bottom-left
    # We'll work in 0-based internally and convert at the end
    grid_cells = []
    for row in range(n_row):
        for col in range(n_col):
            # Convert to 1-based for spacer checking
            row_1based = row + 1
            col_1based = col + 1

            # Check if this cell is a spacer (should be excluded)
            if (row_1based, col_1based) not in spacers:
                # Cell center coordinates (in 0-based system)
                # Cells are centered at 0.5, 1.5, 2.5, etc.
                cell_x = col + 0.5
                cell_y = row + 0.5
                grid_cells.append((row, col, cell_x, cell_y))

    grid_cells = np.array(grid_cells)

    grid_x = grid_cells[:, 2]
    grid_y = grid_cells[:, 3]

    dx = x_scaled.values[:, np.newaxis] - grid_x[np.newaxis, :]
    dy = y_scaled.values[:, np.newaxis] - grid_y[np.newaxis, :]
    cost_matrix = dx**2 + dy**2

    if compactness != 0.5:
        grid_center_x = n_col / 2.0
        grid_center_y = n_row / 2.0

        dist_from_center = (grid_x - grid_center_x) ** 2 + (grid_y - grid_center_y) ** 2

        max_dist = dist_from_center.max()
        if max_dist > 0:
            dist_from_center_normalized = dist_from_center / max_dist
        else:
            dist_from_center_normalized = dist_from_center

        compactness_weight = 2.0 * (compactness - 0.5)

        row_means = cost_matrix.mean(axis=1, keepdims=True)
        penalty_matrix = (
            -compactness_weight * dist_from_center_normalized[np.newaxis, :]
        )
        cost_matrix += penalty_matrix * row_means

    # Step 5: Solve assignment problem using Hungarian algorithm
    # This finds the optimal one-to-one assignment that minimizes total cost
    _, col_ind = linear_sum_assignment(cost_matrix)

    # Step 6: Extract grid assignments and convert to 1-based indexing
    assigned_cells = grid_cells[col_ind]
    result = result.reset_index(drop=True)
    result["row"] = (assigned_cells[:, 0] + 1).astype(int)
    result["col"] = (assigned_cells[:, 1] + 1).astype(int)
    result["grid_x"] = assigned_cells[:, 2]
    result["grid_y"] = assigned_cells[:, 3]

    return result


def compute_allocation_quality(
    result: pd.DataFrame,
    n_row: Optional[int] = None,
    n_col: Optional[int] = None,
) -> Dict[str, float]:
    """
    Compute quality metrics for a grid allocation.

    Parameters
    ----------
    result : pd.DataFrame
        Output from points_to_grid() with 'x', 'y', 'grid_x', 'grid_y' columns
    n_row : int, optional
        Number of grid rows. If None, inferred from result (may underestimate).
    n_col : int, optional
        Number of grid columns. If None, inferred from result (may underestimate).

    Returns
    -------
    dict
        Dictionary with quality metrics:
        - 'mean_distance': Mean Euclidean distance between geographic and grid positions
        - 'total_distance': Sum of all distances
        - 'max_distance': Maximum distance for any point
        - 'rmse': Root mean squared error
    """
    if not all(col in result.columns for col in ["x", "y", "grid_x", "grid_y"]):
        raise ValueError("result must contain x, y, grid_x, and grid_y columns")

    if n_col is None:
        n_col = int(result["col"].max())
    if n_row is None:
        n_row = int(result["row"].max())

    # Note: grid coordinates are in grid units, geographic coords are in original units
    # We need to scale properly for meaningful comparison
    x = result["x"].values
    y = result["y"].values

    # Scale geographic to same range as grid
    x_min, x_max = x.min(), x.max()
    y_min, y_max = y.min(), y.max()
    x_range = x_max - x_min if x_max > x_min else 1.0
    y_range = y_max - y_min if y_max > y_min else 1.0

    x_scaled = (x - x_min) / x_range * n_col
    y_scaled = (y - y_min) / y_range * n_row

    # Compute distances
    grid_x = result["grid_x"].values
    grid_y = result["grid_y"].values

    distances = np.sqrt((x_scaled - grid_x) ** 2 + (y_scaled - grid_y) ** 2)

    return {
        "mean_distance": float(np.mean(distances)),
        "total_distance": float(np.sum(distances)),
        "max_distance": float(np.max(distances)),
        "rmse": float(np.sqrt(np.mean(distances**2))),
    }
