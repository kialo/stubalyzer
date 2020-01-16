from json.decoder import JSONDecodeError
from unittest.mock import Mock, patch

import pytest
from _pytest.capture import CaptureFixture
from mypy.nodes import TypeAlias, TypeVarExpr, Var
from schema import SchemaError

from .analyze import (
    EvaluationResult,
    analyze_stubs,
    compare,
    evaluate_compare_result,
    setup_expected_mismatches,
    write_error,
)
from .compare import ComparisonResult, MatchResult


class TestCompare:
    def test_skip_private_symbols(self) -> None:
        handwritten = [
            Mock(fullname="_private0", spec=TypeAlias),
            Mock(fullname="_private1", spec=TypeVarExpr),
            Mock(fullname="_private2", spec=Var),
            Mock(fullname="public0"),
            Mock(fullname="__public1"),
        ]
        assert len(list(compare(handwritten, []))) == 2

    @patch(
        "stubalyzer.analyze.compare_symbols",
        return_value=ComparisonResult.create_match(Mock(), Mock()),
    )
    def test_match_to_generated_symbols(self, compare_mock: Mock) -> None:
        handwritten = [
            Mock(fullname="found_in_generated"),
            Mock(fullname="not_found_in_generated"),
        ]
        generated = [Mock(fullname="found_in_generated")]
        result = list(compare(handwritten, generated))
        assert len(result) == 2
        assert result[0].match_result == MatchResult.MATCH
        assert result[1].match_result == MatchResult.NOT_FOUND


class TestSetupExpectedMismatches:
    def test_file_not_provided(self) -> None:
        assert setup_expected_mismatches(None) == ({}, set())

    def test_file_not_exists(self, capsys: CaptureFixture) -> None:
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
            SchemaError, match=r'.*"match" is not a valid mismatch type.*'
        ):
            assert setup_expected_mismatches("a_file")

    @patch("pathlib.Path.read_text", return_value='{"lib.1": "unknown_match"}')
    @patch("pathlib.Path.exists", return_value=True)
    def test_json_contains_invalid_types(self, *mocks: Mock) -> None:
        with pytest.raises(
            SchemaError, match=r'.*"unknown_match" is not a valid mismatch type.*'
        ):
            assert setup_expected_mismatches("a_file")

    @patch("pathlib.Path.read_text", return_value="[1,2,3]")
    @patch("pathlib.Path.exists", return_value=True)
    def test_json_invalid_format(self, *mocks: Mock) -> None:
        with pytest.raises(SchemaError, match=r".*should be instance of 'dict'.*"):
            assert setup_expected_mismatches("a_file")

    @patch("pathlib.Path.read_text", return_value="{}")
    @patch("pathlib.Path.exists", return_value=True)
    def test_json_empty_dict(self, *mocks: Mock) -> None:
        assert setup_expected_mismatches("a_file") == ({}, set())

    @patch(
        "pathlib.Path.read_text",
        return_value='{"lib.1": "not_found", "lib.2": "mismatch"}',
    )
    @patch("pathlib.Path.exists", return_value=True)
    def test_json_is_correct(self, *mocks: Mock) -> None:
        assert setup_expected_mismatches("a_file") == (
            {"lib.1": MatchResult.NOT_FOUND, "lib.2": MatchResult.MISMATCH},
            {"lib.1", "lib.2"},
        )


