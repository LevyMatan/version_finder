import pytest
import sys
from version_finder import setup_logger
from ..src.version_finder_cli.cli import main

logger = setup_logger(verbose=True)


class TestCLI:
    @pytest.fixture
    def test_repo(self, tmp_path):
        repo_dir = tmp_path / "test_repo"
        repo_dir.mkdir()
        return repo_dir

    def test_cli_help(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            sys.argv = ['version_finder', '--help']
            main()
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert "usage:" in captured.out

    def test_cli_invalid_path(self, capsys):
        with pytest.raises(SystemExit):
            sys.argv = ['version_finder', '--path', '/nonexistent/path']
            main()
        captured = capsys.readouterr()
        assert "error" in captured.err.lower()

    def test_cli_version_flag(self, capsys):
        sys.argv = ['version_finder', '--version']
        main()
        captured = capsys.readouterr()
        assert "version" in captured.out.lower()

    def test_cli_invalid_option(self, capsys):
        with pytest.raises(SystemExit):
            sys.argv = ['version_finder', '--invalid-option']
            main()
        captured = capsys.readouterr()
        assert "error" in captured.err.lower()

    # def test_cli_verbose_flag(self, capsys, test_repo):
    #     sys.argv = ['version_finder', '--path', str(test_repo), '--verbose']
    #     main()
    #     captured = capsys.readouterr()
    #     assert "debug" in captured.out.lower() or "info" in captured.out.lower()
