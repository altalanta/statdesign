#!/usr/bin/env python3
"""
Test suite for graph_features module.

This script tests the functionality of the TargetGraphFeaturizer
without requiring an actual STRING database file.
"""

import os
import tempfile
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from graph_features import TargetGraphFeaturizer, augment_features_with_graph


class TestTargetGraphFeaturizer:
    """Test cases for TargetGraphFeaturizer class."""

    def test_initialization(self):
        """Test basic initialization."""
        featurizer = TargetGraphFeaturizer()
        assert featurizer.confidence_threshold == 700
        assert featurizer.graph is None
        assert len(featurizer.feature_names) == 15

        # Test with custom parameters
        featurizer2 = TargetGraphFeaturizer(string_db_path="test.txt", confidence_threshold=800)
        assert featurizer2.string_db_path == "test.txt"
        assert featurizer2.confidence_threshold == 800

    def test_feature_names(self):
        """Test that feature names are correctly defined."""
        featurizer = TargetGraphFeaturizer()
        feature_names = featurizer.get_feature_names()

        expected_features = [
            "degree_centrality",
            "betweenness_centrality",
            "closeness_centrality",
            "pagerank_score",
            "clustering_coefficient",
            "n_neighbors_1hop",
            "n_neighbors_2hop",
            "avg_neighbor_degree",
            "max_neighbor_degree",
            "pathway_participation_score",
            "hub_proximity_score",
            "bridge_score",
            "disease_gene_proximity_1hop",
            "disease_gene_proximity_2hop",
            "drugged_target_proximity_1hop",
        ]

        assert feature_names == expected_features
        assert len(feature_names) == 15

    def test_reference_sets(self):
        """Test that disease genes and drug targets are properly defined."""
        featurizer = TargetGraphFeaturizer()

        # Check that known disease genes are included
        assert "TP53" in featurizer.DISEASE_GENES
        assert "BRCA1" in featurizer.DISEASE_GENES
        assert "EGFR" in featurizer.DISEASE_GENES

        # Check that known drug targets are included
        assert "EGFR" in featurizer.DRUGGED_TARGETS
        assert "TNF" in featurizer.DRUGGED_TARGETS
        assert "ESR1" in featurizer.DRUGGED_TARGETS

    def test_extract_features_no_network(self):
        """Test feature extraction behavior when no network is loaded."""
        featurizer = TargetGraphFeaturizer()
        target_proteins = ["TP53", "EGFR", "UNKNOWN"]

        # Should raise error when no network loaded and no path provided
        with pytest.raises(ValueError, match="Network not loaded"):
            featurizer.extract_features(target_proteins)

    @patch("networkx.Graph")
    @patch("builtins.open")
    def test_mock_feature_extraction(self, mock_open, mock_graph):
        """Test feature extraction with mocked network."""
        # Create a mock graph
        mock_graph_instance = MagicMock()
        mock_graph.return_value = mock_graph_instance

        # Mock graph properties
        mock_graph_instance.number_of_nodes.return_value = 100
        mock_graph_instance.number_of_edges.return_value = 500
        mock_graph_instance.__contains__ = lambda self, protein: protein in ["TP53", "EGFR"]
        mock_graph_instance.neighbors = lambda protein: ["NEIGHBOR1", "NEIGHBOR2"]
        mock_graph_instance.degree = lambda protein: 10

        # Mock file content
        mock_file_content = """protein1 protein2 combined_score
9606.TP53 9606.EGFR 900
9606.EGFR 9606.BRCA1 850
"""
        mock_open.return_value.__enter__.return_value = mock_file_content.splitlines()

        # Test featurizer
        featurizer = TargetGraphFeaturizer(string_db_path="mock_string.txt")

        # Mock the centrality computation methods
        with (
            patch.object(featurizer, "_compute_centrality_features") as mock_centrality,
            patch.object(featurizer, "_compute_neighborhood_features") as mock_neighborhood,
            patch.object(featurizer, "_compute_proximity_features") as mock_proximity,
        ):
            # Set up mock returns
            n_proteins = 3
            mock_centrality.return_value = {
                "degree_centrality": np.array([0.5, 0.7, 0.0]),
                "betweenness_centrality": np.array([0.3, 0.6, 0.0]),
                "closeness_centrality": np.array([0.4, 0.8, 0.0]),
                "pagerank_score": np.array([0.2, 0.5, 0.0]),
                "clustering_coefficient": np.array([0.6, 0.4, 0.0]),
            }

            mock_neighborhood.return_value = {
                "n_neighbors_1hop": np.array([10, 15, 0]),
                "n_neighbors_2hop": np.array([50, 60, 0]),
                "avg_neighbor_degree": np.array([8.5, 12.3, 0]),
                "max_neighbor_degree": np.array([25, 30, 0]),
                "pathway_participation_score": np.array([0.3, 0.4, 0]),
                "hub_proximity_score": np.array([0.25, 0.35, 0]),
                "bridge_score": np.array([0.1, 0.2, 0]),
            }

            mock_proximity.return_value = {
                "disease_gene_proximity_1hop": np.array([2, 3, 0]),
                "disease_gene_proximity_2hop": np.array([5, 7, 0]),
                "drugged_target_proximity_1hop": np.array([1, 2, 0]),
            }

            # Test feature extraction
            target_proteins = ["TP53", "EGFR", "UNKNOWN"]

            # Mock the graph loading
            featurizer.graph = mock_graph_instance

            features = featurizer.extract_features(target_proteins)

            # Verify output shape
            assert features.shape == (3, 15)

            # Verify that features are normalized (should be between 0 and 1)
            assert np.all(features >= 0)
            assert np.all(features <= 1)

    def test_augment_features(self):
        """Test the augment_features_with_graph function."""
        # Create mock original features
        original_features = np.random.rand(5, 10)
        protein_ids = ["P1", "P2", "P3", "P4", "P5"]

        with patch.object(TargetGraphFeaturizer, "extract_features") as mock_extract:
            # Mock graph features
            mock_graph_features = np.random.rand(5, 15)
            mock_extract.return_value = mock_graph_features

            # Test augmentation
            combined = augment_features_with_graph(
                original_features, protein_ids, string_db_path="mock.txt"
            )

            # Verify shape
            expected_shape = (5, 25)  # 10 original + 15 graph features
            assert combined.shape == expected_shape

            # Verify that original features are preserved
            np.testing.assert_array_equal(combined[:, :10], original_features)

    def test_load_reference_files(self):
        """Test loading of external reference files."""
        # Create temporary files
        with tempfile.TemporaryDirectory() as temp_dir:
            disease_file = os.path.join(temp_dir, "disease_genes.txt")
            drug_file = os.path.join(temp_dir, "drugged_targets.txt")

            # Write test files
            with open(disease_file, "w") as f:
                f.write("TEST_DISEASE_GENE1\nTEST_DISEASE_GENE2\n")

            with open(drug_file, "w") as f:
                f.write("TEST_DRUG_TARGET1\nTEST_DRUG_TARGET2\n")

            # Change to temp directory
            original_cwd = os.getcwd()
            try:
                os.chdir(temp_dir)

                # Initialize featurizer (should load the files)
                featurizer = TargetGraphFeaturizer()

                # Check that genes were loaded
                assert "TEST_DISEASE_GENE1" in featurizer.DISEASE_GENES
                assert "TEST_DISEASE_GENE2" in featurizer.DISEASE_GENES
                assert "TEST_DRUG_TARGET1" in featurizer.DRUGGED_TARGETS
                assert "TEST_DRUG_TARGET2" in featurizer.DRUGGED_TARGETS

            finally:
                os.chdir(original_cwd)


