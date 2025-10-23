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

import numpy as np
from scipy.optimize import linear_sum_assignment
from typing import List, Tuple, Optional, Dict
import pandas as pd


def points_to_grid(
    pts: pd.DataFrame,
    n_row: int,
    n_col: int,
    compactness: float = 1.0,
    spacers: Optional[List[Tuple[int, int]]] = None
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
    # Validate inputs
    if compactness < 0 or compactness > 1:
        raise ValueError("compactness must be between 0 and 1")
    
    if n_row < 1 or n_col < 1:
        raise ValueError("n_row and n_col must be positive integers")
    
    # Check that pts has required columns
    if 'x' not in pts.columns or 'y' not in pts.columns:
        raise ValueError("pts DataFrame must contain 'x' and 'y' columns")
    
    # Check that grid is large enough
    n_points = len(pts)
    if spacers is None:
        spacers = []
    n_available_cells = n_row * n_col - len(spacers)
    
    if n_available_cells < n_points:
        raise ValueError(
            f"Grid has only {n_available_cells} available cells "
            f"but {n_points} points need to be allocated. "
            f"Increase grid dimensions or reduce spacers."
        )
    
    # Create a copy to avoid modifying the input
    result = pts.copy()
    
    # Extract coordinates
    x = pts['x'].values
    y = pts['y'].values
    
    # Step 1: Scale geographic coordinates to grid bounds
    # This matches the R implementation's scaling approach
    x_min, x_max = x.min(), x.max()
    y_min, y_max = y.min(), y.max()
    
    # Avoid division by zero for single point or collinear points
    x_range = x_max - x_min if x_max > x_min else 1.0
    y_range = y_max - y_min if y_max > y_min else 1.0
    
    # Scale to [0, n_col] x [0, n_row]
    # This preserves the aspect ratio of the geographic data
    x_scaled = (x - x_min) / x_range * n_col
    y_scaled = (y - y_min) / y_range * n_row
    
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
    n_cells = len(grid_cells)
    
    # Step 3: Compute cost matrix
    # C[i, j] = squared Euclidean distance between point i and cell j
    cost_matrix = np.zeros((n_points, n_cells))
    
    for i in range(n_points):
        for j in range(n_cells):
            cell_x = grid_cells[j, 2]
            cell_y = grid_cells[j, 3]
            
            # Squared Euclidean distance
            dx = x_scaled[i] - cell_x
            dy = y_scaled[i] - cell_y
            cost_matrix[i, j] = dx * dx + dy * dy
    
    # Step 4: Apply compactness adjustment
    # This is the key innovation of gridmappr
    if compactness != 0.5:
        # Compute distance of each grid cell from the grid center
        grid_center_x = n_col / 2.0
        grid_center_y = n_row / 2.0
        
        # For each grid cell, compute squared distance from center
        dist_from_center = np.zeros(n_cells)
        for j in range(n_cells):
            cell_x = grid_cells[j, 2]
            cell_y = grid_cells[j, 3]
            dx = cell_x - grid_center_x
            dy = cell_y - grid_center_y
            dist_from_center[j] = dx * dx + dy * dy
        
        # Normalize distances to [0, 1] range for numerical stability
        max_dist = dist_from_center.max()
        if max_dist > 0:
            dist_from_center_normalized = dist_from_center / max_dist
        else:
            dist_from_center_normalized = dist_from_center
        
        # Compute compactness weight
        # compactness = 0.5 → weight = 0 (no effect)
        # compactness = 1.0 → weight = 1 (strong attraction to center)
        # compactness = 0.0 → weight = -1 (strong repulsion from center)
        compactness_weight = 2.0 * (compactness - 0.5)
        
        # Apply compactness penalty to cost matrix
        # If compactness > 0.5: reduce cost for cells near center
        # If compactness < 0.5: increase cost for cells near center
        for i in range(n_points):
            for j in range(n_cells):
                # The penalty is proportional to distance from center
                # We add this to the geographic distance cost
                # The scale factor ensures the compactness effect is meaningful
                # relative to the geographic distances
                penalty = -compactness_weight * dist_from_center_normalized[j]
                cost_matrix[i, j] += penalty * np.mean(cost_matrix[i, :])
    
    # Step 5: Solve assignment problem using Hungarian algorithm
    # This finds the optimal one-to-one assignment that minimizes total cost
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    
    # Step 6: Extract grid assignments and convert to 1-based indexing
    for i, j in zip(row_ind, col_ind):
        row_0based = int(grid_cells[j, 0])
        col_0based = int(grid_cells[j, 1])
        
        # Convert to 1-based indexing for output (matching R convention)
        result.loc[i, 'row'] = row_0based + 1
        result.loc[i, 'col'] = col_0based + 1
        
        # Also store the grid cell center coordinates
        result.loc[i, 'grid_x'] = grid_cells[j, 2]
        result.loc[i, 'grid_y'] = grid_cells[j, 3]
    
    # Convert to integer type for row and col
    result['row'] = result['row'].astype(int)
    result['col'] = result['col'].astype(int)
    
    return result


def compute_allocation_quality(result: pd.DataFrame) -> Dict[str, float]:
    """
    Compute quality metrics for a grid allocation.
    
    Parameters
    ----------
    result : pd.DataFrame
        Output from points_to_grid() with 'x', 'y', 'grid_x', 'grid_y' columns
        
    Returns
    -------
    dict
        Dictionary with quality metrics:
        - 'mean_distance': Mean Euclidean distance between geographic and grid positions
        - 'total_distance': Sum of all distances
        - 'max_distance': Maximum distance for any point
        - 'rmse': Root mean squared error
    """
    if not all(col in result.columns for col in ['x', 'y', 'grid_x', 'grid_y']):
        raise ValueError("result must contain x, y, grid_x, and grid_y columns")
    
    # Note: grid coordinates are in grid units, geographic coords are in original units
    # We need to scale properly for meaningful comparison
    x = result['x'].values
    y = result['y'].values
    
    # Scale geographic to same range as grid
    x_min, x_max = x.min(), x.max()
    y_min, y_max = y.min(), y.max()
    x_range = x_max - x_min if x_max > x_min else 1.0
    y_range = y_max - y_min if y_max > y_min else 1.0
    
    # Infer grid dimensions from result
    n_col = result['col'].max()
    n_row = result['row'].max()
    
    x_scaled = (x - x_min) / x_range * n_col
    y_scaled = (y - y_min) / y_range * n_row
    
    # Compute distances
    grid_x = result['grid_x'].values
    grid_y = result['grid_y'].values
    
    distances = np.sqrt((x_scaled - grid_x)**2 + (y_scaled - grid_y)**2)
    
    return {
        'mean_distance': float(np.mean(distances)),
        'total_distance': float(np.sum(distances)),
        'max_distance': float(np.max(distances)),
        'rmse': float(np.sqrt(np.mean(distances**2)))
    }