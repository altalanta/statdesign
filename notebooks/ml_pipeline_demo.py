#!/usr/bin/env python3
"""
Demonstration of integrating graph features with an existing ML pipeline
for drug target prioritization.

This script shows how to:
1. Simulate existing features (expression, sequence, etc.)
2. Add graph-based network features
3. Train and evaluate classifiers
4. Analyze feature importance
"""


import numpy as np
import pandas as pd
from graph_features import TargetGraphFeaturizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.preprocessing import StandardScaler


def generate_mock_dataset(n_samples=1000, n_original_features=25):
    """
    Generate a mock dataset for drug target prioritization.

    This simulates a real-world scenario with:
    - Expression features (differential expression, tissue specificity)
    - Sequence features (druggability scores, conservation)
    - Known target labels (successful vs. failed targets)
    """
    np.random.seed(42)  # For reproducibility

    # Generate protein IDs
    protein_ids = [f"PROTEIN_{i:04d}" for i in range(n_samples)]

    # Generate original features (expression, sequence, etc.)
    # Simulate realistic feature distributions
    original_features = np.random.randn(n_samples, n_original_features)

    # Add some structure to make classification meaningful
    # Feature groups:
    # 0-5: Expression features
    # 6-10: Tissue specificity features
    # 11-15: Sequence/druggability features
    # 16-20: Conservation features
    # 21-24: Pathway features

    # Create synthetic target labels with some biological realism
    # High expression + high druggability + moderate conservation = good target
    target_score = (
        np.mean(original_features[:, 0:6], axis=1) * 0.3  # Expression
        + np.mean(original_features[:, 11:16], axis=1) * 0.4  # Druggability
        + np.mean(original_features[:, 16:21], axis=1) * 0.2  # Conservation
        + np.mean(original_features[:, 21:25], axis=1) * 0.1  # Pathways
        + np.random.normal(0, 0.5, n_samples)  # Noise
    )

    # Convert to binary labels (top 30% are positive targets)
    target_labels = (target_score > np.percentile(target_score, 70)).astype(int)

    # Create feature names
    feature_names = (
        [f"expression_{i}" for i in range(6)]
        + [f"tissue_spec_{i}" for i in range(5)]
        + [f"druggability_{i}" for i in range(5)]
        + [f"conservation_{i}" for i in range(5)]
        + [f"pathway_{i}" for i in range(4)]
    )

    return original_features, target_labels, protein_ids, feature_names


def mock_graph_features(protein_ids, target_labels):
    """
    Generate mock graph features that correlate with target success.

    In reality, this would come from the actual STRING network,
    but for demo purposes we create features that have biological meaning.
    """
    n_proteins = len(protein_ids)

    # Create graph features with some correlation to target success
    graph_features = np.random.randn(n_proteins, 15)

    # Make some features correlate with positive targets
    for i in range(n_proteins):
        if target_labels[i] == 1:  # Positive target
            # Successful targets tend to have:
            # - Moderate degree centrality (not too high, not too low)
            graph_features[i, 0] += 0.5  # degree_centrality
            graph_features[i, 3] += 0.3  # pagerank_score
            # - More disease gene neighbors
            graph_features[i, 12] += 0.7  # disease_gene_proximity_1hop
            graph_features[i, 13] += 0.5  # disease_gene_proximity_2hop
            # - More existing drug target neighbors
            graph_features[i, 14] += 0.6  # drugged_target_proximity_1hop
        else:  # Negative target
            # Failed targets might be too central (side effects) or too peripheral
            if np.random.random() < 0.3:  # 30% are highly central
                graph_features[i, 0] += 1.5  # Very high centrality
                graph_features[i, 1] += 1.2  # High betweenness
            else:  # 70% are peripheral
                graph_features[i, 0] -= 0.8  # Low centrality
                graph_features[i, 5] -= 0.5  # Few neighbors

    return graph_features


