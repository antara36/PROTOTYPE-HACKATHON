import joblib
import logging
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

from backend.config import MODELS_DIR
from backend.config import MARKET_DATA_END_DATE, MARKET_DATA_START_DATE
from backend.ml.feature_engineering import get_market_data_period, load_and_prepare_crisis_data

logger = logging.getLogger(__name__)

def train_and_save_model():
    """
    Trains a Random Forest Classifier on simulated multi-market crisis indicators,
    evaluates performance, and serializes the model artifact to disk.
    """
    print("Loading and preparing multi-market crisis data...")
    data = load_and_prepare_crisis_data()
    
    X_train_scaled = data["X_train_scaled"]
    y_train = data["y_train"]
    X_test_scaled = data["X_test_scaled"]
    y_test = data["y_test"]
    scaler = data["scaler"]
    feature_names = data["feature_names"]

    print("Training Random Forest Crisis Classifier...")
    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=6,
        min_samples_split=5,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1
    )
    clf.fit(X_train_scaled, y_train)

    # Evaluate
    y_pred = clf.predict(X_test_scaled)
    y_proba = clf.predict_proba(X_test_scaled)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, zero_division=0)
    rec = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)
    roc_auc = roc_auc_score(y_test, y_proba)
    cm = confusion_matrix(y_test, y_pred).tolist()

    feature_importances = dict(zip(feature_names, [round(float(imp), 4) for imp in clf.feature_importances_]))

    metrics = {
        "accuracy": round(acc, 4),
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1_score": round(f1, 4),
        "roc_auc": round(roc_auc, 4),
        "confusion_matrix": cm,
        "feature_importances": feature_importances
    }

    # Save bundle safely
    artifact = {
        "model": clf,
        "scaler": scaler,
        "feature_names": feature_names,
        "metrics": metrics,
        "training_period": {
            "start": get_market_data_period()[0],
            "end": get_market_data_period()[1],
        },
    }
    
    # Ensure destination directory exists before dump
    Path(MODELS_DIR).mkdir(parents=True, exist_ok=True)
    model_path = Path(MODELS_DIR) / "crisis_model.pkl"
    joblib.dump(artifact, model_path)
    
    print(f"Crisis model successfully trained and saved to: {model_path}")
    print(f"Test Accuracy: {acc*100:.2f}%, ROC-AUC: {roc_auc:.4f}")
    return metrics

if __name__ == "__main__":
    train_and_save_model()



# import joblib
# from sklearn.ensemble import RandomForestClassifier
# from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
# from backend.config import MODELS_DIR
# from backend.ml.feature_engineering import load_and_prepare_crisis_data

# def train_and_save_model():
#     """
#     Trains a Random Forest Classifier on simulated multi-market crisis indicators,
#     evaluates performance, and serializes the model artifact to disk.
#     """
#     print("Loading and preparing multi-market crisis data...")
#     data = load_and_prepare_crisis_data()
    
#     X_train_scaled = data["X_train_scaled"]
#     y_train = data["y_train"]
#     X_test_scaled = data["X_test_scaled"]
#     y_test = data["y_test"]
#     scaler = data["scaler"]
#     feature_names = data["feature_names"]

#     print("Training Random Forest Crisis Classifier...")
#     clf = RandomForestClassifier(
#         n_estimators=100,
#         max_depth=6,
#         min_samples_split=5,
#         random_state=42,
#         n_jobs=-1
#     )
#     clf.fit(X_train_scaled, y_train)

#     # Evaluate
#     y_pred = clf.predict(X_test_scaled)
#     y_proba = clf.predict_proba(X_test_scaled)[:, 1]

#     acc = accuracy_score(y_test, y_pred)
#     prec = precision_score(y_test, y_pred, zero_division=0)
#     rec = recall_score(y_test, y_pred, zero_division=0)
#     f1 = f1_score(y_test, y_pred, zero_division=0)
#     roc_auc = roc_auc_score(y_test, y_proba)
#     cm = confusion_matrix(y_test, y_pred).tolist()

#     feature_importances = dict(zip(feature_names, [round(float(imp), 4) for imp in clf.feature_importances_]))

#     metrics = {
#         "accuracy": round(acc, 4),
#         "precision": round(prec, 4),
#         "recall": round(rec, 4),
#         "f1_score": round(f1, 4),
#         "roc_auc": round(roc_auc, 4),
#         "confusion_matrix": cm,
#         "feature_importances": feature_importances
#     }

#     # Save bundle
#     artifact = {
#         "model": clf,
#         "scaler": scaler,
#         "feature_names": feature_names,
#         "metrics": metrics
#     }
#     model_path = MODELS_DIR / "crisis_model.pkl"
#     joblib.dump(artifact, model_path)
#     print(f"Crisis model successfully trained and saved to: {model_path}")
#     print(f"Test Accuracy: {acc*100:.2f}%, ROC-AUC: {roc_auc:.4f}")
#     return metrics

# if __name__ == "__main__":
#     train_and_save_model()
