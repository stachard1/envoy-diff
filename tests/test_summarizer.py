import pytest
from envoy_diff.summarizer import summarize, summary_as_dict


BEFORE = {
    "APP_HOST": "localhost",
    "DB_PASSWORD": "secret",
    "FEATURE_FLAG": "off",
}

AFTER = {
    "APP_HOST": "prod.example.com",
    "DB_PASSWORD": "newsecret",
    "NEW_KEY": "value",
}


@pytest.fixture
def summary():
    return summarize(BEFORE, AFTER)


def test_summarize_returns_env_summary(summary):
    from envoy_diff.summarizer import EnvSummary
    assert isinstance(summary, EnvSummary)


def test_diff_detects_added(summary):
    assert "NEW_KEY" in summary.diff.added


def test_diff_detects_removed(summary):
    assert "FEATURE_FLAG" in summary.diff.removed


def test_diff_detects_changed(summary):
    assert "APP_HOST" in summary.diff.changed
    assert "DB_PASSWORD" in summary.diff.changed


def test_audit_flags_sensitive_change(summary):
    keys = [f.key for f in summary.audit.findings]
    assert "DB_PASSWORD" in keys


def test_score_is_nonzero(summary):
    assert summary.score.total > 0


def test_score_level_is_string(summary):
    assert isinstance(summary.score.level, str)


def test_tags_before_present(summary):
    assert summary.tags_before is not None


def test_tags_after_present(summary):
    assert summary.tags_after is not None


def test_summary_as_dict_keys(summary):
    d = summary_as_dict(summary)
    assert set(d.keys()) == {"diff", "audit", "score", "tags"}


def test_summary_as_dict_diff_added(summary):
    d = summary_as_dict(summary)
    assert "NEW_KEY" in d["diff"]["added"]


def test_summary_as_dict_score(summary):
    d = summary_as_dict(summary)
    assert "total" in d["score"]
    assert "level" in d["score"]


def test_summary_as_dict_audit_findings(summary):
    d = summary_as_dict(summary)
    assert isinstance(d["audit"]["findings"], list)


def test_summary_as_dict_tags_structure(summary):
    d = summary_as_dict(summary)
    assert "before" in d["tags"]
    assert "after" in d["tags"]
