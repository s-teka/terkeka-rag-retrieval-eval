# Evaluation Methodology

## 1. Label the evidence

Each query should identify the chunk(s) that are actually relevant. This is the ground truth for retrieval evaluation.

## 2. Keep retrieval and generation separate

A model may answer correctly from prior knowledge even when retrieval is wrong. Therefore:

1. evaluate retrieval,
2. evaluate grounding/citations,
3. evaluate final-answer quality.

Do not collapse all three into one score.

## 3. Metrics used here

### Recall@K
Measures how much of the labeled relevant set appears in the top K results.

### MRR
Measures the position of the first relevant result.

### NDCG@K
Measures ranking quality when relevance can be graded.

## 4. Release-gate idea

A future CI policy can fail when metrics drop below an accepted baseline, for example:

```text
mean Recall@3 >= 0.95
MRR           >= 0.90
mean NDCG@3   >= 0.90
```

Those are example thresholds only; production thresholds must be based on the real use case and evaluation set.

## 5. Dataset maintenance

The labeled set must evolve when:

- document structure changes,
- chunking changes,
- metadata or filters change,
- user query patterns change,
- new failure classes are discovered.