class TestEvaluateCompareResult:
    def test_everything_ok(self, capsys: CaptureFixture) -> None:
        mismatches_left = {"1", "2", "4"}
        mismatches = {"1": MatchResult.NOT_FOUND}
        compare_result = Mock()
        compare_result.configure_mock(
            match_result=MatchResult.MATCH, message="Alright", symbol_name="3"
        )
        assert (
            evaluate_compare_result(
                compare_result, mismatches, mismatches_left, loggers=[write_error]
            )
            is EvaluationResult.SUCCESS
        )
        _, err = capsys.readouterr()
        assert err == ""
        assert mismatches_left == {"1", "2", "4"}

    def test_accept_expected_mismatches(self, capsys: CaptureFixture) -> None:
        mismatches_left = {"1", "2", "3", "4"}
        mismatches = {"1": MatchResult.NOT_FOUND, "3": MatchResult.MISMATCH}

        compare_result = Mock()
        compare_result.configure_mock(
            match_result=MatchResult.MISMATCH, symbol_name="3"
        )
        assert (
            evaluate_compare_result(
                compare_result, mismatches, mismatches_left, loggers=[write_error]
            )
            is EvaluationResult.EXPECTED_FAILURE
        )
        _, err = capsys.readouterr()
        assert err == ""
        assert mismatches_left == {"1", "2", "4"}

    def test_unwanted_mismatch(self, capsys: CaptureFixture) -> None:
        mismatches_left = {"1"}
        compare_result = Mock()
        compare_result.configure_mock(
            match_result=MatchResult.MISMATCH,
            message="An error happened",
            symbol_name="3",
        )
        assert (
            evaluate_compare_result(
                compare_result, {}, mismatches_left, loggers=[write_error]
            )
            is EvaluationResult.FAILURE
        )
        _, err = capsys.readouterr()
        assert "An error happened" in err
        assert mismatches_left == {"1"}

    def test_unwanted_match_instead_mismatch(self, capsys: CaptureFixture) -> None:
        mismatches_left = {"1", "2", "3", "4"}
        mismatches = {"1": MatchResult.NOT_FOUND, "3": MatchResult.MISMATCH}

        compare_result = Mock()
        compare_result.configure_mock(match_result=MatchResult.MATCH, symbol_name="3")

        expected_mismatches_path = "the/mismatch/path.json"
        assert (
            evaluate_compare_result(
                compare_result,
                mismatches,
                mismatches_left,
                expected_mismatches_path,
                loggers=[write_error],
            )
            is EvaluationResult.FAILURE
        )

        _, err = capsys.readouterr()
        assert 'Expected "3" to be "mismatch" but it matched.' in err
        assert mismatches_left == {"1", "2", "4"}

    def test_unwanted_match_instead_not_found(self, capsys: CaptureFixture) -> None:
        mismatches_left = {"1", "2", "3", "4"}
        mismatches = {"1": MatchResult.NOT_FOUND, "3": MatchResult.NOT_FOUND}

        compare_result = Mock()
        compare_result.configure_mock(match_result=MatchResult.MATCH, symbol_name="3")
        expected_mismatches_path = "the/mismatch/path.json"

        assert (
            evaluate_compare_result(
                compare_result,
                mismatches,
                mismatches_left,
                expected_mismatches_path,
                loggers=[write_error],
            )
            is EvaluationResult.FAILURE
        )

        _, err = capsys.readouterr()
        assert 'Expected "3" to be "not_found" but it matched.' in err
        assert mismatches_left == {"1", "2", "4"}

    def test_wrong_mismatch_type(self, capsys: CaptureFixture) -> None:
        mismatches_left = {"1", "2", "3", "4"}
        mismatches = {"1": MatchResult.NOT_FOUND, "3": MatchResult.MISMATCH}

        compare_result = Mock()
        compare_result.configure_mock(
            match_result=MatchResult.NOT_FOUND, symbol_name="3"
        )
        expected_mismatches_path = "the/mismatch/path.json"

        assert (
            evaluate_compare_result(
                compare_result,
                mismatches,
                mismatches_left,
                expected_mismatches_path,
                loggers=[write_error],
            )
            is EvaluationResult.FAILURE
        )

        _, err = capsys.readouterr()
        assert 'Expected "3" to be "mismatch" but it was "not_found".' in err
        assert mismatches_left == {"1", "2", "4"}


