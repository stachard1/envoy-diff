"""Tests for envoy_diff.parser."""

import textwrap
from pathlib import Path

import pytest

from envoy_diff.parser import parse_env_file, parse_env_string


def test_simple_key_value():
    result = parse_env_string("FOO=bar")
    assert result == {"FOO": "bar"}


def test_export_prefix():
    result = parse_env_string("export DATABASE_URL=postgres://localhost/db")
    assert result["DATABASE_URL"] == "postgres://localhost/db"


def test_quoted_values():
    text = textwrap.dedent("""
        APP_NAME="My Cool App"
        SECRET='top secret'
    """)
    result = parse_env_string(text)
    assert result["APP_NAME"] == "My Cool App"
    assert result["SECRET"] == "top secret"


def test_inline_comments_ignored():
    result = parse_env_string("PORT=8080 # default port")
    assert result["PORT"] == "8080"


def test_blank_and_comment_lines_skipped():
    text = textwrap.dedent("""
        # This is a comment

        KEY=value
    """)
    result = parse_env_string(text)
    assert result == {"KEY": "value"}


def test_multiple_variables():
    text = "A=1\nB=2\nC=3"
    result = parse_env_string(text)
    assert result == {"A": "1", "B": "2", "C": "3"}


def test_empty_string_returns_empty_dict():
    assert parse_env_string("") == {}


def test_parse_env_file(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text("HOST=localhost\nPORT=5432\n", encoding="utf-8")
    result = parse_env_file(env_file)
    assert result == {"HOST": "localhost", "PORT": "5432"}


def test_parse_env_file_missing_raises(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        parse_env_file(tmp_path / "nonexistent.env")
