import pytest
from src.core.recommendation_engine import RecommendationEngine

def test_recommendation_enough_docs(monkeypatch):
    monkeypatch.setenv("RECOMMEND_DOC_THRESHOLD", "2")
    engine = RecommendationEngine()
    data = {"documents": [{"text": "a"}, {"text": "b"}]}
    rec = engine.generate(data)
    assert "upskilling programs" in rec

def test_recommendation_not_enough_docs(monkeypatch):
    monkeypatch.setenv("RECOMMEND_DOC_THRESHOLD", "3")
    engine = RecommendationEngine()
    data = {"documents": [{"text": "a"}]}
    rec = engine.generate(data)
    assert "Please provide additional supporting documents" in rec