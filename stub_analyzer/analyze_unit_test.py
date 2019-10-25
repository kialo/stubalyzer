from json.decoder import JSONDecodeError
from typing import Any
from unittest.mock import Mock, patch

import pytest
from schema import SchemaError

from .analyze import evaluate_compare_result, setup_expected_mismatches
from .compare import MatchResult


class TestSetupExpectedMismatches:
    def test_file_not_provided(self) -> None:
        assert setup_expected_mismatches(None) == ({}, set())

    def test_file_not_exists(self, capsys: Any) -> None:
        assert setup_expected_mismatches("a_file") == ({}, set())
        _, err = capsys.readouterr()
        assert err.startswith("WARNING: Provided")

    @patch("pathlib.Path.read_text", return_value='{\'1: "4"}')
    @patch("pathlib.Path.exists", return_value=True)
    def test_wrong_json(self, exists_mock: Mock, read_mock: Mock) -> None:
        with pytest.raises(JSONDecodeError, match=r".*double quotes.*"):
            assert setup_expected_mismatches("a_file")

    @patch("pathlib.Path.read_text", return_value='{"lib.1": "match"}')
    @patch("pathlib.Path.exists", return_value=True)
    def test_json_contains_matches(self, *mocks: Mock) -> None:
        with pytest.raises(
            SchemaError, match=r".*'match' is not a valid mismatch type.*"
        ):
            assert setup_expected_mismatches("a_file")

    @patch("pathlib.Path.read_text", return_value='{"lib.1": "unknown_match"}')
    @patch("pathlib.Path.exists", return_value=True)
    def test_json_contains_invalid_types(self, *mocks: Mock) -> None:
        with pytest.raises(
            SchemaError, match=r".*'unknown_match' is not a valid mismatch type.*"
        ):
            assert setup_expected_mismatches("a_file")

    @patch("pathlib.Path.read_text", return_value="[1,2,3]")
    @patch("pathlib.Path.exists", return_value=True)
    def test_json_invalid_format(self, *mocks: Mock) -> None:
        with pytest.raises(SchemaError, match=r".*should be instance of 'dict'.*"):
            assert setup_expected_mismatches("a_file")

    @patch(
        "pathlib.Path.read_text",
        return_value='{"lib.1": "not_found", "lib.2": "mismatch"}',
    )
    @patch("pathlib.Path.exists", return_value=True)
    def test_json_is_correct(self, *mocks: Mock) -> None:
        assert setup_expected_mismatches("a_file") == (
            {"lib.1": MatchResult.NOT_FOUND, "lib.2": MatchResult.MISMATCH},
            set(["lib.1", "lib.2"]),
        )


class TestEvaluateCompareResult:
    def test_everything_ok(self) -> None:
        mismatches_left = set(["1", "2", "4"])
        mismatches = {"1": MatchResult.NOT_FOUND}
        compare_result = Mock()
        compare_result.configure_mock(
            match_result=MatchResult.MATCH, message="Alright", symbol_name="3"
        )
        assert evaluate_compare_result(compare_result, mismatches, mismatches_left)
        assert mismatches_left == set(["1", "2", "4"])

    def test_accept_expected_mismatches(self) -> None:
        mismatches_left = set(["1", "2", "3", "4"])
        mismatches = {"1": MatchResult.NOT_FOUND, "3": MatchResult.MISMATCH}

        compare_result = Mock()
        compare_result.configure_mock(
            match_result=MatchResult.MISMATCH, symbol_name="3"
        )
        assert evaluate_compare_result(compare_result, mismatches, mismatches_left)
        assert mismatches_left == set(["1", "2", "4"])

    def test_unwanted_mismatch(self, capsys: Any) -> None:
        mismatches_left = set(["1"])
        compare_result = Mock()
        compare_result.configure_mock(
            match_result=MatchResult.MISMATCH,
            message="An error happened",
            symbol_name="3",
        )
        assert not evaluate_compare_result(compare_result, {}, mismatches_left)
        _, err = capsys.readouterr()
        assert err == "\nAn error happened"
        assert mismatches_left == set(["1"])

    def test_unwanted_match_intead_mismatch(self, capsys: Any) -> None:
        mismatches_left = set(["1", "2", "3", "4"])
        mismatches = {"1": MatchResult.NOT_FOUND, "3": MatchResult.MISMATCH}

        compare_result = Mock()
        compare_result.configure_mock(match_result=MatchResult.MATCH, symbol_name="3")

        assert not evaluate_compare_result(compare_result, mismatches, mismatches_left)

        _, err = capsys.readouterr()
        assert err == '\nExpected "3" to be "mismatch" but it matched.'
        assert mismatches_left == set(["1", "2", "4"])

    def test_unwanted_match_intead_not_found(self, capsys: Any) -> None:
        mismatches_left = set(["1", "2", "3", "4"])
        mismatches = {"1": MatchResult.NOT_FOUND, "3": MatchResult.NOT_FOUND}

        compare_result = Mock()
        compare_result.configure_mock(match_result=MatchResult.MATCH, symbol_name="3")

        assert not evaluate_compare_result(compare_result, mismatches, mismatches_left)

        _, err = capsys.readouterr()
        assert err == '\nExpected "3" to be "not_found" but it matched.'
        assert mismatches_left == set(["1", "2", "4"])

    def test_wrong_mismatch_type(self, capsys: Any) -> None:
        mismatches_left = set(["1", "2", "3", "4"])
        mismatches = {"1": MatchResult.NOT_FOUND, "3": MatchResult.MISMATCH}

        compare_result = Mock()
        compare_result.configure_mock(
            match_result=MatchResult.NOT_FOUND, symbol_name="3"
        )

        assert not evaluate_compare_result(compare_result, mismatches, mismatches_left)

        _, err = capsys.readouterr()
        assert err == '\nExpected "3" to be "mismatch" but it was "not_found".'
        assert mismatches_left == set(["1", "2", "4"])
