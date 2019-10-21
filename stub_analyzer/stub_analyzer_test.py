from stub_analyzer.stub_analyzer import main


class TestStubAnalyzer:
    def test_main_returns_0(self) -> None:
        result = main()
        assert result == 0
