"""
Tests for pygridmappr core functionality.
"""

import numpy as np
import pandas as pd
import pytest

from pygridmappr import compute_allocation_quality, points_to_grid


class TestPointsToGrid:
    def test_basic_2x2_allocation(self):
        pts = pd.DataFrame(
            {
                "area_name": ["A", "B", "C", "D"],
                "x": [0, 100, 100, 0],
                "y": [0, 0, 100, 100],
            }
        )
        result = points_to_grid(pts, n_row=2, n_col=2)

        assert "row" in result.columns
        assert "col" in result.columns
        assert "grid_x" in result.columns
        assert "grid_y" in result.columns
        assert len(result) == 4
        assert all(1 <= r <= 2 for r in result["row"])
        assert all(1 <= c <= 2 for c in result["col"])

    def test_3x3_grid(self):
        pts = pd.DataFrame(
            {"x": np.random.uniform(0, 100, 9), "y": np.random.uniform(0, 100, 9)}
        )
        result = points_to_grid(pts, n_row=3, n_col=3)

        assert len(result) == 9
        assert all(1 <= r <= 3 for r in result["row"])
        assert all(1 <= c <= 3 for c in result["col"])

    def test_non_square_grid(self):
        pts = pd.DataFrame({"x": [0, 50, 100], "y": [0, 50, 100]})
        result = points_to_grid(pts, n_row=3, n_col=2)

        assert len(result) == 3
        assert all(1 <= r <= 3 for r in result["row"])
        assert all(1 <= c <= 2 for c in result["col"])

    def test_with_spacers(self):
        pts = pd.DataFrame(
            {
                "area_name": ["A", "B", "C"],
                "x": [0, 100, 100],
                "y": [0, 0, 100],
            }
        )
        spacers = [(1, 1)]
        result = points_to_grid(pts, n_row=2, n_col=2, spacers=spacers)

        assert len(result) == 3

    def test_single_point(self):
        pts = pd.DataFrame({"x": [50], "y": [50]})
        result = points_to_grid(pts, n_row=1, n_col=1)

        assert len(result) == 1
        assert result["row"].iloc[0] == 1
        assert result["col"].iloc[0] == 1

    def test_all_same_x(self):
        pts = pd.DataFrame({"x": [50, 50, 50, 50], "y": [0, 25, 50, 75]})
        result = points_to_grid(pts, n_row=2, n_col=2)

        assert len(result) == 4

    def test_all_same_y(self):
        pts = pd.DataFrame({"x": [0, 25, 50, 75], "y": [50, 50, 50, 50]})
        result = points_to_grid(pts, n_row=2, n_col=2)

        assert len(result) == 4

    def test_too_many_points_raises_error(self):
        pts = pd.DataFrame({"x": range(10), "y": range(10)})
        with pytest.raises(ValueError, match="exceeds grid capacity"):
            points_to_grid(pts, n_row=2, n_col=2)

    def test_empty_dataframe_raises_error(self):
        pts = pd.DataFrame({"x": [], "y": []})
        with pytest.raises(ValueError, match="pts must not be empty"):
            points_to_grid(pts, n_row=1, n_col=1)

    def test_invalid_compactness_raises_error(self):
        pts = pd.DataFrame({"x": [0, 1], "y": [0, 1]})
        with pytest.raises(ValueError, match="compactness must be in"):
            points_to_grid(pts, n_row=2, n_col=2, compactness=1.5)

    def test_invalid_grid_dimensions_raises_error(self):
        pts = pd.DataFrame({"x": [0, 1], "y": [0, 1]})
        with pytest.raises(ValueError, match="n_row and n_col must be"):
            points_to_grid(pts, n_row=0, n_col=2)

    def test_missing_columns_raises_error(self):
        pts = pd.DataFrame({"z": [0, 1]})
        with pytest.raises(ValueError, match="pts must contain columns"):
            points_to_grid(pts, n_row=2, n_col=2)

    def test_non_dataframe_raises_error(self):
        with pytest.raises(TypeError, match="pts must be a pandas DataFrame"):
            points_to_grid([(0, 1), (2, 3)], n_row=2, n_col=2)


class TestDeterminism:
    def test_points_to_grid_deterministic(self):
        pts = pd.DataFrame(
            {
                "area_name": ["A", "B", "C", "D"],
                "x": [0, 100, 100, 0],
                "y": [0, 0, 100, 100],
            }
        )
        r1 = points_to_grid(pts, n_row=2, n_col=2, compactness=0.5)
        r2 = points_to_grid(pts, n_row=2, n_col=2, compactness=0.5)

        pd.testing.assert_frame_equal(r1, r2)


class TestNoMutation:
    def test_points_to_grid_does_not_mutate_input(self):
        pts = pd.DataFrame({"x": [0, 1, 1, 0], "y": [0, 0, 1, 1]})
        original_cols = set(pts.columns)
        _ = points_to_grid(pts, n_row=2, n_col=2)
        assert set(pts.columns) == original_cols, "Input DataFrame was mutated"


class TestComputeAllocationQuality:
    def test_returns_expected_keys(self):
        pts = pd.DataFrame({"x": [0, 100, 100, 0], "y": [0, 0, 100, 100]})
        result = points_to_grid(pts, n_row=2, n_col=2)
        quality = compute_allocation_quality(result)

        assert "mean_distance" in quality
        assert "total_distance" in quality
        assert "max_distance" in quality
        assert "rmse" in quality
        assert all(v >= 0 for v in quality.values())


class TestGenerateSamplePoints:
    def test_returns_correct_shape(self):
        from pygridmappr import generate_sample_points

        pts = generate_sample_points(n_points=20, pattern="random", seed=42)
        assert len(pts) == 20
        assert "x" in pts.columns
        assert "y" in pts.columns
        assert "area_name" in pts.columns