def test_integration_example():
    """Test a complete integration example with mocked data."""
    # Create sample data
    n_samples, n_features = 100, 20
    original_features = np.random.rand(n_samples, n_features)
    protein_ids = [f"PROTEIN_{i}" for i in range(n_samples)]

    # Mock the feature extraction
    with (
        patch.object(TargetGraphFeaturizer, "load_string_network"),
        patch.object(TargetGraphFeaturizer, "extract_features") as mock_extract,
    ):
        # Mock return graph features
        mock_graph_features = np.random.rand(n_samples, 15)
        mock_extract.return_value = mock_graph_features

        # Test the augmentation
        enhanced_features = augment_features_with_graph(
            original_features, protein_ids, string_db_path="mock_string.txt"
        )

        # Verify results
        assert enhanced_features.shape == (n_samples, n_features + 15)

        # Original features should be preserved
        np.testing.assert_array_equal(enhanced_features[:, :n_features], original_features)


def run_tests():
    """Run all tests manually (without pytest)."""
    print("Running Graph Features Tests")
    print("=" * 40)

    try:
        # Test initialization
        print("✓ Testing initialization...")
        test_case = TestTargetGraphFeaturizer()
        test_case.test_initialization()

        print("✓ Testing feature names...")
        test_case.test_feature_names()

        print("✓ Testing reference sets...")
        test_case.test_reference_sets()

        print("✓ Testing no network behavior...")
        test_case.test_extract_features_no_network()

        print("✓ Testing integration example...")
        test_integration_example()

        print("\n" + "=" * 40)
        print("All tests passed! ✓")

    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    run_tests()
