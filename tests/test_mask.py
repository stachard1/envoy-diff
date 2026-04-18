import pytest
from envoy_diff.mask import mask_env, mask_value, mask_dict, unmask_count, MASK_VALUE


@pytest.fixture
def sample_env():
    return {
        "APP_HOST": "localhost",
        "DB_PASSWORD": "supersecret",
        "API_KEY": "abc123",
        "PORT": "8080",
        "AUTH_TOKEN": "tok_xyz",
    }


def test_mask_env_hides_sensitive(sample_env):
    result = mask_env(sample_env)
    assert result["DB_PASSWORD"] == MASK_VALUE
    assert result["API_KEY"] == MASK_VALUE
    assert result["AUTH_TOKEN"] == MASK_VALUE


def test_mask_env_preserves_non_sensitive(sample_env):
    result = mask_env(sample_env)
    assert result["APP_HOST"] == "localhost"
    assert result["PORT"] == "8080"


def test_mask_env_custom_placeholder(sample_env):
    result = mask_env(sample_env, placeholder="[REDACTED]")
    assert result["DB_PASSWORD"] == "[REDACTED]"


def test_mask_env_empty():
    assert mask_env({}) == {}


def test_mask_value_sensitive():
    assert mask_value("SECRET_KEY", "my_secret") == MASK_VALUE


def test_mask_value_non_sensitive():
    assert mask_value("APP_ENV", "production") == "production"


def test_mask_dict_specific_keys(sample_env):
    result = mask_dict(sample_env, keys=["APP_HOST", "PORT"])
    assert result["APP_HOST"] == MASK_VALUE
    assert result["PORT"] == MASK_VALUE
    assert result["DB_PASSWORD"] == "supersecret"


def test_mask_dict_no_keys_falls_back_to_sensitive(sample_env):
    result = mask_dict(sample_env)
    assert result["DB_PASSWORD"] == MASK_VALUE
    assert result["APP_HOST"] == "localhost"


def test_unmask_count(sample_env):
    masked = mask_env(sample_env)
    count = unmask_count(sample_env, masked)
    assert count == 3


def test_unmask_count_none_masked():
    env = {"HOST": "localhost", "PORT": "80"}
    masked = mask_env(env)
    assert unmask_count(env, masked) == 0


def test_mask_env_does_not_mutate_original(sample_env):
    """Ensure mask_env returns a new dict and does not modify the input."""
    original = dict(sample_env)
    mask_env(sample_env)
    assert sample_env == original
