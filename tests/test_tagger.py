import pytest
from envoy_diff.tagger import tag_key, tag_env, tags_summary, TaggedEnv


def test_tag_key_sensitive():
    assert "sensitive" in tag_key("DB_PASSWORD")


def test_tag_key_database():
    assert "database" in tag_key("POSTGRES_HOST")


def test_tag_key_network():
    assert "network" in tag_key("API_ENDPOINT")


def test_tag_key_feature_flag():
    assert "feature_flag" in tag_key("ENABLE_DARK_MODE")


def test_tag_key_logging():
    assert "logging" in tag_key("LOG_LEVEL")


def test_tag_key_no_match():
    assert tag_key("APP_NAME") == set()


def test_tag_key_multiple_tags():
    tags = tag_key("DATABASE_URL")
    assert "database" in tags
    assert "network" in tags


def test_tag_key_extra_tags():
    tags = tag_key("REGION", extra_tags={"cloud": ["REGION", "ZONE"]})
    assert "cloud" in tags


def test_tag_env_returns_tagged_env():
    env = {"SECRET_KEY": "abc", "APP_NAME": "myapp", "LOG_LEVEL": "info"}
    tagged = tag_env(env)
    assert isinstance(tagged, TaggedEnv)
    assert "sensitive" in tagged.get_tags("SECRET_KEY")
    assert tagged.get_tags("APP_NAME") == set()
    assert "logging" in tagged.get_tags("LOG_LEVEL")


def test_keys_with_tag():
    env = {"DB_HOST": "localhost", "DB_PASSWORD": "s3cr3t", "PORT": "8080"}
    tagged = tag_env(env)
    db_keys = tagged.keys_with_tag("database")
    assert "DB_HOST" in db_keys
    assert "DB_PASSWORD" in db_keys


def test_tags_summary_structure():
    env = {"API_TOKEN": "t", "ENABLE_FEATURE": "true", "APP": "x"}
    tagged = tag_env(env)
    summary = tags_summary(tagged)
    assert "sensitive" in summary
    assert "API_TOKEN" in summary["sensitive"]
    assert "feature_flag" in summary
    assert "ENABLE_FEATURE" in summary["feature_flag"]


def test_tags_summary_empty_env():
    tagged = tag_env({})
    assert tags_summary(tagged) == {}
