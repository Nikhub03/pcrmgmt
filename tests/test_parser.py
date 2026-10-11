import pytest
from src.cli.parser import build_parser


def test_help_command():
    p = build_parser()
    args = p.parse_args(["help"])
    assert args.command == "help"


def test_info_default():
    p = build_parser()
    args = p.parse_args(["info"])
    assert args.output == "text"


def test_monitor_interval():
    p = build_parser()
    args = p.parse_args(["monitor", "--interval", "0.5"])
    assert args.interval == 0.5


def test_unknown_command():
    p = build_parser()
    with pytest.raises(SystemExit):
        p.parse_args(["nonexistent"])
