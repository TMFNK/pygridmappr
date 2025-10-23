#!/usr/bin/env python3
"""
Debug script to compare spacer vs no-spacer allocations in detail
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

import pandas as pd
import numpy as np
from core import points_to_grid

# Reproduce the exact same data as in demo.py
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

print("Original data statistics:")
print(f"Mainland points: {n_mainland}")
print(f"Island points: {n_island}")
mainland_x_min = pts[pts['area_name'].str.startswith('M')]['x'].min()
mainland_x_max = pts[pts['area_name'].str.startswith('M')]['x'].max()
mainland_y_min = pts[pts['area_name'].str.startswith('M')]['y'].min()
mainland_y_max = pts[pts['area_name'].str.startswith('M')]['y'].max()
island_x_min = pts[pts['area_name'].str.startswith('I')]['x'].min()
island_x_max = pts[pts['area_name'].str.startswith('I')]['x'].max()
island_y_min = pts[pts['area_name'].str.startswith('I')]['y'].min()
island_y_max = pts[pts['area_name'].str.startswith('I')]['y'].max()

print(f"Mainland x range: {mainland_x_min:.2f} - {mainland_x_max:.2f}")
print(f"Mainland y range: {mainland_y_min:.2f} - {mainland_y_max:.2f}")
print(f"Island x range: {island_x_min:.2f} - {island_x_max:.2f}")
print(f"Island y range: {island_y_min:.2f} - {island_y_max:.2f}")
print()

# Define the same spacers as in demo.py
spacers = [
    (1, 11), (2, 11), (3, 11),  # Right edge, bottom rows
    (1, 10), (2, 10)             # One column left
]

print(f"Spacers: {spacers}")
print()

# Test without spacers
print("=" * 60)
print("WITHOUT SPACERS:")
print("=" * 60)
result_no_spacers = points_to_grid(pts, n_row=13, n_col=12, compactness=0.6)

island_assignments_no_spacers = result_no_spacers[result_no_spacers['area_name'].str.startswith('I')]
mainland_assignments_no_spacers = result_no_spacers[result_no_spacers['area_name'].str.startswith('M')]

print("Island assignments (no spacers):")
print(island_assignments_no_spacers[['area_name', 'row', 'col']].to_string(index=False))
print(f"Island positions: {list(zip(island_assignments_no_spacers['row'], island_assignments_no_spacers['col']))}")

print("\nMainland assignments (no spacers) - first 10:")
print(mainland_assignments_no_spacers[['area_name', 'row', 'col']].head(10).to_string(index=False))

# Test with spacers
print("\n" + "=" * 60)
print("WITH SPACERS:")
print("=" * 60)
result_with_spacers = points_to_grid(pts, n_row=13, n_col=12, compactness=0.6, spacers=spacers)

island_assignments_with_spacers = result_with_spacers[result_with_spacers['area_name'].str.startswith('I')]
mainland_assignments_with_spacers = result_with_spacers[result_with_spacers['area_name'].str.startswith('M')]

print("Island assignments (with spacers):")
print(island_assignments_with_spacers[['area_name', 'row', 'col']].to_string(index=False))
print(f"Island positions: {list(zip(island_assignments_with_spacers['row'], island_assignments_with_spacers['col']))}")

print("\nMainland assignments (with spacers) - first 10:")
print(mainland_assignments_with_spacers[['area_name', 'row', 'col']].head(10).to_string(index=False))

# Compare the assignments
print("\n" + "=" * 60)
print("COMPARISON:")
print("=" * 60)

island_positions_no_spacers = set(zip(island_assignments_no_spacers['row'], island_assignments_no_spacers['col']))
island_positions_with_spacers = set(zip(island_assignments_with_spacers['row'], island_assignments_with_spacers['col']))

print(f"Island positions without spacers: {sorted(island_positions_no_spacers)}")
print(f"Island positions with spacers: {sorted(island_positions_with_spacers)}")
print(f"Are island positions different? {island_positions_no_spacers != island_positions_with_spacers}")

# Check if any island points got assigned to spacer cells
spacer_set = set(spacers)
island_spacer_conflicts = island_positions_with_spacers & spacer_set
print(f"Island points in spacer cells: {island_spacer_conflicts}")

# Check mainland-island adjacency
mainland_positions = set(zip(mainland_assignments_with_spacers['row'], mainland_assignments_with_spacers['col']))

# Check if island is separated from mainland
island_adjacent_to_mainland = False
for island_row, island_col in island_positions_with_spacers:
    # Check all 8 adjacent cells
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
            adjacent_row, adjacent_col = island_row + dr, island_col + dc
            if (adjacent_row, adjacent_col) in mainland_positions:
                island_adjacent_to_mainland = True
                break
        if island_adjacent_to_mainland:
            break

print(f"Is island still adjacent to mainland? {island_adjacent_to_mainland}")

# Check if the spacers actually create a barrier
spacers_create_barrier = True
for island_row, island_col in island_positions_with_spacers:
    # Check if there's a direct path to mainland that doesn't go through spacers
    # This is a simple check - see if mainland is in the same row or column
    mainland_in_same_row = any(pos[0] == island_row for pos in mainland_positions)
    mainland_in_same_col = any(pos[1] == island_col for pos in mainland_positions)

    if mainland_in_same_row or mainland_in_same_col:
        # Check if the path is blocked by spacers
        if island_col < 10:  # Island is on the left side of spacers
            # Check if there are spacers between island and mainland in this row
            path_blocked = any((island_row, c) in spacer_set for c in range(island_col + 1, 13))
            if not path_blocked:
                spacers_create_barrier = False
                break

print(f"Do spacers create an effective barrier? {spacers_create_barrier}")
