#!/usr/bin/env python3
"""
Example usage of the TargetGraphFeaturizer for drug target prioritization.

This script demonstrates how to:
1. Load a STRING protein interaction network
2. Extract graph-based features for target proteins
3. Integrate with existing feature matrices
4. Validate results with known hub proteins
"""

import numpy as np
from graph_features import TargetGraphFeaturizer, augment_features_with_graph

def main():
    print("Graph-based Feature Extraction Example")
    print("=" * 50)
    
    # Example 1: Basic feature extraction
    print("\n1. Basic Feature Extraction")
    print("-" * 30)
    
    # Initialize featurizer (you would provide actual STRING DB path)
    # featurizer = TargetGraphFeaturizer(string_db_path='string_v11.5_protein_links.txt')
    featurizer = TargetGraphFeaturizer()  # Will work if STRING file available
    
    # Example target proteins (mix of well-known and random)
    target_proteins = [
        'TP53',     # Tumor suppressor - should be highly connected
        'EGFR',     # Growth factor receptor - major hub
        'MYC',      # Transcription factor - highly connected
        'BRCA1',    # DNA repair - disease gene
        'PTEN',     # Tumor suppressor
        'UNKNOWN1', # Non-existent protein
        'RANDOM2'   # Another non-existent protein
    ]
    
    print(f"Target proteins: {target_proteins}")
    
    try:
        # Extract features (this would work with actual STRING database)
        # features = featurizer.extract_features(target_proteins)
        # print(f"Feature matrix shape: {features.shape}")
        # print(f"Feature names: {featurizer.get_feature_names()}")
        
        # Since we don't have STRING DB, create mock features for demonstration
        features = np.random.rand(len(target_proteins), 15)
        print(f"Mock feature matrix shape: {features.shape}")
        print(f"Feature names: {featurizer.get_feature_names()}")
        
        # Display feature summary
        print(f"\nFeature Summary:")
        feature_names = featurizer.get_feature_names()
        for i, name in enumerate(feature_names):
            print(f"{name:30s}: mean={features[:, i].mean():.4f}, std={features[:, i].std():.4f}")
            
    except Exception as e:
        print(f"Feature extraction failed: {e}")
        print("This is expected without a STRING database file")
    
    # Example 2: Integration with existing features
    print("\n\n2. Integration with Existing Features")
    print("-" * 40)
    
    # Mock existing feature matrix (e.g., from expression data, sequence features)
    n_samples = len(target_proteins)
    n_original_features = 20
    original_features = np.random.rand(n_samples, n_original_features)
    
    print(f"Original features shape: {original_features.shape}")
    
    try:
        # Augment with graph features
        # combined_features = augment_features_with_graph(
        #     original_features, 
        #     target_proteins,
        #     string_db_path='string_v11.5_protein_links.txt'
        # )
        
        # Mock combined features for demonstration
        graph_features = np.random.rand(n_samples, 15)
        combined_features = np.hstack([original_features, graph_features])
        
        print(f"Combined features shape: {combined_features.shape}")
        print(f"Added {combined_features.shape[1] - original_features.shape[1]} graph features")
        
    except Exception as e:
        print(f"Feature augmentation failed: {e}")
    
    # Example 3: Analyze known hubs
    print("\n\n3. Known Hub Analysis")
    print("-" * 25)
    
    known_hubs = ['TP53', 'EGFR', 'MYC', 'BRCA1', 'PTEN']
    print(f"Analyzing known hubs: {known_hubs}")
    
    # Mock analysis since we don't have STRING DB
    mock_centrality_scores = {
        'TP53': {'degree': 0.85, 'pagerank': 0.92, 'betweenness': 0.78},
        'EGFR': {'degree': 0.79, 'pagerank': 0.88, 'betweenness': 0.71},
        'MYC': {'degree': 0.73, 'pagerank': 0.81, 'betweenness': 0.69},
        'BRCA1': {'degree': 0.68, 'pagerank': 0.75, 'betweenness': 0.64},
        'PTEN': {'degree': 0.71, 'pagerank': 0.79, 'betweenness': 0.66}
    }
    
    print(f"\nMock centrality scores for known hubs:")
    print(f"{'Protein':<8} {'Degree':<8} {'PageRank':<10} {'Betweenness':<12}")
    print("-" * 40)
    for protein, scores in mock_centrality_scores.items():
        print(f"{protein:<8} {scores['degree']:<8.3f} {scores['pagerank']:<10.3f} {scores['betweenness']:<12.3f}")
    
    # Example 4: Feature interpretation
    print("\n\n4. Feature Interpretation Guide")
    print("-" * 35)
    
    feature_descriptions = {
        'degree_centrality': 'Number of direct interactions (normalized)',
        'betweenness_centrality': 'How often protein lies on shortest paths',
        'closeness_centrality': 'How close protein is to all other proteins',
        'pagerank_score': 'Importance based on neighbor importance',
        'clustering_coefficient': 'How clustered are protein neighbors',
        'n_neighbors_1hop': 'Number of direct interaction partners',
        'n_neighbors_2hop': 'Number of proteins 2 steps away',
        'avg_neighbor_degree': 'Average connectivity of neighbors',
        'max_neighbor_degree': 'Highest connectivity among neighbors',
        'pathway_participation_score': 'Involvement in biological pathways',
        'hub_proximity_score': 'Closeness to network hubs',
        'bridge_score': 'Tendency to connect different clusters',
        'disease_gene_proximity_1hop': 'Disease genes among direct neighbors',
        'disease_gene_proximity_2hop': 'Disease genes within 2 steps',
        'drugged_target_proximity_1hop': 'Existing drug targets among neighbors'
    }
    
    print("Feature interpretations:")
    for feature, description in feature_descriptions.items():
        print(f"  {feature:<30}: {description}")
    
    # Example 5: Usage in ML pipeline
    print("\n\n5. ML Pipeline Integration")
    print("-" * 30)
    
    print("""
Typical usage in a drug target prediction pipeline:

1. Load protein targets and existing features:
   targets = ['PROTEIN1', 'PROTEIN2', ...]
   expression_features = load_expression_data(targets)
   sequence_features = load_sequence_features(targets)
   
2. Combine existing features:
   existing_features = np.hstack([expression_features, sequence_features])
   
3. Augment with graph features:
   from graph_features import augment_features_with_graph
   
   full_features = augment_features_with_graph(
       existing_features, 
       targets,
       string_db_path='path/to/string_db.txt'
   )
   
4. Train classifier:
   from sklearn.ensemble import RandomForestClassifier
   clf = RandomForestClassifier()
   clf.fit(full_features, target_labels)
   
5. The graph features provide biological context that can significantly
   improve prediction accuracy, especially for:
   - Identifying targets in disease-relevant pathways
   - Finding targets with good druggability context
   - Avoiding targets that might cause off-target effects
    """)
    
    print("\nExample complete!")


if __name__ == "__main__":
    main()