from .__cli__ import cli_main
from .__gui__ import gui_main
from .__common__ import parse_arguments


def main():
    """Main entry point for the application."""
    args = parse_arguments()

    if args.cli:
        cli_main(args)
    elif args.gui:
        gui_main(args)
    else:
        print("No arguments provided. Defaulting to CLI.")
        cli_main(args)


if __name__ == "__main__":
    main()
