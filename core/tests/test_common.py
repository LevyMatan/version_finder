from version_finder.common import args_to_command
import argparse
import pytest


class TestCommon:

    def test_args_to_command_1(self):
        """
        Test args_to_command with various argument types including boolean flags and string values.
        """
        # Create a mock Namespace object with different types of arguments
        args = argparse.Namespace(
            verbose=True,
            path="/test/path",
            timeout=30,
            retries=0,
            version=False
        )

        # Call the function under test
        result = args_to_command(args)

        # Assert the expected output
        print(result)
        expected_output = "--verbose --path /test/path --timeout 30 --retries 0"
        assert result == expected_output

    def test_args_to_command_2(self):
        """
        Test args_to_command with non-boolean and non-None values
        """
        # Create a mock argparse.Namespace object
        args = argparse.Namespace()
        args.path = "/path/to/repo"
        args.timeout = 60
        args.retries = 3

        # Call the function under test
        result = args_to_command(args)

        # Assert the expected output
        expected_output = "--path /path/to/repo --timeout 60 --retries 3"
        assert result == expected_output, f"Expected '{expected_output}', but got '{result}'"

    def test_args_to_command_3(self):
        """
        Test args_to_command with a mix of None, False, and non-None values.
        """
        # Create a mock argparse.Namespace object with a mix of values
        args = argparse.Namespace(
            path="/some/path",
            commit=None,
            branch=None,
            verbose=False,
            timeout=30,
            retries=0
        )

        # Call the function under test
        result = args_to_command(args)

        # Assert that the result contains only the non-None and non-False values
        expected = "--path /some/path --timeout 30 --retries 0"
        assert result == expected, f"Expected '{expected}', but got '{result}'"

    def test_args_to_command_boolean_flags(self):
        """
        Test args_to_command with boolean flags in the Namespace.
        """
        args = argparse.Namespace(verbose=True, gui=False)
        result = args_to_command(args)
        assert result == "--verbose", "Expected only True boolean flags to be included"

    def test_args_to_command_empty_namespace(self):
        """
        Test args_to_command with an empty Namespace object.
        """
        empty_args = argparse.Namespace()
        result = args_to_command(empty_args)
        assert result == "", "Expected empty string for empty Namespace"

    def test_args_to_command_empty_string_values(self):
        """
        Test args_to_command with empty string values in the Namespace.
        """
        args = argparse.Namespace(path="", commit="test")
        result = args_to_command(args)
        assert result == "--path  --commit test", "Expected empty string values to be included"

    def test_args_to_command_invalid_type(self):
        """
        Test args_to_command with an invalid input type.
        """
        with pytest.raises(AttributeError):
            args_to_command("not a Namespace object")

    def test_args_to_command_non_string_values(self):
        """
        Test args_to_command with non-string values in the Namespace.
        """
        args = argparse.Namespace(timeout=30, retries=3)
        result = args_to_command(args)
        assert result == "--timeout 30 --retries 3", "Expected correct string representation of non-string values"

    def test_args_to_command_none_values(self):
        """
        Test args_to_command with None values in the Namespace.
        """
        args = argparse.Namespace(path=None, verbose=None)
        result = args_to_command(args)
        assert result == "", "Expected empty string for Namespace with None values"

    def test_args_to_command_special_characters(self):
        """
        Test args_to_command with special characters in argument names.
        """
        args = argparse.Namespace(**{"special_arg!": "value"})
        result = args_to_command(args)
        assert result == "--special-arg! value", "Expected underscore to be replaced with hyphen"

    def test_args_to_command_with_boolean_flag(self):
        """
        Test args_to_command with a boolean flag set to True.
        """
        # Create a mock Namespace object with a boolean flag
        args = argparse.Namespace(verbose=True, path=None)

        # Call the function under test
        result = args_to_command(args)

        # Assert the expected output
        assert result == "--verbose"

    def test_args_to_command_with_none_values(self):
        """
        Test args_to_command with None values, which should be excluded from the command.
        """
        # Create a mock argparse.Namespace object with None values
        args = argparse.Namespace(
            path=None,
            commit=None,
            branch=None,
            verbose=False,
            timeout=None
        )

        # Call the function under test
        result = args_to_command(args)

        # Assert that the result is an empty string, as all values are either None or False
        assert result == "", "Expected an empty string for args with None values"
