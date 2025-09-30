# Graph-Based Feature Extraction for Drug Target Prioritization

This module implements network topology features that augment MLP-based classifiers with protein-protein interaction context from the STRING database. The key insight is that network context (who you interact with) is often more predictive than intrinsic properties for drug target success.

## Overview

The `TargetGraphFeaturizer` class extracts 15 graph-based features from protein-protein interaction networks to enhance drug target prediction models:

### Centrality Features (5)
- **degree_centrality**: Number of direct interactions (normalized)
- **betweenness_centrality**: How often protein lies on shortest paths between other proteins
- **closeness_centrality**: How close protein is to all other proteins in the network
- **pagerank_score**: Importance based on the importance of neighboring proteins
- **clustering_coefficient**: How clustered/interconnected are the protein's neighbors

### Neighborhood Features (8)
- **n_neighbors_1hop**: Number of direct interaction partners
- **n_neighbors_2hop**: Number of proteins exactly 2 steps away
- **avg_neighbor_degree**: Average connectivity of direct neighbors
- **max_neighbor_degree**: Highest connectivity among direct neighbors
- **pathway_participation_score**: Involvement in biological pathways (based on high-degree neighbors)
- **hub_proximity_score**: Average PageRank score of neighbors (closeness to network hubs)
- **bridge_score**: Tendency to connect different network clusters
- **disease_gene_proximity_1hop**: Count of known disease genes among direct neighbors

### Proximity Features (2)
- **disease_gene_proximity_2hop**: Count of known disease genes within 2 steps
- **drugged_target_proximity_1hop**: Count of existing drug targets among direct neighbors

## Installation

```bash
pip install -r requirements_graph_features.txt
```

## Quick Start

```python
from graph_features import TargetGraphFeaturizer, augment_features_with_graph
import numpy as np

# Initialize with STRING database
featurizer = TargetGraphFeaturizer(
    string_db_path='string_v11.5_protein_links.txt',
    confidence_threshold=700
)

# Extract features for target proteins
proteins = ['TP53', 'EGFR', 'BRCA1', 'MYC', 'PTEN']
graph_features = featurizer.extract_features(proteins)

print(f"Extracted {graph_features.shape[1]} features for {graph_features.shape[0]} proteins")
```

## Integration with Existing ML Pipeline

```python
# Combine with existing features
existing_features = np.random.rand(100, 50)  # Your current feature matrix
protein_ids = ['PROTEIN1', 'PROTEIN2', ...]  # Corresponding protein IDs

# Augment with graph features
enhanced_features = augment_features_with_graph(
    existing_features, 
    protein_ids,
    string_db_path='string_v11.5_protein_links.txt'
)

# Now train your classifier with enhanced features
from sklearn.ensemble import RandomForestClassifier
clf = RandomForestClassifier()
clf.fit(enhanced_features, target_labels)
```

## STRING Database Setup

1. Download the STRING database from https://string-db.org/cgi/download.pl
2. For human proteins, download: `9606.protein.links.v11.5.txt.gz`
3. Uncompress and provide the path to the featurizer

The file format should be:
```
protein1 protein2 combined_score
9606.ENSP00000000233 9606.ENSP00000272298 999
9606.ENSP00000000233 9606.ENSP00000253401 999
...
```

## Configuration Options

### Confidence Threshold
Set the minimum STRING confidence score (0-1000):
```python
featurizer = TargetGraphFeaturizer(
    string_db_path='string_db.txt',
    confidence_threshold=700  # High confidence interactions only
)
```

### Custom Disease Genes and Drug Targets
Create text files with additional genes:

**disease_genes.txt**:
```
TP53
BRCA1
BRCA2
EGFR
...
```

**drugged_targets.txt**:
```
EGFR
VEGFA
TNF
ESR1
...
```

These will be automatically loaded if present in the working directory.

## Performance Considerations

### Memory Optimization
- The full STRING network has ~20M edges
- Networks are filtered by organism and confidence threshold
- Graphs are cached using pickle after first load
- Sparse matrices used where possible

