"""
pygridmappr - Python implementation of R package gridmappr
Utility functions for grid generation, visualization, and data handling.

This module provides helper functions for working with grid allocations,
including visualization capabilities and grid manipulation utilities.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from typing import Optional, Tuple, List, Dict, Any, Union
from matplotlib.collections import PatchCollection
from matplotlib.figure import Figure
from matplotlib.axes import Axes


def create_grid_layout(
    n_row: int,
    n_col: int,
    spacers: Optional[List[Tuple[int, int]]] = None
) -> pd.DataFrame:
    """
    Create a DataFrame representing all cells in a grid.
    
    Parameters
    ----------
    n_row : int
        Number of rows in grid
    n_col : int
        Number of columns in grid
    spacers : list of tuple, optional
        List of (row, col) positions to exclude (1-based indexing)
        
    Returns
    -------
    pd.DataFrame
        DataFrame with columns 'row', 'col', 'x', 'y', 'available'
    """
    if spacers is None:
        spacers = []
    
    cells = []
    for row in range(1, n_row + 1):
        for col in range(1, n_col + 1):
            is_spacer = (row, col) in spacers
            cells.append({
                'row': row,
                'col': col,
                'x': col - 0.5,  # Cell center x
                'y': row - 0.5,  # Cell center y
                'available': not is_spacer
            })
    
    return pd.DataFrame(cells)


def visualize_allocation(
    result: pd.DataFrame,
    n_row: int,
    n_col: int,
    spacers: Optional[List[Tuple[int, int]]] = None,
    title: str = "Gridmap Allocation",
    show_labels: bool = True,
    label_column: Optional[str] = None,
    show_geographic: bool = True,
    figsize: Tuple[float, float] = (14, 6),
    **kwargs
) -> Tuple[Figure, Union[Tuple[Optional[Axes], Axes], Tuple[None, Axes]]]:
    """
    Visualize the grid allocation alongside the original geographic layout.
    
    Parameters
    ----------
    result : pd.DataFrame
        Output from points_to_grid()
    n_row : int
        Number of grid rows
    n_col : int
        Number of grid columns
    spacers : list of tuple, optional
        Spacer cells (1-based indexing)
    title : str
        Overall figure title
    show_labels : bool
        Whether to show point labels
    label_column : str, optional
        Column name to use for labels (e.g., 'area_name')
        If None, will attempt to find a suitable label column
    show_geographic : bool
        If True, show both geographic and grid views side-by-side
        If False, show only grid view
    figsize : tuple
        Figure size (width, height)
    **kwargs
        Additional arguments passed to scatter plots
        
    Returns
    -------
    fig : matplotlib.figure.Figure
    axes : matplotlib.axes.Axes or array of Axes
    """
    if spacers is None:
        spacers = []
    
    # Determine label column
    if label_column is None:
        # Try to find a suitable label column
        for col in ['area_name', 'name', 'id', 'label']:
            if col in result.columns:
                label_column = col
                break
    
    # Create figure
    if show_geographic:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    else:
        fig, ax2 = plt.subplots(1, 1, figsize=(figsize[0]/2, figsize[1]))
        ax1 = None
    
    # Default scatter plot kwargs
    scatter_kwargs = {'s': 100, 'alpha': 0.7, 'edgecolors': 'black', 'linewidths': 1}
    scatter_kwargs.update(kwargs)
    
    # Left plot: Geographic layout
    if show_geographic and ax1 is not None:
        ax1.scatter(result['x'], result['y'], **scatter_kwargs)
        
        if show_labels and label_column and label_column in result.columns:
            for idx, row in result.iterrows():
                ax1.annotate(
                    row[label_column],
                    (row['x'], row['y']),
                    fontsize=8,
                    ha='center',
                    va='center'
                )
        
        ax1.set_xlabel('X (Geographic)', fontsize=10)
        ax1.set_ylabel('Y (Geographic)', fontsize=10)
        ax1.set_title('Original Geographic Layout', fontsize=11, fontweight='bold')
        ax1.set_aspect('equal', adjustable='box')
        ax1.grid(True, alpha=0.3)
    
    # Right plot: Grid layout
    # Draw grid cells
    for row in range(1, n_row + 1):
        for col in range(1, n_col + 1):
            # Determine cell color
            if (row, col) in spacers:
                color = 'lightgray'
                alpha = 0.3
            else:
                color = 'white'
                alpha = 1.0
            
            # Draw cell rectangle (using 0-based coordinates for plotting)
            rect = mpatches.Rectangle(
                (col - 1, row - 1),
                1, 1,
                linewidth=1,
                edgecolor='black',
                facecolor=color,
                alpha=alpha
            )
            ax2.add_patch(rect)
    
    # Plot allocated points
    ax2.scatter(
        result['col'] - 0.5,  # Center of cell
        result['row'] - 0.5,
        **scatter_kwargs
    )
    
    # Add labels
    if show_labels and label_column and label_column in result.columns:
        for idx, row in result.iterrows():
            ax2.annotate(
                row[label_column],
                (row['col'] - 0.5, row['row'] - 0.5),
                fontsize=8,
                ha='center',
                va='center'
            )
    
    ax2.set_xlim(-0.5, n_col + 0.5)
    ax2.set_ylim(-0.5, n_row + 0.5)
    ax2.set_xlabel('Column', fontsize=10)
    ax2.set_ylabel('Row', fontsize=10)
    ax2.set_title('Grid Allocation', fontsize=11, fontweight='bold')
    ax2.set_aspect('equal', adjustable='box')
    ax2.grid(True, alpha=0.3, linestyle='--')
    
    # Set integer ticks
    ax2.set_xticks(range(0, n_col + 1))
    ax2.set_yticks(range(0, n_row + 1))
    
    fig.suptitle(title, fontsize=13, fontweight='bold')
    plt.tight_layout()
    
    return fig, (ax1, ax2) if show_geographic else (None, ax2)


def compare_compactness(
    pts: pd.DataFrame,
    n_row: int,
    n_col: int,
    compactness_values: List[float] = [0.0, 0.5, 1.0],
    spacers: Optional[List[Tuple[int, int]]] = None,
    figsize: Tuple[float, float] = (15, 5)
) -> Tuple[Figure, List[Axes]]:
    """
    Compare grid allocations with different compactness values.
    
    Parameters
    ----------
    pts : pd.DataFrame
        Point data with 'x' and 'y' columns
    n_row : int
        Number of grid rows
    n_col : int
        Number of grid columns
    compactness_values : list of float
        List of compactness values to compare
    spacers : list of tuple, optional
        Spacer cells
    figsize : tuple
        Figure size
        
    Returns
    -------
    fig : matplotlib.figure.Figure
    axes : list of matplotlib.axes.Axes
    """
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from core import points_to_grid, compute_allocation_quality
    
    n_plots = len(compactness_values)
    fig, axes = plt.subplots(1, n_plots, figsize=figsize)
    
    if n_plots == 1:
        axes = [axes]
    
    for ax, compactness in zip(axes, compactness_values):
        # Compute allocation
        result = points_to_grid(pts, n_row, n_col, compactness, spacers)
        quality = compute_allocation_quality(result)
        
        # Draw grid
        for row in range(1, n_row + 1):
            for col in range(1, n_col + 1):
                if spacers and (row, col) in spacers:
                    color = 'lightgray'
                    alpha = 0.3
                else:
                    color = 'white'
                    alpha = 1.0
                
                rect = mpatches.Rectangle(
                    (col - 1, row - 1), 1, 1,
                    linewidth=1, edgecolor='black',
                    facecolor=color, alpha=alpha
                )
                ax.add_patch(rect)
        
        # Plot points
        ax.scatter(
            result['col'] - 0.5,
            result['row'] - 0.5,
            s=80, alpha=0.7,
            edgecolors='black',
            linewidths=1
        )
        
        ax.set_xlim(-0.5, n_col + 0.5)
        ax.set_ylim(-0.5, n_row + 0.5)
        ax.set_aspect('equal', adjustable='box')
        ax.set_title(
            f'Compactness = {compactness:.1f}\n'
            f'RMSE = {quality["rmse"]:.2f}',
            fontsize=10,
            fontweight='bold'
        )
        ax.set_xlabel('Column')
        ax.set_ylabel('Row')
        ax.grid(True, alpha=0.3, linestyle='--')
    
    fig.suptitle('Compactness Comparison', fontsize=13, fontweight='bold')
    plt.tight_layout()
    
    return fig, axes


def generate_sample_points(
    n_points: int = 50,
    pattern: str = 'random',
    seed: Optional[int] = None
) -> pd.DataFrame:
    """
    Generate sample point data for testing.
    
    Parameters
    ----------
    n_points : int
        Number of points to generate
    pattern : str
        Pattern type: 'random', 'cluster', 'ring', 'grid'
    seed : int, optional
        Random seed for reproducibility
        
    Returns
    -------
    pd.DataFrame
        DataFrame with 'x', 'y', and 'area_name' columns
    """
    if seed is not None:
        np.random.seed(seed)
    
    if pattern == 'random':
        x = np.random.uniform(0, 100, n_points)
        y = np.random.uniform(0, 100, n_points)
    
    elif pattern == 'cluster':
        # Create multiple clusters
        n_clusters = 4
        points_per_cluster = n_points // n_clusters
        x, y = [], []
        
        cluster_centers = [(25, 25), (75, 25), (25, 75), (75, 75)]
        for cx, cy in cluster_centers:
            x.extend(np.random.normal(cx, 10, points_per_cluster))
            y.extend(np.random.normal(cy, 10, points_per_cluster))
        
        # Add remaining points
        remaining = n_points - len(x)
        x.extend(np.random.uniform(0, 100, remaining))
        y.extend(np.random.uniform(0, 100, remaining))
        
        x = np.array(x)
        y = np.array(y)
    
    elif pattern == 'ring':
        angles = np.linspace(0, 2*np.pi, n_points, endpoint=False)
        radius = 40
        x = 50 + radius * np.cos(angles)
        y = 50 + radius * np.sin(angles)
    
    elif pattern == 'grid':
        # Create a regular grid with some jitter
        n_side = int(np.sqrt(n_points))
        x_base = np.linspace(10, 90, n_side)
        y_base = np.linspace(10, 90, n_side)
        xx, yy = np.meshgrid(x_base, y_base)
        x = xx.flatten()[:n_points]
        y = yy.flatten()[:n_points]
        # Add jitter
        x += np.random.normal(0, 2, len(x))
        y += np.random.normal(0, 2, len(y))
    
    else:
        raise ValueError(f"Unknown pattern: {pattern}")
    
    return pd.DataFrame({
        'area_name': [f'P{i+1}' for i in range(len(x))],
        'x': x,
        'y': y
    })


def export_to_csv(result: pd.DataFrame, filename: str) -> None:
    """
    Export grid allocation results to CSV file.
    
    Parameters
    ----------
    result : pd.DataFrame
        Output from points_to_grid()
    filename : str
        Output filename
    """
    result.to_csv(filename, index=False)
    print(f"Exported {len(result)} allocations to {filename}")


def load_from_csv(filename: str) -> pd.DataFrame:
    """
    Load point data from CSV file.
    
    Parameters
    ----------
    filename : str
        Input filename
        
    Returns
    -------
    pd.DataFrame
        Point data
    """
    df = pd.read_csv(filename)
    if 'x' not in df.columns or 'y' not in df.columns:
        raise ValueError("CSV must contain 'x' and 'y' columns")
    return df
