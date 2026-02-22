# ML Toolkit MCP Server

Train, evaluate, and explain ML models interactively through Claude.

## Tools

| Tool | Description |
|------|-------------|
| `load_data` | Load a CSV dataset and see summary statistics |
| `train_model` | Train a model (7 algorithms available) |
| `evaluate` | Get classification report or regression metrics |
| `feature_importance` | Rank features by importance |
| `predict` | Make predictions on new data |

## Supported Models

- Linear Regression, Logistic Regression
- Random Forest, Gradient Boosting, Decision Tree
- SVM, KNN

## Setup

```bash
pip install mcp scikit-learn pandas numpy
claude mcp add ml-toolkit python servers/ml-toolkit/server.py
```