class TestAnalyzeStubs:
    @patch(
        "stubalyzer.analyze.evaluate_compare_result",
        return_value=EvaluationResult.SUCCESS,
    )
    @patch("stubalyzer.analyze.compare", return_value=range(10))
    @patch("stubalyzer.analyze.generate_stub_types")
    @patch("stubalyzer.analyze.get_stub_types", return_value=[])
    @pytest.mark.parametrize("silent", [False, True])  # type: ignore
    def test_everything_ok(
        self,
        generate_mock: Mock,
        compare_mock: Mock,
        result_mock: Mock,
        get_stub_types_mock: Mock,
        silent: bool,
        capsys: CaptureFixture,
    ) -> None:
        assert analyze_stubs("mypy_conf_path", "base_stubs_path", silent=silent)
        std, err = capsys.readouterr()
        if silent:
            assert "" == std
        else:
            assert "Successfully validated 10 stubs." in std
            assert (
                "0 fail(s) were ignored, "
                "because they were defined to be expected mismatches." not in std
            )
        assert "" == err

    @patch(
        "stubalyzer.analyze.setup_expected_mismatches",
        side_effect=JSONDecodeError("Boom", '{"a": 2}', 4),
    )
    def test_json_error(self, setup_mock: Mock, capsys: CaptureFixture) -> None:
        assert not analyze_stubs("mypy_conf_path", "base_stubs_path")
        _, err = capsys.readouterr()
        assert "Boom: line 1 column 5 (char 4)" in err

    @patch(
        "stubalyzer.analyze.setup_expected_mismatches", side_effect=SchemaError("Boom")
    )
    def test_schema_error(self, setup_mock: Mock, capsys: CaptureFixture) -> None:
        assert not analyze_stubs("mypy_conf_path", "base_stubs_path")
        _, err = capsys.readouterr()
        assert "Boom" in err

    @patch("stubalyzer.analyze.setup_expected_mismatches", return_value=({}, set()))
    @patch(
        "stubalyzer.analyze.evaluate_compare_result",
        side_effect=[EvaluationResult.FAILURE] * 2
        + [EvaluationResult.SUCCESS] * 4
        + [EvaluationResult.EXPECTED_FAILURE] * 4,
    )
    @patch("stubalyzer.analyze.compare", return_value=range(10))
    @patch("stubalyzer.analyze.generate_stub_types")
    @patch("stubalyzer.analyze.get_stub_types", return_value=[])
    @pytest.mark.parametrize("silent", [False, True])  # type: ignore
    def test_some_results_fail_ok(
        self,
        generate_mock: Mock,
        compare_mock: Mock,
        result_mock: Mock,
        setup_mock: Mock,
        get_stub_types_mock: Mock,
        silent: bool,
        capsys: CaptureFixture,
    ) -> None:
        assert not analyze_stubs(
            "mypy_conf_path",
            "base_stubs_path",
            expected_mismatches_path="a/proper/mismatch_path",
            silent=silent,  # Does not affect error output
        )
        std, err = capsys.readouterr()
        assert "Failure: 2 of 10 stubs seem not to be valid." in err
        assert (
            "4 fail(s) were ignored, "
            "because they were defined to be expected mismatches." in err
        )
        assert "" == std

    @patch("stubalyzer.analyze.setup_expected_mismatches", return_value=({}, set()))
    @patch(
        "stubalyzer.analyze.evaluate_compare_result",
        side_effect=[EvaluationResult.FAILURE] * 2
        + [EvaluationResult.SUCCESS] * 4
        + [EvaluationResult.EXPECTED_FAILURE] * 4,
    )
    @patch("stubalyzer.analyze.compare", return_value=range(10))
    @patch("stubalyzer.analyze.generate_stub_types")
    @patch("stubalyzer.analyze.get_stub_types", return_value=[])
    def test_does_not_suppress_error_on_silent(
        self,
        generate_mock: Mock,
        compare_mock: Mock,
        result_mock: Mock,
        setup_mock: Mock,
        get_stub_types_mock: Mock,
        capsys: CaptureFixture,
    ) -> None:
        assert not analyze_stubs(
            "mypy_conf_path",
            "base_stubs_path",
            expected_mismatches_path="a/proper/mismatch_path",
            silent=True,
        )
        std, err = capsys.readouterr()
        assert "Failure: 2 of 10 stubs seem not to be valid." in err
        assert (
            "4 fail(s) were ignored, "
            "because they were defined to be expected mismatches." in err
        )
        assert "" == std

    @patch(
        "stubalyzer.analyze.setup_expected_mismatches",
        return_value=({}, ["lib.1", "lib.2"]),
    )
    @patch("stubalyzer.analyze.compare", return_value=[])
    @patch("stubalyzer.analyze.generate_stub_types")
    @patch("stubalyzer.analyze.get_stub_types", return_value=[])
    def test_unused_mismatches(
        self,
        generate_mock: Mock,
        compare_mock: Mock,
        setup_mock: Mock,
        get_stub_types_mock: Mock,
        capsys: CaptureFixture,
    ) -> None:
        assert not analyze_stubs(
            "mypy_conf_path",
            "base_stubs_path",
            expected_mismatches_path="a/proper/mismatch_path",
        )

        _, err = capsys.readouterr()
        assert (
            "Expected the following symbols to fail, but they were not processed:\n"
            " - lib.1\n"
            " - lib.2\n"
            'Check "a/proper/mismatch_path" to fix.' in err
        )
