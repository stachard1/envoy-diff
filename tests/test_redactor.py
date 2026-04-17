import pytest
from envoy_diff.redactor import redact_env, redact_diff, REDACTED
from envoy_diff.differ import diff_envs


def test_redact_env_sensitive_key():
    env = {"DB_PASSWORD": "secret123", "APP_PORT": "8080"}
    result = redact_env(env)
    assert result["DB_PASSWORD"] == REDACTED
    assert result["APP_PORT"] == "8080"


def test_redact_env_token_key():
    env = {"AUTH_TOKEN": "tok_abc", "HOST": "localhost"}
    result = redact_env(env)
    assert result["AUTH_TOKEN"] == REDACTED
    assert result["HOST"] == "localhost"


def test_redact_env_preserves_non_sensitive():
    env = {"LOG_LEVEL": "debug", "WORKERS": "4"}
    result = redact_env(env)
    assert result == env


def test_redact_env_empty():
    assert redact_env({}) == {}


def test_redact_diff_added_sensitive():
    old = {}
    new = {"API_SECRET": "xyz", "PORT": "3000"}
    d = diff_envs(old, new)
    r = redact_diff(d)
    assert r.added["API_SECRET"] == REDACTED
    assert r.added["PORT"] == "3000"


def test_redact_diff_removed_sensitive():
    old = {"DB_PASSWORD": "pass", "ENV": "prod"}
    new = {}
    d = diff_envs(old, new)
    r = redact_diff(d)
    assert r.removed["DB_PASSWORD"] == REDACTED
    assert r.removed["ENV"] == "prod"


def test_redact_diff_changed_sensitive():
    old = {"SECRET_KEY": "old"}
    new = {"SECRET_KEY": "new"}
    d = diff_envs(old, new)
    r = redact_diff(d)
    assert r.changed["SECRET_KEY"] == (REDACTED, REDACTED)


def test_redact_diff_changed_non_sensitive():
    old = {"WORKERS": "2"}
    new = {"WORKERS": "4"}
    d = diff_envs(old, new)
    r = redact_diff(d)
    assert r.changed["WORKERS"] == ("2", "4")


def test_redact_diff_type_error():
    with pytest.raises(TypeError):
        redact_diff({"not": "a diff result"})