### Computational Efficiency
- Centrality measures computed once for all proteins
- Progress bars for long-running operations
- Betweenness centrality uses sampling for large networks
- Features normalized to [0,1] range using MinMaxScaler

### Caching
Networks are automatically cached in `.cache/` directory:
```
.cache/string_network_9606_700.pkl
```

## API Reference

### TargetGraphFeaturizer

#### Constructor
```python
TargetGraphFeaturizer(string_db_path=None, confidence_threshold=700)
```

#### Methods

**load_string_network(organism_id=9606)**
- Load STRING database for specified organism
- Returns NetworkX graph object
- Automatically caches for faster subsequent loads

**extract_features(target_proteins)**
- Extract 15 graph features for list of proteins
- Returns numpy array of shape (n_proteins, 15)
- Handles missing proteins gracefully (returns zeros)

**get_feature_names()**
- Returns list of 15 feature names
- Useful for feature importance analysis

### Utility Functions

**augment_features_with_graph(original_features, protein_ids, string_db_path=None)**
- Convenience function to add graph features to existing matrix
- Returns combined feature matrix

## Validation

The module includes basic validation for known hub proteins:

```python
from graph_features import test_known_hubs
test_known_hubs()
```

Expected behavior:
- TP53, EGFR, MYC should have high degree centrality
- BRCA1, PTEN should have moderate-to-high centrality
- Known hubs should have above-average PageRank scores

## Example Use Cases

### 1. Target Prioritization
Identify high-value drug targets by combining:
- Expression data (disease vs. normal)
- Sequence features (druggability scores)
- Graph features (network context)

### 2. Safety Assessment
Avoid targets that are:
- Highly connected hubs (potential for side effects)
- Bridge proteins connecting many pathways
- Close to essential genes

### 3. Mechanism Prediction
Use network features to predict:
- Likely mechanism of action
- Potential combination targets
- Biomarker candidates

## Biological Interpretation

### High Centrality Proteins
- Often essential genes
- Good targets for major diseases
- Higher risk of side effects
- May require careful dosing

### Peripheral Proteins
- Lower risk of off-target effects
- May need combination therapy
- Good for rare disease targets
- Easier to achieve selectivity

### Bridge Proteins
- Connect different biological processes
- Potential for broad therapeutic effects
- Risk of disrupting multiple pathways
- Good candidates for systems medicine

## Troubleshooting

### Common Issues

**"Network not loaded" error**
```python
# Make sure to load network first
featurizer.load_string_network()
# Or provide path in constructor
featurizer = TargetGraphFeaturizer(string_db_path='path/to/string.txt')
```

**"Proteins not found" warnings**
- Normal for some proteins not in STRING
- Check protein ID format (gene symbols vs. Ensembl IDs)
- STRING uses specific ID formats per organism

**Memory issues with large networks**
- Increase confidence threshold to reduce network size
- Use organism-specific databases only
- Consider using a subset of proteins for development

**Slow performance**
- Network loading is one-time cost (cached afterward)
- Centrality computation is expensive but done once
- Use progress bars to monitor long operations

## Extension Points

### Custom Features
Add new graph features by extending the class:

```python
class ExtendedFeaturizer(TargetGraphFeaturizer):
    def _compute_custom_features(self, target_proteins):
        # Implement your custom network features
        return features_dict
```

### Alternative Networks
Use other interaction databases:
- BioGRID
- HIPPIE
- IID
- Custom networks

### Multi-organism Support
Extend for comparative analysis across species:
```python
featurizer_human = TargetGraphFeaturizer(organism_id=9606)
featurizer_mouse = TargetGraphFeaturizer(organism_id=10090)
```

## Citation

If you use this module in your research, please cite:
- STRING database: Szklarczyk et al., Nucleic Acids Research (2021)
- NetworkX: Hagberg et al., SciPy (2008)

## Contributing

Contributions welcome! Please:
1. Add tests for new features
2. Follow existing code style
3. Update documentation
4. Validate with known biological examples

## License

This module is provided under the MIT License.