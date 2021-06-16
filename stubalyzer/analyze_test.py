import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

import pytest
from _pytest.capture import CaptureFixture
from mypy.errors import CompileError

from testing.util import MypyNodeFactory, WithStubTestConfig

from .analyze import analyze_stubs, compare, main
from .compare import ComparisonResult, MatchResult


class TestAnalyzeStubs(WithStubTestConfig):
    @pytest.mark.parametrize("silent", [False, True])  # type: ignore
    def test_analyze_missing(self, silent: bool, capsys: CaptureFixture) -> None:
        analyze_stubs(
            self.mypy_config_path,
            self.handwritten_stubs_path,
            self.generated_stubs_path,
            self.get_expectations_path("missing.json"),
            silent=silent,  # Does not afffect error output
        )

        _, err = capsys.readouterr()

        assert "missing.MISSING_CONSTANT" not in err
        assert (
            'Expected "missing.missing_function" to be '
            '"mismatch" but it was "not_found"' in err
        )
        assert (
            "Expected the following symbols to fail, but they were not processed:\n"
            " - missing.missing_decorator" in err
        )
        assert 'Symbol "missing.MissingClass" not found in generated stubs' in err
        assert (
            "1 fail(s) were ignored, "
            "because they were defined to be expected mismatches." in err
        )

    @pytest.mark.parametrize("silent", [False, True])  # type: ignore
    def test_ignore_missing_module_symbols(
        self, silent: bool, capsys: CaptureFixture
    ) -> None:
        success = analyze_stubs(
            self.mypy_config_path,
            self.get_test_stub_path("test_ignore_missing_module_symbols"),
            silent=silent,  # Does not afffect error output
        )

        _, err = capsys.readouterr()

        assert 'Symbol "isort.comments.__name__" not found' not in err
        assert 'Symbol "isort.comments.__doc__" not found' not in err
        assert 'Symbol "isort.comments.__file__" not found' not in err
        assert 'Symbol "isort.comments.__package__" not found' not in err

        assert success

    @pytest.mark.parametrize("silent", [False, True])  # type: ignore
    def test_analyze_mismatching(self, silent: bool, capsys: CaptureFixture) -> None:
        analyze_stubs(
            self.mypy_config_path,
            self.handwritten_stubs_path,
            self.generated_stubs_path,
            self.get_expectations_path("mismatching.json"),
            silent=silent,  # Does not afffect error output
        )

        _, err = capsys.readouterr()

        assert "mismatching.mismatching_function" not in err
        assert (
            'Expected "mismatching.MISMATCHING_CONSTANT" to be "not_found" '
            'but it was "mismatch"' in err
        )
        assert "Types for mismatching.mismatch_variable do not match" in err
        assert (
            "2 fail(s) were ignored, "
            "because they were defined to be expected mismatches." in err
        )

    @pytest.mark.parametrize("silent", [False, True])  # type: ignore
    def test_analyze_matching(self, silent: bool, capsys: CaptureFixture) -> None:
        analyze_stubs(
            self.mypy_config_path,
            self.handwritten_stubs_path,
            self.generated_stubs_path,
            self.get_expectations_path("matching.json"),
            silent=silent,  # Does not afffect error output
        )

        _, err = capsys.readouterr()

        assert "matching.matching_function" not in err
        assert (
            'Expected "matching.MATCHING_CONSTANT" to be "not_found" but it matched'
            in err
        )
        assert (
            'Expected "matching.matching_variable" to be "mismatch" but it matched'
            in err
        )

    @pytest.mark.parametrize("silent", [False, True])  # type: ignore
    def test_analyze_additional_params(
        self, silent: bool, capsys: CaptureFixture
    ) -> None:
        analyze_stubs(
            self.mypy_config_path,
            self.handwritten_stubs_path,
            self.generated_stubs_path,
            self.get_expectations_path("additional_function_params.json"),
            silent=silent,  # Does not afffect error output
        )

        _, err = capsys.readouterr()

        assert "functions.additional_args" not in err
        assert (
            'Expected "functions.matching_function" to be "mismatch" but it matched'
            in err
        )

    def test_analyze_checkstyle_report(self) -> None:
        report_path = "checkstyle_report.xml"
        analyze_stubs(
            self.mypy_config_path,
            self.handwritten_stubs_path,
            self.generated_stubs_path,
            None,
            report_path,
        )

        try:
            written_report = open(report_path)
            base_path = Path.resolve(
                Path(os.path.dirname(os.path.abspath(__file__))) / ".."
            )
            expected_report_path = base_path / "testing" / "test_report.xml"
            expected_report = open(expected_report_path)
            written_tree = ET.fromstring(written_report.read())
            expected_tree = ET.fromstring(
                expected_report.read().format(path=str(base_path))
            )
            assert written_tree.tag == expected_tree.tag
            assert written_tree.attrib == expected_tree.attrib
            assert len(written_tree) == len(expected_tree)
            for (written_file, expected_file) in zip(written_tree, expected_tree):
                assert written_file.tag == expected_file.tag
                assert written_file.attrib == expected_file.attrib
                assert len(written_file) == len(expected_file)
                for (written_error, expected_error) in zip(written_file, expected_file):
                    assert written_error.tag == expected_error.tag
                    assert written_error.attrib == expected_error.attrib
        finally:
            os.unlink(report_path)


