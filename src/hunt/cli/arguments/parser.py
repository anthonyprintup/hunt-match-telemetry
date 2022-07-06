from argparse import ArgumentParser


def setup_argument_parser() -> ArgumentParser:
    """
    Sets up an argument parser with all supported commands.
    :return: an ArgumentParser instance
    """
    argument_parser: ArgumentParser = ArgumentParser(add_help=False, exit_on_error=False)

    # Debug variables
    argument_parser.add_argument("--debug", action="store_true")

    return argument_parser
