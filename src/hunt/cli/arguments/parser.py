from argparse import ArgumentParser, Namespace

from ..config import Config


def setup_argument_parser() -> ArgumentParser:
    """
    Sets up an argument parser with all supported commands.
    :return: an ArgumentParser instance
    """
    argument_parser: ArgumentParser = ArgumentParser(add_help=False, exit_on_error=False)

    # Debug variables
    argument_parser.add_argument("--debug", action="store_true")

    # Test server support
    argument_parser.add_argument("--test-server", action="store_true")

    # Statistics
    argument_parser.add_argument("--statistics", action="store_true")

    return argument_parser


def parse_arguments() -> Config:
    """
    Parses command line arguments into a Config instance.
    :return: a Config instance
    """
    # Parse any provided arguments
    argument_parser: ArgumentParser = setup_argument_parser()
    arguments: Namespace = argument_parser.parse_args()

    # Return a Config instance
    return Config(arguments.debug, arguments.test_server, arguments.statistics)
