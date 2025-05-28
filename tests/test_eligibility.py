import pytest
from src.core.eligibility_engine import EligibilityEngine

@pytest.fixture(autouse=True)
def clear_env(monkeypatch):
    # Clear any model path to force rule-based
    monkeypatch.delenv("ELIGIBILITY_MODEL_PATH", raising=False)
    yield

def test_rule_based_approve():
    engine = EligibilityEngine(model_path="nonexistent.pkl")
    decision = engine.check(processed_data={}, income=1000.0, family_size=4)
    assert decision == "Approve"

def test_rule_based_decline_income_high():
    engine = EligibilityEngine(model_path="nonexistent.pkl")
    decision = engine.check(processed_data={}, income=5000.0, family_size=5)
    assert decision == "Soft Decline"

def test_rule_based_decline_small_family():
    engine = EligibilityEngine(model_path="nonexistent.pkl")
    decision = engine.check(processed_data={}, income=1000.0, family_size=1)
    assert decision == "Soft Decline"
