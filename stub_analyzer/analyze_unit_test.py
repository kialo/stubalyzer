from json.decoder import JSONDecodeError
from typing import Any
from unittest.mock import Mock, patch

import pytest
from mypy.nodes import TypeAlias, TypeVarExpr, Var

from schema import SchemaError

from .analyze import (
    analyze_stubs,
    compare,
    evaluate_compare_result,
    setup_expected_mismatches,
)
from .compare import ComparisonResult, MatchResult


class TestCompare:
    def test_skip_private_symbols(self) -> None:
        handwritten = [
            Mock(fullname=Mock(return_value="_private0"), spec=TypeAlias),
            Mock(fullname=Mock(return_value="_private1"), spec=TypeVarExpr),
            Mock(fullname=Mock(return_value="_private2"), spec=Var),
            Mock(fullname=Mock(return_value="public0")),
            Mock(fullname=Mock(return_value="__public1")),
        ]
        assert len(list(compare(handwritten, []))) == 2

    @patch(
        "stub_analyzer.analyze.compare_symbols",
        return_value=ComparisonResult.create_match(Mock(), Mock()),
    )
    def test_match_to_generated_symbols(self, compare_mock: Mock) -> None:
        handwritten = [
            Mock(fullname=Mock(return_value="found_in_generated")),
            Mock(fullname=Mock(return_value="not_found_in_generated")),
        ]
        generated = [Mock(fullname=Mock(return_value="found_in_generated"))]
        result = list(compare(handwritten, generated))
        assert len(result) == 2
        assert result[0].match_result == MatchResult.MATCH
        assert result[1].match_result == MatchResult.NOT_FOUND


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
    @staticmethod
    def assert_err(expected: str, capsys: Any) -> None:
        _, err = capsys.readouterr()
        assert err.strip() == expected

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
        self.assert_err("An error happened", capsys)
        assert mismatches_left == set(["1"])

    def test_unwanted_match_intead_mismatch(self, capsys: Any) -> None:
        mismatches_left = set(["1", "2", "3", "4"])
        mismatches = {"1": MatchResult.NOT_FOUND, "3": MatchResult.MISMATCH}

        compare_result = Mock()
        compare_result.configure_mock(match_result=MatchResult.MATCH, symbol_name="3")

        assert not evaluate_compare_result(compare_result, mismatches, mismatches_left)

        self.assert_err('Expected "3" to be "mismatch" but it matched.', capsys)
        assert mismatches_left == set(["1", "2", "4"])

    def test_unwanted_match_intead_not_found(self, capsys: Any) -> None:
        mismatches_left = set(["1", "2", "3", "4"])
        mismatches = {"1": MatchResult.NOT_FOUND, "3": MatchResult.NOT_FOUND}

        compare_result = Mock()
        compare_result.configure_mock(match_result=MatchResult.MATCH, symbol_name="3")

        assert not evaluate_compare_result(compare_result, mismatches, mismatches_left)

        self.assert_err('Expected "3" to be "not_found" but it matched.', capsys)
        assert mismatches_left == set(["1", "2", "4"])

    def test_wrong_mismatch_type(self, capsys: Any) -> None:
        mismatches_left = set(["1", "2", "3", "4"])
        mismatches = {"1": MatchResult.NOT_FOUND, "3": MatchResult.MISMATCH}

        compare_result = Mock()
        compare_result.configure_mock(
            match_result=MatchResult.NOT_FOUND, symbol_name="3"
        )

        assert not evaluate_compare_result(compare_result, mismatches, mismatches_left)

        self.assert_err('Expected "3" to be "mismatch" but it was "not_found".', capsys)
        assert mismatches_left == set(["1", "2", "4"])


class TestAnalyzeStubs:
    @staticmethod
    def assert_stdout(expected: str, capsys: Any) -> None:
        out, _ = capsys.readouterr()
        assert out.strip() == expected

    @staticmethod
    def assert_out(expected_std: str, expected_err: str, capsys: Any) -> None:
        std, err = capsys.readouterr()
        assert std.strip() == expected_std
        assert err.strip() == expected_err

    @staticmethod
    def assert_err_contains_line(line: str, capsys: Any) -> None:
        _, err = capsys.readouterr()
        assert line in [err_line.strip() for err_line in err.strip().split("\n")]

    @patch("stub_analyzer.analyze.evaluate_compare_result", return_value=True)
    @patch("stub_analyzer.analyze.compare", return_value=range(10))
    @patch("stub_analyzer.analyze.generate_stub_types")
    def test_everything_ok(
        self, generate_mock: Mock, compare_mock: Mock, result_mock: Mock, capsys: Any
    ) -> None:
        assert analyze_stubs("mypy_conf_path", "base_stubs_path")
        self.assert_out("Comparing failed on 0 of 10 stubs.", "", capsys)

    @patch(
        "stub_analyzer.analyze.setup_expected_mismatches",
        side_effect=JSONDecodeError("Boom", '{"a": 2}', 4),
    )
    def test_json_error(self, setup_mock: Mock, capsys: Any) -> None:
        assert not analyze_stubs("mypy_conf_path", "base_stubs_path")
        self.assert_err_contains_line("Boom: line 1 column 5 (char 4)", capsys)

    @patch(
        "stub_analyzer.analyze.setup_expected_mismatches",
        side_effect=SchemaError("Boom"),
    )
    def test_schema_error(self, setup_mock: Mock, capsys: Any) -> None:
        assert not analyze_stubs("mypy_conf_path", "base_stubs_path")
        self.assert_err_contains_line("Boom", capsys)

    @patch("stub_analyzer.analyze.setup_expected_mismatches", return_value=({}, set()))
    @patch(
        "stub_analyzer.analyze.evaluate_compare_result",
        side_effect=[False] * 3 + [True] * 7,
    )
    @patch("stub_analyzer.analyze.compare", return_value=range(10))
    @patch("stub_analyzer.analyze.generate_stub_types")
    def test_some_results_fail_ok(
        self,
        generate_mock: Mock,
        compare_mock: Mock,
        result_mock: Mock,
        setup_mock: Mock,
        capsys: Any,
    ) -> None:
        assert not analyze_stubs(
            "mypy_conf_path",
            "base_stubs_path",
            expected_mismatches_path="a/proper/mismatch_path",
        )
        self.assert_out(
            "Comparing failed on 3 of 10 stubs.",
            "\n".join(['Check "a/proper/mismatch_path" to fix.'] * 3),
            capsys,
        )

    @patch(
        "stub_analyzer.analyze.setup_expected_mismatches",
        return_value=({}, ["lib.1", "lib.2"]),
    )
    @patch("stub_analyzer.analyze.compare", return_value=[])
    @patch("stub_analyzer.analyze.generate_stub_types")
    def test_unused_mismatches(
        self, generate_mock: Mock, compare_mock: Mock, setup_mock: Mock, capsys: Any
    ) -> None:
        assert not analyze_stubs(
            "mypy_conf_path",
            "base_stubs_path",
            expected_mismatches_path="a/proper/mismatch_path",
        )
        self.assert_err_contains_line(
            'Expected "lib.1, lib.2" to fail, but it was not even processed.', capsys
        )
