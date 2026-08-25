"""Tests for .env credential loading."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from engine_v17.epo_ops.config import _parse_env_line, load_env


class TestParseEnvLine:
    def test_basic_pair(self):
        assert _parse_env_line("KEY=value") == ("KEY", "value")

    def test_whitespace_and_quotes(self):
        assert _parse_env_line('  KEY = "quoted value" ') == ("KEY", "quoted value")
        assert _parse_env_line("KEY='single'") == ("KEY", "single")

    def test_comments_and_blanks(self):
        assert _parse_env_line("# comment") is None
        assert _parse_env_line("") is None
        assert _parse_env_line("   ") is None

    def test_malformed(self):
        assert _parse_env_line("NO_EQUALS_SIGN") is None
        assert _parse_env_line("=novalue") is None

    def test_hash_inside_value_kept(self):
        assert _parse_env_line("SECRET=a#b") == ("SECRET", "a#b")


class TestLoadEnv:
    def test_loads_pairs_from_file(self, tmp_path: Path, monkeypatch):
        env_file = tmp_path / ".env"
        env_file.write_text("EPO_TEST_A=1\n# c\nEPO_TEST_B='two words'\n", encoding="utf-8")
        monkeypatch.delenv("EPO_TEST_A", raising=False)
        monkeypatch.delenv("EPO_TEST_B", raising=False)
        loaded = load_env(env_file)
        assert loaded == env_file
        assert os.environ["EPO_TEST_A"] == "1"
        assert os.environ["EPO_TEST_B"] == "two words"

    def test_never_overrides_existing_env(self, tmp_path: Path, monkeypatch):
        env_file = tmp_path / ".env"
        env_file.write_text("EPO_TEST_C=file-value\n", encoding="utf-8")
        monkeypatch.setenv("EPO_TEST_C", "shell-value")
        load_env(env_file)
        assert os.environ["EPO_TEST_C"] == "shell-value"

    def test_missing_file_returns_none(self, tmp_path: Path):
        assert load_env(tmp_path / "absent.env") is None

    def test_malformed_lines_skipped(self, tmp_path: Path, monkeypatch):
        env_file = tmp_path / ".env"
        env_file.write_text(
            "GOOD=1\nBAD LINE NO EQUALS\n\n# note\n=novalue\n", encoding="utf-8"
        )
        monkeypatch.delenv("GOOD", raising=False)
        assert load_env(env_file) == env_file
        assert os.environ["GOOD"] == "1"
