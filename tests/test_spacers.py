#!/usr/bin/env python3
"""
Test script to verify spacer functionality in pygridmappr
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

import pandas as pd
import numpy as np
from core import points_to_grid

# Create simple test data
np.random.seed(42)

# Create two distinct clusters: mainland and island
mainland_points = pd.DataFrame({
    'area_name': [f'M{i+1}' for i in range(8)],
    'x': np.random.normal(30, 5, 8),
    'y': np.random.normal(50, 10, 8)
})

island_points = pd.DataFrame({
    'area_name': [f'I{i+1}' for i in range(3)],
    'x': np.random.normal(80, 3, 3),
    'y': np.random.normal(20, 3, 3)
})

# Combine all points
pts = pd.concat([mainland_points, island_points], ignore_index=True)

print("Test points:")
print(pts)
print()

# Define spacers to separate island from mainland
spacers = [
    (11, 1), (11, 2), (11, 3), (11, 4),  # Bottom row, left side
    (12, 1), (12, 2), (12, 3), (12, 4),  # Second row, left side
]

print(f"Using {len(spacers)} spacer cells")
print()

# Test without spacers
print("WITHOUT SPACERS:")
result_no_spacers = points_to_grid(pts, n_row=12, n_col=10, compactness=0.5)
print("Mainland assignments:")
mainland_assignments = result_no_spacers[result_no_spacers['area_name'].str.startswith('M')]
print(mainland_assignments[['area_name', 'row', 'col']].to_string(index=False))
print("\nIsland assignments:")
island_assignments = result_no_spacers[result_no_spacers['area_name'].str.startswith('I')]
print(island_assignments[['area_name', 'row', 'col']].to_string(index=False))
print()

# Test with spacers
print("WITH SPACERS:")
result_with_spacers = points_to_grid(pts, n_row=12, n_col=10, compactness=0.5, spacers=spacers)
print("Mainland assignments:")
mainland_assignments = result_with_spacers[result_with_spacers['area_name'].str.startswith('M')]
print(mainland_assignments[['area_name', 'row', 'col']].to_string(index=False))
print("\nIsland assignments:")
island_assignments = result_with_spacers[result_with_spacers['area_name'].str.startswith('I')]
print(island_assignments[['area_name', 'row', 'col']].to_string(index=False))
print()

# Check if spacers are actually being avoided
print("SPACER ANALYSIS:")
spacer_cells = set(spacers)
island_cells_with_spacers = set(zip(island_assignments['row'], island_assignments['col']))
mainland_cells_with_spacers = set(zip(mainland_assignments['row'], mainland_assignments['col']))

print(f"Spacer cells: {sorted(spacer_cells)}")
print(f"Island cells: {sorted(island_cells_with_spacers)}")
print(f"Mainland cells: {sorted(mainland_cells_with_spacers)}")

conflicts = spacer_cells & (island_cells_with_spacers | mainland_cells_with_spacers)
if conflicts:
    print(f"❌ ERROR: Points assigned to spacer cells: {conflicts}")
else:
    print("✅ SUCCESS: No points assigned to spacer cells")

# Check if island and mainland are separated by spacers
island_separated = len(island_cells_with_spacers & mainland_cells_with_spacers) == 0
print(f"Island separated from mainland: {island_separated}")
