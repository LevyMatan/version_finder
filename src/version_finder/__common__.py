import argparse
import shutil
from ._version import __version__


def parse_arguments() -> argparse.Namespace:
    """Parse and validate command line arguments."""
    parser = argparse.ArgumentParser(
        description="Version Finder - A tool to find and compare versions in Git repositories",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -p /path/to/repo                 # Find versions in specified repository
  %(prog)s -v                               # Run with verbose output
  %(prog)s --timeout 60                     # Set git operation timeout to 60 seconds
  %(prog)s --retries 3                      # Set number of retries for git operations
""")

    parser.add_argument("-p", "--path",
                        help="Repository path (defaults to current directory)")

    parser.add_argument("-c", "--commit",
                        help="The commit hash to find the first that includes it")
    parser.add_argument("-b", "--branch",
                        help="The branch to find the first that includes it")
    parser.add_argument("-s", "--submodule",
                        help="The submodule to find the first that includes it")

    parser.add_argument("--cli", action="store_true", help="Run the CLI version")
    parser.add_argument("--gui", action="store_true", help="Run the GUI version")

    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        help="Enable verbose output")

    parser.add_argument("--timeout",
                        type=int,
                        default=30,
                        help="Git operation timeout in seconds (default: 30)")

    parser.add_argument("--retries",
                        type=int,
                        default=0,
                        help="Number of retries for git operations (default: 0)")

    parser.add_argument('--version',
                        action='version',
                        version=f'%(prog)s {__version__}',
                        help="Show program's version number and exit")

    args = parser.parse_args()

    # Validate timeout
    if args.timeout <= 0:
        parser.error("Timeout must be greater than 0")

    # Validate retries
    if args.retries < 0:
        parser.error("Number of retries cannot be negative")

    # Validate path if provided
    if args.path:
        if not shutil.os.path.exists(args.path):
            parser.error(f"Invalid path: {args.path}")

    return args
