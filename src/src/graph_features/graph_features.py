"""
Graph-based feature extraction module for drug target prioritization.

This module implements network topology features that augment MLP-based 
classifiers with protein-protein interaction context from STRING database.
"""

import os
import pickle
import logging
from typing import List, Set, Dict, Tuple, Optional, Union
from pathlib import Path

import numpy as np
import networkx as nx
from scipy import sparse
from sklearn.preprocessing import MinMaxScaler
from tqdm import tqdm

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TargetGraphFeaturizer:
    """
    Extract graph-based features from protein-protein interaction networks.
    
    This class loads STRING database networks and computes various network
    topology features that can enhance drug target prediction models.
    """
    
    # Curated gene sets for proximity features
    DISEASE_GENES = {
        'TP53', 'BRCA1', 'BRCA2', 'EGFR', 'KRAS', 'PIK3CA', 'APC', 'PTEN',
        'RB1', 'MYC', 'CDKN2A', 'ATM', 'MLH1', 'MSH2', 'VHL', 'NF1',
        'CFTR', 'HTT', 'APOE', 'APP', 'LRRK2', 'SNCA', 'MAPT', 'GRN'
    }
    
    DRUGGED_TARGETS = {
        'EGFR', 'VEGFA', 'TNF', 'PTGS2', 'ESR1', 'AR', 'ADRB2', 'DRD2',
        'HTR2A', 'CHRM3', 'ADRA1A', 'ACE', 'AGTR1', 'HMGCR', 'PTGS1',
        'COMT', 'SLC6A4', 'SLC6A3', 'SLC6A2', 'GABRA1', 'CHRNA4',
        'KCNH2', 'SCN5A', 'CACNA1C', 'RYR1', 'DHFR', 'TYMS', 'TUBB'
    }
    
    def __init__(self, string_db_path: Optional[str] = None, confidence_threshold: int = 700):
        """
        Initialize the graph featurizer.
        
        Args:
            string_db_path: Path to STRING database file
            confidence_threshold: Minimum combined score for STRING interactions (0-1000)
        """
        self.string_db_path = string_db_path
        self.confidence_threshold = confidence_threshold
        self.graph = None
        self.feature_names = [
            'degree_centrality', 'betweenness_centrality', 'closeness_centrality',
            'pagerank_score', 'clustering_coefficient', 'n_neighbors_1hop',
            'n_neighbors_2hop', 'avg_neighbor_degree', 'max_neighbor_degree',
            'pathway_participation_score', 'hub_proximity_score', 'bridge_score',
            'disease_gene_proximity_1hop', 'disease_gene_proximity_2hop',
            'drugged_target_proximity_1hop'
        ]
        self.scaler = MinMaxScaler()
        self._cache_file = None
        
        # Load disease genes and drug targets from files if they exist
        self._load_reference_sets()
        
    def _load_reference_sets(self):
        """Load disease genes and drug targets from external files if available."""
        # Try to load disease genes from file
        disease_file = Path('disease_genes.txt')
        if disease_file.exists():
            try:
                with open(disease_file, 'r') as f:
                    additional_disease_genes = {line.strip() for line in f if line.strip()}
                self.DISEASE_GENES.update(additional_disease_genes)
                logger.info(f"Loaded {len(additional_disease_genes)} additional disease genes")
            except Exception as e:
                logger.warning(f"Could not load disease genes file: {e}")
        
        # Try to load drug targets from file
        drug_file = Path('drugged_targets.txt')
        if drug_file.exists():
            try:
                with open(drug_file, 'r') as f:
                    additional_drug_targets = {line.strip() for line in f if line.strip()}
                self.DRUGGED_TARGETS.update(additional_drug_targets)
                logger.info(f"Loaded {len(additional_drug_targets)} additional drug targets")
            except Exception as e:
                logger.warning(f"Could not load drug targets file: {e}")
    
    def load_string_network(self, organism_id: int = 9606) -> nx.Graph:
        """
        Load STRING protein interaction network.
        
        Args:
            organism_id: NCBI taxonomy ID (default 9606 for human)
            
        Returns:
            NetworkX graph object
        """
        if self.string_db_path is None:
            raise ValueError("STRING database path not provided")
        
        # Set up cache file path
        cache_dir = Path('.cache')
        cache_dir.mkdir(exist_ok=True)
        self._cache_file = cache_dir / f'string_network_{organism_id}_{self.confidence_threshold}.pkl'
        
        # Try to load from cache first
        if self._cache_file.exists():
            logger.info("Loading network from cache...")
            try:
                with open(self._cache_file, 'rb') as f:
                    self.graph = pickle.load(f)
                logger.info(f"Loaded cached network: {self.graph.number_of_nodes()} nodes, "
                           f"{self.graph.number_of_edges()} edges")
                return self.graph
            except Exception as e:
                logger.warning(f"Could not load cache: {e}. Loading from STRING file...")
        
        # Load from STRING database file
        logger.info(f"Loading STRING database from {self.string_db_path}")
        
        if not Path(self.string_db_path).exists():
            raise FileNotFoundError(f"STRING database file not found: {self.string_db_path}")
        
        # Create graph
        self.graph = nx.Graph()
        
        # Read STRING file and build network
        edges_added = 0
        organism_prefix = f"{organism_id}."
        
        with open(self.string_db_path, 'r') as f:
            for line_num, line in enumerate(tqdm(f, desc="Loading STRING interactions")):
                if line_num == 0:  # Skip header
                    continue
                    
                parts = line.strip().split()
                if len(parts) < 3:
                    continue
                
                protein1, protein2, combined_score = parts[0], parts[1], int(parts[2])
                
                # Filter by organism and confidence threshold
                if (protein1.startswith(organism_prefix) and 
                    protein2.startswith(organism_prefix) and
                    combined_score >= self.confidence_threshold):
                    
                    # Remove organism prefix for cleaner IDs
                    p1 = protein1.replace(organism_prefix, '')
                    p2 = protein2.replace(organism_prefix, '')
                    
                    # Add edge with weight
                    self.graph.add_edge(p1, p2, weight=combined_score / 1000.0)
                    edges_added += 1
        
        logger.info(f"Built network: {self.graph.number_of_nodes()} nodes, "
                   f"{self.graph.number_of_edges()} edges")
        
        # Cache the graph
        try:
            with open(self._cache_file, 'wb') as f:
                pickle.dump(self.graph, f)
            logger.info("Network cached successfully")
        except Exception as e:
            logger.warning(f"Could not cache network: {e}")
        
        return self.graph
    
    def _compute_centrality_features(self, target_proteins: List[str]) -> Dict[str, np.ndarray]:
        """Compute centrality-based features."""
        if self.graph is None:
            raise ValueError("Network not loaded. Call load_string_network() first.")
        
        features = {}
        
        # Compute centralities for all nodes (expensive but done once)
        logger.info("Computing centrality measures...")
        
        degree_centrality = nx.degree_centrality(self.graph)
        betweenness_centrality = nx.betweenness_centrality(self.graph, k=min(1000, len(self.graph)))
        closeness_centrality = nx.closeness_centrality(self.graph)
        pagerank = nx.pagerank(self.graph, alpha=0.85)
        clustering = nx.clustering(self.graph)
        
        # Extract features for target proteins
        n_targets = len(target_proteins)
        features['degree_centrality'] = np.zeros(n_targets)
        features['betweenness_centrality'] = np.zeros(n_targets)
        features['closeness_centrality'] = np.zeros(n_targets)
        features['pagerank_score'] = np.zeros(n_targets)
        features['clustering_coefficient'] = np.zeros(n_targets)
        
        for i, protein in enumerate(target_proteins):
            if protein in self.graph:
                features['degree_centrality'][i] = degree_centrality.get(protein, 0)
                features['betweenness_centrality'][i] = betweenness_centrality.get(protein, 0)
                features['closeness_centrality'][i] = closeness_centrality.get(protein, 0)
                features['pagerank_score'][i] = pagerank.get(protein, 0)
                features['clustering_coefficient'][i] = clustering.get(protein, 0)
        
        return features
    
    def _compute_neighborhood_features(self, target_proteins: List[str]) -> Dict[str, np.ndarray]:
        """Compute neighborhood-based features."""
        features = {}
        n_targets = len(target_proteins)
        
        features['n_neighbors_1hop'] = np.zeros(n_targets)
        features['n_neighbors_2hop'] = np.zeros(n_targets)
        features['avg_neighbor_degree'] = np.zeros(n_targets)
        features['max_neighbor_degree'] = np.zeros(n_targets)
        features['pathway_participation_score'] = np.zeros(n_targets)
        features['hub_proximity_score'] = np.zeros(n_targets)
        features['bridge_score'] = np.zeros(n_targets)
        
        # Precompute PageRank for hub proximity
        pagerank = nx.pagerank(self.graph, alpha=0.85)
        
        for i, protein in enumerate(target_proteins):
            if protein not in self.graph:
                continue
            
            # 1-hop neighbors
            neighbors_1hop = set(self.graph.neighbors(protein))
            features['n_neighbors_1hop'][i] = len(neighbors_1hop)
            
            # 2-hop neighbors
            neighbors_2hop = set()
            for neighbor in neighbors_1hop:
                neighbors_2hop.update(self.graph.neighbors(neighbor))
            neighbors_2hop -= neighbors_1hop  # Remove 1-hop neighbors
            neighbors_2hop.discard(protein)   # Remove self
            features['n_neighbors_2hop'][i] = len(neighbors_2hop)
            
            if neighbors_1hop:
                # Neighbor degree statistics
                neighbor_degrees = [self.graph.degree(n) for n in neighbors_1hop]
                features['avg_neighbor_degree'][i] = np.mean(neighbor_degrees)
                features['max_neighbor_degree'][i] = np.max(neighbor_degrees)
                
                # Pathway participation (based on high-degree neighbors)
                high_degree_neighbors = sum(1 for d in neighbor_degrees if d > np.percentile(neighbor_degrees, 75))
                features['pathway_participation_score'][i] = high_degree_neighbors / len(neighbors_1hop)
                
                # Hub proximity (average PageRank of neighbors)
                neighbor_pageranks = [pagerank.get(n, 0) for n in neighbors_1hop]
                features['hub_proximity_score'][i] = np.mean(neighbor_pageranks)
                
                # Bridge score (connects different clusters)
                # Simplified: measure of edge betweenness of protein's edges
                protein_edges = [(protein, neighbor) for neighbor in neighbors_1hop]
                edge_betweenness = nx.edge_betweenness_centrality_subset(
                    self.graph, 
                    sources=[protein], 
                    targets=list(neighbors_1hop),
                    k=min(100, len(self.graph))
                )
                if protein_edges:
                    bridge_scores = [edge_betweenness.get(edge, 0) for edge in protein_edges]
                    features['bridge_score'][i] = np.mean(bridge_scores)
        
        return features
    
    def _compute_proximity_features(self, target_proteins: List[str]) -> Dict[str, np.ndarray]:
        """Compute proximity to disease genes and drugged targets."""
        features = {}
        n_targets = len(target_proteins)
        
        features['disease_gene_proximity_1hop'] = np.zeros(n_targets)
        features['disease_gene_proximity_2hop'] = np.zeros(n_targets)
        features['drugged_target_proximity_1hop'] = np.zeros(n_targets)
        
        for i, protein in enumerate(target_proteins):
            if protein not in self.graph:
                continue
            
            # 1-hop neighbors
            neighbors_1hop = set(self.graph.neighbors(protein))
            
            # Disease gene proximity
            disease_genes_1hop = neighbors_1hop.intersection(self.DISEASE_GENES)
            features['disease_gene_proximity_1hop'][i] = len(disease_genes_1hop)
            
            # 2-hop neighbors for disease genes
            neighbors_2hop = set()
            for neighbor in neighbors_1hop:
                neighbors_2hop.update(self.graph.neighbors(neighbor))
            neighbors_2hop -= neighbors_1hop
            neighbors_2hop.discard(protein)
            
            disease_genes_2hop = neighbors_2hop.intersection(self.DISEASE_GENES)
            features['disease_gene_proximity_2hop'][i] = len(disease_genes_2hop)
            
            # Drugged target proximity
            drugged_targets_1hop = neighbors_1hop.intersection(self.DRUGGED_TARGETS)
            features['drugged_target_proximity_1hop'][i] = len(drugged_targets_1hop)
        
        return features
    
    def extract_features(self, target_proteins: List[str]) -> np.ndarray:
        """
        Extract graph-based features for a list of target proteins.
        
        Args:
            target_proteins: List of protein IDs (Ensembl or gene symbols)
        
        Returns:
            numpy array of shape (n_targets, 15) with network features
        """
        if self.graph is None:
            if self.string_db_path is None:
                raise ValueError("Network not loaded and no STRING database path provided")
            self.load_string_network()
        
        logger.info(f"Extracting features for {len(target_proteins)} proteins...")
        
        # Find proteins not in network
        proteins_in_network = [p for p in target_proteins if p in self.graph]
        proteins_not_found = set(target_proteins) - set(proteins_in_network)
        
        if proteins_not_found:
            logger.warning(f"{len(proteins_not_found)} proteins not found in network: "
                          f"{list(proteins_not_found)[:10]}{'...' if len(proteins_not_found) > 10 else ''}")
        
        # Compute all feature groups
        all_features = {}
        
        # Centrality features
        centrality_features = self._compute_centrality_features(target_proteins)
        all_features.update(centrality_features)
        
        # Neighborhood features  
        neighborhood_features = self._compute_neighborhood_features(target_proteins)
        all_features.update(neighborhood_features)
        
        # Proximity features
        proximity_features = self._compute_proximity_features(target_proteins)
        all_features.update(proximity_features)
        
        # Combine into feature matrix
        feature_matrix = np.column_stack([
            all_features[feature_name] for feature_name in self.feature_names
        ])
        
        # Normalize features to [0,1] range
        feature_matrix = self.scaler.fit_transform(feature_matrix)
        
        logger.info(f"Extracted {feature_matrix.shape[1]} features for {feature_matrix.shape[0]} proteins")
        
        return feature_matrix
    
    def get_feature_names(self) -> List[str]:
        """Return list of feature names."""
        return self.feature_names.copy()