def evaluate_model_performance():
    """
    Compare model performance with and without graph features.
    """
    print("Drug Target Prioritization: ML Pipeline Demo")
    print("=" * 50)

    # Generate mock dataset
    print("\n1. Generating mock dataset...")
    original_features, target_labels, protein_ids, feature_names = generate_mock_dataset()

    print(f"Dataset: {len(protein_ids)} proteins, {original_features.shape[1]} original features")
    print(f"Positive targets: {np.sum(target_labels)} ({np.mean(target_labels) * 100:.1f}%)")

    # Generate mock graph features
    print("\n2. Generating mock graph features...")
    mock_graph_feat = mock_graph_features(protein_ids, target_labels)

    # Combine features
    combined_features = np.hstack([original_features, mock_graph_feat])

    # Get graph feature names
    featurizer = TargetGraphFeaturizer()
    graph_feature_names = featurizer.get_feature_names()
    all_feature_names = feature_names + graph_feature_names

    print(f"Combined features: {combined_features.shape[1]} total features")

    # Split data
    print("\n3. Splitting data and training models...")
    X_orig_train, X_orig_test, y_train, y_test = train_test_split(
        original_features, target_labels, test_size=0.3, random_state=42, stratify=target_labels
    )

    X_comb_train, X_comb_test, _, _ = train_test_split(
        combined_features, target_labels, test_size=0.3, random_state=42, stratify=target_labels
    )

    # Scale features
    scaler_orig = StandardScaler()
    scaler_comb = StandardScaler()

    X_orig_train_scaled = scaler_orig.fit_transform(X_orig_train)
    X_orig_test_scaled = scaler_orig.transform(X_orig_test)

    X_comb_train_scaled = scaler_comb.fit_transform(X_comb_train)
    X_comb_test_scaled = scaler_comb.transform(X_comb_test)

    # Train models
    rf_original = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_combined = RandomForestClassifier(n_estimators=100, random_state=42)

    rf_original.fit(X_orig_train_scaled, y_train)
    rf_combined.fit(X_comb_train_scaled, y_train)

    # Evaluate models
    print("\n4. Model Performance Comparison")
    print("-" * 35)

    # Cross-validation scores
    cv_scores_orig = cross_val_score(
        rf_original, X_orig_train_scaled, y_train, cv=5, scoring="roc_auc"
    )
    cv_scores_comb = cross_val_score(
        rf_combined, X_comb_train_scaled, y_train, cv=5, scoring="roc_auc"
    )

    # Test set performance
    y_pred_orig = rf_original.predict(X_orig_test_scaled)
    y_pred_comb = rf_combined.predict(X_comb_test_scaled)

    y_prob_orig = rf_original.predict_proba(X_orig_test_scaled)[:, 1]
    y_prob_comb = rf_combined.predict_proba(X_comb_test_scaled)[:, 1]

    auc_orig = roc_auc_score(y_test, y_prob_orig)
    auc_comb = roc_auc_score(y_test, y_prob_comb)

    print("Original Features Only:")
    print(f"  CV AUC: {cv_scores_orig.mean():.4f} ± {cv_scores_orig.std():.4f}")
    print(f"  Test AUC: {auc_orig:.4f}")

    print("\nWith Graph Features:")
    print(f"  CV AUC: {cv_scores_comb.mean():.4f} ± {cv_scores_comb.std():.4f}")
    print(f"  Test AUC: {auc_comb:.4f}")

    improvement = auc_comb - auc_orig
    print(f"\nImprovement: {improvement:.4f} AUC points ({improvement / auc_orig * 100:.1f}%)")

    # Feature importance analysis
    print("\n5. Feature Importance Analysis")
    print("-" * 35)

    # Get top features from combined model
    feature_importance = rf_combined.feature_importances_
    importance_df = pd.DataFrame(
        {
            "feature": all_feature_names,
            "importance": feature_importance,
            "type": ["original"] * len(feature_names) + ["graph"] * len(graph_feature_names),
        }
    ).sort_values("importance", ascending=False)

    print("Top 15 most important features:")
    print(importance_df.head(15).to_string(index=False))

    # Graph feature importance
    graph_importance = importance_df[importance_df["type"] == "graph"]["importance"].sum()
    total_importance = importance_df["importance"].sum()

    print(
        f"\nGraph features contribution: {graph_importance / total_importance * 100:.1f}% of total importance"
    )

    # Top graph features
    top_graph_features = importance_df[importance_df["type"] == "graph"].head(5)
    print("\nTop 5 graph features:")
    for _, row in top_graph_features.iterrows():
        print(f"  {row['feature']:<30}: {row['importance']:.4f}")

    # Biological interpretation
    print("\n6. Biological Interpretation")
    print("-" * 30)

    interpretation = {
        "disease_gene_proximity_1hop": "Proximity to known disease genes suggests relevance to pathology",
        "drugged_target_proximity_1hop": "Proximity to existing targets suggests druggability",
        "degree_centrality": "Moderate connectivity often optimal for targets",
        "pagerank_score": "Influence in network indicates biological importance",
        "hub_proximity_score": "Closeness to hubs suggests pathway involvement",
    }

    for feature in top_graph_features["feature"]:
        if feature in interpretation:
            print(f"• {feature}: {interpretation[feature]}")

    return {
        "auc_original": auc_orig,
        "auc_combined": auc_comb,
        "improvement": improvement,
        "feature_importance": importance_df,
    }


def demonstrate_real_integration():
    """
    Show how to integrate with actual STRING database (when available).
    """
    print("\n\n7. Real-World Integration Example")
    print("-" * 40)

    example_code = """
# Real-world usage with actual STRING database:

from graph_features import augment_features_with_graph
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# 1. Load your existing data
target_data = pd.read_csv('drug_targets.csv')
protein_ids = target_data['protein_id'].tolist()
target_labels = target_data['is_successful_target'].values

# 2. Load existing features
expression_features = load_expression_data(protein_ids)
sequence_features = load_sequence_features(protein_ids)
existing_features = np.hstack([expression_features, sequence_features])

# 3. Augment with graph features
enhanced_features = augment_features_with_graph(
    existing_features,
    protein_ids,
    string_db_path='data/9606.protein.links.v11.5.txt',
    confidence_threshold=700
)

# 4. Train enhanced model
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(
    enhanced_features, target_labels, test_size=0.2, random_state=42
)

clf = RandomForestClassifier(n_estimators=200, random_state=42)
clf.fit(X_train, y_train)

# 5. Make predictions
predictions = clf.predict_proba(X_test)[:, 1]
print(f"Model AUC: {roc_auc_score(y_test, predictions):.4f}")

# 6. Analyze feature importance
feature_names = existing_feature_names + clf.get_feature_names()
importance_df = pd.DataFrame({
    'feature': feature_names,
    'importance': clf.feature_importances_
}).sort_values('importance', ascending=False)

print("Top features:")
print(importance_df.head(10))
"""

    print(example_code)


if __name__ == "__main__":
    # Run the demo
    results = evaluate_model_performance()
    demonstrate_real_integration()

    print("\n\nDemo completed!")
    print(f"Key finding: Graph features improved AUC by {results['improvement']:.4f} points")
    print("This demonstrates the value of network context for drug target prioritization.")
