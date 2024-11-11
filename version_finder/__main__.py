# version_finder/__main__.py
import argparse
import logging
import os
import subprocess
import sys
import shutil
from typing import Optional, List
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

from .core import VersionFinder, GitConfig, GitError
from .logger import setup_logger
from .protocols import LoggerProtocol
from ._version import __version__

def verify_git_dependency(logger: LoggerProtocol) -> None:
    """
    Verify that git is installed and accessible.
    """
    git_path = shutil.which('git')
    
    if git_path is None:
        logger.error("""
Git is not found in your system PATH. Please ensure that:
1. Git is installed on your system
2. Git is added to your system PATH

You can download Git from: https://git-scm.com/downloads

After installing:
1. Close and reopen your terminal
2. Verify installation with: git --version
""")
        sys.exit(1)
    
    try:
        subprocess.run([git_path, "--version"], 
                      check=True, 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE)
        
    except subprocess.CalledProcessError as e:
        logger.error(f"""
Git was found at {git_path} but failed to execute.
Error: {e.stderr.decode('utf-8', errors='replace')}
""")
        sys.exit(1)
    except Exception as e:
        logger.error(f"""
An unexpected error occurred while running git:
{str(e)}
""")
        sys.exit(1)

    logger.debug(f"Git found at: {git_path}")

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

    return args

def get_branch_selection(branches: List[str], logger: LoggerProtocol) -> str:
    """
    Get branch selection from user with auto-completion.
    
    Args:
        branches: List of available branches
        logger: Logger instance
    
    Returns:
        Selected branch name
    """
    branch_completer = WordCompleter(branches, ignore_case=True)
    
    while True:
        try:
            logger.info("\nAvailable branches:")
            for branch in branches:
                logger.info(f"  - {branch}")
            
            branch = prompt(
                "\nEnter branch name (Tab for completion): ",
                completer=branch_completer,
                complete_while_typing=True
            ).strip()
            
            if branch in branches:
                return branch
            
            logger.error("Invalid branch selected")
            
        except (KeyboardInterrupt, EOFError):
            logger.info("\nOperation cancelled by user")
            sys.exit(0)

def main() -> int:
    """Main entry point for the version finder CLI."""
    # Parse arguments
    args = parse_arguments()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logger = setup_logger(__name__, level=log_level)
    
    logger.debug("Starting Version Finder")
    logger.debug(f"Arguments: {args}")

    # Verify git installation
    verify_git_dependency(logger)

    try:
        # Create git configuration
        config = GitConfig(
            timeout=args.timeout,
            max_retries=args.retries
        )

        # Initialize VersionFinder
        logger.debug(f"Initializing VersionFinder with path: {args.path}")
        finder = VersionFinder(
            path=args.path,
            config=config,
            logger=logger
        )

        # Get available branches
        logger.debug("Fetching available branches")
        branches = finder.get_branches()
        if not branches:
            logger.error("No branches found in repository")
            return 1

        # Get branch selections for comparison
        logger.info("\nSelect first branch for comparison:")
        branch1 = get_branch_selection(branches, logger)
        logger.info(f"Selected first branch: {branch1}")
        
        logger.info("\nSelect second branch for comparison:")
        branch2 = get_branch_selection(branches, logger)
        logger.info(f"Selected second branch: {branch2}")

        # Compare versions between branches
        logger.info("\nComparing versions between branches...")
        comparison = finder.compare_versions(branch1, branch2)
        
        # Display results
        logger.info("\nVersion comparison results:")
        differences_found = False
        
        for file_path, (ver1, ver2) in comparison.items():
            if ver1 != ver2:
                differences_found = True
                logger.info(f"\nFile: {file_path}")
                logger.info(f"  {branch1}: {ver1 or 'Not found'}")
                logger.info(f"  {branch2}: {ver2 or 'Not found'}")
        
        if not differences_found:
            logger.info("No version differences found between branches")

        return 0

    except GitError as e:
        logger.error(f"Git error: {str(e)}")
        return 1
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        return 0
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        if args.verbose:
            logger.debug(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())
