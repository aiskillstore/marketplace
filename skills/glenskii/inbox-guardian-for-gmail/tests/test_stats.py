import os
import pytest
from stats_tracker import StatsTracker

@pytest.fixture
def temp_stats(tmp_path):
    stats_file = os.path.join(tmp_path, "test_stats.json")
    return StatsTracker(stats_file=stats_file)

def test_record_neutralization(temp_stats):
    temp_stats.record_neutralization("spammer@bad.biz", "Account locked", "SPOOF", "bad.biz")
    summary = temp_stats.get_24h_summary()
    assert "1 reviewed actions recorded" in summary
    assert "1 relay domains added" in summary
