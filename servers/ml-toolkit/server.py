"""
MCP Server: ML Toolkit
Train, evaluate, and explain ML models interactively through Claude.
"""

import asyncio
import json
import io
import numpy as np
import pandas as pd
from mcp.server import Server
from mcp.types import Tool, TextContent

app = Server("ml-toolkit")

# In-memory store for loaded data and trained models
_store = {"data": None, "model": None, "model_name": None, "X_train": None, "y_train": None}


@app.list_tools()
async def list_tools():
    return [
        Tool(
            name="load_data",
            description="Load a CSV dataset for ML training. Returns summary statistics.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to CSV file"},
                    "target": {"type": "string", "description": "Target column name"}
                },
                "required": ["path", "target"]
            }
        ),
        Tool(
            name="train_model",
            description="Train an ML model on the loaded dataset.",
            inputSchema={
                "type": "object",
                "properties": {
                    "model_type": {
                        "type": "string",
                        "enum": ["linear_regression", "logistic_regression", "random_forest",
                                 "gradient_boosting", "svm", "knn", "decision_tree"],
                        "description": "Type of model to train"
                    },
                    "test_size": {"type": "number", "default": 0.2, "description": "Test split ratio"}
                },
                "required": ["model_type"]
            }
        ),
        Tool(
            name="evaluate",
            description="Evaluate the trained model and return metrics.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="feature_importance",
            description="Get feature importance from the trained model.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="predict",
            description="Make predictions on new data.",
            inputSchema={
                "type": "object",
                "properties": {
                    "data": {"type": "string", "description": "JSON array of feature values"}
                },
                "required": ["data"]
            }
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    if name == "load_data":
        return load_data(arguments)
    elif name == "train_model":
        return train_model(arguments)
    elif name == "evaluate":
        return evaluate_model()
    elif name == "feature_importance":
        return get_feature_importance()
    elif name == "predict":
        return predict(arguments)
    raise ValueError(f"Unknown tool: {name}")


def load_data(args):
    try:
        df = pd.read_csv(args["path"])
        target = args["target"]
        _store["data"] = df
        _store["target"] = target

        info = {
            "shape": list(df.shape),
            "columns": list(df.columns),
            "target": target,
            "target_dtype": str(df[target].dtype),
            "missing_values": df.isnull().sum().to_dict(),
            "summary": df.describe().to_dict()
        }
        return [TextContent(type="text", text=f"Data loaded successfully.\n\n{json.dumps(info, indent=2, default=str)}")]
    except Exception as e:
        return [TextContent(type="text", text=f"Error loading data: {e}")]


def train_model(args):
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import StandardScaler, LabelEncoder
    from sklearn import linear_model, ensemble, svm, neighbors, tree

    if _store["data"] is None:
        return [TextContent(type="text", text="No data loaded. Use load_data first.")]

    df = _store["data"]
    target = _store["target"]
    model_type = args["model_type"]
    test_size = args.get("test_size", 0.2)

    X = df.drop(columns=[target])
    y = df[target]

    # Handle categorical features
    for col in X.select_dtypes(include=["object"]).columns:
        X[col] = LabelEncoder().fit_transform(X[col].astype(str))

    if y.dtype == "object":
        le = LabelEncoder()
        y = le.fit_transform(y)

    X = X.fillna(X.median(numeric_only=True))
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42)

    models = {
        "linear_regression": linear_model.LinearRegression(),
        "logistic_regression": linear_model.LogisticRegression(max_iter=1000),
        "random_forest": ensemble.RandomForestClassifier(n_estimators=100, random_state=42),
        "gradient_boosting": ensemble.GradientBoostingClassifier(random_state=42),
        "svm": svm.SVC(kernel="rbf"),
        "knn": neighbors.KNeighborsClassifier(),
        "decision_tree": tree.DecisionTreeClassifier(random_state=42),
    }

    model = models.get(model_type)
    if model is None:
        return [TextContent(type="text", text=f"Unknown model: {model_type}")]

    model.fit(X_train, y_train)
    _store["model"] = model
    _store["model_name"] = model_type
    _store["X_test"] = X_test
    _store["y_test"] = y_test
    _store["feature_names"] = list(X.columns)

    train_score = model.score(X_train, y_train)
    test_score = model.score(X_test, y_test)

    result = {
        "model": model_type,
        "train_score": round(train_score, 4),
        "test_score": round(test_score, 4),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "features": len(X.columns)
    }
    return [TextContent(type="text", text=f"Model trained!\n\n{json.dumps(result, indent=2)}")]


def evaluate_model():
    from sklearn.metrics import classification_report, mean_squared_error, r2_score

    if _store["model"] is None:
        return [TextContent(type="text", text="No model trained. Use train_model first.")]

    model = _store["model"]
    X_test = _store["X_test"]
    y_test = _store["y_test"]
    y_pred = model.predict(X_test)

    if _store["model_name"] == "linear_regression":
        metrics = {
            "mse": round(mean_squared_error(y_test, y_pred), 4),
            "rmse": round(mean_squared_error(y_test, y_pred, squared=False), 4),
            "r2": round(r2_score(y_test, y_pred), 4)
        }
    else:
        report = classification_report(y_test, y_pred, output_dict=True)
        metrics = report

    return [TextContent(type="text", text=json.dumps(metrics, indent=2, default=str))]


def get_feature_importance():
    if _store["model"] is None:
        return [TextContent(type="text", text="No model trained.")]

    model = _store["model"]
    names = _store["feature_names"]

    if hasattr(model, "feature_importances_"):
        importances = model.feature_importances_
    elif hasattr(model, "coef_"):
        importances = np.abs(model.coef_).flatten()
    else:
        return [TextContent(type="text", text="This model does not support feature importance.")]

    ranked = sorted(zip(names, importances), key=lambda x: x[1], reverse=True)
    result = [{"feature": name, "importance": round(float(imp), 4)} for name, imp in ranked]
    return [TextContent(type="text", text=json.dumps(result, indent=2))]


def predict(args):
    if _store["model"] is None:
        return [TextContent(type="text", text="No model trained.")]

    data = json.loads(args["data"])
    X_new = np.array(data).reshape(1, -1) if isinstance(data[0], (int, float)) else np.array(data)
    prediction = _store["model"].predict(X_new)
    return [TextContent(type="text", text=f"Prediction: {prediction.tolist()}")]


if __name__ == "__main__":
    import mcp.server.stdio
    asyncio.run(mcp.server.stdio.run(app))
