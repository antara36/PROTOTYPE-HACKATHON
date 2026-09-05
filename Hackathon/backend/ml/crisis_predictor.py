import joblib
import numpy as np
import pandas as pd
from backend.config import MODELS_DIR, RISK_LIMITS
from backend.ml.feature_engineering import get_latest_market_features, get_market_data_period, prepare_inference_features
from backend.ml.train_crisis_model import train_and_save_model

class CrisisPredictor:
    """
    Inferences live market conditions to estimate crisis probability
    and triggers automated stress safeguards if thresholds are breached.
    """
    def __init__(self, model_path=None):
        self.model_path = model_path or (MODELS_DIR / "crisis_model.pkl")
        self._load_model()

    def _load_model(self):
        if self.model_path.exists():
            artifact = joblib.load(self.model_path)
            expected_features = set(get_latest_market_features())
            expected_start, expected_end = get_market_data_period()
            training_period = artifact.get("training_period", {})
            if (
                set(artifact.get("feature_names", [])) != expected_features
                or training_period.get("start") != expected_start
                or training_period.get("end") != expected_end
            ):
                self.model_path.unlink()

        if not self.model_path.exists():
            print("Model artifact not found. Triggering automated training...")
            train_and_save_model()
        
        artifact = joblib.load(self.model_path)
        self.model = artifact["model"]
        self.scaler = artifact["scaler"]
        self.feature_names = artifact["feature_names"]
        self.metrics = artifact.get("metrics", {})

    def predict(self, market_indicators: dict = None) -> dict:
        """
        Takes market indicators dictionary and outputs predicted crisis probability.
        Default inputs represent a normal/calm market baseline.
        """
        if market_indicators is None:
            market_indicators = get_latest_market_features()

        scaled_features = prepare_inference_features(
            market_indicators, self.scaler, self.feature_names
        )

        proba = float(self.model.predict_proba(scaled_features)[0, 1])
        prediction = int(proba >= 0.50)

        trigger_limit = RISK_LIMITS["crisis_probability_trigger"]
        is_triggered = proba >= trigger_limit

        if proba >= 0.70:
            status = "CRITICAL CRISIS REGIME"
            badge = "EXTREME DANGER 🔴"
            color = "#EF4444"
            recommendation = "Automated stress safeguard active: Immediate equity hedging or de-risking required."
        elif proba >= 0.45:
            status = "ELEVATED STRESS"
            badge = "ELEVATED RISK 🟡"
            color = "#F59E0B"
            recommendation = "Heightened market turbulence detected: Prepare defensive liquidity buffers."
        else:
            status = "CALM REGIME"
            badge = "STABLE 🟢"
            color = "#10B981"
            recommendation = "Normal operating environment: Standard allocation controls apply."

        return {
            "crisis_probability": round(proba, 4),
            "crisis_probability_pct": round(proba * 100, 1),
            "is_crisis_predicted": bool(prediction == 1),
            "is_safeguard_triggered": is_triggered,
            "trigger_threshold_pct": round(trigger_limit * 100, 1),
            "regime_status": status,
            "regime_badge": badge,
            "regime_color": color,
            "recommendation": recommendation,
            "input_indicators": market_indicators,
            "model_accuracy": self.metrics.get("accuracy"),
            "feature_importances": self.metrics.get("feature_importances", {})
        }
