import os
from .__cli__ import cli_main
from .__gui__ import gui_main
from .__common__ import parse_arguments
from .core import VersionFinder


def main():
    """Main entry point for the application."""
    args = parse_arguments()

    if args.version:
        from version_finder import __version__
        print(f"version_finder v{__version__}")
        return 0

    if args.cli:
        cli_main(args)
    elif args.gui:
        gui_main(args)
    else:
        if args.path is None:
            args.path = os.getcwd()
        if args.path and args.branch and args.commit:
            vf = VersionFinder(path=args.path)
            vf.update_repository(args.branch)
            version = vf.find_first_version_containing_commit(args.commit, args.submodule)
            if version:
                print(f"The first version which includes commit {args.commit} is {version}")
            else:
                print(f"No version found for commit {args.commit}")
        else:
            print("Please provide a path, branch, and commit to search for.")
            print("Or add --cli or --gui to run the CLI or GUI version respectively.")


if __name__ == "__main__":
    main()
