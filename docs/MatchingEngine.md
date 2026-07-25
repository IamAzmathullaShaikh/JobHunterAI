# Matching Engine

The Matching Engine provides a scientific score of how well a candidate fits a role.

## 1. Scoring Algorithm
The score is a weighted average of several factors:

| Factor | Weight | Method |
| :--- | :--- | :--- |
| **Skills Match** | 35% | Exact and fuzzy matching (aliases) of skills. |
| **Experience** | 25% | Comparison of years of experience and seniority levels. |
| **Keywords** | 15% | Semantic similarity of resume text to JD keywords. |
| **Education** | 10% | Degree level and field of study matching. |
| **Location** | 10% | Remote vs On-site and proximity analysis. |
| **Salary** | 5% | Budget alignment (if available). |

## 2. Skill Aliasing
To prevent "unmatched" skills due to terminology differences, the system uses a deterministic alias map (e.g., "JS" -> "JavaScript", "ML" -> "Machine Learning").

## 3. Semantic Analysis
Beyond simple keyword matching, the engine uses **Embeddings** to understand context. For example, "Building distributed systems" and "Designing scalable backend architectures" will result in a high semantic match score even if the keywords differ.