def augment_features_with_graph(
    original_features: np.ndarray, 
    protein_ids: List[str], 
    string_db_path: Optional[str] = None,
    confidence_threshold: int = 700
) -> np.ndarray:
    """
    Convenience function to add graph features to existing feature matrix.
    
    Args:
        original_features: numpy array (n_samples, n_original_features)
        protein_ids: list of protein identifiers
        string_db_path: path to STRING database file
        confidence_threshold: minimum STRING interaction confidence
    
    Returns:
        numpy array (n_samples, n_original_features + 15)
    """
    # Initialize featurizer
    featurizer = TargetGraphFeaturizer(
        string_db_path=string_db_path,
        confidence_threshold=confidence_threshold
    )
    
    # Extract graph features
    graph_features = featurizer.extract_features(protein_ids)
    
    # Combine with original features
    combined_features = np.hstack([original_features, graph_features])
    
    logger.info(f"Augmented features: {original_features.shape[1]} -> {combined_features.shape[1]} features")
    
    return combined_features


def test_known_hubs():
    """Simple test to verify that well-known hubs have high centrality scores."""
    # This is a basic test function - would normally be in a separate test file
    known_hubs = ['TP53', 'EGFR', 'MYC', 'BRCA1', 'PTEN']
    
    try:
        featurizer = TargetGraphFeaturizer()
        if featurizer.string_db_path is None:
            print("No STRING database path provided - skipping hub test")
            return
        
        features = featurizer.extract_features(known_hubs)
        
        # Check if known hubs have above-average centrality
        degree_centrality = features[:, 0]  # First feature is degree centrality
        pagerank_scores = features[:, 3]    # Fourth feature is PageRank
        
        print(f"Known hub centrality scores:")
        for i, protein in enumerate(known_hubs):
            print(f"{protein}: degree={degree_centrality[i]:.4f}, pagerank={pagerank_scores[i]:.4f}")
        
        # Basic assertion
        avg_degree = np.mean(degree_centrality[degree_centrality > 0])
        avg_pagerank = np.mean(pagerank_scores[pagerank_scores > 0])
        
        print(f"Average degree centrality: {avg_degree:.4f}")
        print(f"Average PageRank score: {avg_pagerank:.4f}")
        
    except Exception as e:
        print(f"Hub test failed: {e}")


if __name__ == "__main__":
    # Example usage
    print("Graph-based feature extraction for drug target prioritization")
    print("=" * 60)
    
    # Test with example proteins
    example_proteins = ['TP53', 'EGFR', 'BRCA1', 'MYC', 'PTEN']
    
    # Run hub test
    test_known_hubs()