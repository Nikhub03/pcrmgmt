"""Точка входа."""
import sys
import os

# Чтобы работал `python -m src.main`
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.config import load_config
from src.core.logger import log_info, log_error
from src.core.errors import InvalidArgument, DeviceNotFound
from src.cli.parser import build_parser
from src.cli.commands import (
    cmd_help, cmd_exit, cmd_status, cmd_info, cmd_monitor,
    cmd_report, cmd_serve,
)


def dispatch(args, parser):
    handlers = {
        "help": cmd_help,
        "exit": cmd_exit,
        "status": cmd_status,
        "info": cmd_info,
        "monitor": cmd_monitor,
        "report": cmd_report,
        "serve": cmd_serve,
    }
    fn = handlers.get(args.command)
    if fn:
        fn(args, parser)
    else:
        parser.print_help()


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    load_config(args.config)
    log_info("CLI", f"User issued command: {' '.join(sys.argv[1:])}")
    try:
        dispatch(args, parser)
    except InvalidArgument as e:
        log_error("CLI", str(e))
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
    except DeviceNotFound as e:
        log_error("CLI", str(e))
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(3)
    except KeyboardInterrupt:
        log_info("CLI", "Application terminated by user")
        sys.exit(0)


if __name__ == "__main__":
    main()