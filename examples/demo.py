"""
Demonstration of pygridmappr functionality

This script demonstrates the key features of pygridmappr including:
- Basic point-to-grid allocation
- Effect of compactness parameter
- Use of spacers to constrain allocation
- Quality metrics computation
- Visualization capabilities

Examples replicate the R package documentation examples where possible.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Import pygridmappr functions
# Import from local modules since package structure needs fixing
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core import points_to_grid, compute_allocation_quality
from utils import (
    visualize_allocation,
    compare_compactness,
    generate_sample_points
)


def demo_basic_allocation():
    """
    Demo 1: Basic allocation with a simple set of points
    """
    print("=" * 70)
    print("DEMO 1: Basic Point Allocation")
    print("=" * 70)
    
    # Create simple test data - 4 points in corners
    pts = pd.DataFrame({
        'area_name': ['NW', 'NE', 'SE', 'SW'],
        'x': [0, 100, 100, 0],
        'y': [100, 100, 0, 0]
    })
    
    print("\nInput points:")
    print(pts)
    
    # Allocate to 2x2 grid with default compactness (1.0)
    result = points_to_grid(pts, n_row=2, n_col=2, compactness=0.5)
    
    print("\nGrid allocation (compactness=0.5):")
    print(result[['area_name', 'x', 'y', 'row', 'col']])
    
    # Compute quality metrics
    quality = compute_allocation_quality(result)
    print("\nQuality metrics:")
    for key, value in quality.items():
        print(f"  {key}: {value:.3f}")
    
    # Visualize
    fig, axes = visualize_allocation(
        result, n_row=2, n_col=2,
        title="Basic Allocation Example",
        label_column='area_name'
    )
    plt.savefig('examples/demo1_basic.png', dpi=150, bbox_inches='tight')
    print("\nVisualization saved as 'demo1_basic.png'")
    plt.close()


def demo_compactness_effect():
    """
    Demo 2: Effect of compactness parameter
    """
    print("\n" + "=" * 70)
    print("DEMO 2: Compactness Parameter Effect")
    print("=" * 70)
    
    # Generate random points
    np.random.seed(42)
    pts = generate_sample_points(n_points=20, pattern='random', seed=42)
    
    print(f"\nGenerated {len(pts)} random points")
    
    # Test different compactness values
    compactness_values = [0.0, 0.3, 0.5, 0.7, 1.0]
    
    print("\nComparing compactness values:")
    print(f"{'Compactness':<12} {'Mean Dist':<12} {'RMSE':<12} {'Max Dist':<12}")
    print("-" * 50)
    
    for c in compactness_values:
        result = points_to_grid(pts, n_row=5, n_col=5, compactness=c)
        quality = compute_allocation_quality(result)
        print(f"{c:<12.1f} {quality['mean_distance']:<12.3f} "
              f"{quality['rmse']:<12.3f} {quality['max_distance']:<12.3f}")
    
    # Create comparison visualization
    fig, axes = compare_compactness(
        pts, n_row=5, n_col=5,
        compactness_values=[0.0, 0.5, 1.0],
        figsize=(15, 5)
    )
    plt.savefig('examples/demo2_compactness.png', dpi=150, bbox_inches='tight')
    print("\nComparison saved as 'demo2_compactness.png'")
    plt.close()


def demo_with_spacers():
    """
    Demo 3: Using spacers to constrain allocation

    This example mimics the France départements example from the R package,
    where spacers are used to separate Corsica from mainland France.
    """
    print("\n" + "=" * 70)
    print("DEMO 3: Using Spacers")
    print("=" * 70)

    # Create synthetic "France-like" data
    # Mainland cluster + separated island cluster
    np.random.seed(123)

    # Mainland points (larger cluster)
    n_mainland = 90
    mainland_x = np.random.normal(50, 15, n_mainland)
    mainland_y = np.random.normal(50, 20, n_mainland)

    # Island points (smaller, separated cluster)
    n_island = 6
    island_x = np.random.normal(85, 3, n_island)
    island_y = np.random.normal(20, 3, n_island)

    # Combine
    x = np.concatenate([mainland_x, island_x])
    y = np.concatenate([mainland_y, island_y])

    pts = pd.DataFrame({
        'area_name': [f'M{i+1}' if i < n_mainland else f'I{i-n_mainland+1}'
                      for i in range(len(x))],
        'x': x,
        'y': y
    })

    print(f"\nCreated synthetic data: {n_mainland} mainland + {n_island} island points")

    # First allocation without spacers
    result_no_spacers = points_to_grid(pts, n_row=13, n_col=12, compactness=0.6)
    quality_no_spacers = compute_allocation_quality(result_no_spacers)

    print("\nWithout spacers:")
    print(f"  RMSE: {quality_no_spacers['rmse']:.3f}")

    # Show island assignments without spacers
    island_no_spacers = result_no_spacers[result_no_spacers['area_name'].str.startswith('I')]
    print(f"  Island positions: {list(zip(island_no_spacers['row'], island_no_spacers['col']))}")

    # Define spacers to separate island from mainland
    # These create a "gap" in the grid
    spacers = [
        (1, 11), (2, 11), (3, 11),  # Right edge, bottom rows
        (1, 10), (2, 10)             # One column left
    ]

    print(f"\nUsing {len(spacers)} spacer cells to create separation")
    print(f"Spacer positions: {spacers}")

    # Allocation with spacers
    result_with_spacers = points_to_grid(
        pts, n_row=13, n_col=12,
        compactness=0.6,
        spacers=spacers
    )
    quality_with_spacers = compute_allocation_quality(result_with_spacers)

    print("\nWith spacers:")
    print(f"  RMSE: {quality_with_spacers['rmse']:.3f}")

    # Show island assignments with spacers
    island_with_spacers = result_with_spacers[result_with_spacers['area_name'].str.startswith('I')]
    print(f"  Island positions: {list(zip(island_with_spacers['row'], island_with_spacers['col']))}")

    # Compare the assignments
    positions_no_spacers = set(zip(island_no_spacers['row'], island_no_spacers['col']))
    positions_with_spacers = set(zip(island_with_spacers['row'], island_with_spacers['col']))
    print(f"  Island positions changed: {positions_no_spacers != positions_with_spacers}")

    # Check for conflicts with spacers
    spacer_set = set(spacers)
    conflicts = positions_with_spacers & spacer_set
    print(f"  Island points in spacer cells: {conflicts}")

    # Visualize both - improved version with better visual distinction
    fig, axes = plt.subplots(1, 2, figsize=(16, 7))

    # Without spacers
    ax = axes[0]
    for row in range(1, 14):
        for col in range(1, 13):
            from matplotlib.patches import Rectangle
            rect = Rectangle((col-1, row-1), 1, 1,
                           linewidth=1, edgecolor='black',
                           facecolor='white', alpha=1.0)
            ax.add_patch(rect)

    # Plot mainland points (blue) and island points (red) separately
    mainland_no_spacers = result_no_spacers[result_no_spacers['area_name'].str.startswith('M')]
    island_no_spacers = result_no_spacers[result_no_spacers['area_name'].str.startswith('I')]

    ax.scatter(mainland_no_spacers['col'] - 0.5,
               mainland_no_spacers['row'] - 0.5,
               s=30, alpha=0.7, c='blue', label='Mainland')
    ax.scatter(island_no_spacers['col'] - 0.5,
               island_no_spacers['row'] - 0.5,
               s=50, alpha=0.9, c='red', label='Island', edgecolors='darkred', linewidth=2)

    ax.set_xlim(-0.5, 12.5)
    ax.set_ylim(-0.5, 13.5)
    ax.set_aspect('equal')
    ax.set_title('Without Spacers\n(Island may mix with mainland)', fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()

    # With spacers
    ax = axes[1]
    for row in range(1, 14):
        for col in range(1, 13):
            is_spacer = (row, col) in spacers
            color = 'lightgray' if is_spacer else 'white'
            alpha = 0.5 if is_spacer else 1.0
            edge_color = 'red' if is_spacer else 'black'
            linewidth = 2 if is_spacer else 1

            rect = Rectangle((col-1, row-1), 1, 1,
                           linewidth=linewidth, edgecolor=edge_color,
                           facecolor=color, alpha=alpha)
            ax.add_patch(rect)

    # Plot mainland points (blue) and island points (red) separately
    mainland_with_spacers = result_with_spacers[result_with_spacers['area_name'].str.startswith('M')]
    island_with_spacers = result_with_spacers[result_with_spacers['area_name'].str.startswith('I')]

    ax.scatter(mainland_with_spacers['col'] - 0.5,
               mainland_with_spacers['row'] - 0.5,
               s=30, alpha=0.7, c='blue', label='Mainland')
    ax.scatter(island_with_spacers['col'] - 0.5,
               island_with_spacers['row'] - 0.5,
               s=50, alpha=0.9, c='red', label='Island', edgecolors='darkred', linewidth=2)

    ax.set_xlim(-0.5, 12.5)
    ax.set_ylim(-0.5, 13.5)
    ax.set_aspect('equal')
    ax.set_title('With Spacers\n(Island separated by barrier)', fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend()

    fig.suptitle('Effect of Spacers on Grid Allocation\nRed circles = Island points, Blue dots = Mainland points',
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('examples/demo3_spacers.png', dpi=150, bbox_inches='tight')
    print("\nVisualization saved as 'demo3_spacers.png'")
    plt.close()


def demo_geographic_patterns():
    """
    Demo 4: Different geographic patterns
    """
    print("\n" + "=" * 70)
    print("DEMO 4: Different Geographic Patterns")
    print("=" * 70)
    
    patterns = ['random', 'cluster', 'ring', 'grid']
    
    fig, axes = plt.subplots(2, 4, figsize=(16, 8))
    
    for idx, pattern in enumerate(patterns):
        # Generate points
        pts = generate_sample_points(n_points=30, pattern=pattern, seed=42)
        
        # Allocate with compactness=0.5 (geographic preservation)
        result = points_to_grid(pts, n_row=6, n_col=6, compactness=0.5)
        quality = compute_allocation_quality(result)
        
        print(f"\n{pattern.upper()} pattern:")
        print(f"  RMSE: {quality['rmse']:.3f}")
        
        # Plot geographic
        ax = axes[0, idx]
        ax.scatter(pts['x'], pts['y'], s=50, alpha=0.7, c='blue')
        ax.set_aspect('equal', adjustable='box')
        ax.set_title(f'{pattern.capitalize()}\nGeographic', fontweight='bold')
        ax.grid(True, alpha=0.3)
        
        # Plot grid
        ax = axes[1, idx]
        for row in range(1, 7):
            for col in range(1, 7):
                from matplotlib.patches import Rectangle
                rect = Rectangle((col-1, row-1), 1, 1,
                               linewidth=1, edgecolor='black',
                               facecolor='white', alpha=1.0)
                ax.add_patch(rect)
        
        ax.scatter(result['col'] - 0.5, result['row'] - 0.5,
                  s=50, alpha=0.7, c='blue')
        ax.set_xlim(-0.5, 6.5)
        ax.set_ylim(-0.5, 6.5)
        ax.set_aspect('equal')
        ax.set_title(f'Grid Allocation\nRMSE={quality["rmse"]:.2f}', 
                    fontweight='bold')
        ax.grid(True, alpha=0.3)
    
    fig.suptitle('Geographic Patterns and Grid Allocations', 
                 fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig('examples/demo4_patterns.png', dpi=150, bbox_inches='tight')
    print("\nVisualization saved as 'demo4_patterns.png'")
    plt.close()


def demo_grid_size_exploration():
    """
    Demo 5: Exploring different grid sizes
    
    This replicates the R package example of trying different grid configurations
    to find the best balance between graphic space and geographic fidelity.
    """
    print("\n" + "=" * 70)
    print("DEMO 5: Grid Size Exploration")
    print("=" * 70)
    
    # Generate test data
    pts = generate_sample_points(n_points=50, pattern='cluster', seed=456)
    
    # Try different grid sizes
    grid_sizes = [(8, 8), (10, 10), (12, 12), (15, 15)]
    
    print("\nGrid size analysis:")
    print(f"{'Grid Size':<15} {'Available':<12} {'Points':<10} {'RMSE':<12}")
    print("-" * 50)
    
    fig, axes = plt.subplots(1, 4, figsize=(16, 4))
    
    for idx, (n_row, n_col) in enumerate(grid_sizes):
        result = points_to_grid(pts, n_row, n_col, compactness=0.6)
        quality = compute_allocation_quality(result)
        
        available_cells = n_row * n_col
        print(f"{n_row}x{n_col:<11} {available_cells:<12} {len(pts):<10} "
              f"{quality['rmse']:<12.3f}")
        
        # Visualize
        ax = axes[idx]
        for row in range(1, n_row + 1):
            for col in range(1, n_col + 1):
                from matplotlib.patches import Rectangle
                rect = Rectangle((col-1, row-1), 1, 1,
                               linewidth=0.5, edgecolor='gray',
                               facecolor='white', alpha=1.0)
                ax.add_patch(rect)
        
        ax.scatter(result['col'] - 0.5, result['row'] - 0.5,
                  s=40, alpha=0.7, c='blue')
        ax.set_xlim(-0.5, n_col + 0.5)
        ax.set_ylim(-0.5, n_row + 0.5)
        ax.set_aspect('equal')
        ax.set_title(f'{n_row}×{n_col} Grid\nRMSE={quality["rmse"]:.2f}',
                    fontweight='bold', fontsize=10)
        ax.grid(True, alpha=0.2)
        ax.set_xticks([])
        ax.set_yticks([])
    
    fig.suptitle('Grid Size Exploration: Balancing Detail vs. Fidelity',
                 fontsize=13, fontweight='bold')
    plt.tight_layout()
    plt.savefig('examples/demo5_grid_sizes.png', dpi=150, bbox_inches='tight')
    print("\nVisualization saved as 'demo5_grid_sizes.png'")
    plt.close()


def run_all_demos():
    """
    Run all demonstration examples
    """
    print("\n")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  PYGRIDMAPPR DEMONSTRATION SUITE".center(68) + "║")
    print("║" + "  Python Implementation of R package gridmappr".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    print()
    
    try:
        demo_basic_allocation()
        demo_compactness_effect()
        demo_with_spacers()
        demo_geographic_patterns()
        demo_grid_size_exploration()
        
        print("\n" + "=" * 70)
        print("ALL DEMOS COMPLETED SUCCESSFULLY")
        print("=" * 70)
        print("\nGenerated files:")
        print("  - demo1_basic.png")
        print("  - demo2_compactness.png")
        print("  - demo3_spacers.png")
        print("  - demo4_patterns.png")
        print("  - demo5_grid_sizes.png")
        print("\nFor more information, see: https://github.com/rogerbeecham/gridmappr")
        
    except Exception as e:
        print(f"\n❌ Error during demo execution: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    run_all_demos()
