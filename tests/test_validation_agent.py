import pytest
from src.agents.validation_agent import ValidationAgent
from fastapi import HTTPException

@pytest.fixture
def agent():
    return ValidationAgent()

def test_validate_success():
    data = {"documents": [{"text": "hello"}]}
    assert agent().validate(data) == data

def test_validate_missing_documents():
    agent = ValidationAgent()
    with pytest.raises(HTTPException) as exc:
        agent.validate({})
    assert exc.value.status_code == 400

def test_validate_not_list():
    agent = ValidationAgent()
    with pytest.raises(HTTPException) as exc:
        agent.validate({"documents": "not_a_list"})
    assert exc.value.status_code == 400

def test_validate_missing_text():
    agent = ValidationAgent()
    with pytest.raises(HTTPException) as exc:
        agent.validate({"documents": [{}]})
    assert exc.value.status_code == 400