class TestCompareSymbols:
    def test_generated_is_missing_a_function(self, mypy_nodes: MypyNodeFactory) -> None:
        func_def_symbol = mypy_nodes.get_missing_function_node()
        result = compare([func_def_symbol], [])

        assert all([x.match_result is MatchResult.NOT_FOUND for x in result])

    def test_generated_has_no_parameters(self, mypy_nodes: MypyNodeFactory) -> None:
        func_def, func_def_reference = mypy_nodes.get_mismatch_with_zero_parameters()
        result = compare([func_def], [func_def_reference])

        assert all([x.match_result is MatchResult.MISMATCH for x in result])

    def test_mislocated_symbol(self, mypy_nodes: MypyNodeFactory) -> None:
        mislocated_method = mypy_nodes.get_mislocated_method_handwritten()
        _, mislocated_methods_class = mypy_nodes.get_mislocated_methods_class()
        _, original_class = mypy_nodes.get_class()
        _, original_method = mypy_nodes.get_method()

        result = list(
            compare(
                [mislocated_method],
                [mislocated_methods_class, original_class, original_method],
            )
        )
        assert result == [
            ComparisonResult.create_mislocated_symbol(
                symbol=mislocated_method,
                reference=original_method,
                data={"containing_class": original_method.info},
            )
        ]


class TestCommandLineTool:
    @patch("sys.argv", ["analyze-stubs"])
    def test_missing_required_arguments(self, capsys: CaptureFixture) -> None:
        with pytest.raises(SystemExit) as ex:
            main()
        assert ex.value.code == 2

        output = capsys.readouterr().err

        assert re.search(r"analyze-stubs: error", output)
        assert re.search(
            r"the following arguments are required: -c/--config, STUBS_HANDWRITTEN",
            output,
        )

    @patch(
        "sys.argv",
        [
            "analyze-stubs",
            "-c",
            "mypy.ini",
            "testing/test-stubs/test_generated_reference_stubs",
        ],
    )
    def test_generated_reference_stubs(self, capsys: CaptureFixture) -> None:
        """
        Ensures that analyzing stubs with automatically generated reference
        stubs works as expected.
        """
        with pytest.raises(SystemExit) as ex:
            main()
        assert ex.value.code == 1

        output = capsys.readouterr().err

        # incorrectly stubbed
        assert re.search(
            r"Types for black.const.DEFAULT_LINE_LENGTH do not match", output
        )
        assert re.search(r"Types for black.concurrency.shutdown do not match", output)
        assert re.search(
            r"Symbol \"black.NotFound\" not found in generated stubs", output
        )

        # cancel has been correctly stubbed
        assert not re.search(r"cancel", output)


class TestMislocatedSymbol(WithStubTestConfig):
    def test_mislocated_symbol(self, capsys: CaptureFixture) -> None:
        analyze_stubs(
            self.mypy_config_path,
            self.handwritten_stubs_path,
            self.generated_stubs_path,
        )

        _, err = capsys.readouterr()

        assert (
            'Found symbol "classes.ClassWithoutSuperClassInHandwritten.a_method"'
            ' in different location "classes.AClass.a_method".'
        ) in err

    def test_mislocated_symbol_expected(self, capsys: CaptureFixture) -> None:
        analyze_stubs(
            self.mypy_config_path,
            self.handwritten_stubs_path,
            self.generated_stubs_path,
            self.get_expectations_path("mislocated_symbol.json"),
        )

        _, err = capsys.readouterr()

        assert (
            'Found symbol "classes.ClassWithoutSuperClassInHandwritten.a_method"'
            ' in different location "classes.AClass.a_method".'
        ) not in err


class TestCompileError(WithStubTestConfig):
    def test_compile_error_invalid_syntax_in_base_stubs(self) -> None:
        """Invalid stubs written by the user should cause a CompileError"""
        with pytest.raises(CompileError) as ex:
            analyze_stubs(
                self.mypy_config_path,
                self.get_test_stub_path("test_compile_error_invalid_syntax"),
            )

        assert "poolmanager.pyi:7: error: invalid syntax" in ex.value.messages[0]

    def test_compile_error_invalid_syntax_in_reference(self) -> None:
        """
        Invalid reference stubs should cause a CompileError, too. This simulates the
        case where stubgen generates invalid stubs due to an internal error.
        """
        with pytest.raises(CompileError) as ex:
            analyze_stubs(
                self.mypy_config_path,
                self.handwritten_stubs_path,
                self.get_test_stub_path("test_compile_error_invalid_syntax"),
            )

        assert "poolmanager.pyi:7: error: invalid syntax" in ex.value.messages[0]


class TestIncludePrivate(WithStubTestConfig):
    def test_include_private_flag_forwarded_to_stubgen(
        self, capsys: CaptureFixture
    ) -> None:
        analyze_stubs(
            self.mypy_config_path,
            self.get_test_stub_path("test_include_private"),
            include_private=True,
        )

        _, err = capsys.readouterr()

        assert err == ""
