import os
import pytest
from reputation_manager import ReputationManager

@pytest.fixture
def temp_reputation(tmp_path):
    db_file = os.path.join(tmp_path, "test_rep.db")
    return ReputationManager(db_path=db_file)

def test_record_interaction_and_trust(temp_reputation):
    temp_reputation.record_interaction("Alice Smith <alice@partner.com>", is_vip=True)
    assert temp_reputation.is_trusted("alice@partner.com") is True
    assert temp_reputation.is_trusted("unknown@stranger.com") is False

def test_score_increment(temp_reputation):
    temp_reputation.record_interaction("Bob <bob@client.com>", score_delta=6)
    assert temp_reputation.is_trusted("bob@client.com") is True

def test_clean_address(temp_reputation):
    email, domain = temp_reputation.clean_address('"John Doe" <john.doe@acme.org>')
    assert email == "john.doe@acme.org"
    assert domain == "acme.org"
